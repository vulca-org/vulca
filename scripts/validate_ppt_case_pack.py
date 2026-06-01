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


RUN1_REQUIRED_FILES = [
    "tutorial_notes.md",
    "design_memory.json",
    "results/asset_provenance.json",
    "results/iteration_log.md",
    "results/render_check.md",
]


RUN1_5_REQUIRED_FILES = [
    *RUN1_REQUIRED_FILES,
    "experiment_protocol.md",
    "bad_data_generation_brief.md",
    "results/ablation_report.md",
    "results/ablation_report.json",
    "results/comparison_report.json",
    "results/delivery_gate.md",
]


RUN2_REQUIRED_FILES = [
    "README.md",
    "commercial_case.md",
    "sources.json",
    "source_cards/README.md",
    "video_cards/README.md",
    "evidence_memory.json",
    "aesthetic_memory.json",
    "asset_memory.json",
    "narrative_spine.json",
    "slide_archetypes.json",
    "aesthetic_rubric.md",
    "vulca_ppt_skill.md",
    "generation_briefs/README.md",
    "generation_briefs/prompt_only.md",
    "generation_briefs/run1_5_skill.md",
    "generation_briefs/run2_skill.md",
    "generation_briefs/bad_aesthetic_memory.md",
    "results/README.md",
    "results/comparison_report.md",
    "results/delivery_gate.md",
]


RUN1_5_REQUIRED_MEMORY_FIELDS = [
    "evidence_id",
    "source_role",
    "observation",
    "design_rule",
    "slide_primitive",
    "layout_constraint",
    "qa_signal",
]


