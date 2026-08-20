#!/usr/bin/env python3
"""Script de geração de Relatório de Evidência Pedagógica (CLI).

Lê os logs anônimos de telemetria (.jsonl) em data/telemetry/ e compila um diagnóstico
estatístico de retenção, taxa de erro por exercício, abandono de lições e vocabulário crítico.

Uso:
    python -m scripts.pedagogical_report
    python -m scripts.pedagogical_report --export report.md
"""

import argparse
import os
import sys
from typing import Optional

# Garantir que a raiz do projeto esteja no sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.services import TelemetryService, PedagogicalAnalyzer


def format_report_markdown(analysis: dict) -> str:
    """Gera um relatório formatado em Markdown com tabelas e diagnósticos."""
    total_events = analysis.get("total_events", 0)
    lines = [
        "# 📊 Relatório de Evidência Pedagógica — Sejong Companion",
        "",
        f"**Total de Eventos Registrados:** {total_events}",
        f"**Quizzes Concluídos:** {analysis['session_summary']['total_quizzes_completed']}",
        f"**Sessões de Revisão Diária:** {analysis['session_summary']['total_reviews_completed']}",
        "",
        "---",
        "",
        "## 1. ⚠️ Questões com Maior Taxa de Erro (Top 5)",
        "",
    ]

    hardest = analysis.get("hardest_questions", [])[:5]
    if hardest:
        lines.extend([
            "| ID da Questão | Unidade | Tentativas | Erros | Taxa de Erro | Tempo Médio (ms) |",
            "| :--- | :--- | :---: | :---: | :---: | :---: |",
        ])
        for q in hardest:
            lines.append(
                f"| `{q['question_id']}` | `{q['unit_id']}` | {q['total_attempts']} | "
                f"{q['errors']} | **{q['error_rate']:.1%}** | {q['avg_response_time_ms']}ms |"
            )
    else:
        lines.append("*Nenhum dado de questão registrado ainda.*")

    lines.extend([
        "",
        "---",
        "",
        "## 2. 📉 Taxa de Abandono por Unidade (Opened vs Completed)",
        "",
    ])

    drop_offs = analysis.get("drop_off_units", [])
    if drop_offs:
        lines.extend([
            "| Unidade | Aberturas | Conclusões | Taxa de Abandono |",
            "| :--- | :---: | :---: | :---: |",
        ])
        for u in drop_offs:
            lines.append(
                f"| `{u['unit_id']}` | {u['opened_count']} | {u['completed_count']} | **{u['drop_off_rate']:.1%}** |"
            )
    else:
        lines.append("*Nenhum dado de abertura/conclusão de unidade registrado ainda.*")

    lines.extend([
        "",
        "---",
        "",
        "## 3. 🔄 Vocabulário Crítico com Mais Reincidência de 'Again' (Top 5)",
        "",
    ])

    critical = analysis.get("critical_vocab", [])[:5]
    if critical:
        lines.extend([
            "| ID do Item | Unidade | Again (Errei) | Hard (Difícil) | Good | Easy | Taxa de Again |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
        ])
        for c in critical:
            lines.append(
                f"| `{c['item_id']}` | `{c['unit_id']}` | **{c['again_count']}** | "
                f"{c['hard_count']} | {c['good_count']} | {c['easy_count']} | {c['again_rate']:.1%} |"
            )
    else:
        lines.append("*Nenhum dado de avaliação de flashcard registrado ainda.*")

    lines.extend([
        "",
        "---",
        "",
        "## 4. ⏱️ Tempo Médio de Resposta por Modalidade de Exercício",
        "",
    ])

    times = analysis.get("avg_response_times", {})
    if times:
        lines.extend([
            "| Tipo de Atividade | Tempo Médio |",
            "| :--- | :---: |",
        ])
        for act, avg_t in times.items():
            lines.append(f"| `{act}` | **{avg_t:.1f}ms** ({avg_t/1000:.2f}s) |")
    else:
        lines.append("*Nenhum tempo de resposta cronometrado ainda.*")

    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Gera relatório de evidência pedagógica do Sejong Companion.")
    parser.add_argument("--session", type=str, default=None, help="Filtrar por UUID de sessão específico")
    parser.add_argument("--export", type=str, default=None, help="Caminho para exportar o relatório em Markdown")
    args = parser.parse_args()

    events = TelemetryService.get_events(session_id=args.session)
    analysis = PedagogicalAnalyzer.analyze(events)
    report_md = format_report_markdown(analysis)

    print("\n" + "=" * 70)
    print(report_md)
    print("=" * 70 + "\n")

    if args.export:
        export_path = os.path.abspath(args.export)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"✅ Relatório exportado com sucesso para: {export_path}")


if __name__ == "__main__":
    main()
