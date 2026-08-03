import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.audio_service import AudioService


class MockPage:
    def __init__(self):
        self.web = True
        self.overlay = []
        self.tasks = []

    def run_task(self, coro, *args, **kwargs):
        self.tasks.append((coro, args, kwargs))

    def update(self):
        pass


class TestAudioService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.page = MockPage()
        self.service = AudioService(self.page)
        self.service.player.play = AsyncMock()
        self.service.player.update = MagicMock()

    def test_init_creates_player_as_attribute(self):
        """O player de áudio deve ser criado como atributo do serviço (não em page.services)."""
        self.assertIsNotNone(self.service.player)
        self.assertEqual(self.service.player.src, "silent.wav")
        self.assertTrue(self.service.player.autoplay)
        self.assertEqual(self.service.player.volume, 0.0)

    @patch("src.audio_service.sys.platform", "win32")
    def test_desktop_windows_uses_wav_and_native_player(self):
        desktop_service = AudioService(type("DesktopPage", (), {"overlay": []})())

        self.assertTrue(desktop_service._use_native_windows_player)
        self.assertEqual(desktop_service.audio_format, "wav")
        self.assertIsNone(desktop_service.player)

    def test_play_korean_delegates_to_run_task(self):
        self.service.play_korean("안녕하세요")

        self.assertEqual(len(self.page.tasks), 1)
        self.assertEqual(self.page.tasks[0][0], self.service.play_korean_async)
        self.assertEqual(self.page.tasks[0][1], ("안녕하세요",))

    @patch("src.audio_service.os.path.exists", return_value=True)
    @patch("src.audio_service.AudioService._play_file", new_callable=AsyncMock)
    async def test_cached_audio_uses_relative_asset_path(self, mock_play_file, _):
        await self.service.play_korean_async("안녕하세요")

        mock_play_file.assert_awaited_once_with(
            f"audio_cache/{self.service._cache_filename('안녕하세요')}"
        )

    @patch("src.audio_service.AudioService._get_google_audio", return_value=b"google-mp3")
    @patch("src.audio_service.AudioService._get_typecast_audio", return_value=None)
    @patch("src.audio_service.os.replace")
    @patch("builtins.open")
    def test_synthesis_falls_back_to_google_and_writes_atomically(
        self, mock_open, mock_replace, mock_typecast, mock_google
    ):
        self.assertTrue(self.service._synthesize_to_cache("안녕하세요", "cache.mp3"))

        mock_typecast.assert_called_once_with("안녕하세요")
        mock_google.assert_called_once_with("안녕하세요")
        mock_replace.assert_called_once_with("cache.mp3.part", "cache.mp3")

    @patch.dict(os.environ, {"TYPECAST_API_KEY": "key"}, clear=True)
    @patch("src.audio_service.requests.post")
    def test_typecast_requests_audio_format_to_match_cache_extension(self, mock_post):
        response = MagicMock(content=b"typecast-mp3")
        mock_post.return_value = response

        self.assertEqual(self.service._get_typecast_audio("안녕하세요"), b"typecast-mp3")
        self.assertEqual(mock_post.call_args.kwargs["json"]["output"]["audio_format"], "mp3")
        self.assertEqual(mock_post.call_args.kwargs["json"]["language"], "kor")

    @patch("src.audio_service.os.path.getsize", return_value=1024)
    @patch("src.audio_service.os.path.exists", return_value=True)
    async def test_play_file_updates_source_and_awaits_player(self, mock_exists, mock_size):
        """_play_file verifica existência do arquivo, atualiza src e chama play()."""
        await self.service._play_file("audio_cache/test.mp3")

        self.assertEqual(self.service.player.src, "audio_cache/test.mp3")
        self.service.player.update.assert_called_once()
        self.service.player.play.assert_awaited_once()

    @patch("src.audio_service.os.path.getsize", return_value=0)
    @patch("src.audio_service.os.path.exists", return_value=True)
    async def test_play_file_rejects_empty_file(self, mock_exists, mock_size):
        """_play_file não tenta reproduzir se o arquivo está vazio (0 bytes)."""
        await self.service._play_file("audio_cache/empty.mp3")

        self.service.player.play.assert_not_awaited()

    @patch("src.audio_service.os.path.exists", return_value=False)
    async def test_play_file_rejects_missing_file(self, mock_exists):
        """_play_file não tenta reproduzir se o arquivo não existe."""
        await self.service._play_file("audio_cache/missing.mp3")

        self.service.player.play.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
