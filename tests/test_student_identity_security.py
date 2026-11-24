"""Testes de segurança e hardening para identidade e recuperação de alunos:
- Separação estrita entre Student ID (identificador público) e Recovery Key (segredo)
- Armazenamento em disco exclusivo de hash salted (SHA-256), sem segredo em texto plano
- Proteção contra Account Takeover usando apenas Student ID
- Verificação de integridade e restauração autorizada
"""

import json
import pytest
from src.services import ProgressService


@pytest.fixture(autouse=True)
def clean_progress_sessions():
    """Garante isolamento de memória entre testes."""
    ProgressService._sessions.clear()
    ProgressService.set_file_path_override(None)
    yield
    ProgressService._sessions.clear()
    ProgressService.set_file_path_override(None)


def test_recovery_code_generation():
    """Valida formato e entropia do código de recuperação."""
    code1 = ProgressService.generate_recovery_code()
    code2 = ProgressService.generate_recovery_code()
    assert code1 != code2
    parts = code1.split("-")
    assert len(parts) == 3
    assert all(len(p) == 4 for p in parts)


def test_student_creation_stores_only_salted_hash(tmp_path):
    """Valida que o segredo de recuperação não é gravado em texto plano no disco."""
    sess_dir = str(tmp_path)
    file_path = tmp_path / "student_sec_01.json"

    # Configurar ProgressService para usar arquivo temporário
    ProgressService.set_file_path_override(str(file_path))
    try:
        ps = ProgressService()
        ps.set_student_name("Marina Silva")
        secret_key = ps.get_or_create_recovery_code()

        assert secret_key != ""
        assert len(secret_key) == 14  # XXXX-XXXX-XXXX

        # Ler arquivo no disco
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # O segredo em texto plano NUNCA deve estar no disco
        assert secret_key not in json.dumps(data)
        # O hash e o salt devem estar presentes
        assert "recovery_salt" in data
        assert "recovery_hash" in data
        assert len(data["recovery_salt"]) >= 16
        assert len(data["recovery_hash"]) == 64  # SHA-256 hex length
    finally:
        ProgressService.set_file_path_override(None)


def test_student_recovery_authorized(tmp_path):
    """Valida restauração de perfil bem-sucedida quando fornecidos ID e Recovery Key corretos."""
    sess_dir = str(tmp_path)
    s_id = "student_rec_success"
    file_path = tmp_path / f"{s_id}.json"

    ProgressService.set_file_path_override(str(file_path))
    try:
        ps = ProgressService()
        ps.set_student_name("Carlos Alberto")
        ps.save_progress("unit_intro", 1.0)
        secret_key = ps.get_or_create_recovery_code()
    finally:
        ProgressService.set_file_path_override(None)

    # Tentar restaurar com as credenciais corretas
    success, restored_id, restored_name, msg = ProgressService.verify_and_restore_student(
        s_id, secret_key, sessions_dir=sess_dir
    )
    assert success is True
    assert restored_id == s_id
    assert restored_name == "Carlos Alberto"


def test_student_recovery_rejected_wrong_secret(tmp_path):
    """Valida que possuir apenas o Student ID NÃO permite recuperar ou assumir o perfil."""
    sess_dir = str(tmp_path)
    s_id = "student_victim_01"
    file_path = tmp_path / f"{s_id}.json"

    ProgressService.set_file_path_override(str(file_path))
    try:
        ps = ProgressService()
        ps.set_student_name("Alice Souza")
        ps.save_progress("unit_intro", 1.0)
        real_secret = ps.get_or_create_recovery_code()
    finally:
        ProgressService.set_file_path_override(None)

    # 1. Tentar com chave incorreta
    success, _, _, msg = ProgressService.verify_and_restore_student(
        s_id, "WRONG-KEY1-2345", sessions_dir=sess_dir
    )
    assert success is False
    assert "incorreta" in msg.lower()

    # 2. Tentar com chave vazia
    success, _, _, msg = ProgressService.verify_and_restore_student(
        s_id, "", sessions_dir=sess_dir
    )
    assert success is False


def test_student_recovery_legacy_profile_fail_closed(tmp_path):
    """Valida que perfis legados sem recovery_hash não são entregues sem verificação."""
    sess_dir = str(tmp_path)
    s_id = "student_legacy_no_salt"
    file_path = tmp_path / f"{s_id}.json"

    # Criar sessão legada sem recovery_salt / recovery_hash
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"student_id": s_id, "student_name": "Antigo Aluno", "progress_unit_intro": 1.0}, f)

    success, _, _, msg = ProgressService.verify_and_restore_student(
        s_id, "ANYK-EY12-3456", sessions_dir=sess_dir
    )
    assert success is False
    assert "não possui chave" in msg.lower() or "suporte" in msg.lower()
