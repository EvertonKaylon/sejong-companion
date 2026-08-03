import flet as ft
from datetime import datetime
from ..theme import get_theme_colors, Styles
from ..services import DataService, ProgressService

def home_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
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
                icon=ft.Icons.PALETTE_OUTLINED,
                icon_color=colors["secondary"],
                on_click=lambda _: page.router.navigate_to("/ui_test"),
                tooltip="Laboratório UI/UX",
            ),
            ft.IconButton(
                icon=ft.Icons.DARK_MODE_ROUNDED if not is_dark else ft.Icons.LIGHT_MODE_ROUNDED,
                icon_color=colors["primary"],
                on_click=toggle_theme,
                tooltip="Mudar Tema"
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
        padding=16,
        margin=ft.Margin.only(bottom=16)
    )

    # ─── CARDS DAS UNIDADES ───

    unit_cards = []
    for unit in curriculum:
        unit_progress = progress_service.get_progress(unit.id)
        is_unlocked = progress_service.is_unlocked(unit.id)

        def create_click_handler(u_id=unit.id, unlocked=is_unlocked):
            def handler(e):
                if not unlocked:
                    snack = ft.SnackBar(
                        content=ft.Text("🔒 Complete as unidades anteriores para desbloquear esta!"),
                        bgcolor=colors["secondary"],
                        open=True,
                    )
                    page.overlay.append(snack)
                    page.update()
                    return

                if u_id == "unit_intro":
                    page.router.navigate_to("/hangul", u_id)
                else:
                    page.router.navigate_to("/lesson", u_id)
            return handler

        badge_text = str(unit.number) if unit.number > 0 else "H"
        badge_color = colors["primary"] if is_unlocked else colors["border"]
        
        card_content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            badge_text,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE if is_unlocked else colors["text_sec"],
                            size=15
                        ),
                        bgcolor=badge_color,
                        shape=ft.BoxShape.CIRCLE,
                        width=38,
                        height=38,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(unit.title_kr, weight=ft.FontWeight.BOLD, size=15, color=colors["text"]),
                                    ft.Icon(
                                        ft.Icons.LOCK_ROUNDED,
                                        size=14,
                                        color=colors["text_sec"],
                                        visible=not is_unlocked
                                    )
                                ],
                                spacing=6
                            ),
                            ft.Text(unit.title_pt, size=12, weight=ft.FontWeight.W_500, color=colors["text_sec"]),
                            ft.Text(
                                unit.description if is_unlocked else "Conteúdo bloqueado.",
                                size=11,
                                color=colors["text_sec"],
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Container(height=4),
                            ft.ProgressBar(
                                value=unit_progress,
                                color=colors["secondary"],
                                bgcolor=colors["border"],
                                height=4,
                                border_radius=2,
                                visible=is_unlocked
                            ) if is_unlocked else ft.Container()
                        ],
                        spacing=1,
                        expand=True,
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=colors["card_bg"] if is_unlocked else "#0874717F",
            border=ft.Border.all(1, colors["primary_light"] if is_unlocked and unit_progress > 0 else colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            padding=14,
            shadow=Styles.CARD_SHADOW if is_unlocked else None,
            on_click=create_click_handler(unit.id, is_unlocked),
            margin=ft.Margin.only(bottom=10)
        )
        unit_cards.append(card_content)

    return ft.View(
        route="/home",
        appbar=app_bar,
        controls=[
            welcome_text,
            neuro_tip_card,
            progress_summary,
            ft.Text("Grade Curricular", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Column(controls=unit_cards)
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"],
        padding=16
    )
