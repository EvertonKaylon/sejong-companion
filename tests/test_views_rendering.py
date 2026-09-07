"""Testes automatizados de renderização e integridade estrutural das rotas/views.
Garante que todas as views do aplicativo sejam instanciadas sem erros de atributos do Flet
(ex: BoxFit vs ImageFit) tanto em Dark Mode quanto em Light Mode.
"""

import pytest
import flet as ft
from src.views import APP_ROUTES
from src.router import Router


class MockPage:
    """Mock leve para testes de instanciação headless de views."""
    def __init__(self, theme_mode=ft.ThemeMode.DARK):
        self.theme_mode = theme_mode
        self.width = 400
        self.views = []
        self.client_storage = None
        self.overlay = []
        self.services = []
        self.audio_service = None
        self._admin_authenticated = False
        self._admin_session_token = None

    def update(self):
        pass

    def run_task(self, fn):
        pass


@pytest.mark.parametrize("route_name", list(APP_ROUTES.keys()))
@pytest.mark.parametrize("theme_mode", [ft.ThemeMode.DARK, ft.ThemeMode.LIGHT])
def test_all_views_instantiation(route_name, theme_mode):
    """Valida que cada view registra uma rota válida e instancia sem AttributeError."""
    page = MockPage(theme_mode=theme_mode)
    router = Router(page)
    page.router = router
    page.router.current_unit_id = "unit_01"

    view_builder = APP_ROUTES[route_name]
    view = view_builder(page)

    assert isinstance(view, ft.View), f"A rota {route_name} deve retornar uma instância de ft.View"
    assert view.route == route_name, f"O atributo route da view deve corresponder a {route_name}"
    assert len(view.controls) > 0, f"A rota {route_name} deve possuir controles renderizados"
