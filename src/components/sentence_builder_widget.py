"""Criador de frases com blocos SOV e modo de digitação Hangul."""

import flet as ft

from ..theme import Styles, get_theme_colors


class SentenceBuilderWidget(ft.Container):
    def __init__(self, challenge: dict, is_dark: bool, on_complete=None, on_audio_click=None):
        self.challenge = challenge
        self.colors = get_theme_colors(is_dark)
        self.on_complete = on_complete
        self.on_audio_click = on_audio_click
        self.mode = "blocks"
        self.selected_indexes = []
        self.feedback = ""
        self.feedback_color = self.colors["text_sec"]
        self.answer_input = ft.TextField(
            hint_text="Digite a frase em 한글",
            border_color=self.colors["border"],
            color=self.colors["text"],
            text_size=16,
        )
        super().__init__(
            bgcolor=self.colors["card_bg"], border=ft.Border.all(1, self.colors["border"]),
            border_radius=Styles.BORDER_RADIUS_LG, padding=16, content=self._build_content(),
        )

    def _build_content(self):
        mode_controls = ft.Row(
            controls=[
                ft.OutlinedButton(content=ft.Text("▣ Modo blocos"), on_click=lambda e: self._set_mode("blocks")),
                ft.OutlinedButton(content=ft.Text("⌨ Digitar Hangul"), on_click=lambda e: self._set_mode("typing")),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        body = self._build_blocks() if self.mode == "blocks" else self._build_typing()
        controls = [
            ft.Text("Criação de frase", size=13, weight=ft.FontWeight.BOLD, color=self.colors["primary"]),
            ft.Text(self.challenge["prompt_pt"], size=18, weight=ft.FontWeight.BOLD, color=self.colors["text"], text_align=ft.TextAlign.CENTER),
            mode_controls,
            body,
        ]
        if self.feedback:
            controls.append(ft.Text(self.feedback, size=12, color=self.feedback_color, text_align=ft.TextAlign.CENTER))
        return ft.Column(controls=controls, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _build_blocks(self):
        words = self.challenge["words"]
        selected_words = [words[index] for index in self.selected_indexes]
        role_by_word = {item["word"]: item.get("role", "") for item in self.challenge.get("sov_breakdown", [])}
        role_colors = {"SUBJECT": self.colors["role_subject"], "OBJECT": self.colors["role_object"], "VERB": self.colors["role_verb"], "PREDICATE": self.colors["role_predicate"], "COMPLEMENT": self.colors["role_object"]}
        selected = ft.Container(
            content=ft.Text(" ".join(selected_words) or "Toque nas palavras para montar a frase", size=16, color=self.colors["text"], text_align=ft.TextAlign.CENTER),
            bgcolor=self.colors["surface"], border=ft.Border.all(1, self.colors["primary_light"]),
            border_radius=Styles.BORDER_RADIUS_SM, padding=12, width=500,
        )
        word_controls = []
        for index, word in enumerate(words):
            used = index in self.selected_indexes
            color = role_colors.get(role_by_word.get(word), self.colors["primary"])
            word_controls.append(ft.Container(
                content=ft.Text(word, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if not used else self.colors["text_sec"]),
                bgcolor=color if not used else self.colors["border"], border_radius=Styles.BORDER_RADIUS_SM,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                on_click=(lambda e, i=index: self._add_word(i)) if not used else None,
            ))
        return ft.Column(controls=[
            selected,
            ft.Row(controls=word_controls, wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            ft.Row(controls=[
                ft.TextButton(content=ft.Text("Desfazer"), on_click=self._undo),
                ft.ElevatedButton(content=ft.Text("Conferir"), on_click=self._check_blocks, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=self.colors["primary"])),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _build_typing(self):
        return ft.Column(controls=[
            self.answer_input,
            ft.ElevatedButton(content=ft.Text("Validar frase"), on_click=self._check_typing, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=self.colors["primary"])),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _set_mode(self, mode: str):
        self.mode = mode
        self._refresh()

    def _add_word(self, index: int):
        self.selected_indexes.append(index)
        self._refresh()

    def _undo(self, _event):
        if self.selected_indexes:
            self.selected_indexes.pop()
        self._refresh()

    def _check_blocks(self, _event):
        attempt = [self.challenge["words"][index] for index in self.selected_indexes]
        self._set_feedback(attempt == self.challenge["correct_order"])

    def _check_typing(self, _event):
        import re
        normalize = lambda value: " ".join(re.sub(r"[.?!,~;:]", "", value or "").strip().split())
        self._set_feedback(normalize(self.answer_input.value) == normalize(self.challenge["answer"]))

    def _set_feedback(self, correct: bool):
        if correct:
            self.feedback = "✅ Excelente! A estrutura da frase está correta."
            self.feedback_color = self.colors["correct"]
            if self.on_audio_click:
                self.on_audio_click(self.challenge["answer"])
            if self.on_complete:
                self.on_complete(True)
        else:
            self.feedback = "↺ Quase! Observe a ordem Sujeito + complementos + verbo."
            self.feedback_color = self.colors["incorrect"]
        self._refresh()

    def _refresh(self):
        self.content = self._build_content()
        try:
            self.update()
        except Exception:
            pass
