"""Testes unitários e de integração para o WhatsNewDialog e release_notes.json.

Cobre:
1. Validação estrutural e semântica de data/release_notes.json (bilinguismo PT/KR, Brand Book v3.1, ausência de 'Sejong').
2. Instanciação e controles do WhatsNewDialog (Navy, Violet, Gold, Cream, Slate, Pretendard, hierarquia visual).
3. Resiliência e fallback gracioso com arquivo inexistente ou corrompido.
4. Lógica de auto-trigger e persistência de 'last_seen_release' via client_storage na HomeView.
5. Acesso sob demanda via AppBar da HomeView.
"""

import json
import os
import tempfile
import pytest
import flet as ft

from src import __version__
from src.components import WhatsNewDialog
from src.components.whats_new_dialog import load_release_notes, _get_fallback_data
from src.theme import Colors, Styles
from src.views.home_view import home_view
from src.router import Router


class MockClientStorage:
    """Mock síncrono para o client_storage do Flet."""

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


class MockPage:
    """Mock robusto de ft.Page para testes de views e dialogs headless."""

    def __init__(self, theme_mode=ft.ThemeMode.DARK, client_storage=None):
        self.theme_mode = theme_mode
        self.width = 400
        self.views = []
        self.overlay = []
        self.dialog = None
        self.shown_dialogs = []
        self.client_storage = client_storage or MockClientStorage()
        self.audio_service = None
        self._admin_authenticated = False
        self._admin_session_token = None

    def update(self):
        pass

    def run_task(self, fn, *args, **kwargs):
        pass

    def show_dialog(self, dialog):
        self.dialog = dialog
        self.shown_dialogs.append(dialog)
        dialog.open = True

    def pop_dialog(self):
        if self.dialog:
            self.dialog.open = False
            self.dialog = None


# ─────────────────────────────────────────────────────────────
# 1. Validação de data/release_notes.json
# ─────────────────────────────────────────────────────────────

