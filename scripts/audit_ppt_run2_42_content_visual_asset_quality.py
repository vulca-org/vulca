from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_41 = PRESENTATIONS / "ppt-run2-41-full-vulca"
BAD_41 = PRESENTATIONS / "ppt-run2-41-bad-thin-content-visual-asset-compiler"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_42_content_visual_asset_quality_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_42_content_visual_asset_quality_audit.md"

NEXT_LAYER = "usecase_specific_visual_asset_semantics_editorial_composition_and_typography_hierarchy"
NEXT_ACTION = "build_run2_43_visual_asset_semantics_editorial_composition_workflow"
ROOT_CAUSE = "visual_asset_surfaces_are_still_schematic_native_shapes_not_true_product_or_scene_assets"
EXPECTED_FULL_STATUS = "same_database_content_visual_asset_compiler_applied"
EXPECTED_BAD_STATUS = "same_database_thin_content_visual_asset_control"


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.42 audit missing required {label}: {path}")


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


def slide_metrics(slide: dict[str, Any]) -> dict[str, Any]:
    metrics = slide.get("layout_metrics") or {}
    return {
        "visible_business_detail_count": int(slide.get("run2_41_visible_business_detail_count") or 0),
        "visual_asset_surface_count": int(slide.get("run2_41_visual_asset_surface_count") or 0),
        "editorial_scene_depth_score": float(slide.get("run2_41_editorial_scene_depth_score") or 0),
        "text_density_tier": metrics.get("text_density_tier", ""),
        "presentation_surface_weight": float(metrics.get("presentation_surface_weight") or 0),
        "trace_panel_visible": bool(metrics.get("trace_panel_visible")),
        "gate_ribbon_visible": bool(metrics.get("gate_ribbon_visible")),
        "visual_asset_surface_types": slide.get("run2_41_visual_asset_surface_types") or [],
    }


def validate_inputs(
    full_trace: dict[str, Any],
    bad_trace: dict[str, Any],
    run241_result: dict[str, Any],
    run240_result: dict[str, Any],
) -> None:
    if full_trace.get("arm_id") != "run2_41_full_content_visual_asset_compiler":
        raise ValueError("Run 2.42 audit expected Run 2.41 full trace")
    if bad_trace.get("arm_id") != "bad_thin_content_visual_asset_compiler":
        raise ValueError("Run 2.42 audit expected Run 2.41 bad thin trace")
    if full_trace.get("run2_41_content_visual_asset_compiler_status") != EXPECTED_FULL_STATUS:
        raise ValueError("Run 2.42 audit expected Run 2.41 full compiler status")
    if bad_trace.get("run2_41_content_visual_asset_compiler_status") != EXPECTED_BAD_STATUS:
        raise ValueError("Run 2.42 audit expected Run 2.41 bad thin control status")
    if run241_result.get("status") != "run2_41_content_visual_asset_compiler_rerun_public_blocked":
        raise ValueError("Run 2.42 audit expected Run 2.41 rerun result")
    if run241_result.get("source_generated_run_id") != "2.40":
        raise ValueError("Run 2.42 audit expected Run 2.41 to source Run 2.40")
    if run240_result.get("status") != "run2_40_visual_compiler_rerun_public_blocked":
        raise ValueError("Run 2.42 audit expected Run 2.40 visual compiler result")
    full_roles = [slide.get("role") for slide in full_trace.get("slides", [])]
    bad_roles = [slide.get("role") for slide in bad_trace.get("slides", [])]
    if len(full_roles) != 6 or len(bad_roles) != 6 or set(full_roles) != set(bad_roles):
        raise ValueError("Run 2.42 audit expected six matching full/bad slide roles")


