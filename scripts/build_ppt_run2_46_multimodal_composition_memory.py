from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_46_multimodal_composition_memory_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_46_multimodal_composition_memory_result.md"

SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "multimodal_composition_memory_and_visual_object_grammar"
NEXT_ACTION = "consume_run2_46_multimodal_composition_memory_before_run2_47_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_47_four_arm_rerun"
SOURCE_AUDIT_ROOT_CAUSE = "run2_44_dataflow_fixed_but_composition_compiler_still_slot_based"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]

ROLE_COMPOSITION_MOVES: dict[str, dict[str, Any]] = {
    "cover": {
        "composition_move": "poster_scene_depth",
        "object_grammar": [
            "one poster-scale generated deck object owns the first read",
            "memory controls sit as a midground field, not equal feature cards",
            "benchmark cues become abstract atmosphere behind the hero object",
            "headline locks to the object edge and leaves open negative space",
        ],
        "quality_checks": [
            "main object reads before labels at contact-sheet scale",
            "supporting objects are visibly secondary",
            "no three-equal-card layout",
            "buyer decision is visible without trace terminology",
        ],
    },
    "setup": {
        "composition_move": "failure_to_route_storyboard",
        "object_grammar": [
            "collapsed prompt output is small, low-confidence, and visibly unstable",
            "selected route is the stable destination object",
            "risk cue connects failure to route without becoming a process diagram",
            "type contrast separates failure label from selected-route claim",
        ],
        "quality_checks": [
            "failure state and selected route are asymmetrical",
            "route object is larger and calmer than failure object",
            "storyboard path is visible without workflow jargon",
            "spacing keeps the route from reading as another block",
        ],
    },
    "contrast": {
        "composition_move": "asymmetric_before_after_delta",
        "object_grammar": [
            "before object is a small thumbnail with low visual confidence",
            "after object is a large product-state surface with clear business consequence",
            "delta strip attaches to the after object rather than floating as a chart",
            "typography compresses the comparison into one after-state claim",
        ],
        "quality_checks": [
            "after state dominates before state",
            "delta is visible as a business consequence",
            "comparison is not two equal cards",
            "support text does not compete with the after object",
        ],
    },
    "proof": {
        "composition_move": "active_product_surface",
        "object_grammar": [
            "one active decision lane anchors the product surface",
            "deck preview and review state are subordinate proof objects",
            "rows and controls feel like a product workspace, not a table",
            "labels explain state changes rather than list internal systems",
        ],
        "quality_checks": [
            "active lane is visually dominant",
            "product proof objects are inspectable",
            "table-like repetition is suppressed",
            "public surface hides database and gate terminology",
        ],
    },
    "climax": {
        "composition_move": "cinematic_result_object",
        "object_grammar": [
            "single result object carries the slide and uses the largest scale contrast",
            "before, memory, and release states fuse into the object rather than separate cards",
            "proof rail stays behind or below the object",
            "motion implication is scale-and-reveal, not transcript or labels",
        ],
        "quality_checks": [
            "one object owns the climax",
            "supporting proof does not split attention",
            "object feels like a publishable result, not a slot",
            "motion beat can be described without needing copied video frames",
        ],
    },
    "close": {
        "composition_move": "decision_room_handoff",
        "object_grammar": [
            "review decision surface becomes an inspectable handoff object",
            "release readiness wall shows state progression without a checklist grid",
            "next-run action surface is directional and secondary",
            "final typography names the release boundary without becoming a report",
        ],
        "quality_checks": [
            "handoff path is visible as one decision scene",
            "release blocked state is clear but not visually dominant",
            "next action is inspectable",
            "close does not collapse into a table or list",
        ],
    },
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


def selected_usecase() -> dict[str, Any]:
    bank = read_json(PACK / "commercial_usecase_bank.json")
    for usecase in bank["usecases"]:
        if usecase["id"] == SELECTED_USECASE_ID:
            return usecase
    raise ValueError(f"missing selected usecase {SELECTED_USECASE_ID}")


def validate_inputs(
    run245: dict[str, Any],
    source_records: dict[str, Any],
    semantic_memory: dict[str, Any],
    editorial_memory: dict[str, Any],
    workflow_gates: dict[str, Any],
) -> None:
    assessment = run245.get("visual_effectiveness_assessment") or {}
    if run245.get("status") != "run2_45_semantic_geometry_effectiveness_audit_public_blocked":
        raise ValueError("Run 2.46 requires Run 2.45 effectiveness audit")
    if run245.get("source_generated_run") != "2.44" or run245.get("source_workflow_run") != "2.43":
        raise ValueError("Run 2.45 source chain mismatch")
    if run245.get("creates_new_ppt_deck") is not False:
        raise ValueError("Run 2.45 must be audit-only")
    if assessment.get("root_cause_primary") != SOURCE_AUDIT_ROOT_CAUSE:
        raise ValueError("Run 2.46 source audit root cause mismatch")
    if assessment.get("top_next_layer_to_thicken") != TARGET_LAYER:
        raise ValueError("Run 2.45 did not target Run 2.46 composition memory")
    if assessment.get("visual_quality_gate") != "blocked":
        raise ValueError("Run 2.46 should only run while visual quality remains blocked")
    if source_records.get("status") != "run2_7_multimodal_source_records_public_blocked":
        raise ValueError("Run 2.46 requires Run 2.7 multimodal source records")
    if semantic_memory.get("status") != "run2_43_semantic_visual_asset_memory_ready_public_blocked":
        raise ValueError("Run 2.46 requires Run 2.43 semantic visual asset memory")
    if editorial_memory.get("status") != "run2_43_editorial_composition_typography_memory_ready_public_blocked":
        raise ValueError("Run 2.46 requires Run 2.43 editorial typography memory")
    if workflow_gates.get("status") != "run2_43_visual_asset_semantics_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.46 requires Run 2.43 workflow gates")
    if len(source_records.get("records") or []) < 6:
        raise ValueError("Run 2.46 expected at least six multimodal source records")


