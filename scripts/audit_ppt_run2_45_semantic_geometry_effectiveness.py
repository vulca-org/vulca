from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_244 = PRESENTATIONS / "ppt-run2-44-full-vulca"
BAD_244 = PRESENTATIONS / "ppt-run2-44-bad-run2-43-name-only-geometry"
FULL_241 = PRESENTATIONS / "ppt-run2-41-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_45_semantic_geometry_effectiveness_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_45_semantic_geometry_effectiveness_audit.md"

RUN244_FULL_STATUS = "run2_43_workflow_consumed_for_data_bound_geometry"
RUN244_BAD_STATUS = "run2_43_names_only_geometry_control"
NEXT_LAYER = "multimodal_composition_memory_and_visual_object_grammar"
NEXT_ACTION = "build_run2_46_multimodal_composition_memory_and_workflow_thickening"
ROOT_CAUSE = "run2_44_dataflow_fixed_but_composition_compiler_still_slot_based"
GEOMETRY_SOURCE = (
    "run2_43_semantic_visual_asset_memory+"
    "run2_43_editorial_composition_typography_memory+"
    "run2_43_visual_asset_semantics_workflow_gates"
)


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.45 audit missing required {label}: {path}")


def read_json(path: Path) -> dict[str, Any]:
    require_file(path, "JSON input")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def list_field(record: dict[str, Any], field: str) -> list[Any]:
    value = record.get(field) or []
    return value if isinstance(value, list) else []


def string_list_field(record: dict[str, Any], field: str) -> list[str]:
    return [str(item) for item in list_field(record, field) if item]


def slide_has_full_run244_binding(slide: dict[str, Any]) -> bool:
    semantic_ids = string_list_field(slide, "run2_43_semantic_visual_asset_ids")
    slots = list_field(slide, "run2_44_semantic_asset_geometry_slots")
    slot_ids = [str(slot.get("asset_id")) for slot in slots if isinstance(slot, dict) and slot.get("asset_id")]
    code_modules = string_list_field(slide, "run2_44_code_module_ids")
    return (
        len(semantic_ids) == 3
        and all(asset_id.startswith("semantic_asset_2_43_") for asset_id in semantic_ids)
        and str(slide.get("run2_43_editorial_typography_memory_id") or "").startswith("editorial_typography_2_43_")
        and str(slide.get("run2_43_visual_asset_semantics_gate_id") or "").startswith("gate_2_43_")
        and slide.get("run2_43_visual_asset_semantics_execution_status") == "consumed_before_native_ppt_drawing"
        and slide.get("run2_43_source_boundary_status") == "derived_only_no_copied_media"
        and slide.get("run2_44_data_bound_geometry") is True
        and slide.get("run2_44_geometry_source") == GEOMETRY_SOURCE
        and len(slots) == 3
        and sorted(slot_ids) == sorted(semantic_ids)
        and len(code_modules) == 1
        and code_modules[0].startswith("drawRun244")
    )


def slide_is_name_only_control(slide: dict[str, Any]) -> bool:
    return (
        string_list_field(slide, "run2_43_semantic_visual_asset_ids") == []
        and (slide.get("run2_43_editorial_typography_memory_id") or "") == ""
        and (slide.get("run2_43_visual_asset_semantics_gate_id") or "") == ""
        and slide.get("run2_43_visual_asset_semantics_execution_status") == "not_consumed_name_only_control"
        and slide.get("run2_44_data_bound_geometry") is False
        and list_field(slide, "run2_44_semantic_asset_geometry_slots") == []
        and string_list_field(slide, "run2_44_code_module_ids") == []
    )