def role_records(full_trace: dict[str, Any], bad_trace: dict[str, Any]) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    records: list[dict[str, Any]] = []
    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        full_metrics = slide_metrics(slide)
        bad_metrics = slide_metrics(bad)
        full_thickness_passed = (
            full_metrics["visible_business_detail_count"] >= 5
            and full_metrics["visual_asset_surface_count"] >= 3
            and full_metrics["editorial_scene_depth_score"] >= 0.7
            and slide.get("run2_41_public_surface_machinery_hidden") is True
            and int(slide.get("run2_41_visible_machinery_terms") or 0) == 0
            and bool(slide.get("run2_41_content_scene_payload"))
            and bool(slide.get("run2_41_visual_asset_surface_types"))
        )
        bad_boundary_passed = (
            bad.get("run2_41_public_surface_machinery_hidden") is True
            and int(bad.get("run2_41_visible_machinery_terms") or 0) == 0
            and bad_metrics["visible_business_detail_count"] <= 2
            and bad_metrics["visual_asset_surface_count"] <= 1
            and bad_metrics["editorial_scene_depth_score"] < 0.5
            and bad_metrics["trace_panel_visible"] is False
        )
        failure_reasons = [
            "visual_asset_surface_is_named_but_not_semantically_rendered_enough",
            "native_shapes_represent_assets_but_do_not_yet_feel_like_real_product_or_scene_evidence",
            "typography_hierarchy_is_functional_but_not_public_video_grade",
            "editorial_composition_has_more_content_but_still_reads_as_a_proof_board",
        ]
        if role == "climax":
            failure_reasons.append("climax_object_is_clear_but_not_cinematic_enough_for_public_video")

        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "title": slide.get("title"),
                "run2_41_code_module_ids": slide.get("run2_41_code_module_ids") or [],
                "run2_41_data_consumed": (
                    str(slide.get("run2_38_visual_direction_memory_id") or "").startswith("direction_2_38_")
                    and str(slide.get("run2_38_per_slide_visual_recipe_id") or "").startswith("recipe_2_38_")
                    and full_trace.get("run2_40_source_rerun_status") == "run2_40_visual_compiler_rerun_public_blocked"
                    and full_trace.get("run2_39_source_rerun_status") == "run2_39_public_video_visual_direction_rerun_public_blocked"
                ),
                "content_visual_asset_thickness_passed": full_thickness_passed,
                "bad_control_boundary_passed": bad_boundary_passed,
                "public_video_grade": False,
                "full_arm_metrics": full_metrics,
                "bad_control_metrics": bad_metrics,
                "aesthetic_failure_reasons": failure_reasons,
                "recommended_next_action": "convert named surfaces into usecase-specific semantic visual assets, then bind them to editorial composition and typography hierarchy gates",
            }
        )
    return records


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_41 / "trace_manifest.json"
    bad_trace_path = BAD_41 / "trace_manifest.json"
    run241_result_path = PACK / "results" / "run2_41_content_visual_asset_compiler_rerun_result.json"
    run240_result_path = PACK / "results" / "run2_40_visual_compiler_rerun_result.json"
    four_arm_path = PRESENTATIONS / "run2-41-four-arm-contact-sheet.png"
    full_series_path = PRESENTATIONS / "run2-full-skill-series-horizontal.png"

    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    run241_result = read_json(run241_result_path)
    run240_result = read_json(run240_result_path)
    validate_inputs(full_trace, bad_trace, run241_result, run240_result)
    require_file(four_arm_path, "Run 2.41 four-arm contact sheet")
    require_file(full_series_path, "Run 2 full-skill series sheet")

    records = role_records(full_trace, bad_trace)
    slide_count = len(full_trace.get("slides", []))
    bad_slide_count = len(bad_trace.get("slides", []))
    full_status_count = 1 if full_trace.get("run2_41_content_visual_asset_compiler_status") == EXPECTED_FULL_STATUS else 0
    bad_status_count = 1 if bad_trace.get("run2_41_content_visual_asset_compiler_status") == EXPECTED_BAD_STATUS else 0
    business_min5 = sum(1 for record in records if record["full_arm_metrics"]["visible_business_detail_count"] >= 5)
    surface_min3 = sum(1 for record in records if record["full_arm_metrics"]["visual_asset_surface_count"] >= 3)
    scene_depth_min = sum(1 for record in records if record["full_arm_metrics"]["editorial_scene_depth_score"] >= 0.7)
    machinery_hidden = sum(
        1
        for slide in full_trace.get("slides", [])
        if slide.get("run2_41_public_surface_machinery_hidden") is True
        and int(slide.get("run2_41_visible_machinery_terms") or 0) == 0
        and not (slide.get("layout_metrics") or {}).get("trace_panel_visible")
    )
    thin_control = sum(
        1
        for record in records
        if record["bad_control_metrics"]["visible_business_detail_count"] <= 2
        and record["bad_control_metrics"]["visual_asset_surface_count"] <= 1
        and record["bad_control_metrics"]["editorial_scene_depth_score"] < 0.5
    )
    bad_machinery_leaks = sum(
        1
        for slide in bad_trace.get("slides", [])
        if int(slide.get("run2_41_visible_machinery_terms") or 0) != 0
        or (slide.get("layout_metrics") or {}).get("trace_panel_visible")
    )
    data_consumed = sum(1 for record in records if record["run2_41_data_consumed"])
    thickness_passed = sum(1 for record in records if record["content_visual_asset_thickness_passed"])
    bad_boundary_passed = sum(1 for record in records if record["bad_control_boundary_passed"])
    forbidden_outputs = sorted(rel(path) for path in PRESENTATIONS.glob("*2-42*"))

    thickness_gate_passes = (
        slide_count == 6
        and full_status_count == 1
        and bad_status_count == 1
        and data_consumed == slide_count
        and thickness_passed == slide_count
        and bad_boundary_passed == slide_count
        and bad_machinery_leaks == 0
    )

    return {
        "schema_version": "ppt_run2_content_visual_asset_quality_audit.v1",
        "run_id": "2.42",
        "status": "run2_42_content_visual_asset_quality_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.41",
        "source_prior_generated_run": "2.40",
        "source_data_workflow_run": "2.38",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "issue_categories": [
            "content_visual_asset_thickness_closure",
            "visual_asset_semantic_realism",
            "editorial_composition_strength",
            "typography_hierarchy",
            "public_video_readiness",
        ],
        "input_chain": {
            "run2_41_full_trace_manifest": rel(full_trace_path),
            "run2_41_bad_trace_manifest": rel(bad_trace_path),
            "run2_41_rerun_result": rel(run241_result_path),
            "run2_40_rerun_result": rel(run240_result_path),
            "run2_41_full_contact_sheet": rel(FULL_41 / "preview" / "contact-sheet.png"),
            "run2_41_four_arm_contact_sheet": rel(four_arm_path),
            "run2_full_skill_series_sheet": rel(full_series_path),
            "source_rerun_verdict": run241_result.get("rerun", {}).get("best_internal_arm_verdict"),
            "source_prior_rerun_status": run240_result.get("status"),
        },
        "no_new_deck_proof": {
            "presentations_dir": rel(PRESENTATIONS),
            "forbidden_run2_42_output_glob": "*2-42*",
            "matched_run2_42_outputs": forbidden_outputs,
            "new_pptx_created": any(path.endswith(".pptx") for path in forbidden_outputs),
            "status": "pass" if not any(path.endswith(".pptx") for path in forbidden_outputs) else "blocked",
        },
        "trace_closure": {
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": slide_count,
                "content_visual_asset_compiler_applied_slides": slide_count if full_status_count else 0,
                "visible_business_detail_min5_slides": business_min5,
                "visual_asset_surface_min3_slides": surface_min3,
                "editorial_scene_depth_min07_slides": scene_depth_min,
                "machinery_hidden_slides": machinery_hidden,
            },
            "bad_control": {
                "arm_id": bad_trace.get("arm_id"),
                "slide_count": bad_slide_count,
                "thin_content_control_slides": thin_control,
                "machinery_leak_slides": bad_machinery_leaks,
            },
        },
        "visual_quality_assessment": {
            "content_visual_asset_gate": "pass_internal_only" if thickness_gate_passes else "blocked",
            "same_database_control_gate": "pass_internal_only" if bad_boundary_passed == slide_count and bad_machinery_leaks == 0 else "blocked",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "content_visual_asset_thickness_delta_from_bad_control": "proven" if thickness_gate_passes else "weak",
            "root_cause_primary": ROOT_CAUSE,
            "root_cause_secondary": [
                "Run 2.41 added visible business details and named visual asset surfaces, but the surfaces are still native schematic representations.",
                "The full arm proves data-to-content compilation, not real product imagery, cinematic scene construction, or mature typography hierarchy.",
                "The contact sheet reads richer than bad control, but still lacks the public-video-grade visual specificity expected from high-end presentation references.",
            ],
            "top_next_layer_to_thicken": NEXT_LAYER,
            "why_user_still_sees_simple_design": (
                "Run 2.41 increases information density and hides machinery, but most visual assets remain abstract native shapes. "
                "The next layer must turn each named asset surface into a usecase-specific semantic object with stronger editorial composition and typography hierarchy."
            ),
        },
        "role_records": records,
        "audit_method": {
            "same_database_rule": "Run 2.42 only reads Run 2.41, Run 2.40, and trace artifacts; it does not create a new database or workflow pack.",
            "thickness_rule": "full slides pass when visible business details >=5, visual asset surfaces >=3, scene depth >=0.7, and machinery is hidden",
            "bad_control_rule": "bad control must use the same database boundary, hide machinery, and remain thin with <=2 business details and <=1 visual asset surface",
            "public_quality_boundary": "content thickness passing does not imply public-video-grade design quality",
        },
        "next_required_action": NEXT_ACTION,
        "release_boundary": "public_blocked_until_run2_43_data_workflow_then_generated_rerun_human_visual_review_native_render_review_and_motion_review",
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    assessment = audit["visual_quality_assessment"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Run 2.42 Content Visual Asset Quality Audit",
                "",
                "Status: audit-only, public blocked.",
                "",
                "Run 2.42 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
                "",
                "Run 2.41 content visual asset thickness passes internally: the full arm consumes the same database, hides machinery, reaches at least five visible business details per slide, and reaches at least three visual asset surfaces per slide.",
                "",
                "Design quality is blocked. The main root cause is `visual_asset_surfaces_are_still_schematic_native_shapes_not_true_product_or_scene_assets`.",
                "",
                f"Next layer to thicken: `{assessment['top_next_layer_to_thicken']}`.",
                "",
                "Run 2.43 data/workflow should convert named surfaces into usecase-specific semantic visual assets, then bind those assets to editorial composition and typography hierarchy gates.",
                "",
                f"Next required action: `{audit['next_required_action']}`.",
                "",
                "Do not advance to Run 3.0.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    args = parser.parse_args()

    audit = build_audit()
    write_json(args.result_json, audit)
    write_markdown(args.result_md, audit)
    print(json.dumps({"result_json": rel(args.result_json.resolve()), "result_md": rel(args.result_md.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
