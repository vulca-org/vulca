from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS_DIR = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_53_product_surface_scene_repair_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_53_product_surface_scene_repair_result.md"

RUN_ID = "2.53"
SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "product_surface_scene_and_business_visual_evidence_repair"
NEXT_ACTION = "consume_run2_53_before_run2_54_four_arm_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_54_four_arm_rerun"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
TRACE_FIELDS = [
    "run2_53_product_surface_scene_id",
    "run2_53_business_visual_evidence_id",
    "run2_53_scene_renderer_gate_id",
    "run2_53_primary_product_or_business_object",
    "run2_53_visual_specificity_status",
    "run2_53_forbidden_generic_geometry_count",
]
FORBIDDEN_PATTERNS = [
    "generic geometric diagram",
    "evidence card only",
    "floating annotation card",
    "square block grid",
    "decorative abstract shapes without product surface",
]

ROLE_SCENE_SPECS: dict[str, dict[str, Any]] = {
    "cover": {
        "scene_object_kind": "launch_deck_product_surface",
        "primary_product_or_business_object": "editable launch deck preview on a presentation workbench",
        "observable_scene_summary": "A real deck surface is the hero object, with small proof badges attached to the canvas.",
        "surface_slots": [
            "editable deck preview frame",
            "selected usecase badge attached to frame",
            "evidence-to-code route marker",
            "public-demo release boundary tag",
        ],
        "reader_question_answered": "What product is being launched, and why should a buyer believe it is more than prompt-only slides?",
    },
    "setup": {
        "scene_object_kind": "workflow_route_product_surface",
        "primary_product_or_business_object": "prompt-to-production route board with broken prompt-only path",
        "observable_scene_summary": "The slide shows a collapsed generic prompt path beside the selected product workflow route.",
        "surface_slots": [
            "failed prompt-only path object",
            "selected workflow route board",
            "data memory gate checkpoint",
            "rerun decision marker",
        ],
        "reader_question_answered": "Where does the old path fail, and what concrete route replaces it?",
    },
    "contrast": {
        "scene_object_kind": "before_after_deck_surface",
        "primary_product_or_business_object": "before and after deck previews with a visible business delta",
        "observable_scene_summary": "Two unequal deck previews show the before/after difference as an inspectable product result.",
        "surface_slots": [
            "before deck preview",
            "after deck preview",
            "delta lens over changed region",
            "business outcome annotation socket",
        ],
        "reader_question_answered": "What changed on the actual presentation surface, and what business consequence does it create?",
    },
    "proof": {
        "scene_object_kind": "inspection_workspace_surface",
        "primary_product_or_business_object": "editable proof workspace with scene, copy, and renderer lanes",
        "observable_scene_summary": "A workspace surface shows evidence becoming copy, surface slots, and renderer constraints.",
        "surface_slots": [
            "copy lane with selected headline",
            "surface scene lane with product object",
            "renderer gate lane with pass/fail chips",
            "inspectable preview tile",
        ],
        "reader_question_answered": "Can the viewer inspect how evidence becomes an editable presentation object?",
    },
    "climax": {
        "scene_object_kind": "dominant_generated_result_surface",
        "primary_product_or_business_object": "large generated deck result object with attached proof tags",
        "observable_scene_summary": "One generated result dominates the frame, with proof tags anchored to visible regions.",
        "surface_slots": [
            "dominant generated result frame",
            "attached typography proof tag",
            "attached spacing proof tag",
            "attached source-boundary proof tag",
        ],
        "reader_question_answered": "What is the strongest generated result, and which visible evidence makes it credible?",
    },
    "close": {
        "scene_object_kind": "release_decision_business_surface",
        "primary_product_or_business_object": "release gate decision wall with next rerun handoff",
        "observable_scene_summary": "The final surface is a decision room that makes release blocked and next rerun explicit.",
        "surface_slots": [
            "release gate wall",
            "next rerun handoff strip",
            "human review blocker note",
            "source boundary check tile",
        ],
        "reader_question_answered": "What can ship later, what remains blocked, and what must Run 2.54 consume?",
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


def assert_no_run253_deck_artifacts() -> None:
    if not PRESENTATIONS_DIR.exists():
        return
    deck_paths = sorted(
        path
        for pattern in ("*2-53*.ppt", "*2-53*.pptx", "ppt-run2-53-*")
        for path in PRESENTATIONS_DIR.glob(pattern)
    )
    if deck_paths:
        names = ", ".join(path.name for path in deck_paths)
        raise ValueError(f"Run 2.53 is data/workflow-only and must not create PPT artifacts: {names}")


def validate_inputs(
    run252_result: dict[str, Any],
    run252_full_trace: dict[str, Any],
    run251_copy: dict[str, Any],
    run251_socket: dict[str, Any],
    run251_gates: dict[str, Any],
) -> None:
    if run252_result.get("status") != "run2_52_editorial_socket_renderer_rerun_public_blocked":
        raise ValueError("Run 2.53 requires Run 2.52 rerun result")
    if run252_result.get("selected_usecase_id") != SELECTED_USECASE_ID:
        raise ValueError("Run 2.53 selected usecase mismatch in Run 2.52 result")
    quality_delta = run252_result.get("quality_delta") or {}
    if quality_delta.get("source_data_status") != "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing":
        raise ValueError("Run 2.53 source_data_status requires Run 2.52 consuming Run 2.51")
    if quality_delta.get("full_slides_with_run2_51_editorial_copy_memory_id") != 6:
        raise ValueError("Run 2.53 requires six Run 2.52 slides with editorial copy ids")
    if quality_delta.get("full_slides_with_run2_51_shape_text_socket_memory_id") != 6:
        raise ValueError("Run 2.53 requires six Run 2.52 slides with shape text socket ids")
    if quality_delta.get("full_slides_with_run2_51_renderer_archetype_gate_id") != 6:
        raise ValueError("Run 2.53 requires six Run 2.52 slides with renderer archetype gate ids")

    if run252_full_trace.get("arm_id") != "run2_52_full_editorial_socket_renderer":
        raise ValueError("Run 2.53 requires the Run 2.52 full editorial socket renderer trace")
    if run252_full_trace.get("selected_usecase_id") != SELECTED_USECASE_ID:
        raise ValueError("Run 2.53 selected usecase mismatch in Run 2.52 trace")
    if run252_full_trace.get("run2_52_editorial_socket_renderer_status") != (
        "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing"
    ):
        raise ValueError("Run 2.53 requires Run 2.52 trace consumption status")

    slides = run252_full_trace.get("slides") or []
    if len(slides) != 6:
        raise ValueError("Run 2.53 expected six Run 2.52 full-arm slides")
    for role in ROLES:
        slide = role_record(slides, role, "Run 2.52 full trace")
        if not str(slide.get("run2_51_editorial_copy_memory_id", "")).startswith("editorial_copy_2_51_"):
            raise ValueError(f"Run 2.53 role {role} missing Run 2.51 editorial copy trace id")
        if not str(slide.get("run2_51_shape_text_socket_memory_id", "")).startswith("shape_text_socket_2_51_"):
            raise ValueError(f"Run 2.53 role {role} missing Run 2.51 shape socket trace id")
        if not str(slide.get("run2_51_renderer_archetype_gate_id", "")).startswith("gate_2_51_"):
            raise ValueError(f"Run 2.53 role {role} missing Run 2.51 renderer gate trace id")
        if slide.get("run2_52_primary_surface_kind") == "square_block_grid":
            raise ValueError(f"Run 2.53 role {role} cannot start from square_block_grid as full-arm proof")

    if run251_copy.get("status") != "run2_51_editorial_copy_memory_ready_public_blocked":
        raise ValueError("Run 2.53 requires Run 2.51 editorial copy memory")
    if run251_socket.get("status") != "run2_51_shape_text_socket_memory_ready_public_blocked":
        raise ValueError("Run 2.53 requires Run 2.51 shape text socket memory")
    if run251_gates.get("status") != "run2_51_renderer_archetype_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.53 requires Run 2.51 renderer archetype workflow gates")
    if len(run251_copy.get("editorial_copy_records") or []) != 6:
        raise ValueError("Run 2.53 expected six Run 2.51 editorial copy records")
    if len(run251_socket.get("shape_text_socket_records") or []) != 6:
        raise ValueError("Run 2.53 expected six Run 2.51 shape text socket records")
    if len(run251_gates.get("renderer_archetype_workflow_gates") or []) != 6:
        raise ValueError("Run 2.53 expected six Run 2.51 renderer archetype gates")


def build_product_surface_scene_memory(
    run252_full_trace: dict[str, Any],
    run251_socket: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    slides = run252_full_trace["slides"]
    socket_records = run251_socket["shape_text_socket_records"]
    for role in ROLES:
        spec = ROLE_SCENE_SPECS[role]
        slide = role_record(slides, role, "Run 2.52 full trace")
        socket = role_record(socket_records, role, "Run 2.51 socket")
        records.append(
            {
                "id": f"product_surface_scene_2_53_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_run_ids": ["2.51", "2.52"],
                "required_run2_51_shape_text_socket_memory_id": socket["socket_memory_id"],
                "required_run2_52_slide_role": role,
                "required_run2_52_primary_surface_kind": slide["run2_52_primary_surface_kind"],
                "scene_object_kind": spec["scene_object_kind"],
                "primary_product_or_business_object": spec["primary_product_or_business_object"],
                "must_render_product_or_business_object": True,
                "observable_scene_summary": spec["observable_scene_summary"],
                "surface_slots": spec["surface_slots"],
                "minimum_scene_requirements": [
                    "one visible product or business object owns the primary surface",
                    "public copy is attached to the object or its inspection surfaces",
                    "proof markers point to a visible region, lane, or preview",
                    "the slide can be understood without trace terminology",
                ],
                "reader_question_answered": spec["reader_question_answered"],
                "forbidden_patterns": FORBIDDEN_PATTERNS,
                "source_boundary": {
                    "derived_observations_only": True,
                    "raw_media_copied": False,
                    "source_layout_copied": False,
                    "source_brand_identity_copied": False,
                },
                "visual_validation_deferred_to_generated_rerun": True,
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )
    return {
        "schema_version": "ppt_run2_product_surface_scene_memory.v1",
        "status": "run2_53_product_surface_scene_memory_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_repair_run_id": "2.51",
        "source_generated_run_id": "2.52",
        "target_layer": TARGET_LAYER,
        "product_surface_scene_records": records,
    }


def build_business_visual_evidence_memory(
    scene_memory: dict[str, Any],
    run251_copy: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    scene_records = scene_memory["product_surface_scene_records"]
    copy_records = run251_copy["editorial_copy_records"]
    for role in ROLES:
        spec = ROLE_SCENE_SPECS[role]
        scene = role_record(scene_records, role, "Run 2.53 product surface scene")
        copy = role_record(copy_records, role, "Run 2.51 editorial copy")
        records.append(
            {
                "id": f"business_visual_evidence_2_53_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_run_ids": ["2.51", "2.52"],
                "required_product_surface_scene_id": scene["id"],
                "required_editorial_copy_memory_id": copy["copy_memory_id"],
                "observable_business_object": spec["primary_product_or_business_object"],
                "reader_question_answered": spec["reader_question_answered"],
                "business_claim_to_make_visible": copy["business_claim_preservation_check"],
                "minimum_visual_specificity_checks": [
                    "names a concrete product or business object before drawing",
                    "uses at least three role-specific surface slots",
                    "anchors proof copy to visible object regions instead of detached cards",
                    "forbids generic geometric diagram as the primary visual answer",
                ],
                "source_boundary": {
                    "derived_observations_only": True,
                    "raw_media_copied": False,
                    "source_layout_copied": False,
                    "source_brand_identity_copied": False,
                },
                "bad_control_probe": "Bad control fails if it can satisfy the slide with generic blocks and no inspectable product object.",
                "visual_validation_deferred_to_generated_rerun": True,
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )
    return {
        "schema_version": "ppt_run2_business_visual_evidence_memory.v1",
        "status": "run2_53_business_visual_evidence_memory_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_repair_run_id": "2.51",
        "source_generated_run_id": "2.52",
        "target_layer": TARGET_LAYER,
        "business_visual_evidence_records": records,
    }


def build_scene_renderer_workflow_gates(
    scene_memory: dict[str, Any],
    evidence_memory: dict[str, Any],
    run251_gates: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    scene_records = scene_memory["product_surface_scene_records"]
    evidence_records = evidence_memory["business_visual_evidence_records"]
    run251_gate_records = run251_gates["renderer_archetype_workflow_gates"]
    for role in ROLES:
        scene = role_record(scene_records, role, "Run 2.53 product surface scene")
        evidence = role_record(evidence_records, role, "Run 2.53 business visual evidence")
        prior_gate = role_record(run251_gate_records, role, "Run 2.51 renderer gate")
        records.append(
            {
                "id": f"scene_renderer_gate_2_53_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_product_surface_scene_id": scene["id"],
                "required_business_visual_evidence_id": evidence["id"],
                "required_run2_51_renderer_archetype_gate_id": prior_gate["gate_id"],
                "required_trace_fields": TRACE_FIELDS,
                "pass_fail_checks": [
                    "Run 2.54 binds one product surface scene id before native drawing.",
                    "Run 2.54 binds one business visual evidence id before native drawing.",
                    "The primary object is a product or business surface, not generic geometry.",
                    "Forbidden generic geometry count is zero.",
                    "Every proof annotation points to a visible surface slot.",
                    "Bad control fails without Run 2.53 scene, evidence, and gate ids.",
                ],
                "consumer_contract": {
                    "next_generated_run": "2.54",
                    "must_bind_before_native_drawing": True,
                    "must_report_primary_product_or_business_object": True,
                    "must_report_forbidden_generic_geometry_count": True,
                    "required_trace_fields": TRACE_FIELDS,
                },
                "next_rerun_contract": NEXT_RERUN_CONTRACT,
                "visual_validation_deferred_to_generated_rerun": True,
                "public_release_gate": "blocked",
            }
        )
    return {
        "schema_version": "ppt_run2_scene_renderer_workflow_gates.v1",
        "status": "run2_53_scene_renderer_workflow_gates_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_repair_run_id": "2.51",
        "source_generated_run_id": "2.52",
        "target_layer": TARGET_LAYER,
        "next_rerun_contract": NEXT_RERUN_CONTRACT,
        "scene_renderer_workflow_gates": records,
    }


def build_result(
    out_dir: Path,
    scene_memory: dict[str, Any],
    evidence_memory: dict[str, Any],
    gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_product_surface_scene_repair_result.v1",
        "run_id": RUN_ID,
        "status": "run2_53_product_surface_scene_repair_ready_public_blocked",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "visual_validation_deferred_to_generated_rerun": True,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_repair_run_id": "2.51",
        "source_generated_run_id": "2.52",
        "target_layer": TARGET_LAYER,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "input_chain": {
            "run2_52_result": rel(PACK / "results" / "run2_52_editorial_socket_renderer_rerun_result.json"),
            "run2_52_full_trace": rel(PRESENTATIONS_DIR / "ppt-run2-52-full-vulca" / "trace_manifest.json"),
            "run2_51_editorial_copy_memory": rel(PACK / "run2_51_editorial_copy_memory.json"),
            "run2_51_shape_text_socket_memory": rel(PACK / "run2_51_shape_text_socket_memory.json"),
            "run2_51_renderer_archetype_workflow_gates": rel(
                PACK / "run2_51_renderer_archetype_workflow_gates.json"
            ),
        },
        "output_chain": {
            "product_surface_scene_memory": rel(out_dir / "run2_53_product_surface_scene_memory.json"),
            "business_visual_evidence_memory": rel(out_dir / "run2_53_business_visual_evidence_memory.json"),
            "scene_renderer_workflow_gates": rel(out_dir / "run2_53_scene_renderer_workflow_gates.json"),
        },
        "artifact_counts": {
            "product_surface_scene_records": len(scene_memory["product_surface_scene_records"]),
            "business_visual_evidence_records": len(evidence_memory["business_visual_evidence_records"]),
            "scene_renderer_workflow_gates": len(gates["scene_renderer_workflow_gates"]),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
        },
        "repair_contract": {
            "product surface scene": "each slide role must name and render an inspectable product or business object",
            "business visual evidence": "each proof claim must answer a viewer question through visible scene evidence",
            "scene renderer gates": "Run 2.54 must bind scene, evidence, and gate ids before native drawing",
            "data/workflow-only": True,
        },
        "release_boundary": (
            "public_blocked_until_run2_54_consumes_run2_53_artifacts_then_visual_review_render_review_motion_review_source_boundary_review_and_human_approval_pass"
        ),
        "public_release_gate": "blocked",
        "next_required_action": NEXT_ACTION,
    }


def workflow_stage(id_: str, order: int, layer: str, inputs: list[str], outputs: list[str], gates: list[str]) -> dict[str, Any]:
    return {
        "id": id_,
        "order": order,
        "layer": layer,
        "inputs": inputs,
        "outputs": outputs,
        "gates": gates,
        "visual_validation_deferred_to_generated_rerun": True,
        "creates_new_ppt_deck": False,
    }


def update_skill_workflow(path: Path) -> None:
    workflow = read_json(path)
    stage_ids = {
        "compile_run2_53_product_surface_scene_memory",
        "compile_run2_53_business_visual_evidence_memory",
        "apply_run2_53_scene_renderer_workflow_gates",
    }
    workflow["stages"] = [stage for stage in workflow["stages"] if stage["id"] not in stage_ids]
    workflow["status"] = "run2_53_product_surface_scene_workflow_directed_public_blocked"
    workflow["stages"].extend(
        [
            workflow_stage(
                "compile_run2_53_product_surface_scene_memory",
                50,
                "evidence_aesthetic_asset_memory",
                [
                    "run2_52_editorial_socket_renderer_rerun_result.json",
                    "ppt-run2-52-full-vulca/trace_manifest.json",
                    "run2_51_shape_text_socket_memory.json",
                ],
                [
                    "product surface scene ids",
                    "role-specific product or business objects",
                    "surface slot obligations",
                    "generic geometry negative rules",
                ],
                [
                    "every role names one primary product or business object",
                    "every role has at least three surface slots",
                    "generic geometric diagram is forbidden as the primary answer",
                ],
            ),
            workflow_stage(
                "compile_run2_53_business_visual_evidence_memory",
                51,
                "evidence_aesthetic_asset_memory",
                [
                    "run2_53_product_surface_scene_memory.json",
                    "run2_51_editorial_copy_memory.json",
                ],
                [
                    "business visual evidence ids",
                    "reader question contracts",
                    "minimum visual specificity checks",
                    "source boundary checks",
                ],
                [
                    "every evidence record binds a product surface scene",
                    "every evidence record binds Run 2.51 editorial copy",
                    "raw media and source layout copying remain false",
                ],
            ),
            workflow_stage(
                "apply_run2_53_scene_renderer_workflow_gates",
                52,
                "skill_workflow",
                [
                    "run2_53_product_surface_scene_memory.json",
                    "run2_53_business_visual_evidence_memory.json",
                    "run2_51_renderer_archetype_workflow_gates.json",
                ],
                [
                    "scene renderer gate ids",
                    "Run 2.54 trace field requirements",
                    "native drawing binding contract",
                    "bad-control failure probe",
                ],
                [
                    "Run 2.54 must bind scene/evidence/gate ids before native drawing",
                    "primary product or business object must be trace-reported",
                    "forbidden generic geometry count must be zero",
                ],
            ),
        ]
    )
    workflow["stages"].sort(key=lambda stage: stage["order"])
    write_json(path, workflow)


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Run 2.53 Product Surface Scene Repair",
                "",
                "Status: data/workflow-only repair pack, public blocked.",
                "",
                "Run 2.53 does not generate a PPT. It thickens the product surface scene, business visual evidence, and scene renderer workflow gates for the next generated rerun.",
                "",
                "The purpose is to stop the deck from solving slides with abstract boxes, generic geometric diagram layouts, or detached evidence cards.",
                "",
                "## Outputs",
                "",
                "- `run2_53_product_surface_scene_memory.json`: per-role product surface scene contracts.",
                "- `run2_53_business_visual_evidence_memory.json`: per-role business visual evidence contracts.",
                "- `run2_53_scene_renderer_workflow_gates.json`: Run 2.54 scene renderer gates and trace requirements.",
                "",
                "## Gate",
                "",
                "Run 2.54 must consume Run 2.53 before native PPT drawing. Visual validation remains deferred until that generated rerun.",
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
        description="Build Run 2.53 product-surface-scene/business-visual-evidence repair pack."
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run252_result = read_json(PACK / "results" / "run2_52_editorial_socket_renderer_rerun_result.json")
    run252_full_trace = read_json(PRESENTATIONS_DIR / "ppt-run2-52-full-vulca" / "trace_manifest.json")
    run251_copy = read_json(PACK / "run2_51_editorial_copy_memory.json")
    run251_socket = read_json(PACK / "run2_51_shape_text_socket_memory.json")
    run251_gates = read_json(PACK / "run2_51_renderer_archetype_workflow_gates.json")
    validate_inputs(run252_result, run252_full_trace, run251_copy, run251_socket, run251_gates)
    assert_no_run253_deck_artifacts()

    usecase = selected_usecase()
    if usecase.get("id") != SELECTED_USECASE_ID:
        raise ValueError("Run 2.53 selected usecase mismatch")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    scene_memory = build_product_surface_scene_memory(run252_full_trace, run251_socket)
    evidence_memory = build_business_visual_evidence_memory(scene_memory, run251_copy)
    gates = build_scene_renderer_workflow_gates(scene_memory, evidence_memory, run251_gates)

    write_json(args.out_dir / "run2_53_product_surface_scene_memory.json", scene_memory)
    write_json(args.out_dir / "run2_53_business_visual_evidence_memory.json", evidence_memory)
    write_json(args.out_dir / "run2_53_scene_renderer_workflow_gates.json", gates)
    update_skill_workflow(PACK / "skill_workflow.json")

    result = build_result(args.out_dir, scene_memory, evidence_memory, gates)
    write_json(args.result_json, result)
    write_markdown(args.result_md, result)
    assert_no_run253_deck_artifacts()
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
