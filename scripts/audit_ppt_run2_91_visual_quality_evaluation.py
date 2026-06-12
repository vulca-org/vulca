from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_ppt_run_html_viewer import DEFAULT_THREAD_ID, build_data


PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / DEFAULT_THREAD_ID / "presentations"
RUN288_FULL = PRESENTATIONS / "ppt-run2-88-full-vulca"
RUN290_FULL = PRESENTATIONS / "ppt-run2-90-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_91_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_91_visual_quality_evaluation.md"

RUN288_RESULT = PACK / "results" / "run2_88_best_layout_visual_primitive_rerun_result.json"
RUN289_EVALUATION = PACK / "results" / "run2_89_visual_quality_evaluation.json"
RUN290_RESULT = PACK / "results" / "run2_90_renderer_asset_surface_composition_rerun_result.json"
RUN288_CONTACT_SHEET = RUN288_FULL / "preview" / "contact-sheet.png"
RUN290_CONTACT_SHEET = RUN290_FULL / "preview" / "contact-sheet.png"
RUN290_FOUR_ARM_SHEET = PRESENTATIONS / "run2-90-four-arm-contact-sheet.png"

ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
MODULE_BY_ROLE = {
    "cover": "product_reveal",
    "setup": "hero_field",
    "contrast": "before_after_theater",
    "proof": "evidence_workspace",
    "climax": "product_reveal",
    "close": "decision_map",
}

QUESTION_ANSWERS = {
    "is_2_90_better_than_2_88": {
        "answer": "yes_asset_surface_visibility_up_public_still_blocked",
        "basis": "2.90 fixes the major fill/surface visibility problem and gives the full arm real product-like planes, but it still reads as an internal design experiment.",
    },
    "did_2_90_fix_wireframe_surface_visibility": {
        "answer": "yes_major_wireframe_surface_reduction",
        "basis": "The Run 2.90 contact sheet shows layered UI surfaces and denser native PPT objects where 2.88 showed mostly outlines.",
    },
    "did_2_90_keep_text_heavy_readability": {
        "answer": "yes_readable_but_split_from_visuals",
        "basis": "Headline, subhead, and proof copy remain readable, but most copy still sits beside the product surface rather than inside the visual object.",
    },
    "did_2_90_integrate_text_with_visual_objects": {
        "answer": "no_text_visual_binding_still_weak",
        "basis": "The main text blocks and the product UI surfaces are parallel layers; captions and proof sentences are not yet embedded as object-bound typography.",
    },
    "does_2_90_reduce_debug_label_aesthetic": {
        "answer": "partial_labels_reduced_but_annotation_feel_remains",
        "basis": "Traceability labels stay off canvas and visible labels are limited, but the remaining captions still read as annotation tags in several slides.",
    },
    "does_2_90_reach_public_video_presentation_direction": {
        "answer": "no_public_blocked",
        "basis": "2.90 is a visible improvement but lacks public-ready text-object composition, editorial hierarchy, and final art direction.",
    },
    "which_layer_needs_next_repair": {
        "answer": "object_bound_typography_and_text_visual_integration",
        "basis": "The next renderer pass must bind headline/proof/caption into product objects, evidence cells, sticker stages, and decision nodes.",
    },
}

