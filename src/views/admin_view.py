import os
from datetime import datetime
import flet as ft
from ..components import centered_content
from ..theme import get_theme_colors, Styles, Responsive
from ..services import AdminService, DataService

# Dicionário de Internacionalização para o Portal do Professor (Português / 한국어)
ADMIN_I18N = {
    "pt": {
        "title": "Portal do Professor",
        "subtitle": "Central de Análise e Evidência Pedagógica",
        "students_kpi": "Alunos",
        "students_sub": "Perfis registrados",
        "progress_kpi": "Progresso Médio",
        "progress_sub": "Currículo 1A + 1B",
        "retention_kpi": "Retenção SRS",
        "cards_suffix": "cartões",
        "quizzes_kpi": "Quizzes",
        "events_suffix": "eventos",
        "tab_diag": "Diagnóstico da Turma",
        "tab_roster": "Roster de Alunos",
        "hardest_title": "⚠️ Questões com Maior Taxa de Erro",
        "hardest_empty": "Nenhum dado de erro em exercícios registrado ainda.",
        "question_prefix": "Questão",
        "attempts": "Tentativas",
        "errors": "Erros",
        "avg_time": "Tempo médio",
        "dropoff_title": "📉 Funil de Conclusão e Abandono por Unidade",
        "dropoff_empty": "Nenhum evento de abertura/abandono registrado ainda.",
        "unit": "Unidade",
        "dropoff": "Abandono",
        "completed": "concluídos",
        "vocab_title": "🔄 Vocabulário Crítico no Active Recall (Again)",
        "vocab_empty": "Nenhuma reincidência crítica de vocabulário registrada.",
        "reviews": "revisões",
        "search_hint": "Buscar aluno por nome ou Student ID...",
        "no_students": "Nenhum aluno encontrado.",
        "book_1a": "Livro 1A",
        "book_1b": "Livro 1B",
        "general_progress": "Progresso Geral",
        "srs_retention": "Retenção SRS",
        "items": "itens",
        "last_study": "Último",
        "refresh_snack": "🔄 Dados recarregados em tempo real!",
        "export_snack": "📄 Relatório exportado com sucesso",
        "logout_tooltip": "Sair do Modo Admin",
        "refresh_tooltip": "Atualizar Dados",
        "export_tooltip": "Exportar Relatório Markdown",
        "lang_toggle_btn": "🇰🇷 한국어로 보기",
        "lang_toggle_tooltip": "Alternar para Coreano / 한국어로 전환",
        # Login
        "login_title": "Portal Pedagógico",
        "login_sub": "Área Administrativa · 관리자",
        "login_desc": "Acesso restrito ao corpo docente do Sejong Hakdang e administradores para análise de evidência pedagógica.",
        "pin_label": "PIN de Acesso",
        "login_btn": "Entrar no Painel",
        "back_home": "Voltar para o Início",
        "pin_error": "PIN incorreto. Tente novamente.",
    },
    "ko": {
        "title": "교사용 포털",
        "subtitle": "학습 데이터 및 교육 성과 분석 센터",
        "students_kpi": "학습자 수",
        "students_sub": "등록된 학생 프로필",
        "progress_kpi": "평균 진도율",
        "progress_sub": "세종한국어 1A + 1B",
        "retention_kpi": "SRS 기억 유지율",
        "cards_suffix": "개 카드",
        "quizzes_kpi": "완료된 퀴즈",
        "events_suffix": "개 학습 이벤트",
        "tab_diag": "학급 진단 분석",
        "tab_roster": "학생 명단",
        "hardest_title": "⚠️ 오답률 상위 문항 (보강 지도 권장)",
        "hardest_empty": "아직 기록된 연습문제 오류 데이터가 없습니다.",
        "question_prefix": "문항",
        "attempts": "시도",
        "errors": "오답",
        "avg_time": "평균 응답시간",
        "dropoff_title": "📉 단원별 이탈률 및 완강 현황",
        "dropoff_empty": "아직 기록된 단원 학습 데이터가 없습니다.",
        "unit": "단원",
        "dropoff": "이탈률",
        "completed": "완료",
        "vocab_title": "🔄 어휘 취약도 분석 (Again 재학습 빈도)",
        "vocab_empty": "심각한 어휘 재학습 오류가 기록되지 않았습니다.",
        "reviews": "회 복습",
        "search_hint": "학생 이름 또는 Student ID 검색...",
        "no_students": "해당하는 학생을 찾을 수 없습니다.",
        "book_1a": "1A 교재",
        "book_1b": "1B 교재",
        "general_progress": "전체 진도율",
        "srs_retention": "SRS 기억력",
        "items": "개 어휘",
        "last_study": "최근 학습",
        "refresh_snack": "🔄 실시간 데이터를 새로고침했습니다!",
        "export_snack": "📄 교육 분석 보고서가 내보내졌습니다",
        "logout_tooltip": "관리자 로그아웃",
        "refresh_tooltip": "데이터 새로고침",
        "export_tooltip": "마크다운 보고서 내보내기",
        "lang_toggle_btn": "🇧🇷 Ver em Português",
        "lang_toggle_tooltip": "Alternar para Português / 포르투갈어로 전환",
        # Login
        "login_title": "세종학당 교수 포털",
        "login_sub": "관리자 및 교수진 전용 · 관리자",
        "login_desc": "세종학당 교수진 및 관리자 전용 교육 성과 분석 포털입니다.",
        "pin_label": "접속 PIN 번호",
        "login_btn": "대시보드 로그인",
        "back_home": "홈 화면으로 돌아가기",
        "pin_error": "PIN 번호가 일치하지 않습니다. 다시 입력해주세요.",
    }
}

