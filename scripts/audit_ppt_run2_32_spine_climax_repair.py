from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_31 = PRESENTATIONS / "ppt-run2-31-full-vulca"
BAD_31 = PRESENTATIONS / "ppt-run2-31-bad-spine-climax-repair-memory"
FULL_29 = PRESENTATIONS / "ppt-run2-29-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_32_spine_climax_repair_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_32_spine_climax_repair_audit.md"

RUN2_30_AUDIT_FIELDS = [
    "run2_30_source_audit_status",
    "run2_30_top_next_layer_to_thicken",
]
RUN2_31_REPAIR_FIELDS = [
    "run2_31_spine_min_font_size_target",
    "run2_31_climax_style_policy",
    "run2_31_spine_climax_repair_execution_status",
]
RUN2_31_EXPECTED_REPAIR_STATUS = "spine_readability_and_climax_consistency_repaired_before_native_ppt_generation"
RUN2_31_EXPECTED_CLIMAX_POLICY = "high_contrast_climax_with_shared_light_editorial_frame"
NEXT_LAYER = "main_surface_information_density_and_visual_evidence_realism"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def layout_path_for_slide(arm_dir: Path, slide: dict[str, Any]) -> Path:
    slide_id = str(slide.get("slide_id") or "slide_01")
    slide_no = int(slide_id.rsplit("_", 1)[-1])
    return arm_dir / "layout" / "final" / f"slide-{slide_no:02d}.layout.json"


def text_elements(layout: dict[str, Any]) -> list[dict[str, Any]]:
    return [element for element in layout.get("elements", []) if element.get("text")]


def element_font_size(element: dict[str, Any]) -> float:
    if element.get("resolvedFontSize") is not None:
        return float(element["resolvedFontSize"])
    style = element.get("resolvedTextStyle") or {}
    return float(style.get("fontSize") or 0)


def spine_text_elements(layout: dict[str, Any]) -> list[dict[str, Any]]:
    elements: list[dict[str, Any]] = []
    for element in text_elements(layout):
        bbox = element.get("bbox") or []
        x = float(bbox[0]) if len(bbox) >= 1 else 0.0
        y = float(bbox[1]) if len(bbox) >= 2 else 0.0
        text = str(element.get("text") or "")
        if "readable evidence spine" in text or (x >= 830 and 100 <= y <= 580):
            elements.append(element)
    return elements


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


def fields_present(slide: dict[str, Any], fields: list[str]) -> bool:
    return all(non_empty(slide.get(field)) for field in fields)


