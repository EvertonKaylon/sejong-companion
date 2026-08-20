"""Testes unitários para o TelemetryService e PedagogicalAnalyzer."""

import os
import shutil
import tempfile
import unittest
from datetime import datetime

from src.models import PedagogicalEvent
from src.services import TelemetryService, PedagogicalAnalyzer


class TestTelemetryService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sejong_test_telemetry_")
        TelemetryService._telemetry_dir_override = self.test_dir

    def tearDown(self):
        TelemetryService._telemetry_dir_override = None
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_record_single_event(self):
        """Grava um único evento e verifica integridade do arquivo JSONL."""
        event = PedagogicalEvent(
            event_type="question_answered",
            unit_id="unit_01",
            item_id="u01_q01",
            payload={"correct": True, "response_time_ms": 1500},
        )
        ok = TelemetryService.record("sess_123", event)
        self.assertTrue(ok)

        events = TelemetryService.get_events("sess_123")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "question_answered")
        self.assertEqual(events[0].unit_id, "unit_01")
        self.assertEqual(events[0].item_id, "u01_q01")
        self.assertTrue(events[0].payload["correct"])
        self.assertEqual(events[0].payload["response_time_ms"], 1500)

    def test_append_only_multiple_events(self):
        """Grava múltiplos eventos sucessivos mantendo integridade e ordem."""
        for i in range(5):
            ev = PedagogicalEvent(
                event_type="flashcard_rated",
                unit_id="unit_02",
                item_id=f"unit_02:vocab:{i}",
                payload={"rating": "good", "response_time_ms": 2000 + i * 100},
            )
            TelemetryService.record("sess_abc", ev)

        events = TelemetryService.get_events("sess_abc")
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0].item_id, "unit_02:vocab:0")
        self.assertEqual(events[4].item_id, "unit_02:vocab:4")

    def test_session_isolation(self):
        """Eventos de sessões diferentes devem ser gravados em arquivos separados."""
        TelemetryService.record(
            "sess_user_A",
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_01"),
        )
        TelemetryService.record(
            "sess_user_B",
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_02"),
        )

        events_a = TelemetryService.get_events("sess_user_A")
        events_b = TelemetryService.get_events("sess_user_B")
        events_all = TelemetryService.get_events()

        self.assertEqual(len(events_a), 1)
        self.assertEqual(events_a[0].unit_id, "unit_01")

        self.assertEqual(len(events_b), 1)
        self.assertEqual(events_b[0].unit_id, "unit_02")

        self.assertEqual(len(events_all), 2)

    def test_resilience_to_corrupted_lines(self):
        """Leitura de eventos deve ignorar linhas em branco ou JSON inválido sem falhar."""
        log_path = os.path.join(self.test_dir, "events_sess_corrupt.jsonl")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write('{"event_type": "lesson_opened", "unit_id": "unit_01", "payload": {}}\n')
            f.write("ESTA LINHA ESTA TOTALMENTE CORROMPIDA {invalid json\n")
            f.write("\n")
            f.write('{"event_type": "quiz_completed", "unit_id": "unit_01", "payload": {"score": 5}}\n')

        events = TelemetryService.get_events("sess_corrupt")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, "lesson_opened")
        self.assertEqual(events[1].event_type, "quiz_completed")

    def test_clear_events(self):
        """Limpeza de eventos específicos ou totais."""
        TelemetryService.record("s1", PedagogicalEvent(event_type="a", unit_id="u1"))
        TelemetryService.record("s2", PedagogicalEvent(event_type="b", unit_id="u2"))

        # Limpar apenas s1
        removed = TelemetryService.clear_events("s1")
        self.assertEqual(removed, 1)
        self.assertEqual(len(TelemetryService.get_events("s1")), 0)
        self.assertEqual(len(TelemetryService.get_events("s2")), 1)

        # Limpar todos
        removed_all = TelemetryService.clear_events()
        self.assertEqual(removed_all, 1)
        self.assertEqual(len(TelemetryService.get_events()), 0)


