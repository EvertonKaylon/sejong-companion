# Saebom Companion — Regras do Projeto

## Identidade do Projeto
- **Nome:** Saebom Companion (새봄 컴패니언)
- **Stack:** Python + Flet (Flutter Engine) — Web, Android, iOS, Desktop
- **Fase atual:** Alpha (`v0.3.6-alpha`)
- **Documentação oficial:** `Documentacao/` (estrutura Obsidian com wikilinks)

## Rebranding & Diretriz Pedagógica da Professora (Regras Invioláveis)
- **Proibição Estrita do Nome "Sejong":** Por ordem expressa da professora do curso, o termo "Sejong" foi categoricamente proibido. É estritamente vedado introduzir o nome "Sejong" em novas views, componentes, títulos de janela, documentações ou assets. O nome oficial da marca é **Saebom Companion (새봄 컴패니언)**.
- **Regra de Ouro Pedagógica:** *"A tecnologia acompanha a pedagogia. Nunca compete com ela."* O aplicativo atua como companion de estudo e fixação fora da sala de aula; nunca como escola paralela ou substituto da professora.
- **Hierarquia Cromática do Brand Book v3.1 (60/20/12/8):**
  - *Navy é território:* `#02060F` (60%) — Fundo escuro silencioso para estudo e foco noturno.
  - *Violet é sistema:* `#8B4DFF` (12%) — Cor primária (`PRIMARY`) para navegação, progresso e botões funcionais.
  - *Gold é sinal:* `#FFAB22` (8%) — Cor de acento (`ACCENT`) para conquistas, medalhas, atenção e CTAs primários.
  - *Superfície e Apoio:* Cream (`#F7F4EC`) e Slate (`#9EA2AE`) para leitura/bordas; Lilac (`#B28AFF`) para apoio (`SECONDARY`).
  - O antigo azul Sejong (`#004C97`) foi descontinuado e não deve ser reutilizado.
- **Invariantes e Proibições Visuais:**
  - É expressamente proibido inserir flores de cerejeira literais (🌸) na logo ou usar primavera como tema decorativo infantil; a primavera (*새봄*) é exclusivamente metáfora pedagógica de recomeço e florescimento.
  - Zero infantilização, estética caricata de K-pop ou promessas mágicas de fluência rápida.
  - Tipografia de interface sempre em Pretendard (prevenção absoluta de *tofu* `□□□□`) e caligrafia em Kyobo Handwriting 2025.

## Rigor Técnico e Epistêmico (Regra Inviolável)
- NUNCA emitir diagnósticos de viabilidade, arquitetura ou estimativas de complexidade baseados em inferência ou memória de sessões passadas.
- Qualquer afirmação sobre comportamento, limitações ou contratos de código DEVE ser verificável na sessão atual com leitura prévia e citação do trecho concreto que a sustenta.

## Convenções de Código e Commits
- Usar **Conventional Commits** em português/inglês técnico: `tipo(escopo): descrição`
  - Tipos válidos: `feat`, `fix`, `refactor`, `docs`, `ci`, `test`, `chore`, `perf`, `security`
- Branch naming: `feature/*`, `fix/*`, `security/*`, `docs/*`
- Nunca commitar credenciais padrão ou segredos no código-fonte. Usar variáveis de ambiente com postura **fail-closed**.

## Segurança (Regras Invioláveis)
- Comparação de segredos (PINs, tokens, recovery keys) SEMPRE via `hmac.compare_digest`.
- Identificadores públicos (student_id) NUNCA devem servir como credencial de autorização.
- `assets/` é estritamente read-only. Dados mutáveis vão para `data/` (cache, sessions, telemetry, reports).
- O `.gitignore` DEVE proteger `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/cache/`, `*.jsonl`.
- **Auditoria Contínua da Linhagem de Segurança:** Antes de concluir qualquer merge em `develop` ou `main`, o agente DEVE verificar formalmente se a linhagem de segurança permanece preservada (`git merge-base --is-ancestor security/hardening-v0.3.2 HEAD`) e executar a bateria dedicada de testes de segurança (`test_admin_auth_hardening.py`, `test_student_identity_security.py`, `test_telemetry_privacy_and_rotation.py` e `test_p4_admin_security_barrier`) com 100% de aprovação.

