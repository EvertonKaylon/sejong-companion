#!/usr/bin/env python3
"""Script CLI para Pré-Carregamento Completo de Áudios (Offline Pre-Warming).

Baixa e armazena em cache 100% de todos os áudios do currículo Sejong 1A
(Hangul, Consoantes Oclusivas, Unidades 01 a 10 e Frases Gramaticais)
diretamente na pasta assets/audio_cache/.

Garante reprodução instantânea (0ms de latência) e funcionamento 100% offline
durante apresentações, testes e uso diário do estudante.
"""

import os
import sys
import time

# Garantir saída UTF-8 no terminal Windows sem quebrar em emojis/Hangul
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Adicionar a raiz do projeto ao path para importar src
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.services import DataService
from src.audio_service import AudioService

class HeadlessPage:
    """Mock leve para instanciar o AudioService fora de uma sessão gráfica Flet."""
    def __init__(self):
        self.web = False
        self.overlay = []

    def update(self):
        pass

    def run_task(self, coro, *args, **kwargs):
        pass

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    """Imprime uma barra de progresso no terminal."""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total) if total > 0 else length
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')

import argparse

def main():
    parser = argparse.ArgumentParser(description="Sejong Companion Audio Pre-Warming CLI")
    parser.add_argument(
        "--force-hd",
        action="store_true",
        help="Força a re-síntese de todos os áudios diretamente com Typecast HD (sobrescrevendo fallbacks)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.35,
        help="Intervalo em segundos entre requisições para evitar rate limit 429 (padrão: 0.35s)",
    )
    args = parser.parse_args()

    print("=" * 65)
    print(" 🇰🇷  SEJONG COMPANION — OFFLINE AUDIO PRE-WARMING CLI")
    print("=" * 65)
    print("Extraindo todos os termos fonéticos do currículo...")

    audio_texts = DataService.get_all_audio_texts()
    total_items = len(audio_texts)
    print(f"Total de itens fonéticos catalogados: {total_items}\n")

    page = HeadlessPage()
    audio_service = AudioService(page)

    if args.force_hd:
        print("🔄 Modo --force-hd ativado: limpando cache para re-síntese completa em Typecast HD...")
        for text in audio_texts:
            clean_text = text.strip().replace(" / ", " ").replace("/", " ")
            fn = audio_service._cache_filename(clean_text)
            fp = os.path.join(audio_service.cache_dir, fn)
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except Exception:
                    pass

    initial_stats = audio_service.get_cache_stats(audio_texts)
    print(f"📦 Estado inicial do cache local:")
    print(f"   • Já em cache: {initial_stats['cached']} ({initial_stats['percent']:.1f}%)")
    print(f"   • Pendentes:   {initial_stats['missing']}")
    print(f"   • Pasta:       {audio_service.cache_dir}\n")

    if initial_stats['missing'] == 0 and not args.force_hd:
        print("✅ Todos os áudios já estão em cache! O app está 100% pronto para uso offline.")
        return

    print(f"⚡ Iniciando download e síntese Typecast HD (delay: {args.delay}s)...")
    start_time = time.time()

    def on_progress(current, total, text, already_cached):
        tag = "[CACHE]" if already_cached else "[HD BAIXADO]"
        short_text = (text[:20] + '..') if len(text) > 20 else text.ljust(22)
        print_progress_bar(
            current,
            total,
            prefix=f"Progresso",
            suffix=f"({current}/{total}) {tag} {short_text}"
        )

    results = audio_service.prewarm_batch_sync(audio_texts, on_progress=on_progress, delay=args.delay)
    elapsed = time.time() - start_time

    final_stats = audio_service.get_cache_stats(audio_texts)
    print("\n" + "=" * 65)
    print(" 📊 RESUMO DO PRÉ-CARREGAMENTO")
    print("=" * 65)
    print(f" • Total processado:    {results['total']}")
    print(f" • Em cache final:      {final_stats['cached']} ({final_stats['percent']:.1f}%)")
    print(f" • Novos sintetizados:  {final_stats['cached'] - initial_stats['cached']}")
    print(f" • Tempo total:         {elapsed:.2f}s")
    missing_count = final_stats['missing']
    status_str = '100% PRONTO (ZERO LATÊNCIA)' if missing_count == 0 else f'{missing_count} pendentes'
    print(f" • Status:              {status_str}")
    print("=" * 65)

if __name__ == "__main__":
    main()
