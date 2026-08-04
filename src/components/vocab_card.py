import flet as ft
from ..theme import get_theme_colors, Styles

class VocabCard(ft.Container):
    def __init__(self, vocab_item, is_dark: bool, on_audio_click=None):
        self.vocab_item = vocab_item
        self.colors = get_theme_colors(is_dark)
        self.on_audio_click = on_audio_click
        
        # Elementos de Texto — SEM romanização (metodologia Sejong)
        word_txt = ft.Text(
            value=vocab_item.word,
            size=22,
            weight=ft.FontWeight.BOLD,
            color=self.colors["primary"]
        )
        
        meaning_txt = ft.Text(
            value=vocab_item.meaning,
            size=15,
            weight=ft.FontWeight.W_500,
            color=self.colors["text"]
        )
        
        example_kr_txt = ft.Text(
            value=vocab_item.example_kr,
            size=14,
            weight=ft.FontWeight.W_500,
            color=self.colors["primary_light"]
        )
        
        example_pt_txt = ft.Text(
            value=vocab_item.example_pt,
            size=13,
            color=self.colors["text_sec"]
        )
        
        # Ícone de áudio destacado no topo à direita
        self.audio_icon = ft.IconButton(
            icon=ft.Icons.VOLUME_UP_ROUNDED,
            icon_color=self.colors["primary"],
            icon_size=26,
            on_click=self.play_audio_animation,
            tooltip="Ouvir pronúncia"
        )

        # Cabeçalho: Palavra em 한글 (expansível) + Botão de Áudio no topo direito
        header_row = ft.Row(
            controls=[
                ft.Container(
                    content=word_txt,
                    expand=True,
                ),
                self.audio_icon
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Significado em Português
        meaning_container = ft.Container(
            content=meaning_txt,
            margin=ft.Margin.only(top=-2, bottom=4)
        )

        # Montagem do conteúdo principal
        main_controls = [
            header_row,
            meaning_container,
            ft.Divider(height=1, color=self.colors["border"]),
            ft.Column(
                controls=[
                    ft.Text("Exemplo:", size=11, color=self.colors["text_sec"], weight=ft.FontWeight.BOLD),
                    example_kr_txt,
                    example_pt_txt
                ],
                spacing=2,
                tight=True
            )
        ]

        # Neuro-tip (dica pedagógica contextual), se disponível
        if hasattr(vocab_item, 'neuro_tip') and vocab_item.neuro_tip:
            main_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE_ROUNDED, size=16, color=self.colors["accent"]),
                            ft.Text(
                                vocab_item.neuro_tip,
                                size=12,
                                color=self.colors["accent"],
                                italic=True,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    bgcolor="#14F5A623",
                    border_radius=Styles.BORDER_RADIUS_SM,
                    border=ft.Border.all(1, "#33F5A623"),
                    margin=ft.Margin.only(top=4)
                )
            )

        # Badges de Papel Sintático e Encaixe Morfofonético (Physics Gating / Implicit)
        role_badges = []
        if hasattr(vocab_item, 'magnetic_slot_role') and vocab_item.magnetic_slot_role:
            role_colors = {
                "SUBJECT": ("👤 Sujeito", self.colors["role_subject"]),
                "OBJECT": ("📦 Objeto", self.colors["role_object"]),
                "VERB": ("⚡ Verbo", self.colors["role_verb"]),
                "PREDICATE": ("⚡ Predicado", self.colors["role_predicate"]),
                "PARTICLE": ("🔗 Partícula", self.colors["role_particle"]),
            }
            if vocab_item.magnetic_slot_role in role_colors:
                role_label, role_col = role_colors[vocab_item.magnetic_slot_role]
                role_badges.append(
                    ft.Container(
                        content=ft.Text(role_label, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                        bgcolor=role_col,
                        border_radius=Styles.BORDER_RADIUS_SM,
                    )
                )

        if hasattr(vocab_item, 'snap_anchor') and vocab_item.snap_anchor:
            anchor_labels = {
                "square": "🔲 받침 (Base Quadrada)",
                "round": "🟢 Vogal (Base Lisa)",
            }
            if vocab_item.snap_anchor in anchor_labels:
                role_badges.append(
                    ft.Container(
                        content=ft.Text(anchor_labels[vocab_item.snap_anchor], size=10, weight=ft.FontWeight.W_500, color=self.colors["text_sec"]),
                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                        bgcolor=self.colors["border"],
                        border_radius=Styles.BORDER_RADIUS_SM,
                    )
                )

        # Badge de categoria, se disponível
        category_badge = None
        if hasattr(vocab_item, 'category') and vocab_item.category:
            category_labels = {
                "cumprimentos": "💬 Cumprimento",
                "pronomes": "👤 Pronome",
                "particulas": "🔗 Partícula",
                "profissoes": "💼 Profissão",
                "paises": "🌍 País",
                "substantivos": "📦 Substantivo",
                "expressoes": "💡 Expressão",
            }
            label = category_labels.get(vocab_item.category, vocab_item.category)
            category_badge = ft.Container(
                content=ft.Text(label, size=10, weight=ft.FontWeight.W_500, color=self.colors["text_sec"]),
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                bgcolor=self.colors["border"],
                border_radius=10,
            )

        meta_badges = []
        if category_badge:
            meta_badges.append(category_badge)
        meta_badges.extend(role_badges)

        if meta_badges:
            main_controls.insert(0, ft.Row(
                controls=meta_badges,
                alignment=ft.MainAxisAlignment.START,
                spacing=6,
                wrap=True,
            ))

        super().__init__(
            content=ft.Column(
                controls=main_controls,
                spacing=8,
            ),
            bgcolor=self.colors["card_bg"],
            border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            padding=14,
            shadow=Styles.CARD_SHADOW,
            margin=ft.Margin.only(bottom=12),
            animate=150,
            on_click=self.play_audio_animation,
            on_hover=self.on_vocab_hover
        )

    def play_audio_animation(self, e):
        # Simular efeito visual de clique no áudio
        self.audio_icon.icon_color = self.colors["secondary"]
        self.audio_icon.update()
        
        # Se houver callback registrado (ex: para reproduzir áudio via TTS)
        if self.on_audio_click:
            self.on_audio_click(self.vocab_item.word)
        else:
            # Feedback visual — mostra a palavra em 한글 (sem romanização!)
            snack = ft.SnackBar(
                content=ft.Text(f"🔊 {self.vocab_item.word}"),
                action="OK",
                duration=1500,
                open=True,
            )
            self.page.overlay.append(snack)
            self.page.update()
            
        # Resetar a cor do ícone
        self.audio_icon.icon_color = self.colors["primary"]
        self.audio_icon.update()

    def on_vocab_hover(self, e):
        if e.data == "true":
            self.shadow = Styles.HOVER_SHADOW
            self.border = ft.Border.all(1, self.colors["primary_light"])
        else:
            self.shadow = Styles.CARD_SHADOW
            self.border = ft.Border.all(1, self.colors["border"])
        self.update()
