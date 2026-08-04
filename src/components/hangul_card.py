import flet as ft
from ..theme import get_theme_colors, Styles

class HangulCard(ft.Container):
    def __init__(self, char_data, is_dark: bool, on_audio_click=None):
        self.char_data = char_data
        self.is_dark = is_dark
        self.colors = get_theme_colors(is_dark)
        self.flipped = False
        self.on_audio_click = on_audio_click
        
        # Frente: Caractere Coreano
        self.char_text = ft.Text(
            value=char_data.char,
            size=60,
            weight=ft.FontWeight.BOLD,
            color=self.colors["primary"],
            text_align=ft.TextAlign.CENTER,
        )
        
        # Verso: Nome em 한글 + Descrição fonética em português
        name_text = char_data.name if hasattr(char_data, 'name') else ""
        
        detail_controls = [
            ft.Text(
                name_text,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=self.colors["text"]
            ),
            ft.Text(
                char_data.pronunciation,
                size=10,
                color=self.colors["text_sec"],
                text_align=ft.TextAlign.CENTER,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        ]

        # Indicador de tipo (para aspiradas/tensas)
        if hasattr(char_data, 'type') and char_data.type != "plain":
            type_labels = {
                "aspirated": "💨 Aspirada",
                "tense": "💪 Tensa",
            }
            type_label = type_labels.get(char_data.type, "")
            if type_label:
                detail_controls.insert(0, ft.Container(
                    content=ft.Text(type_label, size=8, weight=ft.FontWeight.BOLD, color=self.colors["secondary"]),
                    bgcolor="#19188150",
                    border_radius=4,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                ))
        
        # Dica mnemônica para vogais
        if hasattr(char_data, 'mnemonic') and char_data.mnemonic:
            detail_controls.append(
                ft.Container(
                    content=ft.Text(
                        char_data.mnemonic,
                        size=9,
                        color=self.colors["secondary"],
                        text_align=ft.TextAlign.CENTER,
                        italic=True,
                    ),
                    margin=ft.Margin.only(top=4)
                )
            )

        self.detail_col = ft.Column(
            controls=detail_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            visible=False
        )

        super().__init__(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        content=self.char_text,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=self.detail_col,
                        alignment=ft.Alignment.CENTER,
                        padding=8,
                    )
                ]
            ),
            width=140,
            height=140,
            bgcolor=self.colors["card_bg"],
            border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            shadow=Styles.CARD_SHADOW,
            alignment=ft.Alignment.CENTER,
            animate=150,
            on_click=self.toggle_flip,
            on_hover=self.on_card_hover
        )

    def toggle_flip(self, e):
        self.flipped = not self.flipped
        # Áudio-Visual Gating: Tocar no card ativa o áudio nativo imediatamente
        if self.on_audio_click:
            sound_query = getattr(self.char_data, 'char', None) or getattr(self.char_data, 'name', '')
            self.on_audio_click(sound_query)

        if self.flipped:
            self.char_text.visible = False
            self.detail_col.visible = True
            self.bgcolor = self.colors["surface"]
            self.border = ft.Border.all(2, self.colors["primary"])
        else:
            self.char_text.visible = True
            self.detail_col.visible = False
            self.bgcolor = self.colors["card_bg"]
            self.border = ft.Border.all(1, self.colors["border"])
        self.update()

    def on_card_hover(self, e):
        if e.data == "true":
            self.scale = 1.04
            self.shadow = Styles.HOVER_SHADOW
            if not self.flipped:
                self.border = ft.Border.all(1.5, self.colors["primary_light"])
        else:
            self.scale = 1.0
            self.shadow = Styles.CARD_SHADOW
            if not self.flipped:
                self.border = ft.Border.all(1, self.colors["border"])
        self.update()
