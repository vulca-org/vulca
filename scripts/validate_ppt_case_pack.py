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
    "multimodal_database.json",
    "visual_learning_targets.json",
    "visual_target_components.json",
    "video_demo_beat_map.json",
    "motion_learning_targets.json",
    "presentation_sequence_components.json",
    "visual_repair_policy.json",
    "run2_7_commercial_usecase.json",
    "run2_7_multimodal_source_records.json",
    "run2_7_design_memory.json",
    "run2_7_workflow_policy.json",
    "source_cards/README.md",
    "video_cards/README.md",
    "evidence_memory.json",
    "aesthetic_memory.json",
    "asset_memory.json",
    "narrative_spine.json",
    "slide_archetypes.json",
    "aesthetic_rubric.md",
    "vulca_ppt_skill.md",
    "skill_workflow.json",
    "generation_briefs/README.md",
    "generation_briefs/prompt_only.md",
    "generation_briefs/run1_5_skill.md",
    "generation_briefs/run2_skill.md",
    "generation_briefs/bad_aesthetic_memory.md",
    "results/README.md",
    "results/comparison_report.md",
    "results/delivery_gate.md",
]


RUN2_8_REQUIRED_FILES = [
    "run2_8_tutorial_decomposition.json",
    "run2_8_executable_design_memory.json",
    "run2_8_workflow_gate_matrix.json",
    "results/trace_manifest_contract.json",
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
RUN2_MOTION_ROLES = {
    "attention_reset",
    "before_after_reveal",
    "proof_build",
    "scale_emphasis",
    "release_handoff",
}
RUN2_MULTIMODAL_MODALITIES = {"text", "image_reference", "video", "audio", "transcript", "interaction"}
RUN2_MULTIMODAL_ALLOWED_STORAGE = {
    "metadata_only",
    "derived_observations_only",
    "generated_assets_only",
    "local_untracked_cache_only",
}
RUN2_ASSET_TYPES = {
    "generated_background",
    "editable_svg",
    "native_shapes",
    "chart",
    "diagram",
    "video_derived_reference",
}
RUN2_EXTRACTION_UNIT_FIELDS = [
    "unit_id",
    "source_anchor",
    "derived_rule",
    "slide_role",
    "execution_guard",
    "qa_probe",
]
RUN2_FORBIDDEN_MEDIA_REFERENCE_MARKERS = (
    "http://",
    "https://",
    "data:image",
    "base64,",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp4",
    ".mov",
    ".mp3",
    ".wav",
    ".pptx",
    ".key",
)
RUN2_6R_REPAIR_IDS = {
    "repair_editorial_typography_system",
    "repair_spacing_token_visibility",
    "repair_climax_editorial_spread",
    "repair_theme_differentiation_from_run2_5",
    "repair_mini_preview_fidelity",
}
RUN2_6R_REPAIR_FIELDS = [
    "id",
    "target_slide_roles",
    "source_policy_ids",
    "typography_delta",
    "spacing_delta",
    "composition_delta",
    "theme_delta",
    "must_differ_from",
    "native_ppt_requirements",
    "qa_probe",
    "release_boundary",
]
RUN2_6R_REPAIR_ROLES = {"cover", "setup", "contrast", "proof", "climax", "close"}
RUN2_7_MEMORY_FIELDS = [
    "id",
    "source_record_ids",
    "applicable_usecases",
    "applicable_slide_roles",
    "typography_rules",
    "spacing_rules",
    "composition_rules",
    "rhythm_rules",
    "native_ppt_generation_requirements",
    "forbidden_patterns",
    "qa_probes",
    "release_boundary",
]
RUN2_7_TRACE_FIELDS = {
    "run2_7_usecase_id",
    "run2_7_source_record_ids",
    "run2_7_design_memory_ids",
    "run2_7_workflow_decision_ids",
    "run2_7_delta_from_run2_6r",
    "run2_7_quality_gate",
}
RUN2_8_DECOMPOSITION_FIELDS = [
    "id",
    "source_record_ids",
    "source_ids",
    "modality_mix",
    "tutorial_anchor",
    "observed_design_move",
    "derived_rule",
    "code_generation_binding",
    "native_ppt_obligation",
    "layout_budget",
    "failure_probe",
    "anti_copy_boundary",
    "qa_probe",
    "release_boundary",
]
RUN2_8_MEMORY_BINDING_FIELDS = [
    "id",
    "decomposition_unit_ids",
    "applies_to_slide_roles",
    "design_token",
    "code_binding",
    "native_ppt_constraints",
    "typography_constraints",
    "spacing_constraints",
    "composition_constraints",
    "negative_control_failure",
    "qa_probe",
    "release_boundary",
]
RUN2_8_GATE_FIELDS = [
    "id",
    "slide_role",
    "decomposition_unit_ids",
    "memory_binding_ids",
    "required_code_bindings",
    "layout_budget",
    "pass_fail_checks",
    "trace_fields",
    "public_release_gate",
]
RUN2_8_TRACE_FIELDS = {
    "run2_8_decomposition_unit_ids",
    "run2_8_memory_binding_ids",
    "run2_8_gate_matrix_ids",
    "run2_8_code_binding_ids",
    "run2_8_layout_budget",
    "run2_8_visual_delta_from_run2_7",
}
RUN2_8_RELEASE_BOUNDARY = "public_blocked_until_native_render_trace_and_human_review"
RUN2_8_SELECTION_CHAIN = {
    "commercial_usecase",
    "run2_8_decomposition_units",
    "run2_8_executable_memory_bindings",
    "run2_8_gate_matrix",
    "native_ppt_code_generation",
    "layout_quality_gate",
    "delivery_gate",
    "visual_qa_gate",
}
RUN2_8_WORKFLOW_STAGE_INPUTS = {
    "decompose_run2_8_tutorial_video_units": {
        "run2_8_tutorial_decomposition.json",
        "run2_7_multimodal_source_records.json",
        "sources.json",
    },
    "select_run2_8_executable_design_memory": {
        "run2_8_tutorial_decomposition.json",
        "run2_8_executable_design_memory.json",
    },
    "apply_run2_8_workflow_gate_matrix": {
        "run2_8_tutorial_decomposition.json",
        "run2_8_executable_design_memory.json",
        "run2_8_workflow_gate_matrix.json",
        "results/trace_manifest_contract.json",
    },
}
RUN2_8_CODE_BINDING_TERMS = {"fontSize", "bbox", "spacing", "heroObject", "beforeAfter", "workflowGate"}


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
        return [*RUN2_REQUIRED_FILES, *RUN2_8_REQUIRED_FILES]
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


def validate_no_external_media_reference(label: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in RUN2_FORBIDDEN_MEDIA_REFERENCE_MARKERS):
            errors.append(f"{label} must not include external media URLs or file references")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_no_external_media_reference(f"{label}[{index}]", item, errors)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_no_external_media_reference(f"{label}.{key}", item, errors)


def validate_public_blocked_boundary(label: str, value: Any, errors: list[str]) -> None:
    if require_non_empty_string(label, value, errors) and "public_blocked" not in value:
        errors.append(f"{label} must keep public_blocked status")


def validate_run2_8_release_boundary(label: str, value: Any, errors: list[str]) -> None:
    if require_non_empty_string(label, value, errors) and value != RUN2_8_RELEASE_BOUNDARY:
        errors.append(f"{label} must be {RUN2_8_RELEASE_BOUNDARY}")


def validate_known_string_references(
    label: str,
    value: Any,
    known_ids: set[str],
    unknown_name: str,
    errors: list[str],
) -> None:
    if not validate_string_list(label, value, errors):
        return
    for item in value:
        if item not in known_ids:
            errors.append(f"{label} references unknown {unknown_name}: {item}")


def validate_combined_terms(label: str, values: Any, terms: list[str], errors: list[str]) -> None:
    if not validate_string_list(label, values, errors):
        return
    combined = " ".join(values).lower()
    for term in terms:
        if term not in combined:
            errors.append(f"{label} must mention {term}")


def validate_string_mentions(label: str, value: Any, terms: list[str], errors: list[str]) -> None:
    if not require_non_empty_string(label, value, errors):
        return
    lowered = value.lower()
    for term in terms:
        if term.lower() not in lowered:
            errors.append(f"{label} must mention {term}")


def validate_run2_extraction_units(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    for index, unit in enumerate(value):
        unit_label = f"{label}[{index}]"
        if not isinstance(unit, dict):
            errors.append(f"{unit_label} must be an object")
            continue
        require_keys(unit_label, unit, RUN2_EXTRACTION_UNIT_FIELDS, errors)
        for key in RUN2_EXTRACTION_UNIT_FIELDS:
            if key not in unit:
                continue
            if key == "slide_role":
                validate_choice(f"{unit_label}.{key}", unit[key], RUN2_RHYTHM_ROLES, errors)
            else:
                require_non_empty_string(f"{unit_label}.{key}", unit[key], errors)


def validate_run2_multimodal_anchors(
    label: str,
    value: Any,
    record_modalities: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    required = ["anchor_id", "modality", "locator", "observation", "extracted_design_signal", "allowed_use"]
    seen_anchor_ids: set[str] = set()
    for index, anchor in enumerate(value):
        anchor_label = f"{label}[{index}]"
        if not isinstance(anchor, dict):
            errors.append(f"{anchor_label} must be an object")
            continue
        require_keys(anchor_label, anchor, required, errors)
        anchor_id = anchor.get("anchor_id")
        if "anchor_id" in anchor and require_non_empty_string(f"{anchor_label}.anchor_id", anchor_id, errors):
            if anchor_id in seen_anchor_ids:
                errors.append(f"{anchor_label}.anchor_id duplicates {anchor_id}")
            seen_anchor_ids.add(anchor_id)
        if "modality" in anchor:
            modality = anchor["modality"]
            if validate_choice(f"{anchor_label}.modality", modality, RUN2_MULTIMODAL_MODALITIES, errors):
                if modality not in record_modalities:
                    errors.append(f"{anchor_label}.modality {modality} is not listed in the parent record modalities")
        for key in ["locator", "observation", "extracted_design_signal"]:
            if key in anchor:
                require_non_empty_string(f"{anchor_label}.{key}", anchor[key], errors)
        if "allowed_use" in anchor:
            validate_choice(f"{anchor_label}.allowed_use", anchor["allowed_use"], RUN2_ALLOWED_USES, errors)


def validate_run2_multimodal_database(
    pack_dir: Path, source_ids: set[str], errors: list[str]
) -> tuple[set[str], set[str]]:
    data = load_json(pack_dir / "multimodal_database.json", errors)
    require_keys(
        "multimodal_database.json",
        data,
        [
            "schema_version",
            "status",
            "storage_policy",
            "required_modalities",
            "records",
            "cross_modal_design_tasks",
            "qa_gates",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("multimodal_database.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("multimodal_database.status", data["status"], errors)
    if "storage_policy" in data:
        storage_policy = data["storage_policy"]
        if require_non_empty_dict("multimodal_database.storage_policy", storage_policy, errors):
            for key in ["default", "raw_media", "copyright_boundary"]:
                if key in storage_policy:
                    require_non_empty_string(f"multimodal_database.storage_policy.{key}", storage_policy[key], errors)
            default_storage = storage_policy.get("default")
            if isinstance(default_storage, str) and default_storage not in RUN2_MULTIMODAL_ALLOWED_STORAGE:
                errors.append("multimodal_database.storage_policy.default must be an allowed storage policy")
            raw_media = storage_policy.get("raw_media")
            if isinstance(raw_media, str) and raw_media != "forbidden":
                errors.append("multimodal_database.storage_policy.raw_media must be forbidden")
    if "required_modalities" in data:
        validate_exact_string_set(
            "multimodal_database.required_modalities",
            data["required_modalities"],
            RUN2_MULTIMODAL_MODALITIES,
            errors,
        )

    records = data.get("records", [])
    if not require_non_empty_list("multimodal_database.records", records, errors):
        return set(), set()
    seen_record_ids: set[str] = set()
    seen_anchor_ids: set[str] = set()
    covered_modalities: set[str] = set()
    required_record_fields = [
        "id",
        "source_id",
        "source_kind",
        "modalities",
        "allowed_storage",
        "ingestion_status",
        "anchors",
        "derived_outputs",
        "do_not_store",
        "qa_gates",
    ]
    for index, record in enumerate(records):
        label = f"multimodal_database.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, record, required_record_fields, errors)
        record_id = record.get("id")
        if "id" in record and require_non_empty_string(f"{label}.id", record_id, errors):
            if record_id in seen_record_ids:
                errors.append(f"{label}.id duplicates {record_id}")
            seen_record_ids.add(record_id)
        source_id = record.get("source_id")
        if "source_id" in record:
            if require_non_empty_string(f"{label}.source_id", source_id, errors) and source_id not in source_ids:
                errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
        if "source_kind" in record:
            require_non_empty_string(f"{label}.source_kind", record["source_kind"], errors)
        record_modalities: set[str] = set()
        if "modalities" in record and validate_string_list(f"{label}.modalities", record["modalities"], errors):
            for modality in record["modalities"]:
                if modality not in RUN2_MULTIMODAL_MODALITIES:
                    errors.append(f"{label}.modalities has unexpected value: {modality}")
                else:
                    record_modalities.add(modality)
                    covered_modalities.add(modality)
        if "allowed_storage" in record:
            validate_choice(
                f"{label}.allowed_storage",
                record["allowed_storage"],
                RUN2_MULTIMODAL_ALLOWED_STORAGE,
                errors,
            )
        if "ingestion_status" in record:
            require_non_empty_string(f"{label}.ingestion_status", record["ingestion_status"], errors)
        if "anchors" in record:
            validate_run2_multimodal_anchors(f"{label}.anchors", record["anchors"], record_modalities, errors)
            if isinstance(record["anchors"], list):
                for anchor in record["anchors"]:
                    if isinstance(anchor, dict):
                        anchor_id = anchor.get("anchor_id")
                        if isinstance(anchor_id, str) and anchor_id.strip():
                            if anchor_id in seen_anchor_ids:
                                errors.append(f"{label}.anchors has duplicate global anchor_id: {anchor_id}")
                            seen_anchor_ids.add(anchor_id)
        for key in ["derived_outputs", "do_not_store", "qa_gates"]:
            if key in record:
                validate_string_list(f"{label}.{key}", record[key], errors)

    for modality in sorted(RUN2_MULTIMODAL_MODALITIES - covered_modalities):
        errors.append(f"multimodal_database.records missing modality coverage: {modality}")

    tasks = data.get("cross_modal_design_tasks", [])
    if require_non_empty_list("multimodal_database.cross_modal_design_tasks", tasks, errors):
        for index, task in enumerate(tasks):
            label = f"multimodal_database.cross_modal_design_tasks[{index}]"
            if not isinstance(task, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(label, task, ["id", "input_modalities", "task", "required_generator_behavior"], errors)
            for key in ["id", "task", "required_generator_behavior"]:
                if key in task:
                    require_non_empty_string(f"{label}.{key}", task[key], errors)
            if "input_modalities" in task and validate_string_list(
                f"{label}.input_modalities", task["input_modalities"], errors
            ):
                for modality in task["input_modalities"]:
                    if modality not in RUN2_MULTIMODAL_MODALITIES:
                        errors.append(f"{label}.input_modalities has unexpected value: {modality}")
    if "qa_gates" in data:
        validate_string_list("multimodal_database.qa_gates", data["qa_gates"], errors)
    return seen_record_ids, seen_anchor_ids


def validate_run2_visual_learning_targets(
    pack_dir: Path,
    multimodal_record_ids: set[str],
    multimodal_anchor_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "visual_learning_targets.json", errors)
    require_keys(
        "visual_learning_targets.json",
        data,
        ["schema_version", "status", "stage_policy", "native_editable_definition", "targets"],
        errors,
    )
    if "schema_version" in data:
        require_integer("visual_learning_targets.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("visual_learning_targets.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("visual_learning_targets.stage_policy must be repeat_same_five_layers_not_run3")
    if "native_editable_definition" in data:
        if validate_string_list(
            "visual_learning_targets.native_editable_definition", data["native_editable_definition"], errors
        ):
            combined_definition = " ".join(data["native_editable_definition"]).lower()
            if "native" not in combined_definition or "editable" not in combined_definition:
                errors.append("visual_learning_targets.native_editable_definition must define native editable output")
        validate_no_external_media_reference(
            "visual_learning_targets.native_editable_definition", data["native_editable_definition"], errors
        )

    targets = data.get("targets", [])
    if not require_non_empty_list("visual_learning_targets.targets", targets, errors):
        return set()
    required = [
        "id",
        "source_record_ids",
        "anchor_ids",
        "slide_roles",
        "failure_pattern",
        "desired_behavior",
        "code_generation_requirements",
        "qa_probe",
        "release_boundary",
    ]
    seen_target_ids: set[str] = set()
    for index, target in enumerate(targets):
        label = f"visual_learning_targets.targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, target, required, errors)
        target_id = target.get("id")
        if "id" in target and require_non_empty_string(f"{label}.id", target_id, errors):
            if target_id in seen_target_ids:
                errors.append(f"{label}.id duplicates {target_id}")
            seen_target_ids.add(target_id)
        if "source_record_ids" in target and validate_string_list(
            f"{label}.source_record_ids", target["source_record_ids"], errors
        ):
            for record_id in target["source_record_ids"]:
                if record_id not in multimodal_record_ids:
                    errors.append(f"{label}.source_record_ids references unknown multimodal record: {record_id}")
        if "anchor_ids" in target and validate_string_list(f"{label}.anchor_ids", target["anchor_ids"], errors):
            for anchor_id in target["anchor_ids"]:
                if anchor_id not in multimodal_anchor_ids:
                    errors.append(f"{label}.anchor_ids references unknown multimodal anchor: {anchor_id}")
        if "slide_roles" in target and validate_string_list(f"{label}.slide_roles", target["slide_roles"], errors):
            for role in target["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        for key in ["failure_pattern", "desired_behavior", "qa_probe", "release_boundary"]:
            if key in target:
                require_non_empty_string(f"{label}.{key}", target[key], errors)
                validate_no_external_media_reference(f"{label}.{key}", target[key], errors)
        if "code_generation_requirements" in target:
            if validate_string_list(
                f"{label}.code_generation_requirements", target["code_generation_requirements"], errors
            ):
                combined = " ".join(target["code_generation_requirements"]).lower()
                if "native" not in combined or "editable" not in combined:
                    errors.append(f"{label}.code_generation_requirements must require native editable output")
            validate_no_external_media_reference(
                f"{label}.code_generation_requirements",
                target["code_generation_requirements"],
                errors,
            )
        release_boundary = target.get("release_boundary")
        if isinstance(release_boundary, str) and "public_blocked" not in release_boundary:
            errors.append(f"{label}.release_boundary must keep public_blocked status")
    return seen_target_ids


def validate_run2_visual_target_components(
    pack_dir: Path,
    visual_target_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "visual_target_components.json", errors)
    require_keys(
        "visual_target_components.json",
        data,
        ["schema_version", "status", "stage_policy", "components", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("visual_target_components.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("visual_target_components.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("visual_target_components.stage_policy must be repeat_same_five_layers_not_run3")

    components = data.get("components", [])
    if not require_non_empty_list("visual_target_components.components", components, errors):
        return set()
    required = [
        "id",
        "target_ids",
        "slide_roles",
        "native_ppt_primitives",
        "layout_contract",
        "density_contract",
        "trace_fields",
        "generator_prompt",
        "qa_probe",
        "failure_modes",
        "release_boundary",
    ]
    seen_component_ids: set[str] = set()
    for index, component in enumerate(components):
        label = f"visual_target_components.components[{index}]"
        if not isinstance(component, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, component, required, errors)
        component_id = component.get("id")
        if "id" in component and require_non_empty_string(f"{label}.id", component_id, errors):
            if component_id in seen_component_ids:
                errors.append(f"{label}.id duplicates {component_id}")
            seen_component_ids.add(component_id)
        if "target_ids" in component and validate_string_list(f"{label}.target_ids", component["target_ids"], errors):
            for target_index, target_id in enumerate(component["target_ids"]):
                if target_id not in visual_target_ids:
                    errors.append(f"{label}.target_ids[{target_index}] references unknown visual target: {target_id}")
        if "slide_roles" in component and validate_string_list(
            f"{label}.slide_roles", component["slide_roles"], errors
        ):
            for role in component["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        if "native_ppt_primitives" in component:
            if validate_string_list(f"{label}.native_ppt_primitives", component["native_ppt_primitives"], errors):
                combined = " ".join(component["native_ppt_primitives"]).lower()
                if "native" not in combined or "editable" not in combined:
                    errors.append(f"{label}.native_ppt_primitives must require native editable PPT output")
            validate_no_external_media_reference(
                f"{label}.native_ppt_primitives", component["native_ppt_primitives"], errors
            )
        for key in ["layout_contract", "density_contract", "generator_prompt", "qa_probe", "release_boundary"]:
            if key in component:
                require_non_empty_string(f"{label}.{key}", component[key], errors)
                validate_no_external_media_reference(f"{label}.{key}", component[key], errors)
        for key in ["trace_fields", "failure_modes"]:
            if key in component:
                validate_string_list(f"{label}.{key}", component[key], errors)
                validate_no_external_media_reference(f"{label}.{key}", component[key], errors)
        release_boundary = component.get("release_boundary")
        if isinstance(release_boundary, str) and "public_blocked" not in release_boundary:
            errors.append(f"{label}.release_boundary must keep public_blocked status")

    if "qa_gates" in data:
        validate_string_list("visual_target_components.qa_gates", data["qa_gates"], errors)
    return seen_component_ids


def validate_run2_video_demo_beat_map(
    pack_dir: Path,
    source_ids: set[str],
    multimodal_record_ids: set[str],
    multimodal_anchor_ids: set[str],
    card_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "video_demo_beat_map.json", errors)
    require_keys(
        "video_demo_beat_map.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "beats", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("video_demo_beat_map.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("video_demo_beat_map.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("video_demo_beat_map.stage_policy must be repeat_same_five_layers_not_run3")
    if "storage_policy" in data:
        storage_policy = data["storage_policy"]
        if require_non_empty_dict("video_demo_beat_map.storage_policy", storage_policy, errors):
            raw_media = storage_policy.get("raw_media")
            if isinstance(raw_media, str) and raw_media != "forbidden":
                errors.append("video_demo_beat_map.storage_policy.raw_media must be forbidden")
            for key in ["default", "raw_media", "copyright_boundary"]:
                if key in storage_policy:
                    require_non_empty_string(f"video_demo_beat_map.storage_policy.{key}", storage_policy[key], errors)
        validate_no_external_media_reference("video_demo_beat_map.storage_policy", storage_policy, errors)

    beats = data.get("beats", [])
    if not require_non_empty_list("video_demo_beat_map.beats", beats, errors):
        return set()
    required = [
        "id",
        "source_id",
        "source_record_ids",
        "anchor_ids",
        "video_card_ids",
        "locator",
        "observed_demo_move",
        "derived_presentation_rule",
        "motion_role",
        "reveal_sequence",
        "pacing_signal",
        "do_not_store",
        "qa_probe",
        "release_boundary",
    ]
    seen_beat_ids: set[str] = set()
    for index, beat in enumerate(beats):
        label = f"video_demo_beat_map.beats[{index}]"
        if not isinstance(beat, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, beat, required, errors)
        validate_no_external_media_reference(label, beat, errors)
        beat_id = beat.get("id")
        if "id" in beat and require_non_empty_string(f"{label}.id", beat_id, errors):
            if beat_id in seen_beat_ids:
                errors.append(f"{label}.id duplicates {beat_id}")
            seen_beat_ids.add(beat_id)
        source_id = beat.get("source_id")
        if "source_id" in beat and require_non_empty_string(f"{label}.source_id", source_id, errors):
            if source_id not in source_ids:
                errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
        if "source_record_ids" in beat:
            validate_known_string_references(
                f"{label}.source_record_ids",
                beat["source_record_ids"],
                multimodal_record_ids,
                "multimodal record",
                errors,
            )
        if "anchor_ids" in beat:
            validate_known_string_references(
                f"{label}.anchor_ids",
                beat["anchor_ids"],
                multimodal_anchor_ids,
                "multimodal anchor",
                errors,
            )
        if "video_card_ids" in beat:
            validate_known_string_references(
                f"{label}.video_card_ids",
                beat["video_card_ids"],
                card_ids,
                "source or video card",
                errors,
            )
        for key in ["locator", "observed_demo_move", "derived_presentation_rule", "pacing_signal", "qa_probe"]:
            if key in beat:
                require_non_empty_string(f"{label}.{key}", beat[key], errors)
        if "motion_role" in beat:
            validate_choice(f"{label}.motion_role", beat["motion_role"], RUN2_MOTION_ROLES, errors)
        if "reveal_sequence" in beat:
            validate_combined_terms(f"{label}.reveal_sequence", beat["reveal_sequence"], ["native"], errors)
        if "do_not_store" in beat:
            if validate_string_list(f"{label}.do_not_store", beat["do_not_store"], errors):
                combined = " ".join(beat["do_not_store"]).lower()
                for term in ["video", "frames", "audio", "transcript"]:
                    if term not in combined:
                        errors.append(f"{label}.do_not_store must mention {term}")
        if "release_boundary" in beat:
            validate_public_blocked_boundary(f"{label}.release_boundary", beat["release_boundary"], errors)
    if "qa_gates" in data:
        validate_string_list("video_demo_beat_map.qa_gates", data["qa_gates"], errors)
        validate_no_external_media_reference("video_demo_beat_map.qa_gates", data["qa_gates"], errors)
    return seen_beat_ids


def validate_run2_motion_learning_targets(
    pack_dir: Path,
    beat_ids: set[str],
    visual_target_ids: set[str],
    visual_component_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "motion_learning_targets.json", errors)
    require_keys(
        "motion_learning_targets.json",
        data,
        ["schema_version", "status", "stage_policy", "targets", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("motion_learning_targets.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("motion_learning_targets.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("motion_learning_targets.stage_policy must be repeat_same_five_layers_not_run3")

    targets = data.get("targets", [])
    if not require_non_empty_list("motion_learning_targets.targets", targets, errors):
        return set()
    required = [
        "id",
        "beat_ids",
        "visual_target_ids",
        "visual_component_ids",
        "slide_roles",
        "motion_role",
        "failure_pattern",
        "desired_behavior",
        "code_generation_requirements",
        "qa_probe",
        "release_boundary",
    ]
    seen_target_ids: set[str] = set()
    for index, target in enumerate(targets):
        label = f"motion_learning_targets.targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, target, required, errors)
        validate_no_external_media_reference(label, target, errors)
        target_id = target.get("id")
        if "id" in target and require_non_empty_string(f"{label}.id", target_id, errors):
            if target_id in seen_target_ids:
                errors.append(f"{label}.id duplicates {target_id}")
            seen_target_ids.add(target_id)
        if "beat_ids" in target:
            validate_known_string_references(f"{label}.beat_ids", target["beat_ids"], beat_ids, "video beat", errors)
        if "visual_target_ids" in target:
            validate_known_string_references(
                f"{label}.visual_target_ids",
                target["visual_target_ids"],
                visual_target_ids,
                "visual target",
                errors,
            )
        if "visual_component_ids" in target:
            validate_known_string_references(
                f"{label}.visual_component_ids",
                target["visual_component_ids"],
                visual_component_ids,
                "visual component",
                errors,
            )
        if "slide_roles" in target and validate_string_list(f"{label}.slide_roles", target["slide_roles"], errors):
            for role in target["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        if "motion_role" in target:
            validate_choice(f"{label}.motion_role", target["motion_role"], RUN2_MOTION_ROLES, errors)
        for key in ["failure_pattern", "desired_behavior", "qa_probe"]:
            if key in target:
                require_non_empty_string(f"{label}.{key}", target[key], errors)
        if "code_generation_requirements" in target:
            validate_combined_terms(
                f"{label}.code_generation_requirements",
                target["code_generation_requirements"],
                ["native", "editable", "metadata", "trace"],
                errors,
            )
        if "release_boundary" in target:
            validate_public_blocked_boundary(f"{label}.release_boundary", target["release_boundary"], errors)
    if "qa_gates" in data:
        validate_string_list("motion_learning_targets.qa_gates", data["qa_gates"], errors)
        validate_no_external_media_reference("motion_learning_targets.qa_gates", data["qa_gates"], errors)
    return seen_target_ids


def validate_run2_presentation_sequence_components(
    pack_dir: Path,
    motion_target_ids: set[str],
    visual_component_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "presentation_sequence_components.json", errors)
    require_keys(
        "presentation_sequence_components.json",
        data,
        ["schema_version", "status", "stage_policy", "components", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("presentation_sequence_components.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("presentation_sequence_components.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("presentation_sequence_components.stage_policy must be repeat_same_five_layers_not_run3")

    components = data.get("components", [])
    if not require_non_empty_list("presentation_sequence_components.components", components, errors):
        return set()
    required = [
        "id",
        "motion_target_ids",
        "visual_component_ids",
        "slide_roles",
        "native_ppt_primitives",
        "sequence_steps",
        "trace_fields",
        "qa_probe",
        "failure_modes",
        "release_boundary",
    ]
    step_required = ["step_id", "order", "reveal_object", "trigger", "duration", "purpose"]
    seen_component_ids: set[str] = set()
    for index, component in enumerate(components):
        label = f"presentation_sequence_components.components[{index}]"
        if not isinstance(component, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, component, required, errors)
        validate_no_external_media_reference(label, component, errors)
        component_id = component.get("id")
        if "id" in component and require_non_empty_string(f"{label}.id", component_id, errors):
            if component_id in seen_component_ids:
                errors.append(f"{label}.id duplicates {component_id}")
            seen_component_ids.add(component_id)
        if "motion_target_ids" in component:
            validate_known_string_references(
                f"{label}.motion_target_ids",
                component["motion_target_ids"],
                motion_target_ids,
                "motion target",
                errors,
            )
        if "visual_component_ids" in component:
            validate_known_string_references(
                f"{label}.visual_component_ids",
                component["visual_component_ids"],
                visual_component_ids,
                "visual component",
                errors,
            )
        if "slide_roles" in component and validate_string_list(
            f"{label}.slide_roles", component["slide_roles"], errors
        ):
            for role in component["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        if "native_ppt_primitives" in component:
            validate_combined_terms(
                f"{label}.native_ppt_primitives",
                component["native_ppt_primitives"],
                ["native", "editable"],
                errors,
            )
        steps = component.get("sequence_steps", [])
        if require_non_empty_list(f"{label}.sequence_steps", steps, errors):
            seen_orders: list[int] = []
            for step_index, step in enumerate(steps):
                step_label = f"{label}.sequence_steps[{step_index}]"
                if not isinstance(step, dict):
                    errors.append(f"{step_label} must be an object")
                    continue
                require_keys(step_label, step, step_required, errors)
                if "order" in step and require_integer(f"{step_label}.order", step["order"], errors):
                    seen_orders.append(step["order"])
                for key in ["step_id", "reveal_object", "trigger", "duration", "purpose"]:
                    if key in step:
                        require_non_empty_string(f"{step_label}.{key}", step[key], errors)
            expected_orders = list(range(1, len(seen_orders) + 1))
            if seen_orders != expected_orders:
                errors.append(f"{label}.sequence_steps order must be sequential starting at 1")
        if "trace_fields" in component:
            if validate_string_list(f"{label}.trace_fields", component["trace_fields"], errors):
                required_trace = {"motion_target_ids", "sequence_component_ids"}
                actual_trace = set(component["trace_fields"])
                for trace_field in sorted(required_trace - actual_trace):
                    errors.append(f"{label}.trace_fields missing value: {trace_field}")
        for key in ["qa_probe", "release_boundary"]:
            if key in component:
                require_non_empty_string(f"{label}.{key}", component[key], errors)
        if "failure_modes" in component:
            validate_string_list(f"{label}.failure_modes", component["failure_modes"], errors)
        if "release_boundary" in component:
            validate_public_blocked_boundary(f"{label}.release_boundary", component["release_boundary"], errors)
    if "qa_gates" in data:
        validate_string_list("presentation_sequence_components.qa_gates", data["qa_gates"], errors)
        validate_no_external_media_reference("presentation_sequence_components.qa_gates", data["qa_gates"], errors)
    return seen_component_ids


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
    common_required = [
        "schema_version",
        "card_id",
        "source_id",
        "source_type",
        "allowed_use",
        "do_not_copy",
        "extraction_units",
    ]
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
            if "extraction_units" in card:
                validate_run2_extraction_units(f"{card_label}.extraction_units", card["extraction_units"], errors)

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


def validate_run2_aesthetic_move_references(
    label: str,
    aesthetic_move_ids: Any,
    move_ids: set[str],
    errors: list[str],
) -> None:
    if not validate_string_list(label, aesthetic_move_ids, errors):
        return
    for index, move_id in enumerate(aesthetic_move_ids):
        if move_id not in move_ids:
            errors.append(f"{label}[{index}] {move_id} is not defined in aesthetic_memory.json")


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


def validate_run2_aesthetic_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "aesthetic_memory.json", errors)
    require_keys("aesthetic_memory.json", data, ["schema_version", "moves"], errors)
    if "schema_version" in data:
        require_integer("aesthetic_memory.schema_version", data["schema_version"], errors)
    moves = data.get("moves", [])
    if not isinstance(moves, list) or not moves:
        errors.append("aesthetic_memory.moves must be a non-empty list")
        return set()

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
    move_ids: set[str] = set()
    for index, move in enumerate(moves):
        label = f"aesthetic_memory.moves[{index}]"
        if not isinstance(move, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, move, required, errors)
        for key in string_fields:
            if key in move:
                require_non_empty_string(f"{label}.{key}", move[key], errors)
        move_id = move.get("id")
        if isinstance(move_id, str) and move_id.strip():
            if move_id in move_ids:
                errors.append(f"{label}.id duplicates {move_id}")
            move_ids.add(move_id)
        if "source_card_ids" in move:
            validate_run2_source_references(f"{label}.source_card_ids", move["source_card_ids"], card_ids, errors)
        if "density_budget" in move:
            validate_number_mapping(f"{label}.density_budget", move["density_budget"], errors)
        if "rhythm_role" in move:
            validate_choice(f"{label}.rhythm_role", move["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "negative_rules" in move:
            validate_string_list(f"{label}.negative_rules", move["negative_rules"], errors)
    return move_ids


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


def validate_run2_narrative_spine(pack_dir: Path, move_ids: set[str], errors: list[str]) -> None:
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
            validate_run2_aesthetic_move_references(
                f"{label}.aesthetic_move_ids",
                slide["aesthetic_move_ids"],
                move_ids,
                errors,
            )


def validate_run2_slide_archetypes(pack_dir: Path, move_ids: set[str], errors: list[str]) -> None:
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
            validate_run2_aesthetic_move_references(
                f"{label}.aesthetic_move_ids",
                archetype["aesthetic_move_ids"],
                move_ids,
                errors,
            )
        if "density_budget" in archetype:
            validate_number_mapping(f"{label}.density_budget", archetype["density_budget"], errors)


def validate_run2_8_skill_workflow_contract(
    stage_indexes: dict[str, int],
    stage_inputs: dict[str, set[str]],
    errors: list[str],
) -> None:
    stage_ids = list(RUN2_8_WORKFLOW_STAGE_INPUTS)
    for stage_id, expected_inputs in RUN2_8_WORKFLOW_STAGE_INPUTS.items():
        if stage_id not in stage_indexes:
            errors.append(f"skill_workflow.stages missing required Run 2.8 stage: {stage_id}")
            continue
        missing_inputs = expected_inputs - stage_inputs.get(stage_id, set())
        for item in sorted(missing_inputs):
            errors.append(f"skill_workflow.stages[{stage_id}].inputs missing value: {item}")

    if "generate_code_first_ppt" not in stage_indexes:
        errors.append("skill_workflow.stages missing required generation stage: generate_code_first_ppt")
        return

    generation_index = stage_indexes["generate_code_first_ppt"]
    for stage_id in stage_ids:
        if stage_id in stage_indexes and stage_indexes[stage_id] >= generation_index:
            errors.append(f"skill_workflow.stages[{stage_id}] must appear before generate_code_first_ppt")

    for before, after in zip(stage_ids, stage_ids[1:]):
        if before in stage_indexes and after in stage_indexes and stage_indexes[before] >= stage_indexes[after]:
            errors.append(f"skill_workflow.stages[{before}] must appear before {after}")


def validate_run2_skill_workflow(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "skill_workflow.json", errors)
    require_keys(
        "skill_workflow.json",
        data,
        ["schema_version", "workflow_type", "stages", "repair_triggers", "release_decisions"],
        errors,
    )
    if "schema_version" in data:
        require_integer("skill_workflow.schema_version", data["schema_version"], errors)
    if "workflow_type" in data:
        require_non_empty_string("skill_workflow.workflow_type", data["workflow_type"], errors)
    if "stage_policy" in data:
        if data["stage_policy"] != "repeat_same_five_layers_not_run3":
            errors.append("skill_workflow.stage_policy must be repeat_same_five_layers_not_run3")
    if "five_layer_loop" in data:
        validate_exact_string_set(
            "skill_workflow.five_layer_loop",
            data["five_layer_loop"],
            {
                "real_commercial_case",
                "multimodal_tutorial_case_data",
                "evidence_aesthetic_asset_memory",
                "skill_workflow",
                "rerun_and_evaluation",
            },
            errors,
        )
    if "release_decisions" in data:
        validate_string_list("skill_workflow.release_decisions", data["release_decisions"], errors)

    stages = data.get("stages", [])
    if not require_non_empty_list("skill_workflow.stages", stages, errors):
        return
    expected_order = 1
    seen_stage_ids: set[str] = set()
    stage_indexes: dict[str, int] = {}
    stage_inputs: dict[str, set[str]] = {}
    for index, stage in enumerate(stages):
        label = f"skill_workflow.stages[{index}]"
        if not isinstance(stage, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, stage, ["id", "order", "layer", "inputs", "outputs", "gates"], errors)
        if "id" in stage and require_non_empty_string(f"{label}.id", stage["id"], errors):
            if stage["id"] in seen_stage_ids:
                errors.append(f"{label}.id duplicates {stage['id']}")
            seen_stage_ids.add(stage["id"])
            stage_indexes[stage["id"]] = index
        if "order" in stage and require_integer(f"{label}.order", stage["order"], errors):
            if stage["order"] != expected_order:
                errors.append(f"{label}.order must be {expected_order}")
            expected_order += 1
        if "layer" in stage:
            require_non_empty_string(f"{label}.layer", stage["layer"], errors)
        for key in ["inputs", "outputs", "gates"]:
            if key in stage:
                valid_strings = validate_string_list(f"{label}.{key}", stage[key], errors)
                if key == "inputs" and valid_strings and isinstance(stage.get("id"), str):
                    stage_inputs[stage["id"]] = set(stage["inputs"])

    validate_run2_8_skill_workflow_contract(stage_indexes, stage_inputs, errors)

    triggers = data.get("repair_triggers", [])
    if not require_non_empty_list("skill_workflow.repair_triggers", triggers, errors):
        return
    for index, trigger in enumerate(triggers):
        label = f"skill_workflow.repair_triggers[{index}]"
        if not isinstance(trigger, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, trigger, ["id", "trigger", "recommendation", "human_gate"], errors)
        for key in ["id", "trigger", "recommendation", "human_gate"]:
            if key in trigger:
                require_non_empty_string(f"{label}.{key}", trigger[key], errors)


def validate_run2_visual_repair_policy(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "visual_repair_policy.json", errors)
    require_keys(
        "visual_repair_policy.json",
        data,
        ["schema_version", "status", "stage_policy", "default_visual_direction", "repairs"],
        errors,
    )
    if "schema_version" in data:
        require_integer("visual_repair_policy.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_6r_visual_repair_policy_public_blocked":
        errors.append("visual_repair_policy.status must be run2_6r_visual_repair_policy_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("visual_repair_policy.stage_policy must be repeat_same_five_layers_not_run3")
    if (
        "default_visual_direction" in data
        and data["default_visual_direction"] != "light_first_editorial_graphite_with_vivid_proof_color"
    ):
        errors.append(
            "visual_repair_policy.default_visual_direction must be "
            "light_first_editorial_graphite_with_vivid_proof_color"
        )

    repairs = data.get("repairs", [])
    if not require_non_empty_list("visual_repair_policy.repairs", repairs, errors):
        return set()

    seen_repair_ids: set[str] = set()
    for index, repair in enumerate(repairs):
        label = f"visual_repair_policy.repairs[{index}]"
        if not isinstance(repair, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, repair, RUN2_6R_REPAIR_FIELDS, errors)
        repair_id = repair.get("id")
        if "id" in repair and require_non_empty_string(f"{label}.id", repair_id, errors):
            if repair_id in seen_repair_ids:
                errors.append(f"{label}.id duplicates {repair_id}")
            seen_repair_ids.add(repair_id)
        if "target_slide_roles" in repair and validate_string_list(
            f"{label}.target_slide_roles",
            repair["target_slide_roles"],
            errors,
        ):
            for role_index, role in enumerate(repair["target_slide_roles"]):
                validate_choice(
                    f"{label}.target_slide_roles[{role_index}]",
                    role,
                    RUN2_6R_REPAIR_ROLES,
                    errors,
                )
        if "source_policy_ids" in repair:
            validate_string_list(f"{label}.source_policy_ids", repair["source_policy_ids"], errors)
        for key in ["typography_delta", "spacing_delta", "composition_delta"]:
            if key in repair:
                require_non_empty_string(f"{label}.{key}", repair[key], errors)
        if "theme_delta" in repair:
            validate_string_mentions(f"{label}.theme_delta", repair["theme_delta"], ["forest-green", "source-brand"], errors)
        if "must_differ_from" in repair:
            validate_exact_string_set(
                f"{label}.must_differ_from",
                repair["must_differ_from"],
                {"ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"},
                errors,
            )
        if "native_ppt_requirements" in repair:
            validate_combined_terms(f"{label}.native_ppt_requirements", repair["native_ppt_requirements"], ["native", "editable"], errors)
        if "qa_probe" in repair:
            validate_string_mentions(f"{label}.qa_probe", repair["qa_probe"], ["contact sheet"], errors)
        if "release_boundary" in repair:
            validate_public_blocked_boundary(f"{label}.release_boundary", repair["release_boundary"], errors)

    for repair_id in sorted(RUN2_6R_REPAIR_IDS - seen_repair_ids):
        errors.append(f"visual_repair_policy.repairs missing repair id: {repair_id}")
    for repair_id in sorted(seen_repair_ids - RUN2_6R_REPAIR_IDS):
        errors.append(f"visual_repair_policy.repairs has unexpected repair id: {repair_id}")
    return seen_repair_ids


def validate_run2_7_commercial_usecase(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "run2_7_commercial_usecase.json", errors)
    require_keys(
        "run2_7_commercial_usecase.json",
        data,
        [
            "schema_version",
            "status",
            "stage_policy",
            "id",
            "primary_usecase",
            "audience",
            "business_job",
            "business_decision",
            "deck_mission",
            "six_slide_arc",
            "must_show",
            "must_not_show",
            "proof_questions",
            "release_boundary",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_commercial_usecase.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_commercial_usecase_public_blocked":
        errors.append("run2_7_commercial_usecase.status must be run2_7_commercial_usecase_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_commercial_usecase.stage_policy must be repeat_same_five_layers_not_run3")
    usecase_id = data.get("id")
    usecase_ids: set[str] = set()
    if "id" in data and require_non_empty_string("run2_7_commercial_usecase.id", usecase_id, errors):
        usecase_ids.add(usecase_id)
    for key in ["primary_usecase", "business_decision", "deck_mission"]:
        if key in data:
            require_non_empty_string(f"run2_7_commercial_usecase.{key}", data[key], errors)
    if "audience" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.audience",
            data["audience"],
            ["ai product builders", "design engineering leaders", "technical founders"],
            errors,
        )
    if "business_job" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.business_job",
            data["business_job"],
            ["product-system learning", "not one-shot prompting"],
            errors,
        )
    if "must_not_show" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.must_not_show",
            data["must_not_show"],
            ["copy", "source brand", "full-slide raster"],
            errors,
        )
    if "proof_questions" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.proof_questions",
            data["proof_questions"],
            ["data", "memory", "workflow", "ppt"],
            errors,
        )
    if "must_show" in data:
        validate_string_list("run2_7_commercial_usecase.must_show", data["must_show"], errors)
    arc = data.get("six_slide_arc", [])
    if require_non_empty_list("run2_7_commercial_usecase.six_slide_arc", arc, errors):
        expected_roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
        actual_roles: list[str] = []
        for index, slide in enumerate(arc):
            label = f"run2_7_commercial_usecase.six_slide_arc[{index}]"
            if not isinstance(slide, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(label, slide, ["slide_id", "rhythm_role", "job", "must_show", "must_not_show"], errors)
            if "slide_id" in slide:
                require_non_empty_string(f"{label}.slide_id", slide["slide_id"], errors)
            role = slide.get("rhythm_role")
            if "rhythm_role" in slide and validate_choice(f"{label}.rhythm_role", role, RUN2_6R_REPAIR_ROLES, errors):
                actual_roles.append(role)
            if "job" in slide:
                require_non_empty_string(f"{label}.job", slide["job"], errors)
            for key in ["must_show", "must_not_show"]:
                if key in slide:
                    validate_string_list(f"{label}.{key}", slide[key], errors)
        if actual_roles != expected_roles:
            errors.append("run2_7_commercial_usecase.six_slide_arc rhythm_role order must be cover, setup, contrast, proof, climax, close")
    if "release_boundary" in data:
        validate_public_blocked_boundary("run2_7_commercial_usecase.release_boundary", data["release_boundary"], errors)
    return usecase_ids


def validate_run2_7_source_records(pack_dir: Path, source_ids: set[str], errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "run2_7_multimodal_source_records.json", errors)
    require_keys(
        "run2_7_multimodal_source_records.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "records", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_multimodal_source_records.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_multimodal_source_records_public_blocked":
        errors.append("run2_7_multimodal_source_records.status must be run2_7_multimodal_source_records_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_multimodal_source_records.stage_policy must be repeat_same_five_layers_not_run3")
    storage_policy = data.get("storage_policy")
    if isinstance(storage_policy, dict):
        raw_media = storage_policy.get("raw_media")
        if isinstance(raw_media, str) and raw_media != "forbidden":
            errors.append("run2_7_multimodal_source_records.storage_policy.raw_media must be forbidden")
    elif "storage_policy" in data:
        errors.append("run2_7_multimodal_source_records.storage_policy must be a non-empty object")
    if "qa_gates" in data:
        validate_string_list("run2_7_multimodal_source_records.qa_gates", data["qa_gates"], errors)

    records = data.get("records", [])
    if not require_non_empty_list("run2_7_multimodal_source_records.records", records, errors):
        return set()
    required = [
        "id",
        "source_id",
        "source_type",
        "allowed_use",
        "anchor",
        "modalities",
        "visual_observation",
        "transcript_or_teaching_claim",
        "extracted_design_rule",
        "slide_roles",
        "native_ppt_implication",
        "anti_copy_boundary",
        "qa_probe",
        "release_boundary",
    ]
    seen_record_ids: set[str] = set()
    covered_modalities: set[str] = set()
    for index, record in enumerate(records):
        label = f"run2_7_multimodal_source_records.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, record, required, errors)
        record_id = record.get("id")
        if "id" in record and require_non_empty_string(f"{label}.id", record_id, errors):
            if record_id in seen_record_ids:
                errors.append(f"{label}.id duplicates {record_id}")
            seen_record_ids.add(record_id)
        source_id = record.get("source_id")
        if "source_id" in record and require_non_empty_string(f"{label}.source_id", source_id, errors):
            if source_id not in source_ids:
                errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
        if "allowed_use" in record and record["allowed_use"] != "derived_rules_only":
            errors.append(f"{label}.allowed_use must be derived_rules_only")
        if "modalities" in record and validate_string_list(f"{label}.modalities", record["modalities"], errors):
            for modality in record["modalities"]:
                if modality not in RUN2_MULTIMODAL_MODALITIES:
                    errors.append(f"{label}.modalities has unexpected value: {modality}")
                else:
                    covered_modalities.add(modality)
        if "slide_roles" in record and validate_string_list(f"{label}.slide_roles", record["slide_roles"], errors):
            for role in record["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        for key in ["source_type", "anchor", "visual_observation", "transcript_or_teaching_claim", "extracted_design_rule"]:
            if key in record:
                require_non_empty_string(f"{label}.{key}", record[key], errors)
        if "native_ppt_implication" in record:
            validate_string_mentions(f"{label}.native_ppt_implication", record["native_ppt_implication"], ["native", "editable"], errors)
        if "anti_copy_boundary" in record:
            validate_string_mentions(f"{label}.anti_copy_boundary", record["anti_copy_boundary"], ["do not copy"], errors)
        if "qa_probe" in record:
            validate_string_mentions(f"{label}.qa_probe", record["qa_probe"], ["contact sheet"], errors)
        if "release_boundary" in record:
            validate_public_blocked_boundary(f"{label}.release_boundary", record["release_boundary"], errors)
    for modality in sorted(RUN2_MULTIMODAL_MODALITIES - covered_modalities):
        errors.append(f"run2_7_multimodal_source_records.records missing modality coverage: {modality}")
    return seen_record_ids


def validate_run2_7_design_memory(
    pack_dir: Path,
    source_record_ids: set[str],
    usecase_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "run2_7_design_memory.json", errors)
    require_keys(
        "run2_7_design_memory.json",
        data,
        ["schema_version", "status", "stage_policy", "memory_type", "memories", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_design_memory.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_design_memory_public_blocked":
        errors.append("run2_7_design_memory.status must be run2_7_design_memory_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_design_memory.stage_policy must be repeat_same_five_layers_not_run3")
    if "memory_type" in data and data["memory_type"] != "deterministic_serializable_rules":
        errors.append("run2_7_design_memory.memory_type must be deterministic_serializable_rules")
    if "qa_gates" in data:
        validate_string_list("run2_7_design_memory.qa_gates", data["qa_gates"], errors)

    memories = data.get("memories", [])
    if not require_non_empty_list("run2_7_design_memory.memories", memories, errors):
        return set()
    memory_ids: set[str] = set()
    for index, memory in enumerate(memories):
        label = f"run2_7_design_memory.memories[{index}]"
        if not isinstance(memory, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, memory, RUN2_7_MEMORY_FIELDS, errors)
        memory_id = memory.get("id")
        if "id" in memory and require_non_empty_string(f"{label}.id", memory_id, errors):
            if memory_id in memory_ids:
                errors.append(f"{label}.id duplicates {memory_id}")
            memory_ids.add(memory_id)
        if "source_record_ids" in memory:
            validate_known_string_references(
                f"{label}.source_record_ids",
                memory["source_record_ids"],
                source_record_ids,
                "Run 2.7 source record",
                errors,
            )
        if "applicable_usecases" in memory:
            validate_known_string_references(
                f"{label}.applicable_usecases",
                memory["applicable_usecases"],
                usecase_ids,
                "Run 2.7 usecase",
                errors,
            )
        if "applicable_slide_roles" in memory and validate_string_list(
            f"{label}.applicable_slide_roles", memory["applicable_slide_roles"], errors
        ):
            for role in memory["applicable_slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.applicable_slide_roles has unexpected value: {role}")
        for key in ["typography_rules", "spacing_rules", "composition_rules", "rhythm_rules", "forbidden_patterns"]:
            if key in memory:
                validate_string_list(f"{label}.{key}", memory[key], errors)
        if "native_ppt_generation_requirements" in memory:
            validate_combined_terms(
                f"{label}.native_ppt_generation_requirements",
                memory["native_ppt_generation_requirements"],
                ["native", "editable", "trace"],
                errors,
            )
        if "qa_probes" in memory:
            validate_combined_terms(f"{label}.qa_probes", memory["qa_probes"], ["contact sheet"], errors)
        if "release_boundary" in memory:
            validate_public_blocked_boundary(f"{label}.release_boundary", memory["release_boundary"], errors)
    return memory_ids


def validate_run2_7_workflow_policy(
    pack_dir: Path,
    source_record_ids: set[str],
    usecase_ids: set[str],
    memory_ids: set[str],
    visual_repair_ids: set[str],
    errors: list[str],
) -> None:
    data = load_json(pack_dir / "run2_7_workflow_policy.json", errors)
    require_keys(
        "run2_7_workflow_policy.json",
        data,
        [
            "schema_version",
            "status",
            "stage_policy",
            "commercial_usecase_id",
            "selection_chain",
            "slide_role_memory_map",
            "qa_gates",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_workflow_policy.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_workflow_policy_public_blocked":
        errors.append("run2_7_workflow_policy.status must be run2_7_workflow_policy_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_workflow_policy.stage_policy must be repeat_same_five_layers_not_run3")
    if "qa_gates" in data:
        validate_string_list("run2_7_workflow_policy.qa_gates", data["qa_gates"], errors)
    usecase_id = data.get("commercial_usecase_id")
    if "commercial_usecase_id" in data and require_non_empty_string(
        "run2_7_workflow_policy.commercial_usecase_id", usecase_id, errors
    ):
        if usecase_id not in usecase_ids:
            errors.append(f"run2_7_workflow_policy.commercial_usecase_id references unknown Run 2.7 usecase: {usecase_id}")
    if "selection_chain" in data:
        validate_exact_string_set(
            "run2_7_workflow_policy.selection_chain",
            data["selection_chain"],
            {
                "commercial_usecase",
                "source_record_ids",
                "typography_memory_id",
                "spacing_memory_id",
                "composition_memory_id",
                "rhythm_memory_id",
                "brand_sanitization_memory_id",
                "visual_repair_policy_ids",
                "native_ppt_generation",
                "qa_gate",
            },
            errors,
        )

    mappings = data.get("slide_role_memory_map", [])
    if not require_non_empty_list("run2_7_workflow_policy.slide_role_memory_map", mappings, errors):
        return
    required = [
        "rhythm_role",
        "commercial_usecase_id",
        "source_record_ids",
        "design_memory_ids",
        "workflow_decision_ids",
        "visual_repair_policy_ids",
        "native_ppt_generation",
        "workflow_gates",
        "trace_fields",
    ]
    for index, mapping in enumerate(mappings):
        label = f"run2_7_workflow_policy.slide_role_memory_map[{index}]"
        if not isinstance(mapping, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, mapping, required, errors)
        if "rhythm_role" in mapping:
            validate_choice(f"{label}.rhythm_role", mapping["rhythm_role"], RUN2_6R_REPAIR_ROLES, errors)
        if "commercial_usecase_id" in mapping:
            mapping_usecase_id = mapping["commercial_usecase_id"]
            if require_non_empty_string(f"{label}.commercial_usecase_id", mapping_usecase_id, errors):
                if mapping_usecase_id not in usecase_ids:
                    errors.append(f"{label}.commercial_usecase_id references unknown Run 2.7 usecase: {mapping_usecase_id}")
        if "source_record_ids" in mapping:
            validate_known_string_references(
                f"{label}.source_record_ids",
                mapping["source_record_ids"],
                source_record_ids,
                "Run 2.7 source record",
                errors,
            )
        if "design_memory_ids" in mapping:
            validate_known_string_references(
                f"{label}.design_memory_ids",
                mapping["design_memory_ids"],
                memory_ids,
                "Run 2.7 design memory",
                errors,
            )
        if "workflow_decision_ids" in mapping:
            validate_string_list(f"{label}.workflow_decision_ids", mapping["workflow_decision_ids"], errors)
        if "visual_repair_policy_ids" in mapping:
            validate_known_string_references(
                f"{label}.visual_repair_policy_ids",
                mapping["visual_repair_policy_ids"],
                visual_repair_ids,
                "visual repair policy",
                errors,
            )
        if "native_ppt_generation" in mapping:
            validate_string_mentions(f"{label}.native_ppt_generation", mapping["native_ppt_generation"], ["native", "editable"], errors)
        if "workflow_gates" in mapping:
            validate_combined_terms(
                f"{label}.workflow_gates",
                mapping["workflow_gates"],
                ["public_blocked", "native", "source-brand"],
                errors,
            )
        if "trace_fields" in mapping:
            validate_exact_string_set(f"{label}.trace_fields", mapping["trace_fields"], RUN2_7_TRACE_FIELDS, errors)


def validate_run2_8_trace_manifest_contract(pack_dir: Path, errors: list[str]) -> set[str]:
    path = pack_dir / "results" / "trace_manifest_contract.json"
    if not path.exists():
        return set()
    data = load_json(path, errors)
    require_keys(
        "trace_manifest_contract.json",
        data,
        ["schema_version", "per_slide_required_fields"],
        errors,
    )
    if "schema_version" in data:
        require_integer("trace_manifest_contract.schema_version", data["schema_version"], errors)
    fields = data.get("per_slide_required_fields", [])
    if not validate_string_list("trace_manifest_contract.per_slide_required_fields", fields, errors):
        return set()
    actual = set(fields)
    for field in sorted(RUN2_8_TRACE_FIELDS - actual):
        errors.append(f"trace_manifest_contract.per_slide_required_fields missing value: {field}")
    return actual


def validate_run2_8_tutorial_decomposition(
    pack_dir: Path,
    source_ids: set[str],
    run2_7_source_record_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "run2_8_tutorial_decomposition.json", errors)
    require_keys(
        "run2_8_tutorial_decomposition.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "units"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_8_tutorial_decomposition.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_8_tutorial_decomposition_public_blocked":
        errors.append(
            "run2_8_tutorial_decomposition.status must be run2_8_tutorial_decomposition_public_blocked"
        )
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_8_tutorial_decomposition.stage_policy must be repeat_same_five_layers_not_run3")
    storage_policy = data.get("storage_policy")
    if isinstance(storage_policy, dict):
        raw_media = storage_policy.get("raw_media")
        if isinstance(raw_media, str) and raw_media != "forbidden":
            errors.append("run2_8_tutorial_decomposition.storage_policy.raw_media must be forbidden")
        validate_no_external_media_reference("run2_8_tutorial_decomposition.storage_policy", storage_policy, errors)
    elif "storage_policy" in data:
        errors.append("run2_8_tutorial_decomposition.storage_policy must be a non-empty object")

    units = data.get("units", [])
    if not require_non_empty_list("run2_8_tutorial_decomposition.units", units, errors):
        return set()
    unit_ids: set[str] = set()
    derived_modalities = {"video", "audio", "transcript", "image_reference", "interaction"}
    for index, unit in enumerate(units):
        label = f"run2_8_tutorial_decomposition.units[{index}]"
        if not isinstance(unit, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, unit, RUN2_8_DECOMPOSITION_FIELDS, errors)
        validate_no_external_media_reference(label, unit, errors)
        unit_id = unit.get("id")
        if "id" in unit and require_non_empty_string(f"{label}.id", unit_id, errors):
            if unit_id in unit_ids:
                errors.append(f"{label}.id duplicates {unit_id}")
            unit_ids.add(unit_id)
        if "source_record_ids" in unit:
            validate_known_string_references(
                f"{label}.source_record_ids",
                unit["source_record_ids"],
                run2_7_source_record_ids,
                "Run 2.7 source record",
                errors,
            )
        if "source_ids" in unit:
            validate_known_string_references(
                f"{label}.source_ids",
                unit["source_ids"],
                source_ids,
                "source",
                errors,
            )
        if "modality_mix" in unit and validate_string_list(f"{label}.modality_mix", unit["modality_mix"], errors):
            actual_modalities = set(unit["modality_mix"])
            for modality in actual_modalities:
                if modality not in RUN2_MULTIMODAL_MODALITIES:
                    errors.append(f"{label}.modality_mix has unexpected value: {modality}")
            if not actual_modalities & derived_modalities:
                errors.append(f"{label}.modality_mix must include video, audio, transcript, image_reference, or interaction")
        for key in [
            "tutorial_anchor",
            "observed_design_move",
            "derived_rule",
            "native_ppt_obligation",
            "failure_probe",
            "anti_copy_boundary",
            "qa_probe",
        ]:
            if key in unit:
                require_non_empty_string(f"{label}.{key}", unit[key], errors)
        if "code_generation_binding" in unit:
            if require_non_empty_string(f"{label}.code_generation_binding", unit["code_generation_binding"], errors):
                validate_string_mentions(f"{label}.code_generation_binding", unit["code_generation_binding"], ["native"], errors)
        if "layout_budget" in unit:
            validate_number_mapping(f"{label}.layout_budget", unit["layout_budget"], errors)
        if "release_boundary" in unit:
            validate_run2_8_release_boundary(f"{label}.release_boundary", unit["release_boundary"], errors)
    return unit_ids


def validate_run2_8_executable_design_memory(
    pack_dir: Path,
    decomposition_unit_ids: set[str],
    errors: list[str],
) -> tuple[set[str], set[str]]:
    data = load_json(pack_dir / "run2_8_executable_design_memory.json", errors)
    require_keys(
        "run2_8_executable_design_memory.json",
        data,
        ["schema_version", "status", "stage_policy", "memory_type", "bindings"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_8_executable_design_memory.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_8_executable_design_memory_public_blocked":
        errors.append(
            "run2_8_executable_design_memory.status must be run2_8_executable_design_memory_public_blocked"
        )
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_8_executable_design_memory.stage_policy must be repeat_same_five_layers_not_run3")
    if "memory_type" in data and data["memory_type"] != "executable_schema_bindings":
        errors.append("run2_8_executable_design_memory.memory_type must be executable_schema_bindings")

    bindings = data.get("bindings", [])
    if not require_non_empty_list("run2_8_executable_design_memory.bindings", bindings, errors):
        return set(), set()
    binding_ids: set[str] = set()
    code_binding_ids: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"run2_8_executable_design_memory.bindings[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, binding, RUN2_8_MEMORY_BINDING_FIELDS, errors)
        validate_no_external_media_reference(label, binding, errors)
        binding_id = binding.get("id")
        if "id" in binding and require_non_empty_string(f"{label}.id", binding_id, errors):
            if binding_id in binding_ids:
                errors.append(f"{label}.id duplicates {binding_id}")
            binding_ids.add(binding_id)
        if "decomposition_unit_ids" in binding:
            validate_known_string_references(
                f"{label}.decomposition_unit_ids",
                binding["decomposition_unit_ids"],
                decomposition_unit_ids,
                "Run 2.8 decomposition unit",
                errors,
            )
        if "applies_to_slide_roles" in binding and validate_string_list(
            f"{label}.applies_to_slide_roles",
            binding["applies_to_slide_roles"],
            errors,
        ):
            for role in binding["applies_to_slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.applies_to_slide_roles has unexpected value: {role}")
        for key in [
            "native_ppt_constraints",
            "typography_constraints",
            "spacing_constraints",
            "composition_constraints",
        ]:
            if key in binding:
                validate_string_list(f"{label}.{key}", binding[key], errors)
        for key in ["design_token", "negative_control_failure", "qa_probe"]:
            if key in binding:
                require_non_empty_string(f"{label}.{key}", binding[key], errors)
        code_binding = binding.get("code_binding")
        if "code_binding" in binding:
            if require_non_empty_dict(f"{label}.code_binding", code_binding, errors):
                require_keys(f"{label}.code_binding", code_binding, ["function_name", "params", "layout_budget"], errors)
                function_name = code_binding.get("function_name")
                if "function_name" in code_binding and require_non_empty_string(
                    f"{label}.code_binding.function_name",
                    function_name,
                    errors,
                ):
                    code_binding_ids.add(function_name)
                if "params" in code_binding:
                    require_non_empty_dict(f"{label}.code_binding.params", code_binding["params"], errors)
                if "layout_budget" in code_binding:
                    require_non_empty_dict(f"{label}.code_binding.layout_budget", code_binding["layout_budget"], errors)
                code_binding_text = json.dumps(code_binding)
                if not any(term in code_binding_text for term in RUN2_8_CODE_BINDING_TERMS):
                    errors.append(f"{label}.code_binding must mention a Run 2.8 code binding term")
        if "release_boundary" in binding:
            validate_run2_8_release_boundary(f"{label}.release_boundary", binding["release_boundary"], errors)
    return binding_ids, code_binding_ids


def validate_run2_8_workflow_gate_matrix(
    pack_dir: Path,
    decomposition_unit_ids: set[str],
    memory_binding_ids: set[str],
    code_binding_ids: set[str],
    trace_fields: set[str],
    errors: list[str],
) -> None:
    data = load_json(pack_dir / "run2_8_workflow_gate_matrix.json", errors)
    require_keys(
        "run2_8_workflow_gate_matrix.json",
        data,
        ["schema_version", "status", "stage_policy", "selection_chain", "gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_8_workflow_gate_matrix.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_8_workflow_gate_matrix_public_blocked":
        errors.append("run2_8_workflow_gate_matrix.status must be run2_8_workflow_gate_matrix_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_8_workflow_gate_matrix.stage_policy must be repeat_same_five_layers_not_run3")
    if "selection_chain" in data:
        validate_exact_string_set(
            "run2_8_workflow_gate_matrix.selection_chain",
            data["selection_chain"],
            RUN2_8_SELECTION_CHAIN,
            errors,
        )

    gates = data.get("gates", [])
    if not require_non_empty_list("run2_8_workflow_gate_matrix.gates", gates, errors):
        return
    gate_ids: set[str] = set()
    for index, gate in enumerate(gates):
        label = f"run2_8_workflow_gate_matrix.gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, gate, RUN2_8_GATE_FIELDS, errors)
        validate_no_external_media_reference(label, gate, errors)
        gate_id = gate.get("id")
        if "id" in gate and require_non_empty_string(f"{label}.id", gate_id, errors):
            if gate_id in gate_ids:
                errors.append(f"{label}.id duplicates {gate_id}")
            gate_ids.add(gate_id)
        if "slide_role" in gate:
            validate_choice(f"{label}.slide_role", gate["slide_role"], RUN2_6R_REPAIR_ROLES, errors)
        if "decomposition_unit_ids" in gate:
            validate_known_string_references(
                f"{label}.decomposition_unit_ids",
                gate["decomposition_unit_ids"],
                decomposition_unit_ids,
                "Run 2.8 decomposition unit",
                errors,
            )
        if "memory_binding_ids" in gate:
            validate_known_string_references(
                f"{label}.memory_binding_ids",
                gate["memory_binding_ids"],
                memory_binding_ids,
                "Run 2.8 memory binding",
                errors,
            )
        if "required_code_bindings" in gate:
            validate_known_string_references(
                f"{label}.required_code_bindings",
                gate["required_code_bindings"],
                code_binding_ids,
                "Run 2.8 code binding",
                errors,
            )
        if "layout_budget" in gate:
            validate_number_mapping(f"{label}.layout_budget", gate["layout_budget"], errors)
        if "pass_fail_checks" in gate:
            validate_string_list(f"{label}.pass_fail_checks", gate["pass_fail_checks"], errors)
        if "trace_fields" in gate and validate_string_list(f"{label}.trace_fields", gate["trace_fields"], errors):
            actual_trace_fields = set(gate["trace_fields"])
            for field in sorted(RUN2_8_TRACE_FIELDS - actual_trace_fields):
                errors.append(f"{label}.trace_fields missing value: {field}")
            for field in gate["trace_fields"]:
                if trace_fields and field not in trace_fields:
                    errors.append(f"{label}.trace_fields references unknown trace field: {field}")
        if "public_release_gate" in gate:
            validate_run2_8_release_boundary(f"{label}.public_release_gate", gate["public_release_gate"], errors)


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
    run2_8_enabled = profile == "run2"
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
        multimodal_record_ids, multimodal_anchor_ids = validate_run2_multimodal_database(root, source_ids, errors)
        visual_target_ids = validate_run2_visual_learning_targets(
            root,
            multimodal_record_ids,
            multimodal_anchor_ids,
            errors,
        )
        visual_component_ids = validate_run2_visual_target_components(root, visual_target_ids, errors)
        beat_ids = validate_run2_video_demo_beat_map(
            root,
            source_ids,
            multimodal_record_ids,
            multimodal_anchor_ids,
            card_ids,
            errors,
        )
        motion_target_ids = validate_run2_motion_learning_targets(
            root,
            beat_ids,
            visual_target_ids,
            visual_component_ids,
            errors,
        )
        validate_run2_presentation_sequence_components(root, motion_target_ids, visual_component_ids, errors)
        validate_run2_evidence_memory(root, card_ids, errors)
        move_ids = validate_run2_aesthetic_memory(root, card_ids, errors)
        validate_run2_asset_memory(root, card_ids, errors)
        validate_run2_narrative_spine(root, move_ids, errors)
        validate_run2_slide_archetypes(root, move_ids, errors)
        validate_run2_skill_workflow(root, errors)
        visual_repair_ids = validate_run2_visual_repair_policy(root, errors)
        run2_7_usecase_ids = validate_run2_7_commercial_usecase(root, errors)
        run2_7_source_record_ids = validate_run2_7_source_records(root, source_ids, errors)
        run2_7_memory_ids = validate_run2_7_design_memory(
            root,
            run2_7_source_record_ids,
            run2_7_usecase_ids,
            errors,
        )
        validate_run2_7_workflow_policy(
            root,
            run2_7_source_record_ids,
            run2_7_usecase_ids,
            run2_7_memory_ids,
            visual_repair_ids,
            errors,
        )
        if run2_8_enabled:
            trace_fields = validate_run2_8_trace_manifest_contract(root, errors)
            run2_8_decomposition_unit_ids = validate_run2_8_tutorial_decomposition(
                root,
                source_ids,
                run2_7_source_record_ids,
                errors,
            )
            run2_8_memory_binding_ids, run2_8_code_binding_ids = validate_run2_8_executable_design_memory(
                root,
                run2_8_decomposition_unit_ids,
                errors,
            )
            validate_run2_8_workflow_gate_matrix(
                root,
                run2_8_decomposition_unit_ids,
                run2_8_memory_binding_ids,
                run2_8_code_binding_ids,
                trace_fields,
                errors,
            )
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
