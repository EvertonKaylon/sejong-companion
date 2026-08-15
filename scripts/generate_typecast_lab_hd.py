#!/usr/bin/env python3
"""Geração Estrita em Typecast HD para os Áudios do Laboratório Fonético Oclusivo.

Garante que 100% dos áudios das 4 tríades (가/카/까, 다/타/따, 바/파/빠, 자/차/짜)
sejam gerados EXCLUSIVAMENTE via Typecast.ai HD (model: ssfm-v30, voice: tc_69f2e455ea79fd197aa0476f)
para ambos os formatos (WAV para Windows Desktop nativo e MP3 para Web Browser).
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
CACHE_DIR = os.path.join(ROOT_DIR, "assets", "audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# 12 Sons das 4 Tríades Oclusivas
LAB_SYLLABLES = [
    # Velares
    ("가", "ㄱ simples/relaxado"),
    ("카", "ㅋ aspirado com sopro forte"),
    ("까", "ㄲ tenso com contração glotal"),
    # Alveolares
    ("다", "ㄷ simples/relaxado"),
    ("타", "ㅌ aspirado com sopro forte"),
    ("따", "ㄸ tenso com contração glotal"),
    # Bilabiais
    ("바", "ㅂ simples/relaxado"),
    ("파", "ㅍ aspirado com sopro forte"),
    ("빠", "ㅃ tenso com contração glotal"),
    # Palatais
    ("자", "ㅈ simples/relaxado"),
    ("차", "ㅊ aspirado com sopro forte"),
    ("짜", "ㅉ tenso com contração glotal"),
]

TYPECAST_URL = "https://api.typecast.ai/v1/text-to-speech"
TYPECAST_VOICE_ID = "tc_69f2e455ea79fd197aa0476f"
TYPECAST_MODEL = "ssfm-v30"

def get_cache_filename(text: str, audio_format: str) -> str:
    cache_key = f"typecast-{audio_format}-v2\0{text}".encode("utf-8")
    return f"{hashlib.md5(cache_key).hexdigest()}.{audio_format}"

def synthesize_strict_typecast(text: str, audio_format: str, api_key: str, max_retries: int = 5) -> bytes:
    """Sintetiza estritamente com Typecast.ai HD, sem jamais cair em fallback."""
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
                print(f"   ⏳ [Rate limit 429] Aguardando {retry_after:.1f}s antes de tentar novamente (tentativa {attempt}/{max_retries})...")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            content = response.content
            if content and len(content) > 1000:
                return content
            raise ValueError(f"Resposta vazia ou muito curta: {len(content) if content else 0} bytes")

        except requests.RequestException as error:
            print(f"   ⚠️ Erro de rede (tentativa {attempt}/{max_retries}): {error}")
            time.sleep(1.5 * attempt)

    raise RuntimeError(f"Falha ao sintetizar '{text}' em Typecast HD após {max_retries} tentativas.")

def main():
    api_key = os.environ.get("TYPECAST_API_KEY")
    if not api_key:
        print("❌ ERRO: TYPECAST_API_KEY não encontrada no arquivo .env!")
        sys.exit(1)

    print("=" * 70)
    print(" 🔬 SÍNTESE ESTRITA EM TYPECAST HD — LABORATÓRIO FONÉTICO OCLUSIVO")
    print("=" * 70)
    print(f"Total de sons das 4 tríades: {len(LAB_SYLLABLES)}")
    print(f"Formatos suportados: WAV (Windows Desktop) e MP3 (Web Browser)\n")

    formats = ["wav", "mp3"]
    total_generated = 0

    for fmt in formats:
        print(f"\n🎧 Gerando formato: {fmt.upper()}...")
        for syllable, desc in LAB_SYLLABLES:
            filename = get_cache_filename(syllable, fmt)
            dest_path = os.path.join(CACHE_DIR, filename)

            print(f" • Sintetizando [{syllable}] ({desc})...", end="", flush=True)
            try:
                audio_bytes = synthesize_strict_typecast(syllable, fmt, api_key)
                # Escrita atômica
                tmp_path = f"{dest_path}.tmp"
                with open(tmp_path, "wb") as f:
                    f.write(audio_bytes)
                os.replace(tmp_path, dest_path)
                print(f" ✅ OK ({len(audio_bytes):,} bytes)")
                total_generated += 1
                # Espaçamento suave para respeitar a taxa da API
                time.sleep(0.4)
            except Exception as e:
                print(f" ❌ FALHA: {e}")

    print("\n" + "=" * 70)
    print(f"🎉 Concluído! {total_generated}/{len(LAB_SYLLABLES) * len(formats)} arquivos gerados 100% em Typecast HD.")
    print("=" * 70)

if __name__ == "__main__":
    main()
