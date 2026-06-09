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
RUN272_FULL = PRESENTATIONS / "ppt-run2-72-full-vulca"
RUN273_FULL = PRESENTATIONS / "ppt-run2-73-full-vulca"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_74_visual_quality_evaluation.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_74_visual_quality_evaluation.md"

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
    "is_2_73_better_than_2_72",
    "is_text_fused_with_visual_structure",
    "does_it_still_feel_like_engineering_report",
    "do_six_pages_have_distinct_visual_grammar",
    "which_pages_need_repair_and_which_layer",
]
ROLE_JUDGMENTS = {
    "cover": {
        "delta_vs_2_72": "less_boxy_but_less_finished",
        "text_visual_fusion": "partial",
        "report_like_risk": "medium",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The product_reveal module creates open space and edge-bound labels, but the product "
            "surface reads as a thin placeholder rectangle rather than a finished deck object."
        ),
        "repair_instruction": (
            "Make the generated deck surface materially richer: visible editable slide details, "
            "stronger depth, and proof labels snapped to actual product edges."
        ),
    },
    "setup": {
        "delta_vs_2_72": "visual_route_more_distinct_but_too_faint",
        "text_visual_fusion": "improved_but_weak",
        "report_like_risk": "medium",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The hero_field route is a real departure from the 2.72 panel stack, but its contours "
            "are so light that the route reads as background decoration at contact-sheet scale."
        ),
        "repair_instruction": (
            "Increase field contrast, make the destination product object dominant, and bind labels "
            "to route nodes with visible connectors."
        ),
    },
    "contrast": {
        "delta_vs_2_72": "stronger_module_difference_but_overpowered_seam",
        "text_visual_fusion": "partial",
        "report_like_risk": "medium",
        "root_cause_layer": "visual_grammar",
        "visual_observation": (
            "The before_after_theater seam is unmistakable, but the huge vertical seam overpowers "
            "the before/after proof objects and makes the slide feel like a diagram study."
        ),
        "repair_instruction": (
            "Reduce seam dominance and make the before and after product states carry the contrast, "
            "with seam copy attached as secondary evidence."
        ),
    },
    "proof": {
        "delta_vs_2_72": "workspace_structure_improved_but_empty",
        "text_visual_fusion": "partial",
        "report_like_risk": "high",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The evidence_workspace rail is different from 2.72, but the main workspace is mostly "
            "blank and thin-lined, so the page still reads as an internal proof schematic."
        ),
        "repair_instruction": (
            "Populate the workspace with inspectable source, contract, generated output, and review "
            "objects rather than a mostly empty frame."
        ),
    },
    "climax": {
        "delta_vs_2_72": "more_spacious_but_less_climactic",
        "text_visual_fusion": "weak",
        "report_like_risk": "high",
        "root_cause_layer": "renderer",
        "visual_observation": (
            "The climax uses product_reveal again, but the primary object is still a sparse wireframe; "
            "the slide lacks the scale and completion expected from a product moment."
        ),
        "repair_instruction": (
            "Give the editable PPT result a hero-scale finished surface with visible generated slide "
            "content; move secondary labels outside the hero object's negative space."
        ),
    },
    "close": {
        "delta_vs_2_72": "decision_map_distinct_but_too_abstract",
        "text_visual_fusion": "partial",
        "report_like_risk": "high",
        "root_cause_layer": "text_binding",
        "visual_observation": (
            "The decision_map is distinct, but the node labels are too small and proximity-bound; "
            "the close does not yet feel like a confident public handoff."
        ),
        "repair_instruction": (
            "Enlarge decision nodes, add explicit connector endpoints, and turn the next proof path "
            "into a clear release decision rather than tiny orbiting labels."
        ),
    },
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.74 visual evaluation missing required {label}: {path}")


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


def preview_count(workspace: Path) -> int:
    preview = workspace / "preview"
    return len(sorted(preview.glob("slide-*.png"))) if preview.exists() else 0


