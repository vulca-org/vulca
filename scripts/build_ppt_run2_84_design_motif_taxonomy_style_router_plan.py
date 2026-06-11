#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RESULT = PACK / "run2_84_design_motif_taxonomy_style_router_plan.json"

CONSUMED_SOURCES = [
    "docs/product/ppt-run2-data-skill-quality/results/run2_83_workflow_taxonomy_bias_audit.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_source_quality_audit.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_tutorial_to_design_moves.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
    "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
    "docs/product/ppt-run2-data-skill-quality/run2_66_reference_first_design_grammar.json",
    "docs/product/ppt-run2-data-skill-quality/run2_43_editorial_composition_typography_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_49_readability_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
]

PRESERVED_GATES = [
    "traceability",
    "source_availability",
    "validator_required_files",
    "public_release_block",
    "negative_controls",
    "viewer_metadata_routes",
    "reproducible_scripts",
]

MOTIF_FIELDS = [
    "motif_id",
    "motif_family",
    "layout_recipe",
    "spatial_relation",
    "typography_treatment",
    "visual_density",
    "style_family",
    "scenario_fit",
    "renderer_recipe",
    "motif_fidelity_checks",
]

FIDELITY_CHECKS = [
    "motif_family_visible",
    "not_rectangle_only",
    "text_integrated_with_shape",
]

PRESERVED_VISUAL_EFFECTS = [
    "modular_matrix",
    "rectangle_layering",
    "overlay_sticker_stack",
    "product_theater",
    "editorial_text_density",
]

STYLE_FAMILIES = [
    "public_product_keynote",
    "technical_editorial",
    "dense_teaching_walkthrough",
    "financial_decision_brief",
    "high_contrast_demo",
]

SCENARIOS = [
    "product_pitch",
    "teaching_tutorial",
    "financial_product",
    "technical_proof",
    "public_video_demo",
]

