"""
Testes automatizados para verificação do pacote de assets de branding Saebom Companion.
Garante que todos os arquivos vetoriais e rasterizados foram gerados, possuem tamanho > 0
e estão em conformidade com as dimensões esperadas pelo Branding Book v3.1.
"""

import os
import pytest
from PIL import Image

BRANDING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "branding")

EXPECTED_FILES = [
    "saebom_logo_dark.svg",
    "saebom_logo_dark.png",
    "saebom_logo_dark_solid.png",
    "saebom_logo_light.svg",
    "saebom_logo_light.png",
    "saebom_logo_light_solid.png",
    "saebom_logo_horizontal_dark.svg",
    "saebom_logo_horizontal_dark.png",
    "saebom_logo_horizontal_dark_solid.png",
    "saebom_logo_horizontal_light.svg",
    "saebom_logo_horizontal_light.png",
    "saebom_logo_horizontal_light_solid.png",
    "symbol_expansion_rings.svg",
    "symbol_expansion_rings.png",
    "app_icon.svg",
    "app_icon_512.png",
    "app_icon_192.png",
    "favicon_32.png",
    "favicon_16.png",
    "favicon.ico",
    "splash_banner.png",
]


def test_branding_directory_exists():
    """Verifica se o diretório de branding existe no repositório."""
    assert os.path.isdir(BRANDING_DIR), f"Diretório {BRANDING_DIR} não encontrado."


@pytest.mark.parametrize("filename", EXPECTED_FILES)
def test_each_branding_asset_exists_and_non_empty(filename):
    """Verifica se cada arquivo esperado existe e não está vazio (size > 0)."""
    file_path = os.path.join(BRANDING_DIR, filename)
    assert os.path.isfile(file_path), f"Asset {filename} não foi encontrado."
    assert os.path.getsize(file_path) > 0, f"Asset {filename} está vazio."


def test_app_icon_dimensions():
    """Verifica se os app icons gerados possuem exatamente as dimensões esperadas."""
    icon_512 = Image.open(os.path.join(BRANDING_DIR, "app_icon_512.png"))
    assert icon_512.size == (512, 512), f"app_icon_512.png tem tamanho {icon_512.size}"

    icon_192 = Image.open(os.path.join(BRANDING_DIR, "app_icon_192.png"))
    assert icon_192.size == (192, 192), f"app_icon_192.png tem tamanho {icon_192.size}"

    fav_32 = Image.open(os.path.join(BRANDING_DIR, "favicon_32.png"))
    assert fav_32.size == (32, 32), f"favicon_32.png tem tamanho {fav_32.size}"

    fav_16 = Image.open(os.path.join(BRANDING_DIR, "favicon_16.png"))
    assert fav_16.size == (16, 16), f"favicon_16.png tem tamanho {fav_16.size}"


def test_splash_banner_dimensions():
    """Verifica se o splash banner mobile tem resolução Full HD vertical (1080x1920)."""
    banner = Image.open(os.path.join(BRANDING_DIR, "splash_banner.png"))
    assert banner.size == (1080, 1920), f"splash_banner.png tem tamanho {banner.size}"


def test_svg_content_validity():
    """Verifica se os arquivos SVG contêm as tags e cores mínimas exigidas pelo Brand Book."""
    dark_svg = os.path.join(BRANDING_DIR, "saebom_logo_dark.svg")
    with open(dark_svg, "r", encoding="utf-8") as f:
        content = f.read()
        assert "<svg" in content
        assert "새봄" in content
        assert "COMPANION" in content
        assert "#FFAB22" in content  # Gold
