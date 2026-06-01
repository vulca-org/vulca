from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LayoutIssue:
    severity: str
    path: Path
    code: str
    message: str


def _bbox(element: dict[str, Any]) -> tuple[float, float, float, float] | None:
    bbox = element.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    try:
        x, y, w, h = [float(value) for value in bbox]
    except (TypeError, ValueError):
        return None
    return x, y, w, h


def check_layout(path: Path) -> list[LayoutIssue]:
    issues: list[LayoutIssue] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [LayoutIssue("error", path, "invalid-json", f"invalid layout JSON: {exc.msg}")]

    slide = data.get("slide", {})
    frame = slide.get("frame", {}) if isinstance(slide, dict) else {}
    slide_w = float(frame.get("width", 1280))
    slide_h = float(frame.get("height", 720))
    elements = data.get("elements", [])
    if not isinstance(elements, list):
        return [LayoutIssue("error", path, "missing-elements", "layout has no elements list")]

    text_boxes: list[tuple[dict[str, Any], tuple[float, float, float, float]]] = []
    for element in elements:
        if not isinstance(element, dict):
            continue
        bbox = _bbox(element)
        if bbox is None:
            continue
        x, y, w, h = bbox
        label = str(element.get("text") or element.get("id") or "shape")
        if w <= 0 or h <= 0:
            issues.append(LayoutIssue("error", path, "invalid-bbox", f"{label} has non-positive bbox {bbox}"))
        if x < -2 or y < -2 or x + w > slide_w + 2 or y + h > slide_h + 2:
            issues.append(LayoutIssue("error", path, "out-of-bounds", f"{label} escapes slide bounds with bbox {bbox}"))

        text = str(element.get("text") or "").strip()
        if not text:
            continue
        text_boxes.append((element, bbox))
        font_size = float(element.get("resolvedFontSize") or element.get("resolvedTextStyle", {}).get("fontSize") or 0)
        line_count = int(element.get("textLayout", {}).get("lineCount") or max(1, text.count("\n") + 1))
        if font_size and font_size < 7:
            issues.append(LayoutIssue("warning", path, "microtype", f"{text[:60]} uses {font_size:g}px text"))
        if font_size and h < font_size * line_count * 1.05:
            issues.append(
                LayoutIssue(
                    "warning",
                    path,
                    "tight-text",
                    f"{text[:60]} text box is tight: height {h:g}px for {line_count} line(s) at {font_size:g}px",
                )
            )

    for idx, (left, left_box) in enumerate(text_boxes):
        lx, ly, lw, lh = left_box
        for right, right_box in text_boxes[idx + 1 :]:
            rx, ry, rw, rh = right_box
            ix = max(0.0, min(lx + lw, rx + rw) - max(lx, rx))
            iy = max(0.0, min(ly + lh, ry + rh) - max(ly, ry))
            overlap = ix * iy
            if overlap <= 0:
                continue
            smaller = max(1.0, min(lw * lh, rw * rh))
            if overlap / smaller > 0.35:
                lt = str(left.get("text") or "")[:40]
                rt = str(right.get("text") or "")[:40]
                issues.append(LayoutIssue("error", path, "text-overlap", f"{lt} overlaps {rt}"))
    return issues


def write_report(layout_dir: Path, out: Path) -> dict[str, int]:
    files = sorted(layout_dir.glob("*.layout.json"))
    issues: list[LayoutIssue] = []
    for path in files:
        issues.extend(check_layout(path))

    errors = sum(1 for issue in issues if issue.severity == "error")
    warnings = sum(1 for issue in issues if issue.severity == "warning")
    lines = []
    for issue in issues:
        lines.append(f"[{issue.severity}] {issue.path.name}:{issue.code}: {issue.message}")
    lines.append(f"Checked {len(files)} layout file(s): {errors} error(s), {warnings} warning(s).")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"layout_files": len(files), "layout_errors": errors, "layout_warnings": warnings}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check artifact-tool presentation layout JSON for simple geometry issues.")
    parser.add_argument("--layout-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = write_report(args.layout_dir, args.out)
    print(json.dumps(summary, indent=2))
    return 0 if summary["layout_errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
