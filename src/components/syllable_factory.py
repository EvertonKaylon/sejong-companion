"""Fábrica de Sílabas (음절 조합 공장) — Montagem Fonotática Interativa Hangul.

Permite a combinação dinâmica de consoante inicial (초성), vogal (중성) e
consoante final/batchim (종성) em tempo real, calculando o ponto de código Unicode:
  S = 0xAC00 + (c * 588) + (v * 28) + b
"""

import flet as ft
from ..theme import get_theme_colors, Styles

CHOSEONG = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

JUNGSEONG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"
]

JONGSEONG = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]


class SyllableFactory(ft.Container):
    """Componente interativo de montagem e síntese silábica com selo de 받침."""

    def __init__(self, is_dark: bool = True, on_syllable_change=None):
        self.is_dark = is_dark
        self.colors = get_theme_colors(is_dark)
        self.on_syllable_change = on_syllable_change

        self.c_idx = 0   # "ㄱ"
        self.v_idx = 0   # "ㅏ"
        self.b_idx = 0   # "" (sem batchim)

        self.current_initial = CHOSEONG[self.c_idx]
        self.current_vowel = JUNGSEONG[self.v_idx]
        self.current_batchim = JONGSEONG[self.b_idx]
        self.current_syllable = self.compute_syllable()

        # Visualizador central da sílaba
        self.syllable_text = ft.Text(
            value=self.current_syllable,
            size=64,
            weight=ft.FontWeight.BOLD,
            color=self.colors["primary"],
            text_align=ft.TextAlign.CENTER,
        )

        # Selo mecânico do 받침 (barra de prata metálica abaixo da sílaba)
        self.batchim_seal = ft.Container(
            content=ft.Text(
                "받침 SELADO",
                size=10,
                weight=ft.FontWeight.BOLD,
                color=self.colors.get("connector_batchim", "#C0C0C0"),
            ),
            bgcolor=ft.Colors.with_opacity(0.19, self.colors["primary"]),
            border=ft.Border.all(1, self.colors.get("connector_batchim", "#C0C0C0")),
            border_radius=Styles.BORDER_RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            alignment=ft.Alignment.CENTER,
            opacity=0.0,
            animate_opacity=200,
        )

        # Tags descritivas
        self.initial_tag = ft.Text(f"초성: {self.current_initial}", size=12, color=self.colors["text_sec"])
        self.vowel_tag = ft.Text(f"중성: {self.current_vowel}", size=12, color=self.colors["text_sec"])
        self.batchim_tag = ft.Text(f"종성: (없음)", size=12, color=self.colors["text_sec"])

        display_box = ft.Container(
            content=ft.Column(
                controls=[
                    self.syllable_text,
                    self.batchim_seal,
                    ft.Row(
                        controls=[self.initial_tag, self.vowel_tag, self.batchim_tag],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            padding=16,
            bgcolor=self.colors["card_bg"],
            border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            width=280,
            alignment=ft.Alignment.CENTER,
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("Fábrica de Sílabas (음절 조합 공장)", size=14, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                    display_box,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment.CENTER,
        )

    def compute_syllable(self) -> str:
        """Calcula o caractere Hangul através do deslocamento Unicode canônico."""
        code = 0xAC00 + (self.c_idx * 588) + (self.v_idx * 28) + self.b_idx
        return chr(code)

    def set_initial(self, char: str):
        """Define a consoante inicial e recalcula a sílaba."""
        if char in CHOSEONG:
            self.c_idx = CHOSEONG.index(char)
            self.current_initial = char
            self._update_composition()

    def set_vowel(self, char: str):
        """Define a vogal e recalcula a sílaba."""
        if char in JUNGSEONG:
            self.v_idx = JUNGSEONG.index(char)
            self.current_vowel = char
            self._update_composition()

    def set_batchim(self, char: str):
        """Define o 받침 (consoante final) e recalcula a sílaba."""
        if char in JONGSEONG:
            self.b_idx = JONGSEONG.index(char)
            self.current_batchim = char
            self._update_composition()

    def compose(self) -> str:
        """Retorna a sílaba atual montada."""
        return self.current_syllable

    def _update_composition(self):
        """Atualiza os textos de exibição, visibilidade do selo de batchim e callbacks."""
        self.current_syllable = self.compute_syllable()
        self.syllable_text.value = self.current_syllable

        # Atualização do selo de batchim
        if self.b_idx > 0:
            self.batchim_seal.opacity = 1.0
            self.batchim_tag.value = f"종성: {self.current_batchim}"
        else:
            self.batchim_seal.opacity = 0.0
            self.batchim_tag.value = "종성: (없음)"

        self.initial_tag.value = f"초성: {self.current_initial}"
        self.vowel_tag.value = f"중성: {self.current_vowel}"

        if self.on_syllable_change:
            try:
                self.on_syllable_change(self.current_syllable)
            except Exception:
                pass

        try:
            self.update()
        except Exception:
            pass
