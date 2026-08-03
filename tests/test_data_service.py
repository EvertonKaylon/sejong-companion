import unittest
from src.services import DataService
from src.models import Unit, UnitIntroData, UnitOneData

class TestDataService(unittest.TestCase):
    def test_get_curriculum(self):
        curriculum = DataService.get_curriculum()
        self.assertIsInstance(curriculum, list)
        self.assertGreater(len(curriculum), 0)
        for unit in curriculum:
            self.assertIsInstance(unit, Unit)
            self.assertIsNotNone(unit.id)
            self.assertIsNotNone(unit.title_kr)
            self.assertIsNotNone(unit.title_pt)

    def test_get_unit_intro(self):
        intro_data = DataService.get_unit_intro()
        self.assertIsNotNone(intro_data)
        self.assertIsInstance(intro_data, UnitIntroData)
        self.assertEqual(intro_data.unit_id, "unit_intro")
        self.assertGreater(len(intro_data.vowels), 0)
        self.assertGreater(len(intro_data.consonants), 0)

    def test_get_unit_one(self):
        unit_one_data = DataService.get_unit_one()
        self.assertIsNotNone(unit_one_data)
        self.assertIsInstance(unit_one_data, UnitOneData)
        self.assertEqual(unit_one_data.unit_id, "unit_01")
        self.assertGreater(len(unit_one_data.vocabulary), 0)
        self.assertGreater(len(unit_one_data.grammar), 0)

if __name__ == "__main__":
    unittest.main()
