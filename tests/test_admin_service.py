import pytest
import os
import json
from src.services import AdminService, TelemetryService, PedagogicalEvent

def test_admin_authentication_unconfigured(monkeypatch):
    """Valida que sem SEJONG_ADMIN_PIN ou SAEBOM_ADMIN_PIN configurado, o sistema falha fechado."""
    monkeypatch.delenv("SEJONG_ADMIN_PIN", raising=False)
    monkeypatch.delenv("SAEBOM_ADMIN_PIN", raising=False)
    assert AdminService.is_configured() is False
    assert AdminService.authenticate("sejong2026") is False
    assert AdminService.authenticate("any_pin") is False
    assert AdminService.authenticate("") is False
    assert AdminService.authenticate(None) is False


def test_admin_authentication_configured(monkeypatch):
    """Valida autenticação com PIN configurado via variável de ambiente."""
    monkeypatch.delenv("SAEBOM_ADMIN_PIN", raising=False)
    monkeypatch.setenv("SEJONG_ADMIN_PIN", "prof_cccb_99")
    assert AdminService.is_configured() is True
    # PIN correto
    assert AdminService.authenticate("prof_cccb_99") is True
    # PIN com espaços ao redor
    assert AdminService.authenticate(" prof_cccb_99 ") is True
    # PIN incorreto
    assert AdminService.authenticate("wrong_pin") is False
    # Antigo PIN padrão não deve funcionar
    assert AdminService.authenticate("sejong2026") is False
    # PIN vazio ou None
    assert AdminService.authenticate("") is False
    assert AdminService.authenticate(None) is False

def test_admin_get_all_students_summary(tmp_path):
    """Valida a leitura e compilação de múltiplos perfis de alunos simulados."""
    from datetime import datetime
    now_str = datetime.now().isoformat()
    # 1. Criar perfil Aluno 1: Kayzer (Avançado)
    student_1 = {
        "student_id": "kayzer_01",
        "student_name": "Kayzer",
        "streak": 7,
        "total_xp": 350,
        "last_study_date": "2026-08-20",
        "created_at": "2026-08-01",
        "progress_unit_intro": 1.0,
        "progress_unit_01": 1.0,
        "progress_unit_02": 1.0,
        "progress_unit_1b_01": 1.0,
        "memory_nodes": {
            "u01:v0": {"half_life_days": 10.0, "last_reviewed_at": now_str},
            "u01:v1": {"half_life_days": 5.0, "last_reviewed_at": now_str}
        }
    }
    with open(tmp_path / "student_kayzer_01.json", "w", encoding="utf-8") as f:
        json.dump(student_1, f)

    # 2. Criar perfil Aluno 2: Anna (Iniciante)
    student_2 = {
        "student_id": "anna_99",
        "student_name": "Anna",
        "streak": 2,
        "total_xp": 40,
        "last_study_date": "2026-08-19",
        "created_at": "2026-08-18",
        "progress_unit_intro": 1.0,
        "progress_unit_01": 0.5,
        "memory_nodes": {}
    }
    with open(tmp_path / "student_anna_99.json", "w", encoding="utf-8") as f:
        json.dump(student_2, f)

    # 3. Criar arquivo corrompido para testar resiliência
    with open(tmp_path / "student_corrupt.json", "w", encoding="utf-8") as f:
        f.write("{invalid_json: 123")

    # 4. Criar arquivo não-json
    with open(tmp_path / "readme.txt", "w", encoding="utf-8") as f:
        f.write("ignore this")

    students = AdminService.get_all_students_summary(sessions_dir=str(tmp_path))
    assert len(students) == 2

    # Verificar dados do Kayzer
    kayzer = next(s for s in students if s["student_id"] == "kayzer_01")
    assert kayzer["student_name"] == "Kayzer"
    assert kayzer["streak"] == 7
    assert kayzer["total_xp"] == 350
    assert kayzer["completed_1a_count"] >= 3  # unit_intro, unit_01, unit_02
    assert kayzer["completed_1b_count"] >= 1  # unit_1b_01
    assert kayzer["memory_nodes_count"] == 2
    assert kayzer["avg_retention_pct"] > 0.8

    # Verificar dados da Anna
    anna = next(s for s in students if s["student_id"] == "anna_99")
    assert anna["student_name"] == "Anna"
    assert anna["streak"] == 2
    assert anna["memory_nodes_count"] == 0
    assert anna["avg_retention_pct"] == 0.0

def test_admin_global_kpis(tmp_path):
    """Valida o cálculo de KPIs globais da turma."""
    from datetime import datetime
    now_str = datetime.now().isoformat()
    student_1 = {
        "student_id": "s1",
        "student_name": "Aluno 1",
        "streak": 5,
        "total_xp": 100,
        "last_study_date": "2026-08-20",
        "progress_unit_intro": 1.0,
        "progress_unit_01": 1.0,
        "memory_nodes": {
            "v1": {"half_life_days": 10.0, "last_reviewed_at": now_str}
        }
    }
    with open(tmp_path / "student_s1.json", "w", encoding="utf-8") as f:
        json.dump(student_1, f)

    kpis = AdminService.get_global_kpis(sessions_dir=str(tmp_path))
    assert kpis["total_students"] == 1
    assert kpis["avg_progress_pct"] > 0.0
    assert kpis["avg_retention_pct"] > 0.8
    assert kpis["total_memory_nodes"] == 1
    assert "total_quizzes_completed" in kpis
    assert "total_reviews_completed" in kpis

def test_admin_export_report_markdown(tmp_path):
    """Valida a geração de relatório executivo em Markdown."""
    student_1 = {
        "student_id": "s1",
        "student_name": "Carlos",
        "streak": 3,
        "total_xp": 80,
        "last_study_date": "2026-08-20",
        "progress_unit_intro": 1.0,
        "memory_nodes": {}
    }
    with open(tmp_path / "student_s1.json", "w", encoding="utf-8") as f:
        json.dump(student_1, f)

    md = AdminService.export_report_markdown(sessions_dir=str(tmp_path))
    assert "# 🏛️ Relatório Executivo" in md
    assert "Carlos" in md
    assert "`s1`" in md
    assert "Indicadores Globais" in md
    assert "Roster de Alunos" in md
