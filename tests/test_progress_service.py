import os
import tempfile
import unittest
from datetime import datetime, timedelta
from src.services import ProgressService
from src.models import MemoryNode

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

    def test_full_unlock_chain_10_units(self):
        """Cadeia de desbloqueio completa: unit_intro → unit_01 → ... → unit_10."""
        self.service.save_progress("unit_intro", 1.0)
        for i in range(1, 10):
            unit_id = f"unit_{i:02d}"
            next_id = f"unit_{i+1:02d}"
            self.assertTrue(self.service.is_unlocked(unit_id), f"{unit_id} deveria estar desbloqueada")
            self.assertFalse(self.service.is_unlocked(next_id), f"{next_id} deveria estar bloqueada")
            self.service.save_progress(unit_id, 1.0)
            self.assertTrue(self.service.is_unlocked(next_id), f"{next_id} deveria desbloquear após completar {unit_id}")

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

    # ─── SRS (Modelo Heurístico de Retenção Baseado em Meia-Vida) ───

    def test_memory_node_initial_stability(self):
        """MemoryNode sem revisão retorna estabilidade 0.0."""
        node = MemoryNode(unit_id="unit_01")
        self.assertEqual(node.calculate_stability(), 0.0)

    def test_memory_node_stability_after_review(self):
        """Após revisão recente, estabilidade deve ser alta (próxima de 1.0)."""
        node = MemoryNode(unit_id="unit_01", half_life=5.0,
                          last_reviewed=datetime.now().isoformat())
        stability = node.calculate_stability()
        self.assertGreater(stability, 0.99)

    def test_memory_node_stability_decay(self):
        """Após tempo significativo, estabilidade deve decair."""
        past = (datetime.now() - timedelta(days=10)).isoformat()
        node = MemoryNode(unit_id="unit_01", half_life=5.0, last_reviewed=past)
        stability = node.calculate_stability()
        self.assertLess(stability, 0.3)  # 10 dias com meia-vida de 5 → R = 2^(-2) = 0.25

    def test_memory_node_update_correct(self):
        """Resposta correta deve aumentar a meia-vida."""
        node = MemoryNode(unit_id="unit_01", half_life=5.0)
        old_half_life = node.half_life
        node.update_performance(is_correct=True, response_time_ms=1000)
        self.assertGreater(node.half_life, old_half_life)

    def test_memory_node_update_incorrect(self):
        """Resposta incorreta deve diminuir a meia-vida."""
        node = MemoryNode(unit_id="unit_01", half_life=5.0,
                          last_reviewed=datetime.now().isoformat())
        old_half_life = node.half_life
        node.update_performance(is_correct=False)
        self.assertLess(node.half_life, old_half_life)

    def test_vitality_levels(self):
        """Testa os 3 níveis de vitalidade do MemoryNode."""
        # High: revisão muito recente
        node_high = MemoryNode(unit_id="u1", half_life=5.0,
                               last_reviewed=datetime.now().isoformat())
        self.assertEqual(node_high.vitality_level(), "high")

        # Low: revisão muito antiga
        old = (datetime.now() - timedelta(days=30)).isoformat()
        node_low = MemoryNode(unit_id="u2", half_life=5.0, last_reviewed=old)
        self.assertEqual(node_low.vitality_level(), "low")

    def test_service_get_vitality_none_by_default(self):
        """Unidade nunca estudada retorna 'none'."""
        vitality = self.service.get_vitality("unit_01")
        self.assertEqual(vitality, "none")

    def test_service_record_review_persists(self):
        """record_review() deve persistir o MemoryNode no store."""
        node = self.service.record_review("unit_01", is_correct=True, response_time_ms=1500)
        self.assertGreater(node.half_life, 5.0)
        self.assertNotEqual(node.last_reviewed, "")

        # Verificar que vitality agora é 'high'
        vitality = self.service.get_vitality("unit_01")
        self.assertEqual(vitality, "high")

    def test_memory_node_disk_persistence(self):
        """MemoryNode deve sobreviver a reinicializações."""
        self.service.record_review("unit_01", is_correct=True)
        
        # Simular reinicialização
        ProgressService._sessions.clear()
        new_service = ProgressService(self.mock_page)
        
        vitality = new_service.get_vitality("unit_01")
        self.assertEqual(vitality, "high")  # Revisão recente → alta vitalidade

    # ─── Identidade Persistente do Aluno (Client Storage & Perfil) ───

    def test_persistent_student_id_via_client_storage(self):
        """ClientStorage preserva o student_id mesmo após recriar o objeto page."""
        class MockClientStorage:
            def __init__(self):
                self.store = {}
            def get(self, key):
                return self.store.get(key)
            def set(self, key, value):
                self.store[key] = value

        mock_storage = MockClientStorage()

        # 1. Primeira aba/sessão
        page_1 = MockPage()
        page_1.client_storage = mock_storage
        service_1 = ProgressService(page_1)
        student_id_1 = service_1.get_student_id()
        self.assertTrue(student_id_1.startswith("student_"))
        self.assertEqual(mock_storage.get("sejong_student_id"), student_id_1)

        # Salva progresso no perfil
        service_1.save_progress("unit_intro", 1.0)
        service_1.set_student_name("Kayzer")

        # 2. Usuário fecha o navegador e abre novamente (novo objeto page, mesmo client_storage)
        ProgressService._sessions.clear()
        page_2 = MockPage()
        page_2.client_storage = mock_storage
        service_2 = ProgressService(page_2)

        self.assertEqual(service_2.get_student_id(), student_id_1)
        self.assertEqual(service_2.get_student_name(), "Kayzer")
        self.assertEqual(service_2.get_progress("unit_intro"), 1.0)

    def test_export_and_import_backup(self):
        """Garante que o progresso pode ser exportado e restaurado via JSON."""
        self.service.save_progress("unit_01", 0.75)
        self.service.set_student_name("Kayzer Dev")

        backup_json = self.service.export_backup()
        self.assertIn("Kayzer Dev", backup_json)
        self.assertIn("progress_unit_01", backup_json)

        # Resetar e restaurar
        self.service.reset_progress()
        self.assertEqual(self.service.get_progress("unit_01"), 0.0)

        ok = self.service.import_backup(backup_json)
        self.assertTrue(ok)
        self.assertEqual(self.service.get_progress("unit_01"), 0.75)
        self.assertEqual(self.service.get_student_name(), "Kayzer Dev")

    def test_import_invalid_backup(self):
        """Importação de JSON inválido retorna False sem corromper o store."""
        self.service.save_progress("unit_01", 1.0)
        ok = self.service.import_backup("NOT_JSON")
        self.assertFalse(ok)
        self.assertEqual(self.service.get_progress("unit_01"), 1.0)

    def test_corrupted_disk_file_handling(self):
        """Arquivo de sessão corrompido em disco gera backup .corrupt.bak e reinicia seguro."""
        with open(self.test_storage_file, "w", encoding="utf-8") as f:
            f.write("{invalid_json: 123 broken")

        ProgressService._sessions.clear()
        service = ProgressService(MockPage())
        self.assertEqual(service.get_progress("unit_01"), 0.0)
        self.assertTrue(os.path.exists(f"{self.test_storage_file}.corrupt.bak"))

    def test_progress_clamping(self):
        """Valores de progresso são sempre limitados estritamente entre 0.0 e 1.0."""
        self.service.save_progress("unit_01", -0.5)
        self.assertEqual(self.service.get_progress("unit_01"), 0.0)

        self.service.save_progress("unit_01", 1.8)
        self.assertEqual(self.service.get_progress("unit_01"), 1.0)


if __name__ == "__main__":
    unittest.main()
