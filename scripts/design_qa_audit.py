#!/usr/bin/env python3
"""Auditor automatizado de Design QA — Saebom Companion (Brand Book v3.1).

Verifica sincronização entre DESIGN.md e src/theme.py, razões de contraste WCAG 2.1,
invariantes Flet 0.85+ via AST/regex (prevenção de BUG-02, BUG-03, BUG-05, BUG-11 e
regra de self.page), proibição do termo legado na UI e integridade de fontes/assets.

Uso:
    python -m scripts.design_qa_audit
    python -m scripts.design_qa_audit --json
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.theme import Colors, get_theme_colors  # noqa: E402

EXPECTED_BRANDING_FILES: tuple[str, ...] = (
    "saebom_logo_dark.svg",
    "saebom_logo_dark.png",
    "saebom_logo_dark_solid.png",
    "saebom_logo_light.svg",
    "saebom_logo_light.png",
    "saebom_logo_light_solid.png",
    "saebom_logo_horizontal_dark.svg",
    "saebom_logo_horizontal_dark.png",
    "saebom_logo_horizontal_dark_solid.png",
    "saebom_logo_horizontal_light.svg",
    "saebom_logo_horizontal_light.png",
    "saebom_logo_horizontal_light_solid.png",
    "symbol_expansion_rings.svg",
    "symbol_expansion_rings.png",
    "app_icon.svg",
    "app_icon_512.png",
    "app_icon_192.png",
    "favicon_32.png",
    "favicon_16.png",
    "favicon.ico",
    "splash_banner.png",
)

REQUIRED_LOCAL_FONTS: tuple[str, ...] = (
    "Pretendard-Regular.otf",
    "Pretendard-Bold.otf",
    "KyoboHandwriting2025lyb.otf",
)

FLET_CONTROL_BASES = {
    "ft.Control",
    "ft.Container",
    "ft.Column",
    "ft.Row",
    "ft.Stack",
    "ft.AlertDialog",
    "ft.View",
    "ft.UserControl",
    "Control",
    "Container",
    "Column",
    "Row",
    "Stack",
    "AlertDialog",
    "View",
    "UserControl",
}

HEX_CONCAT_RE = re.compile(
    r'(?:colors\s*\[[^\]]+\]|Colors\.[A-Z0-9_]+)\s*\+\s*["\'][0-9A-Fa-f]{2}["\']'
)
HEX_FSTRING_RE = re.compile(
    r'f["\']\{[^}]*(?:colors|Colors)[^}]*\}[0-9A-Fa-f]{2}["\']'
)
SAMPLE_CHARS_LEGACY_RE = re.compile(r'sample_chars\s*=\s*\[[^\]]*(?:"세"|\'세\'|"종"|\'종\')[^\]]*\]')


@dataclass
class CheckResult:
    """Resultado estruturado de uma verificação de Design QA."""

    name: str
    status: str  # "PASS", "WARN", "FAIL"
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializa o resultado para JSON."""
        return asdict(self)


