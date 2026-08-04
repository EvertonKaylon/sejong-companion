import flet as ft
from ..theme import get_theme_colors, Styles
from ..services import DataService, ProgressService, FullscreenService
from ..components.quiz_widget import QuizWidget

def quiz_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    progress_service = ProgressService(page)

    unit_id = page.router.current_unit_id
    
    # Carregar questões da unidade correta
    exercises = []
    unit_title = ""
    if unit_id == "unit_intro":
        data = DataService.get_unit_intro()
        if data:
            exercises = data.exercises
            unit_title = data.title
    elif unit_id == "unit_01":
        data = DataService.get_unit_one()
        if data:
            exercises = data.exercises
            unit_title = data.title

    if not exercises:
        return ft.View(
            route="/quiz",
            controls=[
                ft.AppBar(title=ft.Text("Erro"), bgcolor=colors["surface"]),
                ft.Text("Nenhum exercício encontrado para esta unidade.", color=colors["incorrect"])
            ]
        )

    # Estado local do Quiz
    state = {
        "current_index": 0,
        "score": 0,
        "answers": []  # List of booleans
    }

    # Container principal de conteúdo que será atualizado dinamicamente
    main_content = ft.Container(padding=16)

    # AppBar com progresso
    progress_text = ft.Text("Questão 1 de X", size=13, weight=ft.FontWeight.W_500, color=colors["text_sec"])
    progress_bar = ft.ProgressBar(value=0, color=colors["primary"], bgcolor=colors["border"], height=6, border_radius=3)
    
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: confirm_exit()
        ),
        title=ft.Text(f"Quiz: {unit_title}", weight=ft.FontWeight.BOLD, size=15, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0
    )

    def confirm_exit():
        # Voltar para a view anterior de forma direta
        if unit_id == "unit_intro":
            page.router.navigate_to("/hangul")
        else:
            page.router.navigate_to("/lesson", unit_id)

    def update_progress_header():
        total = len(exercises)
        curr = state["current_index"]
        progress_text.value = f"Questão {curr + 1} de {total}"
        progress_bar.value = curr / total if total > 0 else 0.0
        page.update()

    def handle_answer(is_correct: bool):
        if is_correct:
            state["score"] += 1
        state["answers"].append(is_correct)

    def handle_next():
        state["current_index"] += 1
        if state["current_index"] < len(exercises):
            render_current_question()
        else:
            render_results()

    # Flag para saber se a View já foi montada na página. Na primeira
    # chamada (linha ~219, antes do "return ft.View(...)"), main_content
    # ainda não foi anexado a nenhuma página, e a PROPRIEDADE .page do Flet
    # 0.85 levanta RuntimeError nesse caso (não retorna None como se poderia
    # supor) — por isso NÃO dá pra usar "if main_content.page:" aqui.
    view_mounted = {"value": False}

    def render_current_question():
        update_progress_header()
        q = exercises[state["current_index"]]
        
        # Recriar widget do quiz para a pergunta atual
        main_content.content = QuizWidget(
            question_data=q,
            is_dark=is_dark,
            on_next=handle_next,
            on_answer=handle_answer
        )
        if view_mounted["value"]:
            main_content.update()

    def render_results():
        # Salvar o progresso como concluído (100%) no local storage
        progress_service.save_progress(unit_id, 1.0)
        
        total = len(exercises)
        score = state["score"]
        pct = (score / total) if total > 0 else 0.0
        
        # Mensagens motivacionais personalizadas
        if pct == 1.0:
            msg = "Gabaritou! Excelente progresso! 🎉"
            sub_msg = "Você demonstrou domínio total do conteúdo desta unidade. Continue assim!"
        elif pct >= 0.7:
            msg = "Parabéns! Excelente resultado! 🌟"
            sub_msg = "Você acertou a maior parte das perguntas. Pronto para avançar!"
        else:
            msg = "Bom esforço! Que tal tentar de novo? 💪"
            sub_msg = "Revise as fichas de estudo e tente novamente para melhorar sua pontuação."

        results_layout = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=20),
                    # Círculo com porcentagem de acerto
                    ft.Stack(
                        controls=[
                            ft.ProgressRing(
                                value=pct,
                                color=colors["correct"] if pct >= 0.7 else colors["accent"],
                                bgcolor=colors["border"],
                                width=120,
                                height=120,
                                stroke_width=10
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"{int(pct * 100)}%",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=colors["text"]
                                ),
                                alignment=ft.Alignment.CENTER,
                                width=120,
                                height=120,
                            )
                        ],
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Container(height=16),
                    ft.Text(msg, size=20, weight=ft.FontWeight.BOLD, color=colors["text"], text_align=ft.TextAlign.CENTER),
                    ft.Text(sub_msg, size=13, color=colors["text_sec"], text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    # Placar resumido
                    ft.Row(
                        controls=[
                            ft.Text(f"Acertos: {score}", weight=ft.FontWeight.BOLD, color=colors["correct"], size=15),
                            ft.Text(f"Erros: {total - score}", weight=ft.FontWeight.BOLD, color=colors["incorrect"], size=15),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20
                    ),
                    ft.Container(height=30),
                    # Botões de Ação
                     ft.ElevatedButton(
                        content="Voltar ao Menu Principal",
                        icon=ft.Icons.HOME_ROUNDED,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=colors["primary"],
                            shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                            padding=14
                        ),
                        on_click=lambda e: page.router.navigate_to("/home"),
                        width=250
                    ),
                    ft.OutlinedButton(
                        content="Refazer Desafio",
                        icon=ft.Icons.REPLAY_ROUNDED,
                        style=ft.ButtonStyle(
                            color=colors["primary"],
                            shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                            padding=14
                        ),
                        on_click=lambda e: reset_quiz(),
                        width=250
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.Alignment.CENTER,
        )

        # Ocultar barra de progresso no topo nos resultados
        progress_header.visible = False
        main_content.content = results_layout
        page.update()

    def reset_quiz():
        state["current_index"] = 0
        state["score"] = 0
        state["answers"].clear()
        progress_header.visible = True
        render_current_question()

    progress_header = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([progress_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                progress_bar
            ],
            spacing=4
        ),
        padding=16
    )

    # Iniciar primeira pergunta (main_content ainda não está na página aqui)
    render_current_question()
    view_mounted["value"] = True

    return ft.View(
        route="/quiz",
        appbar=app_bar,
        controls=[
            progress_header,
            main_content
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"]
    )