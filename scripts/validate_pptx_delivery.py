from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PPTX_REQUIRED_ENTRIES = [
    "[Content_Types].xml",
    "ppt/presentation.xml",
]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class DeliveryIssue:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class DeliveryResult:
    label: str
    pptx_path: Path
    layout_dir: Path
    contact_sheet_path: Path
    ok: bool
    delivery_gate: str
    issues: list[DeliveryIssue]
    checks: dict[str, Any]


def error(code: str, message: str) -> DeliveryIssue:
    return DeliveryIssue("error", code, message)


def warning(code: str, message: str) -> DeliveryIssue:
    return DeliveryIssue("warning", code, message)


def normalize_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def png_dimensions(path: Path, issues: list[DeliveryIssue]) -> dict[str, int] | None:
    if not path.exists():
        issues.append(error("missing_contact_sheet", f"contact sheet does not exist: {path}"))
        return None
    if not path.is_file():
        issues.append(error("contact_sheet_not_file", f"contact sheet is not a file: {path}"))
        return None
    try:
        header = path.read_bytes()[:24]
    except OSError as exc:
        issues.append(error("contact_sheet_unreadable", f"unable to read contact sheet: {exc}"))
        return None
    if len(header) < 24 or not header.startswith(PNG_SIGNATURE) or header[12:16] != b"IHDR":
        issues.append(error("contact_sheet_not_png", f"contact sheet is not a PNG: {path}"))
        return None
    width, height = struct.unpack(">II", header[16:24])
    return {"width": int(width), "height": int(height)}


def inspect_pptx(path: Path, issues: list[DeliveryIssue]) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "pptx_exists": path.exists(),
        "pptx_size_bytes": 0,
        "slide_count": 0,
        "media_entries": [],
        "required_entries": {},
    }
    if not path.exists():
        issues.append(error("missing_pptx", f"PPTX does not exist: {path}"))
        return checks
    if not path.is_file():
        issues.append(error("pptx_not_file", f"PPTX is not a file: {path}"))
        return checks
    checks["pptx_size_bytes"] = path.stat().st_size
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            checks["required_entries"] = {entry: entry in names for entry in PPTX_REQUIRED_ENTRIES}
            for entry, present in checks["required_entries"].items():
                if not present:
                    issues.append(error("missing_pptx_entry", f"PPTX missing required entry: {entry}"))

            slide_numbers = sorted(
                int(match.group(1)) for name in names if (match := re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name))
            )
            checks["slide_count"] = len(slide_numbers)
            checks["slide_numbers"] = slide_numbers
            if not slide_numbers:
                issues.append(error("missing_slide_entries", "PPTX contains no ppt/slides/slideN.xml entries"))

            media_entries = sorted(name for name in names if name.startswith("ppt/media/"))
            checks["media_entries"] = media_entries
            if media_entries:
                issues.append(
                    warning(
                        "embedded_media_present",
                        f"PPTX contains {len(media_entries)} ppt/media entry; inspect provenance and editability.",
                    )
                )
    except zipfile.BadZipFile:
        issues.append(error("invalid_pptx_zip", f"PPTX is not a valid ZIP package: {path}"))
    except OSError as exc:
        issues.append(error("pptx_unreadable", f"unable to read PPTX: {exc}"))
    return checks


