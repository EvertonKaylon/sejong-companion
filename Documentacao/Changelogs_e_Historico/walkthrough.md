# Walkthrough: Sejong Companion v0.1.0-alpha

Implementamos com sucesso a versão **0.1.0-alpha** do **Sejong Companion**, introduzindo melhorias neuro-pedagógicas profundas, erradicação total de romanizações e **integração de áudio/TTS offline-first** para todas as frentes de estudo.

---

## 🛠️ O que foi Desenvolvido na Versão 0.1.0-alpha

### 1. 🔊 Resolução do Erro "Unknown control: Audio" & Loop de Reinício (Flet Overlay)
Identificamos e corrigimos a causa raiz do loop de reinício e do erro de controle desconhecido:
- **O Problema:** O controle `Audio` do pacote `flet-audio` é um componente **não-visual (serviço)**. Ao tentarmos instanciar e adicionar este controle dentro de `active_view.controls` (que é a árvore de layout visual da tela), o Flutter Engine do Flet Desktop tentava renderizá-lo como um widget visual na tela. Como ele não possui interface física, isso gerava um crash de desserialização e um erro de `Unknown control: Audio` que fechava a sessão e forçava o app desktop a reiniciar infinitamente.
- **A Solução:**
  1. Refatoramos o [audio_service.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/audio_service.py) para criar um player único e persistente no início do ciclo de vida da aplicação.
  2. Adicionamos o player à lista **`page.overlay`** (exclusiva para componentes não-visuais e persistentes no Flet) em vez de `view.controls`.
  3. No método de reprodução `_play_file`, agora simplesmente atualizamos a fonte do player (`self.player.src = src_path`) e executamos `await self.player.play()`.
  4. Isso corrige o erro de "Multiple parents" e "Unknown control" em definitivo tanto no Desktop quanto na Web!

---

### 2. 🔌 Configuração de IP Multidispositivo (0.0.0.0 vs 127.0.0.1)
Corrigimos o erro `ERR_ADDRESS_INVALID` que acontecia na inicialização do aplicativo ao tentar abrir o endereço `http://0.0.0.0:8554` no navegador padrão:
- O IP `0.0.0.0` indica que o servidor deve escutar todas as conexões da rede, mas o navegador local do Windows não consegue direcionar tráfego para ele como destino final.
- **Solução:** No [main.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/main.py), definimos o parâmetro `host="127.0.0.1"` dentro de `ft.run` (para que o navegador abra em `http://127.0.0.1:8554` localmente) e injetamos a variável de ambiente `FLET_SERVER_IP = "0.0.0.0"` no topo do código. Dessa forma, o servidor Flet continua escutando em todas as interfaces de rede, permitindo o acesso externo via celular (ex: `http://192.168.15.140:8554`), sem quebrar a inicialização no computador local.

---

### 3. 🐛 Correção de Ciclo de Vida do Quiz (`Control must be added first`)
Corrigimos o erro `RuntimeError: Container(479) Control must be added to the page first` que impedia a visualização do Quiz:
- Esse bug acontecia porque o método `render_current_question()` de [quiz_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/quiz_view.py) chamava o método `main_content.update()` na inicialização da tela, antes de o `main_content` ser efetivamente montado e retornado pela função `ft.View`.
- **Solução:** Adicionamos uma validação condicional simples: `if main_content.page: main_content.update()`. Isso evita a tentativa precoce de atualização da árvore de componentes, permitindo que a view inicialize estaticamente no primeiro render sem quebras.

---

### 4. 🐛 Correção do Bug de Abas (Tab `label`)
Corrigimos o erro de inicialização das abas (`TypeError: Tab.__init__() got an unexpected keyword argument 'text'`) que ocorria ao transitar para as lições e retornar:
- No Flet, a propriedade que define o texto de cabeçalho do controle `ft.Tab` chama-se **`label`** e não `text`.
- Atualizamos todas as definições de abas em [lesson_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/lesson_view.py) e [hangul_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/hangul_view.py) para utilizar `label="..."`, estabilizando a navegação por rotas do roteador.

---

### 5. 🐛 Correção do Bug de Botões (Button `content`)
Corrigimos o erro de inicialização dos botões (`TypeError: Button.__init__() got an unexpected keyword argument 'text'`) que ocorria ao carregar botões com rótulos de texto:
- No Flet v0.85.3, a propriedade que define o texto de botões como `ft.ElevatedButton`, `ft.OutlinedButton` e `ft.TextButton` é chamada de **`content`** (ou aceita um controle visual no lugar do texto), em vez de `text`.
- Atualizamos todas as declarações de botões no projeto em [quiz_widget.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/components/quiz_widget.py), [lesson_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/lesson_view.py), [hangul_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/hangul_view.py) e [quiz_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/quiz_view.py) para utilizar `content="..."`, eliminando por completo o erro na interface.

