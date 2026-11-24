#!/usr/bin/env python3
"""Auditor automatizado de Security QA — Saebom Companion.

Verifica linhagem de segurança Git, proteção Zero-PII em arquivos rastreados,
ausência de segredos ou PINs legados comprometidos, análise SAST AST em Python
e conformidade de criptografia/infraestrutura (Dockerfile, docker-compose, Caddyfile).

Uso:
    python -m scripts.security_qa_audit
    python -m scripts.security_qa_audit --json
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable

import yaml

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURITY_ANCHOR_REF = "security/hardening-v0.3.2"

# Construído via join em runtime para evitar constant-folding no .pyc durante o secret scan do CI.
LEGACY_COMPROMISED_PIN = "".join(("sej", "ong", "2026"))

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("PIN padrão hardcoded (DEFAULT_PIN)", re.compile(r"\bDEFAULT_PIN\s*(?::[^=]+)?=\s*[\"'][^\"']+[\"']")),
    ("Chave estilo sk-*", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("Token GitHub PAT (ghp_*)", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("Chave Google API (AIza*)", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("Chave privada PEM", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)

PII_TRACKED_PREFIXES = (
    "data/sessions/",
    "data/telemetry/",
    "data/reports/",
    "data/cache/",
)

IGNORED_SCAN_DIRS = {"__pycache__", ".git", ".venv", "venv", ".pytest_cache", "node_modules"}
SCANNABLE_EXTENSIONS = {".py", ".yml", ".yaml", ".sh", ".json", ".toml", ".ini", ".cfg"}
SCANNABLE_NAMES = {"Dockerfile", "Caddyfile", ".dockerignore", ".env"}


@dataclass
class CheckResult:
    """Resultado estruturado de uma verificação individual de QA."""

    name: str
    status: str  # "PASS", "WARN", "FAIL"
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializa o resultado para JSON."""
        return asdict(self)


def _iter_target_files(paths: Iterable[Path]) -> list[Path]:
    """Expande diretórios e arquivos filtrando artefatos transitórios."""
    collected: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        if path.is_file():
            collected.append(path)
            continue
        for item in sorted(path.rglob("*")):
            if any(part in IGNORED_SCAN_DIRS for part in item.parts):
                continue
            if item.is_file() and (
                item.suffix.lower() in SCANNABLE_EXTENSIONS
                or item.name in SCANNABLE_NAMES
                or item.name.startswith(".env")
            ):
                collected.append(item)
    return collected


def check_git_security_lineage(project_root: Path = PROJECT_ROOT) -> CheckResult:
    """Verifica se a ref de hardening de segurança é ancestral do HEAD atual."""
    root = Path(project_root)
    if not (root / ".git").exists():
        return CheckResult(
            name="git_security_lineage",
            status="WARN",
            details=["Diretório .git ausente; checagem de linhagem ignorada."],
        )

    anchor_check = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", SECURITY_ANCHOR_REF],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if anchor_check.returncode != 0:
        return CheckResult(
            name="git_security_lineage",
            status="WARN",
            details=[
                f"Ref '{SECURITY_ANCHOR_REF}' não está disponível localmente (ex.: shallow clone no CI)."
            ],
        )

    ancestor_proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SECURITY_ANCHOR_REF, "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if ancestor_proc.returncode == 0:
        return CheckResult(
            name="git_security_lineage",
            status="PASS",
            details=[f"'{SECURITY_ANCHOR_REF}' é ancestral direto de HEAD."],
        )

    return CheckResult(
        name="git_security_lineage",
        status="FAIL",
        details=[
            f"REGRESSÃO DE LINHAGEM: '{SECURITY_ANCHOR_REF}' NÃO é ancestral de HEAD!"
        ],
    )


