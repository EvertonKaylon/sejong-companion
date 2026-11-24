# Changelog — Saebom Companion

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## Ciclo de Vida do Projeto

```text
Pré-Alpha → Alpha → Beta → RC → RTM → GA
               ▲
          ESTAMOS AQUI
          v0.3.9-alpha
```

| Fase | Versão Alvo | Critérios de Entrada |
|------|-------------|----------------------|
| **Alpha** (atual) | `0.3.9-alpha` | Fechamento BUG-13 (Caddy CSP/HSTS, Named Volumes UID 10001), P0/P1 Estabilização, CI Playwright & 473 Testes + 21 subtestes (100% OK) |
| **Beta** | `0.6.0-beta` | Sincronização Cloud, Banco de dados persistente, PWA Mobile Audit, modo offline |
| **RC** | `1.0.0-rc.1` | Feature-complete, testes E2E, zero bugs críticos |
| **GA** | `1.0.0` | Pronto para distribuição pública |

## [0.3.9-alpha] — 2026-11-24

### Classificação: Alpha (Fechamento de Segurança de Produção, Estabilização P0/P1, CI Playwright & Saneamento Documental)
> Milestone de Fechamento e Endurecimento de Release: Integração da branch `origin/main` (`9dafd2f` — `README.md`) sobre `security/mitre-owasp-hardening` na branch `fix/v0.3.9-hardening-and-cleanup`, resolução integral das 5 lacunas residuais de produção catalogadas no [`BUG-13`](../Bugs_Criticos/bug_13_hardening_owasp_mitre_container_caddy_auditoria.md), conclusão funcional de componentes interativos e serviços de áudio/identidade (P0/P1), ampliação do pipeline CI com job dedicado de Playwright Chromium (`e2e-playwright`), alinhamento unificado de versão para `0.3.9-alpha` e saneamento completo de branding e portabilidade de links na documentação oficial.

### Security & Infrastructure — Fechamento Integral do `BUG-13`
- **Separação HTTP/HTTPS e CSP Completa no Proxy (`Caddyfile:3-43`)** — Bloco `:80` isolado com `redir https://saebomcompanion.duckdns.org{uri} permanent` (sem emitir HSTS em HTTP plano, conformidade RFC 6797 §7.2); bloco HTTPS `saebomcompanion.duckdns.org` com HSTS exclusivo em TLS e `Content-Security-Policy` compatível com Flutter Web CanvasKit/Skwasm (`'wasm-unsafe-eval'`, `https://www.gstatic.com` em `script-src` e `connect-src`, `worker-src 'self' blob:`, `media-src 'self' data: blob:`).
- **Named Volumes Docker e Seed para `saebomuser` (`Dockerfile:33-38`, `docker-compose.yml:12-49`)** — Substituição dos bind mounts de host por named volumes (`saebom_audio_cache`, `saebom_sessions`, `saebom_telemetry`, `saebom_reports`, `saebom_announcements`) compatíveis com `UID/GID 10001`, cópia condicional de seed `announcements.json` no build, variável `SAEBOM_ANNOUNCEMENTS_PATH=/app/data/announcements/announcements.json` e restauração da checagem obrigatória fail-closed `SAEBOM_ADMIN_PIN=${SAEBOM_ADMIN_PIN:?SAEBOM_ADMIN_PIN environment variable is required}`.
- **Endurecimento de `.dockerignore` e Script OCI (`scripts/setup_oci_server.sh`)** — Inclusão de `Documentacao/`, `tests/`, `.agents/`, `audit_report.md` e `docs/` em `.dockerignore:53-58`; rebranding do script OCI para Saebom Companion (`REPO_DIR="$HOME/saebom-companion"`), remoção da abertura da porta `8554` no `iptables`, validação prévia obrigatória de `SAEBOM_ADMIN_PIN` no `.env` e URLs HTTPS.
- **Isolamento de `client_key` e Filtros Zero-PII no Admin (`src/views/admin_view.py:149-171`, `src/services.py:1622-1645`)** — Implementação de `_resolve_admin_client_key(page)` (`ip_` > `sess_` > `std_` > `anon_`) eliminando o balde global compartilhado `"admin_client"` em deep links `/admin`, e filtragem de `event_type != "security_audit"` em `AdminService.get_global_kpis()` e `get_pedagogical_diagnostics()`.
- **CI Ampliado com Playwright Chromium (`.github/workflows/ci.yml:1-85`)** — Workflow renomeado para `Saebom Companion CI & Security Gates`, secret scan ampliado (`src/ main.py scripts/ docker-compose.yml Caddyfile`), `SAEBOM_ADMIN_PIN` unificado nos dois jobs e novo job `e2e-playwright` (`chromium` via Playwright) após `test-and-security` (Python `3.11`/`3.12`).

### Fixed — Correções P0 & P1 na Aplicação
- **Eliminação de Vazamento Legado na Aba de Caligrafia (`src/views/hangul_view.py:630`)** — Substituição de `"세"` e `"종"` por `"새"` e `"봄"` nos botões rápidos (`sample_chars`), e conexão de `NumberTraining.on_complete` à reprodução de áudio (`L589`).
- **Transição Atômica no Rebuild do Admin (`src/views/admin_view.py:194-198`)** — `rebuild_view()` agora constrói `new_view = admin_view(page)` antes de executar `page.views.clear()` e `page.views.append(new_view)`.
- **Fontes 100% Locais (`src/theme.py:280-300`)** — Remoção das URLs externas do Google Fonts (`Noto Sans KR` e `Inter`), mantendo exclusivamente fontes locais em `assets/fonts/` (`Pretendard`, `Kyobo Handwriting 2025`, `Seollip-che`).
- **Conclusão Funcional de `SpatialStage` (`src/components/spatial_stage.py:105-245`, `src/views/lesson_view.py:250-264`)** — Inclusão de `self.object_container` dentro do `ft.Stack` em `_build_stage_canvas()`, movimentação animada via `POSITION_COORDS` em `select_position()`, botão `self.next_btn` (`Próximo Desafio →`) acionando `next_challenge()` com reset visual, e reprodução de `prompt_kr` via `on_challenge_completed` na `unit_03`.
- **Conclusão Funcional de `NumberTraining` (`src/components/number_training.py:24-48,176-282`)** — Adição de `"0": "영"` em `NATIVE_MAP`, suporte completo a numerais nativos compostos `10`–`99` em `_update_display()`, ação do botão `OK` no modo livre atualizando `feedback_text` e invocando `on_complete`, e atualização visual ativa em `set_system()`.
- **Resolução Web Dual no `AudioService` (`src/audio_service.py:27-35,98-123,292-332`)** — Adição de `get_bundled_assets_audio_dir()`, checagem combinada entre `data/cache/audio/` e `assets/audio_cache/`, e envio direto de `bytes` ao `flet_audio.Audio.src` quando o áudio existir apenas em `cache_dir` (`data/cache/audio/`), mantendo `assets/` estritamente *read-only*.
- **Persistência Unificada & Timeouts Assíncronos (`src/services.py:600-611`, `src/announcement_service.py:15-75`, `src/views/onboarding_view.py:75-78`, `src/views/home_view.py:173-174`)** — Remoção da definição duplicada de `ProgressService.set_student_name`, unificando canonicalização PascalCase e sincronização `saebom_student_name`/`sejong_student_name`; `AnnouncementService` com suporte a `SAEBOM_ANNOUNCEMENTS_PATH`, `threading.RLock()` e escrita atômica via temporário + `os.replace()` (fallback apenas em `errno.EBUSY`); e `asyncio.wait_for(..., timeout=0.8)` em `SharedPreferences.set()`.

### Changed & Docs — Bump `0.3.9-alpha`, `README.md` & Saneamento Documental P2
- **Bump Unificado para `0.3.9-alpha`** — Atualização síncrona em `src/__init__.py`, `src/components/whats_new_dialog.py`, `data/release_notes.json` (`release_date: "2026-11-24"`), `GEMINI.md` e `DESIGN.md`.
- **Integração e Rebranding de `README.md`** — Incorporado de `origin/main` (`9dafd2f`) e atualizado para **Saebom Companion (새봄 컴패니언) (`v0.3.9-alpha`)**, preservando o disclaimer pedagógico oficial (*Sejong Coreano 1A e 1B* / KSIF).
- **Atualização Integral de Documentação & Portabilidade de Links (`Documentacao/`)** — Rebranding e atualização de [`ROADMAP_MESTRE_COMPANION.md`](../Planos_e_Arquitetura/ROADMAP_MESTRE_COMPANION.md) (corrigindo numeração duplicada da Fase 4), [`estrategia_hospedagem_oci_always_free_vs_render.md`](../Planos_e_Arquitetura/estrategia_hospedagem_oci_always_free_vs_render.md), [`MANUAL_DE_IDENTIDADE_SAEBOM.md`](../Design_e_Branding/MANUAL_DE_IDENTIDADE_SAEBOM.md) (todos os 21 assets reais de `assets/branding/`), [`DESIGN_SYSTEM_CHANGELOG.md`](DESIGN_SYSTEM_CHANGELOG.md) (tipografia local da Rodada 4), todos os 10 documentos em [`Documentacao/Conceitos/`](../Conceitos/INDICE_CONCEITOS.md), arquivamento histórico de `audit_report.md` em [`audit_report_historico.md`](audit_report_historico.md) e conversão determinística de todos os links `file:///` para caminhos relativos POSIX portáteis.

### Métricas de Qualidade & Linhagem de Segurança
- **Total de Testes Globais:** **473 testes aprovados + 21 subtestes em `43.74s`** (incluindo todos os 5 cenários Playwright E2E no Chromium com `test_p4_admin_security_barrier`).
- **Bateria Dedicada de Segurança (`GEMINI.md`):** **25 testes aprovados em `1.15s`** (`test_admin_auth_hardening.py`, `test_student_identity_security.py`, `test_telemetry_privacy_and_rotation.py`, `test_infrastructure_security.py`).
- **Compileall & Secret Scan:** `compileall` exit code `0`; busca por `"sejong2026"` em `src/`, `main.py`, `scripts/`, `docker-compose.yml` e `Caddyfile` com **0 ocorrências**.
- **Validação de Links (`Documentacao/**/*.md`):** `FILE_URI_COUNT=0`, `BROKEN_LINKS=0`, `BACKSLASHES_IN_LINKS=0`, `ORPHAN_WIKILINKS=0`, `LINE_REF_ERRORS=0`.
- **Linhagem de Segurança Preservada:** `git merge-base --is-ancestor security/hardening-v0.3.2 HEAD` (exit code `0`).
- **Taxa de Falhas:** **0 falhas, 0 erros, 0 skipped, 0 warnings**.

## [0.3.8-alpha] — 2026-09-21

### Classificação: Alpha (Hardening Global de Infraestrutura e Aplicação — OWASP Top 10 & MITRE ATT&CK Enterprise)
> Milestone de Segurança e Conformidade Estrutural: Implementação de defesas em profundidade contra riscos do OWASP Top 10 (2021/2025) e táticas da Matriz MITRE ATT&CK Enterprise (TA0001 Reconnaissance, TA0004 Privilege Escalation, TA0005 Defense Evasion, TA0006 Credential Access, TA0009 Collection, TA0011 Command and Control). Hardening de containers eliminando execução como root (`Dockerfile` com usuário não-privilegiado `saebomuser` UID 10001 e `security_opt: [no-new-privileges:true]`), blindagem contra vazamento de credenciais e dados em build de imagens (`.dockerignore`), isolamento de proxy reverso (`Caddyfile`) com cabeçalhos de segurança defensivos (CSP inicial para Flet Web com `font-src 'self' data:;` e `https://unpkg.com` — com lacunas residuais de runtime em CanvasKit/Skwasm e `:80` documentadas em `BUG-13` —, HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff, supressão de Server banner), trilha estruturada de auditoria de autenticação com Zero PII (`AdminService.login` com logs de telemetria de segurança em falhas e lockouts), e sanitização defensiva de entrada no mural pedagógico (`AnnouncementService` com limites estritos de caracteres e expurgo de bytes nulos). Bateria de testes automatizados de segurança de infraestrutura integrada à suíte contínua.

### Security — Hardening OWASP Top 10 & MITRE ATT&CK
- **Blindagem de Build de Containers (`.dockerignore`)** — Prevenção de vazamento acidental de segredos locais (`.env*`), dados de sessões (`data/sessions/`), relatórios (`data/reports/`), telemetria (`data/telemetry/`), caches e arquivos PDF de referência durante a construção de imagens Docker (mitigação MITRE T1552.001 / OWASP A01 & A05).
- **Execução Não-Privilegiada no Dockerfile (`Dockerfile`)** — Criação de usuário de sistema e grupo dedicados (`saebomuser:saebom`, UID/GID 10001), concessão de permissões mínimas em `/app/data` e instrução `USER saebomuser`, impedindo fuga de container com privilégios de superusuário (mitigação MITRE T1611 / OWASP A05).
- **Proteção no Orquestrador (`docker-compose.yml`)** — Adição de `security_opt: [no-new-privileges:true]` para os serviços de aplicação e proxy Caddy, padronização estrita de variáveis de ambiente (`SAEBOM_ADMIN_PIN`) e volume persistente para `announcements.json`.
- **Cabeçalhos de Segurança Estritos no Proxy Reverso (`Caddyfile`)** — Inclusão de bloco de cabeçalhos de segurança OWASP:
  - `Content-Security-Policy`: Defesa contra XSS (OWASP A03 / MITRE T1059.007) configurada com `font-src 'self' data:;` (sem Google Fonts externas), WebSockets (`ws:` / `wss:`) e `script-src` com `https://unpkg.com`.
  - `X-Frame-Options: DENY`: Prevenção contra Clickjacking e iframing não autorizado (OWASP A05).
  - `X-Content-Type-Options: nosniff`: Prevenção de MIME-sniffing malicioso.
  - `Strict-Transport-Security`: Enforcing de HTTPS com max-age de 1 ano.
  - `Permissions-Policy`: Desativação de APIs sensíveis de hardware (câmera, microfone, geolocalização).
  - `-Server`: Ocultação do cabeçalho de identificação de versão do proxy (mitigação MITRE T1592 / OWASP A05).
