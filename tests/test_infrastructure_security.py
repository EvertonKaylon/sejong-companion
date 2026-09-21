"""Suíte de Testes de Segurança de Infraestrutura e Conformidade OWASP / MITRE ATT&CK.

Valida:
1. .dockerignore: Prevenção de vazamento de segredos, dados mutáveis e artefatos (OWASP A05 / MITRE T1552, T1005).
2. Dockerfile: Princípio do menor privilégio com usuário não-root saebomuser (OWASP A05 / MITRE T1068, T1611).
3. Caddyfile: Cabeçalhos defensivos de segurança (CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Permissions-Policy).
4. docker-compose.yml: Flags de isolamento de privilégios (no-new-privileges) e volumes de dados.
5. Telemetry & Auditoria: Log estruturado de eventos de segurança durante falhas de autenticação (OWASP A09 / MITRE T1070).
6. Sanitização de Anúncios: Limitação de tamanho e expurgo de caracteres nulos (OWASP A03, A04 / MITRE T1499).
"""

import os
import pytest
from src.services import AdminService, TelemetryService, AnnouncementService
from src import __version__

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_dockerignore_prevents_secret_and_data_leakage():
    """Valida que o .dockerignore existe e protege todos os segredos e dados de alunos."""
    dockerignore_path = os.path.join(PROJECT_ROOT, ".dockerignore")
    assert os.path.exists(dockerignore_path), ".dockerignore não encontrado na raiz!"

    with open(dockerignore_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Padrões obrigatórios de bloqueio
    required_patterns = [
        ".env",
        ".git",
        "data/sessions/",
        "data/telemetry/",
        "data/reports/",
        "data/cache/",
        "*.jsonl",
        "*.tmp",
        ".pytest_cache",
        "scratch/",
    ]
    for pattern in required_patterns:
        assert pattern in content, f"Padrão de segurança ausente no .dockerignore: {pattern}"


def test_dockerfile_configures_non_root_user():
    """Valida que o Dockerfile define um usuário não-privilegiado (não executa como root)."""
    dockerfile_path = os.path.join(PROJECT_ROOT, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile não encontrado na raiz!"

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    has_user_directive = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("USER ") and "saebomuser" in stripped:
            has_user_directive = True
            break

    assert has_user_directive, "Dockerfile deve conter 'USER saebomuser' para mitigar Container Escape (MITRE T1611)"


def test_caddyfile_contains_owasp_security_headers():
    """Valida a presença dos cabeçalhos recomendados pela OWASP no Caddyfile."""
    caddyfile_path = os.path.join(PROJECT_ROOT, "Caddyfile")
    assert os.path.exists(caddyfile_path), "Caddyfile não encontrado na raiz!"

    with open(caddyfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Cabeçalhos obrigatórios da OWASP
    assert "Content-Security-Policy" in content, "Falta Content-Security-Policy no Caddyfile"
    assert "X-Content-Type-Options" in content and "nosniff" in content
    assert "X-Frame-Options" in content and "DENY" in content
    assert "Strict-Transport-Security" in content
    assert "Permissions-Policy" in content
    assert "-Server" in content, "Caddyfile deve remover o cabeçalho 'Server' para ofuscação"

    # Governança de marca: Proibição estrita do nome legado
    assert "sejong" not in content.lower(), "Violação de Rebranding: termo proibido detectado no Caddyfile!"


def test_docker_compose_security_options():
    """Valida opções de isolamento de privilégios e persistência no docker-compose.yml."""
    compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml não encontrado na raiz!"

    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "no-new-privileges:true" in content, "docker-compose deve conter 'no-new-privileges:true'"
    assert "announcements.json" in content, "docker-compose deve mapear volume para announcements.json"


def test_admin_auth_records_security_audit_events(monkeypatch, tmp_path):
    """Valida que falhas de autenticação e lockouts geram eventos de auditoria de segurança no TelemetryService."""
    monkeypatch.setattr(TelemetryService, "_get_telemetry_dir", lambda: str(tmp_path))
    monkeypatch.setenv("SAEBOM_ADMIN_PIN", "correct_pin_456")
    monkeypatch.delenv("SEJONG_ADMIN_PIN", raising=False)

    client_key = "test_audit_client_99"
    AdminService.reset_rate_limit(client_key)

    # 1. Tentativa com PIN errado
    success, token, msg = AdminService.login("wrong_pin", client_key=client_key)
    assert success is False

    # Verificar se o log de auditoria foi gravado
    events = TelemetryService.get_events(session_id=f"audit_{client_key}")
    assert len(events) >= 1
    assert events[-1].event_type == "security_audit"
    assert events[-1].item_id == "login_failed"
    assert events[-1].payload.get("action") == "failed_attempt"
    # Garantir Zero PII: o PIN errado não deve constar no payload
    assert "wrong_pin" not in str(events[-1].payload)

    # 2. Forçar até o Lockout Tier 1 (5 tentativas)
    for _ in range(4):
        AdminService.login("wrong_pin", client_key=client_key)

    events_after = TelemetryService.get_events(session_id=f"audit_{client_key}")
    lockout_events = [e for e in events_after if e.item_id == "lockout_tier1"]
    assert len(lockout_events) >= 1
    assert lockout_events[0].payload.get("action") == "lockout_tier1"

    # Reset & Limpeza de telemetria de teste
    AdminService.reset_rate_limit(client_key)
    TelemetryService.clear_events(session_id=f"audit_{client_key}")


def test_announcement_service_enforces_length_limits_and_null_byte_sanitization(tmp_path, monkeypatch):
    """Valida que o AnnouncementService trunca entradas longas e remove caracteres nulos sem sujar os dados reais."""
    temp_storage = tmp_path / "announcements.json"
    monkeypatch.setattr(AnnouncementService, "_get_data_path", lambda: str(temp_storage))

    long_title = "A" * 200
    long_content = "B" * 1500
    author_with_null = "Professora\x00Hacker"

    ann = AnnouncementService.post_announcement(
        title=long_title,
        content=long_content,
        author=author_with_null,
    )
    assert ann is not None
    assert len(ann["title"]) == AnnouncementService.MAX_TITLE_LENGTH
    assert len(ann["content"]) == AnnouncementService.MAX_CONTENT_LENGTH
    assert "\x00" not in ann["author"]
    assert ann["author"] == "ProfessoraHacker"

