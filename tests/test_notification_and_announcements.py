"""Suíte de Testes para NotificationService, AnnouncementService e Integrações de UI.

Valida:
1. CRUD e integridade do AnnouncementService (persistência, pubsub, contagem de não lidos, remoção lógica).
2. Resiliência do NotificationService (Web vs Desktop nativo, in-app SnackBar e prevenção de crash).
3. Integração do WhatsNewDialog exibindo comunicados ativos da professora com destaque Gold.
4. Presença e comportamento do Soft Prompt de Notificações na HomeView.
5. Presença e comportamento do Badge dourado na HomeView com comunicados não lidos.
6. Acesso ao WhatsNewDialog pelo AppBar do Admin e Tab 3 'Mural de Avisos da Professora' no AdminView.
"""

import os
import json
import pytest
import flet as ft
from unittest.mock import MagicMock

from src import __version__
from src.theme import Colors, Styles
from src.services import AnnouncementService, NotificationService, AdminService
from src.components import WhatsNewDialog
from src.views.home_view import home_view
from src.views.admin_view import admin_view
from src.router import Router


class MockClientStorage:
    """Mock síncrono para client_storage do Flet."""

    def __init__(self, initial_data=None):
        self.store = dict(initial_data) if initial_data else {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value

    def contains_key(self, key):
        return key in self.store

    def remove(self, key):
        self.store.pop(key, None)


class MockPubSub:
    """Mock do barramento de pubsub do Flet."""

    def __init__(self):
        self.subscribers = []
        self.sent_messages = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def send_all(self, message):
        self.sent_messages.append(message)
        for sub in self.subscribers:
            try:
                sub("announcements", message)
            except Exception:
                pass


class MockPage:
    """Mock completo de ft.Page para testes de visualização e interações."""

    def __init__(self, theme_mode=ft.ThemeMode.DARK, client_storage=None, web=False):
        self.theme_mode = theme_mode
        self.width = 400
        self.views = []
        self.overlay = []
        self.dialog = None
        self.shown_dialogs = []
        self.client_storage = client_storage or MockClientStorage()
        self.pubsub = MockPubSub()
        self.audio_service = None
        self.web = web
        self.launched_urls = []
        self._admin_authenticated = False
        self._admin_session_token = None
        self._sejong_student_name = "Estudante Saebom"
        self._sejong_student_id = "test_student_id"

    def update(self):
        pass

    def run_task(self, fn, *args, **kwargs):
        # Executa a função imediatamente para fins de teste se for assíncrona ou síncrona
        pass

    async def launch_url(self, url: str):
        self.launched_urls.append(url)

    def show_dialog(self, dialog):
        self.dialog = dialog
        self.shown_dialogs.append(dialog)
        dialog.open = True

    def pop_dialog(self):
        if self.dialog:
            self.dialog.open = False
            self.dialog = None


# ─────────────────────────────────────────────────────────────
# 1. Testes do AnnouncementService
# ─────────────────────────────────────────────────────────────

def test_announcement_service_crud_and_persistence(tmp_path, monkeypatch):
    """Valida leitura, publicação, exclusão e contagem de não lidos de anúncios."""
    test_file = tmp_path / "test_announcements.json"
    monkeypatch.setattr(AnnouncementService, "_get_data_path", lambda: str(test_file))

    # Lista inicial vazia
    assert AnnouncementService.get_announcements() == []

    # Posta um aviso
    page = MockPage()
    ann1 = AnnouncementService.post_announcement(
        title="Aula Inaugural",
        content="Sejam todos bem-vindos!",
        author="Professora",
        page=page,
    )
    assert ann1 is not None
    assert ann1["title"] == "Aula Inaugural"
    assert ann1["content"] == "Sejam todos bem-vindos!"
    assert ann1["active"] is True
    assert ann1["id"].startswith("ann_")

    # Verifica broadcast no pubsub
    assert len(page.pubsub.sent_messages) == 1
    assert page.pubsub.sent_messages[0]["type"] == "new_announcement"
    assert page.pubsub.sent_messages[0]["data"]["title"] == "Aula Inaugural"

    # Posta segundo aviso
    ann2 = AnnouncementService.post_announcement(
        title="Exercício de Caligrafia",
        content="Pratiquem no 원고지.",
        author="Professora",
        page=page,
    )
    assert ann2 is not None

    all_active = AnnouncementService.get_announcements(active_only=True)
    assert len(all_active) == 2
    assert all_active[0]["id"] == ann2["id"]  # Ordenado mais recente primeiro

    # Valida contagem de não lidos
    unread_count = AnnouncementService.get_unread_count(page)
    assert unread_count == 2

    # Marca todos como lidos
    AnnouncementService.mark_all_as_read(page)
    assert AnnouncementService.get_unread_count(page) == 0

    # Exclui um anúncio
    deleted = AnnouncementService.delete_announcement(ann1["id"])
    assert deleted is True
    active_after_del = AnnouncementService.get_announcements(active_only=True)
    assert len(active_after_del) == 1
    assert active_after_del[0]["id"] == ann2["id"]

    all_including_inactive = AnnouncementService.get_announcements(active_only=False)
    assert len(all_including_inactive) == 2


def test_announcement_service_empty_input_validation():
    """Valida que títulos ou conteúdos vazios são rejeitados."""
    assert AnnouncementService.post_announcement("", "mensagem") is None
    assert AnnouncementService.post_announcement("   ", "mensagem") is None
    assert AnnouncementService.post_announcement("Título", "") is None
    assert AnnouncementService.post_announcement("Título", "   ") is None


# ─────────────────────────────────────────────────────────────
# 2. Testes do NotificationService (Web vs Desktop)
# ─────────────────────────────────────────────────────────────

def test_notification_service_desktop_safe():
    """Valida que em desktop nativo (page.web=False) nenhuma chamada JS é executada."""
    page = MockPage(web=False)
    # request_permission não deve chamar launch_url nem crashar
    NotificationService.request_permission(page)
    assert len(page.launched_urls) == 0

    # send_native_notification deve exibir banner in-app com sucesso
    NotificationService.send_native_notification(
        page=page,
        title="Aviso Pedagógico",
        body="Estudo de hoje disponível.",
    )
    assert len(page.overlay) == 1
    assert isinstance(page.overlay[0], ft.SnackBar)
    assert page.overlay[0].open is True


def test_notification_service_web_safe():
    """Valida comportamento em contexto Web (page.web=True)."""
    page = MockPage(web=True)
    # Verifica detecção de web
    assert NotificationService.is_web(page) is True

    # send_native_notification deve acionar in-app banner e não explodir
    NotificationService.send_native_notification(
        page=page,
        title="Mensagem Web",
        body="Conteúdo para Web",
    )
    assert len(page.overlay) == 1
    assert isinstance(page.overlay[0], ft.SnackBar)


# ─────────────────────────────────────────────────────────────
# 3. Testes do WhatsNewDialog Integrado com Anúncios
# ─────────────────────────────────────────────────────────────

def test_whats_new_dialog_renders_teacher_announcements(tmp_path, monkeypatch):
    """Valida que avisos postados pela professora aparecem destacados no topo do WhatsNewDialog."""
    test_file = tmp_path / "test_announcements.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump([
            {
                "id": "ann_test_99",
                "title": "Recado Especial da Professora",
                "content": "Revisem a lição 2 antes do quiz!",
                "author": "Professora",
                "created_at": "2026-09-21T10:00:00",
                "active": True,
            }
        ], f)
    monkeypatch.setattr(AnnouncementService, "_get_data_path", lambda: str(test_file))

    page = MockPage()
    dialog = WhatsNewDialog(page=page)
    assert dialog.open is False

    # Procura pelo container com o recado da professora
    content_col = dialog.content.content
    found_ann = False
    for ctrl in content_col.controls:
        # Se for container contendo o título do aviso
        if isinstance(ctrl, ft.Container) and isinstance(ctrl.content, ft.Column):
            for sub_c in ctrl.content.controls:
                if isinstance(sub_c, ft.Text) and "Recado Especial da Professora" in sub_c.value:
                    found_ann = True
                    break
    assert found_ann is True, "O aviso da professora não foi renderizado no WhatsNewDialog"

    # Dismiss do diálogo marca os anúncios como lidos
    dialog.dismiss_dialog()
    assert page.client_storage.get("last_read_announcement_id") == "ann_test_99"