def validate_inputs(run272_trace: dict[str, Any], run273_trace: dict[str, Any], run272_result: dict[str, Any], run273_result: dict[str, Any]) -> None:
    if run272_trace.get("arm_id") != "run2_72_full_shape_bound_text":
        raise ValueError("Run 2.74 evaluation expected Run 2.72 full trace")
    if run273_trace.get("arm_id") != "run2_73_full_validated_scene_renderer":
        raise ValueError("Run 2.74 evaluation expected Run 2.73 full trace")
    if run272_result.get("status") != "run2_72_shape_bound_text_rerun_public_blocked":
        raise ValueError("Run 2.74 evaluation expected Run 2.72 result")
    if run273_result.get("status") != "run2_73_validated_scene_renderer_rerun_generated_public_blocked":
        raise ValueError("Run 2.74 evaluation expected Run 2.73 result")
    if [slide.get("role") for slide in run273_trace.get("slides", [])] != ROLES:
        raise ValueError("Run 2.74 evaluation expected six ordered Run 2.73 roles")


def viewer_closure() -> dict[str, Any]:
    viewer_path = PRESENTATIONS / "ppt-run-viewer.html"
    require_file(viewer_path, "PPT run viewer")
    data = build_data(PRESENTATIONS, viewer_path)
    run_ids = {run["id"] for run in data.get("runs", [])}
    run272 = next((run for run in data.get("runs", []) if run.get("id") == "2.72"), {})
    run273 = next((run for run in data.get("runs", []) if run.get("id") == "2.73"), {})
    return {
        "ppt_run_viewer": rel(viewer_path),
        "viewer_latest_run_id": "2.73",
        "current_viewer_latest_run_id": data.get("latestRunId"),
        "viewer_can_compare_2_72_and_2_73": {"2.72", "2.73"} <= run_ids,
        "run2_72_full_preview_count": len((run272.get("fullArm") or {}).get("slides") or []),
        "run2_73_full_preview_count": len((run273.get("fullArm") or {}).get("slides") or []),
        "browser_check_required_for_handoff": True,
        "browser_check_note": (
            "H requires a browser check of the viewer after writing this artifact; the script records "
            "the expected closure but does not drive the browser."
        ),
    }


