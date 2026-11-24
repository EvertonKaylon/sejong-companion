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


def test_number_training_native_mode_and_free_ok_playback():
    """Valida modo nativo (0, 10, compostos 10-99, >99/zeros à esquerda) e OK em modo livre."""
    spoken = []
    training = NumberTraining(
        is_dark=True,
        system="sino",
        on_complete=lambda txt: spoken.append(txt),
    )

    # Alternância visual de sistema
    training.set_system("native")
    assert training.system == "native"
    sino_btn, native_btn = training.system_selector.controls
    assert native_btn.style.bgcolor == training.colors["primary"]
    assert sino_btn.style.bgcolor == training.colors["surface"]

    # 0 -> 영
    training.press_key("0")
    assert training.translation_text.value == "영"

    # 10 -> 열
    training.press_key("C")
    training.press_key("1")
    training.press_key("0")
    assert training.translation_text.value == "열"

    # 11 -> 열하나
    training.press_key("C")
    training.press_key("1")
    training.press_key("1")
    assert training.translation_text.value == "열하나"

    # 20 -> 스물
    training.press_key("C")
    training.press_key("2")
    training.press_key("0")
    assert training.translation_text.value == "스물"

    # 25 -> 스물다섯 e OK em modo livre chama on_complete
    training.press_key("C")
    training.press_key("2")
    training.press_key("5")
    assert training.translation_text.value == "스물다섯"
    training.press_key("OK")
    assert training.feedback_text.value == "🔊 스물다섯"
    assert spoken == ["스물다섯"]

    # Zeros à esquerda e >= 100 permanecem dígito-a-dígito
    training.press_key("C")
    training.press_key("0")
    training.press_key("5")
    assert training.translation_text.value == "영 다섯"

    training.press_key("C")
    training.press_key("1")
    training.press_key("2")
    training.press_key("3")
    assert training.translation_text.value == "하나 둘 셋"


def test_spatial_stage_diorama():
    """Valida diorama 2D de postposições espaciais, movimentação de object_img e next_challenge."""
    stage = SpatialStage(is_dark=True)

    # Conferir caminhos dos assets
    for ch in stage.challenges:
        assert ch["object_asset"].startswith("/spatial/"), f"Asset {ch['object_asset']} deve começar com '/'"
        assert ch["base_asset"].startswith("/spatial/"), f"Asset {ch['base_asset']} deve começar com '/'"

    # Validar que object_container (com object_img) está dentro do ft.Stack
    stacks = []
    def find_stacks(ctrl):
        if isinstance(ctrl, ft.Stack):
            stacks.append(ctrl)
        if hasattr(ctrl, "controls") and isinstance(ctrl.controls, list):
            for c in ctrl.controls:
                find_stacks(c)
        elif hasattr(ctrl, "content") and ctrl.content:
            find_stacks(ctrl.content)

    find_stacks(stage)
    assert len(stacks) == 1
    assert stage.object_container in stacks[0].controls
    assert stage.object_container.content is stage.object_img

    initial_pos = (stage.object_container.top, stage.object_container.left)

    # Primeiro desafio (가방 + 책상 -> target: 위)
    assert stage.current_challenge["target_pos"] == "위"

    # Posição incorreta: 아래 (deve mover o objeto para a coordenada de 아래)
    stage.select_position("아래")
    assert "❌" in stage.feedback_text.value
    assert (stage.object_container.top, stage.object_container.left) == SpatialStage.POSITION_COORDS["아래"]

    # Posição correta: 위 (deve mover o objeto para 위)
    stage.select_position("위")
    assert "✅" in stage.feedback_text.value
    assert (stage.object_container.top, stage.object_container.left) == SpatialStage.POSITION_COORDS["위"]

    # Botão Próximo Desafio deve avançar e resetar posição
    assert hasattr(stage, "next_btn") and isinstance(stage.next_btn, ft.Button)
    stage.next_btn.on_click(None)
    assert stage.current_idx == 1
    assert stage.feedback_text.value == ""
    assert (stage.object_container.top, stage.object_container.left) == initial_pos


def test_lesson_view_spatial_stage_plays_audio_on_completion():
    """Valida que SpatialStage na unit_03 dispara play_korean(prompt_kr) ao acertar posição."""
    from src.views.lesson_view import lesson_view
    from src.router import Router

    played = []

    class MockAudio:
        def play_korean(self, text):
            played.append(text)

    class MockPage:
        def __init__(self, audio_service=None):
            self.theme_mode = ft.ThemeMode.DARK
            self.width = 400
            self.views = []
            self.overlay = []
            self.services = []
            self.client_storage = None
            self.audio_service = audio_service

        def update(self):
            pass

        def run_task(self, fn, *args, **kwargs):
            pass

    def find_spatial(ctrl):
        if isinstance(ctrl, SpatialStage):
            return ctrl
        if hasattr(ctrl, "controls") and isinstance(ctrl.controls, list):
            for ch in ctrl.controls:
                res = find_spatial(ch)
                if res is not None:
                    return res
        if hasattr(ctrl, "content") and ctrl.content:
            return find_spatial(ctrl.content)
        return None

    page = MockPage(audio_service=MockAudio())
    page.router = Router(page)
    page.router.current_unit_id = "unit_03"
    view = lesson_view(page)

    spatial = find_spatial(view)
    assert spatial is not None
    spatial.select_position(spatial.current_challenge["target_pos"])
    assert played == [spatial.current_challenge["prompt_kr"]]

    # Sem audio_service não deve levantar exceção
    page_no_audio = MockPage(audio_service=None)
    page_no_audio.router = Router(page_no_audio)
    page_no_audio.router.current_unit_id = "unit_03"
    view_no_audio = lesson_view(page_no_audio)
    spatial_no_audio = find_spatial(view_no_audio)
    assert spatial_no_audio is not None
    spatial_no_audio.select_position(spatial_no_audio.current_challenge["target_pos"])