def admin_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    w = page.width or 400

    # Estado de autenticação e idioma da sessão
    if not hasattr(page, "_admin_authenticated"):
        page._admin_authenticated = False
    if not hasattr(page, "_admin_lang"):
        page._admin_lang = "pt"

    t = ADMIN_I18N[page._admin_lang]

    def toggle_lang(e=None):
        page._admin_lang = "ko" if page._admin_lang == "pt" else "pt"
        rebuild_view()

    def rebuild_view():
        page.views.clear()
        page.views.append(admin_view(page))
        page.update()

    # ─── 1. TELA DE LOGIN / AUTENTICAÇÃO POR PIN ───
    if not page._admin_authenticated:
        pin_input = ft.TextField(
            label=t["pin_label"],
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.KEY_ROUNDED,
            border_color=colors["border"],
            focused_border_color=colors["primary"],
            cursor_color=colors["primary"],
            text_size=15,
            autofocus=True,
        )
        error_banner = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=colors["incorrect"], size=16),
                    ft.Text(t["pin_error"], size=12, color=colors["incorrect"], weight=ft.FontWeight.W_500),
                ],
                spacing=6,
            ),
            visible=False,
            margin=ft.Margin.only(top=6, bottom=4),
        )

        def handle_login(e):
            entered_pin = pin_input.value or ""
            if AdminService.authenticate(entered_pin):
                page._admin_authenticated = True
                rebuild_view()
            else:
                error_banner.visible = True
                pin_input.border_color = colors["incorrect"]
                page.update()

        pin_input.on_submit = handle_login

        login_card = ft.Container(
            content=ft.Column(
                controls=[
                    # Seletor de Idioma no topo do card
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                content=ft.Text(t["lang_toggle_btn"], size=11, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                                on_click=toggle_lang,
                                tooltip=t["lang_toggle_tooltip"],
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED, color=colors["primary"], size=44),
                        width=72,
                        height=72,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=f"{colors['primary']}18",
                        shape=ft.BoxShape.CIRCLE,
                    ),
                    ft.Container(height=8),
                    ft.Text(t["login_title"], size=20, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Text(t["login_sub"], size=13, weight=ft.FontWeight.W_600, color=colors["primary"]),
                    ft.Text(
                        t["login_desc"],
                        size=12,
                        color=colors["text_sec"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=14),
                    pin_input,
                    error_banner,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.LOGIN_ROUNDED, size=18),
                                ft.Text(t["login_btn"], weight=ft.FontWeight.BOLD, size=14),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        bgcolor=colors["primary"],
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                            padding=ft.Padding.symmetric(vertical=14, horizontal=20),
                        ),
                        on_click=handle_login,
                        width=320,
                    ),
                    ft.Container(height=6),
                    ft.TextButton(
                        content=ft.Text(t["back_home"], color=colors["text_sec"], size=12),
                        on_click=lambda e: page.router.navigate_to("/home"),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor=colors["surface"],
            border=ft.Border.all(1, colors["border"]),
            border_radius=Styles.BORDER_RADIUS_LG,
            padding=Responsive.value(w, compact=18, medium=28),
            shadow=Styles.CARD_SHADOW,
            width=420,
        )

        return ft.View(
            route="/admin",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                centered_content(
                    page,
                    ft.Container(
                        content=login_card,
                        alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.symmetric(vertical=30),
                    )
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            bgcolor=colors["bg"],
            padding=0,
        )

    # ─── 2. TELA AUTENTICADA: DASHBOARD PEDAGÓGICO COMPLETO ───
    kpis = AdminService.get_global_kpis()
    diagnostics = AdminService.get_pedagogical_diagnostics()
    all_students = AdminService.get_all_students_summary()

    def handle_logout(e):
        page._admin_authenticated = False
        rebuild_view()

    def handle_refresh(e):
        rebuild_view()
        snack = ft.SnackBar(
            content=ft.Text(t["refresh_snack"]),
            bgcolor=colors["secondary"],
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    def handle_export(e):
        report_md = AdminService.export_report_markdown()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        reports_dir = os.path.join(base_dir, "data", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filename = f"relatorio_pedagogico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_md)

        snack = ft.SnackBar(
            content=ft.Text(f"{t['export_snack']}: data/reports/{filename}"),
            bgcolor=colors["correct"],
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: page.router.navigate_to("/home"),
            tooltip=t["back_home"],
        ),
        title=ft.Text(t["title"], weight=ft.FontWeight.BOLD, size=16, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0,
        actions=[
            # Botão de Tradução Instantânea (PT / KO)
            ft.Container(
                content=ft.TextButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TRANSLATE_ROUNDED, size=14, color=colors["primary"]),
                            ft.Text(t["lang_toggle_btn"], size=11, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                        ],
                        spacing=4,
                    ),
                    on_click=toggle_lang,
                    tooltip=t["lang_toggle_tooltip"],
                ),
                padding=ft.Padding.only(right=4),
            ),
            ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                icon_color=colors["primary"],
                on_click=handle_refresh,
                tooltip=t["refresh_tooltip"],
            ),
            ft.IconButton(
                icon=ft.Icons.DOWNLOAD_ROUNDED,
                icon_color=colors["secondary"],
                on_click=handle_export,
                tooltip=t["export_tooltip"],
            ),
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                icon_color=colors["incorrect"],
                on_click=handle_logout,
                tooltip=t["logout_tooltip"],
            ),
            ft.Container(width=4),
        ],
    )

    # ─── KPI CARDS ───
    def make_kpi_card(title: str, value: str, subtitle: str, icon: str, color_hex: str):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(icon, size=18),
                                width=32,
                                height=32,
                                alignment=ft.Alignment.CENTER,
                                bgcolor=f"{color_hex}15",
                                border_radius=Styles.BORDER_RADIUS_SM,
                            ),
                            ft.Text(title, size=12, weight=ft.FontWeight.W_600, color=colors["text_sec"]),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Text(subtitle, size=10, color=colors["text_sec"]),
                ],
                spacing=2,
            ),
            bgcolor=colors["surface"],
            border=ft.Border.all(1, colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            padding=10,
            expand=True,
        )

    kpi_grid = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    make_kpi_card(t["students_kpi"], str(kpis["total_students"]), t["students_sub"], "👥", colors["primary"]),
                    make_kpi_card(t["progress_kpi"], f"{kpis['avg_progress_pct']:.1%}", t["progress_sub"], "📊", colors["secondary"]),
                ],
                spacing=8,
            ),
            ft.Row(
                controls=[
                    make_kpi_card(t["retention_kpi"], f"{kpis['avg_retention_pct']:.1%}", f"{kpis['total_memory_nodes']} {t['cards_suffix']}", "🧠", colors["vitality_high"]),
                    make_kpi_card(t["quizzes_kpi"], str(kpis["total_quizzes_completed"]), f"{kpis['total_telemetry_events']} {t['events_suffix']}", "📝", "#F88807"),
                ],
                spacing=8,
            ),
        ],
        spacing=8,
    )

    # ─── TAB 1: DIAGNÓSTICO MACROPEDAGÓGICO ───
    hardest_questions = diagnostics.get("hardest_questions", [])[:6]
    hardest_controls = []
    if hardest_questions:
        for q in hardest_questions:
            error_pct = q["error_rate"]
            badge_color = colors["incorrect"] if error_pct >= 0.5 else colors["warning"]
            hardest_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"{error_pct:.0%}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=badge_color,
                                border_radius=Styles.BORDER_RADIUS_SM,
                                padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(f"{t['question_prefix']}: {q['question_id']} ({q['unit_id']})", size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(f"{t['attempts']}: {q['total_attempts']} | {t['errors']}: {q['errors']} | {t['avg_time']}: {q['avg_response_time_ms']}ms", size=11, color=colors["text_sec"]),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    bgcolor=colors["surface"],
                    border=ft.Border.all(1, colors["border"]),
                    border_radius=Styles.BORDER_RADIUS_SM,
                    padding=10,
                    margin=ft.Margin.only(bottom=6),
                )
            )
    else:
        hardest_controls.append(
            ft.Container(
                content=ft.Text(t["hardest_empty"], size=12, color=colors["text_sec"]),
                padding=10,
            )
        )

    # Funil de Abandono
    drop_offs = diagnostics.get("drop_off_units", [])[:6]
    drop_off_controls = []
    if drop_offs:
        for u in drop_offs:
            rate = u["drop_off_rate"]
            drop_off_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(f"{t['unit']}: {u['unit_id']}", size=12, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(f"{t['dropoff']}: {rate:.1%} ({u['completed_count']}/{u['opened_count']} {t['completed']})", size=11, color=colors["text_sec"]),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(
                                value=1.0 - rate,
                                color=colors["primary"] if rate < 0.4 else colors["warning"],
                                bgcolor=colors["border"],
                                height=6,
                                border_radius=3,
                            ),
                        ],
                        spacing=4,
                    ),
                    bgcolor=colors["surface"],
                    border=ft.Border.all(1, colors["border"]),
                    border_radius=Styles.BORDER_RADIUS_SM,
                    padding=10,
                    margin=ft.Margin.only(bottom=6),
                )
            )
    else:
        drop_off_controls.append(
            ft.Container(
                content=ft.Text(t["dropoff_empty"], size=12, color=colors["text_sec"]),
                padding=10,
            )
        )

    # Vocabulário Crítico com Again
    critical_vocab = diagnostics.get("critical_vocab", [])[:6]
    vocab_controls = []
    if critical_vocab:
        for c in critical_vocab:
            vocab_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("Again", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=colors["incorrect"],
                                border_radius=Styles.BORDER_RADIUS_SM,
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(f"{c['item_id']} ({c['unit_id']})", size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(f"{t['errors']} (Again): {c['again_count']}x / {c['total_reviews']} {t['reviews']} ({c['again_rate']:.1%})", size=11, color=colors["text_sec"]),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    bgcolor=colors["surface"],
                    border=ft.Border.all(1, colors["border"]),
                    border_radius=Styles.BORDER_RADIUS_SM,
                    padding=10,
                    margin=ft.Margin.only(bottom=6),
                )
            )
    else:
        vocab_controls.append(
            ft.Container(
                content=ft.Text(t["vocab_empty"], size=12, color=colors["text_sec"]),
                padding=10,
            )
        )

    tab_diagnostics_content = ft.Column(
        controls=[
            ft.Container(height=6),
            ft.Text(t["hardest_title"], size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Column(controls=hardest_controls, spacing=0),
            ft.Container(height=12),
            ft.Text(t["dropoff_title"], size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Column(controls=drop_off_controls, spacing=0),
            ft.Container(height=12),
            ft.Text(t["vocab_title"], size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Column(controls=vocab_controls, spacing=0),
        ],
        spacing=2,
    )

    # ─── TAB 2: ROSTER DE ALUNOS (VISÃO INDIVIDUAL) ───
    students_list_column = ft.Column(spacing=8)

    def render_student_cards(query: str = ""):
        students_list_column.controls.clear()
        q_norm = query.strip().lower()

        filtered = [
            s for s in all_students
            if not q_norm or q_norm in s["student_id"].lower() or q_norm in s["student_name"].lower()
        ]

        if not filtered:
            students_list_column.controls.append(
                ft.Container(
                    content=ft.Text(t["no_students"], size=13, color=colors["text_sec"]),
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                )
            )
            return

        for s in filtered:
            s_name = s["student_name"]
            s_id = s["student_id"]
            prog_pct = s["overall_progress_pct"]
            ret_pct = s["avg_retention_pct"]
            streak = s["streak"]
            xp = s["total_xp"]
            c_1a = s["completed_1a_count"]
            c_1b = s["completed_1b_count"]
            last_date = s["last_study_date"]

            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(s_name[0].upper() if s_name else "A", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    bgcolor=colors["primary"],
                                    shape=ft.BoxShape.CIRCLE,
                                    width=36,
                                    height=36,
                                    alignment=ft.Alignment.CENTER,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(s_name, size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                        ft.Text(f"ID: {s_id}", size=11, color=colors["text_sec"]),
                                    ],
                                    spacing=1,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Text(f"{streak}🔥", size=12, weight=ft.FontWeight.BOLD, color=colors["warning"]),
                                            ft.Text(f"{xp} XP", size=12, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                                        ],
                                        spacing=6,
                                    ),
                                    bgcolor=colors["card_bg"],
                                    border=ft.Border.all(1, colors["border"]),
                                    border_radius=Styles.BORDER_RADIUS_SM,
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=4),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(f"{t['book_1a']}: {c_1a}/11", size=11, color=colors["text_sec"]),
                                        ft.ProgressBar(value=min(1.0, c_1a / 11.0), color=colors["primary"], bgcolor=colors["border"], height=4, border_radius=2),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"{t['book_1b']}: {c_1b}/12", size=11, color=colors["text_sec"]),
                                        ft.ProgressBar(value=min(1.0, c_1b / 12.0), color=colors["secondary"], bgcolor=colors["border"], height=4, border_radius=2),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                        ft.Container(height=2),
                        ft.Row(
                            controls=[
                                ft.Text(f"{t['general_progress']}: {prog_pct:.1%}", size=11, weight=ft.FontWeight.W_600, color=colors["text"]),
                                ft.Text(f"{t['srs_retention']}: {ret_pct:.1%} ({s['memory_nodes_count']} {t['items']})", size=11, weight=ft.FontWeight.W_600, color=colors["vitality_high"] if ret_pct >= 0.75 else colors["warning"]),
                                ft.Text(f"{t['last_study']}: {last_date}", size=11, color=colors["text_sec"]),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=6,
                ),
                bgcolor=colors["surface"],
                border=ft.Border.all(1, colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                padding=12,
            )
            students_list_column.controls.append(card)

    search_field = ft.TextField(
        hint_text=t["search_hint"],
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_color=colors["border"],
        focused_border_color=colors["primary"],
        text_size=13,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        on_change=lambda e: (render_student_cards(e.control.value), page.update()),
    )

    render_student_cards()

    tab_students_content = ft.Column(
        controls=[
            ft.Container(height=6),
            search_field,
            ft.Container(height=6),
            students_list_column,
        ],
        spacing=4,
    )

    # ─── SEGMENTED TAB SWITCHER (100% RESPONSIVO / SEM COLLAPSE) ───
    active_tab = [0]
    tab_container = ft.Container(content=tab_diagnostics_content)

    tab_btn_diag = ft.Container(expand=True)
    tab_btn_roster = ft.Container(expand=True)
    tabs_switcher_row = ft.Row(controls=[tab_btn_diag, tab_btn_roster], spacing=8)

    def set_tab(index: int):
        active_tab[0] = index
        tab_container.content = tab_diagnostics_content if index == 0 else tab_students_content
        refresh_tab_buttons()
        page.update()

    def refresh_tab_buttons():
        is_diag = active_tab[0] == 0
        tab_btn_diag.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.INSIGHTS_ROUNDED, size=15, color=ft.Colors.WHITE if is_diag else colors["text_sec"]),
                ft.Text(t["tab_diag"], size=12, weight=ft.FontWeight.BOLD if is_diag else ft.FontWeight.W_500, color=ft.Colors.WHITE if is_diag else colors["text_sec"]),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        )
        tab_btn_diag.bgcolor = colors["primary"] if is_diag else colors["surface"]
        tab_btn_diag.border = ft.Border.all(1, colors["primary"] if is_diag else colors["border"])
        tab_btn_diag.border_radius = Styles.BORDER_RADIUS_SM
        tab_btn_diag.padding = ft.Padding.symmetric(vertical=10, horizontal=6)
        tab_btn_diag.alignment = ft.Alignment.CENTER
        tab_btn_diag.on_click = lambda e: set_tab(0)

        is_roster = active_tab[0] == 1
        tab_btn_roster.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.PEOPLE_ROUNDED, size=15, color=ft.Colors.WHITE if is_roster else colors["text_sec"]),
                ft.Text(f"{t['tab_roster']} ({len(all_students)})", size=12, weight=ft.FontWeight.BOLD if is_roster else ft.FontWeight.W_500, color=ft.Colors.WHITE if is_roster else colors["text_sec"]),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        )
        tab_btn_roster.bgcolor = colors["primary"] if is_roster else colors["surface"]
        tab_btn_roster.border = ft.Border.all(1, colors["primary"] if is_roster else colors["border"])
        tab_btn_roster.border_radius = Styles.BORDER_RADIUS_SM
        tab_btn_roster.padding = ft.Padding.symmetric(vertical=10, horizontal=6)
        tab_btn_roster.alignment = ft.Alignment.CENTER
        tab_btn_roster.on_click = lambda e: set_tab(1)

    refresh_tab_buttons()

    return ft.View(
        route="/admin",
        appbar=app_bar,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            centered_content(
                page,
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=colors["secondary"], size=16),
                                    ft.Text(t["subtitle"], size=12, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ],
                                spacing=6,
                            ),
                            margin=ft.Margin.only(top=4, bottom=8),
                        ),
                        kpi_grid,
                        ft.Container(height=12),
                        tabs_switcher_row,
                        ft.Container(height=8),
                        tab_container,
                    ],
                    spacing=0,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"],
        padding=0,
    )
