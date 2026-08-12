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
    """Gerenciador de progresso com persistência em disco e isolamento por sessão.
    
    Cada sessão Flet (aba do navegador / conexão) recebe um UUID único, garantindo
    que múltiplos usuários simultâneos em modo web não compartilhem progresso.
    Os dados são persistidos em data/sessions/{session_id}.json de forma atômica.
    """
    
    _file_path_override: Optional[str] = None  # Override para testes
    _sessions: dict = {}  # {session_id: store_dict}

    # Cadeia de desbloqueio progressivo: ao completar a chave, desbloqueia o valor
    _UNLOCK_CHAIN: dict = {
        "unit_intro": "unit_01",
        "unit_01": "unit_02",
        "unit_02": "unit_03",
    }

    @staticmethod
    def _get_session_id(page) -> str:
        """Obtém ou gera um UUID único para a sessão desta page."""
        if page is None:
            return "__default__"
        if not hasattr(page, '_sejong_session_id'):
            import uuid
            page._sejong_session_id = uuid.uuid4().hex[:12]
        return page._sejong_session_id

    @classmethod
    def _get_storage_path(cls, session_id: str) -> str:
        if cls._file_path_override:
            return cls._file_path_override
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "data", "sessions", f"{session_id}.json")

    @classmethod
    def _load_from_disk(cls, session_id: str) -> dict:
        path = cls._get_storage_path(session_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                print(f"[ProgressService] Warning: Error reading session {session_id}: {e}")
        return {}

    @classmethod
    def _save_to_disk(cls, session_id: str, data: dict) -> None:
        path = cls._get_storage_path(session_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = f"{path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, path)
        except Exception as e:
            print(f"[ProgressService] Error writing session {session_id}: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def __init__(self, page=None):
        self.page = page
        self._session_id = self._get_session_id(page)
        # Inicializar store desta sessão a partir do disco, se ainda não carregada
        if self._session_id not in ProgressService._sessions:
            ProgressService._sessions[self._session_id] = self._load_from_disk(self._session_id)

    @property
    def _store(self) -> dict:
        """Retorna o store isolado desta sessão."""
        return ProgressService._sessions.setdefault(self._session_id, {})

    def get_progress(self, unit_id: str) -> float:
        val = self._store.get(f"progress_{unit_id}", 0.0)
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def save_progress(self, unit_id: str, progress: float) -> None:
        val = float(progress)
        self._store[f"progress_{unit_id}"] = val

        # Desbloqueio progressivo via cadeia data-driven
        if val >= 1.0 and unit_id in ProgressService._UNLOCK_CHAIN:
            next_unit = ProgressService._UNLOCK_CHAIN[unit_id]
            self._store[f"unlocked_{next_unit}"] = True

        # Gravação persistente atômica em disco
        ProgressService._save_to_disk(self._session_id, self._store)

    def is_unlocked(self, unit_id: str) -> bool:
        if unit_id in ["unit_intro", "unit_01"]:
            return True
        return bool(self._store.get(f"unlocked_{unit_id}", False))

    def reset_progress(self) -> None:
        """Reseta o progresso da sessão atual."""
        self._store.clear()
        ProgressService._save_to_disk(self._session_id, self._store)

    def get_all_progress(self) -> dict:
        """Retorna uma cópia dos dados de progresso desta sessão."""
        return dict(self._store)


class FullscreenService:
    """Serviço para alternância de Tela Cheia (Fullscreen) e responsividade Mobile/PWA."""

    @staticmethod
    def toggle_fullscreen(page: ft.Page):
        new_state = False
        try:
            # 1. Toggle via propriedade oficial Flet
            if hasattr(page, "window"):
                current_state = bool(getattr(page.window, "full_screen", False))
                new_state = not current_state
                page.window.full_screen = new_state
                page.update()
        except Exception as e:
            print(f"Error toggling page.window.full_screen: {e}")

        # 2. Tentar via JS launch_url para navegadores Web
        js_code = (
            "if(!document.fullscreenElement && !document.webkitFullscreenElement){"
            "var d=document.documentElement;var r=d.requestFullscreen||d.webkitRequestFullscreen;"
            "if(r){r.call(d);}"
            "}else{"
            "var x=document.exitFullscreen||document.webkitExitFullscreen;"
            "if(x){x.call(document);}"
            "}"
        )

        async def _exec_js():
            # BUGFIX (11/08): page.launch_url() NÃO executa JS na página -- ele delega
            # pro plugin Flutter url_launcher, que trata a string como uma URL/link
            # externo. Em contexto web isso pelo menos tenta rodar como "javascript:"
            # URI; em janela desktop nativa (AppView.FLET_APP, o padrão do ft.app()
            # quando não se passa view=) não existe documento HTML nenhum, e o
            # Windows não sabe abrir um link "javascript:...". Isso derruba a conexão
            # do cliente Flutter, que reconecta automaticamente, recriando a sessão
            # e disparando este mesmo código de novo -- loop infinito de
            # "RuntimeError: Session closed" / "attempt to fetch destroyed session".
            # Guard com page.web (mesmo padrão usado internamente pelo próprio Flet
            # para o fluxo de OAuth) resolve na raiz.
            if not getattr(page, "web", False):
                return
            try:
                if hasattr(page, 'launch_url'):
                    await page.launch_url(f"javascript:{js_code}")
            except Exception:
                pass

        try:
            if hasattr(page, 'run_task'):
                page.run_task(_exec_js)
        except Exception:
            pass

        # 3. Notificação visual de confirmação ao usuário
        try:
            msg = "📱 Modo Tela Cheia Ativado! (Dica: no celular, você também pode 'Adicionar à Tela de Início' para abrir como App Nativo)" if new_state else "📱 Modo Tela Cheia Desativado"
            snack = ft.SnackBar(
                content=ft.Text(msg, size=12, weight=ft.FontWeight.BOLD),
                duration=2500,
                open=True
            )
            page.overlay.append(snack)
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
            # BUGFIX (11/08): mesma causa raiz do _exec_js em toggle_fullscreen (ver
            # comentário lá). Esta função em especial roda incondicionalmente em TODA
            # sessão (chamada direto em main.py), então era a origem do loop de
            # reconexão infinita reportado ao rodar `python main.py` no Windows sem
            # view=WEB_BROWSER (ft.app() abre janela desktop nativa por padrão).
            # Meta tags de viewport/PWA também só fazem sentido em navegador --
            # não existe <head> HTML numa janela desktop nativa.
            if not getattr(page, "web", False):
                return
            try:
                if hasattr(page, 'launch_url'):
                    await page.launch_url(f"javascript:{js_meta}")
            except Exception:
                pass

        try:
            if hasattr(page, 'run_task'):
                page.run_task(_exec_meta)
        except Exception:
            pass

    @staticmethod
    def create_fullscreen_button(page: ft.Page, colors: dict) -> ft.IconButton:
        """Cria um botão com ícone de entrar/sair da Tela Cheia para ser usado nas AppBars."""
        return ft.IconButton(
            icon=ft.Icons.FULLSCREEN_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: FullscreenService.toggle_fullscreen(page),
            tooltip="Alternar Modo Tela Cheia (Fullscreen)",
        )

