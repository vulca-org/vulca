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
RUN282_FULL = PRESENTATIONS / "ppt-run2-82-full-vulca"
RUN285_FULL = PRESENTATIONS / "ppt-run2-85-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_86_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_86_visual_quality_evaluation.md"

RUN282_RESULT = PACK / "results" / "run2_82_renderer_product_surface_text_composition_rerun_result.json"
RUN284_P1_PLAN = PACK / "run2_84_design_motif_taxonomy_style_router_plan.json"
RUN285_RESULT = PACK / "results" / "run2_85_design_motif_renderer_rerun_result.json"
RUN282_CONTACT_SHEET = RUN282_FULL / "preview" / "contact-sheet.png"
RUN285_CONTACT_SHEET = RUN285_FULL / "preview" / "contact-sheet.png"

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
    "is_2_85_better_than_2_82",
    "did_2_85_restore_design_motif_visual_language",
    "did_2_85_keep_text_heavy_layout_readability",
    "did_2_85_preserve_modular_matrix_and_sticker_effects",
    "does_2_85_explain_why_late_2_series_lost_aesthetic",
    "does_2_85_reach_public_video_presentation_direction",
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
            "ppt-run2-82-full-vulca/preview/contact-sheet.png"
        ),
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-85-full-vulca/preview/contact-sheet.png"
        ),
    ],
    "reviewed_artifacts": [
        {
            "run_id": "2.85",
            "file": (
                "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
                "ppt-run2-85-full-vulca/preview/contact-sheet.png"
            ),
            "key_findings": [
                "new terminology and structural layout updates are visible",
                "slide 05 colored borders improve the overlay sticker stack scannability",
                "slide 04 moves toward a modular matrix workspace",
                "slide 06 still shows text overlap or collision risk",
            ],
            "risks": [
                "renderer primitive ceiling blocks motif fidelity",
                "composition engine still over-regularizes pages",
                "layout collision avoidance still needs repair",
                "public audience may read it as an internal system diagram",
            ],
        }
    ],
    "run2_85_findings": [
        "slide 05 colored borders improve scannability",
        "slide 04 modular matrix structure is clearer",
        "motif trace up relative to 2.82",
        "text-heavy layout remains readable but rigid",
        "modular and sticker effects are present as hints, not as high-fidelity design language",
        "slide 06 has an unresolved overlap or collision risk",
    ],
    "run2_85_risks": [
        "renderer primitive ceiling",
        "composition engine still conservative",
        "layout collision avoidance still weak",
        "late 2.x engineering gates may still dominate aesthetic execution",
    ],
    "limitations": [
        "Review is based on static full-arm contact sheets and manifest trace; no motion, OCR, or audience test was performed.",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "delta_vs_2_82": "partial",
        "motif_realization": "partial",
        "layout_distinctiveness": "partial",
        "text_composition": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "renderer_visual_primitives",
        "visual_observation": (
            "The product-theater motif is traceable and the page has a stronger stage direction, but it still "
            "depends on a simple native product shell rather than a convincing public-facing surface."
        ),
        "next_repair_instruction": (
            "Recover the strongest historical hero layout, then replace the generic product shell with a richer "
            "native PPT product-theater primitive."
        ),
    },
    "setup": {
        "delta_vs_2_82": "partial",
        "motif_realization": "partial",
        "layout_distinctiveness": "partial",
        "text_composition": "rigid",
        "public_video_direction": "no",
        "root_cause_layer": "text_composition",
        "visual_observation": (
            "The editorial text-field intent is clearer, but the text still sits in predictable blocks rather than "
            "a composed magazine-like field with a varied reading rhythm."
        ),
        "next_repair_instruction": (
            "Turn the setup into a true editorial spread: stronger paragraph grouping, side captions, and one "
            "anchored product destination object."
        ),
    },
    "contrast": {
        "delta_vs_2_82": "improved",
        "motif_realization": "partial",
        "layout_distinctiveness": "strong",
        "text_composition": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "design_motif_binding",
        "visual_observation": (
            "The before/after theater remains the most readable motif, but the after-state still lacks the richer "
            "surface detail needed for a public-quality optical win."
        ),
        "next_repair_instruction": (
            "Preserve the before/after theater, enlarge the after surface, and add finer native UI/detail primitives "
            "instead of more labels."
        ),
    },
    "proof": {
        "delta_vs_2_82": "partial",
        "motif_realization": "weak",
        "layout_distinctiveness": "partial",
        "text_composition": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "renderer_visual_primitives",
        "visual_observation": (
            "The modular-matrix motif is declared and partly visible, but it still feels like a grid of blocks, not "
            "a designed evidence workspace."
        ),
        "next_repair_instruction": (
            "Introduce a real matrix primitive with varied cell hierarchy, connected proof object, and readable "
            "evidence captions."
        ),
    },
    "climax": {
        "delta_vs_2_82": "partial",
        "motif_realization": "partial",
        "layout_distinctiveness": "partial",
        "text_composition": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "composition_engine",
        "visual_observation": (
            "The overlay-sticker stack is visible as a concept, but the climax does not yet feel like a designed "
            "payoff moment; it is still assembled from simple panels."
        ),
        "next_repair_instruction": (
            "Recover the best historical climax layout and build sticker-stack primitives with overlap, scale, "
            "tilt, and a single dominant generated deck surface."
        ),
    },
    "close": {
        "delta_vs_2_82": "partial",
        "motif_realization": "partial",
        "layout_distinctiveness": "partial",
        "text_composition": "rigid",
        "public_video_direction": "partial",
        "root_cause_layer": "composition_engine",
        "visual_observation": (
            "The decision-map direction is understandable, but the map still reads as small nodes and labels rather "
            "than a confident closing decision object."
        ),
        "next_repair_instruction": (
            "Make the release decision map the visual object: larger branch geometry, one blocked-public outcome, "
            "and less generic node styling."
        ),
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.86 visual evaluation missing required {label}: {path}")


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


def validate_inputs(run282: dict[str, Any], p1_plan: dict[str, Any], run285: dict[str, Any]) -> None:
    if run282.get("status") != "run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked":
        raise ValueError("Run 2.86 evaluation expected Run 2.82 product surface/text composition result")
    if p1_plan.get("status") != "run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked":
        raise ValueError("Run 2.86 evaluation expected Run 2.84/P1 design motif plan")
    if p1_plan.get("next_required_action") != "part_p2_renderer_rerun_from_design_motif_layer_and_style_router":
        raise ValueError("Run 2.86 evaluation expected P1 to hand off to P2")
    if run285.get("status") != "run2_85_design_motif_renderer_rerun_generated_public_blocked":
        raise ValueError("Run 2.86 evaluation expected Run 2.85 design motif renderer result")
    if run285.get("next_required_action") != "part_q_visual_quality_evaluation_for_run2_85":
        raise ValueError("Run 2.86 evaluation expected Run 2.85 to hand off to Part Q")

    for label, data in [("Run 2.82", run282), ("Run 2.85", run285)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.86 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.86 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run282 = next((run for run in runs if run.get("id") == "2.82"), {})
    run285 = next((run for run in runs if run.get("id") == "2.85"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_82_and_2_85": {"2.82", "2.85"} <= run_ids,
        "run2_82_full_preview_count": len((run282.get("fullArm") or {}).get("slides") or []),
        "run2_85_full_preview_count": len((run285.get("fullArm") or {}).get("slides") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": (
            "Part Q records expected viewer closure. Browser verification must confirm latest 2.85 "
            "and visible 2.82/2.85 comparison after this artifact is written."
        ),
    }


def role_assessments(run285: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run285.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "delta_vs_2_82": judgment["delta_vs_2_82"],
                "motif_realization": judgment["motif_realization"],
                "layout_distinctiveness": judgment["layout_distinctiveness"],
                "text_composition": judgment["text_composition"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "next_repair_instruction": judgment["next_repair_instruction"],
                "trace_support": {
                    "motif_family": page.get("motif_family", ""),
                    "style_family": page.get("style_family", ""),
                    "scenario": page.get("scenario", ""),
                    "source_p1_primary_motif_id": page.get("source_p1_primary_motif_id", ""),
                    "label_count": page.get("label_count", 0),
                    "not_rectangle_only": page.get("not_rectangle_only", False),
                    "text_integrated_with_shape": page.get("text_integrated_with_shape", False),
                    "preserved_visual_effects_rendered": page.get("preserved_visual_effects_rendered", []),
                },
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    for path, label in [
        (RUN282_CONTACT_SHEET, "Run 2.82 full contact sheet"),
        (RUN285_CONTACT_SHEET, "Run 2.85 full contact sheet"),
    ]:
        require_file(path, label)

    run282 = read_json(RUN282_RESULT)
    p1_plan = read_json(RUN284_P1_PLAN)
    run285 = read_json(RUN285_RESULT)
    validate_inputs(run282, p1_plan, run285)

    role_records = role_assessments(run285)
    closure = viewer_closure()

    return {
        "artifact_id": "run2_86_visual_quality_evaluation",
        "part": "Part Q",
        "schema_version": "ppt_run2_86_visual_quality_evaluation.v1",
        "run_id": "2.86",
        "status": "run2_86_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_p2_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_q_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.82",
            "evaluated_run": "2.85",
            "design_contract_run": "2.84",
            "prior_reference_run": "2.79",
        },
        "input_chain": {
            "run2_85_result": rel(RUN285_RESULT),
            "run2_84_p1_design_motif_plan": rel(RUN284_P1_PLAN),
            "run2_82_result": rel(RUN282_RESULT),
            "run2_82_full_contact_sheet": rel(RUN282_CONTACT_SHEET),
            "run2_85_full_contact_sheet": rel(RUN285_CONTACT_SHEET),
            "ppt_run_viewer": closure["ppt_run_viewer"],
        },
        "viewer_comparison_closure": closure,
        "gemini_agent_review_summary": GEMINI_AGENT_REVIEW_SUMMARY,
        "evaluation_questions": {
            "is_2_85_better_than_2_82": {
                "answer": "partial_motif_trace_up_visual_delta_small_public_blocked",
                "basis": (
                    "2.85 consumes the motif layer and creates more differentiated scene intent, but the visible "
                    "contact-sheet delta remains incremental rather than a public-quality leap."
                ),
            },
            "did_2_85_restore_design_motif_visual_language": {
                "answer": "partial_motif_metadata_visible_but_renderer_primitives_still_simple",
                "basis": (
                    "The motif family is traceable per page, but the renderer still expresses most motifs through "
                    "basic panels, ellipses, lines, and small labels."
                ),
            },
            "did_2_85_keep_text_heavy_layout_readability": {
                "answer": "partial_text_hierarchy_present_but_composition_still_rigid",
                "basis": (
                    "The pages keep headline/subhead/proof/caption hierarchy, but the editorial field is not yet "
                    "composed with high-end typography rhythm."
                ),
            },
            "did_2_85_preserve_modular_matrix_and_sticker_effects": {
                "answer": "partial_effects_declared_and_some_visible_but_not_high_fidelity",
                "basis": (
                    "Matrix and sticker-stack effects are represented, but they read as primitives rather than "
                    "fully designed presentation language."
                ),
            },
            "does_2_85_explain_why_late_2_series_lost_aesthetic": {
                "answer": "yes_engineering_gates_and_contracts_overweighted_renderer_conservatism",
                "basis": (
                    "Run 2.85 proves data and motif wiring improved, so the remaining flatness points to conservative "
                    "renderer primitives and composition templates."
                ),
            },
            "does_2_85_reach_public_video_presentation_direction": {
                "answer": "no_public_blocked",
                "basis": "2.85 remains an internal generated comparison, not a public presentation pass.",
            },
            "which_layer_needs_next_repair": {
                "answer": "renderer_visual_primitive_and_composition_engine",
                "basis": (
                    "Further data contracts are likely low leverage until the renderer can draw richer motif-specific "
                    "primitives and recover the best historical layouts."
                ),
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_82": "motif_contract_consumed_but_visual_result_remains_incremental",
            "top_blocker": "renderer_visual_primitives_are_too_simple_to_realize_design_motifs",
            "next_layer_to_fix": "renderer_visual_primitive_and_composition_engine",
        },
        "role_assessments": role_records,
        "root_cause_summary": {
            "primary_layer": "renderer_visual_primitive_and_composition_engine",
            "secondary_layers": ["design_motif_binding", "text_composition", "visual_grammar"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": (
                "engineering_traceability_and_contract_layers_became_stronger_than_visual_execution_primitives"
            ),
            "rationale": (
                "P1/P2 consume source, motif, style, text, and product-surface contracts. Because visual delta remains "
                "small after that wiring, the next bottleneck is how the renderer draws and composes motif primitives."
            ),
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_r_best_layout_recovery_and_visual_primitive_plan_from_q_evaluation",
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
            raise ValueError(f"Part Q boundary violation: {key} must remain {str(expected).lower()}")
    proof = audit.get("no_new_renderer_proof", {})
    for key in ["new_pptx_created", "new_html_created", "starts_renderer_rerun"]:
        if proof.get(key) is not False:
            raise ValueError(f"Part Q boundary violation: no_new_renderer_proof.{key} must remain false")


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Run 2.86 Visual Quality Evaluation",
        "",
        (
            "Part Q compares 2.85 vs 2.82. Conclusion: motif wiring improved and a few slides are more "
            "scannable, but the public-quality visual result remains incremental; public blocked."
        ),
        "",
        "Gemini review input: one 2.85 full contact-sheet artifact review with `gemini-3.5-flash` was used for the verdict, alongside the Part P1/P2 trace.",
        "",
        "## Verdict",
        "",
        f"- Status: `{audit['status']}`",
        f"- Global delta: `{audit['visual_quality_assessment']['global_delta_vs_2_82']}`",
        f"- Top blocker: `{audit['visual_quality_assessment']['top_blocker']}`",
        (
            "- Visual read: Slide 04/05 improved, Slide 06 still has collision risk, and renderer visual "
            "primitive plus composition engine are now the bottleneck."
        ),
        "",
        "## Why Late 2.x Lost Aesthetic",
        "",
        "- Engineering traceability, validators, socket contracts, and release gates became strong enough to constrain output.",
        "- The renderer stayed conservative, so richer data was collapsed into simple native shapes and regular text blocks.",
        "- This is not primarily a data-absence problem anymore.",
        "",
        "## Limitations",
        "",
        "- Gemini review used static contact sheets, not motion, OCR, or public audience testing.",
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
            f"- Slide {record['slide_index']} `{record['role']}` / `{record['trace_support']['motif_family']}`: "
            f"{record['next_repair_instruction']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No renderer rerun was started.",
            "- No PPT or HTML viewer output was generated by Part Q.",
            "- Next required action: `part_r_best_layout_recovery_and_visual_primitive_plan_from_q_evaluation`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Run 2.85 visual quality against Run 2.82.")
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
