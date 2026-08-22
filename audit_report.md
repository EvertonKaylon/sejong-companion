# 🔍 Auditoria Profunda — Sejong Companion

> Análise exaustiva de bugs, implementações falsas/mockadas, funcionalidades quebradas, anti-patterns e falhas de segurança.

---

## 🔴 Severidade CRÍTICA (Causa crash, perda de dados ou funcionalidade completamente quebrada)

---

### 1. Router Quebrado — `view_pop()` nunca funciona
**Arquivo:** [`router.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/router.py#L17-L48)

O `route_change` (L19) **sempre limpa todas as views** com `self.page.views.clear()` e depois adiciona apenas 1 view. Consequência direta: `self.page.views` **sempre** terá tamanho 1. A condição `if len(self.page.views) > 1` em `view_pop` (L43) **nunca será verdadeira**.

**Impacto:** O botão "voltar" nativo do sistema/navegador **não funciona**. Toda a navegação de retorno está reimplementada como `navigate_to("/home")` hardcoded nas views, poluindo a pilha de rotas e quebrando a UX padrão de navegação.

```python
# L17-19: SEMPRE limpa tudo
def route_change(self, e):
    self.page.views.clear()  # 🐛 Mata o histórico inteiro
    # ...adiciona só 1 view

# L41-47: Condição NUNCA verdadeira
def view_pop(self, e):
    if len(self.page.views) > 1:  # 🐛 Sempre é 1
        self.page.views.pop()
```

---

### 2. `silent.wav` não existe — Áudio Web **completamente quebrado**
**Arquivo:** [`audio_service.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/audio_service.py#L56-L61)

O `AudioService.__init__` cria um player Flet com `src="silent.wav"` e `autoplay=True` para "destravar" o autoplay do Chrome/Edge. **Porém o arquivo `silent.wav` não existe no projeto** (`assets/` não contém nenhum `silent*`).

**Impacto:** Em modo web (deploy em nuvem ou `--browser`), o mecanismo de destravamento de autoplay falha silenciosamente. O player nunca é destravado, e **toda reprodução de áudio subsequente será bloqueada pelo navegador** (timeout no `play()`). O app fica mudo para todos os usuários web.

---

### 3. Fontes Google Fonts via CSS — Flet ignora silenciosamente
**Arquivo:** [`theme.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/theme.py#L263-L264)

```python
"Noto Sans KR": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR...",
"Inter": "https://fonts.googleapis.com/css2?family=Inter...",
```

O `page.fonts` do Flet (baseado em Flutter) **exige URLs diretas para arquivos `.ttf`/`.otf`/`.woff`**. Estas URLs apontam para **arquivos CSS** que o Google Fonts retorna como stylesheet. Flutter não sabe parsear CSS como fonte — **falha silenciosamente** e renderiza com a fonte de fallback do sistema.

**Impacto:** Os textos que deveriam usar "Noto Sans KR" ou "Inter" são renderizados com a fonte padrão do sistema, quebrando o design coreano.

---

### 4. Bug matemático no SRS — `half_life` vai a zero/negativo em erros consecutivos
**Arquivo:** [`models.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/models.py#L231-L234)

```python
def update_performance(self, is_correct: bool, response_time_ms=2000):
    if not is_correct:
        self.error_count += 1
        self.half_life = self.half_life * (0.3 / (self.error_count * 0.5))
```

Quando `error_count` sobe (L232 incrementa **antes** do cálculo em L233):
- 1° erro: `error_count=1` → `h * (0.3 / 0.5)` = `h * 0.6` ✓
- 2° erro: `error_count=2` → `h * (0.3 / 1.0)` = `h * 0.3` ✓
- 3° erro: `error_count=3` → `h * (0.3 / 1.5)` = `h * 0.2`
- 10° erro: `error_count=10` → `h * (0.3 / 5.0)` = `h * 0.06`

Após poucos erros consecutivos, `half_life` fica tão próximo de zero (~0.01) que a meia-vida equivale a **menos de 1 minuto**. O item ficará **permanentemente** na fila de revisão porque `calculate_stability()` retornará ~0% imediatamente. O aluno nunca consegue "sair" desse cartão.

---

### 5. Memory Leak no servidor — Sessões NUNCA são liberadas da RAM
**Arquivo:** [`services.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L223)

```python
class ProgressService:
    _sessions: dict = {}  # 🐛 Class-level, NUNCA limpo
```

O dicionário `_sessions` é um atributo de **classe** (compartilhado entre todas as instâncias). Cada novo aluno que acessa o app adiciona uma entrada, e **nenhuma lógica de evicção existe**. Em deploy cloud com múltiplos alunos simultâneos, isso é um **memory leak progressivo** que eventualmente derrubará o processo.

---

### 6. Race Condition em escritas de arquivo concorrentes
**Arquivo:** [`services.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L328-L332)

```python
def _save_to_disk(cls, session_id, data):
    tmp_path = f"{path}.tmp"  # 🐛 Nome estático, sem lock
    with open(tmp_path, "w") as f:
        json.dump(data, f)
    os.replace(tmp_path, path)
```

O nome do temporário é **estático** (`{path}.tmp`). Se duas requisições do mesmo aluno executam `_save_to_disk` simultaneamente (ex: áudio + quiz callback em tabs paralelas), ambas escrevem no mesmo `.tmp` simultaneamente → **corrupção de dados**.

O `TelemetryService.record()` (L726-728) tem o mesmo problema: `open("a")` sem lock em ambiente async.

---

## 🟠 Severidade ALTA (Funcionalidade que parece funcionar mas não funciona de verdade)

---

### 7. Animação de áudio falsa — Mudança de cor invisível
**Arquivo:** [`vocab_card.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/vocab_card.py#L192-L213)

```python
def play_audio_animation(self, e):
    self.audio_icon.icon_color = self.colors["secondary"]  # muda
    self.audio_icon.update()
    if self.on_audio_click:
        self.on_audio_click(self.vocab_item.word)
    self.audio_icon.icon_color = self.colors["primary"]    # volta
    self.audio_icon.update()
```

É uma função **síncrona**. O Flet faz batching de updates por frame — as duas mudanças de cor (L194 e L212) são agrupadas num único frame, e o usuário **nunca vê a animação**. Precisaria de `await asyncio.sleep()` entre as mudanças.

---

### 8. Windows Desktop sem fallback de áudio — App fica **mudo**
**Arquivo:** [`audio_service.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/audio_service.py#L195-L196)

```python
if audio is None and not self._use_native_windows_player:
    audio = self._get_google_audio(text)
```

Se a API Typecast falhar (ou a chave não estiver configurada) e o app rodar como desktop Windows:
- `_use_native_windows_player = True` → pula o fallback Google TTS
- `winsound` só aceita WAV, e o Google retorna MP3
- Resultado: **nenhum áudio** é reproduzido, sem erro visível

O app parece funcional mas é **completamente mudo** quando Typecast não está disponível no desktop Windows.

---

### 9. Normalização incompleta no Sentence Builder — Respostas corretas rejeitadas
**Arquivo:** [`sentence_builder_widget.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/sentence_builder_widget.py#L101)

```python
normalize = lambda value: " ".join((value or "").strip().replace(".", "").split())
```

Só remove `.` (ponto final). Não remove `?`, `,`, `!`, que são comuns em frases coreanas. Se o aluno digitar `저는 학생입니까?` e a resposta for `저는 학생입니까`, será marcado como **errado** por causa do `?`.

---

### 10. `except TypeError` engolindo erros reais no Quiz
**Arquivo:** [`quiz_widget.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/quiz_widget.py#L468-L472)

```python
try:
    self.on_answer(is_correct, elapsed_ms)
except TypeError:
    self.on_answer(is_correct)  # 🐛 fallback perigoso
```

Se `on_answer` tiver a assinatura correta (2 args) mas **dentro da execução** disparar um `TypeError` (ex: operação com tipo errado), essa exceção será engolida silenciosamente e `on_answer` será chamado novamente **sem o tempo de resposta**. Comportamento silenciosamente corrompido e impossível de debugar.

---

### 11. SRS duplicado e inconsistente — Dois motores competindo
**Arquivo:** [`services.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L449-L454) vs [`services.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L502-L517)

Existem **dois sistemas SRS rodando em paralelo**:

| Método | Fórmula | Usado por |
|---|---|---|
| `record_review()` L449 | Delega para `MemoryNode.update_performance()` (speed_factor, error_count) | Quizzes |
| `record_item_recall()` L502 | Multiplicadores hardcoded: `again=0.3, hard=0.3, good=1.5, easy=2.2` | Flashcards |

Os dois operam sobre o mesmo modelo `MemoryNode` mas com fórmulas **completamente diferentes**. Um item revisado via flashcard terá uma trajetória de meia-vida diferente de um revisado via quiz. **"again" e "hard" têm o mesmo multiplicador (0.3)** — são indistinguíveis para o motor SRS.

---

### 12. Docker: `TYPECAST_API_KEY` não propagada → Deploy sem áudio
**Arquivo:** [`docker-compose.yml`](file:///c:/Users/Pichau/Documents/sejong_companion/docker-compose.yml#L11-L12)

```yaml
# Opcional: Descomente e insira sua chave Typecast para síntese ao vivo na nuvem
# - TYPECAST_API_KEY=sua_chave_aqui
```

A chave da API está **comentada** no docker-compose. Um deploy padrão não terá `TYPECAST_API_KEY` → o Typecast retorna `None` → o Google TTS é o fallback (mas é uma API não-oficial que pode bloquear por rate-limit). O deploy de produção **depende de um hack não-documentado** para ter áudio.

---

## 🟡 Severidade MÉDIA (Anti-patterns, mocks, código frágil)

---

### 13. Autenticação Admin — PIN hardcoded e exposto na UI
**Arquivos:** [`services.py` L959](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L959) + [`admin_view.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/admin_view.py)

```python
DEFAULT_PIN: str = "sejong2026"
```

- PIN de admin em texto puro no código-fonte
- A própria tela de login exibe: *"PIN padrão de homologação: sejong2026"*
- Controle de acesso mantido no frontend: `page._admin_authenticated = True`
- Qualquer pessoa pode acessar o painel administrativo

---

### 14. `toggle_theme` destrói o histórico de navegação
**Arquivo:** [`home_view.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/home_view.py#L22)

O toggle de tema faz `page.views.clear()` seguido de rebuild. Isso **apaga todo o histórico de navegação** da sessão. Se o aluno mudar o tema durante um quiz, perde o contexto inteiro.

---

### 15. `AdminService` parser de IDs com offset errado
**Arquivo:** [`services.py` L1008-L1009](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L1008-L1009)

```python
if filename.startswith("student_") and filename.endswith(".json"):
    s_id = filename[8:-5]  # 🐛 corta "student_" (8 chars) do ID
```

O arquivo se chama `student_{uuid}.json`, mas o `_get_session_id` gera IDs como `student_abc123def456`. Quando o admin lê o arquivo, corta `student_` do nome → o ID mostrado no painel (`abc123def456`) **não corresponde** ao ID real (`student_abc123def456`). Isso quebra correlação entre dados admin e dados do aluno.

---

### 16. Tratamento de erros silencioso em massa
**Arquivos múltiplos:**

| Local | Impacto |
|---|---|
| [`services.py` L18-20](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py#L18-L20) | `DataService` engole erros de JSON, retorna `[]` |
| [`splash_view.py` L110-152](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/splash_view.py) | 5 blocos `except: pass` — splash pode travar silenciosamente |
| [`router.py` L36-39, L47-48, L55-56](file:///c:/Users/Pichau/Documents/sejong_companion/src/router.py) | 3 blocos `except: pass` — erros de navegação somem |

O padrão `except Exception: pass` é usado **sistematicamente** em todo o projeto. Erros críticos (JSON corrompido, falha de I/O, referência a propriedade inexistente) são engolidos sem log.

---

### 17. `import random` dentro de método
**Arquivo:** [`quiz_widget.py` L164](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/quiz_widget.py#L164)

Import dentro de `_build_order_words()`. Má prática que dificulta análise estática e potencialmente causa latência na primeira chamada.

---

### 18. Monkey-patching de serviços no `page`
**Arquivos:** [`main.py` L75-76, L83](file:///c:/Users/Pichau/Documents/sejong_companion/main.py#L75-L83)

```python
page.router = router
page.audio_service = AudioService(page)
```

Serviços globais são injetados como atributos dinâmicos no objeto `page`. Isso:
- Oculta dependências (nenhum type hint, nenhum IDE sabe que `page.router` existe)
- Quebra encapsulamento
- Impossibilita testes unitários limpos
- Causa `AttributeError` se alguma view for renderizada antes da injeção

---

### 19. Hardcoding de dados curriculares nas views
**Arquivo:** [`hangul_view.py` L404-415](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/hangul_view.py#L404-L415)

Os numerais coreanos (Sino-Coreanos vs Nativos) estão **chumbados no código** da view ao invés de serem providos pelo `DataService`. Qualquer alteração curricular exige mudança no código Python.

---

### 20. State management via rebuild total
**Arquivos:** [`flashcards_view.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/flashcards_view.py), [`review_view.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/review_view.py), [`quiz_view.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/quiz_view.py)

Todas as views usam dicionários mutáveis + closures + rebuild total do container a cada interação. Nenhuma view usa o padrão reativo do Flet (atualizar propriedades individuais dos controles). Isso causa flickering, perda de scroll position, e performance degradada.

---

## 🔵 Severidade BAIXA (Qualidade de código, acessibilidade, manutenibilidade)

---

### 21. Acessibilidade inexistente
- Containers com `on_click` sem semântica ARIA (nenhum `tooltip`, `semantics_label`)
- Progresso exibido como barras visuais sem texto alternativo para screen readers
- Blocos silábicos do Hangul sem `aria-label` adequado

### 22. `python-dotenv` no `requirements.txt` mas carregamento manual no `main.py`
O [`main.py`](file:///c:/Users/Pichau/Documents/sejong_companion/main.py#L6-L20) implementa seu próprio parser de `.env` (L6-20) "sem adicionar dependência de dotenv", mas `python-dotenv>=1.0.0` está em [`requirements.txt`](file:///c:/Users/Pichau/Documents/sejong_companion/requirements.txt#L6). Redundância e inconsistência.

### 23. `gTTS` no `requirements.txt` mas nunca usado
[`requirements.txt` L5](file:///c:/Users/Pichau/Documents/sejong_companion/requirements.txt#L5) lista `gTTS>=2.5.0`, mas o `audio_service.py` usa `requests` direto para Google Translate TTS (`_get_google_audio`), nunca importando `gTTS`.

### 24. Filtragem de livros por prefixo hardcoded
[`home_view.py` L219-226](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/home_view.py): Usa `.startswith("unit_1b_")` para distinguir livro 1A de 1B em vez de metadados (`unit.book`).

---

## 📊 Resumo Executivo

| Severidade | Qtd | Exemplos-chave |
|---|---|---|
| 🔴 **Crítica** | 6 | Router quebrado, `silent.wav` inexistente, memory leak, SRS math bug |
| 🟠 **Alta** | 6 | Audio mudo no Windows, normalização falha, race conditions |
| 🟡 **Média** | 8 | PIN exposto, SRS dual, monkey-patching, `except: pass` em massa |
| 🔵 **Baixa** | 4 | Acessibilidade, deps mortas, hardcoding |
| **Total** | **24** | |

> [!CAUTION]
> Os bugs #1 (Router), #2 (`silent.wav`) e #4 (SRS math) são os mais impactantes para o usuário final. O router quebra toda navegação, a falta do `silent.wav` deixa o deploy web mudo, e o bug matemático do SRS causa "loops de revisão infinita" para alunos que erram 3+ vezes.

> [!IMPORTANT]
> O projeto tem uma arquitetura sólida em conceito (SRS, telemetria, currículo data-driven), mas sofre de **falta de testes de integração** — os testes unitários existem mas não cobrem os cenários de interação real que revelam esses bugs.
