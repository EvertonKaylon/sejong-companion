"""Testes automatizados para questões de caligrafia (Wongoji Lab & Workbooks) no Quiz Engine."""

import unittest
from unittest.mock import MagicMock
from pydantic import ValidationError

from src.models import QuizQuestion
from src.components.quiz_widget import QuizWidget
from src.components.wongoji_multi_cell_widget import WongojiMultiCellWidget


class TestCalligraphyQuizModels(unittest.TestCase):
    """Testes de contrato e validação Pydantic para o tipo 'calligraphy'."""

    def test_valid_single_char_calligraphy_question(self):
        q = QuizQuestion(
            id="cal-01",
            type="calligraphy",
            question="Escreva a consoante 'ㄱ' na grade 원고지.",
            target_char="ㄱ",
            min_iou=0.50,
            show_ghost=True,
            explanation="A consoante ㄱ (기역) é traçada com dois movimentos: horizontal para a direita e vertical para baixo.",
        )
        self.assertEqual(q.type, "calligraphy")
        self.assertEqual(q.target_text, "ㄱ")
        self.assertEqual(q.min_iou, 0.50)
        self.assertTrue(q.show_ghost)

    def test_valid_word_calligraphy_question(self):
        q = QuizQuestion(
            id="cal-02",
            type="calligraphy",
            question="Escreva a palavra '한국' (Coreia) na grade 원고지.",
            target_text="한국",
            min_iou=0.40,
            show_ghost=True,
        )
        self.assertEqual(q.target_text, "한국")
        self.assertEqual(q.min_iou, 0.40)
        self.assertTrue(q.show_ghost)

    def test_valid_phrase_calligraphy_question(self):
        q = QuizQuestion(
            id="cal-03",
            type="calligraphy",
            question="Escreva a frase '밥을 먹어요' na grade 원고지.",
            target_text="밥을 먹어요",
            min_iou=0.40,
            show_ghost=False,
        )
        self.assertEqual(q.target_text, "밥을 먹어요")
        self.assertEqual(len(q.target_text), 6)  # 5 caracteres + 1 espaço
        self.assertFalse(q.show_ghost)

    def test_calligraphy_requires_target_text_or_char(self):
        with self.assertRaises(ValidationError):
            QuizQuestion(
                id="cal-err-1",
                type="calligraphy",
                question="Escreva o texto.",
            )

    def test_calligraphy_rejects_empty_target(self):
        with self.assertRaises(ValidationError):
            QuizQuestion(
                id="cal-err-2",
                type="calligraphy",
                question="Escreva o texto.",
                target_text="",
            )
        with self.assertRaises(ValidationError):
            QuizQuestion(
                id="cal-err-3",
                type="calligraphy",
                question="Escreva o texto.",
                target_text="   ",
            )

    def test_calligraphy_rejects_invalid_min_iou(self):
        with self.assertRaises(ValidationError):
            QuizQuestion(
                id="cal-err-4",
                type="calligraphy",
                question="Escreva.",
                target_text="가",
                min_iou=0.0,
            )
        with self.assertRaises(ValidationError):
            QuizQuestion(
                id="cal-err-5",
                type="calligraphy",
                question="Escreva.",
                target_text="가",
                min_iou=1.5,
            )

    def test_legacy_quiz_questions_unaffected(self):
        mc = QuizQuestion(
            id="mc-01",
            type="multiple_choice",
            question="Qual o som de 가?",
            options=["ga", "na", "da"],
            correct_index=0,
        )
        self.assertEqual(mc.type, "multiple_choice")
        self.assertIsNone(mc.target_text)


