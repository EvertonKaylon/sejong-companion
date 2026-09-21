"""Componente WhatsNewDialog — Modal 'Novidades do Saebom' (새봄 소식).

Em estrita conformidade com o Brand Book v3.1:
  - Fundo: Navy (#02060F)
  - Botão Primário e Badges: Violet (#8B4DFF)
  - Sinais de Atenção e Destaques: Gold (#FFAB22)
  - Leitura e Subtítulos: Cream (#F7F4EC) e Slate (#9EA2AE)
  - Tipografia: Pretendard
"""

import json
import os
from typing import Any, Callable, Dict, Optional
import flet as ft
from ..theme import Colors, Styles

ICON_MAP: Dict[str, str] = {
    "psychology": ft.Icons.PSYCHOLOGY_ROUNDED,
    "explore": ft.Icons.EXPLORE_ROUNDED,
    "person": ft.Icons.PERSON_ROUNDED,
    "draw": ft.Icons.DRAW_ROUNDED,
    "auto_awesome": ft.Icons.AUTO_AWESOME_ROUNDED,
}


def _get_fallback_data(error_msg: str = "") -> Dict[str, Any]:
    """Retorna dados de fallback pedagógicos caso o release_notes.json não possa ser carregado."""
    return {
        "version": "0.3.6-alpha",
        "release_date": "2026-09-20",
        "title_pt": "Novidades do Saebom",
        "title_kr": "새봄 소식",
        "greeting_pt": "Olá! Confira as novidades preparadas para você e sua professora:",
        "greeting_kr": "안녕하세요! 새로운 학습 기능을 확인해보세요:",
        "highlights": [
            {
                "tag": "Neurociência",
                "tag_kr": "뇌과학",
                "icon": "psychology",
                "title_pt": "Fábrica de Sílabas e Física Articulatória",
                "title_kr": "음절 공장 & 조음 물리",
                "desc_pt": "Formação visual de blocos Hangul e feedback sensorial com tempo de início de voz (VOT).",
                "desc_kr": "시각적 한글 음절 조합 및 음성개시시간(VOT) 기반 감각 피드백 훈련.",
            },
            {
                "tag": "Estágio Espacial",
                "tag_kr": "공간 훈련",
                "icon": "explore",
                "title_pt": "Posições e Vocabulário Visual",
                "title_kr": "위치 표현 & 시각 어휘",
                "desc_pt": "Treinamento imersivo de conceitos espaciais (위, 아래, 앞, 뒤, 안, 밖).",
                "desc_kr": "공간 개념(위, 아래, 앞, 뒤, 안, 밖)을 위한 몰입형 시각 어휘 훈련.",
            },
            {
                "tag": "Identidade",
                "tag_kr": "학습자 식별",
                "icon": "person",
                "title_pt": "Fusão Inteligente de Sessões",
                "title_kr": "지능형 세션 통합",
                "desc_pt": "Identificação sem distinção de maiúsculas/minúsculas e preservação de progresso.",
                "desc_kr": "대소문자 구분 없는 학습자 식별 및 안전한 학습 진행도 보존.",
            },
            {
                "tag": "Caligrafia",
                "tag_kr": "원고지 쓰기",
                "icon": "draw",
                "title_pt": "Modo Focus e Gabaritos Oficiais",
                "title_kr": "집중 모드 & 공식 답안",
                "desc_pt": "Caligrafia guiada em 원고지 com fidelidade aos livros oficiais e avaliação por IoU.",
                "desc_kr": "공식 교재 기반 원고지 쓰기 및 IoU 정밀 획 분석.",
            },
        ],
        "footer_pt": "A tecnologia acompanha a pedagogia. Nunca compete com ela.",
        "footer_kr": "기술은 교육을 보조하며 결코 앞서지 않습니다.",
    }