def inspect_layout_dir(path: Path, expected_slide_count: int, issues: list[DeliveryIssue]) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "layout_dir_exists": path.exists(),
        "layout_file_count": 0,
        "layout_files": [],
    }
    if not path.exists():
        issues.append(error("missing_layout_dir", f"layout directory does not exist: {path}"))
        return checks
    if not path.is_dir():
        issues.append(error("layout_dir_not_directory", f"layout path is not a directory: {path}"))
        return checks

    layout_files = sorted(path.glob("*.layout.json"))
    checks["layout_file_count"] = len(layout_files)
    checks["layout_files"] = [str(item) for item in layout_files]
    if not layout_files:
        issues.append(error("missing_layout_json", f"layout directory contains no *.layout.json files: {path}"))
        return checks
    if expected_slide_count and len(layout_files) != expected_slide_count:
        issues.append(
            warning(
                "layout_slide_count_mismatch",
                f"layout JSON count {len(layout_files)} does not match PPTX slide count {expected_slide_count}.",
            )
        )

    for layout_file in layout_files:
        try:
            data = json.loads(layout_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(error("invalid_layout_json", f"{layout_file.name} is not valid JSON: {exc.msg}"))
            continue
        except OSError as exc:
            issues.append(error("layout_unreadable", f"unable to read {layout_file.name}: {exc}"))
            continue
        if not isinstance(data, dict):
            issues.append(error("layout_not_object", f"{layout_file.name} must contain a JSON object"))
            continue
        if not str(data.get("schema", "")).startswith("openai.presentation.layout/"):
            issues.append(warning("unknown_layout_schema", f"{layout_file.name} has unknown layout schema"))
        if not isinstance(data.get("elements"), list):
            issues.append(error("layout_missing_elements", f"{layout_file.name} missing elements list"))
    return checks


def detect_renderers() -> dict[str, str | None]:
    return {
        "libreoffice": shutil.which("libreoffice") or shutil.which("soffice"),
        "powerpoint": (
            "/Applications/Microsoft PowerPoint.app"
            if Path("/Applications/Microsoft PowerPoint.app").exists()
            else None
        ),
        "keynote": "/Applications/Keynote.app" if Path("/Applications/Keynote.app").exists() else None,
    }


def renderer_checks(renderer_paths: dict[str, str | None] | None, issues: list[DeliveryIssue]) -> dict[str, str | None]:
    renderers = detect_renderers() if renderer_paths is None else dict(renderer_paths)
    issues.append(
        warning(
            "native_render_not_run",
            "Renderer availability was checked, but no native PowerPoint, Keynote, or Google Slides render was executed.",
        )
    )
    if not any(renderers.values()):
        issues.append(
            warning(
                "native_renderer_unverified",
                "No native renderer was detected; v1 does not prove native PowerPoint, Keynote, or Google Slides visual fidelity.",
            )
        )
    return renderers


def delivery_gate_for(issues: list[DeliveryIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "blocked"
    return "internal-demo-ok-public-blocked"


def validate_delivery(
    *,
    pptx_path: str | Path,
    layout_dir: str | Path,
    contact_sheet_path: str | Path,
    label: str,
    renderer_paths: dict[str, str | None] | None = None,
) -> DeliveryResult:
    pptx = normalize_path(pptx_path)
    layout = normalize_path(layout_dir)
    contact_sheet = normalize_path(contact_sheet_path)
    issues: list[DeliveryIssue] = []

    pptx_checks = inspect_pptx(pptx, issues)
    layout_checks = inspect_layout_dir(layout, int(pptx_checks.get("slide_count") or 0), issues)
    contact_sheet_checks = png_dimensions(contact_sheet, issues)
    renderers = renderer_checks(renderer_paths, issues)

    checks: dict[str, Any] = {
        **pptx_checks,
        **layout_checks,
        "contact_sheet": contact_sheet_checks,
        "renderers": renderers,
        "human_review_required": True,
    }
    gate = delivery_gate_for(issues)
    return DeliveryResult(
        label=label,
        pptx_path=pptx,
        layout_dir=layout,
        contact_sheet_path=contact_sheet,
        ok=gate != "blocked",
        delivery_gate=gate,
        issues=issues,
        checks=checks,
    )


def write_markdown_report(results: list[DeliveryResult], out_path: str | Path) -> None:
    out = normalize_path(out_path)
    lines = [
        "# PPT Delivery QA Report",
        "",
        "This report is structural delivery QA. It does not prove native PowerPoint, Keynote, or Google Slides visual fidelity.",
        "",
    ]
    for result in results:
        errors = [issue for issue in result.issues if issue.severity == "error"]
        warnings = [issue for issue in result.issues if issue.severity == "warning"]
        lines.extend(
            [
                f"## {result.label}",
                "",
                f"- Delivery gate: `{result.delivery_gate}`",
                f"- PPTX: `{result.pptx_path}`",
                f"- Layout JSON: `{result.layout_dir}`",
                f"- Contact sheet: `{result.contact_sheet_path}`",
                f"- Slide count: `{result.checks.get('slide_count', 0)}`",
                f"- Layout file count: `{result.checks.get('layout_file_count', 0)}`",
                f"- Media entries: `{len(result.checks.get('media_entries', []))}`",
                f"- Human review required: `{result.checks.get('human_review_required')}`",
                "",
                "### Renderer Availability",
                "",
            ]
        )
        renderers = result.checks.get("renderers", {})
        if isinstance(renderers, dict):
            for name, path in renderers.items():
                lines.append(f"- {name}: `{path or 'not detected'}`")
        lines.extend(["", "### Issues", ""])
        if not result.issues:
            lines.append("- none")
        for issue in result.issues:
            lines.append(f"- `{issue.severity}` `{issue.code}`: {issue.message}")
        lines.extend(
            [
                "",
                "### Gate Notes",
                "",
                f"- Errors: `{len(errors)}`",
                f"- Warnings: `{len(warnings)}`",
                "- Public publishing remains blocked until human review and native/cross-platform inspection.",
                "",
            ]
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate structural delivery readiness for a generated PPTX deck.")
    parser.add_argument("--pptx", required=True)
    parser.add_argument("--layout-dir", required=True)
    parser.add_argument("--contact-sheet", required=True)
    parser.add_argument("--label", default="PPTX deck")
    parser.add_argument("--out", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = validate_delivery(
        pptx_path=args.pptx,
        layout_dir=args.layout_dir,
        contact_sheet_path=args.contact_sheet,
        label=args.label,
    )
    write_markdown_report([result], args.out)
    print(f"{result.label}: {result.delivery_gate}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