def role_assessments(run273_result: dict[str, Any]) -> list[dict[str, Any]]:
    rendered_by_role = {page["role"]: page for page in run273_result.get("rendered_pages", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        page = rendered_by_role.get(role, {})
        judgment = ROLE_JUDGMENTS[role]
        module = str(page.get("visual_grammar_module") or MODULE_BY_ROLE[role])
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module,
                "layout_signature": page.get("layout_signature", ""),
                "delta_vs_2_72": judgment["delta_vs_2_72"],
                "text_visual_fusion": judgment["text_visual_fusion"],
                "report_like_risk": judgment["report_like_risk"],
                "root_cause_layer": judgment["root_cause_layer"],
                "repair_required": True,
                "visual_observation": judgment["visual_observation"],
                "repair_instruction": judgment["repair_instruction"],
                "trace_support": {
                    "source_text_binding_id": page.get("source_text_binding_id", ""),
                    "text_socket_count": len(page.get("text_socket_bindings") or []),
                    "visual_container_count": len(page.get("visual_containers") or []),
                    "source_trace_terms_visible_on_canvas": page.get("source_trace_terms_visible_on_canvas", []),
                },
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    run272_trace_path = RUN272_FULL / "trace_manifest.json"
    run273_trace_path = RUN273_FULL / "trace_manifest.json"
    run272_result_path = PACK / "results" / "run2_72_shape_bound_text_rerun_result.json"
    run273_result_path = PACK / "results" / "run2_73_validated_scene_renderer_rerun_result.json"
    run272_contact_path = RUN272_FULL / "preview" / "contact-sheet.png"
    run273_contact_path = RUN273_FULL / "preview" / "contact-sheet.png"
    run273_four_arm_path = PRESENTATIONS / "run2-73-four-arm-contact-sheet.png"

    for path, label in [
        (run272_contact_path, "Run 2.72 full contact sheet"),
        (run273_contact_path, "Run 2.73 full contact sheet"),
        (run273_four_arm_path, "Run 2.73 four-arm contact sheet"),
    ]:
        require_file(path, label)

    run272_trace = read_json(run272_trace_path)
    run273_trace = read_json(run273_trace_path)
    run272_result = read_json(run272_result_path)
    run273_result = read_json(run273_result_path)
    validate_inputs(run272_trace, run273_trace, run272_result, run273_result)

    rendered_pages = run273_result.get("rendered_pages", [])
    modules = [page.get("visual_grammar_module") for page in rendered_pages]
    signatures = [page.get("layout_signature") for page in rendered_pages]
    checks = run273_result.get("render_quality_checks", {})
    role_records = role_assessments(run273_result)
    root_layers = [record["root_cause_layer"] for record in role_records]

    return {
        "artifact_id": "run2_74_visual_quality_evaluation",
        "part": "Part H",
        "schema_version": "ppt_run2_74_visual_quality_evaluation.v1",
        "run_id": "2.74",
        "status": "run2_74_visual_quality_evaluation_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "public_ready": False,
        "quality_claim_boundary": "part_h_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.72",
            "evaluated_run": "2.73",
        },
        "input_chain": {
            "run2_72_result": rel(run272_result_path),
            "run2_73_result": rel(run273_result_path),
            "run2_72_full_trace_manifest": rel(run272_trace_path),
            "run2_73_full_trace_manifest": rel(run273_trace_path),
            "run2_72_full_contact_sheet": rel(run272_contact_path),
            "run2_73_full_contact_sheet": rel(run273_contact_path),
            "run2_73_four_arm_contact_sheet": rel(run273_four_arm_path),
            "ppt_run_viewer": rel(PRESENTATIONS / "ppt-run-viewer.html"),
        },
        "viewer_comparison_closure": viewer_closure(),
        "evaluation_questions": {
            "is_2_73_better_than_2_72": {
                "answer": "mixed_not_public_quality_pass",
                "rationale": (
                    "2.73 is better at exposing A-F workflow data and distinct visual grammar, but "
                    "2.72 still reads more finished and product-like. This is not a public-quality pass."
                ),
            },
            "is_text_fused_with_visual_structure": {
                "answer": "partial",
                "rationale": (
                    "Part F sockets are consumed and labels move near visual objects, but several labels "
                    "still rely on proximity rather than strong connector endpoints or product-edge attachment."
                ),
            },
            "does_it_still_feel_like_engineering_report": {
                "answer": "yes_but_different_failure_mode",
                "rationale": (
                    "The report-card stack is reduced, but the deck now reads as a sparse system-architecture "
                    "diagram with thin lines and abstract placeholders."
                ),
            },
            "do_six_pages_have_distinct_visual_grammar": {
                "answer": "yes_trace_and_thumbnail",
                "rationale": (
                    f"Trace has {checks.get('pages_using_expected_visual_grammar')} pages using expected grammar "
                    f"and {len(set(modules))} distinct modules across six pages."
                ),
            },
            "which_pages_need_repair_and_which_layer": {
                "answer": "renderer_first",
                "rationale": (
                    "All pages need renderer-level repair before another public-quality claim; contrast also "
                    "needs visual-grammar tuning and close needs text-binding strengthening."
                ),
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_72": "structural_variety_up_public_polish_down",
            "top_blocker": "thin_abstract_renderer_placeholders_do_not_read_as_product_presentation",
            "next_layer_to_fix": "renderer",
            "why_not_public_ready": (
                "The generated full arm proves data/workflow consumption and visual grammar variation, but "
                "its visible objects are too sparse, thin, and schematic to read as a polished public product presentation."
            ),
            "run2_73_internal_passes": {
                "expected_visual_grammar_pages": checks.get("pages_using_expected_visual_grammar"),
                "required_text_socket_pages": checks.get("pages_using_required_text_sockets"),
                "distinct_text_layout_signatures": checks.get("distinct_text_layout_signatures"),
                "empty_visual_containers": checks.get("empty_visual_container_count"),
                "floating_text_without_bound_visual_object": checks.get("floating_text_without_bound_visual_object_count"),
            },
            "run2_72_advantage": [
                "more finished visual surface",
                "stronger product mock density",
                "higher perceived polish in contact sheet",
            ],
            "run2_73_advantage": [
                "more distinct module selection",
                "less rectangular card stacking",
                "clearer data-workflow trace into visual structure",
            ],
        },
        "role_assessments": role_records,
        "root_cause_summary": {
            "primary_layer": "renderer",
            "not_primary_layer": "data_absence",
            "secondary_layers": sorted(set(root_layers) - {"renderer"}),
            "renderer_role_count": root_layers.count("renderer"),
            "visual_grammar_role_count": root_layers.count("visual_grammar"),
            "text_binding_role_count": root_layers.count("text_binding"),
            "content_role_count": root_layers.count("content"),
            "diagnosis": (
                "A-F contracts now reach the screen, but the renderer maps them into low-density abstract "
                "geometry rather than finished product surfaces with strong hierarchy."
            ),
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "delivery_artifacts_reviewed": {
            "run2_72_full_preview_count": preview_count(RUN272_FULL),
            "run2_73_full_preview_count": preview_count(RUN273_FULL),
            "run2_73_trace_slide_count": len(run273_trace.get("slides", [])),
            "run2_73_rendered_page_count": len(rendered_pages),
            "run2_73_unique_layout_signature_count": len(set(signatures)),
            "run2_73_unique_visual_module_count": len(set(modules)),
        },
        "next_required_action": "part_i_renderer_repair_from_visual_quality_evaluation",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    assessment = audit["visual_quality_assessment"]
    questions = audit["evaluation_questions"]
    lines = [
        "# Run 2.74 Visual Quality Evaluation",
        "",
        "Status: audit-only, public blocked.",
        "",
        "This is the Part H comparison loop for 2.73 vs 2.72. It does not generate a new PPT, HTML viewer, or public release.",
        "",
        "## Bottom Line",
        "",
        "- 2.73 is a workflow/rendering integration win, not a visual-quality win.",
        "- Compared with 2.72: structural variety up, public polish down.",
        "- The top blocker is thin abstract renderer placeholders, not missing A-F data.",
        "",
        "## H Questions",
        "",
        f"- Is 2.73 better than 2.72? `{questions['is_2_73_better_than_2_72']['answer']}`.",
        f"- Text fused with visual structure? `{questions['is_text_fused_with_visual_structure']['answer']}`.",
        f"- Still like an engineering report? `{questions['does_it_still_feel_like_engineering_report']['answer']}`.",
        f"- Six distinct visual grammars? `{questions['do_six_pages_have_distinct_visual_grammar']['answer']}`.",
        f"- Repair layer? `{questions['which_pages_need_repair_and_which_layer']['answer']}`.",
        "",
        "## Gates",
        "",
        f"- Data/workflow entry: `{assessment['data_workflow_entry_gate']}`.",
        f"- Viewer comparison: `{assessment['viewer_comparison_gate']}`.",
        f"- Design quality: `{assessment['design_quality_gate']}`.",
        f"- Public video readiness: `{assessment['public_video_readiness']}`.",
        "",
        "## Page Repairs",
        "",
    ]
    for record in audit["role_assessments"]:
        lines.append(
            f"- {record['slide_index']:02d} `{record['role']}` / `{record['visual_grammar_module']}`: "
            f"{record['repair_instruction']}"
        )
    lines += [
        "",
        "## Next",
        "",
        f"Part I should `{audit['next_required_action']}`.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Run 2.73 visual quality against Run 2.72.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    write_json(args.result_json, audit)
    write_report(audit, args.result_md)
    print(json.dumps({"status": audit["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
