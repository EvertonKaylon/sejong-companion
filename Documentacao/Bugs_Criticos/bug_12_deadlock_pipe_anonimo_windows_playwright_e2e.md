# BUG-12: Deadlock de Pipe Anônimo no Windows em Testes E2E com Playwright

| Metadado | Detalhe |
| :--- | :--- |
| **ID do Bug** | `BUG-12` |
| **Severidade** | 🔴 Crítica (Deadlock de Processo & Bloqueio da Suíte E2E no Windows) |
| **Componentes Afetados** | Fixture `flet_server` (`tests/test_playwright_e2e.py`), Infraestrutura de Testes E2E, Pipeline de CI/CD |
| **Data de Resolução** | 2026-09-20 |
| **Branch** | `develop` / `feature/branding` (Reconciliação Milestones M1 & M5) |
| **Testes Automatizados** | `tests/test_playwright_e2e.py` (5/5 PASS em ~26s no Chromium real), `tests/test_e2e_full_coverage.py` (16/16 PASS) |

---

## 1. Descrição Sintomática

Ao executar a suíte de testes de integração ponta a ponta (E2E) com Playwright Chromium em ambiente Windows (`python -m pytest tests/test_playwright_e2e.py -v`), a execução iniciava normalmente no primeiro cenário (`test_p1_infra_and_server_handshake`), mas travava indefinidamente a partir da navegação ou transição para o segundo cenário (`test_p2_architecture_and_black_screen_prevention`).

### Sintomas Observados:
1. **Congelamento Silencioso:** O executor do `pytest` congelava indefinidamente sem consumir CPU, sem gerar exceções, traceback ou expirar por timeout nos steps do Playwright.
2. **Navegador Suspenso:** A instância do Chromium aberta pelo Playwright permanecia em espera passiva aguardando mensagens WebSocket ou requisições HTTP do servidor Flet Web (`http://127.0.0.1:8554`).
3. **Estado dos Processos no Kernel:** Ao inspecionar os processos no Windows Resource Monitor / Process Explorer, o processo filho do servidor Flet (`python main.py`) figurava no estado `Wait:Executive` bloqueado em chamada de sistema de escrita de arquivo, enquanto o processo pai (`pytest`) permanecia bloqueado em chamadas de sincronização do Playwright (`Wait:UserRequest`).
4. **Impacto Bloqueante:** A bateria de testes E2E tornava-se inviável para execução local em estações Windows e travava pipelines automatizados de CI/CD que executavam o comando completo `pytest tests/`.

---

## 2. Causa Raiz Técnica

A análise de chamadas de sistema e depuração de descritores de processo revelou um deadlock circular clássico entre processo pai e processo filho decorrente do gerenciamento de pipes no Windows NT:

### A. Capacidade Reduzida do Buffer de Pipe Anônimo no Windows NT
No sistema operacional Windows, os pipes anônimos criados pela API Win32 `CreatePipe()` (invocada internamente pelo módulo `subprocess` do Python ao especificar `stdout=subprocess.PIPE` e `stderr=subprocess.PIPE`) possuem um buffer circular padrão de apenas **4.096 bytes (4 KB)**.

### B. Volume Elevado de Telemetria e Logs do Servidor Flet Web
O servidor Flet Web, alimentado pelo ASGI Uvicorn/FastAPI e servindo os assets do Flutter CanvasKit, WebSockets bidirecionais e roteamento dinâmico, emite logs detalhados de inicialização, requisições HTTP (GET `/`, `/flutter.js`, `/canvaskit/canvaskit.wasm`, `/branding/*`) e conexões WebSocket. Em menos de 2 a 3 requisições de página pelo Playwright, o volume total de bytes impressos em `stdout` e `stderr` supera com folga a capacidade de 4 KB do buffer.

### C. Ausência de Drenagem no Processo Pai (Deadlock)
Na implementação original da fixture `flet_server` com escopo de módulo (`scope="module"`), o processo pai iniciava o servidor via:
```python
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    env=env,
    cwd=root_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
```
Como o processo pai passava o controle imediatamente para a execução dos métodos de teste do Playwright (`yield base_url`), nenhuma thread lia ou esvaziava os descritores `proc.stdout` e `proc.stderr`. 

