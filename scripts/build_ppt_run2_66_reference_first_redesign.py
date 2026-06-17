from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RESULTS = PACK / "results"

NEXT_ACTION = "run2_67_generate_four_arm_ppt_consuming_run2_66_reference_first_design_grammar"

REFERENCE_RECORDS = [
    {
        "reference_id": "stripe_sessions_2025_product_keynote",
        "title": "Stripe Sessions 2025 Product Keynote",
        "url": "https://stripe.com/gb/sessions/2025/product-keynote",
        "reference_type": "product_keynote_with_live_demo_and_platform_story",
        "verified_on": "2026-06-08",
        "derived_observation": (
            "A strong product keynote ties launches to a business platform shift, demo sequence, "
            "and concrete product proof instead of showing internal process panels."
        ),
    },
    {
        "reference_id": "figma_demo_platform_overview",
        "title": "Figma on-demand product demos",
        "url": "https://www.figma.com/demo/",
        "reference_type": "product_platform_demo_library",
        "verified_on": "2026-06-08",
        "derived_observation": (
            "The public page groups demos by audience outcome and product surface, not by trace metadata."
        ),
    },
    {
        "reference_id": "figma_config_2026_opening_keynote",
        "title": "Config 2026 Opening Keynote",
        "url": "https://config.figma.com/san-francisco/session/829e6ced-3257-4f5c-b675-aa72f4d1f98f/",
        "reference_type": "design_product_launch_keynote",
        "verified_on": "2026-06-08",
        "derived_observation": (
            "The public promise is framed as rethinking product development and product-building roles; "
            "the slide grammar should make the audience see a launch moment first."
        ),
    },
    {
        "reference_id": "figma_config_2024_slides_keynote",
        "title": "Config 2024 Figma Slides keynote moment",
        "url": "https://www.figma.com/blog/whats-happening-at-config-2024/",
        "reference_type": "presentation_product_launch_inside_keynote",
        "verified_on": "2026-06-08",
        "derived_observation": (
            "Figma Slides became a product reveal because the keynote itself used the product; "
            "the demo surface and story were one object."
        ),
    },
    {
        "reference_id": "apple_liquid_glass_newsroom",
        "title": "Apple Liquid Glass design language launch",
        "url": "https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/",
        "reference_type": "design_language_launch_reference",
        "verified_on": "2026-06-08",
        "derived_observation": (
            "A design-language launch is led by sensory product experience and hierarchy, not explanatory grids."
        ),
    },
]

