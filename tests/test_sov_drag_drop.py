import json
import unittest
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from src.models import QuizQuestion, SovSlotDefinition, SovWordItem, is_role_accepted


ROOT = Path(__file__).resolve().parents[1]


class TestSovDragDropModels(unittest.TestCase):
    def test_role_acceptance_obeys_slot_contract(self):
        self.assertTrue(is_role_accepted("OBJECT", ["OBJECT"]))
        self.assertFalse(is_role_accepted("VERB", ["OBJECT"]))
        self.assertTrue(is_role_accepted("VERB", ["ANY"]))

    def test_semantic_question_accepts_complete_contract(self):
        question = QuizQuestion(
            id="semantic",
            type="drag_and_drop_sov",
            question="Monte a frase.",
            words=["저는", "학생이에요"],
            correct_order=["저는", "학생이에요"],
            sov_items=[
                SovWordItem(word="저는", role="SUBJECT", snap_anchor="round"),
                SovWordItem(word="학생이에요", role="PREDICATE"),
            ],
            sov_slots=[
                SovSlotDefinition(role="SUBJECT", label="주어 (S)", accepted_roles=["SUBJECT"]),
                SovSlotDefinition(role="PREDICATE", label="서술어 (Pred)", accepted_roles=["PREDICATE", "VERB"]),
            ],
        )
        self.assertEqual(question.sov_items[0].role, "SUBJECT")
        self.assertEqual(question.sov_slots[1].accepted_roles, ["PREDICATE", "VERB"])

    def test_semantic_question_requires_metadata(self):
        with self.assertRaises(ValidationError):
            QuizQuestion(
                id="invalid",
                type="drag_and_drop_sov",
                question="Monte a frase.",
                words=["저는"],
                correct_order=["저는"],
            )

    def test_legacy_question_types_remain_compatible(self):
        multiple_choice = QuizQuestion(
            id="legacy-choice",
            type="multiple_choice",
            question="Teste",
            options=["A", "B"],
            correct_index=0,
        )
        order_words = QuizQuestion(
            id="legacy-order",
            type="order_words",
            question="Teste",
            words=["B", "A"],
            correct_order=["A", "B"],
        )
        self.assertIsNone(multiple_choice.sov_items)
        self.assertIsNone(order_words.sov_slots)


class TestSovCurriculumData(unittest.TestCase):
    def test_all_sentence_building_exercises_have_semantic_contracts(self):
        for unit_number in range(1, 11):
            path = ROOT / "data" / "units" / f"unit_{unit_number:02d}.json"
            with self.subTest(unit=path.name):
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                sov_questions = [
                    question for question in data["exercises"]
                    if question["type"] == "drag_and_drop_sov"
                ]
                self.assertGreater(len(sov_questions), 0)
                for raw_question in sov_questions:
                    question = QuizQuestion.model_validate(raw_question)
                    self.assertEqual(len(question.sov_items), len(question.sov_slots))
                    self.assertEqual(
                        Counter(item.word for item in question.sov_items),
                        Counter(question.correct_order),
                    )
                    role_by_word = {item.word: item.role for item in question.sov_items}
                    for word, slot in zip(question.correct_order, question.sov_slots):
                        self.assertTrue(is_role_accepted(role_by_word[word], slot.accepted_roles))
                    for item in question.sov_items:
                        self.assertIn(item.snap_anchor, {"square", "round"})


if __name__ == "__main__":
    unittest.main()
