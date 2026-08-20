# Changelog — Sejong Companion

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## Ciclo de Vida do Projeto

```
Pré-Alpha → Alpha → Beta → RC → RTM → GA
               ▲
          ESTAMOS AQUI
          v0.3.1-alpha
```

| Fase | Versão Alvo | Critérios de Entrada |
|------|-------------|----------------------|
| **Alpha** (atual) | `0.3.1-alpha` | Livro Sejong 1A (11 unidades) + Livro Sejong 1B (12 unidades), 79 Testes Automatizados, HLR SRS, Lab Fonético, Drag & Drop SOV |
| **Beta** | `0.6.0-beta` | Sincronização Cloud, Banco de dados persistente, PWA Mobile Audit, modo offline |
| **RC** | `1.0.0-rc.1` | Feature-complete, testes E2E, zero bugs críticos |
| **GA** | `1.0.0` | Pronto para distribuição pública |

---

## [0.3.1-alpha] — 2026-08-20

### Classificação: Alpha
> Milestone de Expansão Curricular: Integração Integral do Livro Sejong Hakdang 1B e Workbook 1B (12 novas unidades temáticas: `unit_1b_01` a `unit_1b_12`), Desafios Sintáticos SOV com papéis semânticos, Cadeia Contínua de Desbloqueio $1A \rightarrow 1B$, Seções Visuais de Livro na Home e Suíte Expandida para 79 Testes Automatizados.

### Added — Features
- **Currículo Sejong 1B Completo (12 Unidades)** — Implementação completa dos arquivos `unit_1b_01.json` a `unit_1b_12.json` baseados no currículo oficial do King Sejong Institute 1B:
  - `unit_1b_01`: 무슨 음식을 좋아해요? (Comida, 무슨, 못)
  - `unit_1b_02`: 도서관에 책을 빌리러 가요 (Hobbies, -(으)러 가다/오다, 도)
  - `unit_1b_03`: 백화점에서 쇼핑할 거예요 (Compras, -아서/어서 [motivo], -(으)ㄹ 거예요 [futuro])
  - `unit_1b_04`: 더 큰 사이즈는 없어요? (Adjetivos, -(으)ㄴ + N, -습니다/ㅂ니다)
  - `unit_1b_05`: 세종식당이 어디에 있어요? (Direções, 의문사 어디, (으)로)
  - `unit_1b_06`: 한국미술관까지 어떻게 가요? (Transportes, ~에서 ~까지, -아요/어요 [sugestão])
  - `unit_1b_07`: 제주도에 가려고 해요 (Viagem, -(으)려고 하다, -고)
  - `unit_1b_08`: 지난번 여행보다 좋았어요 (Experiências, -(으)ㄴ 후에, 보다)
  - `unit_1b_09`: 집에서 푹 쉬어야 돼요 (Saúde, -지만, -아야/어야 되다)
  - `unit_1b_10`: 학교에 가기 전에 수영을 해요 (Rotina Saudável, -기 전에, -아서/어서 [sequência])
  - `unit_1b_11`: 한국 음식을 만들 수 있어요? (Encontros, -(으)ㄹ 수 있다/없다, -고 있다)
  - `unit_1b_12`: 저는 지니 씨에게 펜을 선물할 거예요 (Presentes, 에게/한테, -(으)니까)
- **Cadeia de Desbloqueio Expandida ($1A \rightarrow 1B$)** — Conexão contínua da progressão de `unit_10` para `unit_1b_01` até `unit_1b_12` no `ProgressService._UNLOCK_CHAIN`.
- **Organização Visual da Home por Livro Didático** — Divisores de seção para `Sejong Coreano 1A` e `Sejong Coreano 1B`, com badges compactas e orbes de retenção SRS individuais para todas as 23 unidades.
- **Expansão do Banco de Flashcards e Desafios SOV** — `DataService.get_all_flashcards()` e `get_sentence_builder_challenges()` agora incorporam organicamente todo o vocabulário e exercícios do 1B.
- **Portal Pedagógico & Dashboard de Administração (`/admin`)** — Acesso protegido por PIN institucional (`AdminService`) com compilação de KPIs multi-student, diagnóstico pedagógico de taxas de erro por questão, funil de abandono de lições, vocabulário crítico e roster individual de todos os `Student IDs` com exportação de relatórios em Markdown.

### Added — Suíte de Testes
- **84 Testes Automatizados (100% OK)** — Inclusão de `tests/test_unit_1b_content.py` e `tests/test_admin_service.py` validando os 12 arquivos do 1B, autenticação de administrador, varredura de sessões em disco, resiliência a arquivos corrompidos e compatibilidade curricular integral (23 unidades).

---

## [0.3.0-alpha] — 2026-08-14

