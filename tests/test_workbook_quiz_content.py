import json
import unittest
from pathlib import Path

from src.models import UnitData, UnitIntroData


ROOT = Path(__file__).resolve().parents[1]
UNITS_DIR = ROOT / "data" / "units"


class TestWorkbookQuizContent(unittest.TestCase):
    def test_every_lesson_has_integrated_workbook_questions(self):
        paths = [UNITS_DIR / "unit_intro.json"] + [
            UNITS_DIR / f"unit_{number:02d}.json" for number in range(1, 11)
        ]

        for path in paths:
            with self.subTest(unit=path.name):
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                model = UnitIntroData if path.name == "unit_intro.json" else UnitData
                model.model_validate(data)

                workbook_questions = [
                    question
                    for question in data["exercises"]
                    if question["id"].startswith("wb_")
                ]
                self.assertEqual(len(workbook_questions), 4)
                self.assertTrue(
                    all(question["type"] == "multiple_choice" for question in workbook_questions)
                )

    def test_workbook_question_ids_are_unique(self):
        question_ids = []
        for path in UNITS_DIR.glob("unit_*.json"):
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            question_ids.extend(
                question["id"]
                for question in data["exercises"]
                if question["id"].startswith("wb_")
            )

        self.assertEqual(len(question_ids), len(set(question_ids)))
        self.assertEqual(len(question_ids), 44)


if __name__ == "__main__":
    unittest.main()