## Arquitetura Flet & Flutter Engine
- **Prevenção de Tela Preta e Resolução de Assets Web:** Todos os caminhos de imagens passados a `ft.Image(src=...)` DEVEM começar obrigatoriamente com barra inicial `/` (ex: `/branding/app_icon_512.png`), nunca com caminho relativo. Caminhos relativos causam HTTP 404 em rotas aninhadas do Flutter Web (`/splash`, `/onboarding`, `/home`), colapsando o pipeline de renderização do CanvasKit ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Transição Atômica de Views no Router:** No roteador (`Router`), NUNCA limpar `page.views` (`page.views.clear()`) antes que o construtor da nova view retorne com sucesso. Se ocorrer exceção no construtor da view, `page.views` ficaria com 0 elementos, gerando tela preta absoluta. Manter a view anterior ou prover uma view de fallback de emergência ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Timeouts Estritos em Chamadas Assíncronas de Serviços:** Métodos assíncronos de serviços acoplados ao Flet (ex: `SharedPreferences.get`, bridges de runtime) invocados no ciclo de vida de carregamento de tela DEVEM possuir timeout explícito via `asyncio.wait_for(..., timeout=0.8)` para prevenir que a tela fique congelada indefinidamente caso o cliente Web não responda ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Preservação de Deep Links Web e Rota Inicial:** No `main.py`, NUNCA forçar navegação estática para `/splash` sem inspecionar `page.route`. O entrypoint DEVE respeitar `initial_route = getattr(page, "route", None) or "/splash"`. Forçar rota fixa sobrescreve a URL requisitada pelo navegador e redireciona qualquer deep link (`/admin`, `/hangul`) para o Onboarding.
- **Renderização Centralizada de Rotas (`Router`):** O roteador DEVE implementar um método `render_route(route: str)` desacoplado de instâncias de `ft.RouteChangeEvent` (cujo construtor requer parâmetros internos de controle no Flet 0.85+). No `navigate_to`, só disparar nova montagem se `page.views[-1].route != route_name`, prevenindo duplicação desnecessária de `page.update()`.
- **Inspeção Estática de Telas Transientes (`/splash?no_redirect=1`):** Views com temporizadores assíncronos de transição automática DEVEM checar a presença de parâmetros de auditoria (ex: `no_redirect` na URL) antes de disparar redirects, permitindo auditorias visuais completas sem fechamento prematuro da tela.
- **Opacidade de Cores no Padrão do Flutter Engine:** NUNCA concatenar valores de canal alfa ao final de strings hex (ex: `f"{colors['primary']}12"`), pois o Flutter interpreta 8 dígitos como `#AARRGGBB` e inverte as cores. Usar sempre a função canônica `ft.Colors.with_opacity(opacity, color)` ([`BUG-03`](Documentacao/Bugs_Criticos/bug_03_inversao_hex_alpha_aarrggbb_flet_flutter.md), [`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Alocação de Memória e Re-renders:** NUNCA recriar instâncias de `ft.BoxShadow`, paletas de cores ou sombras complexas dentro de métodos ou loops de renderização. Reaproveitar sempre as constantes estáticas centralizadas em `Styles` e `Tokens` de `src/theme.py` ([`BUG-05`](Documentacao/Bugs_Criticos/bug_05_w_ampa_simulador_neuromorfico_e_performance.md)).
- **Sintaxe e Enums Canônicos do Flet 0.85+:**
  - Ajustes de imagem: utilizar `ft.BoxFit.CONTAIN` / `ft.BoxFit.COVER`; `ft.ImageFit` foi descontinuado ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
  - Espaçamento de texto: utilizar exclusivamente `style=ft.TextStyle(letter_spacing=...)` em `ft.Text`; o kwarg direto `letter_spacing` foi descontinuado ([`BUG-02`](Documentacao/Bugs_Criticos/bug_02_sintaxe_flet_085_letter_spacing_e_button_args.md)).
  - Botões: texto deve ser passado como argumento posicional (`ft.Button("Texto", ...)`) ou `content=ft.Text(...)`, nunca como argumento nomeado `text=` ([`BUG-02`](Documentacao/Bugs_Criticos/bug_02_sintaxe_flet_085_letter_spacing_e_button_args.md)).
- **Hierarquia de Layout e Scroll em Views:**
  - Em telas principais, utilizar `scroll=ft.ScrollMode.AUTO` e `appbar=...` diretamente no construtor `ft.View(...)`.
  - NUNCA aninhar `ft.ListView` dentro de `ft.View.controls` sem definir `expand=True`, pois isso colapsa a altura do viewport e trava a rolagem ([`BUG-04`](Documentacao/Bugs_Criticos/bug_04_bloqueio_de_scroll_listview_e_appbar.md)).
- **Gesture Arena & Scroll:** NUNCA alterar dinamicamente propriedades de scroll (`Column.scroll = None`) durante eventos de toque/arrasto. A troca destrói o `RenderViewport` e reseta o scroll para o topo. Para captura de gestos contínuos de desenho em telas roláveis, adotar o padrão **Focus Mode** (prévia passiva na página e modal dedicado sem scroll para interação), conforme catalogado em [`BUG-10`](Documentacao/Bugs_Criticos/bug_10_disputa_gesture_arena_e_calibracao_iou_caligrafia.md).
- **Proporção e Z-Index no Canvas:** Manter fonte, proporção de escala e alinhamento do modelo guia estritamente idênticos aos do gabarito de avaliação (escala $0.68$), e renderizar camadas de diagnóstico (overlays) no topo da tinta desenhada ([`BUG-10`](Documentacao/Bugs_Criticos/bug_10_disputa_gesture_arena_e_calibracao_iou_caligrafia.md)).
- **Updates Defensivos em Widgets:** Em código novo ou refatorado, proteger chamadas `self.update()` com `try ... except Exception: pass` para garantir testabilidade unitária headless sem dependência de ciclo de vida de `page`.
  - *Retrofit concluído (v0.3.6):* `quiz_widget.py`, `flashcard_widget.py`, `hangul_card.py`, `vocab_card.py` 100% protegidos.
- **Propriedade Somente-Leitura `page` em Controles Flet:** Em subclasses de `ft.Control` (como `ft.Container`, `ft.Column`), NUNCA tentar sobrescrever `self.page = page`. A propriedade `page` é um getter somente leitura gerenciado pelo framework e lançará `AttributeError`. Armazenar sempre referências manuais em atributos privados protegidos (ex: `self._page = page`).

## Áudio & Autoplay no Navegador (Web & Mobile PWA)
- **Player Singleton Centralizado:** NUNCA instanciar `ft.Audio()` diretamente dentro do método de construção de uma `View` individual. O ciclo de vida do player deve ser gerenciado exclusivamente pelo serviço global `page.audio_service` e anexado a `page.overlay` ([`BUG-01`](Documentacao/Bugs_Criticos/bug_01_flet_audio_corridas_e_page_services.md)).
- **Destravamento de Autoplay na Web:** Em ambiente navegador (PWA/Web), a política de autoplay bloqueia áudio invocado assincronamente. O `AudioService` DEVE pré-montar na inicialização um elemento mudo com `src="silent.wav"` (`volume=0.0`, `autoplay=True`) na raiz de `assets/` para desbloquear a reprodução da sessão, e NUNCA destruir o player único durante transições de rota ([`BUG-08`](Documentacao/Bugs_Criticos/bug_08_politica_autoplay_navegador_e_silent_wav.md)).

## Tipografia & Prevenção de Tofu
- **Tema Global com Cobertura CJK Unificada:** NUNCA definir uma fonte exclusivamente latina (ex: `Inter`) como `font_family` padrão do tema global (`page.theme`). O tema deve utilizar fontes unificadas com suporte integral a caracteres Hangul (U+AC00 a U+D7A3), sendo **Pretendard** a fonte primária oficial da interface (prevenção absoluta de *tofu* `□□□□`) e **Kyobo Handwriting 2025** para exercícios caligráficos ([`BUG-07`](Documentacao/Bugs_Criticos/bug_07_flutter_font_fallback_tofu_hangul.md)).

## Rede e Inicialização do Servidor
- **Binding de Rede Local no Windows:** Para desenvolvimento local em ambiente Windows, o host do servidor Flet DEVE ser configurado como `127.0.0.1` (localhost). O IP `0.0.0.0` e wildcard `*` falham no Winsock do Windows e quebram a abertura automática do navegador com `ERR_ADDRESS_INVALID` ou `getaddrinfo failed`. O bind em `0.0.0.0` é reservado exclusivamente para deploy em containers em nuvem (`PORT` presente no ambiente) ([`BUG-06`](Documentacao/Bugs_Criticos/bug_06_bind_windows_flet_server_ip.md)).

## Modelagem e Contratos (Quiz Engine)
- Todo novo tipo de questão em `QuizQuestion` DEVE implementar validador `@model_validator(mode="after")` com postura **fail-closed**, rejeitando metadados ausentes, nulos ou fora do contrato antes que qualquer elemento chegue à UI (padrão `validate_sov_metadata` e `validate_calligraphy_metadata`).

## Conformidade Curricular com os Gabaritos Oficiais (Sejong 1A e 1B)
- **Fidelidade ao Material Oficial (국립국어원):** Todos os exercícios de caligrafia nos workbooks DEVEM ser derivados estritamente dos gabaritos e atividades do *Sejong Korean Workbook* (1A e 1B).
- **Workbooks 1A:** Foco em combinações léxicas e conjugações fundamentais do gabarito oficial (ex: `자전거를 타요`, `밥을 먹어요`, `쉬었어요`, `가고 싶어요`).
- **Workbooks 1B:** Foco em estruturas gramaticais com conectivos, negação e futuro do gabarito oficial (ex: `농구를 자주 해요`, `옷을 못 입어요`, `커피를 좋아해서`, `살 거예요`).
- **Regra de 띄어쓰기:** Frases e expressões de 2 ou mais palavras DEVEM respeitar o espaçamento oficial coreano, reservando células em branco no 원고지.
- **Gatilho de Avaliação:** Em todas as unidades de ambos os livros, a avaliação é acionada exclusivamente pelo botão **"✅ Terminei"**.

## Documentação Oficial — Sincronização Obrigatória
Ao concluir qualquer alteração significativa (feature, bugfix, security, refactor), o agente DEVE atualizar:
1. **`Documentacao/Changelogs_e_Historico/CHANGELOG.md`** — Adicionar entrada de release com seções Added/Fixed/Security/Changed conforme [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).
2. **`Documentacao/Bugs_Criticos/INDICE_BUGS.md`** — Se um bug foi corrigido, adicionar a entrada na tabela com severidade, categoria e link.
3. **`Documentacao/Bugs_Criticos/bug_XX_*.md`** — Para bugs complexos, criar arquivo dedicado com: Diagnóstico, Causa Raiz, Código Antes/Depois, Regras Preventivas.
4. **`Documentacao/INDICE_DOCUMENTACAO.md`** — Atualizar o índice mestre se novos documentos foram criados.
5. **Nunca esperar o usuário perguntar "está documentado?"** — a documentação é parte integrante da entrega.
6. **Caminhos de Mídias em Markdown (Windows):** Em toda documentação e artefatos, links de imagens locais DEVEM utilizar exclusivamente barras normais `/` (ex: `C:/Users/.../imagem.png`). Contrabarras `\` são tratadas como escape por navegadores e quebram a renderização.

## Testes
- Toda alteração de código deve ser acompanhada de testes automatizados em `tests/`.
- Ao finalizar uma branch, executar `pytest tests/ -v` e confirmar 100% de aprovação antes de commitar documentação ou solicitar merge.
- O CI (`.github/workflows/ci.yml`) valida: compileall, secret scanning e pytest.
- **Testes E2E e Renderização Web (Playwright):** Para alterações críticas que envolvam o ciclo de vida do Flutter Web (CanvasKit, rotas de View, `AudioService` autoplay com `silent.wav`, ou canvas de caligrafia no 원고지), utilizar testes automatizados ponta a ponta via Playwright (`tests/e2e/` ou `tests/test_playwright_e2e.py`) para garantir ausência de tela preta (`BUG-11`), desbloqueio de áudio (`BUG-08`) e prevenção visual de tofu em caracteres Hangul (`BUG-07`).
- **Subprocesso Flet para Testes E2E:** O servidor Flet Web NUNCA deve ser executado em `threading.Thread` em fixtures de teste (conflito com `signal.signal` da thread principal). O servidor DEVE ser disparado via `subprocess.Popen([sys.executable, "main.py"], env=env)` com `FLET_FORCE_WEB_SERVER="true"`, `PORT=<porta_dinamica>`, `FLET_SERVER_IP="127.0.0.1"` e encerrado no teardown via `proc.terminate()` e `proc.wait()`.
- **Prevenção de Deadlock de Buffer em Subprocessos (Windows NT):** Em fixtures de teste com `subprocess.Popen`, NUNCA utilizar `stdout=subprocess.PIPE, stderr=subprocess.PIPE` sem drenagem concorrente ativa em threads separadas. No Windows, o esgotamento do buffer de pipe anônimo (~4KB a 64KB) pelos logs do servidor trava irreversivelmente o processo filho em operações subsequentes. Utilizar obrigatoriamente `stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL` ([`BUG-12`](Documentacao/Bugs_Criticos/bug_12_deadlock_pipe_anonimo_windows_playwright_e2e.md)).
- **Auditoria de Unicidade Visual em Testes Playwright:** Testes E2E de navegador NUNCA devem assumir que uma view foi renderizada corretamente apenas verificando luminância acima de preto puro. A suíte DEVE verificar seletores exclusivos ou auditar a unicidade de hashes MD5 entre screenshots de rotas distintas para prevenir falsos positivos por telas colapsadas na mesma rota.

