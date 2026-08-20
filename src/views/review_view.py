"""Tela de revisão diária baseada na fila de retenção por meia-vida (SRS)."""

import time
import flet as ft

from ..components import FlashcardWidget, centered_content
from ..models import PedagogicalEvent
from ..services import ProgressService, TelemetryService
from ..theme import Styles, get_theme_colors


def review_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    progress_service = ProgressService(page)
    session_id = ProgressService._get_session_id(page)
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
        
        # Telemetria de conclusão da sessão de revisão
        TelemetryService.record(
            session_id,
            PedagogicalEvent(
                event_type="review_completed",
                unit_id="all",
                payload={
                    "cards_reviewed": reviewed,
                    "xp_earned": progress_service.get_total_xp() - state['starting_xp'],
                },
            ),
        )

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

        # Telemetria da avaliação do flashcard
        TelemetryService.record(
            session_id,
            PedagogicalEvent(
                event_type="flashcard_rated",
                unit_id=card.unit_id,
                item_id=card.id,
                payload={
                    "rating": rating,
                    "response_time_ms": elapsed_ms,
                },
            ),
        )

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
        content.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=52, color=colors["accent"]),
                            ft.Text(
                                "✨ Sua revisão adaptativa está em dia!",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=colors["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Nenhum item estudado está abaixo do limiar crítico de retenção (75%).",
                                size=13,
                                color=colors["text_sec"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=ft.Padding.symmetric(vertical=6),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Você ainda pode:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=colors["text"],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.AUTO_STORIES_ROUNDED, size=18, color=colors["primary"]),
                                    ft.Text(
                                        "• Aprender conteúdo novo na trilha",
                                        size=13,
                                        color=colors["text"],
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.FITNESS_CENTER_ROUNDED, size=18, color=colors["secondary"]),
                                    ft.Text(
                                        "• Fazer prática preventiva nos flashcards",
                                        size=13,
                                        color=colors["text"],
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=18, color=colors["accent"]),
                                    ft.Text(
                                        "• Revisar unidades específicas no menu",
                                        size=13,
                                        color=colors["text"],
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=colors["card_bg"],
                    padding=16,
                    border_radius=Styles.BORDER_RADIUS_MD,
                    border=ft.Border.all(1, colors["border"]),
                ),
                ft.Container(height=4),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Text("Continuar Trilha"),
                            icon=ft.Icons.EXPLORE_ROUNDED,
                            on_click=lambda e: page.router.navigate_to("/home"),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=colors["primary"],
                                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                                padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                            ),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Prática Preventiva"),
                            icon=ft.Icons.STYLE_ROUNDED,
                            on_click=lambda e: page.router.navigate_to("/flashcards"),
                            style=ft.ButtonStyle(
                                color=colors["text"],
                                side=ft.BorderSide(1, colors["border"]),
                                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                                padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        )

    return ft.View(
        route="/review",
        appbar=ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color=colors["primary"], on_click=back),
            title=ft.Text("🔥 Revisão do Dia", weight=ft.FontWeight.BOLD, color=colors["text"]), bgcolor=colors["surface"], elevation=0,
        ),
        controls=[centered_content(page, content, padding=ft.Padding.symmetric(horizontal=14, vertical=18))],
        bgcolor=colors["bg"], scroll=ft.ScrollMode.AUTO, padding=0,
    )
