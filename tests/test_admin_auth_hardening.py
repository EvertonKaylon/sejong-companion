"""Testes de segurança e hardening para autenticação administrativa:
- Rate Limiting e Brute-Force Lockout
- Proteção contra Timing Attacks (hmac.compare_digest)
- Gestão de Sessões Temporárias e Expiração
- Revogação de Sessão (Logout)
"""

import time
import pytest
from src.services import AdminService


@pytest.fixture(autouse=True)
def reset_admin_state(monkeypatch):
    monkeypatch.delenv("SAEBOM_ADMIN_PIN", raising=False)
    monkeypatch.setenv("SEJONG_ADMIN_PIN", "sejong_secure_pin_2026")
    AdminService.reset_rate_limit("test_client")
    AdminService.reset_rate_limit("client_b")
    AdminService._active_tokens.clear()
    yield
    AdminService.reset_rate_limit("test_client")
    AdminService.reset_rate_limit("client_b")
    AdminService._active_tokens.clear()


def test_admin_successful_login():
    """Valida login bem-sucedido retornando token de sessão válido."""
    success, token, msg = AdminService.login("sejong_secure_pin_2026", client_key="test_client")
    assert success is True
    assert token is not None
    assert len(token) >= 32
    assert "sucesso" in msg.lower()
    assert AdminService.validate_session(token) is True


def test_admin_rate_limiting_tier_1():
    """Valida bloqueio temporário após 5 tentativas incorretas."""
    client = "test_client"

    # 4 tentativas incorretas não devem bloquear
    for i in range(4):
        success, token, msg = AdminService.login("wrong_pin", client_key=client)
        assert success is False
        assert token is None
        assert AdminService.get_lockout_remaining(client) == 0.0

    # 5ª tentativa incorreta deve disparar o lockout tier 1
    success, token, msg = AdminService.login("wrong_pin", client_key=client)
    assert success is False
    assert "bloqueio" in msg.lower() or "tentativas" in msg.lower()
    assert AdminService.get_lockout_remaining(client) > 0.0

    # Próxima tentativa (mesmo com PIN correto) deve ser rejeitada durante o lockout
    success, token, msg = AdminService.login("sejong_secure_pin_2026", client_key=client)
    assert success is False
    assert "bloqueio" in msg.lower() or "muitas tentativas" in msg.lower()


def test_admin_rate_limiting_independent_clients():
    """Valida que o lockout de um cliente não bloqueia outros clientes."""
    client_a = "test_client"
    client_b = "client_b"

    # Bloquear cliente A
    for _ in range(5):
        AdminService.login("wrong_pin", client_key=client_a)
    assert AdminService.get_lockout_remaining(client_a) > 0.0

    # Cliente B deve conseguir logar normalmente
    success, token, msg = AdminService.login("sejong_secure_pin_2026", client_key=client_b)
    assert success is True
    assert token is not None


def test_admin_rate_limiting_reset_on_success():
    """Valida que tentativas incorretas acumuladas são zeradas após um login com sucesso."""
    client = "test_client"

    # 3 falhas
    for _ in range(3):
        AdminService.login("wrong_pin", client_key=client)

    # 1 sucesso
    success, token, msg = AdminService.login("sejong_secure_pin_2026", client_key=client)
    assert success is True

    # Mais 3 falhas não devem causar lockout (pois o contador foi resetado)
    for _ in range(3):
        success, token, msg = AdminService.login("wrong_pin", client_key=client)
        assert success is False
        assert AdminService.get_lockout_remaining(client) == 0.0


def test_admin_session_expiration():
    """Valida expiração de tokens de sessão temporários."""
    success, token, _ = AdminService.login("sejong_secure_pin_2026", client_key="test_client")
    assert success is True
    assert AdminService.validate_session(token) is True

    # Forçar expiração do token retroagindo o timestamp
    AdminService._active_tokens[token] = time.time() - 10.0
    assert AdminService.validate_session(token) is False


def test_admin_session_revocation():
    """Valida revogação de sessão (logout)."""
    success, token, _ = AdminService.login("sejong_secure_pin_2026", client_key="test_client")
    assert success is True
    assert AdminService.validate_session(token) is True

    # Revogar (logout)
    AdminService.revoke_session(token)
    assert AdminService.validate_session(token) is False
    assert AdminService.validate_session(None) is False
    assert AdminService.validate_session("") is False


def test_resolve_admin_client_key_isolates_sessions_without_global_fallback():
    """Valida que _resolve_admin_client_key isola páginas distintas e respeita a ordem de prioridade."""
    from src.views.admin_view import _resolve_admin_client_key

    class BarePage:
        pass

    p1 = BarePage()
    p2 = BarePage()
    k1 = _resolve_admin_client_key(p1)
    k2 = _resolve_admin_client_key(p2)

    assert k1 != "admin_client"
    assert k2 != "admin_client"
    assert k1.startswith("anon_")
    assert k2.startswith("anon_")
    assert k1 != k2
    # Chamadas subsequentes na mesma página preservam a chave em cache
    assert _resolve_admin_client_key(p1) == k1

    # Bloqueio de p1 não pode afetar p2
    for _ in range(5):
        AdminService.login("wrong_pin", client_key=k1)
    assert AdminService.get_lockout_remaining(k1) > 0.0
    assert AdminService.get_lockout_remaining(k2) == 0.0
    ok, _, _ = AdminService.login("sejong_secure_pin_2026", client_key=k2)
    assert ok is True
    AdminService.reset_rate_limit(k1)
    AdminService.reset_rate_limit(k2)

    # Ordem de prioridade: client_ip > session_id > _saebom_student_id/_sejong_student_id > anon
    p_std = BarePage()
    p_std._sejong_student_id = "student_legacy"
    assert _resolve_admin_client_key(p_std) == "std_student_legacy"
    p_std._saebom_student_id = "student_new"
    assert _resolve_admin_client_key(p_std) == "std_student_new"
    p_std.session_id = "sess_abc"
    assert _resolve_admin_client_key(p_std) == "sess_sess_abc"
    p_std.client_ip = "203.0.113.42"
    assert _resolve_admin_client_key(p_std) == "ip_203.0.113.42"
