import pytest
import os
import json
from src.services import DataService, ProgressService
from src.models import UnitData, QuizQuestion

def test_all_1b_units_load_and_validate():
    """Valida que todas as 12 unidades do Sejong 1B existem e seguem o schema Pydantic."""
    unit_ids = [f"unit_1b_{i:02d}" for i in range(1, 13)]
    assert len(unit_ids) == 12

    for u_id in unit_ids:
        unit = DataService.get_unit(u_id)
        assert unit is not None, f"Falha ao carregar unidade {u_id}"
        assert isinstance(unit, UnitData)
        assert unit.unit_id == u_id
        assert len(unit.title) > 0

        # Validação de vocabulário
        assert len(unit.vocabulary) >= 8, f"Unidade {u_id} com vocabulário insuficiente ({len(unit.vocabulary)})"
        for v in unit.vocabulary:
            assert v.word and len(v.word) > 0
            assert v.meaning and len(v.meaning) > 0
            assert v.example_kr and len(v.example_kr) > 0
            assert v.example_pt and len(v.example_pt) > 0
            assert v.snap_anchor in ("square", "round", None)
            assert v.magnetic_slot_role in ("SUBJECT", "OBJECT", "VERB", "PARTICLE", "PREDICATE", "LOCATION", None)

        # Validação de gramática
        assert len(unit.grammar) == 2, f"Unidade {u_id} deve conter exatamente 2 seções gramaticais"
        for g in unit.grammar:
            assert g.title and len(g.title) > 0
            assert g.explanation and len(g.explanation) > 0
            assert len(g.examples) >= 1
            for ex in g.examples:
                assert ex.kr and ex.pt
            assert g.lusophone_tip and len(g.lusophone_tip) > 0

        # Validação de notas culturais
        assert len(unit.cultural_notes) >= 1, f"Unidade {u_id} sem nota cultural"
        for c in unit.cultural_notes:
            assert c.title and c.content and c.icon

        # Validação de exercícios (Workbook)
        assert len(unit.exercises) >= 3, f"Unidade {u_id} com poucos exercícios"
        has_mc = False
        has_order = False
        has_sov = False
        for ex in unit.exercises:
            assert isinstance(ex, QuizQuestion)
            if ex.type == "multiple_choice":
                has_mc = True
                assert ex.options and len(ex.options) >= 3
                assert ex.correct_index is not None
                assert 0 <= ex.correct_index < len(ex.options)
            elif ex.type == "order_words":
                has_order = True
                assert ex.words and ex.correct_order
                assert sorted(ex.words) == sorted(ex.correct_order)
            elif ex.type == "drag_and_drop_sov":
                has_sov = True
                assert ex.sov_items and ex.sov_slots
                assert len(ex.sov_items) == len(ex.sov_slots)
                assert ex.correct_order
                assert sorted(i.word for i in ex.sov_items) == sorted(ex.correct_order)

        assert has_mc, f"Unidade {u_id} deve ter questão de múltipla escolha"
        assert has_order or has_sov, f"Unidade {u_id} deve ter questão de ordenação ou SOV"

def test_curriculum_contains_1b_units():
    """Valida que o curriculum.json tem todas as 12 unidades do 1B registradas."""
    curriculum = DataService.get_curriculum()
    unit_ids = [u.id for u in curriculum]

    assert "unit_intro" in unit_ids
    for i in range(1, 11):
        assert f"unit_{i:02d}" in unit_ids
    for i in range(1, 13):
        assert f"unit_1b_{i:02d}" in unit_ids

    # Total: 1 (intro) + 10 (1A) + 12 (1B) = 23 unidades
    assert len(curriculum) == 23

def test_unlock_chain_from_1a_to_1b(tmp_path):
    """Valida a progressão contínua da unit_10 para a unit_1b_01 até a unit_1b_12."""
    session_file = str(tmp_path / "student_test_1b.json")
    ProgressService._file_path_override = session_file
    ProgressService._sessions.clear()

    svc = ProgressService(None)

    # 1. unit_intro e unit_01 desbloqueadas por padrão
    assert svc.is_unlocked("unit_intro") is True
    assert svc.is_unlocked("unit_01") is True
    assert svc.is_unlocked("unit_10") is False
    assert svc.is_unlocked("unit_1b_01") is False

    # 2. Concluir unit_09 desbloqueia unit_10
    svc.save_progress("unit_09", 1.0)
    assert svc.is_unlocked("unit_10") is True
    assert svc.is_unlocked("unit_1b_01") is False

    # 3. Concluir unit_10 (final do 1A) desbloqueia unit_1b_01 (início do 1B)
    svc.save_progress("unit_10", 1.0)
    assert svc.is_unlocked("unit_1b_01") is True
    assert svc.is_unlocked("unit_1b_02") is False

    # 4. Cadeia interna do 1B
    for i in range(1, 12):
        curr_id = f"unit_1b_{i:02d}"
        next_id = f"unit_1b_{i+1:02d}"
        svc.save_progress(curr_id, 1.0)
        assert svc.is_unlocked(next_id) is True, f"Falha ao desbloquear {next_id} após completar {curr_id}"

    # Limpeza
    ProgressService._file_path_override = None
    ProgressService._sessions.clear()

def test_flashcards_include_1b_units():
    """Valida que get_all_flashcards inclui vocabulário do 1B."""
    cards = DataService.get_all_flashcards()
    unit_ids_in_cards = {c.unit_id for c in cards}

    for i in range(1, 13):
        assert f"unit_1b_{i:02d}" in unit_ids_in_cards

    # Vocabulário total expandido (deve ter mais de 150 cartões)
    assert len(cards) >= 150

def test_audio_texts_include_1b_units():
    """Valida que get_all_audio_texts inclui textos do 1B."""
    audio_texts = DataService.get_all_audio_texts()
    assert len(audio_texts) >= 150
    # Verifica termos marcantes do 1B
    assert "불고기" in audio_texts
    assert "제주도" in audio_texts
    assert "기타를 치다" in audio_texts or "기타를 칠 수 있어요?" in audio_texts or "축하하다" in audio_texts
