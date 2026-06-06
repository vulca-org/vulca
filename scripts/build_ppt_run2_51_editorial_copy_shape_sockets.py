from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS_DIR = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_51_editorial_shape_text_repair_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_51_editorial_shape_text_repair_result.md"

RUN_ID = "2.51"
SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "editorial_copy_and_shape_text_socket_repair"
NEXT_ACTION = "consume_run2_51_before_run2_52_four_arm_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_52_four_arm_rerun"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
FORBIDDEN_PUBLIC_TERMS = [
    "run2",
    "memory",
    "workflow gate",
    "trace",
    "audit",
    "negative control",
    "public blocked",
]

ROLE_ARCHETYPES = {
    "cover": {
        "primary_archetype": "poster_stage",
        "required_sockets": [
            "headline_plane",
            "hero_object_caption",
            "proof_badge",
            "source_boundary_whisper",
        ],
        "shape_primitives": ["stage", "spotlight", "stamp_badge", "ribbon"],
    },
    "setup": {
        "primary_archetype": "route_map",
        "required_sockets": [
            "failure_path_title",
            "route_node_labels",
            "break_risk_marker",
            "selected_route_claim",
        ],
        "shape_primitives": ["route_path", "bracket_callout", "stamp_badge", "depth_stack"],
    },
    "contrast": {
        "primary_archetype": "before_after_lens",
        "required_sockets": ["before_caption", "after_claim", "delta_marker", "implication_line"],
        "shape_primitives": ["lens", "route_path", "bracket_callout", "spotlight"],
    },
    "proof": {
        "primary_archetype": "workspace_surface",
        "required_sockets": [
            "workspace_title",
            "lane_labels",
            "proof_nuggets",
            "inspectable_object_captions",
        ],
        "shape_primitives": ["stage", "depth_stack", "bracket_callout", "stamp_badge"],
    },
    "climax": {
        "primary_archetype": "exploded_hero_object",
        "required_sockets": [
            "result_headline",
            "exploded_proof_tags",
            "release_boundary_tag",
            "memory_route_label",
        ],
        "shape_primitives": ["exploded_layers", "spotlight", "ribbon", "bracket_callout"],
    },
    "close": {
        "primary_archetype": "decision_room",
        "required_sockets": [
            "decision_headline",
            "gate_labels",
            "next_action_strip",
            "residual_blocker_caption",
        ],
        "shape_primitives": ["decision_wall", "route_path", "ribbon", "stamp_badge"],
    },
}

COPY_BUDGETS = {
    "headline": {"max_words": 7, "max_chars": 48, "max_lines": 2},
    "subline": {"max_words": 18, "max_chars": 120, "max_lines": 3},
    "proof_nugget": {"max_words": 8, "max_chars": 54, "max_lines": 2},
    "annotation": {"max_words": 6, "max_chars": 42, "max_lines": 2},
    "state_label": {"max_words": 4, "max_chars": 28, "max_lines": 1},
}

ROLE_COPY: dict[str, dict[str, Any]] = {
    "cover": {
        "headline": "Design decks people can judge",
        "subline": "Turn messy design evidence into a launch-ready presentation path.",
        "proof_nuggets": ["Real brief selected", "Evidence becomes design", "Deck stays editable"],
        "annotations": ["Usecase locked", "Public copy only", "No raw process"],
        "state_labels": ["Brief", "Learn", "Build"],
        "business_claim": "The product can convert design evidence into an editable launch presentation.",
    },
    "setup": {
        "headline": "The old path stays boxy",
        "subline": "Prompt-only decks miss the route from evidence to visual decision.",
        "proof_nuggets": ["Failure is visible", "Route is selected", "Risk is named"],
        "annotations": ["Before state", "Decision path", "Break point"],
        "state_labels": ["Fail", "Route", "Select"],
        "business_claim": "The setup slide explains the commercial failure and the selected correction route.",
    },
    "contrast": {
        "headline": "Evidence changes the surface",
        "subline": "The after state must show a business consequence, not another equal card set.",
        "proof_nuggets": ["Before is smaller", "After owns focus", "Delta is explicit"],
        "annotations": ["Before", "After", "Why it matters"],
        "state_labels": ["Before", "After", "Delta"],
        "business_claim": "The contrast slide must make the improvement legible as a business outcome.",
    },
    "proof": {
        "headline": "Proof lives inside the workspace",
        "subline": "Each proof point is attached to an inspectable object, lane, or surface.",
        "proof_nuggets": ["Decision lane", "Preview object", "Review state"],
        "annotations": ["Active lane", "Proof object", "Review state"],
        "state_labels": ["Lane", "Proof", "Review"],
        "business_claim": "The proof slide shows how evidence becomes a working presentation surface.",
    },
    "climax": {
        "headline": "One result owns the frame",
        "subline": "The peak slide needs one dominant generated result with attached proof tags.",
        "proof_nuggets": ["Result object", "Layered proof", "Release boundary"],
        "annotations": ["Large result", "Proof tag", "Boundary"],
        "state_labels": ["Result", "Proof", "Gate"],
        "business_claim": "The climax slide must focus attention on the generated result and its evidence.",
    },
    "close": {
        "headline": "Ship only after the gate",
        "subline": "The handoff makes next action clear while release remains blocked.",
        "proof_nuggets": ["Decision wall", "Next action", "Residual blocker"],
        "annotations": ["Decision", "Next step", "Blocked item"],
        "state_labels": ["Gate", "Next", "Hold"],
        "business_claim": "The close slide turns evaluation into a clear release decision.",
    },
}