def relative_luminance(hex_color: str) -> float:
    """Calcula a luminância relativa sRGB (WCAG 2.1) para uma cor #RRGGBB."""
    clean = hex_color.strip().lstrip("#")
    if len(clean) == 8:
        clean = clean[2:]
    if len(clean) != 6:
        raise ValueError(f"Cor hexadecimal inválida para cálculo WCAG: {hex_color!r}")

    channels = [int(clean[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def _linearize(value: float) -> float:
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    r, g, b = (_linearize(c) for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Calcula a razão de contraste WCAG 2.1 entre primeiro plano e fundo."""
    lum_1 = relative_luminance(fg_hex)
    lum_2 = relative_luminance(bg_hex)
    lighter = max(lum_1, lum_2)
    darker = min(lum_1, lum_2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_design_md_tokens(design_md_path: Path) -> dict[str, str]:
    """Lê o frontmatter YAML de DESIGN.md e retorna o mapa de tokens de cor."""
    content = Path(design_md_path).read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise ValueError(f"Frontmatter YAML não encontrado em {design_md_path}")

    parsed = yaml.safe_load(match.group(1)) or {}
    raw_colors = parsed.get("colors", {})
    return {str(k): str(v).upper() for k, v in raw_colors.items()}


def check_design_md_theme_sync(project_root: Path = PROJECT_ROOT) -> CheckResult:
    """Valida sincronismo dos 6 tokens mestres Brand Book v3.1 entre DESIGN.md e Colors."""
    design_path = Path(project_root) / "DESIGN.md"
    if not design_path.is_file():
        return CheckResult(name="design_md_theme_sync", status="FAIL", details=["DESIGN.md não encontrado."])

    tokens = parse_design_md_tokens(design_path)
    expected_pairs = (
        ("background", Colors.NAVY, "#02060F"),
        ("primary", Colors.VIOLET, "#8B4DFF"),
        ("tertiary", Colors.GOLD, "#FFAB22"),
        ("secondary", Colors.LILAC, "#B28AFF"),
        ("inverse-surface", Colors.CREAM, "#F7F4EC"),
        ("on-surface-variant", Colors.SLATE, "#9EA2AE"),
    )

    mismatches: list[str] = []
    for design_key, py_val, canonical_hex in expected_pairs:
        design_hex = tokens.get(design_key)
        if design_hex != canonical_hex or py_val.upper() != canonical_hex:
            mismatches.append(
                f"Token '{design_key}': DESIGN.md={design_hex}, Colors={py_val}, esperado={canonical_hex}."
            )

    if mismatches:
        return CheckResult(name="design_md_theme_sync", status="FAIL", details=mismatches)

    return CheckResult(
        name="design_md_theme_sync",
        status="PASS",
        details=["Todos os 6 tokens mestres (60/20/12/8 + Lilac) sincronizados entre DESIGN.md e src/theme.py."],
    )


def check_wcag_contrast() -> tuple[CheckResult, list[dict[str, Any]]]:
    """Audita pares de contraste em Dark Mode e Light Mode com hard gates e advisories."""
    failures: list[str] = []
    warnings: list[str] = []
    report_rows: list[dict[str, Any]] = []

    fg_keys = ("text", "text_sec", "primary", "secondary", "accent", "correct", "incorrect")
    bg_keys = ("bg", "surface", "card_bg")

    for mode_name, is_dark in (("DARK", True), ("LIGHT", False)):
        palette = get_theme_colors(is_dark)
        for fg_key in fg_keys:
            for bg_key in bg_keys:
                fg_hex = palette[fg_key]
                bg_hex = palette[bg_key]
                ratio = round(contrast_ratio(fg_hex, bg_hex), 2)

                is_hard_fail = False
                if fg_key == "text" and ratio < 7.0:
                    is_hard_fail = True
                elif is_dark and fg_key in {"text_sec", "secondary", "accent"} and ratio < 4.5:
                    is_hard_fail = True
                elif fg_key == "primary" and bg_key == "bg" and ratio < 3.0:
                    is_hard_fail = True

                status = "PASS"
                if is_hard_fail:
                    status = "FAIL"
                    failures.append(
                        f"{mode_name} {fg_key} ({fg_hex}) sobre {bg_key} ({bg_hex}) = {ratio:.2f}:1 (abaixo do piso)."
                    )
                elif ratio < 4.5:
                    status = "WARN"
                    warnings.append(
                        f"{mode_name} {fg_key} ({fg_hex}) sobre {bg_key} ({bg_hex}) = {ratio:.2f}:1 (advisory WCAG AA < 4.5:1)."
                    )

                report_rows.append(
                    {
                        "mode": mode_name,
                        "fg": fg_key,
                        "fg_hex": fg_hex,
                        "bg": bg_key,
                        "bg_hex": bg_hex,
                        "ratio": ratio,
                        "status": status,
                    }
                )

    if failures:
        return CheckResult(name="wcag_contrast", status="FAIL", details=failures + warnings), report_rows
    if warnings:
        return CheckResult(name="wcag_contrast", status="WARN", details=warnings), report_rows
    return CheckResult(name="wcag_contrast", status="PASS", details=["Todos os pares WCAG AA >= 4.5:1."]), report_rows


def _is_flet_control_subclass(class_node: ast.ClassDef) -> bool:
    for base in class_node.bases:
        base_str = ast.unparse(base)
        if base_str in FLET_CONTROL_BASES or base_str.startswith("ft."):
            return True
    return False


def _scan_class_for_self_page_assign(class_node: ast.ClassDef, py_file: Path, failures: list[str]) -> None:
    """Detecta atribuição a self.page dentro de subclasses Flet, ignorando classes aninhadas puras."""
    for child in class_node.body:
        if isinstance(child, ast.ClassDef):
            continue
        for sub in ast.walk(child):
            if isinstance(sub, ast.Assign):
                for target in sub.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                        and target.attr == "page"
                    ):
                        failures.append(
                            f"{py_file}:{sub.lineno}: sobrescrita proibida de propriedade somente-leitura 'self.page' em {class_node.name}."
                        )


def _check_image_src_node(node: ast.Call, py_file: Path, failures: list[str]) -> None:
    for kw in node.keywords:
        if kw.arg != "src":
            continue
        literal_prefix: str | None = None
        if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            literal_prefix = kw.value.value
        elif isinstance(kw.value, ast.JoinedStr) and kw.value.values:
            first = kw.value.values[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                literal_prefix = first.value

        if literal_prefix is not None and not literal_prefix.startswith(("/", "http://", "https://")):
            failures.append(
                f"{py_file}:{node.lineno}: ft.Image(src={literal_prefix!r}) sem '/' inicial (risco BUG-11)."
            )


def scan_flet_ui_invariants(src_dir: Path) -> tuple[list[str], list[str]]:
    """Audita invariantes Flet 0.85+, prevenção de bugs catalogados e marca em src/."""
    failures: list[str] = []
    warnings: list[str] = []

    py_files = [p for p in sorted(Path(src_dir).rglob("*.py")) if "__pycache__" not in p.parts]
    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))
        except (OSError, SyntaxError) as exc:
            failures.append(f"{py_file}: erro ao analisar Python ({exc}).")
            continue

        lines = content.splitlines()
        for lineno, line in enumerate(lines, start=1):
            if "#004C97" in line.upper():
                failures.append(f"{py_file}:{lineno}: cor legada descontinuada #004C97 detectada.")
            if "ft.ImageFit" in line:
                failures.append(f"{py_file}:{lineno}: API Flet descontinuada ft.ImageFit detectada (BUG-11).")
            if "ft.ElevatedButton" in line:
                failures.append(f"{py_file}:{lineno}: API Flet descontinuada ft.ElevatedButton detectada (BUG-02).")
            if HEX_CONCAT_RE.search(line) or HEX_FSTRING_RE.search(line):
                failures.append(f"{py_file}:{lineno}: concatenação dinâmica hex-alpha proibida (BUG-03).")
            if "fonts.googleapis.com" in line:
                failures.append(f"{py_file}:{lineno}: referência externa Google Fonts proibida (use assets/fonts locais).")
            if "ft.BoxShadow(" in line and py_file.name != "theme.py":
                warnings.append(f"{py_file}:{lineno}: ft.BoxShadow fora de src/theme.py (advisory BUG-05).")

        if SAMPLE_CHARS_LEGACY_RE.search(content):
            failures.append(f"{py_file}: caracteres proibidos da marca legada em sample_chars.")

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and _is_flet_control_subclass(node):
                _scan_class_for_self_page_assign(node, py_file, failures)
            elif isinstance(node, ast.Call):
                func_name = ast.unparse(node.func)
                if func_name in {"ft.Text", "Text"}:
                    if any(kw.arg == "letter_spacing" for kw in node.keywords):
                        failures.append(
                            f"{py_file}:{node.lineno}: kwarg direto letter_spacing= em ft.Text (use ft.TextStyle, BUG-02)."
                        )
                elif func_name in {"ft.Image", "Image"}:
                    _check_image_src_node(node, py_file, failures)

    return failures, warnings


def check_branding_and_fonts_assets(project_root: Path = PROJECT_ROOT) -> CheckResult:
    """Valida ausência de termo proibido em dados públicos e presença de fontes/branding locais."""
    root = Path(project_root)
    failures: list[str] = []

    for rel_json in ("data/release_notes.json", "data/announcements.json"):
        json_path = root / rel_json
        if not json_path.is_file():
            failures.append(f"Arquivo esperado ausente: {rel_json}")
        else:
            raw = json_path.read_text(encoding="utf-8")
            if "sejong" in raw.lower():
                failures.append(f"Termo proibido detectado em {rel_json}.")

    fonts_dir = root / "assets" / "fonts"
    for font_name in REQUIRED_LOCAL_FONTS:
        font_path = fonts_dir / font_name
        if not font_path.is_file() or font_path.stat().st_size == 0:
            failures.append(f"Fonte obrigatória ausente ou vazia: assets/fonts/{font_name}")

    branding_dir = root / "assets" / "branding"
    for asset_name in EXPECTED_BRANDING_FILES:
        asset_path = branding_dir / asset_name
        if not asset_path.is_file() or asset_path.stat().st_size == 0:
            failures.append(f"Asset de branding ausente ou vazio: assets/branding/{asset_name}")

    if failures:
        return CheckResult(name="branding_and_fonts_assets", status="FAIL", details=failures)

    return CheckResult(
        name="branding_and_fonts_assets",
        status="PASS",
        details=[
            f"JSONs públicos limpos, {len(REQUIRED_LOCAL_FONTS)} fontes locais e {len(EXPECTED_BRANDING_FILES)} assets de branding validados."
        ],
    )


def run_design_audit(project_root: Path | str | None = None) -> dict[str, Any]:
    """Executa toda a bateria de Design QA e retorna relatório consolidado."""
    root = Path(project_root) if project_root else PROJECT_ROOT

    sync_check = check_design_md_theme_sync(root)
    wcag_check, contrast_report = check_wcag_contrast()
    ui_failures, ui_warnings = scan_flet_ui_invariants(root / "src")
    ui_check = CheckResult(
        name="flet_ui_invariants",
        status="FAIL" if ui_failures else ("WARN" if ui_warnings else "PASS"),
        details=ui_failures + ui_warnings or ["Todos os invariantes Flet 0.85+ e de branding em src/ conformes."],
    )
    assets_check = check_branding_and_fonts_assets(root)

    checks = [sync_check, wcag_check, ui_check, assets_check]
    failures: list[str] = []
    warnings: list[str] = []

    for item in checks:
        if item.status == "FAIL":
            if item.name == "flet_ui_invariants":
                failures.extend(f"[{item.name}] {d}" for d in ui_failures)
                warnings.extend(f"[{item.name}] {w}" for w in ui_warnings)
            elif item.name == "wcag_contrast":
                failures.extend(f"[{item.name}] {d}" for d in item.details if "(advisory" not in d)
                warnings.extend(f"[{item.name}] {d}" for d in item.details if "(advisory" in d)
            else:
                failures.extend(f"[{item.name}] {d}" for d in item.details)
        elif item.status == "WARN":
            warnings.extend(f"[{item.name}] {d}" for d in item.details)

    return {
        "passed": len(failures) == 0,
        "checks": [c.to_dict() for c in checks],
        "failures": failures,
        "warnings": warnings,
        "contrast_report": contrast_report,
    }


def _print_report(report: dict[str, Any]) -> None:
    print("=" * 72)
    print(" 🎨 SAEBOM COMPANION — AUDITORIA DE DESIGN QA (BRAND BOOK v3.1)")
    print("=" * 72)
    for check in report["checks"]:
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(check["status"], "•")
        print(f"{icon} [{check['status']}] {check['name']}")
        if check["status"] == "PASS":
            for detail in check["details"]:
                print(f"   - {detail}")
        elif check["status"] == "WARN":
            print(f"   - {len(check['details'])} advisories registrados (ver abaixo).")
        else:
            for detail in check["details"]:
                print(f"   - {detail}")

    if report["warnings"]:
        print("\nAdvisories / Warnings (não bloqueantes):")
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
    parser = argparse.ArgumentParser(description="Auditoria automatizada de Design QA do Saebom Companion")
    parser.add_argument("--json", action="store_true", help="Imprime relatório completo em JSON")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT, help="Diretório raiz do projeto")
    args = parser.parse_args(argv)

    report = run_design_audit(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_report(report)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