### Classificação: Alpha
> Milestone de Conteúdo & Inteligência de Memória: Currículo completo do Sejong Korean 1A (Unidades 01 a 10), Algoritmo HLR de Ebbinghaus, Laboratório Fonético Oclusivo, Mecânica Drag & Drop SOV Semântica com Rejeição Elástica em Tempo Real, Active Recall Dashboard e Flashcards Gamificados com Criador de Frases.

### Added — Features
- **Currículo Sejong 1A Completo (10 Unidades)** — Criadas as unidades didáticas `unit_02.json` até `unit_10.json` com vocabulário, gramática formatada em Markdown, dicas lusófonas e exercícios interativos.
- **Política Estrita Zero Romanização** — Todo o conteúdo coreano padronizado exclusivamente em 한글, eliminando muletas de romanização.
- **Motor Matemático HLR SRS (Half-Life Regression de Ebbinghaus)** — Retenção calculada via $R = 2^{-t / h}$, com recálculo dinâmico de meia-vida no Active Recall com base em acurácia e tempo de resposta.
- **Orbes de Vitalidade SRS na Home** — Indicadores visuais nos cartões de unidade para memorização Alta ($\ge 75\%$), Média ($35\%-75\%$) e Baixa/Urgente ($< 35\%$).
- **Cadeia de Desbloqueio Progressivo de 10 Unidades** — Expansão do fluxo didático contínuo de `unit_intro` até `unit_10` com persistência atômica.
- **Laboratório Fonético Oclusivo** — Componente `oclusive_lab.py` na aba de Consoantes para as 4 tríades (ㄱ/ㅋ/ㄲ, ㄷ/ㅌ/ㄸ, ㅂ/ㅍ/ㅃ, ㅈ/ㅊ/ㅉ) com feedback visual por cor e pronúncia em áudio HD.
- **Drag & Drop Sintático SOV Semântico com Rejeição Elástica em Tempo Real** — Slots semânticos (`주어`, `목적어`, `동사`, `장소`, `서술어`) com validação de papéis no ato do drop. Ao soltar no slot incorreto, ocorre *shake* elástico oscilatório (`-0.04 → +0.04 → 0.0`), alerta visual e devolução imediata da palavra ao pool sem bloquear a questão.
- **Active Recall Dashboard / Revisão do Dia (`/review`)** — Rota e tela dedicada de revisão com agregação inteligente de itens com retenção $R < 75\%$, autoavaliação (Errei / Bom / Fácil), streaks diários (🔥) e ganho de XP.
- **Flashcards Gamificados & Sentence Builder (`/flashcards`)** — Hub com 3 níveis de dificuldade (Fácil, Médio, Difícil), flip cards táteis com pronúncia em áudio HD e módulo criador de frases com validação sintática imediata.
- **Padronização de Layout Dead-Center** — Componente `centered_content` garantindo alinhamento central absoluto em telas widescreen e ultra-wide.

- **Sistema de Evidência Pedagógica & Telemetria Local (`TelemetryService`)** — Registro append-only JSONL de interações didáticas (respostas a questões com cronometragem, avaliações no Active Recall, aberturas/conclusões de lições) com zero PII e CLI `scripts.pedagogical_report` para diagnóstico pedagógico.

- **Identidade Persistente do Aluno (`Persistent Student ID`)** — Integração nativa com `page.client_storage` (localStorage / SharedPreferences), garantindo que fechar e reabrir o navegador/app preserva o mesmo perfil de estudante, progresso, streak e nós de retenção sem exigir login em servidor.
- **Backup e Restauração de Perfil (`export_backup` / `import_backup`)** — Suporte a exportação e importação do progresso integral do aluno em formato JSON portátil.

### Added — Suíte de Testes
- **74 Testes Automatizados (100% OK)** — Suíte completa cobrindo carregamento das 11 unidades (`test_data_service.py`), estabilidade da meia-vida, cadeia de desbloqueio, identidade persistente via client_storage e backup JSON (`test_progress_service.py`), contratos semânticos de SOV (`test_sov_drag_drop.py`), agregação SRS e classificação de flashcards (`test_active_recall.py`), pré-aquecimento e resiliência de cache de áudio (`test_audio_prewarm.py`, `test_audio_service.py`), roteamento de views (`test_router.py`), validação de conteúdo de quizzes (`test_workbook_quiz_content.py`) e telemetria pedagógica append-only com diagnósticos analíticos (`test_telemetry_service.py`).

### Added — Governança e Arquitetura
- **ADR-001 (Motor Adaptativo Local vs. IA Generativa)** — Registro formal da decisão de adotar IA Simbólica / Cognitive Learning Engine determinístico local, com desacoplamento dos 4 pilares: Completion, Mastery, Retention e Confidence.
- **Nó Conceitual Learning Engine** — Documentação do Grafo de Conceitos (Learning Graph) do Sejong 1A e árvore de decisão pedagógica determinística.

