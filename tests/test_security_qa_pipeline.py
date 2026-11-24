"""Testes do pipeline automatizado de Security QA (/saebom-security-qa e CI)."""

from pathlib import Path
import re
import yaml

from scripts.security_qa_audit import (
    run_security_audit,
    scan_python_sast_ast,
    scan_secrets_in_files,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_saebom_security_qa_skill_exists_with_valid_frontmatter():
    """Valida a existência e o frontmatter YAML da skill /saebom-security-qa."""
    skill_path = PROJECT_ROOT / ".agents" / "skills" / "saebom-security-qa" / "SKILL.md"
    assert skill_path.is_file(), f"Skill não encontrada: {skill_path}"

    content = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert match is not None, "Frontmatter YAML ausente em saebom-security-qa/SKILL.md"

    frontmatter = yaml.safe_load(match.group(1))
    assert frontmatter["name"] == "saebom-security-qa"
    assert isinstance(frontmatter["description"], str) and len(frontmatter["description"]) > 20
    assert "scripts.security_qa_audit" in content
    assert "bandit" in content
    assert "pip-audit" in content


def test_run_security_audit_passes_on_repository():
    """Valida que a auditoria completa de segurança passa sem falhas críticas no estado atual."""
    report = run_security_audit(PROJECT_ROOT)
    assert report["passed"] is True, f"Falhas inesperadas: {report['failures']}"
    assert report["failures"] == []
    check_names = {c["name"] for c in report["checks"]}
    assert {
        "git_security_lineage",
        "zero_pii_tracked_files",
        "secret_scan",
        "python_sast_ast",
        "crypto_and_infra_hardening",
    }.issubset(check_names)


def test_scan_secrets_in_files_detects_compromised_pin_and_default_pin(tmp_path):
    """Valida detecção negativa de PIN legado comprometido e atribuição DEFAULT_PIN."""
    bad_file = tmp_path / "leaky_config.py"
    legacy_pin = "sejong" + "2026"
    bad_file.write_text(
        f'ADMIN_FALLBACK = "{legacy_pin}"\nDEFAULT_PIN = "123456"\n',
        encoding="utf-8",
    )

    findings = scan_secrets_in_files([bad_file])
    assert len(findings) >= 2
    joined = "\n".join(findings)
    assert "credencial legada comprometida" in joined
    assert "DEFAULT_PIN" in joined


def test_scan_python_sast_ast_detects_unsafe_eval_and_shell_true(tmp_path):
    """Valida detecção AST de chamadas perigosas (eval e subprocess com shell=True)."""
    unsafe_file = tmp_path / "unsafe_module.py"
    unsafe_file.write_text(
        "import subprocess\n"
        "def run_cmd(user_in):\n"
        "    eval(user_in)\n"
        "    subprocess.run(user_in, shell=True)\n",
        encoding="utf-8",
    )

    findings = scan_python_sast_ast([unsafe_file])
    assert len(findings) == 2
    joined = "\n".join(findings)
    assert "eval()" in joined
    assert "shell=True" in joined


def test_ci_workflow_integrates_security_qa_job():
    """Valida YAML do CI e presença do job dedicado security-qa com bandit e pip-audit."""
    ci_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    parsed = yaml.safe_load(ci_path.read_text(encoding="utf-8"))
    jobs = parsed.get("jobs", {})
    assert "security-qa" in jobs, "Job 'security-qa' ausente em .github/workflows/ci.yml"

    sec_job = jobs["security-qa"]
    steps_run = "\n".join(step.get("run", "") for step in sec_job.get("steps", []))
    assert "python -m scripts.security_qa_audit" in steps_run
    assert "bandit" in steps_run
    assert "pip-audit" in steps_run
    assert "test_security_qa_pipeline.py" in steps_run