- **Trilha de Auditoria Estruturada com Zero PII (`src/services.py`)** — `AdminService.login()` instrumentado para gerar eventos de telemetria de segurança (`security_audit`) em eventos de falha de autenticação (`login_failed`), bloqueio temporário (`lockout_tier1`) e bloqueio prolongado (`lockout_tier2`), isolados por `client_key` em sessões de auditoria, garantindo que nenhum segredo/PIN seja registrado em log (mitigação OWASP A09 / MITRE T1070).
- **Truncamento e Sanitização de Entrada no Mural Pedagógico (`src/announcement_service.py`)** — Aplicação de limites máximos de comprimento (`MAX_TITLE_LENGTH = 120`, `MAX_CONTENT_LENGTH = 1000`, `MAX_AUTHOR_LENGTH = 50`) e remoção preventiva de caracteres nulos (`\x00`), mitigando ataques de DoS por tamanho de payload, corrupção de JSON e exploração de parser (mitigação OWASP A03, A04 / MITRE T1499).
- **Suíte de Testes de Segurança de Infraestrutura (`tests/test_infrastructure_security.py`)** — 6 novos testes automatizados cobrindo `.dockerignore`, `Dockerfile` (usuário não-root), `Caddyfile` (cabeçalhos OWASP), `docker-compose.yml` (privilégios e volumes), trilha de auditoria e sanitização de dados.
- **Registro e Lacunas Residuais Abertas ([`BUG-13`](../Bugs_Criticos/bug_13_hardening_owasp_mitre_container_caddy_auditoria.md))** — Documentadas 5 pendências de runtime após `d6289d5`: (1) CSP em `Caddyfile:33` ainda omite `https://www.gstatic.com`, `worker-src 'self' blob:` e `'wasm-unsafe-eval'` necessários ao boot do CanvasKit/Skwasm sem `no_cdn=True` (além de `font-src 'self' data:` bloquear fallback `fonts.gstatic.com` e `src/theme.py:287-288` referenciar `fonts.googleapis.com`); (2) bloco único `:80, :443` emite HSTS em HTTP `:80` e desabilita redirect HTTP→HTTPS; (3) conflito entre `USER saebomuser` (UID `10001`) e bind mounts de host (`./data/*` e `./data/announcements.json`); (4) `client_key` global `"admin_client"` em deep links `/admin` e soma de eventos `security_audit` em `AdminService.get_global_kpis()`; (5) relaxamento para `${SAEBOM_ADMIN_PIN:-}` no `docker-compose.yml` e escrita direta `open("w")` em `AnnouncementService._save_announcements()`.

### Added — Ativação de Mecânicas de Neurociência nas Telas
- **Montagem da Fábrica de Sílabas e Teclado Numérico (Dialpad) na Tela de Hangul (`src/views/hangul_view.py`)** — Inserção ativa do `SyllableFactory` (com seletores táteis de 초성, 중성 e 종성, selo mecânico prateado de 받침 e reprodução de áudio) e do `NumberTraining` (Dialpad retrô 3x4 com alternância Sino-Coreano/Nativo, buffer e feedback imediato) dentro da aba de Sílabas.
- **Enriquecimento Tátil da Fábrica de Sílabas (`src/components/syllable_factory.py`)** — Adição de seletores interativos em chips coloridos com feedback visual do item selecionado e reprodução por clique.
- **Montagem do Diorama Espacial na Lição 03 (`src/views/lesson_view.py`)** — Inserção ativa do `SpatialStage` no topo da aba de gramática da Lição 03 ("제 가방은 책상 옆에 있어요") para treino visual de postposições espaciais coreanas (`위, 아래, 앞, 뒤, 옆`).
- **Testes Automatizados de Montagem em Views (`tests/test_views_rendering.py`)** — Novos testes validando a montagem funcional e navegação das novas ferramentas nas rotas `/hangul` e `/lesson`.

### Métricas de Qualidade & Linhagem de Segurança
- **Total de Testes Globais:** **459 testes aprovados + 21 subtestes** (454 unitários/integração + 5 Playwright E2E; executados em `34.76s`).
- **Bateria Dedicada de Segurança:** **19 testes aprovados** (`1.31s`) + `test_p4_admin_security_barrier` aprovado (`26.01s`).
- **Linhagem de Segurança Preservada:** `git merge-base --is-ancestor security/hardening-v0.3.2 HEAD` (exit code 0).
- **Taxa de Falhas:** **0 falhas, 0 erros, 0 skipped, 0 warnings**.
- **Nota de Versão em Código:** `src/__init__.py` (`__version__`) e `data/release_notes.json` ainda permanecem em `0.3.6-alpha` aguardando bump formal de release.

## [0.3.7-alpha] — 2026-09-21

### Classificação: Alpha (Sistema Integrado de Notificações Nativas Web/PWA e Desktop, Mural de Avisos da Professora, Badges Dinâmicos e Vínculo com WhatsNewDialog)
> Milestone de Notificações e Comunicação Pedagógica: Implementação unificada do serviço de notificações nativas do sistema operacional (`NotificationService`) via Web Notification API para navegadores/PWA (Windows Action Center, Central de Notificações do Android/macOS) com foco de janela, ícone oficial e fallback in-app garantido (`ft.SnackBar`) no padrão Brand Book v3.1. Criação do serviço de anúncios pedagógicos (`AnnouncementService`) com persistência atômica em `data/announcements.json` e transmissão em tempo real para múltiplos clientes conectados via barramento `page.pubsub`. Integração do "Soft Prompt" amigável na `HomeView` com persistência em `client_storage`, badges dourados dinâmicos no AppBar (`ft.Badge(small_size=8, bgcolor=colors["accent"])`), botão de acesso às Novidades da Versão no AppBar da tela `/admin`, e 3ª aba dedicada no painel pedagógico: **"📢 Mural de Avisos da Professora"** com formulário de envio, botão primário "📢 Notificar Turma", exclusão lógica e histórico ativo. Cobertura completa de testes automatizados elevando a suíte para **451+ testes (100% aprovados, 0 falhas, 0 erros)**.