def test_release_notes_json_exists_and_is_valid():
    """Valida existência e integridade do arquivo data/release_notes.json."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "release_notes.json")
    assert os.path.exists(json_path), f"Arquivo não encontrado: {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Campos obrigatórios estruturados
    assert data["version"] == __version__
    assert "release_date" in data
    assert "title_pt" in data and len(data["title_pt"]) > 0
    assert "title_kr" in data and len(data["title_kr"]) > 0
    assert "greeting_pt" in data and len(data["greeting_pt"]) > 0
    assert "greeting_kr" in data and len(data["greeting_kr"]) > 0
    assert "highlights" in data and isinstance(data["highlights"], list)
    assert len(data["highlights"]) >= 3

    # Destaques bilingues com tags e ícones
    for h in data["highlights"]:
        assert "tag" in h and len(h["tag"]) > 0
        assert "tag_kr" in h and len(h["tag_kr"]) > 0
        assert "icon" in h and len(h["icon"]) > 0
        assert "title_pt" in h and len(h["title_pt"]) > 0
        assert "title_kr" in h and len(h["title_kr"]) > 0
        assert "desc_pt" in h and len(h["desc_pt"]) > 0


def test_release_notes_strictly_prohibits_sejong_brand():
    """Garante ausência absoluta da palavra proibida 'Sejong' nas notas de versão."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "release_notes.json")
    with open(json_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    assert "sejong" not in raw_text.lower(), (
        "Violação da diretriz de Rebranding: termo proibido 'Sejong' detectado em release_notes.json!"
    )


# ─────────────────────────────────────────────────────────────
# 2. Instanciação e Estilização Brand Book v3.1 do WhatsNewDialog
# ─────────────────────────────────────────────────────────────

def test_whats_new_dialog_instantiation_and_palette():
    """Valida controles e paleta Brand Book v3.1 (Navy, Violet, Gold, Cream, Slate)."""
    page = MockPage()
    dialog = WhatsNewDialog(page=page)

    assert isinstance(dialog, ft.AlertDialog)
    assert dialog.modal is True

    # 1. Território: Fundo Navy #02060F
    assert dialog.bgcolor == Colors.NAVY or dialog.bgcolor == "#02060F"

    # 2. Borda Arredondada
    assert isinstance(dialog.shape, ft.RoundedRectangleBorder)

    # 3. Título com ícone Gold e texto Pretendard
    assert isinstance(dialog.title, ft.Row)
    icon_container = dialog.title.controls[0]
    assert isinstance(icon_container.content, ft.Icon)
    assert (getattr(icon_container.content, "icon", None) or getattr(icon_container.content, "name", None)) == ft.Icons.AUTO_AWESOME_ROUNDED
    assert icon_container.content.color == Colors.GOLD

    title_column = dialog.title.controls[1]
    title_text = title_column.controls[0]
    assert title_text.color == Colors.CREAM
    assert title_text.font_family == "Pretendard"

    # 4. Conteúdo com largura responsiva delimitada
    content_container = dialog.content
    assert isinstance(content_container, ft.Container)
    h = getattr(content_container, "height", None) or getattr(getattr(content_container, "constraints", None), "max_height", None)
    assert h is not None and h <= 480

    column = content_container.content
    assert isinstance(column, ft.Column)
    assert column.scroll == ft.ScrollMode.AUTO

    # 5. Ação: Botão Primário Violet #8B4DFF
    assert len(dialog.actions) == 1
    cta_btn = dialog.actions[0]
    assert isinstance(cta_btn, ft.Button)
    assert cta_btn.style.bgcolor == Colors.VIOLET


# ─────────────────────────────────────────────────────────────
# 3. Resiliência a Falhas e Fallback Gracioso
# ─────────────────────────────────────────────────────────────

def test_load_release_notes_fallback_on_missing_file():
    """Valida retorno do fallback padrão quando o arquivo não existe."""
    fallback_data = load_release_notes(custom_path="/caminho/completamente/inexistente/notes.json")
    assert fallback_data is not None
    assert fallback_data["version"] == __version__
    assert "highlights" in fallback_data
    assert len(fallback_data["highlights"]) >= 3


def test_load_release_notes_fallback_on_corrupt_json():
    """Valida tolerância a falhas quando o JSON está corrompido com sintaxe inválida."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as f:
        f.write("{ invalid json [ broken syntax ...")
        temp_file = f.name

    try:
        data = load_release_notes(custom_path=temp_file)
        assert data is not None
        assert data["version"] == __version__
        assert len(data["highlights"]) >= 3
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_whats_new_dialog_renders_gracefully_with_corrupt_data():
    """Valida instanciação do dialog sem exceções mesmo se o arquivo estiver corrompido."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as f:
        f.write("{ corrupt json")
        temp_file = f.name

    try:
        dialog = WhatsNewDialog(release_notes_path=temp_file)
        assert isinstance(dialog, WhatsNewDialog)
        assert dialog.title is not None
        assert dialog.content is not None
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# ─────────────────────────────────────────────────────────────
# 4. Lógica de Dismissal e Persistência
# ─────────────────────────────────────────────────────────────

def test_whats_new_dialog_dismiss_callback_and_page_close():
    """Valida execução segura do callback e fechamento do modal."""
    page = MockPage()
    dismissed = False

    def on_close():
        nonlocal dismissed
        dismissed = True

    dialog = WhatsNewDialog(page=page, on_dismiss=on_close)
    page.show_dialog(dialog)
    assert dialog.open is True

    # Clique no botão de ação
    dialog.dismiss_dialog()
    assert dismissed is True
    assert dialog.open is False

    # Múltiplas chamadas não disparam duplicatas
    dismissed = False
    dialog.dismiss_dialog()
    assert dismissed is False


# ─────────────────────────────────────────────────────────────
# 5. Integração na HomeView (Auto-Trigger e Sob Demanda)
# ─────────────────────────────────────────────────────────────

def test_home_view_auto_triggers_dialog_when_release_is_new():
    """Valida abertura automática única quando last_seen_release é diferente de __version__."""
    storage = MockClientStorage({"last_seen_release": "0.3.5-alpha"})
    page = MockPage(client_storage=storage)
    page.router = Router(page)

    view = home_view(page)
    assert len(page.shown_dialogs) == 1
    dialog = page.shown_dialogs[0]
    assert isinstance(dialog, WhatsNewDialog)

    # Ao fechar o modal, client_storage é atualizado com __version__
    dialog.dismiss_dialog()
    assert storage.get("last_seen_release") == __version__


def test_home_view_does_not_auto_trigger_when_already_seen():
    """Valida que o modal NÃO abre automaticamente se a versão já foi vista."""
    storage = MockClientStorage({"last_seen_release": __version__})
    page = MockPage(client_storage=storage)
    page.router = Router(page)

    view = home_view(page)
    assert len(page.shown_dialogs) == 0


def test_home_view_app_bar_contains_whats_new_button():
    """Valida presença do botão sob demanda na AppBar da HomeView."""
    storage = MockClientStorage({"last_seen_release": __version__})
    page = MockPage(client_storage=storage)
    page.router = Router(page)

    view = home_view(page)
    app_bar = view.appbar
    assert app_bar is not None

    # Procura o botão com ícone AUTO_AWESOME_ROUNDED e tooltip correspondente
    whats_new_action = None
    for action in app_bar.actions:
        if isinstance(action, ft.IconButton) and action.icon == ft.Icons.AUTO_AWESOME_ROUNDED:
            whats_new_action = action
            break

    assert whats_new_action is not None, "Botão de novidades não encontrado na AppBar da HomeView"
    assert "Novidades do Saebom" in whats_new_action.tooltip
    assert whats_new_action.icon_color == Colors.GOLD or whats_new_action.icon_color == "#FFAB22"

    # Aciona o botão manualmente e valida que abre o WhatsNewDialog
    assert len(page.shown_dialogs) == 0
    whats_new_action.on_click(None)
    assert len(page.shown_dialogs) == 1
    assert isinstance(page.shown_dialogs[0], WhatsNewDialog)
