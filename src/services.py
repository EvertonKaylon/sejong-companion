import json
import os
from typing import List, Optional
import flet as ft
from .models import Unit, UnitIntroData, UnitOneData

class DataService:
    @staticmethod
    def get_curriculum() -> List[Unit]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "curriculum.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Unit(**item) for item in data]
        except Exception as e:
            print(f"Error loading curriculum: {e}")
            return []

    @staticmethod
    def get_unit_intro() -> Optional[UnitIntroData]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "units", "unit_intro.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UnitIntroData(**data)
        except Exception as e:
            print(f"Error loading unit_intro: {e}")
            return None

    @staticmethod
    def get_unit_one() -> Optional[UnitOneData]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "units", "unit_01.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UnitOneData(**data)
        except Exception as e:
            print(f"Error loading unit_01: {e}")
            return None

class ProgressService:
    """Gerenciador de progresso e preferências em memória (alpha).
    Usa um dicionário simples ao invés de shared_preferences (assíncrono)
    para compatibilidade com a construção síncrona das views do Flet."""
    
    _store: dict = {}

    def __init__(self, page: ft.Page):
        self.page = page

    def get_progress(self, unit_id: str) -> float:
        val = ProgressService._store.get(f"progress_{unit_id}", 0.0)
        return float(val)

    def save_progress(self, unit_id: str, progress: float) -> None:
        ProgressService._store[f"progress_{unit_id}"] = float(progress)
        
        # Lógica de desbloqueio simples para o Beta
        if progress >= 1.0:
            if unit_id == "unit_intro":
                ProgressService._store["unlocked_unit_01"] = True
            elif unit_id == "unit_01":
                ProgressService._store["unlocked_unit_02"] = True

    def is_unlocked(self, unit_id: str) -> bool:
        if unit_id in ["unit_intro", "unit_01"]:
            return True
        return bool(ProgressService._store.get(f"unlocked_{unit_id}", False))


class FullscreenService:
    """Serviço para alternância de Tela Cheia (Fullscreen) e responsividade Mobile/PWA."""

    _is_fullscreen: bool = False

    @staticmethod
    def toggle_fullscreen(page: ft.Page):
        FullscreenService._is_fullscreen = not FullscreenService._is_fullscreen

        # 1. Execução via JavaScript no navegador (Mobile Browser / PWA & Web Desktop)
        js_code = (
            "if(!document.fullscreenElement && !document.webkitFullscreenElement && !document.mozFullScreenElement && !document.msFullscreenElement){"
            "var docEl=document.documentElement;"
            "var req=docEl.requestFullscreen||docEl.webkitRequestFullscreen||docEl.mozRequestFullScreen||docEl.msRequestFullscreen;"
            "if(req){req.call(docEl);}"
            "}else{"
            "var exit=document.exitFullscreen||document.webkitExitFullscreen||document.mozCancelFullScreen||document.msExitFullscreen;"
            "if(exit){exit.call(document);}"
            "}"
        )

        async def _exec_fullscreen():
            try:
                if hasattr(page, 'launch_url'):
                    await page.launch_url(f"javascript:{js_code}")
            except Exception as ex:
                print(f"Fullscreen JS error: {ex}")

        try:
            if hasattr(page, 'run_task'):
                page.run_task(_exec_fullscreen)
        except Exception as e:
            print(f"Task error: {e}")

        # 2. Atualização de estado nativo (Desktop Flet App se disponível)
        try:
            win = getattr(page, "window", None)
            if win and hasattr(win, "full_screen"):
                win.full_screen = FullscreenService._is_fullscreen
                page.update()
        except Exception:
            pass

    @staticmethod
    def setup_mobile_responsive_viewport(page: ft.Page):
        """Injeta meta-tags de viewport e PWA para o navegador mobile se comportar como App instalado."""
        js_meta = (
            "(function(){"
            "var m=document.querySelector('meta[name=\"viewport\"]');"
            "if(!m){m=document.createElement('meta');m.name='viewport';document.head.appendChild(m);}"
            "m.content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';"
            "var t=document.querySelector('meta[name=\"theme-color\"]');"
            "if(!t){t=document.createElement('meta');t.name='theme-color';document.head.appendChild(t);}"
            "t.content='#02060E';"
            "var ap=document.createElement('meta');ap.name='apple-mobile-web-app-capable';ap.content='yes';document.head.appendChild(ap);"
            "var st=document.createElement('meta');st.name='apple-mobile-web-app-status-bar-style';st.content='black-translucent';document.head.appendChild(st);"
            "})();"
        )

        async def _exec_meta():
            try:
                if hasattr(page, 'launch_url'):
                    await page.launch_url(f"javascript:{js_meta}")
            except Exception as ex:
                print(f"Viewport JS error: {ex}")

        try:
            if hasattr(page, 'run_task'):
                page.run_task(_exec_meta)
        except Exception as e:
            print(f"Task meta error: {e}")

    @staticmethod
    def create_fullscreen_button(page: ft.Page, colors: dict) -> ft.IconButton:
        """Cria um botão com ícone de entrar/sair da Tela Cheia para ser usado nas AppBars."""
        return ft.IconButton(
            icon=ft.Icons.FULLSCREEN_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: FullscreenService.toggle_fullscreen(page),
            tooltip="Alternar Modo Tela Cheia (Fullscreen)",
        )


