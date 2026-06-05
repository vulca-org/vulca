from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_43_visual_asset_semantics_workflow_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_43_visual_asset_semantics_workflow_result.md"

SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "usecase_specific_visual_asset_semantics_editorial_composition_and_typography_hierarchy"
NEXT_ACTION = "consume_run2_43_visual_asset_semantics_workflow_before_run2_44_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_44_four_arm_rerun"
SOURCE_AUDIT_ROOT_CAUSE = "visual_asset_surfaces_are_still_schematic_native_shapes_not_true_product_or_scene_assets"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]


ROLE_SEMANTIC_OBJECTS: dict[str, list[str]] = {
    "cover": [
        "market-facing launch poster scene with the buyer decision visible before any workflow detail",
        "generated launch deck hero object with attached design-memory controls and review state",
        "source-safe benchmark cue rendered as an abstract design-quality signal, not a copied source asset",
    ],
    "setup": [
        "prompt-only failure storyboard showing loss of context, source boundary, and reviewability",
        "collapsed prompt output surface that looks thin and commercially risky at thumbnail scale",
        "selected route scene where usecase, memory, and QA gate converge before generation",
    ],
    "contrast": [
        "small before thumbnail that intentionally reads generic and underpowered",
        "dominant after launch surface carrying selected usecase, visual memory, and output state",
        "business delta strip that explains the commercial improvement without trace jargon",
    ],
    "proof": [
        "product UI evidence surface showing role-to-visual-decision mapping as an app state",
        "editable deck preview object with selected memory and slide-code status visible",
        "review status badge that is quiet and source-boundary safe, not a public ribbon composition",
    ],
    "climax": [
        "cinematic output stage where the generated deck object owns most of the frame",
        "launch asset surface fusing before, memory, and release state into one result object",
        "audience proof rail that supports the hero result without becoming the main composition",
    ],
    "close": [
        "review decision table rendered as a decision-room surface, not a spreadsheet block",
        "release readiness wall with internal demo, native review, and public block states",
        "next-run action surface that makes the Run 2.44 consumption contract inspectable",
    ],
}


