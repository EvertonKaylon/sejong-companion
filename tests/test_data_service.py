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

    def test_implicit_sensory_attributes(self):
        intro_data = DataService.get_unit_intro()
        for vowel in intro_data.vowels:
            self.assertIsNotNone(vowels := vowel.audio_wave_profile)
        for consonant in intro_data.consonants:
            self.assertIsNotNone(consonant.audio_wave_profile)

    def test_implicit_snap_and_roles(self):
        unit_one_data = DataService.get_unit_one()
        has_snap = any(item.snap_anchor is not None for item in unit_one_data.vocabulary)
        has_role = any(item.magnetic_slot_role is not None for item in unit_one_data.vocabulary)
        self.assertTrue(has_snap)
        self.assertTrue(has_role)

if __name__ == "__main__":
    unittest.main()
