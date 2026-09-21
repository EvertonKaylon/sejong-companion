import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import flet as ft


class AnnouncementService:
    """Serviço de gerenciamento do Mural de Avisos da Professora e Notificações Pedagógicas."""

    _DATA_FILE_NAME = "announcements.json"

    @classmethod
    def _get_data_path(cls) -> str:
        """Retorna o caminho seguro para o arquivo de avisos dentro de data/."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, cls._DATA_FILE_NAME)

    @classmethod
    def get_announcements(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        """Lê todos os avisos registrados no servidor."""
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
        """Persiste a lista de avisos de forma atômica."""
        path = cls._get_data_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(announcements, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def post_announcement(
        cls,
        title: str,
        content: str,
        author: str = "Professora",
        page: Optional[ft.Page] = None,
        badge_color: str = "#FFAB22",
    ) -> Optional[Dict[str, Any]]:
        """Publica um novo recado da professora e dispara notificação em tempo real via PubSub."""
        clean_title = (title or "").strip()
        clean_content = (content or "").strip()
        if not clean_title or not clean_content:
            return None

        announcement = {
            "id": f"ann_{uuid.uuid4().hex[:8]}",
            "title": clean_title,
            "content": clean_content,
            "author": (author or "Professora").strip(),
            "created_at": datetime.now().isoformat(),
            "active": True,
            "badge_color": badge_color,
        }

        current = cls.get_announcements(active_only=False)
        current.insert(0, announcement)
        if cls._save_announcements(current):
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
