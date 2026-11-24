"""Testes do pipeline automatizado de Design QA (/saebom-design-qa e CI)."""

from pathlib import Path
import re
import pytest
import yaml

from scripts.design_qa_audit import (
    contrast_ratio,
    run_design_audit,
    scan_flet_ui_invariants,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_saebom_design_qa_skill_exists_with_valid_frontmatter():
    """Valida a existência, frontmatter e referências ao StitchMCP e Brand Book v3.1."""
    skill_path = PROJECT_ROOT / ".agents" / "skills" / "saebom-design-qa" / "SKILL.md"
    assert skill_path.is_file(), f"Skill não encontrada: {skill_path}"

    content = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert match is not None, "Frontmatter YAML ausente em saebom-design-qa/SKILL.md"

    frontmatter = yaml.safe_load(match.group(1))
    assert frontmatter["name"] == "saebom-design-qa"
    assert isinstance(frontmatter["description"], str) and len(frontmatter["description"]) > 20
    assert "StitchMCP" in content
    assert "Brand Book v3.1" in content
    assert "scripts.design_qa_audit" in content


def test_wcag_contrast_ratio_math():
    """Valida a fórmula sRGB de contraste WCAG 2.1 com extremos preto/branco."""
    assert contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0, rel=1e-3)
    assert contrast_ratio("#02060F", "#02060F") == pytest.approx(1.0, rel=1e-6)


def test_run_design_audit_passes_on_repository():
    """Valida que o Design QA passa sem falhas críticas e registra advisories conhecidos."""
    report = run_design_audit(PROJECT_ROOT)
    assert report["passed"] is True, f"Falhas inesperadas: {report['failures']}"
    assert report["failures"] == []
    assert len(report["warnings"]) >= 1
    assert len(report["contrast_report"]) == 42


def test_scan_flet_ui_invariants_detects_all_regressions(tmp_path):
    """Valida detecção negativa de todas as violações Flet 0.85+ e regras do GEMINI.md."""
    bad_src = tmp_path / "src"
    bad_src.mkdir()
    bad_widget = bad_src / "bad_widget.py"
    bad_widget.write_text(
        "import flet as ft\n"
        "LEGACY_BLUE = '#004C97'\n"
        "class BadWidget(ft.Container):\n"
        "    def __init__(self, page):\n"
        "        self.page = page\n"
        "        img = ft.Image(src='branding/a.png', fit=ft.ImageFit.CONTAIN)\n"
        "        btn = ft.ElevatedButton('x')\n"
        "        txt = ft.Text('x', letter_spacing=1)\n",
        encoding="utf-8",
    )

    failures, _ = scan_flet_ui_invariants(bad_src)
    joined = "\n".join(failures)
    assert "#004C97" in joined
    assert "self.page" in joined
    assert "branding/a.png" in joined
    assert "ft.ImageFit" in joined
    assert "ft.ElevatedButton" in joined
    assert "letter_spacing=" in joined


def test_ci_workflow_integrates_design_qa_job():
    """Valida YAML do CI e presença do job dedicado design-qa."""
    ci_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    parsed = yaml.safe_load(ci_path.read_text(encoding="utf-8"))
    jobs = parsed.get("jobs", {})
    assert "design-qa" in jobs, "Job 'design-qa' ausente em .github/workflows/ci.yml"

    design_job = jobs["design-qa"]
    steps_run = "\n".join(step.get("run", "") for step in design_job.get("steps", []))
    assert "python -m scripts.design_qa_audit" in steps_run
    assert "test_design_qa_pipeline.py" in steps_run
