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

## Arquitetura Flet & Flutter Engine
- **Prevenção de Tela Preta e Resolução de Assets Web:** Todos os caminhos de imagens passados a `ft.Image(src=...)` DEVEM começar obrigatoriamente com barra inicial `/` (ex: `/branding/app_icon_512.png`), nunca com caminho relativo. Caminhos relativos causam HTTP 404 em rotas aninhadas do Flutter Web (`/splash`, `/onboarding`, `/home`), colapsando o pipeline de renderização do CanvasKit ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Transição Atômica de Views no Router:** No roteador (`Router`), NUNCA limpar `page.views` (`page.views.clear()`) antes que o construtor da nova view retorne com sucesso. Se ocorrer exceção no construtor da view, `page.views` ficaria com 0 elementos, gerando tela preta absoluta. Manter a view anterior ou prover uma view de fallback de emergência ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Timeouts Estritos em Chamadas Assíncronas de Serviços:** Métodos assíncronos de serviços acoplados ao Flet (ex: `SharedPreferences.get`, bridges de runtime) invocados no ciclo de vida de carregamento de tela DEVEM possuir timeout explícito via `asyncio.wait_for(..., timeout=0.8)` para prevenir que a tela fique congelada indefinidamente caso o cliente Web não responda ([`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Opacidade de Cores no Padrão do Flutter Engine:** NUNCA concatenar valores de canal alfa ao final de strings hex (ex: `f"{colors['primary']}12"`), pois o Flutter interpreta 8 dígitos como `#AARRGGBB` e inverte as cores. Usar sempre a função canônica `ft.Colors.with_opacity(opacity, color)` ([`BUG-03`](Documentacao/Bugs_Criticos/bug_03_inversao_hex_alpha_aarrggbb_flet_flutter.md), [`BUG-11`](Documentacao/Bugs_Criticos/bug_11_tela_preta_flutter_web_assets_e_views_router.md)).
- **Enums Canônicos do Flet 0.85+:** Em ajustes de imagem, utilizar `ft.BoxFit.CONTAIN` / `ft.BoxFit.COVER`; o antigo `ft.ImageFit` foi descontinuado e não existe no runtime moderno.
- **Gesture Arena & Scroll:** NUNCA alterar dinamicamente propriedades de scroll (`Column.scroll = None`) durante eventos de toque/arrasto. A troca destrói o `RenderViewport` e reseta o scroll para o topo. Para captura de gestos contínuos de desenho em telas roláveis, adotar o padrão **Focus Mode** (prévia passiva na página e modal dedicado sem scroll para interação), conforme catalogado em [`BUG-10`](Documentacao/Bugs_Criticos/bug_10_disputa_gesture_arena_e_calibracao_iou_caligrafia.md).
- **Proporção e Z-Index no Canvas:** Manter fonte, proporção de escala e alinhamento do modelo guia estritamente idênticos aos do gabarito de avaliação (ex: escala $0.68$), e renderizar camadas de diagnóstico (overlays) no topo da tinta desenhada ([`BUG-10`](Documentacao/Bugs_Criticos/bug_10_disputa_gesture_arena_e_calibracao_iou_caligrafia.md)).
- **Updates Defensivos em Widgets:** Em código novo ou refatorado, proteger chamadas `self.update()` com `try ... except Exception: pass` para garantir testabilidade unitária headless sem dependência de ciclo de vida de `page`.
  - *Fila de Retrofit pendente:* `quiz_widget.py`, `flashcard_widget.py`, `hangul_card.py`, `vocab_card.py`.

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

## Testes
- Toda alteração de código deve ser acompanhada de testes automatizados em `tests/`.
- Ao finalizar uma branch, executar `pytest tests/ -v` e confirmar 100% de aprovação antes de commitar documentação ou solicitar merge.
- O CI (`.github/workflows/ci.yml`) valida: compileall, secret scanning e pytest.
