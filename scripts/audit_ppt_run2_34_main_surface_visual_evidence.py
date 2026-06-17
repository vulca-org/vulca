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
FULL_33 = PRESENTATIONS / "ppt-run2-33-full-vulca"
BAD_33 = PRESENTATIONS / "ppt-run2-33-bad-main-surface-visual-evidence-memory"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_34_main_surface_visual_evidence_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_34_main_surface_visual_evidence_audit.md"

SOURCE_TARGET = "main_surface_information_density_and_visual_evidence_realism"
SOURCE_RERUN_VERDICT = (
    "main_surface_information_density_and_visual_evidence_realism_thickened_before_native_ppt_generation"
)
NEXT_LAYER = "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
NEXT_ACTION = "thicken_run2_33_visual_evidence_asset_realism_and_editorial_composition_before_run2_35_data_workflow"

RUN2_32_AUDIT_FIELDS = [
    "run2_32_source_audit_status",
    "run2_32_top_next_layer_to_thicken",
]
RUN2_33_MAIN_SURFACE_FIELDS = [
    "run2_33_visual_evidence_object_min_target",
    "run2_33_main_surface_visual_evidence_execution_status",
]
RUN2_33_REQUIRED_MODULES = [
    "drawRun233MainSurfaceEvidenceLayer",
    "drawRun233VisualEvidenceStoryboard",
]


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Run 2.34 audit missing required {label}: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Run 2.34 audit required {label} is not a file: {path}")


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


def bad_field_leak_count(slide: dict[str, Any]) -> int:
    return sum(1 for field in RUN2_32_AUDIT_FIELDS + RUN2_33_MAIN_SURFACE_FIELDS if non_empty(slide.get(field)))


def delivery_for_full_arm():
    require_file(FULL_33 / "output" / "ppt-run2-33-full-vulca.pptx", "Run 2.33 full PPTX")
    require_file(FULL_33 / "preview" / "contact-sheet.png", "Run 2.33 full contact sheet")
    return validate_delivery(
        pptx_path=FULL_33 / "output" / "ppt-run2-33-full-vulca.pptx",
        layout_dir=FULL_33 / "layout" / "final",
        contact_sheet_path=FULL_33 / "preview" / "contact-sheet.png",
        label="run2_33_full_vulca",
    )