Quando o buffer de 4 KB do pipe enchia:
1. O processo filho (servidor Flet) executava uma chamada Win32 `WriteFile()` para emitir o próximo log.
2. O kernel do Windows suspendia o thread do servidor até que espaço fosse liberado no buffer do pipe.
3. Com o thread do servidor congelado, o servidor Flet parava de responder requisições HTTP e de processar mensagens WebSocket.
4. O Playwright (no processo pai) aguardava indefinidamente a resposta da rede do servidor para completar a asserção da tela.
5. **Deadlock Estabelecido:** O pai espera o filho responder à rede; o filho espera o pai ler seu buffer de pipe.

---

## 3. Soluções e Código: Antes vs. Depois

### A. Configuração da Fixture no Arquivo `tests/test_playwright_e2e.py`

#### Antes (Buffer PIPE sem drenagem -> Deadlock no Windows):
```python
# ❌ Saturação do buffer de 4 KB do kernel Windows NT bloqueia WriteFile()
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    env=env,
    cwd=root_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

# Timeout de espera inicial
for _ in range(30):
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        raise RuntimeError(
            f"Flet server process terminated early with code {proc.returncode}.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
        )
    ...
```

#### Depois (Descarte Imediato em `subprocess.DEVNULL` -> Zero Alocação de Buffer):
```python
# ✅ Descritores redirecionados para o dispositivo NUL do SO (sem buffers intermediários)
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    env=env,
    cwd=root_dir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    text=True,
)

# Verificação sem communicate() bloqueante
for _ in range(30):
    if proc.poll() is not None:
        raise RuntimeError(
            f"Flet server process terminated early with code {proc.returncode}."
        )
    ...
```

### B. Benefícios Obtidos com a Correção:
1. **Desempenho I/O Ótimo:** Redirecionar para `subprocess.DEVNULL` instrui o sistema operacional a descartar os descritores diretamente no driver `\\Device\\Null` (`NUL`), eliminando alocação de memória no pool não-paginado do kernel.
2. **Execução Estável e Fluida:** A suíte completa com os 5 cenários dinâmicos do Chromium roda de forma contínua em **~26 segundos** (incluindo pausas deliberadas de estabilização visual do CanvasKit).
3. **Isolamento Concorrente:** Não há necessidade de instanciar threads de leitura em segundo plano (`threading.Thread`) no pytest que poderiam concorrer com os event loops assíncronos do Playwright.

---

## 4. Regras Preventivas

Para evitar a reintrodução de deadlocks de I/O em fixtures de teste ou processos de suporte em segundo plano no ecossistema Python/Windows:

1. **Proibição de `PIPE` Desassistido:** NUNCA utilizar `stdout=subprocess.PIPE` ou `stderr=subprocess.PIPE` em subprocessos com ciclo de vida longo (`scope="module"`, `scope="session"`, daemons ou servidores web locais) a menos que haja leitura contínua e assíncrona dedicada em threads separadas.
2. **Uso Canônico de `subprocess.DEVNULL`:** Em fixtures de teste onde o objetivo é testar o serviço via protocolo de rede (HTTP, WebSockets, Playwright) e não a saída de console, redirecionar sempre ambos `stdout` e `stderr` para `subprocess.DEVNULL`.
3. **Captura Opcional via Arquivo Temporário:** Se for estritamente necessário capturar logs do servidor para diagnóstico pós-falha, redirecionar a saída para um arquivo temporário em disco via `tempfile.NamedTemporaryFile(delete=False)`. O sistema de arquivos não impõe o limite de 4 KB de buffer e permite inspeção segura no bloco de teardown da fixture.
4. **Timeouts Explícitos em Chamadas Subprocess:** Assegurar que qualquer chamada a `proc.wait()` ou asserções de encerramento no teardown possuam timeout rígido (`proc.wait(timeout=5)`), seguido de `proc.kill()` caso o processo não finalize graciosamente.

---

## 5. Verificação da Correção

A resolução foi validada em ambiente Windows nativo com os seguintes testes automatizados:

```powershell
# 1. Execução da suíte E2E Playwright completa (5 cenários dinâmicos)
python -m pytest tests/test_playwright_e2e.py -v
# Resultado: 5 passed in 26.65s (Zero deadlocks, 100% de aprovação)

# 2. Execução da suíte de 5 pilares estruturais
python -m pytest tests/test_e2e_full_coverage.py -v
# Resultado: 16 passed in 1.31s (Zero regressões)
```
