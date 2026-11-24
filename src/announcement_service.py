import errno
import os
import json
import threading
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import flet as ft


class AnnouncementService:
    """Serviço de gerenciamento do Mural de Avisos da Professora e Notificações Pedagógicas."""

    _DATA_FILE_NAME = "announcements.json"
    _LOCK = threading.RLock()

    @classmethod
    def _get_data_path(cls) -> str:
        """Retorna o caminho seguro para o arquivo de avisos dentro de data/ ou SAEBOM_ANNOUNCEMENTS_PATH."""
        env_path = os.environ.get("SAEBOM_ANNOUNCEMENTS_PATH", "").strip()
        if env_path:
            parent_dir = os.path.dirname(os.path.abspath(env_path))
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            return env_path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, cls._DATA_FILE_NAME)

    @classmethod
    def get_announcements(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        """Lê todos os avisos registrados no servidor."""
        with cls._LOCK:
            path = cls._get_data_path()
            if not os.path.exists(path):
                return []
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        return []
                    if active_only:
                        return [item for item in data if item.get("active", True)]
                    return data
            except Exception:
                return []

    @classmethod
    def _save_announcements(cls, announcements: List[Dict[str, Any]]) -> bool:
        """Persiste a lista de avisos de forma thread-safe e atômica."""
        with cls._LOCK:
            path = cls._get_data_path()
            parent_dir = os.path.dirname(os.path.abspath(path))
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            tmp_path = f"{path}.tmp.{uuid.uuid4().hex[:8]}"
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(announcements, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, path)
                return True
            except OSError as exc:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                if exc.errno == errno.EBUSY:
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(announcements, f, ensure_ascii=False, indent=2)
                        return True
                    except Exception:
                        return False
                return False
            except Exception:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                return False

    MAX_TITLE_LENGTH: int = 120
    MAX_CONTENT_LENGTH: int = 1000
    MAX_AUTHOR_LENGTH: int = 50

    @classmethod
    def post_announcement(
        cls,
        title: str,
        content: str,
        author: str = "Professora",
        page: Optional[ft.Page] = None,
        badge_color: str = "#FFAB22",
    ) -> Optional[Dict[str, Any]]:
        """Publica um novo recado da professora e dispara notificação em tempo real via PubSub.
        
        Aplica limites estritos de comprimento e sanitização contra payload inflation (OWASP A04 / MITRE T1499).
        """
        # Sanitizar e truncar entradas para prevenir DoS por payload excessivo
        clean_title = (title or "").strip().replace("\x00", "")[:cls.MAX_TITLE_LENGTH]
        clean_content = (content or "").strip().replace("\x00", "")[:cls.MAX_CONTENT_LENGTH]
        clean_author = (author or "Professora").strip().replace("\x00", "")[:cls.MAX_AUTHOR_LENGTH] or "Professora"

        if not clean_title or not clean_content:
            return None

        announcement = {
            "id": f"ann_{uuid.uuid4().hex[:8]}",
            "title": clean_title,
            "content": clean_content,
            "author": clean_author,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "badge_color": badge_color,
        }

        with cls._LOCK:
            current = cls.get_announcements(active_only=False)
            current.insert(0, announcement)
            saved = cls._save_announcements(current)

        if saved:
            # Se a página fornecer pubsub, notificar todos os clientes conectados em tempo real
            if page is not None and hasattr(page, "pubsub") and page.pubsub:
                try:
                    page.pubsub.send_all({
                        "type": "new_announcement",
                        "data": announcement,
                    })
                except Exception:
                    pass
            return announcement
        return None

    @classmethod
    def delete_announcement(cls, announcement_id: str) -> bool:
        """Marca um anúncio como inativo/removido."""
        if not announcement_id:
            return False
        with cls._LOCK:
            current = cls.get_announcements(active_only=False)
            updated = False
            for item in current:
                if item.get("id") == announcement_id:
                    item["active"] = False
                    updated = True
                    break
            if updated:
                return cls._save_announcements(current)
        return False

    @classmethod
    def get_unread_count(cls, page: Optional[ft.Page]) -> int:
        """Retorna o número de avisos ativos que o aluno ainda não visualizou."""
        active = cls.get_announcements(active_only=True)
        if not active:
            return 0
        if not page or not hasattr(page, "client_storage") or not page.client_storage:
            return len(active)
        try:
            last_read_id = page.client_storage.get("last_read_announcement_id")
            if not last_read_id:
                return len(active)
            # Contar quantos avisos estão antes do último lido
            count = 0
            for item in active:
                if item.get("id") == last_read_id:
                    break
                count += 1
            return count
        except Exception:
            return len(active)

    @classmethod
    def mark_all_as_read(cls, page: Optional[ft.Page]) -> None:
        """Marca todos os avisos atuais como visualizados para a sessão do aluno."""
        if not page or not hasattr(page, "client_storage") or not page.client_storage:
            return
        active = cls.get_announcements(active_only=True)
        if not active:
            return
        try:
            latest_id = active[0].get("id")
            if latest_id:
                page.client_storage.set("last_read_announcement_id", latest_id)
        except Exception:
            pass