MOTIF_DEFINITIONS = [
    {
        "motif_family": "editorial_text_field",
        "style_family": "technical_editorial",
        "visual_density": "dense",
        "scenario_fit": ["product_pitch", "technical_proof", "teaching_tutorial"],
        "composition_pattern": "large editorial copy block paired with one anchored product/evidence surface",
        "reading_path": "headline_to_subhead_to_proof_sentence_to_object_caption",
        "focal_object_strategy": "text-heavy but anchored to visible product surface or source-to-memory flow",
        "text_to_object_relation": "main text block sits on a shared axis with the product surface",
        "object_to_background_relation": "quiet field supports dense text without turning into dashboard cards",
        "evidence_relation": "proof sentence attaches to one evidence strip or source-memory route",
        "paragraph_behavior": "paragraph block is intentionally composed, not a pile of labels",
        "caption_behavior": "caption locks to product edge or evidence object",
        "source_trace": [
            "run2_43_editorial_composition_typography_memory.json",
            "run2_49_readability_memory.json",
            "run2_81_text_composition_typography_plan.json",
        ],
    },
    {
        "motif_family": "modular_matrix",
        "style_family": "financial_decision_brief",
        "visual_density": "balanced",
        "scenario_fit": ["financial_product", "technical_proof", "product_pitch"],
        "composition_pattern": "matrix of unequal modules with one dominant proof object and secondary comparison cells",
        "reading_path": "claim_to_matrix_header_to_dominant_cell_to_supporting_cells",
        "focal_object_strategy": "one large module carries the business decision while smaller modules carry evidence",
        "text_to_object_relation": "cell copy is embedded inside or directly beside matrix modules",
        "object_to_background_relation": "matrix sits on a full-canvas grid with outer breathing room",
        "evidence_relation": "evidence cards become matrix cells, not floating chips",
        "paragraph_behavior": "short structured copy inside cells with visible grouping",
        "caption_behavior": "captions attach to module headers",
        "source_trace": [
            "run2_73_visual_grammar_modules.json",
            "run2_73_tutorial_to_design_moves.json",
        ],
    },
    {
        "motif_family": "overlay_sticker_stack",
        "style_family": "high_contrast_demo",
        "visual_density": "climax",
        "scenario_fit": ["public_video_demo", "product_pitch", "teaching_tutorial"],
        "composition_pattern": "layered stickers, callouts, and cropped objects over a dominant product surface",
        "reading_path": "hero_object_to_overlay_callout_to_caption_to_release_gate",
        "focal_object_strategy": "large product object remains dominant while overlays add energy and emphasis",
        "text_to_object_relation": "callout text physically touches or overlaps the object it explains",
        "object_to_background_relation": "foreground stack creates depth without debug annotations",
        "evidence_relation": "evidence is a visible sticker or badge attached to product surface",
        "paragraph_behavior": "short punchy copy blocks, never loose trace labels",
        "caption_behavior": "caption becomes a visible product annotation, not metadata",
        "source_trace": [
            "run2_73_tutorial_to_design_moves.json",
            "run2_82_renderer_product_surface_text_composition_rerun_result.json",
        ],
    },
    {
        "motif_family": "product_theater",
        "style_family": "public_product_keynote",
        "visual_density": "sparse",
        "scenario_fit": ["product_pitch", "public_video_demo"],
        "composition_pattern": "single product surface staged as the main character with supporting narrative copy",
        "reading_path": "product_surface_to_headline_to_subhead_to_caption",
        "focal_object_strategy": "product mock is large enough to read as a real product surface",
        "text_to_object_relation": "headline and subhead orbit the product, leaving the product dominant",
        "object_to_background_relation": "full-slide stage field with controlled depth and shadow",
        "evidence_relation": "proof object appears as a purposeful product detail, not a status chip",
        "paragraph_behavior": "minimal cinematic copy with one proof sentence",
        "caption_behavior": "caption attaches to product mock edge",
        "source_trace": [
            "run2_73_visual_grammar_modules.json",
            "run2_80_visual_quality_evaluation.json",
        ],
    },
    {
        "motif_family": "before_after_theater",
        "style_family": "high_contrast_demo",
        "visual_density": "balanced",
        "scenario_fit": ["product_pitch", "teaching_tutorial", "technical_proof"],
        "composition_pattern": "before and after surfaces separated by a visible transformation path",
        "reading_path": "before_state_to_transformation_object_to_after_state_to_delta_caption",
        "focal_object_strategy": "the transformation object is central and larger than labels",
        "text_to_object_relation": "delta copy sits on the transformation path, not in corner chips",
        "object_to_background_relation": "two surfaces share one stage to avoid a report-grid feel",
        "evidence_relation": "evidence appears as concrete before/after visual delta",
        "paragraph_behavior": "one short explanatory copy block per state",
        "caption_behavior": "caption names the visual delta",
        "source_trace": [
            "run2_73_visual_grammar_modules.json",
            "run2_73_tutorial_to_design_moves.json",
        ],
    },
    {
        "motif_family": "evidence_workspace",
        "style_family": "dense_teaching_walkthrough",
        "visual_density": "dense",
        "scenario_fit": ["technical_proof", "teaching_tutorial", "financial_product"],
        "composition_pattern": "workspace surface with source, memory, workflow, and output objects visibly connected",
        "reading_path": "source_object_to_memory_object_to_workflow_object_to_output_object",
        "focal_object_strategy": "workflow objects are real surfaces with labels embedded inside the route",
        "text_to_object_relation": "text becomes embedded notes in the workspace, not standalone chips",
        "object_to_background_relation": "objects sit on a shared workbench plane with connectors",
        "evidence_relation": "proof is shown as connected artifacts rather than abstract claims",
        "paragraph_behavior": "explanatory copy appears as one readable workspace note",
        "caption_behavior": "caption names what the viewer should inspect",
        "source_trace": [
            "run2_73_source_quality_audit.json",
            "run2_73_renderer_adapter_contracts.json",
        ],
    },
    {
        "motif_family": "decision_map",
        "style_family": "financial_decision_brief",
        "visual_density": "balanced",
        "scenario_fit": ["financial_product", "technical_proof", "product_pitch"],
        "composition_pattern": "decision path from evidence to release gate with one clear recommendation node",
        "reading_path": "evidence_nodes_to_decision_path_to_recommendation",
        "focal_object_strategy": "recommendation node is visually stronger than process labels",
        "text_to_object_relation": "decision copy is embedded in path nodes",
        "object_to_background_relation": "path floats over a quiet field with visible hierarchy",
        "evidence_relation": "evidence objects feed directly into the decision node",
        "paragraph_behavior": "compact decision copy, not status inventory",
        "caption_behavior": "caption states the release decision boundary",
        "source_trace": [
            "run2_73_visual_grammar_modules.json",
            "run2_83_workflow_taxonomy_bias_audit.json",
        ],
    },
]

