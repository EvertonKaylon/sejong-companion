"""Testes de Identidade do Aluno: Normalização PascalCase, Chave NFKC e Fusão de Sessões.

Valida conformidade com a diretriz pedagógica:
- Normalização em Title Case / PascalCase sem corromper Hangul nem nomes compostos com hífen/apóstrofo
- Busca case-insensitive via chave canônica NFKC (normalize_name_key)
- Fusão atômica de sessões e histórico de estudo (merge_session_data)
- Resolução e persistência de sessões no ProgressService e deduplicação no AdminService
"""

import json
import os
import pytest

from src.services import (
    canonicalize_student_name,
    normalize_name_key,
    merge_session_data,
    ProgressService,
    AdminService,
)


def test_canonicalize_student_name_latin():
    """Valida formatação de nomes em alfabeto latino para PascalCase/TitleCase."""
    assert canonicalize_student_name("everton kaylon") == "Everton Kaylon"
    assert canonicalize_student_name("EVERTON KAYLON") == "Everton Kaylon"
    assert canonicalize_student_name("eVeRtOn   kAyLoN") == "Everton Kaylon"
    assert canonicalize_student_name("   marianelly    seitz   arnold  ") == "Marianelly Seitz Arnold"
    assert canonicalize_student_name("carlos d'angelo") == "Carlos D'Angelo"
    assert canonicalize_student_name("ana-paula silva") == "Ana-Paula Silva"
    # Fallbacks e termos legados devem retornar "Estudante Saebom"
    assert canonicalize_student_name("") == "Estudante Saebom"
    assert canonicalize_student_name(None) == "Estudante Saebom"
    assert canonicalize_student_name("estudante saebom") == "Estudante Saebom"
    assert canonicalize_student_name("estudante sejong") == "Estudante Saebom"


def test_canonicalize_student_name_korean():
    """Valida preservação estrita de nomes em Hangul sem corrupção Unicode."""
    assert canonicalize_student_name("김철수") == "김철수"
    assert canonicalize_student_name("홍길동") == "홍길동"
    assert canonicalize_student_name("안나") == "안나"
    assert canonicalize_student_name("  김철수  ") == "김철수"
    assert canonicalize_student_name("홍길동 (Hong Gildong)") == "홍길동 (Hong Gildong)"


def test_normalize_name_key():
    """Valida geração de chave canônica NFKC em minúsculas para busca case-insensitive."""
    assert normalize_name_key("Everton Kaylon") == "everton kaylon"
    assert normalize_name_key("EVERTON KAYLON") == "everton kaylon"
    assert normalize_name_key("  everton   kaylon  ") == "everton kaylon"
    assert normalize_name_key("Carlos D'Angelo") == "carlos d'angelo"
    assert normalize_name_key("김철수") == "김철수"
    assert normalize_name_key("") == ""
    assert normalize_name_key(None) == ""


def test_merge_session_data():
    """Valida fusão atômica de duas sessões de um mesmo aluno."""
    session_a = {
        "student_id": "std_1",
        "student_name": "Everton Kaylon",
        "study_dates": ["2026-08-20", "2026-08-21"],
        "streak": 2,
        "total_xp": 100,
        "progress_unit_01": 0.8,
        "unlocked_unit_01": True,
        "unlocked_unit_02": False,
        "memory_nodes": {
            "node_1": {"half_life": 5.0, "last_reviewed": "2026-08-20"},
        },
    }
    session_b = {
        "student_id": "std_2",
        "student_name": "EVERTON KAYLON",
        "study_dates": ["2026-08-21", "2026-08-22"],
        "streak": 3,
        "total_xp": 150,
        "progress_unit_01": 1.0,
        "progress_unit_02": 0.3,
        "unlocked_unit_01": True,
        "unlocked_unit_02": True,
        "memory_nodes": {
            "node_1": {"half_life": 8.0, "last_reviewed": "2026-08-22"},
            "node_2": {"half_life": 4.0, "last_reviewed": "2026-08-22"},
        },
    }

    merged = merge_session_data(session_a, session_b)

    assert set(merged["study_dates"]) == {"2026-08-20", "2026-08-21", "2026-08-22"}
    assert merged["streak"] == 3
    assert merged["total_xp"] == 150
    assert merged["progress_unit_01"] == 1.0
    assert merged["progress_unit_02"] == 0.3
    assert merged["unlocked_unit_02"] is True
    assert merged["memory_nodes"]["node_1"]["half_life"] == 8.0
    assert "node_2" in merged["memory_nodes"]


