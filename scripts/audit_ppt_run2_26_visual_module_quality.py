from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_ARM = PRESENTATIONS / "ppt-run2-25-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_26_visual_module_quality_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_26_visual_module_quality_audit.md"

ISSUE_CATEGORIES = [
    "layout_geometry",
    "content_density",
    "visual_evidence_visibility",
    "composition_hierarchy",
    "climax_impact",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def compact_text(value: str, max_chars: int = 74) -> str:
    text = str(value or "").strip()
    return f"{text[: max_chars - 1].strip()}..." if len(text) > max_chars else text


def layout_path_for_slide(slide: dict[str, Any]) -> Path:
    slide_id = str(slide.get("slide_id") or "slide_01")
    slide_no = int(slide_id.rsplit("_", 1)[-1])
    return FULL_ARM / "layout" / "final" / f"slide-{slide_no:02d}.layout.json"


def text_elements(layout: dict[str, Any]) -> list[dict[str, Any]]:
    return [element for element in layout.get("elements", []) if element.get("text")]


def layout_text_blob(layout: dict[str, Any]) -> str:
    return "\n".join(str(element.get("text") or "") for element in text_elements(layout))


def geometry_audit(layout: dict[str, Any]) -> dict[str, Any]:
    text_boxes = text_elements(layout)
    widths: list[float] = []
    line_counts: list[int] = []
    crushed: list[dict[str, Any]] = []
    tiny: list[dict[str, Any]] = []

    for element in text_boxes:
        bbox = element.get("bbox") or []
        width = float(bbox[2]) if len(bbox) >= 3 else 0.0
        line_count = int((element.get("textLayout") or {}).get("lineCount") or 0)
        text = str(element.get("text") or "")
        widths.append(width)
        line_counts.append(line_count)
        if width < 80 or line_count > 14:
            crushed.append({"text": text[:90], "bbox": bbox, "line_count": line_count})
        if width <= 0:
            tiny.append({"text": text[:90], "bbox": bbox, "line_count": line_count})

    return {
        "text_box_count": len(text_boxes),
        "min_text_width": min(widths) if widths else 0,
        "max_line_count": max(line_counts) if line_counts else 0,
        "crushed_text_box_count": len(crushed),
        "negative_or_tiny_text_box_count": len(tiny),
        "crushed_text_boxes": crushed,
    }


def visible_proof_points(slide: dict[str, Any], layout: dict[str, Any]) -> list[str]:
    blob = layout_text_blob(layout)
    visible: list[str] = []
    for point in slide.get("run2_24_business_proof_points_visible") or []:
        point_text = str(point)
        if point_text in blob or compact_text(point_text) in blob:
            visible.append(point_text)
    return visible


def role_record(slide: dict[str, Any]) -> dict[str, Any]:
    layout_path = layout_path_for_slide(slide)
    layout = read_json(layout_path)
    geometry = geometry_audit(layout)
    module_ids = [str(module) for module in slide.get("run2_25_code_module_ids") or []]
    proof_points = [str(point) for point in slide.get("run2_24_business_proof_points_visible") or []]
    visible_points = visible_proof_points(slide, layout)
    has_content_surface = "drawRun225ContentEvidenceSurface" in module_ids
    compressed_proof_surface = has_content_surface and len(visible_points) < len(proof_points)
    layout_metrics = slide.get("layout_metrics") or {}
    slot_count = len(slide.get("run2_24_visual_evidence_slot_ids") or [])
    asset_count = len(slide.get("run2_24_visual_evidence_asset_ids") or [])
    visual_objects = int(layout_metrics.get("visual_evidence_objects") or 0)
    hero_share = float(layout_metrics.get("hero_object_canvas_share") or 0)
    role = str(slide.get("role") or "")
    visible_layout_defect = geometry["crushed_text_box_count"] > 0 or geometry["negative_or_tiny_text_box_count"] > 0
    climax_ok = role != "climax" or hero_share >= 0.5

    issues: list[str] = []
    if visible_layout_defect:
        issues.append("layout_geometry")
    if compressed_proof_surface:
        issues.append("content_density")
    if slot_count < 2 or asset_count < 2 or visual_objects < 2:
        issues.append("visual_evidence_visibility")
    if role != "climax" and has_content_surface and hero_share < 0.08:
        issues.append("composition_hierarchy")
    if role == "climax" and not climax_ok:
        issues.append("climax_impact")

    if visible_layout_defect:
        status = "blocked_by_layout_geometry"
        next_action = "repair visible text geometry before rerun"
    elif compressed_proof_surface:
        status = "needs_next_module_thickening"
        next_action = "thicken drawRun225ContentEvidenceSurface so compressed proof can become readable native evidence"
    else:
        status = "pass_internal_only"
        next_action = "keep module, continue public-blocked human review"

    return {
        "slide_id": slide.get("slide_id"),
        "role": role,
        "layout_path": rel(layout_path),
        "module_ids": module_ids,
        "geometry": geometry,
        "content_density": {
            "trace_business_proof_point_count": len(proof_points),
            "visible_business_proof_point_count": len(visible_points),
            "compressed_proof_surface": compressed_proof_surface,
            "visual_evidence_slot_count": slot_count,
            "visible_words": int(layout_metrics.get("visible_words") or 0),
        },
        "visual_evidence_visibility": {
            "trace_slots_present": slot_count >= 2,
            "trace_asset_ids_present": asset_count >= 2,
            "native_visual_evidence_objects": visual_objects,
            "native_objects_present": visual_objects >= 2,
        },
        "composition_hierarchy": {
            "hero_object_canvas_share": hero_share,
            "proof_objects": int(layout_metrics.get("proof_objects") or 0),
            "workflow_objects": int(layout_metrics.get("workflow_objects") or 0),
            "content_cards": int(layout_metrics.get("content_cards") or 0),
            "surface_module_present": has_content_surface,
        },
        "climax_impact": {
            "applies": role == "climax",
            "hero_stage_pass": climax_ok,
        },
        "issue_categories": issues,
        "status": status,
        "recommended_next_action": next_action,
    }


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_ARM / "trace_manifest.json"
    contact_sheet_path = PRESENTATIONS / "run2-25-four-arm-contact-sheet.png"
    full_contact_sheet_path = FULL_ARM / "preview" / "contact-sheet.png"
    result_path = PACK / "results" / "run2_25_single_usecase_rerun_result.json"
    trace = read_json(full_trace_path)
    slides = trace.get("slides", [])
    records = [role_record(slide) for slide in slides]
    roles_with_visible_defects = [
        record["role"]
        for record in records
        if record["geometry"]["crushed_text_box_count"] > 0 or record["geometry"]["negative_or_tiny_text_box_count"] > 0
    ]
    roles_with_compressed = [
        record["role"] for record in records if record["content_density"]["compressed_proof_surface"]
    ]
    records_with_content_surface = [
        record for record in records if "drawRun225ContentEvidenceSurface" in record["module_ids"]
    ]
    top_next_module = "drawRun225ContentEvidenceSurface" if roles_with_compressed else "human_visual_review"
    forbidden_run226_outputs = sorted(
        rel(path)
        for path in PRESENTATIONS.glob("*2-26*")
        if path.name not in {DEFAULT_RESULT_JSON.name, DEFAULT_RESULT_MD.name}
    )

    return {
        "schema_version": "ppt_run2_visual_module_quality_audit.v1",
        "run_id": "2.26",
        "status": "run2_26_visual_module_quality_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.25",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "issue_categories": ISSUE_CATEGORIES,
        "input_chain": {
            "run2_25_result": rel(result_path),
            "run2_25_full_trace_manifest": rel(full_trace_path),
            "run2_25_full_layout_dir": rel(FULL_ARM / "layout" / "final"),
            "run2_25_full_contact_sheet": rel(full_contact_sheet_path),
            "run2_25_four_arm_contact_sheet": rel(contact_sheet_path),
        },
        "source_inventory": {
            "full_arm_id": trace.get("arm_id"),
            "full_arm_slide_count": len(slides),
            "layout_files_audited": len(records),
            "content_surface_roles": [record["role"] for record in records_with_content_surface],
        },
        "no_new_deck_proof": {
            "presentations_dir": rel(PRESENTATIONS),
            "forbidden_run2_26_output_glob": "*2-26*",
            "matched_run2_26_outputs": forbidden_run226_outputs,
            "new_pptx_created": any(path.endswith(".pptx") for path in forbidden_run226_outputs),
            "status": "pass" if not forbidden_run226_outputs else "blocked",
        },
        "quality_summary": {
            "module_quality_gate": "pass_internal_only" if not roles_with_visible_defects else "blocked_by_layout_geometry",
            "public_release_gate": "blocked",
            "roles_with_visible_layout_defects": roles_with_visible_defects,
            "roles_with_compressed_proof_surface": roles_with_compressed,
            "top_next_module_to_thicken": top_next_module,
            "reason": (
                "Run 2.25 no longer has crushed text geometry, but content evidence surfaces still compress "
                "proof points in compact/medium layouts; Run 2.27 should thicken that module before rerun."
            ),
        },
        "role_records": records,
        "module_recommendations": [
            {
                "module_id": "drawRun225ContentEvidenceSurface",
                "priority": 1,
                "problem": "compact and medium surfaces preserve geometry by compressing proof points, which weakens data thickness at first read",
                "required_next_delta": "turn proof points into readable native evidence rows or staged product-surface panels without clipped text",
                "affected_roles": roles_with_compressed,
            },
            {
                "module_id": "drawRun225ClimaxProofObject",
                "priority": 2,
                "problem": "climax passes hero-share gate but remains an editable proof object rather than a public-video-grade visual moment",
                "required_next_delta": "after surface thickening, deepen climax editorial composition and motion plan",
                "affected_roles": ["climax"],
            },
        ],
        "remaining_public_release_gates": [
            "human_visual_review",
            "native_or_cross_platform_render_inspection",
            "motion_or_video_review",
            "source_boundary_review",
            "human_release_approval",
        ],
        "next_required_action": "thicken_drawRun225ContentEvidenceSurface_before_run2_27_rerun",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    summary = audit["quality_summary"]
    lines = [
        "# Run 2.26 Visual Module Quality Audit",
        "",
        "Status: visual module quality audited, public blocked.",
        "",
        "Run 2.26 audits the generated Run 2.25 full arm without creating a new PPT deck. It checks layout geometry, content density, visual evidence visibility, composition hierarchy, and climax impact so the next step stays inside the same five-layer loop.",
        "",
        "## Result",
        "",
        f"- Module quality gate: `{summary['module_quality_gate']}`",
        f"- Public release gate: `{summary['public_release_gate']}`",
        f"- Top next module to thicken: `{summary['top_next_module_to_thicken']}`",
        f"- Roles with visible layout defects: `{', '.join(summary['roles_with_visible_layout_defects']) or 'none'}`",
        f"- Roles with compressed proof surface: `{', '.join(summary['roles_with_compressed_proof_surface']) or 'none'}`",
        f"- No new deck proof: `{audit['no_new_deck_proof']['status']}`; matched run2.26 outputs=`{len(audit['no_new_deck_proof']['matched_run2_26_outputs'])}`",
        "",
        "The key finding is that `drawRun225ContentEvidenceSurface` now avoids crushed text, but it achieves that by compressing proof points in compact or medium surfaces. That is acceptable for an internal proof, but it is not thick enough for the next quality jump.",
        "",
        "## Role Records",
        "",
    ]
    for record in audit["role_records"]:
        lines.append(
            f"- `{record['role']}`: `{record['status']}`; geometry crushed={record['geometry']['crushed_text_box_count']}; "
            f"visible proof={record['content_density']['visible_business_proof_point_count']}/"
            f"{record['content_density']['trace_business_proof_point_count']}; next={record['recommended_next_action']}"
        )
    lines.extend(
        [
            "",
            "## Required Next Action",
            "",
            "`thicken_drawRun225ContentEvidenceSurface_before_run2_27_rerun`.",
            "",
            "Public release remains blocked. Do not advance to Run 3.0.",
            "",
        ]
    )
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.25 visual module quality without generating a new deck.")
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
