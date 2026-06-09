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
RUN273_FULL = PRESENTATIONS / "ppt-run2-73-full-vulca"
RUN275_FULL = PRESENTATIONS / "ppt-run2-75-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_76_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_76_visual_quality_evaluation.md"

RUN273_RESULT = PACK / "results" / "run2_73_validated_scene_renderer_rerun_result.json"
RUN274_H_EVALUATION = PACK / "results" / "run2_74_visual_quality_evaluation.json"
RUN275_RESULT = PACK / "results" / "run2_75_renderer_repair_rerun_result.json"
RUN273_CONTACT_SHEET = RUN273_FULL / "preview" / "contact-sheet.png"
RUN275_CONTACT_SHEET = RUN275_FULL / "preview" / "contact-sheet.png"

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
    "is_2_75_better_than_2_73",
    "does_2_75_have_stronger_product_feel",
    "are_page_differences_stronger_or_weaker",
    "is_text_binding_better",
    "does_2_75_reach_public_video_presentation_direction",
]

GEMINI_AGENT_REVIEW_SUMMARY = {
    "tool": "mcp__gemini_agent.gemini_artifact_review",
    "model": "gemini-3.5-flash",
    "review_count": 2,
    "used_for_verdict": True,
    "capture_method": "live_gemini_agent_artifact_review",
    "reviewed_artifacts": [
        {
            "run_id": "2.73",
            "file": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-73-full-vulca/preview/contact-sheet.png",
            "key_findings": [
                "excellent_structural_variety",
                "spatial_text_binding_present",
                "product_feel_highly_technical_and_schematic",
            ],
            "risks": [
                "high_engineering_blueprint_risk",
                "tiny_label_legibility_risk",
            ],
        },
        {
            "run_id": "2.75",
            "file": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-75-full-vulca/preview/contact-sheet.png",
            "key_findings": [
                "product_surface_detail_up",
                "page_differentiation_regression_for_01_02_04_05",
                "spatial_text_anchors_consistent",
            ],
            "risks": [
                "high_engineering_blueprint_risk",
                "tiny_label_legibility_risk",
            ],
        },
    ],
    "run2_73_findings": [
        "excellent_structural_variety",
        "high_engineering_blueprint_risk",
        "tiny_label_legibility_risk",
    ],
    "run2_75_findings": [
        "product_surface_detail_up",
        "page_differentiation_regression_for_01_02_04_05",
        "high_engineering_blueprint_risk",
        "tiny_label_legibility_risk",
    ],
    "shared_risks": [
        "engineering blueprint risk remains",
        "tiny secondary labels reduce public presentation readability",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "product_feel_delta": "improved_but_wireframe",
        "page_differentiation_delta": "weaker",
        "text_binding_delta": "slightly_stronger_but_small",
        "engineering_report_risk": "high",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "2.75 adds more visible product surface detail, but the opening still reads as a thin "
            "wireframe deck surface with debug-like red markers."
        ),
        "repair_instruction": (
            "Replace the repeated wireframe deck surface with a more inspectable finished product "
            "hero and fewer debug-colored markers."
        ),
    },
    "setup": {
        "product_feel_delta": "partial",
        "page_differentiation_delta": "weaker",
        "text_binding_delta": "partial",
        "engineering_report_risk": "high",
        "public_video_direction": "no",
        "root_cause_layer": "visual_grammar",
        "visual_observation": (
            "The hero field keeps text attached to the route, but its product destination now feels "
            "too close to the repeated product reveal surface."
        ),
        "repair_instruction": (
            "Make the hero field visually distinct from product reveal pages; the route should drive "
            "a larger and more legible destination state."
        ),
    },
    "contrast": {
        "product_feel_delta": "partial",
        "page_differentiation_delta": "same",
        "text_binding_delta": "partial",
        "engineering_report_risk": "medium",
        "public_video_direction": "partial",
        "root_cause_layer": "visual_grammar",
        "visual_observation": (
            "The comparison seam remains one of the more distinct pages, but the before/after states "
            "still look like a diagram study more than a public product transformation."
        ),
        "repair_instruction": (
            "Keep the seam but reduce debug-lens feeling; make before and after product states visibly "
            "different at thumbnail scale."
        ),
    },
    "proof": {
        "product_feel_delta": "improved_but_wireframe",
        "page_differentiation_delta": "weaker",
        "text_binding_delta": "slightly_stronger_but_small",
        "engineering_report_risk": "high",
        "public_video_direction": "no",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The proof workspace is more populated than 2.73, but the repeated thin surfaces and tiny "
            "labels still read as internal QA documentation."
        ),
        "repair_instruction": (
            "Turn the workspace into source, output, and review objects with readable labels, not "
            "repeated thin UI cards."
        ),
    },
    "climax": {
        "product_feel_delta": "improved_but_wireframe",
        "page_differentiation_delta": "weaker",
        "text_binding_delta": "partial",
        "engineering_report_risk": "high",
        "public_video_direction": "no",
        "root_cause_layer": "visual_grammar",
        "visual_observation": (
            "The climax has a denser product surface than 2.73, but it is too similar to the cover "
            "and does not yet deliver a finished reveal moment."
        ),
        "repair_instruction": (
            "Differentiate climax from cover with scale, richer product content, and a decisive "
            "completion moment."
        ),
    },
    "close": {
        "product_feel_delta": "partial",
        "page_differentiation_delta": "same",
        "text_binding_delta": "slightly_stronger_but_small",
        "engineering_report_risk": "medium",
        "public_video_direction": "partial",
        "root_cause_layer": "text_binding",
        "visual_observation": (
            "The decision map remains structurally distinct, but its labels and endpoints need more "
            "public-facing hierarchy."
        ),
        "repair_instruction": (
            "Keep decision nodes but enlarge labels and make the release decision visually dominant."
        ),
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.76 visual evaluation missing required {label}: {path}")


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


def validate_inputs(run273: dict[str, Any], h_eval: dict[str, Any], run275: dict[str, Any]) -> None:
    if run273.get("status") != "run2_73_validated_scene_renderer_rerun_generated_public_blocked":
        raise ValueError("Run 2.76 evaluation expected Run 2.73 validated scene renderer result")
    if h_eval.get("status") != "run2_74_visual_quality_evaluation_public_blocked":
        raise ValueError("Run 2.76 evaluation expected Run 2.74 visual quality evaluation")
    if run275.get("status") != "run2_75_renderer_repair_rerun_generated_public_blocked":
        raise ValueError("Run 2.76 evaluation expected Run 2.75 renderer repair rerun result")
    if run275.get("next_required_action") != "part_j_visual_quality_evaluation_for_run2_75":
        raise ValueError("Run 2.76 evaluation expected Run 2.75 to hand off to Part J")

    for label, data in [("Run 2.73", run273), ("Run 2.75", run275)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.76 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.76 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run273 = next((run for run in runs if run.get("id") == "2.73"), {})
    run275 = next((run for run in runs if run.get("id") == "2.75"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_73_and_2_75": {"2.73", "2.75"} <= run_ids,
        "run2_73_full_preview_count": len((run273.get("fullArm") or {}).get("slides") or []),
        "run2_75_full_preview_count": len((run275.get("fullArm") or {}).get("slides") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": (
            "Part J records the expected viewer closure. Browser verification must confirm latest "
            "2.75 and visible 2.73/2.75 comparison after this artifact is written."
        ),
    }


def role_assessments(run275: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run275.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "product_feel_delta": judgment["product_feel_delta"],
                "page_differentiation_delta": judgment["page_differentiation_delta"],
                "text_binding_delta": judgment["text_binding_delta"],
                "engineering_report_risk": judgment["engineering_report_risk"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "repair_instruction": judgment["repair_instruction"],
                "trace_support": {
                    "source_text_binding_id": page.get("source_text_binding_id", ""),
                    "visual_density_profile": page.get("visual_density_profile", ""),
                    "product_surface_detail_count": page.get("product_surface_detail_count", 0),
                    "connector_or_edge_binding_count": page.get("connector_or_edge_binding_count", 0),
                },
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    for path, label in [
        (RUN273_CONTACT_SHEET, "Run 2.73 full contact sheet"),
        (RUN275_CONTACT_SHEET, "Run 2.75 full contact sheet"),
    ]:
        require_file(path, label)

    run273 = read_json(RUN273_RESULT)
    h_eval = read_json(RUN274_H_EVALUATION)
    run275 = read_json(RUN275_RESULT)
    validate_inputs(run273, h_eval, run275)

    role_records = role_assessments(run275)
    closure = viewer_closure()

    return {
        "artifact_id": "run2_76_visual_quality_evaluation",
        "part": "Part J",
        "schema_version": "ppt_run2_76_visual_quality_evaluation.v1",
        "run_id": "2.76",
        "status": "run2_76_visual_quality_evaluation_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "public_ready": False,
        "quality_claim_boundary": "part_j_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.73",
            "evaluated_run": "2.75",
        },
        "input_chain": {
            "run2_73_result": rel(RUN273_RESULT),
            "run2_75_result": rel(RUN275_RESULT),
            "run2_74_h_evaluation": rel(RUN274_H_EVALUATION),
            "run2_73_full_contact_sheet": rel(RUN273_CONTACT_SHEET),
            "run2_75_full_contact_sheet": rel(RUN275_CONTACT_SHEET),
            "ppt_run_viewer": closure["ppt_run_viewer"],
        },
        "viewer_comparison_closure": closure,
        "gemini_agent_review_summary": GEMINI_AGENT_REVIEW_SUMMARY,
        "evaluation_questions": {
            "is_2_75_better_than_2_73": {
                "answer": "mixed_product_surface_up_page_differentiation_down_public_blocked",
                "basis": (
                    "2.75 increases product surface detail, but Gemini and local review both find "
                    "page differentiation regression and unchanged public-readiness blockers."
                ),
            },
            "does_2_75_have_stronger_product_feel": {
                "answer": "yes_but_still_wireframe",
                "basis": (
                    "The repair adds more product-like deck surfaces and connectors, but most pages "
                    "still read as schematic UI wireframes rather than finished presentation scenes."
                ),
            },
            "are_page_differences_stronger_or_weaker": {
                "answer": "weaker_for_core_product_surface_pages",
                "basis": (
                    "Slides 01, 02, 04, and 05 converge around similar wireframe product surfaces, "
                    "while contrast and close remain more distinct."
                ),
            },
            "is_text_binding_better": {
                "answer": "slightly_stronger_but_small_labels_remain",
                "basis": (
                    "Text anchors are more consistently attached to edges, rails, seams, and nodes, "
                    "but small labels still reduce contact-sheet and public-video readability."
                ),
            },
            "does_2_75_reach_public_video_presentation_direction": {
                "answer": "no_internal_blueprint_risk_remains",
                "basis": (
                    "The deck is internally viewable, but the wireframe blueprint aesthetic and "
                    "debug-like marks still make it feel like an engineering review."
                ),
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_73": "product_surface_up_page_differentiation_down_public_readiness_still_blocked",
            "top_blocker": (
                "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams"
            ),
            "next_layer_to_fix": "visual_grammar_and_renderer",
        },
        "role_assessments": role_records,
        "root_cause_summary": {
            "primary_layer": "visual_grammar_and_renderer",
            "secondary_layers": ["text_binding"],
            "not_primary_layer": "data_absence",
            "rationale": (
                "A-F data is present and consumed; the remaining visible failure is how the visual "
                "grammar and renderer realize product surfaces, rhythm, and public hierarchy."
            ),
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_k_visual_grammar_and_renderer_repair_from_j_evaluation",
    }


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Run 2.76 Visual Quality Evaluation",
        "",
        "Part J compares 2.75 vs 2.73. Conclusion: product surface up, page differentiation down, public blocked.",
        "",
        "Gemini review input: two contact-sheet artifact reviews with `gemini-3.5-flash` were used for the verdict.",
        "",
        "## Verdict",
        "",
        f"- Status: `{audit['status']}`",
        f"- Global delta: `{audit['visual_quality_assessment']['global_delta_vs_2_73']}`",
        f"- Top blocker: `{audit['visual_quality_assessment']['top_blocker']}`",
        "- Visual read: the wireframe blueprint aesthetic still dominates the public impression.",
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
            f"{record['repair_instruction']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No renderer rerun was started.",
            "- No PPT or HTML viewer output was generated by Part J.",
            "- Next required action: `part_k_visual_grammar_and_renderer_repair_from_j_evaluation`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Run 2.75 visual quality against Run 2.73.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    args = parser.parse_args()

    audit = build_audit()
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
