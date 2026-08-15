import asyncio
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.services import DataService
from src.audio_service import AudioService

class MockPage:
    def __init__(self):
        self.web = False
        self.overlay = []

    def update(self):
        pass

    def run_task(self, coro, *args, **kwargs):
        pass

class TestAudioPrewarm(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_page = MockPage()
        self.audio_service = AudioService(self.mock_page)
        # Apontar cache para diretório temporário
        self.audio_service.cache_dir = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_priority_audio_texts_structure(self):
        """get_priority_audio_texts() deve extrair vogais, consoantes, oclusivas e vocab u1."""
        priority = DataService.get_priority_audio_texts()
        self.assertIsInstance(priority, list)
        self.assertGreater(len(priority), 20)

        # Deve conter consoantes oclusivas essenciais
        for char in ["ㄱ", "ㅋ", "ㄲ", "ㄷ", "ㅌ", "ㄸ", "ㅂ", "ㅍ", "ㅃ", "ㅈ", "ㅊ", "ㅉ"]:
            self.assertIn(char, priority)

        # Não deve ter duplicatas
        self.assertEqual(len(priority), len(set(priority)))

    def test_get_all_audio_texts_structure(self):
        """get_all_audio_texts() deve agregar todo o currículo de forma desduplicada."""
        all_texts = DataService.get_all_audio_texts()
        priority = DataService.get_priority_audio_texts()

        self.assertIsInstance(all_texts, list)
        # O total deve ser maior que apenas os prioritários
        self.assertGreater(len(all_texts), len(priority))

        # Não deve conter duplicatas nem strings vazias
        self.assertEqual(len(all_texts), len(set(all_texts)))
        self.assertTrue(all(len(t.strip()) > 0 for t in all_texts))

    def test_is_cached_returns_false_for_missing(self):
        """is_cached() deve retornar False para texto ainda não sintetizado."""
        self.assertFalse(self.audio_service.is_cached("안녕하세요"))
        self.assertFalse(self.audio_service.is_cached(""))

    def test_is_cached_returns_true_when_file_exists(self):
        """is_cached() retorna True quando o arquivo existe e tem tamanho > 0."""
        text = "감사합니다"
        filename = self.audio_service._cache_filename(text)
        file_path = os.path.join(self.audio_service.cache_dir, filename)

        with open(file_path, "wb") as f:
            f.write(b"fake audio data")

        self.assertTrue(self.audio_service.is_cached(text))

    def test_get_cache_stats(self):
        """get_cache_stats() calcula percentuais e contagens corretas."""
        texts = ["단어1", "단어2", "단어3", "단어4"]

        # Criar 2 arquivos no cache falso
        for t in texts[:2]:
            fn = self.audio_service._cache_filename(t)
            with open(os.path.join(self.audio_service.cache_dir, fn), "wb") as f:
                f.write(b"audio")

        stats = self.audio_service.get_cache_stats(texts)
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["cached"], 2)
        self.assertEqual(stats["missing"], 2)
        self.assertEqual(stats["percent"], 50.0)

    @patch.object(AudioService, "_synthesize_to_cache", return_value=True)
    def test_prewarm_batch_sync(self, mock_synth):
        """prewarm_batch_sync sintetiza itens faltantes e emite progresso."""
        texts = ["사과", "바나나", "우유"]
        progress_records = []

        def on_prog(curr, tot, txt, cached):
            progress_records.append((curr, tot, txt, cached))

        res = self.audio_service.prewarm_batch_sync(texts, on_progress=on_prog)
        self.assertEqual(res["total"], 3)
        self.assertEqual(len(progress_records), 3)
        self.assertEqual(mock_synth.call_count, 3)

    @patch.object(AudioService, "_synthesize_to_cache", return_value=True)
    def test_prewarm_batch_async(self, mock_synth):
        """prewarm_batch_async executa em lote assíncrono respeitando concorrência."""
        texts = ["하나", "둘", "셋", "넷", "다섯"]
        progress_calls = []

        def on_prog(curr, tot, txt):
            progress_calls.append(curr)

        async def run_async_test():
            return await self.audio_service.prewarm_batch_async(texts, on_progress=on_prog, max_concurrent=2)

        res = asyncio.run(run_async_test())
        self.assertEqual(res["total"], 5)
        self.assertEqual(res["processed"], 5)
        self.assertEqual(len(progress_calls), 5)

if __name__ == "__main__":
    unittest.main()