def geometry_slot_roles(slide: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    for slot in list_field(slide, "run2_44_semantic_asset_geometry_slots"):
        if isinstance(slot, dict) and slot.get("slot_role"):
            roles.append(str(slot["slot_role"]))
    return roles


def role_records(full_trace: dict[str, Any], bad_trace: dict[str, Any], run241_trace: dict[str, Any]) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    run241_by_role = {slide.get("role"): slide for slide in run241_trace.get("slides", [])}
    records: list[dict[str, Any]] = []
    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        prior = run241_by_role.get(role, {})
        slots = list_field(slide, "run2_44_semantic_asset_geometry_slots")
        slot_area_total = sum(
            float(slot.get("w") or 0) * float(slot.get("h") or 0)
            for slot in slots
            if isinstance(slot, dict)
        )
        main_slot_area = 0.0
        if slots and isinstance(slots[0], dict):
            main_slot_area = float(slots[0].get("w") or 0) * float(slots[0].get("h") or 0)
        slot_weight_ratio = round(main_slot_area / slot_area_total, 3) if slot_area_total else 0
        metrics = slide.get("layout_metrics") or {}
        prior_metrics = prior.get("layout_metrics") or {}
        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "title": slide.get("title"),
                "run2_43_semantic_visual_asset_ids": string_list_field(slide, "run2_43_semantic_visual_asset_ids"),
                "run2_43_editorial_typography_memory_id": slide.get("run2_43_editorial_typography_memory_id") or "",
                "run2_43_visual_asset_semantics_gate_id": slide.get("run2_43_visual_asset_semantics_gate_id") or "",
                "run2_44_layout_signature_target": slide.get("run2_44_layout_signature_target") or "",
                "run2_44_code_module_ids": string_list_field(slide, "run2_44_code_module_ids"),
                "geometry_slot_roles": geometry_slot_roles(slide),
                "geometry_slot_count": len(slots),
                "main_slot_area_ratio": slot_weight_ratio,
                "data_bound_geometry": slide.get("run2_44_data_bound_geometry") is True,
                "full_binding_passed": slide_has_full_run244_binding(slide),
                "bad_control_boundary_passed": slide_is_name_only_control(bad),
                "delta_from_run2_41": {
                    "prior_code_module_ids": string_list_field(prior, "run2_41_code_module_ids"),
                    "prior_visual_asset_surface_types": string_list_field(prior, "run2_41_visual_asset_surface_types"),
                    "prior_presentation_surface_weight": prior_metrics.get("presentation_surface_weight"),
                    "run2_44_presentation_surface_weight": metrics.get("presentation_surface_weight"),
                    "interpretation": "Run 2.44 changes the data binding and module path, but still renders semantic objects as explicit geometry slots.",
                },
                "composition_failure_reasons": [
                    "semantic objects are bound to rectangular or elliptical geometry slots",
                    "workflow gates prove id consumption but do not yet score editorial composition quality",
                    "visual object grammar remains generated from abstract derived instructions rather than tutorial/video composition examples",
                    "public-video-grade typography, motion, and cinematic object realism remain unproven",
                ],
                "recommended_next_action": NEXT_ACTION,
            }
        )
    return records