ROLE_GRAMMAR = {
    "cover": {
        "layout_archetype": "cinematic_product_reveal",
        "public_first_read_object": "one finished launch deck emerging from a real brief and source memory",
        "composition_lock": "product_object_first_then_supporting_system",
        "scene_objects": ["launch deck", "brief capsule", "source memory field", "code rail"],
        "modules": [
            "drawRun267CinematicDeckReveal",
            "drawRun267SourceMemoryField",
            "drawRun267EditableDeckSurface",
            "drawRun267QuietTraceAnnotation",
        ],
    },
    "setup": {
        "layout_archetype": "operating_loop_stage",
        "public_first_read_object": "a design-to-code operating stage with one visible handoff path",
        "composition_lock": "stage_depth_path_not_equal_node_grid",
        "scene_objects": ["source wall", "memory compiler", "skill workflow", "code generator"],
        "modules": [
            "drawRun267LayeredOperatingStage",
            "drawRun267SourceWall",
            "drawRun267CompilerPath",
            "drawRun267OutcomePreview",
        ],
    },
    "contrast": {
        "layout_archetype": "before_after_theater",
        "public_first_read_object": "large after-state deck surface overpowering the small prompt-only result",
        "composition_lock": "asymmetric_theater_with_after_state_dominance",
        "scene_objects": ["before thumbnail", "after stage", "difference lens", "proof marker"],
        "modules": [
            "drawRun267BeforeAfterTheater",
            "drawRun267AfterStateHeroSurface",
            "drawRun267DifferenceLens",
            "drawRun267ProofMarker",
        ],
    },
    "proof": {
        "layout_archetype": "inspectable_product_workspace",
        "public_first_read_object": "review workspace where a user can inspect source, decision, output, and gate",
        "composition_lock": "workspace_scene_with_real_product_panes",
        "scene_objects": ["source pane", "decision pane", "output pane", "release gate"],
        "modules": [
            "drawRun267InspectableWorkspace",
            "drawRun267SourcePane",
            "drawRun267DecisionPane",
            "drawRun267ReleaseGate",
        ],
    },
    "climax": {
        "layout_archetype": "hero_product_surface_demo",
        "public_first_read_object": "one high-fidelity editable PPT preview with data and code visibly embedded",
        "composition_lock": "hero_surface_demo_with_depth_and_craft",
        "scene_objects": ["editable slide canvas", "code strip", "data trace drawer", "review status"],
        "modules": [
            "drawRun267HeroEditableSurface",
            "drawRun267CodeStrip",
            "drawRun267DataTraceDrawer",
            "drawRun267ReviewStatus",
        ],
    },
    "close": {
        "layout_archetype": "release_decision_map",
        "public_first_read_object": "clear decision map showing generated proof, blocked release, and next rerun",
        "composition_lock": "decision_map_with_one_dominant_next_action",
        "scene_objects": ["generated proof", "human review", "public gate", "next run"],
        "modules": [
            "drawRun267ReleaseDecisionMap",
            "drawRun267HumanReviewGate",
            "drawRun267NextRunTarget",
            "drawRun267PublicReadinessMeter",
        ],
    },
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.66 missing required input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


def validate_inputs(run265_result: dict[str, Any], run265_trace: dict[str, Any]) -> None:
    if run265_result.get("run_id") != "2.65":
        raise ValueError("Run 2.66 expected Run 2.65 result input")
    if run265_result.get("status") != "run2_65_renderer_composition_rerun_public_blocked":
        raise ValueError("Run 2.66 expected Run 2.65 public-blocked result")
    if run265_trace.get("arm_id") != "run2_65_full_renderer_composition_repair":
        raise ValueError("Run 2.66 expected Run 2.65 full trace")
    if run265_trace.get("run2_65_renderer_composition_repair_status") != (
        "run2_64_renderer_composition_repair_consumed_before_native_ppt_drawing"
    ):
        raise ValueError("Run 2.66 expected Run 2.65 to consume Run 2.64 before drawing")


def build_failure_audit() -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_66_visual_failure_audit.v1",
        "status": "run2_66_visual_failure_audit_ready_public_blocked",
        "run_id": "2.66",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "source_generated_run": "2.65",
        "failure_layer": "public_surface_art_direction_not_renderer_contracts",
        "root_causes": [
            "engineering_proof_surface_dominates_public_surface",
            "reference_data_reduced_to_trace_contracts",
            "renderer_shape_vocabulary_too_primitive",
            "public_story_lacks_scene_specific_business_evidence",
            "tests_measure_trace_not_public_video_aesthetic_grade",
        ],
        "not_primary_causes": [
            "run2_64_data_not_consumed",
            "missing_four_arm_comparison",
            "missing_trace_manifest",
        ],
        "blocked_next_action": "do_not_tune_run2_65_rectangles",
        "required_repair": (
            "compile reference-first art direction and layout grammar before any new native PPT drawing"
        ),
    }


def build_design_grammar() -> dict[str, Any]:
    records = []
    source_ids = [reference["reference_id"] for reference in REFERENCE_RECORDS]
    for role, spec in ROLE_GRAMMAR.items():
        records.append(
            {
                "reference_archetype_id": f"reference_first_archetype_2_66_{role}",
                "role": role,
                "selected_usecase_id": "usecase_design_to_production_platform_launch",
                "source_reference_ids": source_ids[:4],
                "layout_archetype": spec["layout_archetype"],
                "public_first_read_object": spec["public_first_read_object"],
                "composition_lock": spec["composition_lock"],
                "scene_specific_business_objects": spec["scene_objects"],
                "composition_contract": {
                    "forbid_rect_ellipse_only_primary_surface": True,
                    "forbid_bottom_socket_legend_as_primary_information": True,
                    "forbid_trace_terms_on_public_surface": True,
                    "max_visible_trace_terms": 0,
                    "min_depth_layers": 4,
                    "min_scene_specific_business_objects": 3,
                    "min_non_card_visual_regions": 3,
                    "must_have_one_dominant_public_object": True,
                    "must_read_without_data_skill_panel": True,
                },
                "native_ppt_required_modules": spec["modules"],
                "bad_control_probe": (
                    f"fail_if_{role}_uses_run2_65_renderer_shapes_without_reference_first_archetype"
                ),
                "required_trace_fields_for_run2_67": [
                    "run2_66_reference_archetype_id",
                    "run2_66_public_first_read_object",
                    "run2_66_layout_archetype",
                    "run2_66_art_direction_contract_id",
                    "run2_66_public_surface_aesthetic_gate_status",
                ],
            }
        )
    return {
        "schema_version": "ppt_run2_66_reference_first_design_grammar.v1",
        "status": "run2_66_reference_first_design_grammar_ready_public_blocked",
        "run_id": "2.66",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": "usecase_design_to_production_platform_launch",
        "source_generated_run": "2.65",
        "raw_media_policy": "forbidden_reference_analysis_only",
        "reference_records": REFERENCE_RECORDS,
        "role_design_grammar_records": records,
        "source_boundary": (
            "Derived observations only; no copied screenshots, source layouts, brand marks, video frames, "
            "audio, transcripts, or proprietary assets."
        ),
    }


