import flet as ft
from ..theme import get_theme_colors, Styles
from ..services import DataService, ProgressService, FullscreenService
from ..components.vocab_card import VocabCard

def lesson_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    progress_service = ProgressService(page)

    unit_id = page.router.current_unit_id
    
    # Carregar dados apropriados dependendo do ID
    unit_data = None
    if unit_id == "unit_01":
        unit_data = DataService.get_unit_one()

    if not unit_data:
        return ft.View(
            route=f"/lesson",
            controls=[
                ft.AppBar(title=ft.Text("Erro"), bgcolor=colors["surface"]),
                ft.Text("Unidade não encontrada ou não implementada nesta versão.", color=colors["incorrect"])
            ]
        )

    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: page.router.navigate_to("/home")
        ),
        title=ft.Text(unit_data.title, weight=ft.FontWeight.BOLD, size=16, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0
    )

    # ─── Tab 1: Lista de Vocabulário ───

    vocab_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    for item in unit_data.vocabulary:
        vocab_col.controls.append(
            VocabCard(
                item,
                is_dark,
                on_audio_click=lambda w: page.audio_service.play_korean(w)
            )
        )


    # ─── Tab 2: Gramática (lista de seções) ───

    grammar_controls = []
    for g_section in unit_data.grammar:
        # Título da seção
        grammar_controls.append(
            ft.Text(g_section.title, size=18, weight=ft.FontWeight.BOLD, color=colors["primary"])
        )
        grammar_controls.append(ft.Container(height=6))
        
        # Explicação
        grammar_controls.append(
            ft.Text(g_section.explanation, size=14, color=colors["text"])
        )
        grammar_controls.append(ft.Container(height=12))
        
        # Exemplos
        grammar_controls.append(
            ft.Text("Exemplos de Uso:", size=14, weight=ft.FontWeight.BOLD, color=colors["text"])
        )
        grammar_controls.append(ft.Container(height=6))
        
        for ex in g_section.examples:
            grammar_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(ex.kr, size=15, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                            ft.Text(ex.pt, size=13, color=colors["text_sec"])
                        ],
                        spacing=2
                    ),
                    padding=10,
                    border_radius=Styles.BORDER_RADIUS_SM,
                    bgcolor=colors["surface"],
                    border=ft.Border.all(1, colors["border"]),
                    margin=ft.Margin.only(bottom=8)
                )
            )
        
        # Dica para lusófonos, se disponível
        if g_section.lusophone_tip:
            grammar_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("🇧🇷", size=18),
                            ft.Text(
                                g_section.lusophone_tip,
                                size=13,
                                color=colors["accent"],
                                italic=True,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=12,
                    bgcolor="#0FF5A623",
                    border_radius=Styles.BORDER_RADIUS_SM,
                    border=ft.Border.all(1, "#26F5A623"),
                    margin=ft.Margin.only(bottom=16, top=4)
                )
            )
        
        # Separador entre seções
        grammar_controls.append(ft.Divider(height=1, color=colors["border"]))
        grammar_controls.append(ft.Container(height=10))

    grammar_col = ft.Column(
        controls=grammar_controls,
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    # ─── Tab 3: Notas Culturais ───

    culture_controls = []
    if unit_data.cultural_notes:
        for note in unit_data.cultural_notes:
            culture_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(note.icon, size=28),
                                    ft.Text(note.title, size=16, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ],
                                spacing=10,
                            ),
                            ft.Container(height=6),
                            ft.Text(note.content, size=13, color=colors["text_sec"]),
                        ],
                        spacing=4,
                    ),
                    padding=16,
                    bgcolor=colors["card_bg"],
                    border=ft.Border.all(1, colors["border"]),
                    border_radius=Styles.BORDER_RADIUS_MD,
                    shadow=Styles.CARD_SHADOW,
                    margin=ft.Margin.only(bottom=12),
                )
            )

    culture_col = ft.Column(
        controls=culture_controls if culture_controls else [
            ft.Text("Notas culturais estarão disponíveis em breve.", size=14, color=colors["text_sec"], italic=True)
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    # ─── Abas (Tabs) ───
    tab_headers = [
        ft.Tab(label="Vocabulário", icon=ft.Icons.BOOK_ROUNDED),
        ft.Tab(label="Gramática", icon=ft.Icons.MENU_BOOK_ROUNDED),
    ]
    tab_contents = [
        vocab_col,
        grammar_col,
    ]

    if unit_data.cultural_notes:
        tab_headers.append(ft.Tab(label="Cultura", icon=ft.Icons.PUBLIC_ROUNDED))
        tab_contents.append(culture_col)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        height=580,  # Altura fixa para se integrar perfeitamente a view scrollavel
        length=len(tab_headers),
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=tab_headers,
                    label_color=colors["primary"],
                    unselected_label_color=colors["text_sec"],
                    indicator_color=colors["primary"]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=tab_contents
                )
            ]
        )
    )

    # Botão de Exercícios
    exercise_button = ft.Container(
        content=ft.ElevatedButton(
            content="Praticar com Exercícios (Quiz)",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=colors["secondary"],
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                padding=14
            ),
            on_click=lambda e: page.router.navigate_to("/quiz", unit_id),
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=colors["surface"],
        border=ft.Border.only(top=ft.BorderSide(1, colors["border"])),
    )

    return ft.View(
        route=f"/lesson",
        appbar=app_bar,
        controls=[
            tabs,
            exercise_button
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"]
    )