class TestWongojiMultiCellWidget(unittest.TestCase):
    """Testes unitários dedicados do componente WongojiMultiCellWidget."""

    def test_multi_cell_initialization(self):
        widget = WongojiMultiCellWidget(
            target_text="한국어 공부",
            cell_size=210.0,
            is_dark=False,
            show_ghost=True,
            min_iou=0.45,
        )
        self.assertEqual(widget.target_text, "한국어 공부")
        self.assertEqual(widget.num_cells, 6)
        self.assertEqual(widget.active_cell_size, 210.0)
        self.assertEqual(len(widget.strokes_by_cell), 6)

    def test_space_cell_identified_and_neutral(self):
        widget = WongojiMultiCellWidget(target_text="밥 먹다")
        # '밥' (idx 0), ' ' (idx 1), '먹' (idx 2), '다' (idx 3)
        self.assertEqual(widget.target_text[1], " ")

        # Avaliação ignora células de espaço no cálculo de avaliação
        passed, avg_score, scores = widget.evaluate()
        self.assertNotIn(1, scores)
        self.assertIn(0, scores)
        self.assertIn(2, scores)
        self.assertIn(3, scores)

    def test_reset_clears_all_cell_strokes(self):
        widget = WongojiMultiCellWidget(target_text="가나")
        widget.strokes_by_cell[0].append([(0.2, 0.2), (0.8, 0.2)])
        widget.reset()
        self.assertEqual(widget.strokes_by_cell[0], [])
        self.assertEqual(widget.strokes_by_cell[1], [])


class TestCalligraphyQuizWidgetUI(unittest.TestCase):
    """Testes de inicialização e interação do QuizWidget com caligrafia multi-célula."""

    def test_calligraphy_quiz_widget_initialization(self):
        q = QuizQuestion(
            id="cal-ui-01",
            type="calligraphy",
            question="Escreva '한국' na grade abaixo.",
            target_text="한국",
            min_iou=0.45,
            show_ghost=True,
            explanation="한국 = Coreia",
        )
        on_next = MagicMock()
        on_answer = MagicMock()

        widget = QuizWidget(
            question_data=q,
            is_dark=False,
            on_next=on_next,
            on_answer=on_answer,
        )

        self.assertIsNotNone(widget.calligraphy_comp)
        self.assertEqual(widget.calligraphy_comp.target_text, "한국")
        self.assertTrue(widget.calligraphy_comp.show_ghost)
        self.assertFalse(widget.answered)
        self.assertIsNotNone(widget.btn_calligraphy_check)

    def test_calligraphy_check_success_flow(self):
        q = QuizQuestion(
            id="cal-ui-02",
            type="calligraphy",
            question="Escreva '밥을 먹어요'.",
            target_text="밥을 먹어요",
            min_iou=0.40,
            explanation="Excelente!",
        )
        on_next = MagicMock()
        on_answer = MagicMock()

        widget = QuizWidget(
            question_data=q,
            is_dark=False,
            on_next=on_next,
            on_answer=on_answer,
        )

        # Mock do método evaluate do componente para simular aprovação
        widget.calligraphy_comp.evaluate = MagicMock(return_value=(True, 0.85, {0: 0.85, 1: 0.90, 3: 0.80, 4: 0.85, 5: 0.88}))
        widget._check_calligraphy(None)

        self.assertTrue(widget.answered)
        self.assertTrue(widget.btn_calligraphy_check.disabled)
        self.assertTrue(widget.explanation_container.visible)
        self.assertTrue(widget.next_button.visible)
        on_answer.assert_called_once()
        self.assertTrue(on_answer.call_args[0][0])  # is_correct = True

    def test_calligraphy_check_retry_on_insufficient_score(self):
        q = QuizQuestion(
            id="cal-ui-03",
            type="calligraphy",
            question="Escreva '한국'.",
            target_text="한국",
            min_iou=0.50,
        )
        on_next = MagicMock()
        on_answer = MagicMock()

        widget = QuizWidget(
            question_data=q,
            is_dark=False,
            on_next=on_next,
            on_answer=on_answer,
        )

        # Mock do evaluate com célula 2 insuficiente
        widget.calligraphy_comp.evaluate = MagicMock(return_value=(False, 0.35, {0: 0.60, 1: 0.10}))
        widget._check_calligraphy(None)

        # Não deve marcar como respondido nem travar a tela
        self.assertFalse(widget.answered)
        self.assertFalse(widget.btn_calligraphy_check.disabled)
        self.assertFalse(widget.next_button.visible)
        self.assertIn("Similaridade de 35%", widget.calligraphy_status_msg.value)
        self.assertIn("Célula 2 precisa de ajuste", widget.calligraphy_status_msg.value)
        on_answer.assert_not_called()