def source_records_for_role(source_records: dict[str, Any], role: str) -> list[dict[str, Any]]:
    records = [
        record
        for record in source_records["records"]
        if role in (record.get("slide_roles") or [])
        and record.get("allowed_use") == "derived_rules_only"
    ]
    if not records:
        raise ValueError(f"Run 2.46 missing multimodal source records for {role}")
    return records


def semantic_assets_for_role(semantic_memory: dict[str, Any], role: str) -> list[dict[str, Any]]:
    records = [record for record in semantic_memory["semantic_visual_asset_records"] if record["role"] == role]
    if len(records) != 3:
        raise ValueError(f"Run 2.46 expected three semantic assets for {role}")
    return records


def editorial_for_role(editorial_memory: dict[str, Any], role: str) -> dict[str, Any]:
    for record in editorial_memory["editorial_composition_typography_records"]:
        if record["role"] == role:
            return record
    raise ValueError(f"Run 2.46 missing editorial memory for {role}")


def gate_for_role(workflow_gates: dict[str, Any], role: str) -> dict[str, Any]:
    for gate in workflow_gates["visual_asset_semantics_workflow_gates"]:
        if gate["role"] == role:
            return gate
    raise ValueError(f"Run 2.46 missing workflow gate for {role}")


def build_multimodal_composition_decomposition(
    run245: dict[str, Any],
    source_records: dict[str, Any],
    semantic_memory: dict[str, Any],
) -> dict[str, Any]:
    role_records = {
        record["role"]: record
        for record in run245["semantic_geometry_trace_effectiveness"]["full_arm"]["role_records"]
    }
    records: list[dict[str, Any]] = []
    for role in ROLES:
        sources = source_records_for_role(source_records, role)
        source_ids = [record["id"] for record in sources]
        modalities = sorted({modality for record in sources for modality in (record.get("modalities") or [])})
        move = ROLE_COMPOSITION_MOVES[role]
        semantic_assets = semantic_assets_for_role(semantic_memory, role)
        slot_roles = role_records[role].get("geometry_slot_roles") or []
        records.append(
            {
                "decomposition_id": f"composition_decomposition_2_46_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_audit_run": "2.45",
                "source_generated_run": "2.44",
                "source_workflow_run": "2.43",
                "source_audit_root_cause": SOURCE_AUDIT_ROOT_CAUSE,
                "multimodal_source_record_ids": source_ids,
                "modalities": modalities,
                "source_observations": [record["visual_observation"] for record in sources],
                "source_teaching_rules": [record["extracted_design_rule"] for record in sources],
                "run2_43_semantic_visual_asset_ids": [asset["semantic_asset_id"] for asset in semantic_assets],
                "run2_44_slot_roles_to_replace": slot_roles,
                "slot_based_failure_mode": "semantic_objects_bound_to_geometry_slots",
                "composition_move": move["composition_move"],
                "native_ppt_composition_implications": [
                    move["object_grammar"][0],
                    move["object_grammar"][1],
                    "use native editable shapes, masks, type, connectors, and generated vector-like illustration only",
                    "make object relationships visible through scale, depth, overlap, cropping, and reveal order",
                ],
                "source_boundary_rules": [
                    "do not copy screenshots, source layouts, video frames, audio, transcript text, brand marks, icons, or tutorial examples",
                    "store derived composition instructions only",
                    "use source records as teaching constraints, not as visual templates",
                ],
                "qa_probe": (
                    "At contact-sheet scale, the slide should read as a composed object scene, "
                    "not as three labeled geometry slots."
                ),
            }
        )

    return {
        "schema_version": "ppt_run2_multimodal_composition_decomposition.v1",
        "status": "run2_46_multimodal_composition_decomposition_ready_public_blocked",
        "run_id": "2.46",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.45",
        "source_multimodal_source_records": "run2_7_multimodal_source_records.json",
        "target_layer": TARGET_LAYER,
        "source_boundary": {
            "allowed_storage": "derived_composition_instructions_only",
            "copied_screenshots": "forbidden",
            "source_layouts": "forbidden",
            "raw_tutorial_or_video_media": "forbidden",
            "audio_or_transcript_text": "forbidden",
            "brand_marks": "forbidden",
        },
        "multimodal_composition_decomposition_records": records,
    }


