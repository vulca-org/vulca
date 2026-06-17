from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_247 = PRESENTATIONS / "ppt-run2-47-full-vulca"
BAD_247 = PRESENTATIONS / "ppt-run2-47-bad-missing-composition-grammar"
PRIOR_244 = PRESENTATIONS / "ppt-run2-44-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_48_composition_grammar_effectiveness_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_48_composition_grammar_effectiveness_audit.md"

FULL_STATUS = "run2_46_composition_grammar_consumed_before_native_ppt_drawing"
BAD_STATUS = "run2_44_geometry_present_but_run2_46_composition_grammar_missing"
NEXT_LAYER = "readability_content_density_and_editorial_renderer_repair"
NEXT_ACTION = "build_run2_49_readability_content_density_and_editorial_renderer_repair_before_rerun"
ROOT_CAUSE = (
    "run2_47_composition_grammar_consumed_but_visual_editorial_quality_still_not_public_grade"
)


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.48 audit missing required {label}: {path}")


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


def slot_count(slide: dict[str, Any]) -> int:
    return len(list_field(slide, "run2_44_semantic_asset_geometry_slots"))


def scene_object_count(slide: dict[str, Any]) -> int:
    return len(list_field(slide, "run2_47_visual_object_scene_objects"))


def slide_has_full_run247_binding(slide: dict[str, Any]) -> bool:
    code_modules = string_list_field(slide, "run2_47_code_module_ids")
    return (
        str(slide.get("run2_46_visual_object_grammar_id") or "").startswith(
            "visual_object_grammar_2_46_"
        )
        and str(slide.get("run2_46_multimodal_composition_decomposition_id") or "").startswith(
            "composition_decomposition_2_46_"
        )
        and str(slide.get("run2_46_composition_gate_id") or "").startswith("gate_2_46_")
        and slide.get("run2_46_slot_based_geometry_replaced") is True
        and slide.get("run2_46_source_boundary_status") == "derived_only_no_copied_media"
        and str(slide.get("run2_47_primary_composition_kind") or "")
        != "slot_based_semantic_geometry"
        and scene_object_count(slide) >= 3
        and slot_count(slide) == 0
        and len(code_modules) == 1
        and code_modules[0].startswith("drawRun247")
        and len(list_field(slide, "run2_46_composition_quality_checks")) >= 3
    )


def slide_is_bad_missing_composition_control(slide: dict[str, Any]) -> bool:
    return (
        (slide.get("run2_46_visual_object_grammar_id") or "") == ""
        and (slide.get("run2_46_multimodal_composition_decomposition_id") or "") == ""
        and (slide.get("run2_46_composition_gate_id") or "") == ""
        and slide.get("run2_46_slot_based_geometry_replaced") is False
        and str(slide.get("run2_47_primary_composition_kind") or "")
        == "slot_based_semantic_geometry"
        and scene_object_count(slide) == 0
        and slot_count(slide) == 3
    )


def role_records(
    full_trace: dict[str, Any],
    bad_trace: dict[str, Any],
    prior_trace: dict[str, Any],
) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    prior_by_role = {slide.get("role"): slide for slide in prior_trace.get("slides", [])}
    records: list[dict[str, Any]] = []
    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        prior = prior_by_role.get(role, {})
        metrics = slide.get("layout_metrics") or {}
        prior_metrics = prior.get("layout_metrics") or {}
        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "title": slide.get("title"),
                "run2_46_visual_object_grammar_id": slide.get(
                    "run2_46_visual_object_grammar_id"
                )
                or "",
                "run2_46_multimodal_composition_decomposition_id": slide.get(
                    "run2_46_multimodal_composition_decomposition_id"
                )
                or "",
                "run2_46_composition_gate_id": slide.get("run2_46_composition_gate_id") or "",
                "run2_47_primary_composition_kind": slide.get(
                    "run2_47_primary_composition_kind"
                )
                or "",
                "run2_47_scene_object_count": scene_object_count(slide),
                "run2_44_slots_in_full": slot_count(slide),
                "run2_44_slots_in_bad_control": slot_count(bad),
                "run2_44_slots_in_prior_full": slot_count(prior),
                "full_binding_passed": slide_has_full_run247_binding(slide),
                "bad_control_boundary_passed": slide_is_bad_missing_composition_control(bad),
                "quality_checks": list_field(slide, "run2_46_composition_quality_checks"),
                "motion_or_sequence_implication": slide.get(
                    "run2_46_motion_or_sequence_implication"
                )
                or "",
                "content_density": {
                    "visible_words": metrics.get("visible_words"),
                    "text_density_tier": metrics.get("text_density_tier"),
                    "text_box_count": metrics.get("text_box_count"),
                    "proof_objects": metrics.get("proof_objects"),
                    "prior_visible_words": prior_metrics.get("visible_words"),
                    "prior_text_box_count": prior_metrics.get("text_box_count"),
                },
                "interpretation": (
                    "Run 2.47 changes the compiler path from Run 2.44 slots to a composed "
                    "visual-object scene, but the public surface still needs readability, "
                    "content-evidence density, and editorial renderer repair."
                ),
            }
        )
    return records


