"""Cartão de active recall com revelação e autoavaliação."""

import flet as ft

from ..theme import Styles, get_theme_colors


class FlashcardWidget(ft.Container):
    """Um cartão autocontido; a view dona decide como avançar a sessão."""

    _DIFFICULTY_LABELS = {
        "easy": "Fácil · 초급",
        "medium": "Médio · 중급",
        "hard": "Difícil · 고급",
    }

    def __init__(self, card, is_dark: bool, on_rate, on_audio_click=None):
        self.card = card
        self.colors = get_theme_colors(is_dark)
        self.on_rate = on_rate
        self.on_audio_click = on_audio_click
        self.revealed = False
        super().__init__(
            bgcolor=self.colors["card_bg"],
            border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_LG,
            padding=20,
            shadow=Styles.CARD_SHADOW,
            content=self._build_content(),
        )

    def _badge(self, label: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor=color,
            padding=ft.Padding.symmetric(horizontal=9, vertical=4),
            border_radius=Styles.BORDER_RADIUS_PILL,
        )

    def _build_content(self):
        badge_color = {"easy": self.colors["correct"], "medium": self.colors["warning"], "hard": self.colors["incorrect"]}.get(
            self.card.difficulty, self.colors["primary"]
        )
        header = ft.Row(
            controls=[
                self._badge(self._DIFFICULTY_LABELS.get(self.card.difficulty, self.card.difficulty), badge_color),
                self._badge(self.card.category.replace("_", " ").title(), self.colors["primary"]),
            ],
            wrap=True,
            spacing=6,
        )
        controls = [header, ft.Container(height=14)]
        if not self.revealed:
            controls.extend([
                ft.Text(self.card.korean, size=34, weight=ft.FontWeight.BOLD, color=self.colors["primary"], text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Text("Tente recuperar o significado antes de revelar.", size=13, color=self.colors["text_sec"], text_align=ft.TextAlign.CENTER),
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.VOLUME_UP_ROUNDED,
                            icon_color=self.colors["primary"],
                            tooltip="Ouvir pronúncia",
                            on_click=lambda e: self.on_audio_click(self.card.korean) if self.on_audio_click else None,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text("Revelar resposta"),
                            icon=ft.Icons.VISIBILITY_ROUNDED,
                            on_click=self._toggle_reveal,
                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=self.colors["primary"]),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ])
        else:
            controls.extend([
                ft.Text(self.card.portuguese, size=24, weight=ft.FontWeight.BOLD, color=self.colors["text"], text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Text(self.card.example_kr or "", size=15, color=self.colors["primary_light"], text_align=ft.TextAlign.CENTER, visible=bool(self.card.example_kr)),
                ft.Text(self.card.example_pt or "", size=13, color=self.colors["text_sec"], text_align=ft.TextAlign.CENTER, visible=bool(self.card.example_pt)),
            ])
            if self.card.lusophone_tip:
                controls.append(ft.Container(
                    content=ft.Text(f"💡 {self.card.lusophone_tip}", size=12, color=self.colors["accent"]),
                    bgcolor="#14F5A623",
                    border_radius=Styles.BORDER_RADIUS_SM,
                    padding=10,
                    margin=ft.Margin.only(top=8),
                ))
            controls.extend([
                ft.Container(height=12),
                ft.Text("Como foi lembrar?", size=12, color=self.colors["text_sec"], text_align=ft.TextAlign.CENTER),
                ft.Row(
                    controls=[
                        self._rating_button("🔴\nDe novo", "again", self.colors["incorrect"]),
                        self._rating_button("🟡\nBom", "good", self.colors["warning"]),
                        self._rating_button("🟢\nFácil", "easy", self.colors["correct"]),
                    ],
                    spacing=6,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ])
        return ft.Column(controls=controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

    def _rating_button(self, label: str, rating: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=11, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=color,
            border_radius=Styles.BORDER_RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=8, vertical=9),
            expand=True,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e: self.on_rate(rating),
        )

    def _toggle_reveal(self, _event):
        self.revealed = not self.revealed
        self.content = self._build_content()
        self.update()
