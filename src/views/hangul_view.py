import flet as ft
from ..components import HangulCard, centered_content, build_oclusive_lab
from ..theme import get_theme_colors, Styles, Responsive
from ..services import DataService

def hangul_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)
    w = page.width or 400

    # Carregar dados do Hangul
    data = DataService.get_unit_intro()
    if not data:
        return ft.View(
            route="/hangul",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.AppBar(title=ft.Text("Erro"), bgcolor=colors["surface"]),
                ft.Text("Erro ao carregar dados do 한글.", color=colors["incorrect"])
            ]
        )

    # AppBar
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: page.router.navigate_to("/home")
        ),
        title=ft.Text("Alfabeto 한글", weight=ft.FontWeight.BOLD, size=18, color=colors["text"]),
        bgcolor=colors["surface"],
        elevation=0
    )

    # ─── Aviso Anti-Romanização ───
    anti_roman_banner = ft.Container()
    if data.anti_romanization_notice:
        notice = data.anti_romanization_notice
        anti_roman_banner = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(notice.icon, size=22),
                            ft.Text(notice.title, size=13, weight=ft.FontWeight.BOLD, color=colors["incorrect"]),
                        ],
                        spacing=8,
                    ),
                    ft.Text(notice.content, size=12, color=colors["text_sec"]),
                ],
                spacing=4,
            ),
            padding=Responsive.value(w, compact=10, medium=12),
            bgcolor="#0DC50337",
            border=ft.Border.all(1, "#33C50337"),
            border_radius=Styles.BORDER_RADIUS_MD,
            margin=ft.Margin.only(bottom=8),
        )

    # ─── Aviso de Escrita Manual ───
    writing_banner = ft.Container()
    if data.writing_alert:
        wa = data.writing_alert
        writing_banner = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(wa.icon, size=22),
                            ft.Text(wa.title, size=13, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                        ],
                        spacing=8,
                    ),
                    ft.Text(wa.content, size=12, color=colors["text_sec"]),
                ],
                spacing=4,
            ),
            padding=Responsive.value(w, compact=10, medium=12),
            bgcolor="#0D188150",
            border=ft.Border.all(1, "#33188150"),
            border_radius=Styles.BORDER_RADIUS_MD,
            margin=ft.Margin.only(bottom=8),
        )

    # ─── Grid de Vogais ───
    card_size = Responsive.value(w, compact=100, medium=140)

    vowels_wrap = ft.Row(
        controls=[HangulCard(v, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w), size=card_size) for v in data.vowels],
        spacing=10,
        run_spacing=10,
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    vowels_col = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=4),
                vowels_wrap,
                ft.Container(height=12),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=4, vertical=6),
        alignment=ft.Alignment.TOP_CENTER,
    )

    # ─── Grid de Consoantes Planas ───
    plain_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("🌱", size=18),
                ft.Text("Consoantes Planas (기본)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        margin=ft.Margin.only(top=4, bottom=6),
        alignment=ft.Alignment.CENTER,
    )

    consonants_wrap = ft.Row(
        controls=[HangulCard(c, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w), size=card_size) for c in data.consonants],
        spacing=10,
        run_spacing=10,
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # ─── Grid de Consoantes Aspiradas ───
    aspirated_section = ft.Container()
    if data.aspirated_consonants:
        aspirated_section = ft.Column(
            controls=[
                ft.Container(height=12),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("💨", size=18),
                            ft.Text("Consoantes Aspiradas", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    margin=ft.Margin.only(bottom=4),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text("Produzidas com sopro forte de ar. Coloque a mão na frente da boca para sentir!", size=12, color=colors["text_sec"]),
                ft.Container(height=8),
                ft.Row(
                    controls=[HangulCard(c, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w), size=card_size) for c in data.aspirated_consonants],
                    spacing=10,
                    run_spacing=10,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ─── Grid de Consoantes Tensas ───
    tense_section = ft.Container()
    if data.tense_consonants:
        tense_section = ft.Column(
            controls=[
                ft.Container(height=12),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("💪", size=18),
                            ft.Text("Consoantes Tensas (쌍)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    margin=ft.Margin.only(bottom=4),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text("Produzidas com tensão na garganta, SEM sopro de ar. Essa distinção não existe no português!", size=12, color=colors["text_sec"]),
                ft.Container(height=8),
                ft.Row(
                    controls=[HangulCard(c, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w), size=card_size) for c in data.tense_consonants],
                    spacing=10,
                    run_spacing=10,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ─── Lab Oclusivo (integrado na aba Consoantes) ───
    oclusive_lab_section = build_oclusive_lab(page, colors, w)

    consonants_col = ft.Container(
        content=ft.Column(
            controls=[
                plain_header,
                consonants_wrap,
                aspirated_section,
                tense_section,
                ft.Divider(height=1, color=colors["border"]),
                oclusive_lab_section,
                ft.Container(height=12),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=4, vertical=6),
        alignment=ft.Alignment.TOP_CENTER,
    )

    # ─── 받침 Guide ───
    batchim_section = ft.Container()
    if data.batchim_guide:
        bg = data.batchim_guide
        
        batchim_controls = [
            ft.Text(
                bg.title,
                size=17,
                weight=ft.FontWeight.BOLD,
                color=colors["primary"],
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=2),
            ft.Text(bg.explanation, size=12, color=colors["text_sec"], text_align=ft.TextAlign.CENTER),
            ft.Container(height=8),
        ]

        # Aviso do 'i' fantasma
        if bg.lusophone_warning:
            lw = bg.lusophone_warning
            batchim_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(lw.icon, size=24),
                                    ft.Text(lw.title, size=13, weight=ft.FontWeight.BOLD, color=colors["incorrect"]),
                                ],
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Container(height=2),
                            ft.Text(lw.content, size=12, color=colors["text"]),
                        ],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=12,
                    bgcolor="#0DC50337",
                    border=ft.Border.all(1, "#33C50337"),
                    border_radius=Styles.BORDER_RADIUS_MD,
                    margin=ft.Margin.only(bottom=10),
                )
            )

        # Regras de neutralização com Exemplo Auditivo (Áudio-Visual Gating)
        for rule in bg.neutralization_rules:
            chars_text = " / ".join(rule.batchim_chars)
            rule_column_controls = [
                ft.Row(
                    controls=[
                        ft.Text(rule.position, size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Text(f"[ {chars_text} ]", size=13, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(f"→ {rule.sound}", size=12, color=colors["text_sec"]),
                ft.Text(f"💡 {rule.tip}", size=11, color=colors["accent"], italic=True),
            ]

            # Botão / Badge de Exemplo Auditivo
            if hasattr(rule, 'example_word') and rule.example_word:
                ex_word = rule.example_word
                ex_meaning = getattr(rule, 'example_meaning', '')
                audio_btn = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.VOLUME_UP_ROUNDED, size=16, color=colors["primary"]),
                            ft.Text(f"Exemplo Auditivo: {ex_word}", size=12, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                            ft.Text(f"({ex_meaning})" if ex_meaning else "", size=11, color=colors["text_sec"]),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    bgcolor="#14004C97",
                    border=ft.Border.all(1, colors["primary_light"]),
                    border_radius=Styles.BORDER_RADIUS_SM,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    on_click=lambda e, w=ex_word: page.audio_service.play_korean(w),
                    tooltip="Toque para ouvir a pronúncia exata do 받침",
                    margin=ft.Margin.only(top=4),
                )
                rule_column_controls.append(audio_btn)

            batchim_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=rule_column_controls,
                        spacing=3,
                    ),
                    padding=12,
                    bgcolor=colors["card_bg"],
                    border=ft.Border.all(1, colors["border"]),
                    border_radius=Styles.BORDER_RADIUS_MD,
                    margin=ft.Margin.only(bottom=8),
                )
            )

        batchim_section = ft.Container(
            content=ft.Column(
                controls=batchim_controls,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=4, vertical=6),
            alignment=ft.Alignment.TOP_CENTER,
        )

    # ─── Ganada (가나다) — Sequência Alfabética Tradicional (ZERO Romanização) ───

    ganada_chars = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하"]

    chip_size = Responsive.value(w, compact=46, medium=60)
    chip_font_size = Responsive.value(w, compact=18, medium=24)

    ganada_chips = []
    for char in ganada_chars:
        ganada_chips.append(
            ft.Container(
                content=ft.Text(char, size=chip_font_size, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                width=chip_size,
                height=chip_size,
                alignment=ft.Alignment.CENTER,
                bgcolor=colors["surface"],
                border=ft.Border.all(1.5, colors["primary"]),
                border_radius=Styles.BORDER_RADIUS_SM,
                on_click=lambda e, c=char: page.audio_service.play_korean(c),
                animate=150,
                tooltip=f"Ouvir {char}",
            )
        )

    ganada_section = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("🔤", size=18),
                        ft.Text("Sequência Ganada (가나다)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                margin=ft.Margin.only(bottom=4),
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(
                "A ordem alfabética coreana combina as 14 consoantes básicas com a vogal ㅏ (a). Toque para ouvir!",
                size=12, color=colors["text_sec"], no_wrap=False,
            ),
            ft.Container(height=6),
            # Explicação do bloco silábico
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Estrutura do Bloco Silábico:", size=12, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                        ft.Text("• Consoante + Vogal → 가 (ㄱ + ㅏ)", size=12, color=colors["text_sec"]),
                        ft.Text("• Consoante + Vogal + 받침 → 강 (ㄱ + ㅏ + ㅇ)", size=12, color=colors["text_sec"]),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=12,
                bgcolor=colors["surface"],
                border=ft.Border.all(1, colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                margin=ft.Margin.only(bottom=8),
            ),
            ft.Row(
                controls=ganada_chips,
                wrap=True,
                spacing=6,
                run_spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ─── Números Coreanos (1–10) ───

    numbers_data = [
        ("1", "일", "하나"),
        ("2", "이", "둘"),
        ("3", "삼", "셋"),
        ("4", "사", "넷"),
        ("5", "오", "다섯"),
        ("6", "육", "여섯"),
        ("7", "칠", "일곱"),
        ("8", "팔", "여덟"),
        ("9", "구", "아홉"),
        ("10", "십", "열"),
    ]

    number_rows = []
    for num, sino, native in numbers_data:
        number_rows.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        # Número
                        ft.Container(
                            content=ft.Text(num, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            width=32, height=32,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=colors["primary"],
                            border_radius=Styles.BORDER_RADIUS_SM,
                        ),
                        # Sino-Coreano
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("한자어", size=9, color=colors["text_sec"]),
                                    ft.Text(sino, size=17, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                            ),
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            on_click=lambda e, s=sino: page.audio_service.play_korean(s),
                        ),
                        ft.VerticalDivider(width=1, color=colors["border"]),
                        # Coreano Nativo
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("고유어", size=9, color=colors["text_sec"]),
                                    ft.Text(native, size=17, weight=ft.FontWeight.BOLD, color=colors["accent"]),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                            ),
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            on_click=lambda e, n=native: page.audio_service.play_korean(n),
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                bgcolor=colors["card_bg"],
                border=ft.Border.all(1, colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                on_click=lambda e, s=sino, n=native: page.audio_service.play_korean(f"{s}, {n}"),
                animate=150,
            )
        )

    numbers_section = ft.Column(
        controls=[
            ft.Container(height=12),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("🔢", size=18),
                        ft.Text("Números Coreanos (1–10)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                margin=ft.Margin.only(bottom=4),
                alignment=ft.Alignment.CENTER,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("O coreano possui dois sistemas numéricos:", size=12, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                        ft.Text("• 한자어 (Sino-Coreano): usado para datas, dinheiro, telefone e minutos.", size=12, color=colors["text_sec"], no_wrap=False),
                        ft.Text("• 고유어 (Nativo): usado para horas, idade e contar objetos.", size=12, color=colors["text_sec"], no_wrap=False),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=12,
                bgcolor=colors["surface"],
                border=ft.Border.all(1, colors["border"]),
                border_radius=Styles.BORDER_RADIUS_MD,
                margin=ft.Margin.only(bottom=8),
            ),
            ft.Column(controls=number_rows, spacing=4),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ─── Lista de Sílabas Originais ───
    original_syllables_header = ft.Column(
        controls=[
            ft.Container(height=12),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("📝", size=18),
                        ft.Text("Sílabas de Exemplo", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                margin=ft.Margin.only(bottom=6),
                alignment=ft.Alignment.CENTER,
            ),
        ],
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    syllable_box_size = Responsive.value(w, compact=46, medium=60)
    syllable_font_size = Responsive.value(w, compact=20, medium=26)

    syllable_cards = []
    for s in data.syllables:
        syllable_cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        # Botão quadrado clicável da sílaba
                        ft.Container(
                            content=ft.Text(s.block, size=syllable_font_size, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                            bgcolor=colors["surface"],
                            border=ft.Border.all(1.5, colors["primary"]),
                            border_radius=Styles.BORDER_RADIUS_SM,
                            width=syllable_box_size,
                            height=syllable_box_size,
                            alignment=ft.Alignment.CENTER,
                            tooltip=f"Ouvir sílaba {s.block}",
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(f"Composição: {s.spelling}", size=13, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ft.Text(f"Significado: {s.meaning}", size=12, color=colors["text_sec"])
                            ],
                            spacing=2,
                            expand=True
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=12,
                border_radius=Styles.BORDER_RADIUS_MD,
                border=ft.Border.all(1, colors["border"]),
                bgcolor=colors["card_bg"],
                on_click=lambda e, block=s.block: page.audio_service.play_korean(block),
                animate=150,
            )
        )

    syllables_col = ft.Container(
        content=ft.Column(
            controls=[
                ganada_section,
                numbers_section,
                original_syllables_header,
                *syllable_cards,
                ft.Container(height=12),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=4, vertical=6),
        alignment=ft.Alignment.TOP_CENTER,
    )

    # ─── Abas (Tabs) ───
    tab_headers = [
        ft.Tab(label="Vogais", icon=ft.Icons.FONT_DOWNLOAD_OUTLINED),
        ft.Tab(label="Consoantes", icon=ft.Icons.SPELLCHECK_ROUNDED),
        ft.Tab(label="받침", icon=ft.Icons.LAYERS_ROUNDED),
        ft.Tab(label="Sílabas", icon=ft.Icons.GRID_VIEW_ROUNDED),
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
                    indicator_color=colors["primary"]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        vowels_col,
                        consonants_col,
                        batchim_section,
                        syllables_col,
                    ]
                )
            ]
        )
    )

    # Botão de Teste Fixo Inferior
    quiz_button = ft.Container(
        content=ft.ElevatedButton(
            content="Testar Conhecimentos (Desafio)",
            icon=ft.Icons.QUIZ_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=colors["secondary"],
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                padding=14
            ),
            on_click=lambda e: page.router.navigate_to("/quiz", "unit_intro"),
        ),
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        bgcolor=colors["surface"],
        border=ft.Border.only(top=ft.BorderSide(1, colors["border"])),
    )

    return ft.View(
        route="/hangul",
        appbar=app_bar,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            centered_content(
                page,
                ft.Column(
                            controls=[
                                anti_roman_banner,
                                writing_banner,
                                ft.Container(
                                    content=ft.Text("Toque nos cards para ver detalhes fonéticos e dicas mnemônicas.", size=11, color=colors["text_sec"], italic=True, text_align=ft.TextAlign.CENTER),
                                    padding=ft.Padding.symmetric(horizontal=4, vertical=2),
                                    alignment=ft.Alignment.CENTER,
                                ),
                                tabs,
                            ],
                            expand=True,
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=4),
                expand=True,
            ),
            centered_content(page, quiz_button, alignment=ft.Alignment.CENTER)
        ],
        scroll=None,
        bgcolor=colors["bg"],
        padding=0
    )