GEMINI_AGENT_REVIEW_SUMMARY = {
    "tool": "gemini-agent artifact-review",
    "model": "gemini-3.5-flash",
    "review_count": 1,
    "used_for_verdict": True,
    "capture_method": "contact_sheet_artifact_review_with_local_browser_confirmation",
    "comparison_artifacts": [
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-88-full-vulca/preview/contact-sheet.png"
        ),
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-90-full-vulca/preview/contact-sheet.png"
        ),
    ],
    "run2_90_findings": [
        "surface visibility is up",
        "asset surface materiality is now visible across the full arm",
        "wireframe compositions map abstract layout primitives to concrete interface components",
        "full arm separates from the bad asset-surface ablation",
        "slide 05 and the hero/product pages recover visible design density",
    ],
    "run2_90_risks": [
        "text-visual integration remains split",
        "thin wireframe lines occasionally intersect slide copy and compete with text legibility",
        "caption anchors still feel annotation-like",
        "proof copy is not yet embedded into evidence objects",
        "public audience may still read several pages as a system diagram rather than a finished presentation",
    ],
    "limitations": [
        "Review is based on static contact sheets, browser-visible previews, and renderer manifests, not motion, OCR, or public audience testing.",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "asset_surface_delta": "strong",
        "text_visual_integration": "partial",
        "caption_anchor_quality": "partial",
        "proof_embedding_quality": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "object_bound_typography",
        "visual_observation": "The product surface is now visible, but the headline and proof copy still sit beside the surface instead of driving a single reveal composition.",
        "next_repair_instruction": "Make the headline overlap or frame the hero surface and bind the proof sentence to a visible product state.",
    },
    "setup": {
        "asset_surface_delta": "partial",
        "text_visual_integration": "weak",
        "caption_anchor_quality": "partial",
        "proof_embedding_quality": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "text_visual_integration",
        "visual_observation": "The editorial field remains readable, but the product destination object is still a separate surface on the right.",
        "next_repair_instruction": "Turn the text block into an editorial spread whose captions and sidebars attach to the visible destination object.",
    },
    "contrast": {
        "asset_surface_delta": "strong",
        "text_visual_integration": "partial",
        "caption_anchor_quality": "partial",
        "proof_embedding_quality": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "caption_anchor_binding",
        "visual_observation": "The after-state surface has more materiality, but before/after copy still reads as labels around the stage.",
        "next_repair_instruction": "Embed the before and after claims into the two product states rather than keeping them as external annotations.",
    },
    "proof": {
        "asset_surface_delta": "partial",
        "text_visual_integration": "weak",
        "caption_anchor_quality": "weak",
        "proof_embedding_quality": "weak",
        "public_video_direction": "no",
        "root_cause_layer": "proof_object_embedding",
        "visual_observation": "The evidence workspace is more visible, but the proof sentence is still outside the matrix instead of becoming the dominant evidence cell.",
        "next_repair_instruction": "Put the proof sentence into a dominant evidence cell and bind support captions to cell geometry.",
    },
    "climax": {
        "asset_surface_delta": "strong",
        "text_visual_integration": "partial",
        "caption_anchor_quality": "partial",
        "proof_embedding_quality": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "composition_rhythm",
        "visual_observation": "The sticker stage now has visible overlap and density, but stickers still work as callouts rather than a single payoff sequence.",
        "next_repair_instruction": "Make the badges, deck surface, and proof copy form one staged reveal path.",
    },
    "close": {
        "asset_surface_delta": "partial",
        "text_visual_integration": "weak",
        "caption_anchor_quality": "partial",
        "proof_embedding_quality": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "object_bound_typography",
        "visual_observation": "The close has a product surface and decision path, but decision text still floats around the board.",
        "next_repair_instruction": "Move decision text into board nodes and make the blocked-public outcome the dominant visual object.",
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.91 visual evaluation missing required {label}: {path}")


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


def validate_inputs(run288: dict[str, Any], run289: dict[str, Any], run290: dict[str, Any]) -> None:
    if run288.get("status") != "run2_88_best_layout_visual_primitive_rerun_generated_public_blocked":
        raise ValueError("Run 2.91 evaluation expected Run 2.88 renderer result")
    if run289.get("status") != "run2_89_visual_quality_evaluation_public_blocked":
        raise ValueError("Run 2.91 evaluation expected Run 2.89 visual quality evaluation")
    if run289.get("next_required_action") != "part_u_renderer_asset_surface_composition_repair_from_t_evaluation":
        raise ValueError("Run 2.91 evaluation expected Part T to request Part U")
    if run290.get("status") != "run2_90_renderer_asset_surface_composition_rerun_generated_public_blocked":
        raise ValueError("Run 2.91 evaluation expected Run 2.90 renderer result")
    if run290.get("next_required_action") != "part_v_visual_quality_evaluation_for_run2_90":
        raise ValueError("Run 2.91 evaluation expected Run 2.90 to hand off to Part V")

    for label, data in [("Run 2.88", run288), ("Run 2.90", run290)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.91 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.91 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run288 = next((run for run in runs if run.get("id") == "2.88"), {})
    run290 = next((run for run in runs if run.get("id") == "2.90"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_88_and_2_90": {"2.88", "2.90"} <= run_ids,
        "run2_88_full_preview_count": len((run288.get("fullArm") or {}).get("slides") or []),
        "run2_90_full_preview_count": len((run290.get("fullArm") or {}).get("slides") or []),
        "run2_90_arm_count": len(run290.get("arms") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": "Part V records current viewer closure. Browser verification must confirm latest 2.90 and visible 2.88/2.90 comparison after this artifact is written.",
    }


def role_assessments(run290: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run290.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "asset_surface_delta": judgment["asset_surface_delta"],
                "text_visual_integration": judgment["text_visual_integration"],
                "caption_anchor_quality": judgment["caption_anchor_quality"],
                "proof_embedding_quality": judgment["proof_embedding_quality"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "next_repair_instruction": judgment["next_repair_instruction"],
                "trace_support": {
                    "asset_surface_composition_id": str(page.get("asset_surface_composition_id") or ""),
                    "renderer_function_name": str(page.get("renderer_function_name") or ""),
                    "asset_surface_rendered": bool(page.get("asset_surface_rendered")),
                    "composition_detail_added": bool(page.get("composition_detail_added")),
                    "traceability_on_canvas": bool(page.get("traceability_on_canvas")),
                    "label_count": int(page.get("label_count") or 0),
                    "surface_detail_count": int(page.get("surface_detail_count") or 0),
                },
            }
        )
    return records


def no_new_renderer_proof() -> dict[str, Any]:
    return {
        "new_pptx_created": False,
        "new_html_created": False,
        "starts_renderer_rerun": False,
        "status": "pass",
    }


def build_audit(run288: dict[str, Any], run289: dict[str, Any], run290: dict[str, Any]) -> dict[str, Any]:
    validate_inputs(run288, run289, run290)
    for path, label in [
        (RUN288_CONTACT_SHEET, "Run 2.88 full contact sheet"),
        (RUN290_CONTACT_SHEET, "Run 2.90 full contact sheet"),
        (RUN290_FOUR_ARM_SHEET, "Run 2.90 four-arm contact sheet"),
    ]:
        require_file(path, label)

    return {
        "artifact_id": "run2_91_visual_quality_evaluation",
        "part": "Part V",
        "schema_version": "ppt_run2_91_visual_quality_evaluation.v1",
        "run_id": "2.91",
        "status": "run2_91_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_part_u_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_v_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.88",
            "evaluated_run": "2.90",
            "repair_source_run": "2.89",
            "prior_reference_run": "2.85",
        },
        "input_chain": {
            "run2_90_result": rel(RUN290_RESULT),
            "run2_89_t_evaluation": rel(RUN289_EVALUATION),
            "run2_88_result": rel(RUN288_RESULT),
            "run2_88_full_contact_sheet": rel(RUN288_CONTACT_SHEET),
            "run2_90_full_contact_sheet": rel(RUN290_CONTACT_SHEET),
            "run2_90_four_arm_contact_sheet": rel(RUN290_FOUR_ARM_SHEET),
            "ppt_run_viewer": rel(PRESENTATIONS / "ppt-run-viewer.html"),
        },
        "viewer_comparison_closure": viewer_closure(),
        "gemini_agent_review_summary": GEMINI_AGENT_REVIEW_SUMMARY,
        "evaluation_questions": QUESTION_ANSWERS,
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_88": "asset_surface_visibility_up_text_visual_integration_still_split",
            "top_blocker": "text_blocks_and_product_surfaces_remain_parallel_not_integrated",
            "next_layer_to_fix": "object_bound_typography_and_text_visual_integration",
        },
        "role_assessments": role_assessments(run290),
        "root_cause_summary": {
            "primary_layer": "object_bound_typography_and_text_visual_integration",
            "secondary_layers": ["text_visual_integration", "caption_anchor_binding", "proof_object_embedding"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": "surface_layer_fixed_before_text_visual_binding_layer",
            "rationale": (
                "2.90 repaired surface visibility, but text and visual systems still behave as parallel layers "
                "rather than one object-bound presentation composition."
            ),
        },
        "no_new_renderer_proof": no_new_renderer_proof(),
        "next_required_action": "part_w_renderer_text_visual_binding_repair_from_v_evaluation",
    }


def build_markdown(audit: dict[str, Any]) -> str:
    assessment = audit["visual_quality_assessment"]
    return "\n".join(
        [
            "# Run 2.91 Visual Quality Evaluation",
            "",
            f"Status: {audit['status']}",
            "",
            "Comparison: 2.90 vs 2.88",
            "",
            "Verdict: asset surface visibility improved, but text-visual integration remains blocked.",
            "",
            "Key finding: text and visual systems still behave as parallel layers; captions, proof sentences, and headline blocks are not yet object-bound typography.",
            "",
            f"Design quality gate: {assessment['design_quality_gate']}",
            f"Global delta: {assessment['global_delta_vs_2_88']}",
            f"Top blocker: {assessment['top_blocker']}",
            "",
            "Role-level repair focus:",
            *[
                f"- {record['role']}: {record['root_cause_layer']} -> {record['next_repair_instruction']}"
                for record in audit["role_assessments"]
            ],
            "",
            "Boundary: public blocked. Part V does not create a new PPT, rerun renderer, or update the HTML viewer.",
            "",
            f"Next required action: {audit['next_required_action']} (Part W)",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.90 visual quality after Part U.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run288 = read_json(RUN288_RESULT)
    run289 = read_json(RUN289_EVALUATION)
    run290 = read_json(RUN290_RESULT)
    audit = build_audit(run288, run289, run290)
    write_json(args.result_json, audit)
    args.result_md.parent.mkdir(parents=True, exist_ok=True)
    args.result_md.write_text(build_markdown(audit), encoding="utf-8")
    print(audit["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
