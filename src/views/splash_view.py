import flet as ft
import asyncio
from ..components import centered_content
from ..theme import get_theme_colors, Styles
from ..theme import Responsive

def splash_view(page: ft.Page) -> ft.View:
    # A tela de abertura (splash) abre no Modo Escuro (Midnight Blue) por padrão
    is_dark = True
    colors = get_theme_colors(is_dark)
    w = page.width or 400

    from ..theme import Colors

    # Logo central (estilo brasão retrô-industrial Seollip-che)
    logo_badge = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "세종학당",
                    size=32,
                    font_family="Seollip-che",
                    weight=ft.FontWeight.W_900,
                    color=Colors.ACCENT if is_dark else Colors.PRIMARY_DARK,
                    style=ft.TextStyle(letter_spacing=Responsive.value(w, compact=1, medium=3)),
                ),
                ft.Text(
                    "COMPANION",
                    size=13,
                    font_family="Pretendard",
                    weight=ft.FontWeight.BOLD,
                    color=Colors.SECONDARY_LIGHT if is_dark else Colors.PRIMARY,
                    style=ft.TextStyle(letter_spacing=Responsive.value(w, compact=2, medium=6)),
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=Responsive.value(w, compact=12, medium=24), vertical=16),
        bgcolor="#14004C97" if not is_dark else "#1E7C4DFF",
        border=ft.Border.all(3, Colors.PRIMARY if not is_dark else Colors.SECONDARY),
        border_radius=Styles.BORDER_RADIUS_MD,
        shadow=Styles.CARD_SHADOW,
    )

    # Indicador de status de carregamento e áudio
    status_label = ft.Text(
        "⚡ Sincronizando pronúncias em áudio HD...",
        size=12,
        font_family="Pretendard",
        color=colors["text_sec"],
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    progress_bar = ft.ProgressBar(
        width=180,
        color=Colors.ACCENT,
        bgcolor="#1E7C4DFF",
        border_radius=Styles.BORDER_RADIUS_SM,
        visible=False,
    )

    logo_layout = ft.Column(
        controls=[
            logo_badge,
            ft.Container(height=12),
            ft.Text(
                "세종학당 컴패니언",
                size=26,
                font_family="Seollip-che",
                weight=ft.FontWeight.W_900,
                color=Colors.PRIMARY if not is_dark else Colors.ACCENT,
                style=ft.TextStyle(letter_spacing=2),
            ),
            ft.Text(
                "Centro Cultural Coreano no Brasil • 세종학당재단",
                size=12,
                font_family="Pretendard",
                color=colors["text_sec"],
                weight=ft.FontWeight.W_500,
            ),
            ft.Container(height=20),
            ft.ProgressRing(color=colors["secondary"], width=28, height=28),
            ft.Container(height=4),
            status_label,
            progress_bar,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )

    # Pré-carregar lote prioritário de áudios no splash e continuar o restante em background
    async def prewarm_and_redirect():
        from ..services import DataService
        try:
            audio_service = getattr(page, "audio_service", None)
            if audio_service:
                priority_texts = DataService.get_priority_audio_texts()
                stats = audio_service.get_cache_stats(priority_texts)

                # Se faltarem áudios prioritários, pré-carregar com feedback visual
                if stats["missing"] > 0:
                    progress_bar.visible = True
                    status_label.value = f"⚡ Baixando áudios prioritários... (0/{len(priority_texts)})"
                    try:
                        page.update()
                    except Exception:
                        pass

                    async def _on_progress(current, total, text):
                        progress_bar.value = current / total if total > 0 else 1.0
                        status_label.value = f"⚡ Baixando áudios prioritários... ({current}/{total})"
                        try:
                            page.update()
                        except Exception:
                            pass

                    # Aquecimento com timeout de segurança (máx 3.5s no splash)
                    try:
                        await asyncio.wait_for(
                            audio_service.prewarm_batch_async(priority_texts, on_progress=_on_progress, max_concurrent=3),
                            timeout=3.5,
                        )
                    except asyncio.TimeoutError:
                        pass

            # ─── VERIFICAÇÃO DE IDENTIDADE PERSISTENTE ───
            next_route = "/onboarding"
            try:
                sp = ft.SharedPreferences()
                if hasattr(page, "services") and sp not in page.services:
                    page.services.append(sp)
                saved_id = await sp.get("sejong_student_id")
                saved_name = await sp.get("sejong_student_name")
                if saved_id and str(saved_id).strip():
                    clean_id = str(saved_id).strip()
                    page._sejong_student_id = clean_id
                    if saved_name and str(saved_name).strip() and str(saved_name).strip() != "Aluno Anônimo":
                        page._sejong_student_name = str(saved_name).strip()
                        from ..services import ProgressService
                        ps = ProgressService(page)
                        ps.set_student_name(page._sejong_student_name)
                        next_route = "/home"
            except Exception as e:
                print(f"[Splash] Erro ao consultar SharedPreferences: {e}")

            # Tempo mínimo para visualização suave da marca (~1.2s)
            await asyncio.sleep(1.2)

            # Navegar para a rota correta (Home ou Onboarding)
            page.router.navigate_to(next_route)

            # Em segundo plano: continuar baixando silenciosamente o restante do currículo
            if audio_service:
                async def _background_full_prewarm():
                    try:
                        all_texts = DataService.get_all_audio_texts()
                        await audio_service.prewarm_batch_async(all_texts, max_concurrent=2)
                    except Exception:
                        pass

                page.run_task(_background_full_prewarm)

        except Exception:
            # Fallback seguro para navegação
            try:
                page.router.navigate_to("/home")
            except Exception:
                pass

    page.run_task(prewarm_and_redirect)

    return ft.View(
        route="/splash",
        controls=[
            centered_content(page, logo_layout, alignment=ft.Alignment.CENTER)
        ],
        bgcolor=colors["bg"],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )
