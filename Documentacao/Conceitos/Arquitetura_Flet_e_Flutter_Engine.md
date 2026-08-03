# Arquitetura Flet e Flutter Engine

**Conceito Relacionado:** [[Desenvolvimento_Multiplataforma_Python]] | [[Integracao_TTS_Typecast_e_Audio]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[analise_stack_multiplataforma]] | [[Plano_UIUX_Flet_Sejong_Companion]]  
**Bugs Catalogados:** [[bug_01_flet_audio_corridas_e_page_services]] | [[bug_04_bloqueio_de_scroll_listview_e_appbar]] | [[bug_02_sintaxe_flet_085_letter_spacing_e_button_args]] | [[bug_06_bind_windows_flet_server_ip]]  

---

## 1. ⚡ Visão Geral da Arquitetura Interna

O **Flet** é um framework moderno de desenvolvimento de interfaces que permite construir aplicações nativas multiplataforma utilizando **Python** na camada de lógica e o **Flutter Engine** na camada de renderização gráfica.

Entender o funcionamento interno dessa ponte (*bridge*) é essencial para evitar vazamentos de memória, gargalos de performance e erros de ciclo de vida de componentes.

```
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
 │    Flet Client (Dart / Flutter CanvasKit / Skia / Impeller)     │
 │                        │                                         │
 │                        ▼                                         │
 │              GPU / Tela Nativa (Web/Android/iOS)                 │
 └──────────────────────────────────────────────────────────────────┘
```

---

## 2. 🔬 Componentes Fundamentais da Engine

### A. O Ciclo de Vida da `ft.Page` e a Árvore de Controles
A `ft.Page` representa a raiz da sessão de usuário. Cada elemento visual (`ft.Text`, `ft.Container`, `ft.View`) é uma subclasse de `ft.Control`. 

Quando uma propriedade de um controle é alterada em Python (ex: `text.value = "안녕하세요"`), a mudança **não desenha na tela imediatamente**. A alteração altera o estado interno do controle Python. Somente quando a função `page.update()` é invocada, o Flet calcula a diferença de estado (*diffing*) e transmite um pacote JSON com a atualização (*delta patch*) via WebSocket para o Flutter Client redesenhar o Canvas.

### B. Gerenciamento de Serviços Não-Visuais (`page.overlay` vs `page.services`)
Controles não-visuais — como players de áudio (`flet_audio.Audio`), seletores de arquivo (`FilePicker`) ou caixas de diálogo (`AlertDialog`) — não pertencem à árvore visual comum de uma `View`.

- **`page.overlay`**: Lista de controles não-visuais cujo ciclo de vida está permanentemente atrelado à **sessão principal da página**. É a forma recomendada no Flet 0.85+ para adicionar componentes globais como áudios e modais sem risco de desconexão.
- **`page.services`**: Lista de serviços legada. Adicionar itens diretamente em `page.services` sem limpeza causa acúmulo de objetos não descartados pelo Garbage Collector.

### C. Cálculo de Layout de Viewport e Scroll Engine
O Flutter Engine calcula o tamanho dos elementos na tela através de restrições descendentes (*Constraints go down, Sizes go up, Parent sets position*).

No Flet, quando um controle rolável (`ft.ListView`) é colocado dentro de uma `ft.View` sem altura definida:
1. A `ft.View` envia restrição de altura infinita para o `ft.ListView`.
2. O `ft.ListView` colapsa para altura zero ou trava o viewport por não conseguir calcular o limite de rolagem.
3. **Solução**: O uso de `scroll=ft.ScrollMode.AUTO` e `appbar=app_bar` diretamente na `ft.View` faz com que a própria janela gerencie a rolagem nativamente com suporte a aceleração via hardware.

---

## 3. 🚨 Análise de Bugs Críticos da Arquitetura

### 1. Corrida de Montagem e Destruição de Áudio ([[bug_01_flet_audio_corridas_e_page_services]])
- **O Problema**: A criação de instâncias de `ft.Audio()` dentro das views locais do quiz causava exceções `Control not found` quando a view era destruída durante o carregamento do som.
- **Solução Arquitetural**: Criação do serviço singleton `AudioService` (em `src/audio_service.py`) injetado em `page.overlay`, garantindo que o player permaneça vivo na sessão da página independente da navegação entre views.

### 2. Quebra de Rolagem na View de Testes ([[bug_04_bloqueio_de_scroll_listview_e_appbar]])
- **O Problema**: A view de laboratório UI/UX montada com `ListView` interno cortava os cartões a partir da primeira pergunta do quiz.
- **Solução Arquitetural**: Eliminação do `ListView` interno e atribuição de `scroll=ft.ScrollMode.AUTO` e `appbar=app_bar` no construtor raiz de `ft.View()`.

### 3. Atualização de Sintaxe Flet 0.85+ ([[bug_02_sintaxe_flet_085_letter_spacing_e_button_args]])
- **O Problema**: Argumentos kwargs antigos (`letter_spacing=` e `text=`) geravam `TypeError` de inicialização.
- **Solução Arquitetural**: Transição para a nova especificação de tipagem do Flet utilizando `style=ft.TextStyle(letter_spacing=...)` e rótulo posicional para botões.

---

## 4. 🛠️ Padrão de Código Recomendado para Views

```python
# Estrutura Padrão de View no Sejong Companion

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
            on_click=lambda _: page.router.navigate_to("/home")
        ),
        title=ft.Text("Título da Tela", size=18, weight=ft.FontWeight.BOLD, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0
    )

    # 2. Construção dos Controles Principais
    content = ft.Column(
        controls=[
            ft.Text("Conteúdo com scroll nativo e performático", color=colors["text"]),
        ],
        spacing=16
    )

    # 3. Retorno da View com Scroll Raiz Nativo
    return ft.View(
        route="/exemplo",
        appbar=app_bar,
        controls=[content],
        scroll=ft.ScrollMode.AUTO, # Gerenciado pela View
        bgcolor=colors["bg"],
        padding=16
    )
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🎙️ Integração de Áudio TTS: [[Integracao_TTS_Typecast_e_Audio]]
- 📱 Desenvolvimento Multiplataforma: [[Desenvolvimento_Multiplataforma_Python]]
- 🚨 Catálogo de Bugs: [[INDICE_BUGS]]
