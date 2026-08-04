from ..theme import Colors, Styles, get_theme_colors
from ..services import FullscreenService

def ui_test_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)

    # Estado local da página de teste
    selected_quiz_option = [None]  # Index da opção selecionada
    quiz_submitted = [False]       # Se o quiz já foi enviado
    audio_playing = [False]        # Estado de reprodução do áudio simulado

    def refresh_page():
        page.views.clear()
        page.views.append(ui_test_view(page))
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if is_dark else ft.ThemeMode.DARK
        refresh_page()

    # ─── CABEÇALHO COM LOGO RETRÔ SEJOLLIP-CHE ───
    logo_container = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "세종학당",
                                size=20,
                                font_family="Seollip-che",
                                weight=ft.FontWeight.W_900,
                                color=Colors.ACCENT if is_dark else Colors.PRIMARY_DARK,
                                style=ft.TextStyle(letter_spacing=2),
                            ),
                            ft.Text(
                                "COMPANION",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=Colors.SECONDARY_LIGHT if is_dark else Colors.PRIMARY,
                                style=ft.TextStyle(letter_spacing=4),
                            ),
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                    bgcolor="#1E004C97" if not is_dark else "#267C4DFF",
                    border=ft.Border.all(2, Colors.PRIMARY if not is_dark else Colors.SECONDARY),
                    border_radius=Styles.BORDER_RADIUS_SM,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "세종학당 컴패니언",
                            size=18,
                            font_family="Seollip-che",
                            weight=ft.FontWeight.BOLD,
                            color=colors["text"],
                        ),
                        ft.Text(
                            "Plano UI/UX • Modo Midnight Blue & KSI Light",
                            size=11,
                            color=colors["text_sec"],
                        ),
                    ],
                    spacing=2,
                ),
            ],
            spacing=14,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.all(12),
        bgcolor=colors["surface"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
    )

    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda _: page.router.navigate_to("/home"),
            tooltip="Voltar para o Início",
        ),
        title=ft.Text("Laboratório UI/UX", weight=ft.FontWeight.BOLD, size=18, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0,
        actions=[
            FullscreenService.create_fullscreen_button(page, colors),
            ft.IconButton(
                icon=ft.Icons.DARK_MODE_ROUNDED if not is_dark else ft.Icons.LIGHT_MODE_ROUNDED,
                icon_color=colors["primary"],
                on_click=toggle_theme,
                tooltip="Alternar Tema (Claro / Midnight Blue)",
            ),
            ft.Container(width=8),
        ],
    )

    # ─── SEÇÃO 1: SWATCHES DE CORES E PAPÉIS SEMÂNTICOS ───
    def make_swatch(title: str, hex_val: str, role_desc: str, text_color="#FFFFFF"):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        height=44,
                        bgcolor=hex_val,
                        border_radius=Styles.BORDER_RADIUS_SM,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(hex_val, size=11, weight=ft.FontWeight.BOLD, color=text_color),
                    ),
                    ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Text(role_desc, size=10, color=colors["text_sec"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=4,
            ),
            padding=ft.Padding.all(10),
            bgcolor=colors["surface"],
            border=ft.Border.all(1, colors["border"]),
            border_radius=Styles.BORDER_RADIUS_MD,
            width=160,
        )

    swatches_row = ft.Row(
        controls=[
            make_swatch("Azul Sejong (Primary)", Colors.PRIMARY, "Cor oficial KSI • Estrutura, abas & títulos"),
            make_swatch("Violeta (Secondary)", Colors.SECONDARY, "Ações de destaque, TTS & progresso"),
            make_swatch("Dourado (Accent)", Colors.ACCENT, "Dicas mnemônicas & selos culturais", "#1A1A1A"),
            make_swatch("Carmesim (Erro/Quiz)", Colors.INCORRECT, "Uso estrito: Resposta errada & erros"),
            make_swatch("Verde (Sucesso)", Colors.CORRECT, "Uso estrito: Resposta correta & progresso"),
            make_swatch("Midnight Blue (Dark)", Colors.DARK_BG, "Fundo escuro profundo elegante"),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
    )

    palette_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PALETTE_ROUNDED, color=colors["primary"], size=20),
                        ft.Text("1. Harmonia de Cores & Papéis Semânticos", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "O Violeta (#7C3AED) é preservado como cor de ação interativa (Secondary), enquanto o Azul Real Sejong (#0356C5) garante alinhamento com a marca oficial. O Carmesim (#C50337) fica isolado para feedback de erro.",
                    size=12,
                    color=colors["text_sec"],
                ),
                ft.Container(height=6),
                swatches_row,
            ],
            spacing=8,
        ),
        padding=ft.Padding.all(16),
        bgcolor=colors["card_bg"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
    )

    # ─── SEÇÃO 2: LOGO RETRÔ & TIPOGRAFIA ───
    typography_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.TEXT_FIELDS_ROUNDED, color=colors["secondary"], size=20),
                        ft.Text("2. Identidade Tipográfica & Logotipo Retrô", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "Apresentação da marca 세종학당 컴패니언 com conceito retrô-industrial inspirado no letreiro Seollip-che (설립체), com Noto Sans KR mantendo clareza total na interface de ensino.",
                    size=12,
                    color=colors["text_sec"],
                ),
                ft.Container(height=8),
                # Wordmark retrô grande
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("세종학당 컴패니언", size=26, font_family="Seollip-che", weight=ft.FontWeight.W_900, color=Colors.PRIMARY if not is_dark else Colors.ACCENT, style=ft.TextStyle(letter_spacing=2)),
                            ft.Text("KING SEJONG INSTITUTE COMPANION • LEARNING SYSTEM", size=10, weight=ft.FontWeight.BOLD, color=Colors.SECONDARY_LIGHT, style=ft.TextStyle(letter_spacing=3)),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=ft.Padding.symmetric(vertical=20, horizontal=16),
                    bgcolor="#0D004C97" if not is_dark else "#9902060E",
                    border=ft.Border.all(2, Colors.PRIMARY if not is_dark else Colors.INFO_500),
                    border_radius=Styles.BORDER_RADIUS_LG,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(height=10),
                # Comparativo de Fontes
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text("PRETENDARD (Fonte Padrão da UI)", size=11, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                                            ft.Container(content=ft.Text("Ativa no Sistema", size=9, color="#FFFFFF"), bgcolor=colors["primary"], padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Text("안녕하세요? 저는 안나예요. (Pretendard 15px)", size=15, font_family="Pretendard", weight=ft.FontWeight.W_600, color=colors["text"]),
                                    ft.Text("Interface limpa com encaixe perfeito entre caracteres latinos e coreanos.", size=11, font_family="Pretendard", color=colors["text_sec"]),
                                ],
                                spacing=2,
                            ),
                            padding=ft.Padding.all(10),
                            bgcolor="#0A004C97" if not is_dark else "#99091122",
                            border=ft.Border.all(1, colors["primary_light"] if not is_dark else colors["border"]),
                            border_radius=Styles.BORDER_RADIUS_SM,
                        ),
                        ft.Container(height=4),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("SEOLLIP-CHE / 설립체 (Fonte Retrô do Logotipo)", size=11, weight=ft.FontWeight.BOLD, color=Colors.ACCENT if is_dark else Colors.PRIMARY_DARK),
                                    ft.Text("세종학당 컴패니언 (Seollip-che 18px)", size=18, font_family="Seollip-che", color=colors["text"]),
                                ],
                                spacing=2,
                            ),
                            padding=ft.Padding.all(10),
                            bgcolor="#0AF5A623" if not is_dark else "#14F5A623",
                            border=ft.Border.all(1, Colors.ACCENT),
                            border_radius=Styles.BORDER_RADIUS_SM,
                        ),
                    ],
                    spacing=6,
                )
            ],
            spacing=8,
        ),
        padding=ft.Padding.all(16),
        bgcolor=colors["card_bg"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
    )

    # ─── SEÇÃO 3: SIMULADOR DE QUIZ (SEMÂNTICA DE AÇÃO VS ERRO) ───
    quiz_options_container = ft.Column(spacing=8)

    def render_quiz_options():
        quiz_options_container.controls.clear()
        options_data = [
            ("A", "안녕 (Annyeong)", False),
            ("B", "안녕하세요 (Annyeonghaseyo)", True), # Resposta correta
            ("C", "감사합니다 (Kamsahamnida)", False),
            ("D", "죄송합니다 (Joesonghamnida)", False),
        ]

        for idx, (letter, text, is_correct_choice) in enumerate(options_data):
            sel = selected_quiz_option[0] == idx
            sub = quiz_submitted[0]

            # Cores dinâmicas por estado
            bg_color = colors["surface"]
            border_color = colors["border"]
            icon_control = None
            text_col = colors["text"]

            if sub:
                if is_correct_choice:
                    bg_color = "#2619BD56"
                    border_color = Colors.CORRECT
                    icon_control = ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=Colors.CORRECT, size=20)
                    text_col = Colors.CORRECT
                elif sel and not is_correct_choice:
                    bg_color = "#26C50337"
                    border_color = Colors.INCORRECT
                    icon_control = ft.Icon(ft.Icons.CANCEL_ROUNDED, color=Colors.INCORRECT, size=20)
                    text_col = Colors.INCORRECT
            elif sel:
                border_color = colors["primary"]
                bg_color = "#190356C5"

            def make_on_click(i):
                def handler(e):
                    if not quiz_submitted[0]:
                        selected_quiz_option[0] = i
                        render_quiz_options()
                        page.update()
                return handler

            quiz_options_container.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(letter, size=12, weight=ft.FontWeight.BOLD, color=border_color if sel or sub else colors["text_sec"]),
                                width=28, height=28,
                                border_radius=14,
                                border=ft.Border.all(1.5, border_color),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Text(text, size=14, weight=ft.FontWeight.W_500, color=text_col, expand=True),
                            icon_control if icon_control else ft.Container(),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.all(12),
                    bgcolor=bg_color,
                    border=ft.Border.all(1.5 if (sel or sub) else 1, border_color),
                    border_radius=Styles.BORDER_RADIUS_SM,
                    on_click=make_on_click(idx),
                )
            )

    render_quiz_options()

    def submit_quiz(e):
        if selected_quiz_option[0] is not None and not quiz_submitted[0]:
            quiz_submitted[0] = True
            render_quiz_options()
            page.update()

    def reset_quiz(e):
        selected_quiz_option[0] = None
        quiz_submitted[0] = False
        render_quiz_options()
        page.update()

    quiz_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.QUIZ_ROUNDED, color=colors["primary"], size=20),
                        ft.Text("3. Validador de Quiz (Semântica de Erro vs Ação)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "Teste prático: Selecione uma opção e clique em 'Confirmar'. Note como o botão principal em Azul/Violeta permanece neutro e o Carmesim (#C50337) aparece exclusivamente na opção errada.",
                    size=12,
                    color=colors["text_sec"],
                ),
                ft.Container(height=4),
                ft.Text("Pergunta: Como se diz 'Olá' formal em coreano?", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                ft.Container(height=4),
                quiz_options_container,
                ft.Container(height=6),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Confirmar Resposta",
                            icon=ft.Icons.CHECK_ROUNDED,
                            bgcolor=colors["primary"],
                            color="#FFFFFF",
                            on_click=submit_quiz,
                        ),
                        ft.OutlinedButton(
                            "Resetar Teste",
                            icon=ft.Icons.REFRESH_ROUNDED,
                            on_click=reset_quiz,
                        ),
                    ],
                    spacing=12,
                )
            ],
            spacing=8,
        ),
        padding=ft.Padding.all(16),
        bgcolor=colors["card_bg"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
    )

    # ─── SEÇÃO 4: DEMONSTRADOR DE ÁUDIO TTS (TYPECAST.AI) ───
    audio_status_text = ft.Text("Pronto para ouvir (Voz Typecast.ai)", size=12, color=colors["text_sec"])

    def toggle_audio_sim(e):
        audio_playing[0] = not audio_playing[0]
        if audio_playing[0]:
            audio_status_text.value = "▶ Reproduzindo: '안녕하세요?' (Voz Coreana Natural)..."
            audio_status_text.color = Colors.SECONDARY
        else:
            audio_status_text.value = "⏹ Reprodução pausada."
            audio_status_text.color = colors["text_sec"]
        refresh_page()

    audio_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.GRAPHIC_EQ_ROUNDED, color=Colors.SECONDARY, size=20),
                        ft.Text("4. Microinteração de Áudio TTS (Typecast.ai)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "O Violeta (#7C3AED) é a cor principal para botões de escuta e recursos multimídia, separando claramente ações de aprendizagem de navegação geral.",
                    size=12,
                    color=colors["text_sec"],
                ),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.PAUSE_ROUNDED if audio_playing[0] else ft.Icons.PLAY_ARROW_ROUNDED,
                                icon_color="#FFFFFF",
                                icon_size=28,
                                on_click=toggle_audio_sim,
                            ),
                            bgcolor=Colors.SECONDARY if not audio_playing[0] else Colors.SECONDARY_LIGHT,
                            border_radius=Styles.BORDER_RADIUS_PILL,
                            padding=ft.Padding.all(6),
                            shadow=Styles.HOVER_SHADOW if audio_playing[0] else None,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Ouvir Pronúncia Nativa", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                audio_status_text,
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=8,
        ),
        padding=ft.Padding.all(16),
        bgcolor=colors["card_bg"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=Styles.BORDER_RADIUS_MD,
    )

    return ft.View(
        route="/ui_test",
        appbar=app_bar,
        controls=[
            logo_container,
            ft.Container(height=12),
            palette_card,
            ft.Container(height=12),
            typography_card,
            ft.Container(height=12),
            quiz_card,
            ft.Container(height=12),
            audio_card,
            ft.Container(height=24),
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"],
        padding=16,
    )
