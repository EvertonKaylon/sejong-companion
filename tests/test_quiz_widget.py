"""Testes do QuizWidget: SOV drag-and-drop, múltipla escolha e ordenação de palavras.

Cobre fidelidade curricular (todos os tipos de questão e todas as unidades),
tolerância a índice 0 (truthiness de 0 vs None), physics gate sintático,
liberação de slots, fiação de botões e ciclos de resposta completos.
"""

from types import SimpleNamespace
from typing import List, Tuple
import pytest
import flet as ft

from src.models import QuizQuestion, is_role_accepted
from src.components.quiz_widget import QuizWidget
from src.services import DataService


class MockPage:
    """Mock leve de ft.Page para testes unitários headless de drag-and-drop."""

    def __init__(self):
        self._controls = {}

    def get_control(self, cid: str):
        return self._controls.get(cid)

    def run_task(self, target, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


def _load_curriculum_questions() -> Tuple[List[QuizQuestion], List[QuizQuestion], List[QuizQuestion]]:
    """Carrega todas as questões de quiz de todas as unidades curriculares oficiais."""
    sov_questions = []
    mc_questions = []
    ow_questions = []

    for unit_id in DataService._get_all_unit_ids():
        unit = DataService.get_unit(unit_id)
        questions = getattr(unit, "exercises", None) or getattr(unit, "quiz", None) or []
        for q in questions:
            if q.type == "drag_and_drop_sov":
                sov_questions.append(q)
            elif q.type == "multiple_choice":
                mc_questions.append(q)
            elif q.type == "order_words":
                ow_questions.append(q)

    return sov_questions, mc_questions, ow_questions


SOV_QUESTIONS, MC_QUESTIONS, OW_QUESTIONS = _load_curriculum_questions()


def test_curriculum_has_all_three_question_types():
    """Valida que o currículo oficial contém os 3 tipos de questão de quiz."""
    found_types = set()
    for unit_id in DataService._get_all_unit_ids():
        unit = DataService.get_unit(unit_id)
        questions = getattr(unit, "exercises", None) or getattr(unit, "quiz", None) or []
        for q in questions:
            found_types.add(q.type)

    assert "multiple_choice" in found_types, "Currículo deve conter questões de múltipla escolha"
    assert "order_words" in found_types, "Currículo deve conter questões de ordenação de palavras"
    assert "drag_and_drop_sov" in found_types, "Currículo deve conter questões de drag-and-drop SOV"
    assert len(SOV_QUESTIONS) >= 40, f"Esperado pelo menos 40 questões SOV, encontrado {len(SOV_QUESTIONS)}"
    assert len(MC_QUESTIONS) >= 30, f"Esperado pelo menos 30 questões MC, encontrado {len(MC_QUESTIONS)}"
    assert len(OW_QUESTIONS) >= 12, f"Esperado pelo menos 12 questões OW, encontrado {len(OW_QUESTIONS)}"


@pytest.mark.parametrize("sov_q", SOV_QUESTIONS, ids=[q.id for q in SOV_QUESTIONS])
def test_every_sov_question_builds_and_completes(sov_q: QuizQuestion):
    """Valida que cada questão SOV monta corretamente e completa o ciclo de verificação."""
    next_called = False
    answer_result = None

    def on_next():
        nonlocal next_called
        next_called = True

    def on_answer(is_correct, elapsed_ms=0):
        nonlocal answer_result
        answer_result = is_correct

    widget = QuizWidget(question_data=sov_q, is_dark=True, on_next=on_next, on_answer=on_answer)

    # Verificar construção dos slots e drag sources
    assert len(widget.sov_slot_containers) == len(sov_q.sov_slots)
    assert len(widget.sov_items) == len(sov_q.sov_items)
    assert widget.sov_check_btn.disabled is True

    # Preencher todos os slots com as palavras na ordem correta
    for slot_idx, slot_def in enumerate(widget.sov_slot_definitions):
        target_word = widget.sov_correct_order[slot_idx]
        item_id = next(
            i_id for i_id, item in widget.sov_items_by_id.items()
            if item.word == target_word and i_id not in widget.sov_slots
        )
        widget.sov_slots[slot_idx] = item_id
        widget._sov_render_filled_slot(slot_idx, item_id)

    widget._refresh_sov_drag_sources()
    widget.sov_check_btn.disabled = any(s is None for s in widget.sov_slots)

    assert widget.sov_check_btn.disabled is False
    assert len(widget.sov_drag_row.controls) == 0

    # Executar verificação
    widget._sov_check_order(None)

    assert widget.answered is True
    assert answer_result is True
    assert widget.explanation_container.visible is True
    assert widget.next_button.visible is True

    widget.handle_next(None)
    assert next_called is True


def test_sov_drag_index_zero_is_not_treated_as_falsy():
    """Valida correção de regressão: item com índice 0 não deve ser tratado como falsy."""
    assert len(SOV_QUESTIONS) > 0, "Deve haver ao menos uma questão SOV no currículo"
    sov_q = SOV_QUESTIONS[0]

    widget = QuizWidget(question_data=sov_q, is_dark=True, on_next=lambda: None, on_answer=lambda c, t=0: None)
    mock_page = MockPage()
    widget._page = mock_page

    # O item com chave 0 em sov_items_by_id
    item_0 = widget.sov_items_by_id[0]

    # Encontrar um slot compatível com o papel de item_0
    compatible_slot_idx = next(
        idx for idx, slot_def in enumerate(widget.sov_slot_definitions)
        if is_role_accepted(item_0.role, slot_def.accepted_roles)
    )

    # Registrar controle de drag correspondente ao item 0
    drag_control = SimpleNamespace(data="0")
    mock_page._controls["drag_src_0"] = drag_control

    # Simular drop no slot compatível
    drop_event = SimpleNamespace(src_id="drag_src_0")
    widget._sov_on_accept(drop_event, slot_idx=compatible_slot_idx)

    # Deve ter aceito e gravado o número inteiro 0 (e não ignorado por ser falsy)
    assert widget.sov_slots[compatible_slot_idx] == 0
    assert widget.sov_slots[compatible_slot_idx] is not None

    # Liberar o slot 0 deve funcionar (não retornar prematuramente por if not self.sov_slots[idx])
    widget._sov_release_slot(compatible_slot_idx)
    assert widget.sov_slots[compatible_slot_idx] is None


def test_sov_incompatible_drop_is_rejected_not_crashed():
    """Valida que drop de item com papel sintático incompatível é rejeitado sem colapsar o widget."""
    assert len(SOV_QUESTIONS) > 0
    sov_q = SOV_QUESTIONS[0]

    widget = QuizWidget(question_data=sov_q, is_dark=True, on_next=lambda: None, on_answer=lambda c, t=0: None)
    mock_page = MockPage()
    widget._page = mock_page

    # Localizar um par (item, slot) comprovadamente incompatível
    incompatible_pair = None
    for item_id, item in widget.sov_items_by_id.items():
        for slot_idx, slot_def in enumerate(widget.sov_slot_definitions):
            if not is_role_accepted(item.role, slot_def.accepted_roles):
                incompatible_pair = (item_id, item, slot_idx)
                break
        if incompatible_pair:
            break

    assert incompatible_pair is not None, "Deve existir ao menos um par item-slot incompatível para testar o physics gate"
    item_id, item, slot_idx = incompatible_pair

    drag_control = SimpleNamespace(data=str(item_id))
    mock_page._controls["drag_incompat"] = drag_control

    drop_event = SimpleNamespace(src_id="drag_incompat")
    widget._sov_on_accept(drop_event, slot_idx=slot_idx)

    # O slot deve continuar vazio (None) e a rejeição não deve travar o widget
    assert widget.sov_slots[slot_idx] is None
    assert widget.sov_check_btn.disabled is True


def test_sov_clear_and_release_slot():
    """Valida liberação pontual de slots e botão Limpar (devolução ao pool)."""
    assert len(SOV_QUESTIONS) > 0
    sov_q = SOV_QUESTIONS[0]

    widget = QuizWidget(question_data=sov_q, is_dark=True, on_next=lambda: None, on_answer=lambda c, t=0: None)

    # Encaixar item 0 no slot 0 diretamente
    widget.sov_slots[0] = 0
    widget._sov_render_filled_slot(0, 0)
    widget._refresh_sov_drag_sources()

    # O item 0 não deve mais estar no pool
    occupied_words = [widget.sov_items_by_id[0].word]
    pool_words = [c.content.content.value for c in widget.sov_drag_row.controls]
    assert widget.sov_items_by_id[0].word not in pool_words

    # Liberar o slot 0 individualmente
    widget._sov_release_slot(0)
    assert widget.sov_slots[0] is None
    pool_words_after_release = [c.content.content.value for c in widget.sov_drag_row.controls]
    assert widget.sov_items_by_id[0].word in pool_words_after_release

    # Preencher todos os slots e testar _sov_clear
    for idx in range(widget.sov_slot_count):
        widget.sov_slots[idx] = idx
        widget._sov_render_filled_slot(idx, idx)
    widget._refresh_sov_drag_sources()
    assert len(widget.sov_drag_row.controls) == 0

    widget._sov_clear(None)
    assert all(s is None for s in widget.sov_slots)
    assert len(widget.sov_drag_row.controls) == widget.sov_slot_count
    assert widget.sov_check_btn.disabled is True


def test_sov_check_and_clear_buttons_are_wired():
    """Valida fiação correta dos manipuladores de eventos em sov_check_btn e sov_clear_btn."""
    assert len(SOV_QUESTIONS) > 0
    sov_q = SOV_QUESTIONS[0]

    widget = QuizWidget(question_data=sov_q, is_dark=True, on_next=lambda: None, on_answer=lambda c, t=0: None)

    assert widget.sov_check_btn is not None
    assert widget.sov_clear_btn is not None
    assert callable(widget.sov_check_btn.on_click)
    assert callable(widget.sov_clear_btn.on_click)
    assert widget.sov_check_btn.on_click == widget._sov_check_order
    assert widget.sov_clear_btn.on_click == widget._sov_clear
    assert widget.sov_check_btn.disabled is True
    assert widget.sov_clear_btn.disabled is False


@pytest.mark.parametrize("mc_q", MC_QUESTIONS, ids=[q.id for q in MC_QUESTIONS])
def test_every_multiple_choice_question_builds_and_answers(mc_q: QuizQuestion):
    """Valida construção e resposta de todas as questões de múltipla escolha do currículo."""
    answer_received = None

    def on_answer(is_correct, elapsed_ms=0):
        nonlocal answer_received
        answer_received = is_correct

    widget = QuizWidget(question_data=mc_q, is_dark=True, on_next=lambda: None, on_answer=on_answer)

    assert len(widget.option_buttons) == len(mc_q.options)
    assert widget.answered is False

    # Selecionar a opção correta
    widget.handle_select(mc_q.correct_index)

    assert widget.answered is True
    assert answer_received is True
    assert widget.explanation_container.visible is True
    assert widget.next_button.visible is True


@pytest.mark.parametrize("ow_q", OW_QUESTIONS, ids=[q.id for q in OW_QUESTIONS])
def test_every_order_words_question_builds_and_answers(ow_q: QuizQuestion):
    """Valida construção e ordenação de todas as questões order_words do currículo."""
    answer_received = None

    def on_answer(is_correct, elapsed_ms=0):
        nonlocal answer_received
        answer_received = is_correct

    widget = QuizWidget(question_data=ow_q, is_dark=True, on_next=lambda: None, on_answer=on_answer)

    assert len(widget.available_words) == len(ow_q.words)
    assert widget.answered is False
    assert widget.check_btn.disabled is True

    # Adicionar palavras na ordem correta
    for word in ow_q.correct_order:
        widget._add_word(word)

    assert widget.selected_words == ow_q.correct_order
    assert widget.check_btn.disabled is False

    # Checar ordem
    widget._check_order(None)

    assert widget.answered is True
    assert answer_received is True
    assert widget.explanation_container.visible is True
    assert widget.next_button.visible is True
