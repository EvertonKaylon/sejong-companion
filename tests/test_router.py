import unittest
import flet as ft
from src.router import Router

class MockPage:
    def __init__(self):
        self.views = []
        self.on_route_change = None
        self.on_view_pop = None
        self.route = None
        self.updated_calls = 0

    def update(self):
        self.updated_calls += 1

    def go(self, route):
        self.route = route
        if self.on_route_change:
            class MockEvent:
                def __init__(self, route):
                    self.route = route
            self.on_route_change(MockEvent(route))

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.page = MockPage()
        self.router = Router(self.page)
        
        # Mock view builders
        self.router.register_route("/splash", lambda page: ft.View(route="/splash"))
        self.router.register_route("/home", lambda page: ft.View(route="/home"))
        self.router.register_route("/lesson", lambda page: ft.View(route="/lesson"))

    def test_register_route(self):
        self.assertIn("/splash", self.router.routes)
        self.assertIn("/home", self.router.routes)

    def test_navigate_to(self):
        # Navegar com parâmetro de unidade
        self.router.navigate_to("/lesson", "unit_01")
        self.assertEqual(self.router.current_unit_id, "unit_01")
        self.assertEqual(self.page.route, "/lesson")
        self.assertEqual(len(self.page.views), 1)
        self.assertEqual(self.page.views[0].route, "/lesson")
        self.assertEqual(self.page.updated_calls, 1)

    def test_fallback_route(self):
        # Rota inexistente deve ir para /splash se cadastrada
        self.page.go("/invalid_route")
        self.assertEqual(len(self.page.views), 1)
        self.assertEqual(self.page.views[0].route, "/splash")

    def test_view_pop(self):
        # Adicionar views simuladas
        view1 = ft.View(route="/home")
        view2 = ft.View(route="/lesson")
        self.page.views = [view1, view2]

        class MockPopEvent:
            pass

        self.router.view_pop(MockPopEvent())
        
        # Deve remover a de cima (/lesson) e navegar para a restante (/home)
        self.assertEqual(len(self.page.views), 1)
        self.assertEqual(self.page.route, "/home")

if __name__ == "__main__":
    unittest.main()
