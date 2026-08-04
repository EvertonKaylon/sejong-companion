import asyncio
import hashlib
import os
import sys

import flet as ft
import flet_audio as fa
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class AudioService:
    """Synthesizes Korean text once, caches it, and plays it through Flet."""

    TYPECAST_URL = "https://api.typecast.ai/v1/text-to-speech"
    TYPECAST_VOICE_ID = "tc_69f2e455ea79fd197aa0476f"
    TYPECAST_MODEL = "ssfm-v30"
    # The Typecast reference uses a 60-second request timeout.  The connect
    # timeout is kept short so the fallback is still responsive offline.
    REQUEST_TIMEOUT = (5, 60)

    def __init__(self, page: ft.Page):
        self.page = page
        self._is_loading = False
        self._use_native_windows_player = sys.platform == "win32" and not getattr(page, "web", False)
        self.audio_format = "wav" if self._use_native_windows_player else "mp3"

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_dir = os.path.join(base_dir, "assets", "audio_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        self.player = None
        if not self._use_native_windows_player:
            # --- Destrave do autoplay do navegador (Chrome/Edge) ---
            # Confirmado pela própria equipe do Flet como comportamento do
            # NAVEGADOR, não bug do Flet: qualquer chamada a play() que
            # chegue via round-trip servidor->cliente (que é como o Flet
            # SEMPRE funciona, mesmo para o play() "instantâneo" de um
            # arquivo em cache) não conta como gesto direto do usuário para
            # o Chrome/Edge, que então bloqueia a reprodução silenciosamente
            # (ver flet-dev/flet#3695). O desktop nunca sofre disso porque
            # não é um navegador de verdade.
            #
            # O workaround validado pela comunidade Flet: o MESMO elemento
            # de áudio faz um autoplay MUDO (volume=0) de um arquivo
            # silencioso assim que é montado na página. Autoplay mudo é
            # permitido por padrão em todos os navegadores. Isso "destrava"
            # esse elemento específico para o resto da sessão — chamadas
            # play() subsequentes no MESMO elemento (só trocando src) deixam
            # de ser bloqueadas, mesmo vindas de forma assíncrona depois.
            # Por isso é essencial reusar sempre este mesmo self.player.
            self.player = fa.Audio(
                src="silent.wav",
                autoplay=True,
                volume=0.0,
                release_mode=fa.ReleaseMode.STOP,
            )
            self._audio_unlocked = False

    def play_korean(self, text: str):
        text = text.strip() if text else ""
        if text:
            # Sanitizar barras e caracteres de formato (ex: "은 / 는" -> "은 는")
            clean_text = text.replace(" / ", " ").replace("/", " ")
            self.page.run_task(self.play_korean_async, clean_text)

    async def play_korean_async(self, text: str):
        if self._is_loading:
            return

        self._is_loading = True
        try:
            await self._play_korean_async_inner(text)
        finally:
            self._is_loading = False

    async def _play_korean_async_inner(self, text: str):
        filename = self._cache_filename(text)
        local_file_path = os.path.join(self.cache_dir, filename)

        if not os.path.exists(local_file_path):
            # requests is synchronous. Running it in a worker keeps Flet's
            # event loop free to register the Audio service and handle its
            # invoke-method reply instead of producing a playback timeout.
            fetched = await asyncio.to_thread(self._synthesize_to_cache, text, local_file_path)
            if not fetched:
                self._show_audio_error(text)
                return

        # Asset paths are relative to assets_dir; a leading slash is an HTTP
        # path and can bypass Flet's asset resolver on web clients.
        if self._use_native_windows_player:
            await self._play_native_file(local_file_path)
        else:
            await self._play_file(f"audio_cache/{filename}")

    def _cache_filename(self, text: str) -> str:
        # Version the key to avoid reusing old .mp3 files that may actually
        # contain Typecast's former default WAV response.
        cache_key = f"typecast-{self.audio_format}-v2\0{text}".encode("utf-8")
        return f"{hashlib.md5(cache_key).hexdigest()}.{self.audio_format}"

    def _synthesize_to_cache(self, text: str, destination: str) -> bool:
        audio = self._get_typecast_audio(text)
        if audio is None and not self._use_native_windows_player:
            audio = self._get_google_audio(text)
        if not audio:
            return False

        # Never expose a partially written response as a cache hit.
        temporary_path = f"{destination}.part"
        try:
            with open(temporary_path, "wb") as audio_file:
                audio_file.write(audio)
            os.replace(temporary_path, destination)
            return True
        except OSError as error:
            print(f"Audio cache write error: {error}")
            try:
                if os.path.exists(temporary_path):
                    os.remove(temporary_path)
            except OSError:
                pass
            return False

    def _get_typecast_audio(self, text: str) -> bytes | None:
        api_key = os.environ.get("TYPECAST_API_KEY")
        if not api_key:
            return None

        payload = {
            "text": text,
            "voice_id": self.TYPECAST_VOICE_ID,
            "model": self.TYPECAST_MODEL,
            "language": "kor",
            "output": {"audio_format": self.audio_format},
        }
        try:
            response = requests.post(
                self.TYPECAST_URL,
                json=payload,
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.content or None
        except requests.RequestException as error:
            print(f"Typecast TTS error: {error}. Using Google TTS fallback.")
            return None

    def _get_google_audio(self, text: str) -> bytes | None:
        try:
            response = requests.get(
                "https://translate.google.com/translate_tts",
                params={"ie": "UTF-8", "tl": "ko", "client": "tw-ob", "q": text},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.content or None
        except requests.RequestException as error:
            print(f"Google TTS error: {error}")
            return None

    async def _play_file(self, src_path: str):
        assert self.player is not None

        # Sanity check *before* touching Flet at all: rules out "the file
        # doesn't exist / is empty / never finished writing" as a cause,
        # which looks identical to a playback timeout from the outside
        # (no sound, no crash) but has nothing to do with the Audio service.
        local_path = os.path.join(self.cache_dir, os.path.basename(src_path))
        if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
            print(f"Audio playback error: arquivo ausente/vazio em {local_path!r}")
            self._show_audio_error()
            return

        # A primeira reprodução "real" desfaz o mudo do autoplay de
        # destravamento (volume=0 -> volume=1). Feito só uma vez.
        if not self._audio_unlocked:
            self.player.volume = 1.0
            self._audio_unlocked = True

        self.player.src = src_path
        self._flush()

        try:
            await asyncio.wait_for(self.player.play(), timeout=8)
        except asyncio.TimeoutError:
            # O cliente nunca confirmou o invoke_method de play(). Se o
            # destravamento de autoplay (silent.wav) não tiver rodado antes
            # deste ponto (ver __init__), isto costuma ser a política de
            # autoplay do Chrome/Edge bloqueando a chamada por não vir de um
            # gesto síncrono do usuário (flet-dev/flet#3695) — e não um
            # problema de rede/CDN de verdade.
            print(
                "Audio playback error: timeout aguardando confirmação do "
                f"cliente para {src_path!r}."
            )
            self._show_audio_error()
        except RuntimeError as error:
            print(f"Audio playback error (RuntimeError): {error}")
            self._show_audio_error()
        except Exception as error:  # nunca deixar a task morrer em silêncio
            print(f"Audio playback error (unexpected {type(error).__name__}): {error}")
            self._show_audio_error()

    def _flush(self):
        """Atualiza o player sem derrubar a task se ele ainda não estiver
        montado na página (ex.: logo após reconectar/navegar). Nesse caso
        cai para page.update(), que sempre funciona porque percorre a
        árvore inteira a partir da página."""
        try:
            self.player.update()
        except RuntimeError:
            self.page.update()

    async def _play_native_file(self, local_file_path: str):
        """Use Windows' built-in WAV player when running as a desktop app."""
        try:
            import winsound

            await asyncio.to_thread(
                winsound.PlaySound,
                local_file_path,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
        except RuntimeError as error:
            print(f"Native audio playback error: {error}")
            self._show_audio_error()

    def _show_audio_error(self, text: str | None = None):
        message = "Não foi possível tocar o áudio agora."
        if text:
            message = f"{text} (sem conexão de áudio)"
        snack = ft.SnackBar(content=ft.Text(f"🔊 {message}"), duration=1500, open=True)
        self.page.overlay.append(snack)
        self.page.update()
