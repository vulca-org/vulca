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
RUN290_FULL = PRESENTATIONS / "ppt-run2-90-full-vulca"
RUN292_FULL = PRESENTATIONS / "ppt-run2-92-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_93_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_93_visual_quality_evaluation.md"

RUN281_TEXT_PLAN = PACK / "run2_81_text_composition_typography_plan.json"
RUN290_RESULT = PACK / "results" / "run2_90_renderer_asset_surface_composition_rerun_result.json"
RUN291_EVALUATION = PACK / "results" / "run2_91_visual_quality_evaluation.json"
RUN292_RESULT = PACK / "results" / "run2_92_renderer_text_visual_binding_repair_rerun_result.json"
RUN290_CONTACT_SHEET = PRESENTATIONS / "ppt-run2-90-full-vulca/preview/contact-sheet.png"
RUN292_CONTACT_SHEET = PRESENTATIONS / "ppt-run2-92-full-vulca/preview/contact-sheet.png"
RUN292_FOUR_ARM_SHEET = PRESENTATIONS / "run2-92-four-arm-contact-sheet.png"

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
    "is_2_92_better_than_2_90": {
        "answer": "yes_text_visual_binding_up_public_still_blocked",
        "basis": "2.92 attaches headline/proof/caption text to visible product objects more clearly than 2.90 while keeping the deck blocked from public release.",
    },
    "did_2_92_fix_text_visual_binding": {
        "answer": "partial_object_binding_visible_but_not_public_ready",
        "basis": "Object-bound typography, caption anchors, and proof embedding are now visible in the manifest and contact sheet, but the execution still reads as an internal wireframe in several pages.",
    },
    "did_2_92_preserve_2_90_asset_surface_gain": {
        "answer": "yes_asset_surface_preserved",
        "basis": "2.92 consumes and preserves the 2.90 asset surface layer instead of reverting to sparse text-only slides.",
    },
    "did_2_92_keep_text_heavy_readability": {
        "answer": "partial_readable_hierarchy_up_small_bound_text_risk",
        "basis": "The text-heavy direction remains, but some bound captions are small and need stronger public-presentation typography.",
    },
    "does_2_92_reduce_parallel_text_surface_failure": {
        "answer": "yes_parallel_layer_failure_reduced",
        "basis": "2.92 reduces the prior split where product surfaces and text blocks acted as separate layers.",
    },
    "does_2_92_reach_public_video_presentation_direction": {
        "answer": "no_public_blocked",
        "basis": "The deck has better binding but still lacks public-grade polish, surface realism, and legibility hierarchy.",
    },
    "which_layer_needs_next_repair": {
        "answer": "visual_polish_legibility_and_surface_realism",
        "basis": "The next renderer pass should keep the binding but make bound typography larger, more composed, and less diagrammatic.",
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
            "ppt-run2-90-full-vulca/preview/contact-sheet.png"
        ),
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-92-full-vulca/preview/contact-sheet.png"
        ),
    ],
    "run2_92_findings": [
        "text-object binding improved compared with 2.90",
        "proof sentences and object captions are visibly closer to product surfaces",
        "asset surface is preserved while the text layer is less parallel",
        "binding text directly to visual objects reduces cognitive load versus detached side-by-side comparisons",
        "slide 05 shifts toward a unified generated deck surface with bound proofs",
        "traceability remains off canvas and labels stay limited",
    ],
    "run2_92_risks": [
        "public polish still blocked because the surfaces remain diagram-like",
        "some bound text is still small and can read as annotation instead of presentation copy",
        "thin wireframe connector lines and overlapping boxes still have low visual contrast",
        "slide 05 needs clearer z-index and depth separation to avoid confusing overlaps",
        "composition balance is uneven across setup, proof, and close",
        "surface realism is not yet strong enough for a public video presentation",
        "the deck needs a final visual polish pass before public readiness can be judged again",
    ],
    "limitations": [
        "Review is based on static contact sheets, browser-visible previews, and renderer manifests, not motion, OCR, or public audience testing.",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "text_visual_binding_delta": "strong",
        "asset_surface_preservation": "strong",
        "legibility_quality": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "visual_polish_legibility",
        "visual_observation": "The hero surface and headline now feel more connected, but the slide still needs stronger type contrast and less internal-product-diagram texture.",
        "next_repair_instruction": "Keep the hero object binding and push the headline/proof relationship into a larger editorial lockup.",
    },
    "setup": {
        "text_visual_binding_delta": "partial",
        "asset_surface_preservation": "partial",
        "legibility_quality": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "composition_balance",
        "visual_observation": "Text is more anchored than 2.90, but the spread still separates explanatory copy from the product surface too cleanly.",
        "next_repair_instruction": "Merge the explanatory block, caption, and surface into one readable editorial spread with fewer axes.",
    },
    "contrast": {
        "text_visual_binding_delta": "strong",
        "asset_surface_preservation": "partial",
        "legibility_quality": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "object_bound_typography",
        "visual_observation": "The before/after stage benefits from attached captions, but the comparison still needs a stronger public-facing reading path.",
        "next_repair_instruction": "Turn the before/after captions into large comparison labels that are part of the stage, not annotation tags.",
    },
    "proof": {
        "text_visual_binding_delta": "partial",
        "asset_surface_preservation": "partial",
        "legibility_quality": "weak",
        "public_video_direction": "no",
        "root_cause_layer": "proof_object_embedding",
        "visual_observation": "The proof sentence is embedded more directly than in 2.90, but proof-page text remains too small and workbench-like.",
        "next_repair_instruction": "Promote the proof sentence into a dominant evidence object with one large caption and fewer small marks.",
    },
    "climax": {
        "text_visual_binding_delta": "partial",
        "asset_surface_preservation": "strong",
        "legibility_quality": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "surface_realism",
        "visual_observation": "The climax keeps the asset-surface gain and improves bound copy, but the payoff still reads as native-shape construction rather than a finished product reveal.",
        "next_repair_instruction": "Make the surface material and staged object richer while preserving the text-object lockup.",
    },
    "close": {
        "text_visual_binding_delta": "partial",
        "asset_surface_preservation": "partial",
        "legibility_quality": "weak",
        "public_video_direction": "no",
        "root_cause_layer": "public_art_direction",
        "visual_observation": "Decision text is more board-bound than 2.90, but the close still lacks a decisive public-release visual finish.",
        "next_repair_instruction": "Turn the decision board into a clearer public handoff surface with larger node text and less diagram residue.",
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.93 visual evaluation missing required {label}: {path}")


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


def validate_inputs(
    run281: dict[str, Any],
    run290: dict[str, Any],
    run291: dict[str, Any],
    run292: dict[str, Any],
) -> None:
    if run281.get("status") != "run2_81_text_composition_typography_plan_ready_public_blocked":
        raise ValueError("Run 2.93 evaluation expected Run 2.81 text composition plan")
    if run290.get("status") != "run2_90_renderer_asset_surface_composition_rerun_generated_public_blocked":
        raise ValueError("Run 2.93 evaluation expected Run 2.90 renderer result")
    if run290.get("next_required_action") != "part_v_visual_quality_evaluation_for_run2_90":
        raise ValueError("Run 2.93 evaluation expected Run 2.90 to hand off to Part V")
    if run291.get("status") != "run2_91_visual_quality_evaluation_public_blocked":
        raise ValueError("Run 2.93 evaluation expected Run 2.91 visual quality evaluation")
    if run291.get("next_required_action") != "part_w_renderer_text_visual_binding_repair_from_v_evaluation":
        raise ValueError("Run 2.93 evaluation expected Part V to request Part W")
    if run292.get("status") != "run2_92_renderer_text_visual_binding_repair_rerun_generated_public_blocked":
        raise ValueError("Run 2.93 evaluation expected Run 2.92 renderer result")
    if run292.get("next_required_action") != "part_x_visual_quality_evaluation_for_run2_92":
        raise ValueError("Run 2.93 evaluation expected Run 2.92 to hand off to Part X")

    for label, data in [("Run 2.90", run290), ("Run 2.92", run292)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.93 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.93 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run290 = next((run for run in runs if run.get("id") == "2.90"), {})
    run292 = next((run for run in runs if run.get("id") == "2.92"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_90_and_2_92": {"2.90", "2.92"} <= run_ids,
        "run2_90_full_preview_count": len((run290.get("fullArm") or {}).get("slides") or []),
        "run2_92_full_preview_count": len((run292.get("fullArm") or {}).get("slides") or []),
        "run2_92_arm_count": len(run292.get("arms") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": "Part X records current viewer closure. Browser verification must confirm latest 2.92 and visible 2.90/2.92 comparison after this artifact is written.",
    }


def role_assessments(run292: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run292.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "text_visual_binding_delta": judgment["text_visual_binding_delta"],
                "asset_surface_preservation": judgment["asset_surface_preservation"],
                "legibility_quality": judgment["legibility_quality"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "next_repair_instruction": judgment["next_repair_instruction"],
                "trace_support": {
                    "text_visual_binding_id": str(page.get("text_visual_binding_id") or ""),
                    "renderer_function_name": str(page.get("renderer_function_name") or ""),
                    "object_bound_typography_applied": bool(page.get("object_bound_typography_applied")),
                    "caption_anchor_binding_applied": bool(page.get("caption_anchor_binding_applied")),
                    "proof_sentence_embedded_in_visual_object": bool(page.get("proof_sentence_embedded_in_visual_object")),
                    "traceability_on_canvas": bool(page.get("traceability_on_canvas")),
                    "label_count": int(page.get("label_count") or 0),
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


def build_audit(
    run281: dict[str, Any],
    run290: dict[str, Any],
    run291: dict[str, Any],
    run292: dict[str, Any],
) -> dict[str, Any]:
    validate_inputs(run281, run290, run291, run292)
    for path, label in [
        (RUN290_CONTACT_SHEET, "Run 2.90 full contact sheet"),
        (RUN292_CONTACT_SHEET, "Run 2.92 full contact sheet"),
        (RUN292_FOUR_ARM_SHEET, "Run 2.92 four-arm contact sheet"),
    ]:
        require_file(path, label)

    return {
        "artifact_id": "run2_93_visual_quality_evaluation",
        "part": "Part X",
        "schema_version": "ppt_run2_93_visual_quality_evaluation.v1",
        "run_id": "2.93",
        "status": "run2_93_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_part_w_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_x_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.90",
            "evaluated_run": "2.92",
            "repair_source_run": "2.91",
            "text_contract_run": "2.81",
        },
        "input_chain": {
            "run2_92_result": rel(RUN292_RESULT),
            "run2_91_v_evaluation": rel(RUN291_EVALUATION),
            "run2_90_result": rel(RUN290_RESULT),
            "run2_81_text_composition_plan": rel(RUN281_TEXT_PLAN),
            "run2_90_full_contact_sheet": rel(RUN290_CONTACT_SHEET),
            "run2_92_full_contact_sheet": rel(RUN292_CONTACT_SHEET),
            "run2_92_four_arm_contact_sheet": rel(RUN292_FOUR_ARM_SHEET),
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
            "global_delta_vs_2_90": "text_visual_binding_up_surface_preserved_public_polish_still_blocked",
            "top_blocker": "bound_text_and_surfaces_still_read_as_internal_wireframe_not_public_presentation",
            "next_layer_to_fix": "visual_polish_legibility_and_surface_realism",
        },
        "role_assessments": role_assessments(run292),
        "root_cause_summary": {
            "primary_layer": "visual_polish_legibility_and_surface_realism",
            "secondary_layers": ["small_bound_text_legibility", "surface_realism", "composition_balance"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": "binding_layer_fixed_before_public_surface_polish",
            "rationale": (
                "2.92 repaired the parallel text-surface failure enough to see object-bound typography, "
                "but the slides still need public-grade polish, larger bound type, and more realistic product surfaces."
            ),
        },
        "no_new_renderer_proof": no_new_renderer_proof(),
        "next_required_action": "part_y_renderer_visual_polish_legibility_repair_from_x_evaluation",
    }


def build_markdown(audit: dict[str, Any]) -> str:
    assessment = audit["visual_quality_assessment"]
    return "\n".join(
        [
            "# Run 2.93 Visual Quality Evaluation",
            "",
            f"Status: {audit['status']}",
            "",
            "Comparison: 2.92 vs 2.90",
            "",
            "Verdict: text-object binding improved and asset surface preserved, but public blocked.",
            "",
            "Key finding: 2.92 reduces the parallel text/surface failure. The remaining blocker is visual polish, legibility, and surface realism.",
            "",
            f"Design quality gate: {assessment['design_quality_gate']}",
            f"Global delta: {assessment['global_delta_vs_2_90']}",
            f"Top blocker: {assessment['top_blocker']}",
            "",
            "Role-level repair focus:",
            *[
                f"- {record['role']}: {record['root_cause_layer']} -> {record['next_repair_instruction']}"
                for record in audit["role_assessments"]
            ],
            "",
            "Boundary: public blocked. Part X does not create a new PPT, rerun renderer, or update the HTML viewer.",
            "",
            f"Next required action: {audit['next_required_action']} (Part Y)",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.92 visual quality after Part W.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run281 = read_json(RUN281_TEXT_PLAN)
    run290 = read_json(RUN290_RESULT)
    run291 = read_json(RUN291_EVALUATION)
    run292 = read_json(RUN292_RESULT)
    audit = build_audit(run281, run290, run291, run292)
    write_json(args.result_json, audit)
    args.result_md.parent.mkdir(parents=True, exist_ok=True)
    args.result_md.write_text(build_markdown(audit), encoding="utf-8")
    print(audit["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