def validate_inputs(full_trace: dict[str, Any], bad_trace: dict[str, Any], run244_result: dict[str, Any]) -> None:
    if full_trace.get("arm_id") != "run2_44_full_semantic_geometry_compiler":
        raise ValueError("Run 2.45 audit expected Run 2.44 full trace")
    if bad_trace.get("arm_id") != "bad_run2_43_name_only_geometry":
        raise ValueError("Run 2.45 audit expected Run 2.44 bad name-only trace")
    if full_trace.get("run2_44_semantic_geometry_status") != RUN244_FULL_STATUS:
        raise ValueError("Run 2.45 audit expected Run 2.44 full semantic geometry status")
    if bad_trace.get("run2_44_semantic_geometry_status") != RUN244_BAD_STATUS:
        raise ValueError("Run 2.45 audit expected Run 2.44 bad name-only status")
    if run244_result.get("status") != "run2_44_semantic_geometry_rerun_public_blocked":
        raise ValueError("Run 2.45 audit expected Run 2.44 rerun result")
    full_roles = [slide.get("role") for slide in full_trace.get("slides", [])]
    bad_roles = [slide.get("role") for slide in bad_trace.get("slides", [])]
    if len(full_roles) != 6 or len(bad_roles) != 6 or set(full_roles) != set(bad_roles):
        raise ValueError("Run 2.45 audit expected six matching full/bad slide roles")


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_244 / "trace_manifest.json"
    bad_trace_path = BAD_244 / "trace_manifest.json"
    run241_trace_path = FULL_241 / "trace_manifest.json"
    run244_result_path = PACK / "results" / "run2_44_semantic_geometry_rerun_result.json"
    run243_semantic_path = PACK / "run2_43_semantic_visual_asset_memory.json"
    run243_editorial_path = PACK / "run2_43_editorial_composition_typography_memory.json"
    run243_gates_path = PACK / "run2_43_visual_asset_semantics_workflow_gates.json"
    run244_four_arm_path = PRESENTATIONS / "run2-44-four-arm-contact-sheet.png"
    run2_full_series_path = PRESENTATIONS / "run2-full-skill-series-horizontal.png"

    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    run241_trace = read_json(run241_trace_path)
    run244_result = read_json(run244_result_path)
    run243_semantic = read_json(run243_semantic_path)
    run243_editorial = read_json(run243_editorial_path)
    run243_gates = read_json(run243_gates_path)
    require_file(run244_four_arm_path, "Run 2.44 four-arm contact sheet")
    require_file(run2_full_series_path, "Run 2 full-skill series sheet")
    validate_inputs(full_trace, bad_trace, run244_result)

    full_slides = full_trace.get("slides", [])
    bad_slides = bad_trace.get("slides", [])
    records = role_records(full_trace, bad_trace, run241_trace)
    full_bound_count = sum(1 for slide in full_slides if slide_has_full_run244_binding(slide))
    full_ids_count = sum(1 for slide in full_slides if len(string_list_field(slide, "run2_43_semantic_visual_asset_ids")) == 3)
    full_geometry_count = sum(1 for slide in full_slides if slide.get("run2_44_data_bound_geometry") is True)
    bad_name_only_count = sum(1 for slide in bad_slides if slide_is_name_only_control(slide))
    bad_no_ids_count = sum(1 for slide in bad_slides if string_list_field(slide, "run2_43_semantic_visual_asset_ids") == [])
    bad_no_geometry_count = sum(1 for slide in bad_slides if slide.get("run2_44_data_bound_geometry") is False)
    slot_based_count = sum(
        1
        for slide in full_slides
        if len(list_field(slide, "run2_44_semantic_asset_geometry_slots")) == 3
        and geometry_slot_roles(slide)
    )
    full_all = len(full_slides) == 6 and full_bound_count == 6
    bad_boundary = len(bad_slides) == 6 and bad_name_only_count == 6

    return {
        "schema_version": "ppt_run2_semantic_geometry_effectiveness_audit.v1",
        "run_id": "2.45",
        "status": "run2_45_semantic_geometry_effectiveness_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.44",
        "source_workflow_run": "2.43",
        "comparison_prior_generated_run": "2.41",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "input_chain": {
            "run2_44_full_trace_manifest": rel(full_trace_path),
            "run2_44_bad_trace_manifest": rel(bad_trace_path),
            "run2_44_rerun_result": rel(run244_result_path),
            "run2_43_semantic_visual_asset_memory": rel(run243_semantic_path),
            "run2_43_editorial_composition_typography_memory": rel(run243_editorial_path),
            "run2_43_visual_asset_semantics_workflow_gates": rel(run243_gates_path),
            "run2_41_full_trace_manifest": rel(run241_trace_path),
            "run2_44_four_arm_contact_sheet": rel(run244_four_arm_path),
            "run2_full_skill_series_sheet": rel(run2_full_series_path),
        },
        "source_inventory": {
            "run2_43_semantic_visual_asset_records": len(run243_semantic["semantic_visual_asset_records"]),
            "run2_43_editorial_composition_typography_records": len(
                run243_editorial["editorial_composition_typography_records"]
            ),
            "run2_43_visual_asset_semantics_workflow_gates": len(
                run243_gates["visual_asset_semantics_workflow_gates"]
            ),
            "run2_44_full_trace_slides": len(full_slides),
            "run2_44_bad_trace_slides": len(bad_slides),
        },
        "semantic_geometry_trace_effectiveness": {
            "dataflow_bug_fixed": full_all and bad_boundary,
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": len(full_slides),
                "slides_with_run2_43_semantic_asset_ids": full_ids_count,
                "slides_with_editorial_typography_memory_id": sum(
                    1
                    for slide in full_slides
                    if str(slide.get("run2_43_editorial_typography_memory_id") or "").startswith(
                        "editorial_typography_2_43_"
                    )
                ),
                "slides_with_visual_asset_semantics_gate_id": sum(
                    1
                    for slide in full_slides
                    if str(slide.get("run2_43_visual_asset_semantics_gate_id") or "").startswith("gate_2_43_")
                ),
                "slides_with_data_bound_geometry": full_geometry_count,
                "all_slides_have_semantic_ids_memory_gate_and_geometry": full_all,
                "role_records": records,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": len(bad_slides),
                "name_only_boundary_passed": bad_boundary,
                "slides_without_semantic_asset_ids": bad_no_ids_count,
                "slides_without_data_bound_geometry": bad_no_geometry_count,
                "slides_with_name_only_surface_types": sum(
                    1
                    for slide in bad_slides
                    if string_list_field(slide, "run2_43_semantic_visual_asset_surface_types")
                    and slide_is_name_only_control(slide)
                ),
            },
        },
        "visual_effectiveness_assessment": {
            "composition_compiler_kind": "slot_based_semantic_geometry",
            "slot_based_geometry_slides": slot_based_count,
            "dataflow_fix_visual_delta_from_bad_control": "proven_internal_only" if full_all and bad_boundary else "blocked",
            "public_video_grade_visual_quality": False,
            "visual_quality_gate": "blocked",
            "root_cause_primary": ROOT_CAUSE,
            "root_cause_secondary": [
                "Run 2.44 binds data correctly, but the compiler still renders semantic assets as explicit geometry slots.",
                "Run 2.43 gates require id, memory, and gate binding, but they do not yet judge composition sophistication, visual object realism, or motion rhythm.",
                "The semantic memory is derived and source-safe, which is correct for copyright boundaries, but it needs thicker multimodal tutorial decomposition to become a richer composition language.",
                "The full arm is meaningfully stronger than the name-only control, but it is still not public-video-grade presentation design.",
            ],
            "top_next_layer_to_thicken": NEXT_LAYER,
            "why_user_still_sees_simple_design": (
                "The data path is now real, but the data is compiled into slot geometry. "
                "That proves workflow consumption while still feeling like a designed proof board rather than a high-end public presentation."
            ),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [rel(run244_four_arm_path), rel(run2_full_series_path)],
        },
        "gate_summary": {
            "dataflow_gate": "pass_internal_only" if full_all else "blocked",
            "bad_control_gate": "pass" if bad_boundary else "blocked",
            "composition_quality_gate": "blocked",
            "public_release_gate": "blocked",
            "summary": (
                "Run 2.45 confirms the Run 2.44 dataflow fix and preserves the name-only negative control, "
                "but blocks visual quality because the composition compiler is still slot-based."
            ),
        },
        "next_required_action": NEXT_ACTION,
        "release_boundary": "public_blocked_until_run2_46_data_workflow_thickening_then_generated_rerun_human_visual_review_native_render_review_and_motion_review",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    trace = audit["semantic_geometry_trace_effectiveness"]
    visual = audit["visual_effectiveness_assessment"]
    gate = audit["gate_summary"]
    lines = [
        "# Run 2.45 Semantic Geometry Effectiveness Audit",
        "",
        "Status: audit-only, public blocked.",
        "",
        "Run 2.45 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "The audit checks whether Run 2.44 actually fixed the Run 2.43 dataflow bug, and whether that fix is enough for public-video-grade presentation quality.",
        "",
        "## Result",
        "",
        f"- The dataflow bug is fixed: {str(trace['dataflow_bug_fixed']).lower()}.",
        f"- Full arm slides with semantic visual asset ids: {trace['full_arm']['slides_with_run2_43_semantic_asset_ids']} / 6.",
        f"- Full arm slides with data-bound geometry: {trace['full_arm']['slides_with_data_bound_geometry']} / 6.",
        f"- Bad name-only control passed: {str(trace['bad_control']['name_only_boundary_passed']).lower()}.",
        "",
        "## Visual Finding",
        "",
        f"- Composition compiler kind: `{visual['composition_compiler_kind']}`.",
        f"- Slot-based semantic geometry slides: {visual['slot_based_geometry_slides']} / 6.",
        "- The full arm is stronger than the name-only control, but it is not public-video-grade.",
        "- The composition compiler is still slot-based: semantic objects are placed into geometry slots rather than generated as richer product scenes, editorial spreads, or cinematic objects.",
        "",
        "## Gate",
        "",
        f"- Dataflow gate: `{gate['dataflow_gate']}`.",
        f"- Composition quality gate: `{gate['composition_quality_gate']}`.",
        f"- Public release gate: `{gate['public_release_gate']}`.",
        "",
        f"Next layer to thicken: `{visual['top_next_layer_to_thicken']}`.",
        "",
        f"Next: Run 2.46 should `{audit['next_required_action']}`.",
        "",
        "Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.44 semantic geometry effectiveness.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    write_json(args.result_json, audit)
    write_report(audit, args.result_md)
    print(json.dumps({"status": audit["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