RUN1_5_SOURCE_ROLES = {"brief", "source", "tutorial", "review"}
RUN1_5_SLIDE_PRIMITIVES = {"cockpit", "learning_map", "comparison_delta", "qa_gate", "decision_table"}
RUN2_SOURCE_TYPES = {"commercial_case", "tutorial", "video", "design_article", "reference_deck"}
RUN2_ALLOWED_USES = {"short_analysis", "derived_rules_only", "visual_inspiration", "timestamped_observation_only"}
RUN2_RHYTHM_ROLES = {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}
RUN2_ASSET_TYPES = {
    "generated_background",
    "editable_svg",
    "native_shapes",
    "chart",
    "diagram",
    "video_derived_reference",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def required_files_for_profile(profile: str) -> list[str]:
    if profile == "default":
        return REQUIRED_FILES
    if profile == "run1":
        return [*REQUIRED_FILES, *RUN1_REQUIRED_FILES]
    if profile == "run1_5":
        return [*REQUIRED_FILES, *RUN1_5_REQUIRED_FILES]
    if profile == "run2":
        return RUN2_REQUIRED_FILES
    raise ValueError(f"unknown case-pack profile: {profile}")


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


def load_json_files(directory: Path, label: str, errors: list[str]) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.exists():
        errors.append(f"{label} directory does not exist")
        return []
    if not directory.is_dir():
        errors.append(f"{label} must be a directory")
        return []
    paths = sorted(directory.glob("*.json"))
    if not paths:
        errors.append(f"{label} must contain at least one JSON file")
        return []
    return [(path, load_json(path, errors)) for path in paths]


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


def validate_choice(label: str, value: Any, choices: set[str], errors: list[str]) -> bool:
    if not require_non_empty_string(label, value, errors):
        return False
    if value not in choices:
        errors.append(f"{label} must be one of {', '.join(sorted(choices))}")
        return False
    return True


def validate_exact_string_set(label: str, value: Any, expected: set[str], errors: list[str]) -> None:
    if not validate_string_list(label, value, errors):
        return
    actual = set(value)
    for item in sorted(expected - actual):
        errors.append(f"{label} missing value: {item}")
    for item in sorted(actual - expected):
        errors.append(f"{label} has unexpected value: {item}")


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


def validate_sources(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "sources.json", errors)
    require_keys("sources.json", data, ["schema_version", "sources"], errors)
    if "schema_version" in data:
        require_integer("sources.json.schema_version", data["schema_version"], errors)
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("sources.json sources must be a non-empty list")
        return set()

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
    return seen_ids


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


def collect_run2_card_ids(pack_dir: Path, source_ids: set[str], errors: list[str]) -> set[str]:
    card_ids: set[str] = set()
    common_required = ["schema_version", "card_id", "source_id", "source_type", "allowed_use", "do_not_copy"]
    source_required = ["observed_move", "why_it_works", "ppt_translation", "quality_risk"]
    video_required = [
        "timestamp_map",
        "keyframe_descriptions",
        "pacing_notes",
        "transition_observations",
        "derived_aesthetic_cards",
    ]

    for label, required in [
        ("source_cards", [*common_required, *source_required]),
        ("video_cards", [*common_required, *video_required]),
    ]:
        for path, card in load_json_files(pack_dir / label, label, errors):
            card_label = f"{label}/{path.name}"
            require_keys(card_label, card, required, errors)
            if "schema_version" in card:
                require_integer(f"{card_label}.schema_version", card["schema_version"], errors)
            card_id = card.get("card_id")
            if "card_id" in card and require_non_empty_string(f"{card_label}.card_id", card_id, errors):
                if card_id in card_ids:
                    errors.append(f"{card_label}.card_id duplicates {card_id}")
                card_ids.add(card_id)
            if "source_id" in card:
                source_id = card["source_id"]
                if (
                    require_non_empty_string(f"{card_label}.source_id", source_id, errors)
                    and source_id not in source_ids
                ):
                    errors.append(f"{card_label}.source_id {source_id} is not defined in sources.json")
            if "source_type" in card:
                validate_choice(f"{card_label}.source_type", card["source_type"], RUN2_SOURCE_TYPES, errors)
            if "allowed_use" in card:
                validate_choice(f"{card_label}.allowed_use", card["allowed_use"], RUN2_ALLOWED_USES, errors)
            if "do_not_copy" in card:
                require_non_empty_string(f"{card_label}.do_not_copy", card["do_not_copy"], errors)

            if label == "source_cards":
                for key in source_required:
                    if key in card:
                        require_non_empty_string(f"{card_label}.{key}", card[key], errors)
            else:
                for key in ["timestamp_map", "keyframe_descriptions", "derived_aesthetic_cards"]:
                    if key in card:
                        validate_string_list(f"{card_label}.{key}", card[key], errors)
                for key in ["pacing_notes", "transition_observations"]:
                    if key in card:
                        require_non_empty_string(f"{card_label}.{key}", card[key], errors)
    return card_ids


def validate_run2_source_references(
    label: str,
    source_card_ids: Any,
    card_ids: set[str],
    errors: list[str],
) -> None:
    if not validate_string_list(label, source_card_ids, errors):
        return
    for index, source_card_id in enumerate(source_card_ids):
        if source_card_id not in card_ids:
            errors.append(f"{label}[{index}] {source_card_id} is not defined by source_cards or video_cards")


def validate_run2_evidence_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "evidence_memory.json", errors)
    require_keys("evidence_memory.json", data, ["schema_version", "claims"], errors)
    if "schema_version" in data:
        require_integer("evidence_memory.schema_version", data["schema_version"], errors)
    claims = data.get("claims", [])
    if not isinstance(claims, list) or not claims:
        errors.append("evidence_memory.claims must be a non-empty list")
        return

    required = ["id", "source_card_ids", "claim", "business_relevance", "allowed_use", "qa_checks"]
    for index, claim in enumerate(claims):
        label = f"evidence_memory.claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, claim, required, errors)
        for key in ["id", "claim", "business_relevance"]:
            if key in claim:
                require_non_empty_string(f"{label}.{key}", claim[key], errors)
        if "allowed_use" in claim:
            validate_choice(f"{label}.allowed_use", claim["allowed_use"], RUN2_ALLOWED_USES, errors)
        if "qa_checks" in claim:
            validate_string_list(f"{label}.qa_checks", claim["qa_checks"], errors)
        if "source_card_ids" in claim:
            validate_run2_source_references(f"{label}.source_card_ids", claim["source_card_ids"], card_ids, errors)


