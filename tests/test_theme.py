"""
Testes automatizados para o Design System e tokens de cores do Saebom Companion.
Garante a conformidade dos tokens semânticos com o Branding Book v3.1 oficial.
"""

from unittest.mock import MagicMock
from src.theme import Colors, Styles, get_theme_colors, apply_app_theme
from src import __version__


def test_saebom_master_colors_match_brand_book():
    """Valida as cores mestras oficiais do Brand Book v3.1."""
    assert Colors.NAVY == "#02060F", "Navy deve ser #02060F (60% território)"
    assert Colors.VIOLET == "#8B4DFF", "Violet deve ser #8B4DFF (12% sistema)"
    assert Colors.GOLD == "#FFAB22", "Gold deve ser #FFAB22 (8% sinal)"
    assert Colors.LILAC == "#B28AFF", "Lilac deve ser #B28AFF (apoio)"
    assert Colors.CREAM == "#F7F4EC", "Cream deve ser #F7F4EC (leitura/light)"
    assert Colors.SLATE == "#9EA2AE", "Slate deve ser #9EA2AE (estrutura/linhas)"


def test_saebom_semantic_roles():
    """Valida a atribuição dos papéis semânticos no aplicativo."""
    assert Colors.PRIMARY == Colors.VIOLET, "PRIMARY deve ser Violet (#8B4DFF)"
    assert Colors.SECONDARY == Colors.LILAC, "SECONDARY deve ser Lilac (#B28AFF)"
    assert Colors.ACCENT == Colors.GOLD, "ACCENT deve ser Gold (#FFAB22)"
    assert Colors.DARK_BG == Colors.NAVY, "DARK_BG deve ser Midnight Navy (#02060F)"
    assert Colors.LIGHT_BG == Colors.CREAM, "LIGHT_BG deve ser Cream (#F7F4EC)"


def test_get_theme_colors_dark_mode():
    """Valida o dicionário de cores retornado para o modo escuro."""
    colors = get_theme_colors(is_dark=True)
    assert colors["bg"] == "#02060F"
    assert colors["primary"] == "#8B4DFF"
    assert colors["secondary"] == "#B28AFF"
    assert colors["accent"] == "#FFAB22"
    assert colors["navy"] == "#02060F"
    assert colors["violet"] == "#8B4DFF"
    assert colors["gold"] == "#FFAB22"
    assert colors["lilac"] == "#B28AFF"
    assert colors["cream"] == "#F7F4EC"
    assert colors["slate"] == "#9EA2AE"


def test_get_theme_colors_light_mode():
    """Valida o dicionário de cores retornado para o modo claro."""
    colors = get_theme_colors(is_dark=False)
    assert colors["bg"] == "#F7F4EC"
    assert colors["primary"] == "#8B4DFF"
    assert colors["secondary"] == "#B28AFF"
    assert colors["accent"] == "#FFAB22"
    assert colors["navy"] == "#02060F"
    assert colors["cream"] == "#F7F4EC"


def test_hover_shadow_violet_tint():
    """Valida que a sombra hover utiliza a tonalidade violeta de 35%."""
    assert Styles.HOVER_SHADOW.color == "#598B4DFF"


def test_apply_app_theme_sets_saebom_title():
    """Valida que apply_app_theme atribui o título Saebom Companion à página."""
    mock_page = MagicMock()
    apply_app_theme(mock_page)
    assert f"Saebom Companion v{__version__}" in mock_page.title
    assert "Sejong" not in mock_page.title, "O nome 'Sejong' foi proibido e não deve constar no título da página"