def build_art_direction() -> dict[str, Any]:
    contracts = []
    for role, spec in ROLE_GRAMMAR.items():
        contracts.append(
            {
                "art_direction_contract_id": f"art_direction_contract_2_66_{role}",
                "role": role,
                "required_reference_archetype_id": f"reference_first_archetype_2_66_{role}",
                "copy_strategy": {
                    "public_copy_mode": "reader_outcome_first",
                    "headline_obligation": "name the commercial outcome before naming the mechanism",
                    "body_copy_obligation": "explain one visible product/business scene, not a trace checklist",
                },
                "visual_strategy": {
                    "must_show_product_or_business_scene": True,
                    "primary_scene": spec["public_first_read_object"],
                    "avoid": [
                        "equal rectangles as primary surface",
                        "bottom legend as required reading",
                        "trace ids on public canvas",
                        "generic workflow diagram without a product object",
                    ],
                },
                "content_strategy": {
                    "min_scene_specific_content_units": 4,
                    "required_units": spec["scene_objects"],
                    "max_public_visible_words": 80,
                    "public_trace_term_budget": 0,
                },
                "qa_contract": {
                    "human_review_question": (
                        "Would this read as a public product/keynote slide without seeing trace metadata?"
                    ),
                    "fail_if_answer_is_no": True,
                    "visual_review_before_run2_67_public_claim": True,
                },
            }
        )
    return {
        "schema_version": "ppt_run2_66_slide_art_direction_contracts.v1",
        "status": "run2_66_slide_art_direction_contracts_ready_public_blocked",
        "run_id": "2.66",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.65",
        "slide_art_direction_contracts": contracts,
    }


def build_workflow_gates() -> dict[str, Any]:
    required_trace_fields = [
        "run2_66_reference_archetype_id",
        "run2_66_public_first_read_object",
        "run2_66_layout_archetype",
        "run2_66_art_direction_contract_id",
        "run2_66_public_surface_aesthetic_gate_status",
        "run2_66_scene_specific_business_object_count",
        "run2_66_visible_trace_term_count",
        "run2_66_non_card_visual_region_count",
    ]
    return {
        "schema_version": "ppt_run2_66_reference_first_workflow_gates.v1",
        "status": "run2_66_reference_first_workflow_gates_ready_public_blocked",
        "run_id": "2.66",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.65",
        "bad_control_arm": "bad_run2_65_without_run2_66_reference_first_grammar",
        "required_trace_fields_for_run2_67": required_trace_fields,
        "next_generated_run_contract": {
            "run_id": "2.67",
            "must_consume_before_native_ppt_drawing": True,
            "full_arm_pass_status": "run2_66_reference_first_design_grammar_consumed_before_native_ppt_drawing",
            "bad_control_arm": "bad_run2_65_without_run2_66_reference_first_grammar",
            "required_trace_fields": required_trace_fields,
        },
        "pass_fail_checks": [
            "Every full-arm slide binds one Run 2.66 reference archetype before drawing.",
            "Every full-arm slide binds one Run 2.66 art direction contract before writing public copy.",
            "Visible trace term count is zero on the public slide canvas.",
            "Each slide has at least three non-card visual regions and four scene-specific content units.",
            "Bad control fails if it lacks Run 2.66 reference-first grammar ids.",
        ],
    }