ROLE_COMPOSITION_RULES: dict[str, dict[str, Any]] = {
    "cover": {
        "layout_signature": "poster_scene_with_one_generated_deck_hero",
        "climax_or_scene_depth_rule": "Use foreground deck hero, midground memory controls, and background market cue so the cover reads as a launch scene.",
        "primary_weight": 0.66,
    },
    "setup": {
        "layout_signature": "failure_storyboard_to_selected_route",
        "climax_or_scene_depth_rule": "Make the failure path visibly collapse before the selected route appears as the stable object.",
        "primary_weight": 0.58,
    },
    "contrast": {
        "layout_signature": "small_before_large_after_semantic_product_state",
        "climax_or_scene_depth_rule": "The after-state object must dwarf the before-state object and carry the clearest business delta.",
        "primary_weight": 0.64,
    },
    "proof": {
        "layout_signature": "working_product_surface_with_active_decision_lane",
        "climax_or_scene_depth_rule": "One active decision lane must sit above quieter rows so the proof feels like product evidence, not a table.",
        "primary_weight": 0.60,
    },
    "climax": {
        "layout_signature": "single_cinematic_result_object_with_supporting_proof_rail",
        "climax_or_scene_depth_rule": "The result object must carry the slide; supporting proof stays below or behind it.",
        "primary_weight": 0.78,
    },
    "close": {
        "layout_signature": "decision_room_handoff_with_one_release_boundary",
        "climax_or_scene_depth_rule": "The decision handoff owns the first read, with release states as supporting proof rather than a checklist.",
        "primary_weight": 0.56,
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def selected_usecase() -> dict[str, Any]:
    bank = read_json(PACK / "commercial_usecase_bank.json")
    for usecase in bank["usecases"]:
        if usecase["id"] == SELECTED_USECASE_ID:
            return usecase
    raise ValueError(f"missing selected usecase {SELECTED_USECASE_ID}")


def validate_inputs(audit: dict[str, Any], run241: dict[str, Any], run240: dict[str, Any], full_trace: dict[str, Any]) -> None:
    assessment = audit.get("visual_quality_assessment") or {}
    if audit.get("status") != "run2_42_content_visual_asset_quality_audit_public_blocked":
        raise ValueError("Run 2.43 requires the Run 2.42 content visual asset quality audit")
    if audit.get("source_generated_run") != "2.41" or audit.get("source_prior_generated_run") != "2.40":
        raise ValueError("Run 2.42 source chain mismatch")
    if assessment.get("design_quality_gate") != "blocked":
        raise ValueError("Run 2.43 should only run while design quality remains blocked")
    if assessment.get("root_cause_primary") != SOURCE_AUDIT_ROOT_CAUSE:
        raise ValueError("Run 2.43 source audit root cause mismatch")
    if assessment.get("top_next_layer_to_thicken") != TARGET_LAYER:
        raise ValueError("Run 2.42 did not target the Run 2.43 semantic visual asset layer")
    if run241.get("status") != "run2_41_content_visual_asset_compiler_rerun_public_blocked":
        raise ValueError("Run 2.41 rerun result mismatch")
    if run240.get("status") != "run2_40_visual_compiler_rerun_public_blocked":
        raise ValueError("Run 2.40 rerun result mismatch")
    if full_trace.get("arm_id") != "run2_41_full_content_visual_asset_compiler":
        raise ValueError("Run 2.43 must consume the Run 2.41 full-arm trace")
    slides = full_trace.get("slides") or []
    if len(slides) != 6:
        raise ValueError("Run 2.41 full arm must have six slides")
    for slide in slides:
        surfaces = slide.get("run2_41_visual_asset_surface_types") or []
        if len(surfaces) != 3:
            raise ValueError(f"Run 2.43 expected three visual asset surfaces for {slide.get('role')}")


def build_semantic_visual_asset_memory(usecase: dict[str, Any], audit: dict[str, Any], full_trace: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    source_ids = list(usecase.get("source_ids") or [])
    for slide_index, slide in enumerate(full_trace["slides"], start=1):
        role = slide["role"]
        payload = slide.get("run2_41_content_scene_payload") or {}
        semantic_objects = ROLE_SEMANTIC_OBJECTS[role]
        for surface_index, surface_type in enumerate(slide["run2_41_visual_asset_surface_types"], start=1):
            semantic_object = semantic_objects[surface_index - 1]
            records.append(
                {
                    "semantic_asset_id": f"semantic_asset_2_43_{role}_{surface_index}",
                    "role": role,
                    "slide_index": slide_index,
                    "selected_usecase_id": SELECTED_USECASE_ID,
                    "source_audit_run": "2.42",
                    "source_generated_run": "2.41",
                    "source_prior_generated_run": "2.40",
                    "source_audit_root_cause": audit["visual_quality_assessment"]["root_cause_primary"],
                    "source_ids": source_ids,
                    "source_run2_41_surface_type": surface_type,
                    "source_run2_41_code_module_ids": slide.get("run2_41_code_module_ids") or [],
                    "source_scene_payload": payload,
                    "usecase_specific_semantic_object": semantic_object,
                    "observable_scene_evidence": [
                        f"first read object: {payload.get('first_read_object')}",
                        f"visual rhythm: {payload.get('visual_rhythm_id')}",
                        f"surface role: {surface_type}",
                        f"business decision: {payload.get('business_decision')}",
                    ],
                    "allowed_native_ppt_representation": (
                        "editable native PPT vectors, type, gradients, masks, depth layers, state labels, "
                        "and original SVG-like illustration generated from derived instructions only"
                    ),
                    "forbidden_schematic_substitutes": [
                        "generic placeholder",
                        "equal-weight rectangles",
                        "named-but-empty visual surface",
                        "schematic native shape-only surface",
                        "copied screenshots/source media",
                        "source brand imitation",
                    ],
                    "source_boundary_note": (
                        "Derived semantic visual asset only; no copied screenshots/source media, "
                        "raw video frames, source layouts, brand marks, audio, or transcript text."
                    ),
                    "required_trace_fields": [
                        "run2_43_semantic_visual_asset_ids",
                        "run2_43_semantic_visual_asset_surface_types",
                        "run2_43_source_boundary_status",
                        "run2_43_visual_asset_semantics_execution_status",
                    ],
                    "qa_probe": (
                        "At contact-sheet scale, this surface must read as a product or business object "
                        "specific to the selected usecase, not as a labeled abstract block."
                    ),
                }
            )

    return {
        "schema_version": "ppt_run2_semantic_visual_asset_memory.v1",
        "status": "run2_43_semantic_visual_asset_memory_ready_public_blocked",
        "run_id": "2.43",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.42",
        "source_generated_run": "2.41",
        "source_prior_generated_run": "2.40",
        "target_layer": TARGET_LAYER,
        "source_boundary": {
            "allowed_storage": "derived_semantic_visual_asset_instructions_only",
            "copied_screenshots": "forbidden",
            "raw_tutorial_or_video_media": "forbidden",
            "video_frames": "forbidden",
            "source_layouts": "forbidden",
            "brand_marks": "forbidden",
            "audio_or_transcript_text": "forbidden",
        },
        "semantic_visual_asset_records": records,
    }


def build_editorial_composition_typography_memory(semantic_memory: dict[str, Any], full_trace: dict[str, Any]) -> dict[str, Any]:
    assets_by_role: dict[str, list[str]] = {role: [] for role in ROLES}
    for record in semantic_memory["semantic_visual_asset_records"]:
        assets_by_role[record["role"]].append(record["semantic_asset_id"])

    slides_by_role = {slide["role"]: slide for slide in full_trace["slides"]}
    records: list[dict[str, Any]] = []
    for role in ROLES:
        spec = ROLE_COMPOSITION_RULES[role]
        payload = slides_by_role[role].get("run2_41_content_scene_payload") or {}
        records.append(
            {
                "editorial_typography_memory_id": f"editorial_typography_2_43_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_semantic_asset_ids": assets_by_role[role],
                "first_read_scene_object": payload.get("first_read_object"),
                "visual_rhythm_id": payload.get("visual_rhythm_id"),
                "layout_signature_target": spec["layout_signature"],
                "primary_visual_weight_target": spec["primary_weight"],
                "typography_hierarchy_rules": [
                    "Use one dominant claim that explains the commercial scene, not a workflow label.",
                    "Use one concrete scene or object label tied to the selected usecase.",
                    "Keep proof captions short and subordinate to the main visual object.",
                    "Keep run ids, trace ids, gate names, and database terms out of the public first-read surface.",
                ],
                "editorial_composition_rules": [
                    "One semantic asset must own the first read before supporting assets appear.",
                    "Layer foreground, midground, and background so the slide reads as a scene, not a grid.",
                    "Use supporting rails only when they explain the hero object.",
                    "Make the semantic assets visibly different in shape, scale, and purpose.",
                ],
                "spacing_depth_rules": [
                    "Protect the hero object with whitespace on at least two sides.",
                    "Avoid distributing the three semantic assets as equal cards.",
                    "Use overlap, crop, or scale contrast to create depth while keeping text legible.",
                ],
                "climax_or_scene_depth_rule": spec["climax_or_scene_depth_rule"],
                "public_surface_forbidden_patterns": [
                    "schematic native shape-only surface",
                    "generic placeholder blocks",
                    "equal feature-card grid",
                    "workflow report panel",
                    "copied screenshots/source media",
                ],
                "required_trace_fields": [
                    "run2_43_editorial_typography_memory_id",
                    "run2_43_layout_signature_target",
                    "run2_43_primary_visual_weight_target",
                    "run2_43_visual_asset_semantics_execution_status",
                ],
                "qa_probe": (
                    "A reviewer should be able to name the slide's main semantic object and typography hierarchy "
                    "without reading the trace manifest."
                ),
            }
        )

    return {
        "schema_version": "ppt_run2_editorial_composition_typography_memory.v1",
        "status": "run2_43_editorial_composition_typography_memory_ready_public_blocked",
        "run_id": "2.43",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_semantic_visual_asset_memory": "run2_43_semantic_visual_asset_memory.json",
        "target_layer": TARGET_LAYER,
        "editorial_composition_typography_records": records,
    }


def build_workflow_gates(semantic_memory: dict[str, Any], editorial_memory: dict[str, Any]) -> dict[str, Any]:
    assets_by_role: dict[str, list[str]] = {role: [] for role in ROLES}
    for record in semantic_memory["semantic_visual_asset_records"]:
        assets_by_role[record["role"]].append(record["semantic_asset_id"])
    editorial_by_role = {
        record["role"]: record["editorial_typography_memory_id"]
        for record in editorial_memory["editorial_composition_typography_records"]
    }

    gates: list[dict[str, Any]] = []
    for role in ROLES:
        gates.append(
            {
                "gate_id": f"gate_2_43_{role}_visual_asset_semantics",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_semantic_asset_ids": assets_by_role[role],
                "required_editorial_typography_memory_id": editorial_by_role[role],
                "min_semantic_visual_assets": 3,
                "forbid_generic_placeholder_assets": True,
                "forbid_schematic_native_shape_only_surface": True,
                "forbid_equal_card_distribution": True,
                "forbid_copied_source_media": True,
                "next_rerun_contract": NEXT_RERUN_CONTRACT,
                "required_trace_fields": [
                    "run2_43_semantic_visual_asset_ids",
                    "run2_43_editorial_typography_memory_id",
                    "run2_43_visual_asset_semantics_gate_id",
                    "run2_43_visual_asset_semantics_execution_status",
                    "run2_43_source_boundary_status",
                ],
                "pass_fail_checks": [
                    "The generated slide binds three Run 2.43 semantic visual asset ids before native PPT drawing.",
                    "The generated slide binds one Run 2.43 editorial typography memory id before native PPT drawing.",
                    "The public surface must not use generic placeholders or equal schematic cards as the main visual.",
                    "The public surface must make at least one semantic asset the first-read object.",
                    "No copied screenshots, raw tutorial frames, source layouts, brand marks, audio, or transcript text are used.",
                ],
                "bad_control_probe": (
                    "A negative control may receive the same usecase and Run 2.41 surface names, but fails if it lacks "
                    "Run 2.43 semantic asset ids, editorial typography memory, or gate id."
                ),
                "public_release_gate": "blocked",
            }
        )

    return {
        "schema_version": "ppt_run2_visual_asset_semantics_workflow_gates.v1",
        "status": "run2_43_visual_asset_semantics_workflow_gates_ready_public_blocked",
        "run_id": "2.43",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "next_rerun_contract": NEXT_RERUN_CONTRACT,
        "visual_asset_semantics_workflow_gates": gates,
    }


def build_result(semantic_memory: dict[str, Any], editorial_memory: dict[str, Any], gates: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_visual_asset_semantics_workflow_result.v1",
        "run_id": "2.43",
        "status": "run2_43_visual_asset_semantics_workflow_ready_public_blocked",
        "source_audit_run": "2.42",
        "source_generated_run": "2.41",
        "source_prior_generated_run": "2.40",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "input_chain": {
            "content_visual_asset_quality_audit": rel(PACK / "results" / "run2_42_content_visual_asset_quality_audit.json"),
            "run2_41_full_trace_manifest": rel(
                ROOT
                / "outputs"
                / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
                / "presentations"
                / "ppt-run2-41-full-vulca"
                / "trace_manifest.json"
            ),
            "run2_41_rerun_result": rel(PACK / "results" / "run2_41_content_visual_asset_compiler_rerun_result.json"),
            "run2_40_rerun_result": rel(PACK / "results" / "run2_40_visual_compiler_rerun_result.json"),
            "commercial_usecase_bank": rel(PACK / "commercial_usecase_bank.json"),
        },
        "output_chain": {
            "semantic_visual_asset_memory": rel(PACK / "run2_43_semantic_visual_asset_memory.json"),
            "editorial_composition_typography_memory": rel(
                PACK / "run2_43_editorial_composition_typography_memory.json"
            ),
            "visual_asset_semantics_workflow_gates": rel(
                PACK / "run2_43_visual_asset_semantics_workflow_gates.json"
            ),
        },
        "target_layer": TARGET_LAYER,
        "artifact_counts": {
            "semantic_visual_asset_records": len(semantic_memory["semantic_visual_asset_records"]),
            "editorial_composition_typography_records": len(
                editorial_memory["editorial_composition_typography_records"]
            ),
            "workflow_gates": len(gates["visual_asset_semantics_workflow_gates"]),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
            "html_motion_renderer_paths": [],
        },
        "public_release_gate": "blocked",
        "release_boundary": "public_blocked_until_run2_44_consumes_run2_43_workflow_native_render_review_and_human_approval",
        "next_required_action": NEXT_ACTION,
    }


def update_skill_workflow() -> None:
    path = PACK / "skill_workflow.json"
    workflow = read_json(path)
    workflow["status"] = "run2_43_visual_asset_semantics_workflow_directed_public_blocked"
    existing = {stage["id"]: stage for stage in workflow["stages"]}
    new_stages = [
        {
            "id": "compile_run2_43_semantic_visual_asset_memory",
            "order": 41,
            "layer": "semantic_visual_asset_memory",
            "inputs": [
                "results/run2_42_content_visual_asset_quality_audit.json",
                "results/run2_41_content_visual_asset_compiler_rerun_result.json",
                "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-41-full-vulca/trace_manifest.json",
                "commercial_usecase_bank.json",
            ],
            "outputs": ["run2_43_semantic_visual_asset_memory.json"],
            "gates": [
                "each Run 2.41 named visual asset surface becomes a usecase-specific semantic visual asset",
                "generic placeholders, equal rectangles, and schematic native shape-only surfaces are forbidden",
                "raw tutorial media, copied screenshots, source layouts, brand marks, audio, and transcript text remain forbidden",
            ],
        },
        {
            "id": "compile_run2_43_editorial_composition_typography_memory",
            "order": 42,
            "layer": "editorial_composition_typography_memory",
            "inputs": ["run2_43_semantic_visual_asset_memory.json"],
            "outputs": ["run2_43_editorial_composition_typography_memory.json"],
            "gates": [
                "each role defines a first-read semantic object, typography hierarchy, layout signature, and depth rule",
                "three semantic assets must not become equal cards",
                "public first read excludes trace ids, run ids, gate names, and database terms",
            ],
        },
        {
            "id": "apply_run2_43_visual_asset_semantics_workflow_gates",
            "order": 43,
            "layer": "skill_workflow",
            "inputs": [
                "run2_43_semantic_visual_asset_memory.json",
                "run2_43_editorial_composition_typography_memory.json",
            ],
            "outputs": [
                "run2_43_visual_asset_semantics_workflow_gates.json",
                "results/run2_43_visual_asset_semantics_workflow_result.json",
            ],
            "gates": [
                "Run 2.44 must consume Run 2.43 semantic visual assets, editorial typography memory, and gates before native PPT generation",
                "negative control may receive Run 2.41 surface names but not Run 2.43 semantic asset ids or gate ids",
                "Run 2.43 is not a new PPT output and does not advance to Run 3.0",
            ],
        },
    ]
    for stage in new_stages:
        existing[stage["id"]] = stage
    workflow["stages"] = sorted(existing.values(), key=lambda item: item["order"])
    triggers = {trigger["id"]: trigger for trigger in workflow.get("repair_triggers", [])}
    triggers["run2_43_visual_asset_semantics_required_before_run2_44_rerun"] = {
        "id": "run2_43_visual_asset_semantics_required_before_run2_44_rerun",
        "trigger": (
            "Run 2.42 found that Run 2.41 proves content and visual asset thickness but still feels simple "
            "because the named surfaces are schematic native shapes rather than semantic product or scene assets"
        ),
        "recommendation": (
            "require run2_43_semantic_visual_asset_memory.json, "
            "run2_43_editorial_composition_typography_memory.json, and "
            "run2_43_visual_asset_semantics_workflow_gates.json before Run 2.44 four-arm rerun"
        ),
        "human_gate": "required before Run 2.44 generated rerun",
    }
    workflow["repair_triggers"] = list(triggers.values())
    write_json(path, workflow)


def write_report(result: dict[str, Any], result_md: Path) -> None:
    lines = [
        "# Run 2.43 Visual Asset Semantics Workflow",
        "",
        "Status: Run 2.43 data/workflow pack completed, public blocked.",
        "",
        "Run 2.43 is data/workflow-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It converts the Run 2.42 finding into stricter semantic visual assets, editorial composition, and typography hierarchy obligations.",
        "",
        f"Target layer: `{result['target_layer']}`.",
        "",
        "## What Changed",
        "",
        "- `run2_43_semantic_visual_asset_memory.json` turns each Run 2.41 named surface into a concrete usecase-specific semantic visual asset.",
        "- `run2_43_editorial_composition_typography_memory.json` defines per-slide first-read objects, layout signatures, editorial composition, spacing, and typography hierarchy rules.",
        "- `run2_43_visual_asset_semantics_workflow_gates.json` requires the next generated rerun to bind semantic assets and editorial typography memory before native PPT drawing.",
        "",
        "## Gate",
        "",
        "- Creates new PPT deck: false.",
        "- Public ready: false.",
        "- Public release gate: blocked.",
        "- Raw tutorial media, copied screenshots, source layouts, brand marks, audio, and transcript text remain forbidden in the database.",
        "- Run 2.44 four-arm rerun must consume this workflow before any generated slide claims better design quality.",
        "",
        "Next: consume the Run 2.43 visual asset semantics workflow before Run 2.44 four-arm rerun. Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Run 2.43 visual asset semantics data/workflow pack.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    usecase = selected_usecase()
    audit = read_json(PACK / "results" / "run2_42_content_visual_asset_quality_audit.json")
    run241 = read_json(PACK / "results" / "run2_41_content_visual_asset_compiler_rerun_result.json")
    run240 = read_json(PACK / "results" / "run2_40_visual_compiler_rerun_result.json")
    full_trace = read_json(
        ROOT
        / "outputs"
        / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
        / "presentations"
        / "ppt-run2-41-full-vulca"
        / "trace_manifest.json"
    )
    validate_inputs(audit, run241, run240, full_trace)

    semantic_memory = build_semantic_visual_asset_memory(usecase, audit, full_trace)
    editorial_memory = build_editorial_composition_typography_memory(semantic_memory, full_trace)
    workflow_gates = build_workflow_gates(semantic_memory, editorial_memory)
    result = build_result(semantic_memory, editorial_memory, workflow_gates)

    out_dir = args.out_dir
    write_json(out_dir / "run2_43_semantic_visual_asset_memory.json", semantic_memory)
    write_json(out_dir / "run2_43_editorial_composition_typography_memory.json", editorial_memory)
    write_json(out_dir / "run2_43_visual_asset_semantics_workflow_gates.json", workflow_gates)
    write_json(args.result_json, result)
    write_report(result, args.result_md)
    if out_dir.resolve() == DEFAULT_OUT_DIR.resolve():
        update_skill_workflow()
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