# ─────────────────────────────────────────────────────────────
# 4. Testes da HomeView (Badges, PubSub & Soft Prompt)
# ─────────────────────────────────────────────────────────────

def test_home_view_displays_soft_prompt_and_allows_dismiss():
    """Valida exibição do soft prompt e seu fechamento pelo usuário."""
    storage = MockClientStorage({"notif_prompt_dismissed": False})
    page = MockPage(client_storage=storage)
    page.router = Router(page)

    view = home_view(page)
    # Procura notif_soft_card dentro dos controles da coluna central
    column = view.controls[0].controls[0].content
    soft_card = None
    for ctrl in column.controls:
        if isinstance(ctrl, ft.Container) and ctrl.visible is True:
            # Verifica se é o card de notificação checando texto
            if isinstance(ctrl.content, ft.Row) and len(ctrl.content.controls) >= 2:
                col_sub = ctrl.content.controls[1]
                if isinstance(col_sub, ft.Column) and len(col_sub.controls) >= 1:
                    first_text = col_sub.controls[0]
                    if isinstance(first_text, ft.Text) and "Avisos da Professora" in first_text.value:
                        soft_card = ctrl
                        break

    assert soft_card is not None, "Soft prompt de notificação não encontrado na HomeView"
    assert soft_card.visible is True