def check_zero_pii_tracked_files(project_root: Path = PROJECT_ROOT) -> CheckResult:
    """Garante que nenhum arquivo de sessão, telemetria, relatório, cache ou .env está rastreado."""
    root = Path(project_root)
    if not (root / ".git").exists():
        return CheckResult(
            name="zero_pii_tracked_files",
            status="WARN",
            details=["Diretório .git ausente; checagem de arquivos rastreados ignorada."],
        )

    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return CheckResult(
            name="zero_pii_tracked_files",
            status="FAIL",
            details=[f"Falha ao executar 'git ls-files': {proc.stderr.strip()}"],
        )

    violations: list[str] = []
    for raw_line in proc.stdout.splitlines():
        posix = raw_line.strip().replace("\\", "/")
        if not posix:
            continue
        filename = posix.rsplit("/", 1)[-1]
        if (
            posix.startswith(PII_TRACKED_PREFIXES)
            or posix.endswith(".jsonl")
            or filename == ".env"
            or filename.startswith(".env.")
            or filename.endswith(".env")
        ):
            violations.append(f"Arquivo sensível ou com PII rastreado no Git: {posix}")

    if violations:
        return CheckResult(name="zero_pii_tracked_files", status="FAIL", details=violations)

    return CheckResult(
        name="zero_pii_tracked_files",
        status="PASS",
        details=["0 arquivos de sessão, telemetria, relatório, cache, JSONL ou .env rastreados."],
    )


def scan_secrets_in_files(paths: Iterable[Path]) -> list[str]:
    """Varre arquivos procurando credenciais comprometidas ou segredos hardcoded."""
    findings: list[str] = []
    self_resolved = Path(__file__).resolve()

    for file_path in _iter_target_files(paths):
        resolved = file_path.resolve()
        if resolved == self_resolved:
            continue
        # Suítes de teste validam explicitamente a rejeição do PIN legado.
        if "tests" in file_path.parts and file_path.name.startswith("test_"):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(f"Erro ao ler {file_path}: {exc}")
            continue

        for lineno, line in enumerate(content.splitlines(), start=1):
            if LEGACY_COMPROMISED_PIN in line:
                findings.append(
                    f"{file_path}:{lineno}: credencial legada comprometida detectada."
                )
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{file_path}:{lineno}: {label} detectado.")

    return findings