### Added — Notificações Nativas & Mural Pedagógico
- **Serviço de Notificações Nativas (`src/notification_service.py`)** — Classe `NotificationService` provendo `request_permission()`, `send_native_notification()` e `show_in_app_banner()`. Suporte à Web Notification API com guards estritos (`page.web`) prevenindo crash em runtime desktop nativo, sanitização JSON de payloads e in-app SnackBar simultâneo.
- **Serviço de Comunicados & PubSub (`src/announcement_service.py`)** — Classe `AnnouncementService` gerenciando persistência de avisos em `data/announcements.json` (fora de `assets/`), transmissão em tempo real (`page.pubsub.send_all()`), contagem de não lidos com base em `last_read_announcement_id` e marcação coletiva de leitura.
- **Base de Avisos Inicial (`data/announcements.json`)** — Registro estruturado contendo comunicado inaugural de boas-vindas e incentivo ao estudo diário pela professora.
- **Soft Prompt de Notificações na Home (`src/views/home_view.py`)** — Card acolhedor solicitando autorização do usuário de forma não intrusiva com opções "Ativar Notificações" e "Agora não", persistindo decisão em `client_storage`.
- **Badges Visuais Dinâmicos no AppBar (`src/views/home_view.py`)** — Indicador dourado (`ft.Badge(small_size=8, bgcolor=colors["accent"])`) sobre o ícone `AUTO_AWESOME_ROUNDED` na Home ativado quando houver notas de versão novas ou avisos da professora não lidos.
- **Ouvinte em Tempo Real via PubSub (`src/views/home_view.py`)** — Escuta contínua de eventos `new_announcement` disparando notificações nativas imediatas e acendendo badges em todos os alunos com app aberto.
- **Aba "Mural de Avisos" no Painel Pedagógico (`src/views/admin_view.py`)** — 3ª aba no Segmented Tab Switcher do Admin (`tab_btn_announcements`) com formulário responsivo (título, mensagem multiline, botão primário "📢 Notificar Turma"), validação de campos, snackbars informativos e cards de avisos ativos com exclusão unitária.
- **Botão de Novidades no AppBar Admin (`src/views/admin_view.py`)** — Acesso direto ao `WhatsNewDialog` a partir da tela de administração docente com ícone `AUTO_AWESOME_ROUNDED` em cor Gold.
- **Destaque de Comunicados no WhatsNewDialog (`src/components/whats_new_dialog.py`)** — Exibição prioritária dos avisos ativos da professora em cartões Gold `#FFAB22` no topo do diálogo e marcação automática de leitura ao fechar o modal.
- **Bateria de Testes Automatizados (`tests/test_notification_and_announcements.py`)** — 10 novos testes cobrindo CRUD de anúncios, validação de campos, segurança desktop vs web, renderização no WhatsNewDialog, soft prompt na Home, badges dourados e abas no Admin.

### Changed — Expansão Curricular & Sincronização
- **Internacionalização Bilíngue (PT/KO)** — Adicionadas chaves de tradução no dicionário `ADMIN_I18N` para o Mural de Avisos, formulários, botões de ação e tooltips em Português e Coreano.
- **Release Notes Atualizadas (`data/release_notes.json`)** — Inclusão do card de destaque pedagógico "Mural de Avisos e Notificações do Sistema" no diálogo de boas-vindas.

### Fixed — Autenticação & Isolamento de Testes
- **Desbloqueio do Campo de PIN e Aviso de Configuração no Admin (`c7aa16e`, `src/views/admin_view.py`)** — Removido `disabled=not AdminService.is_configured()` de `pin_input` (`disabled=False`), mantendo o banner de erro visível com ícone `WARNING_AMBER_ROUNDED` e mensagens bilíngues `pin_unconfigured` / `pin_unconfigured_hint` em `ADMIN_I18N` (PT/KO) quando `SAEBOM_ADMIN_PIN` não está definido; isolamento explícito de `SAEBOM_ADMIN_PIN` nos fixtures de `tests/test_admin_auth_hardening.py` e `tests/test_admin_service.py`.

### Métricas de Qualidade & Testes
- **Total de Testes Globais:** **451 testes 100% aprovados** (441 anteriores + 10 novos testes de notificações e comunicados, além de 21 subtestes de unittest).
- **Linhagem de Segurança Preservada:** Auditoria formal `git merge-base --is-ancestor security/hardening-v0.3.2 HEAD` confirmada (código de saída 0).
- **Taxa de Falhas:** **0 falhas, 0 erros**.

## [0.3.6-alpha] — 2026-09-20 (Consolidação: Neurociência, WhatsNewDialog & BUG-12)

### Classificação: Alpha (Consolidação Arquitetural, Reconciliação de Neurociência, WhatsNewDialog e Estabilização de Produção)
> Milestone de Unificação e Estabilização Final: Reconciliação completa da branch `feature/neuroscience-gap-closure` sobre a linha estável `feature/branding`, integrando 6 novos módulos neuropedagógicos, 11 assets vetoriais de física articulatória e relações espaciais com prefixo `/` absoluto para compatibilidade CanvasKit (BUG-11), implementação do componente pedagógico "Novidades do Saebom" (`WhatsNewDialog`) com persistência inteligente via `client_storage` e dados bilíngues em `data/release_notes.json`. Eliminação definitiva de deadlocks no Windows NT em testes Playwright (`BUG-12`) via descritores `subprocess.DEVNULL`, expurgo de concatenações hex alpha no `WongojiMultiCellWidget` (`BUG-03`), updates defensivos contra descarte de views no `home_view.py` e em componentes visuais, substituição integral de `ft.ElevatedButton` por `ft.Button` e eliminação de cores legadas. Consolidação da suíte de testes globais alcançando a marca histórica de **300+ testes automatizados (100% aprovados, 0 falhas, 0 erros)**.

### Added — Neurociência, Interatividade & Novos Componentes
- **6 Módulos de Neurociência Cognitiva & Feedback Sensorial** — Integração dos módulos especializados na raiz e em componentes:
  - `SyllableFactory` (`src/components/syllable_factory.py`) — Fábrica interativa de blocos silábicos Hangul com suporte a regras de física articulatória, Voice Onset Time (VOT), decomposição silábica e integração de áudio.
  - `SpatialStage` (`src/components/spatial_stage.py`) — Estágio visual de relações espaciais para fixação implícita de preposições coreanas (`위`, `아래`, `앞`, `뒤`, `안`, `밖`).
  - `NumberTraining` (`src/components/number_training.py`) — Treinamento interativo dos sistemas numéricos nativo coreano (하나, 둘, 셋) e sino-coreano (일, 이, 삼).
  - `AirParticleEffect` (`src/components/air_particle_effect.py`) — Motor de partículas de dispersão de ar com simulação física de plosão e reentrancy guard assíncrono.
  - `HapticService` (`src/haptic_service.py`) — Serviço unificado de feedback tátil e vibração háptica adaptativa para Web e Mobile.
  - `TaskUtils` (`src/task_utils.py`) — Utilitários de gerenciamento assíncrono resiliente de tarefas em segundo plano.
- **11 Assets Vetoriais SVG com Resolução Absoluta (`/`)** — Formas de boca anatômicas (`assets/mouth_shapes/*.svg`) e vetores de representação espacial (`assets/spatial/*.svg`) rigorosamente configurados com barra inicial `/` em todos os controles `ft.Image(src=...)` prevenindo erros 404 e tela preta no Flutter Web CanvasKit (diretriz `BUG-11`).
- **Modal "Novidades do Saebom" (`WhatsNewDialog`)** — Componente modal de acolhimento pedagógico em `src/components/whats_new_dialog.py` renderizando destaques de versão bilíngues (Português/Coreano) no padrão Brand Book v3.1 (Navy `#02060F`, Violet `#8B4DFF`, Gold `#FFAB22`, tipografia Pretendard).
- **Notas de Versão Estruturadas (`data/release_notes.json`)** — Base de dados JSON desacoplada contendo saudações, tags pedagógicas e resumos didáticos para estudantes e professores.
- **Gatilho Inteligente e Acesso Sob Demanda (`src/views/home_view.py`)** — Exibição automática única na `HomeView` disparada quando `last_seen_release != __version__` persistindo o estado em `client_storage` após fechamento seguro, além de botão dedicado na AppBar com ícone `auto_awesome` e cor de acento Gold.
- **Normalização e Fusão Atômica de Identidade (`src/services.py`)** — Métodos `canonicalize_student_name`, `normalize_name_key` e `merge_session_data` permitindo registro e login case-insensitive em PascalCase sem perda ou fragmentação de progresso prévio, com fallback oficial para "Estudante Saebom".
- **Suíte de Testes do WhatsNewDialog (`tests/test_whats_new_dialog.py`)** — 10 novos testes unitários e de integração validando integridade de dados, proibição de termos legados, fidelidade cromática 60/20/12/8, fallbacks contra arquivos inexistentes/corrompidos, ciclo de vida de fechamento e acionamento na HomeView.
- **Suíte Unificada de Neurociência & Interatividade** — Inclusão e estabilização de `test_phase1_sensory_features.py`, `test_phase2_interactive_features.py`, `test_student_name_case_and_merge.py`, `test_haptic_service.py` e `test_quiz_widget.py`.

