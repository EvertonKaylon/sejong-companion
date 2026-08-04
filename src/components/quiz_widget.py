import flet as ft
from typing import Callable, List
from ..theme import get_theme_colors, Styles

class QuizWidget(ft.Container):
    """Widget unificado de quiz que suporta multiple_choice e order_words.
    Refatorado para responsividade total em viewport 384×715."""

    def __init__(self, question_data, is_dark: bool, on_next: Callable, on_answer: Callable):
        self.q_data = question_data
        self.is_dark = is_dark
        self.colors = get_theme_colors(is_dark)
        self.on_next = on_next
        self.on_answer = on_answer
        self.answered = False

        # Pergunta (comum aos dois tipos) — com quebra de linha automática
        self.question_text = ft.Text(
            value=question_data.question,
            size=17,
            weight=ft.FontWeight.BOLD,
            color=self.colors["text"],
            text_align=ft.TextAlign.LEFT,
            no_wrap=False,
        )

        self.explanation_container = ft.Container(visible=False, animate_opacity=200)
        self.next_button = ft.ElevatedButton(
            content="Próxima Pergunta",
            icon=ft.Icons.ARROW_FORWARD_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=self.colors["primary"],
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            ),
            visible=False,
            on_click=self.handle_next,
            expand=True,
        )

        # Montar layout de acordo com o tipo de questão
        if question_data.type == "order_words":
            quiz_body = self._build_order_words()
        else:
            quiz_body = self._build_multiple_choice()

        super().__init__(
            content=ft.Column(
                controls=[
                    self.question_text,
                    ft.Container(height=6),
                    quiz_body,
                    ft.Container(height=6),
                    self.explanation_container,
                    ft.Row(
                        controls=[self.next_button],
                        alignment=ft.MainAxisAlignment.END,
                    )
                ],
                spacing=8,
            ),
            padding=12,
            bgcolor=self.colors["surface"],
            border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            shadow=Styles.CARD_SHADOW,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    # ─── MULTIPLE CHOICE ───

    def _build_multiple_choice(self):
        self.options_column = ft.Column(spacing=8)
        self.option_buttons = []
        for i, option in enumerate(self.q_data.options):
            option_text = ft.Text(
                option,
                size=14,
                weight=ft.FontWeight.W_500,
                color=self.colors["text"],
                no_wrap=False,
                expand=True,
            )
            letter_badge = ft.Container(
                content=ft.Text(
                    chr(65 + i),
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    size=12,
                ),
                bgcolor=self.colors["primary"],
                border_radius=Styles.BORDER_RADIUS_SM,
                width=26,
                height=26,
                alignment=ft.Alignment.CENTER,
            )
            btn = ft.Container(
                content=ft.Row(
                    controls=[
                        letter_badge,
                        option_text,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                bgcolor=self.colors["card_bg"],
                border=ft.Border.all(1, self.colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                on_click=lambda e, idx=i: self.handle_select(idx),
                on_hover=self.handle_hover,
                data={"index": i},
                animate=150,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
            self.option_buttons.append(btn)
            self.options_column.controls.append(btn)
        return self.options_column

    def handle_hover(self, e):
        if self.answered:
            return
        btn = e.control
        if e.data == "true":
            btn.bgcolor = self.colors["border"]
            btn.border = ft.Border.all(1.5, self.colors["primary_light"])
        else:
            btn.bgcolor = self.colors["card_bg"]
            btn.border = ft.Border.all(1, self.colors["border"])
        btn.update()

    def handle_select(self, selected_index: int):
        if self.answered:
            return
        self.answered = True
        is_correct = (selected_index == self.q_data.correct_index)

        for i, btn in enumerate(self.option_buttons):
            btn.on_click = None
            if i == self.q_data.correct_index:
                btn.bgcolor = "#26188150"
                btn.border = ft.Border.all(2, self.colors["correct"])
            elif i == selected_index:
                btn.bgcolor = "#26C50337"
                btn.border = ft.Border.all(2, self.colors["incorrect"])
            else:
                btn.opacity = 0.5
            btn.update()

        self._show_feedback(is_correct)

    # ─── ORDER WORDS (UNSCRAMBLING) ───

    def _build_order_words(self):
        """Constrói o widget de ordenação de palavras (click-to-order)."""
        import random

        self.selected_words: List[str] = []
        self.available_words: List[str] = list(self.q_data.words)
        random.shuffle(self.available_words)

        # Área onde a frase montada aparece
        self.sentence_display = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Toque nas palavras para montar a frase...",
                        size=13,
                        italic=True,
                        color=self.colors["text_sec"],
                        no_wrap=False,
                    )
                ],
                wrap=True,
                spacing=6,
                run_spacing=6,
            ),
            padding=12,
            bgcolor=self.colors["card_bg"],
            border=ft.Border.all(2, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

        # Chips com palavras disponíveis
        self.word_chips_row = ft.Row(
            controls=[],
            wrap=True,
            spacing=6,
            run_spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        self._refresh_word_chips()

        # Botões de controle
        self.clear_btn = ft.TextButton(
            content="🔄 Limpar",
            style=ft.ButtonStyle(color=self.colors["text_sec"]),
            on_click=self._clear_order,
        )
        self.check_btn = ft.ElevatedButton(
            content="✅ Verificar",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=self.colors["secondary"],
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
            ),
            on_click=self._check_order,
            disabled=True,
        )

        return ft.Column(
            controls=[
                # Rótulo da área de montagem
                ft.Text("Sua resposta:", size=12, weight=ft.FontWeight.BOLD, color=self.colors["text_sec"]),
                self.sentence_display,
                ft.Container(height=4),
                ft.Text("Palavras disponíveis:", size=12, weight=ft.FontWeight.BOLD, color=self.colors["text_sec"]),
                self.word_chips_row,
                ft.Container(height=4),
                ft.Row(
                    controls=[self.clear_btn, self.check_btn],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=6,
        )

    def _refresh_word_chips(self):
        """Reconstrói os chips de palavras disponíveis."""
        self.word_chips_row.controls.clear()
        for word in self.available_words:
            chip = ft.Container(
                content=ft.Text(
                    word,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=self.colors["primary"],
                    no_wrap=False,
                ),
                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                bgcolor=self.colors["card_bg"],
                border=ft.Border.all(1.5, self.colors["primary_light"]),
                border_radius=Styles.BORDER_RADIUS_LG,
                on_click=lambda e, w=word: self._add_word(w),
                on_hover=self._chip_hover,
                animate=150,
                shadow=Styles.CARD_SHADOW,
            )
            self.word_chips_row.controls.append(chip)

    def _chip_hover(self, e):
        if self.answered:
            return
        btn = e.control
        if e.data == "true":
            btn.shadow = Styles.HOVER_SHADOW
            btn.border = ft.Border.all(2, self.colors["primary"])
            btn.scale = 1.05
        else:
            btn.shadow = Styles.CARD_SHADOW
            btn.border = ft.Border.all(1.5, self.colors["primary_light"])
            btn.scale = 1.0
        btn.update()

    def _add_word(self, word: str):
        """Adiciona uma palavra à frase montada."""
        if self.answered:
            return

        self.selected_words.append(word)
        self.available_words.remove(word)
        self._update_sentence_display()
        self._refresh_word_chips()

        # Habilitar verificação quando todas as palavras foram colocadas
        self.check_btn.disabled = len(self.available_words) > 0
        self.update()

    def _remove_word(self, word: str):
        """Remove uma palavra da frase montada e devolve aos chips."""
        if self.answered:
            return

        self.selected_words.remove(word)
        self.available_words.append(word)
        self._update_sentence_display()
        self._refresh_word_chips()
        self.check_btn.disabled = True
        self.update()

    def _update_sentence_display(self):
        """Atualiza a exibição da frase montada com chips removíveis."""
        if not self.selected_words:
            self.sentence_display.content = ft.Row(
                controls=[
                    ft.Text(
                        "Toque nas palavras para montar a frase...",
                        size=13,
                        italic=True,
                        color=self.colors["text_sec"],
                        no_wrap=False,
                    )
                ],
                wrap=True,
                spacing=6,
                run_spacing=6,
            )
        else:
            chips = []
            for word in self.selected_words:
                chip = ft.Container(
                    content=ft.Text(
                        word,
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color=self.colors["text"],
                        no_wrap=False,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                    bgcolor="#147C4DFF",
                    border=ft.Border.all(1.5, self.colors["primary"]),
                    border_radius=Styles.BORDER_RADIUS_LG,
                    on_click=lambda e, w=word: self._remove_word(w),
                    animate=150,
                )
                chips.append(chip)

            self.sentence_display.content = ft.Row(
                controls=chips,
                wrap=True,
                spacing=6,
                run_spacing=6,
            )

    def _clear_order(self, e):
        """Limpa toda a frase montada."""
        if self.answered:
            return
        self.available_words.extend(self.selected_words)
        self.selected_words.clear()
        self._update_sentence_display()
        self._refresh_word_chips()
        self.check_btn.disabled = True
        self.update()

    def _check_order(self, e):
        """Verifica se a ordem está correta."""
        if self.answered:
            return
        self.answered = True

        is_correct = self.selected_words == self.q_data.correct_order

        # Feedback visual
        if is_correct:
            self.sentence_display.border = ft.Border.all(2, self.colors["correct"])
            self.sentence_display.bgcolor = "#14188150"
        else:
            self.sentence_display.border = ft.Border.all(2, self.colors["incorrect"])
            self.sentence_display.bgcolor = "#14C50337"
            # Mostrar resposta correta abaixo
            self.sentence_display.content = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    w, size=15, weight=ft.FontWeight.W_600,
                                    color=self.colors["incorrect"], no_wrap=False,
                                ),
                                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                                bgcolor="#14C50337",
                                border=ft.Border.all(1.5, self.colors["incorrect"]),
                                border_radius=Styles.BORDER_RADIUS_LG,
                            ) for w in self.selected_words
                        ],
                        wrap=True,
                        spacing=6,
                        run_spacing=6,
                    ),
                    ft.Divider(height=1, color=self.colors["border"]),
                    ft.Text("Resposta correta:", size=11, weight=ft.FontWeight.BOLD, color=self.colors["correct"]),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    w, size=15, weight=ft.FontWeight.W_600,
                                    color=self.colors["correct"], no_wrap=False,
                                ),
                                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                                bgcolor="#14188150",
                                border=ft.Border.all(1.5, self.colors["correct"]),
                                border_radius=Styles.BORDER_RADIUS_LG,
                            ) for w in self.q_data.correct_order
                        ],
                        wrap=True,
                        spacing=6,
                        run_spacing=6,
                    ),
                ],
                spacing=6,
            )

        # Desabilitar controles
        self.clear_btn.disabled = True
        self.check_btn.disabled = True
        self.word_chips_row.visible = False

        self._show_feedback(is_correct)

    # ─── FEEDBACK COMPARTILHADO ───

    def _show_feedback(self, is_correct: bool):
        """Exibe a explicação e o botão de próxima após resposta."""
        self.explanation_container.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED if is_correct else ft.Icons.CANCEL_ROUNDED,
                                color=self.colors["correct"] if is_correct else self.colors["incorrect"],
                                size=22
                            ),
                            ft.Text(
                                "Resposta Correta!" if is_correct else "Resposta Incorreta!",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=self.colors["correct"] if is_correct else self.colors["incorrect"],
                                expand=True,
                                no_wrap=False,
                            )
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        self.q_data.explanation,
                        size=13,
                        color=self.colors["text_sec"],
                        no_wrap=False,
                    )
                ],
                spacing=4,
            ),
            bgcolor=self.colors["card_bg"],
            padding=12,
            border_radius=Styles.BORDER_RADIUS_SM,
            border=ft.Border.all(1, self.colors["border"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        self.explanation_container.visible = True
        self.explanation_container.opacity = 1
        self.next_button.visible = True

        self.update()

        if self.on_answer:
            self.on_answer(is_correct)

    def handle_next(self, e):
        if self.on_next:
            self.on_next()
