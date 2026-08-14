"""Hub de flashcards e desafios de criação de frases."""

import time
import flet as ft

from ..components import FlashcardWidget, SentenceBuilderWidget, centered_content
from ..services import DataService, ProgressService
from ..theme import Styles, get_theme_colors


def flashcards_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    progress_service = ProgressService(page)
    state = {"difficulty": None, "category": None, "mode": "cards", "index": 0, "started_at": time.monotonic()}
    stage = ft.Container()

    def filtered_cards():
        cards = DataService.get_all_flashcards(state["difficulty"])
        return [card for card in cards if not state["category"] or card.category == state["category"]]

    def set_difficulty(difficulty):
        state.update({"difficulty": difficulty, "category": None, "index": 0})
        render()

    def set_mode(mode):
        state.update({"mode": mode, "index": 0})
        render()

    def rate_card(rating):
        cards = filtered_cards()
        if not cards:
            return
        card = cards[state["index"] % len(cards)]
        progress_service.record_item_recall(card.id, rating, int((time.monotonic() - state["started_at"]) * 1000))
        state["index"] = (state["index"] + 1) % len(cards)
        state["started_at"] = time.monotonic()
        render()

    def change_category(event):
        state["category"] = event.control.value or None
        state["index"] = 0
        render()

    def render():
        all_cards = DataService.get_all_flashcards(state["difficulty"])
        categories = sorted({card.category for card in all_cards})
        difficulty_controls = []
        for label, value in [("Todos", None), ("Fácil · 초급", "easy"), ("Médio · 중급", "medium"), ("Difícil · 고급", "hard")]:
            active = state["difficulty"] == value
            difficulty_controls.append(ft.OutlinedButton(
                content=ft.Text(label), on_click=lambda e, v=value: set_difficulty(v),
                style=ft.ButtonStyle(color=ft.Colors.WHITE if active else colors["primary"], bgcolor=colors["primary"] if active else colors["surface"]),
            ))
        toolbar = ft.Column(controls=[
            ft.Row(controls=difficulty_controls, wrap=True, spacing=5, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(controls=[
                ft.OutlinedButton(content=ft.Text("🃏 Flashcards"), on_click=lambda e: set_mode("cards"),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE if state["mode"] == "cards" else colors["primary"], bgcolor=colors["primary"] if state["mode"] == "cards" else colors["surface"])),
                ft.OutlinedButton(content=ft.Text("✍ Criador de frases"), on_click=lambda e: set_mode("builder"),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE if state["mode"] == "builder" else colors["primary"], bgcolor=colors["primary"] if state["mode"] == "builder" else colors["surface"])),
            ], wrap=True, alignment=ft.MainAxisAlignment.CENTER),
            ft.Dropdown(label="Categoria", value=state["category"], options=[ft.DropdownOption(key=category, text=category.title()) for category in categories],
                        on_select=change_category, width=260, visible=state["mode"] == "cards"),
            ft.Text(f"✨ {progress_service.get_total_xp()} XP · 📅 {progress_service.get_daily_streak()} dias estudados", size=12, color=colors["accent"], text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
        if state["mode"] == "cards":
            cards = filtered_cards()
            if cards:
                state["index"] %= len(cards)
                body = ft.Column(controls=[
                    ft.Text(f"{state['index'] + 1} de {len(cards)} cartões", size=12, color=colors["text_sec"], text_align=ft.TextAlign.CENTER),
                    FlashcardWidget(cards[state["index"]], is_dark, rate_card, lambda text: page.audio_service.play_korean(text)),
                ], spacing=10)
            else:
                body = ft.Text("Nenhum cartão neste filtro.", color=colors["text_sec"], text_align=ft.TextAlign.CENTER)
        else:
            levels = [state["difficulty"]] if state["difficulty"] else ["easy", "medium", "hard"]
            challenges = [challenge for level in levels for challenge in DataService.get_sentence_builder_challenges(level)]
            if challenges:
                state["index"] %= len(challenges)
                body = ft.Column(controls=[
                    ft.Text(f"Desafio {state['index'] + 1} de {len(challenges)}", size=12, color=colors["text_sec"], text_align=ft.TextAlign.CENTER),
                    SentenceBuilderWidget(challenges[state["index"]], is_dark,
                        on_complete=lambda correct: progress_service.record_daily_activity() if correct else None,
                        on_audio_click=lambda text: page.audio_service.play_korean(text)),
                    ft.TextButton(content=ft.Text("Próximo desafio →"), on_click=lambda e: next_challenge(len(challenges))),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            else:
                body = ft.Text("Ainda não há desafios nesta dificuldade.", color=colors["text_sec"])
        stage.content = ft.Column(controls=[toolbar, ft.Divider(color=colors["border"]), body], spacing=12)
        try:
            stage.update()
        except RuntimeError:
            pass

    def next_challenge(total):
        state["index"] = (state["index"] + 1) % total
        render()

    render()
    return ft.View(
        route="/flashcards",
        appbar=ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=colors["primary"], on_click=lambda e: page.router.navigate_to("/home")),
            title=ft.Text("🃏 Flashcards & 문장", weight=ft.FontWeight.BOLD, color=colors["text"]), bgcolor=colors["surface"], elevation=0,
        ),
        controls=[centered_content(page, stage, padding=ft.Padding.symmetric(horizontal=12, vertical=12))],
        bgcolor=colors["bg"], scroll=ft.ScrollMode.AUTO, padding=0,
    )
