---
name: saebom-design-qa
description: >-
  Orquestra o planejamento visual e o Design QA automatizado do Saebom Companion
  (새봄 컴패니언) no padrão Brand Book v3.1: pesquisa de UX (Mobbin), prototipação
  no StitchMCP, auditoria de tokens DESIGN.md vs src/theme.py, contraste WCAG 2.1,
  invariantes Flet 0.85+ e regressão visual multi-viewport no Playwright. Use ao
  planejar novas telas/componentes ou validar qualidade visual antes de releases.
---

# Design & Brand QA — Saebom Companion (Brand Book v3.1)

## Quando Ativar
- **Modo A (Pré-Código):** antes de criar ou redesenhar telas e fluxos (ex.: Dashboard Cognitivo `v0.5.0-alpha`, Teacher Companion `v0.8.0-beta`).
- **Modo B (Pós-Código / Gate de QA):** após mudanças em `src/theme.py`, `src/views/`, `src/components/`, `DESIGN.md`, `assets/branding/` ou `assets/fonts/`.

---

## Modo A — Planejamento de Design Pré-Código

### 1. Benchmark Pedagógico & Pesquisa de UX
- Consultar as regras invioláveis em `GEMINI.md`, `DESIGN.md` e `Documentacao/Design_e_Branding/MANUAL_DE_IDENTIDADE_SAEBOM.md`.
- Quando aplicável, pesquisar padrões reais de interface com as skills do **Mobbin** (`search` e `redesign-screen`) adaptando à regra pedagógica: *"A tecnologia acompanha a pedagogia. Nunca compete com ela."*

### 2. Prototipação Integrada com `StitchMCP`
O Design System oficial está vinculado ao projeto Google Stitch **`10905381626038373944`** (`DESIGN.md`):
1. Sincronizar alterações de tokens via `upload_design_md` / `apply_design_system`.
2. Inspecionar telas existentes com `list_screens` / `get_screen`.
3. Gerar propostas ou variações visuais com `generate_screen_from_text`, `generate_variants` ou `edit_screens` antes de implementar em Flet Python.

### 3. Checklist Editorial Brand Book v3.1 (Aprovação Pré-Código)
- **Sistema Cromático 60/20/12/8:** Navy `#02060F` (60% território), Cream `#F7F4EC` & Slate `#9EA2AE` (20% leitura/estrutura), Violet `#8B4DFF` (12% `PRIMARY`), Gold `#FFAB22` (8% `ACCENT`) e Lilac `#B28AFF` (`SECONDARY`). Proibição total do antigo `#004C97`.
- **Tipografia Segura (Zero Tofu):** interface em **Pretendard** e caligrafia em **Kyobo Handwriting 2025**, servidas localmente em `assets/fonts/`.
- **Ergonomia e Grid:** escala 4 px, canal de leitura máximo `600px`, alvos táteis `>= 48px` (áudio `44–48px`) e breakpoints `320px` (Compact), `390px` (Medium) e `1024px` (Expanded).
- **Invariantes Culturais:** zero menções visuais à marca legada, zero flores de cerejeira decorativas literais e zero estética infantilizada.

---

## Modo B — Design QA Automatizado Pós-Código

### 1. Auditoria Estática e de Tokens (`scripts/design_qa_audit.py`)
Executar o auditor automatizado (exit code `0` = aprovado; `1` = falha crítica):
```powershell
.venv\Scripts\python.exe -m scripts.design_qa_audit
```
Valida automaticamente:
1. `design_md_theme_sync` — sincronia dos 6 tokens mestres entre `DESIGN.md` e `src/theme.py` (`Colors`).
2. `wcag_contrast` — cálculo de luminância sRGB e contraste WCAG 2.1 em Dark Mode e Light Mode.
3. `flet_ui_invariants` — varredura AST/regex em `src/` para bloquear `#004C97`, `ft.ImageFit`, `ft.ElevatedButton` (`BUG-02`), `letter_spacing=` direto em `ft.Text` (`BUG-02`), `ft.Image(src=...)` sem `/` inicial (`BUG-11`), concatenação dinâmica `#RRGGBBAA` (`BUG-03`), URLs externas `fonts.googleapis.com`, sobrescrita `self.page =` em subclasses Flet e caracteres legados em `sample_chars`, além de emitir advisory (`BUG-05`) para `ft.BoxShadow` fora de `src/theme.py`.
4. `branding_and_fonts_assets` — integridade dos JSONs públicos (`release_notes.json`, `announcements.json`), fontes locais (`Pretendard`, `KyoboHandwriting2025lyb`) e todos os `21` assets de `assets/branding/`.

### 2. Testes Automatizados de Design System & Assets
```powershell
.venv\Scripts\python.exe -m pytest `
  tests/test_theme.py `
  tests/test_branding_assets.py `
  tests/test_design_qa_pipeline.py -v
```

### 3. Regressão Visual Multi-Viewport (Playwright + Pillow)
Executar a suíte Playwright para auditar renderização CanvasKit real, ausência de tela preta (`BUG-11`), ausência de *tofu* em Hangul (`BUG-07`) e unicidade MD5 entre rotas:
```powershell
.venv\Scripts\python.exe -m pytest tests/test_playwright_e2e.py -v
```
*(Em auditorias visuais completas de novas telas, capturar screenshots adicionais nos viewports `320x715`, `390x844` e `1024x768` em Dark e Light mode para inspeção de overflow e ergonomia.)*

---

## Topologia Recomendada com `/swarm`
- **Fluxo Pré-Código (Planejamento):**
  - **`ux-researcher`**: pesquisa referências (Mobbin) e mapeia jornada pedagógica.
  - **`stitch-designer`**: atualiza `DESIGN.md` no `StitchMCP` e gera protótipos/variantes.
  - **`brand-reviewer`**: revisa aderência ao Brand Book v3.1 e ergonomia antes do código.
- **Fluxo Pós-Código (Auditoria):**
  - **`design-static`**: executa `scripts.design_qa_audit` + `test_theme.py` + `test_branding_assets.py` + `test_design_qa_pipeline.py`.
  - **`design-visual`**: executa `test_playwright_e2e.py` e analisa screenshots multi-viewport.

## Critérios de Bloqueio vs Advisories WCAG
1. **Bloqueadores (`FAIL`):** dessincronia `DESIGN.md` ↔ `Colors`, texto principal (`text`) < `7.0:1`, texto secundário/apoio (`text_sec`, `secondary`, `accent`) < `4.5:1` no Dark Mode, `primary` < `3.0:1` sobre fundo base, qualquer violação AST Flet 0.85+ (`BUG-02/03/11`, `self.page =`), `#004C97`, fonte externa `fonts.googleapis.com` ou asset de branding/fonte ausente.
2. **Advisories (`WARN`, não bloqueantes):** `ft.BoxShadow` pontual fora de `src/theme.py` (`BUG-05`) e pares de acento decorativo/secundário abaixo de `4.5:1` em Light Mode ou em cards escuros (`card_bg`), sinalizados para aprimoramento futuro sem bloquear textos grandes/ícones.
