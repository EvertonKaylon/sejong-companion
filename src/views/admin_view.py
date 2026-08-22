import flet as ft
from datetime import datetime
from ..components import centered_content
from ..theme import get_theme_colors, Styles, Responsive
from ..services import AdminService, DataService

def admin_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    w = page.width or 400

    # Estado de autenticação administrativa na sessão ativa
    if not hasattr(page, "_admin_authenticated"):
        page._admin_authenticated = False

    def rebuild_view():
        page.views.clear()
        page.views.append(admin_view(page))
        page.update()

    # ─── 1. TELA DE LOGIN / AUTENTICAÇÃO POR PIN ───
    if not page._admin_authenticated:
        pin_input = ft.TextField(
            label="PIN de Acesso",
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
                    ft.Text("PIN incorreto. Tente novamente.", size=12, color=colors["incorrect"], weight=ft.FontWeight.W_500),
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
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED, color=colors["primary"], size=44),
                        width=72,
                        height=72,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=f"{colors['primary']}18",
                        shape=ft.BoxShape.CIRCLE,
                    ),
                    ft.Container(height=8),
                    ft.Text("Portal Pedagógico", size=20, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Text("Área Administrativa · 관리자", size=13, weight=ft.FontWeight.W_600, color=colors["primary"]),
                    ft.Text(
                        "Acesso restrito ao corpo docente do Sejong Hakdang e administradores para análise de evidência pedagógica.",
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
                                ft.Text("Entrar no Painel", weight=ft.FontWeight.BOLD, size=14),
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
                        content=ft.Text("Voltar para o Início", color=colors["text_sec"], size=12),
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
            content=ft.Text("🔄 Dados recarregados em tempo real!"),
            bgcolor=colors["secondary"],
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    def handle_export(e):
        report_md = AdminService.export_report_markdown()
        # Salvar arquivo de relatório em scratch ou data/reports
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        reports_dir = os.path.join(base_dir, "data", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filename = f"relatorio_pedagogico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_md)

        snack = ft.SnackBar(
            content=ft.Text(f"📄 Relatório exportado com sucesso: data/reports/{filename}"),
            bgcolor=colors["correct"],
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    import os  # Local import just in case

    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: page.router.navigate_to("/home"),
            tooltip="Voltar para a Home",
        ),
        title=ft.Text("Portal do Professor · 교사용", weight=ft.FontWeight.BOLD, size=18, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0,
        actions=[
            ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                icon_color=colors["primary"],
                on_click=handle_refresh,
                tooltip="Atualizar Dados",
            ),
            ft.IconButton(
                icon=ft.Icons.DOWNLOAD_ROUNDED,
                icon_color=colors["secondary"],
                on_click=handle_export,
                tooltip="Exportar Relatório Markdown",
            ),
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                icon_color=colors["incorrect"],
                on_click=handle_logout,
                tooltip="Sair do Modo Admin",
            ),
            ft.Container(width=6),
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
                                width=34,
                                height=34,
                                alignment=ft.Alignment.CENTER,
                                bgcolor=f"{color_hex}15",
                                border_radius=Styles.BORDER_RADIUS_SM,
                            ),
                            ft.Text(title, size=12, weight=ft.FontWeight.W_600, color=colors["text_sec"]),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Text(subtitle, size=11, color=colors["text_sec"]),
                ],
                spacing=3,
            ),
            bgcolor=colors["surface"],
            border=ft.Border.all(1, colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            padding=12,
            expand=True,
        )

    kpi_row = ft.Row(
        controls=[
            make_kpi_card("Alunos", str(kpis["total_students"]), "Perfis em disco", "👥", colors["primary"]),
            make_kpi_card("Progresso Médio", f"{kpis['avg_progress_pct']:.1%}", "Currículo 1A + 1B", "📊", colors["secondary"]),
            make_kpi_card("Retenção SRS", f"{kpis['avg_retention_pct']:.1%}", f"{kpis['total_memory_nodes']} cartões", "🧠", colors["vitality_high"]),
            make_kpi_card("Quizzes", str(kpis["total_quizzes_completed"]), f"{kpis['total_telemetry_events']} eventos", "📝", "#F88807"),
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
                                    ft.Text(f"Questão: {q['question_id']} ({q['unit_id']})", size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(f"Tentativas: {q['total_attempts']} | Erros: {q['errors']} | Tempo médio: {q['avg_response_time_ms']}ms", size=11, color=colors["text_sec"]),
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
                content=ft.Text("Nenhum dado de erro em exercícios registrado ainda.", size=12, color=colors["text_sec"]),
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
                                    ft.Text(f"Unidade: {u['unit_id']}", size=12, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(f"Abandono: {rate:.1%} ({u['completed_count']}/{u['opened_count']} concluídos)", size=11, color=colors["text_sec"]),
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
                content=ft.Text("Nenhum evento de abertura/abandono registrado ainda.", size=12, color=colors["text_sec"]),
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
                                    ft.Text(f"Item: {c['item_id']} ({c['unit_id']})", size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(f"Erros (Again): {c['again_count']}x de {c['total_reviews']} revisões ({c['again_rate']:.1%})", size=11, color=colors["text_sec"]),
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
                content=ft.Text("Nenhuma reincidência crítica de vocabulário registrada.", size=12, color=colors["text_sec"]),
                padding=10,
            )
        )

    tab_diagnostics_content = ft.Column(
        controls=[
            ft.Container(height=10),
            ft.Text("⚠️ Questões com Maior Taxa de Erro (Top Foco de Reforço)", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Column(controls=hardest_controls, spacing=0),
            ft.Container(height=14),
            ft.Text("📉 Funil de Conclusão e Abandono por Unidade", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Column(controls=drop_off_controls, spacing=0),
            ft.Container(height=14),
            ft.Text("🔄 Vocabulário com Maior Taxa de 'Again' (Memória Frágil)", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
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
                    content=ft.Text("Nenhum aluno encontrado.", size=13, color=colors["text_sec"]),
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
                                        ft.Text(f"Livro 1A: {c_1a}/11", size=11, color=colors["text_sec"]),
                                        ft.ProgressBar(value=min(1.0, c_1a / 11.0), color=colors["primary"], bgcolor=colors["border"], height=4, border_radius=2),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"Livro 1B: {c_1b}/12", size=11, color=colors["text_sec"]),
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
                                ft.Text(f"Progresso Geral: {prog_pct:.1%}", size=11, weight=ft.FontWeight.W_600, color=colors["text"]),
                                ft.Text(f"Retenção SRS: {ret_pct:.1%} ({s['memory_nodes_count']} itens)", size=11, weight=ft.FontWeight.W_600, color=colors["vitality_high"] if ret_pct >= 0.75 else colors["warning"]),
                                ft.Text(f"Último: {last_date}", size=11, color=colors["text_sec"]),
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
        hint_text="Buscar aluno por nome ou Student ID...",
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
            ft.Container(height=10),
            search_field,
            ft.Container(height=6),
            students_list_column,
        ],
        spacing=4,
    )

    tab_headers = [
        ft.Tab(label="Diagnóstico da Turma", icon=ft.Icons.INSIGHTS_ROUNDED),
        ft.Tab(label=f"Roster de Alunos ({len(all_students)})", icon=ft.Icons.PEOPLE_ROUNDED),
    ]
    tab_contents = [
        tab_diagnostics_content,
        tab_students_content,
    ]

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        expand=True,
        length=len(tab_headers),
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=tab_headers,
                    label_color=colors["primary"],
                    unselected_label_color=colors["text_sec"],
                    indicator_color=colors["primary"],
                ),
                ft.TabBarView(
                    expand=True,
                    controls=tab_contents,
                ),
            ],
        ),
    )

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
                                    ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=colors["secondary"], size=18),
                                    ft.Text("Central de Análise e Evidência Pedagógica", size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ],
                                spacing=6,
                            ),
                            margin=ft.Margin.only(top=4, bottom=8),
                        ),
                        kpi_row,
                        ft.Container(height=12),
                        tabs,
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
