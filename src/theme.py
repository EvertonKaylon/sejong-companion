import flet as ft

class Responsive:
    """Breakpoints e tokens responsivos para adaptar layout por largura de tela.
    
    Alvo mínimo: Galaxy Fold fechado (280px).
    """
    COMPACT = 360   # Telas ultra-estreitas (Galaxy Fold 280px, iPhone SE 320px)
    MEDIUM = 480    # Smartphones padrão
    EXPANDED = 768  # Tablets

    @staticmethod
    def value(width: float, compact, medium=None, expanded=None):
        """Retorna o valor adequado ao breakpoint da largura fornecida.
        
        Exemplo: Responsive.value(page.width, compact=110, medium=140)
        """
        if width < Responsive.COMPACT:
            return compact
        if medium is not None and width < Responsive.MEDIUM:
            return medium
        return expanded if expanded is not None else (medium if medium is not None else compact)

class Colors:
    # ============================================================
    # DESIGN SYSTEM — escalas completas de cor
    # Portadas de design-system/app/globals.css (Next.js + Tailwind v4 + shadcn/ui)
    # ============================================================

    # Primary — Vibrant Violet
    PRIMARY_50 = "#F4F0FE"
    PRIMARY_100 = "#E6DDFD"
    PRIMARY_200 = "#C7B4FD"
    PRIMARY_300 = "#A180FF"
    PRIMARY_400 = "#8E66FF"
    PRIMARY_500 = "#7C4DFF"
    PRIMARY_600 = "#5A1FFF"
    PRIMARY_700 = "#3E00EB"
    PRIMARY_800 = "#3000B8"
    PRIMARY_900 = "#24008A"
    PRIMARY_950 = "#18005C"

    # Neutral
    NEUTRAL_50 = "#FAFAFA"
    NEUTRAL_100 = "#F5F5F5"
    NEUTRAL_200 = "#E7E7E9"
    NEUTRAL_300 = "#D2D1D6"
    NEUTRAL_400 = "#A19EA9"
    NEUTRAL_500 = "#74717F"
    NEUTRAL_600 = "#595661"
    NEUTRAL_700 = "#434149"
    NEUTRAL_800 = "#2D2B31"
    NEUTRAL_900 = "#1A1A1A"
    NEUTRAL_950 = "#02060E"

    # Destructive — Crimson
    DESTRUCTIVE_50 = "#FFF0F4"
    DESTRUCTIVE_100 = "#FED7E1"
    DESTRUCTIVE_200 = "#FEAAC0"
    DESTRUCTIVE_300 = "#FD6890"
    DESTRUCTIVE_400 = "#FC225C"
    DESTRUCTIVE_500 = "#C50337"
    DESTRUCTIVE_600 = "#B00331"
    DESTRUCTIVE_700 = "#920229"
    DESTRUCTIVE_800 = "#740220"
    DESTRUCTIVE_900 = "#550118"
    DESTRUCTIVE_950 = "#32010E"

    # Info — Royal Blue
    INFO_50 = "#EBF3FF"
    INFO_100 = "#CDE2FE"
    INFO_200 = "#96C2FD"
    INFO_300 = "#4F99FC"
    INFO_400 = "#0066CC"
    INFO_600 = "#003B75"
    INFO_700 = "#003366"
    INFO_800 = "#00254B"
    INFO_900 = "#001833"
    INFO_950 = "#000D1F"

    # Success — Accessibility Grade (4.89:1 Contrast)
    SUCCESS_50 = "#EDFDF3"
    SUCCESS_100 = "#D2F9E0"
    SUCCESS_200 = "#A5F3C2"
    SUCCESS_300 = "#62EA94"
    SUCCESS_400 = "#27E26C"
    SUCCESS_500 = "#188150"
    SUCCESS_600 = "#156E44"
    SUCCESS_700 = "#115B38"
    SUCCESS_800 = "#0E482C"
    SUCCESS_900 = "#0B3520"
    SUCCESS_950 = "#072013"

    # Warning
    WARNING_50 = "#FFF8F0"
    WARNING_100 = "#FEECD7"
    WARNING_200 = "#FDD7AB"
    WARNING_300 = "#FBBA6F"
    WARNING_400 = "#FAA038"
    WARNING_500 = "#F88807"
    WARNING_600 = "#D07206"
    WARNING_700 = "#AE5F05"
    WARNING_800 = "#904F04"
    WARNING_900 = "#723F03"
    WARNING_950 = "#4A2902"

    # ============================================================
    # DESIGN SYSTEM SAEBOM COMPANION — PALETA OFICIAL (BRANDING BOOK v3.1)
    #   - NAVY (60% - Território): #02060F (Quietude noturna de foco)
    #   - CREAM / SLATE (20% - Leitura/Estrutura): #F7F4EC / #9EA2AE
    #   - VIOLET (12% - Sistema/Navegação): #8B4DFF (PRIMARY)
    #   - GOLD (8% - Sinal/Atenção/Conquista): #FFAB22 (ACCENT)
    #   - LILAC (Apoio/Companheirismo): #B28AFF (SECONDARY)
    # ============================================================

    # Cores Mestras Saebom
    NAVY = "#02060F"              # Midnight Navy — Território (60%)
    VIOLET = "#8B4DFF"            # Violet — Sistema (12%)
    GOLD = "#FFAB22"              # Gold — Sinal (8%)
    LILAC = "#B28AFF"             # Lilac — Apoio
    CREAM = "#F7F4EC"             # Cream — Leitura / Light BG (10%)
    SLATE = "#9EA2AE"             # Slate — Estrutura e Linhas (10%)

    # Papéis Semânticos Oficiais
    PRIMARY = VIOLET              # #8B4DFF — Sistema, navegação, progresso e botões
    PRIMARY_LIGHT = "#A875FF"
    PRIMARY_DARK = "#5A1FFF"

    SECONDARY = LILAC             # #B28AFF — Companheirismo e elementos complementares
    SECONDARY_LIGHT = "#C7A6FF"
    SECONDARY_DARK = "#7C4DFF"

    ACCENT = GOLD                 # #FFAB22 — Conquistas, sinais de atenção, medalhas e CTAs nobres

    # Paleta Tema Claro (Cream & Slate)
    LIGHT_BG = CREAM              # #F7F4EC
    LIGHT_SURFACE = "#FFFFFF"
    LIGHT_TEXT_PRIMARY = NAVY     # #02060F
    LIGHT_TEXT_SECONDARY = SLATE  # #9EA2AE
    LIGHT_BORDER = "#E7E7E9"
    LIGHT_CARD_BG = "#FFFFFF"

    # Paleta Tema Escuro (Midnight Navy)
    DARK_BG = NAVY                # #02060F
    DARK_SURFACE = "#091122"
    DARK_TEXT_PRIMARY = NEUTRAL_50
    DARK_TEXT_SECONDARY = SLATE   # #9EA2AE
    DARK_BORDER = "#1E293B"
    DARK_CARD_BG = "#0B172E"

    # Cores de Estado e Papel Gramatical (Physics Gating SOV)
    CORRECT = "#188150"          # Verde acessível (4.89:1)
    INCORRECT = DESTRUCTIVE_500  # Carmesim (#C50337)
    NEUTRAL = NEUTRAL_500
    INFO = VIOLET
    WARNING = GOLD

    # Cores Semânticas de Papel Sintático (Sintaxe SOV)
    ROLE_SUBJECT = "#3B82F6"     # Sujeito (Azul)
    ROLE_OBJECT = "#10B981"      # Objeto (Verde Esmeralda)
    ROLE_VERB = "#8B5CF6"        # Verbo (Violeta)
    ROLE_PREDICATE = "#8B5CF6"   # Predicado (Violeta)
    ROLE_PARTICLE = "#F59E0B"    # Partícula (Âmbar)

    # Vitalidade SRS (Retenção Baseada em Meia-Vida)
    VITALITY_HIGH = "#10B981"    # Retenção >= 75% (Esmeralda)
    VITALITY_MEDIUM = "#F59E0B"  # 35% <= Retenção < 75% (Âmbar)
    VITALITY_LOW = "#EF4444"     # Retenção < 35% (Vermelho Urgência)
    VITALITY_NONE = NEUTRAL_500  # Nunca estudada

    # Tripartição Oclusiva (Laboratório Fonético)
    OCLUSIVE_LAX = "#94A3B8"         # Simples (ㅂ, ㄷ, ㄱ): Neutro / Suave
    OCLUSIVE_ASPIRATED = "#38BDF8"   # Aspirada (ㅅ, ㅊ, ㅋ): Expansão Azul Ar
    OCLUSIVE_TENSE = "#EF4444"       # Tensa (ㅃ, ㄸ, ㄲ): Vermelho Tensão Glotal

    # Conectores Metálicos (Fase 2 Interativa)
    CONNECTOR_VOWEL = "#B87333"      # Cobre Metálico
    CONNECTOR_BATCHIM = "#C0C0C0"    # Prata Metálica

