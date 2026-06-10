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
RUN277_FULL = PRESENTATIONS / "ppt-run2-77-full-vulca"
RUN279_FULL = PRESENTATIONS / "ppt-run2-79-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_80_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_80_visual_quality_evaluation.md"

RUN277_RESULT = PACK / "results" / "run2_77_visual_grammar_renderer_repair_rerun_result.json"
RUN278_L_EVALUATION = PACK / "results" / "run2_78_visual_quality_evaluation.json"
RUN279_RESULT = PACK / "results" / "run2_79_renderer_art_direction_repair_rerun_result.json"
RUN277_CONTACT_SHEET = RUN277_FULL / "preview" / "contact-sheet.png"
RUN279_CONTACT_SHEET = RUN279_FULL / "preview" / "contact-sheet.png"

ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
MODULE_BY_ROLE = {
    "cover": "product_reveal",
    "setup": "hero_field",
    "contrast": "before_after_theater",
    "proof": "evidence_workspace",
    "climax": "product_reveal",
    "close": "decision_map",
}

QUESTION_IDS = [
    "is_2_79_better_than_2_77",
    "did_2_79_reduce_wireframe_and_annotation",
    "did_2_79_fix_small_label_problem",
    "did_2_79_create_concrete_product_surface",
    "does_2_79_reach_public_video_presentation_direction",
    "which_layer_needs_next_repair",
]