def _is_truthy_constant(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and bool(node.value)


def _node_mentions_assets(node: ast.AST) -> bool:
    unparsed = ast.unparse(node).lower()
    return '"assets' in unparsed or "'assets" in unparsed or "/assets" in unparsed


def _is_write_open_call(call: ast.Call) -> bool:
    if len(call.args) >= 2 and isinstance(call.args[1], ast.Constant) and isinstance(call.args[1].value, str):
        return any(flag in call.args[1].value for flag in ("w", "a", "x", "+"))
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return any(flag in kw.value.value for flag in ("w", "a", "x", "+"))
    return False


def scan_python_sast_ast(paths: Iterable[Path]) -> list[str]:
    """Executa análise estática AST para chamadas Python inseguras e escrita em assets/."""
    findings: list[str] = []
    python_files = [p for p in _iter_target_files(paths) if p.suffix == ".py"]

    for py_file in python_files:
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (OSError, SyntaxError) as exc:
            findings.append(f"{py_file}: erro de parsing AST ({exc}).")
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            func_name = ast.unparse(node.func)
            if func_name in {"eval", "exec"}:
                findings.append(f"{py_file}:{node.lineno}: chamada insegura '{func_name}()'.")
            elif func_name in {"pickle.load", "pickle.loads"}:
                findings.append(f"{py_file}:{node.lineno}: desserialização insegura '{func_name}()'.")
            elif func_name == "yaml.load":
                has_safe_loader = any(
                    kw.arg == "Loader" and "SafeLoader" in ast.unparse(kw.value)
                    for kw in node.keywords
                )
                if not has_safe_loader:
                    findings.append(
                        f"{py_file}:{node.lineno}: 'yaml.load()' sem SafeLoader (use yaml.safe_load)."
                    )
            elif func_name.startswith("subprocess.") and any(
                kw.arg == "shell" and _is_truthy_constant(kw.value) for kw in node.keywords
            ):
                findings.append(f"{py_file}:{node.lineno}: '{func_name}()' com shell=True.")
            elif func_name == "open" and node.args and _is_write_open_call(node):
                if _node_mentions_assets(node.args[0]):
                    findings.append(
                        f"{py_file}:{node.lineno}: escrita em diretório read-only assets/ detectada."
                    )

    return findings


def _check_docker_compose(root: Path, failures: list[str]) -> None:
    compose_path = root / "docker-compose.yml"
    if not compose_path.is_file():
        failures.append("docker-compose.yml ausente na raiz.")
        return

    raw = compose_path.read_text(encoding="utf-8")
    if "no-new-privileges:true" not in raw:
        failures.append("docker-compose.yml deve definir 'no-new-privileges:true'.")
    if "SAEBOM_ADMIN_PIN=${SAEBOM_ADMIN_PIN:?" not in raw:
        failures.append("docker-compose.yml deve exigir 'SAEBOM_ADMIN_PIN=${SAEBOM_ADMIN_PIN:?...}' (fail-closed).")

    parsed = yaml.safe_load(raw) or {}
    app_ports = parsed.get("services", {}).get("app", {}).get("ports", []) or []
    for port_entry in app_ports:
        if "8554" in str(port_entry):
            failures.append(f"docker-compose.yml publica porta interna 8554 em services.app.ports ({port_entry}).")


def _check_caddyfile(root: Path, failures: list[str]) -> None:
    caddy_path = root / "Caddyfile"
    if not caddy_path.is_file():
        failures.append("Caddyfile ausente na raiz.")
        return

    raw = caddy_path.read_text(encoding="utf-8")
    http_match = re.search(r":80\s*\{(.*?)\n\}", raw, re.DOTALL)
    if not http_match:
        failures.append("Caddyfile deve isolar explicitamente o bloco HTTP ':80'.")
    elif "Strict-Transport-Security" in http_match.group(1):
        failures.append("Caddyfile emite HSTS no bloco HTTP ':80' (violação RFC 6797 §7.2).")

    https_idx = raw.find("saebomcompanion.duckdns.org {")
    if https_idx == -1:
        failures.append("Caddyfile não declara o bloco HTTPS 'saebomcompanion.duckdns.org {'.")
        return

    https_block = raw[https_idx:]
    required_caddy_tokens = (
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "'wasm-unsafe-eval'",
        "https://www.gstatic.com",
        "worker-src 'self' blob:",
        "media-src 'self' data: blob:",
        "-Server",
    )
    for token in required_caddy_tokens:
        if token not in https_block:
            failures.append(f"Caddyfile HTTPS sem diretiva de segurança obrigatória: {token}")


def check_crypto_and_infra_hardening(project_root: Path = PROJECT_ROOT) -> CheckResult:
    """Valida controles criptográficos em Python e hardening de container/proxy."""
    root = Path(project_root)
    failures: list[str] = []

    services_path = root / "src" / "services.py"
    if not services_path.is_file():
        failures.append("src/services.py não encontrado.")
    else:
        services_txt = services_path.read_text(encoding="utf-8")
        compare_count = services_txt.count("hmac.compare_digest")
        if compare_count < 2:
            failures.append(
                f"src/services.py deve usar hmac.compare_digest em auth e recovery (encontrado {compare_count}x)."
            )

    dockerignore_path = root / ".dockerignore"
    if not dockerignore_path.is_file():
        failures.append(".dockerignore ausente na raiz.")
    else:
        di_txt = dockerignore_path.read_text(encoding="utf-8")
        for req in (".env", "data/sessions/", "data/telemetry/", "data/reports/", "data/cache/", "*.jsonl"):
            if req not in di_txt:
                failures.append(f".dockerignore sem proteção obrigatória para '{req}'.")

    dockerfile_path = root / "Dockerfile"
    if not dockerfile_path.is_file():
        failures.append("Dockerfile ausente na raiz.")
    elif "USER saebomuser" not in dockerfile_path.read_text(encoding="utf-8"):
        failures.append("Dockerfile deve configurar 'USER saebomuser' (execução não-root).")

    _check_docker_compose(root, failures)
    _check_caddyfile(root, failures)

    oci_script = root / "scripts" / "setup_oci_server.sh"
    if oci_script.is_file() and "8554" in oci_script.read_text(encoding="utf-8"):
        failures.append("scripts/setup_oci_server.sh ainda referencia/abre porta interna 8554.")

    if failures:
        return CheckResult(name="crypto_and_infra_hardening", status="FAIL", details=failures)

    return CheckResult(
        name="crypto_and_infra_hardening",
        status="PASS",
        details=[
            "hmac.compare_digest, .dockerignore, Dockerfile (saebomuser), docker-compose.yml, Caddyfile (:80 vs HTTPS + CSP) e setup_oci_server.sh conformes."
        ],
    )


def detect_optional_external_scanners() -> dict[str, bool]:
    """Detecta scanners de segurança externos instalados no ambiente atual."""
    return {
        tool: shutil.which(tool) is not None
        for tool in ("bandit", "pip-audit", "trivy", "gitleaks")
    }


def run_security_audit(project_root: Path | str | None = None) -> dict[str, Any]:
    """Executa todas as verificações locais de Security QA e retorna relatório consolidado."""
    root = Path(project_root) if project_root else PROJECT_ROOT

    lineage = check_git_security_lineage(root)
    zero_pii = check_zero_pii_tracked_files(root)
    hardening = check_crypto_and_infra_hardening(root)

    secret_targets = [
        root / "src",
        root / "main.py",
        root / "scripts",
        root / "docker-compose.yml",
        root / "Caddyfile",
    ]
    secret_hits = scan_secrets_in_files(secret_targets)
    secret_check = CheckResult(
        name="secret_scan",
        status="FAIL" if secret_hits else "PASS",
        details=secret_hits or ["Nenhum segredo ou PIN comprometido encontrado."],
    )

    sast_hits = scan_python_sast_ast([root / "src", root / "main.py"])
    sast_check = CheckResult(
        name="python_sast_ast",
        status="FAIL" if sast_hits else "PASS",
        details=sast_hits or ["Nenhuma chamada insegura (eval/exec/pickle/yaml.load/shell=True/assets write) detectada."],
    )

    checks = [lineage, zero_pii, secret_check, sast_check, hardening]
    failures: list[str] = []
    warnings: list[str] = []

    for item in checks:
        if item.status == "FAIL":
            failures.extend(f"[{item.name}] {d}" for d in item.details)
        elif item.status == "WARN":
            warnings.extend(f"[{item.name}] {d}" for d in item.details)

    external_tools = detect_optional_external_scanners()
    missing_tools = [name for name, installed in external_tools.items() if not installed]
    if missing_tools:
        warnings.append(
            "[external_scanners] Ferramentas opcionais não instaladas localmente (executadas no CI): "
            + ", ".join(missing_tools)
        )

    return {
        "passed": len(failures) == 0,
        "checks": [c.to_dict() for c in checks],
        "failures": failures,
        "warnings": warnings,
        "external_tools": external_tools,
    }


def _print_report(report: dict[str, Any]) -> None:
    print("=" * 72)
    print(" 🛡️ SAEBOM COMPANION — AUDITORIA DE SECURITY QA")
    print("=" * 72)
    for check in report["checks"]:
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(check["status"], "•")
        print(f"{icon} [{check['status']}] {check['name']}")
        for detail in check["details"]:
            print(f"   - {detail}")

    print("-" * 72)
    print("Scanners externos no PATH:", report["external_tools"])
    if report["warnings"]:
        print("\nAdvisories / Warnings:")
        for warning in report["warnings"]:
            print(f"  ⚠️ {warning}")

    if report["failures"]:
        print("\nFalhas Críticas:")
        for failure in report["failures"]:
            print(f"  ❌ {failure}")
        print("\nRESULTADO: REPROVADO (exit code 1)")
    else:
        print("\nRESULTADO: APROVADO (exit code 0)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auditoria automatizada de Security QA do Saebom Companion")
    parser.add_argument("--json", action="store_true", help="Imprime relatório em formato JSON")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT, help="Diretório raiz do projeto")
    args = parser.parse_args(argv)

    report = run_security_audit(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_report(report)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