### Current Known Limitations (Alpha)
- **Persistência por Sessão Local:** O armazenamento atual opera em `data/sessions/{uuid}.json` (isolamento por aba/conexão local), devendo evoluir para persistência de conta de usuário em banco de dados na fase Beta (`0.6.0-beta`).
- **Modelo de Retenção Heurístico:** O algoritmo atual é uma modelagem heurística de decaimento temporal com multiplicadores fixos, aguardando dados anônimos de interação real para calibração estatística fina.
- **Testes E2E Automatizados:** Cobertura focada em regras de domínio e serviços Python; testes ponta-a-ponta na UI Flutter ainda dependem de validação manual via walkthrough.

---

## [0.2.0-alpha] — 2026-08-11

### Classificação: Alpha
> Milestone de Arquitetura & Isolamento Multi-Sessão: Persistência atômica por sessão, neuro-dicas de cronobiologia e modo Fullscreen/PWA.

### Added — Features
- **Isolamento de Sessão Web / Multi-User** — Cada aba/conexão do navegador recebe um UUID próprio (`data/sessions/{uuid}.json`), evitando conflito de progresso entre usuários simultâneos.
- **Cronobiologia Adaptativa (Neuro-Tips)** — Card dinâmico na Home com recomendações de estudo personalizadas de acordo com o horário do dia (manhã, tarde, noite).
- **Serviço de Tela Cheia (FullscreenService)** — Suporte a alternância de tela cheia via Flet e injeção de viewport mobile/PWA para Web.
- **Tokens Semânticos de Papel Sintático** — Cores dedicadas para Sujeito (`#3B82F6`), Objeto (`#10B981`), Verbo (`#8B5CF6`) e Partícula (`#F59E0B`).

---

## [0.1.0-alpha] — 2026-07-23

### Classificação: Alpha
> Software funcional com features core implementadas, testado internamente.
> Incompleto: faltavam unidades curriculares (criadas na v0.3.0), persistência real e responsividade mobile.

### Added — Features
- **Serviço de Áudio TTS Offline-First** — Typecast.ai (primário) + Google TTS (fallback), cache atômico em disco, autoplay unlock para navegadores
- **Design System Completo** — Escalas de cor (50→950) portadas de Next.js/shadcn/ui, tema claro/escuro com toggle instantâneo
- **Módulo Hangul (Unit Intro)** — 4 abas (Vogais, Consoantes, 받침, Sílabas), HangulCard com flip + hover + áudio
- **Módulo de Lições (Unit 01)** — Vocabulário, Gramática, Notas Culturais com VocabCard interativo
- **Motor de Quiz Unificado** — Multiple choice + order_words (SOV), tela de resultados com placar
- **Dashboard Home** — Grade curricular, progresso geral, painel de cronobiologia adaptativo
- **Router SPA** — Navegação por builder functions, fallback, estado de unidade
- **Persistência Real em Disco** — `ProgressService` com gravação atômica em `data/user_progress.json`, mantendo o progresso e desbloqueio curricular mesmo após reinicialização do app/servidor
- **Pedagogia Neuro-Linguística** — Anti-romanização, alerta "i fantasma" (epêntese lusófona), dicas mnemônicas, neuro-tips por vocabulário
- **Suíte TDD** — 25 testes unitários (audio, data, progress com persistência, router) com mocks Flet

### Added — Infra
- `requirements.txt` — flet==0.85.3, pydantic>=2.0.0, requests>=2.34.2, flet-audio==0.85.3
- `.env` — API key Typecast (gitignored)
- `.gitignore`
- `DESIGN_SYSTEM_CHANGELOG.md` — Registro de decisões de portabilidade visual

### Fixed — Bugs Resolvidos
- `Unknown control: Audio` + loop de reinício desktop (player movido para atributo do AudioService)
- `RuntimeError: Session closed` em callbacks assíncronos (try-except em splash e router)
- `OSError [10048]` port bind (documentação + instruções de taskkill)
- `Container must be added to page first` no Quiz (flag view_mounted)
- `Tab.__init__() unexpected keyword 'text'` (corrigido para `label=`)
- `Button.__init__() unexpected keyword 'text'` (corrigido para `content=`)
- `ERR_ADDRESS_INVALID` ao iniciar navegador (host 127.0.0.1 + FLET_SERVER_IP 0.0.0.0)
- Toggle claro/escuro sem efeito instantâneo (reconstrução in-place da view)
- Autoplay bloqueado pelo Chrome/Edge (silent.wav mudo no init)
- `min_height=` removido do Flet 0.85 (substituído por padding)
- Perda de progresso ao reiniciar o app/servidor (migrado de memória pura para persistência atômica em disco)
