import json
import flet as ft
from typing import Optional


class NotificationService:
    """Serviço unificado para Notificações Nativas do Sistema (Web/PWA) e In-App Feedback."""

    @staticmethod
    def is_web(page: ft.Page) -> bool:
        """Verifica se a sessão está em contexto de navegador Web."""
        return bool(getattr(page, "web", False))

    @classmethod
    def request_permission(cls, page: ft.Page) -> None:
        """Solicita permissão ao sistema operacional/navegador para envio de notificações nativas.
        
        Adota guard estrito com page.web para prevenir crash em runtime de janela desktop nativa.
        """
        if not cls.is_web(page):
            return

        js_code = (
            "(function(){"
            "if(!('Notification' in window)) return;"
            "if(Notification.permission !== 'granted' && Notification.permission !== 'denied'){"
            "Notification.requestPermission().then(function(p){"
            "console.log('[Saebom] Notification permission result:', p);"
            "});"
            "}"
            "})();"
        )

        async def _exec_js():
            try:
                if hasattr(page, "launch_url"):
                    await page.launch_url(f"javascript:{js_code}")
            except Exception:
                pass

        try:
            if hasattr(page, "run_task"):
                page.run_task(_exec_js)
        except Exception:
            pass

    @classmethod
    def send_native_notification(
        cls,
        page: ft.Page,
        title: str,
        body: str,
        icon: str = "/branding/app_icon_192.png",
        tag: str = "saebom_announcement",
    ) -> None:
        """Dispara uma notificação nativa do sistema operacional (Windows, Android, macOS, iOS PWA).
        
        Utiliza a Web Notification API quando em ambiente navegador.
        Em todos os ambientes, oferece fallback visual garantido via SnackBar in-app.
        """
        # 1. Disparo nativo via JavaScript se em ambiente Web/PWA
        if cls.is_web(page):
            t_json = json.dumps(title)
            b_json = json.dumps(body)
            i_json = json.dumps(icon)
            tag_json = json.dumps(tag)

            js_code = (
                "(function(){"
                "if(!('Notification' in window)) return;"
                "if(Notification.permission === 'granted'){"
                f"var n = new Notification({t_json}, {{"
                f"body: {b_json},"
                f"icon: {i_json},"
                f"badge: {i_json},"
                f"tag: {tag_json}"
                "});"
                "n.onclick = function(){"
                "window.focus();"
                "this.close();"
                "};"
                "}"
                "})();"
            )

            async def _exec_js():
                try:
                    if hasattr(page, "launch_url"):
                        await page.launch_url(f"javascript:{js_code}")
                except Exception:
                    pass

            try:
                if hasattr(page, "run_task"):
                    page.run_task(_exec_js)
            except Exception:
                pass

        # 2. Exibição in-app simultânea para garantia visual
        cls.show_in_app_banner(page, title, body)

    @classmethod
    def show_in_app_banner(
        cls,
        page: ft.Page,
        title: str,
        message: str,
    ) -> None:
        """Exibe um aviso in-app estético no padrão Brand Book v3.1."""
        try:
            snack = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CAMPAIGN_ROUNDED, color="#FFAB22", size=22),
                        ft.Column(
                            controls=[
                                ft.Text(title, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.WHITE),
                                ft.Text(message, size=11, color="#E2E8F0", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                            spacing=1,
                            expand=True,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#121826",
                duration=4500,
                open=True,
            )
            if hasattr(page, "overlay"):
                page.overlay.append(snack)
            if hasattr(page, "update"):
                page.update()
        except Exception:
            pass
