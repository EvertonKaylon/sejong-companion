# Relatório Consolidado do Estado Atual — Saebom Companion (`v0.3.8-alpha`)

**Data de Consolidação:** 2026-11-23  
**Branch Auditada:** `security/mitre-owasp-hardening` (`HEAD` = `e59946f`)  
**Escopo:** Auditoria integral de versão, Git/infraestrutura, arquitetura Flet, branding, currículo/assets, segurança OWASP/MITRE, suíte de testes e documentação oficial.

---

## 1. Sumário Executivo & Divergência de Versão

O **Saebom Companion (새봄 컴패니언)** evoluiu na documentação de changelog até **`0.3.8-alpha`** na branch `security/mitre-owasp-hardening` (`e59946f`), com **459 testes aprovados + 21 subtestes** (incluindo 5 testes Playwright E2E no Chromium real), linhagem de segurança preservada desde `security/hardening-v0.3.2` (`16a8f36`) e currículo completo de **23 unidades** (Hangul + Livros 1A e 1B).

Entretanto, existe uma **divergência formal de versão** entre a documentação/branch e os artefatos de runtime:

| Artefato | Versão Declarada | Observação |
| :--- | :--- | :--- |
| [`src/__init__.py`](../../src/__init__.py#L3) | `0.3.6-alpha` | `__version__ = "0.3.6-alpha"` |
| [`main.py`](../../main.py#L3) | `0.3.6-alpha` | Imprime `Saebom Companion v{__version__}` (`L98`) |
| [`src/theme.py`](../../src/theme.py#L281-L282) | `0.3.6-alpha` | Define `page.title = f"Saebom Companion v{__version__}"` |
| [`data/release_notes.json`](../../data/release_notes.json#L2) | `0.3.6-alpha` | `release_date: "2026-09-20"`; validado contra `__version__` em `tests/test_whats_new_dialog.py:89` |
| [`src/components/whats_new_dialog.py`](../../src/components/whats_new_dialog.py#L30) | `0.3.6-alpha` | Fallback e default nas linhas `30` e `121` |
| [`src/views/home_view.py`](../../src/views/home_view.py#L38) | `0.3.6-alpha` | Compara `last_seen_release` contra `__version__` (`L38, L52, L101`) |
| [`GEMINI.md`](../../GEMINI.md#L6) | `v0.3.6-alpha` | Declara `Fase atual: Alpha (v0.3.6-alpha)` |
| [`CHANGELOG.md`](CHANGELOG.md#L19) | `0.3.8-alpha` | Registra `0.3.7-alpha` (`88b35aa`) e `0.3.8-alpha` (`9c49112`, `e59946f`) |

**Diagnóstico de Prontidão:** A aplicação está funcional e verde em testes unitários, integração e E2E local, porém **não deve ir para deploy atrás do Caddy sem corrigir os 5 achados residuais do [`BUG-13`](../Bugs_Criticos/bug_13_hardening_owasp_mitre_container_caddy_auditoria.md)** (especialmente CSP bloqueando `gstatic.com`/worker `blob:`/`wasm-unsafe-eval` e conflito de UID `10001` nos bind mounts Linux).

---

## 2. Git, Branches, Working Tree, Raiz & `.gitignore`

### 2.1 Topologia de Branches e Divergências (`HEAD` = `e59946f`)
* **Working tree inicial:** Limpo (`git status --short --branch` em `## security/mitre-owasp-hardening` sem modificados ou não-rastreados fora de ignore).
* **Branches locais e remotas:**
  * `* security/mitre-owasp-hardening`: `e59946f` (`HEAD`)
  * `develop`: `88b35aa` (`[origin/develop: ahead 53]`)
  * `main`: `2b11937` (`[origin/main: behind 1]`)
  * `security/hardening-v0.3.2`: `16a8f36`
  * `feature/branding`: `c51dc3a` | `feature/calligraphy-grid`: `fe68e7c` | `feature/neuroscience-gap-closure`: `0a248c2`
  * `remotes/origin/develop`: `2b11937` | `remotes/origin/main`: `9dafd2f` (`README.md`, +56 linhas) | `remotes/origin/HEAD -> origin/main`
* **Divergências (`git rev-list --left-right --count HEAD...<ref>`):**
  * `HEAD...develop`: **4 à frente / 0 atrás**
  * `HEAD...main`: **57 à frente / 0 atrás**
  * `HEAD...origin/develop`: **57 à frente / 0 atrás**
  * `HEAD...origin/main`: **57 à frente / 1 atrás** (commit `9dafd2f` em `origin/main`)
  * `HEAD...security/hardening-v0.3.2`: **49 à frente / 0 atrás**
* **Linhagem de Segurança (`GEMINI.md`):**
  * `git merge-base --is-ancestor security/hardening-v0.3.2 HEAD` → **exit code `0`** (`True`, `merge-base = 16a8f365d5131a40f7b8af3822b93365cf196bbe`).

### 2.2 Histórico Recente (`ca3a01e` → `e59946f`)
1. `ca3a01e` — `feat(release): merge v0.3.6-alpha with neuroscience reconciliation, whats-new modal and E2E stabilization` (`139 files, +12833/-712`)
2. `f35c633` — `chore(rules): atualizar GEMINI.md com salvaguardas de auditoria de seguranca, deadlock BUG-12 e Flet page property` (`1 file, +4/-1`)
3. `c7aa16e` — `fix(admin): desbloquear campo de PIN, exibir aviso claro quando nao configurado e isolar testes` (`3 files, +25/-7`: `admin_view.py`, `test_admin_auth_hardening.py`, `test_admin_service.py`)
4. `981838e` — `feat(notifications): implementar notificacoes nativas, mural de avisos da professora e badges integrados` (`9 files, +1180/-25`)
5. `88b35aa` — `docs(changelog): registrar versao 0.3.7-alpha com ecossistema de comunicacao e notificacoes` (`1 file, +27/-1`)
6. `d6289d5` — `feat(security): aplicar hardening owasp top 10 e mitre attack em container, caddy e auditoria` (`8 files, +314/-13`)
7. `9c49112` — `docs(security): documentar hardening owasp e mitre attack no changelog` (`1 file, +26/-1`)
8. `66874a8` — `feat(neuroscience): montar dialpad, fabrica de silabas e diorama espacial nas views` (`4 files, +220/-4`)
9. `e59946f` — `docs(changelog): documentar ativacao visual dos componentes de neurociencia` (`1 file, +7/-1`)

### 2.3 Inventário da Raiz, `.gitignore` e `.git/info/exclude`
* **Rastreados na raiz (`git ls-tree --name-only HEAD`):** `.dockerignore`, `.gitignore`, `Caddyfile`, `DESIGN.md`, `Dockerfile`, `GEMINI.md`, `Saebom_Companion_Branding_Book_v3.1_mesclado.pdf`, `audit_report.md`, `docker-compose.yml`, `main.py`, `requirements.txt`, além das pastas `.github/` (1), `.licenses/` (1), `assets/` (952), `data/` (26 JSONs), `docs/` (4 PDFs em `docs/reference/`), `Documentacao/` (44 antes deste sync), `scripts/` (7), `src/` (36), `tests/` (33) e `.agents/skills/sejong-docs-sync/SKILL.md` (1).
* **`.gitignore` (61 linhas):** Protege `.env` (`L2`), `*.env` (`L3`), `.env.*` (`L4`), `data/cache/` (`L34`), `data/sessions/` (`L39`), `data/telemetry/` (`L40`), `data/reports/` (`L41`), `*.jsonl` (`L43`), `scratch/` (`L50`), `WhatsApp*` (`L51`), `gabarito*` (`L52`), `attack_matrix*.pdf` (`L53`), `getting-started-with-attack*.pdf` (`L54`), `tests/screenshots/` (`L55`). `git ls-files` confirma **0 arquivos rastreados** em `data/sessions`, `data/telemetry`, `data/reports`, `data/cache`, `*.jsonl` e `.env*`. `git ls-files --others --exclude-standard` está vazio.
* **Lacuna em `.git/info/exclude`:** `ORIGINAL_REQUEST.md` (`.git/info/exclude:9`) e pastas internas de `.agents/` (`.git/info/exclude:7`, exceto a skill rastreada) dependem de exclusão local e não constam no `.gitignore` versionado.

---

## 3. Arquitetura Flet, Inventário de Código/Scripts, Neurociência e Bugs Funcionais

### 3.1 Inventário de Código e Scripts
* **Entrypoint:** [`main.py`](../../main.py) (`124L`: `load_local_env@L6`, `main@L54`, bind `127.0.0.1` local e `0.0.0.0` apenas quando `PORT` existe em `L39-44,124`).
* **`src/*.py` (11 arquivos):** `__init__.py` (`3L`), `announcement_service.py` (`151L`), `audio_service.py` (`353L`), `haptic_service.py` (`101L`), `jamo_utils.py` (`347L`), `models.py` (`310L`), `notification_service.py` (`136L`), `router.py` (`100L`), `services.py` (`1761L`), `task_utils.py` (`35L`), `theme.py` (`302L`). **Nota:** O pacote `src/engine/` planejado para `v0.4.0-alpha` ainda não existe.
* **`src/views/*.py` (9 views + `__init__.py`):** `splash_view.py` (`231L`, `/splash`), `onboarding_view.py` (`264L`, `/onboarding`), `home_view.py` (`793L`, `/home`), `hangul_view.py` (`931L`, `/hangul`), `lesson_view.py` (`388L`, `/lesson`), `quiz_view.py` (`424L`, `/quiz`), `review_view.py` (`279L`, `/review`), `flashcards_view.py` (`137L`, `/flashcards`), `admin_view.py` (`1054L`, `/admin`).
* **`src/components/*.py` (14 componentes + `__init__.py`):** `air_particle_effect.py` (`111L`), `calligraphy_widget.py` (`813L`), `flashcard_widget.py` (`130L`), `hangul_card.py` (`189L`), `layout.py` (`33L`), `number_training.py` (`237L`), `oclusive_lab.py` (`281L`), `quiz_widget.py` (`880L`), `sentence_builder_widget.py` (`133L`), `spatial_stage.py` (`213L`), `syllable_factory.py` (`285L`), `vocab_card.py` (`252L`), `whats_new_dialog.py` (`407L`), `wongoji_multi_cell_widget.py` (`537L`).
* **`scripts/*` (7 arquivos):** `audit_curriculum.py` (`133L`), `bundle_all_typecast_audio.py` (`173L`), `generate_branding_assets.py` (`450L`), `generate_typecast_lab_hd.py` (`136L`), `pedagogical_report.py` (`153L`), `prewarm_audio.py` (`134L`), `setup_oci_server.sh` (`60L`).

### 3.2 Matriz de Integração de Neurociência / Interatividade

| Componente | Onde é Montado | Status | Achados Concretos |
| :--- | :--- | :---: | :--- |
| `SyllableFactory` | `hangul_view.py:8,581-584,594` | ✅ Completo | Integrado na aba Sílabas com chips de 초성/중성/종성 e áudio. |
| `SpatialStage` | `lesson_view.py:2,249-256` (`unit_03`) | ⚠️ Parcial | `self.object_img` (`spatial_stage.py:96-101,207`) nunca é adicionado ao `ft.Stack` (`L164-175`); não há botão na UI para `next_challenge()` (`L199`) nem `on_challenge_completed` ligado em `lesson_view.py:253`. |
| `NumberTraining` | `hangul_view.py:9,586-589,598` | ⚠️ Parcial | Discador livre sem `on_complete` ou `current_challenge_target` (`OK` inerte em `L168-171`); `NATIVE_MAP` (`L24-35`) omite `"0"` e tem `"10": "열"` inatingível pelas teclas `"0"`–`"9"`. |
| `OclusiveLab` | `hangul_view.py:6,206,216` | ✅ Completo | Montado na aba Consoantes com `audio_service.play_korean` (sem ligação a `AirParticleEffect`/`HapticService`). |
| `AirParticleEffect` | Exportado em `components/__init__.py` | ❌ Órfão | Não importado nem montado em nenhuma view ou componente em produção (`HapticService`, `TaskUtils` e `jamo_utils.layout_syllable_strokes` também estão desconectados da UI). |
| `WongojiMultiCellWidget` | `quiz_widget.py:9,517-523` | ✅ Completo | Servido por `quiz_view.py:204` nas questões `calligraphy`. |
| `CalligraphyWidget` | `hangul_view.py:7,622-627,707-743` | ✅ Completo | Focus Mode em `AlertDialog` + prévia estática (import não utilizado remanescente em `quiz_widget.py:8`). |
| `SentenceBuilderWidget` | `flashcards_view.py:6,111-113` | ✅ Completo | Montado no modo `"builder"`. |
| `WhatsNewDialog` | `home_view.py:4,61`, `admin_view.py:4,359` | ✅ Completo | Auto-trigger por `__version__` e botão na AppBar. |
| `FlashcardWidget` | `review_view.py:6,138,158`, `flashcards_view.py:6,101` | ✅ Completo | Botões `again`/`good`/`easy` em `L103-105` (omite `hard`). |
| `QuizWidget` | `quiz_view.py:2,204-209` | ✅ Completo | Cobre `multiple_choice`, `drag_and_drop_sov`, `order_words` e `calligraphy`. |

### 3.3 Conformidade Flet 0.85.3 & Bugs Funcionais Abertos
* **Conformes:** `ft.Image(src=...)` com `/` inicial (6/6), 0 ocorrências de `ft.ImageFit`, `ft.ElevatedButton`, kwarg `letter_spacing`, concatenação hex-alpha `#RRGGBBAA`, `#004C97` ou sobrescrita `self.page =`; tipografia `Pretendard` + `Kyobo Handwriting 2025` e escala `0.68` preservadas; `Router` (`src/router.py:17-100`) e `home_view.py:24-27` realizam transição atômica.
* **Não conformes / Bugs funcionais:**
  1. **`admin_view.py:168-171` (`rebuild_view`):** chama `page.views.clear()` (`L169`) antes de construir `admin_view(page)` (`L170`), violando a atomicidade (`GEMINI.md:42`).
  2. **Timeouts ausentes em `SharedPreferences.set`:** `onboarding_view.py:72-73` e `home_view.py:169` chamam `sp.set(...)` sem `asyncio.wait_for(..., timeout=...)`.
  3. **`oclusive_lab.py:111`:** instancia `ft.BoxShadow` dentro de `_build_oclusive_button` (12x) em vez de reutilizar `Styles.*` (`GEMINI.md:48`).
  4. **Divergência `AudioService` Web (`data/cache/audio` vs `assets/audio_cache`):** sem `SAEBOM_AUDIO_CACHE_DIR`, `get_cache_dir()` (`audio_service.py:27-36`) grava sínteses novas em `data/cache/audio/` (640 arquivos), mas `_play_korean_async_inner` (`L110`) passa `src="audio_cache/{filename}"` relativo a `assets_dir="assets"` (`main.py:124` → `assets/audio_cache/`, 1.328 arquivos). Sínteses novas não ficam acessíveis ao player Web, além de `self.player` não ser anexado a `page.overlay` (confia em `ft.Service.init()`).
  5. **`ProgressService.set_student_name` duplicado (`src/services.py:600-604` e `L716-726`):** a segunda definição sobrescreve a primeira, ignora `canonicalize_student_name` e grava apenas `sejong_student_name` em `client_storage`.
  6. **`AnnouncementService._save_announcements` (`src/announcement_service.py:40-48`):** docstring afirma escrita atômica, porém abre o arquivo diretamente com `open(path, "w")`.

---

## 4. Branding v3.1 & Auditoria do Termo `"Sejong"`

* **`data/release_notes.json` e `data/announcements.json`:** **0 ocorrências** do termo legado.
* **Paleta Brand Book v3.1 (60/20/12/8):** **0 ocorrências** de `#004C97` em `src/`.
* **Vazamento crítico na UI (`src/views/hangul_view.py:629`):**
  * `sample_chars = ["가", "나", "다", "한", "글", "세", "종", "ㄱ", "ㄴ", "ㄷ", "ㅏ", "ㅓ", "ㅗ"]` exibe os caracteres **"세", "종" (`세종`)** diretamente na aba de Caligrafia.
* **Fallbacks legítimos preservados:** `SEJONG_AUDIO_CACHE_DIR` (`audio_service.py:29`), `SEJONG_ADMIN_PIN` (`services.py:1348`), canonicalização `"estudante sejong"` → `"Estudante Saebom"` (`services.py:41`), leitura fallback `sejong_student_id`/`sejong_student_name` (`services.py:318,406,420`, `splash_view.py:170-171`).
* **Resíduos internos pendentes de padronização para `saebom_*`:** `_sejong_student_id` / `_sejong_session_id` e gravação de chaves `sejong_student_id`/`sejong_student_name` em `src/services.py` (`L310-444,723`), `src/views/onboarding_view.py` (`L59-60,72-73,92`), `src/views/home_view.py` (`L165,169`), `src/views/splash_view.py` (`L154-155,175,177-178`) e `src/views/admin_view.py:215`.
* **`scripts/` e `.github/`:** `scripts/pedagogical_report.py:29,132`, `scripts/prewarm_audio.py:4,56,71`, `scripts/audit_curriculum.py:2,4`, `scripts/bundle_all_typecast_audio.py:4`, `scripts/setup_oci_server.sh:3,10,36,38,40,54` e `.github/workflows/ci.yml:1,54` ainda mantêm referências de marca/variável legada (além do termo em `unit_1b_05` `"세종식당이 어디에 있어요?"` / `unit_01.json:477` ligado ao material didático).

---

## 5. Currículo 1A/1B, `audit_curriculum.py`, Assets e Dados Mutáveis (Zero PII)

* **`data/curriculum.json` (23 entradas, `number` 0–22):**
  * **Hangul (`unit_intro`, `number: 0`):** 1 unidade (`is_unlocked: true`, sem campo `"book"` explícito — default `"1A"` em `models.py:16`; `title_kr="한글을 배워요"` difere de `unit_intro.json:3`).
  * **Livro 1A (`unit_01`–`unit_10`, `number` 1–10):** 10 unidades (omitem `"book"` no JSON).
  * **Livro 1B (`unit_1b_01`–`unit_1b_12`, `number` 11–22):** 12 unidades (`"book": "1B"` explícito).
* **Totais dos 23 JSONs (`data/units/*.json`, 100% válidos via Pydantic):**
  * **Hangul (`unit_intro.json`):** 6 vogais, 10 consoantes simples, 4 aspiradas, 5 tensas, 7 sílabas, 5 regras `batchim`; **9 exercícios** (8 `multiple_choice`, 1 `calligraphy` [`wb_intro_q1`]; 4 com prefixo `wb_*`).
  * **Livro 1A:** **130** itens de vocabulário (22 na `unit_01`, 12 em `unit_02`–`unit_10`), **20** tópicos gramaticais (41 exemplos), **11** notas culturais, **130** exercícios (90 `multiple_choice`, 30 `drag_and_drop_sov`, 10 `calligraphy`, 0 `order_words`).
  * **Livro 1B:** **136** itens de vocabulário (9–15/un.), **24** tópicos gramaticais (48 exemplos), **12** notas culturais, **60** exercícios (24 `multiple_choice`, 12 `order_words`, 12 `drag_and_drop_sov`, 12 `calligraphy`).
  * **Total Global:** **266** itens de vocabulário (`241` palavras únicas; `23` repetidas) → **266 flashcards**; **44** tópicos gramaticais (**89** exemplos); **23** notas culturais; **199** exercícios únicos (`122` `multiple_choice`, `42` `drag_and_drop_sov` → `42` Sentence Builder, `23` `calligraphy`, `12` `order_words`, `0` `listening`). Observação: `unit_01` tem `'한국 노래 (K-pop)'` em `vocab.example_kr`.
* **Gabaritos 1A/1B, 띄어쓰기 e `'✅ Terminei'`:** todas as **22** frases multi-palavra de caligrafia aplicam `띄어쓰기` correto (`WongojiMultiCellWidget` renderiza células `␣` e as exclui do IoU em `L68-75,250-263,499-501`), o gatilho exclusivo é `"✅ Terminei"` (`quiz_widget.py:532-541`), e as estruturas oficiais 1A/1B estão presentes (`밥을 먹어요`, `집에서 쉬었어요`, `자전거를 타요`, `한국에 가고 싶어요`, `커피를 좋아해서`, `불고기를 자주 먹어요`, `자전거를 못 타요`, `티셔츠를 입어요`).
* **Execução de `scripts/audit_curriculum.py` (somente leitura, exit code `0`):** reportou `23` unidades, `266` vocabulários, `44` tópicos gramaticais, `190` exercícios (pula as 9 questões de `unit_intro` via `continue` em `L67-72`; total real = **199**), `42` SOV, `266` flashcards, `42` Sentence Builder — **100% aprovados**.
* **`data/release_notes.json` (`2.654 B`) e `data/announcements.json` (`406 B`):** 5 highlights válidos; 1 comunicado ativo (`ann_init_01`) dentro dos limites `MAX_*`.
* **Inventário de `assets/` (Total: `1.375` arquivos / `164.638.783` bytes):**
  * `assets/branding/`: **21 arquivos** (`272.471 B`: 14 `.png`, 6 `.svg`, 1 `.ico`).
  * `assets/fonts/`: **13 arquivos** (`28.924.060 B`: 10 `.otf` + 3 `.ttf`, incluindo `Pretendard` e `Kyobo Handwriting 2025`).
  * `assets/silent.wav`: **1 arquivo** (`8.864 B`, mono 16-bit, 44.100 Hz, 0,1000 s).
  * `assets/audio_cache/`: **1.328 arquivos** (`135.405.576 B`: `672 .mp3` = `42.718.202 B` + `656 .wav` = `92.687.374 B`; cobre **616/616** textos curriculares em `.mp3` e `.wav`).
  * `assets/mouth_shapes/`: **6 SVGs** (`4.458 B`).
  * `assets/spatial/`: **5 SVGs** (`5.627 B`).
  * `assets/stroke_order/jamo_strokes.json`: **1 arquivo** (`17.727 B`, `639` linhas, `51` jamo: 19 consoantes, 21 vogais, 11 compostos).
* **Dados mutáveis em `data/` (apenas agregados, ZERO PII):**
  * `data/cache/`: **640 arquivos**, `1` subdiretório (`audio`), `42.272.885 bytes` (`635 .mp3` + `5 .wav`).
  * `data/reports/`: **1 arquivo** (`.md`), `1.787 bytes`.
  * `data/sessions/`: **18 arquivos** (`.json`), `4.832 bytes`.
  * `data/telemetry/`: **208 arquivos / 119.335 bytes** antes da execução ao vivo da suíte de testes → **215 arquivos / 131.124 bytes** após a execução completa da suíte (em `data/telemetry/*.jsonl`).

---

## 6. Segurança OWASP/MITRE, Infraestrutura, Lacunas de `d6289d5` (`BUG-13`) & `audit_report.md`

* **Verificações locais executadas:**
  * `.venv\Scripts\python.exe -m compileall src tests` → **PASSOU (`exit code 0`)**.
  * Secret scan (`ci.yml:46`, `sejong2026` em `src/` e `docker-compose.yml`) → **0 ocorrências** (no repo rastreado fora de `Documentacao/` e `audit_report.md`, aparece apenas em `ci.yml:46-47` e asserções negativas de `test_admin_service.py:11,29`).
* **Controles de Segurança na Aplicação:** `AdminService` (`src/services.py:1327-1491`) opera fail-closed, compara segredos com `hmac.compare_digest` (`L1390`), aplica lockouts Tier 1 (`5` → `30s`) / Tier 2 (`10` → `300s`), tokens `secrets.token_urlsafe(32)` (`3600s`) e auditoria `security_audit` Zero-PII; `StudentIdentity` / `verify_and_restore_student` exigem recovery code salted SHA-256 + `hmac.compare_digest` (`L709`); `TelemetryService` rotaciona a cada `5000` eventos; `AnnouncementService` aplica `MAX_*` (`120`/`1000`/`50`) e remoção de `\x00`.
* **Lacunas residuais do commit `d6289d5` (detalhadas em [`BUG-13`](../Bugs_Criticos/bug_13_hardening_owasp_mitre_container_caddy_auditoria.md)):**
  1. CSP do `Caddyfile:33` bloqueia `https://www.gstatic.com`, worker `blob:` e `'wasm-unsafe-eval'` necessários ao boot Web sem `no_cdn=True`, além de `font-src 'self' data:` bloquear `fonts.gstatic.com` (com `src/theme.py:287-288` apontando para `fonts.googleapis.com`).
  2. Bloco único `:80, :443` em `Caddyfile:3,30` emite HSTS em HTTP `:80` (violação RFC 6797 §7.2) e quebra redirect automático HTTP→HTTPS.
  3. Conflito entre `USER saebomuser` (`Dockerfile:29-37`, UID `10001`) e bind mounts de host (`docker-compose.yml:18-22` `./data/*` e `./data/announcements.json`).
  4. `AdminService.get_global_kpis()` (`src/services.py:1627,1635`) mistura eventos `security_audit` nos KPIs pedagógicos, e `admin_view.py:215` usa `client_key` compartilhado `"admin_client"` em acessos diretos `/admin`.
  5. `docker-compose.yml:12` relaxou para `${SAEBOM_ADMIN_PIN:-}` e `AnnouncementService._save_announcements()` (`L40-48`) realiza gravação não-atômica direta.
* **Infraestrutura adicional:** `.dockerignore` não exclui `.agents/`, `Documentacao/`, `tests/` e `audit_report.md`; `scripts/setup_oci_server.sh` ainda abre porta `8554` no `iptables` (`L22`), usa marca legada (`L3,10,36,54`) e não prepara permissões UID `10001`; `requirements.txt` mantém `gTTS>=2.5.0` morto (`L5`) e `python-dotenv>=1.0.0` (`L6`) redundante com `main.py:6-23`.
* **Comparativo dos 24 achados de [`audit_report.md` (arquivado)](audit_report_historico.md):**
  * **7 Resolvidos:** `#1` (`view_pop` / `_history` em `src/router.py`), `#2` (`assets/silent.wav`), `#4` (piso `half_life >= 0.2`), `#9` (normalização `[.?!,~;:]`), `#12` (`TYPECAST_API_KEY` no compose), `#13` (remoção `DEFAULT_PIN`), `#15` (remoção do slice `filename[8:-5]`).
  * **9 Parciais:** `#3` (`Noto Sans KR`/`Inter` CSS URLs ainda em `theme.py:287-288`), `#6` (`AnnouncementService` e `TelemetryService.record` sem lock), `#11` (`hard=0.6`, mas dois motores SRS coexistem), `#14` (`admin_view.py:169` ainda limpa `page.views` antes do rebuild), `#16` (`except: pass` remanescentes em views/services), `#17` (`import random` redundante em `quiz_widget.py:180`), `#21` (`tooltip` em 43 locais, `semantics_label` = 0), `#22` (`load_local_env()` manual vs `python-dotenv`), `#24` (`startswith("unit_1b_")` ainda usado em `home_view.py` e `services.py`).
  * **8 Pendentes:** `#5` (`_sessions` sem evicção), `#7` (`VocabCard.play_audio_animation` síncrona), `#8` (Windows Desktop sem fallback Google TTS), `#10` (`except TypeError` em `quiz_widget.py:500-503`), `#18` (`page.router`/`page.audio_service` dinâmicos), `#19` (`numbers_data` hardcoded em `hangul_view.py:412-423`), `#20` (rebuild total nas views de exercício), `#23` (`gTTS>=2.5.0` morto em `requirements.txt`).

---

## 7. Testes Automatizados ao Vivo, Segurança, Playwright E2E & Cobertura

* **Ambiente verificado:** `.venv\Scripts\python.exe` — Python `3.12.14` (`pytest 9.1.1`, `anyio 4.14.2`, `pytest-asyncio 1.4.0`, `flet 0.85.3`, `playwright 1.62.0`; `coverage`/`pytest-cov` ausentes).
* **Inventário (`32` arquivos `test_*.py`, `459` itens coletados + `21` subtestes):**
  * Segurança/Auth/Privacidade/Infra (4 arqs, 19): `test_admin_auth_hardening.py` (6), `test_student_identity_security.py` (5), `test_telemetry_privacy_and_rotation.py` (2), `test_infrastructure_security.py` (6).
  * Serviços/Persistência/Identidade/Telemetria (6 arqs, 57): `test_data_service.py` (8), `test_progress_service.py` (25), `test_active_recall.py` (7), `test_student_identity_and_persistence.py` (2), `test_student_name_case_and_merge.py` (6), `test_telemetry_service.py` (9).
  * Admin/Comunicação/Release Notes (3 arqs, 25): `test_admin_service.py` (5), `test_notification_and_announcements.py` (10), `test_whats_new_dialog.py` (10).
  * Áudio/Háptico (3 arqs, 23): `test_audio_service.py` (9), `test_audio_prewarm.py` (7), `test_haptic_service.py` (7).
  * Currículo/Modelos (4 arqs, 17 + 21 subtestes): `test_curriculum_integrity.py` (5), `test_unit_1b_content.py` (5), `test_workbook_quiz_content.py` (2 + 11 subtestes), `test_sov_drag_drop.py` (5 + 10 subtestes).
  * Caligrafia/Jamo/Quiz/Neurociência (6 arqs, 239): `test_jamo_utils.py` (24), `test_calligraphy_widget.py` (18), `test_quiz_calligraphy.py` (13), `test_quiz_widget.py` (173), `test_phase1_sensory_features.py` (5), `test_phase2_interactive_features.py` (6).
  * UI/Tema/Branding/Router/Views (4 arqs, 58): `test_theme.py` (6), `test_branding_assets.py` (25), `test_router.py` (6), `test_views_rendering.py` (21).
  * E2E/Playwright (2 arqs, 21): `test_e2e_full_coverage.py` (16), `test_playwright_e2e.py` (5).
* **Execuções Reais desta Auditoria:**
  * **Bateria de Segurança (`GEMINI.md`):** `19 passed in 1.31s` (`0 failed`, `0 skipped`, `0 warnings`) + `test_p4_admin_security_barrier` → **`1 passed, 4 deselected in 26.01s`**.
  * **Suíte Completa (`.venv\Scripts\python.exe -m pytest tests/ -v`):** **`459 passed, 21 subtests passed in 34.76s`** (`0 failed`, `0 skipped`, `0 warnings`).
  * **Playwright E2E:** **5/5 PASSED** com regeneração das 5 screenshots em `tests/screenshots/` (`2026-11-23 21:25:36–21:25:51`) e 5 hashes MD5 distintos (`p2_splash_screen.png` `6AD3690166D726655EF71A88C2D072F3`, `p3_onboarding_screen.png` `A4ABAF9CBDD36C525B05863F84FA2F0D`, `p4_admin_login.png` `7B8A5C5C6229E5684B905B685CE1C2B0`, `p5_hangul_view.png` `5427F85A0E91382DBB9AF6D284CCA357`, `p5_hangul_drawn.png` `F120CE3D11BF0EE3C7002B53CB9899AF`).
* **Lacunas de Cobertura:** Sem teste dedicado direto para `src/task_utils.py`, `src/components/flashcard_widget.py`, `src/components/layout.py`, `FullscreenService`, `StudentIdentity.set_student_id`, `ProgressService.{has_recovery_code,get_memory_node,save_memory_node,get_study_days}`, `DataService._flashcard_difficulty` e `Responsive`; `flashcards_view.py`, `review_view.py`, `quiz_view.py`, `onboarding_view.py` e `lesson_view.py` possuem apenas *smoke instantiation*; no Playwright faltam fluxos autenticados de `/admin`, `/onboarding`, `/home`, `/lesson`, `/quiz`, `/review`, `/flashcards` e verificação de autoplay `silent.wav`; `test_quiz_widget.py` não parametriza `unit_intro` nem as 23 questões `calligraphy`, e `test_curriculum_integrity.py::test_zero_romanization_policy` pula `unit_intro` e não inspeciona `grammar` ou `calligraphy.target_text`.

---

## 8. Estado da Documentação & Resumo deste Sync (`/saebom-docs-sync`)

### 8.1 Diagnóstico dos Documentos Fora do Escopo de Edição Imediata
* [`ROADMAP_MESTRE_COMPANION.md`](../Planos_e_Arquitetura/ROADMAP_MESTRE_COMPANION.md): congelado em `2026-08-19` (`v0.3.2-alpha`); omite `0.3.2-security` até `0.3.8-alpha`; lista como `PLANEJADO` itens já implementados (telemetria local da `0.5.0-alpha` e base do Teacher Companion `/admin` da `0.8.0-beta`), enquanto continuam realmente pendentes `src/engine/` (`0.4.0-alpha`), dashboard cognitivo do aluno (`0.5.0-alpha`), PostgreSQL/sync cloud (`0.6.0-beta`) e GA (`1.0.0`); mantém título legado, domínio antigo na `L72` e cabeçalho duplicado `Fase 4:` (`L80` e `L105`).
* [`MANUAL_DE_IDENTIDADE_SAEBOM.md`](../Design_e_Branding/MANUAL_DE_IDENTIDADE_SAEBOM.md): Seção 8 (`L217-233`) cataloga 15 arquivos de `assets/branding/`, omitindo 6 dos 21 arquivos existentes.
* [`DESIGN_SYSTEM_CHANGELOG.md`](DESIGN_SYSTEM_CHANGELOG.md): Seção de Tipografia (`L55-66`) ainda documenta `Inter`/`Noto Sans KR` sem cobrir a adoção de `Pretendard` + `Kyobo Handwriting 2025` na Rodada 4.
* [`estrategia_hospedagem_oci_always_free_vs_render.md`](../Planos_e_Arquitetura/estrategia_hospedagem_oci_always_free_vs_render.md): marcado como `VIGENTE`, mas ainda usa o nome antigo, domínio antigo e referencia `assets/audio_cache/` em vez de `data/cache/audio/`.
* [`Documentacao/Conceitos/`](../Conceitos/INDICE_CONCEITOS.md): 9 arquivos (incluindo `INDICE_CONCEITOS.md`) mantêm branding e tokens pré-rebranding como se fossem atuais.
* **Portabilidade de links `file:///`:** 137 links em 16 arquivos de `Documentacao/` (+30 em `audit_report.md`) usam caminhos absolutos locais (`file:///c:/Users/Pichau/Documents/sejong_companion/...`).

### 8.2 Arquivos Sincronizados Nesta Rodada (8 arquivos em `Documentacao/`, sem commit)
1. [`CHANGELOG.md`](CHANGELOG.md): diagrama ASCII atualizado para `v0.3.8-alpha`, métricas reais (`459 testes aprovados + 21 subtestes`), correção do CSP (`font-src 'self' data:;`), referência a `BUG-13` e suas 5 lacunas residuais, registro do commit `c7aa16e` em `[0.3.7-alpha]`, desambiguação dos dois títulos `[0.3.6-alpha]` e correção para `21` assets de branding.
2. [`bug_13_hardening_owasp_mitre_container_caddy_auditoria.md`](../Bugs_Criticos/bug_13_hardening_owasp_mitre_container_caddy_auditoria.md): criado no padrão completo de `saebom-docs-sync` com o hardening `d6289d5` e as 5 lacunas residuais abertas.
3. [`INDICE_BUGS.md`](../Bugs_Criticos/INDICE_BUGS.md): adicionada a entrada `BUG-13`.
4. [`relatorio_estado_atual_v0.3.8.md`](relatorio_estado_atual_v0.3.8.md): este relatório consolidado.
5. [`analise_estado_atual.md`](analise_estado_atual.md): preservado intacto com nota no topo apontando para este relatório.
6. [`INDICE_DOCUMENTACAO.md`](../INDICE_DOCUMENTACAO.md): link de `implementation_plan(v0.1.0-alpha).md` corrigido (`%28`/`%29`), `analise_estado_atual.md` marcado como histórico e entradas adicionadas para `relatorio_estado_atual_v0.3.8.md` e `BUG-13`.
7. `Documentacao/Planos_e_Arquitetura/implementation_plan(v0.1.0-alpha).md`: link da `L6` corrigido para [`CHANGELOG.md`](CHANGELOG.md).
8. [`Bem-vindo.md`](../Bem-vindo.md): wikilink órfão substituído por `[[INDICE_DOCUMENTACAO]]`.

---

## 9. Backlog Priorizado (P0 / P1 / P2) e Decisões Pendentes

### Prioridade P0 (Bloqueadores de Produção / Rebranding / Segurança)
1. **Corrigir CSP & HSTS no `Caddyfile` (e/ou ativar `no_cdn=True` em `main.py` + remover CSS Google Fonts em `src/theme.py:287-288`):** liberar `https://www.gstatic.com`, `worker-src 'self' blob:`, `'wasm-unsafe-eval'` (ou servir 100% local), separar bloco `:80` (redirect HTTPS) de `:443` (HSTS).
2. **Resolver permissões UID `10001` (`saebomuser`) × bind mounts (`docker-compose.yml` / `scripts/setup_oci_server.sh`):** garantir ownership `10001:10001` ou volumes adequados, remover abertura da porta `8554` do `iptables` em `setup_oci_server.sh:22` e evitar bind mount de arquivo único sobre `./data/announcements.json` se usar escrita atômica.
3. **Remover vazamento `"세"`, `"종"` em `src/views/hangul_view.py:629`** (`sample_chars`).
4. **Corrigir `admin_view.py:169` (`rebuild_view` não-atômico)** e **isolar `client_key` / excluir `security_audit` de `AdminService.get_global_kpis()`** (`src/services.py:1627,1635`; `src/views/admin_view.py:215`).

### Prioridade P1 (Bugs Funcionais & Consistência de Release)
1. **Corrigir `SpatialStage` (`object_img` fora do `ft.Stack` e ausência de botão `next_challenge()`)** e **completar `NumberTraining` (`NATIVE_MAP` `"10"`/`"0"` e desafio `OK`)**, além de conectar ou remover `AirParticleEffect`/`HapticService` órfãos.
2. **Resolver divergência `AudioService` Web (`data/cache/audio` vs `assets/audio_cache`)**, remover `ProgressService.set_student_name` duplicado (`src/services.py:600,716`), adicionar `asyncio.wait_for` nos `sp.set(...)` (`onboarding_view.py`, `home_view.py`) e corrigir `AnnouncementService._save_announcements` atômico.
3. **Sincronizar `__version__` (`src/__init__.py:3`) e `data/release_notes.json` (e `GEMINI.md` / `DESIGN.md`)** para `0.3.8-alpha` (ou versão oficial da próxima tag) e padronizar chaves internas `sejong_*` → `saebom_*` mantendo apenas fallback de leitura.

### Prioridade P2 (Manutenibilidade, Cobertura & Documentação)
1. **Atualizar `ROADMAP_MESTRE_COMPANION.md`, `estrategia_hospedagem_oci_always_free_vs_render.md`, `MANUAL_DE_IDENTIDADE_SAEBOM.md` (21 assets), `DESIGN_SYSTEM_CHANGELOG.md` e `Conceitos/*`.**
2. **Limpar dívida técnica e CI:** remover `gTTS` morto de `requirements.txt`, atualizar `.github/workflows/ci.yml` (`SAEBOM_ADMIN_PIN`, nome do workflow, check de `"sejong"`), mover `ORIGINAL_REQUEST.md` para `.gitignore` se desejado, e ampliar cobertura de testes em views/E2E (`silent.wav`, `FlashcardWidget`, `TaskUtils`).

### Decisões Pendentes para o Usuário
1. **Versão oficial atual:** promover `src/__init__.py`, `data/release_notes.json` e `GEMINI.md` para `0.3.8-alpha` agora ou preparar `0.3.9-alpha`/`0.4.0-alpha` após corrigir os P0/P1?
2. **Portabilidade dos links em `Documentacao/`:** converter os 137 links `file:///c:/Users/Pichau/Documents/sejong_companion/...` para links relativos POSIX (portáteis no GitHub e entre máquinas) ou manter `file:///` local?
3. **Sincronização Git (`develop`, `main` e `origin/main`):** integrar `origin/main` (`9dafd2f`, `README.md`) e promover as correções antes do merge de `security/mitre-owasp-hardening` → `develop` → `main`?
4. **`audit_report.md` na raiz:** arquivar em `Documentacao/Changelogs_e_Historico/` com nota de status histórico ou remover após resolver os 17 itens parciais/pendentes restantes?
