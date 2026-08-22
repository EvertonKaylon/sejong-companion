"""Testes para o fluxo de Identificação e Persistência do Aluno (Onboarding + Session ID)."""

import os
import unittest
from unittest.mock import MagicMock
from src.services import ProgressService
from src.components.sentence_builder_widget import SentenceBuilderWidget

class MockPage:
    def __init__(self):
        self.client_storage = None
        self.session = None
        self.views = []
        self.route = "/home"

    def update(self):
        pass

    def go(self, route):
        self.route = route

class TestStudentIdentityAndPersistence(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_sessions_tmp")
        os.makedirs(self.test_dir, exist_ok=True)
        ProgressService._file_path_override = os.path.join(self.test_dir, "test_student.json")
        ProgressService._sessions.clear()

    def tearDown(self):
        ProgressService._file_path_override = None
        ProgressService._sessions.clear()
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_student_name_persistence(self):
        page = MockPage()
        page._sejong_student_id = "student_test_123"
        ps = ProgressService(page)
        
        self.assertEqual(ps.get_student_name(), "Estudante Sejong")
        
        ps.set_student_name("Marina Silva")
        self.assertEqual(ps.get_student_name(), "Marina Silva")
        
        # Simular reconexão de nova página para o mesmo student_id
        page2 = MockPage()
        page2._sejong_student_id = "student_test_123"
        ProgressService._sessions.clear() # Limpa RAM para forçar leitura de disco
        
        ps2 = ProgressService(page2)
        self.assertEqual(ps2.get_student_name(), "Marina Silva")
        self.assertEqual(ps2.get_student_id(), "student_test_123")

    def test_sentence_builder_punctuation_normalization(self):
        widget = SentenceBuilderWidget(
            challenge={
                "id": "c1",
                "prompt_pt": "Eu como arroz.",
                "sentence_pt": "Eu como arroz.",
                "words": ["저는", "밥을", "먹어요."],
                "correct_order": ["저는", "밥을", "먹어요."],
                "answer": "저는 밥을 먹어요.",
            },
            is_dark=True,
        )
        widget.answer_input = MagicMock()
        
        # Testar resposta correta com pontuação diferente
        widget.answer_input.value = "저는 밥을 먹어요"  # sem ponto
        widget._check_typing(None)
        self.assertIn("Excelente", widget.feedback)
        
        widget.answer_input.value = "저는 밥을 먹어요!"  # com exclamação
        widget._check_typing(None)
        self.assertIn("Excelente", widget.feedback)

        widget.answer_input.value = "저는 밥을 먹어요?"  # com interrogação
        widget._check_typing(None)
        self.assertIn("Excelente", widget.feedback)

        # Testar resposta incorreta
        widget.answer_input.value = "저는 빵을 먹어요"
        widget._check_typing(None)
        self.assertIn("Quase", widget.feedback)

if __name__ == "__main__":
    unittest.main()
