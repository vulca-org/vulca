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


def read_text_file(path: Path, label: str, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"unable to read {label}: {exc}")
    except UnicodeDecodeError as exc:
        errors.append(f"{label} must be UTF-8 text: {exc}")
    return None


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    body = read_text_file(path, path.name, errors)
    if body is None:
        return {}
    try:
        value = json.loads(body)
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


def require_integer(label: str, value: Any, errors: list[str]) -> bool:
    if type(value) is not int:
        errors.append(f"{label} must be an integer")
        return False
    return True


def require_non_empty_string(label: str, value: Any, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return False
    return True


def require_non_empty_dict(label: str, value: Any, errors: list[str]) -> bool:
    if not isinstance(value, dict) or not value:
        errors.append(f"{label} must be a non-empty object")
        return False
    return True


def require_non_empty_list(label: str, value: Any, errors: list[str]) -> bool:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return False
    return True


def validate_string_list(label: str, value: Any, errors: list[str]) -> bool:
    if not require_non_empty_list(label, value, errors):
        return False
    ok = True
    for index, item in enumerate(value):
        if not require_non_empty_string(f"{label}[{index}]", item, errors):
            ok = False
    return ok


def validate_string_mapping(label: str, value: Any, errors: list[str]) -> bool:
    if not require_non_empty_dict(label, value, errors):
        return False
    ok = True
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{label} keys must be non-empty strings")
            ok = False
        if not require_non_empty_string(f"{label}.{key}", item, errors):
            ok = False
    return ok


def validate_number_mapping(label: str, value: Any, errors: list[str]) -> bool:
    if not require_non_empty_dict(label, value, errors):
        return False
    ok = True
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{label} keys must be non-empty strings")
            ok = False
        if not isinstance(item, int | float) or isinstance(item, bool):
            errors.append(f"{label}.{key} must be a number")
            ok = False
    return ok


def validate_sources(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "sources.json", errors)
    require_keys("sources.json", data, ["schema_version", "sources"], errors)
    if "schema_version" in data:
        require_integer("sources.json.schema_version", data["schema_version"], errors)
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
        for key in required:
            if key in source:
                require_non_empty_string(f"sources[{index}].{key}", source[key], errors)
        source_id = source.get("id")
        if isinstance(source_id, str) and source_id.strip():
            if source_id in seen_ids:
                errors.append(f"sources[{index}].id duplicates {source_id}")
            seen_ids.add(source_id)
        url = source.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"sources[{index}].url must be https")
        allowed_use = source.get("allowed_use")
        if isinstance(allowed_use, str) and allowed_use != "reference_analysis_only":
            errors.append(f"sources[{index}].allowed_use must be reference_analysis_only")


def validate_narrative_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "narrative_rules.json", errors)
    require_keys(
        "narrative_rules.json", data, ["schema_version", "opening", "progression", "technical_depth", "closing"], errors
    )
    if "schema_version" in data:
        require_integer("narrative_rules.schema_version", data["schema_version"], errors)
    for key in ["opening", "technical_depth", "closing"]:
        if key in data:
            require_non_empty_string(f"narrative_rules.{key}", data[key], errors)
    progression = data.get("progression", [])
    validate_string_list("narrative_rules.progression", progression, errors)


def validate_style_tokens(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "style_tokens.json", errors)
    require_keys(
        "style_tokens.json",
        data,
        ["schema_version", "palette", "font_stack", "spacing", "corner_radius", "stroke_widths"],
        errors,
    )
    if "schema_version" in data:
        require_integer("style_tokens.schema_version", data["schema_version"], errors)
    validate_string_mapping("style_tokens.palette", data.get("palette", {}), errors)
    validate_string_list("style_tokens.font_stack", data.get("font_stack", []), errors)
    validate_number_mapping("style_tokens.spacing", data.get("spacing", {}), errors)
    validate_number_mapping("style_tokens.corner_radius", data.get("corner_radius", {}), errors)
    validate_number_mapping("style_tokens.stroke_widths", data.get("stroke_widths", {}), errors)


def validate_asset_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_rules.json", errors)
    require_keys(
        "asset_rules.json",
        data,
        ["schema_version", "preferred_assets", "bitmap_use", "forbidden", "provenance_required"],
        errors,
    )
    if "schema_version" in data:
        require_integer("asset_rules.schema_version", data["schema_version"], errors)
    validate_string_list("asset_rules.preferred_assets", data.get("preferred_assets", []), errors)
    if "bitmap_use" in data:
        require_non_empty_string("asset_rules.bitmap_use", data["bitmap_use"], errors)
    validate_string_list("asset_rules.forbidden", data.get("forbidden", []), errors)
    if "provenance_required" in data and not isinstance(data.get("provenance_required"), bool):
        errors.append("asset_rules.provenance_required must be a boolean")


def validate_slide_patterns(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "slide_patterns.json", errors)
    require_keys("slide_patterns.json", data, ["schema_version", "patterns"], errors)
    if "schema_version" in data:
        require_integer("slide_patterns.schema_version", data["schema_version"], errors)
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
        for key in ["id", "role", "content_density", "layout_shape", "visual_asset_type"]:
            if key in pattern:
                require_non_empty_string(f"slide_patterns.patterns[{index}].{key}", pattern[key], errors)
        pattern_id = pattern.get("id")
        if isinstance(pattern_id, str) and pattern_id.strip():
            if pattern_id in pattern_ids:
                errors.append(f"slide_patterns.patterns[{index}].id duplicates {pattern_id}")
            pattern_ids.add(pattern_id)
        if "editability_requirements" in pattern:
            validate_string_list(
                f"slide_patterns.patterns[{index}].editability_requirements",
                pattern["editability_requirements"],
                errors,
            )
    return pattern_ids


def validate_deck_outline(pack_dir: Path, pattern_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "deck_outline.json", errors)
    require_keys("deck_outline.json", data, ["schema_version", "title", "slides"], errors)
    if "schema_version" in data:
        require_integer("deck_outline.schema_version", data["schema_version"], errors)
    if "title" in data:
        require_non_empty_string("deck_outline.title", data["title"], errors)
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
        for key in required:
            if key in slide:
                require_non_empty_string(f"deck_outline.slides[{index}].{key}", slide[key], errors)
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
        body = read_text_file(path, rel, errors)
        if body is not None and not body.strip():
            errors.append(f"{rel} must not be empty")


def validate_case_pack(pack_dir: str | Path) -> ValidationResult:
    root = Path(pack_dir)
    errors: list[str] = []
    if not root.exists():
        return ValidationResult(False, [f"case pack directory does not exist: {root}"])
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif not path.is_file():
            errors.append(f"required path is not a file: {rel}")
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
