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

    # Logo central oficial Saebom Companion (Brand Book v3.1)
    logo_badge = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(
                    src="/branding/app_icon_512.png",
                    width=Responsive.value(w, compact=84, medium=96),
                    height=Responsive.value(w, compact=84, medium=96),
                    border_radius=Styles.BORDER_RADIUS_LG,
                    fit=ft.BoxFit.CONTAIN,
                ),
                ft.Container(height=6),
                ft.Text(
                    "새봄",
                    size=Responsive.value(w, compact=32, medium=38),
                    font_family="Pretendard-Bold",
                    weight=ft.FontWeight.W_900,
                    color=colors["text"],
                    style=ft.TextStyle(letter_spacing=Responsive.value(w, compact=2, medium=4)),
                ),
                ft.Text(
                    "C O M P A N I O N",
                    size=12,
                    font_family="Pretendard-Bold",
                    weight=ft.FontWeight.BOLD,
                    color=colors["accent"],
                    style=ft.TextStyle(letter_spacing=Responsive.value(w, compact=4, medium=8)),
                ),
                ft.Text(
                    "SAEBOM COMPANION",
                    size=9,
                    font_family="Pretendard",
                    weight=ft.FontWeight.W_600,
                    color=colors["text_sec"],
                    style=ft.TextStyle(letter_spacing=Responsive.value(w, compact=2, medium=4)),
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=Responsive.value(w, compact=16, medium=28), vertical=18),
        bgcolor=ft.Colors.with_opacity(0.12, colors["primary"]),
        border=ft.Border.all(1.5, ft.Colors.with_opacity(0.25, colors["primary"])),
        border_radius=Styles.BORDER_RADIUS_LG,
        shadow=Styles.CARD_SHADOW,
    )

    # Indicador de status de carregamento e áudio
    status_label = ft.Text(
        "⚡ Sincronizando pronúncias em áudio HD...",
        size=12,
        color=colors["text_sec"],
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    progress_bar = ft.ProgressBar(
        width=180,
        color=colors["accent"],
        bgcolor=ft.Colors.with_opacity(0.15, colors["primary"]),
        border_radius=Styles.BORDER_RADIUS_SM,
        visible=False,
    )

    logo_layout = ft.Column(
        controls=[
            logo_badge,
            ft.Container(height=14),
            ft.Text(
                "“Uma nova primavera para a aprendizagem.”",
                size=12,
                color=colors["text_sec"],
                weight=ft.FontWeight.W_500,
                italic=True,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "Companion Institucional de Aprendizagem de Coreano",
                size=11,
                color=colors["text_sec"],
                weight=ft.FontWeight.W_400,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=20),
            ft.ProgressRing(color=colors["primary"], width=28, height=28),
            ft.Container(height=6),
            status_label,
            progress_bar,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=3,
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
                from ..services import StudentIdentity, ProgressService
                existing_id = StudentIdentity.get_student_id(page)
                ps = ProgressService(page)
                saved_name = ps.get_student_name()

                if existing_id and not existing_id.startswith("student_") and saved_name and saved_name != "Aluno Anônimo":
                    page._sejong_student_id = existing_id
                    page._sejong_student_name = saved_name
                    next_route = "/home"
                else:
                    # Tentar SharedPreferences de forma estritamente defensiva com timeout de 0.8s
                    try:
                        sp = ft.SharedPreferences()
                        if hasattr(page, "services") and sp not in page.services:
                            page.services.append(sp)

                        async def _safe_get(k: str):
                            try:
                                return await asyncio.wait_for(sp.get(k), timeout=0.8)
                            except Exception:
                                return None

                        saved_id = await _safe_get("saebom_student_id") or await _safe_get("sejong_student_id")
                        saved_name = await _safe_get("saebom_student_name") or await _safe_get("sejong_student_name")

                        if saved_id and str(saved_id).strip():
                            clean_id = str(saved_id).strip()
                            page._sejong_student_id = clean_id
                            if saved_name and str(saved_name).strip() and str(saved_name).strip() != "Aluno Anônimo":
                                page._sejong_student_name = str(saved_name).strip()
                                ps.set_student_name(page._sejong_student_name)
                                next_route = "/home"
                    except Exception as e:
                        print(f"[Splash] SharedPreferences inacessível ou ignorado: {e}")
            except Exception as e:
                print(f"[Splash] Erro na checagem de identidade: {e}")

            # Não redirecionar se a rota solicitou modo estático (ex: /splash?no_redirect=1 para auditorias visuais)
            if "no_redirect" in (getattr(page, "route", "") or ""):
                return

            # Tempo mínimo para visualização suave da marca (~1.2s)
            await asyncio.sleep(1.2)

            # Navegar para a rota correta (Home ou Onboarding)
            try:
                page.router.navigate_to(next_route)
            except Exception as e:
                print(f"[Splash] Erro ao navegar para {next_route}: {e}")
                try:
                    page.router.navigate_to("/home")
                except Exception:
                    pass

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
