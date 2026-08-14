"""Primitivos de layout compartilhados pelas telas do aplicativo."""

import flet as ft


CONTENT_MAX_WIDTH = 600
DEFAULT_VIEWPORT_WIDTH = 400


def centered_content(
    page: ft.Page,
    content: ft.Control,
    *,
    padding=None,
    expand: bool = False,
    alignment: ft.Alignment | None = None,
) -> ft.Row:
    """Mantém o conteúdo principal centralizado, com largura legível em telas grandes."""
    # No primeiro build o Flet pode ainda não ter informado a largura da página.
    # O fallback mobile evita renderizar uma coluna de 600 px nessa situação.
    viewport_width = page.width or DEFAULT_VIEWPORT_WIDTH
    return ft.Row(
        controls=[
            ft.Container(
                content=content,
                width=min(viewport_width, CONTENT_MAX_WIDTH),
                padding=padding,
                alignment=alignment,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        expand=expand,
    )
