import flet as ft
from datetime import datetime
from ..components import centered_content
from ..theme import get_theme_colors, Styles, Responsive
from ..services import DataService, ProgressService, FullscreenService

def home_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    w = page.width or 400
    progress_service = ProgressService(page)

    curriculum = DataService.get_curriculum()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if is_dark else ft.ThemeMode.DARK
        # Navegar para a mesma rota ("/home" -> "/home") não dispara
        # reconstrução no Flet — o roteador do cliente ignora navegação para
        # a rota que já está ativa. Por isso o tema só "aplicava" depois de
        # entrar em outra tela e voltar. Aqui reconstruímos a view atual
        # diretamente, no lugar, para o toggle ser instantâneo.
        page.views.clear()
        page.views.append(home_view(page))
        page.update()

    app_bar = ft.AppBar(
        leading=ft.Container(
            content=ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, color=colors["primary"], size=22),
            padding=ft.Padding.only(left=12)
        ),
        title=ft.Text("Sejong Companion", weight=ft.FontWeight.BOLD, size=20, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0,
        actions=[
            ft.IconButton(
                icon=ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED,
                icon_color=colors["secondary"],
                on_click=lambda e: page.router.navigate_to("/admin"),
                tooltip="Portal Pedagógico (Admin)",
            ),
            ft.IconButton(
                icon=ft.Icons.DARK_MODE_ROUNDED if not is_dark else ft.Icons.LIGHT_MODE_ROUNDED,
                icon_color=colors["primary"],
                on_click=toggle_theme,
                tooltip="Mudar Tema",
            ),
            ft.Container(width=8)
        ]
    )

    welcome_text = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Olá, Estudante! 👋", size=22, weight=ft.FontWeight.BOLD, color=colors["text"]),
                ft.Text(
                    "Acompanhe o currículo do Sejong Hakdang de forma complementar e interativa.",
                    size=13,
                    color=colors["text_sec"]
                )
            ],
            spacing=2
        ),
        margin=ft.Margin.only(bottom=12)
    )

    # ─── NEURO-TIP DINÂMICO (Cronobiologia) ───

    now = datetime.now()
    hour = now.hour

    if 6 <= hour < 12:
        tip_icon = "☀️"
        tip_title = "Pico de Atenção Matinal"
        tip_text = "Excelente momento para estudar gramática de partículas e decodificar a sintaxe SOV. Seu córtex pré-frontal está no auge!"
        tip_color = "#F88807"  # warning-500 do design system
    elif 12 <= hour < 18:
        tip_icon = "🌤️"
        tip_title = "Hora de Praticar"
        tip_text = "Boa hora para exercícios interativos e quiz! A memória procedural (de habilidades) funciona bem à tarde."
        tip_color = "#0356C5"  # info-500 do design system
    elif 18 <= hour < 22:
        tip_icon = "🌙"
        tip_title = "Janela de Consolidação"
        tip_text = "Ótimo momento para revisar vocabulário e 한글 antes de dormir. A memória se consolida durante o sono!"
        tip_color = "#7C4DFF"  # primary-500 do design system
    else:
        tip_icon = "🌟"
        tip_title = "Sessão Noturna"
        tip_text = "Revisão leve e espaçada é ideal agora. Leia os exemplos sem pressão — amanhã você lembrará melhor!"
        tip_color = "#3E00EB"  # primary-700 do design system, mais profundo

    neuro_tip_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(tip_icon, size=28),
                    width=48,
                    height=48,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=f"{tip_color}15",
                    border_radius=Styles.BORDER_RADIUS_SM,
                ),
                ft.Column(
                    controls=[
                        ft.Text(tip_title, size=14, weight=ft.FontWeight.BOLD, color=tip_color),
                        ft.Text(tip_text, size=12, color=colors["text_sec"], max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=colors["surface"],
        border=ft.Border.all(1, f"{tip_color}30"),
        border_radius=Styles.BORDER_RADIUS_MD,
        padding=14,
        margin=ft.Margin.only(bottom=12),
    )

    # ─── PROGRESSO GERAL ───

    unlocked_count = sum(1 for u in curriculum if progress_service.is_unlocked(u.id))
    total_units = len(curriculum)
    overall_progress = sum(progress_service.get_progress(u.id) for u in curriculum) / total_units if total_units > 0 else 0.0

    progress_summary = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Seu Progresso Geral", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Text(f"{unlocked_count} de {total_units} unidades liberadas", size=12, color=colors["text_sec"]),
                    ],
                    spacing=2,
                    expand=True
                ),
                ft.Stack(
                    controls=[
                        ft.ProgressRing(
                            value=overall_progress,
                            color=colors["secondary"],
                            bgcolor=colors["border"],
                            width=48,
                            height=48,
                            stroke_width=5
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"{int(overall_progress * 100)}%",
                                size=10,
                                weight=ft.FontWeight.BOLD,
                                color=colors["text"]
                            ),
                            alignment=ft.Alignment.CENTER,
                            width=48,
                            height=48,
                        )
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        bgcolor=colors["surface"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
        padding=Responsive.value(w, compact=10, medium=16),
        margin=ft.Margin.only(bottom=16)
    )

    # ─── ACESSOS DE REVISÃO E FLASHCARDS ───
    due_count = len(progress_service.get_due_reviews())
    review_ready = due_count > 0
    review_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(content=ft.Text("🔥", size=26), width=44, height=44, alignment=ft.Alignment.CENTER,
                             bgcolor="#14F5A623", border_radius=Styles.BORDER_RADIUS_SM),
                ft.Column(controls=[
                    ft.Text("Revisão do Dia · 일일 복습", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Text(f"{due_count} item(ns) com retenção abaixo de 75%" if review_ready else "Tudo em dia! ✨ Faça uma revisão preventiva.",
                            size=11, color=colors["text_sec"]),
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, size=16, color=colors["primary"]),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
        ),
        bgcolor=colors["card_bg"], border=ft.Border.all(1, colors["warning"] if review_ready else colors["correct"]),
        border_radius=Styles.BORDER_RADIUS_MD, padding=12, margin=ft.Margin.only(bottom=9),
        on_click=lambda e: page.router.navigate_to("/review"),
    )
    flashcards_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(content=ft.Text("🃏", size=24), width=44, height=44, alignment=ft.Alignment.CENTER,
                             bgcolor="#147C4DFF", border_radius=Styles.BORDER_RADIUS_SM),
                ft.Column(
                    controls=[
                        ft.Text("Flashcards & Criação de Texto · 문장", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Text("Treine por nível e monte frases em coreano.", size=11, color=colors["text_sec"]),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, size=16, color=colors["primary"]),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=colors["card_bg"],
        border=ft.Border.all(1, colors["secondary"]),
        border_radius=Styles.BORDER_RADIUS_MD,
        padding=12,
        margin=ft.Margin.only(bottom=16),
        on_click=lambda e: page.router.navigate_to("/flashcards"),
    )

    # ─── SUMÁRIO DE PROGRESSO DOS LIVROS (1A & 1B) ───
    completed_1a = sum(
        1 for u in curriculum
        if (not u.id.startswith("unit_1b_")) and progress_service.get_progress(u.id) >= 1.0
    )
    total_1a = sum(1 for u in curriculum if not u.id.startswith("unit_1b_"))

    completed_1b = sum(
        1 for u in curriculum
        if u.id.startswith("unit_1b_") and progress_service.get_progress(u.id) >= 1.0
    )
    total_1b = sum(1 for u in curriculum if u.id.startswith("unit_1b_"))

    progress_summary_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=14, color=colors["primary"]),
                                            ft.Text("Livro 1A", size=12, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                                        ],
                                        spacing=4,
                                    ),
                                    ft.Text(f"{completed_1a}/{total_1a}", size=11, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(
                                value=completed_1a / max(1, total_1a),
                                color=colors["primary"],
                                bgcolor=colors["border"],
                                height=4,
                                border_radius=2,
                            ),
                        ],
                        spacing=3,
                    ),
                    expand=True,
                ),
                ft.Container(width=10),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.AUTO_STORIES_ROUNDED, size=14, color=colors["secondary"]),
                                            ft.Text("Livro 1B", size=12, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                                        ],
                                        spacing=4,
                                    ),
                                    ft.Text(f"{completed_1b}/{total_1b}", size=11, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(
                                value=completed_1b / max(1, total_1b),
                                color=colors["secondary"],
                                bgcolor=colors["border"],
                                height=4,
                                border_radius=2,
                            ),
                        ],
                        spacing=3,
                    ),
                    expand=True,
                ),
            ],
        ),
        bgcolor=colors["surface"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
        padding=10,
        margin=ft.Margin.only(bottom=14),
    )

    # ─── CARDS DAS UNIDADES COM FILTRAGEM REATIVA ───
    selected_filter = ["ALL"]  # "ALL" | "1A" | "1B"
    units_column = ft.Column(spacing=0)
    filter_pills_row = ft.Row(spacing=6)

    def render_single_unit_card(unit, is_1b: bool):
        unit_progress = progress_service.get_progress(unit.id)
        is_unlocked = progress_service.is_unlocked(unit.id)

        def click_handler(e):
            if not is_unlocked:
                snack = ft.SnackBar(
                    content=ft.Text("🔒 Complete as unidades anteriores para desbloquear esta!"),
                    bgcolor=colors["secondary"],
                    open=True,
                )
                page.overlay.append(snack)
                page.update()
                return

            if unit.id == "unit_intro":
                page.router.navigate_to("/hangul", unit.id)
            else:
                page.router.navigate_to("/lesson", unit.id)

        if unit.id == "unit_intro":
            badge_text = "H"
        elif is_1b:
            badge_text = f"B{int(unit.id.split('_')[-1])}"
        else:
            badge_text = str(unit.number)

        badge_color = colors["primary"] if is_unlocked else colors["border"]

        # Orbe de Vitalidade SRS (Retenção por Meia-Vida)
        vitality = progress_service.get_vitality(unit.id) if is_unlocked and unit_progress > 0 else "none"
        vitality_color_map = {
            "high": colors["vitality_high"],
            "medium": colors["vitality_medium"],
            "low": colors["vitality_low"],
            "none": colors["vitality_none"],
        }
        vitality_color = vitality_color_map.get(vitality, colors["vitality_none"])
        vitality_tooltip_map = {
            "high": "Memória forte! ✅",
            "medium": "Hora de revisar ⚠️",
            "low": "Memória enfraquecendo! 🔴",
            "none": "",
        }
        vitality_tooltip = vitality_tooltip_map.get(vitality, "")

        badge_stack = ft.Stack(
            controls=[
                ft.Container(
                    content=ft.Text(
                        badge_text,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE if is_unlocked else colors["text_sec"],
                        size=15,
                    ),
                    bgcolor=badge_color,
                    shape=ft.BoxShape.CIRCLE,
                    width=38,
                    height=38,
                    alignment=ft.Alignment.CENTER,
                ),
            ] + ([
                ft.Container(
                    width=12,
                    height=12,
                    bgcolor=vitality_color,
                    shape=ft.BoxShape.CIRCLE,
                    border=ft.Border.all(2, colors["card_bg"]),
                    top=0,
                    right=0,
                    tooltip=vitality_tooltip,
                ),
            ] if vitality != "none" else []),
            width=38,
            height=38,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    badge_stack,
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(unit.title_kr, weight=ft.FontWeight.BOLD, size=15, color=colors["text"]),
                                    ft.Icon(
                                        ft.Icons.LOCK_ROUNDED,
                                        size=14,
                                        color=colors["text_sec"],
                                        visible=not is_unlocked,
                                    ),
                                ],
                                spacing=6,
                            ),
                            ft.Text(unit.title_pt, size=12, weight=ft.FontWeight.W_500, color=colors["text_sec"]),
                            ft.Text(
                                unit.description if is_unlocked else "Conteúdo bloqueado.",
                                size=11,
                                color=colors["text_sec"],
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Container(height=4),
                            ft.ProgressBar(
                                value=unit_progress,
                                color=colors["secondary"],
                                bgcolor=colors["border"],
                                height=4,
                                border_radius=2,
                                visible=is_unlocked,
                            ) if is_unlocked else ft.Container(),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=colors["card_bg"] if is_unlocked else "#0874717F",
            border=ft.Border.all(1, colors["primary_light"] if is_unlocked and unit_progress > 0 else colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            padding=14,
            shadow=Styles.CARD_SHADOW if is_unlocked else None,
            on_click=click_handler,
            margin=ft.Margin.only(bottom=10),
        )

    def refresh_units_display():
        units_column.controls.clear()
        filter_mode = selected_filter[0]

        has_shown_1a = False
        has_shown_1b = False

        for unit in curriculum:
            is_1b = getattr(unit, "book", "") == "1B" or unit.id.startswith("unit_1b_")

            if filter_mode == "1A" and is_1b:
                continue
            if filter_mode == "1B" and not is_1b:
                continue

            if filter_mode == "ALL":
                if not is_1b and not has_shown_1a:
                    units_column.controls.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=16, color=colors["primary"]),
                                    ft.Text("Sejong Coreano 1A · 세종한국어 1A", size=13, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                                ],
                                spacing=6,
                            ),
                            margin=ft.Margin.only(top=10, bottom=8),
                        )
                    )
                    has_shown_1a = True
                elif is_1b and not has_shown_1b:
                    units_column.controls.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.AUTO_STORIES_ROUNDED, size=16, color=colors["secondary"]),
                                    ft.Text("Sejong Coreano 1B · 세종한국어 1B", size=13, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                                ],
                                spacing=6,
                            ),
                            margin=ft.Margin.only(top=14, bottom=8),
                        )
                    )
                    has_shown_1b = True

            units_column.controls.append(render_single_unit_card(unit, is_1b))

    def set_filter(mode: str):
        selected_filter[0] = mode
        refresh_filter_pills()
        refresh_units_display()
        page.update()

    def refresh_filter_pills():
        filter_pills_row.controls.clear()
        filters_data = [
            ("Todas", "ALL", len(curriculum)),
            ("Livro 1A", "1A", total_1a),
            ("Livro 1B", "1B", total_1b),
        ]
        for label, mode, count in filters_data:
            is_active = selected_filter[0] == mode
            pill = ft.Container(
                content=ft.Text(
                    f"{label} ({count})",
                    size=12,
                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500,
                    color=ft.Colors.WHITE if is_active else colors["text_sec"],
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=colors["primary"] if is_active else colors["surface"],
                border=ft.Border.all(1, colors["primary"] if is_active else colors["border"]),
                border_radius=Styles.BORDER_RADIUS_SM,
                padding=ft.Padding.symmetric(horizontal=4, vertical=6),
                alignment=ft.Alignment.CENTER,
                on_click=lambda e, m=mode: set_filter(m),
                expand=True,
            )
            filter_pills_row.controls.append(pill)

    refresh_filter_pills()
    refresh_units_display()

    return ft.View(
        route="/home",
        appbar=app_bar,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            centered_content(
                page,
                ft.Column(
                    controls=[
                        welcome_text,
                        neuro_tip_card,
                        progress_summary,
                        review_card,
                        flashcards_card,
                        progress_summary_card,
                        ft.Text("Grade Curricular", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Container(height=8),
                        filter_pills_row,
                        ft.Container(height=10),
                        units_column,
                    ],
                    spacing=0,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"],
        padding=0,
    )