TRACE_FIELDS = [
    "run2_51_editorial_copy_memory_id",
    "run2_51_shape_text_socket_memory_id",
    "run2_51_renderer_archetype_gate_id",
    "run2_51_primary_archetype",
    "run2_51_public_surface_copy_status",
    "run2_51_text_socket_placement_status",
    "run2_51_shape_vocabulary_status",
    "run2_51_character_fit_status",
    "run2_51_forbidden_surface_terms_count",
    "run2_51_equal_card_cluster_count",
    "run2_51_semantic_primitive_count",
]

GEOMETRY_CONSTRAINTS = {
    "stage": "poster-scale field; not an equal card; owns the headline plane",
    "route_path": "connected path with at least three node sockets and visible connectors",
    "lens": "oval, circle, or cropped-window comparison surface; not a plain rectangle",
    "exploded_layers": "at least three offset layers with scale separation and connector lines",
    "bracket_callout": "brace, bracket, or leader line that anchors annotation copy",
    "ribbon": "narrow strip or diagonal strip for state labels; smaller than the main surface",
    "stamp_badge": "compact proof marker with status or proof socket",
    "spotlight": "clipped focus field that creates contrast around the main object",
    "depth_stack": "unequal overlapping layers with visible offset",
    "decision_wall": "handoff surface with gate/action sockets and grouped decisions",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def count_words(value: str) -> int:
    return len([part for part in re.split(r"\s+", value.strip()) if part])


def role_record(records: list[dict[str, Any]], role: str, key: str) -> dict[str, Any]:
    for record in records:
        if record.get("role") == role:
            return record
    raise ValueError(f"missing {key} for role {role}")


def selected_usecase() -> dict[str, Any]:
    bank = read_json(PACK / "commercial_usecase_bank.json")
    for usecase in bank["usecases"]:
        if usecase["id"] == SELECTED_USECASE_ID:
            return usecase
    raise ValueError(f"missing selected usecase {SELECTED_USECASE_ID}")


def assert_no_run251_deck_artifacts() -> None:
    if not PRESENTATIONS_DIR.exists():
        return
    deck_paths = sorted(
        path
        for pattern in ("*2-51*.ppt", "*2-51*.pptx")
        for path in PRESENTATIONS_DIR.glob(pattern)
    )
    if deck_paths:
        names = ", ".join(path.name for path in deck_paths)
        raise ValueError(f"Run 2.51 is data/workflow-only and must not create PPT artifacts: {names}")


def validate_inputs(
    run249_result: dict[str, Any],
    run249_readability: dict[str, Any],
    run249_density: dict[str, Any],
    run249_gates: dict[str, Any],
    run250_result: dict[str, Any],
) -> None:
    if run249_result.get("status") != "run2_49_readability_content_density_renderer_repair_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 repair result")
    if run249_readability.get("status") != "run2_49_readability_memory_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 readability memory")
    if run249_density.get("status") != "run2_49_content_evidence_density_memory_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 content evidence density memory")
    if run249_gates.get("status") != "run2_49_editorial_renderer_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 editorial renderer workflow gates")
    if run250_result.get("status") != "run2_50_readability_density_renderer_rerun_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.50 rerun result")
    quality_delta = run250_result.get("quality_delta") or {}
    if quality_delta.get("target_layer") != "readability_content_density_and_editorial_renderer_binding":
        raise ValueError("Run 2.50 quality_delta.target_layer must be readability/content-density/editorial-renderer binding")
    if quality_delta.get("source_data_status") != "run2_49_repair_pack_consumed_before_native_ppt_drawing":
        raise ValueError("Run 2.50 must prove Run 2.49 repair pack consumption before Run 2.51")
    repair_modules = quality_delta.get("repair_modules")
    if not isinstance(repair_modules, list) or len(repair_modules) != 6:
        raise ValueError("Run 2.50 quality_delta.repair_modules must be a list with exactly six items")
    if len(run249_readability.get("readability_records") or []) != 6:
        raise ValueError("Run 2.51 expected six Run 2.49 readability records")
    if len(run249_density.get("content_evidence_density_records") or []) != 6:
        raise ValueError("Run 2.51 expected six Run 2.49 density records")
    if len(run249_gates.get("editorial_renderer_workflow_gates") or []) != 6:
        raise ValueError("Run 2.51 expected six Run 2.49 renderer gate records")