def role_records(full_trace: dict[str, Any], bad_trace: dict[str, Any], delivery_media_count: int) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    records: list[dict[str, Any]] = []
    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        code_modules = [str(module) for module in slide.get("run2_33_code_module_ids") or []]
        metrics = slide.get("layout_metrics") or {}
        visual_evidence_objects = int(metrics.get("visual_evidence_objects") or 0)
        visual_evidence_min_target = int(slide.get("run2_33_visual_evidence_object_min_target") or 0)
        hero_share = float(metrics.get("hero_object_canvas_share") or 0)
        schematic_visual_evidence = delivery_media_count == 0
        weak_editorial_anchor = hero_share < 0.35
        issue_categories: list[str] = []
        if schematic_visual_evidence:
            issue_categories.append("visual_evidence_asset_realism")
        if weak_editorial_anchor:
            issue_categories.append("editorial_composition_strength")

        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "title": slide.get("title"),
                "run2_33_presentation_module_id": slide.get("run2_33_presentation_module_id"),
                "run2_33_required_code_module_ids": slide.get("run2_33_required_code_module_ids") or [],
                "run2_33_code_module_ids": code_modules,
                "main_surface_trace_closure": {
                    "run2_32_audit_status_present": non_empty(slide.get("run2_32_source_audit_status")),
                    "run2_32_top_next_layer": slide.get("run2_32_top_next_layer_to_thicken"),
                    "execution_status_present": slide.get("run2_33_main_surface_visual_evidence_execution_status")
                    == SOURCE_RERUN_VERDICT,
                    "required_trace_fields_present": all(
                        non_empty(slide.get(field)) for field in RUN2_32_AUDIT_FIELDS + RUN2_33_MAIN_SURFACE_FIELDS
                    ),
                },
                "main_surface_modules": {
                    "main_surface_evidence_layer_called": "drawRun233MainSurfaceEvidenceLayer" in code_modules,
                    "visual_evidence_storyboard_called": "drawRun233VisualEvidenceStoryboard" in code_modules,
                    "readable_evidence_spine_preserved": "drawRun233ReadableEvidenceSpine" in code_modules,
                },
                "main_surface_density": {
                    "visible_words": int(metrics.get("visible_words") or 0),
                    "proof_objects": int(metrics.get("proof_objects") or 0),
                    "content_cards": int(metrics.get("content_cards") or 0),
                    "visual_evidence_objects": visual_evidence_objects,
                    "visual_evidence_object_min_target": visual_evidence_min_target,
                    "visual_evidence_object_target_met": visual_evidence_objects >= visual_evidence_min_target >= 2,
                },
                "visual_evidence_realism": {
                    "asset_ids": slide.get("run2_24_visual_evidence_asset_ids") or [],
                    "media_entries_in_pptx": delivery_media_count,
                    "schematic_visual_evidence": schematic_visual_evidence,
                    "needs_usecase_specific_asset_realism": schematic_visual_evidence,
                },
                "editorial_composition": {
                    "hero_object_canvas_share": hero_share,
                    "weak_editorial_anchor": weak_editorial_anchor,
                    "needs_stronger_climax_or_product_stage": weak_editorial_anchor,
                },
                "bad_control_leaked_field_count": bad_field_leak_count(bad),
                "issue_categories": issue_categories,
                "status": "pass_internal_only_needs_next_data_workflow_thickening"
                if issue_categories
                else "pass_internal_only",
                "recommended_next_action": (
                    "thicken visual evidence asset realism and editorial composition in Run 2.35 data/workflow"
                    if issue_categories
                    else "preserve this role contract and continue public-blocked review"
                ),
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_33 / "trace_manifest.json"
    bad_trace_path = BAD_33 / "trace_manifest.json"
    run233_result_path = PACK / "results" / "run2_33_main_surface_visual_evidence_rerun_result.json"
    run232_audit_path = PACK / "results" / "run2_32_spine_climax_repair_audit.json"
    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    run233_result = read_json(run233_result_path)
    run232_audit = read_json(run232_audit_path)
    delivery = delivery_for_full_arm()
    delivery_media_count = len(delivery.checks.get("media_entries", []))
    records = role_records(full_trace, bad_trace, delivery_media_count)

    slide_count = len(full_trace.get("slides", []))
    source_audit_consumed = sum(
        1
        for slide in full_trace.get("slides", [])
        if slide.get("run2_32_top_next_layer_to_thicken") == SOURCE_TARGET
        and non_empty(slide.get("run2_32_source_audit_status"))
    )
    main_surface_status_slides = sum(
        1
        for slide in full_trace.get("slides", [])
        if slide.get("run2_33_main_surface_visual_evidence_execution_status") == SOURCE_RERUN_VERDICT
    )
    main_surface_module_count = sum(
        1
        for record in records
        if record["main_surface_modules"]["main_surface_evidence_layer_called"]
    )
    storyboard_module_count = sum(
        1
        for record in records
        if record["main_surface_modules"]["visual_evidence_storyboard_called"]
    )
    target_met_count = sum(
        1
        for record in records
        if record["main_surface_density"]["visual_evidence_object_target_met"]
    )
    bad_leaks = sum(record["bad_control_leaked_field_count"] for record in records)
    weak_editorial_roles = [
        record["role"] for record in records if record["editorial_composition"]["weak_editorial_anchor"]
    ]
    schematic_roles = [
        record["role"] for record in records if record["visual_evidence_realism"]["schematic_visual_evidence"]
    ]
    forbidden_outputs = sorted(rel(path) for path in PRESENTATIONS.glob("*2-34*"))
    static_no_animation = not bool((delivery.checks.get("motion") or {}).get("has_motion_xml"))

    closed_target = (
        source_audit_consumed == slide_count
        and main_surface_status_slides == slide_count
        and main_surface_module_count == slide_count
        and storyboard_module_count == slide_count
        and target_met_count == slide_count
        and bad_leaks == 0
    )

    return {
        "schema_version": "ppt_run2_main_surface_visual_evidence_audit.v1",
        "run_id": "2.34",
        "status": "run2_34_main_surface_visual_evidence_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.33",
        "source_audit_run": "2.32",
        "source_rerun_run": "2.33",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "issue_categories": [
            "main_surface_visual_evidence_closure",
            "visual_evidence_asset_realism",
            "editorial_composition_strength",
            "motion_or_video_delivery",
            "public_release_gate",
        ],
        "input_chain": {
            "run2_33_full_trace_manifest": rel(full_trace_path),
            "run2_33_bad_trace_manifest": rel(bad_trace_path),
            "run2_33_rerun_result": rel(run233_result_path),
            "run2_32_spine_climax_repair_audit": rel(run232_audit_path),
            "run2_33_full_layout_dir": rel(FULL_33 / "layout" / "final"),
            "run2_33_full_contact_sheet": rel(FULL_33 / "preview" / "contact-sheet.png"),
            "run2_33_four_arm_contact_sheet": rel(PRESENTATIONS / "run2-33-four-arm-contact-sheet.png"),
            "run2_33_delivery_validation": rel(FULL_33 / "qa" / "delivery-validation.json"),
            "source_audit_target": run232_audit.get("quality_summary", {}).get("top_next_layer_to_thicken"),
            "source_rerun_verdict": run233_result.get("rerun", {}).get("best_internal_arm_verdict"),
        },
        "no_new_deck_proof": {
            "presentations_dir": rel(PRESENTATIONS),
            "forbidden_run2_34_output_glob": "*2-34*",
            "matched_run2_34_outputs": forbidden_outputs,
            "new_pptx_created": any(path.endswith(".pptx") for path in forbidden_outputs),
            "status": "pass" if not any(path.endswith(".pptx") for path in forbidden_outputs) else "blocked",
        },
        "trace_closure": {
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": slide_count,
                "run2_32_audit_consumed_slides": source_audit_consumed,
                "main_surface_execution_status_slides": main_surface_status_slides,
                "main_surface_evidence_layer_modules_called": main_surface_module_count,
                "visual_evidence_storyboard_modules_called": storyboard_module_count,
                "visual_evidence_object_target_slides": target_met_count,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": len(bad_trace.get("slides", [])),
                "main_surface_fields_leaked": bad_leaks,
            },
        },
        "main_surface_verification": {
            "source_audit_target": run232_audit.get("quality_summary", {}).get("top_next_layer_to_thicken"),
            "source_rerun_verdict": run233_result.get("rerun", {}).get("best_internal_arm_verdict"),
            "closure_basis": "contract_only_module_calls_trace_fields_and_visual_object_counts_not_public_semantic_quality",
            "visual_evidence_object_target_met": target_met_count == slide_count,
            "main_surface_modules_called_by_contract": main_surface_module_count == slide_count
            and storyboard_module_count == slide_count,
            "delivery_gate": delivery.delivery_gate,
            "static_no_animation": static_no_animation,
            "human_review_required": bool(delivery.checks.get("human_review_required")),
            "media_entry_count": delivery_media_count,
            "native_render_verified": False,
        },
        "quality_summary": {
            "main_surface_visual_evidence_gate": "pass_internal_only" if closed_target else "blocked",
            "public_release_gate": "blocked",
            "closed_target_layers": [SOURCE_TARGET] if closed_target else [],
            "closed_target_layers_basis": "internal_contract_only_not_public_video_grade_or_semantic_evidence_quality",
            "roles_with_weak_editorial_anchor": weak_editorial_roles,
            "roles_with_schematic_visual_evidence": schematic_roles,
            "top_next_layer_to_thicken": NEXT_LAYER,
            "reason": (
                "Run 2.33 closes the contract-only quantitative main-surface visual-evidence target internally: each slide "
                "calls the main-surface evidence layer and storyboard modules, preserves the Run 2.32 audit target, "
                "and renders at least two visual evidence objects. It still remains public-blocked because the "
                "evidence is mostly schematic native PPT structure, several roles have weak editorial anchors, "
                "and the PPTX is static with no motion/video delivery."
            ),
        },
        "role_records": records,
        "audit_method": {
            "schematic_visual_evidence_rule": "pptx_media_entry_count_equals_zero_so_visual_evidence_is_native_schematic_not_real_or_high_fidelity_media",
            "weak_editorial_anchor_rule": "hero_object_canvas_share_below_0_35",
            "quantity_gate_rule": "each_full_slide_calls_drawRun233MainSurfaceEvidenceLayer_and_drawRun233VisualEvidenceStoryboard_and_has_visual_evidence_objects_greater_or_equal_to_target",
            "public_quality_boundary": "audit_does_not_claim_public_video_grade_aesthetic_or_semantic_visual_evidence_quality",
        },
        "module_recommendations": [
            {
                "target": NEXT_LAYER,
                "priority": 1,
                "issue": "visual evidence objects are traceable but still schematic rather than usecase-specific product or business evidence",
                "affected_roles": schematic_roles,
                "required_next_delta": (
                    "Run 2.35 data/workflow should expand visual evidence asset memory with richer product states, "
                    "case-specific proof captions, and native drawing instructions that avoid generic block diagrams."
                ),
            },
            {
                "target": NEXT_LAYER,
                "priority": 2,
                "issue": "cover, setup, contrast, and close do not yet have a strong enough editorial anchor at thumbnail scale",
                "affected_roles": weak_editorial_roles,
                "required_next_delta": (
                    "Run 2.35 data/workflow should add editorial composition obligations before the next generated rerun: "
                    "larger product/result objects, clearer hierarchy, and fewer equal-weight schematic panels."
                ),
            },
            {
                "target": "motion_or_video_delivery",
                "priority": 3,
                "issue": "delivery validator confirms static PPTX output with no transition, timing, animation, audio, or video XML",
                "affected_roles": [record["role"] for record in records],
                "required_next_delta": "keep public release blocked until a later motion/video proof or native-render review exists",
            },
        ],
        "remaining_public_release_gates": [
            "human_visual_review",
            "native_or_cross_platform_render_inspection",
            "motion_or_video_review",
            "source_boundary_review",
            "human_release_approval",
        ],
        "next_required_action": NEXT_ACTION,
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    summary = audit["quality_summary"]
    verification = audit["main_surface_verification"]
    trace = audit["trace_closure"]
    lines = [
        "# Run 2.34 Main Surface Visual Evidence Audit",
        "",
        "Status: main-surface visual-evidence audit completed, public blocked.",
        "",
        "Run 2.34 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It audits whether Run 2.33 actually consumed the Run 2.32 spine/climax repair audit and thickened `drawRun233MainSurfaceEvidenceLayer` plus `drawRun233VisualEvidenceStoryboard` before deciding the next data/workflow target.",
        "",
        "## Result",
        "",
        f"- Main-surface gate: `{summary['main_surface_visual_evidence_gate']}`",
        f"- Public release gate: `{summary['public_release_gate']}`",
        f"- Source audit target: `{verification['source_audit_target']}`",
        f"- Source rerun verdict: `{verification['source_rerun_verdict']}`",
        f"- Closure basis: `{verification['closure_basis']}`",
        f"- Visual evidence object target met: `{verification['visual_evidence_object_target_met']}`",
        f"- Delivery gate: `{verification['delivery_gate']}`",
        f"- Static/no animation: `{verification['static_no_animation']}`",
        f"- Human review required: `{verification['human_review_required']}`",
        f"- Run 2.32 audit consumed slides: `{trace['full_arm']['run2_32_audit_consumed_slides']}` / `{trace['full_arm']['slide_count']}`",
        f"- Main-surface module calls: `{trace['full_arm']['main_surface_evidence_layer_modules_called']}` / `{trace['full_arm']['slide_count']}`",
        f"- Storyboard module calls: `{trace['full_arm']['visual_evidence_storyboard_modules_called']}` / `{trace['full_arm']['slide_count']}`",
        f"- Bad-control main-surface leaks: `{trace['bad_control']['main_surface_fields_leaked']}`",
        f"- Top next layer to thicken: `{summary['top_next_layer_to_thicken']}`",
        f"- Weak editorial anchor roles: `{', '.join(summary['roles_with_weak_editorial_anchor']) or 'none'}`",
        f"- Schematic visual evidence roles: `{', '.join(summary['roles_with_schematic_visual_evidence']) or 'none'}`",
        "",
        "## Role Records",
        "",
    ]
    for record in audit["role_records"]:
        lines.append(
            f"- `{record['role']}`: module=`{record['run2_33_presentation_module_id']}`; "
            f"visual_evidence={record['main_surface_density']['visual_evidence_objects']}; "
            f"hero_share={record['editorial_composition']['hero_object_canvas_share']:.3f}; "
            f"schematic={record['visual_evidence_realism']['schematic_visual_evidence']}; "
            f"issues=`{', '.join(record['issue_categories']) or 'none'}`; "
            f"next={record['recommended_next_action']}"
        )
    lines.extend(
        [
            "",
            "## Required Next Action",
            "",
            f"`{NEXT_LAYER}` in Run 2.35 data/workflow before another generated rerun.",
            "",
            "Do not advance to Run 3.0.",
            "",
        ]
    )
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.33 main-surface visual evidence without generating a deck.")
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
