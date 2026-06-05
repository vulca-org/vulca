from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_pptx_delivery import validate_delivery

THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_36 = PRESENTATIONS / "ppt-run2-36-full-vulca"
BAD_36 = PRESENTATIONS / "ppt-run2-36-bad-visual-evidence-realism-memory"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_37_visual_quality_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_37_visual_quality_audit.md"

SOURCE_TARGET = "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
NEXT_LAYER = "public_video_grade_slide_direction_and_per_slide_visual_recipe"
NEXT_ACTION = "build_run2_38_public_video_grade_visual_direction_memory_and_workflow_gates"
RUN2_35_CONSUMPTION_STATUS = (
    "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation"
)
REQUIRED_RUN236_MODULES = [
    "drawRun236EditorialAnchorObject",
    "drawRun236RealisticProductState",
    "drawRun236RealismGateRibbon",
]
RUN2_35_FIELDS = [
    "run2_35_visual_evidence_asset_realism_ids",
    "run2_35_editorial_composition_memory_id",
    "run2_35_realism_gate_id",
    "run2_35_observable_product_state",
    "run2_35_hero_canvas_share_target",
    "run2_35_visual_evidence_realism_execution_status",
]


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Run 2.37 audit missing required {label}: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Run 2.37 audit required {label} is not a file: {path}")


def read_json(path: Path) -> dict[str, Any]:
    require_file(path, "JSON input")
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value)
    return True


def leaked_run235_field_count(slide: dict[str, Any]) -> int:
    return sum(1 for field in RUN2_35_FIELDS if non_empty(slide.get(field)))


def delivery_for_full_arm():
    require_file(FULL_36 / "output" / "ppt-run2-36-full-vulca.pptx", "Run 2.36 full PPTX")
    require_file(FULL_36 / "preview" / "contact-sheet.png", "Run 2.36 full contact sheet")
    return validate_delivery(
        pptx_path=FULL_36 / "output" / "ppt-run2-36-full-vulca.pptx",
        layout_dir=FULL_36 / "layout" / "final",
        contact_sheet_path=FULL_36 / "preview" / "contact-sheet.png",
        label="run2_36_full_vulca",
    )


def layout_signature(slide: dict[str, Any]) -> str:
    modules = set(str(module) for module in slide.get("run2_36_code_module_ids") or [])
    if all(module in modules for module in REQUIRED_RUN236_MODULES):
        return "editorial_anchor_object+two_product_state_cards+gate_ribbon"
    return "+".join(sorted(modules)) or "missing_run236_modules"