def test_resolve_or_create_student_case_insensitive(tmp_path):
    """Valida resolução e fusão de sessões por nome case-insensitive em disco."""
    sessions_dir = str(tmp_path)

    # 1. Primeiro cadastro com lowercase
    id1, data1 = ProgressService.resolve_or_create_student("everton kaylon", sessions_dir=sessions_dir)
    assert data1["student_name"] == "Everton Kaylon"

    # Simular estudo registrado
    data1["progress_unit_01"] = 1.0
    data1["total_xp"] = 100
    ProgressService._save_to_disk(id1, data1, sessions_dir=sessions_dir)

    # 2. Re-autenticação com UPPERCASE: deve resolver para o mesmo student_id e carregar o progresso
    id2, data2 = ProgressService.resolve_or_create_student("EVERTON KAYLON", sessions_dir=sessions_dir)
    assert id2 == id1
    assert data2["student_name"] == "Everton Kaylon"
    assert data2.get("progress_unit_01") == 1.0
    assert data2.get("total_xp") == 100


def test_admin_service_deduplication(tmp_path):
    """Valida desduplicação de múltiplos arquivos do mesmo aluno com casings diferentes no resumo administrativo."""
    sessions_dir = str(tmp_path)

    # Criar arquivo 1: everton kaylon
    file1 = os.path.join(sessions_dir, "student_1.json")
    with open(file1, "w", encoding="utf-8") as f:
        json.dump({
            "student_id": "student_1",
            "student_name": "everton kaylon",
            "total_xp": 50,
            "streak": 2,
            "study_dates": ["2026-08-20"],
            "progress_unit_01": 0.5,
        }, f)

    # Criar arquivo 2: EVERTON KAYLON
    file2 = os.path.join(sessions_dir, "student_2.json")
    with open(file2, "w", encoding="utf-8") as f:
        json.dump({
            "student_id": "student_2",
            "student_name": "EVERTON KAYLON",
            "total_xp": 120,
            "streak": 4,
            "study_dates": ["2026-08-21"],
            "progress_unit_01": 1.0,
        }, f)

    summary = AdminService.get_all_students_summary(sessions_dir=sessions_dir)

    # Deve conter exatamente 1 registro consolidado para Everton Kaylon
    matching = [s for s in summary if normalize_name_key(s["student_name"]) == "everton kaylon"]
    assert len(matching) == 1
    consolidated = matching[0]
    assert consolidated["total_xp"] == 120
    assert consolidated["streak"] == 4


def test_progress_service_set_student_name_canonicalizes_and_persists(tmp_path):
    """Valida que ProgressService.set_student_name canonicaliza, persiste em disco e sincroniza."""
    class MockClientStorage:
        def __init__(self):
            self.store = {}
        def get(self, key):
            return self.store.get(key)
        def set(self, key, value):
            self.store[key] = value

    class MockPage:
        def __init__(self):
            self.client_storage = MockClientStorage()
            self.session = None

    ProgressService._sessions.clear()
    ProgressService.set_file_path_override(str(tmp_path / "student_case.json"))
    try:
        page = MockPage()
        ps = ProgressService(page)
        result = ps.set_student_name("  everton kaylon ")

        assert result == "Everton Kaylon"
        assert ps.get_student_name() == "Everton Kaylon"
        assert page.client_storage.get("saebom_student_name") == "Everton Kaylon"
        assert page.client_storage.get("sejong_student_name") == "Everton Kaylon"

        # Recarregar do disco para garantir persistência canônica
        ProgressService._sessions.clear()
        ps2 = ProgressService(page)
        assert ps2.get_student_name() == "Everton Kaylon"
    finally:
        ProgressService._sessions.clear()
        ProgressService.set_file_path_override(None)
