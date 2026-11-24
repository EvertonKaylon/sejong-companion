# Arquitetura Flet e Flutter Engine

**Conceito Relacionado:** [[Desenvolvimento_Multiplataforma_Python]] | [[Integracao_TTS_Typecast_e_Audio]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[analise_stack_multiplataforma]] | [[MANUAL_DE_IDENTIDADE_SAEBOM]]  
**Bugs Catalogados:** [[bug_01_flet_audio_corridas_e_page_services]] | [[bug_04_bloqueio_de_scroll_listview_e_appbar]] | [[bug_02_sintaxe_flet_085_letter_spacing_e_button_args]] | [[bug_06_bind_windows_flet_server_ip]] | [[bug_11_tela_preta_flutter_web_assets_e_views_router]]  

---

## 1. ⚡ Visão Geral da Arquitetura Interna

O **Flet** (versão 0.85.3 no **Saebom Companion**) permite construir aplicações nativas multiplataforma utilizando **Python** na camada de lógica e o **Flutter Engine** na camada de renderização gráfica.

Entender o funcionamento interno dessa ponte (*bridge*) é essencial para evitar vazamentos de memória, telas pretas no CanvasKit Web, gargalos de performance e erros de ciclo de vida de componentes.

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                   CAMADA DE LÓGICA (PYTHON)                      │
 │                                                                  │
 │   main.py ──> Router (src/router.py) ──> Views (src/views/*.py)  │
 │                        │                                         │
 │                        ▼                                         │
 │           Árvore de Controles (Controls Tree)                    │
 └────────────────────────┬─────────────────────────────────────────┘
                          │
                          │ Comunicação assíncrona (WebSocket/JSON)
                          │ Protocolo Delta Patching
                          ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                 CAMADA DE RENDERIZAÇÃO (FLUTTER)                 │
 │                                                                  │
 │    Flet Client (Dart / Flutter CanvasKit / Skwasm / Impeller)    │
 │                        │                                         │
 │                        ▼                                         │
 │              GPU / Tela Nativa (Web/Android/iOS)                 │
 └──────────────────────────────────────────────────────────────────┘
```

---

## 2. 🔬 Componentes Fundamentais da Engine

### A. O Ciclo de Vida da `ft.Page` e a Árvore de Controles
A `ft.Page` representa a raiz da sessão de usuário. Cada elemento visual (`ft.Text`, `ft.Container`, `ft.View`) é uma subclasse de `ft.Control`.

Quando uma propriedade de um controle é alterada em Python (ex: `text.value = "안녕하세요"`), a mudança **não desenha na tela imediatamente**. Somente quando `update()` é invocado (sempre protegido por `try ... except Exception: pass` em widgets reutilizáveis para suportar testes headless), o Flet calcula o *diffing* e transmite o *delta patch* via WebSocket para o Flutter Client redesenhar o Canvas. Além disso, em subclasses de `ft.Control`, a propriedade `self.page` é somente leitura — referências manuais devem usar atributo privado (ex.: `self._page`).

### B. Serviços Globais, `page.overlay` e Isolamento `assets/` vs. `data/`
Controles e serviços de ciclo de vida longo — como `page.audio_service` (`flet_audio.Audio`), `SnackBar` ou `AlertDialog` — não pertencem a uma `View` transitória.

- **`page.overlay` / `page.audio_service`**: Garante que o player singleton de áudio (incluindo o destravamento mudo com `silent.wav`) e diálogos globais sobrevivam à navegação entre rotas sem exceções `Control not found`.
- **`assets/` estritamente Read-Only vs. `data/` mutável**: Toda imagem servida por `ft.Image(src=...)` deve iniciar com `/` (ex.: `/branding/app_icon_512.png`) e usar `ft.BoxFit.CONTAIN` / `ft.BoxFit.COVER` (nunca `ft.ImageFit`, descontinuado), evitando HTTP 404 em rotas aninhadas do CanvasKit (`BUG-11`). Dados mutáveis gravados em runtime (`data/cache/audio/`, `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/announcements.json`) ficam estritamente isolados em `data/`.

### C. Cálculo de Layout, Scroll Engine e Transição Atômica de Views
O Flutter Engine calcula o tamanho dos elementos por restrições descendentes (*Constraints go down, Sizes go up, Parent sets position*).

- **Scroll em Views:** Usar `scroll=ft.ScrollMode.AUTO` e `appbar=app_bar` diretamente em `ft.View(...)`, evitando `ft.ListView` aninhado sem `expand=True` (`BUG-04`). Em canvas de desenho sobre telas roláveis, não alternar `Column.scroll = None` dinamicamente — adotar o padrão **Focus Mode** em `AlertDialog` (`BUG-10`).
- **Transição Atômica no `Router`:** Nunca executar `page.views.clear()` antes de construir a nova view com sucesso, evitando lista vazia e tela preta (`BUG-11`).
- **Timeouts Assíncronos:** Chamadas assíncronas ao cliente (`SharedPreferences.get` / `.set`) no carregamento ou onboarding devem utilizar `asyncio.wait_for(..., timeout=0.8)`.

---

## 3. 🚨 Análise de Bugs Críticos da Arquitetura

### 1. Corrida de Montagem e Destruição de Áudio ([[bug_01_flet_audio_corridas_e_page_services]])
- **O Problema**: Instanciar `ft.Audio()` dentro de views locais do quiz causava `Control not found` ao trocar de rota durante a reprodução.
- **Solução Arquitetural**: Serviço singleton `AudioService` em `src/audio_service.py` ligado à página (`page.audio_service`), mantendo o mesmo player vivo na sessão.

### 2. Quebra de Rolagem na View ([[bug_04_bloqueio_de_scroll_listview_e_appbar]])
- **O Problema**: `ListView` interno sem `expand=True` colapsava o viewport e cortava os cartões.
- **Solução Arquitetural**: `scroll=ft.ScrollMode.AUTO` e `appbar=app_bar` no construtor raiz de `ft.View()`.

### 3. Atualização de Sintaxe Flet 0.85+ ([[bug_02_sintaxe_flet_085_letter_spacing_e_button_args]])
- **O Problema**: Argumentos descontinuados (`letter_spacing=` direto, `text=` em botões, `ft.ElevatedButton`, `ft.ImageFit`) quebravam a montagem.
- **Solução Arquitetural**: Uso exclusivo de `style=ft.TextStyle(letter_spacing=...)`, `ft.Button("Texto", ...)` / `content=...` e `ft.BoxFit.CONTAIN`.

### 4. Tela Preta no Flutter Web & Deep Links ([[bug_11_tela_preta_flutter_web_assets_e_views_router]])
- **O Problema**: Caminhos relativos de imagem sem `/`, limpeza prematura de `page.views` e sobrescrita da rota inicial em `main.py` causavam colapso visual ou perda de deep links (`/admin`, `/hangul`).
- **Solução Arquitetural**: Prefixos `/` em `ft.Image`, `Router.render_route` com construção prévia + fallback de emergência e leitura de `page.route` no entrypoint.

---

## 4. 🛠️ Padrão de Código Recomendado para Views

```python
# Estrutura Padrão de View no Saebom Companion (Brand Book v3.1 + Flet 0.85+)

import flet as ft
from ..theme import get_theme_colors, Styles


def exemplo_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)

    # 1. Definição da AppBar Nativa
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=colors["primary"],
            tooltip="Voltar para o início",
            on_click=lambda _: page.router.navigate_to("/home"),
        ),
        title=ft.Text(
            "Título da Tela",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=colors["text"],
        ),
        bgcolor=colors["surface"],
        elevation=0,
    )

    # 2. Construção dos Controles Principais com Tokens Únicos
    content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text("Conteúdo com scroll nativo e performático", color=colors["text"]),
                bgcolor=colors["card_bg"],
                border_radius=Styles.BORDER_RADIUS_MD,
                border=ft.Border.all(1, colors["border"]),
                padding=16,
                shadow=Styles.CARD_SHADOW,
            ),
        ],
        spacing=16,
    )

    # 3. Retorno da View com Scroll Raiz Nativo
    return ft.View(
        route="/exemplo",
        appbar=app_bar,
        controls=[content],
        scroll=ft.ScrollMode.AUTO,  # Gerenciado pela View
        bgcolor=colors["bg"],       # Midnight Navy (#02060F) ou Cream (#F7F4EC)
        padding=16,
    )
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🎙️ Integração de Áudio TTS: [[Integracao_TTS_Typecast_e_Audio]]
- 📱 Desenvolvimento Multiplataforma: [[Desenvolvimento_Multiplataforma_Python]]
- 🚨 Catálogo de Bugs: [[INDICE_BUGS]]