def average(values: list[int]) -> float:
    return round(sum(values) / len(values), 1) if values else 0.0


def validate_inputs(
    full_trace: dict[str, Any],
    bad_trace: dict[str, Any],
    prior_trace: dict[str, Any],
    run247_result: dict[str, Any],
) -> None:
    if full_trace.get("arm_id") != "run2_47_full_composition_grammar_compiler":
        raise ValueError("Run 2.48 audit expected Run 2.47 full trace")
    if full_trace.get("run2_47_composition_grammar_status") != FULL_STATUS:
        raise ValueError("Run 2.48 audit expected Run 2.47 full composition grammar status")
    if bad_trace.get("arm_id") != "bad_run2_46_missing_composition_grammar":
        raise ValueError("Run 2.48 audit expected Run 2.47 bad missing grammar trace")
    if bad_trace.get("run2_47_composition_grammar_status") != BAD_STATUS:
        raise ValueError("Run 2.48 audit expected Run 2.47 bad missing grammar status")
    if prior_trace.get("arm_id") != "run2_44_full_semantic_geometry_compiler":
        raise ValueError("Run 2.48 audit expected Run 2.44 full prior trace")
    if run247_result.get("status") != "run2_47_composition_grammar_rerun_public_blocked":
        raise ValueError("Run 2.48 audit expected Run 2.47 rerun result")

    full_roles = [slide.get("role") for slide in full_trace.get("slides", [])]
    bad_roles = [slide.get("role") for slide in bad_trace.get("slides", [])]
    prior_roles = [slide.get("role") for slide in prior_trace.get("slides", [])]
    if len(full_roles) != 6 or set(full_roles) != set(bad_roles) or set(full_roles) != set(prior_roles):
        raise ValueError("Run 2.48 audit expected six matching full, bad, and prior roles")


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_247 / "trace_manifest.json"
    bad_trace_path = BAD_247 / "trace_manifest.json"
    prior_trace_path = PRIOR_244 / "trace_manifest.json"
    run247_result_path = PACK / "results" / "run2_47_composition_grammar_rerun_result.json"
    run246_decomposition_path = PACK / "run2_46_multimodal_composition_decomposition.json"
    run246_grammar_path = PACK / "run2_46_visual_object_grammar_memory.json"
    run246_gates_path = PACK / "run2_46_composition_workflow_gates.json"
    run247_four_arm_path = PRESENTATIONS / "run2-47-four-arm-contact-sheet.png"
    run2_full_series_path = PRESENTATIONS / "run2-full-skill-series-horizontal.png"

    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    prior_trace = read_json(prior_trace_path)
    run247_result = read_json(run247_result_path)
    run246_decomposition = read_json(run246_decomposition_path)
    run246_grammar = read_json(run246_grammar_path)
    run246_gates = read_json(run246_gates_path)
    require_file(run247_four_arm_path, "Run 2.47 four-arm contact sheet")
    require_file(run2_full_series_path, "Run 2 full-skill series sheet")
    validate_inputs(full_trace, bad_trace, prior_trace, run247_result)

    full_slides = full_trace.get("slides", [])
    bad_slides = bad_trace.get("slides", [])
    prior_slides = prior_trace.get("slides", [])
    records = role_records(full_trace, bad_trace, prior_trace)
    full_binding_count = sum(1 for slide in full_slides if slide_has_full_run247_binding(slide))
    full_grammar_count = sum(
        1
        for slide in full_slides
        if str(slide.get("run2_46_visual_object_grammar_id") or "").startswith(
            "visual_object_grammar_2_46_"
        )
    )
    full_decomposition_count = sum(
        1
        for slide in full_slides
        if str(slide.get("run2_46_multimodal_composition_decomposition_id") or "").startswith(
            "composition_decomposition_2_46_"
        )
    )
    full_gate_count = sum(
        1
        for slide in full_slides
        if str(slide.get("run2_46_composition_gate_id") or "").startswith("gate_2_46_")
    )
    full_replaced_count = sum(
        1 for slide in full_slides if slide.get("run2_46_slot_based_geometry_replaced") is True
    )
    full_scene_count = sum(1 for slide in full_slides if scene_object_count(slide) >= 3)
    full_without_slots_count = sum(1 for slide in full_slides if slot_count(slide) == 0)
    bad_boundary_count = sum(
        1 for slide in bad_slides if slide_is_bad_missing_composition_control(slide)
    )
    bad_without_grammar_count = sum(
        1 for slide in bad_slides if (slide.get("run2_46_visual_object_grammar_id") or "") == ""
    )
    bad_with_slots_count = sum(1 for slide in bad_slides if slot_count(slide) == 3)
    prior_with_slots_count = sum(1 for slide in prior_slides if slot_count(slide) == 3)
    full_all = len(full_slides) == 6 and full_binding_count == 6
    bad_boundary = len(bad_slides) == 6 and bad_boundary_count == 6
    visible_words = [
        int((slide.get("layout_metrics") or {}).get("visible_words") or 0)
        for slide in full_slides
    ]
    text_boxes = [
        int((slide.get("layout_metrics") or {}).get("text_box_count") or 0)
        for slide in full_slides
    ]

    return {
        "schema_version": "ppt_run2_composition_grammar_effectiveness_audit.v1",
        "run_id": "2.48",
        "status": "run2_48_composition_grammar_effectiveness_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.47",
        "source_composition_memory_run": "2.46",
        "comparison_prior_generated_run": "2.44",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "input_chain": {
            "run2_47_full_trace_manifest": rel(full_trace_path),
            "run2_47_bad_trace_manifest": rel(bad_trace_path),
            "run2_47_rerun_result": rel(run247_result_path),
            "run2_46_multimodal_composition_decomposition": rel(run246_decomposition_path),
            "run2_46_visual_object_grammar_memory": rel(run246_grammar_path),
            "run2_46_composition_workflow_gates": rel(run246_gates_path),
            "run2_44_full_trace_manifest": rel(prior_trace_path),
            "run2_47_four_arm_contact_sheet": rel(run247_four_arm_path),
            "run2_full_skill_series_sheet": rel(run2_full_series_path),
        },
        "source_inventory": {
            "run2_46_multimodal_composition_decomposition_records": len(
                run246_decomposition["multimodal_composition_decomposition_records"]
            ),
            "run2_46_visual_object_grammar_records": len(
                run246_grammar["visual_object_grammar_records"]
            ),
            "run2_46_composition_workflow_gates": len(
                run246_gates["composition_workflow_gates"]
            ),
            "run2_47_full_trace_slides": len(full_slides),
            "run2_47_bad_trace_slides": len(bad_slides),
            "run2_44_prior_trace_slides": len(prior_slides),
        },
        "composition_grammar_trace_effectiveness": {
            "composition_grammar_consumed": full_all,
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": len(full_slides),
                "slides_with_run2_46_visual_object_grammar_id": full_grammar_count,
                "slides_with_run2_46_multimodal_composition_decomposition_id": (
                    full_decomposition_count
                ),
                "slides_with_run2_46_composition_gate_id": full_gate_count,
                "slides_with_slot_based_geometry_replaced": full_replaced_count,
                "slides_with_run2_47_scene_objects": full_scene_count,
                "slides_without_run2_44_slots": full_without_slots_count,
                "all_slides_have_grammar_decomposition_gate_and_slot_replacement": full_all,
                "role_records": records,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": len(bad_slides),
                "missing_composition_grammar_boundary_passed": bad_boundary,
                "slides_without_run2_46_grammar": bad_without_grammar_count,
                "slides_with_run2_44_slots": bad_with_slots_count,
                "slides_with_slot_based_primary_kind": sum(
                    1
                    for slide in bad_slides
                    if slide.get("run2_47_primary_composition_kind")
                    == "slot_based_semantic_geometry"
                ),
            },
            "prior_run2_44": {
                "arm_id": prior_trace.get("arm_id"),
                "slide_count": len(prior_slides),
                "slides_with_run2_44_slots": prior_with_slots_count,
                "compiler_kind": "slot_based_semantic_geometry",
            },
        },
        "visual_effectiveness_assessment": {
            "composition_compiler_kind": "visual_object_grammar_composed_object_scene",
            "prior_compiler_kind": "slot_based_semantic_geometry",
            "composition_grammar_delta_from_run2_44": (
                "proven_internal_only" if full_all and bad_boundary else "blocked"
            ),
            "public_video_grade_visual_quality": False,
            "visual_quality_gate": "blocked",
            "root_cause_primary": ROOT_CAUSE,
            "root_cause_secondary": [
                "Run 2.47 consumes Run 2.46 grammar and removes Run 2.44 slot geometry, so the data/workflow path is not the main failure anymore.",
                "The contact sheet shows a real structural delta, but some text is too small or clipped at review scale.",
                "Trace content density is rich by word count, yet the visual evidence is still abstract and not inspectable enough as commercial proof.",
                "The output still reads as an internal product-system presentation rather than a polished public-video-grade keynote.",
            ],
            "content_density_diagnosis": {
                "average_visible_words_per_slide": average(visible_words),
                "average_text_boxes_per_slide": average(text_boxes),
                "slides_with_rich_text_density": sum(
                    1
                    for slide in full_slides
                    if (slide.get("layout_metrics") or {}).get("text_density_tier") == "rich"
                ),
                "interpretation": (
                    "The issue is not raw word count. It is the hierarchy and inspectability of "
                    "commercial evidence, visual proof objects, and readable editorial surfaces."
                ),
            },
            "public_video_blockers": [
                "contact_sheet_scale_text_readability_and_slide_title_clipping",
                "commercial_proof_objects_not_yet_inspectable_enough",
                "editorial_composition_more_structured_than_prior_but_not_yet_premium",
                "motion_or_sequence_rules_stored_in_trace_but_not_delivered_as_native_animation",
            ],
            "top_next_layer_to_thicken": NEXT_LAYER,
            "why_user_still_sees_simple_design": (
                "The grammar changed layout structure, but the renderer still translates that grammar "
                "into native PPT shape scenes with limited photographic/product specificity, limited "
                "large-readable proof surfaces, and no delivered motion."
            ),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [rel(run247_four_arm_path), rel(run2_full_series_path)],
        },
        "gate_summary": {
            "grammar_consumption_gate": "pass_internal_only" if full_all else "blocked",
            "bad_control_gate": "pass" if bad_boundary else "blocked",
            "visual_effectiveness_gate": "blocked",
            "public_release_gate": "blocked",
            "summary": (
                "Run 2.48 confirms that Run 2.47 consumes visual object grammar and beats the "
                "bad missing-grammar control structurally, but public release stays blocked until "
                "readability, content-evidence density, and editorial renderer quality are repaired."
            ),
        },
        "next_required_action": NEXT_ACTION,
        "release_boundary": (
            "public_blocked_until_run2_49_repairs_readability_content_density_editorial_renderer_and_then_reruns_four_arms"
        ),
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    trace = audit["composition_grammar_trace_effectiveness"]
    full = trace["full_arm"]
    bad = trace["bad_control"]
    visual = audit["visual_effectiveness_assessment"]
    gate = audit["gate_summary"]
    lines = [
        "# Run 2.48 Composition Grammar Effectiveness Audit",
        "",
        "Status: audit-only, public blocked.",
        "",
        "Run 2.48 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "No Run 2.48 PPTX or download artifact is expected; the latest generated deck remains Run 2.47.",
        "",
        "The audit checks whether Run 2.47 really consumes Run 2.46 visual object grammar, whether slot-based geometry replaced Run 2.44, and why the full arm is still not public-video-grade.",
        "",
        "## Result",
        "",
        f"- Full arm consumes Run 2.46 grammar: {str(trace['composition_grammar_consumed']).lower()}.",
        f"- Full arm slides with visual object grammar ids: {full['slides_with_run2_46_visual_object_grammar_id']} / 6.",
        f"- Full arm slides with slot-based geometry replaced: {full['slides_with_slot_based_geometry_replaced']} / 6.",
        f"- Full arm slides without Run 2.44 slots: {full['slides_without_run2_44_slots']} / 6.",
        f"- Bad missing-grammar control passed: {str(bad['missing_composition_grammar_boundary_passed']).lower()}.",
        f"- Bad control slides with Run 2.44 slots: {bad['slides_with_run2_44_slots']} / 6.",
        "",
        "## Visual Finding",
        "",
        f"- Composition compiler kind: `{visual['composition_compiler_kind']}`.",
        f"- Delta from Run 2.44: `{visual['composition_grammar_delta_from_run2_44']}`.",
        "- The full arm is structurally stronger than the bad control, but it is not public-video-grade.",
        "- The problem has moved from data/workflow consumption to readability, content-evidence density, editorial composition, and renderer polish.",
        "- The trace has rich word count, but public-facing evidence still needs larger, more inspectable visual proof objects.",
        "",
        "## Gate",
        "",
        f"- Grammar consumption gate: `{gate['grammar_consumption_gate']}`.",
        f"- Bad control gate: `{gate['bad_control_gate']}`.",
        f"- Visual effectiveness gate: `{gate['visual_effectiveness_gate']}`.",
        f"- Public release gate: `{gate['public_release_gate']}`.",
        "",
        f"Next layer to thicken: `{visual['top_next_layer_to_thicken']}`.",
        "",
        f"Next: Run 2.49 should `{audit['next_required_action']}`.",
        "",
        "Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Run 2.47 composition grammar effectiveness."
    )
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
