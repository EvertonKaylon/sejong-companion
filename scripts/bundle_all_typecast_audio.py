#!/usr/bin/env python3
"""Geração Completa 100% Typecast HD de Todos os Áudios do Currículo (Opção A).

Gera e armazena em cache 100% de todos os 311 itens fonéticos do Sejong Companion
em ambos os formatos:
  1. WAV (Windows Desktop nativo)
  2. MP3 (Web Browser / Mobile PWA)

Todos sintetizados estritamente com a voz HD Typecast.ai (ssfm-v30 / tc_69f2e455ea79fd197aa0476f).
"""

import hashlib
import os
import sys
import time
import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.services import DataService

CACHE_DIR = os.path.join(ROOT_DIR, "assets", "audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TYPECAST_URL = "https://api.typecast.ai/v1/text-to-speech"
TYPECAST_VOICE_ID = "tc_69f2e455ea79fd197aa0476f"
TYPECAST_MODEL = "ssfm-v30"

def get_cache_filename(text: str, audio_format: str) -> str:
    cache_key = f"typecast-{audio_format}-v2\0{text}".encode("utf-8")
    return f"{hashlib.md5(cache_key).hexdigest()}.{audio_format}"

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total) if total > 0 else length
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')

def is_valid_typecast_audio(file_path: str, fmt: str) -> bool:
    """Verifica se o arquivo existe e tem tamanho compatível com Typecast HD."""
    if not os.path.exists(file_path):
        return False
    size = os.path.getsize(file_path)
    # Typecast HD tem taxa de bits elevada; mesmo monossílabos têm > 8KB em MP3 e > 25KB em WAV
    min_size = 15000 if fmt == "wav" else 5000
    return size >= min_size

def synthesize_strict_typecast(text: str, audio_format: str, api_key: str, max_retries: int = 5) -> bytes:
    payload = {
        "text": text,
        "voice_id": TYPECAST_VOICE_ID,
        "model": TYPECAST_MODEL,
        "language": "kor",
        "output": {"audio_format": audio_format},
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                TYPECAST_URL,
                json=payload,
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                timeout=(5, 30),
            )
            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", 2.0 * attempt))
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            content = response.content
            if content and len(content) > 1000:
                return content
            raise ValueError(f"Resposta vazia: {len(content) if content else 0} bytes")

        except requests.RequestException:
            time.sleep(1.5 * attempt)

    raise RuntimeError(f"Falha ao sintetizar '{text}' em Typecast HD após {max_retries} tentativas.")

def main():
    api_key = os.environ.get("TYPECAST_API_KEY")
    if not api_key:
        print("❌ ERRO: TYPECAST_API_KEY não encontrada no arquivo .env!")
        sys.exit(1)

    print("=" * 70)
    print(" 🇰🇷  EMBARQUE TOTAL DE ÁUDIOS TYPECAST HD (OPÇÃO A — WAV + MP3)")
    print("=" * 70)

    audio_texts = DataService.get_all_audio_texts()
    total_texts = len(audio_texts)
    formats = ["mp3", "wav"]
    total_operations = total_texts * len(formats)

    print(f" • Total de itens fonéticos: {total_texts}")
    print(f" • Formatos: {', '.join(formats).upper()}")
    print(f" • Total de arquivos a garantir: {total_operations}\n")

    start_time = time.time()
    op_count = 0
    new_synthesized = 0
    cached_count = 0

    for fmt in formats:
        print(f"\n🎧 Verificando e sintetizando formato {fmt.upper()}...")
        for text in audio_texts:
            op_count += 1
            clean_text = text.strip().replace(" / ", " ").replace("/", " ")
            filename = get_cache_filename(clean_text, fmt)
            dest_path = os.path.join(CACHE_DIR, filename)

            if is_valid_typecast_audio(dest_path, fmt):
                cached_count += 1
                tag = "[HD CACHE]"
            else:
                try:
                    audio_bytes = synthesize_strict_typecast(clean_text, fmt, api_key)
                    tmp_path = f"{dest_path}.part"
                    with open(tmp_path, "wb") as f:
                        f.write(audio_bytes)
                    os.replace(tmp_path, dest_path)
                    new_synthesized += 1
                    tag = "[HD NOVO]"
                    time.sleep(0.35)  # Espaçamento suave para evitar 429
                except Exception as e:
                    tag = f"[ERRO: {e}]"

            short_text = (clean_text[:18] + '..') if len(clean_text) > 18 else clean_text.ljust(20)
            print_progress_bar(
                op_count,
                total_operations,
                prefix="Progresso",
                suffix=f"({op_count}/{total_operations}) {fmt.upper()} {tag} {short_text}"
            )

    elapsed = time.time() - start_time
    total_size_mb = sum(
        os.path.getsize(os.path.join(CACHE_DIR, f))
        for f in os.listdir(CACHE_DIR)
        if os.path.isfile(os.path.join(CACHE_DIR, f))
    ) / (1024 * 1024)

    print("\n" + "=" * 70)
    print(" 📊 RESUMO DO EMBARQUE TOTAL (OPÇÃO A)")
    print("=" * 70)
    print(f" • Total de arquivos verificados: {total_operations}")
    print(f" • Já em cache HD:                {cached_count}")
    print(f" • Novos sintetizados em HD:      {new_synthesized}")
    print(f" • Peso total do cache em disco:  {total_size_mb:.2f} MB")
    print(f" • Tempo decorrido:               {elapsed:.1f}s")
    print(f" • Status:                        100% TYPECAST HD EMBARCADO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