---

### 6. 🚫 Erradicação Completa da Romanização
A romanização foi inteiramente eliminada do core do projeto (modelos, dados e telas), forçando o estudante a processar as informações diretamente em coreano:
- **Exclusão nos Modelos:** Limpeza das propriedades de romanização em [models.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/models.py).
- **Sem muletas na interface:** Foco absoluto no 한글 original acompanhado por explicações fonéticas textuais e sonoras em português.

---

### 7. 🧠 Enriquecimento Neuro-Pedagógico do Hangul
Aprimoramos e organizamos o aprendizado de alfabetização em [hangul_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/hangul_view.py):
- **Aviso Científico Anti-Romanização:** Raciocínio científico contra o uso de letras ocidentais para representar o coreano.
- **Dica de Escrita Manual:** Explicação sobre ativação de áreas corticais ao desenhar os traços de próprio punho.
- **Aba Exclusiva de 받침 (Batchim):** Guia com regras de neutralização articulatória e o **Alerta do "i" Fantasma** (epêntese vocálica típica de falantes de português).

---

### 8. 💼 Expansão de Profissões e Ordem SOV
- **Mais Profissões:** Incluídos mais de 15 termos do campo profissional (engenharias, RH, marketing, psicologia, meio ambiente e jornalismo) em [unit_01.json](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/data/units/unit_01.json).
- **Exercícios `order_words`:** Novo widget interativo no quiz ([quiz_widget.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/components/quiz_widget.py)) para organizar blocos de palavras e treinar a fixação da estrutura oracional SOV (Sujeito-Objeto-Verbo).

---

### ☀️ Cronobiologia e Neuro-Tips
Adicionado painel adaptativo à hora local em [home_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/home_view.py) fornecendo conselhos circadianos específicos para maximizar o rendimento cognitivo do estudante.

---

## 🧪 Verificação de Estabilização via TDD e Manual

Para garantir a ausência de regressões e a estabilidade definitiva das correções de áudio e rotas, realizamos duas etapas de validação:

### 1. Suíte de Testes Automatizados (TDD Verification)
Implementamos uma suíte completa com **16 testes unitários** usando `unittest` e um mock leve da interface Flet. Os testes cobrem:
* **Integridade dos Dados:** Validação do currículo e lições via esquemas Pydantic.
* **Persistência de Progresso:** Cálculo correto e persistência local das lições e progresso do estudante.
* **Segurança de Roteamento:** Transição limpa de telas, controle de instâncias órfãs e resiliência a cancelamentos.
* **Ciclo de Vida do Áudio:** Validação do correto registro persistente na `overlay` da página, evitando duplicações e vazamento de sessões.

Resultado da execução dos testes:
```bash
python -m unittest discover -s tests -p "test_*.py"
Ran 16 tests in 0.081s
OK
```

### 2. Verificação Manual no Navegador (Web Client)
Utilizamos um agente automatizado de navegação para simular a interação real do usuário no cliente web da aplicação (`http://127.0.0.1:8554`).

#### Resultados Detalhados:
1. **Splash Screen:** Carregamento correto no caminho `/splash`.
2. **Redirecionamento:** Transição automática de rota do splash para `/home` em ~3 segundos, sem erros de sessão pendente.
3. **Navegação do Hangul:** Acesso estável à tela de estudo do alfabeto (`/hangul`).
4. **Interação com Áudio:** Cliques nas cartas de vogais e consoantes executados com sucesso, sem causar quebras, travamentos ou loops de reinicialização.
5. **Console sem Erros:** Nenhum erro de comunicação WebSocket (`Session closed` / `TimeoutException`) foi disparado.

Abaixo estão os registros visuais coletados em tempo real durante a verificação:

#### Capturas de Tela da Verificação:

![Tela Splash](C:/Users/Pichau/.gemini/antigravity-ide/brain/0837bac1-da20-41ef-846c-f7f208bf3774/splash_screen_1784068256990.png)

![Tela Home](C:/Users/Pichau/.gemini/antigravity-ide/brain/0837bac1-da20-41ef-846c-f7f208bf3774/home_screen_1784068264889.png)

![Tela Hangul](C:/Users/Pichau/.gemini/antigravity-ide/brain/0837bac1-da20-41ef-846c-f7f208bf3774/hangul_screen_1784068272516.png)

#### Gravação do Fluxo Completo:
Veja a animação do teste de estabilidade sendo executado:
![Gravação da Verificação Manual](C:/Users/Pichau/.gemini/antigravity-ide/brain/0837bac1-da20-41ef-846c-f7f208bf3774/stabilization_verification_1784068247829.webp)