def assert_copy_fits_budget(role: str, bundle: dict[str, Any]) -> None:
    headline = str(bundle["headline"])
    subline = str(bundle["subline"])
    if count_words(headline) > COPY_BUDGETS["headline"]["max_words"]:
        raise ValueError(f"{role} headline exceeds word budget")
    if len(headline) > COPY_BUDGETS["headline"]["max_chars"]:
        raise ValueError(f"{role} headline exceeds character budget")
    if count_words(subline) > COPY_BUDGETS["subline"]["max_words"]:
        raise ValueError(f"{role} subline exceeds word budget")
    if len(subline) > COPY_BUDGETS["subline"]["max_chars"]:
        raise ValueError(f"{role} subline exceeds character budget")
    for key, budget_key in (
        ("proof_nuggets", "proof_nugget"),
        ("annotations", "annotation"),
        ("state_labels", "state_label"),
    ):
        for value in bundle[key]:
            if count_words(value) > COPY_BUDGETS[budget_key]["max_words"]:
                raise ValueError(f"{role} {key} exceeds word budget: {value}")
            if len(value) > COPY_BUDGETS[budget_key]["max_chars"]:
                raise ValueError(f"{role} {key} exceeds character budget: {value}")
    lowered = " ".join(
        [headline, subline, *bundle["proof_nuggets"], *bundle["annotations"], *bundle["state_labels"]]
    ).lower()
    for term in FORBIDDEN_PUBLIC_TERMS:
        if term in lowered:
            raise ValueError(f"{role} public copy contains forbidden term: {term}")


