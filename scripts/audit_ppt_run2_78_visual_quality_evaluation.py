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
RUN275_FULL = PRESENTATIONS / "ppt-run2-75-full-vulca"
RUN277_FULL = PRESENTATIONS / "ppt-run2-77-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_78_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_78_visual_quality_evaluation.md"

RUN275_RESULT = PACK / "results" / "run2_75_renderer_repair_rerun_result.json"
RUN276_J_EVALUATION = PACK / "results" / "run2_76_visual_quality_evaluation.json"
RUN276_K1_REPAIR_PLAN = PACK / "run2_76_visual_grammar_renderer_repair_plan.json"
RUN277_RESULT = PACK / "results" / "run2_77_visual_grammar_renderer_repair_rerun_result.json"
RUN275_CONTACT_SHEET = RUN275_FULL / "preview" / "contact-sheet.png"
RUN277_CONTACT_SHEET = RUN277_FULL / "preview" / "contact-sheet.png"

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
    "is_2_77_better_than_2_75",
    "did_2_77_restore_page_differentiation",
    "did_2_77_reduce_wireframe_aesthetic",
    "did_2_77_reduce_small_label_problem",
    "does_2_77_improve_product_presentation_feel",
    "does_2_77_reach_public_video_presentation_direction",
]

GEMINI_AGENT_REVIEW_SUMMARY = {
    "tool": "mcp__gemini_agent.gemini_artifact_review",
    "model": "gemini-3.5-flash",
    "review_count": 1,
    "used_for_verdict": True,
    "capture_method": "live_gemini_agent_artifact_review",
    "comparison_artifacts": [
        "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-75-full-vulca/preview/contact-sheet.png",
        "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-77-full-vulca/preview/contact-sheet.png",
    ],
    "reviewed_artifacts": [
        {
            "run_id": "2.77",
            "file": (
                "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
                "ppt-run2-77-full-vulca/preview/contact-sheet.png"
            ),
            "key_findings": [
                "moderate_page_differentiation",
                "slides_02_03_06_have_distinct_layouts",
                "slides_01_04_05_share_wireframe_box_structure",
                "technical_abstract_feel_remains",
            ],
            "risks": [
                "wireframe_aesthetic_remains",
                "small_label_readability_risk",
                "red_annotation_marks_can_read_as_debug_or_interactive_ui",
            ],
        }
    ],
    "run2_77_findings": [
        "moderate page differentiation",
        "slides 02, 03, and 06 are more distinct",
        "slides 01, 04, and 05 still share a wireframe box family",
        "technical abstract presentation feel remains",
    ],
    "run2_77_risks": [
        "wireframe aesthetic remains",
        "small labels remain compressed",
        "red annotation marks may read as debug or interactive controls",
    ],
    "limitations": [
        "Review is based on the static full-arm contact sheet; no transition or OCR verification was performed.",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "delta_vs_2_75": "partial",
        "page_differentiation": "partial",
        "wireframe_reduction": "weak",
        "label_hierarchy": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The opening hero keeps a clearer product edge than the pre-K repair plan, but it still "
            "reads as a thin outlined product diagram with red annotation marks."
        ),
        "next_repair_instruction": (
            "Replace the thin product-outline hero with a more finished product crop and reduce red "
            "debug markers to one purposeful editorial highlight."
        ),
    },
    "setup": {
        "delta_vs_2_75": "partial",
        "page_differentiation": "improved",
        "wireframe_reduction": "weak",
        "label_hierarchy": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The route field is more clearly a transformation scene, but the destination surface and "
            "route labels still feel schematic."
        ),
        "next_repair_instruction": (
            "Keep the route bend and unequal field scale, then give the destination a stronger "
            "public-facing product surface instead of stacked outline panels."
        ),
    },
    "contrast": {
        "delta_vs_2_75": "improved",
        "page_differentiation": "improved",
        "wireframe_reduction": "partial",
        "label_hierarchy": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "visual_grammar",
        "visual_observation": (
            "The asymmetric seam remains the clearest differentiated scene, but the after-state is "
            "still an abstract product wireframe."
        ),
        "next_repair_instruction": (
            "Preserve the seam and after-state dominance while making the after product visibly richer "
            "at thumbnail scale."
        ),
    },
    "proof": {
        "delta_vs_2_75": "partial",
        "page_differentiation": "partial",
        "wireframe_reduction": "weak",
        "label_hierarchy": "weak",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The proof page has an inspection-scene direction, but the active proof object remains a "
            "large thin-line frame with tiny labels."
        ),
        "next_repair_instruction": (
            "Turn the proof object into a larger, legible evidence surface with two readable labels, "
            "not a thin workbench diagram."
        ),
    },
    "climax": {
        "delta_vs_2_75": "partial",
        "page_differentiation": "improved",
        "wireframe_reduction": "weak",
        "label_hierarchy": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The climax is more differentiated from the cover by scale and frame ownership, but the "
            "payoff is still mostly an outlined UI shell."
        ),
        "next_repair_instruction": (
            "Make the completion reveal feel like a finished editable PPT result with richer slide "
            "content and less schematic outline language."
        ),
    },
    "close": {
        "delta_vs_2_75": "partial",
        "page_differentiation": "improved",
        "wireframe_reduction": "partial",
        "label_hierarchy": "weak",
        "public_video_direction": "partial",
        "root_cause_layer": "text_binding",
        "visual_observation": (
            "The release gate direction is visible and different from the product pages, but the node "
            "labels are still too small for public-video readability."
        ),
        "next_repair_instruction": (
            "Keep the release-gate map, enlarge the decision labels, and make the blocked-public "
            "branch the dominant visual decision."
        ),
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.78 visual evaluation missing required {label}: {path}")


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


def validate_inputs(run275: dict[str, Any], j_eval: dict[str, Any], k1_plan: dict[str, Any], run277: dict[str, Any]) -> None:
    if run275.get("status") != "run2_75_renderer_repair_rerun_generated_public_blocked":
        raise ValueError("Run 2.78 evaluation expected Run 2.75 renderer repair result")
    if j_eval.get("status") != "run2_76_visual_quality_evaluation_public_blocked":
        raise ValueError("Run 2.78 evaluation expected Run 2.76/Part J visual quality evaluation")
    if k1_plan.get("status") != "run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked":
        raise ValueError("Run 2.78 evaluation expected Run 2.76/K1 repair plan")
    if run277.get("status") != "run2_77_visual_grammar_renderer_repair_rerun_generated_public_blocked":
        raise ValueError("Run 2.78 evaluation expected Run 2.77 renderer repair rerun result")
    if run277.get("next_required_action") != "part_l_visual_quality_evaluation_for_run2_77":
        raise ValueError("Run 2.78 evaluation expected Run 2.77 to hand off to Part L")

    for label, data in [("Run 2.75", run275), ("Run 2.77", run277)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.78 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.78 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run275 = next((run for run in runs if run.get("id") == "2.75"), {})
    run277 = next((run for run in runs if run.get("id") == "2.77"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_75_and_2_77": {"2.75", "2.77"} <= run_ids,
        "run2_75_full_preview_count": len((run275.get("fullArm") or {}).get("slides") or []),
        "run2_77_full_preview_count": len((run277.get("fullArm") or {}).get("slides") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": (
            "Part L records expected viewer closure. Browser verification must confirm latest 2.77 "
            "and visible 2.75/2.77 comparison after this artifact is written."
        ),
    }


def role_assessments(run277: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run277.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "delta_vs_2_75": judgment["delta_vs_2_75"],
                "page_differentiation": judgment["page_differentiation"],
                "wireframe_reduction": judgment["wireframe_reduction"],
                "label_hierarchy": judgment["label_hierarchy"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "next_repair_instruction": judgment["next_repair_instruction"],
                "trace_support": {
                    "target_scene_direction": page.get("target_scene_direction", ""),
                    "visual_density_profile": page.get("visual_density_profile", ""),
                    "renderer_capabilities_applied": page.get("renderer_capabilities_applied", []),
                    "label_count": page.get("label_count", 0),
                },
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    for path, label in [
        (RUN275_CONTACT_SHEET, "Run 2.75 full contact sheet"),
        (RUN277_CONTACT_SHEET, "Run 2.77 full contact sheet"),
    ]:
        require_file(path, label)

    run275 = read_json(RUN275_RESULT)
    j_eval = read_json(RUN276_J_EVALUATION)
    k1_plan = read_json(RUN276_K1_REPAIR_PLAN)
    run277 = read_json(RUN277_RESULT)
    validate_inputs(run275, j_eval, k1_plan, run277)

    role_records = role_assessments(run277)
    closure = viewer_closure()

    return {
        "artifact_id": "run2_78_visual_quality_evaluation",
        "part": "Part L",
        "schema_version": "ppt_run2_78_visual_quality_evaluation.v1",
        "run_id": "2.78",
        "status": "run2_78_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_k2_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_l_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.75",
            "evaluated_run": "2.77",
            "prior_reference_run": "2.73",
        },
        "input_chain": {
            "run2_75_result": rel(RUN275_RESULT),
            "run2_77_result": rel(RUN277_RESULT),
            "run2_76_j_evaluation": rel(RUN276_J_EVALUATION),
            "run2_76_k1_repair_plan": rel(RUN276_K1_REPAIR_PLAN),
            "run2_75_full_contact_sheet": rel(RUN275_CONTACT_SHEET),
            "run2_77_full_contact_sheet": rel(RUN277_CONTACT_SHEET),
            "ppt_run_viewer": closure["ppt_run_viewer"],
        },
        "viewer_comparison_closure": closure,
        "gemini_agent_review_summary": GEMINI_AGENT_REVIEW_SUMMARY,
        "evaluation_questions": {
            "is_2_77_better_than_2_75": {
                "answer": "partial_page_differentiation_up_public_blocked",
                "basis": (
                    "2.77 applies the K1 target scene directions and reduces label count, but Gemini "
                    "and local review both find persistent wireframe/public-readiness blockers."
                ),
            },
            "did_2_77_restore_page_differentiation": {
                "answer": "moderately_improved_but_01_04_05_share_wireframe_family",
                "basis": (
                    "Setup, contrast, climax, and close read more distinct than the mixed 2.75 state, "
                    "but cover, proof, and climax still share a thin product-surface family."
                ),
            },
            "did_2_77_reduce_wireframe_aesthetic": {
                "answer": "no_wireframe_still_dominant",
                "basis": (
                    "Thin grey/blue outlines and red annotation circles are still first-read features "
                    "across the contact sheet."
                ),
            },
            "did_2_77_reduce_small_label_problem": {
                "answer": "partial_label_count_down_but_labels_still_tiny",
                "basis": (
                    "K2 reduced metadata label count and bound text to scene objects, but remaining "
                    "labels are still compressed at contact-sheet scale."
                ),
            },
            "does_2_77_improve_product_presentation_feel": {
                "answer": "partial_more_scene_specific_but_abstract_product_surface",
                "basis": (
                    "The visual grammar directions are clearer, but the product surfaces remain abstract "
                    "wireframe shells rather than finished public presentation objects."
                ),
            },
            "does_2_77_reach_public_video_presentation_direction": {
                "answer": "no_public_blocked",
                "basis": (
                    "2.77 is useful for internal workflow verification, but still reads too technical "
                    "and schematic for public-video presentation."
                ),
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_75": "page_differentiation_up_label_count_down_wireframe_still_blocks_public_readiness",
            "top_blocker": "thin_wireframe_product_surfaces_and_annotation_marks_still_read_as_internal_diagram",
            "next_layer_to_fix": "renderer_art_direction_and_scene_realization",
        },
        "role_assessments": role_records,
        "root_cause_summary": {
            "primary_layer": "renderer_art_direction_and_scene_realization",
            "secondary_layers": ["text_binding", "visual_grammar"],
            "not_primary_layer": "data_absence",
            "rationale": (
                "K2 consumed J, 2.75, D2/D3/E/E2/F, and the K1 repair plan. Remaining visible blockers "
                "are the renderer's art direction, surface finish, and public hierarchy."
            ),
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_m_renderer_art_direction_repair_from_l_evaluation",
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
            raise ValueError(f"Part L boundary violation: {key} must remain {str(expected).lower()}")
    proof = audit.get("no_new_renderer_proof", {})
    for key in ["new_pptx_created", "new_html_created", "starts_renderer_rerun"]:
        if proof.get(key) is not False:
            raise ValueError(f"Part L boundary violation: no_new_renderer_proof.{key} must remain false")


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Run 2.78 Visual Quality Evaluation",
        "",
        "Part L compares 2.77 vs 2.75. Conclusion: page differentiation up, label count down, wireframe still blocks public readiness.",
        "",
        "Gemini review input: one 2.77 full contact-sheet artifact review with `gemini-3.5-flash` was used for the verdict, alongside the prior J evaluation of 2.75.",
        "",
        "## Verdict",
        "",
        f"- Status: `{audit['status']}`",
        f"- Global delta: `{audit['visual_quality_assessment']['global_delta_vs_2_75']}`",
        f"- Top blocker: `{audit['visual_quality_assessment']['top_blocker']}`",
        "- Visual read: wireframe still blocks public-video presentation direction.",
        "",
        "## Limitations",
        "",
        "- Gemini review used the static 2.77 full-arm contact sheet, not pixel-level OCR, motion, or public audience testing.",
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
            "- No PPT or HTML viewer output was generated by Part L.",
            "- Next required action: `part_m_renderer_art_direction_repair_from_l_evaluation`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Run 2.77 visual quality against Run 2.75.")
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