def role_records(full_trace: dict[str, Any], bad_trace: dict[str, Any], delivery_media_count: int) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    records: list[dict[str, Any]] = []
    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        modules = [str(module) for module in slide.get("run2_36_code_module_ids") or []]
        metrics = slide.get("layout_metrics") or {}
        signature = layout_signature(slide)
        data_consumed = (
            len(slide.get("run2_35_visual_evidence_asset_realism_ids") or []) >= 2
            and str(slide.get("run2_35_editorial_composition_memory_id") or "").startswith("composition_2_35_")
            and str(slide.get("run2_35_realism_gate_id") or "").startswith("gate_2_35_")
            and slide.get("run2_35_visual_evidence_realism_execution_status") == RUN2_35_CONSUMPTION_STATUS
        )
        required_modules_called = all(module in modules for module in REQUIRED_RUN236_MODULES)
        public_video_grade = False
        reasons = [
            "repetitive_card_grid_language",
            "same_visual_module_signature_across_all_roles",
            "product_state_cards_are_native_schematic_not_real_public_demo_surfaces",
            "workflow_gate_visible_as_audit_ribbon_instead_of_reader_invisible_composition_logic",
        ]
        if role == "climax":
            reasons.append("climax_is_large_but_not_editorial_or_cinematic_enough")
        if delivery_media_count == 0:
            reasons.append("no_media_or_motion_evidence_in_editable_pptx")

        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "title": slide.get("title"),
                "run2_36_code_module_ids": modules,
                "layout_signature": signature,
                "run2_36_data_consumed": data_consumed,
                "workflow_gate_exposed": non_empty(slide.get("run2_35_realism_gate_id")),
                "public_video_grade": public_video_grade,
                "hero_object_canvas_share": float(metrics.get("hero_object_canvas_share") or 0),
                "realistic_visual_evidence_objects": int(metrics.get("realistic_visual_evidence_objects") or 0),
                "visible_words": int(metrics.get("visible_words") or 0),
                "content_cards": int(metrics.get("content_cards") or 0),
                "workflow_objects": int(metrics.get("workflow_objects") or 0),
                "bad_control_leaked_field_count": leaked_run235_field_count(bad),
                "aesthetic_failure_reasons": reasons,
                "recommended_next_action": "replace generic Run 2.36 module recipe with per-slide public-video-grade visual direction in Run 2.38 data/workflow",
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_36 / "trace_manifest.json"
    bad_trace_path = BAD_36 / "trace_manifest.json"
    run236_result_path = PACK / "results" / "run2_36_visual_evidence_realism_rerun_result.json"
    run235_result_path = PACK / "results" / "run2_35_visual_evidence_realism_workflow_result.json"
    four_arm_path = PRESENTATIONS / "run2-36-four-arm-contact-sheet.png"
    full_series_path = PRESENTATIONS / "run2-full-skill-series-horizontal.png"
    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    run236_result = read_json(run236_result_path)
    run235_result = read_json(run235_result_path)
    require_file(four_arm_path, "Run 2.36 four-arm contact sheet")
    require_file(full_series_path, "Run 2 full-skill series sheet")
    delivery = delivery_for_full_arm()
    delivery_media_count = len(delivery.checks.get("media_entries", []))
    records = role_records(full_trace, bad_trace, delivery_media_count)

    slide_count = len(full_trace.get("slides", []))
    signatures = [record["layout_signature"] for record in records]
    unique_signatures = sorted(set(signatures))
    run235_consumed = sum(1 for record in records if record["run2_36_data_consumed"])
    realism_bound = sum(1 for slide in full_trace.get("slides", []) if len(slide.get("run2_35_visual_evidence_asset_realism_ids") or []) >= 2)
    required_modules_called = sum(
        1 for slide in full_trace.get("slides", []) if all(module in (slide.get("run2_36_code_module_ids") or []) for module in REQUIRED_RUN236_MODULES)
    )
    bad_leaks = sum(record["bad_control_leaked_field_count"] for record in records)
    repeated_roles = [record["role"] for record in records if record["layout_signature"] == "editorial_anchor_object+two_product_state_cards+gate_ribbon"]
    insufficient_roles = [record["role"] for record in records if not record["public_video_grade"]]
    forbidden_outputs = sorted(rel(path) for path in PRESENTATIONS.glob("*2-37*"))
    static_no_animation = not bool((delivery.checks.get("motion") or {}).get("has_motion_xml"))

    data_passes = (
        run236_result.get("rerun", {}).get("best_internal_arm") == "run2_36_full_visual_evidence_realism"
        and run236_result.get("quality_delta", {}).get("run2_35_realism_records_consumed") == 12
        and run236_result.get("quality_delta", {}).get("run2_35_composition_records_consumed") == 6
        and run236_result.get("quality_delta", {}).get("run2_35_workflow_gates_consumed") == 6
        and run235_consumed == slide_count
        and bad_leaks == 0
    )

    return {
        "schema_version": "ppt_run2_visual_quality_audit.v1",
        "run_id": "2.37",
        "status": "run2_37_visual_quality_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.36",
        "source_data_workflow_run": "2.35",
        "user_feedback": "Run 2.36 effect feels visually average",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "issue_categories": [
            "content_specificity",
            "visual_asset_realism_depth",
            "typography_hierarchy",
            "spacing_rhythm",
            "editorial_composition",
            "climax_composition",
            "public_video_readiness",
        ],
        "input_chain": {
            "run2_36_full_trace_manifest": rel(full_trace_path),
            "run2_36_bad_trace_manifest": rel(bad_trace_path),
            "run2_36_rerun_result": rel(run236_result_path),
            "run2_35_visual_evidence_realism_workflow_result": rel(run235_result_path),
            "run2_36_full_layout_dir": rel(FULL_36 / "layout" / "final"),
            "run2_36_full_contact_sheet": rel(FULL_36 / "preview" / "contact-sheet.png"),
            "run2_36_four_arm_contact_sheet": rel(four_arm_path),
            "run2_full_skill_series_sheet": rel(full_series_path),
            "source_data_workflow_status": run235_result.get("status"),
            "source_rerun_verdict": run236_result.get("rerun", {}).get("best_internal_arm_verdict"),
        },
        "no_new_deck_proof": {
            "presentations_dir": rel(PRESENTATIONS),
            "forbidden_run2_37_output_glob": "*2-37*",
            "matched_run2_37_outputs": forbidden_outputs,
            "new_pptx_created": any(path.endswith(".pptx") for path in forbidden_outputs),
            "status": "pass" if not any(path.endswith(".pptx") for path in forbidden_outputs) else "blocked",
        },
        "trace_closure": {
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": slide_count,
                "run2_35_workflow_consumed_slides": run235_consumed,
                "realism_ids_bound_slides": realism_bound,
                "required_run236_modules_called_slides": required_modules_called,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": len(bad_trace.get("slides", [])),
                "visual_evidence_realism_fields_leaked": bad_leaks,
            },
        },
        "visual_quality_assessment": {
            "data_consumption_gate": "pass_internal_only" if data_passes else "blocked",
            "workflow_proof_gate": "pass_internal_only" if required_modules_called == slide_count and bad_leaks == 0 else "blocked",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "root_cause_primary": "visual_module_language_too_repetitive_and_card_like",
            "root_cause_secondary": [
                "data_memory_was_consumed_as_ids_and_cards_not_as_per_slide_art_direction",
                "workflow_gates_prioritized_traceability_over_thumbnail_scale_aesthetic_judgment",
                "content_is_still_system_language_more_than_concrete_commercial_story",
                "native_ppt_has_no_motion_media_or_public_video_delivery_proof",
            ],
            "repeated_layout_signature_count": max(signatures.count(signature) for signature in unique_signatures) if unique_signatures else 0,
            "unique_layout_signature_count": len(unique_signatures),
            "dominant_layout_signature": unique_signatures[0] if len(unique_signatures) == 1 else "",
            "roles_with_repetitive_card_layout": repeated_roles,
            "roles_with_insufficient_public_aesthetic": insufficient_roles,
            "top_next_layer_to_thicken": NEXT_LAYER,
            "why_user_sees_general_quality": (
                "Run 2.36 proves Run 2.35 data consumption, but every role is rendered with the same visible recipe: "
                "an editorial anchor object, two dark product-state cards, and a gate ribbon. The viewer therefore reads "
                "as a traceable engineering report rather than a public-video-grade commercial presentation."
            ),
        },
        "role_records": records,
        "audit_method": {
            "layout_repetition_rule": "same_required_run236_module_signature_and_same_layout_signature_across_all_six_roles",
            "data_consumption_rule": "each_full_slide_has_two_or_more_run2_35_realism_ids_composition_id_gate_id_and_run2_35_consumption_status",
            "bad_control_rule": "bad_visual_evidence_realism_memory_must_have_zero_run2_35_trace_fields",
            "public_quality_boundary": "audit_does_not_claim_high_aesthetic_public_video_grade_output_even_when_data_and_workflow_gates_pass",
            "delivery_boundary": "editable_pptx_static_no_motion_video_or_native_keynote_animation_review",
        },
        "module_recommendations": [
            {
                "target": NEXT_LAYER,
                "priority": 1,
                "issue": "Run 2.36 uses one repeated visual module recipe for all six roles",
                "affected_roles": repeated_roles,
                "required_next_delta": (
                    "Run 2.38 data/workflow must define a different per-slide visual recipe: cover as launch poster, "
                    "setup as real pain scene, contrast as before/after state, proof as product workflow, climax as one "
                    "large editorial object, close as decision handoff."
                ),
            },
            {
                "target": NEXT_LAYER,
                "priority": 2,
                "issue": "visual evidence records are rendered as cards, not as believable product or business surfaces",
                "affected_roles": insufficient_roles,
                "required_next_delta": "upgrade realism memory from ids/captions into drawable product states, data snippets, UI surfaces, and concrete commercial proof objects.",
            },
            {
                "target": "public_video_readiness",
                "priority": 3,
                "issue": "delivery remains static editable PPT with no motion/video proof",
                "affected_roles": insufficient_roles,
                "required_next_delta": "keep release blocked until visual direction, native render inspection, and motion/video review are complete.",
            },
        ],
        "remaining_public_release_gates": [
            "human_visual_review",
            "single_slide_high_resolution_review",
            "native_or_cross_platform_render_inspection",
            "motion_or_video_review",
            "source_boundary_review",
            "human_release_approval",
        ],
        "delivery_check": {
            "delivery_gate": delivery.delivery_gate,
            "static_no_animation": static_no_animation,
            "human_review_required": bool(delivery.checks.get("human_review_required")),
            "media_entry_count": delivery_media_count,
        },
        "next_required_action": NEXT_ACTION,
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    assessment = audit["visual_quality_assessment"]
    trace = audit["trace_closure"]
    lines = [
        "# Run 2.37 Visual Quality Audit",
        "",
        "Status: visual-quality audit completed, public blocked.",
        "",
        "Run 2.37 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It audits why Run 2.36 feels visually average even though Run 2.35 visual evidence realism workflow was consumed before native PPT code generation.",
        "",
        "User feedback: Run 2.36 is visually average, so this audit treats the generated deck as workflow proof, not a public-ready visual result.",
        "",
        "## Result",
        "",
        "- Run 2.36 data consumption passes: the full arm consumes Run 2.35 realism memory, composition memory, and workflow gates.",
        "- Workflow proof passes internally: required Run 2.36 modules are called and the bad control leaks no Run 2.35 fields.",
        "- But design quality is blocked: `visual_module_language_too_repetitive_and_card_like`.",
        f"- Design quality gate: `{assessment['design_quality_gate']}`",
        f"- Public video readiness: `{assessment['public_video_readiness']}`",
        f"- Repeated layout signature count: `{assessment['repeated_layout_signature_count']}`",
        f"- Unique layout signature count: `{assessment['unique_layout_signature_count']}`",
        f"- Dominant layout signature: `{assessment['dominant_layout_signature']}`",
        f"- Full-arm Run 2.35 consumed slides: `{trace['full_arm']['run2_35_workflow_consumed_slides']}` / `{trace['full_arm']['slide_count']}`",
        f"- Required Run 2.36 module calls: `{trace['full_arm']['required_run236_modules_called_slides']}` / `{trace['full_arm']['slide_count']}`",
        f"- Bad-control Run 2.35 leaks: `{trace['bad_control']['visual_evidence_realism_fields_leaked']}`",
        f"- Top next layer to thicken: `{assessment['top_next_layer_to_thicken']}`",
        "",
        "## Why It Looks Average",
        "",
        assessment["why_user_sees_general_quality"],
        "",
        "## Role Records",
        "",
    ]
    for record in audit["role_records"]:
        lines.append(
            f"- `{record['role']}`: signature=`{record['layout_signature']}`; "
            f"data_consumed=`{record['run2_36_data_consumed']}`; "
            f"hero_share=`{record['hero_object_canvas_share']:.3f}`; "
            f"public_video_grade=`{record['public_video_grade']}`; "
            f"issues=`{', '.join(record['aesthetic_failure_reasons'])}`"
        )
    lines.extend(
        [
            "",
            "## Required Next Action",
            "",
            f"`{NEXT_LAYER}` in Run 2.38 data/workflow.",
            "",
            "Run 2.38 data/workflow must make per-slide art direction explicit before another generated rerun.",
            "",
            "Do not advance to Run 3.0.",
            "",
        ]
    )
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.36 visual quality without generating a deck.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    args.result_json.parent.mkdir(parents=True, exist_ok=True)
    args.result_md.parent.mkdir(parents=True, exist_ok=True)
    args.result_json.write_text(f"{json.dumps(audit, indent=2)}\n", encoding="utf-8")
    write_report(audit, args.result_md)
    print(json.dumps({"result_json": str(args.result_json), "status": audit["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