def build_visual_object_grammar_memory(
    decomposition: dict[str, Any],
    semantic_memory: dict[str, Any],
    editorial_memory: dict[str, Any],
    workflow_gates: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    decompositions = {
        record["role"]: record
        for record in decomposition["multimodal_composition_decomposition_records"]
    }
    for role in ROLES:
        move = ROLE_COMPOSITION_MOVES[role]
        semantic_assets = semantic_assets_for_role(semantic_memory, role)
        editorial = editorial_for_role(editorial_memory, role)
        prior_gate = gate_for_role(workflow_gates, role)
        records.append(
            {
                "visual_object_grammar_id": f"visual_object_grammar_2_46_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_decomposition_id": decompositions[role]["decomposition_id"],
                "required_run2_43_semantic_visual_asset_ids": [asset["semantic_asset_id"] for asset in semantic_assets],
                "required_run2_43_editorial_typography_memory_id": editorial["editorial_typography_memory_id"],
                "required_run2_43_visual_asset_semantics_gate_id": prior_gate["gate_id"],
                "replaces_run2_44_slot_based_geometry": True,
                "visual_object_grammar": move["object_grammar"],
                "composition_quality_checks": move["quality_checks"],
                "native_ppt_generation_contract": [
                    "draw one primary composed object scene before support objects",
                    "use scale, crop, overlap, depth, and connective state rather than equal slots",
                    "derive all shapes and text from source-safe instructions",
                    "hide run ids, memory ids, gate ids, and database terms from the public surface",
                ],
                "motion_or_sequence_implication": (
                    "Preserve a reveal order: primary object first, support evidence second, release/state cue third."
                ),
                "forbidden_patterns": [
                    "slot_based_semantic_geometry_as_primary_surface",
                    "three_equal_feature_cards",
                    "generic dashboard grid",
                    "visible workflow report panel",
                    "copied source media or source layout",
                ],
                "required_trace_fields": [
                    "run2_46_visual_object_grammar_id",
                    "run2_46_multimodal_composition_decomposition_id",
                    "run2_46_composition_gate_id",
                    "run2_46_slot_based_geometry_replaced",
                    "run2_46_source_boundary_status",
                ],
                "qa_probe": (
                    "A reviewer should be able to describe the composed visual object without reading slot labels."
                ),
            }
        )

    return {
        "schema_version": "ppt_run2_visual_object_grammar_memory.v1",
        "status": "run2_46_visual_object_grammar_memory_ready_public_blocked",
        "run_id": "2.46",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_multimodal_composition_decomposition": "run2_46_multimodal_composition_decomposition.json",
        "target_layer": TARGET_LAYER,
        "visual_object_grammar_records": records,
    }


def build_composition_workflow_gates(grammar_memory: dict[str, Any], decomposition: dict[str, Any]) -> dict[str, Any]:
    decomposition_by_role = {
        record["role"]: record
        for record in decomposition["multimodal_composition_decomposition_records"]
    }
    grammar_by_role = {
        record["role"]: record
        for record in grammar_memory["visual_object_grammar_records"]
    }
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        grammar = grammar_by_role[role]
        decomp = decomposition_by_role[role]
        gates.append(
            {
                "gate_id": f"gate_2_46_{role}_composition_quality",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_visual_object_grammar_id": grammar["visual_object_grammar_id"],
                "required_multimodal_composition_decomposition_id": decomp["decomposition_id"],
                "min_composition_quality_checks": 4,
                "forbid_slot_based_geometry_as_primary_surface": True,
                "forbid_equal_card_distribution": True,
                "forbid_copied_source_media": True,
                "require_multimodal_composition_decomposition": True,
                "next_rerun_contract": NEXT_RERUN_CONTRACT,
                "required_trace_fields": [
                    "run2_46_visual_object_grammar_id",
                    "run2_46_multimodal_composition_decomposition_id",
                    "run2_46_composition_gate_id",
                    "run2_46_slot_based_geometry_replaced",
                    "run2_46_source_boundary_status",
                ],
                "pass_fail_checks": [
                    "The generated slide binds one Run 2.46 visual object grammar id before native PPT drawing.",
                    "The generated slide binds one Run 2.46 multimodal composition decomposition id before native PPT drawing.",
                    "The primary composition is not three explicit semantic geometry slots.",
                    "The public surface makes the primary object scene visible before labels are read.",
                    "No copied screenshots, raw tutorial frames, source layouts, brand marks, audio, or transcript text are used.",
                ],
                "bad_control_probe": (
                    "A negative control may receive Run 2.43 ids and Run 2.44 geometry slots, "
                    "but fails if it lacks Run 2.46 visual object grammar and composition gate ids."
                ),
                "public_release_gate": "blocked",
            }
        )

    return {
        "schema_version": "ppt_run2_composition_workflow_gates.v1",
        "status": "run2_46_composition_workflow_gates_ready_public_blocked",
        "run_id": "2.46",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "next_rerun_contract": NEXT_RERUN_CONTRACT,
        "composition_workflow_gates": gates,
    }


def build_result(
    out_dir: Path,
    decomposition: dict[str, Any],
    grammar_memory: dict[str, Any],
    workflow_gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_multimodal_composition_memory_result.v1",
        "run_id": "2.46",
        "status": "run2_46_multimodal_composition_memory_ready_public_blocked",
        "source_audit_run": "2.45",
        "source_generated_run": "2.44",
        "source_workflow_run": "2.43",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "target_layer": TARGET_LAYER,
        "input_chain": {
            "semantic_geometry_effectiveness_audit": rel(PACK / "results" / "run2_45_semantic_geometry_effectiveness_audit.json"),
            "multimodal_source_records": rel(PACK / "run2_7_multimodal_source_records.json"),
            "semantic_visual_asset_memory": rel(PACK / "run2_43_semantic_visual_asset_memory.json"),
            "editorial_composition_typography_memory": rel(PACK / "run2_43_editorial_composition_typography_memory.json"),
            "visual_asset_semantics_workflow_gates": rel(PACK / "run2_43_visual_asset_semantics_workflow_gates.json"),
        },
        "output_chain": {
            "multimodal_composition_decomposition": rel(out_dir / "run2_46_multimodal_composition_decomposition.json"),
            "visual_object_grammar_memory": rel(out_dir / "run2_46_visual_object_grammar_memory.json"),
            "composition_workflow_gates": rel(out_dir / "run2_46_composition_workflow_gates.json"),
        },
        "artifact_counts": {
            "multimodal_composition_decomposition_records": len(
                decomposition["multimodal_composition_decomposition_records"]
            ),
            "visual_object_grammar_records": len(grammar_memory["visual_object_grammar_records"]),
            "composition_workflow_gates": len(workflow_gates["composition_workflow_gates"]),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
        },
        "public_release_gate": "blocked",
        "release_boundary": "public_blocked_until_run2_47_consumes_run2_46_memory_native_render_review_and_human_approval",
        "next_required_action": NEXT_ACTION,
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Run 2.46 Multimodal Composition Memory",
                "",
                "Status: audit-only data/workflow thickening, public blocked.",
                "",
                "Run 2.46 creates no PPT deck and does not advance to Run 3.0.",
                "",
                "It responds to Run 2.45 by turning the slot-based failure into a source-safe multimodal composition decomposition, visual object grammar, and composition workflow gates.",
                "",
                "## Outputs",
                "",
                "- `run2_46_multimodal_composition_decomposition.json`: derived multimodal composition decomposition records.",
                "- `run2_46_visual_object_grammar_memory.json`: per-role visual object grammar that replaces slot-based geometry.",
                "- `run2_46_composition_workflow_gates.json`: gates that must be consumed before Run 2.47.",
                "",
                "## Gate",
                "",
                "Run 2.47 must consume this pack before any generated slide claims improved visual quality.",
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
    parser = argparse.ArgumentParser(description="Build Run 2.46 multimodal composition memory pack.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run245 = read_json(PACK / "results" / "run2_45_semantic_geometry_effectiveness_audit.json")
    source_records = read_json(PACK / "run2_7_multimodal_source_records.json")
    semantic_memory = read_json(PACK / "run2_43_semantic_visual_asset_memory.json")
    editorial_memory = read_json(PACK / "run2_43_editorial_composition_typography_memory.json")
    workflow_gates = read_json(PACK / "run2_43_visual_asset_semantics_workflow_gates.json")
    validate_inputs(run245, source_records, semantic_memory, editorial_memory, workflow_gates)

    usecase = selected_usecase()
    if usecase.get("id") != SELECTED_USECASE_ID:
        raise ValueError("Run 2.46 selected usecase mismatch")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    decomposition = build_multimodal_composition_decomposition(run245, source_records, semantic_memory)
    grammar_memory = build_visual_object_grammar_memory(decomposition, semantic_memory, editorial_memory, workflow_gates)
    composition_gates = build_composition_workflow_gates(grammar_memory, decomposition)

    write_json(args.out_dir / "run2_46_multimodal_composition_decomposition.json", decomposition)
    write_json(args.out_dir / "run2_46_visual_object_grammar_memory.json", grammar_memory)
    write_json(args.out_dir / "run2_46_composition_workflow_gates.json", composition_gates)

    result = build_result(args.out_dir, decomposition, grammar_memory, composition_gates)
    write_json(args.result_json, result)
    write_markdown(args.result_md, result)
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
