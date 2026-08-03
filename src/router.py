import flet as ft
from typing import Dict, Callable

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, Callable[[ft.Page], ft.View]] = {}
        # Estado global simples mantido no roteador
        self.current_unit_id: str = "unit_intro"
        
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

    def register_route(self, route_name: str, view_builder: Callable[[ft.Page], ft.View]):
        self.routes[route_name] = view_builder

    def route_change(self, e: ft.RouteChangeEvent):
        # Limpar views anteriores para evitar duplicados
        self.page.views.clear()
        
        # Tratar a rota básica
        route = e.route
        base_route = route.split("?")[0]
        
        # Construir e adicionar a nova view correspondente
        if base_route in self.routes:
            view = self.routes[base_route](self.page)
            self.page.views.append(view)
        else:
            # Rota padrão de fallback
            if "/splash" in self.routes:
                self.page.views.append(self.routes["/splash"](self.page))
            elif "/home" in self.routes:
                self.page.views.append(self.routes["/home"](self.page))
        
        try:
            self.page.update()
        except Exception:
            pass

    def view_pop(self, e: ft.ViewPopEvent):
        try:
            if len(self.page.views) > 1:
                self.page.views.pop()
                top_view = self.page.views[-1]
                self.page.go(top_view.route)
        except Exception:
            pass

    def navigate_to(self, route_name: str, unit_id: str = None):
        if unit_id:
            self.current_unit_id = unit_id
        try:
            self.page.go(route_name)
        except Exception:
            pass
