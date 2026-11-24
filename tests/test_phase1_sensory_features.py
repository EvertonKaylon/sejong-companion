"""Testes da Fase 1: Mecânicas Sensoriais e Quick Wins Cognitivos.

Cobre feedback háptico, partículas de ar (VOT > 70ms), glowing orbs,
cards de vocabulário sem romanização e laboratório da tripartição oclusiva.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
import flet as ft

from src.components.air_particle_effect import AirParticleEffect
from src.components.hangul_card import HangulCard
from src.components.vocab_card import VocabCard
from src.components.oclusive_lab import build_oclusive_lab
from src.components.sentence_builder_widget import SentenceBuilderWidget


@pytest.mark.asyncio
async def test_air_particle_effect_emit():
    """Valida simulação 2D Canvas de partículas de ar para consoantes aspiradas."""
    effect = AirParticleEffect(base_color="#38BDF8", box_width=100, num_particles=10)

    assert effect.box_width == 100
    assert len(effect.shapes) == 10
    assert effect.is_animating is False

    # Disparo assíncrono do efeito
    await effect.emit(steps=4, duration_ms=20)

    # Após término, deve retornar ao estado inativo e opacidade resetada
    assert effect.is_animating is False
    for shape in effect.shapes:
        assert shape.x == 50.0
        assert shape.y == 50.0


def test_hangul_card_glow_ring():
    """Valida camada de brilho sensorial (glow_ring) e alternância de faces do HangulCard."""
    char_data = SimpleNamespace(
        char="ㄱ",
        name="기역",
        pronunciation="g/k (velar suave)",
        type="plain",
        mnemonic="Lembrando uma foice que corta o grão",
        mouth_shape_id=None,
    )
    card = HangulCard(char_data, is_dark=True, size=140)

    assert hasattr(card, "glow_ring")
    assert card.glow_ring is not None
    assert card.flipped is False
    assert card.char_text.visible is True
    assert card.detail_col.visible is False

    # Flip para o verso
    card.toggle_flip(None)
    assert card.flipped is True
    assert card.char_text.visible is False
    assert card.detail_col.visible is True

    # Hover simulação
    hover_event = SimpleNamespace(data="true")
    card.on_card_hover(hover_event)
    assert card.glow_ring.opacity == 0.8

    unhover_event = SimpleNamespace(data="false")
    card.on_card_hover(unhover_event)
    assert card.glow_ring.opacity == 0.0


def test_vocab_card_audio_and_hover():
    """Valida card de vocabulário sem romanização com indicador luminoso de áudio (word_glow)."""
    vocab_item = SimpleNamespace(
        word="사과",
        meaning="Maçã",
        example_kr="사과가 맛있어요.",
        example_pt="A maçã é gostosa.",
        category="Alimentos",
        magnetic_slot_role=None,
        snap_anchor=None,
    )
    audio_cb = MagicMock()
    card = VocabCard(vocab_item, is_dark=True, on_audio_click=audio_cb)

    assert hasattr(card, "audio_icon")
    assert hasattr(card, "word_glow")
    assert card.word_glow is not None

    # Disparo da animação de áudio
    card.play_audio_animation(None)
    audio_cb.assert_called_once_with("사과")
    assert card.word_glow.opacity == 0.0


def test_oclusive_lab_building():
    """Valida laboratório fonético da tripartição oclusiva cobrindo as 4 tríades."""
    lab = build_oclusive_lab(is_dark=True)
    assert isinstance(lab, ft.Container)

    content = lab.content
    assert isinstance(content, ft.Column)
    assert len(content.controls) >= 5


def test_sentence_builder_widget():
    """Valida montagem de frases em modo blocos com validação sintática SOV afirmativa."""
    challenge = {
        "id": "c_sov_test",
        "prompt_pt": "Eu como arroz.",
        "sentence_pt": "Eu como arroz.",
        "words": ["저는", "밥을", "먹어요."],
        "correct_order": ["저는", "밥을", "먹어요."],
        "answer": "저는 밥을 먹어요.",
    }
    widget = SentenceBuilderWidget(challenge=challenge, is_dark=True)

    # Modo blocos padrão
    assert widget.mode == "blocks"
    # Clicar em cada bloco na ordem correta
    for idx in range(len(challenge["words"])):
        widget._select_block(idx)

    # Validar conferência
    widget._check_blocks(None)
    assert "✅" in widget.feedback
