import flet as ft
from typing import Dict, Callable

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, Callable[[ft.Page], ft.View]] = {}
        self.current_unit_id: str = "unit_intro"
        self._history: list[str] = []
        
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

    def register_route(self, route_name: str, view_builder: Callable[[ft.Page], ft.View]):
        self.routes[route_name] = view_builder

    def route_change(self, e: ft.RouteChangeEvent):
        route = e.route or "/splash"
        base_route = route.split("?")[0]
        if base_route in ("", "/"):
            base_route = "/splash"
        
        # Gerenciar histórico
        if not self._history or self._history[-1] != base_route:
            if base_route in ("/splash", "/onboarding", "/home"):
                self._history = [base_route]
            else:
                self._history.append(base_route)

        target_builder = self.routes.get(base_route) or self.routes.get("/splash") or self.routes.get("/home")
        view = None
        if target_builder:
            try:
                view = target_builder(self.page)
            except Exception as ex:
                print(f"[Router] Erro ao construir view '{base_route}': {ex}")
                fallback_builder = self.routes.get("/home") or self.routes.get("/splash")
                if fallback_builder and fallback_builder != target_builder:
                    try:
                        view = fallback_builder(self.page)
                    except Exception:
                        pass

        if view is not None:
            self.page.views.clear()
            self.page.views.append(view)
        elif not self.page.views:
            # Fallback defensivo para garantir que views nunca fique vazia (prevenção de tela preta)
            self.page.views.append(
                ft.View(
                    route=base_route,
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(width=32, height=32),
                                    ft.Text("Carregando...", size=14, color="#9EA2AE"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.Alignment.CENTER,
                            expand=True,
                        )
                    ],
                    bgcolor="#02060F",
                )
            )

        try:
            self.page.update()
        except Exception:
            pass

    def _go_to(self, route_name: str):
        try:
            self.page.go(route_name)
        except Exception:
            pass

    def view_pop(self, e: ft.ViewPopEvent = None):
        try:
            if len(self._history) > 1:
                self._history.pop()
                prev_route = self._history[-1]
                self._go_to(prev_route)
            else:
                self._go_to("/home")
        except Exception:
            self._go_to("/home")

    def navigate_to(self, route_name: str, unit_id: str = None):
        if unit_id:
            self.current_unit_id = unit_id
        self._go_to(route_name)
