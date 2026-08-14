import os
import tempfile
import unittest
from datetime import datetime, timedelta

from src.services import DataService, ProgressService


class MockPage:
    pass


class TestActiveRecall(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        ProgressService._file_path_override = os.path.join(self.temp_dir.name, "review.json")
        ProgressService._sessions.clear()
        self.service = ProgressService(MockPage())

    def tearDown(self):
        ProgressService._sessions.clear()
        ProgressService._file_path_override = None
        self.temp_dir.cleanup()

    def test_flashcards_are_compiled_and_classified(self):
        cards = DataService.get_all_flashcards()
        self.assertGreater(len(cards), 20)
        self.assertEqual({"easy", "medium", "hard"}, {card.difficulty for card in cards})
        self.assertTrue(all(card.id and card.korean and card.portuguese for card in cards))
        self.assertTrue(all(card.unit_id.startswith("unit_") for card in cards))

    def test_due_reviews_only_returns_retention_below_threshold(self):
        card = DataService.get_all_flashcards()[0]
        self.service.record_item_recall(card.id, "good")
        self.assertEqual(self.service.get_due_reviews(), [])

        node = self.service.get_item_memory_node(card.id)
        node.last_reviewed = (datetime.now() - timedelta(days=40)).isoformat()
        self.service._save_item_memory_node(card.id, node)
        due = self.service.get_due_reviews()

        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["item"].id, card.id)
        self.assertLess(due[0]["retention"], 0.75)

    def test_item_recall_uses_specified_half_life_multipliers(self):
        card = DataService.get_all_flashcards()[0]
        node = self.service.record_item_recall(card.id, "good")
        self.assertEqual(node.half_life, 7.5)
        node = self.service.record_item_recall(card.id, "easy")
        self.assertEqual(node.half_life, 16.5)
        node = self.service.record_item_recall(card.id, "again")
        self.assertEqual(node.half_life, 4.95)

    def test_daily_streak_is_persisted(self):
        self.assertEqual(self.service.get_daily_streak(), 0)
        self.assertEqual(self.service.record_daily_activity(), 1)
        self.assertEqual(self.service.record_daily_activity(), 1)
        self.assertEqual(self.service.get_daily_streak(), 1)

    def test_absence_never_resets_study_days_or_xp(self):
        today = datetime.now().date()
        self.service._store["study_days"] = 6
        self.service._store["daily_streak"] = 6
        self.service._store["study_dates"] = [(today - timedelta(days=2)).isoformat()]
        self.service._store["total_xp"] = 60

        self.assertEqual(self.service.record_daily_activity(), 7)
        self.assertEqual(self.service.get_daily_streak(), 7)
        self.assertEqual(self.service.get_total_xp(), 120)  # 10 padrão + 50 do marco de 7
        self.assertEqual(self.service.record_daily_activity(), 7)
        self.assertEqual(self.service.get_total_xp(), 120)  # mesmo dia não duplica XP

    def test_milestone_schedule_matches_the_gamification_rules(self):
        self.assertTrue(ProgressService._is_milestone(7))
        self.assertFalse(ProgressService._is_milestone(10))
        for milestone in (15, 20, 25, 30, 35, 40, 45):
            self.assertTrue(ProgressService._is_milestone(milestone))

    def test_sentence_builder_challenges_have_a_valid_solution(self):
        for difficulty in ("easy", "medium", "hard"):
            challenges = DataService.get_sentence_builder_challenges(difficulty)
            self.assertGreater(len(challenges), 0, difficulty)
            for challenge in challenges:
                self.assertEqual(challenge["answer"], " ".join(challenge["correct_order"]))
                self.assertTrue(challenge["prompt_pt"])


if __name__ == "__main__":
    unittest.main()
