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


def test_image_asset_paths_are_absolute_for_web():
    """Garante que todas as imagens declaradas nas views usem caminho absoluto com barra inicial.
    
    Caminhos relativos (ex: 'branding/app_icon.png') causam erro 404 no Flutter Web
    quando o navegador está em rotas aninhadas como /splash ou /onboarding.
    """
    page = MockPage()
    router = Router(page)
    page.router = router

    def extract_images(control):
        images = []
        if isinstance(control, ft.Image):
            images.append(control)
        # Inspecionar atributos de controles aninhados
        for child_attr in ("content", "controls", "leading", "actions"):
            child = getattr(control, child_attr, None)
            if isinstance(child, list):
                for item in child:
                    images.extend(extract_images(item))
            elif child is not None:
                images.extend(extract_images(child))
        return images

    checked_routes = ["/splash", "/home", "/onboarding"]
    total_images = 0
    for r in checked_routes:
        view = APP_ROUTES[r](page)
        # AppBar também pode conter leading com imagem
        images = []
        if getattr(view, "appbar", None):
            images.extend(extract_images(view.appbar))
        for c in view.controls:
            images.extend(extract_images(c))

        for img in images:
            total_images += 1
            assert img.src.startswith("/") or img.src.startswith("http"), (
                f"Imagem na rota {r} possui caminho relativo perigoso '{img.src}'. "
                f"Deve começar com '/' para resolução estática correta no Flutter Web."
            )

    assert total_images >= 3, f"Esperado ao menos 3 imagens de branding testadas, encontradas {total_images}"
