import unittest
from src.services import ProgressService

class MockPage:
    pass

class TestProgressService(unittest.TestCase):
    def setUp(self):
        # Limpar o store global compartilhado antes de cada teste
        ProgressService._store.clear()
        self.mock_page = MockPage()
        self.service = ProgressService(self.mock_page)

    def test_get_progress_default(self):
        self.assertEqual(self.service.get_progress("unit_intro"), 0.0)
        self.assertEqual(self.service.get_progress("unit_01"), 0.0)

    def test_save_and_get_progress(self):
        self.service.save_progress("unit_intro", 0.5)
        self.assertEqual(self.service.get_progress("unit_intro"), 0.5)
        
        self.service.save_progress("unit_01", 1.0)
        self.assertEqual(self.service.get_progress("unit_01"), 1.0)

    def test_is_unlocked_defaults(self):
        # Unidades padrão desbloqueadas
        self.assertTrue(self.service.is_unlocked("unit_intro"))
        self.assertTrue(self.service.is_unlocked("unit_01"))
        
        # Outras unidades bloqueadas inicialmente
        self.assertFalse(self.service.is_unlocked("unit_02"))
        self.assertFalse(self.service.is_unlocked("unit_03"))

    def test_unlock_progression(self):
        # Concluir unit_intro deve liberar unit_01 (mas unit_01 já é liberada por padrão)
        self.service.save_progress("unit_intro", 1.0)
        self.assertTrue(self.service.is_unlocked("unit_01"))

        # Concluir unit_01 deve liberar unit_02
        self.assertFalse(self.service.is_unlocked("unit_02"))
        self.service.save_progress("unit_01", 1.0)
        self.assertTrue(self.service.is_unlocked("unit_02"))

if __name__ == "__main__":
    unittest.main()
