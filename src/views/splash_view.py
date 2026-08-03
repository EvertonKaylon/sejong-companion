import flet as ft
import asyncio
from ..theme import get_theme_colors, Styles

def splash_view(page: ft.Page) -> ft.View:
    # A tela de abertura (splash) abre no Modo Escuro (Midnight Blue) por padrão
    is_dark = True
    colors = get_theme_colors(is_dark)

    from ..theme import Colors

    # Logo central (estilo brasão retrô-industrial Seollip-che)
    logo_badge = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "세종학당",
                    size=32,
                    font_family="Seollip-che",
                    weight=ft.FontWeight.W_900,
                    color=Colors.ACCENT if is_dark else Colors.PRIMARY_DARK,
                    style=ft.TextStyle(letter_spacing=3),
                ),
                ft.Text(
                    "COMPANION",
                    size=13,
                    font_family="Pretendard",
                    weight=ft.FontWeight.BOLD,
                    color=Colors.SECONDARY_LIGHT if is_dark else Colors.PRIMARY,
                    style=ft.TextStyle(letter_spacing=6),
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=24, vertical=16),
        bgcolor="#14004C97" if not is_dark else "#1E7C4DFF",
        border=ft.Border.all(3, Colors.PRIMARY if not is_dark else Colors.SECONDARY),
        border_radius=Styles.BORDER_RADIUS_MD,
        shadow=Styles.CARD_SHADOW,
    )

    logo_layout = ft.Column(
        controls=[
            logo_badge,
            ft.Container(height=12),
            ft.Text(
                "세종학당 컴패니언",
                size=26,
                font_family="Seollip-che",
                weight=ft.FontWeight.W_900,
                color=Colors.PRIMARY if not is_dark else Colors.ACCENT,
                style=ft.TextStyle(letter_spacing=2),
            ),
            ft.Text(
                "Centro Cultural Coreano no Brasil • 세종학당재단",
                size=12,
                font_family="Pretendard",
                color=colors["text_sec"],
                weight=ft.FontWeight.W_500,
            ),
            ft.Container(height=28),
            ft.ProgressRing(color=colors["secondary"], width=28, height=28),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
    )

    # Redirecionar após pequeno delay de forma segura no loop de eventos do Flet
    async def redirect():
        try:
            await asyncio.sleep(1.8)
            page.router.navigate_to("/home")
        except Exception as ex:
            # Ignorar silenciosamente se a sessao ja estiver fechada/destruida
            pass

    page.run_task(redirect)

    return ft.View(
        route="/splash",
        controls=[logo_layout],
        bgcolor=colors["bg"],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )
