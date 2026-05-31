from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "README.md",
    "sources.json",
    "source_summaries.md",
    "commercial_brief.md",
    "design_notes.md",
    "narrative_rules.json",
    "slide_patterns.json",
    "style_tokens.json",
    "asset_rules.json",
    "evaluation_rubric.md",
    "vulca_ppt_skill.md",
    "deck_outline.json",
    "baseline_prompt.md",
    "vulca_generation_brief.md",
    "gemini_review_prompt.md",
    "results/README.md",
    "results/comparison_report.md",
]


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} is not valid JSON: {exc.msg}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a JSON object")
        return {}
    return value


def require_keys(label: str, value: dict[str, Any], keys: list[str], errors: list[str]) -> None:
    for key in keys:
        if key not in value:
            errors.append(f"{label} missing key: {key}")


def validate_sources(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "sources.json", errors)
    require_keys("sources.json", data, ["schema_version", "sources"], errors)
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("sources.json sources must be a non-empty list")
        return

    required = ["id", "title", "url", "role", "accessed_on", "allowed_use", "copyright_note"]
    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        require_keys(f"sources[{index}]", source, required, errors)
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in seen_ids:
                errors.append(f"sources[{index}].id duplicates {source_id}")
            seen_ids.add(source_id)
        else:
            errors.append(f"sources[{index}].id must be a string")
        url = source.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"sources[{index}].url must be https")
        if source.get("allowed_use") != "reference_analysis_only":
            errors.append(f"sources[{index}].allowed_use must be reference_analysis_only")


def validate_narrative_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "narrative_rules.json", errors)
    require_keys("narrative_rules.json", data, ["schema_version", "opening", "progression", "technical_depth", "closing"], errors)
    progression = data.get("progression", [])
    if not isinstance(progression, list) or not progression:
        errors.append("narrative_rules.progression must be a non-empty list")


def validate_style_tokens(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "style_tokens.json", errors)
    require_keys("style_tokens.json", data, ["schema_version", "palette", "font_stack", "spacing", "corner_radius", "stroke_widths"], errors)
    palette = data.get("palette", {})
    if not isinstance(palette, dict) or not palette:
        errors.append("style_tokens.palette must be a non-empty object")
    font_stack = data.get("font_stack", [])
    if not isinstance(font_stack, list) or not font_stack:
        errors.append("style_tokens.font_stack must be a non-empty list")


def validate_asset_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_rules.json", errors)
    require_keys("asset_rules.json", data, ["schema_version", "preferred_assets", "bitmap_use", "forbidden", "provenance_required"], errors)
    preferred_assets = data.get("preferred_assets", [])
    if not isinstance(preferred_assets, list) or not preferred_assets:
        errors.append("asset_rules.preferred_assets must be a non-empty list")
    forbidden = data.get("forbidden", [])
    if not isinstance(forbidden, list):
        errors.append("asset_rules.forbidden must be a list")
    if not isinstance(data.get("provenance_required"), bool):
        errors.append("asset_rules.provenance_required must be a boolean")


def validate_slide_patterns(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "slide_patterns.json", errors)
    require_keys("slide_patterns.json", data, ["schema_version", "patterns"], errors)
    patterns = data.get("patterns", [])
    if not isinstance(patterns, list) or not patterns:
        errors.append("slide_patterns.patterns must be a non-empty list")
        return set()

    required = ["id", "role", "content_density", "layout_shape", "visual_asset_type", "editability_requirements"]
    pattern_ids: set[str] = set()
    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            errors.append(f"slide_patterns.patterns[{index}] must be an object")
            continue
        require_keys(f"slide_patterns.patterns[{index}]", pattern, required, errors)
        pattern_id = pattern.get("id")
        if isinstance(pattern_id, str):
            if pattern_id in pattern_ids:
                errors.append(f"slide_patterns.patterns[{index}].id duplicates {pattern_id}")
            pattern_ids.add(pattern_id)
        else:
            errors.append(f"slide_patterns.patterns[{index}].id must be a string")
        requirements = pattern.get("editability_requirements", [])
        if not isinstance(requirements, list) or not requirements:
            errors.append(f"slide_patterns.patterns[{index}].editability_requirements must be non-empty")
    return pattern_ids


def validate_deck_outline(pack_dir: Path, pattern_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "deck_outline.json", errors)
    require_keys("deck_outline.json", data, ["schema_version", "title", "slides"], errors)
    slides = data.get("slides", [])
    if not isinstance(slides, list) or not slides:
        errors.append("deck_outline.slides must be a non-empty list")
        return

    required = ["id", "pattern_id", "title", "claim", "proof_object"]
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            errors.append(f"deck_outline.slides[{index}] must be an object")
            continue
        require_keys(f"deck_outline.slides[{index}]", slide, required, errors)
        pattern_id = slide.get("pattern_id")
        if not isinstance(pattern_id, str):
            errors.append(f"deck_outline.slides[{index}].pattern_id must be a string")
        elif pattern_id not in pattern_ids:
            errors.append(f"deck_outline.slides[{index}].pattern_id {pattern_id} is not defined in slide_patterns.json")


def validate_markdown_not_empty(pack_dir: Path, errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not rel.endswith(".md"):
            continue
        path = pack_dir / rel
        if path.exists() and not path.read_text(encoding="utf-8").strip():
            errors.append(f"{rel} must not be empty")


def validate_case_pack(pack_dir: str | Path) -> ValidationResult:
    root = Path(pack_dir)
    errors: list[str] = []
    if not root.exists():
        return ValidationResult(False, [f"case pack directory does not exist: {root}"])
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")
    if errors:
        return ValidationResult(False, errors)

    validate_sources(root, errors)
    validate_narrative_rules(root, errors)
    validate_style_tokens(root, errors)
    validate_asset_rules(root, errors)
    pattern_ids = validate_slide_patterns(root, errors)
    validate_deck_outline(root, pattern_ids, errors)
    validate_markdown_not_empty(root, errors)
    return ValidationResult(not errors, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Vulca PPT case pack.")
    parser.add_argument("pack_dir", type=Path)
    args = parser.parse_args()
    result = validate_case_pack(args.pack_dir)
    if result.ok:
        print(f"case pack ok: {args.pack_dir}")
        return 0
    for error in result.errors:
        print(f"error: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