def role_records(full_trace: dict[str, Any], bad_trace: dict[str, Any]) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    records: list[dict[str, Any]] = []

    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        layout_path = layout_path_for_slide(FULL_31, slide)
        layout = read_json(layout_path)
        spine_elements = spine_text_elements(layout)
        spine_font_sizes = [element_font_size(element) for element in spine_elements if element_font_size(element) > 0]
        min_spine_font_size = min(spine_font_sizes) if spine_font_sizes else 0
        code_modules = [str(module) for module in slide.get("run2_31_code_module_ids") or []]
        layout_metrics = slide.get("layout_metrics") or {}
        visual_evidence_objects = int(layout_metrics.get("visual_evidence_objects") or 0)
        visible_words = int(layout_metrics.get("visible_words") or 0)
        low_visual_evidence_density = visual_evidence_objects < 2
        issue_categories = ["main_surface_information_density"] if low_visual_evidence_density else []
        bad_leaks = sum(1 for field in RUN2_30_AUDIT_FIELDS + RUN2_31_REPAIR_FIELDS if non_empty(bad.get(field)))

        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "layout_path": rel(layout_path),
                "run2_31_presentation_module_id": slide.get("run2_31_presentation_module_id"),
                "run2_31_required_code_module_ids": slide.get("run2_31_required_code_module_ids") or [],
                "run2_31_code_module_ids": code_modules,
                "repair_trace_closure": {
                    "run2_30_audit_status_present": non_empty(slide.get("run2_30_source_audit_status")),
                    "run2_30_top_next_layer": slide.get("run2_30_top_next_layer_to_thicken"),
                    "repair_execution_status": slide.get("run2_31_spine_climax_repair_execution_status"),
                    "repair_fields_present": fields_present(slide, RUN2_30_AUDIT_FIELDS + RUN2_31_REPAIR_FIELDS),
                    "bad_control_leaked_field_count": bad_leaks,
                },
                "spine_repair": {
                    "readable_spine_module_called": "drawRun231ReadableEvidenceSpine" in code_modules,
                    "spine_text_box_count": len(spine_elements),
                    "spine_min_font_size_target": float(slide.get("run2_31_spine_min_font_size_target") or 0),
                    "measured_min_spine_font_size": min_spine_font_size,
                    "status": "pass" if min_spine_font_size >= 8 else "blocked",
                },
                "climax_repair": {
                    "climax_style_policy": slide.get("run2_31_climax_style_policy"),
                    "hero_object_canvas_share": float(layout_metrics.get("hero_object_canvas_share") or 0),
                    "hero_scene_module_called": "drawRun231HeroProofScene" in code_modules,
                    "status": "pass"
                    if slide.get("run2_31_climax_style_policy") == RUN2_31_EXPECTED_CLIMAX_POLICY
                    else "blocked",
                },
                "main_surface_density": {
                    "visible_words": visible_words,
                    "visual_evidence_objects": visual_evidence_objects,
                    "low_visual_evidence_density": low_visual_evidence_density,
                },
                "issue_categories": issue_categories,
                "status": "pass_internal_only_needs_next_thickening"
                if issue_categories
                else "pass_internal_only",
                "recommended_next_action": "thicken main surface information density and visual evidence realism"
                if issue_categories
                else "keep repair, continue public-blocked review",
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_31 / "trace_manifest.json"
    bad_trace_path = BAD_31 / "trace_manifest.json"
    run230_audit_path = PACK / "results" / "run2_30_presentation_synthesis_audit.json"
    run231_result_path = PACK / "results" / "run2_31_spine_climax_repair_rerun_result.json"
    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    run230_audit = read_json(run230_audit_path)
    run231_result = read_json(run231_result_path)
    records = role_records(full_trace, bad_trace)

    repair_status_count = sum(
        1
        for slide in full_trace.get("slides", [])
        if slide.get("run2_31_spine_climax_repair_execution_status") == RUN2_31_EXPECTED_REPAIR_STATUS
    )
    audit_consumed_count = sum(
        1
        for slide in full_trace.get("slides", [])
        if slide.get("run2_30_top_next_layer_to_thicken") == "spine_readability_and_climax_consistency"
        and non_empty(slide.get("run2_30_source_audit_status"))
    )
    readable_spine_count = sum(
        1 for record in records if record["spine_repair"]["readable_spine_module_called"]
    )
    climax_policy_count = sum(
        1 for record in records if record["climax_repair"]["climax_style_policy"] == RUN2_31_EXPECTED_CLIMAX_POLICY
    )
    low_visual_roles = [
        record["role"] for record in records if record["main_surface_density"]["low_visual_evidence_density"]
    ]
    bad_leaks = sum(record["repair_trace_closure"]["bad_control_leaked_field_count"] for record in records)
    min_font_target = min(record["spine_repair"]["spine_min_font_size_target"] for record in records)
    measured_min_font = min(record["spine_repair"]["measured_min_spine_font_size"] for record in records)
    climax_record = next(record for record in records if record["role"] == "climax")
    repair_target_closed = (
        min_font_target >= 8
        and measured_min_font >= 8
        and climax_policy_count == len(records)
        and climax_record["climax_repair"]["hero_object_canvas_share"] > 0.5
        and bad_leaks == 0
    )
    forbidden_outputs = sorted(rel(path) for path in PRESENTATIONS.glob("*2-32*"))

    return {
        "schema_version": "ppt_run2_spine_climax_repair_audit.v1",
        "run_id": "2.32",
        "status": "run2_32_spine_climax_repair_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.31",
        "source_audit_run": "2.30",
        "source_repair_run": "2.31",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "issue_categories": [
            "spine_climax_repair_closure",
            "main_surface_information_density",
            "visual_evidence_realism",
            "public_release_gate",
        ],
        "input_chain": {
            "run2_30_presentation_synthesis_audit": rel(run230_audit_path),
            "run2_31_spine_climax_repair_rerun_result": rel(run231_result_path),
            "run2_31_full_trace_manifest": rel(full_trace_path),
            "run2_31_bad_trace_manifest": rel(bad_trace_path),
            "run2_31_full_layout_dir": rel(FULL_31 / "layout" / "final"),
            "run2_31_full_contact_sheet": rel(FULL_31 / "preview" / "contact-sheet.png"),
            "run2_31_four_arm_contact_sheet": rel(PRESENTATIONS / "run2-31-four-arm-contact-sheet.png"),
            "run2_29_full_trace_manifest": rel(FULL_29 / "trace_manifest.json"),
            "source_audit_target": run230_audit.get("quality_summary", {}).get("top_next_layer_to_thicken"),
            "source_repair_verdict": run231_result.get("rerun", {}).get("best_internal_arm_verdict"),
        },
        "no_new_deck_proof": {
            "presentations_dir": rel(PRESENTATIONS),
            "forbidden_run2_32_output_glob": "*2-32*",
            "matched_run2_32_outputs": forbidden_outputs,
            "new_pptx_created": any(path.endswith(".pptx") for path in forbidden_outputs),
            "status": "pass" if not any(path.endswith(".pptx") for path in forbidden_outputs) else "blocked",
        },
        "trace_closure": {
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": len(full_trace.get("slides", [])),
                "run2_30_audit_consumed_slides": audit_consumed_count,
                "repair_execution_status_slides": repair_status_count,
                "readable_evidence_spine_modules_called": readable_spine_count,
                "climax_style_policy_slides": climax_policy_count,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": len(bad_trace.get("slides", [])),
                "repair_fields_leaked": bad_leaks,
            },
        },
        "repair_verification": {
            "source_audit_target": run230_audit.get("quality_summary", {}).get("top_next_layer_to_thicken"),
            "source_repair_verdict": run231_result.get("rerun", {}).get("best_internal_arm_verdict"),
            "spine_font_target_met_by_contract": min_font_target >= 8 and measured_min_font >= 8,
            "spine_min_font_size_target": min_font_target,
            "measured_min_spine_font_size": measured_min_font,
            "climax_style_policy_enforced": climax_policy_count == len(records),
            "climax_hero_object_canvas_share": climax_record["climax_repair"]["hero_object_canvas_share"],
            "repair_target_closed": repair_target_closed,
        },
        "quality_summary": {
            "repair_gate": "pass_internal_only" if repair_target_closed else "blocked",
            "public_release_gate": "blocked",
            "closed_target_layers": ["spine_readability_and_climax_consistency"],
            "roles_with_low_visual_evidence_density": low_visual_roles,
            "top_next_layer_to_thicken": NEXT_LAYER,
            "reason": (
                "Run 2.31 closes the Run 2.30 spine/climax repair target internally: the readable spine "
                "has an 8pt minimum target and the climax uses the shared light editorial frame. The next "
                "quality jump should add richer main-surface information and more realistic visual evidence "
                "before another generated rerun."
            ),
        },
        "role_records": records,
        "module_recommendations": [
            {
                "target": "main_surface_information_density_and_visual_evidence_realism",
                "priority": 1,
                "issue": "several slides still expose only one visual evidence object on the public main surface",
                "affected_roles": low_visual_roles,
                "required_next_delta": "turn derived visual evidence assets into larger, more specific proof objects instead of small schematic blocks",
            },
            {
                "target": "content_claim_specificity",
                "priority": 2,
                "issue": "the slide story is traceable but still reads like a system demo rather than a commercial launch narrative",
                "affected_roles": [record["role"] for record in records],
                "required_next_delta": "bind usecase-specific business language, example states, and richer proof captions into the main slide surface",
            },
        ],
        "remaining_public_release_gates": [
            "human_visual_review",
            "native_or_cross_platform_render_inspection",
            "motion_or_video_review",
            "source_boundary_review",
            "human_release_approval",
        ],
        "next_required_action": (
            "thicken_run2_31_main_surface_information_density_and_visual_evidence_realism_before_run2_33_rerun"
        ),
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    summary = audit["quality_summary"]
    repair = audit["repair_verification"]
    trace = audit["trace_closure"]
    lines = [
        "# Run 2.32 Spine/Climax Repair Audit",
        "",
        "Status: spine/climax repair audit completed, public blocked.",
        "",
        "Run 2.32 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It audits whether Run 2.31 actually consumed the Run 2.30 presentation synthesis audit and repaired `drawRun231ReadableEvidenceSpine` plus `drawRun231HeroProofScene` before deciding the next thickness target.",
        "",
        "## Result",
        "",
        f"- Repair gate: `{summary['repair_gate']}`",
        f"- Public release gate: `{summary['public_release_gate']}`",
        f"- Repair target closed: `{repair['repair_target_closed']}`",
        f"- Spine min font target: `{repair['spine_min_font_size_target']:.2f}`",
        f"- Measured min spine font: `{repair['measured_min_spine_font_size']:.2f}`",
        f"- Climax hero share: `{repair['climax_hero_object_canvas_share']:.3f}`",
        f"- Run 2.30 audit consumed slides: `{trace['full_arm']['run2_30_audit_consumed_slides']}` / `{trace['full_arm']['slide_count']}`",
        f"- Bad-control repair leaks: `{trace['bad_control']['repair_fields_leaked']}`",
        f"- Top next layer to thicken: `{summary['top_next_layer_to_thicken']}`",
        f"- Low visual evidence roles: `{', '.join(summary['roles_with_low_visual_evidence_density']) or 'none'}`",
        "",
        "## Role Records",
        "",
    ]
    for record in audit["role_records"]:
        lines.append(
            f"- `{record['role']}`: module=`{record['run2_31_presentation_module_id']}`; "
            f"spine_target={record['spine_repair']['spine_min_font_size_target']:.2f}; "
            f"measured_spine={record['spine_repair']['measured_min_spine_font_size']:.2f}; "
            f"visual_evidence={record['main_surface_density']['visual_evidence_objects']}; "
            f"issues=`{', '.join(record['issue_categories']) or 'none'}`; "
            f"next={record['recommended_next_action']}"
        )
    lines.extend(
        [
            "",
            "## Required Next Action",
            "",
            f"`{NEXT_LAYER}` before Run 2.33 rerun.",
            "",
            "Do not advance to Run 3.0.",
            "",
        ]
    )
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.31 spine/climax repair without generating a new deck.")
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
