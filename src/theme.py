import flet as ft

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

    # Info — Sejong Royal Blue
    INFO_50 = "#EBF3FF"
    INFO_100 = "#CDE2FE"
    INFO_200 = "#96C2FD"
    INFO_300 = "#4F99FC"
    INFO_400 = "#0066CC"
    INFO_500 = "#004C97"
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
    # CORES SEMÂNTICAS — Sejong Companion (Rodada 3 Reconciliada)
    #   - PRIMARY: Azul Real Sejong oficial (#004C97) do site da Fundação.
    #   - SECONDARY: Roxo Vibrante do design system (#7C4DFF).
    #   - ACCENT: Dourado Sejong (#F5A623).
    #   - CORRECT: Verde acessível com contraste 4.89:1 (#188150).
    #   - DARK_BG: Midnight Blue (#02060E).
    # ============================================================
    PRIMARY = "#004C97"           # Azul Real Sejong Oficial (세종학당재단)
    PRIMARY_LIGHT = "#0066CC"
    PRIMARY_DARK = "#003366"

    SECONDARY = "#7C4DFF"        # Roxo Vibrante do design system
    SECONDARY_LIGHT = "#9E77FF"

    ACCENT = "#F5A623"           # Dourado Sejong

    # Paleta Tema Claro
    LIGHT_BG = "#FAF9F6"         # Warm Off-White
    LIGHT_SURFACE = "#FFFFFF"
    LIGHT_TEXT_PRIMARY = NEUTRAL_900
    LIGHT_TEXT_SECONDARY = NEUTRAL_500
    LIGHT_BORDER = "#E2E8F0"
    LIGHT_CARD_BG = "#FFFFFF"

    # Paleta Tema Escuro (Midnight Blue)
    DARK_BG = "#02060E"
    DARK_SURFACE = "#091122"
    DARK_TEXT_PRIMARY = NEUTRAL_50
    DARK_TEXT_SECONDARY = NEUTRAL_400
    DARK_BORDER = "#1E293B"
    DARK_CARD_BG = "#0B172E"

    # Cores de Estado e Papel Gramatical (Physics Gating SOV)
    CORRECT = "#188150"          # Verde acessível (4.89:1)
    INCORRECT = DESTRUCTIVE_500  # Carmesim (#C50337)
    NEUTRAL = NEUTRAL_500
    INFO = PRIMARY
    WARNING = WARNING_500

    # Cores Semânticas de Papel Sintático (Sintaxe SOV)
    ROLE_SUBJECT = "#3B82F6"     # Sujeito (Azul)
    ROLE_OBJECT = "#10B981"      # Objeto (Verde Esmeralda)
    ROLE_VERB = "#8B5CF6"        # Verbo (Violeta)
    ROLE_PREDICATE = "#8B5CF6"   # Predicado (Violeta)
    ROLE_PARTICLE = "#F59E0B"    # Partícula (Âmbar)

class Styles:
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

    # Brilho azul (shadow-primary) — #59004C97 (35% opacidade de #004C97)
    HOVER_SHADOW = ft.BoxShadow(
        spread_radius=-4,
        blur_radius=20,
        color="#59004C97",
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
        "role_subject": Colors.ROLE_SUBJECT,
        "role_object": Colors.ROLE_OBJECT,
        "role_verb": Colors.ROLE_VERB,
        "role_predicate": Colors.ROLE_PREDICATE,
        "role_particle": Colors.ROLE_PARTICLE,
    }

def apply_app_theme(page: ft.Page):
    from src import __version__
    page.title = f"Sejong Companion v{__version__}"
    page.fonts = {
        "Pretendard": "fonts/Pretendard-Regular.otf",
        "Pretendard-Regular": "fonts/Pretendard-Regular.otf",
        "Pretendard-Medium": "fonts/Pretendard-Medium.otf",
        "Pretendard-SemiBold": "fonts/Pretendard-SemiBold.otf",
        "Pretendard-Bold": "fonts/Pretendard-Bold.otf",
        "Pretendard-ExtraBold": "fonts/Pretendard-ExtraBold.otf",
        "Pretendard-Black": "fonts/Pretendard-Black.otf",
        "PretendardVariable": "fonts/PretendardVariable.ttf",
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
