"""Testes de privacidade, retenção de telemetria e isolamento de arquivos:
- Rotação de logs JSONL ao atingir o limite MAX_EVENTS_PER_FILE
- Validação de regras do .gitignore para proteção de dados educacionais
"""

import os
import pytest
from src.services import TelemetryService, PedagogicalEvent


def test_telemetry_rotation(tmp_path, monkeypatch):
    """Valida que o arquivo de telemetria não cresce indefinidamente e realiza rotação."""
    sess_id = "test_student_rotation"
    log_file = tmp_path / f"events_{sess_id}.jsonl"

    # Redirecionar diretório de telemetria para tmp_path
    monkeypatch.setattr(TelemetryService, "_get_telemetry_dir", classmethod(lambda cls: str(tmp_path)))
    # Definir limite pequeno para o teste
    monkeypatch.setattr(TelemetryService, "MAX_EVENTS_PER_FILE", 5)

    # Gravar 10 eventos
    for i in range(10):
        ev = PedagogicalEvent(
            event_type="question_answered",
            unit_id="unit_01",
            item_id=f"q_{i}",
            payload={"correct": True, "seq": i}
        )
        TelemetryService.record(sess_id, ev)

    # Verificar que o arquivo contém no máximo 5 eventos mais recentes
    with open(log_file, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    assert len(lines) == 5
    # O último evento deve ser q_9
    assert '"q_9"' in lines[-1]
    assert '"q_5"' in lines[0]


def test_gitignore_protects_educational_data():
    """Valida que .gitignore possui regras explícitas para dados sensíveis em runtime."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gitignore_path = os.path.join(root_dir, ".gitignore")
    assert os.path.exists(gitignore_path)

    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "data/sessions/" in content
    assert "data/telemetry/" in content
    assert "data/reports/" in content
    assert "data/cache/" in content
    assert "*.jsonl" in content