ROLE_BINDINGS = [
    ("cover", "product_reveal", "motif_2_84_product_theater", "motif_2_84_editorial_text_field", "public_product_keynote", "product_pitch"),
    ("setup", "hero_field", "motif_2_84_editorial_text_field", "motif_2_84_evidence_workspace", "technical_editorial", "teaching_tutorial"),
    ("contrast", "before_after_theater", "motif_2_84_before_after_theater", "motif_2_84_modular_matrix", "high_contrast_demo", "product_pitch"),
    ("proof", "evidence_workspace", "motif_2_84_modular_matrix", "motif_2_84_evidence_workspace", "dense_teaching_walkthrough", "technical_proof"),
    ("climax", "product_reveal", "motif_2_84_overlay_sticker_stack", "motif_2_84_product_theater", "high_contrast_demo", "public_video_demo"),
    ("close", "decision_map", "motif_2_84_decision_map", "motif_2_84_modular_matrix", "financial_decision_brief", "financial_product"),
]


def source_inputs() -> list[dict[str, Any]]:
    return [
        {
            "path": source,
            "available": (ROOT / source).exists(),
            "usage": "design_motif_style_router_source",
        }
        for source in CONSUMED_SOURCES
    ]


def motif_record(definition: dict[str, Any]) -> dict[str, Any]:
    family = definition["motif_family"]
    return {
        "motif_id": f"motif_2_84_{family}",
        "motif_family": family,
        "layout_recipe": {
            "composition_pattern": definition["composition_pattern"],
            "reading_path": definition["reading_path"],
            "focal_object_strategy": definition["focal_object_strategy"],
        },
        "spatial_relation": {
            "text_to_object_relation": definition["text_to_object_relation"],
            "object_to_background_relation": definition["object_to_background_relation"],
            "evidence_relation": definition["evidence_relation"],
        },
        "typography_treatment": {
            "hierarchy_model": "headline_subhead_proof_caption",
            "paragraph_behavior": definition["paragraph_behavior"],
            "caption_behavior": definition["caption_behavior"],
        },
        "visual_density": definition["visual_density"],
        "style_family": definition["style_family"],
        "scenario_fit": definition["scenario_fit"],
        "renderer_recipe": {
            "native_ppt_primitives": [
                "editable text",
                "native shape",
                "image placeholder",
                "connector",
                "clipped surface",
            ],
            "forbidden_renderer_shortcuts": [
                "generic rectangles only",
                "traceability labels on canvas",
            ],
            "metadata_routes": [
                "source trace",
                "motif id",
                "style family",
                "fidelity checks",
            ],
        },
        "motif_fidelity_checks": FIDELITY_CHECKS,
        "source_trace": definition["source_trace"],
    }