### Fixed — Infraestrutura, Deadlock Windows & Estabilidade
- **Resolução do Deadlock de Pipe Anônimo no Windows NT (`BUG-12`)** — Correção da fixture `flet_server` em `tests/test_playwright_e2e.py` redirecionando descritores de console para `stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL` e removendo chamadas bloqueantes a `proc.communicate()`. Eliminação do gargalo de 4 KB do buffer de pipe do kernel Windows NT, viabilizando execução fluida de toda a bateria Playwright em ~26s sem travamentos.
- **Eliminação de Concatenação Hex Alpha no Wongoji (`BUG-03`)** — Substituição de `self.colors["primary"] + "18"` por `ft.Colors.with_opacity(...)` em `src/components/wongoji_multi_cell_widget.py:284`, prevenindo inversão de cores e artefatos de canal alfa pelo Flutter Engine.
- **Transição Atômica de Views em Ações da UI (`BUG-11`)** — Proteção defensiva da reconstrução de `page.views` em `home_view.py:22-25` e `toggle_theme`, instanciando a nova view antes de limpar o stack para impedir tela preta sob falhas transientes.
- **Updates Defensivos em Controles Gráficos** — Encapsulamento de chamadas `self.update()` em blocos `try ... except Exception: pass` e sobrescrita defensiva do método `update()` em `QuizWidget`, `FlashcardWidget`, `SentenceBuilderWidget`, `HangulCard` e `VocabCard`, garantindo operabilidade plena em execuções headless desacopladas de `page`.
- **Reentrancy Guard no Efeito de Partículas** — Trava assíncrona `self.is_animating` com cláusula `finally` em `AirParticleEffect.emit()` prevenindo condições de corrida durante disparos repetidos de consoantes plosivas.
- **Simetria de Chaves de Sessão** — Leitura sincronizada de `saebom_student_id` com fallback gracioso para `sejong_student_id` no `ProgressService`, garantindo compatibilidade com sessões legadas.

### Changed — Sanitização Geral de Código & Deprecações
- **Migração Integral de `ft.ElevatedButton` para `ft.Button`** — Substituição em conformidade com a sintaxe oficial do Flet 0.85+ em todas as views (`review_view.py`, `quiz_view.py`, `lesson_view.py`, `hangul_view.py`, `admin_view.py`, `flashcard_widget.py`, `sentence_builder_widget.py`), atingindo 0 avisos de deprecação no terminal.
- **Expurgo Total de Cores Legadas Descontinuadas** — Eliminação completa da constante `INFO_500 = "#004C97"` em `src/theme.py`, `#14004C97` em `hangul_view.py:296`, e cores legadas `#147C4DFF` e `#F5A623`, substituídas pelos papéis semânticos e funções `with_opacity` do Brand Book v3.1.
- **Governança Estrita do Nome "Sejong"** — 0 ocorrências de termos legados na interface de usuário, modais, cabeçalhos, títulos de tela ou novos arquivos de documentação, em respeito rigoroso à diretriz pedagógica da professora.

### Métricas de Qualidade & Testes
- **Total de Testes Automatizados:** **≥ 300 testes 100% aprovados** (270+ testes unitários/integração + 16 testes de 5 pilares estruturais + 5 cenários E2E dinâmicos no Chromium real com Playwright).
- **Tempo de Execução da Suíte Playwright E2E:** Reduzido para **~26 segundos** no Windows nativo sem deadlocks.
- **Taxa de Falhas:** **0 falhas, 0 erros, 0 vazamentos de integridade**.

## [0.3.6-alpha] — 2026-09-09 (Marco Inicial: Rebranding Saebom Companion & Estabilização Web BUG-11)

### Classificação: Alpha (Rebranding Saebom Companion, Pacote de Branding Oficial & Manual de Identidade Visual)
> Milestone de Rebranding Institucional e Padronização de Marca: Transição do projeto para **Saebom Companion (새봄 컴패니언)** por diretriz pedagógica estrita da professora (descontinuação do nome "Sejong" para preservar separação institucional e foco como companion de estudo). Implementação do pipeline determinístico de geração de assets gráficos em `scripts/generate_branding_assets.py` com supersampling Pillow e tipografia Pretendard, produzindo 21 arquivos oficiais em `assets/branding/` (logotipos verticais e horizontais em modos dark e light, anéis concêntricos de expansão, app icons SVG/512/192, favicons web e splash banner 1080×1920). Elaboração do Manual de Identidade Visual oficial (`Documentacao/Design_e_Branding/MANUAL_DE_IDENTIDADE_SAEBOM.md`) baseado no Branding Book v3.1, detalhando o sistema cromático 60/20/12/8 (Midnight Navy, Cream/Slate, Violet, Gold, Lilac), arquitetura de marca de 4 camadas, regras de uso correto/proibições e checklist de governança. Expansão da suíte de testes para **234 testes automatizados (100% OK, incluindo Playwright E2E Chromium)**.

### Added — Sistema de Marca & Assets Gráficos
- **Gerador de Assets de Marca (`scripts/generate_branding_assets.py`)** — Script determinístico para renderização de logotipos vetoriais SVG e imagens rasterizadas de alta fidelidade com supersampling 2x/3x e renderização CJK precisa.
- **21 Assets Oficiais de Marca (`assets/branding/`)** — Logotipo vertical Dark e Light (SVG, PNG transparente e sólido), assinatura horizontal para AppBar (SVG, PNG transparente e sólido), símbolo oficial de Anéis Concêntricos de Expansão (SVG e PNG 512px), Ícones de aplicativo squircle (`app_icon.svg`, 512px, 192px), Favicons web (32px, 16px e multi-resolução `favicon.ico`) e Splash Banner mobile Full HD vertical (1080×1920).
- **Manual de Identidade Visual Saebom Companion (`Documentacao/Design_e_Branding/MANUAL_DE_IDENTIDADE_SAEBOM.md`)** — Documentação mestre completa em 8 seções transcrevendo e estruturando o Branding Book v3.1 oficial para o Obsidian.
- **Suíte de Testes de Branding & Tema (`tests/test_branding_assets.py` & `tests/test_theme.py`)** — 31 novos testes automatizados (25 em `test_branding_assets.py` + 6 em `test_theme.py`) cobrindo integridade física dos 21 assets, conformidade vetorial de SVG, regras estritas de proibição de nomes legados no título da janela, e aderência estrita aos tokens da paleta 60/20/12/8 do Brand Book v3.1.
- **Suíte E2E de Cobertura Total (`tests/test_e2e_full_coverage.py`)** — 16 testes ponta a ponta cobrindo os 5 pilares fundamentais (Infraestrutura, Segurança, Arquitetura Web, Rebranding e Caligrafia Curricular).
- **Suíte E2E com Playwright Chromium em Navegador Real (`tests/test_playwright_e2e.py`)** — 5 testes automatizados em headless browser Chromium com CanvasKit real, cobrindo startup em processo isolado (`FLET_FORCE_WEB_SERVER="true"`), handshake WebSocket bidirecional, auditoria de luminância contra tela preta (100% de pixels renderizados), ausência de vazamento de segredos no DOM, e despacho de gestos touch no canvas Wongoji, elevando a suíte global para **234 testes automatizados (100% OK)**.

