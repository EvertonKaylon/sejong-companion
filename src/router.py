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
        
        # Gerenciar histórico
        if not self._history or self._history[-1] != base_route:
            if base_route in ("/splash", "/onboarding", "/home"):
                self._history = [base_route]
            else:
                self._history.append(base_route)

        self.page.views.clear()
        
        if base_route in self.routes:
            view = self.routes[base_route](self.page)
            self.page.views.append(view)
        else:
            if "/splash" in self.routes:
                self.page.views.append(self.routes["/splash"](self.page))
            elif "/home" in self.routes:
                self.page.views.append(self.routes["/home"](self.page))
        
        try:
            self.page.update()
        except Exception:
            pass

    def view_pop(self, e: ft.ViewPopEvent = None):
        try:
            if len(self._history) > 1:
                self._history.pop()
                prev_route = self._history[-1]
                self.page.go(prev_route)
            else:
                self.page.go("/home")
        except Exception:
            try:
                self.page.go("/home")
            except Exception:
                pass

    def navigate_to(self, route_name: str, unit_id: str = None):
        if unit_id:
            self.current_unit_id = unit_id
        try:
            self.page.go(route_name)
        except Exception:
            pass
