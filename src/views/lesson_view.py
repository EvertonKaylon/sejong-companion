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
            route="/lesson",
            appbar=ft.AppBar(
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                    icon_color=colors["primary"],
                    on_click=lambda e: page.router.navigate_to("/home"),
                ),
                title=ft.Text("Em Construção", weight=ft.FontWeight.BOLD, size=16, color=colors["text"]),
                bgcolor=colors["surface"],
                elevation=0,
            ),
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(height=40),
                            ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=64, color=colors["accent"]),
                            ft.Container(height=16),
                            ft.Text(
                                "Conteúdo em Construção 🚧",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=colors["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=8),
                            ft.Text(
                                "Esta lição está sendo preparada com muito carinho pela equipe Sejong Companion.\n\nEm breve, novos conteúdos estarão disponíveis!",
                                size=14,
                                color=colors["text_sec"],
                                text_align=ft.TextAlign.CENTER,
                                no_wrap=False,
                            ),
                            ft.Container(height=24),
                            ft.ElevatedButton(
                                content="Voltar ao Menu",
                                icon=ft.Icons.HOME_ROUNDED,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=colors["primary"],
                                    shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                                    padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                                ),
                                on_click=lambda e: page.router.navigate_to("/home"),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=24,
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            bgcolor=colors["bg"],
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


    # ─── Tab 2: Gramática (Formatada & Estruturada em Cards) ───

    grammar_controls = []
    for idx, g_section in enumerate(unit_data.grammar, 1):
        # 1. Cabeçalho da Seção com Badge Numérico
        section_header = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(f"Regra {idx}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=colors["primary"],
                    border_radius=Styles.BORDER_RADIUS_SM,
                ),
                ft.Text(g_section.title, size=16, weight=ft.FontWeight.BOLD, color=colors["text"], expand=True),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        )

        # 2. Explicação Formatada em Markdown Rico
        explanation_box = ft.Container(
            content=ft.Markdown(
                value=g_section.explanation,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            ),
            padding=12,
            bgcolor=colors["surface"],
            border=ft.Border.all(1, colors["border"]),
            border_radius=Styles.BORDER_RADIUS_SM,
            margin=ft.Margin.only(top=6, bottom=10),
        )

        # 3. Bloco de Exemplos Práticos Interativos com Áudio
        example_cards = []
        for ex in g_section.examples:
            example_cards.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(ex.kr, size=15, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                                    ft.Text(ex.pt, size=13, color=colors["text_sec"])
                                ],
                                spacing=2,
                                expand=True
                            ),
                            ft.IconButton(
                                icon=ft.Icons.VOLUME_UP_ROUNDED,
                                icon_color=colors["primary"],
                                icon_size=22,
                                on_click=lambda e, text=ex.kr: page.audio_service.play_korean(text),
                                tooltip="Ouvir pronúncia HD"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=10,
                    border_radius=Styles.BORDER_RADIUS_SM,
                    bgcolor=colors["surface"],
                    border=ft.Border.all(1, colors["border"]),
                    margin=ft.Margin.only(bottom=4),
                    on_click=lambda e, text=ex.kr: page.audio_service.play_korean(text),
                    animate=150,
                )
            )

        examples_box = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.RECORD_VOICE_OVER_ROUNDED, size=15, color=colors["secondary"]),
                        ft.Text("Exemplos Práticos:", size=13, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                    ],
                    spacing=6,
                ),
                ft.Column(controls=example_cards, spacing=4),
            ],
            spacing=6,
        )

        # 4. Dica Lusófona (se disponível)
        lusophone_box = None
        if g_section.lusophone_tip:
            lusophone_box = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("🇧🇷", size=18),
                        ft.Column(
                            controls=[
                                ft.Text("Dica para Falantes de Português:", size=11, weight=ft.FontWeight.BOLD, color=colors["accent"]),
                                ft.Text(
                                    g_section.lusophone_tip,
                                    size=12,
                                    color=colors["text"],
                                    italic=True,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=10,
                bgcolor="#14F5A623",
                border_radius=Styles.BORDER_RADIUS_SM,
                border=ft.Border.all(1, "#33F5A623"),
                margin=ft.Margin.only(top=8, bottom=2),
            )

        # Cartão Completo da Seção de Gramática
        card_children = [section_header, explanation_box, examples_box]
        if lusophone_box:
            card_children.append(lusophone_box)

        grammar_controls.append(
            ft.Container(
                content=ft.Column(
                    controls=card_children,
                    spacing=4,
                ),
                padding=14,
                bgcolor=colors["card_bg"],
                border=ft.Border.all(1, colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                shadow=Styles.CARD_SHADOW,
                margin=ft.Margin.only(bottom=14),
            )
        )

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
        expand=True,
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
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        bgcolor=colors["surface"],
        border=ft.Border.only(top=ft.BorderSide(1, colors["border"])),
    )

    return ft.View(
        route=f"/lesson",
        appbar=app_bar,
        controls=[
            ft.Container(
                content=tabs,
                expand=True,
            ),
            exercise_button
        ],
        scroll=None,
        bgcolor=colors["bg"],
        padding=0
    )