### Changed — Aplicação Visual nas Telas & Descontinuação do Termo Legado
- **Splash View (`src/views/splash_view.py`)** — Tela de abertura reestruturada com badge oficial Saebom Companion, ícone squircle 512px, tipografia Pretendard para '새봄', micro-badge 'COMPANION' em Gold/Violet, e slogan oficial *"Uma nova primavera para a aprendizagem."*.
- **Home View & AppBar (`src/views/home_view.py`)** — AppBar atualizada com o novo ícone oficial de 192px e título estilizado 'Saebom COMPANION'; cabeçalhos de seções atualizados para 'Nível 1A · 한국어 1A' e 'Nível 1B · 한국어 1B'; subtítulo de boas-vindas reformulado com foco pedagógico autônomo.
- **Onboarding View (`src/views/onboarding_view.py`)** — Brasão institucional substituído pelo emblema oficial Saebom Companion com ícone de 192px, tipografia Pretendard e subtítulo "Companion Institucional de Aprendizagem de Coreano".
- **Review & Lesson Views (`src/views/review_view.py`, `src/views/lesson_view.py`)** — Badges de origem de cartas atualizados para 'Nível 1A' / 'Nível 1B' e tela de lição em construção atualizada para a equipe Saebom Companion.
- **Admin View (`src/views/admin_view.py`)** — Descrições de login e relatórios i18n atualizados em português e coreano ('새봄 교수 포털') removendo termos legados.
- **Services & Retrocompatibilidade (`src/services.py`, `src/audio_service.py`)** — Suporte às novas variáveis `SAEBOM_ADMIN_PIN` e `SAEBOM_AUDIO_CACHE_DIR` com postura fail-closed e retrocompatibilidade para variáveis legadas; fallback de identidade de aluno atualizado para "Estudante Saebom". Implementação da classe `StudentIdentity` com persistência segura.
- **Hardening de Rede Docker (`docker-compose.yml`)** — Alteração do container `app` de `ports: - "8554:8554"` para `expose: - "8554"`, fechando a interface para a internet e eliminando alertas de requisições HTTP inválidas originadas por scanners TLS externos.

### Fixed — Compatibilidade Flet & Estabilização Web (BUG-11)
- **Correção de Controle de Ajuste de Imagem (`ft.BoxFit.CONTAIN`)** — Resolução de `AttributeError: module 'flet' has no attribute 'ImageFit'` em `splash_view.py`, `home_view.py` e `onboarding_view.py`, substituindo referências pelo enumerador canônico `ft.BoxFit.CONTAIN`.
- **Prevenção de Tela Preta no Flutter Web (BUG-11)** — Resolução definitiva de tela preta ao executar `python main.py --browser`:
  - *Caminhos Absolutos de Assets:* Inclusão de barra inicial `/` em todos os `src` de imagem (`/branding/app_icon_512.png`, `/branding/app_icon_192.png`), evitando 404 em rotas aninhadas (`/splash`, `/home`, `/onboarding`).
  - *Roteamento Resiliente (`src/router.py`):* Esvaziamento de `page.views` agora ocorre de forma atômica somente após o sucesso do construtor da view com fallback de emergência para tela de carregamento, garantindo que `page.views` nunca fique vazia.
  - *Roteamento Web Direto e Renderização Atômica (`src/router.py`, `main.py`):* Resolução do comportamento em que URLs diretas do navegador (`/admin`, `/hangul`, `/onboarding`) eram forçadas incondicionalmente para `/splash` e redirecionadas para `/onboarding`. Implementado método `render_route` resiliente que previne duplicação de renders e respeita o `page.route` inicial, garantindo que cada rota exiba sua respectiva view com integridade e unicidade visual comprovada (5/5 screenshots Playwright distintas).
  - *Timeout de Segurança no Splash (`src/views/splash_view.py`):* Timeout de 0.8s para consultas de persistência (`SharedPreferences`), impedindo bloqueios indefinidos na inicialização.
  - *Padronização de Opacidade Hex (`BUG-03`):* Substituição de sufixos de opacidade concatenados pela função nativa `ft.Colors.with_opacity` em `oclusive_lab.py`, `admin_view.py` e `home_view.py`.
- **Suíte de Testes Expandida (`tests/test_router.py`, `tests/test_views_rendering.py`, `tests/test_e2e_full_coverage.py`, `tests/test_playwright_e2e.py`)** — Total de **234 testes automatizados aprovados sem falhas (100% OK)**.

## [0.3.5-alpha] — 2026-08-30

### Classificação: Alpha (Modo de Escrita Ampliado, Fonte Caligráfica Kyobo & IoU Tolerante)
> Milestone de Estabilização e Calibração Tátil no Wongoji Lab: Resolução de conflitos de gestos na Gesture Arena do Flutter mediante introdução do Modo de Escrita em foco modal (`ft.AlertDialog` dedicado sem viewport rolável) e prévia passiva na aba de caligrafia (eliminando scroll jumps e resets de posição). Adoção da tipografia manuscrita oficial coreana `Kyobo Handwriting 2025` (`assets/fonts/KyoboHandwriting2025lyb.otf`) para prática de traçado, preservando `Pretendard` como fonte global do sistema. Implementação de camada modelo fantasma (Ghost Layer) vetorial suave, algoritmo de IoU Tolerante Espacialmente (`calculate_tolerant_iou`) com dilatação morfológica para calibração justa de scores humanos, correção do empilhamento de camadas no Canvas (Z-Index do mapa de diagnóstico acima dos traços), sincronização bidirecional entre modal e prévia, catálogo completo de 획순 (51 jamo KS X 1001) em `jamo_utils`, e expansão da suíte para **161 testes automatizados (100% OK)**.

