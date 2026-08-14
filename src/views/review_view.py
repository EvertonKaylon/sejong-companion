"""Tela de revisão diária baseada na fila HLR de cartões vencidos."""

import time
import flet as ft

from ..components import FlashcardWidget, centered_content
from ..services import ProgressService
from ..theme import Styles, get_theme_colors


def review_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    progress_service = ProgressService(page)
    due_entries = progress_service.get_due_reviews()
    state = {
        "cards": [entry["item"] for entry in due_entries],
        "index": 0,
        "starting_xp": progress_service.get_total_xp(),
        "history": [],
        "started_at": time.monotonic(),
    }
    content = ft.Container()

    def back(_event=None):
        page.router.navigate_to("/home")

    def render_complete():
        reviewed = len(state["history"])
        content.content = ft.Column(
            controls=[
                ft.Icon(ft.Icons.CELEBRATION_ROUNDED, color=colors["accent"], size=58),
                ft.Text("Revisão concluída!", size=24, weight=ft.FontWeight.BOLD, color=colors["text"]),
                ft.Text(f"{reviewed} recordações consolidadas · +{progress_service.get_total_xp() - state['starting_xp']} XP hoje", size=14, color=colors["text_sec"], text_align=ft.TextAlign.CENTER),
                ft.Text(f"📅 {progress_service.get_daily_streak()} dias estudados · ✨ {progress_service.get_total_xp()} XP", size=14, color=colors["accent"]),
                ft.ElevatedButton(content=ft.Text("Voltar à Home"), icon=ft.Icons.HOME_ROUNDED, on_click=back,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=colors["primary"])),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14,
        )
        content.update()

    def rate_card(rating: str):
        card = state["cards"][state["index"]]
        elapsed_ms = int((time.monotonic() - state["started_at"]) * 1000)
        progress_service.record_item_recall(card.id, rating, elapsed_ms)
        state["history"].append({"item_id": card.id, "rating": rating})
        if rating == "again":
            # Active recall: um erro reaparece no fim da mesma sessão.
            state["cards"].append(card)
        state["index"] += 1
        state["started_at"] = time.monotonic()
        if state["index"] >= len(state["cards"]):
            render_complete()
        else:
            render_current()

    def render_current():
        index = state["index"]
        total = len(state["cards"])
        card = state["cards"][index]
        retention = next((entry["retention"] for entry in due_entries if entry["item"].id == card.id), 0.0)
        content.content = ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Text(f"Cartão {index + 1} de {total}", size=12, color=colors["text_sec"]),
                    ft.Text(f"📅 {progress_service.get_daily_streak()} dias  ·  ✨ {progress_service.get_total_xp()} XP", size=12, color=colors["accent"]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ProgressBar(value=index / total if total else 0, color=colors["secondary"], bgcolor=colors["border"], height=6),
                ft.Text(f"Retenção estimada: {int(retention * 100)}%", size=12, color=colors["incorrect"] if retention < .35 else colors["warning"]),
                FlashcardWidget(card, is_dark, on_rate=rate_card, on_audio_click=lambda text: page.audio_service.play_korean(text)),
            ], spacing=12,
        )
        content.update()

    if state["cards"]:
        # A primeira montagem ainda não está ligada à página; apenas atribuir.
        index, total = 0, len(state["cards"])
        card = state["cards"][0]
        retention = due_entries[0]["retention"]
        content.content = ft.Column(controls=[
            ft.Row(controls=[
                ft.Text(f"Cartão {index + 1} de {total}", size=12, color=colors["text_sec"]),
                ft.Text(f"📅 {progress_service.get_daily_streak()} dias  ·  ✨ {progress_service.get_total_xp()} XP", size=12, color=colors["accent"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(value=0, color=colors["secondary"], bgcolor=colors["border"], height=6),
            ft.Text(f"Retenção estimada: {int(retention * 100)}%", size=12, color=colors["incorrect"] if retention < .35 else colors["warning"]),
            FlashcardWidget(card, is_dark, on_rate=rate_card, on_audio_click=lambda text: page.audio_service.play_korean(text)),
        ], spacing=12)
    else:
        content.content = ft.Column(controls=[
            ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=56, color=colors["correct"]),
            ft.Text("Tudo em dia! ✨", size=23, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Text("Nenhum cartão estudado está abaixo de 75% de retenção. Explore a trilha para uma revisão preventiva.",
                    size=13, color=colors["text_sec"], text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(content=ft.Text("Abrir Flashcards"), icon=ft.Icons.STYLE_ROUNDED,
                on_click=lambda e: page.router.navigate_to("/flashcards"),
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=colors["primary"])),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14)

    return ft.View(
        route="/review",
        appbar=ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=colors["primary"], on_click=back),
            title=ft.Text("🔥 Revisão do Dia", weight=ft.FontWeight.BOLD, color=colors["text"]), bgcolor=colors["surface"], elevation=0,
        ),
        controls=[centered_content(page, content, padding=ft.Padding.symmetric(horizontal=14, vertical=18))],
        bgcolor=colors["bg"], scroll=ft.ScrollMode.AUTO, padding=0,
    )
