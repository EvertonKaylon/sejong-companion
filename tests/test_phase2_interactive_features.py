"""Testes da Fase 2: Mecânicas Interativas de Neurociência e Conectores Morfofonéticos.

Cobre Fábrica de Sílabas, Teclado Numérico (Dialpad), Diorama Espacial,
tokens metálicos de conectores e silhuetas vetoriais articulatórias.
"""

import os
from types import SimpleNamespace
import pytest
import flet as ft

from src.theme import Styles, Colors
from src.components.hangul_card import HangulCard
from src.components.syllable_factory import SyllableFactory
from src.components.number_training import NumberTraining
from src.components.spatial_stage import SpatialStage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_metallic_connector_tokens():
    """Valida tokens metálicos de conectores para transições de base lisa vs batchim."""
    assert Styles.CONNECTOR_VOWEL == "#B87333", "Conector de terminação vogal deve ser Cobre Metálico (#B87333)"
    assert Styles.CONNECTOR_BATCHIM == "#C0C0C0", "Conector de terminação batchim deve ser Prata Metálica (#C0C0C0)"
    assert Colors.CONNECTOR_VOWEL == "#B87333"
    assert Colors.CONNECTOR_BATCHIM == "#C0C0C0"


def test_mouth_shape_svgs_exist():
    """Valida a existência física de todos os 6 SVGs de silhuetas articulatórias da boca."""
    mouth_dir = os.path.join(BASE_DIR, "assets", "mouth_shapes")
    assert os.path.isdir(mouth_dir), f"Diretório '{mouth_dir}' não encontrado!"

    expected_svgs = [
        "mouth_a.svg",
        "mouth_eo.svg",
        "mouth_eu.svg",
        "mouth_i.svg",
        "mouth_o.svg",
        "mouth_u.svg",
    ]
    for svg_name in expected_svgs:
        svg_path = os.path.join(mouth_dir, svg_name)
        assert os.path.isfile(svg_path), f"Arquivo SVG obrigatório '{svg_name}' não existe em {mouth_dir}!"
        assert os.path.getsize(svg_path) > 100, f"Arquivo SVG '{svg_name}' parece corrompido ou vazio!"


def test_hangul_card_with_mouth_shape():
    """Valida injeção da silhueta articulatória com caminho absoluto '/mouth_shapes/...' no HangulCard."""
    char_data = SimpleNamespace(
        char="ㅏ",
        name="아",
        pronunciation="a (aberta)",
        type="plain",
        mnemonic="Lábios relaxados e língua baixa",
        mouth_shape_id="mouth_a",
    )
    card = HangulCard(char_data, is_dark=True)

    # Localizar controle de imagem da boca nos controles do verso
    found_images = []
    for ctrl in card.detail_col.controls:
        if isinstance(ctrl, ft.Container) and isinstance(ctrl.content, ft.Image):
            found_images.append(ctrl.content)

    assert len(found_images) >= 1, "Card de vogal com mouth_shape_id deve conter ft.Image no verso"
    mouth_img = found_images[0]
    assert mouth_img.src.startswith("/mouth_shapes/"), (
        f"Caminho da imagem '{mouth_img.src}' DEVE começar com '/' para prevenir tela preta no Flutter Web (BUG-11)"
    )
    assert mouth_img.src == "/mouth_shapes/mouth_a.svg"


def test_syllable_factory_composition():
    """Valida síntese Unicode Hangul em tempo real na Fábrica de Sílabas:

    ㄱ + ㅏ = 가 (selo 0.0) -> + ㅇ = 강 (selo 1.0) -> + ㅗ = 공 -> + ㅂ = 봉
    """
    factory = SyllableFactory(is_dark=True)

    # 1. Estado inicial padrão: ㄱ + ㅏ = 가
    assert factory.current_initial == "ㄱ"
    assert factory.current_vowel == "ㅏ"
    assert factory.current_batchim == ""
    assert factory.compose() == "가"
    assert factory.batchim_seal.opacity == 0.0

    # 2. Adicionar batchim ㅇ -> 강 (selo ativo)
    factory.set_batchim("ㅇ")
    assert factory.compose() == "강"
    assert factory.batchim_seal.opacity == 1.0

    # 3. Alterar vogal para ㅗ -> 공
    factory.set_vowel("ㅗ")
    assert factory.compose() == "공"
    assert factory.batchim_seal.opacity == 1.0

    # 4. Alterar consoante inicial para ㅂ -> 봉
    factory.set_initial("ㅂ")
    assert factory.compose() == "봉"
    assert factory.batchim_seal.opacity == 1.0

    # 5. Remover batchim -> 보 (selo inativo)
    factory.set_batchim("")
    assert factory.compose() == "보"
    assert factory.batchim_seal.opacity == 0.0


def test_number_training_dialpad():
    """Valida buffer de digitação de 10 teclas e validação de desafio no NumberTraining."""
    training = NumberTraining(is_dark=True, system="sino")

    assert training.buffer == ""

    # Digitar "1", "2", "3", "4"
    training.press_key("1")
    training.press_key("2")
    training.press_key("3")
    training.press_key("4")
    assert training.buffer == "1234"

    # Verificar desafio com sucesso
    is_ok = training.check_challenge("1234")
    assert is_ok is True
    assert "✅" in training.feedback_text.value

    # Limpar buffer
    training.press_key("C")
    assert training.buffer == ""


def test_spatial_stage_diorama():
    """Valida diorama 2D de postposições espaciais e caminhos canônicos '/spatial/...':"""
    stage = SpatialStage(is_dark=True)

    # Conferir caminhos dos assets
    for ch in stage.challenges:
        assert ch["object_asset"].startswith("/spatial/"), f"Asset {ch['object_asset']} deve começar com '/'"
        assert ch["base_asset"].startswith("/spatial/"), f"Asset {ch['base_asset']} deve começar com '/'"

    # Primeiro desafio (가방 + 책상 -> target: 위)
    assert stage.current_challenge["target_pos"] == "위"

    # Posição incorreta: 아래
    stage.select_position("아래")
    assert "❌" in stage.feedback_text.value

    # Posição correta: 위
    stage.select_position("위")
    assert "✅" in stage.feedback_text.value
