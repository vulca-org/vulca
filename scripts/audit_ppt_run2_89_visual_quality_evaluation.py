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
RUN285_FULL = PRESENTATIONS / "ppt-run2-85-full-vulca"
RUN288_FULL = PRESENTATIONS / "ppt-run2-88-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_89_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_89_visual_quality_evaluation.md"

RUN285_RESULT = PACK / "results" / "run2_85_design_motif_renderer_rerun_result.json"
RUN287_PLAN = PACK / "run2_87_best_layout_recovery_visual_primitive_plan.json"
RUN288_RESULT = PACK / "results" / "run2_88_best_layout_visual_primitive_rerun_result.json"
RUN285_CONTACT_SHEET = RUN285_FULL / "preview" / "contact-sheet.png"
RUN288_CONTACT_SHEET = RUN288_FULL / "preview" / "contact-sheet.png"
RUN288_FOUR_ARM_SHEET = PRESENTATIONS / "run2-88-four-arm-contact-sheet.png"

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
    "is_2_88_better_than_2_85",
    "did_2_88_recover_best_layout_visual_primitives",
    "did_2_88_keep_text_heavy_readability",
    "did_2_88_preserve_modular_matrix_and_sticker_effects",
    "does_2_88_fix_late_2_series_aesthetic_bottleneck",
    "does_2_88_reach_public_video_presentation_direction",
    "which_layer_needs_next_repair",
]

GEMINI_AGENT_REVIEW_SUMMARY = {
    "tool": "gemini-agent artifact-review",
    "model": "gemini-3.5-flash",
    "review_count": 1,
    "used_for_verdict": True,
    "capture_method": "live_gemini_agent_artifact_review",
    "comparison_artifacts": [
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-85-full-vulca/preview/contact-sheet.png"
        ),
        (
            "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/"
            "ppt-run2-88-full-vulca/preview/contact-sheet.png"
        ),
    ],
    "run2_88_findings": [
        "layout templates are structurally identical",
        "terminology and conceptual framing changed from motif language to layout-primitive language",
        "slide 04 and 05 preserve matrix and sticker hints",
        "2.88 improves semantic framing more than visible composition",
    ],
    "run2_88_risks": [
        "slides remain wireframe-like",
        "Slide 06 has a text collision near review",
        "abstract boxes still do not read as public product surfaces",
        "low-resolution contact sheets limit fine typography inspection",
    ],
    "limitations": [
        "Review is based on static contact sheets, not motion, OCR, or public audience testing.",
    ],
}

