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


def test_hangul_view_contains_syllable_factory_and_dialpad():
    """Garante que a view de Hangul monta ativamente a Fábrica de Sílabas e o Teclado Numérico (Dialpad)."""
    from src.components.syllable_factory import SyllableFactory
    from src.components.number_training import NumberTraining

    page = MockPage(theme_mode=ft.ThemeMode.DARK)
    router = Router(page)
    page.router = router

    view = APP_ROUTES["/hangul"](page)
    found_factory = False
    found_dialpad = False

    def search_controls(ctrl):
        nonlocal found_factory, found_dialpad
        if isinstance(ctrl, SyllableFactory):
            found_factory = True
        if isinstance(ctrl, NumberTraining):
            found_dialpad = True

        if hasattr(ctrl, "controls") and isinstance(ctrl.controls, list):
            for ch in ctrl.controls:
                search_controls(ch)
        elif hasattr(ctrl, "content") and ctrl.content:
            search_controls(ctrl.content)

        if hasattr(ctrl, "data") and isinstance(ctrl.data, list):
            for ch in ctrl.data:
                search_controls(ch)

    for c in view.controls:
        search_controls(c)

    assert found_factory is True, "SyllableFactory DEVE estar montado na aba de Sílabas em /hangul"
    assert found_dialpad is True, "NumberTraining (Dialpad) DEVE estar montado na aba de Sílabas em /hangul"


def test_lesson_view_unit_03_mounts_spatial_stage():
    """Garante que a Lição 03 monta ativamente o Diorama Espacial (SpatialStage) na aba de gramática."""
    from src.components.spatial_stage import SpatialStage

    page = MockPage(theme_mode=ft.ThemeMode.DARK)
    router = Router(page)
    page.router = router
    page.router.current_unit_id = "unit_03"

    view = APP_ROUTES["/lesson"](page)
    found_spatial = False

    def search_controls(ctrl):
        nonlocal found_spatial
        if isinstance(ctrl, SpatialStage):
            found_spatial = True

        if hasattr(ctrl, "controls") and isinstance(ctrl.controls, list):
            for ch in ctrl.controls:
                search_controls(ch)
        elif hasattr(ctrl, "content") and ctrl.content:
            search_controls(ctrl.content)

    for c in view.controls:
        search_controls(c)

    assert found_spatial is True, "SpatialStage DEVE estar montado na gramática da Lição 03"


def test_hangul_view_calligraphy_buttons_use_saebom_brand_chars():
    """Valida que os botões de caligrafia do /hangul usam 새/봄 e não contêm 세/종."""
    page = MockPage(theme_mode=ft.ThemeMode.DARK)
    router = Router(page)
    page.router = router

    view = APP_ROUTES["/hangul"](page)
    button_labels = []

    def collect_texts(ctrl):
        if isinstance(ctrl, ft.Text) and ctrl.value:
            button_labels.append(ctrl.value)
        if hasattr(ctrl, "controls") and isinstance(ctrl.controls, list):
            for ch in ctrl.controls:
                collect_texts(ch)
        elif hasattr(ctrl, "content") and ctrl.content:
            collect_texts(ctrl.content)
        if hasattr(ctrl, "data") and isinstance(ctrl.data, list):
            for ch in ctrl.data:
                collect_texts(ch)

    for c in view.controls:
        collect_texts(c)

    single_chars = {lbl for lbl in button_labels if len(lbl) == 1}
    assert "새" in single_chars
    assert "봄" in single_chars
    assert "세" not in single_chars
    assert "종" not in single_chars