def build_editorial_copy_memory(
    run249_readability: dict[str, Any],
    run249_density: dict[str, Any],
    run250_result: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    readability_records = run249_readability["readability_records"]
    density_records = run249_density["content_evidence_density_records"]
    for role in ROLES:
        readability = role_record(readability_records, role, "Run 2.49 readability")
        density = role_record(density_records, role, "Run 2.49 density")
        copy = ROLE_COPY[role]
        bundle = {
            "headline": copy["headline"],
            "subline": copy["subline"],
            "proof_nuggets": copy["proof_nuggets"],
            "annotations": copy["annotations"],
            "state_labels": copy["state_labels"],
        }
        assert_copy_fits_budget(role, bundle)
        records.append(
            {
                "copy_memory_id": f"editorial_copy_2_51_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_run_ids": ["2.49", "2.50"],
                "required_run2_49_readability_memory_id": readability["readability_memory_id"],
                "required_run2_49_content_evidence_density_memory_id": density[
                    "content_evidence_density_memory_id"
                ],
                "raw_evidence_inputs": {
                    "readability_goal": readability["readability_goal"],
                    "business_proof_points": density.get("business_proof_points", []),
                    "run2_50_quality_delta": (run250_result.get("quality_delta") or {}).get("target_layer"),
                },
                "public_surface_copy_bundle": bundle,
                "trace_only_copy_bundle": {
                    "source_status": run250_result.get("status"),
                    "source_data_status": (run250_result.get("quality_delta") or {}).get("source_data_status"),
                },
                "copy_fit_budget": COPY_BUDGETS,
                "forbidden_surface_terms": FORBIDDEN_PUBLIC_TERMS,
                "business_claim_preservation_check": copy["business_claim"],
                "visual_validation_deferred_to_generated_rerun": True,
                "bad_control_probe": "Bad control fails if public copy is raw Run 2.49/2.50 workflow language.",
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )
    return {
        "schema_version": "ppt_run2_editorial_copy_memory.v1",
        "status": "run2_51_editorial_copy_memory_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "target_layer": TARGET_LAYER,
        "editorial_copy_records": records,
    }


def copy_role_for_socket(socket_name: str) -> str:
    if "headline" in socket_name or "title" in socket_name or "claim" in socket_name:
        return "headline"
    if "caption" in socket_name or "implication" in socket_name or "whisper" in socket_name:
        return "subline"
    if "proof" in socket_name:
        return "proof_nugget"
    if "label" in socket_name or "tag" in socket_name or "marker" in socket_name:
        return "state_label"
    return "annotation"


def socket_contracts_for(role: str, archetype: dict[str, Any]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for index, socket_name in enumerate(archetype["required_sockets"], start=1):
        copy_role = copy_role_for_socket(socket_name)
        budget = COPY_BUDGETS[copy_role]
        primitive = archetype["shape_primitives"][(index - 1) % len(archetype["shape_primitives"])]
        contracts.append(
            {
                "socket_id": f"socket_2_51_{role}_{socket_name}",
                "copy_role": copy_role,
                "owning_shape_id": f"shape_2_51_{role}_{primitive}_{index}",
                "placement_rule": (
                    f"bind {socket_name} to {primitive} with visible padding and no float-away label"
                ),
                "max_lines": budget["max_lines"],
                "font_size_range": [11, 34] if copy_role == "headline" else [8, 18],
                "character_budget": budget["max_chars"],
                "minimum_padding": 8,
                "alignment": "center" if copy_role == "headline" else "left",
                "overflow_policy": "reject_and_recompile",
            }
        )
    if not any(contract["copy_role"] == "proof_nugget" for contract in contracts):
        proof_socket_name = f"{role}_derived_proof_socket"
        budget = COPY_BUDGETS["proof_nugget"]
        primitive = archetype["shape_primitives"][0]
        contracts.append(
            {
                "socket_id": f"socket_2_51_{role}_{proof_socket_name}",
                "copy_role": "proof_nugget",
                "owning_shape_id": f"shape_2_51_{role}_{primitive}_derived_proof",
                "placement_rule": (
                    f"bind derived proof socket to {primitive} with visible proof ownership and no detached proof label"
                ),
                "max_lines": budget["max_lines"],
                "font_size_range": [8, 18],
                "character_budget": budget["max_chars"],
                "minimum_padding": 8,
                "alignment": "left",
                "overflow_policy": "reject_and_recompile",
                "fallback_reason": "required proof socket added because the archetype socket list had no proof_nugget lane",
            }
        )
    return contracts


def build_shape_text_socket_memory(
    copy_memory: dict[str, Any],
    run249_gates: dict[str, Any],
) -> dict[str, Any]:
    copy_records = copy_memory["editorial_copy_records"]
    prior_gates = run249_gates["editorial_renderer_workflow_gates"]
    records: list[dict[str, Any]] = []
    for role in ROLES:
        copy_record = role_record(copy_records, role, "Run 2.51 copy")
        prior_gate = role_record(prior_gates, role, "Run 2.49 renderer gate")
        archetype = ROLE_ARCHETYPES[role]
        socket_contracts = socket_contracts_for(role, archetype)
        proof_socket_ids = [
            contract["socket_id"] for contract in socket_contracts if contract["copy_role"] == "proof_nugget"
        ]
        if not proof_socket_ids:
            raise ValueError(f"Run 2.51 role {role} must have at least one proof_nugget socket")
        constraints = [GEOMETRY_CONSTRAINTS[primitive] for primitive in archetype["shape_primitives"]]
        records.append(
            {
                "socket_memory_id": f"shape_text_socket_2_51_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_run_ids": ["2.49", "2.50"],
                "required_editorial_copy_memory_id": copy_record["copy_memory_id"],
                "required_run2_49_editorial_renderer_gate_id": prior_gate["gate_id"],
                "primary_archetype": archetype["primary_archetype"],
                "shape_primitives": archetype["shape_primitives"],
                "socket_contracts": socket_contracts,
                "geometry_constraints": constraints,
                "proof_socket_ids": proof_socket_ids,
                "copy_role_bindings": {
                    "headline": "dominant archetype title socket",
                    "subline": "secondary semantic surface socket",
                    "proof_nugget": "proof object, path node, badge, callout, or layer tag",
                    "annotation": "bracket, leader, or caption socket",
                    "state_label": "ribbon, badge, or node label socket",
                },
                "fit_checks": [
                    "character budget passes before drawing",
                    "max-line budget passes before drawing",
                    "public copy is bound to a socket, not a free-floating label",
                ],
                "forbidden_layout_patterns": [
                    "equal card cluster as primary surface",
                    "plain rectangle renamed as lens",
                    "proof text detached from proof object",
                    "workflow terms rendered as public labels",
                ],
                "bad_control_probe": "Bad control fails if it draws text without Run 2.51 socket ids.",
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )
    return {
        "schema_version": "ppt_run2_shape_text_socket_memory.v1",
        "status": "run2_51_shape_text_socket_memory_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "target_layer": TARGET_LAYER,
        "shape_text_socket_records": records,
    }


def build_renderer_archetype_workflow_gates(
    copy_memory: dict[str, Any],
    socket_memory: dict[str, Any],
) -> dict[str, Any]:
    copy_records = copy_memory["editorial_copy_records"]
    socket_records = socket_memory["shape_text_socket_records"]
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        copy_record = role_record(copy_records, role, "Run 2.51 copy")
        socket_record = role_record(socket_records, role, "Run 2.51 socket")
        gates.append(
            {
                "gate_id": f"gate_2_51_{role}_renderer_archetype",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_editorial_copy_memory_id": copy_record["copy_memory_id"],
                "required_shape_text_socket_memory_id": socket_record["socket_memory_id"],
                "primary_archetype": socket_record["primary_archetype"],
                "forbid_square_block_grid_as_primary_surface": True,
                "max_equal_card_clusters": 1,
                "min_semantic_primitives": 3,
                "min_socket_bound_public_text_elements": 4,
                "max_socket_bound_public_text_elements": 7,
                "require_character_fit_status": True,
                "require_forbidden_surface_terms_count_zero": True,
                "visual_validation_deferred_to_generated_rerun": True,
                "consumer_contract": {
                    "next_generated_run": "2.52",
                    "must_bind_before_public_text": True,
                    "required_trace_fields": TRACE_FIELDS,
                },
                "next_rerun_contract": NEXT_RERUN_CONTRACT,
                "required_trace_fields": TRACE_FIELDS,
                "pass_fail_checks": [
                    "Run 2.52 binds one Run 2.51 editorial copy memory id before drawing public text.",
                    "Run 2.52 binds one Run 2.51 shape text socket memory id before drawing semantic surfaces.",
                    "Slide has one primary archetype and at least three semantic primitives.",
                    "Every public proof nugget is socket-bound to a proof object, path node, badge, callout, or layer tag.",
                    "Forbidden workflow terms have count zero on the public surface.",
                    "Bad control fails without Run 2.51 copy/socket/archetype ids.",
                ],
                "bad_control_probe": (
                    "A negative control may reuse Run 2.49/2.50 context, but fails if it lacks Run 2.51 "
                    "copy, socket, and archetype gate ids."
                ),
                "public_release_gate": "blocked",
            }
        )
    return {
        "schema_version": "ppt_run2_renderer_archetype_workflow_gates.v1",
        "status": "run2_51_renderer_archetype_workflow_gates_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "target_layer": TARGET_LAYER,
        "next_rerun_contract": NEXT_RERUN_CONTRACT,
        "renderer_archetype_workflow_gates": gates,
    }


def build_result(
    out_dir: Path,
    copy_memory: dict[str, Any],
    socket_memory: dict[str, Any],
    gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_editorial_shape_text_repair_result.v1",
        "run_id": RUN_ID,
        "status": "run2_51_editorial_shape_text_repair_ready_public_blocked",
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "visual_validation_deferred_to_generated_rerun": True,
        "target_layer": TARGET_LAYER,
        "input_chain": {
            "run2_49_result": rel(
                PACK / "results" / "run2_49_readability_content_density_renderer_repair_result.json"
            ),
            "run2_49_readability_memory": rel(PACK / "run2_49_readability_memory.json"),
            "run2_49_content_evidence_density_memory": rel(
                PACK / "run2_49_content_evidence_density_memory.json"
            ),
            "run2_49_editorial_renderer_workflow_gates": rel(
                PACK / "run2_49_editorial_renderer_workflow_gates.json"
            ),
            "run2_50_result": rel(PACK / "results" / "run2_50_readability_density_renderer_rerun_result.json"),
        },
        "output_chain": {
            "editorial_copy_memory": rel(out_dir / "run2_51_editorial_copy_memory.json"),
            "shape_text_socket_memory": rel(out_dir / "run2_51_shape_text_socket_memory.json"),
            "renderer_archetype_workflow_gates": rel(
                out_dir / "run2_51_renderer_archetype_workflow_gates.json"
            ),
        },
        "artifact_counts": {
            "editorial_copy_records": len(copy_memory["editorial_copy_records"]),
            "shape_text_socket_records": len(socket_memory["shape_text_socket_records"]),
            "renderer_archetype_workflow_gates": len(gates["renderer_archetype_workflow_gates"]),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
        },
        "repair_contract": {
            "editorial copy": "raw evidence becomes short public-facing display copy",
            "shape text sockets": "text is bound to semantic shape sockets before drawing",
            "renderer archetypes": (
                "each slide role has one dominant visual archetype and explicit geometry gates"
            ),
            "data/workflow-only": True,
        },
        "public_release_gate": "blocked",
        "release_boundary": (
            "public_blocked_until_run2_52_consumes_run2_51_artifacts_then_visual_review_render_review_and_human_approval_pass"
        ),
        "next_required_action": NEXT_ACTION,
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Run 2.51 Editorial Copy And Shape Text Socket Repair",
                "",
                "Status: data/workflow-only repair pack, public blocked.",
                "",
                "Run 2.51 creates editorial copy and shape text sockets only; visual validation is deferred.",
                "",
                "This data/workflow-only pack converts internal evidence into editorial copy, shape text sockets, and renderer archetype gates.",
                "",
                "It records deferred visual validation so Run 2.52 can bind public text before drawing and complete the next generated rerun.",
                "",
                "## Outputs",
                "",
                "- `run2_51_editorial_copy_memory.json`: per-role editorial copy bundles with budget checks.",
                "- `run2_51_shape_text_socket_memory.json`: per-role shape text sockets bound to archetypal primitives.",
                "- `run2_51_renderer_archetype_workflow_gates.json`: renderer gates for archetypes, geometry, and socket-bound text.",
                "",
                "## Gate",
                "",
                "Deferred visual validation remains in force until Run 2.52 consumes this pack.",
                "",
                f"Next: `{result['next_required_action']}`.",
                "",
                "Do not advance to Run 3.0.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Run 2.51 editorial-copy/shape-text-socket repair pack."
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run249_result = read_json(PACK / "results" / "run2_49_readability_content_density_renderer_repair_result.json")
    run249_readability = read_json(PACK / "run2_49_readability_memory.json")
    run249_density = read_json(PACK / "run2_49_content_evidence_density_memory.json")
    run249_gates = read_json(PACK / "run2_49_editorial_renderer_workflow_gates.json")
    run250_result = read_json(PACK / "results" / "run2_50_readability_density_renderer_rerun_result.json")
    validate_inputs(run249_result, run249_readability, run249_density, run249_gates, run250_result)
    assert_no_run251_deck_artifacts()

    usecase = selected_usecase()
    if usecase.get("id") != SELECTED_USECASE_ID:
        raise ValueError("Run 2.51 selected usecase mismatch")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    copy_memory = build_editorial_copy_memory(run249_readability, run249_density, run250_result)
    socket_memory = build_shape_text_socket_memory(copy_memory, run249_gates)
    gates = build_renderer_archetype_workflow_gates(copy_memory, socket_memory)

    write_json(args.out_dir / "run2_51_editorial_copy_memory.json", copy_memory)
    write_json(args.out_dir / "run2_51_shape_text_socket_memory.json", socket_memory)
    write_json(args.out_dir / "run2_51_renderer_archetype_workflow_gates.json", gates)

    result = build_result(args.out_dir, copy_memory, socket_memory, gates)
    write_json(args.result_json, result)
    write_markdown(args.result_md, result)
    assert_no_run251_deck_artifacts()
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