def validate_run2_aesthetic_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "aesthetic_memory.json", errors)
    require_keys("aesthetic_memory.json", data, ["schema_version", "moves"], errors)
    if "schema_version" in data:
        require_integer("aesthetic_memory.schema_version", data["schema_version"], errors)
    moves = data.get("moves", [])
    if not isinstance(moves, list) or not moves:
        errors.append("aesthetic_memory.moves must be a non-empty list")
        return

    required = [
        "id",
        "source_card_ids",
        "aesthetic_move",
        "trigger",
        "composition_rule",
        "typography_rule",
        "density_budget",
        "rhythm_role",
        "ppt_primitive",
        "negative_rules",
        "qa_signal",
    ]
    string_fields = [
        "id",
        "aesthetic_move",
        "trigger",
        "composition_rule",
        "typography_rule",
        "ppt_primitive",
        "qa_signal",
    ]
    for index, move in enumerate(moves):
        label = f"aesthetic_memory.moves[{index}]"
        if not isinstance(move, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, move, required, errors)
        for key in string_fields:
            if key in move:
                require_non_empty_string(f"{label}.{key}", move[key], errors)
        if "source_card_ids" in move:
            validate_run2_source_references(f"{label}.source_card_ids", move["source_card_ids"], card_ids, errors)
        if "density_budget" in move:
            validate_number_mapping(f"{label}.density_budget", move["density_budget"], errors)
        if "rhythm_role" in move:
            validate_choice(f"{label}.rhythm_role", move["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "negative_rules" in move:
            validate_string_list(f"{label}.negative_rules", move["negative_rules"], errors)


def validate_run2_asset_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_memory.json", errors)
    require_keys("asset_memory.json", data, ["schema_version", "assets"], errors)
    if "schema_version" in data:
        require_integer("asset_memory.schema_version", data["schema_version"], errors)
    assets = data.get("assets", [])
    if not isinstance(assets, list) or not assets:
        errors.append("asset_memory.assets must be a non-empty list")
        return

    required = [
        "id",
        "asset_type",
        "source_card_ids",
        "allowed_slide_roles",
        "provenance_state",
        "text_editability",
        "license_state",
        "render_risks",
        "accessibility_risks",
    ]
    for index, asset in enumerate(assets):
        label = f"asset_memory.assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, asset, required, errors)
        for key in ["id", "provenance_state", "text_editability", "license_state"]:
            if key in asset:
                require_non_empty_string(f"{label}.{key}", asset[key], errors)
        if "asset_type" in asset:
            validate_choice(f"{label}.asset_type", asset["asset_type"], RUN2_ASSET_TYPES, errors)
        if "source_card_ids" in asset:
            validate_run2_source_references(f"{label}.source_card_ids", asset["source_card_ids"], card_ids, errors)
        for key in ["allowed_slide_roles", "render_risks", "accessibility_risks"]:
            if key in asset:
                validate_string_list(f"{label}.{key}", asset[key], errors)


def validate_run2_narrative_spine(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "narrative_spine.json", errors)
    require_keys("narrative_spine.json", data, ["schema_version", "deck_length", "slides"], errors)
    if "schema_version" in data:
        require_integer("narrative_spine.schema_version", data["schema_version"], errors)
    if "deck_length" in data:
        require_integer("narrative_spine.deck_length", data["deck_length"], errors)
    slides = data.get("slides", [])
    if not isinstance(slides, list) or not slides:
        errors.append("narrative_spine.slides must be a non-empty list")
        return

    required = ["id", "rhythm_role", "aesthetic_move_ids"]
    for index, slide in enumerate(slides):
        label = f"narrative_spine.slides[{index}]"
        if not isinstance(slide, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, slide, required, errors)
        if "id" in slide:
            require_non_empty_string(f"{label}.id", slide["id"], errors)
        if "rhythm_role" in slide:
            validate_choice(f"{label}.rhythm_role", slide["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "aesthetic_move_ids" in slide:
            validate_string_list(f"{label}.aesthetic_move_ids", slide["aesthetic_move_ids"], errors)


def validate_run2_slide_archetypes(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "slide_archetypes.json", errors)
    require_keys("slide_archetypes.json", data, ["schema_version", "archetypes"], errors)
    if "schema_version" in data:
        require_integer("slide_archetypes.schema_version", data["schema_version"], errors)
    archetypes = data.get("archetypes", [])
    if not isinstance(archetypes, list) or not archetypes:
        errors.append("slide_archetypes.archetypes must be a non-empty list")
        return

    required = ["id", "rhythm_role", "aesthetic_move_ids", "density_budget"]
    for index, archetype in enumerate(archetypes):
        label = f"slide_archetypes.archetypes[{index}]"
        if not isinstance(archetype, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, archetype, required, errors)
        if "id" in archetype:
            require_non_empty_string(f"{label}.id", archetype["id"], errors)
        if "rhythm_role" in archetype:
            validate_choice(f"{label}.rhythm_role", archetype["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "aesthetic_move_ids" in archetype:
            validate_string_list(f"{label}.aesthetic_move_ids", archetype["aesthetic_move_ids"], errors)
        if "density_budget" in archetype:
            validate_number_mapping(f"{label}.density_budget", archetype["density_budget"], errors)


def validate_run1_design_memory_observations(observations: list[Any], errors: list[str]) -> None:
    required = ["id", "source_ids", "principle", "code_generation_rule", "do_not_copy"]
    seen_ids: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"design_memory.observations[{index}] must be an object")
            continue
        require_keys(f"design_memory.observations[{index}]", observation, required, errors)
        for key in ["id", "principle", "code_generation_rule", "do_not_copy"]:
            if key in observation:
                require_non_empty_string(f"design_memory.observations[{index}].{key}", observation[key], errors)
        observation_id = observation.get("id")
        if isinstance(observation_id, str) and observation_id.strip():
            if observation_id in seen_ids:
                errors.append(f"design_memory.observations[{index}].id duplicates {observation_id}")
            seen_ids.add(observation_id)
        if "source_ids" in observation:
            validate_string_list(f"design_memory.observations[{index}].source_ids", observation["source_ids"], errors)


def validate_run1_5_design_memory_contract(data: dict[str, Any], errors: list[str]) -> None:
    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("design_memory.contract must be an object")
        return

    require_keys(
        "design_memory.contract",
        contract,
        ["required_fields", "allowed_source_roles", "allowed_slide_primitives"],
        errors,
    )
    if "required_fields" in contract:
        validate_exact_string_set(
            "design_memory.contract.required_fields",
            contract["required_fields"],
            set(RUN1_5_REQUIRED_MEMORY_FIELDS),
            errors,
        )
    if "allowed_source_roles" in contract:
        validate_exact_string_set(
            "design_memory.contract.allowed_source_roles",
            contract["allowed_source_roles"],
            RUN1_5_SOURCE_ROLES,
            errors,
        )
    if "allowed_slide_primitives" in contract:
        validate_exact_string_set(
            "design_memory.contract.allowed_slide_primitives",
            contract["allowed_slide_primitives"],
            RUN1_5_SLIDE_PRIMITIVES,
            errors,
        )


def validate_run1_5_design_memory_observations(observations: list[Any], errors: list[str]) -> None:
    required = [*RUN1_5_REQUIRED_MEMORY_FIELDS, "source_ids", "do_not_copy"]
    seen_ids: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"design_memory.observations[{index}] must be an object")
            continue
        require_keys(f"design_memory.observations[{index}]", observation, required, errors)
        for key in [*RUN1_5_REQUIRED_MEMORY_FIELDS, "do_not_copy"]:
            if key in observation and key not in {"source_role", "slide_primitive"}:
                require_non_empty_string(f"design_memory.observations[{index}].{key}", observation[key], errors)
        if "source_role" in observation:
            validate_choice(
                f"design_memory.observations[{index}].source_role",
                observation["source_role"],
                RUN1_5_SOURCE_ROLES,
                errors,
            )
        if "slide_primitive" in observation:
            validate_choice(
                f"design_memory.observations[{index}].slide_primitive",
                observation["slide_primitive"],
                RUN1_5_SLIDE_PRIMITIVES,
                errors,
            )
        evidence_id = observation.get("evidence_id")
        if isinstance(evidence_id, str) and evidence_id.strip():
            if evidence_id in seen_ids:
                errors.append(f"design_memory.observations[{index}].evidence_id duplicates {evidence_id}")
            seen_ids.add(evidence_id)
        if "source_ids" in observation:
            validate_string_list(f"design_memory.observations[{index}].source_ids", observation["source_ids"], errors)


def validate_design_memory(pack_dir: Path, errors: list[str], profile: str = "run1") -> None:
    data = load_json(pack_dir / "design_memory.json", errors)
    required_top_level = ["schema_version", "observations"]
    if profile == "run1_5":
        required_top_level.append("contract")
    require_keys("design_memory.json", data, required_top_level, errors)
    if "schema_version" in data:
        require_integer("design_memory.schema_version", data["schema_version"], errors)
    observations = data.get("observations", [])
    if not isinstance(observations, list) or not observations:
        errors.append("design_memory.observations must be a non-empty list")
        return

    if profile == "run1_5":
        validate_run1_5_design_memory_contract(data, errors)
        validate_run1_5_design_memory_observations(observations, errors)
    else:
        validate_run1_design_memory_observations(observations, errors)


def validate_markdown_not_empty(pack_dir: Path, errors: list[str], required_files: list[str]) -> None:
    for rel in required_files:
        if not rel.endswith(".md"):
            continue
        path = pack_dir / rel
        body = read_text_file(path, rel, errors)
        if body is not None and not body.strip():
            errors.append(f"{rel} must not be empty")


def validate_case_pack(pack_dir: str | Path, profile: str = "default") -> ValidationResult:
    root = Path(pack_dir)
    errors: list[str] = []
    try:
        required_files = required_files_for_profile(profile)
    except ValueError as exc:
        return ValidationResult(False, [str(exc)])
    if not root.exists():
        return ValidationResult(False, [f"case pack directory does not exist: {root}"])
    for rel in required_files:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif not path.is_file():
            errors.append(f"required path is not a file: {rel}")
    if errors:
        return ValidationResult(False, errors)

    validate_markdown_not_empty(root, errors, required_files)
    if profile == "run2":
        source_ids = validate_sources(root, errors)
        card_ids = collect_run2_card_ids(root, source_ids, errors)
        validate_run2_evidence_memory(root, card_ids, errors)
        validate_run2_aesthetic_memory(root, card_ids, errors)
        validate_run2_asset_memory(root, card_ids, errors)
        validate_run2_narrative_spine(root, errors)
        validate_run2_slide_archetypes(root, errors)
        return ValidationResult(not errors, errors)

    validate_sources(root, errors)
    validate_narrative_rules(root, errors)
    validate_style_tokens(root, errors)
    validate_asset_rules(root, errors)
    pattern_ids = validate_slide_patterns(root, errors)
    validate_deck_outline(root, pattern_ids, errors)
    if profile in {"run1", "run1_5"}:
        validate_design_memory(root, errors, profile=profile)
    return ValidationResult(not errors, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Vulca PPT case pack.")
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--profile", choices=["default", "run1", "run1_5", "run2"], default="default")
    args = parser.parse_args()
    result = validate_case_pack(args.pack_dir, profile=args.profile)
    if result.ok:
        print(f"case pack ok: {args.pack_dir}")
        return 0
    for error in result.errors:
        print(f"error: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