class Styles:
    # Conectores Metálicos
    CONNECTOR_VOWEL = Colors.CONNECTOR_VOWEL
    CONNECTOR_BATCHIM = Colors.CONNECTOR_BATCHIM

    # Bordas — escala do design system
    BORDER_RADIUS_SM = 9
    BORDER_RADIUS_MD = 12
    BORDER_RADIUS_LG = 18
    BORDER_RADIUS_PILL = 999

    # Sombras — Formato nativo #AARRGGBB do Flutter Engine
    SHADOW_SM = ft.BoxShadow(
        blur_radius=2,
        color="#0D1A1A1A",
        offset=ft.Offset(0, 1),
    )

    CARD_SHADOW = [
        ft.BoxShadow(
            spread_radius=-2,
            blur_radius=10,
            color="#141A1A1A",
            offset=ft.Offset(0, 4),
        ),
        ft.BoxShadow(
            spread_radius=-2,
            blur_radius=4,
            color="#0A1A1A1A",
            offset=ft.Offset(0, 2),
        ),
    ]

    SHADOW_LG = [
        ft.BoxShadow(
            spread_radius=-6,
            blur_radius=24,
            color="#1F1A1A1A",
            offset=ft.Offset(0, 12),
        ),
        ft.BoxShadow(
            spread_radius=-4,
            blur_radius=8,
            color="#0F1A1A1A",
            offset=ft.Offset(0, 4),
        ),
    ]

    # Brilho violeta (shadow-primary) — #598B4DFF (35% opacidade de Violet #8B4DFF)
    HOVER_SHADOW = ft.BoxShadow(
        spread_radius=-4,
        blur_radius=20,
        color="#598B4DFF",
        offset=ft.Offset(0, 8),
    )