def load_release_notes(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """Carrega as notas de versão com tolerância a falhas."""
    if custom_path and os.path.exists(custom_path):
        try:
            with open(custom_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return _get_fallback_data(str(e))

    # Tenta caminhos padrões (relativo ao CWD e relativo a este arquivo)
    candidate_paths = [
        os.path.join("data", "release_notes.json"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "release_notes.json")),
    ]

    for p in candidate_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return _get_fallback_data(str(e))

    return _get_fallback_data("File not found")


class WhatsNewDialog(ft.AlertDialog):
    """Modal 'Novidades do Saebom' (새봄 소식) renderizado no padrão Brand Book v3.1."""

    def __init__(
        self,
        page: Optional[ft.Page] = None,
        on_dismiss: Optional[Callable[[], None]] = None,
        release_notes_path: Optional[str] = None,
        **kwargs,
    ):
        self._page = page
        self._on_dismiss_callback = on_dismiss
        self.release_data = load_release_notes(release_notes_path)

        title_pt = self.release_data.get("title_pt", "Novidades do Saebom")
        title_kr = self.release_data.get("title_kr", "새봄 소식")
        version = self.release_data.get("version", "0.3.6-alpha")
        greeting_pt = self.release_data.get("greeting_pt", "")
        greeting_kr = self.release_data.get("greeting_kr", "")
        highlights = self.release_data.get("highlights", [])
        footer_pt = self.release_data.get("footer_pt", "A tecnologia acompanha a pedagogia. Nunca compete com ela.")

        # Cabeçalho com Ícone Dourado e Tipografia Pretendard
        title_control = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=Colors.GOLD, size=24),
                    padding=6,
                    bgcolor=ft.Colors.with_opacity(0.12, Colors.GOLD),
                    border_radius=Styles.BORDER_RADIUS_SM,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            title_pt,
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=Colors.CREAM,
                            font_family="Pretendard",
                        ),
                        ft.Text(
                            f"{title_kr} · v{version}",
                            size=11,
                            weight=ft.FontWeight.W_500,
                            color=Colors.SLATE,
                            font_family="Pretendard",
                        ),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Saudação inicial acolhedora
        greeting_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        greeting_pt,
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=Colors.CREAM,
                        font_family="Pretendard",
                    ),
                    ft.Text(
                        greeting_kr,
                        size=11,
                        color=Colors.SLATE,
                        font_family="Pretendard",
                    ),
                ],
                spacing=3,
            ),
            padding=ft.Padding.all(10),
            bgcolor=ft.Colors.with_opacity(0.12, Colors.VIOLET),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.25, Colors.VIOLET)),
            border_radius=Styles.BORDER_RADIUS_SM,
        )

        # Cards de Destaque
        highlight_cards = []
        for h in highlights:
            icon_key = h.get("icon", "auto_awesome")
            icon_name = ICON_MAP.get(icon_key, ft.Icons.AUTO_AWESOME_ROUNDED)
            tag_pt = h.get("tag", "")
            tag_kr = h.get("tag_kr", "")
            h_title_pt = h.get("title_pt", "")
            h_title_kr = h.get("title_kr", "")
            h_desc_pt = h.get("desc_pt", "")

            badge_text = f"{tag_pt} · {tag_kr}" if tag_kr else tag_pt

            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon_name, color=Colors.GOLD, size=20),
                            width=36,
                            height=36,
                            bgcolor=ft.Colors.with_opacity(0.12, Colors.VIOLET),
                            border_radius=Styles.BORDER_RADIUS_SM,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(
                                                badge_text,
                                                size=9,
                                                weight=ft.FontWeight.BOLD,
                                                color=Colors.VIOLET,
                                                font_family="Pretendard",
                                            ),
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            bgcolor=ft.Colors.with_opacity(0.15, Colors.VIOLET),
                                            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, Colors.VIOLET)),
                                            border_radius=4,
                                        ),
                                    ],
                                    spacing=4,
                                ),
                                ft.Text(
                                    f"{h_title_pt} ({h_title_kr})" if h_title_kr else h_title_pt,
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=Colors.CREAM,
                                    font_family="Pretendard",
                                ),
                                ft.Text(
                                    h_desc_pt,
                                    size=11,
                                    color=Colors.SLATE,
                                    font_family="Pretendard",
                                ),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.Padding.all(10),
                bgcolor=ft.Colors.with_opacity(0.4, Colors.DARK_SURFACE),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.2, Colors.SLATE)),
                border_radius=Styles.BORDER_RADIUS_MD,
            )
            highlight_cards.append(card)

        # Rodapé pedagógico
        footer_note = ft.Container(
            content=ft.Text(
                f"🌱 {footer_pt}",
                size=10,
                color=Colors.SLATE,
                text_align=ft.TextAlign.CENTER,
                font_family="Pretendard",
                italic=True,
            ),
            padding=ft.Padding.only(top=4, bottom=2),
            alignment=ft.Alignment.CENTER,
        )

        content_column = ft.Column(
            controls=[
                greeting_card,
                *highlight_cards,
                footer_note,
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            tight=True,
        )

        dialog_content = ft.Container(
            content=content_column,
            width=440,
            height=420,
        )

        # Botão de Ação (Fechar / Entendi) em Violet #8B4DFF
        action_btn = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=16, color=ft.Colors.WHITE),
                    ft.Text("Começar a Explorar · 확인", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=6,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=Colors.VIOLET,
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            ),
            on_click=self.dismiss_dialog,
        )

        super().__init__(
            modal=True,
            title=title_control,
            content=dialog_content,
            actions=[action_btn],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=Colors.NAVY,
            shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_MD),
            content_padding=ft.Padding.all(16),
            inset_padding=ft.Padding.symmetric(horizontal=12, vertical=20),
            on_dismiss=self._handle_system_dismiss,
            **kwargs,
        )

    def dismiss_dialog(self, e=None):
        """Fecha o modal e dispara o callback de notificação de persistência."""
        self._notify_dismiss()
        self.open = False
        if self._page:
            try:
                if hasattr(self._page, "pop_dialog"):
                    self._page.pop_dialog()
                elif hasattr(self._page, "close"):
                    self._page.close(self)
                elif hasattr(self._page, "update"):
                    self._page.update()
            except Exception:
                pass

    def _handle_system_dismiss(self, e=None):
        """Dispara callback se o modal for fechado pelo sistema/backdrop."""
        self._notify_dismiss()

    def _notify_dismiss(self):
        """Executa com segurança o callback de fechamento."""
        if self._on_dismiss_callback:
            try:
                self._on_dismiss_callback()
            except Exception:
                pass
            # Garante chamada única
            self._on_dismiss_callback = None