def style_router_rules() -> list[dict[str, Any]]:
    return [
        {
            "scenario": "product_pitch",
            "primary_style_family": "public_product_keynote",
            "allowed_motif_families": ["product_theater", "before_after_theater", "editorial_text_field"],
            "density_policy": "prefer sparse or balanced unless proof burden requires a matrix",
            "business_fit_rationale": "make the product surface and commercial transformation inspectable first",
        },
        {
            "scenario": "teaching_tutorial",
            "primary_style_family": "dense_teaching_walkthrough",
            "allowed_motif_families": ["evidence_workspace", "editorial_text_field", "overlay_sticker_stack"],
            "density_policy": "allow dense explanatory copy when it is grouped into a readable route",
            "business_fit_rationale": "teach the workflow without turning the slide into loose labels",
        },
        {
            "scenario": "financial_product",
            "primary_style_family": "financial_decision_brief",
            "allowed_motif_families": ["modular_matrix", "decision_map", "before_after_theater"],
            "density_policy": "use balanced density with visible decision hierarchy",
            "business_fit_rationale": "financial audiences need comparison, risk, and decision objects",
        },
        {
            "scenario": "technical_proof",
            "primary_style_family": "technical_editorial",
            "allowed_motif_families": ["evidence_workspace", "modular_matrix", "editorial_text_field"],
            "density_policy": "use dense proof only when hierarchy and object anchors are explicit",
            "business_fit_rationale": "technical proof needs traceable evidence while staying presentation-like",
        },
        {
            "scenario": "public_video_demo",
            "primary_style_family": "high_contrast_demo",
            "allowed_motif_families": ["product_theater", "overlay_sticker_stack", "before_after_theater"],
            "density_policy": "prefer high-contrast, low-label scenes with one climactic visual object",
            "business_fit_rationale": "video needs immediate visual read and less audit vocabulary on canvas",
        },
    ]


def page_role_motif_bindings() -> list[dict[str, Any]]:
    return [
        {
            "role": role,
            "slide_index": index,
            "visual_grammar_module": module,
            "primary_motif_id": primary,
            "fallback_motif_id": fallback,
            "style_family": style,
            "scenario": scenario,
            "required_motif_fidelity_checks": FIDELITY_CHECKS,
        }
        for index, (role, module, primary, fallback, style, scenario) in enumerate(ROLE_BINDINGS, start=1)
    ]


def build_plan() -> dict[str, Any]:
    return {
        "artifact_id": "run2_84_design_motif_taxonomy_style_router_plan",
        "part": "Part P1",
        "schema_version": "ppt_run2_84_design_motif_taxonomy_style_router_plan.v1",
        "run_id": "2.84",
        "status": "run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked",
        "stage_policy": "part_p1_design_motif_taxonomy_and_style_router_plan_only_no_renderer_rerun_no_public_release",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "design_motif_contract_only_no_visual_quality_verdict_no_public_release",
        "consumed_sources": CONSUMED_SOURCES,
        "source_inputs": source_inputs(),
        "source_p0_audit": {
            "status": "run2_83_workflow_taxonomy_bias_audit_ready_public_blocked",
            "next_required_action": "part_p1_design_motif_taxonomy_and_style_router_plan",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_83_workflow_taxonomy_bias_audit.json",
        },
        "preserved_visual_effects": PRESERVED_VISUAL_EFFECTS,
        "design_motif_taxonomy": [motif_record(definition) for definition in MOTIF_DEFINITIONS],
        "style_router_rules": style_router_rules(),
        "page_role_motif_bindings": page_role_motif_bindings(),
        "engineering_gate_bridge": {
            "preserve_existing_gates": PRESERVED_GATES,
            "traceability_route": "viewer_metadata_and_speaker_notes",
            "slide_canvas_traceability_allowed": False,
            "public_release_gate_remains_blocked": True,
            "validator_remains_authoritative": True,
        },
        "renderer_contract_preview": {
            "next_renderer_must_consume_p1": True,
            "required_fields_for_next_rerun": MOTIF_FIELDS,
            "does_not_execute_renderer": True,
        },
        "no_new_renderer_proof": {
            "new_ppt_created": False,
            "new_html_created": False,
            "viewer_updated": False,
        },
        "next_required_action": "part_p2_renderer_rerun_from_design_motif_layer_and_style_router",
    }


def main() -> None:
    plan = build_plan()
    RESULT.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {RESULT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
