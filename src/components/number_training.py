"""Teclado Numérico (Dialpad) de Treinamento dos Sistemas Numéricos Coreanos.

Suporta a alternância entre o Sistema Sino-Coreano (일, 이, 삼, 사...) e
o Sistema Nativo Coreano (하나, 둘, 셋, 넷...), com buffer de 10 teclas e checagem de desafio.
"""

from typing import Optional, Callable
import flet as ft
from ..theme import get_theme_colors, Styles

SINO_MAP = {
    "0": "영",
    "1": "일",
    "2": "이",
    "3": "삼",
    "4": "사",
    "5": "오",
    "6": "육",
    "7": "칠",
    "8": "팔",
    "9": "구",
}

NATIVE_MAP = {
    "1": "하나",
    "2": "둘",
    "3": "셋",
    "4": "넷",
    "5": "다섯",
    "6": "여섯",
    "7": "일곱",
    "8": "여덟",
    "9": "아홉",
    "10": "열",
}


class NumberTraining(ft.Container):
    """Widget de treinamento dos sistemas numéricos coreanos com teclado discador."""

    def __init__(
        self,
        is_dark: bool = True,
        system: str = "sino",
        on_complete: Optional[Callable] = None,
    ):
        self.is_dark = is_dark
        self.colors = get_theme_colors(is_dark)
        self.system = system
        self.on_complete = on_complete
        self.buffer = ""
        self.current_challenge_target = ""

        # Visor de texto do buffer e feedback
        self.display_text = ft.Text(
            value="_ _ _ _",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=self.colors["text"],
            text_align=ft.TextAlign.CENTER,
        )

        self.translation_text = ft.Text(
            value="",
            size=14,
            color=self.colors["primary"],
            text_align=ft.TextAlign.CENTER,
        )

        self.feedback_text = ft.Text(
            value="",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=self.colors["correct"],
            text_align=ft.TextAlign.CENTER,
        )

        # Montagem do teclado numérico 3x4
        key_grid = self._build_dialpad()

        # Seletor de sistema
        self.system_selector = ft.Row(
            controls=[
                ft.Button(
                    content="Sino-Coreano",
                    on_click=lambda _: self.set_system("sino"),
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["primary"] if self.system == "sino" else self.colors["surface"],
                        color=ft.Colors.WHITE if self.system == "sino" else self.colors["text_sec"],
                    ),
                ),
                ft.Button(
                    content="Nativo Coreano",
                    on_click=lambda _: self.set_system("native"),
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["primary"] if self.system == "native" else self.colors["surface"],
                        color=ft.Colors.WHITE if self.system == "native" else self.colors["text_sec"],
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    self.system_selector,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.display_text,
                                self.translation_text,
                                self.feedback_text,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                        ),
                        padding=12,
                        bgcolor=self.colors["card_bg"],
                        border=ft.Border.all(1, self.colors["border"]),
                        border_radius=Styles.BORDER_RADIUS_MD,
                        width=260,
                    ),
                    key_grid,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.Alignment.CENTER,
        )

    def _build_dialpad(self) -> ft.Column:
        """Constrói o layout de grade do discador com botões de 0 a 9 e Limpar."""
        rows = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["C", "0", "OK"],
        ]
        grid_rows = []
        for row in rows:
            btn_row = []
            for key in row:
                btn = ft.Button(
                    content=key,
                    width=68,
                    height=52,
                    on_click=lambda e, k=key: self.press_key(k),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                        bgcolor=self.colors["surface"],
                        color=self.colors["text"],
                    ),
                )
                btn_row.append(btn)
            grid_rows.append(ft.Row(controls=btn_row, alignment=ft.MainAxisAlignment.CENTER, spacing=8))

        return ft.Column(controls=grid_rows, spacing=8)

    def press_key(self, key: str):
        """Processa a digitação de uma tecla no dialpad."""
        if key == "C":
            self.clear_buffer()
            return
        elif key == "OK":
            if self.current_challenge_target:
                self.check_challenge(self.current_challenge_target)
            return

        if len(self.buffer) < 8:
            self.buffer += key
            self._update_display()

    def clear_buffer(self):
        """Limpa o buffer de digitação."""
        self.buffer = ""
        self.feedback_text.value = ""
        self._update_display()

    def set_system(self, system: str):
        """Altera o sistema de contagem ativo (sino ou native)."""
        self.system = system
        self._update_display()

    def switch_system(self, system: str):
        """Alias para set_system."""
        self.set_system(system)

    def check_challenge(self, expected: str) -> bool:
        """Valida o buffer digitado contra o valor numérico esperado no desafio."""
        self.current_challenge_target = expected
        if self.buffer == str(expected):
            self.feedback_text.value = "✅ 정답입니다! (Correto!)"
            self.feedback_text.color = self.colors["correct"]
            if self.on_complete:
                try:
                    self.on_complete(self.buffer)
                except Exception:
                    pass
            try:
                self.update()
            except Exception:
                pass
            return True
        else:
            self.feedback_text.value = "❌ 다시 시도하세요 (Tente novamente)"
            self.feedback_text.color = self.colors["incorrect"]
            try:
                self.update()
            except Exception:
                pass
            return False

    def _update_display(self):
        """Atualiza a exibição de dígitos e a leitura fonética em Hangul."""
        if not self.buffer:
            self.display_text.value = "_ _ _ _"
            self.translation_text.value = ""
        else:
            self.display_text.value = " ".join(self.buffer)
            # Tradução para Hangul
            hangul_parts = []
            if self.system == "sino":
                for digit in self.buffer:
                    hangul_parts.append(SINO_MAP.get(digit, ""))
            else:
                for digit in self.buffer:
                    hangul_parts.append(NATIVE_MAP.get(digit, digit))
            self.translation_text.value = " ".join(hangul_parts)

        try:
            self.update()
        except Exception:
            pass