def get_theme_colors(is_dark: bool):
    return {
        "bg": Colors.DARK_BG if is_dark else Colors.LIGHT_BG,
        "surface": Colors.DARK_SURFACE if is_dark else Colors.LIGHT_SURFACE,
        "text": Colors.DARK_TEXT_PRIMARY if is_dark else Colors.LIGHT_TEXT_PRIMARY,
        "text_sec": Colors.DARK_TEXT_SECONDARY if is_dark else Colors.LIGHT_TEXT_SECONDARY,
        "border": Colors.DARK_BORDER if is_dark else Colors.LIGHT_BORDER,
        "card_bg": Colors.DARK_CARD_BG if is_dark else Colors.LIGHT_CARD_BG,
        "primary": Colors.PRIMARY,
        "primary_light": Colors.PRIMARY_LIGHT,
        "secondary": Colors.SECONDARY,
        "secondary_light": Colors.SECONDARY_LIGHT,
        "accent": Colors.ACCENT,
        "correct": Colors.CORRECT,
        "incorrect": Colors.INCORRECT,
        "info": Colors.INFO,
        "warning": Colors.WARNING,
        # Tokens Nomeados do Brand Book Saebom
        "navy": Colors.NAVY,
        "violet": Colors.VIOLET,
        "gold": Colors.GOLD,
        "lilac": Colors.LILAC,
        "cream": Colors.CREAM,
        "slate": Colors.SLATE,
        # Cores Semânticas de Papel Sintático (Sintaxe SOV)
        "role_subject": Colors.ROLE_SUBJECT,
        "role_object": Colors.ROLE_OBJECT,
        "role_verb": Colors.ROLE_VERB,
        "role_predicate": Colors.ROLE_PREDICATE,
        "role_particle": Colors.ROLE_PARTICLE,
        # Vitalidade SRS
        "vitality_high": Colors.VITALITY_HIGH,
        "vitality_medium": Colors.VITALITY_MEDIUM,
        "vitality_low": Colors.VITALITY_LOW,
        "vitality_none": Colors.VITALITY_NONE,
        # Oclusivas
        "oclusive_lax": Colors.OCLUSIVE_LAX,
        "oclusive_aspirated": Colors.OCLUSIVE_ASPIRATED,
        "oclusive_tense": Colors.OCLUSIVE_TENSE,
        # Conectores Metálicos
        "connector_vowel": Colors.CONNECTOR_VOWEL,
        "connector_batchim": Colors.CONNECTOR_BATCHIM,
    }

def apply_app_theme(page: ft.Page):
    from src import __version__
    page.title = f"Saebom Companion v{__version__}"
    page.fonts = {
        "Pretendard": "fonts/Pretendard-Regular.otf",
        "Pretendard-Bold": "fonts/Pretendard-Bold.otf",
        "Kyobo Handwriting": "fonts/KyoboHandwriting2025lyb.otf",
        "Noto Sans KR": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap",
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        "Seollip-che": "fonts/establish_retrosans.ttf",
        "establish Retrosans": "fonts/establish_retrosans.ttf",
    }
    # Configure custom styles
    page.theme = ft.Theme(
        font_family="Pretendard",
        color_scheme_seed=Colors.PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.dark_theme = ft.Theme(
        font_family="Pretendard",
        color_scheme_seed=Colors.PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