GEMINI_AGENT_REVIEW_SUMMARY = {
    "tool": "mcp__gemini_agent.gemini_artifact_review",
    "model": "gemini-3.5-flash",
    "review_count": 1,
    "used_for_verdict": True,
    "capture_method": "live_gemini_agent_artifact_review",
    "comparison_artifacts": [
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-77-full-vulca/preview/contact-sheet.png"
        ),
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-79-full-vulca/preview/contact-sheet.png"
        ),
    ],
    "reviewed_artifacts": [
        {
            "run_id": "2.79",
            "file": (
                "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
                "ppt-run2-79-full-vulca/preview/contact-sheet.png"
            ),
            "key_findings": [
                "ultra_minimalist_layout",
                "sparse_text_wireframe",
                "debug_annotations_removed",
                "concrete_product_surface_not_visible",
            ],
            "risks": [
                "product_surface_absent",
                "small_labels_remain",
                "public_audience_may_read_it_as_structural_wireframe",
            ],
        }
    ],
    "run2_79_findings": [
        "ultra minimalist layout",
        "debug annotations are reduced",
        "sparse text wireframe remains dominant",
        "concrete product surface is not visibly realized",
    ],
    "run2_79_risks": [
        "product surface absent",
        "small labels remain scattered",
        "lack of actual UI mockups weakens public presentation read",
    ],
    "limitations": [
        "Review is based on the static 2.79 full-arm contact sheet; no motion, OCR, or audience testing was performed.",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "delta_vs_2_77": "partial",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "product_surface_realization": "absent",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The red/debug annotation feel is gone, but the hero crop does not render as a visible product object; "
            "it reads as headline plus scattered labels."
        ),
        "next_repair_instruction": (
            "Render the opening hero as a concrete product surface or cropped editable PPT object, then attach only "
            "one readable public-facing label."
        ),
    },
    "setup": {
        "delta_vs_2_77": "partial",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "product_surface_realization": "absent",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The route labels are more audience-readable than M metadata, but the transformation field has almost no "
            "visible destination product surface."
        ),
        "next_repair_instruction": (
            "Keep the source-to-memory route, but make the destination a visible, large product surface rather than "
            "empty spatial anchors."
        ),
    },
    "contrast": {
        "delta_vs_2_77": "partial",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "product_surface_realization": "weak",
        "public_video_direction": "partial",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The before/after page keeps an asymmetric title/copy layout, but the after-state product is not visible "
            "enough to prove a richer result."
        ),
        "next_repair_instruction": (
            "Make the after side a visible product reveal with larger surface detail, so the contrast is optical rather "
            "than label-only."
        ),
    },
    "proof": {
        "delta_vs_2_77": "partial",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "product_surface_realization": "absent",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The proof page no longer looks like a debug rail, but it also lacks the enlarged evidence object required "
            "for an inspection scene."
        ),
        "next_repair_instruction": (
            "Place a large evidence/proof object on the canvas and bind two readable labels directly to that object."
        ),
    },
    "climax": {
        "delta_vs_2_77": "partial",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "product_surface_realization": "absent",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The completion reveal is typographically clear, but the supposed full-frame editable result is not visible "
            "at presentation scale."
        ),
        "next_repair_instruction": (
            "Make the climax a full-frame editable PPT result with visible slide thumbnails, surface controls, and fewer "
            "floating labels."
        ),
    },
    "close": {
        "delta_vs_2_77": "partial",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "product_surface_realization": "weak",
        "public_video_direction": "partial",
        "root_cause_layer": "text_binding",
        "visual_observation": (
            "The release-gate copy is understandable, but the decision map is still mostly tiny labels in open space."
        ),
        "next_repair_instruction": (
            "Turn the close into a dominant release-gate decision object with large branch labels and a clear blocked "
            "public outcome."
        ),
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.80 visual evaluation missing required {label}: {path}")


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


def validate_inputs(run277: dict[str, Any], l_eval: dict[str, Any], run279: dict[str, Any]) -> None:
    if run277.get("status") != "run2_77_visual_grammar_renderer_repair_rerun_generated_public_blocked":
        raise ValueError("Run 2.80 evaluation expected Run 2.77 renderer repair rerun result")
    if l_eval.get("status") != "run2_78_visual_quality_evaluation_public_blocked":
        raise ValueError("Run 2.80 evaluation expected Run 2.78/Part L visual quality evaluation")
    if l_eval.get("next_required_action") != "part_m_renderer_art_direction_repair_from_l_evaluation":
        raise ValueError("Run 2.80 evaluation expected Part L to hand off to Part M")
    if run279.get("status") != "run2_79_renderer_art_direction_repair_rerun_generated_public_blocked":
        raise ValueError("Run 2.80 evaluation expected Run 2.79 renderer art-direction rerun result")
    if run279.get("next_required_action") != "part_n_visual_quality_evaluation_for_run2_79":
        raise ValueError("Run 2.80 evaluation expected Run 2.79 to hand off to Part N")

    for label, data in [("Run 2.77", run277), ("Run 2.79", run279)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.80 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.80 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run277 = next((run for run in runs if run.get("id") == "2.77"), {})
    run279 = next((run for run in runs if run.get("id") == "2.79"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_77_and_2_79": {"2.77", "2.79"} <= run_ids,
        "run2_77_full_preview_count": len((run277.get("fullArm") or {}).get("slides") or []),
        "run2_79_full_preview_count": len((run279.get("fullArm") or {}).get("slides") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": (
            "Part N records expected viewer closure. Browser verification must confirm latest 2.79 "
            "and visible 2.77/2.79 comparison after this artifact is written."
        ),
    }


def role_assessments(run279: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run279.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "delta_vs_2_77": judgment["delta_vs_2_77"],
                "wireframe_reduction": judgment["wireframe_reduction"],
                "label_hierarchy": judgment["label_hierarchy"],
                "product_surface_realization": judgment["product_surface_realization"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "next_repair_instruction": judgment["next_repair_instruction"],
                "trace_support": {
                    "art_direction_scene": page.get("art_direction_scene", ""),
                    "label_count": page.get("label_count", 0),
                    "debug_annotation_count": page.get("debug_annotation_count", 0),
                    "wireframe_dependency": page.get("wireframe_dependency", ""),
                    "dominant_product_object_scale": page.get("dominant_product_object_scale", ""),
                },
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    for path, label in [
        (RUN277_CONTACT_SHEET, "Run 2.77 full contact sheet"),
        (RUN279_CONTACT_SHEET, "Run 2.79 full contact sheet"),
    ]:
        require_file(path, label)

    run277 = read_json(RUN277_RESULT)
    l_eval = read_json(RUN278_L_EVALUATION)
    run279 = read_json(RUN279_RESULT)
    validate_inputs(run277, l_eval, run279)

    role_records = role_assessments(run279)
    closure = viewer_closure()

    return {
        "artifact_id": "run2_80_visual_quality_evaluation",
        "part": "Part N",
        "schema_version": "ppt_run2_80_visual_quality_evaluation.v1",
        "run_id": "2.80",
        "status": "run2_80_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_m_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_n_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.77",
            "evaluated_run": "2.79",
            "prior_reference_run": "2.75",
        },
        "input_chain": {
            "run2_79_result": rel(RUN279_RESULT),
            "run2_78_l_evaluation": rel(RUN278_L_EVALUATION),
            "run2_77_result": rel(RUN277_RESULT),
            "run2_77_full_contact_sheet": rel(RUN277_CONTACT_SHEET),
            "run2_79_full_contact_sheet": rel(RUN279_CONTACT_SHEET),
            "ppt_run_viewer": closure["ppt_run_viewer"],
        },
        "viewer_comparison_closure": closure,
        "gemini_agent_review_summary": GEMINI_AGENT_REVIEW_SUMMARY,
        "evaluation_questions": {
            "is_2_79_better_than_2_77": {
                "answer": "mixed_annotation_down_but_product_surface_absent_public_blocked",
                "basis": (
                    "2.79 removes the most obvious debug annotations and uses more audience-readable labels, "
                    "but the contact sheet still lacks visible product surfaces and remains public blocked."
                ),
            },
            "did_2_79_reduce_wireframe_and_annotation": {
                "answer": "partial_debug_annotations_removed_but_typographic_wireframe_remains",
                "basis": (
                    "Red/debug markers are gone, but the dominant read is now sparse typographic wireframe "
                    "rather than a finished presentation scene."
                ),
            },
            "did_2_79_fix_small_label_problem": {
                "answer": "no_labels_still_tiny_and_spatially_scattered",
                "basis": (
                    "Label wording improved, but the labels remain small, isolated, and hard to read at "
                    "presentation-preview scale."
                ),
            },
            "did_2_79_create_concrete_product_surface": {
                "answer": "no_product_surface_not_visibly_realized",
                "basis": (
                    "The rendered contact sheet does not visibly show the large product objects declared in metadata."
                ),
            },
            "does_2_79_reach_public_video_presentation_direction": {
                "answer": "no_public_blocked",
                "basis": (
                    "2.79 is an internal renderer-art-direction proof, not a public-video presentation pass."
                ),
            },
            "which_layer_needs_next_repair": {
                "answer": "renderer_product_surface_realization",
                "basis": (
                    "The remaining problem is visual realization of product surfaces and public hierarchy, not source data."
                ),
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_77": "debug_annotations_down_but_product_surface_absent_and_small_labels_remain",
            "top_blocker": "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes",
            "next_layer_to_fix": "renderer_product_surface_realization",
        },
        "role_assessments": role_records,
        "root_cause_summary": {
            "primary_layer": "renderer_product_surface_realization",
            "secondary_layers": ["text_binding", "visual_grammar"],
            "not_primary_layer": "data_absence",
            "rationale": (
                "2.79 consumed Part L, 2.77, and K1 and removed debug annotations. The blocker moved from "
                "debug annotation language to missing visible product-surface realization."
            ),
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_o_renderer_product_surface_repair_from_n_evaluation",
    }


def assert_evaluation_boundary(audit: dict[str, Any]) -> None:
    boundary_flags = {
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
    }
    for key, expected in boundary_flags.items():
        if audit.get(key) is not expected:
            raise ValueError(f"Part N boundary violation: {key} must remain {str(expected).lower()}")
    proof = audit.get("no_new_renderer_proof", {})
    for key in ["new_pptx_created", "new_html_created", "starts_renderer_rerun"]:
        if proof.get(key) is not False:
            raise ValueError(f"Part N boundary violation: no_new_renderer_proof.{key} must remain false")


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Run 2.80 Visual Quality Evaluation",
        "",
        "Part N compares 2.79 vs 2.77. Conclusion: debug annotations down, but product surface absent and small labels remain; public blocked.",
        "",
        "Gemini review input: one 2.79 full contact-sheet artifact review with `gemini-3.5-flash` was used for the verdict, alongside the Part L evaluation of 2.77.",
        "",
        "## Verdict",
        "",
        f"- Status: `{audit['status']}`",
        f"- Global delta: `{audit['visual_quality_assessment']['global_delta_vs_2_77']}`",
        f"- Top blocker: `{audit['visual_quality_assessment']['top_blocker']}`",
        "- Visual read: product surface absent; the deck remains a sparse text wireframe, not a public-video presentation.",
        "",
        "## Limitations",
        "",
        "- Gemini review used the static 2.79 full-arm contact sheet, not motion, OCR, or public audience testing.",
        "- This artifact is an evaluation gate only; it must not be read as a public-quality pass.",
        "",
        "## Answers",
        "",
    ]
    for question_id in QUESTION_IDS:
        question = audit["evaluation_questions"][question_id]
        lines.append(f"- `{question_id}`: `{question['answer']}`")
        lines.append(f"  {question['basis']}")
    lines.extend(["", "## Page Repairs", ""])
    for record in audit["role_assessments"]:
        lines.append(
            f"- Slide {record['slide_index']} `{record['role']}` / `{record['visual_grammar_module']}`: "
            f"{record['next_repair_instruction']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No renderer rerun was started.",
            "- No PPT or HTML viewer output was generated by Part N.",
            "- Next required action: `part_o_renderer_product_surface_repair_from_n_evaluation`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Run 2.79 visual quality against Run 2.77.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    args = parser.parse_args()

    audit = build_audit()
    assert_evaluation_boundary(audit)
    write_json(args.result_json, audit)
    write_report(args.result_md, audit)
    print(
        json.dumps(
            {
                "status": audit["status"],
                "result_json": rel(args.result_json),
                "result_md": rel(args.result_md),
                "public_ready": audit["public_ready"],
                "next_required_action": audit["next_required_action"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
