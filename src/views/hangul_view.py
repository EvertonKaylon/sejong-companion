import flet as ft
from ..theme import get_theme_colors, Styles
from ..services import DataService, FullscreenService
from ..components.hangul_card import HangulCard

def hangul_view(page: ft.Page) -> ft.View:
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    colors = get_theme_colors(is_dark)

    # Carregar dados do Hangul
    data = DataService.get_unit_intro()
    if not data:
        return ft.View(
            route="/hangul",
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
                            ft.Text(notice.icon, size=24),
                            ft.Text(notice.title, size=14, weight=ft.FontWeight.BOLD, color=colors["incorrect"]),
                        ],
                        spacing=8,
                    ),
                    ft.Text(notice.content, size=12, color=colors["text_sec"]),
                ],
                spacing=6,
            ),
            padding=14,
            bgcolor="#0DC50337",
            border=ft.Border.all(1, "#33C50337"),
            border_radius=Styles.BORDER_RADIUS_MD,
            margin=ft.Margin.only(left=16, right=16, top=10, bottom=6),
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
                            ft.Text(wa.icon, size=24),
                            ft.Text(wa.title, size=14, weight=ft.FontWeight.BOLD, color=colors["secondary"]),
                        ],
                        spacing=8,
                    ),
                    ft.Text(wa.content, size=12, color=colors["text_sec"]),
                ],
                spacing=6,
            ),
            padding=14,
            bgcolor="#0D188150",
            border=ft.Border.all(1, "#33188150"),
            border_radius=Styles.BORDER_RADIUS_MD,
            margin=ft.Margin.only(left=16, right=16, bottom=6),
        )

    # ─── Grid de Vogais ───
    vowels_wrap = ft.Row(
        controls=[HangulCard(v, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w)) for v in data.vowels],
        spacing=10,
        run_spacing=10,
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # ─── Grid de Consoantes Planas ───
    consonants_wrap = ft.Row(
        controls=[HangulCard(c, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w)) for c in data.consonants],
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
                    ),
                    margin=ft.Margin.only(bottom=8),
                ),
                ft.Text("Produzidas com sopro forte de ar. Coloque a mão na frente da boca para sentir!", size=12, color=colors["text_sec"]),
                ft.Container(height=8),
                ft.Row(
                    controls=[HangulCard(c, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w)) for c in data.aspirated_consonants],
                    spacing=10,
                    run_spacing=10,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
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
                    ),
                    margin=ft.Margin.only(bottom=8),
                ),
                ft.Text("Produzidas com tensão na garganta, SEM sopro de ar. Essa distinção não existe no português!", size=12, color=colors["text_sec"]),
                ft.Container(height=8),
                ft.Row(
                    controls=[HangulCard(c, is_dark, on_audio_click=lambda w: page.audio_service.play_korean(w)) for c in data.tense_consonants],
                    spacing=10,
                    run_spacing=10,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

    # ─── 받침 Guide ───
    batchim_section = ft.Container()
    if data.batchim_guide:
        bg = data.batchim_guide
        
        batchim_controls = [
            ft.Text(bg.title, size=18, weight=ft.FontWeight.BOLD, color=colors["primary"]),
            ft.Container(height=6),
            ft.Text(bg.explanation, size=13, color=colors["text_sec"]),
            ft.Container(height=12),
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
                                    ft.Text(lw.icon, size=28),
                                    ft.Text(lw.title, size=14, weight=ft.FontWeight.BOLD, color=colors["incorrect"]),
                                ],
                                spacing=8,
                            ),
                            ft.Container(height=4),
                            ft.Text(lw.content, size=12, color=colors["text"]),
                        ],
                        spacing=4,
                    ),
                    padding=14,
                    bgcolor="#0DC50337",
                    border=ft.Border.all(1, "#33C50337"),
                    border_radius=Styles.BORDER_RADIUS_MD,
                    margin=ft.Margin.only(bottom=12),
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
                    padding=10,
                    bgcolor=colors["card_bg"],
                    border=ft.Border.all(1, colors["border"]),
                    border_radius=Styles.BORDER_RADIUS_SM,
                    margin=ft.Margin.only(bottom=8),
                )
            )

        batchim_section = ft.Column(controls=batchim_controls, scroll=ft.ScrollMode.AUTO, expand=True)

    # ─── Lista de Sílabas ───
    syllables_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    for s in data.syllables:
        syllables_col.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(s.block, size=24, weight=ft.FontWeight.BOLD, color=colors["primary"]),
                            bgcolor=colors["surface"],
                            border=ft.Border.all(1, colors["border"]),
                            border_radius=Styles.BORDER_RADIUS_SM,
                            width=60,
                            height=60,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(f"Composição: {s.spelling}", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                ft.Text(f"Significado: {s.meaning}", size=12, color=colors["text_sec"])
                            ],
                            spacing=2,
                            expand=True
                        )
                    ],
                ),
                padding=12,
                border_radius=Styles.BORDER_RADIUS_MD,
                border=ft.Border.all(1, colors["border"]),
                bgcolor=colors["card_bg"],
            )
        )

    # ─── Abas (Tabs) ───
    tab_headers = [
        ft.Tab(label="Vogais", icon=ft.Icons.FONT_DOWNLOAD_OUTLINED),
        ft.Tab(label="Consoantes", icon=ft.Icons.SPELLCHECK_ROUNDED),
        ft.Tab(label="받침", icon=ft.Icons.LAYERS_ROUNDED),
        ft.Tab(label="Sílabas", icon=ft.Icons.GRID_VIEW_ROUNDED),
    ]

    vowels_col = ft.Column(
        controls=[vowels_wrap],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    consonants_col = ft.Column(
        controls=[
            ft.Text("Consoantes Planas (기본)", size=15, weight=ft.FontWeight.BOLD, color=colors["text"]),
            ft.Container(height=8),
            consonants_wrap,
            aspirated_section,
            tense_section,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        height=620,  # Altura fixa para se integrar perfeitamente a view scrollavel
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

    # Botão de Teste
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
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=colors["surface"],
        border=ft.Border.only(top=ft.BorderSide(1, colors["border"])),
    )

    return ft.View(
        route="/hangul",
        appbar=app_bar,
        controls=[
            anti_roman_banner,
            writing_banner,
            ft.Container(
                content=ft.Text("Toque nos cards para ver detalhes fonéticos e dicas mnemônicas.", size=12, color=colors["text_sec"], italic=True),
                padding=ft.Padding.only(left=16, right=16, top=4, bottom=4)
            ),
            tabs,
            quiz_button
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=colors["bg"]
    )
