import os
import tempfile
import unittest
from src.services import ProgressService

class MockPage:
    pass

class TestProgressService(unittest.TestCase):
    def setUp(self):
        # Usar arquivo temporário isolado para os testes de persistência em disco
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_storage_file = os.path.join(self.temp_dir.name, "test_progress.json")
        ProgressService._file_path_override = self.test_storage_file
        ProgressService._sessions.clear()

        self.mock_page = MockPage()
        self.service = ProgressService(self.mock_page)

    def tearDown(self):
        ProgressService._sessions.clear()
        ProgressService._file_path_override = None
        self.temp_dir.cleanup()

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
        # Concluir unit_intro deve liberar unit_01 (já liberada por padrão)
        self.service.save_progress("unit_intro", 1.0)
        self.assertTrue(self.service.is_unlocked("unit_01"))

        # Concluir unit_01 deve liberar unit_02
        self.assertFalse(self.service.is_unlocked("unit_02"))
        self.service.save_progress("unit_01", 1.0)
        self.assertTrue(self.service.is_unlocked("unit_02"))

        # Concluir unit_02 deve liberar unit_03
        self.assertFalse(self.service.is_unlocked("unit_03"))
        self.service.save_progress("unit_02", 1.0)
        self.assertTrue(self.service.is_unlocked("unit_03"))

    def test_disk_persistence_across_restarts(self):
        # 1. Salvar dados na instância atual
        self.service.save_progress("unit_intro", 0.8)
        self.service.save_progress("unit_01", 1.0)
        self.assertTrue(os.path.exists(self.test_storage_file))

        # 2. Simular reinicialização total do app (limpar memória, manter disco)
        ProgressService._sessions.clear()

        # 3. Criar nova instância com o MESMO page (mesmo session_id) → carrega do disco
        new_service = ProgressService(self.mock_page)
        self.assertEqual(new_service.get_progress("unit_intro"), 0.8)
        self.assertEqual(new_service.get_progress("unit_01"), 1.0)
        self.assertTrue(new_service.is_unlocked("unit_02"))

    def test_reset_progress(self):
        self.service.save_progress("unit_01", 1.0)
        self.assertEqual(self.service.get_progress("unit_01"), 1.0)
        self.assertTrue(self.service.is_unlocked("unit_02"))

        # Resetar progresso
        self.service.reset_progress()
        self.assertEqual(self.service.get_progress("unit_01"), 0.0)
        self.assertFalse(self.service.is_unlocked("unit_02"))

        # Verificar que o reset foi persistido em disco (simular reinicialização)
        ProgressService._sessions.clear()
        new_service = ProgressService(self.mock_page)
        self.assertEqual(new_service.get_progress("unit_01"), 0.0)
        self.assertFalse(new_service.is_unlocked("unit_02"))

    def test_get_all_progress(self):
        self.service.save_progress("unit_intro", 0.75)
        all_data = self.service.get_all_progress()
        self.assertIn("progress_unit_intro", all_data)
        self.assertEqual(all_data["progress_unit_intro"], 0.75)

    def test_get_all_progress_returns_copy(self):
        """Garante que mutações no retorno não afetam o store interno."""
        self.service.save_progress("unit_intro", 0.75)
        all_data = self.service.get_all_progress()
        all_data["progress_unit_intro"] = 9999  # Mutação no retorno
        self.assertEqual(self.service.get_progress("unit_intro"), 0.75)  # Store intacto

    def test_session_isolation(self):
        """Progresso de uma sessão NÃO deve afetar outra sessão."""
        page_a = MockPage()
        page_b = MockPage()

        service_a = ProgressService(page_a)
        service_b = ProgressService(page_b)

        # Usuário A completa unit_01
        service_a.save_progress("unit_01", 1.0)

        # Usuário A vê progresso e desbloqueio
        self.assertEqual(service_a.get_progress("unit_01"), 1.0)
        self.assertTrue(service_a.is_unlocked("unit_02"))

        # Usuário B NÃO vê o progresso do Usuário A
        self.assertEqual(service_b.get_progress("unit_01"), 0.0)
        self.assertFalse(service_b.is_unlocked("unit_02"))

    def test_same_page_same_session(self):
        """Múltiplas instâncias com o mesmo page compartilham a mesma sessão."""
        service_1 = ProgressService(self.mock_page)
        service_2 = ProgressService(self.mock_page)

        service_1.save_progress("unit_intro", 0.5)
        self.assertEqual(service_2.get_progress("unit_intro"), 0.5)

if __name__ == "__main__":
    unittest.main()
