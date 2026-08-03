# 📚 Central de Documentação — Sejong Companion (세종학당 컴패니언)

Bem-vindo ao repositório central de documentação e conhecimento do projeto **Sejong Companion**. Este espaço foi organizado para fácil navegação via [Obsidian](https://obsidian.md) com suporte completo a mapas de rede (Graph View) e wikilinks (`[[NomeDoConceito]]`).

---

## 🗂️ Estrutura de Documentos e Conhecimento

### 🧠 1. Mapa de Conceitos do Projeto (`/Conceitos`)
- 📌 **[[INDICE_CONCEITOS]]** — Mapa mestre de teoria, arquitetura e conceitos do projeto.
- 📐 **[[SDD_Spec_Driven_Development]]** — Metodologia Spec-Driven Development e Single Source of Truth.
- ⚡ **[[Arquitetura_Flet_e_Flutter_Engine]]** — Bridge Python/Flutter, CanvasKit e gerenciamento de `page.overlay`.
- 🎨 **[[Design_System_e_Tokens_Semanticos]]** — Papéis semânticos, modo escuro Midnight Blue e notação HEX `#AARRGGBB`.
- 🔤 **[[Tipografia_Bilingue_e_CJK]]** — Estratégia dual Pretendard + 설립체 (Seollip-che) e prevenção de tofu.
- 📱 **[[Desenvolvimento_Multiplataforma_Python]]** — Base única Python para Web, Android e iOS.
- 🎮 **[[Neuropedagogia_e_Gamificacao]]** — Cronobiologia, repetição espaçada e máquina de estados de quiz.
- 🎙️ **[[Integracao_TTS_Typecast_e_Audio]]** — Arquitetura de reprodução de voz natural em coreano com `AudioService`.

---

### 🎯 2. Planos e Arquitetura (`/Planos_e_Arquitetura`)
- 🎨 **[Plano_UIUX_Flet_Sejong_Companion.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Planos_e_Arquitetura/Plano_UIUX_Flet_Sejong_Companion.md)** — Guia mestre de UI/UX, Design Tokens, tipografia e boas práticas Flet.
- 📋 **[plano_ensino_implicito_neurociencia.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Planos_e_Arquitetura/plano_ensino_implicito_neurociencia.md)** — Plano de refatoração para ensino de coreano implícito sem avisos por escrito.
- 📋 **[implementation_plan.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Planos_e_Arquitetura/implementation_plan.md)** — Plano de implementação técnica do aplicativo, estrutura de lições e roteiro.
- ⚙️ **[analise_stack_multiplataforma.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Planos_e_Arquitetura/analise_stack_multiplataforma.md)** — Análise comparativa da stack Python/Flet vs Next.js/Tailwind e viabilidade cross-platform.

---

### 🔬 3. Viabilidade e Pesquisa (`/Viabilidade_e_Pesquisa`)
- 🧠 **[didactic_neuroscience_korean_ptbr.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Viabilidade_e_Pesquisa/didactic_neuroscience_korean_ptbr.md)** — Estudo mestre neuropedagógico para falantes de PT-BR com ensino 100% implícito.
- 📖 **[viabilidade_sejong_companion.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Viabilidade_e_Pesquisa/viabilidade_sejong_companion.md)** — Estudo de viabilidade educacional com base no material do Sejong Hakdang.
- 🇰🇷 **[viabilidade_app_coreano.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Viabilidade_e_Pesquisa/viabilidade_app_coreano.md)** — Análise pedagógica para ensino de Hangul e gramática SOV a brasileiros.

---

### 📜 4. Histórico e Changlog (`/Changelogs_e_Historico`)
- 🚀 **[CHANGELOG.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Changelogs_e_Historico/CHANGELOG.md)** — Registro de versões e funcionalidades entregues.
- 🎨 **[DESIGN_SYSTEM_CHANGELOG.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Changelogs_e_Historico/DESIGN_SYSTEM_CHANGELOG.md)** — Histórico de evolução dos tokens de cores e temas.
- 🚶 **[walkthrough.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Changelogs_e_Historico/walkthrough.md)** — Guia passo a passo de verificação manual e validação.

---

### 🚨 5. Catálogo de Bugs Críticos (`/Bugs_Criticos`)
- 📌 **[INDICE_BUGS.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/INDICE_BUGS.md)** — Índice geral de erros complexos resolvidos.
- 🔴 **[BUG-01: Áudio e page.services](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_01_flet_audio_corridas_e_page_services.md)** — Solução para corridas de montagem no player TTS.
- 🟠 **[BUG-02: Sintaxe Flet 0.85+](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_02_sintaxe_flet_085_letter_spacing_e_button_args.md)** — Adequação a `ft.TextStyle` e parâmetros de botões.
- 🟡 **[BUG-03: Inversão HEX `#AARRGGBB`](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_03_inversao_hex_alpha_aarrggbb_flet_flutter.md)** — Ajuste de cores de opacidade em quiz.
- 🟡 **[BUG-04: Bloqueio de Scroll](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_04_bloqueio_de_scroll_listview_e_appbar.md)** — Correção de layout e scroll da view.
- 🟡 **[BUG-05: Teto de Memória](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_05_w_ampa_simulador_neuromorfico_e_performance.md)** — Otimização de alocação de objetos em renderização.
- 🟠 **[BUG-06: Bind Windows `127.0.0.1`](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_06_bind_windows_flet_server_ip.md)** — Resolução de erros de rede no SO Windows.
- 🟠 **[BUG-07: Glifos Tofu em Hangul](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_07_flutter_font_fallback_tofu_hangul.md)** — Solução de fonte unificada Pretendard.
