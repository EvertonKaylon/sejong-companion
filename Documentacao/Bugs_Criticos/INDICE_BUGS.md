# Catalogo de Bugs Criticos e Resoluções — Sejong Companion

Este documento cataloga os bugs mais complexos e desafiadores identificados e resolvidos durante o desenvolvimento do aplicativo **Sejong Companion (세종학당 컴패니언)** em Flet (Python) / Flutter Engine.

---

## 📌 Índice de Bugs Catalogados

| ID | Nome / Diagnóstico | Severidade | Categoria | Arquivo Detalhado |
| :--- | :--- | :---: | :--- | :--- |
| **BUG-01** | Corrida de Montagem de Áudio (`flet-audio`) & Vazamento em `page.services` | 🔴 Crítica | Áudio / Ciclo de Vida | [bug_01_flet_audio_corridas_e_page_services.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_01_flet_audio_corridas_e_page_services.md) |
| **BUG-02** | Quebra de Sintaxe no Flet 0.85+ (`letter_spacing` e `text=` em Buttons) | 🟠 Alta | Flet API / Tipagem | [bug_02_sintaxe_flet_085_letter_spacing_e_button_args.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_02_sintaxe_flet_085_letter_spacing_e_button_args.md) |
| **BUG-03** | Inversão de Cores no Parser HEX de 8 Dígitos (`#AARRGGBB` vs `#RRGGBBAA`) | 🟡 Média | Flutter UI / Color System | [bug_03_inversao_hex_alpha_aarrggbb_flet_flutter.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_03_inversao_hex_alpha_aarrggbb_flet_flutter.md) |
| **BUG-04** | Bloqueio de Rolagem Vertical (`ft.ListView` dentro de `ft.View`) | 🟡 Média | Layout / Scroll Engine | [bug_04_bloqueio_de_scroll_listview_e_appbar.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_04_bloqueio_de_scroll_listview_e_appbar.md) |
| **BUG-05** | Instabilidade de Memória por Falta de Teto (`w_ampa` / Neuro-Tip) | 🟡 Média | Performance / Tokens | [bug_05_w_ampa_simulador_neuromorfico_e_performance.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_05_w_ampa_simulador_neuromorfico_e_performance.md) |
| **BUG-06** | Falha de Bind de Redes no Windows (`FLET_SERVER_IP="0.0.0.0"`) | 🟠 Alta | Network / Windows OS | [bug_06_bind_windows_flet_server_ip.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_06_bind_windows_flet_server_ip.md) |
| **BUG-07** | Renderização de Tofu (Caixas Vazias) em Hangul por Fallback de Fonte | 🟠 Alta | Tipografia / Flutter Web | [bug_07_flutter_font_fallback_tofu_hangul.md](file:///c:/Users/Pichau/Documents/sejong_companion/Documentação/Bugs_Criticos/bug_07_flutter_font_fallback_tofu_hangul.md) |

---

## 🛠️ Como Utilizar Este Catálogo

Cada arquivo individual contém:
1. **Descrição Sintomática**: Como o erro se manifesta para o usuário ou no console.
2. **Causa Raiz Técnica**: A explicação exata do comportamento subjacente no motor Flet/Flutter ou SO.
3. **Solução Código Antes vs Depois**: Snippets práticos demonstrando o código quebrado e o código corrigido.
4. **Regra Preventiva**: Como evitar a reintrodução desse erro em atualizações futuras.