class TestPedagogicalAnalyzer(unittest.TestCase):
    def test_empty_events_analysis(self):
        """Análise com lista vazia retorna estrutura segura sem divisão por zero."""
        result = PedagogicalAnalyzer.analyze([])
        self.assertEqual(result["total_events"], 0)
        self.assertEqual(result["hardest_questions"], [])
        self.assertEqual(result["drop_off_units"], [])
        self.assertEqual(result["critical_vocab"], [])

    def test_hardest_questions_calculation(self):
        """Identifica questões com maior taxa de erro e tempo de hesitação."""
        events = [
            # Q1: 1 acerto, 2 erros (66.7% erro)
            PedagogicalEvent(event_type="question_answered", unit_id="u1", item_id="q1", payload={"correct": False, "response_time_ms": 4000}),
            PedagogicalEvent(event_type="question_answered", unit_id="u1", item_id="q1", payload={"correct": False, "response_time_ms": 5000}),
            PedagogicalEvent(event_type="question_answered", unit_id="u1", item_id="q1", payload={"correct": True, "response_time_ms": 3000}),
            # Q2: 2 acertos, 0 erros (0% erro)
            PedagogicalEvent(event_type="question_answered", unit_id="u1", item_id="q2", payload={"correct": True, "response_time_ms": 1500}),
            PedagogicalEvent(event_type="question_answered", unit_id="u1", item_id="q2", payload={"correct": True, "response_time_ms": 1700}),
        ]
        res = PedagogicalAnalyzer.analyze(events)
        hardest = res["hardest_questions"]
        self.assertEqual(len(hardest), 2)
        self.assertEqual(hardest[0]["question_id"], "q1")
        self.assertAlmostEqual(hardest[0]["error_rate"], 0.6667, places=3)
        self.assertEqual(hardest[0]["avg_response_time_ms"], 4000.0)
        self.assertEqual(hardest[1]["question_id"], "q2")
        self.assertEqual(hardest[1]["error_rate"], 0.0)

    def test_drop_off_units_calculation(self):
        """Calcula taxa de abandono (aberturas sem conclusão correspondente)."""
        events = [
            # Unit 01: 3 aberturas, 3 conclusões (0% abandono)
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_01"),
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_01"),
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_01"),
            PedagogicalEvent(event_type="lesson_completed", unit_id="unit_01"),
            PedagogicalEvent(event_type="lesson_completed", unit_id="unit_01"),
            PedagogicalEvent(event_type="lesson_completed", unit_id="unit_01"),
            # Unit 02: 4 aberturas, 1 conclusão (75% abandono)
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_02"),
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_02"),
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_02"),
            PedagogicalEvent(event_type="lesson_opened", unit_id="unit_02"),
            PedagogicalEvent(event_type="lesson_completed", unit_id="unit_02"),
        ]
        res = PedagogicalAnalyzer.analyze(events)
        drop_offs = res["drop_off_units"]
        self.assertEqual(len(drop_offs), 2)
        # Unit 02 deve estar no topo com 75% de abandono
        self.assertEqual(drop_offs[0]["unit_id"], "unit_02")
        self.assertEqual(drop_offs[0]["drop_off_rate"], 0.75)
        self.assertEqual(drop_offs[1]["unit_id"], "unit_01")
        self.assertEqual(drop_offs[1]["drop_off_rate"], 0.0)

    def test_critical_vocab_ratings(self):
        """Identifica vocabulários mais avaliados com 'again'."""
        events = [
            PedagogicalEvent(event_type="flashcard_rated", unit_id="u1", item_id="card_easy", payload={"rating": "easy", "response_time_ms": 1000}),
            PedagogicalEvent(event_type="flashcard_rated", unit_id="u1", item_id="card_easy", payload={"rating": "good", "response_time_ms": 1200}),
            PedagogicalEvent(event_type="flashcard_rated", unit_id="u2", item_id="card_hard", payload={"rating": "again", "response_time_ms": 4000}),
            PedagogicalEvent(event_type="flashcard_rated", unit_id="u2", item_id="card_hard", payload={"rating": "again", "response_time_ms": 4500}),
            PedagogicalEvent(event_type="flashcard_rated", unit_id="u2", item_id="card_hard", payload={"rating": "hard", "response_time_ms": 3800}),
        ]
        res = PedagogicalAnalyzer.analyze(events)
        critical = res["critical_vocab"]
        self.assertEqual(len(critical), 2)
        self.assertEqual(critical[0]["item_id"], "card_hard")
        self.assertEqual(critical[0]["again_count"], 2)
        self.assertAlmostEqual(critical[0]["again_rate"], 0.6667, places=3)


if __name__ == "__main__":
    unittest.main()