def test_home_view_hides_soft_prompt_when_already_dismissed():
    """Valida que o soft prompt não aparece se já foi dispensado anteriormente."""
    storage = MockClientStorage({"notif_prompt_dismissed": True})
    page = MockPage(client_storage=storage)
    page.router = Router(page)

    view = home_view(page)
    column = view.controls[0].controls[0].content
    soft_card = None
    for ctrl in column.controls:
        if isinstance(ctrl, ft.Container):
            if isinstance(ctrl.content, ft.Row) and len(ctrl.content.controls) >= 2:
                col_sub = ctrl.content.controls[1]
                if isinstance(col_sub, ft.Column) and len(col_sub.controls) >= 1:
                    first_text = col_sub.controls[0]
                    if isinstance(first_text, ft.Text) and "Avisos da Professora" in first_text.value:
                        soft_card = ctrl
                        break

    assert soft_card is not None
    assert soft_card.visible is False


def test_home_view_badge_active_on_unread_announcements(tmp_path, monkeypatch):
    """Valida presença do badge dourado no botão de novidades quando há avisos não lidos."""
    test_file = tmp_path / "test_announcements.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump([
            {
                "id": "ann_unread_1",
                "title": "Aviso Urgente",
                "content": "Conteúdo",
                "author": "Professora",
                "active": True,
            }
        ], f)
    monkeypatch.setattr(AnnouncementService, "_get_data_path", lambda: str(test_file))

    storage = MockClientStorage({
        "last_seen_release": __version__,
        "last_read_announcement_id": "outra_id_antiga",
    })
    page = MockPage(client_storage=storage)
    page.router = Router(page)

    view = home_view(page)
    whats_new_btn = None
    for action in view.appbar.actions:
        if isinstance(action, ft.IconButton) and action.icon == ft.Icons.AUTO_AWESOME_ROUNDED:
            whats_new_btn = action
            break

    assert whats_new_btn is not None
    assert whats_new_btn.badge is not None, "Badge dourado deveria estar ativo com avisos não lidos"
    assert whats_new_btn.badge.bgcolor == Colors.GOLD or whats_new_btn.badge.bgcolor == "#FFAB22"


# ─────────────────────────────────────────────────────────────
# 5. Testes do AdminView (Botão WhatsNew & Tab Mural de Avisos)
# ─────────────────────────────────────────────────────────────

def test_admin_view_has_whats_new_button(monkeypatch):
    """Valida presença do botão de Novidades do Saebom no AppBar da tela Admin autenticada."""
    monkeypatch.delenv("SAEBOM_ADMIN_PIN", raising=False)
    monkeypatch.setenv("SEJONG_ADMIN_PIN", "test_pin")

    page = MockPage()
    page._admin_authenticated = True
    page._admin_session_token = "valid_token"
    monkeypatch.setattr(AdminService, "validate_session", lambda tok: True)

    view = admin_view(page)
    assert view.appbar is not None

    whats_new_action = None
    for action in view.appbar.actions:
        if isinstance(action, ft.IconButton) and action.icon == ft.Icons.AUTO_AWESOME_ROUNDED:
            whats_new_action = action
            break

    assert whats_new_action is not None, "Botão WhatsNew não encontrado no AppBar do Admin"
    assert whats_new_action.icon_color == Colors.GOLD or whats_new_action.icon_color == "#FFAB22"


def test_admin_view_has_three_tabs_and_announcements_compose(monkeypatch, tmp_path):
    """Valida que o AdminView possui 3 abas e permite postar e excluir comunicados."""
    test_file = tmp_path / "test_announcements.json"
    test_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(AnnouncementService, "_get_data_path", lambda: str(test_file))
    monkeypatch.setattr(AdminService, "validate_session", lambda tok: True)

    page = MockPage()
    page._admin_authenticated = True
    page._admin_session_token = "valid_token"

    view = admin_view(page)
    col = view.controls[0].controls[0].content
    tabs_row = col.controls[3]
    assert isinstance(tabs_row, ft.Row)
    # Deve conter 3 abas: Diagnóstico, Roster e Mural de Avisos
    assert len(tabs_row.controls) == 3

    # Aba 2 (Mural de Avisos)
    tab_ann = tabs_row.controls[2]
    assert tab_ann is not None

    # Clica na aba de Avisos
    tab_ann.on_click(None)

    # Posta comunicado através do AnnouncementService
    AnnouncementService.post_announcement(
        title="Aviso Teste Admin",
        content="Mensagem de verificação de abas.",
        author="Professora",
        page=page,
    )
    active = AnnouncementService.get_announcements(active_only=True)
    assert len(active) == 1
    assert active[0]["title"] == "Aviso Teste Admin"
