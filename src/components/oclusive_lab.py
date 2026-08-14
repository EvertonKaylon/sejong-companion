"""Laboratório Fonético da Tripartição Oclusiva Coreana.

Componente interativo para as 4 tríades de consoantes oclusivas:
  ㄱ/ㅋ/ㄲ (Velares), ㄷ/ㅌ/ㄸ (Alveolares), ㅂ/ㅍ/ㅃ (Bilabiais), ㅈ/ㅊ/ㅉ (Palatais).

Cada botão circular tem cor fonética distinta (Neutro / Aspirada / Tensa),
animação de escala ao toque e reprodução de áudio via AudioService.
"""

import flet as ft
from ..theme import get_theme_colors, Styles, Responsive


# Dados das 4 tríades oclusivas
_TRIADS = [
    {
        "label": "Velares",
        "chars": [
            {"hangul": "ㄱ", "type": "lax"},
            {"hangul": "ㅋ", "type": "aspirated"},
            {"hangul": "ㄲ", "type": "tense"},
        ],
    },
    {
        "label": "Alveolares",
        "chars": [
            {"hangul": "ㄷ", "type": "lax"},
            {"hangul": "ㅌ", "type": "aspirated"},
            {"hangul": "ㄸ", "type": "tense"},
        ],
    },
    {
        "label": "Bilabiais",
        "chars": [
            {"hangul": "ㅂ", "type": "lax"},
            {"hangul": "ㅍ", "type": "aspirated"},
            {"hangul": "ㅃ", "type": "tense"},
        ],
    },
    {
        "label": "Palatais",
        "chars": [
            {"hangul": "ㅈ", "type": "lax"},
            {"hangul": "ㅊ", "type": "aspirated"},
            {"hangul": "ㅉ", "type": "tense"},
        ],
    },
]


def _get_oclusive_color(oc_type: str, colors: dict) -> str:
    """Retorna a cor fonética para o tipo oclusivo."""
    if oc_type == "aspirated":
        return colors["oclusive_aspirated"]
    elif oc_type == "tense":
        return colors["oclusive_tense"]
    return colors["oclusive_lax"]


def _get_oclusive_label(oc_type: str) -> str:
    """Retorna o rótulo descritivo do tipo."""
    if oc_type == "aspirated":
        return "Aspirada 💨"
    elif oc_type == "tense":
        return "Tensa 💪"
    return "Simples 🌱"


def _build_oclusive_button(
    hangul: str,
    oc_type: str,
    colors: dict,
    size: int,
    on_audio_click,
) -> ft.Container:
    """Cria um botão circular tátil para uma consoante oclusiva."""
    border_color = _get_oclusive_color(oc_type, colors)
    border_width = 3.0 if oc_type == "tense" else 1.8

    return ft.Container(
        content=ft.Text(
            hangul,
            size=size * 0.4,
            weight=ft.FontWeight.BOLD,
            color=border_color,
        ),
        width=size,
        height=size,
        alignment=ft.Alignment.CENTER,
        bgcolor=colors["surface"],
        shape=ft.BoxShape.CIRCLE,
        border=ft.Border.all(border_width, border_color),
        shadow=[
            ft.BoxShadow(
                color=f"{border_color}30",
                blur_radius=10,
                spread_radius=1,
            )
        ],
        on_click=lambda e, c=hangul: on_audio_click(c),
        animate=150,
        tooltip=f"Ouvir {hangul} ({_get_oclusive_label(oc_type)})",
    )


def build_oclusive_lab(page: ft.Page, colors: dict, w: float) -> ft.Column:
    """Constrói o Laboratório Fonético Oclusivo completo."""
    btn_size = Responsive.value(w, compact=64, medium=80)

    # Legenda
    legend = ft.Container(
        content=ft.Row(
            controls=[
                _legend_dot(colors["oclusive_lax"], "Simples"),
                _legend_dot(colors["oclusive_aspirated"], "Aspirada"),
                _legend_dot(colors["oclusive_tense"], "Tensa"),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        margin=ft.Margin.only(bottom=8),
        alignment=ft.Alignment.CENTER,
    )

    # Explicação
    explanation = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Compare os 3 tipos de consoantes oclusivas coreanas:",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=colors["secondary"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "• Simples: produzida sem esforço extra (som neutro)\n"
                    "• Aspirada: produzida com sopro forte de ar (coloque a mão na boca)\n"
                    "• Tensa: produzida com tensão na garganta, SEM sopro",
                    size=11,
                    color=colors["text_sec"],
                    no_wrap=False,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=12,
        bgcolor=colors["surface"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
        margin=ft.Margin.only(bottom=10),
    )

    # Tríades
    triad_cards = []
    for triad in _TRIADS:
        buttons = []
        for char_info in triad["chars"]:
            buttons.append(
                ft.Column(
                    controls=[
                        _build_oclusive_button(
                            char_info["hangul"],
                            char_info["type"],
                            colors,
                            btn_size,
                            lambda c: page.audio_service.play_korean(c),
                        ),
                        ft.Text(
                            _get_oclusive_label(char_info["type"]),
                            size=9,
                            color=_get_oclusive_color(char_info["type"], colors),
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            )

        triad_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            triad["label"],
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=colors["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Row(
                            controls=buttons,
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        ),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=14,
                bgcolor=colors["card_bg"],
                border=ft.Border.all(1, colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                margin=ft.Margin.only(bottom=8),
            )
        )

    return ft.Column(
        controls=[
            ft.Container(height=8),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("🔬", size=18),
                        ft.Text(
                            "Laboratório Fonético Oclusivo",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=colors["text"],
                        ),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                margin=ft.Margin.only(bottom=4),
                alignment=ft.Alignment.CENTER,
            ),
            explanation,
            legend,
            *triad_cards,
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _legend_dot(color: str, label: str) -> ft.Row:
    """Cria um ponto de legenda colorido."""
    return ft.Row(
        controls=[
            ft.Container(
                width=10,
                height=10,
                bgcolor=color,
                shape=ft.BoxShape.CIRCLE,
            ),
            ft.Text(label, size=10, color=color),
        ],
        spacing=4,
    )