### Added & Changed — Wongoji Lab & Experiência Tátil
- **Modo de Escrita em Modal / Wongoji Focus Mode (`src/views/hangul_view.py` & `src/components/calligraphy_widget.py`)** — A grade da aba Caligrafia opera como prévia passiva, permitindo rolagem fluida sem interferência na Gesture Arena. O toque na prévia abre o modo de escrita ampliado em diálogo modal sem ancestrais roláveis, com isolamento total dos eventos de desenho.
- **Tipografia Caligráfica Oficial Kyobo (`assets/fonts/KyoboHandwriting2025lyb.otf`)** — Integração da fonte de caligrafia coreana Kyobo Handwriting no motor de rasterização e no guia visual da grade, enquanto Pretendard permanece como fonte de alta legibilidade para a interface do app.
- **Ghost Layer Vetorial Suave (`src/components/calligraphy_widget.py`)** — Substituição da projeção matricial pixelada por glifos vetoriais nítidos em `cv.Text` com renderização suave em ambos os modos claro e escuro.
- **IoU Tolerante a Variação Motora (`calculate_tolerant_iou`)** — Algoritmo de dilatação morfológica com raio espacial ajustável ($\pm 1$ pixel em 48×48) para premiar a precisão anatômica do aluno sem penalizar microdesvios naturais de traçado manual.
- **Correção da Ordem de Camadas do Canvas (Z-Index)** — O overlay de diagnóstico (acertos verdes, excessos vermelhos e omissões cinzas) agora é renderizado no topo dos traços de tinta do aluno, garantindo clareza visual pós-avaliação.
- **Sincronização de Estado & Limpeza em Cancelamento** — Coordenadas, pontuações e diagnósticos persistem e são atualizados na prévia ao fechar o diálogo; traços incompletos por cancelamento de gesto são descartados de forma limpa.
- **Catálogo Completo de Stroke Order (`assets/stroke_order/jamo_strokes.json` & `src/jamo_utils.py`)** — Dataset de 획순 alinhado ao mapa KS X 1001: 19 consoantes (incluindo tensas), 21 vogais e 11 겹받침. Correção da ordem oficial de ㅓ/ㅕ, ㄹ com 5 traços (L inferior unificado) e API `load_stroke_catalog` / `get_stroke_data` / `layout_syllable_strokes`.
- **Tipo de Questão 'Calligraphy' nos Quizzes (`src/models.py` & `src/components/quiz_widget.py`)** — Suporte a exercícios de fixação de escrita Hangul no Quiz Engine com contrato fail-closed via `@model_validator` (`validate_calligraphy_metadata`), suporte a `target_text` para palavras e frases, renderização de `WongojiMultiCellWidget` em `_build_calligraphy_exercise()`, fluxo pedagógico com retry orientativo e submissão explícita via botão **"✅ Terminei"**.
- **Componente WongojiMultiCellWidget (`src/components/wongoji_multi_cell_widget.py`)** — Grade multi-célula virtualizada em Canvas Único com `cv.Path` otimizado, suporte a espaçamento canônico (*띄어쓰기*), avaliação individualizada por célula via IoU tolerante e reprodução de pronúncia de palavras/frases completas via `AudioService`.
- **Alinhamento com os Gabaritos Oficiais do Sejong 1A e 1B (국립국어원 익힘책 모범 답안)** — Integração de exercícios práticos de caligrafia nos workbooks de todas as 23 unidades curriculares (`unit_intro.json`, `unit_01.json` a `unit_10.json` e `unit_1b_01.json` a `unit_1b_12.json`), cobrindo combinações léxicas fundamentais em 1A (ex: `한국 사람`, `밥을 먹어요`, `집에서 쉬었어요`) e estruturas sintáticas compostas em 1B (ex: `불고기를 자주 먹어요`, `자전거를 못 타요`, `커피를 좋아해서`, `제주도에 여행을 갔어요`).

### Added — Suíte de Testes
- **161 Testes Automatizados (100% OK)** — Inclusão de testes unitários para `calculate_tolerant_iou`, validação de descarte de traços em `_on_pan_cancel`, escala de prévia passiva, consistência de tipografia no guia, cálculo de espessura proporcional de traço no `tests/test_calligraphy_widget.py`, cobertura do catálogo completo de jamo em `tests/test_jamo_utils.py`, testes de contrato e UI de caligrafia multi-célula no quiz em `tests/test_quiz_calligraphy.py` e validação curricular em `tests/test_workbook_quiz_content.py` e `tests/test_unit_1b_content.py`.

---

## [0.3.4-alpha] — 2026-08-28

### Classificação: Alpha (Wongoji Lab: Escrita Livre & Diagnóstico Visual Matricial)
> Evolução do Motor de Caligrafia Hangul: Substituição do modelo rígido de stroke order por um ambiente de escrita 100% livre com avaliação matemática real por Bitmap IoU (Intersection over Union 48×48 com a fonte oficial `Pretendard-Bold.otf` e Pillow). Introdução de mapa visual de diagnóstico colorido (🟢 Verde = Acerto, 🔴 Vermelho = Excesso/Desvio, ⚪ Cinza = Omissão/Falta), telemetria ao vivo (pontos amostrados, traços), botões de controle tátil ("Limpar", "Avaliar Sílaba", "Diagnóstico") e expansão para **135 testes automatizados (100% OK)**.

### Added — Wongoji Lab & Visão Computacional
- **Escrita Livre & Natural (`src/components/calligraphy_widget.py`)** — O aluno escreve livremente qualquer traço na grade 원고지 sem interrupções ou rejeições durante o movimento.
- **Motor de Visão Tipográfica & IoU (`calculate_iou`, `render_reference_bitmap`, `render_strokes_bitmap`)** — Rasterização 48×48 com fonte Pretendard oficial, permitindo validar qualquer uma das 11.172 sílabas Hangul KS X 1001 e Jamo isolados com precisão métrica.
- **Overlay Colorido de Diagnóstico (`generate_diagnostic_overlay`)** — Mapa de calor em 3 canais renderizado diretamente no Flet Canvas pós-avaliação, destacando com precisão os acertos, excessos e omissões.
- **Controles de Ação & Telemetria** — Botões "Limpar", "Avaliar Sílaba", alternador de guia fantasma e alternador de diagnóstico, com contagem viva de pontos e traços.
- **Integração de Áudio Nativo** — Disparo automático da pronúncia em coreano via `AudioService` ao atingir o limiar de acerto.
- **Dependência Pillow (`requirements.txt`)** — Adicionado `Pillow>=10.0.0` para geração e processamento matricial.

### Added — Suíte de Testes
- **135 Testes Automatizados (100% OK)** — Testes unitários para `calculate_iou`, `render_reference_bitmap`, `render_strokes_bitmap`, `generate_diagnostic_overlay` e fluxo de UI completo no `tests/test_calligraphy_widget.py`.

---

## [0.3.3-alpha] — 2026-08-28

### Classificação: Alpha (Motor de Caligrafia & Reconhecimento Tátil 원고지)
> Milestone de Caligrafia e Prática Motora de Escrita: Introdução da grade tradicional de manuscrito coreano 원고지 (Wongoji) para prática de escrita dos livros e workbooks. Implementação de decomposição aritmética Unicode (KS X 1001), classificação de 6 geometrias de blocos silábicos (CV/CVC), motor de validação de traços em tempo real por Path Matching (tolerância euclidiana, direcionalidade vetorial e desvio ponto-segmento), camada de modelo fantasma (ghost layer) com indicadores de ponto de início, dataset de stroke order para os 40 Jamo básicos e expansão da suíte para **134 testes automatizados (100% OK)**.

### Added — Caligrafia & Reconhecimento Tátil
- **Componente `CalligraphyWidget` (`src/components/calligraphy_widget.py`)** — Grade interativa 원고지 em Flet Canvas + GestureDetector com proporção 1:1, linhas pontilhadas de cruz central, feedback em tempo real (~60fps), botões de alternância de modelo e reinício.
- **Decomposição Unicode e Layout de Blocos (`src/jamo_utils.py`)** — Decomposição aritmética pura de sílabas Hangul (가-힣) em Choseong, Jungseong e Jongseong, classificação de 6 tipos de blocos (`CV_VERTICAL`, `CV_HORIZONTAL`, `CV_COMPOUND`, `CVC_VERTICAL`, `CVC_HORIZONTAL`, `CVC_COMPOUND`) e mapeamento espacial de caixas delimitadoras.
- **Dataset de Stroke Order (`assets/stroke_order/jamo_strokes.json`)** — Vetores de traços normalizados [0.0, 1.0] para 14 consoantes básicas e 11 vogais essenciais (adaptado de *hangeul-stroke-order*, CC BY-SA 4.0).
- **Documento Conceitual Mestre (`Documentacao/Conceitos/Reconhecimento_Tatil_e_Caligrafia_Hangul.md`)** — Fundamentos do Hunminjeongeum, princípios neuropedagógicos de memória motora e comparação arquitetural entre Path Matching e OCR.

### Added — Suíte de Testes
- **134 Testes Automatizados (100% OK)** — Inclusão de `tests/test_jamo_utils.py` (16 testes) e `tests/test_calligraphy_widget.py` (12 testes).

---

## [0.3.2-security] — 2026-08-28

### Classificação: Security Hardening (Resolução de Bloqueadores P0/P1)
> Milestone de Segurança e Integridade Operacional: Resolução formal dos apontamentos críticos da auditoria de segurança da branch `main`. Eliminação total de PIN administrativo padrão com postura fail-closed obrigatória, implementação de rate limiting e lockout progressivo com mitigação de timing attacks (`hmac.compare_digest`), desacoplamento estrito entre Student ID (público) e Recovery Key (segredo protegido via salted SHA-256), isolamento de cache mutável fora de `assets/` (`data/cache/audio/`), política de rotação e retenção de telemetria, regras rigorosas de privacidade no `.gitignore`, implementação do pipeline CI no GitHub Actions (`.github/workflows/ci.yml`) e expansão da suíte para **106 testes automatizados (100% OK)**.

### Fixed — Autenticação Administrativa & Governança (P0 / P1)
- **Eliminação de PIN Padrão (P0)** — Removido `DEFAULT_PIN = "sejong2026"` do `AdminService`. Variável `SEJONG_ADMIN_PIN` torna-se obrigatória para qualquer acesso ao `/admin` (fail-closed).
- **Docker Fail-Closed** — Sintaxe de interpolação `${SEJONG_ADMIN_PIN:?SEJONG_ADMIN_PIN environment variable is required}` no `docker-compose.yml`, impedindo que containers subam sem credencial configurada.
- **Proteção contra Brute Force & Timing Attacks (P1)** — Rate limiter em memória com lockout escalonado (5 falhas $\rightarrow$ 30s / 10 falhas $\rightarrow$ 5 min) e verificação via `hmac.compare_digest`.
- **Sessões Administrativas Temporárias (P1)** — Emissão de tokens efêmeros com expiração automática em 1 hora e revogação ativa no logout.

### Security — Identidade, Dados & Armazenamento (P1)
- **Desacoplamento de Student ID e Chave de Recuperação** — O Student ID (`student_XXXXXXXXXXXX`) passa a ser estritamente um identificador público. Para restaurar sessões entre navegadores/dispositivos, o aluno deve fornecer a Chave Secreta de Recuperação (`XXXX-XXXX-XXXX`).
- **Zero Plaintext no Servidor** — A chave de recuperação é armazenada apenas como hash SHA-256 com salt criptográfico (`recovery_salt` + `recovery_hash`).
- **Isolamento de Armazenamento Mutável** — Cache de áudio sintetizado em runtime transferido para `data/cache/audio/`, tornando a pasta `assets/` 100% estática (read-only bundle).
- **Proteção de Privacidade & Rotação de Telemetria** — `.gitignore` atualizado para ignorar `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/cache/`, `*.jsonl`, com rotação automática em `TelemetryService` (`MAX_EVENTS_PER_FILE = 5000`).

### Added — CI & Suíte de Testes
- **Pipeline GitHub Actions (`.github/workflows/ci.yml`)** — Validação automatizada em Python 3.11 e 3.12, compilação de bytecode, scan de segredos e execução de testes.
- **106 Testes Automatizados (100% OK)** — Inclusão de `tests/test_admin_auth_hardening.py`, `tests/test_student_identity_security.py` e `tests/test_telemetry_privacy_and_rotation.py`.

---

## [0.3.2-alpha] — 2026-08-22

### Classificação: Alpha (Piloto Público Ativo — Turmas 1A CCCB)
> Milestone de Estabilização, Hardening & Piloto Pedagógico Real: Lançamento do piloto público oficial com a professora e turmas do Sejong Coreano 1A para coleta e validação de métricas pedagógicas autênticas em produção. Introdução da tela institucional de Onboarding com identificação nominal do estudante (Nome + Sobrenome vinculados ao Student ID), persistência real multiplataforma via `ft.SharedPreferences` (fim da perda de sessão mobile ao desligar/bloquear a tela), deploy de alta performance 24/7 na Oracle Cloud Infrastructure com domínio e HTTPS automático (`sejongcompanion.duckdns.org`), inclusão do binário canônico `assets/silent.wav` (destravamento de autoplay web / BUG-08 catalogado), hardening do algoritmo de repetição espaçada SRS com piso de meia-vida $\ge 0.2$ dias e expansão da suíte para **93 testes automatizados (100% OK)**.

### Added — Onboarding, Persistência & Identidade
- **Onboarding e Identificação Institucional (`onboarding_view.py`)** — Tela acolhedora de boas-vindas do Centro Cultural Coreano no Brasil para novos estudantes cadastrarem seu Nome e Sobrenome, vinculando-os ao seu Student ID permanente, com suporte a restauração de progresso para alunos que trocam de aparelho.
- **Persistência Real Multiplataforma (`ft.SharedPreferences`)** — Integração assíncrona com o storage nativo do cliente durante o handshake do `splash_view.py`, garantindo que desbloquear a tela do celular ou reabrir o navegador preserve 100% da sessão sem criar alunos anônimos duplicados.
- **Saudação Nominal e Modal de Perfil na Home (`home_view.py`)** — Abertura personalizada com *"Olá, [Nome do Aluno]! 👋"* e diálogo de perfil com exibição do Código Institucional e edição do nome.
- **Identificação Nominal no Portal do Professor (`admin_view.py` & `services.py`)** — Relatórios pedagógicos e listagens da turma identificando os alunos nominalmente (ex: *"A aluna Marina Silva..."*).

### Added — Infraestrutura & Áudio
- **Deploy 24/7 na Oracle Cloud Infrastructure (OCI Always Free)** — Container multi-arch com Caddy reverse proxy e HTTPS automático no domínio `sejongcompanion.duckdns.org`.
- **Binário Canônico `assets/silent.wav` & BUG-08 Catalogado** — Destravamento definitivo da política de autoplay em navegadores móveis (flet-dev/flet#3695) e documentação formal em `Documentacao/Bugs_Criticos/bug_08_politica_autoplay_navegador_e_silent_wav.md`.

### Added — Suíte de Testes
- **93 Testes Automatizados (100% OK)** — Inclusão de `tests/test_student_identity_and_persistence.py` validando o fluxo de identidade nominal, persistência entre sessões e normalização fonética/sintática no Sentence Builder.

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
