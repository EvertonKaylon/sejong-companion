import flet as ft
import uuid
from ..components import centered_content
from ..theme import get_theme_colors, Styles, Colors, Responsive
from ..services import ProgressService

def onboarding_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK if hasattr(page, "theme_mode") else True
    colors = get_theme_colors(is_dark)
    w = page.width or 400

    # Estado local
    show_restore = [False]
    error_text = ft.Text("", size=12, color=colors["incorrect"], weight=ft.FontWeight.W_500, visible=False)

    # Campos de entrada
    name_input = ft.TextField(
        label="Nome e Sobrenome",
        hint_text="Ex: Marina Silva",
        prefix_icon=ft.Icons.PERSON_ROUNDED,
        bgcolor=colors["surface"],
        color=colors["text"],
        border_color=colors["border"],
        focused_border_color=colors["primary"],
        border_radius=Styles.BORDER_RADIUS_SM,
        text_size=14,
        autofocus=True,
    )

    code_input = ft.TextField(
        label="Identificador do Aluno (Student ID)",
        hint_text="Ex: student_a1b2c3d4e5f6 ou Nome",
        prefix_icon=ft.Icons.BADGE_ROUNDED,
        bgcolor=colors["surface"],
        color=colors["text"],
        border_color=colors["border"],
        focused_border_color=colors["secondary"],
        border_radius=Styles.BORDER_RADIUS_SM,
        text_size=13,
        visible=False,
    )

    recovery_input = ft.TextField(
        label="Chave Secreta de Recuperação",
        hint_text="Ex: 9K7X-2PQM-7V4N",
        prefix_icon=ft.Icons.KEY_ROUNDED,
        password=True,
        can_reveal_password=True,
        bgcolor=colors["surface"],
        color=colors["text"],
        border_color=colors["border"],
        focused_border_color=colors["secondary"],
        border_radius=Styles.BORDER_RADIUS_SM,
        text_size=13,
        visible=False,
    )

    async def save_and_proceed(student_id: str, student_name: str):
        page._sejong_student_id = student_id
        page._sejong_student_name = student_name
        
        # Persistir no servidor via ProgressService e garantir credencial de recuperação
        ps = ProgressService(page)
        ps.set_student_name(student_name)
        ps.get_or_create_recovery_code()

        # Persistir no SharedPreferences (localStorage do navegador)
        try:
            sp = ft.SharedPreferences()
            if hasattr(page, "services") and sp not in page.services:
                page.services.append(sp)
            await sp.set("sejong_student_id", student_id)
            await sp.set("sejong_student_name", student_name)
        except Exception as e:
            print(f"[Onboarding] Erro ao gravar SharedPreferences: {e}")

        # Redirecionar para a Home
        if hasattr(page, "router"):
            page.router.navigate_to("/home")
        else:
            page.go("/home")

    def handle_submit(e):
        name = (name_input.value or "").strip()
        if not name or len(name) < 2:
            error_text.value = "Por favor, digite seu nome e sobrenome para continuar."
            error_text.visible = True
            page.update()
            return

        error_text.visible = False
        new_id = getattr(page, "_sejong_student_id", None) or f"student_{uuid.uuid4().hex[:12]}"
        
        async def _run():
            await save_and_proceed(new_id, name)

        page.run_task(_run)

    def handle_restore_submit(e):
        ident = (code_input.value or "").strip()
        rec_key = (recovery_input.value or "").strip()

        if not ident:
            error_text.value = "Por favor, informe seu Student ID ou Nome cadastrado."
            error_text.visible = True
            page.update()
            return

        if not rec_key:
            error_text.value = "Por favor, informe a Chave Secreta de Recuperação do seu perfil."
            error_text.visible = True
            page.update()
            return

        success, s_id, s_name, msg = ProgressService.verify_and_restore_student(ident, rec_key)
        if not success:
            error_text.value = msg
            error_text.visible = True
            page.update()
            return

        error_text.visible = False
        async def _run():
            await save_and_proceed(s_id, s_name)

        page.run_task(_run)

    def toggle_restore_mode(e):
        show_restore[0] = not show_restore[0]
        code_input.visible = show_restore[0]
        recovery_input.visible = show_restore[0]
        restore_btn.visible = show_restore[0]
        name_input.visible = not show_restore[0]
        start_btn.visible = not show_restore[0]
        toggle_link.content.value = "← Voltar para criar novo perfil" if show_restore[0] else "Já tem uma chave de recuperação? Restaurar perfil"
        error_text.visible = False
        page.update()

    start_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Começar Meus Estudos · 시작하기", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=16, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=colors["primary"],
        border_radius=Styles.BORDER_RADIUS_SM,
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
        alignment=ft.Alignment.CENTER,
        on_click=handle_submit,
        shadow=Styles.CARD_SHADOW,
    )

    restore_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Restaurar Meu Progresso · 복구", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Icon(ft.Icons.DOWNLOAD_DONE_ROUNDED, size=16, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=colors["secondary"],
        border_radius=Styles.BORDER_RADIUS_SM,
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
        alignment=ft.Alignment.CENTER,
        on_click=handle_restore_submit,
        visible=False,
    )

    toggle_link = ft.TextButton(
        content=ft.Text("Já tem um código de aluno? Restaurar progresso", size=12),
        on_click=toggle_restore_mode,
        style=ft.ButtonStyle(color=colors["secondary"]),
    )

    card_content = ft.Container(
        content=ft.Column(
            controls=[
                # Brasão e Título Institucional Oficial Saebom Companion
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Image(
                                    src="branding/app_icon_192.png",
                                    width=54,
                                    height=54,
                                    border_radius=12,
                                    fit=ft.BoxFit.CONTAIN,
                                ),
                                alignment=ft.Alignment.CENTER,
                                margin=ft.Margin.only(bottom=6),
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text("새봄", size=26, font_family="Pretendard", weight=ft.FontWeight.W_900, color=colors["text"]),
                                    ft.Container(
                                        content=ft.Text("COMPANION", size=10, weight=ft.FontWeight.BOLD, color=colors["accent"]),
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=f"{colors['primary']}22",
                                        border=ft.Border.all(1, f"{colors['primary']}44"),
                                        border_radius=4,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            ft.Text("SAEBOM COMPANION", size=10, font_family="Pretendard", weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                            ft.Container(height=4),
                            ft.Text("Companion Institucional de Aprendizagem de Coreano", size=11, color=colors["text_sec"], weight=ft.FontWeight.W_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.symmetric(vertical=10),
                ),
                ft.Divider(color=colors["border"], height=1),
                ft.Container(height=10),
                ft.Text(
                    "Identificação do Aluno",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=colors["text"],
                ),
                ft.Text(
                    "Informe seu nome e sobrenome para que seus professores acompanhem sua frequência e evolução nos estudos:",
                    size=12,
                    color=colors["text_sec"],
                    style=ft.TextStyle(height=1.4),
                ),
                ft.Container(height=14),
                name_input,
                code_input,
                recovery_input,
                error_text,
                ft.Container(height=14),
                start_btn,
                restore_btn,
                ft.Container(height=4),
                ft.Row([toggle_link], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=4,
        ),
        bgcolor=colors["card_bg"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
        padding=20,
        shadow=Styles.CARD_SHADOW,
        margin=ft.Margin.symmetric(vertical=16),
    )

    return ft.View(
        route="/onboarding",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            centered_content(page, card_content, alignment=ft.Alignment.CENTER)
        ],
        bgcolor=colors["bg"],
        padding=0,
    )
