"""Diorama 2D de Relações Espaciais e Postposições Coreanas (공간 위치 훈련).

Componente interativo para fixação de postposições espaciais (위, 아래, 옆, 앞, 뒤)
da Unidade 03, utilizando paleta Brand Book v3.1 e assets vetoriais canônicos.
"""

from typing import Optional, Callable, List, Dict, Tuple
import flet as ft
from ..theme import get_theme_colors, Styles


class SpatialStage(ft.Container):
    """Diorama interativo 2D de relações e postposições espaciais."""

    DEFAULT_OBJECT_POS: Tuple[int, int] = (8, 12)
    POSITION_COORDS: Dict[str, Tuple[int, int]] = {
        "위": (36, 135),
        "아래": (152, 135),
        "옆": (75, 48),
        "앞": (136, 135),
        "뒤": (62, 200),
    }

    def __init__(
        self,
        page: Optional[ft.Page] = None,
        is_dark: bool = True,
        on_challenge_completed: Optional[Callable] = None,
    ):
        self._page = page
        self.is_dark = is_dark
        self.colors = get_theme_colors(is_dark)
        self.on_challenge_completed = on_challenge_completed

        self.challenges: List[Dict[str, str]] = [
            {
                "id": "s1",
                "object_name": "가방",
                "object_asset": "/spatial/bag.svg",
                "base_name": "책상",
                "base_asset": "/spatial/desk.svg",
                "target_pos": "위",
                "prompt_kr": "가방이 책상 위에 있어요.",
            },
            {
                "id": "s2",
                "object_name": "강아지",
                "object_asset": "/spatial/dog.svg",
                "base_name": "의자",
                "base_asset": "/spatial/chair.svg",
                "target_pos": "아래",
                "prompt_kr": "강아지가 의자 아래에 있어요.",
            },
            {
                "id": "s3",
                "object_name": "책",
                "object_asset": "/spatial/book.svg",
                "base_name": "책상",
                "base_asset": "/spatial/desk.svg",
                "target_pos": "옆",
                "prompt_kr": "책이 책상 옆에 있어요.",
            },
            {
                "id": "s4",
                "object_name": "가방",
                "object_asset": "/spatial/bag.svg",
                "base_name": "의자",
                "base_asset": "/spatial/chair.svg",
                "target_pos": "뒤",
                "prompt_kr": "가방이 의자 뒤에 있어요.",
            },
            {
                "id": "s5",
                "object_name": "강아지",
                "object_asset": "/spatial/dog.svg",
                "base_name": "책상",
                "base_asset": "/spatial/desk.svg",
                "target_pos": "앞",
                "prompt_kr": "강아지가 책상 앞에 있어요.",
            },
        ]

        self.current_idx = 0
        self.current_challenge = self.challenges[self.current_idx]
        self.placed_pos: Optional[str] = None

        # Rótulos textuais
        self.prompt_text = ft.Text(
            value=self.current_challenge["prompt_kr"],
            size=18,
            weight=ft.FontWeight.BOLD,
            color=self.colors["text"],
            text_align=ft.TextAlign.CENTER,
        )

        self.feedback_text = ft.Text(
            value="",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=self.colors["correct"],
            text_align=ft.TextAlign.CENTER,
        )

        # Imagem do Objeto Móvel (posicionável no Stack) e Objeto Base
        self.object_img = ft.Image(
            src=self.current_challenge["object_asset"],
            width=50,
            height=50,
            fit=ft.BoxFit.CONTAIN,
        )

        self.object_container = ft.Container(
            content=self.object_img,
            top=self.DEFAULT_OBJECT_POS[0],
            left=self.DEFAULT_OBJECT_POS[1],
            animate_position=200,
        )

        self.base_img = ft.Image(
            src=self.current_challenge["base_asset"],
            width=110,
            height=110,
            fit=ft.BoxFit.CONTAIN,
        )

        self.next_btn = ft.Button(
            "Próximo Desafio →",
            on_click=lambda _: self.next_challenge(),
            style=ft.ButtonStyle(
                bgcolor=self.colors["primary"],
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
            ),
        )

        # Construção do palco com slots clicáveis
        stage_canvas = self._build_stage_canvas()

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("Relações Espaciais (위치 관계 훈련)", size=13, weight=ft.FontWeight.BOLD, color=self.colors["primary"]),
                    self.prompt_text,
                    ft.Container(
                        content=stage_canvas,
                        alignment=ft.Alignment.CENTER,
                        padding=12,
                        bgcolor=self.colors["card_bg"],
                        border=ft.Border.all(1, self.colors["border"]),
                        border_radius=Styles.BORDER_RADIUS_MD,
                        width=320,
                        height=260,
                    ),
                    self.feedback_text,
                    self.next_btn,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment.CENTER,
        )

    def _build_slot_button(self, pos_name: str, pos_label: str) -> ft.Container:
        """Cria um botão de slot para posicionamento de alvo espacial."""
        return ft.Container(
            content=ft.Text(pos_label, size=11, weight=ft.FontWeight.BOLD, color=self.colors["text_sec"]),
            bgcolor=self.colors["surface"],
            border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            on_click=lambda _: self.select_position(pos_name),
            alignment=ft.Alignment.CENTER,
        )

    def _build_stage_canvas(self) -> ft.Stack:
        """Monta o diorama 2D com slots nos 5 pontos cardeais em volta da base."""
        slot_top = ft.Container(content=self._build_slot_button("위", "위 (Cima)"), top=10, left=110)
        slot_bottom = ft.Container(content=self._build_slot_button("아래", "아래 (Baixo)"), bottom=10, left=105)
        slot_left = ft.Container(content=self._build_slot_button("옆", "옆 (Lado)"), top=105, left=15)
        slot_front = ft.Container(content=self._build_slot_button("앞", "앞 (Frente)"), bottom=45, left=70)
        slot_back = ft.Container(content=self._build_slot_button("뒤", "뒤 (Atrás)"), top=45, right=35)

        base_container = ft.Container(
            content=self.base_img,
            top=75,
            left=105,
            alignment=ft.Alignment.CENTER,
        )

        return ft.Stack(
            controls=[
                slot_top,
                slot_back,
                base_container,
                self.object_container,
                slot_left,
                slot_front,
                slot_bottom,
            ],
            width=300,
            height=240,
        )

    def select_position(self, pos: str):
        """Seleciona a posição espacial para testar contra o alvo do desafio."""
        self.placed_pos = pos
        top, left = self.POSITION_COORDS.get(pos, self.DEFAULT_OBJECT_POS)
        self.object_container.top = top
        self.object_container.left = left

        target = self.current_challenge["target_pos"]

        if pos == target:
            self.feedback_text.value = "✅ 맞아요! (Correto!)"
            self.feedback_text.color = self.colors["correct"]
            if self.on_challenge_completed:
                try:
                    self.on_challenge_completed(self.current_challenge["id"])
                except Exception:
                    pass
        else:
            self.feedback_text.value = "❌ 다시 생각해보세요! (Tente novamente)"
            self.feedback_text.color = self.colors["incorrect"]

        try:
            self.update()
        except Exception:
            pass

    def next_challenge(self):
        """Avança para o próximo desafio da lista."""
        self.current_idx = (self.current_idx + 1) % len(self.challenges)
        self.current_challenge = self.challenges[self.current_idx]
        self.placed_pos = None

        self.object_container.top, self.object_container.left = self.DEFAULT_OBJECT_POS
        self.prompt_text.value = self.current_challenge["prompt_kr"]
        self.feedback_text.value = ""
        self.object_img.src = self.current_challenge["object_asset"]
        self.base_img.src = self.current_challenge["base_asset"]

        try:
            self.update()
        except Exception:
            pass