def build_result(
    failure_audit: dict[str, Any],
    design_grammar: dict[str, Any],
    art_direction: dict[str, Any],
    workflow_gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": "2.66",
        "status": "run2_66_reference_first_redesign_ready_public_blocked",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": "usecase_design_to_production_platform_launch",
        "source_generated_run": "2.65",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "input_chain": {
            "run2_65_result": "docs/product/ppt-run2-data-skill-quality/results/run2_65_renderer_composition_rerun_result.json",
            "run2_65_full_trace": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-65-full-vulca/trace_manifest.json",
            "sources": "docs/product/ppt-run2-data-skill-quality/sources.json",
            "commercial_usecase_bank": "docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json",
        },
        "output_chain": {
            "failure_audit": "docs/product/ppt-run2-data-skill-quality/run2_66_visual_failure_audit.json",
            "design_grammar": "docs/product/ppt-run2-data-skill-quality/run2_66_reference_first_design_grammar.json",
            "art_direction": "docs/product/ppt-run2-data-skill-quality/run2_66_slide_art_direction_contracts.json",
            "workflow_gates": "docs/product/ppt-run2-data-skill-quality/run2_66_reference_first_workflow_gates.json",
        },
        "quality_delta": {
            "target_layer": "reference_first_public_surface_art_direction",
            "root_causes_fixed": len(failure_audit["root_causes"]),
            "reference_records": len(design_grammar["reference_records"]),
            "role_design_grammar_records": len(design_grammar["role_design_grammar_records"]),
            "slide_art_direction_contracts": len(art_direction["slide_art_direction_contracts"]),
            "workflow_gates": len(workflow_gates["pass_fail_checks"]),
        },
        "next_required_action": NEXT_ACTION,
        "release_boundary": "public_blocked_until_run2_67_generated_output_and_human_visual_review",
    }


def write_result_md(result: dict[str, Any]) -> None:
    lines = [
        "# Run 2.66 Reference-First Redesign",
        "",
        "Status: data/workflow repair completed, public blocked.",
        "",
        "Run 2.66 does not generate a new PPT. It records why Run 2.65 still looks weak and converts ",
        "public keynote/product-demo references into reference-first design grammar, slide art direction, ",
        "and workflow gates for the next generated rerun.",
        "",
        "## Outputs",
        "",
        "- `run2_66_visual_failure_audit.json`",
        "- `run2_66_reference_first_design_grammar.json`",
        "- `run2_66_slide_art_direction_contracts.json`",
        "- `run2_66_reference_first_workflow_gates.json`",
        "",
        "## Result",
        "",
        f"Target layer: `{result['quality_delta']['target_layer']}`.",
        "",
        "The repair moves the next run from renderer-contract proof to public surface art direction. ",
        "Run 2.67 must consume this reference-first design grammar before native PPT drawing.",
        "",
        "Do not advance to Run 3.0.",
        "",
    ]
    (RESULTS / "run2_66_reference_first_redesign_result.md").write_text("\n".join(lines), encoding="utf-8")


def build_artifacts() -> dict[str, Any]:
    run265_result = read_json(RESULTS / "run2_65_renderer_composition_rerun_result.json")
    run265_trace = read_json(
        ROOT
        / "outputs"
        / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
        / "presentations"
        / "ppt-run2-65-full-vulca"
        / "trace_manifest.json"
    )
    validate_inputs(run265_result, run265_trace)
    failure_audit = build_failure_audit()
    design_grammar = build_design_grammar()
    art_direction = build_art_direction()
    workflow_gates = build_workflow_gates()
    result = build_result(failure_audit, design_grammar, art_direction, workflow_gates)
    return {
        "failure_audit": failure_audit,
        "design_grammar": design_grammar,
        "art_direction": art_direction,
        "workflow_gates": workflow_gates,
        "result": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifacts = build_artifacts()
    if args.check:
        print(json.dumps({"status": artifacts["result"]["status"], "run_id": "2.66"}, indent=2))
        return 0
    write_json(PACK / "run2_66_visual_failure_audit.json", artifacts["failure_audit"])
    write_json(PACK / "run2_66_reference_first_design_grammar.json", artifacts["design_grammar"])
    write_json(PACK / "run2_66_slide_art_direction_contracts.json", artifacts["art_direction"])
    write_json(PACK / "run2_66_reference_first_workflow_gates.json", artifacts["workflow_gates"])
    write_json(RESULTS / "run2_66_reference_first_redesign_result.json", artifacts["result"])
    write_result_md(artifacts["result"])
    print(
        json.dumps(
            {
                "run_id": "2.66",
                "status": artifacts["result"]["status"],
                "next_required_action": artifacts["result"]["next_required_action"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