ROLE_JUDGMENTS = {
    "cover": {
        "delta_vs_2_85": "partial",
        "best_layout_recovery": "partial",
        "visual_primitive_fidelity": "weak",
        "text_composition": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "renderer_asset_surface",
        "visual_observation": (
            "The cover names best-layout recovery, but the product theater is still mostly empty space plus small "
            "outlined labels rather than a finished product surface."
        ),
        "next_repair_instruction": (
            "Replace the hero/proof rail boxes with a concrete product-surface asset primitive and a stronger "
            "editorial headline composition."
        ),
    },
    "setup": {
        "delta_vs_2_85": "partial",
        "best_layout_recovery": "partial",
        "visual_primitive_fidelity": "weak",
        "text_composition": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "text_composition",
        "visual_observation": (
            "The text-field framing is clearer, but the page is still a sparse field of copy and labels instead of "
            "a composed editorial spread."
        ),
        "next_repair_instruction": (
            "Turn the text field into a real typography composition with a visible product destination object."
        ),
    },
    "contrast": {
        "delta_vs_2_85": "partial",
        "best_layout_recovery": "partial",
        "visual_primitive_fidelity": "partial",
        "text_composition": "partial",
        "public_video_direction": "partial",
        "root_cause_layer": "layout_engine_reuse",
        "visual_observation": (
            "The before/after stage is still the clearest page, but Gemini judged the layout structure largely "
            "identical to 2.85."
        ),
        "next_repair_instruction": (
            "Keep the before/after stage and add real after-state surface detail, not another label rename."
        ),
    },
    "proof": {
        "delta_vs_2_85": "partial",
        "best_layout_recovery": "partial",
        "visual_primitive_fidelity": "weak",
        "text_composition": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "visual_primitive_fidelity",
        "visual_observation": (
            "The unequal-matrix wording is better, but the visible matrix remains a few outline blocks rather than "
            "a high-fidelity evidence workspace."
        ),
        "next_repair_instruction": (
            "Render an unequal evidence matrix with real cell hierarchy, fills, density, and object-linked captions."
        ),
    },
    "climax": {
        "delta_vs_2_85": "unchanged",
        "best_layout_recovery": "partial",
        "visual_primitive_fidelity": "partial",
        "text_composition": "partial",
        "public_video_direction": "no",
        "root_cause_layer": "composition_engine",
        "visual_observation": (
            "The sticker-stack page preserves the colored structure, but the same sparse blocks remain and the "
            "payoff still does not feel cinematic."
        ),
        "next_repair_instruction": (
            "Build a denser sticker-stack stage with overlap, tilt, fills, and one dominant generated-deck object."
        ),
    },
    "close": {
        "delta_vs_2_85": "partial",
        "best_layout_recovery": "partial",
        "visual_primitive_fidelity": "weak",
        "text_composition": "rigid",
        "public_video_direction": "no",
        "root_cause_layer": "composition_engine",
        "visual_observation": (
            "The decision-map claim is clearer, but the page still has scattered labels and a visible collision near "
            "review, which blocks public readiness."
        ),
        "next_repair_instruction": (
            "Make the decision map one large visual object, fix the review collision, and reduce scattered labels."
        ),
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.89 visual evaluation missing required {label}: {path}")


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


def validate_inputs(run285: dict[str, Any], plan287: dict[str, Any], run288: dict[str, Any]) -> None:
    if run285.get("status") != "run2_85_design_motif_renderer_rerun_generated_public_blocked":
        raise ValueError("Run 2.89 evaluation expected Run 2.85 renderer result")
    if plan287.get("status") != "run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked":
        raise ValueError("Run 2.89 evaluation expected Run 2.87 best-layout plan")
    if plan287.get("next_required_action") != "part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan":
        raise ValueError("Run 2.89 evaluation expected Part R to hand off to Part S")
    if run288.get("status") != "run2_88_best_layout_visual_primitive_rerun_generated_public_blocked":
        raise ValueError("Run 2.89 evaluation expected Run 2.88 renderer rerun result")
    if run288.get("next_required_action") != "part_t_visual_quality_evaluation_for_run2_88":
        raise ValueError("Run 2.89 evaluation expected Run 2.88 to hand off to Part T")

    for label, data in [("Run 2.85", run285), ("Run 2.88", run288)]:
        roles = [page.get("role") for page in data.get("rendered_pages", [])]
        if roles != ROLES:
            raise ValueError(f"Run 2.89 evaluation expected ordered six-page role set for {label}")
        modules = [page.get("visual_grammar_module") for page in data.get("rendered_pages", [])]
        expected_modules = [MODULE_BY_ROLE[role] for role in ROLES]
        if modules != expected_modules:
            raise ValueError(f"Run 2.89 evaluation expected visual grammar mapping for {label}")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    runs = data.get("runs", [])
    run_ids = {run["id"] for run in runs}
    run285 = next((run for run in runs if run.get("id") == "2.85"), {})
    run288 = next((run for run in runs if run.get("id") == "2.88"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_85_and_2_88": {"2.85", "2.88"} <= run_ids,
        "run2_85_full_preview_count": len((run285.get("fullArm") or {}).get("slides") or []),
        "run2_88_full_preview_count": len((run288.get("fullArm") or {}).get("slides") or []),
        "run2_88_arm_count": len(run288.get("arms") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": (
            "Part T records expected viewer closure. Browser verification must confirm latest 2.88 "
            "and visible 2.85/2.88 comparison after this artifact is written."
        ),
    }


def role_assessments(run288: dict[str, Any]) -> list[dict[str, Any]]:
    pages_by_role = {page["role"]: page for page in run288.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = pages_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role]),
                "delta_vs_2_85": judgment["delta_vs_2_85"],
                "best_layout_recovery": judgment["best_layout_recovery"],
                "visual_primitive_fidelity": judgment["visual_primitive_fidelity"],
                "text_composition": judgment["text_composition"],
                "public_video_direction": judgment["public_video_direction"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "next_repair_instruction": judgment["next_repair_instruction"],
                "trace_support": {
                    "renderer_primitive_id": page.get("renderer_primitive_id", ""),
                    "renderer_function_name": page.get("renderer_function_name", ""),
                    "label_count": page.get("label_count", 0),
                    "not_rectangle_only": page.get("not_rectangle_only", False),
                    "text_integrated_with_shape": page.get("text_integrated_with_shape", False),
                    "collision_or_overlap_risk": role == "close",
                },
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    for path, label in [
        (RUN285_CONTACT_SHEET, "Run 2.85 full contact sheet"),
        (RUN288_CONTACT_SHEET, "Run 2.88 full contact sheet"),
        (RUN288_FOUR_ARM_SHEET, "Run 2.88 four-arm contact sheet"),
    ]:
        require_file(path, label)

    run285 = read_json(RUN285_RESULT)
    plan287 = read_json(RUN287_PLAN)
    run288 = read_json(RUN288_RESULT)
    validate_inputs(run285, plan287, run288)

    closure = viewer_closure()
    role_records = role_assessments(run288)

    return {
        "artifact_id": "run2_89_visual_quality_evaluation",
        "part": "Part T",
        "schema_version": "ppt_run2_89_visual_quality_evaluation.v1",
        "run_id": "2.89",
        "status": "run2_89_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_part_s_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_t_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.85",
            "evaluated_run": "2.88",
            "repair_contract_run": "2.87",
            "prior_reference_run": "2.82",
        },
        "input_chain": {
            "run2_88_result": rel(RUN288_RESULT),
            "run2_87_plan": rel(RUN287_PLAN),
            "run2_85_result": rel(RUN285_RESULT),
            "run2_85_full_contact_sheet": rel(RUN285_CONTACT_SHEET),
            "run2_88_full_contact_sheet": rel(RUN288_CONTACT_SHEET),
            "run2_88_four_arm_contact_sheet": rel(RUN288_FOUR_ARM_SHEET),
            "ppt_run_viewer": closure["ppt_run_viewer"],
        },
        "viewer_comparison_closure": closure,
        "gemini_agent_review_summary": GEMINI_AGENT_REVIEW_SUMMARY,
        "evaluation_questions": {
            "is_2_88_better_than_2_85": {
                "answer": "partial_semantic_framing_up_visual_delta_small_public_blocked",
                "basis": (
                    "2.88 reframes pages around best-layout and primitive language, but Gemini judged the visible "
                    "layout templates structurally close to 2.85."
                ),
            },
            "did_2_88_recover_best_layout_visual_primitives": {
                "answer": "partial_primitives_named_but_layout_engine_positions_remain_similar",
                "basis": (
                    "The Run 2.87 primitive IDs and drawRun287 functions are consumed, but the contact sheet still "
                    "shows sparse labels and similar spatial structure."
                ),
            },
            "did_2_88_keep_text_heavy_readability": {
                "answer": "yes_text_hierarchy_readable_but_sparse_and_wireframe",
                "basis": (
                    "The pages preserve headline/subhead/proof/caption readability, but typography still feels "
                    "like an internal wireframe rather than public presentation art direction."
                ),
            },
            "did_2_88_preserve_modular_matrix_and_sticker_effects": {
                "answer": "partial_slide_04_05_preserved_but_not_high_fidelity",
                "basis": (
                    "Slide 04 and 05 keep matrix/sticker cues, but they remain outline-block primitives rather "
                    "than high-fidelity visual effects."
                ),
            },
            "does_2_88_fix_late_2_series_aesthetic_bottleneck": {
                "answer": "no_visual_execution_still_wireframe_like",
                "basis": (
                    "The late 2.x bottleneck is now visible execution: asset surfaces, fills, density, and "
                    "composition detail lag behind the data contracts."
                ),
            },
            "does_2_88_reach_public_video_presentation_direction": {
                "answer": "no_public_blocked",
                "basis": "2.88 remains an internal renderer experiment and does not reach public video presentation quality.",
            },
            "which_layer_needs_next_repair": {
                "answer": "renderer_asset_surface_and_composition_detail",
                "basis": (
                    "The next repair must make primitives visually material: concrete product surfaces, denser "
                    "composition, real fills, and collision cleanup."
                ),
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_85": "best_layout_language_up_but_visual_structure_mostly_unchanged",
            "top_blocker": "layout_primitive_names_changed_but_visual_execution_remains_wireframe_like",
            "next_layer_to_fix": "renderer_asset_surface_and_composition_detail",
        },
        "role_assessments": role_records,
        "root_cause_summary": {
            "primary_layer": "renderer_asset_surface_and_composition_detail",
            "secondary_layers": ["visual_primitive_fidelity", "layout_engine_reuse", "text_composition"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": "semantic_contracts_and_primitive_names_changed_faster_than_visible_composition",
            "rationale": (
                "Part R and S prove the best-layout primitive contract is consumed. Since the visible result remains "
                "close to 2.85, the next bottleneck is asset-surface and composition-detail execution."
            ),
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_u_renderer_asset_surface_composition_repair_from_t_evaluation",
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
            raise ValueError(f"Part T boundary violation: {key} must remain {str(expected).lower()}")
    proof = audit.get("no_new_renderer_proof", {})
    for key in ["new_pptx_created", "new_html_created", "starts_renderer_rerun"]:
        if proof.get(key) is not False:
            raise ValueError(f"Part T boundary violation: no_new_renderer_proof.{key} must remain false")


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Run 2.89 Visual Quality Evaluation",
        "",
        (
            "Part T compares 2.88 vs 2.85. Conclusion: layout-primitive language improved faster than "
            "visible composition; the result is still wireframe-like, so public remains blocked."
        ),
        "",
        "Gemini review input: 2.85 and 2.88 full contact sheets were compared with `gemini-3.5-flash`.",
        "",
        "## Verdict",
        "",
        f"- Status: `{audit['status']}`",
        f"- Global delta: `{audit['visual_quality_assessment']['global_delta_vs_2_85']}`",
        f"- Top blocker: `{audit['visual_quality_assessment']['top_blocker']}`",
        "- Visual read: the layouts are structurally identical enough that Part U must focus on real asset surfaces and composition detail.",
        "",
        "## Why 2.88 Is Still Blocked",
        "",
        "- The renderer consumes Run 2.87 primitive IDs and functions, but many visible elements are still outline labels.",
        "- The slide system keeps text readable, but the canvas is sparse and wireframe-like.",
        "- Slide 06 still carries a collision/overlap risk near the review label.",
        "- This is not primarily a data-absence problem.",
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
            f"- Slide {record['slide_index']} `{record['role']}`: {record['next_repair_instruction']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No renderer rerun was started.",
            "- No PPT or HTML viewer output was generated by Part T.",
            "- Next required action: `part_u_renderer_asset_surface_composition_repair_from_t_evaluation`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Run 2.88 visual quality against Run 2.85.")
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
