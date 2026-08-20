import unittest
from src.services import DataService
from src.models import Unit, UnitIntroData, UnitOneData, UnitData

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

    def test_curriculum_has_23_entries(self):
        """O currículo completo tem 23 entradas: unit_intro + 10 do 1A + 12 do 1B."""
        curriculum = DataService.get_curriculum()
        self.assertEqual(len(curriculum), 23)

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

    def test_get_unit_generic_all(self):
        """DataService.get_unit() deve carregar todas as unidades do 1A (01-10) e 1B (1b_01-1b_12)."""
        all_ids = [f"unit_{i:02d}" for i in range(1, 11)] + [f"unit_1b_{i:02d}" for i in range(1, 13)]
        for unit_id in all_ids:
            data = DataService.get_unit(unit_id)
            self.assertIsNotNone(data, f"{unit_id} retornou None")
            self.assertIsInstance(data, UnitData)
            self.assertEqual(data.unit_id, unit_id)
            self.assertGreater(len(data.vocabulary), 0, f"{unit_id} sem vocabulário")
            self.assertGreater(len(data.grammar), 0, f"{unit_id} sem gramática")
            self.assertGreater(len(data.exercises), 0, f"{unit_id} sem exercícios")

    def test_get_unit_nonexistent_returns_none(self):
        """Unidade inexistente retorna None sem exceção."""
        data = DataService.get_unit("unit_99")
        self.assertIsNone(data)

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
