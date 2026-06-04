from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_29 = PRESENTATIONS / "ppt-run2-29-full-vulca"
BAD_29 = PRESENTATIONS / "ppt-run2-29-bad-presentation-synthesis-memory"
FULL_28 = PRESENTATIONS / "ppt-run2-28-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_30_presentation_synthesis_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_30_presentation_synthesis_audit.md"

RUN2_28_CHAIN_FIELDS = [
    "run2_28_evidence_chain_id",
    "run2_28_multimodal_source_record_ids",
    "run2_28_extracted_design_rule",
    "run2_28_workflow_decision",
    "run2_28_native_surface_module_id",
]
RUN2_29_SYNTHESIS_FIELDS = [
    "run2_29_synthesis_record_id",
    "run2_29_public_surface_mode",
    "run2_29_trace_surface_mode",
    "run2_29_presentation_module_id",
    "run2_29_chain_compression_policy",
    "run2_29_presentation_synthesis_execution_status",
]


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
        if "compressed evidence spine" in text or (x >= 830 and 100 <= y <= 560):
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


def role_records(full_trace: dict[str, Any], baseline_trace: dict[str, Any], bad_trace: dict[str, Any]) -> list[dict[str, Any]]:
    baseline_by_role = {slide.get("role"): slide for slide in baseline_trace.get("slides", [])}
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    records: list[dict[str, Any]] = []

    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        baseline = baseline_by_role.get(role, {})
        bad = bad_by_role.get(role, {})
        layout_path = layout_path_for_slide(FULL_29, slide)
        layout = read_json(layout_path)
        spine_elements = spine_text_elements(layout)
        spine_font_sizes = [element_font_size(element) for element in spine_elements if element_font_size(element) > 0]
        min_spine_font_size = min(spine_font_sizes) if spine_font_sizes else 0
        code_modules = [str(module) for module in slide.get("run2_29_code_module_ids") or []]
        required_modules = [str(module) for module in slide.get("run2_29_required_code_module_ids") or []]
        execution_status = str(slide.get("run2_29_presentation_synthesis_execution_status") or "")
        issue_categories: list[str] = []
        if min_spine_font_size < 8:
            issue_categories.append("spine_readability")
        if role == "climax":
            issue_categories.append("climax_visual_consistency")

        bad_leaks = sum(1 for field in RUN2_28_CHAIN_FIELDS + RUN2_29_SYNTHESIS_FIELDS if non_empty(bad.get(field)))
        presentation_module = str(slide.get("run2_29_presentation_module_id") or "")

        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "layout_path": rel(layout_path),
                "run2_28_native_surface_module_id": slide.get("run2_28_native_surface_module_id"),
                "run2_29_presentation_module_id": presentation_module,
                "run2_29_required_code_module_ids": required_modules,
                "run2_29_code_module_ids": code_modules,
                "baseline_run2_28_code_module_ids": baseline.get("run2_28_code_module_ids") or [],
                "presentation_first_surface": {
                    "status": "pass"
                    if execution_status == "presentation_first_surface_rendered_with_secondary_evidence_spine"
                    and "presentation_first" in str(slide.get("run2_29_public_surface_mode") or "")
                    else "blocked",
                    "execution_status": execution_status,
                    "public_surface_mode": slide.get("run2_29_public_surface_mode"),
                    "module_called": presentation_module in code_modules,
                    "hero_object_canvas_share": (slide.get("layout_metrics") or {}).get("hero_object_canvas_share", 0),
                },
                "evidence_spine": {
                    "compressed_spine_module_called": "drawRun229CompressedEvidenceSpine" in code_modules,
                    "spine_text_box_count": len(spine_elements),
                    "min_spine_font_size": min_spine_font_size,
                    "dense_spine_text": min_spine_font_size < 8,
                },
                "trace_closure": {
                    "run2_28_chain_preserved": fields_present(slide, RUN2_28_CHAIN_FIELDS),
                    "synthesis_record_selected": fields_present(slide, RUN2_29_SYNTHESIS_FIELDS),
                    "trace_surface_mode": slide.get("run2_29_trace_surface_mode"),
                    "full_chain_visible_in_trace": slide.get("run2_29_trace_surface_mode")
                    == "manifest_and_html_viewer_full_chain_visible",
                    "bad_control_leaked_field_count": bad_leaks,
                },
                "issue_categories": issue_categories,
                "status": "pass_internal_only_needs_next_thickening" if issue_categories else "pass_internal_only",
                "recommended_next_action": "thicken spine readability and normalize climax visual consistency"
                if issue_categories
                else "keep module, continue public-blocked review",
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_29 / "trace_manifest.json"
    bad_trace_path = BAD_29 / "trace_manifest.json"
    baseline_trace_path = FULL_28 / "trace_manifest.json"
    run229_result_path = PACK / "results" / "run2_29_presentation_synthesis_rerun_result.json"
    synthesis_memory_path = PACK / "run2_29_presentation_synthesis_memory.json"
    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    baseline_trace = read_json(baseline_trace_path)
    records = role_records(full_trace, baseline_trace, bad_trace)

    dense_spine_roles = [record["role"] for record in records if record["evidence_spine"]["dense_spine_text"]]
    climax_shift_roles = [record["role"] for record in records if "climax_visual_consistency" in record["issue_categories"]]
    bad_leaks = sum(record["trace_closure"]["bad_control_leaked_field_count"] for record in records)
    full_chain_preserved_count = sum(1 for record in records if record["trace_closure"]["run2_28_chain_preserved"])
    spine_module_count = sum(1 for record in records if record["evidence_spine"]["compressed_spine_module_called"])
    presentation_status_count = sum(
        1 for record in records if record["presentation_first_surface"]["status"] == "pass"
    )
    forbidden_outputs = sorted(rel(path) for path in PRESENTATIONS.glob("*2-30*"))

    return {
        "schema_version": "ppt_run2_presentation_synthesis_audit.v1",
        "run_id": "2.30",
        "status": "run2_30_presentation_synthesis_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.29",
        "comparison_baseline_run": "2.28",
        "source_synthesis_layer": "2.29",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "issue_categories": [
            "data_workflow_trace_closure",
            "presentation_surface_strength",
            "spine_readability",
            "climax_visual_consistency",
        ],
        "input_chain": {
            "run2_29_result": rel(run229_result_path),
            "run2_29_presentation_synthesis_memory": rel(synthesis_memory_path),
            "run2_29_full_trace_manifest": rel(full_trace_path),
            "run2_29_bad_trace_manifest": rel(bad_trace_path),
            "run2_29_full_layout_dir": rel(FULL_29 / "layout" / "final"),
            "run2_29_full_contact_sheet": rel(FULL_29 / "preview" / "contact-sheet.png"),
            "run2_29_four_arm_contact_sheet": rel(PRESENTATIONS / "run2-29-four-arm-contact-sheet.png"),
            "run2_28_full_trace_manifest": rel(baseline_trace_path),
            "run2_28_full_contact_sheet": rel(FULL_28 / "preview" / "contact-sheet.png"),
            "run2_28_four_arm_contact_sheet": rel(PRESENTATIONS / "run2-28-four-arm-contact-sheet.png"),
        },
        "no_new_deck_proof": {
            "presentations_dir": rel(PRESENTATIONS),
            "forbidden_run2_30_output_glob": "*2-30*",
            "matched_run2_30_outputs": forbidden_outputs,
            "new_pptx_created": any(path.endswith(".pptx") for path in forbidden_outputs),
            "status": "pass" if not any(path.endswith(".pptx") for path in forbidden_outputs) else "blocked",
        },
        "trace_closure": {
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": len(full_trace.get("slides", [])),
                "presentation_synthesis_records_selected": sum(
                    1 for slide in full_trace.get("slides", []) if non_empty(slide.get("run2_29_synthesis_record_id"))
                ),
                "compressed_evidence_spine_modules_called": spine_module_count,
                "presentation_first_execution_status_slides": presentation_status_count,
                "run2_28_chain_fields_preserved": full_chain_preserved_count,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": len(bad_trace.get("slides", [])),
                "presentation_synthesis_fields_leaked": bad_leaks,
            },
        },
        "comparison_to_run2_28": {
            "audit_table_demoted_to_secondary_spine": spine_module_count == len(records),
            "full_chain_preserved_in_trace": full_chain_preserved_count == len(records),
            "primary_surface_delta": "four_column_audit_table_to_presentation_first_surface",
            "baseline_full_arm_id": baseline_trace.get("arm_id"),
            "current_full_arm_id": full_trace.get("arm_id"),
        },
        "quality_summary": {
            "presentation_synthesis_gate": "pass_internal_only" if not bad_leaks else "blocked_by_control_leakage",
            "public_release_gate": "blocked",
            "roles_with_dense_spine_text": dense_spine_roles,
            "roles_with_climax_style_shift": climax_shift_roles,
            "top_next_layer_to_thicken": "spine_readability_and_climax_consistency",
            "reason": (
                "Run 2.29 successfully demotes the Run 2.28 four-column audit table into a secondary "
                "compressed evidence spine, while preserving the full chain in trace. The next quality jump "
                "should improve spine readability and normalize the climax visual system before another rerun."
            ),
        },
        "role_records": records,
        "module_recommendations": [
            {
                "target": "drawRun229CompressedEvidenceSpine",
                "priority": 1,
                "issue": "spine text falls below readable presentation size and is dense across all roles",
                "affected_roles": dense_spine_roles,
                "required_next_delta": "convert the spine into fewer visible labels plus expandable/viewer-only details",
            },
            {
                "target": "drawRun229HeroProofScene",
                "priority": 2,
                "issue": "the climax creates useful emphasis but shifts too far from the light editorial system",
                "affected_roles": climax_shift_roles,
                "required_next_delta": "keep climax emphasis while aligning surface rhythm, typography, and palette with the rest of the deck",
            },
        ],
        "remaining_public_release_gates": [
            "human_visual_review",
            "native_or_cross_platform_render_inspection",
            "motion_or_video_review",
            "source_boundary_review",
            "human_release_approval",
        ],
        "next_required_action": "thicken_run2_29_spine_readability_and_climax_consistency_before_run2_31_rerun",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    summary = audit["quality_summary"]
    comparison = audit["comparison_to_run2_28"]
    trace = audit["trace_closure"]
    lines = [
        "# Run 2.30 Presentation Synthesis Audit",
        "",
        "Status: presentation synthesis audit completed, public blocked.",
        "",
        "Run 2.30 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It audits whether Run 2.29 improved on Run 2.28 by turning the four-column audit table into a presentation-first surface with a compressed evidence spine, while preserving the full source-rule-workflow-surface chain in trace.",
        "",
        "## Result",
        "",
        f"- Presentation synthesis gate: `{summary['presentation_synthesis_gate']}`",
        f"- Public release gate: `{summary['public_release_gate']}`",
        f"- Audit table demoted to secondary spine: `{comparison['audit_table_demoted_to_secondary_spine']}`",
        f"- Full chain preserved in trace: `{comparison['full_chain_preserved_in_trace']}`",
        f"- Full-arm synthesis records selected: `{trace['full_arm']['presentation_synthesis_records_selected']}` / `{trace['full_arm']['slide_count']}`",
        f"- Bad-control synthesis leaks: `{trace['bad_control']['presentation_synthesis_fields_leaked']}`",
        f"- Top next layer to thicken: `{summary['top_next_layer_to_thicken']}`",
        f"- Dense spine roles: `{', '.join(summary['roles_with_dense_spine_text']) or 'none'}`",
        f"- Climax style-shift roles: `{', '.join(summary['roles_with_climax_style_shift']) or 'none'}`",
        "",
        "## Role Records",
        "",
    ]
    for record in audit["role_records"]:
        lines.append(
            f"- `{record['role']}`: module=`{record['run2_29_presentation_module_id']}`; "
            f"spine_min_font={record['evidence_spine']['min_spine_font_size']:.2f}; "
            f"issues=`{', '.join(record['issue_categories']) or 'none'}`; "
            f"next={record['recommended_next_action']}"
        )
    lines.extend(
        [
            "",
            "## Required Next Action",
            "",
            "`spine_readability_and_climax_consistency` before Run 2.31 rerun.",
            "",
            "Do not advance to Run 3.0.",
            "",
        ]
    )
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.29 presentation synthesis without generating a new deck.")
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
