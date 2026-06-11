from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "README.md",
    "sources.json",
    "source_summaries.md",
    "commercial_brief.md",
    "design_notes.md",
    "narrative_rules.json",
    "slide_patterns.json",
    "style_tokens.json",
    "asset_rules.json",
    "evaluation_rubric.md",
    "vulca_ppt_skill.md",
    "deck_outline.json",
    "baseline_prompt.md",
    "vulca_generation_brief.md",
    "gemini_review_prompt.md",
    "results/README.md",
    "results/comparison_report.md",
]


RUN1_REQUIRED_FILES = [
    "tutorial_notes.md",
    "design_memory.json",
    "results/asset_provenance.json",
    "results/iteration_log.md",
    "results/render_check.md",
]


RUN1_5_REQUIRED_FILES = [
    *RUN1_REQUIRED_FILES,
    "experiment_protocol.md",
    "bad_data_generation_brief.md",
    "results/ablation_report.md",
    "results/ablation_report.json",
    "results/comparison_report.json",
    "results/delivery_gate.md",
]


RUN2_REQUIRED_FILES = [
    "README.md",
    "commercial_case.md",
    "sources.json",
    "multimodal_database.json",
    "visual_learning_targets.json",
    "visual_target_components.json",
    "video_demo_beat_map.json",
    "motion_learning_targets.json",
    "presentation_sequence_components.json",
    "visual_repair_policy.json",
    "run2_7_commercial_usecase.json",
    "run2_7_multimodal_source_records.json",
    "run2_7_design_memory.json",
    "run2_7_workflow_policy.json",
    "source_cards/README.md",
    "video_cards/README.md",
    "evidence_memory.json",
    "aesthetic_memory.json",
    "asset_memory.json",
    "narrative_spine.json",
    "slide_archetypes.json",
    "aesthetic_rubric.md",
    "vulca_ppt_skill.md",
    "skill_workflow.json",
    "generation_briefs/README.md",
    "generation_briefs/prompt_only.md",
    "generation_briefs/run1_5_skill.md",
    "generation_briefs/run2_skill.md",
    "generation_briefs/bad_aesthetic_memory.md",
    "results/README.md",
    "results/comparison_report.md",
    "results/delivery_gate.md",
]


RUN2_8_REQUIRED_FILES = [
    "run2_8_tutorial_decomposition.json",
    "run2_8_executable_design_memory.json",
    "run2_8_workflow_gate_matrix.json",
    "results/trace_manifest_contract.json",
]

RUN2_73_REQUIRED_FILES = [
    "run2_73_visual_grammar_modules.json",
    "run2_73_renderer_adapter_contracts.json",
    "run2_73_text_binding_strategy.json",
    "results/run2_73_validated_scene_renderer_rerun_result.json",
    "results/run2_74_visual_quality_evaluation.json",
    "results/run2_75_renderer_repair_rerun_result.json",
    "results/run2_76_visual_quality_evaluation.json",
    "run2_76_visual_grammar_renderer_repair_plan.json",
    "results/run2_77_visual_grammar_renderer_repair_rerun_result.json",
    "results/run2_78_visual_quality_evaluation.json",
    "results/run2_79_renderer_art_direction_repair_rerun_result.json",
    "results/run2_80_visual_quality_evaluation.json",
    "run2_81_text_composition_typography_plan.json",
    "results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
    "results/run2_83_workflow_taxonomy_bias_audit.json",
    "run2_84_design_motif_taxonomy_style_router_plan.json",
    "results/run2_85_design_motif_renderer_rerun_result.json",
]


RUN1_5_REQUIRED_MEMORY_FIELDS = [
    "evidence_id",
    "source_role",
    "observation",
    "design_rule",
    "slide_primitive",
    "layout_constraint",
    "qa_signal",
]


RUN1_5_SOURCE_ROLES = {"brief", "source", "tutorial", "review"}
RUN1_5_SLIDE_PRIMITIVES = {"cockpit", "learning_map", "comparison_delta", "qa_gate", "decision_table"}
RUN2_SOURCE_TYPES = {"commercial_case", "tutorial", "video", "design_article", "reference_deck"}
RUN2_ALLOWED_USES = {"short_analysis", "derived_rules_only", "visual_inspiration", "timestamped_observation_only"}
RUN2_RHYTHM_ROLES = {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}
RUN2_MOTION_ROLES = {
    "attention_reset",
    "before_after_reveal",
    "proof_build",
    "scale_emphasis",
    "release_handoff",
}
RUN2_MULTIMODAL_MODALITIES = {"text", "image_reference", "video", "audio", "transcript", "interaction"}
RUN2_MULTIMODAL_ALLOWED_STORAGE = {
    "metadata_only",
    "derived_observations_only",
    "generated_assets_only",
    "local_untracked_cache_only",
}
RUN2_ASSET_TYPES = {
    "generated_background",
    "editable_svg",
    "native_shapes",
    "chart",
    "diagram",
    "video_derived_reference",
}
RUN2_EXTRACTION_UNIT_FIELDS = [
    "unit_id",
    "source_anchor",
    "derived_rule",
    "slide_role",
    "execution_guard",
    "qa_probe",
]
RUN2_FORBIDDEN_MEDIA_REFERENCE_MARKERS = (
    "http://",
    "https://",
    "data:image",
    "base64,",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp4",
    ".mov",
    ".mp3",
    ".wav",
    ".pptx",
    ".key",
)
RUN2_6R_REPAIR_IDS = {
    "repair_editorial_typography_system",
    "repair_spacing_token_visibility",
    "repair_climax_editorial_spread",
    "repair_theme_differentiation_from_run2_5",
    "repair_mini_preview_fidelity",
}
RUN2_6R_REPAIR_FIELDS = [
    "id",
    "target_slide_roles",
    "source_policy_ids",
    "typography_delta",
    "spacing_delta",
    "composition_delta",
    "theme_delta",
    "must_differ_from",
    "native_ppt_requirements",
    "qa_probe",
    "release_boundary",
]
RUN2_6R_REPAIR_ROLES = {"cover", "setup", "contrast", "proof", "climax", "close"}
RUN2_7_MEMORY_FIELDS = [
    "id",
    "source_record_ids",
    "applicable_usecases",
    "applicable_slide_roles",
    "typography_rules",
    "spacing_rules",
    "composition_rules",
    "rhythm_rules",
    "native_ppt_generation_requirements",
    "forbidden_patterns",
    "qa_probes",
    "release_boundary",
]
RUN2_7_TRACE_FIELDS = {
    "run2_7_usecase_id",
    "run2_7_source_record_ids",
    "run2_7_design_memory_ids",
    "run2_7_workflow_decision_ids",
    "run2_7_delta_from_run2_6r",
    "run2_7_quality_gate",
}
RUN2_8_DECOMPOSITION_FIELDS = [
    "id",
    "source_record_ids",
    "source_ids",
    "modality_mix",
    "tutorial_anchor",
    "observed_design_move",
    "derived_rule",
    "code_generation_binding",
    "native_ppt_obligation",
    "layout_budget",
    "failure_probe",
    "anti_copy_boundary",
    "qa_probe",
    "release_boundary",
]
RUN2_8_MEMORY_BINDING_FIELDS = [
    "id",
    "decomposition_unit_ids",
    "applies_to_slide_roles",
    "design_token",
    "code_binding",
    "native_ppt_constraints",
    "typography_constraints",
    "spacing_constraints",
    "composition_constraints",
    "negative_control_failure",
    "qa_probe",
    "release_boundary",
]
RUN2_8_GATE_FIELDS = [
    "id",
    "slide_role",
    "decomposition_unit_ids",
    "memory_binding_ids",
    "required_code_bindings",
    "layout_budget",
    "pass_fail_checks",
    "trace_fields",
    "public_release_gate",
]
RUN2_8_TRACE_FIELDS = {
    "run2_8_decomposition_unit_ids",
    "run2_8_memory_binding_ids",
    "run2_8_gate_matrix_ids",
    "run2_8_code_binding_ids",
    "run2_8_layout_budget",
    "run2_8_visual_delta_from_run2_7",
}
RUN2_8_RELEASE_BOUNDARY = "public_blocked_until_native_render_trace_and_human_review"
RUN2_8_SELECTION_CHAIN = {
    "commercial_usecase",
    "run2_8_decomposition_units",
    "run2_8_executable_memory_bindings",
    "run2_8_gate_matrix",
    "native_ppt_code_generation",
    "layout_quality_gate",
    "delivery_gate",
    "visual_qa_gate",
}
RUN2_8_WORKFLOW_STAGE_INPUTS = {
    "decompose_run2_8_tutorial_video_units": {
        "run2_8_tutorial_decomposition.json",
        "run2_7_multimodal_source_records.json",
        "sources.json",
    },
    "select_run2_8_executable_design_memory": {
        "run2_8_tutorial_decomposition.json",
        "run2_8_executable_design_memory.json",
    },
    "apply_run2_8_workflow_gate_matrix": {
        "run2_8_tutorial_decomposition.json",
        "run2_8_executable_design_memory.json",
        "run2_8_workflow_gate_matrix.json",
        "results/trace_manifest_contract.json",
    },
}
RUN2_8_CODE_BINDING_TERMS = {"fontSize", "bbox", "spacing", "heroObject", "beforeAfter", "workflowGate"}
RUN2_73_VISUAL_GRAMMAR_STAGE_POLICY = (
    "part_e_visual_grammar_modules_only_no_renderer_rerun_no_public_release"
)
RUN2_73_VISUAL_GRAMMAR_STATUS = "run2_73_visual_grammar_modules_ready_public_blocked"
RUN2_73_VISUAL_GRAMMAR_ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
RUN2_73_VISUAL_GRAMMAR_MODULE_IDS = {
    "hero_field",
    "before_after_theater",
    "evidence_workspace",
    "product_reveal",
    "decision_map",
}
RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP = {
    "cover": "product_reveal",
    "setup": "hero_field",
    "contrast": "before_after_theater",
    "proof": "evidence_workspace",
    "climax": "product_reveal",
    "close": "decision_map",
}
RUN2_73_VISUAL_GRAMMAR_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/run2_66_reference_first_design_grammar.json",
    "docs/product/ppt-run2-data-skill-quality/run2_43_semantic_visual_asset_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_46_visual_object_grammar_memory.json",
}
RUN2_73_VISUAL_GRAMMAR_FORBIDDEN_SCOPE = {
    "renderer_rerun",
    "pptx_output",
    "html_viewer",
    "public_release",
}
RUN2_73_VISUAL_GRAMMAR_SUCCESS_FLAGS = {
    "every_page_has_non_rectangular_or_non_card_main_structure",
    "every_main_structure_serves_content",
    "all_requested_modules_defined",
    "no_module_depends_on_copied_source_media",
    "public_surface_trace_terms_hidden",
}
RUN2_73_RENDERER_ADAPTER_STAGE_POLICY = (
    "part_e2_renderer_adapter_contracts_only_no_renderer_rerun_no_public_release"
)
RUN2_73_RENDERER_ADAPTER_STATUS = "run2_73_renderer_adapter_contracts_ready_public_blocked"
RUN2_73_RENDERER_ADAPTER_NEXT_REQUIRED_ACTION = "renderer_execute_from_d2_d3_e_adapter_manifest"
RUN2_73_RENDERER_ADAPTER_SOURCE_POINTERS = {
    "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
    "source_renderer_input_validation": "run2_73_renderer_input_validation.json",
    "source_visual_grammar_modules": "run2_73_visual_grammar_modules.json",
}
RUN2_73_RENDERER_ADAPTER_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
}
RUN2_73_RENDERER_ADAPTER_SOURCE_FILES = {
    "run2_73_scene_plan_expansion.json",
    "run2_73_renderer_input_validation.json",
    "run2_73_visual_grammar_modules.json",
}
RUN2_73_TEXT_BINDING_STAGE_POLICY = (
    "part_f_text_binding_strategy_only_no_renderer_rerun_no_public_release"
)
RUN2_73_TEXT_BINDING_STATUS = "run2_73_text_binding_strategy_ready_public_blocked"
RUN2_73_TEXT_BINDING_NEXT_REQUIRED_ACTION = "part_g_renderer_rerun_from_validated_text_binding_strategy"
RUN2_73_TEXT_BINDING_SOURCE_POINTERS = {
    "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
    "source_renderer_adapter_contracts": "run2_73_renderer_adapter_contracts.json",
    "source_visual_grammar_modules": "run2_73_visual_grammar_modules.json",
    "source_slide_story": "run2_74_slide_story.json",
    "source_content_quality_audit": "run2_74_content_quality_audit.json",
}
RUN2_73_TEXT_BINDING_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
    "docs/product/ppt-run2-data-skill-quality/run2_74_slide_story.json",
    "docs/product/ppt-run2-data-skill-quality/run2_74_content_quality_audit.json",
}
RUN2_73_TEXT_BINDING_SOURCE_FILES = {
    "run2_73_scene_plan_expansion.json",
    "run2_73_renderer_adapter_contracts.json",
    "run2_73_visual_grammar_modules.json",
    "run2_74_slide_story.json",
    "run2_74_content_quality_audit.json",
}
RUN2_73_TEXT_BINDING_REQUIRED_SOCKETS = {
    "headline_socket",
    "proof_label_sockets",
    "supporting_copy_socket",
    "callout_sockets",
    "viewer_note_socket",
}
RUN2_73_TEXT_BINDING_VISUAL_OBJECT_TYPES = {
    "product edge",
    "field route",
    "comparison seam",
    "evidence rail",
    "decision node",
    "negative space pocket",
    "connector endpoint",
}
RUN2_73_TEXT_BINDING_ROLES = {
    "headline",
    "proof_label",
    "supporting_copy",
    "callout",
    "viewer_note",
}
RUN2_73_TEXT_BINDING_HIERARCHY_LEVELS = {
    "h1",
    "h2",
    "proof_label",
    "supporting_copy",
    "callout",
    "viewer_note",
}
RUN2_73_TEXT_BINDING_OVERFLOW_BEHAVIORS = {
    "truncate_with_route_to_viewer",
    "route_to_speaker_note",
    "route_to_html_viewer_metadata",
}
RUN2_73_TEXT_BINDING_SOURCE_ARTIFACTS = {
    "run2_73_scene_plan_expansion",
    "run2_73_renderer_adapter_contracts",
}
RUN2_73_TEXT_BINDING_FORBIDDEN_PATTERNS = {
    "empty text box",
    "generic rectangle label",
    "duplicated headline/supporting copy",
    "text floating without bound visual object",
    "all slides using the same text layout",
}
RUN2_73_VALIDATED_RENDERER_STATUS = "run2_73_validated_scene_renderer_rerun_generated_public_blocked"
RUN2_73_VALIDATED_RENDERER_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
}
RUN2_73_VALIDATED_RENDERER_REQUIRED_OUTPUTS = {
    "html_viewer",
    "pptx",
    "ppt_run_viewer",
}
RUN2_73_VALIDATED_RENDERER_REQUIRED_CHECKS = {
    "empty_visual_container_count": 0,
    "floating_text_without_bound_visual_object_count": 0,
    "generic_rectangle_label_count": 0,
    "source_trace_terms_visible_on_canvas_count": 0,
    "distinct_text_layout_signatures": 6,
    "pages_using_expected_visual_grammar": 6,
    "pages_using_required_text_sockets": 6,
}
RUN2_74_VISUAL_QUALITY_EVALUATION_STATUS = "run2_74_visual_quality_evaluation_public_blocked"
RUN2_74_VISUAL_QUALITY_QUESTION_IDS = {
    "is_2_73_better_than_2_72",
    "is_text_fused_with_visual_structure",
    "does_it_still_feel_like_engineering_report",
    "do_six_pages_have_distinct_visual_grammar",
    "which_pages_need_repair_and_which_layer",
}
RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS = {
    "renderer",
    "visual_grammar",
    "text_binding",
    "content",
}
RUN2_74_TEXT_VISUAL_FUSION_VALUES = {
    "improved_but_weak",
    "partial",
    "weak",
}
RUN2_74_REPORT_RISK_VALUES = {"low", "medium", "high"}
RUN2_75_RENDERER_REPAIR_STATUS = "run2_75_renderer_repair_rerun_generated_public_blocked"
RUN2_75_RENDERER_REPAIR_CONSUMED_SOURCE_PATHS = RUN2_73_VALIDATED_RENDERER_CONSUMED_SOURCE_PATHS | {
    "docs/product/ppt-run2-data-skill-quality/results/run2_74_visual_quality_evaluation.json",
}
RUN2_75_RENDERER_REPAIR_DIRECTIVES = {
    "h_repair_instruction_consumed",
    "concrete_product_surface",
    "higher_visual_density",
    "stronger_text_visual_attachment",
    "public_polish_not_claimed",
}
RUN2_75_RENDERER_REPAIR_REQUIRED_CHECKS = {
    "empty_visual_container_count": 0,
    "floating_text_without_bound_visual_object_count": 0,
    "generic_rectangle_label_count": 0,
    "source_trace_terms_visible_on_canvas_count": 0,
    "pages_using_expected_visual_grammar": 6,
    "pages_using_required_text_sockets": 6,
    "pages_with_h_repair_directive_consumed": 6,
    "pages_with_concrete_product_surface": 6,
    "pages_with_stronger_connector_or_edge_binding": 6,
    "distinct_visual_density_profiles": 6,
}
RUN2_76_VISUAL_QUALITY_EVALUATION_STATUS = "run2_76_visual_quality_evaluation_public_blocked"
RUN2_76_VISUAL_QUALITY_QUESTION_IDS = {
    "is_2_75_better_than_2_73",
    "does_2_75_have_stronger_product_feel",
    "are_page_differences_stronger_or_weaker",
    "is_text_binding_better",
    "does_2_75_reach_public_video_presentation_direction",
}
RUN2_76_PRODUCT_FEEL_DELTA_VALUES = {"improved_but_wireframe", "partial", "not_improved"}
RUN2_76_PAGE_DIFFERENTIATION_VALUES = {"improved", "same", "weaker"}
RUN2_76_TEXT_BINDING_DELTA_VALUES = {"slightly_stronger_but_small", "partial", "weak"}
RUN2_76_PUBLIC_VIDEO_DIRECTION_VALUES = {"no", "partial", "yes"}
RUN2_76_K1_REPAIR_PLAN_STATUS = "run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked"
RUN2_76_K1_REPAIR_PLAN_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
}
RUN2_76_K1_RENDERER_CAPABILITIES = {
    "hero crop",
    "editorial mask",
    "asymmetric foreground/background depth",
    "larger proof object",
    "fewer but more meaningful labels",
    "scene-specific connectors",
    "non-grid evidence arrangement",
}
RUN2_76_K1_FORBIDDEN_RENDERER_FALLBACKS = {
    "debug-like outlines",
    "uniform small label wall",
    "same product window skeleton on every page",
    "schematic blueprint as final visual unless it is the actual proof object",
}
RUN2_76_K1_PAGE_REPAIR_FIELDS = [
    "role",
    "slide_index",
    "visual_grammar_module",
    "source_j_assessment",
    "current_failure",
    "target_scene_direction",
    "visual_grammar_change",
    "renderer_change",
    "text_binding_adjustment",
    "must_preserve_from_2_75",
    "must_remove_from_2_75",
    "acceptance_checks",
]
RUN2_76_K1_ACCEPTANCE_CHECK_KEYS = {
    "page_differentiation_check",
    "wireframe_reduction_check",
    "renderer_capability_check",
    "no_renderer_rerun_in_k1",
}
RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_STATUS = "run2_77_visual_grammar_renderer_repair_rerun_generated_public_blocked"
RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_CONSUMED_SOURCE_PATHS = RUN2_76_K1_REPAIR_PLAN_CONSUMED_SOURCE_PATHS | {
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
    "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
}
RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_DIRECTIVES = {
    "k1_repair_plan_consumed",
    "target_scene_direction_applied",
    "page_differentiation_repaired",
    "forbidden_fallbacks_removed",
    "public_polish_not_claimed",
}
RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_REQUIRED_CHECKS = {
    "pages_with_k1_repair_plan_consumed": 6,
    "pages_using_expected_visual_grammar": 6,
    "distinct_target_scene_directions": 6,
    "pages_with_forbidden_fallbacks_absent": 6,
    "pages_with_reduced_label_count": 6,
}
RUN2_78_VISUAL_QUALITY_EVALUATION_STATUS = "run2_78_visual_quality_evaluation_public_blocked"
RUN2_78_VISUAL_QUALITY_QUESTION_IDS = {
    "is_2_77_better_than_2_75",
    "did_2_77_restore_page_differentiation",
    "did_2_77_reduce_wireframe_aesthetic",
    "did_2_77_reduce_small_label_problem",
    "does_2_77_improve_product_presentation_feel",
    "does_2_77_reach_public_video_presentation_direction",
}
RUN2_78_VISUAL_QUALITY_EXPECTED_ANSWERS = {
    "is_2_77_better_than_2_75": "partial_page_differentiation_up_public_blocked",
    "did_2_77_restore_page_differentiation": "moderately_improved_but_01_04_05_share_wireframe_family",
    "did_2_77_reduce_wireframe_aesthetic": "no_wireframe_still_dominant",
    "did_2_77_reduce_small_label_problem": "partial_label_count_down_but_labels_still_tiny",
    "does_2_77_improve_product_presentation_feel": "partial_more_scene_specific_but_abstract_product_surface",
    "does_2_77_reach_public_video_presentation_direction": "no_public_blocked",
}
RUN2_78_DELTA_VALUES = {"improved", "partial", "unchanged", "regressed"}
RUN2_78_WIREFRAME_REDUCTION_VALUES = {"strong", "partial", "weak", "none"}
RUN2_78_LABEL_HIERARCHY_VALUES = {"improved", "partial", "weak"}
RUN2_79_RENDERER_ART_DIRECTION_REPAIR_STATUS = "run2_79_renderer_art_direction_repair_rerun_generated_public_blocked"
RUN2_79_RENDERER_ART_DIRECTION_REPAIR_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_77_visual_grammar_renderer_repair_rerun_result.json",
    "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
}
RUN2_79_RENDERER_ART_DIRECTION_REPAIR_DIRECTIVES = {
    "l_repair_instruction_consumed",
    "wireframe_surface_replaced",
    "debug_annotation_removed",
    "dominant_product_object",
    "foreground_background_depth",
    "public_scene_hierarchy",
    "public_polish_not_claimed",
}
RUN2_79_RENDERER_ART_DIRECTION_REPAIR_REQUIRED_CHECKS = {
    "pages_with_l_repair_instruction_consumed": 6,
    "pages_with_debug_annotations_removed": 6,
    "pages_with_dominant_product_object": 6,
    "pages_with_public_scene_hierarchy": 6,
    "pages_with_reduced_wireframe_dependency": 6,
    "pages_with_min_visible_label_size": 6,
    "source_trace_terms_visible_on_canvas_count": 0,
}
RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS = "run2_80_visual_quality_evaluation_public_blocked"
RUN2_80_VISUAL_QUALITY_QUESTION_IDS = {
    "is_2_79_better_than_2_77",
    "did_2_79_reduce_wireframe_and_annotation",
    "did_2_79_fix_small_label_problem",
    "did_2_79_create_concrete_product_surface",
    "does_2_79_reach_public_video_presentation_direction",
    "which_layer_needs_next_repair",
}
RUN2_80_VISUAL_QUALITY_EXPECTED_ANSWERS = {
    "is_2_79_better_than_2_77": "mixed_annotation_down_but_product_surface_absent_public_blocked",
    "did_2_79_reduce_wireframe_and_annotation": "partial_debug_annotations_removed_but_typographic_wireframe_remains",
    "did_2_79_fix_small_label_problem": "no_labels_still_tiny_and_spatially_scattered",
    "did_2_79_create_concrete_product_surface": "no_product_surface_not_visibly_realized",
    "does_2_79_reach_public_video_presentation_direction": "no_public_blocked",
    "which_layer_needs_next_repair": "renderer_product_surface_realization",
}
RUN2_80_DELTA_VALUES = {"improved", "partial", "unchanged", "regressed"}
RUN2_80_PRODUCT_SURFACE_REALIZATION_VALUES = {"strong", "partial", "weak", "absent"}
RUN2_81_TEXT_COMPOSITION_TYPOGRAPHY_PLAN_STATUS = "run2_81_text_composition_typography_plan_ready_public_blocked"
RUN2_81_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/run2_43_editorial_composition_typography_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_49_readability_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_64_text_fit_renderer_gates.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_tutorial_to_design_moves.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
}
RUN2_81_REQUIRED_TEXT_BLOCKS = {
    "headline_block",
    "subhead_block",
    "proof_sentence",
    "object_caption",
}
RUN2_81_FORBIDDEN_PATTERNS = {
    "floating labels",
    "tiny labels without object anchors",
    "duplicate run tags",
    "traceability on slide canvas",
    "headline plus chips only",
}
RUN2_81_BOUND_VISUAL_OBJECT_TYPES = {
    "product surface",
    "evidence object",
    "comparison object",
    "decision object",
}
RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_STATUS = (
    "run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked"
)
RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_79_renderer_art_direction_repair_rerun_result.json",
    "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
}
RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_DIRECTIVES = {
    "n_repair_instruction_consumed",
    "o1_text_composition_consumed",
    "concrete_product_surface_rendered",
    "text_hierarchy_applied",
    "floating_labels_removed",
    "traceability_routed_off_canvas",
    "public_polish_not_claimed",
}
RUN2_82_PRODUCT_SURFACE_TYPES = {
    "editable_ppt_product_mock",
    "source_to_memory_product_flow",
    "before_after_product_theater",
    "evidence_product_workspace",
    "release_decision_product_map",
}
RUN2_82_TEXT_COMPOSITION_REQUIRED_CHECKS = {
    "pages_with_o1_text_composition_consumed": 6,
    "pages_with_concrete_product_surface": 6,
    "pages_with_text_hierarchy_applied": 6,
    "pages_with_floating_labels_removed": 6,
    "pages_with_traceability_routed_off_canvas": 6,
}
RUN2_83_WORKFLOW_TAXONOMY_BIAS_AUDIT_STATUS = "run2_83_workflow_taxonomy_bias_audit_ready_public_blocked"
RUN2_83_WORKFLOW_TAXONOMY_BIAS_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/skill_workflow.json",
    "docs/product/ppt-run2-data-skill-quality/run2_8_workflow_gate_matrix.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_42_content_visual_asset_quality_audit.json",
    "docs/product/ppt-run2-data-skill-quality/run2_43_editorial_composition_typography_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_49_readability_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_64_text_fit_renderer_gates.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_source_quality_audit.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_tutorial_to_design_moves.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_74_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
}
RUN2_83_ENGINEERING_GATES_TO_PRESERVE = {
    "traceability",
    "source_availability",
    "validator_required_files",
    "public_release_block",
    "negative_controls",
    "viewer_metadata_routes",
    "reproducible_scripts",
}
RUN2_83_LAYER_BIAS_IDS = {
    "source_quality_inventory",
    "workflow_gate_matrix",
    "tutorial_design_moves",
    "visual_grammar_modules",
    "renderer_adapter_contracts",
    "text_binding_strategy",
    "text_composition_plan",
    "renderer_rerun_results",
    "visual_quality_evaluation_loop",
    "validator_and_tests",
}
RUN2_83_LAYER_BIAS_DIRECTIONS = {
    "engineering_gate_dominant",
    "design_signal_collapsed",
    "renderer_execution_dominant",
    "evaluation_detects_but_does_not_teach_motif",
}
RUN2_83_MISSING_DESIGN_TAXONOMY_FIELDS = {
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
}
RUN2_83_SERIES_STAGE_RANGES = ["2.7-2.18", "2.24-2.42", "2.43-2.64", "2.73-2.82"]
RUN2_84_DESIGN_MOTIF_TAXONOMY_STYLE_ROUTER_STATUS = (
    "run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked"
)
RUN2_84_DESIGN_MOTIF_CONSUMED_SOURCE_PATHS = {
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
}
RUN2_84_DESIGN_MOTIF_FAMILIES = {
    "editorial_text_field",
    "modular_matrix",
    "overlay_sticker_stack",
    "product_theater",
    "before_after_theater",
    "evidence_workspace",
    "decision_map",
}
RUN2_84_STYLE_FAMILIES = {
    "public_product_keynote",
    "technical_editorial",
    "dense_teaching_walkthrough",
    "financial_decision_brief",
    "high_contrast_demo",
}
RUN2_84_SCENARIOS = {
    "product_pitch",
    "teaching_tutorial",
    "financial_product",
    "technical_proof",
    "public_video_demo",
}
RUN2_84_VISUAL_DENSITIES = {"sparse", "balanced", "dense", "climax"}
RUN2_84_PRESERVED_VISUAL_EFFECTS = {
    "modular_matrix",
    "rectangle_layering",
    "overlay_sticker_stack",
    "product_theater",
    "editorial_text_density",
}
RUN2_84_REQUIRED_MOTIF_FIDELITY_CHECKS = {
    "motif_family_visible",
    "not_rectangle_only",
    "text_integrated_with_shape",
}
RUN2_84_FORBIDDEN_RENDERER_SHORTCUTS = {
    "generic rectangles only",
    "traceability labels on canvas",
}
RUN2_85_DESIGN_MOTIF_RENDERER_RERUN_STATUS = "run2_85_design_motif_renderer_rerun_generated_public_blocked"
RUN2_85_DESIGN_MOTIF_RENDERER_CONSUMED_SOURCE_PATHS = {
    "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
}
RUN2_85_DESIGN_MOTIF_RENDERER_ARMS = {
    "prompt_only",
    "run1_5_skill",
    "run2_85_full_design_motif_style_router",
    "bad_run2_85_without_design_motif_layer",
}
RUN2_85_DESIGN_MOTIF_RENDERER_DIRECTIVES = {
    "p1_design_motif_layer_consumed",
    "style_router_applied",
    "motif_family_rendered",
    "preserved_visual_effects_rendered",
    "text_integrated_with_motif",
    "traceability_routed_off_canvas",
    "public_polish_not_claimed",
}
RUN2_85_DESIGN_MOTIF_REQUIRED_CHECKS = {
    "pages_with_p1_motif_consumed": 6,
    "pages_with_motif_family_visible": 6,
    "pages_with_not_rectangle_only": 6,
    "pages_with_text_integrated_with_shape": 6,
    "pages_with_traceability_routed_off_canvas": 6,
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def required_files_for_profile(profile: str) -> list[str]:
    if profile == "default":
        return REQUIRED_FILES
    if profile == "run1":
        return [*REQUIRED_FILES, *RUN1_REQUIRED_FILES]
    if profile == "run1_5":
        return [*REQUIRED_FILES, *RUN1_5_REQUIRED_FILES]
    if profile == "run2":
        return [*RUN2_REQUIRED_FILES, *RUN2_8_REQUIRED_FILES, *RUN2_73_REQUIRED_FILES]
    raise ValueError(f"unknown case-pack profile: {profile}")


def read_text_file(path: Path, label: str, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"unable to read {label}: {exc}")
    except UnicodeDecodeError as exc:
        errors.append(f"{label} must be UTF-8 text: {exc}")
    return None


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    body = read_text_file(path, path.name, errors)
    if body is None:
        return {}
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} is not valid JSON: {exc.msg}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a JSON object")
        return {}
    return value


def load_json_files(directory: Path, label: str, errors: list[str]) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.exists():
        errors.append(f"{label} directory does not exist")
        return []
    if not directory.is_dir():
        errors.append(f"{label} must be a directory")
        return []
    paths = sorted(directory.glob("*.json"))
    if not paths:
        errors.append(f"{label} must contain at least one JSON file")
        return []
    return [(path, load_json(path, errors)) for path in paths]


def require_keys(label: str, value: dict[str, Any], keys: list[str], errors: list[str]) -> None:
    for key in keys:
        if key not in value:
            errors.append(f"{label} missing key: {key}")


def require_integer(label: str, value: Any, errors: list[str]) -> bool:
    if type(value) is not int:
        errors.append(f"{label} must be an integer")
        return False
    return True


def require_non_empty_string(label: str, value: Any, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return False
    return True


def require_non_empty_dict(label: str, value: Any, errors: list[str]) -> bool:
    if not isinstance(value, dict) or not value:
        errors.append(f"{label} must be a non-empty object")
        return False
    return True


def require_non_empty_list(label: str, value: Any, errors: list[str]) -> bool:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return False
    return True


def validate_string_list(label: str, value: Any, errors: list[str]) -> bool:
    if not require_non_empty_list(label, value, errors):
        return False
    ok = True
    for index, item in enumerate(value):
        if not require_non_empty_string(f"{label}[{index}]", item, errors):
            ok = False
    return ok


def validate_string_mapping(label: str, value: Any, errors: list[str]) -> bool:
    if not require_non_empty_dict(label, value, errors):
        return False
    ok = True
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{label} keys must be non-empty strings")
            ok = False
        if not require_non_empty_string(f"{label}.{key}", item, errors):
            ok = False
    return ok


def validate_choice(label: str, value: Any, choices: set[str], errors: list[str]) -> bool:
    if not require_non_empty_string(label, value, errors):
        return False
    if value not in choices:
        errors.append(f"{label} must be one of {', '.join(sorted(choices))}")
        return False
    return True


def validate_exact_string_set(label: str, value: Any, expected: set[str], errors: list[str]) -> None:
    if not validate_string_list(label, value, errors):
        return
    actual = set(value)
    for item in sorted(expected - actual):
        errors.append(f"{label} missing value: {item}")
    for item in sorted(actual - expected):
        errors.append(f"{label} has unexpected value: {item}")


def validate_number_mapping(label: str, value: Any, errors: list[str]) -> bool:
    if not require_non_empty_dict(label, value, errors):
        return False
    ok = True
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{label} keys must be non-empty strings")
            ok = False
        if not isinstance(item, int | float) or isinstance(item, bool):
            errors.append(f"{label}.{key} must be a number")
            ok = False
    return ok


def validate_no_external_media_reference(label: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in RUN2_FORBIDDEN_MEDIA_REFERENCE_MARKERS):
            errors.append(f"{label} must not include external media URLs or file references")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_no_external_media_reference(f"{label}[{index}]", item, errors)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_no_external_media_reference(f"{label}.{key}", item, errors)


def validate_public_blocked_boundary(label: str, value: Any, errors: list[str]) -> None:
    if require_non_empty_string(label, value, errors) and "public_blocked" not in value:
        errors.append(f"{label} must keep public_blocked status")


def validate_run2_8_release_boundary(label: str, value: Any, errors: list[str]) -> None:
    if require_non_empty_string(label, value, errors) and value != RUN2_8_RELEASE_BOUNDARY:
        errors.append(f"{label} must be {RUN2_8_RELEASE_BOUNDARY}")


def validate_known_string_references(
    label: str,
    value: Any,
    known_ids: set[str],
    unknown_name: str,
    errors: list[str],
) -> None:
    if not validate_string_list(label, value, errors):
        return
    for item in value:
        if item not in known_ids:
            errors.append(f"{label} references unknown {unknown_name}: {item}")


def validate_combined_terms(label: str, values: Any, terms: list[str], errors: list[str]) -> None:
    if not validate_string_list(label, values, errors):
        return
    combined = " ".join(values).lower()
    for term in terms:
        if term not in combined:
            errors.append(f"{label} must mention {term}")


def validate_string_mentions(label: str, value: Any, terms: list[str], errors: list[str]) -> None:
    if not require_non_empty_string(label, value, errors):
        return
    lowered = value.lower()
    for term in terms:
        if term.lower() not in lowered:
            errors.append(f"{label} must mention {term}")


def validate_run2_extraction_units(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    for index, unit in enumerate(value):
        unit_label = f"{label}[{index}]"
        if not isinstance(unit, dict):
            errors.append(f"{unit_label} must be an object")
            continue
        require_keys(unit_label, unit, RUN2_EXTRACTION_UNIT_FIELDS, errors)
        for key in RUN2_EXTRACTION_UNIT_FIELDS:
            if key not in unit:
                continue
            if key == "slide_role":
                validate_choice(f"{unit_label}.{key}", unit[key], RUN2_RHYTHM_ROLES, errors)
            else:
                require_non_empty_string(f"{unit_label}.{key}", unit[key], errors)


def validate_run2_multimodal_anchors(
    label: str,
    value: Any,
    record_modalities: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    required = ["anchor_id", "modality", "locator", "observation", "extracted_design_signal", "allowed_use"]
    seen_anchor_ids: set[str] = set()
    for index, anchor in enumerate(value):
        anchor_label = f"{label}[{index}]"
        if not isinstance(anchor, dict):
            errors.append(f"{anchor_label} must be an object")
            continue
        require_keys(anchor_label, anchor, required, errors)
        anchor_id = anchor.get("anchor_id")
        if "anchor_id" in anchor and require_non_empty_string(f"{anchor_label}.anchor_id", anchor_id, errors):
            if anchor_id in seen_anchor_ids:
                errors.append(f"{anchor_label}.anchor_id duplicates {anchor_id}")
            seen_anchor_ids.add(anchor_id)
        if "modality" in anchor:
            modality = anchor["modality"]
            if validate_choice(f"{anchor_label}.modality", modality, RUN2_MULTIMODAL_MODALITIES, errors):
                if modality not in record_modalities:
                    errors.append(f"{anchor_label}.modality {modality} is not listed in the parent record modalities")
        for key in ["locator", "observation", "extracted_design_signal"]:
            if key in anchor:
                require_non_empty_string(f"{anchor_label}.{key}", anchor[key], errors)
        if "allowed_use" in anchor:
            validate_choice(f"{anchor_label}.allowed_use", anchor["allowed_use"], RUN2_ALLOWED_USES, errors)


def validate_run2_multimodal_database(
    pack_dir: Path, source_ids: set[str], errors: list[str]
) -> tuple[set[str], set[str]]:
    data = load_json(pack_dir / "multimodal_database.json", errors)
    require_keys(
        "multimodal_database.json",
        data,
        [
            "schema_version",
            "status",
            "storage_policy",
            "required_modalities",
            "records",
            "cross_modal_design_tasks",
            "qa_gates",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("multimodal_database.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("multimodal_database.status", data["status"], errors)
    if "storage_policy" in data:
        storage_policy = data["storage_policy"]
        if require_non_empty_dict("multimodal_database.storage_policy", storage_policy, errors):
            for key in ["default", "raw_media", "copyright_boundary"]:
                if key in storage_policy:
                    require_non_empty_string(f"multimodal_database.storage_policy.{key}", storage_policy[key], errors)
            default_storage = storage_policy.get("default")
            if isinstance(default_storage, str) and default_storage not in RUN2_MULTIMODAL_ALLOWED_STORAGE:
                errors.append("multimodal_database.storage_policy.default must be an allowed storage policy")
            raw_media = storage_policy.get("raw_media")
            if isinstance(raw_media, str) and raw_media != "forbidden":
                errors.append("multimodal_database.storage_policy.raw_media must be forbidden")
    if "required_modalities" in data:
        validate_exact_string_set(
            "multimodal_database.required_modalities",
            data["required_modalities"],
            RUN2_MULTIMODAL_MODALITIES,
            errors,
        )

    records = data.get("records", [])
    if not require_non_empty_list("multimodal_database.records", records, errors):
        return set(), set()
    seen_record_ids: set[str] = set()
    seen_anchor_ids: set[str] = set()
    covered_modalities: set[str] = set()
    required_record_fields = [
        "id",
        "source_id",
        "source_kind",
        "modalities",
        "allowed_storage",
        "ingestion_status",
        "anchors",
        "derived_outputs",
        "do_not_store",
        "qa_gates",
    ]
    for index, record in enumerate(records):
        label = f"multimodal_database.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, record, required_record_fields, errors)
        record_id = record.get("id")
        if "id" in record and require_non_empty_string(f"{label}.id", record_id, errors):
            if record_id in seen_record_ids:
                errors.append(f"{label}.id duplicates {record_id}")
            seen_record_ids.add(record_id)
        source_id = record.get("source_id")
        if "source_id" in record:
            if require_non_empty_string(f"{label}.source_id", source_id, errors) and source_id not in source_ids:
                errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
        if "source_kind" in record:
            require_non_empty_string(f"{label}.source_kind", record["source_kind"], errors)
        record_modalities: set[str] = set()
        if "modalities" in record and validate_string_list(f"{label}.modalities", record["modalities"], errors):
            for modality in record["modalities"]:
                if modality not in RUN2_MULTIMODAL_MODALITIES:
                    errors.append(f"{label}.modalities has unexpected value: {modality}")
                else:
                    record_modalities.add(modality)
                    covered_modalities.add(modality)
        if "allowed_storage" in record:
            validate_choice(
                f"{label}.allowed_storage",
                record["allowed_storage"],
                RUN2_MULTIMODAL_ALLOWED_STORAGE,
                errors,
            )
        if "ingestion_status" in record:
            require_non_empty_string(f"{label}.ingestion_status", record["ingestion_status"], errors)
        if "anchors" in record:
            validate_run2_multimodal_anchors(f"{label}.anchors", record["anchors"], record_modalities, errors)
            if isinstance(record["anchors"], list):
                for anchor in record["anchors"]:
                    if isinstance(anchor, dict):
                        anchor_id = anchor.get("anchor_id")
                        if isinstance(anchor_id, str) and anchor_id.strip():
                            if anchor_id in seen_anchor_ids:
                                errors.append(f"{label}.anchors has duplicate global anchor_id: {anchor_id}")
                            seen_anchor_ids.add(anchor_id)
        for key in ["derived_outputs", "do_not_store", "qa_gates"]:
            if key in record:
                validate_string_list(f"{label}.{key}", record[key], errors)

    for modality in sorted(RUN2_MULTIMODAL_MODALITIES - covered_modalities):
        errors.append(f"multimodal_database.records missing modality coverage: {modality}")

    tasks = data.get("cross_modal_design_tasks", [])
    if require_non_empty_list("multimodal_database.cross_modal_design_tasks", tasks, errors):
        for index, task in enumerate(tasks):
            label = f"multimodal_database.cross_modal_design_tasks[{index}]"
            if not isinstance(task, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(label, task, ["id", "input_modalities", "task", "required_generator_behavior"], errors)
            for key in ["id", "task", "required_generator_behavior"]:
                if key in task:
                    require_non_empty_string(f"{label}.{key}", task[key], errors)
            if "input_modalities" in task and validate_string_list(
                f"{label}.input_modalities", task["input_modalities"], errors
            ):
                for modality in task["input_modalities"]:
                    if modality not in RUN2_MULTIMODAL_MODALITIES:
                        errors.append(f"{label}.input_modalities has unexpected value: {modality}")
    if "qa_gates" in data:
        validate_string_list("multimodal_database.qa_gates", data["qa_gates"], errors)
    return seen_record_ids, seen_anchor_ids


def validate_run2_visual_learning_targets(
    pack_dir: Path,
    multimodal_record_ids: set[str],
    multimodal_anchor_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "visual_learning_targets.json", errors)
    require_keys(
        "visual_learning_targets.json",
        data,
        ["schema_version", "status", "stage_policy", "native_editable_definition", "targets"],
        errors,
    )
    if "schema_version" in data:
        require_integer("visual_learning_targets.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("visual_learning_targets.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("visual_learning_targets.stage_policy must be repeat_same_five_layers_not_run3")
    if "native_editable_definition" in data:
        if validate_string_list(
            "visual_learning_targets.native_editable_definition", data["native_editable_definition"], errors
        ):
            combined_definition = " ".join(data["native_editable_definition"]).lower()
            if "native" not in combined_definition or "editable" not in combined_definition:
                errors.append("visual_learning_targets.native_editable_definition must define native editable output")
        validate_no_external_media_reference(
            "visual_learning_targets.native_editable_definition", data["native_editable_definition"], errors
        )

    targets = data.get("targets", [])
    if not require_non_empty_list("visual_learning_targets.targets", targets, errors):
        return set()
    required = [
        "id",
        "source_record_ids",
        "anchor_ids",
        "slide_roles",
        "failure_pattern",
        "desired_behavior",
        "code_generation_requirements",
        "qa_probe",
        "release_boundary",
    ]
    seen_target_ids: set[str] = set()
    for index, target in enumerate(targets):
        label = f"visual_learning_targets.targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, target, required, errors)
        target_id = target.get("id")
        if "id" in target and require_non_empty_string(f"{label}.id", target_id, errors):
            if target_id in seen_target_ids:
                errors.append(f"{label}.id duplicates {target_id}")
            seen_target_ids.add(target_id)
        if "source_record_ids" in target and validate_string_list(
            f"{label}.source_record_ids", target["source_record_ids"], errors
        ):
            for record_id in target["source_record_ids"]:
                if record_id not in multimodal_record_ids:
                    errors.append(f"{label}.source_record_ids references unknown multimodal record: {record_id}")
        if "anchor_ids" in target and validate_string_list(f"{label}.anchor_ids", target["anchor_ids"], errors):
            for anchor_id in target["anchor_ids"]:
                if anchor_id not in multimodal_anchor_ids:
                    errors.append(f"{label}.anchor_ids references unknown multimodal anchor: {anchor_id}")
        if "slide_roles" in target and validate_string_list(f"{label}.slide_roles", target["slide_roles"], errors):
            for role in target["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        for key in ["failure_pattern", "desired_behavior", "qa_probe", "release_boundary"]:
            if key in target:
                require_non_empty_string(f"{label}.{key}", target[key], errors)
                validate_no_external_media_reference(f"{label}.{key}", target[key], errors)
        if "code_generation_requirements" in target:
            if validate_string_list(
                f"{label}.code_generation_requirements", target["code_generation_requirements"], errors
            ):
                combined = " ".join(target["code_generation_requirements"]).lower()
                if "native" not in combined or "editable" not in combined:
                    errors.append(f"{label}.code_generation_requirements must require native editable output")
            validate_no_external_media_reference(
                f"{label}.code_generation_requirements",
                target["code_generation_requirements"],
                errors,
            )
        release_boundary = target.get("release_boundary")
        if isinstance(release_boundary, str) and "public_blocked" not in release_boundary:
            errors.append(f"{label}.release_boundary must keep public_blocked status")
    return seen_target_ids


def validate_run2_visual_target_components(
    pack_dir: Path,
    visual_target_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "visual_target_components.json", errors)
    require_keys(
        "visual_target_components.json",
        data,
        ["schema_version", "status", "stage_policy", "components", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("visual_target_components.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("visual_target_components.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("visual_target_components.stage_policy must be repeat_same_five_layers_not_run3")

    components = data.get("components", [])
    if not require_non_empty_list("visual_target_components.components", components, errors):
        return set()
    required = [
        "id",
        "target_ids",
        "slide_roles",
        "native_ppt_primitives",
        "layout_contract",
        "density_contract",
        "trace_fields",
        "generator_prompt",
        "qa_probe",
        "failure_modes",
        "release_boundary",
    ]
    seen_component_ids: set[str] = set()
    for index, component in enumerate(components):
        label = f"visual_target_components.components[{index}]"
        if not isinstance(component, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, component, required, errors)
        component_id = component.get("id")
        if "id" in component and require_non_empty_string(f"{label}.id", component_id, errors):
            if component_id in seen_component_ids:
                errors.append(f"{label}.id duplicates {component_id}")
            seen_component_ids.add(component_id)
        if "target_ids" in component and validate_string_list(f"{label}.target_ids", component["target_ids"], errors):
            for target_index, target_id in enumerate(component["target_ids"]):
                if target_id not in visual_target_ids:
                    errors.append(f"{label}.target_ids[{target_index}] references unknown visual target: {target_id}")
        if "slide_roles" in component and validate_string_list(
            f"{label}.slide_roles", component["slide_roles"], errors
        ):
            for role in component["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        if "native_ppt_primitives" in component:
            if validate_string_list(f"{label}.native_ppt_primitives", component["native_ppt_primitives"], errors):
                combined = " ".join(component["native_ppt_primitives"]).lower()
                if "native" not in combined or "editable" not in combined:
                    errors.append(f"{label}.native_ppt_primitives must require native editable PPT output")
            validate_no_external_media_reference(
                f"{label}.native_ppt_primitives", component["native_ppt_primitives"], errors
            )
        for key in ["layout_contract", "density_contract", "generator_prompt", "qa_probe", "release_boundary"]:
            if key in component:
                require_non_empty_string(f"{label}.{key}", component[key], errors)
                validate_no_external_media_reference(f"{label}.{key}", component[key], errors)
        for key in ["trace_fields", "failure_modes"]:
            if key in component:
                validate_string_list(f"{label}.{key}", component[key], errors)
                validate_no_external_media_reference(f"{label}.{key}", component[key], errors)
        release_boundary = component.get("release_boundary")
        if isinstance(release_boundary, str) and "public_blocked" not in release_boundary:
            errors.append(f"{label}.release_boundary must keep public_blocked status")

    if "qa_gates" in data:
        validate_string_list("visual_target_components.qa_gates", data["qa_gates"], errors)
    return seen_component_ids


def validate_run2_video_demo_beat_map(
    pack_dir: Path,
    source_ids: set[str],
    multimodal_record_ids: set[str],
    multimodal_anchor_ids: set[str],
    card_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "video_demo_beat_map.json", errors)
    require_keys(
        "video_demo_beat_map.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "beats", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("video_demo_beat_map.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("video_demo_beat_map.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("video_demo_beat_map.stage_policy must be repeat_same_five_layers_not_run3")
    if "storage_policy" in data:
        storage_policy = data["storage_policy"]
        if require_non_empty_dict("video_demo_beat_map.storage_policy", storage_policy, errors):
            raw_media = storage_policy.get("raw_media")
            if isinstance(raw_media, str) and raw_media != "forbidden":
                errors.append("video_demo_beat_map.storage_policy.raw_media must be forbidden")
            for key in ["default", "raw_media", "copyright_boundary"]:
                if key in storage_policy:
                    require_non_empty_string(f"video_demo_beat_map.storage_policy.{key}", storage_policy[key], errors)
        validate_no_external_media_reference("video_demo_beat_map.storage_policy", storage_policy, errors)

    beats = data.get("beats", [])
    if not require_non_empty_list("video_demo_beat_map.beats", beats, errors):
        return set()
    required = [
        "id",
        "source_id",
        "source_record_ids",
        "anchor_ids",
        "video_card_ids",
        "locator",
        "observed_demo_move",
        "derived_presentation_rule",
        "motion_role",
        "reveal_sequence",
        "pacing_signal",
        "do_not_store",
        "qa_probe",
        "release_boundary",
    ]
    seen_beat_ids: set[str] = set()
    for index, beat in enumerate(beats):
        label = f"video_demo_beat_map.beats[{index}]"
        if not isinstance(beat, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, beat, required, errors)
        validate_no_external_media_reference(label, beat, errors)
        beat_id = beat.get("id")
        if "id" in beat and require_non_empty_string(f"{label}.id", beat_id, errors):
            if beat_id in seen_beat_ids:
                errors.append(f"{label}.id duplicates {beat_id}")
            seen_beat_ids.add(beat_id)
        source_id = beat.get("source_id")
        if "source_id" in beat and require_non_empty_string(f"{label}.source_id", source_id, errors):
            if source_id not in source_ids:
                errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
        if "source_record_ids" in beat:
            validate_known_string_references(
                f"{label}.source_record_ids",
                beat["source_record_ids"],
                multimodal_record_ids,
                "multimodal record",
                errors,
            )
        if "anchor_ids" in beat:
            validate_known_string_references(
                f"{label}.anchor_ids",
                beat["anchor_ids"],
                multimodal_anchor_ids,
                "multimodal anchor",
                errors,
            )
        if "video_card_ids" in beat:
            validate_known_string_references(
                f"{label}.video_card_ids",
                beat["video_card_ids"],
                card_ids,
                "source or video card",
                errors,
            )
        for key in ["locator", "observed_demo_move", "derived_presentation_rule", "pacing_signal", "qa_probe"]:
            if key in beat:
                require_non_empty_string(f"{label}.{key}", beat[key], errors)
        if "motion_role" in beat:
            validate_choice(f"{label}.motion_role", beat["motion_role"], RUN2_MOTION_ROLES, errors)
        if "reveal_sequence" in beat:
            validate_combined_terms(f"{label}.reveal_sequence", beat["reveal_sequence"], ["native"], errors)
        if "do_not_store" in beat:
            if validate_string_list(f"{label}.do_not_store", beat["do_not_store"], errors):
                combined = " ".join(beat["do_not_store"]).lower()
                for term in ["video", "frames", "audio", "transcript"]:
                    if term not in combined:
                        errors.append(f"{label}.do_not_store must mention {term}")
        if "release_boundary" in beat:
            validate_public_blocked_boundary(f"{label}.release_boundary", beat["release_boundary"], errors)
    if "qa_gates" in data:
        validate_string_list("video_demo_beat_map.qa_gates", data["qa_gates"], errors)
        validate_no_external_media_reference("video_demo_beat_map.qa_gates", data["qa_gates"], errors)
    return seen_beat_ids


def validate_run2_motion_learning_targets(
    pack_dir: Path,
    beat_ids: set[str],
    visual_target_ids: set[str],
    visual_component_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "motion_learning_targets.json", errors)
    require_keys(
        "motion_learning_targets.json",
        data,
        ["schema_version", "status", "stage_policy", "targets", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("motion_learning_targets.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("motion_learning_targets.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("motion_learning_targets.stage_policy must be repeat_same_five_layers_not_run3")

    targets = data.get("targets", [])
    if not require_non_empty_list("motion_learning_targets.targets", targets, errors):
        return set()
    required = [
        "id",
        "beat_ids",
        "visual_target_ids",
        "visual_component_ids",
        "slide_roles",
        "motion_role",
        "failure_pattern",
        "desired_behavior",
        "code_generation_requirements",
        "qa_probe",
        "release_boundary",
    ]
    seen_target_ids: set[str] = set()
    for index, target in enumerate(targets):
        label = f"motion_learning_targets.targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, target, required, errors)
        validate_no_external_media_reference(label, target, errors)
        target_id = target.get("id")
        if "id" in target and require_non_empty_string(f"{label}.id", target_id, errors):
            if target_id in seen_target_ids:
                errors.append(f"{label}.id duplicates {target_id}")
            seen_target_ids.add(target_id)
        if "beat_ids" in target:
            validate_known_string_references(f"{label}.beat_ids", target["beat_ids"], beat_ids, "video beat", errors)
        if "visual_target_ids" in target:
            validate_known_string_references(
                f"{label}.visual_target_ids",
                target["visual_target_ids"],
                visual_target_ids,
                "visual target",
                errors,
            )
        if "visual_component_ids" in target:
            validate_known_string_references(
                f"{label}.visual_component_ids",
                target["visual_component_ids"],
                visual_component_ids,
                "visual component",
                errors,
            )
        if "slide_roles" in target and validate_string_list(f"{label}.slide_roles", target["slide_roles"], errors):
            for role in target["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        if "motion_role" in target:
            validate_choice(f"{label}.motion_role", target["motion_role"], RUN2_MOTION_ROLES, errors)
        for key in ["failure_pattern", "desired_behavior", "qa_probe"]:
            if key in target:
                require_non_empty_string(f"{label}.{key}", target[key], errors)
        if "code_generation_requirements" in target:
            validate_combined_terms(
                f"{label}.code_generation_requirements",
                target["code_generation_requirements"],
                ["native", "editable", "metadata", "trace"],
                errors,
            )
        if "release_boundary" in target:
            validate_public_blocked_boundary(f"{label}.release_boundary", target["release_boundary"], errors)
    if "qa_gates" in data:
        validate_string_list("motion_learning_targets.qa_gates", data["qa_gates"], errors)
        validate_no_external_media_reference("motion_learning_targets.qa_gates", data["qa_gates"], errors)
    return seen_target_ids


def validate_run2_presentation_sequence_components(
    pack_dir: Path,
    motion_target_ids: set[str],
    visual_component_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "presentation_sequence_components.json", errors)
    require_keys(
        "presentation_sequence_components.json",
        data,
        ["schema_version", "status", "stage_policy", "components", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("presentation_sequence_components.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("presentation_sequence_components.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("presentation_sequence_components.stage_policy must be repeat_same_five_layers_not_run3")

    components = data.get("components", [])
    if not require_non_empty_list("presentation_sequence_components.components", components, errors):
        return set()
    required = [
        "id",
        "motion_target_ids",
        "visual_component_ids",
        "slide_roles",
        "native_ppt_primitives",
        "sequence_steps",
        "trace_fields",
        "qa_probe",
        "failure_modes",
        "release_boundary",
    ]
    step_required = ["step_id", "order", "reveal_object", "trigger", "duration", "purpose"]
    seen_component_ids: set[str] = set()
    for index, component in enumerate(components):
        label = f"presentation_sequence_components.components[{index}]"
        if not isinstance(component, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, component, required, errors)
        validate_no_external_media_reference(label, component, errors)
        component_id = component.get("id")
        if "id" in component and require_non_empty_string(f"{label}.id", component_id, errors):
            if component_id in seen_component_ids:
                errors.append(f"{label}.id duplicates {component_id}")
            seen_component_ids.add(component_id)
        if "motion_target_ids" in component:
            validate_known_string_references(
                f"{label}.motion_target_ids",
                component["motion_target_ids"],
                motion_target_ids,
                "motion target",
                errors,
            )
        if "visual_component_ids" in component:
            validate_known_string_references(
                f"{label}.visual_component_ids",
                component["visual_component_ids"],
                visual_component_ids,
                "visual component",
                errors,
            )
        if "slide_roles" in component and validate_string_list(
            f"{label}.slide_roles", component["slide_roles"], errors
        ):
            for role in component["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        if "native_ppt_primitives" in component:
            validate_combined_terms(
                f"{label}.native_ppt_primitives",
                component["native_ppt_primitives"],
                ["native", "editable"],
                errors,
            )
        steps = component.get("sequence_steps", [])
        if require_non_empty_list(f"{label}.sequence_steps", steps, errors):
            seen_orders: list[int] = []
            for step_index, step in enumerate(steps):
                step_label = f"{label}.sequence_steps[{step_index}]"
                if not isinstance(step, dict):
                    errors.append(f"{step_label} must be an object")
                    continue
                require_keys(step_label, step, step_required, errors)
                if "order" in step and require_integer(f"{step_label}.order", step["order"], errors):
                    seen_orders.append(step["order"])
                for key in ["step_id", "reveal_object", "trigger", "duration", "purpose"]:
                    if key in step:
                        require_non_empty_string(f"{step_label}.{key}", step[key], errors)
            expected_orders = list(range(1, len(seen_orders) + 1))
            if seen_orders != expected_orders:
                errors.append(f"{label}.sequence_steps order must be sequential starting at 1")
        if "trace_fields" in component:
            if validate_string_list(f"{label}.trace_fields", component["trace_fields"], errors):
                required_trace = {"motion_target_ids", "sequence_component_ids"}
                actual_trace = set(component["trace_fields"])
                for trace_field in sorted(required_trace - actual_trace):
                    errors.append(f"{label}.trace_fields missing value: {trace_field}")
        for key in ["qa_probe", "release_boundary"]:
            if key in component:
                require_non_empty_string(f"{label}.{key}", component[key], errors)
        if "failure_modes" in component:
            validate_string_list(f"{label}.failure_modes", component["failure_modes"], errors)
        if "release_boundary" in component:
            validate_public_blocked_boundary(f"{label}.release_boundary", component["release_boundary"], errors)
    if "qa_gates" in data:
        validate_string_list("presentation_sequence_components.qa_gates", data["qa_gates"], errors)
        validate_no_external_media_reference("presentation_sequence_components.qa_gates", data["qa_gates"], errors)
    return seen_component_ids


def validate_sources(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "sources.json", errors)
    require_keys("sources.json", data, ["schema_version", "sources"], errors)
    if "schema_version" in data:
        require_integer("sources.json.schema_version", data["schema_version"], errors)
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("sources.json sources must be a non-empty list")
        return set()

    required = ["id", "title", "url", "role", "accessed_on", "allowed_use", "copyright_note"]
    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        require_keys(f"sources[{index}]", source, required, errors)
        for key in required:
            if key in source:
                require_non_empty_string(f"sources[{index}].{key}", source[key], errors)
        source_id = source.get("id")
        if isinstance(source_id, str) and source_id.strip():
            if source_id in seen_ids:
                errors.append(f"sources[{index}].id duplicates {source_id}")
            seen_ids.add(source_id)
        url = source.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"sources[{index}].url must be https")
        allowed_use = source.get("allowed_use")
        if isinstance(allowed_use, str) and allowed_use != "reference_analysis_only":
            errors.append(f"sources[{index}].allowed_use must be reference_analysis_only")
    return seen_ids


def validate_narrative_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "narrative_rules.json", errors)
    require_keys(
        "narrative_rules.json", data, ["schema_version", "opening", "progression", "technical_depth", "closing"], errors
    )
    if "schema_version" in data:
        require_integer("narrative_rules.schema_version", data["schema_version"], errors)
    for key in ["opening", "technical_depth", "closing"]:
        if key in data:
            require_non_empty_string(f"narrative_rules.{key}", data[key], errors)
    progression = data.get("progression", [])
    validate_string_list("narrative_rules.progression", progression, errors)


def validate_style_tokens(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "style_tokens.json", errors)
    require_keys(
        "style_tokens.json",
        data,
        ["schema_version", "palette", "font_stack", "spacing", "corner_radius", "stroke_widths"],
        errors,
    )
    if "schema_version" in data:
        require_integer("style_tokens.schema_version", data["schema_version"], errors)
    validate_string_mapping("style_tokens.palette", data.get("palette", {}), errors)
    validate_string_list("style_tokens.font_stack", data.get("font_stack", []), errors)
    validate_number_mapping("style_tokens.spacing", data.get("spacing", {}), errors)
    validate_number_mapping("style_tokens.corner_radius", data.get("corner_radius", {}), errors)
    validate_number_mapping("style_tokens.stroke_widths", data.get("stroke_widths", {}), errors)


def validate_asset_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_rules.json", errors)
    require_keys(
        "asset_rules.json",
        data,
        ["schema_version", "preferred_assets", "bitmap_use", "forbidden", "provenance_required"],
        errors,
    )
    if "schema_version" in data:
        require_integer("asset_rules.schema_version", data["schema_version"], errors)
    validate_string_list("asset_rules.preferred_assets", data.get("preferred_assets", []), errors)
    if "bitmap_use" in data:
        require_non_empty_string("asset_rules.bitmap_use", data["bitmap_use"], errors)
    validate_string_list("asset_rules.forbidden", data.get("forbidden", []), errors)
    if "provenance_required" in data and not isinstance(data.get("provenance_required"), bool):
        errors.append("asset_rules.provenance_required must be a boolean")


def validate_slide_patterns(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "slide_patterns.json", errors)
    require_keys("slide_patterns.json", data, ["schema_version", "patterns"], errors)
    if "schema_version" in data:
        require_integer("slide_patterns.schema_version", data["schema_version"], errors)
    patterns = data.get("patterns", [])
    if not isinstance(patterns, list) or not patterns:
        errors.append("slide_patterns.patterns must be a non-empty list")
        return set()

    required = ["id", "role", "content_density", "layout_shape", "visual_asset_type", "editability_requirements"]
    pattern_ids: set[str] = set()
    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            errors.append(f"slide_patterns.patterns[{index}] must be an object")
            continue
        require_keys(f"slide_patterns.patterns[{index}]", pattern, required, errors)
        for key in ["id", "role", "content_density", "layout_shape", "visual_asset_type"]:
            if key in pattern:
                require_non_empty_string(f"slide_patterns.patterns[{index}].{key}", pattern[key], errors)
        pattern_id = pattern.get("id")
        if isinstance(pattern_id, str) and pattern_id.strip():
            if pattern_id in pattern_ids:
                errors.append(f"slide_patterns.patterns[{index}].id duplicates {pattern_id}")
            pattern_ids.add(pattern_id)
        if "editability_requirements" in pattern:
            validate_string_list(
                f"slide_patterns.patterns[{index}].editability_requirements",
                pattern["editability_requirements"],
                errors,
            )
    return pattern_ids


def validate_deck_outline(pack_dir: Path, pattern_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "deck_outline.json", errors)
    require_keys("deck_outline.json", data, ["schema_version", "title", "slides"], errors)
    if "schema_version" in data:
        require_integer("deck_outline.schema_version", data["schema_version"], errors)
    if "title" in data:
        require_non_empty_string("deck_outline.title", data["title"], errors)
    slides = data.get("slides", [])
    if not isinstance(slides, list) or not slides:
        errors.append("deck_outline.slides must be a non-empty list")
        return

    required = ["id", "pattern_id", "title", "claim", "proof_object"]
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            errors.append(f"deck_outline.slides[{index}] must be an object")
            continue
        require_keys(f"deck_outline.slides[{index}]", slide, required, errors)
        for key in required:
            if key in slide:
                require_non_empty_string(f"deck_outline.slides[{index}].{key}", slide[key], errors)
        pattern_id = slide.get("pattern_id")
        if not isinstance(pattern_id, str):
            errors.append(f"deck_outline.slides[{index}].pattern_id must be a string")
        elif pattern_id not in pattern_ids:
            errors.append(f"deck_outline.slides[{index}].pattern_id {pattern_id} is not defined in slide_patterns.json")


def collect_run2_card_ids(pack_dir: Path, source_ids: set[str], errors: list[str]) -> set[str]:
    card_ids: set[str] = set()
    common_required = [
        "schema_version",
        "card_id",
        "source_id",
        "source_type",
        "allowed_use",
        "do_not_copy",
        "extraction_units",
    ]
    source_required = ["observed_move", "why_it_works", "ppt_translation", "quality_risk"]
    video_required = [
        "timestamp_map",
        "keyframe_descriptions",
        "pacing_notes",
        "transition_observations",
        "derived_aesthetic_cards",
    ]

    for label, required in [
        ("source_cards", [*common_required, *source_required]),
        ("video_cards", [*common_required, *video_required]),
    ]:
        for path, card in load_json_files(pack_dir / label, label, errors):
            card_label = f"{label}/{path.name}"
            require_keys(card_label, card, required, errors)
            if "schema_version" in card:
                require_integer(f"{card_label}.schema_version", card["schema_version"], errors)
            card_id = card.get("card_id")
            if "card_id" in card and require_non_empty_string(f"{card_label}.card_id", card_id, errors):
                if card_id in card_ids:
                    errors.append(f"{card_label}.card_id duplicates {card_id}")
                card_ids.add(card_id)
            if "source_id" in card:
                source_id = card["source_id"]
                if (
                    require_non_empty_string(f"{card_label}.source_id", source_id, errors)
                    and source_id not in source_ids
                ):
                    errors.append(f"{card_label}.source_id {source_id} is not defined in sources.json")
            if "source_type" in card:
                validate_choice(f"{card_label}.source_type", card["source_type"], RUN2_SOURCE_TYPES, errors)
            if "allowed_use" in card:
                validate_choice(f"{card_label}.allowed_use", card["allowed_use"], RUN2_ALLOWED_USES, errors)
            if "do_not_copy" in card:
                require_non_empty_string(f"{card_label}.do_not_copy", card["do_not_copy"], errors)
            if "extraction_units" in card:
                validate_run2_extraction_units(f"{card_label}.extraction_units", card["extraction_units"], errors)

            if label == "source_cards":
                for key in source_required:
                    if key in card:
                        require_non_empty_string(f"{card_label}.{key}", card[key], errors)
            else:
                for key in ["timestamp_map", "keyframe_descriptions", "derived_aesthetic_cards"]:
                    if key in card:
                        validate_string_list(f"{card_label}.{key}", card[key], errors)
                for key in ["pacing_notes", "transition_observations"]:
                    if key in card:
                        require_non_empty_string(f"{card_label}.{key}", card[key], errors)
    return card_ids


def validate_run2_source_references(
    label: str,
    source_card_ids: Any,
    card_ids: set[str],
    errors: list[str],
) -> None:
    if not validate_string_list(label, source_card_ids, errors):
        return
    for index, source_card_id in enumerate(source_card_ids):
        if source_card_id not in card_ids:
            errors.append(f"{label}[{index}] {source_card_id} is not defined by source_cards or video_cards")


def validate_run2_aesthetic_move_references(
    label: str,
    aesthetic_move_ids: Any,
    move_ids: set[str],
    errors: list[str],
) -> None:
    if not validate_string_list(label, aesthetic_move_ids, errors):
        return
    for index, move_id in enumerate(aesthetic_move_ids):
        if move_id not in move_ids:
            errors.append(f"{label}[{index}] {move_id} is not defined in aesthetic_memory.json")


def validate_run2_evidence_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "evidence_memory.json", errors)
    require_keys("evidence_memory.json", data, ["schema_version", "claims"], errors)
    if "schema_version" in data:
        require_integer("evidence_memory.schema_version", data["schema_version"], errors)
    claims = data.get("claims", [])
    if not isinstance(claims, list) or not claims:
        errors.append("evidence_memory.claims must be a non-empty list")
        return

    required = ["id", "source_card_ids", "claim", "business_relevance", "allowed_use", "qa_checks"]
    for index, claim in enumerate(claims):
        label = f"evidence_memory.claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, claim, required, errors)
        for key in ["id", "claim", "business_relevance"]:
            if key in claim:
                require_non_empty_string(f"{label}.{key}", claim[key], errors)
        if "allowed_use" in claim:
            validate_choice(f"{label}.allowed_use", claim["allowed_use"], RUN2_ALLOWED_USES, errors)
        if "qa_checks" in claim:
            validate_string_list(f"{label}.qa_checks", claim["qa_checks"], errors)
        if "source_card_ids" in claim:
            validate_run2_source_references(f"{label}.source_card_ids", claim["source_card_ids"], card_ids, errors)


def validate_run2_aesthetic_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "aesthetic_memory.json", errors)
    require_keys("aesthetic_memory.json", data, ["schema_version", "moves"], errors)
    if "schema_version" in data:
        require_integer("aesthetic_memory.schema_version", data["schema_version"], errors)
    moves = data.get("moves", [])
    if not isinstance(moves, list) or not moves:
        errors.append("aesthetic_memory.moves must be a non-empty list")
        return set()

    required = [
        "id",
        "source_card_ids",
        "aesthetic_move",
        "trigger",
        "composition_rule",
        "typography_rule",
        "density_budget",
        "rhythm_role",
        "ppt_primitive",
        "negative_rules",
        "qa_signal",
    ]
    string_fields = [
        "id",
        "aesthetic_move",
        "trigger",
        "composition_rule",
        "typography_rule",
        "ppt_primitive",
        "qa_signal",
    ]
    move_ids: set[str] = set()
    for index, move in enumerate(moves):
        label = f"aesthetic_memory.moves[{index}]"
        if not isinstance(move, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, move, required, errors)
        for key in string_fields:
            if key in move:
                require_non_empty_string(f"{label}.{key}", move[key], errors)
        move_id = move.get("id")
        if isinstance(move_id, str) and move_id.strip():
            if move_id in move_ids:
                errors.append(f"{label}.id duplicates {move_id}")
            move_ids.add(move_id)
        if "source_card_ids" in move:
            validate_run2_source_references(f"{label}.source_card_ids", move["source_card_ids"], card_ids, errors)
        if "density_budget" in move:
            validate_number_mapping(f"{label}.density_budget", move["density_budget"], errors)
        if "rhythm_role" in move:
            validate_choice(f"{label}.rhythm_role", move["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "negative_rules" in move:
            validate_string_list(f"{label}.negative_rules", move["negative_rules"], errors)
    return move_ids


def validate_run2_asset_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_memory.json", errors)
    require_keys("asset_memory.json", data, ["schema_version", "assets"], errors)
    if "schema_version" in data:
        require_integer("asset_memory.schema_version", data["schema_version"], errors)
    assets = data.get("assets", [])
    if not isinstance(assets, list) or not assets:
        errors.append("asset_memory.assets must be a non-empty list")
        return

    required = [
        "id",
        "asset_type",
        "source_card_ids",
        "allowed_slide_roles",
        "provenance_state",
        "text_editability",
        "license_state",
        "render_risks",
        "accessibility_risks",
    ]
    for index, asset in enumerate(assets):
        label = f"asset_memory.assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, asset, required, errors)
        for key in ["id", "provenance_state", "text_editability", "license_state"]:
            if key in asset:
                require_non_empty_string(f"{label}.{key}", asset[key], errors)
        if "asset_type" in asset:
            validate_choice(f"{label}.asset_type", asset["asset_type"], RUN2_ASSET_TYPES, errors)
        if "source_card_ids" in asset:
            validate_run2_source_references(f"{label}.source_card_ids", asset["source_card_ids"], card_ids, errors)
        for key in ["allowed_slide_roles", "render_risks", "accessibility_risks"]:
            if key in asset:
                validate_string_list(f"{label}.{key}", asset[key], errors)


def validate_run2_narrative_spine(pack_dir: Path, move_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "narrative_spine.json", errors)
    require_keys("narrative_spine.json", data, ["schema_version", "deck_length", "slides"], errors)
    if "schema_version" in data:
        require_integer("narrative_spine.schema_version", data["schema_version"], errors)
    if "deck_length" in data:
        require_integer("narrative_spine.deck_length", data["deck_length"], errors)
    slides = data.get("slides", [])
    if not isinstance(slides, list) or not slides:
        errors.append("narrative_spine.slides must be a non-empty list")
        return

    required = ["id", "rhythm_role", "aesthetic_move_ids"]
    for index, slide in enumerate(slides):
        label = f"narrative_spine.slides[{index}]"
        if not isinstance(slide, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, slide, required, errors)
        if "id" in slide:
            require_non_empty_string(f"{label}.id", slide["id"], errors)
        if "rhythm_role" in slide:
            validate_choice(f"{label}.rhythm_role", slide["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "aesthetic_move_ids" in slide:
            validate_run2_aesthetic_move_references(
                f"{label}.aesthetic_move_ids",
                slide["aesthetic_move_ids"],
                move_ids,
                errors,
            )


def validate_run2_slide_archetypes(pack_dir: Path, move_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "slide_archetypes.json", errors)
    require_keys("slide_archetypes.json", data, ["schema_version", "archetypes"], errors)
    if "schema_version" in data:
        require_integer("slide_archetypes.schema_version", data["schema_version"], errors)
    archetypes = data.get("archetypes", [])
    if not isinstance(archetypes, list) or not archetypes:
        errors.append("slide_archetypes.archetypes must be a non-empty list")
        return

    required = ["id", "rhythm_role", "aesthetic_move_ids", "density_budget"]
    for index, archetype in enumerate(archetypes):
        label = f"slide_archetypes.archetypes[{index}]"
        if not isinstance(archetype, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, archetype, required, errors)
        if "id" in archetype:
            require_non_empty_string(f"{label}.id", archetype["id"], errors)
        if "rhythm_role" in archetype:
            validate_choice(f"{label}.rhythm_role", archetype["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "aesthetic_move_ids" in archetype:
            validate_run2_aesthetic_move_references(
                f"{label}.aesthetic_move_ids",
                archetype["aesthetic_move_ids"],
                move_ids,
                errors,
            )
        if "density_budget" in archetype:
            validate_number_mapping(f"{label}.density_budget", archetype["density_budget"], errors)


def validate_run2_8_skill_workflow_contract(
    stage_indexes: dict[str, int],
    stage_inputs: dict[str, set[str]],
    errors: list[str],
) -> None:
    stage_ids = list(RUN2_8_WORKFLOW_STAGE_INPUTS)
    for stage_id, expected_inputs in RUN2_8_WORKFLOW_STAGE_INPUTS.items():
        if stage_id not in stage_indexes:
            errors.append(f"skill_workflow.stages missing required Run 2.8 stage: {stage_id}")
            continue
        missing_inputs = expected_inputs - stage_inputs.get(stage_id, set())
        for item in sorted(missing_inputs):
            errors.append(f"skill_workflow.stages[{stage_id}].inputs missing value: {item}")

    if "generate_code_first_ppt" not in stage_indexes:
        errors.append("skill_workflow.stages missing required generation stage: generate_code_first_ppt")
        return

    generation_index = stage_indexes["generate_code_first_ppt"]
    for stage_id in stage_ids:
        if stage_id in stage_indexes and stage_indexes[stage_id] >= generation_index:
            errors.append(f"skill_workflow.stages[{stage_id}] must appear before generate_code_first_ppt")

    for before, after in zip(stage_ids, stage_ids[1:]):
        if before in stage_indexes and after in stage_indexes and stage_indexes[before] >= stage_indexes[after]:
            errors.append(f"skill_workflow.stages[{before}] must appear before {after}")


def validate_run2_skill_workflow(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "skill_workflow.json", errors)
    require_keys(
        "skill_workflow.json",
        data,
        ["schema_version", "workflow_type", "stages", "repair_triggers", "release_decisions"],
        errors,
    )
    if "schema_version" in data:
        require_integer("skill_workflow.schema_version", data["schema_version"], errors)
    if "workflow_type" in data:
        require_non_empty_string("skill_workflow.workflow_type", data["workflow_type"], errors)
    if "stage_policy" in data:
        if data["stage_policy"] != "repeat_same_five_layers_not_run3":
            errors.append("skill_workflow.stage_policy must be repeat_same_five_layers_not_run3")
    if "five_layer_loop" in data:
        validate_exact_string_set(
            "skill_workflow.five_layer_loop",
            data["five_layer_loop"],
            {
                "real_commercial_case",
                "multimodal_tutorial_case_data",
                "evidence_aesthetic_asset_memory",
                "skill_workflow",
                "rerun_and_evaluation",
            },
            errors,
        )
    if "release_decisions" in data:
        validate_string_list("skill_workflow.release_decisions", data["release_decisions"], errors)

    stages = data.get("stages", [])
    if not require_non_empty_list("skill_workflow.stages", stages, errors):
        return
    expected_order = 1
    seen_stage_ids: set[str] = set()
    stage_indexes: dict[str, int] = {}
    stage_inputs: dict[str, set[str]] = {}
    for index, stage in enumerate(stages):
        label = f"skill_workflow.stages[{index}]"
        if not isinstance(stage, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, stage, ["id", "order", "layer", "inputs", "outputs", "gates"], errors)
        if "id" in stage and require_non_empty_string(f"{label}.id", stage["id"], errors):
            if stage["id"] in seen_stage_ids:
                errors.append(f"{label}.id duplicates {stage['id']}")
            seen_stage_ids.add(stage["id"])
            stage_indexes[stage["id"]] = index
        if "order" in stage and require_integer(f"{label}.order", stage["order"], errors):
            if stage["order"] != expected_order:
                errors.append(f"{label}.order must be {expected_order}")
            expected_order += 1
        if "layer" in stage:
            require_non_empty_string(f"{label}.layer", stage["layer"], errors)
        for key in ["inputs", "outputs", "gates"]:
            if key in stage:
                valid_strings = validate_string_list(f"{label}.{key}", stage[key], errors)
                if key == "inputs" and valid_strings and isinstance(stage.get("id"), str):
                    stage_inputs[stage["id"]] = set(stage["inputs"])

    validate_run2_8_skill_workflow_contract(stage_indexes, stage_inputs, errors)

    triggers = data.get("repair_triggers", [])
    if not require_non_empty_list("skill_workflow.repair_triggers", triggers, errors):
        return
    for index, trigger in enumerate(triggers):
        label = f"skill_workflow.repair_triggers[{index}]"
        if not isinstance(trigger, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, trigger, ["id", "trigger", "recommendation", "human_gate"], errors)
        for key in ["id", "trigger", "recommendation", "human_gate"]:
            if key in trigger:
                require_non_empty_string(f"{label}.{key}", trigger[key], errors)


def validate_run2_visual_repair_policy(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "visual_repair_policy.json", errors)
    require_keys(
        "visual_repair_policy.json",
        data,
        ["schema_version", "status", "stage_policy", "default_visual_direction", "repairs"],
        errors,
    )
    if "schema_version" in data:
        require_integer("visual_repair_policy.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_6r_visual_repair_policy_public_blocked":
        errors.append("visual_repair_policy.status must be run2_6r_visual_repair_policy_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("visual_repair_policy.stage_policy must be repeat_same_five_layers_not_run3")
    if (
        "default_visual_direction" in data
        and data["default_visual_direction"] != "light_first_editorial_graphite_with_vivid_proof_color"
    ):
        errors.append(
            "visual_repair_policy.default_visual_direction must be "
            "light_first_editorial_graphite_with_vivid_proof_color"
        )

    repairs = data.get("repairs", [])
    if not require_non_empty_list("visual_repair_policy.repairs", repairs, errors):
        return set()

    seen_repair_ids: set[str] = set()
    for index, repair in enumerate(repairs):
        label = f"visual_repair_policy.repairs[{index}]"
        if not isinstance(repair, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, repair, RUN2_6R_REPAIR_FIELDS, errors)
        repair_id = repair.get("id")
        if "id" in repair and require_non_empty_string(f"{label}.id", repair_id, errors):
            if repair_id in seen_repair_ids:
                errors.append(f"{label}.id duplicates {repair_id}")
            seen_repair_ids.add(repair_id)
        if "target_slide_roles" in repair and validate_string_list(
            f"{label}.target_slide_roles",
            repair["target_slide_roles"],
            errors,
        ):
            for role_index, role in enumerate(repair["target_slide_roles"]):
                validate_choice(
                    f"{label}.target_slide_roles[{role_index}]",
                    role,
                    RUN2_6R_REPAIR_ROLES,
                    errors,
                )
        if "source_policy_ids" in repair:
            validate_string_list(f"{label}.source_policy_ids", repair["source_policy_ids"], errors)
        for key in ["typography_delta", "spacing_delta", "composition_delta"]:
            if key in repair:
                require_non_empty_string(f"{label}.{key}", repair[key], errors)
        if "theme_delta" in repair:
            validate_string_mentions(f"{label}.theme_delta", repair["theme_delta"], ["forest-green", "source-brand"], errors)
        if "must_differ_from" in repair:
            validate_exact_string_set(
                f"{label}.must_differ_from",
                repair["must_differ_from"],
                {"ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"},
                errors,
            )
        if "native_ppt_requirements" in repair:
            validate_combined_terms(f"{label}.native_ppt_requirements", repair["native_ppt_requirements"], ["native", "editable"], errors)
        if "qa_probe" in repair:
            validate_string_mentions(f"{label}.qa_probe", repair["qa_probe"], ["contact sheet"], errors)
        if "release_boundary" in repair:
            validate_public_blocked_boundary(f"{label}.release_boundary", repair["release_boundary"], errors)

    for repair_id in sorted(RUN2_6R_REPAIR_IDS - seen_repair_ids):
        errors.append(f"visual_repair_policy.repairs missing repair id: {repair_id}")
    for repair_id in sorted(seen_repair_ids - RUN2_6R_REPAIR_IDS):
        errors.append(f"visual_repair_policy.repairs has unexpected repair id: {repair_id}")
    return seen_repair_ids


def validate_run2_7_commercial_usecase(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "run2_7_commercial_usecase.json", errors)
    require_keys(
        "run2_7_commercial_usecase.json",
        data,
        [
            "schema_version",
            "status",
            "stage_policy",
            "id",
            "primary_usecase",
            "audience",
            "business_job",
            "business_decision",
            "deck_mission",
            "six_slide_arc",
            "must_show",
            "must_not_show",
            "proof_questions",
            "release_boundary",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_commercial_usecase.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_commercial_usecase_public_blocked":
        errors.append("run2_7_commercial_usecase.status must be run2_7_commercial_usecase_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_commercial_usecase.stage_policy must be repeat_same_five_layers_not_run3")
    usecase_id = data.get("id")
    usecase_ids: set[str] = set()
    if "id" in data and require_non_empty_string("run2_7_commercial_usecase.id", usecase_id, errors):
        usecase_ids.add(usecase_id)
    for key in ["primary_usecase", "business_decision", "deck_mission"]:
        if key in data:
            require_non_empty_string(f"run2_7_commercial_usecase.{key}", data[key], errors)
    if "audience" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.audience",
            data["audience"],
            ["ai product builders", "design engineering leaders", "technical founders"],
            errors,
        )
    if "business_job" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.business_job",
            data["business_job"],
            ["product-system learning", "not one-shot prompting"],
            errors,
        )
    if "must_not_show" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.must_not_show",
            data["must_not_show"],
            ["copy", "source brand", "full-slide raster"],
            errors,
        )
    if "proof_questions" in data:
        validate_combined_terms(
            "run2_7_commercial_usecase.proof_questions",
            data["proof_questions"],
            ["data", "memory", "workflow", "ppt"],
            errors,
        )
    if "must_show" in data:
        validate_string_list("run2_7_commercial_usecase.must_show", data["must_show"], errors)
    arc = data.get("six_slide_arc", [])
    if require_non_empty_list("run2_7_commercial_usecase.six_slide_arc", arc, errors):
        expected_roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
        actual_roles: list[str] = []
        for index, slide in enumerate(arc):
            label = f"run2_7_commercial_usecase.six_slide_arc[{index}]"
            if not isinstance(slide, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(label, slide, ["slide_id", "rhythm_role", "job", "must_show", "must_not_show"], errors)
            if "slide_id" in slide:
                require_non_empty_string(f"{label}.slide_id", slide["slide_id"], errors)
            role = slide.get("rhythm_role")
            if "rhythm_role" in slide and validate_choice(f"{label}.rhythm_role", role, RUN2_6R_REPAIR_ROLES, errors):
                actual_roles.append(role)
            if "job" in slide:
                require_non_empty_string(f"{label}.job", slide["job"], errors)
            for key in ["must_show", "must_not_show"]:
                if key in slide:
                    validate_string_list(f"{label}.{key}", slide[key], errors)
        if actual_roles != expected_roles:
            errors.append("run2_7_commercial_usecase.six_slide_arc rhythm_role order must be cover, setup, contrast, proof, climax, close")
    if "release_boundary" in data:
        validate_public_blocked_boundary("run2_7_commercial_usecase.release_boundary", data["release_boundary"], errors)
    return usecase_ids


def validate_run2_7_source_records(pack_dir: Path, source_ids: set[str], errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "run2_7_multimodal_source_records.json", errors)
    require_keys(
        "run2_7_multimodal_source_records.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "records", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_multimodal_source_records.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_multimodal_source_records_public_blocked":
        errors.append("run2_7_multimodal_source_records.status must be run2_7_multimodal_source_records_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_multimodal_source_records.stage_policy must be repeat_same_five_layers_not_run3")
    storage_policy = data.get("storage_policy")
    if isinstance(storage_policy, dict):
        raw_media = storage_policy.get("raw_media")
        if isinstance(raw_media, str) and raw_media != "forbidden":
            errors.append("run2_7_multimodal_source_records.storage_policy.raw_media must be forbidden")
    elif "storage_policy" in data:
        errors.append("run2_7_multimodal_source_records.storage_policy must be a non-empty object")
    if "qa_gates" in data:
        validate_string_list("run2_7_multimodal_source_records.qa_gates", data["qa_gates"], errors)

    records = data.get("records", [])
    if not require_non_empty_list("run2_7_multimodal_source_records.records", records, errors):
        return set()
    required = [
        "id",
        "source_id",
        "source_type",
        "allowed_use",
        "anchor",
        "modalities",
        "visual_observation",
        "transcript_or_teaching_claim",
        "extracted_design_rule",
        "slide_roles",
        "native_ppt_implication",
        "anti_copy_boundary",
        "qa_probe",
        "release_boundary",
    ]
    seen_record_ids: set[str] = set()
    covered_modalities: set[str] = set()
    for index, record in enumerate(records):
        label = f"run2_7_multimodal_source_records.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, record, required, errors)
        record_id = record.get("id")
        if "id" in record and require_non_empty_string(f"{label}.id", record_id, errors):
            if record_id in seen_record_ids:
                errors.append(f"{label}.id duplicates {record_id}")
            seen_record_ids.add(record_id)
        source_id = record.get("source_id")
        if "source_id" in record and require_non_empty_string(f"{label}.source_id", source_id, errors):
            if source_id not in source_ids:
                errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
        if "allowed_use" in record and record["allowed_use"] != "derived_rules_only":
            errors.append(f"{label}.allowed_use must be derived_rules_only")
        if "modalities" in record and validate_string_list(f"{label}.modalities", record["modalities"], errors):
            for modality in record["modalities"]:
                if modality not in RUN2_MULTIMODAL_MODALITIES:
                    errors.append(f"{label}.modalities has unexpected value: {modality}")
                else:
                    covered_modalities.add(modality)
        if "slide_roles" in record and validate_string_list(f"{label}.slide_roles", record["slide_roles"], errors):
            for role in record["slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.slide_roles has unexpected value: {role}")
        for key in ["source_type", "anchor", "visual_observation", "transcript_or_teaching_claim", "extracted_design_rule"]:
            if key in record:
                require_non_empty_string(f"{label}.{key}", record[key], errors)
        if "native_ppt_implication" in record:
            validate_string_mentions(f"{label}.native_ppt_implication", record["native_ppt_implication"], ["native", "editable"], errors)
        if "anti_copy_boundary" in record:
            validate_string_mentions(f"{label}.anti_copy_boundary", record["anti_copy_boundary"], ["do not copy"], errors)
        if "qa_probe" in record:
            validate_string_mentions(f"{label}.qa_probe", record["qa_probe"], ["contact sheet"], errors)
        if "release_boundary" in record:
            validate_public_blocked_boundary(f"{label}.release_boundary", record["release_boundary"], errors)
    for modality in sorted(RUN2_MULTIMODAL_MODALITIES - covered_modalities):
        errors.append(f"run2_7_multimodal_source_records.records missing modality coverage: {modality}")
    return seen_record_ids


def validate_run2_7_design_memory(
    pack_dir: Path,
    source_record_ids: set[str],
    usecase_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "run2_7_design_memory.json", errors)
    require_keys(
        "run2_7_design_memory.json",
        data,
        ["schema_version", "status", "stage_policy", "memory_type", "memories", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_design_memory.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_design_memory_public_blocked":
        errors.append("run2_7_design_memory.status must be run2_7_design_memory_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_design_memory.stage_policy must be repeat_same_five_layers_not_run3")
    if "memory_type" in data and data["memory_type"] != "deterministic_serializable_rules":
        errors.append("run2_7_design_memory.memory_type must be deterministic_serializable_rules")
    if "qa_gates" in data:
        validate_string_list("run2_7_design_memory.qa_gates", data["qa_gates"], errors)

    memories = data.get("memories", [])
    if not require_non_empty_list("run2_7_design_memory.memories", memories, errors):
        return set()
    memory_ids: set[str] = set()
    for index, memory in enumerate(memories):
        label = f"run2_7_design_memory.memories[{index}]"
        if not isinstance(memory, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, memory, RUN2_7_MEMORY_FIELDS, errors)
        memory_id = memory.get("id")
        if "id" in memory and require_non_empty_string(f"{label}.id", memory_id, errors):
            if memory_id in memory_ids:
                errors.append(f"{label}.id duplicates {memory_id}")
            memory_ids.add(memory_id)
        if "source_record_ids" in memory:
            validate_known_string_references(
                f"{label}.source_record_ids",
                memory["source_record_ids"],
                source_record_ids,
                "Run 2.7 source record",
                errors,
            )
        if "applicable_usecases" in memory:
            validate_known_string_references(
                f"{label}.applicable_usecases",
                memory["applicable_usecases"],
                usecase_ids,
                "Run 2.7 usecase",
                errors,
            )
        if "applicable_slide_roles" in memory and validate_string_list(
            f"{label}.applicable_slide_roles", memory["applicable_slide_roles"], errors
        ):
            for role in memory["applicable_slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.applicable_slide_roles has unexpected value: {role}")
        for key in ["typography_rules", "spacing_rules", "composition_rules", "rhythm_rules", "forbidden_patterns"]:
            if key in memory:
                validate_string_list(f"{label}.{key}", memory[key], errors)
        if "native_ppt_generation_requirements" in memory:
            validate_combined_terms(
                f"{label}.native_ppt_generation_requirements",
                memory["native_ppt_generation_requirements"],
                ["native", "editable", "trace"],
                errors,
            )
        if "qa_probes" in memory:
            validate_combined_terms(f"{label}.qa_probes", memory["qa_probes"], ["contact sheet"], errors)
        if "release_boundary" in memory:
            validate_public_blocked_boundary(f"{label}.release_boundary", memory["release_boundary"], errors)
    return memory_ids


def validate_run2_7_workflow_policy(
    pack_dir: Path,
    source_record_ids: set[str],
    usecase_ids: set[str],
    memory_ids: set[str],
    visual_repair_ids: set[str],
    errors: list[str],
) -> None:
    data = load_json(pack_dir / "run2_7_workflow_policy.json", errors)
    require_keys(
        "run2_7_workflow_policy.json",
        data,
        [
            "schema_version",
            "status",
            "stage_policy",
            "commercial_usecase_id",
            "selection_chain",
            "slide_role_memory_map",
            "qa_gates",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_workflow_policy.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_7_workflow_policy_public_blocked":
        errors.append("run2_7_workflow_policy.status must be run2_7_workflow_policy_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_workflow_policy.stage_policy must be repeat_same_five_layers_not_run3")
    if "qa_gates" in data:
        validate_string_list("run2_7_workflow_policy.qa_gates", data["qa_gates"], errors)
    usecase_id = data.get("commercial_usecase_id")
    if "commercial_usecase_id" in data and require_non_empty_string(
        "run2_7_workflow_policy.commercial_usecase_id", usecase_id, errors
    ):
        if usecase_id not in usecase_ids:
            errors.append(f"run2_7_workflow_policy.commercial_usecase_id references unknown Run 2.7 usecase: {usecase_id}")
    if "selection_chain" in data:
        validate_exact_string_set(
            "run2_7_workflow_policy.selection_chain",
            data["selection_chain"],
            {
                "commercial_usecase",
                "source_record_ids",
                "typography_memory_id",
                "spacing_memory_id",
                "composition_memory_id",
                "rhythm_memory_id",
                "brand_sanitization_memory_id",
                "visual_repair_policy_ids",
                "native_ppt_generation",
                "qa_gate",
            },
            errors,
        )

    mappings = data.get("slide_role_memory_map", [])
    if not require_non_empty_list("run2_7_workflow_policy.slide_role_memory_map", mappings, errors):
        return
    required = [
        "rhythm_role",
        "commercial_usecase_id",
        "source_record_ids",
        "design_memory_ids",
        "workflow_decision_ids",
        "visual_repair_policy_ids",
        "native_ppt_generation",
        "workflow_gates",
        "trace_fields",
    ]
    for index, mapping in enumerate(mappings):
        label = f"run2_7_workflow_policy.slide_role_memory_map[{index}]"
        if not isinstance(mapping, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, mapping, required, errors)
        if "rhythm_role" in mapping:
            validate_choice(f"{label}.rhythm_role", mapping["rhythm_role"], RUN2_6R_REPAIR_ROLES, errors)
        if "commercial_usecase_id" in mapping:
            mapping_usecase_id = mapping["commercial_usecase_id"]
            if require_non_empty_string(f"{label}.commercial_usecase_id", mapping_usecase_id, errors):
                if mapping_usecase_id not in usecase_ids:
                    errors.append(f"{label}.commercial_usecase_id references unknown Run 2.7 usecase: {mapping_usecase_id}")
        if "source_record_ids" in mapping:
            validate_known_string_references(
                f"{label}.source_record_ids",
                mapping["source_record_ids"],
                source_record_ids,
                "Run 2.7 source record",
                errors,
            )
        if "design_memory_ids" in mapping:
            validate_known_string_references(
                f"{label}.design_memory_ids",
                mapping["design_memory_ids"],
                memory_ids,
                "Run 2.7 design memory",
                errors,
            )
        if "workflow_decision_ids" in mapping:
            validate_string_list(f"{label}.workflow_decision_ids", mapping["workflow_decision_ids"], errors)
        if "visual_repair_policy_ids" in mapping:
            validate_known_string_references(
                f"{label}.visual_repair_policy_ids",
                mapping["visual_repair_policy_ids"],
                visual_repair_ids,
                "visual repair policy",
                errors,
            )
        if "native_ppt_generation" in mapping:
            validate_string_mentions(f"{label}.native_ppt_generation", mapping["native_ppt_generation"], ["native", "editable"], errors)
        if "workflow_gates" in mapping:
            validate_combined_terms(
                f"{label}.workflow_gates",
                mapping["workflow_gates"],
                ["public_blocked", "native", "source-brand"],
                errors,
            )
        if "trace_fields" in mapping:
            validate_exact_string_set(f"{label}.trace_fields", mapping["trace_fields"], RUN2_7_TRACE_FIELDS, errors)


def validate_run2_8_trace_manifest_contract(pack_dir: Path, errors: list[str]) -> set[str]:
    path = pack_dir / "results" / "trace_manifest_contract.json"
    if not path.exists():
        return set()
    data = load_json(path, errors)
    require_keys(
        "trace_manifest_contract.json",
        data,
        ["schema_version", "per_slide_required_fields"],
        errors,
    )
    if "schema_version" in data:
        require_integer("trace_manifest_contract.schema_version", data["schema_version"], errors)
    fields = data.get("per_slide_required_fields", [])
    if not validate_string_list("trace_manifest_contract.per_slide_required_fields", fields, errors):
        return set()
    actual = set(fields)
    for field in sorted(RUN2_8_TRACE_FIELDS - actual):
        errors.append(f"trace_manifest_contract.per_slide_required_fields missing value: {field}")
    return actual


def validate_run2_8_tutorial_decomposition(
    pack_dir: Path,
    source_ids: set[str],
    run2_7_source_record_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "run2_8_tutorial_decomposition.json", errors)
    require_keys(
        "run2_8_tutorial_decomposition.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "units"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_8_tutorial_decomposition.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_8_tutorial_decomposition_public_blocked":
        errors.append(
            "run2_8_tutorial_decomposition.status must be run2_8_tutorial_decomposition_public_blocked"
        )
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_8_tutorial_decomposition.stage_policy must be repeat_same_five_layers_not_run3")
    storage_policy = data.get("storage_policy")
    if isinstance(storage_policy, dict):
        raw_media = storage_policy.get("raw_media")
        if isinstance(raw_media, str) and raw_media != "forbidden":
            errors.append("run2_8_tutorial_decomposition.storage_policy.raw_media must be forbidden")
        validate_no_external_media_reference("run2_8_tutorial_decomposition.storage_policy", storage_policy, errors)
    elif "storage_policy" in data:
        errors.append("run2_8_tutorial_decomposition.storage_policy must be a non-empty object")

    units = data.get("units", [])
    if not require_non_empty_list("run2_8_tutorial_decomposition.units", units, errors):
        return set()
    unit_ids: set[str] = set()
    derived_modalities = {"video", "audio", "transcript", "image_reference", "interaction"}
    for index, unit in enumerate(units):
        label = f"run2_8_tutorial_decomposition.units[{index}]"
        if not isinstance(unit, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, unit, RUN2_8_DECOMPOSITION_FIELDS, errors)
        validate_no_external_media_reference(label, unit, errors)
        unit_id = unit.get("id")
        if "id" in unit and require_non_empty_string(f"{label}.id", unit_id, errors):
            if unit_id in unit_ids:
                errors.append(f"{label}.id duplicates {unit_id}")
            unit_ids.add(unit_id)
        if "source_record_ids" in unit:
            validate_known_string_references(
                f"{label}.source_record_ids",
                unit["source_record_ids"],
                run2_7_source_record_ids,
                "Run 2.7 source record",
                errors,
            )
        if "source_ids" in unit:
            validate_known_string_references(
                f"{label}.source_ids",
                unit["source_ids"],
                source_ids,
                "source",
                errors,
            )
        if "modality_mix" in unit and validate_string_list(f"{label}.modality_mix", unit["modality_mix"], errors):
            actual_modalities = set(unit["modality_mix"])
            for modality in actual_modalities:
                if modality not in RUN2_MULTIMODAL_MODALITIES:
                    errors.append(f"{label}.modality_mix has unexpected value: {modality}")
            if not actual_modalities & derived_modalities:
                errors.append(f"{label}.modality_mix must include video, audio, transcript, image_reference, or interaction")
        for key in [
            "tutorial_anchor",
            "observed_design_move",
            "derived_rule",
            "native_ppt_obligation",
            "failure_probe",
            "anti_copy_boundary",
            "qa_probe",
        ]:
            if key in unit:
                require_non_empty_string(f"{label}.{key}", unit[key], errors)
        if "code_generation_binding" in unit:
            if require_non_empty_string(f"{label}.code_generation_binding", unit["code_generation_binding"], errors):
                validate_string_mentions(f"{label}.code_generation_binding", unit["code_generation_binding"], ["native"], errors)
        if "layout_budget" in unit:
            validate_number_mapping(f"{label}.layout_budget", unit["layout_budget"], errors)
        if "release_boundary" in unit:
            validate_run2_8_release_boundary(f"{label}.release_boundary", unit["release_boundary"], errors)
    return unit_ids


def validate_run2_8_executable_design_memory(
    pack_dir: Path,
    decomposition_unit_ids: set[str],
    errors: list[str],
) -> tuple[set[str], set[str]]:
    data = load_json(pack_dir / "run2_8_executable_design_memory.json", errors)
    require_keys(
        "run2_8_executable_design_memory.json",
        data,
        ["schema_version", "status", "stage_policy", "memory_type", "bindings"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_8_executable_design_memory.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_8_executable_design_memory_public_blocked":
        errors.append(
            "run2_8_executable_design_memory.status must be run2_8_executable_design_memory_public_blocked"
        )
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_8_executable_design_memory.stage_policy must be repeat_same_five_layers_not_run3")
    if "memory_type" in data and data["memory_type"] != "executable_schema_bindings":
        errors.append("run2_8_executable_design_memory.memory_type must be executable_schema_bindings")

    bindings = data.get("bindings", [])
    if not require_non_empty_list("run2_8_executable_design_memory.bindings", bindings, errors):
        return set(), set()
    binding_ids: set[str] = set()
    code_binding_ids: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"run2_8_executable_design_memory.bindings[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, binding, RUN2_8_MEMORY_BINDING_FIELDS, errors)
        validate_no_external_media_reference(label, binding, errors)
        binding_id = binding.get("id")
        if "id" in binding and require_non_empty_string(f"{label}.id", binding_id, errors):
            if binding_id in binding_ids:
                errors.append(f"{label}.id duplicates {binding_id}")
            binding_ids.add(binding_id)
        if "decomposition_unit_ids" in binding:
            validate_known_string_references(
                f"{label}.decomposition_unit_ids",
                binding["decomposition_unit_ids"],
                decomposition_unit_ids,
                "Run 2.8 decomposition unit",
                errors,
            )
        if "applies_to_slide_roles" in binding and validate_string_list(
            f"{label}.applies_to_slide_roles",
            binding["applies_to_slide_roles"],
            errors,
        ):
            for role in binding["applies_to_slide_roles"]:
                if role not in RUN2_RHYTHM_ROLES:
                    errors.append(f"{label}.applies_to_slide_roles has unexpected value: {role}")
        for key in [
            "native_ppt_constraints",
            "typography_constraints",
            "spacing_constraints",
            "composition_constraints",
        ]:
            if key in binding:
                validate_string_list(f"{label}.{key}", binding[key], errors)
        for key in ["design_token", "negative_control_failure", "qa_probe"]:
            if key in binding:
                require_non_empty_string(f"{label}.{key}", binding[key], errors)
        code_binding = binding.get("code_binding")
        if "code_binding" in binding:
            if require_non_empty_dict(f"{label}.code_binding", code_binding, errors):
                require_keys(f"{label}.code_binding", code_binding, ["function_name", "params", "layout_budget"], errors)
                function_name = code_binding.get("function_name")
                if "function_name" in code_binding and require_non_empty_string(
                    f"{label}.code_binding.function_name",
                    function_name,
                    errors,
                ):
                    code_binding_ids.add(function_name)
                if "params" in code_binding:
                    require_non_empty_dict(f"{label}.code_binding.params", code_binding["params"], errors)
                if "layout_budget" in code_binding:
                    require_non_empty_dict(f"{label}.code_binding.layout_budget", code_binding["layout_budget"], errors)
                code_binding_text = json.dumps(code_binding)
                if not any(term in code_binding_text for term in RUN2_8_CODE_BINDING_TERMS):
                    errors.append(f"{label}.code_binding must mention a Run 2.8 code binding term")
        if "release_boundary" in binding:
            validate_run2_8_release_boundary(f"{label}.release_boundary", binding["release_boundary"], errors)
    return binding_ids, code_binding_ids


def validate_run2_8_workflow_gate_matrix(
    pack_dir: Path,
    decomposition_unit_ids: set[str],
    memory_binding_ids: set[str],
    code_binding_ids: set[str],
    trace_fields: set[str],
    errors: list[str],
) -> None:
    data = load_json(pack_dir / "run2_8_workflow_gate_matrix.json", errors)
    require_keys(
        "run2_8_workflow_gate_matrix.json",
        data,
        ["schema_version", "status", "stage_policy", "selection_chain", "gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_8_workflow_gate_matrix.schema_version", data["schema_version"], errors)
    if "status" in data and data["status"] != "run2_8_workflow_gate_matrix_public_blocked":
        errors.append("run2_8_workflow_gate_matrix.status must be run2_8_workflow_gate_matrix_public_blocked")
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_8_workflow_gate_matrix.stage_policy must be repeat_same_five_layers_not_run3")
    if "selection_chain" in data:
        validate_exact_string_set(
            "run2_8_workflow_gate_matrix.selection_chain",
            data["selection_chain"],
            RUN2_8_SELECTION_CHAIN,
            errors,
        )

    gates = data.get("gates", [])
    if not require_non_empty_list("run2_8_workflow_gate_matrix.gates", gates, errors):
        return
    gate_ids: set[str] = set()
    for index, gate in enumerate(gates):
        label = f"run2_8_workflow_gate_matrix.gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, gate, RUN2_8_GATE_FIELDS, errors)
        validate_no_external_media_reference(label, gate, errors)
        gate_id = gate.get("id")
        if "id" in gate and require_non_empty_string(f"{label}.id", gate_id, errors):
            if gate_id in gate_ids:
                errors.append(f"{label}.id duplicates {gate_id}")
            gate_ids.add(gate_id)
        if "slide_role" in gate:
            validate_choice(f"{label}.slide_role", gate["slide_role"], RUN2_6R_REPAIR_ROLES, errors)
        if "decomposition_unit_ids" in gate:
            validate_known_string_references(
                f"{label}.decomposition_unit_ids",
                gate["decomposition_unit_ids"],
                decomposition_unit_ids,
                "Run 2.8 decomposition unit",
                errors,
            )
        if "memory_binding_ids" in gate:
            validate_known_string_references(
                f"{label}.memory_binding_ids",
                gate["memory_binding_ids"],
                memory_binding_ids,
                "Run 2.8 memory binding",
                errors,
            )
        if "required_code_bindings" in gate:
            validate_known_string_references(
                f"{label}.required_code_bindings",
                gate["required_code_bindings"],
                code_binding_ids,
                "Run 2.8 code binding",
                errors,
            )
        if "layout_budget" in gate:
            validate_number_mapping(f"{label}.layout_budget", gate["layout_budget"], errors)
        if "pass_fail_checks" in gate:
            validate_string_list(f"{label}.pass_fail_checks", gate["pass_fail_checks"], errors)
        if "trace_fields" in gate and validate_string_list(f"{label}.trace_fields", gate["trace_fields"], errors):
            actual_trace_fields = set(gate["trace_fields"])
            for field in sorted(RUN2_8_TRACE_FIELDS - actual_trace_fields):
                errors.append(f"{label}.trace_fields missing value: {field}")
            for field in gate["trace_fields"]:
                if trace_fields and field not in trace_fields:
                    errors.append(f"{label}.trace_fields references unknown trace field: {field}")
        if "public_release_gate" in gate:
            validate_run2_8_release_boundary(f"{label}.public_release_gate", gate["public_release_gate"], errors)


def resolve_run2_source_input_path(pack_dir: Path, source_path: str) -> Path:
    pack_prefix = "docs/product/ppt-run2-data-skill-quality/"
    if source_path.startswith(pack_prefix):
        return pack_dir / source_path.removeprefix(pack_prefix)
    return pack_dir / source_path


def collect_run2_record_ids(
    pack_dir: Path,
    source_path: str,
    record_key: str,
    id_key: str,
    errors: list[str],
) -> set[str]:
    path = resolve_run2_source_input_path(pack_dir, source_path)
    if not path.exists():
        errors.append(f"run2_73_visual_grammar_modules source input missing: {source_path}")
        return set()
    data = load_json(path, errors)
    records = data.get(record_key, [])
    if not require_non_empty_list(f"{path.name}.{record_key}", records, errors):
        return set()
    ids: set[str] = set()
    for index, record in enumerate(records):
        label = f"{path.name}.{record_key}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        record_id = record.get(id_key)
        if require_non_empty_string(f"{label}.{id_key}", record_id, errors):
            if record_id in ids:
                errors.append(f"{label}.{id_key} duplicates {record_id}")
            ids.add(record_id)
    return ids


def validate_run2_73_visual_grammar_modules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "run2_73_visual_grammar_modules.json", errors)
    require_keys(
        "run2_73_visual_grammar_modules.json",
        data,
        [
            "artifact_id",
            "part",
            "schema_version",
            "status",
            "selected_usecase_id",
            "objective",
            "artifact_scope",
            "source_inputs",
            "stage_policy",
            "global_visual_grammar_contract",
            "page_type_to_visual_grammar",
            "visual_grammar_modules",
            "module_geometry_blueprints",
            "module_selection_rules",
            "coverage_matrix",
            "success_criteria_check",
            "traceability_summary",
        ],
        errors,
    )
    if data.get("artifact_id") != "run2_73_visual_grammar_modules":
        errors.append("run2_73_visual_grammar_modules.artifact_id must be run2_73_visual_grammar_modules")
    if data.get("part") != "Part E":
        errors.append("run2_73_visual_grammar_modules.part must be Part E")
    if "schema_version" in data:
        require_non_empty_string("run2_73_visual_grammar_modules.schema_version", data["schema_version"], errors)
    if data.get("status") != RUN2_73_VISUAL_GRAMMAR_STATUS:
        errors.append(f"run2_73_visual_grammar_modules.status must be {RUN2_73_VISUAL_GRAMMAR_STATUS}")
    if data.get("stage_policy") != RUN2_73_VISUAL_GRAMMAR_STAGE_POLICY:
        errors.append(
            "run2_73_visual_grammar_modules.stage_policy must be "
            f"{RUN2_73_VISUAL_GRAMMAR_STAGE_POLICY}"
        )

    scope = data.get("artifact_scope")
    if require_non_empty_dict("run2_73_visual_grammar_modules.artifact_scope", scope, errors):
        does_not_start = scope.get("does_not_start", [])
        if validate_string_list("run2_73_visual_grammar_modules.artifact_scope.does_not_start", does_not_start, errors):
            actual_scope = set(does_not_start)
            for item in sorted(RUN2_73_VISUAL_GRAMMAR_FORBIDDEN_SCOPE - actual_scope):
                errors.append(
                    "run2_73_visual_grammar_modules.artifact_scope.does_not_start "
                    f"must include {item}"
                )

    source_inputs = data.get("source_inputs", [])
    if validate_run2_73_visual_grammar_source_inputs(source_inputs, errors):
        source_paths = {
            source.get("path")
            for source in source_inputs
            if isinstance(source, dict) and isinstance(source.get("path"), str)
        }
        for source_path in sorted(RUN2_73_VISUAL_GRAMMAR_SOURCE_PATHS - source_paths):
            errors.append(f"run2_73_visual_grammar_modules.source_inputs missing path: {source_path}")

    source_reference_ids = collect_run2_record_ids(
        pack_dir,
        "docs/product/ppt-run2-data-skill-quality/run2_66_reference_first_design_grammar.json",
        "role_design_grammar_records",
        "reference_archetype_id",
        errors,
    )
    source_semantic_asset_ids = collect_run2_record_ids(
        pack_dir,
        "docs/product/ppt-run2-data-skill-quality/run2_43_semantic_visual_asset_memory.json",
        "semantic_visual_asset_records",
        "semantic_asset_id",
        errors,
    )
    source_object_grammar_ids = collect_run2_record_ids(
        pack_dir,
        "docs/product/ppt-run2-data-skill-quality/run2_46_visual_object_grammar_memory.json",
        "visual_object_grammar_records",
        "visual_object_grammar_id",
        errors,
    )

    validate_run2_73_visual_grammar_pages(
        data.get("page_type_to_visual_grammar", []),
        source_reference_ids,
        source_semantic_asset_ids,
        source_object_grammar_ids,
        errors,
    )
    validate_run2_73_visual_grammar_module_records(data.get("visual_grammar_modules", []), errors)
    validate_run2_73_visual_grammar_blueprints(data.get("module_geometry_blueprints", []), errors)
    validate_run2_73_visual_grammar_selection_rules(data.get("module_selection_rules", []), errors)
    validate_run2_73_visual_grammar_coverage(
        data.get("coverage_matrix", {}),
        source_reference_ids,
        source_semantic_asset_ids,
        source_object_grammar_ids,
        errors,
    )
    validate_run2_73_visual_grammar_success(data.get("success_criteria_check", {}), errors)
    validate_run2_73_visual_grammar_trace_summary(data.get("traceability_summary", {}), errors)


def validate_run2_73_visual_grammar_source_inputs(value: Any, errors: list[str]) -> bool:
    if not require_non_empty_list("run2_73_visual_grammar_modules.source_inputs", value, errors):
        return False
    ok = True
    for index, source in enumerate(value):
        label = f"run2_73_visual_grammar_modules.source_inputs[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            ok = False
            continue
        require_keys(label, source, ["path", "required", "available", "record_count", "id_field", "use_in_this_artifact"], errors)
        if "path" in source:
            ok = require_non_empty_string(f"{label}.path", source["path"], errors) and ok
        for key in ["required", "available"]:
            if key in source and type(source[key]) is not bool:
                errors.append(f"{label}.{key} must be a boolean")
                ok = False
        if "record_count" in source and not require_integer(f"{label}.record_count", source["record_count"], errors):
            ok = False
    return ok


def validate_run2_73_visual_grammar_pages(
    value: Any,
    source_reference_ids: set[str],
    source_semantic_asset_ids: set[str],
    source_object_grammar_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_list("run2_73_visual_grammar_modules.page_type_to_visual_grammar", value, errors):
        return
    roles: list[str] = []
    for index, page in enumerate(value):
        label = f"run2_73_visual_grammar_modules.page_type_to_visual_grammar[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(
            label,
            page,
            [
                "page_type",
                "slide_index",
                "visual_role",
                "primary_visual_grammar_module",
                "module_variant",
                "source_reference_archetype_id",
                "source_visual_object_grammar_id",
                "source_semantic_asset_ids",
                "main_structure",
                "draw_order",
                "forbidden_fallbacks",
                "success_probe",
            ],
            errors,
        )
        role = page.get("page_type")
        module_id = page.get("primary_visual_grammar_module")
        if "page_type" in page and validate_choice(f"{label}.page_type", role, set(RUN2_73_VISUAL_GRAMMAR_ROLES), errors):
            roles.append(role)
        if "slide_index" in page:
            require_integer(f"{label}.slide_index", page["slide_index"], errors)
        if "primary_visual_grammar_module" in page:
            validate_choice(
                f"{label}.primary_visual_grammar_module",
                module_id,
                RUN2_73_VISUAL_GRAMMAR_MODULE_IDS,
                errors,
            )
            if isinstance(role, str) and role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
                expected = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
                if module_id != expected:
                    errors.append(f"{label}.primary_visual_grammar_module must be {expected}")
        if "source_reference_archetype_id" in page:
            source_id = page["source_reference_archetype_id"]
            if require_non_empty_string(f"{label}.source_reference_archetype_id", source_id, errors):
                if source_id not in source_reference_ids:
                    errors.append(f"{label}.source_reference_archetype_id references unknown source archetype: {source_id}")
        if "source_visual_object_grammar_id" in page:
            grammar_id = page["source_visual_object_grammar_id"]
            if require_non_empty_string(f"{label}.source_visual_object_grammar_id", grammar_id, errors):
                if grammar_id not in source_object_grammar_ids:
                    errors.append(f"{label}.source_visual_object_grammar_id references unknown visual object grammar: {grammar_id}")
        if "source_semantic_asset_ids" in page:
            validate_known_string_references(
                f"{label}.source_semantic_asset_ids",
                page["source_semantic_asset_ids"],
                source_semantic_asset_ids,
                "semantic visual asset",
                errors,
            )
            if isinstance(page["source_semantic_asset_ids"], list) and len(page["source_semantic_asset_ids"]) < 3:
                errors.append(f"{label}.source_semantic_asset_ids must contain at least 3 assets")
        main_structure = page.get("main_structure")
        if "main_structure" in page and require_non_empty_dict(f"{label}.main_structure", main_structure, errors):
            require_non_empty_string(f"{label}.main_structure.name", main_structure.get("name"), errors)
            basis = main_structure.get("non_rectangular_or_non_card_basis", [])
            if validate_string_list(f"{label}.main_structure.non_rectangular_or_non_card_basis", basis, errors):
                if len(basis) < 3:
                    errors.append(f"{label}.main_structure.non_rectangular_or_non_card_basis must contain at least 3 reasons")
            require_non_empty_string(
                f"{label}.main_structure.serves_content_by",
                main_structure.get("serves_content_by"),
                errors,
            )
        for list_key in ["draw_order", "forbidden_fallbacks"]:
            if list_key in page:
                validate_string_list(f"{label}.{list_key}", page[list_key], errors)
                if list_key == "draw_order" and isinstance(page[list_key], list) and len(page[list_key]) < 3:
                    errors.append(f"{label}.draw_order must contain at least 3 steps")
        if "success_probe" in page:
            require_non_empty_string(f"{label}.success_probe", page["success_probe"], errors)
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(
            "run2_73_visual_grammar_modules.page_type_to_visual_grammar page roles must be "
            f"{', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}"
        )


def validate_run2_73_visual_grammar_module_records(value: Any, errors: list[str]) -> None:
    if not require_non_empty_list("run2_73_visual_grammar_modules.visual_grammar_modules", value, errors):
        return
    module_ids: set[str] = set()
    for index, module in enumerate(value):
        label = f"run2_73_visual_grammar_modules.visual_grammar_modules[{index}]"
        if not isinstance(module, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(
            label,
            module,
            ["module_id", "display_name", "use_when", "primary_structure", "how_to_draw", "content_service", "native_ppt_primitives", "avoid"],
            errors,
        )
        module_id = module.get("module_id")
        if "module_id" in module and validate_choice(f"{label}.module_id", module_id, RUN2_73_VISUAL_GRAMMAR_MODULE_IDS, errors):
            if module_id in module_ids:
                errors.append(f"{label}.module_id duplicates {module_id}")
            module_ids.add(module_id)
        for key in ["display_name", "primary_structure", "content_service"]:
            if key in module:
                require_non_empty_string(f"{label}.{key}", module[key], errors)
        for key in ["use_when", "native_ppt_primitives", "avoid"]:
            if key in module:
                validate_string_list(f"{label}.{key}", module[key], errors)
        if "how_to_draw" in module:
            if validate_string_list(f"{label}.how_to_draw", module["how_to_draw"], errors) and len(module["how_to_draw"]) < 3:
                errors.append(f"{label}.how_to_draw must contain at least 3 steps")
    if module_ids != RUN2_73_VISUAL_GRAMMAR_MODULE_IDS:
        missing = RUN2_73_VISUAL_GRAMMAR_MODULE_IDS - module_ids
        extra = module_ids - RUN2_73_VISUAL_GRAMMAR_MODULE_IDS
        for module_id in sorted(missing):
            errors.append(f"run2_73_visual_grammar_modules.visual_grammar_modules missing module: {module_id}")
        for module_id in sorted(extra):
            errors.append(f"run2_73_visual_grammar_modules.visual_grammar_modules has unexpected module: {module_id}")


def validate_run2_73_visual_grammar_blueprints(value: Any, errors: list[str]) -> None:
    if not require_non_empty_list("run2_73_visual_grammar_modules.module_geometry_blueprints", value, errors):
        return
    module_ids: set[str] = set()
    for index, blueprint in enumerate(value):
        label = f"run2_73_visual_grammar_modules.module_geometry_blueprints[{index}]"
        if not isinstance(blueprint, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(
            label,
            blueprint,
            [
                "module_id",
                "coordinate_system",
                "primary_structure_is_not",
                "primary_structure_is",
                "native_ppt_shape_plan",
                "content_attachment_points",
            ],
            errors,
        )
        module_id = blueprint.get("module_id")
        if "module_id" in blueprint and validate_choice(f"{label}.module_id", module_id, RUN2_73_VISUAL_GRAMMAR_MODULE_IDS, errors):
            if module_id in module_ids:
                errors.append(f"{label}.module_id duplicates {module_id}")
            module_ids.add(module_id)
        if blueprint.get("coordinate_system") != "normalized_16_9_canvas_0_100":
            errors.append(f"{label}.coordinate_system must be normalized_16_9_canvas_0_100")
        for key in ["primary_structure_is_not", "primary_structure_is"]:
            if key in blueprint:
                require_non_empty_string(f"{label}.{key}", blueprint[key], errors)
        if "content_attachment_points" in blueprint:
            validate_string_list(f"{label}.content_attachment_points", blueprint["content_attachment_points"], errors)
        shape_plan = blueprint.get("native_ppt_shape_plan", [])
        if not require_non_empty_list(f"{label}.native_ppt_shape_plan", shape_plan, errors):
            continue
        if len(shape_plan) < 3:
            errors.append(f"{label}.native_ppt_shape_plan must contain at least 3 shapes")
        has_why_not_card = False
        for shape_index, shape in enumerate(shape_plan):
            shape_label = f"{label}.native_ppt_shape_plan[{shape_index}]"
            if not isinstance(shape, dict):
                errors.append(f"{shape_label} must be an object")
                continue
            require_keys(shape_label, shape, ["shape_id", "primitive", "semantic_role"], errors)
            for key in ["shape_id", "primitive", "semantic_role"]:
                if key in shape:
                    require_non_empty_string(f"{shape_label}.{key}", shape[key], errors)
            if "why_not_card" in shape:
                has_why_not_card = require_non_empty_string(f"{shape_label}.why_not_card", shape["why_not_card"], errors) or has_why_not_card
        if not has_why_not_card:
            errors.append(f"{label}.native_ppt_shape_plan must include at least one why_not_card explanation")
    if module_ids != RUN2_73_VISUAL_GRAMMAR_MODULE_IDS:
        for module_id in sorted(RUN2_73_VISUAL_GRAMMAR_MODULE_IDS - module_ids):
            errors.append(f"run2_73_visual_grammar_modules.module_geometry_blueprints missing module: {module_id}")


def validate_run2_73_visual_grammar_selection_rules(value: Any, errors: list[str]) -> None:
    if not require_non_empty_list("run2_73_visual_grammar_modules.module_selection_rules", value, errors):
        return
    selected_modules: set[str] = set()
    selected_module_by_role: dict[str, str] = {}
    for index, rule in enumerate(value):
        label = f"run2_73_visual_grammar_modules.module_selection_rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, rule, ["rule_id", "condition", "select_module", "applies_to_page_types"], errors)
        for key in ["rule_id", "condition"]:
            if key in rule:
                require_non_empty_string(f"{label}.{key}", rule[key], errors)
        if "select_module" in rule:
            module_id = rule["select_module"]
            if validate_choice(f"{label}.select_module", module_id, RUN2_73_VISUAL_GRAMMAR_MODULE_IDS, errors):
                selected_modules.add(module_id)
        if "applies_to_page_types" in rule:
            validate_known_string_references(
                f"{label}.applies_to_page_types",
                rule["applies_to_page_types"],
                set(RUN2_73_VISUAL_GRAMMAR_ROLES),
                "Part E page role",
                errors,
            )
            if isinstance(rule.get("select_module"), str) and isinstance(rule["applies_to_page_types"], list):
                for role_index, role in enumerate(rule["applies_to_page_types"]):
                    if not isinstance(role, str) or role not in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
                        continue
                    expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
                    if rule["select_module"] != expected_module:
                        errors.append(
                            f"{label}.applies_to_page_types[{role_index}] "
                            f"must select {expected_module} for {role}"
                        )
                    if role in selected_module_by_role:
                        errors.append(f"{label}.applies_to_page_types[{role_index}] duplicates page role: {role}")
                    selected_module_by_role[role] = rule["select_module"]
    if len(value) != 5:
        errors.append("run2_73_visual_grammar_modules.module_selection_rules must contain 5 rules")
    if selected_modules != RUN2_73_VISUAL_GRAMMAR_MODULE_IDS:
        for module_id in sorted(RUN2_73_VISUAL_GRAMMAR_MODULE_IDS - selected_modules):
            errors.append(f"run2_73_visual_grammar_modules.module_selection_rules missing module: {module_id}")
    if selected_module_by_role != RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
        for role in RUN2_73_VISUAL_GRAMMAR_ROLES:
            if role not in selected_module_by_role:
                errors.append(f"run2_73_visual_grammar_modules.module_selection_rules missing page role: {role}")


def validate_run2_73_visual_grammar_coverage(
    value: Any,
    source_reference_ids: set[str],
    source_semantic_asset_ids: set[str],
    source_object_grammar_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_dict("run2_73_visual_grammar_modules.coverage_matrix", value, errors):
        return
    if "page_roles_covered" in value:
        validate_exact_string_set(
            "run2_73_visual_grammar_modules.coverage_matrix.page_roles_covered",
            value["page_roles_covered"],
            set(RUN2_73_VISUAL_GRAMMAR_ROLES),
            errors,
        )
    if "modules_covered" in value:
        validate_exact_string_set(
            "run2_73_visual_grammar_modules.coverage_matrix.modules_covered",
            value["modules_covered"],
            RUN2_73_VISUAL_GRAMMAR_MODULE_IDS,
            errors,
        )
    if "source_reference_archetype_ids_covered" in value:
        validate_known_string_references(
            "run2_73_visual_grammar_modules.coverage_matrix.source_reference_archetype_ids_covered",
            value["source_reference_archetype_ids_covered"],
            source_reference_ids,
            "source archetype",
            errors,
        )
    if "source_visual_object_grammar_ids_covered" in value:
        validate_known_string_references(
            "run2_73_visual_grammar_modules.coverage_matrix.source_visual_object_grammar_ids_covered",
            value["source_visual_object_grammar_ids_covered"],
            source_object_grammar_ids,
            "visual object grammar",
            errors,
        )
    if "source_semantic_asset_ids_covered" in value:
        validate_known_string_references(
            "run2_73_visual_grammar_modules.coverage_matrix.source_semantic_asset_ids_covered",
            value["source_semantic_asset_ids_covered"],
            source_semantic_asset_ids,
            "semantic visual asset",
            errors,
        )


def validate_run2_73_visual_grammar_success(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_visual_grammar_modules.success_criteria_check", value, errors):
        return
    for flag in sorted(RUN2_73_VISUAL_GRAMMAR_SUCCESS_FLAGS):
        if value.get(flag) is not True:
            errors.append(f"run2_73_visual_grammar_modules.success_criteria_check.{flag} must be true")


def validate_run2_73_visual_grammar_trace_summary(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_visual_grammar_modules.traceability_summary", value, errors):
        return
    expected_counts = {
        "page_type_count": 6,
        "visual_grammar_module_count": 5,
        "semantic_asset_count_bound": 18,
        "reference_archetype_count_bound": 6,
        "visual_object_grammar_count_bound": 6,
    }
    for key, expected in expected_counts.items():
        if key in value and value[key] != expected:
            errors.append(f"run2_73_visual_grammar_modules.traceability_summary.{key} must be {expected}")
    if "primary_structure_policy" in value:
        validate_string_mentions(
            "run2_73_visual_grammar_modules.traceability_summary.primary_structure_policy",
            value["primary_structure_policy"],
            ["non_rectangular", "proof_object"],
            errors,
        )


def collect_run2_73_role_records(
    pack_dir: Path,
    file_name: str,
    record_key: str,
    role_key: str,
    id_key: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    data = load_json(pack_dir / file_name, errors)
    records = data.get(record_key, [])
    if not require_non_empty_list(f"{file_name}.{record_key}", records, errors):
        return {}
    by_role: dict[str, dict[str, Any]] = {}
    roles: list[str] = []
    for index, record in enumerate(records):
        label = f"{file_name}.{record_key}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        role = record.get(role_key)
        if validate_choice(f"{label}.{role_key}", role, set(RUN2_73_VISUAL_GRAMMAR_ROLES), errors):
            roles.append(role)
            if role in by_role:
                errors.append(f"{label}.{role_key} duplicates page role: {role}")
            by_role[role] = record
        if id_key in record:
            require_non_empty_string(f"{label}.{id_key}", record[id_key], errors)
    if roles and roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{file_name}.{record_key} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    return by_role


def validate_run2_73_renderer_adapter_contracts(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "run2_73_renderer_adapter_contracts.json", errors)
    require_keys(
        "run2_73_renderer_adapter_contracts.json",
        data,
        [
            "artifact_id",
            "part",
            "schema_version",
            "status",
            "stage_policy",
            "source_scene_plan_expansion",
            "source_renderer_input_validation",
            "source_visual_grammar_modules",
            "source_inputs",
            "artifact_scope",
            "execution_guard",
            "adapter_scene_records",
            "traceability_summary",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != "run2_73_renderer_adapter_contracts":
        errors.append("run2_73_renderer_adapter_contracts.artifact_id must be run2_73_renderer_adapter_contracts")
    if data.get("part") != "Part E2":
        errors.append("run2_73_renderer_adapter_contracts.part must be Part E2")
    if "schema_version" in data:
        require_non_empty_string("run2_73_renderer_adapter_contracts.schema_version", data["schema_version"], errors)
    if data.get("status") != RUN2_73_RENDERER_ADAPTER_STATUS:
        errors.append(f"run2_73_renderer_adapter_contracts.status must be {RUN2_73_RENDERER_ADAPTER_STATUS}")
    if data.get("stage_policy") != RUN2_73_RENDERER_ADAPTER_STAGE_POLICY:
        errors.append(
            "run2_73_renderer_adapter_contracts.stage_policy must be "
            f"{RUN2_73_RENDERER_ADAPTER_STAGE_POLICY}"
        )
    for key, expected in RUN2_73_RENDERER_ADAPTER_SOURCE_POINTERS.items():
        if data.get(key) != expected:
            errors.append(f"run2_73_renderer_adapter_contracts.{key} must be {expected}")

    validate_run2_73_renderer_adapter_source_inputs(data.get("source_inputs", []), errors)
    validate_run2_73_renderer_adapter_scope(data.get("artifact_scope", {}), errors)
    validate_run2_73_renderer_adapter_execution_guard(data.get("execution_guard", {}), errors)

    scene_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_scene_plan_expansion.json",
        "scene_structures",
        "role",
        "expansion_id",
        errors,
    )
    validation_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_renderer_input_validation.json",
        "scene_validation_results",
        "role",
        "validation_id",
        errors,
    )
    grammar_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_visual_grammar_modules.json",
        "page_type_to_visual_grammar",
        "page_type",
        "page_type",
        errors,
    )
    grammar = load_json(pack_dir / "run2_73_visual_grammar_modules.json", errors)
    blueprint_module_ids = {
        blueprint.get("module_id")
        for blueprint in grammar.get("module_geometry_blueprints", [])
        if isinstance(blueprint, dict) and isinstance(blueprint.get("module_id"), str)
    }

    validate_run2_73_renderer_adapter_scene_records(
        data.get("adapter_scene_records", []),
        scene_by_role,
        validation_by_role,
        grammar_by_role,
        blueprint_module_ids,
        errors,
    )
    validate_run2_73_renderer_adapter_trace_summary(data.get("traceability_summary", {}), errors)
    if data.get("next_required_action") != RUN2_73_RENDERER_ADAPTER_NEXT_REQUIRED_ACTION:
        errors.append(
            "run2_73_renderer_adapter_contracts.next_required_action must be "
            f"{RUN2_73_RENDERER_ADAPTER_NEXT_REQUIRED_ACTION}"
        )


def validate_run2_73_renderer_adapter_source_inputs(value: Any, errors: list[str]) -> None:
    if not require_non_empty_list("run2_73_renderer_adapter_contracts.source_inputs", value, errors):
        return
    source_paths: set[str] = set()
    for index, source in enumerate(value):
        label = f"run2_73_renderer_adapter_contracts.source_inputs[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, source, ["path", "available", "use_in_this_artifact"], errors)
        if "path" in source and require_non_empty_string(f"{label}.path", source["path"], errors):
            source_paths.add(source["path"])
        if "available" in source and type(source["available"]) is not bool:
            errors.append(f"{label}.available must be a boolean")
        if "use_in_this_artifact" in source:
            require_non_empty_string(f"{label}.use_in_this_artifact", source["use_in_this_artifact"], errors)
    for source_path in sorted(RUN2_73_RENDERER_ADAPTER_SOURCE_PATHS - source_paths):
        errors.append(f"run2_73_renderer_adapter_contracts.source_inputs missing path: {source_path}")


def validate_run2_73_renderer_adapter_scope(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_renderer_adapter_contracts.artifact_scope", value, errors):
        return
    if "starts" in value:
        validate_string_list("run2_73_renderer_adapter_contracts.artifact_scope.starts", value["starts"], errors)
    does_not_start = value.get("does_not_start", [])
    if validate_string_list("run2_73_renderer_adapter_contracts.artifact_scope.does_not_start", does_not_start, errors):
        actual_scope = set(does_not_start)
        for item in sorted(RUN2_73_VISUAL_GRAMMAR_FORBIDDEN_SCOPE - actual_scope):
            errors.append(
                "run2_73_renderer_adapter_contracts.artifact_scope.does_not_start "
                f"must include {item}"
            )


def validate_run2_73_renderer_adapter_execution_guard(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_renderer_adapter_contracts.execution_guard", value, errors):
        return
    if value.get("mode") != "adapter_contract_only":
        errors.append("run2_73_renderer_adapter_contracts.execution_guard.mode must be adapter_contract_only")
    if value.get("rendering_subprocesses_allowed") is not False:
        errors.append(
            "run2_73_renderer_adapter_contracts.execution_guard.rendering_subprocesses_allowed must be false"
        )
    if "allowed_side_effects" in value:
        validate_string_list(
            "run2_73_renderer_adapter_contracts.execution_guard.allowed_side_effects",
            value["allowed_side_effects"],
            errors,
        )
    if "forbidden_invocations" in value:
        validate_exact_string_set(
            "run2_73_renderer_adapter_contracts.execution_guard.forbidden_invocations",
            value["forbidden_invocations"],
            RUN2_73_VISUAL_GRAMMAR_FORBIDDEN_SCOPE,
            errors,
        )
    else:
        errors.append("run2_73_renderer_adapter_contracts.execution_guard missing key: forbidden_invocations")
    for key in ["forbidden_runtime_imports", "forbidden_dynamic_import_calls"]:
        if key in value:
            validate_string_list(f"run2_73_renderer_adapter_contracts.execution_guard.{key}", value[key], errors)


def validate_run2_73_renderer_adapter_scene_records(
    value: Any,
    scene_by_role: dict[str, dict[str, Any]],
    validation_by_role: dict[str, dict[str, Any]],
    grammar_by_role: dict[str, dict[str, Any]],
    blueprint_module_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_list("run2_73_renderer_adapter_contracts.adapter_scene_records", value, errors):
        return
    roles: list[str] = []
    for index, record in enumerate(value):
        label = f"run2_73_renderer_adapter_contracts.adapter_scene_records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(
            label,
            record,
            [
                "adapter_scene_id",
                "role",
                "slide_index",
                "source_expansion_id",
                "source_validation_id",
                "source_visual_grammar_page_type",
                "validation_status",
                "adapter_blocking_issues",
                "visual_grammar_binding",
                "geometry_blueprint_binding",
                "adapter_renderer_instructions",
            ],
            errors,
        )
        role = record.get("role")
        role_is_known = validate_choice(f"{label}.role", role, set(RUN2_73_VISUAL_GRAMMAR_ROLES), errors)
        if role_is_known:
            roles.append(role)
            if record.get("adapter_scene_id") != f"renderer_adapter_2_73_{role}":
                errors.append(f"{label}.adapter_scene_id must be renderer_adapter_2_73_{role}")
            expected_slide_index = RUN2_73_VISUAL_GRAMMAR_ROLES.index(role) + 1
            if record.get("slide_index") != expected_slide_index:
                errors.append(f"{label}.slide_index must be {expected_slide_index}")
            validate_run2_73_renderer_adapter_source_bindings(
                label,
                record,
                role,
                scene_by_role,
                validation_by_role,
                grammar_by_role,
                blueprint_module_ids,
                errors,
            )
        elif "slide_index" in record:
            require_integer(f"{label}.slide_index", record["slide_index"], errors)
        if record.get("validation_status") != "pass":
            errors.append(f"{label}.validation_status must be pass")
        blocking_issues = record.get("adapter_blocking_issues")
        if not isinstance(blocking_issues, list):
            errors.append(f"{label}.adapter_blocking_issues must be a list")
        elif blocking_issues:
            errors.append(f"{label}.adapter_blocking_issues must be empty")
        validate_run2_73_renderer_adapter_instructions(
            f"{label}.adapter_renderer_instructions",
            record.get("adapter_renderer_instructions", {}),
            errors,
        )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(
            "run2_73_renderer_adapter_contracts.adapter_scene_records roles must be "
            f"{', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}"
        )


def validate_run2_73_renderer_adapter_source_bindings(
    label: str,
    record: dict[str, Any],
    role: str,
    scene_by_role: dict[str, dict[str, Any]],
    validation_by_role: dict[str, dict[str, Any]],
    grammar_by_role: dict[str, dict[str, Any]],
    blueprint_module_ids: set[str],
    errors: list[str],
) -> None:
    scene_record = scene_by_role.get(role, {})
    validation_record = validation_by_role.get(role, {})
    grammar_record = grammar_by_role.get(role, {})
    if scene_record and record.get("source_expansion_id") != scene_record.get("expansion_id"):
        errors.append(f"{label}.source_expansion_id must match D2 scene expansion id for {role}")
    if validation_record and record.get("source_validation_id") != validation_record.get("validation_id"):
        errors.append(f"{label}.source_validation_id must match D3 validation id for {role}")
    if record.get("source_visual_grammar_page_type") != role:
        errors.append(f"{label}.source_visual_grammar_page_type must be {role}")

    visual_binding = record.get("visual_grammar_binding", {})
    if require_non_empty_dict(f"{label}.visual_grammar_binding", visual_binding, errors):
        require_keys(f"{label}.visual_grammar_binding", visual_binding, ["module_id", "main_structure"], errors)
        module_id = visual_binding.get("module_id")
        if "module_id" in visual_binding:
            validate_choice(f"{label}.visual_grammar_binding.module_id", module_id, RUN2_73_VISUAL_GRAMMAR_MODULE_IDS, errors)
        expected_module = grammar_record.get("primary_visual_grammar_module")
        if isinstance(expected_module, str) and module_id != expected_module:
            errors.append(f"{label}.visual_grammar_binding.module_id must match Part E module for {role}")
        if "main_structure" in visual_binding:
            require_non_empty_dict(f"{label}.visual_grammar_binding.main_structure", visual_binding["main_structure"], errors)
        if "module_variant" in visual_binding and isinstance(grammar_record.get("module_variant"), str):
            if visual_binding["module_variant"] != grammar_record["module_variant"]:
                errors.append(f"{label}.visual_grammar_binding.module_variant must match Part E module variant for {role}")
        if "draw_order" in visual_binding:
            validate_string_list(f"{label}.visual_grammar_binding.draw_order", visual_binding["draw_order"], errors)

    geometry_binding = record.get("geometry_blueprint_binding", {})
    if require_non_empty_dict(f"{label}.geometry_blueprint_binding", geometry_binding, errors):
        require_keys(f"{label}.geometry_blueprint_binding", geometry_binding, ["module_id", "coordinate_system"], errors)
        geometry_module_id = geometry_binding.get("module_id")
        if "module_id" in geometry_binding:
            validate_choice(
                f"{label}.geometry_blueprint_binding.module_id",
                geometry_module_id,
                RUN2_73_VISUAL_GRAMMAR_MODULE_IDS,
                errors,
            )
            if geometry_module_id not in blueprint_module_ids:
                errors.append(f"{label}.geometry_blueprint_binding.module_id references missing Part E blueprint")
        if geometry_binding.get("coordinate_system") != "normalized_16_9_canvas_0_100":
            errors.append(f"{label}.geometry_blueprint_binding.coordinate_system must be normalized_16_9_canvas_0_100")
        if "native_ppt_shape_plan" in geometry_binding:
            validate_run2_73_adapter_shape_plan(
                f"{label}.geometry_blueprint_binding.native_ppt_shape_plan",
                geometry_binding["native_ppt_shape_plan"],
                errors,
            )


def validate_run2_73_adapter_shape_plan(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    for index, shape in enumerate(value):
        shape_label = f"{label}[{index}]"
        if not isinstance(shape, dict):
            errors.append(f"{shape_label} must be an object")
            continue
        require_keys(shape_label, shape, ["shape_id", "primitive", "semantic_role"], errors)


def validate_run2_73_renderer_adapter_instructions(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    required_false = [
        "renderer_execution_allowed_in_this_artifact",
        "public_release_allowed_in_this_artifact",
    ]
    for key in required_false:
        if value.get(key) is not False:
            errors.append(f"{label}.{key} must be false")
    for key in [
        "draw_primary_structure_before_components",
        "apply_geometry_blueprint_before_component_layout",
        "bind_semantic_components_before_geometry",
        "preserve_off_canvas_contract",
    ]:
        if key in value and value[key] is not True:
            errors.append(f"{label}.{key} must be true")


def validate_run2_73_renderer_adapter_trace_summary(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_renderer_adapter_contracts.traceability_summary", value, errors):
        return
    expected_counts = {
        "scene_count": 6,
        "validated_scene_count": 6,
        "visual_grammar_module_count": 5,
        "geometry_blueprint_count": 5,
        "adapter_blocking_issue_count": 0,
    }
    for key, expected in expected_counts.items():
        if value.get(key) != expected:
            errors.append(f"run2_73_renderer_adapter_contracts.traceability_summary.{key} must be {expected}")
    if "sources_consumed" in value:
        validate_exact_string_set(
            "run2_73_renderer_adapter_contracts.traceability_summary.sources_consumed",
            value["sources_consumed"],
            RUN2_73_RENDERER_ADAPTER_SOURCE_FILES,
            errors,
        )
    else:
        errors.append("run2_73_renderer_adapter_contracts.traceability_summary missing key: sources_consumed")


def validate_run2_73_text_binding_strategy(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "run2_73_text_binding_strategy.json", errors)
    require_keys(
        "run2_73_text_binding_strategy.json",
        data,
        [
            "artifact_id",
            "part",
            "schema_version",
            "status",
            "stage_policy",
            "source_scene_plan_expansion",
            "source_renderer_adapter_contracts",
            "source_visual_grammar_modules",
            "source_slide_story",
            "source_content_quality_audit",
            "source_inputs",
            "artifact_scope",
            "execution_guard",
            "global_text_binding_contract",
            "global_forbidden_text_patterns",
            "page_text_binding_records",
            "traceability_summary",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != "run2_73_text_binding_strategy":
        errors.append("run2_73_text_binding_strategy.artifact_id must be run2_73_text_binding_strategy")
    if data.get("part") != "Part F":
        errors.append("run2_73_text_binding_strategy.part must be Part F")
    if "schema_version" in data:
        require_non_empty_string("run2_73_text_binding_strategy.schema_version", data["schema_version"], errors)
    if data.get("status") != RUN2_73_TEXT_BINDING_STATUS:
        errors.append(f"run2_73_text_binding_strategy.status must be {RUN2_73_TEXT_BINDING_STATUS}")
    if data.get("stage_policy") != RUN2_73_TEXT_BINDING_STAGE_POLICY:
        errors.append(
            "run2_73_text_binding_strategy.stage_policy must be "
            f"{RUN2_73_TEXT_BINDING_STAGE_POLICY}"
        )
    for key, expected in RUN2_73_TEXT_BINDING_SOURCE_POINTERS.items():
        if data.get(key) != expected:
            errors.append(f"run2_73_text_binding_strategy.{key} must be {expected}")

    validate_run2_73_text_binding_source_inputs(data.get("source_inputs", []), errors)
    validate_run2_73_text_binding_scope(data.get("artifact_scope", {}), errors)
    validate_run2_73_text_binding_execution_guard(data.get("execution_guard", {}), errors)
    validate_run2_73_text_binding_global_contract(data.get("global_text_binding_contract", {}), errors)
    validate_exact_string_set(
        "run2_73_text_binding_strategy.global_forbidden_text_patterns",
        data.get("global_forbidden_text_patterns", []),
        RUN2_73_TEXT_BINDING_FORBIDDEN_PATTERNS,
        errors,
    )

    scene_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_scene_plan_expansion.json",
        "scene_structures",
        "role",
        "expansion_id",
        errors,
    )
    adapter_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_renderer_adapter_contracts.json",
        "adapter_scene_records",
        "role",
        "adapter_scene_id",
        errors,
    )
    grammar_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_visual_grammar_modules.json",
        "page_type_to_visual_grammar",
        "page_type",
        "page_type",
        errors,
    )
    story_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_74_slide_story.json",
        "slides",
        "role",
        "slide_id",
        errors,
    )
    audit_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_74_content_quality_audit.json",
        "slide_quality_audits",
        "role",
        "audit_id",
        errors,
    )
    known_binding_ids_by_role = collect_run2_73_text_binding_source_ids(scene_by_role, adapter_by_role)

    validate_run2_73_text_binding_records(
        data.get("page_text_binding_records", []),
        scene_by_role,
        adapter_by_role,
        grammar_by_role,
        story_by_role,
        audit_by_role,
        known_binding_ids_by_role,
        errors,
    )
    validate_run2_73_text_binding_trace_summary(data.get("traceability_summary", {}), errors)
    if data.get("next_required_action") != RUN2_73_TEXT_BINDING_NEXT_REQUIRED_ACTION:
        errors.append(
            "run2_73_text_binding_strategy.next_required_action must be "
            f"{RUN2_73_TEXT_BINDING_NEXT_REQUIRED_ACTION}"
        )


def validate_run2_73_text_binding_source_inputs(value: Any, errors: list[str]) -> None:
    if not require_non_empty_list("run2_73_text_binding_strategy.source_inputs", value, errors):
        return
    source_paths: set[str] = set()
    for index, source in enumerate(value):
        label = f"run2_73_text_binding_strategy.source_inputs[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(label, source, ["path", "available", "use_in_this_artifact"], errors)
        if "path" in source and require_non_empty_string(f"{label}.path", source["path"], errors):
            source_paths.add(source["path"])
        if "available" in source and type(source["available"]) is not bool:
            errors.append(f"{label}.available must be a boolean")
        if "use_in_this_artifact" in source:
            require_non_empty_string(f"{label}.use_in_this_artifact", source["use_in_this_artifact"], errors)
    for source_path in sorted(RUN2_73_TEXT_BINDING_SOURCE_PATHS - source_paths):
        errors.append(f"run2_73_text_binding_strategy.source_inputs missing path: {source_path}")


def validate_run2_73_text_binding_scope(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_text_binding_strategy.artifact_scope", value, errors):
        return
    if "starts" in value:
        validate_string_list("run2_73_text_binding_strategy.artifact_scope.starts", value["starts"], errors)
    does_not_start = value.get("does_not_start", [])
    if validate_string_list("run2_73_text_binding_strategy.artifact_scope.does_not_start", does_not_start, errors):
        actual_scope = set(does_not_start)
        for item in sorted(RUN2_73_VISUAL_GRAMMAR_FORBIDDEN_SCOPE - actual_scope):
            errors.append(
                "run2_73_text_binding_strategy.artifact_scope.does_not_start "
                f"must include {item}"
            )


def validate_run2_73_text_binding_execution_guard(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_text_binding_strategy.execution_guard", value, errors):
        return
    if value.get("mode") != "text_binding_strategy_only":
        errors.append("run2_73_text_binding_strategy.execution_guard.mode must be text_binding_strategy_only")
    if value.get("rendering_subprocesses_allowed") is not False:
        errors.append("run2_73_text_binding_strategy.execution_guard.rendering_subprocesses_allowed must be false")
    if "allowed_side_effects" in value:
        validate_string_list(
            "run2_73_text_binding_strategy.execution_guard.allowed_side_effects",
            value["allowed_side_effects"],
            errors,
        )
    if "forbidden_invocations" in value:
        validate_exact_string_set(
            "run2_73_text_binding_strategy.execution_guard.forbidden_invocations",
            value["forbidden_invocations"],
            RUN2_73_VISUAL_GRAMMAR_FORBIDDEN_SCOPE,
            errors,
        )
    else:
        errors.append("run2_73_text_binding_strategy.execution_guard missing key: forbidden_invocations")
    for key in ["forbidden_runtime_imports", "forbidden_dynamic_import_calls"]:
        if key in value:
            validate_string_list(f"run2_73_text_binding_strategy.execution_guard.{key}", value[key], errors)


def validate_run2_73_text_binding_global_contract(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_text_binding_strategy.global_text_binding_contract", value, errors):
        return
    for key in [
        "must_bind_text_to_visual_object",
        "must_define_socket_capacity_before_render",
        "must_route_overflow_off_canvas",
        "must_preserve_distinct_layout_signature_per_role",
    ]:
        if value.get(key) is not True:
            errors.append(f"run2_73_text_binding_strategy.global_text_binding_contract.{key} must be true")


def collect_run2_73_text_binding_source_ids(
    scene_by_role: dict[str, dict[str, Any]],
    adapter_by_role: dict[str, dict[str, Any]],
) -> dict[str, set[str]]:
    ids_by_role: dict[str, set[str]] = {}
    for role in RUN2_73_VISUAL_GRAMMAR_ROLES:
        ids: set[str] = set()
        scene = scene_by_role.get(role, {})
        adapter = adapter_by_role.get(role, {})
        for key in ["expansion_id"]:
            value = scene.get(key)
            if isinstance(value, str):
                ids.add(value)
        for component in scene.get("semantic_components", {}).values():
            if isinstance(component, dict) and isinstance(component.get("component_id"), str):
                ids.add(component["component_id"])
        for container in scene.get("visual_containers", []):
            if isinstance(container, dict) and isinstance(container.get("container_id"), str):
                ids.add(container["container_id"])
        for binding in scene.get("expanded_renderer_action_bindings", []):
            if isinstance(binding, dict) and isinstance(binding.get("binding_id"), str):
                ids.add(binding["binding_id"])
        if isinstance(adapter.get("adapter_scene_id"), str):
            ids.add(adapter["adapter_scene_id"])
        manifest = adapter.get("renderer_adapter_manifest", {})
        if isinstance(manifest, dict):
            for key in ["semantic_component_ids", "visual_container_ids", "expanded_renderer_binding_ids"]:
                values = manifest.get(key, [])
                if isinstance(values, list):
                    ids.update(value for value in values if isinstance(value, str))
        ids_by_role[role] = ids
    return ids_by_role


def validate_run2_73_text_binding_records(
    value: Any,
    scene_by_role: dict[str, dict[str, Any]],
    adapter_by_role: dict[str, dict[str, Any]],
    grammar_by_role: dict[str, dict[str, Any]],
    story_by_role: dict[str, dict[str, Any]],
    audit_by_role: dict[str, dict[str, Any]],
    known_binding_ids_by_role: dict[str, set[str]],
    errors: list[str],
) -> None:
    if not require_non_empty_list("run2_73_text_binding_strategy.page_text_binding_records", value, errors):
        return
    roles: list[str] = []
    layout_signatures: set[str] = set()
    for index, record in enumerate(value):
        label = f"run2_73_text_binding_strategy.page_text_binding_records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_keys(
            label,
            record,
            [
                "text_binding_id",
                "role",
                "slide_index",
                "layout_signature",
                "source_expansion_id",
                "source_adapter_scene_id",
                "source_visual_grammar_module",
                "source_slide_story_id",
                "source_content_audit_id",
                "text_socket_strategy",
                "overflow_policy",
                "text_routing",
                "forbidden_text_patterns",
            ],
            errors,
        )
        role = record.get("role")
        role_is_known = validate_choice(f"{label}.role", role, set(RUN2_73_VISUAL_GRAMMAR_ROLES), errors)
        if role_is_known:
            roles.append(role)
            expected_slide_index = RUN2_73_VISUAL_GRAMMAR_ROLES.index(role) + 1
            if record.get("text_binding_id") != f"text_binding_2_73_{role}":
                errors.append(f"{label}.text_binding_id must be text_binding_2_73_{role}")
            if record.get("slide_index") != expected_slide_index:
                errors.append(f"{label}.slide_index must be {expected_slide_index}")
            layout_signature = record.get("layout_signature")
            if require_non_empty_string(f"{label}.layout_signature", layout_signature, errors):
                if layout_signature in layout_signatures:
                    errors.append(f"{label}.layout_signature duplicates {layout_signature}")
                layout_signatures.add(layout_signature)
            validate_run2_73_text_binding_record_sources(
                label,
                record,
                role,
                scene_by_role,
                adapter_by_role,
                grammar_by_role,
                story_by_role,
                audit_by_role,
                errors,
            )
            validate_run2_73_text_socket_strategy(
                f"{label}.text_socket_strategy",
                record.get("text_socket_strategy", {}),
                known_binding_ids_by_role.get(role, set()),
                errors,
            )
        validate_run2_73_text_binding_overflow_policy(
            f"{label}.overflow_policy",
            record.get("overflow_policy", {}),
            errors,
        )
        validate_run2_73_text_binding_routing(f"{label}.text_routing", record.get("text_routing", {}), errors)
        if "forbidden_text_patterns" in record:
            validate_exact_string_set(
                f"{label}.forbidden_text_patterns",
                record["forbidden_text_patterns"],
                RUN2_73_TEXT_BINDING_FORBIDDEN_PATTERNS,
                errors,
            )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(
            "run2_73_text_binding_strategy.page_text_binding_records roles must be "
            f"{', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}"
        )
    if len(layout_signatures) != 6:
        errors.append("run2_73_text_binding_strategy.page_text_binding_records must contain 6 distinct layout signatures")


def validate_run2_73_text_binding_record_sources(
    label: str,
    record: dict[str, Any],
    role: str,
    scene_by_role: dict[str, dict[str, Any]],
    adapter_by_role: dict[str, dict[str, Any]],
    grammar_by_role: dict[str, dict[str, Any]],
    story_by_role: dict[str, dict[str, Any]],
    audit_by_role: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    scene = scene_by_role.get(role, {})
    adapter = adapter_by_role.get(role, {})
    grammar = grammar_by_role.get(role, {})
    story = story_by_role.get(role, {})
    audit = audit_by_role.get(role, {})
    if scene and record.get("source_expansion_id") != scene.get("expansion_id"):
        errors.append(f"{label}.source_expansion_id must match D2 scene expansion id for {role}")
    if adapter and record.get("source_adapter_scene_id") != adapter.get("adapter_scene_id"):
        errors.append(f"{label}.source_adapter_scene_id must match E2 adapter scene id for {role}")
    expected_module = (
        adapter.get("visual_grammar_binding", {}).get("module_id")
        if isinstance(adapter.get("visual_grammar_binding"), dict)
        else grammar.get("primary_visual_grammar_module")
    )
    if isinstance(expected_module, str) and record.get("source_visual_grammar_module") != expected_module:
        errors.append(f"{label}.source_visual_grammar_module must match Part E/E2 module for {role}")
    if story and record.get("source_slide_story_id") != story.get("slide_id"):
        errors.append(f"{label}.source_slide_story_id must match Run 2.74 slide story id for {role}")
    if audit and record.get("source_content_audit_id") != audit.get("audit_id"):
        errors.append(f"{label}.source_content_audit_id must match Run 2.74 content audit id for {role}")


def validate_run2_73_text_socket_strategy(
    label: str,
    value: Any,
    known_binding_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key in sorted(RUN2_73_TEXT_BINDING_REQUIRED_SOCKETS - set(value)):
        errors.append(f"{label} missing key: {key}")
    if "headline_socket" in value:
        validate_run2_73_text_socket(f"{label}.headline_socket", value["headline_socket"], known_binding_ids, errors)
    if "supporting_copy_socket" in value:
        validate_run2_73_text_socket(
            f"{label}.supporting_copy_socket",
            value["supporting_copy_socket"],
            known_binding_ids,
            errors,
        )
    if "viewer_note_socket" in value:
        validate_run2_73_text_socket(
            f"{label}.viewer_note_socket",
            value["viewer_note_socket"],
            known_binding_ids,
            errors,
        )
    for socket_list_key in ["proof_label_sockets", "callout_sockets"]:
        sockets = value.get(socket_list_key, [])
        if not require_non_empty_list(f"{label}.{socket_list_key}", sockets, errors):
            continue
        if len(sockets) < 2:
            errors.append(f"{label}.{socket_list_key} must contain at least 2 sockets")
        for index, socket in enumerate(sockets):
            validate_run2_73_text_socket(
                f"{label}.{socket_list_key}[{index}]",
                socket,
                known_binding_ids,
                errors,
            )


def validate_run2_73_text_socket(
    label: str,
    value: Any,
    known_binding_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "socket_id",
            "binding_role",
            "bound_visual_object_type",
            "bound_source_artifact",
            "bound_source_id",
            "bound_source_path",
            "capacity",
        ],
        errors,
    )
    for key in ["socket_id", "bound_source_path"]:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)
    if "binding_role" in value:
        validate_choice(f"{label}.binding_role", value["binding_role"], RUN2_73_TEXT_BINDING_ROLES, errors)
    if "bound_visual_object_type" in value:
        validate_choice(
            f"{label}.bound_visual_object_type",
            value["bound_visual_object_type"],
            RUN2_73_TEXT_BINDING_VISUAL_OBJECT_TYPES,
            errors,
        )
    if "bound_source_artifact" in value:
        validate_choice(
            f"{label}.bound_source_artifact",
            value["bound_source_artifact"],
            RUN2_73_TEXT_BINDING_SOURCE_ARTIFACTS,
            errors,
        )
    if "bound_source_id" in value and require_non_empty_string(f"{label}.bound_source_id", value["bound_source_id"], errors):
        if value["bound_source_id"] not in known_binding_ids:
            errors.append(f"{label}.bound_source_id references unknown D2/E2 binding: {value['bound_source_id']}")
    if "capacity" in value:
        validate_run2_73_text_socket_capacity(f"{label}.capacity", value["capacity"], errors)


def validate_run2_73_text_socket_capacity(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        ["max_words", "max_lines", "hierarchy_level", "allowed_font_scale", "overflow_behavior"],
        errors,
    )
    for key in ["max_words", "max_lines"]:
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] <= 0:
            errors.append(f"{label}.{key} must be greater than 0")
    if "hierarchy_level" in value:
        validate_choice(f"{label}.hierarchy_level", value["hierarchy_level"], RUN2_73_TEXT_BINDING_HIERARCHY_LEVELS, errors)
    if "overflow_behavior" in value:
        validate_choice(
            f"{label}.overflow_behavior",
            value["overflow_behavior"],
            RUN2_73_TEXT_BINDING_OVERFLOW_BEHAVIORS,
            errors,
        )
    font_scale = value.get("allowed_font_scale")
    if require_non_empty_dict(f"{label}.allowed_font_scale", font_scale, errors):
        for key in ["min", "max"]:
            if key not in font_scale:
                errors.append(f"{label}.allowed_font_scale missing key: {key}")
                continue
            if not isinstance(font_scale[key], int | float) or isinstance(font_scale[key], bool):
                errors.append(f"{label}.allowed_font_scale.{key} must be a number")
            elif font_scale[key] <= 0:
                errors.append(f"{label}.allowed_font_scale.{key} must be greater than 0")
        if (
            isinstance(font_scale.get("min"), int | float)
            and not isinstance(font_scale.get("min"), bool)
            and isinstance(font_scale.get("max"), int | float)
            and not isinstance(font_scale.get("max"), bool)
            and font_scale["max"] < font_scale["min"]
        ):
            errors.append(f"{label}.allowed_font_scale.max must be greater than or equal to min")


def validate_run2_73_text_binding_overflow_policy(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        ["max_canvas_words", "max_proof_labels_on_canvas", "route_excess_to", "never_create_empty_text_box"],
        errors,
    )
    for key in ["max_canvas_words", "max_proof_labels_on_canvas"]:
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] <= 0:
            errors.append(f"{label}.{key} must be greater than 0")
    if "route_excess_to" in value:
        validate_exact_string_set(f"{label}.route_excess_to", value["route_excess_to"], {"speaker_note", "html_viewer_metadata"}, errors)
    if value.get("never_create_empty_text_box") is not True:
        errors.append(f"{label}.never_create_empty_text_box must be true")


def validate_run2_73_text_binding_routing(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    expected_keys = {"canvas_text", "speaker_note_text", "html_viewer_metadata"}
    actual_keys = set(value)
    for key in sorted(expected_keys - actual_keys):
        errors.append(f"{label} missing key: {key}")
    for key in sorted(actual_keys - expected_keys):
        errors.append(f"{label} has unexpected key: {key}")
    for key in sorted(expected_keys & actual_keys):
        validate_string_list(f"{label}.{key}", value[key], errors)
    if "canvas_text" in value and isinstance(value["canvas_text"], list):
        for required in ["headline_socket", "supporting_copy_socket"]:
            if required not in value["canvas_text"]:
                errors.append(f"{label}.canvas_text missing value: {required}")
    if "speaker_note_text" in value and isinstance(value["speaker_note_text"], list):
        if "viewer_note_socket" not in value["speaker_note_text"]:
            errors.append(f"{label}.speaker_note_text missing value: viewer_note_socket")
    if "html_viewer_metadata" in value and isinstance(value["html_viewer_metadata"], list):
        if "overflow_payload" not in value["html_viewer_metadata"]:
            errors.append(f"{label}.html_viewer_metadata missing value: overflow_payload")


def validate_run2_73_text_binding_trace_summary(value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict("run2_73_text_binding_strategy.traceability_summary", value, errors):
        return
    expected_counts = {
        "page_text_binding_count": 6,
        "layout_signature_count": 6,
    }
    for key, expected in expected_counts.items():
        if value.get(key) != expected:
            errors.append(f"run2_73_text_binding_strategy.traceability_summary.{key} must be {expected}")
    if "socket_count" in value and require_integer(
        "run2_73_text_binding_strategy.traceability_summary.socket_count",
        value["socket_count"],
        errors,
    ):
        if value["socket_count"] < 36:
            errors.append("run2_73_text_binding_strategy.traceability_summary.socket_count must be at least 36")
    if "sources_consumed" in value:
        validate_exact_string_set(
            "run2_73_text_binding_strategy.traceability_summary.sources_consumed",
            value["sources_consumed"],
            RUN2_73_TEXT_BINDING_SOURCE_FILES,
            errors,
        )
    else:
        errors.append("run2_73_text_binding_strategy.traceability_summary missing key: sources_consumed")


def collect_run2_73_validated_renderer_known_binding_ids(
    scene: dict[str, Any],
    adapter: dict[str, Any],
) -> set[str]:
    known: set[str] = set()
    for value in [scene.get("expansion_id"), adapter.get("adapter_scene_id")]:
        if isinstance(value, str) and value:
            known.add(value)
    semantic_components = scene.get("semantic_components", {})
    if isinstance(semantic_components, dict):
        for component in semantic_components.values():
            if isinstance(component, dict):
                for key in ["component_id", "target_component_id"]:
                    value = component.get(key)
                    if isinstance(value, str) and value:
                        known.add(value)
    visual_containers = scene.get("visual_containers", [])
    if isinstance(visual_containers, list):
        for container in visual_containers:
            if isinstance(container, dict):
                for key in ["container_id", "bound_component_id"]:
                    value = container.get(key)
                    if isinstance(value, str) and value:
                        known.add(value)
    expanded_bindings = scene.get("expanded_renderer_action_bindings", [])
    if isinstance(expanded_bindings, list):
        for binding in expanded_bindings:
            if isinstance(binding, dict):
                for key in ["binding_id", "target_component_id"]:
                    value = binding.get(key)
                    if isinstance(value, str) and value:
                        known.add(value)
    manifest = adapter.get("renderer_adapter_manifest", {})
    if isinstance(manifest, dict):
        for key in ["semantic_component_ids", "visual_container_ids", "expanded_renderer_binding_ids"]:
            values = manifest.get(key, [])
            if isinstance(values, list):
                known.update(value for value in values if isinstance(value, str) and value)
    return known


def validate_run2_73_validated_scene_renderer_result(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_73_validated_scene_renderer_rerun_result.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_73_validated_scene_renderer_rerun_result"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "public_ready",
            "public_release_started",
            "quality_claim_boundary",
            "consumed_sources",
            "rerun_manifest",
            "rendered_pages",
            "render_quality_checks",
        ],
        errors,
    )
    if data.get("artifact_id") != "run2_73_validated_scene_renderer_rerun_result":
        errors.append(f"{label}.artifact_id must be run2_73_validated_scene_renderer_rerun_result")
    if data.get("part") != "Part G":
        errors.append(f"{label}.part must be Part G")
    if data.get("run_id") != "2.73":
        errors.append(f"{label}.run_id must be 2.73")
    if data.get("status") != RUN2_73_VALIDATED_RENDERER_STATUS:
        errors.append(f"{label}.status must be {RUN2_73_VALIDATED_RENDERER_STATUS}")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("quality_claim_boundary") != "generated_viewer_check_only_no_part_h_quality_verdict":
        errors.append(f"{label}.quality_claim_boundary must be generated_viewer_check_only_no_part_h_quality_verdict")
    if "consumed_sources" in data:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            data["consumed_sources"],
            RUN2_73_VALIDATED_RENDERER_CONSUMED_SOURCE_PATHS,
            errors,
        )
    manifest = data.get("rerun_manifest", {})
    validate_run2_73_validated_renderer_manifest(f"{label}.rerun_manifest", manifest, errors)

    scene_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_scene_plan_expansion.json",
        "scene_structures",
        "role",
        "expansion_id",
        errors,
    )
    adapter_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_renderer_adapter_contracts.json",
        "adapter_scene_records",
        "role",
        "adapter_scene_id",
        errors,
    )
    text_by_role = collect_run2_73_role_records(
        pack_dir,
        "run2_73_text_binding_strategy.json",
        "page_text_binding_records",
        "role",
        "text_binding_id",
        errors,
    )
    validate_run2_73_validated_renderer_pages(
        f"{label}.rendered_pages",
        data.get("rendered_pages", []),
        scene_by_role,
        adapter_by_role,
        text_by_role,
        errors,
    )
    validate_run2_73_validated_renderer_checks(
        f"{label}.render_quality_checks",
        data.get("render_quality_checks", {}),
        errors,
    )


def validate_run2_73_validated_renderer_manifest(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["generator", "consumed_sources", "best_internal_arm", "outputs", "viewer_update"], errors)
    if value.get("generator") != "scripts/generate_ppt_run2_73_validated_scene_renderer_arms.mjs":
        errors.append(f"{label}.generator must be scripts/generate_ppt_run2_73_validated_scene_renderer_arms.mjs")
    if "consumed_sources" in value:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            value["consumed_sources"],
            RUN2_73_VALIDATED_RENDERER_CONSUMED_SOURCE_PATHS,
            errors,
        )
    if value.get("best_internal_arm") != "run2_73_full_validated_scene_renderer":
        errors.append(f"{label}.best_internal_arm must be run2_73_full_validated_scene_renderer")
    outputs = value.get("outputs", {})
    if require_non_empty_dict(f"{label}.outputs", outputs, errors):
        for key in sorted(RUN2_73_VALIDATED_RENDERER_REQUIRED_OUTPUTS - set(outputs)):
            errors.append(f"{label}.outputs missing key: {key}")
        for key in sorted(RUN2_73_VALIDATED_RENDERER_REQUIRED_OUTPUTS & set(outputs)):
            require_non_empty_string(f"{label}.outputs.{key}", outputs[key], errors)
    viewer_update = value.get("viewer_update", {})
    if require_non_empty_dict(f"{label}.viewer_update", viewer_update, errors):
        if viewer_update.get("latest_run_id") != "2.73":
            errors.append(f"{label}.viewer_update.latest_run_id must be 2.73")
        if viewer_update.get("viewer_can_reference_new_run") is not True:
            errors.append(f"{label}.viewer_update.viewer_can_reference_new_run must be true")


def validate_run2_73_validated_renderer_pages(
    label: str,
    value: Any,
    scene_by_role: dict[str, dict[str, Any]],
    adapter_by_role: dict[str, dict[str, Any]],
    text_by_role: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    layout_signatures: set[str] = set()
    for index, page in enumerate(value):
        page_label = f"{label}[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{page_label} must be an object")
            continue
        require_keys(
            page_label,
            page,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "layout_signature",
                "source_text_binding_id",
                "text_sockets_used",
                "text_socket_bindings",
                "visual_containers",
                "source_trace_terms_visible_on_canvas",
                "forbidden_text_patterns_absent",
            ],
            errors,
        )
        role = page.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in page and require_integer(f"{page_label}.slide_index", page["slide_index"], errors):
            if page["slide_index"] != index + 1:
                errors.append(f"{page_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if page.get("visual_grammar_module") != expected_module:
                errors.append(f"{page_label}.visual_grammar_module must be {expected_module} for {role}")
        if isinstance(page.get("layout_signature"), str) and page["layout_signature"]:
            layout_signatures.add(page["layout_signature"])
        text_record = text_by_role.get(role, {}) if isinstance(role, str) else {}
        if text_record and page.get("source_text_binding_id") != text_record.get("text_binding_id"):
            errors.append(f"{page_label}.source_text_binding_id must match Part F text binding id for {role}")
        if "text_sockets_used" in page:
            validate_exact_string_set(
                f"{page_label}.text_sockets_used",
                page["text_sockets_used"],
                RUN2_73_TEXT_BINDING_REQUIRED_SOCKETS,
                errors,
            )
        scene = scene_by_role.get(role, {}) if isinstance(role, str) else {}
        adapter = adapter_by_role.get(role, {}) if isinstance(role, str) else {}
        known_binding_ids = collect_run2_73_validated_renderer_known_binding_ids(scene, adapter)
        validate_run2_73_validated_renderer_socket_bindings(
            f"{page_label}.text_socket_bindings",
            page.get("text_socket_bindings", []),
            known_binding_ids,
            errors,
        )
        validate_run2_73_validated_renderer_visual_containers(
            f"{page_label}.visual_containers",
            page.get("visual_containers", []),
            errors,
        )
        if "source_trace_terms_visible_on_canvas" in page:
            visible = page["source_trace_terms_visible_on_canvas"]
            if not isinstance(visible, list):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be a list")
            elif any(not isinstance(item, str) for item in visible):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must contain only strings")
            elif visible:
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be empty")
        if "forbidden_text_patterns_absent" in page:
            validate_exact_string_set(
                f"{page_label}.forbidden_text_patterns_absent",
                page["forbidden_text_patterns_absent"],
                RUN2_73_TEXT_BINDING_FORBIDDEN_PATTERNS,
                errors,
            )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if len(layout_signatures) != 6:
        errors.append(f"{label} must contain 6 distinct layout signatures")


def validate_run2_73_validated_renderer_socket_bindings(
    label: str,
    value: Any,
    known_binding_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    socket_keys: set[str] = set()
    for index, binding in enumerate(value):
        binding_label = f"{label}[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{binding_label} must be an object")
            continue
        require_keys(binding_label, binding, ["socket_id", "socket_key", "bound_visual_object_type", "bound_source_id", "capacity"], errors)
        if "socket_id" in binding:
            require_non_empty_string(f"{binding_label}.socket_id", binding["socket_id"], errors)
        if "socket_key" in binding:
            validate_choice(f"{binding_label}.socket_key", binding["socket_key"], RUN2_73_TEXT_BINDING_REQUIRED_SOCKETS, errors)
            if isinstance(binding.get("socket_key"), str):
                socket_keys.add(binding["socket_key"])
        if "bound_visual_object_type" in binding:
            validate_choice(
                f"{binding_label}.bound_visual_object_type",
                binding["bound_visual_object_type"],
                RUN2_73_TEXT_BINDING_VISUAL_OBJECT_TYPES,
                errors,
            )
        if "bound_source_id" in binding and require_non_empty_string(f"{binding_label}.bound_source_id", binding["bound_source_id"], errors):
            if binding["bound_source_id"] not in known_binding_ids:
                errors.append(f"{binding_label}.bound_source_id references unknown D2/E2 binding: {binding['bound_source_id']}")
        if "capacity" in binding:
            validate_run2_73_text_socket_capacity(f"{binding_label}.capacity", binding["capacity"], errors)
    for key in sorted(RUN2_73_TEXT_BINDING_REQUIRED_SOCKETS - socket_keys):
        errors.append(f"{label} missing socket key: {key}")


def validate_run2_73_validated_renderer_visual_containers(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    for index, container in enumerate(value):
        container_label = f"{label}[{index}]"
        if not isinstance(container, dict):
            errors.append(f"{container_label} must be an object")
            continue
        require_keys(container_label, container, ["container_id", "visual_object_type", "bound_text_socket_ids", "empty"], errors)
        if "container_id" in container:
            require_non_empty_string(f"{container_label}.container_id", container["container_id"], errors)
        if "visual_object_type" in container:
            validate_choice(
                f"{container_label}.visual_object_type",
                container["visual_object_type"],
                RUN2_73_TEXT_BINDING_VISUAL_OBJECT_TYPES,
                errors,
            )
        if "bound_text_socket_ids" in container:
            require_non_empty_list(f"{container_label}.bound_text_socket_ids", container["bound_text_socket_ids"], errors)
        if container.get("empty") is not False:
            errors.append(f"{container_label}.empty must be false")


def validate_run2_73_validated_renderer_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key, expected in RUN2_73_VALIDATED_RENDERER_REQUIRED_CHECKS.items():
        if key not in value:
            errors.append(f"{label} missing key: {key}")
            continue
        if require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")


def validate_run2_74_visual_quality_evaluation(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_74_visual_quality_evaluation.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_74_visual_quality_evaluation"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "public_ready",
            "quality_claim_boundary",
            "source_runs",
            "input_chain",
            "viewer_comparison_closure",
            "evaluation_questions",
            "visual_quality_assessment",
            "role_assessments",
            "root_cause_summary",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part H":
        errors.append(f"{label}.part must be Part H")
    if data.get("run_id") != "2.74":
        errors.append(f"{label}.run_id must be 2.74")
    if data.get("status") != RUN2_74_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_74_VISUAL_QUALITY_EVALUATION_STATUS}")
    if data.get("creates_new_ppt_deck") is not False:
        errors.append(f"{label}.creates_new_ppt_deck must be false")
    if data.get("starts_renderer_rerun") is not False:
        errors.append(f"{label}.starts_renderer_rerun must be false")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("quality_claim_boundary") != "part_h_evaluation_only_no_public_release_no_renderer_rerun":
        errors.append(f"{label}.quality_claim_boundary must be part_h_evaluation_only_no_public_release_no_renderer_rerun")

    validate_run2_74_visual_quality_source_runs(f"{label}.source_runs", data.get("source_runs", {}), errors)
    validate_run2_74_visual_quality_input_chain(f"{label}.input_chain", data.get("input_chain", {}), errors)
    validate_run2_74_visual_quality_viewer_closure(
        f"{label}.viewer_comparison_closure",
        data.get("viewer_comparison_closure", {}),
        errors,
    )
    validate_run2_74_visual_quality_questions(
        f"{label}.evaluation_questions",
        data.get("evaluation_questions", {}),
        errors,
    )
    validate_run2_74_visual_quality_assessment(
        f"{label}.visual_quality_assessment",
        data.get("visual_quality_assessment", {}),
        errors,
    )
    validate_run2_74_visual_quality_role_assessments(
        f"{label}.role_assessments",
        data.get("role_assessments", []),
        errors,
    )
    validate_run2_74_visual_quality_root_cause_summary(
        f"{label}.root_cause_summary",
        data.get("root_cause_summary", {}),
        errors,
    )
    if data.get("next_required_action") != "part_i_renderer_repair_from_visual_quality_evaluation":
        errors.append(f"{label}.next_required_action must be part_i_renderer_repair_from_visual_quality_evaluation")


def validate_run2_74_visual_quality_source_runs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["comparison_baseline", "evaluated_run"], errors)
    if value.get("comparison_baseline") != "2.72":
        errors.append(f"{label}.comparison_baseline must be 2.72")
    if value.get("evaluated_run") != "2.73":
        errors.append(f"{label}.evaluated_run must be 2.73")


def validate_run2_74_visual_quality_input_chain(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    required = [
        "run2_72_result",
        "run2_73_result",
        "run2_72_full_trace_manifest",
        "run2_73_full_trace_manifest",
        "ppt_run_viewer",
    ]
    require_keys(label, value, required, errors)
    for key in required:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_74_visual_quality_viewer_closure(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "viewer_latest_run_id",
            "viewer_can_compare_2_72_and_2_73",
            "run2_72_full_preview_count",
            "run2_73_full_preview_count",
            "browser_check_required_for_handoff",
        ],
        errors,
    )
    if value.get("viewer_latest_run_id") != "2.73":
        errors.append(f"{label}.viewer_latest_run_id must be 2.73")
    if value.get("viewer_can_compare_2_72_and_2_73") is not True:
        errors.append(f"{label}.viewer_can_compare_2_72_and_2_73 must be true")
    for key in ["run2_72_full_preview_count", "run2_73_full_preview_count"]:
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] != 6:
            errors.append(f"{label}.{key} must be 6")
    if value.get("browser_check_required_for_handoff") is not True:
        errors.append(f"{label}.browser_check_required_for_handoff must be true")


def validate_run2_74_visual_quality_questions(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for question_id in sorted(RUN2_74_VISUAL_QUALITY_QUESTION_IDS):
        if question_id not in value:
            errors.append(f"{label} missing key: {question_id}")
            continue
        question = value[question_id]
        question_label = f"{label}.{question_id}"
        if not require_non_empty_dict(question_label, question, errors):
            continue
        require_keys(question_label, question, ["answer"], errors)
        if "answer" in question:
            require_non_empty_string(f"{question_label}.answer", question["answer"], errors)
    for question_id in sorted(set(value) - RUN2_74_VISUAL_QUALITY_QUESTION_IDS):
        errors.append(f"{label} unknown key: {question_id}")
    expected_answers = {
        "is_2_73_better_than_2_72": "mixed_not_public_quality_pass",
        "is_text_fused_with_visual_structure": "partial",
        "does_it_still_feel_like_engineering_report": "yes_but_different_failure_mode",
        "do_six_pages_have_distinct_visual_grammar": "yes_trace_and_thumbnail",
        "which_pages_need_repair_and_which_layer": "renderer_first",
    }
    for question_id, expected in expected_answers.items():
        question = value.get(question_id)
        if isinstance(question, dict) and question.get("answer") != expected:
            errors.append(f"{label}.{question_id}.answer must be {expected}")


def validate_run2_74_visual_quality_assessment(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    expected_values = {
        "data_workflow_entry_gate": "pass_internal_only",
        "viewer_comparison_gate": "pass_internal_only",
        "design_quality_gate": "blocked",
        "public_video_readiness": "blocked",
        "global_delta_vs_2_72": "structural_variety_up_public_polish_down",
        "top_blocker": "thin_abstract_renderer_placeholders_do_not_read_as_product_presentation",
        "next_layer_to_fix": "renderer",
    }
    require_keys(label, value, list(expected_values), errors)
    for key, expected in expected_values.items():
        if value.get(key) != expected:
            errors.append(f"{label}.{key} must be {expected}")


def validate_run2_74_visual_quality_role_assessments(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    repair_required_count = 0
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(
            record_label,
            record,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "delta_vs_2_72",
                "text_visual_fusion",
                "report_like_risk",
                "root_cause_layer",
                "repair_required",
                "repair_instruction",
            ],
            errors,
        )
        role = record.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in record and require_integer(f"{record_label}.slide_index", record["slide_index"], errors):
            if record["slide_index"] != index + 1:
                errors.append(f"{record_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if record.get("visual_grammar_module") != expected_module:
                errors.append(f"{record_label}.visual_grammar_module must be {expected_module} for {role}")
        if "delta_vs_2_72" in record:
            require_non_empty_string(f"{record_label}.delta_vs_2_72", record["delta_vs_2_72"], errors)
        if "text_visual_fusion" in record:
            validate_choice(
                f"{record_label}.text_visual_fusion",
                record["text_visual_fusion"],
                RUN2_74_TEXT_VISUAL_FUSION_VALUES,
                errors,
            )
        if "report_like_risk" in record:
            validate_choice(
                f"{record_label}.report_like_risk",
                record["report_like_risk"],
                RUN2_74_REPORT_RISK_VALUES,
                errors,
            )
        if "root_cause_layer" in record:
            validate_choice(
                f"{record_label}.root_cause_layer",
                record["root_cause_layer"],
                RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS,
                errors,
            )
        if record.get("repair_required") is True:
            repair_required_count += 1
        elif "repair_required" in record:
            errors.append(f"{record_label}.repair_required must be true or false")
        if "repair_instruction" in record:
            require_non_empty_string(f"{record_label}.repair_instruction", record["repair_instruction"], errors)
        if "visual_observation" in record:
            require_non_empty_string(f"{record_label}.visual_observation", record["visual_observation"], errors)
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if repair_required_count < 4:
        errors.append(f"{label} must mark at least 4 pages repair_required")


def validate_run2_74_visual_quality_root_cause_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["primary_layer", "not_primary_layer"], errors)
    if value.get("primary_layer") != "renderer":
        errors.append(f"{label}.primary_layer must be renderer")
    if value.get("not_primary_layer") != "data_absence":
        errors.append(f"{label}.not_primary_layer must be data_absence")
    secondary = value.get("secondary_layers")
    if secondary is not None:
        validate_string_list(f"{label}.secondary_layers", secondary, errors)


def validate_run2_75_renderer_repair_rerun_result(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_75_renderer_repair_rerun_result.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_75_renderer_repair_rerun_result"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "public_ready",
            "public_release_started",
            "quality_claim_boundary",
            "consumed_sources",
            "source_h_evaluation",
            "renderer_repair_manifest",
            "rendered_pages",
            "renderer_repair_checks",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part I":
        errors.append(f"{label}.part must be Part I")
    if data.get("run_id") != "2.75":
        errors.append(f"{label}.run_id must be 2.75")
    if data.get("status") != RUN2_75_RENDERER_REPAIR_STATUS:
        errors.append(f"{label}.status must be {RUN2_75_RENDERER_REPAIR_STATUS}")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("quality_claim_boundary") != "renderer_repair_generated_viewer_check_only_no_part_j_quality_verdict":
        errors.append(f"{label}.quality_claim_boundary must be renderer_repair_generated_viewer_check_only_no_part_j_quality_verdict")
    if "consumed_sources" in data:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            data["consumed_sources"],
            RUN2_75_RENDERER_REPAIR_CONSUMED_SOURCE_PATHS,
            errors,
        )
    validate_run2_75_renderer_repair_h_source(
        f"{label}.source_h_evaluation",
        data.get("source_h_evaluation", {}),
        errors,
    )
    validate_run2_75_renderer_repair_manifest(
        f"{label}.renderer_repair_manifest",
        data.get("renderer_repair_manifest", {}),
        errors,
    )
    validate_run2_75_renderer_repair_pages(
        f"{label}.rendered_pages",
        data.get("rendered_pages", []),
        errors,
    )
    validate_run2_75_renderer_repair_checks(
        f"{label}.renderer_repair_checks",
        data.get("renderer_repair_checks", {}),
        errors,
    )
    if data.get("next_required_action") != "part_j_visual_quality_evaluation_for_run2_75":
        errors.append(f"{label}.next_required_action must be part_j_visual_quality_evaluation_for_run2_75")


def validate_run2_75_renderer_repair_h_source(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "top_blocker", "next_required_action"], errors)
    if value.get("status") != RUN2_74_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_74_VISUAL_QUALITY_EVALUATION_STATUS}")
    if value.get("top_blocker") != "thin_abstract_renderer_placeholders_do_not_read_as_product_presentation":
        errors.append(f"{label}.top_blocker must be thin_abstract_renderer_placeholders_do_not_read_as_product_presentation")
    if value.get("next_required_action") != "part_i_renderer_repair_from_visual_quality_evaluation":
        errors.append(f"{label}.next_required_action must be part_i_renderer_repair_from_visual_quality_evaluation")


def validate_run2_75_renderer_repair_manifest(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["generator", "consumed_sources", "best_internal_arm", "outputs", "viewer_update"], errors)
    if value.get("generator") != "scripts/generate_ppt_run2_75_renderer_repair_arms.mjs":
        errors.append(f"{label}.generator must be scripts/generate_ppt_run2_75_renderer_repair_arms.mjs")
    if "consumed_sources" in value:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            value["consumed_sources"],
            RUN2_75_RENDERER_REPAIR_CONSUMED_SOURCE_PATHS,
            errors,
        )
    if value.get("best_internal_arm") != "run2_75_full_renderer_repair":
        errors.append(f"{label}.best_internal_arm must be run2_75_full_renderer_repair")
    outputs = value.get("outputs", {})
    if require_non_empty_dict(f"{label}.outputs", outputs, errors):
        for key in ["html_viewer", "pptx", "ppt_run_viewer"]:
            if key not in outputs:
                errors.append(f"{label}.outputs missing key: {key}")
            else:
                require_non_empty_string(f"{label}.outputs.{key}", outputs[key], errors)
    viewer_update = value.get("viewer_update", {})
    if require_non_empty_dict(f"{label}.viewer_update", viewer_update, errors):
        if viewer_update.get("latest_run_id") != "2.75":
            errors.append(f"{label}.viewer_update.latest_run_id must be 2.75")
        if viewer_update.get("viewer_can_reference_new_run") is not True:
            errors.append(f"{label}.viewer_update.viewer_can_reference_new_run must be true")


def validate_run2_75_renderer_repair_pages(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    density_profiles: set[str] = set()
    for index, page in enumerate(value):
        page_label = f"{label}[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{page_label} must be an object")
            continue
        require_keys(
            page_label,
            page,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "visual_density_profile",
                "source_text_binding_id",
                "text_sockets_used",
                "h_repair_source",
                "renderer_repair_directives_applied",
                "product_surface_detail_count",
                "connector_or_edge_binding_count",
                "source_trace_terms_visible_on_canvas",
                "forbidden_text_patterns_absent",
            ],
            errors,
        )
        role = page.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in page and require_integer(f"{page_label}.slide_index", page["slide_index"], errors):
            if page["slide_index"] != index + 1:
                errors.append(f"{page_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if page.get("visual_grammar_module") != expected_module:
                errors.append(f"{page_label}.visual_grammar_module must be {expected_module} for {role}")
        if "visual_density_profile" in page and require_non_empty_string(
            f"{page_label}.visual_density_profile",
            page["visual_density_profile"],
            errors,
        ):
            density_profiles.add(page["visual_density_profile"])
        if isinstance(role, str) and "source_text_binding_id" in page:
            expected_text_id = f"text_binding_2_73_{role}"
            if page.get("source_text_binding_id") != expected_text_id:
                errors.append(f"{page_label}.source_text_binding_id must be {expected_text_id}")
        if "text_sockets_used" in page:
            validate_exact_string_set(
                f"{page_label}.text_sockets_used",
                page["text_sockets_used"],
                RUN2_73_TEXT_BINDING_REQUIRED_SOCKETS,
                errors,
            )
        validate_run2_75_renderer_repair_page_h_source(f"{page_label}.h_repair_source", page.get("h_repair_source", {}), errors)
        if "renderer_repair_directives_applied" in page:
            validate_exact_string_set(
                f"{page_label}.renderer_repair_directives_applied",
                page["renderer_repair_directives_applied"],
                RUN2_75_RENDERER_REPAIR_DIRECTIVES,
                errors,
            )
        if "product_surface_detail_count" in page and require_integer(
            f"{page_label}.product_surface_detail_count",
            page["product_surface_detail_count"],
            errors,
        ) and page["product_surface_detail_count"] < 5:
            errors.append(f"{page_label}.product_surface_detail_count must be at least 5")
        if "connector_or_edge_binding_count" in page and require_integer(
            f"{page_label}.connector_or_edge_binding_count",
            page["connector_or_edge_binding_count"],
            errors,
        ) and page["connector_or_edge_binding_count"] < 3:
            errors.append(f"{page_label}.connector_or_edge_binding_count must be at least 3")
        if "source_trace_terms_visible_on_canvas" in page:
            visible = page["source_trace_terms_visible_on_canvas"]
            if not isinstance(visible, list):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be a list")
            elif visible:
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be empty")
        if "forbidden_text_patterns_absent" in page:
            validate_exact_string_set(
                f"{page_label}.forbidden_text_patterns_absent",
                page["forbidden_text_patterns_absent"],
                RUN2_73_TEXT_BINDING_FORBIDDEN_PATTERNS,
                errors,
            )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if len(density_profiles) != 6:
        errors.append(f"{label} must contain 6 distinct visual_density_profile values")


def validate_run2_75_renderer_repair_page_h_source(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["root_cause_layer", "repair_instruction"], errors)
    if "root_cause_layer" in value:
        validate_choice(
            f"{label}.root_cause_layer",
            value["root_cause_layer"],
            RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS,
            errors,
        )
    if "repair_instruction" in value:
        require_non_empty_string(f"{label}.repair_instruction", value["repair_instruction"], errors)


def validate_run2_75_renderer_repair_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key, expected in RUN2_75_RENDERER_REPAIR_REQUIRED_CHECKS.items():
        if key not in value:
            errors.append(f"{label} missing key: {key}")
            continue
        if require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")
    if value.get("public_quality_verdict_started") is not False:
        errors.append(f"{label}.public_quality_verdict_started must be false")


def validate_run2_76_visual_quality_evaluation(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_76_visual_quality_evaluation.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_76_visual_quality_evaluation"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "public_ready",
            "quality_claim_boundary",
            "source_runs",
            "input_chain",
            "viewer_comparison_closure",
            "gemini_agent_review_summary",
            "evaluation_questions",
            "visual_quality_assessment",
            "role_assessments",
            "root_cause_summary",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part J":
        errors.append(f"{label}.part must be Part J")
    if data.get("run_id") != "2.76":
        errors.append(f"{label}.run_id must be 2.76")
    if data.get("status") != RUN2_76_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_76_VISUAL_QUALITY_EVALUATION_STATUS}")
    if data.get("creates_new_ppt_deck") is not False:
        errors.append(f"{label}.creates_new_ppt_deck must be false")
    if data.get("starts_renderer_rerun") is not False:
        errors.append(f"{label}.starts_renderer_rerun must be false")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("quality_claim_boundary") != "part_j_evaluation_only_no_public_release_no_renderer_rerun":
        errors.append(f"{label}.quality_claim_boundary must be part_j_evaluation_only_no_public_release_no_renderer_rerun")
    validate_run2_76_visual_quality_source_runs(f"{label}.source_runs", data.get("source_runs", {}), errors)
    validate_run2_76_visual_quality_input_chain(f"{label}.input_chain", data.get("input_chain", {}), errors)
    validate_run2_76_visual_quality_viewer_closure(
        f"{label}.viewer_comparison_closure",
        data.get("viewer_comparison_closure", {}),
        errors,
    )
    validate_run2_76_gemini_summary(
        f"{label}.gemini_agent_review_summary",
        data.get("gemini_agent_review_summary", {}),
        errors,
    )
    validate_run2_76_visual_quality_questions(
        f"{label}.evaluation_questions",
        data.get("evaluation_questions", {}),
        errors,
    )
    validate_run2_76_visual_quality_assessment(
        f"{label}.visual_quality_assessment",
        data.get("visual_quality_assessment", {}),
        errors,
    )
    validate_run2_76_visual_quality_role_assessments(
        f"{label}.role_assessments",
        data.get("role_assessments", []),
        errors,
    )
    validate_run2_76_visual_quality_root_cause_summary(
        f"{label}.root_cause_summary",
        data.get("root_cause_summary", {}),
        errors,
    )
    if data.get("next_required_action") != "part_k_visual_grammar_and_renderer_repair_from_j_evaluation":
        errors.append(f"{label}.next_required_action must be part_k_visual_grammar_and_renderer_repair_from_j_evaluation")


def validate_run2_76_visual_quality_source_runs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["comparison_baseline", "evaluated_run"], errors)
    if value.get("comparison_baseline") != "2.73":
        errors.append(f"{label}.comparison_baseline must be 2.73")
    if value.get("evaluated_run") != "2.75":
        errors.append(f"{label}.evaluated_run must be 2.75")


def validate_run2_76_visual_quality_input_chain(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    required = [
        "run2_73_result",
        "run2_75_result",
        "run2_74_h_evaluation",
        "run2_73_full_contact_sheet",
        "run2_75_full_contact_sheet",
        "ppt_run_viewer",
    ]
    require_keys(label, value, required, errors)
    for key in required:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_76_visual_quality_viewer_closure(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "viewer_latest_run_id",
            "viewer_can_compare_2_73_and_2_75",
            "run2_73_full_preview_count",
            "run2_75_full_preview_count",
            "browser_check_required_for_handoff",
        ],
        errors,
    )
    if value.get("viewer_latest_run_id") != "2.75":
        errors.append(f"{label}.viewer_latest_run_id must be 2.75")
    if value.get("viewer_can_compare_2_73_and_2_75") is not True:
        errors.append(f"{label}.viewer_can_compare_2_73_and_2_75 must be true")
    for key in ["run2_73_full_preview_count", "run2_75_full_preview_count"]:
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] != 6:
            errors.append(f"{label}.{key} must be 6")
    if value.get("browser_check_required_for_handoff") is not True:
        errors.append(f"{label}.browser_check_required_for_handoff must be true")


def validate_run2_76_gemini_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["tool", "model", "review_count", "used_for_verdict", "run2_75_findings", "shared_risks"], errors)
    if value.get("tool") != "mcp__gemini_agent.gemini_artifact_review":
        errors.append(f"{label}.tool must be mcp__gemini_agent.gemini_artifact_review")
    if value.get("model") != "gemini-3.5-flash":
        errors.append(f"{label}.model must be gemini-3.5-flash")
    if "review_count" in value and require_integer(f"{label}.review_count", value["review_count"], errors) and value["review_count"] != 2:
        errors.append(f"{label}.review_count must be 2")
    if value.get("used_for_verdict") is not True:
        errors.append(f"{label}.used_for_verdict must be true")
    if "run2_75_findings" in value:
        validate_string_list(f"{label}.run2_75_findings", value["run2_75_findings"], errors)
    if "shared_risks" in value:
        validate_string_list(f"{label}.shared_risks", value["shared_risks"], errors)


def validate_run2_76_visual_quality_questions(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for question_id in sorted(RUN2_76_VISUAL_QUALITY_QUESTION_IDS):
        if question_id not in value:
            errors.append(f"{label} missing key: {question_id}")
            continue
        question = value[question_id]
        question_label = f"{label}.{question_id}"
        if not require_non_empty_dict(question_label, question, errors):
            continue
        require_keys(question_label, question, ["answer"], errors)
        if "answer" in question:
            require_non_empty_string(f"{question_label}.answer", question["answer"], errors)
    expected_answers = {
        "is_2_75_better_than_2_73": "mixed_product_surface_up_page_differentiation_down_public_blocked",
        "does_2_75_have_stronger_product_feel": "yes_but_still_wireframe",
        "are_page_differences_stronger_or_weaker": "weaker_for_core_product_surface_pages",
        "is_text_binding_better": "slightly_stronger_but_small_labels_remain",
        "does_2_75_reach_public_video_presentation_direction": "no_internal_blueprint_risk_remains",
    }
    for question_id, expected in expected_answers.items():
        question = value.get(question_id)
        if isinstance(question, dict) and question.get("answer") != expected:
            errors.append(f"{label}.{question_id}.answer must be {expected}")


def validate_run2_76_visual_quality_assessment(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    expected_values = {
        "data_workflow_entry_gate": "pass_internal_only",
        "viewer_comparison_gate": "pass_internal_only",
        "design_quality_gate": "blocked",
        "public_video_readiness": "blocked",
        "global_delta_vs_2_73": "product_surface_up_page_differentiation_down_public_readiness_still_blocked",
        "top_blocker": "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams",
        "next_layer_to_fix": "visual_grammar_and_renderer",
    }
    require_keys(label, value, list(expected_values), errors)
    for key, expected in expected_values.items():
        if value.get(key) != expected:
            errors.append(f"{label}.{key} must be {expected}")


def validate_run2_76_visual_quality_role_assessments(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    repair_count = 0
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(
            record_label,
            record,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "product_feel_delta",
                "page_differentiation_delta",
                "text_binding_delta",
                "engineering_report_risk",
                "public_video_direction",
                "root_cause_layer",
                "repair_required",
                "repair_instruction",
            ],
            errors,
        )
        role = record.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in record and require_integer(f"{record_label}.slide_index", record["slide_index"], errors):
            if record["slide_index"] != index + 1:
                errors.append(f"{record_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if record.get("visual_grammar_module") != expected_module:
                errors.append(f"{record_label}.visual_grammar_module must be {expected_module} for {role}")
        if "product_feel_delta" in record:
            validate_choice(f"{record_label}.product_feel_delta", record["product_feel_delta"], RUN2_76_PRODUCT_FEEL_DELTA_VALUES, errors)
        if "page_differentiation_delta" in record:
            validate_choice(
                f"{record_label}.page_differentiation_delta",
                record["page_differentiation_delta"],
                RUN2_76_PAGE_DIFFERENTIATION_VALUES,
                errors,
            )
        if "text_binding_delta" in record:
            validate_choice(f"{record_label}.text_binding_delta", record["text_binding_delta"], RUN2_76_TEXT_BINDING_DELTA_VALUES, errors)
        if "engineering_report_risk" in record:
            validate_choice(f"{record_label}.engineering_report_risk", record["engineering_report_risk"], RUN2_74_REPORT_RISK_VALUES, errors)
        if "public_video_direction" in record:
            validate_choice(f"{record_label}.public_video_direction", record["public_video_direction"], RUN2_76_PUBLIC_VIDEO_DIRECTION_VALUES, errors)
        if "root_cause_layer" in record:
            validate_choice(
                f"{record_label}.root_cause_layer",
                record["root_cause_layer"],
                RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS,
                errors,
            )
        if record.get("repair_required") is True:
            repair_count += 1
        elif "repair_required" in record:
            errors.append(f"{record_label}.repair_required must be true or false")
        if "repair_instruction" in record:
            require_non_empty_string(f"{record_label}.repair_instruction", record["repair_instruction"], errors)
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if repair_count < 5:
        errors.append(f"{label} must mark at least 5 pages repair_required")


def validate_run2_76_visual_quality_root_cause_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["primary_layer", "not_primary_layer"], errors)
    if value.get("primary_layer") != "visual_grammar_and_renderer":
        errors.append(f"{label}.primary_layer must be visual_grammar_and_renderer")
    if value.get("not_primary_layer") != "data_absence":
        errors.append(f"{label}.not_primary_layer must be data_absence")
    secondary = value.get("secondary_layers")
    if secondary is not None:
        validate_string_list(f"{label}.secondary_layers", secondary, errors)


def validate_run2_76_visual_grammar_renderer_repair_plan(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "run2_76_visual_grammar_renderer_repair_plan.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_76_visual_grammar_renderer_repair_plan"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "stage_policy",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "updates_html_viewer",
            "public_release_started",
            "public_ready",
            "quality_claim_boundary",
            "consumed_sources",
            "source_j_evaluation",
            "source_run2_75_renderer_repair",
            "source_trace",
            "global_repair_strategy",
            "page_repair_plans",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part K1":
        errors.append(f"{label}.part must be Part K1")
    if data.get("run_id") != "2.76":
        errors.append(f"{label}.run_id must be 2.76")
    if data.get("status") != RUN2_76_K1_REPAIR_PLAN_STATUS:
        errors.append(f"{label}.status must be {RUN2_76_K1_REPAIR_PLAN_STATUS}")
    if data.get("stage_policy") != "part_k1_repair_contract_only_no_renderer_rerun_no_public_release":
        errors.append(f"{label}.stage_policy must be part_k1_repair_contract_only_no_renderer_rerun_no_public_release")
    if data.get("creates_new_ppt_deck") is not False:
        errors.append(f"{label}.creates_new_ppt_deck must be false")
    if data.get("starts_renderer_rerun") is not False:
        errors.append(f"{label}.starts_renderer_rerun must be false")
    if data.get("updates_html_viewer") is not False:
        errors.append(f"{label}.updates_html_viewer must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("quality_claim_boundary") != "part_k1_repair_contract_only_no_renderer_rerun_no_public_release":
        errors.append(f"{label}.quality_claim_boundary must be part_k1_repair_contract_only_no_renderer_rerun_no_public_release")
    validate_exact_string_set(f"{label}.consumed_sources", data.get("consumed_sources", []), RUN2_76_K1_REPAIR_PLAN_CONSUMED_SOURCE_PATHS, errors)
    validate_run2_76_k1_source_j_evaluation(f"{label}.source_j_evaluation", data.get("source_j_evaluation", {}), errors)
    validate_run2_76_k1_source_run2_75(
        f"{label}.source_run2_75_renderer_repair",
        data.get("source_run2_75_renderer_repair", {}),
        errors,
    )
    validate_run2_76_k1_source_trace(f"{label}.source_trace", data.get("source_trace", {}), errors)
    validate_run2_76_k1_global_repair_strategy(
        f"{label}.global_repair_strategy",
        data.get("global_repair_strategy", {}),
        errors,
    )
    validate_run2_76_k1_page_repair_plans(f"{label}.page_repair_plans", data.get("page_repair_plans", []), errors)
    if data.get("next_required_action") != "part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan":
        errors.append(f"{label}.next_required_action must be part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan")


def validate_run2_76_k1_source_j_evaluation(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "source_path",
            "status",
            "top_blocker",
            "primary_layer_to_fix",
            "secondary_layers",
            "next_required_action",
        ],
        errors,
    )
    if value.get("source_path") != "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json":
        errors.append(f"{label}.source_path must reference run2_76_visual_quality_evaluation.json")
    if value.get("status") != RUN2_76_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_76_VISUAL_QUALITY_EVALUATION_STATUS}")
    if value.get("top_blocker") != "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams":
        errors.append(f"{label}.top_blocker must match Run 2.76 visual quality top blocker")
    if value.get("primary_layer_to_fix") != "visual_grammar_and_renderer":
        errors.append(f"{label}.primary_layer_to_fix must be visual_grammar_and_renderer")
    if "secondary_layers" in value:
        validate_string_list(f"{label}.secondary_layers", value["secondary_layers"], errors)
        if set(value["secondary_layers"]) != {"text_binding"}:
            errors.append(f"{label}.secondary_layers must include only text_binding")
    if value.get("next_required_action") != "part_k_visual_grammar_and_renderer_repair_from_j_evaluation":
        errors.append(f"{label}.next_required_action must be part_k_visual_grammar_and_renderer_repair_from_j_evaluation")


def validate_run2_76_k1_source_run2_75(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["source_path", "status", "public_ready"], errors)
    if value.get("source_path") != "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json":
        errors.append(f"{label}.source_path must reference run2_75_renderer_repair_rerun_result.json")
    if value.get("status") != RUN2_75_RENDERER_REPAIR_STATUS:
        errors.append(f"{label}.status must be {RUN2_75_RENDERER_REPAIR_STATUS}")
    if value.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")


def validate_run2_76_k1_source_trace(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    expected = {
        "visual_grammar_modules": "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
        "renderer_adapter_contracts": "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
        "text_binding_strategy": "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
        "scene_plan_expansion": "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
    }
    require_keys(label, value, list(expected), errors)
    for key, expected_path in expected.items():
        if value.get(key) != expected_path:
            errors.append(f"{label}.{key} must be {expected_path}")


def validate_run2_76_k1_global_repair_strategy(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "from_failure_mode",
            "target_shift",
            "primary_layers_to_fix",
            "secondary_layers_to_fix",
            "not_data_layer_reason",
            "page_differentiation_mandates",
            "renderer_capabilities_required",
            "forbidden_renderer_fallbacks",
            "quality_gate",
        ],
        errors,
    )
    for key in ["from_failure_mode", "target_shift", "not_data_layer_reason", "quality_gate"]:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)
    if value.get("primary_layers_to_fix") != ["visual_grammar", "renderer"]:
        errors.append(f"{label}.primary_layers_to_fix must be visual_grammar, renderer")
    if value.get("secondary_layers_to_fix") != ["text_binding"]:
        errors.append(f"{label}.secondary_layers_to_fix must be text_binding")
    if "page_differentiation_mandates" in value:
        validate_string_list(f"{label}.page_differentiation_mandates", value["page_differentiation_mandates"], errors)
    validate_exact_string_set(
        f"{label}.renderer_capabilities_required",
        value.get("renderer_capabilities_required", []),
        RUN2_76_K1_RENDERER_CAPABILITIES,
        errors,
    )
    validate_exact_string_set(
        f"{label}.forbidden_renderer_fallbacks",
        value.get("forbidden_renderer_fallbacks", []),
        RUN2_76_K1_FORBIDDEN_RENDERER_FALLBACKS,
        errors,
    )


def validate_run2_76_k1_page_repair_plans(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    target_scene_directions: set[str] = set()
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(record_label, record, RUN2_76_K1_PAGE_REPAIR_FIELDS, errors)
        role = record.get("role")
        expected_role = RUN2_73_VISUAL_GRAMMAR_ROLES[index] if index < len(RUN2_73_VISUAL_GRAMMAR_ROLES) else None
        if role != expected_role:
            errors.append(f"{record_label}.role must be {expected_role}")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in record and require_integer(f"{record_label}.slide_index", record["slide_index"], errors):
            if record["slide_index"] != index + 1:
                errors.append(f"{record_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if record.get("visual_grammar_module") != expected_module:
                errors.append(f"{record_label}.visual_grammar_module must be {expected_module} for {role}")
        for key in [
            "current_failure",
            "target_scene_direction",
            "visual_grammar_change",
            "renderer_change",
            "text_binding_adjustment",
        ]:
            if key in record:
                require_non_empty_string(f"{record_label}.{key}", record[key], errors)
        target = record.get("target_scene_direction")
        if isinstance(target, str) and target.strip():
            if target in target_scene_directions:
                errors.append(f"{record_label}.target_scene_direction duplicates {target}")
            target_scene_directions.add(target)
        validate_string_list(f"{record_label}.must_preserve_from_2_75", record.get("must_preserve_from_2_75", []), errors)
        if validate_string_list(f"{record_label}.must_remove_from_2_75", record.get("must_remove_from_2_75", []), errors):
            if not (set(record["must_remove_from_2_75"]) & RUN2_76_K1_FORBIDDEN_RENDERER_FALLBACKS):
                errors.append(f"{record_label}.must_remove_from_2_75 must include a forbidden 2.75 renderer fallback")
        validate_run2_76_k1_page_source_j_assessment(
            f"{record_label}.source_j_assessment",
            record.get("source_j_assessment", {}),
            errors,
        )
        validate_run2_76_k1_acceptance_checks(
            f"{record_label}.acceptance_checks",
            record.get("acceptance_checks", {}),
            errors,
        )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if len(target_scene_directions) != 6:
        errors.append(f"{label}.target_scene_direction values must be unique across six pages")


def validate_run2_76_k1_page_source_j_assessment(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["root_cause_layer", "repair_instruction"], errors)
    if "root_cause_layer" in value:
        validate_choice(f"{label}.root_cause_layer", value["root_cause_layer"], RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS, errors)
    if "repair_instruction" in value:
        require_non_empty_string(f"{label}.repair_instruction", value["repair_instruction"], errors)


def validate_run2_76_k1_acceptance_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, sorted(RUN2_76_K1_ACCEPTANCE_CHECK_KEYS), errors)
    for key in ["page_differentiation_check", "wireframe_reduction_check", "renderer_capability_check"]:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)
    if value.get("no_renderer_rerun_in_k1") is not True:
        errors.append(f"{label}.no_renderer_rerun_in_k1 must be true")


def validate_run2_77_visual_grammar_renderer_repair_rerun_result(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_77_visual_grammar_renderer_repair_rerun_result.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_77_visual_grammar_renderer_repair_rerun_result"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "public_ready",
            "public_release_started",
            "quality_claim_boundary",
            "consumed_sources",
            "source_k1_repair_plan",
            "visual_grammar_renderer_repair_manifest",
            "rendered_pages",
            "visual_grammar_renderer_repair_checks",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part K2":
        errors.append(f"{label}.part must be Part K2")
    if data.get("run_id") != "2.77":
        errors.append(f"{label}.run_id must be 2.77")
    if data.get("status") != RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_STATUS:
        errors.append(f"{label}.status must be {RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_STATUS}")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("quality_claim_boundary") != "visual_grammar_renderer_repair_generated_viewer_check_only_no_part_l_quality_verdict":
        errors.append(f"{label}.quality_claim_boundary must be visual_grammar_renderer_repair_generated_viewer_check_only_no_part_l_quality_verdict")
    if "consumed_sources" in data:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            data["consumed_sources"],
            RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_CONSUMED_SOURCE_PATHS,
            errors,
        )
    validate_run2_77_source_k1_repair_plan(f"{label}.source_k1_repair_plan", data.get("source_k1_repair_plan", {}), errors)
    validate_run2_77_repair_manifest(
        f"{label}.visual_grammar_renderer_repair_manifest",
        data.get("visual_grammar_renderer_repair_manifest", {}),
        errors,
    )
    validate_run2_77_rendered_pages(f"{label}.rendered_pages", data.get("rendered_pages", []), errors)
    validate_run2_77_repair_checks(
        f"{label}.visual_grammar_renderer_repair_checks",
        data.get("visual_grammar_renderer_repair_checks", {}),
        errors,
    )
    if data.get("next_required_action") != "part_l_visual_quality_evaluation_for_run2_77":
        errors.append(f"{label}.next_required_action must be part_l_visual_quality_evaluation_for_run2_77")


def validate_run2_77_source_k1_repair_plan(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "top_blocker", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_76_K1_REPAIR_PLAN_STATUS:
        errors.append(f"{label}.status must be {RUN2_76_K1_REPAIR_PLAN_STATUS}")
    if value.get("top_blocker") != "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams":
        errors.append(f"{label}.top_blocker must match Run 2.76/K1 top blocker")
    if value.get("next_required_action") != "part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan":
        errors.append(f"{label}.next_required_action must be part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json":
        errors.append(f"{label}.source_result must reference run2_76_visual_grammar_renderer_repair_plan.json")


def validate_run2_77_repair_manifest(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["generator", "consumed_sources", "best_internal_arm", "outputs", "viewer_update"], errors)
    if value.get("generator") != "scripts/generate_ppt_run2_77_visual_grammar_renderer_repair_arms.mjs":
        errors.append(f"{label}.generator must be scripts/generate_ppt_run2_77_visual_grammar_renderer_repair_arms.mjs")
    if "consumed_sources" in value:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            value["consumed_sources"],
            RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_CONSUMED_SOURCE_PATHS,
            errors,
        )
    if value.get("best_internal_arm") != "run2_77_full_visual_grammar_renderer_repair":
        errors.append(f"{label}.best_internal_arm must be run2_77_full_visual_grammar_renderer_repair")
    outputs = value.get("outputs", {})
    if require_non_empty_dict(f"{label}.outputs", outputs, errors):
        for key in ["html_viewer", "pptx", "ppt_run_viewer"]:
            if key not in outputs:
                errors.append(f"{label}.outputs missing key: {key}")
            else:
                require_non_empty_string(f"{label}.outputs.{key}", outputs[key], errors)
    viewer_update = value.get("viewer_update", {})
    if require_non_empty_dict(f"{label}.viewer_update", viewer_update, errors):
        if viewer_update.get("latest_run_id") != "2.77":
            errors.append(f"{label}.viewer_update.latest_run_id must be 2.77")
        if viewer_update.get("viewer_can_reference_new_run") is not True:
            errors.append(f"{label}.viewer_update.viewer_can_reference_new_run must be true")


def validate_run2_77_rendered_pages(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    target_scene_directions: set[str] = set()
    capability_union: set[str] = set()
    for index, page in enumerate(value):
        page_label = f"{label}[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{page_label} must be an object")
            continue
        require_keys(
            page_label,
            page,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "target_scene_direction",
                "source_k1_repair_plan",
                "renderer_repair_directives_applied",
                "renderer_capabilities_applied",
                "forbidden_renderer_fallbacks_absent",
                "label_count",
                "source_trace_terms_visible_on_canvas",
                "visual_containers",
                "k1_acceptance_checks",
            ],
            errors,
        )
        role = page.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in page and require_integer(f"{page_label}.slide_index", page["slide_index"], errors):
            if page["slide_index"] != index + 1:
                errors.append(f"{page_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if page.get("visual_grammar_module") != expected_module:
                errors.append(f"{page_label}.visual_grammar_module must be {expected_module} for {role}")
        target = page.get("target_scene_direction")
        if require_non_empty_string(f"{page_label}.target_scene_direction", target, errors):
            if target in target_scene_directions:
                errors.append(f"{page_label}.target_scene_direction duplicates {target}")
            target_scene_directions.add(target)
        if "renderer_repair_directives_applied" in page:
            validate_exact_string_set(
                f"{page_label}.renderer_repair_directives_applied",
                page["renderer_repair_directives_applied"],
                RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_DIRECTIVES,
                errors,
            )
        if validate_string_list(f"{page_label}.renderer_capabilities_applied", page.get("renderer_capabilities_applied", []), errors):
            capabilities = set(page["renderer_capabilities_applied"])
            capability_union.update(capabilities)
            for capability in sorted(capabilities - RUN2_76_K1_RENDERER_CAPABILITIES):
                errors.append(f"{page_label}.renderer_capabilities_applied has unexpected value: {capability}")
        if "forbidden_renderer_fallbacks_absent" in page:
            validate_exact_string_set(
                f"{page_label}.forbidden_renderer_fallbacks_absent",
                page["forbidden_renderer_fallbacks_absent"],
                RUN2_76_K1_FORBIDDEN_RENDERER_FALLBACKS,
                errors,
            )
        if "label_count" in page and require_integer(f"{page_label}.label_count", page["label_count"], errors):
            if page["label_count"] > 5:
                errors.append(f"{page_label}.label_count must be at most 5")
        if "source_trace_terms_visible_on_canvas" in page:
            visible = page["source_trace_terms_visible_on_canvas"]
            if not isinstance(visible, list):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be a list")
            elif visible:
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be empty")
        if "visual_containers" in page:
            require_non_empty_list(f"{page_label}.visual_containers", page["visual_containers"], errors)
        validate_run2_76_k1_acceptance_checks(
            f"{page_label}.k1_acceptance_checks",
            page.get("k1_acceptance_checks", {}),
            errors,
        )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if len(target_scene_directions) != 6:
        errors.append(f"{label}.target_scene_direction values must be unique across six pages")
    for capability in sorted(RUN2_76_K1_RENDERER_CAPABILITIES - capability_union):
        errors.append(f"{label}.renderer_capabilities_applied missing required capability across pages: {capability}")


def validate_run2_77_repair_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key, expected in RUN2_77_VISUAL_GRAMMAR_RENDERER_REPAIR_REQUIRED_CHECKS.items():
        if key not in value:
            errors.append(f"{label} missing key: {key}")
            continue
        if require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")
    if "required_renderer_capabilities_covered" in value:
        validate_exact_string_set(
            f"{label}.required_renderer_capabilities_covered",
            value["required_renderer_capabilities_covered"],
            RUN2_76_K1_RENDERER_CAPABILITIES,
            errors,
        )
    else:
        errors.append(f"{label} missing key: required_renderer_capabilities_covered")
    if value.get("public_quality_verdict_started") is not False:
        errors.append(f"{label}.public_quality_verdict_started must be false")


def validate_run2_78_visual_quality_evaluation(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_78_visual_quality_evaluation.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_78_visual_quality_evaluation"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "updates_html_viewer",
            "public_release_started",
            "public_ready",
            "quality_claim_boundary",
            "source_runs",
            "input_chain",
            "viewer_comparison_closure",
            "gemini_agent_review_summary",
            "evaluation_questions",
            "visual_quality_assessment",
            "role_assessments",
            "root_cause_summary",
            "no_new_renderer_proof",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part L":
        errors.append(f"{label}.part must be Part L")
    if data.get("run_id") != "2.78":
        errors.append(f"{label}.run_id must be 2.78")
    if data.get("status") != RUN2_78_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_78_VISUAL_QUALITY_EVALUATION_STATUS}")
    if data.get("creates_new_ppt_deck") is not False:
        errors.append(f"{label}.creates_new_ppt_deck must be false")
    if data.get("starts_renderer_rerun") is not False:
        errors.append(f"{label}.starts_renderer_rerun must be false")
    if data.get("updates_html_viewer") is not False:
        errors.append(f"{label}.updates_html_viewer must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("quality_claim_boundary") != "part_l_evaluation_only_no_public_release_no_renderer_rerun":
        errors.append(f"{label}.quality_claim_boundary must be part_l_evaluation_only_no_public_release_no_renderer_rerun")
    validate_run2_78_visual_quality_source_runs(f"{label}.source_runs", data.get("source_runs", {}), errors)
    validate_run2_78_visual_quality_input_chain(f"{label}.input_chain", data.get("input_chain", {}), errors)
    validate_run2_78_visual_quality_viewer_closure(
        f"{label}.viewer_comparison_closure",
        data.get("viewer_comparison_closure", {}),
        errors,
    )
    validate_run2_78_gemini_summary(
        f"{label}.gemini_agent_review_summary",
        data.get("gemini_agent_review_summary", {}),
        errors,
    )
    validate_run2_78_visual_quality_questions(
        f"{label}.evaluation_questions",
        data.get("evaluation_questions", {}),
        errors,
    )
    validate_run2_78_visual_quality_assessment(
        f"{label}.visual_quality_assessment",
        data.get("visual_quality_assessment", {}),
        errors,
    )
    validate_run2_78_visual_quality_role_assessments(
        f"{label}.role_assessments",
        data.get("role_assessments", []),
        errors,
    )
    validate_run2_78_visual_quality_root_cause_summary(
        f"{label}.root_cause_summary",
        data.get("root_cause_summary", {}),
        errors,
    )
    validate_run2_78_no_new_renderer_proof(
        f"{label}.no_new_renderer_proof",
        data.get("no_new_renderer_proof", {}),
        errors,
    )
    if data.get("next_required_action") != "part_m_renderer_art_direction_repair_from_l_evaluation":
        errors.append(f"{label}.next_required_action must be part_m_renderer_art_direction_repair_from_l_evaluation")


def validate_run2_78_visual_quality_source_runs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["comparison_baseline", "evaluated_run", "prior_reference_run"], errors)
    if value.get("comparison_baseline") != "2.75":
        errors.append(f"{label}.comparison_baseline must be 2.75")
    if value.get("evaluated_run") != "2.77":
        errors.append(f"{label}.evaluated_run must be 2.77")
    if value.get("prior_reference_run") != "2.73":
        errors.append(f"{label}.prior_reference_run must be 2.73")


def validate_run2_78_visual_quality_input_chain(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    required = [
        "run2_77_result",
        "run2_76_j_evaluation",
        "run2_76_k1_repair_plan",
        "run2_75_full_contact_sheet",
        "run2_77_full_contact_sheet",
        "ppt_run_viewer",
    ]
    require_keys(label, value, required, errors)
    for key in required:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_78_visual_quality_viewer_closure(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "viewer_latest_run_id",
            "viewer_can_compare_2_75_and_2_77",
            "run2_75_full_preview_count",
            "run2_77_full_preview_count",
            "browser_check_required_for_handoff",
        ],
        errors,
    )
    if value.get("viewer_latest_run_id") != "2.77":
        errors.append(f"{label}.viewer_latest_run_id must be 2.77")
    if value.get("viewer_can_compare_2_75_and_2_77") is not True:
        errors.append(f"{label}.viewer_can_compare_2_75_and_2_77 must be true")
    for key in ["run2_75_full_preview_count", "run2_77_full_preview_count"]:
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] != 6:
            errors.append(f"{label}.{key} must be 6")
    if value.get("browser_check_required_for_handoff") is not True:
        errors.append(f"{label}.browser_check_required_for_handoff must be true")


def validate_run2_78_gemini_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["tool", "model", "review_count", "used_for_verdict", "run2_77_findings", "run2_77_risks"], errors)
    if value.get("tool") != "mcp__gemini_agent.gemini_artifact_review":
        errors.append(f"{label}.tool must be mcp__gemini_agent.gemini_artifact_review")
    if value.get("model") != "gemini-3.5-flash":
        errors.append(f"{label}.model must be gemini-3.5-flash")
    if "review_count" in value and require_integer(f"{label}.review_count", value["review_count"], errors) and value["review_count"] != 1:
        errors.append(f"{label}.review_count must be 1")
    if value.get("used_for_verdict") is not True:
        errors.append(f"{label}.used_for_verdict must be true")
    if "run2_77_findings" in value:
        validate_string_list(f"{label}.run2_77_findings", value["run2_77_findings"], errors)
    if "run2_77_risks" in value:
        validate_string_list(f"{label}.run2_77_risks", value["run2_77_risks"], errors)


def validate_run2_78_visual_quality_questions(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for question_id in sorted(RUN2_78_VISUAL_QUALITY_QUESTION_IDS):
        if question_id not in value:
            errors.append(f"{label} missing key: {question_id}")
            continue
        question = value[question_id]
        question_label = f"{label}.{question_id}"
        if not require_non_empty_dict(question_label, question, errors):
            continue
        require_keys(question_label, question, ["answer"], errors)
        if "answer" in question:
            require_non_empty_string(f"{question_label}.answer", question["answer"], errors)
    for question_id, expected in RUN2_78_VISUAL_QUALITY_EXPECTED_ANSWERS.items():
        question = value.get(question_id)
        if isinstance(question, dict) and question.get("answer") != expected:
            errors.append(f"{label}.{question_id}.answer must be {expected}")


def validate_run2_78_visual_quality_assessment(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    expected_values = {
        "data_workflow_entry_gate": "pass_internal_only",
        "viewer_comparison_gate": "pass_internal_only",
        "design_quality_gate": "blocked",
        "public_video_readiness": "blocked",
        "global_delta_vs_2_75": "page_differentiation_up_label_count_down_wireframe_still_blocks_public_readiness",
        "top_blocker": "thin_wireframe_product_surfaces_and_annotation_marks_still_read_as_internal_diagram",
        "next_layer_to_fix": "renderer_art_direction_and_scene_realization",
    }
    require_keys(label, value, list(expected_values), errors)
    for key, expected in expected_values.items():
        if value.get(key) != expected:
            errors.append(f"{label}.{key} must be {expected}")


def validate_run2_78_visual_quality_role_assessments(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    repair_count = 0
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(
            record_label,
            record,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "delta_vs_2_75",
                "page_differentiation",
                "wireframe_reduction",
                "label_hierarchy",
                "public_video_direction",
                "root_cause_layer",
                "repair_required",
                "next_repair_instruction",
                "trace_support",
            ],
            errors,
        )
        role = record.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in record and require_integer(f"{record_label}.slide_index", record["slide_index"], errors):
            if record["slide_index"] != index + 1:
                errors.append(f"{record_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if record.get("visual_grammar_module") != expected_module:
                errors.append(f"{record_label}.visual_grammar_module must be {expected_module} for {role}")
        if "delta_vs_2_75" in record:
            validate_choice(f"{record_label}.delta_vs_2_75", record["delta_vs_2_75"], RUN2_78_DELTA_VALUES, errors)
        if "page_differentiation" in record:
            validate_choice(f"{record_label}.page_differentiation", record["page_differentiation"], RUN2_78_DELTA_VALUES, errors)
        if "wireframe_reduction" in record:
            validate_choice(f"{record_label}.wireframe_reduction", record["wireframe_reduction"], RUN2_78_WIREFRAME_REDUCTION_VALUES, errors)
        if "label_hierarchy" in record:
            validate_choice(f"{record_label}.label_hierarchy", record["label_hierarchy"], RUN2_78_LABEL_HIERARCHY_VALUES, errors)
        if "public_video_direction" in record:
            validate_choice(f"{record_label}.public_video_direction", record["public_video_direction"], RUN2_76_PUBLIC_VIDEO_DIRECTION_VALUES, errors)
        if "root_cause_layer" in record:
            validate_choice(
                f"{record_label}.root_cause_layer",
                record["root_cause_layer"],
                RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS,
                errors,
            )
        if record.get("repair_required") is not True:
            errors.append(f"{record_label}.repair_required must be true")
        else:
            repair_count += 1
        if "next_repair_instruction" in record:
            require_non_empty_string(f"{record_label}.next_repair_instruction", record["next_repair_instruction"], errors)
        trace = record.get("trace_support", {})
        if require_non_empty_dict(f"{record_label}.trace_support", trace, errors):
            if "target_scene_direction" in trace:
                require_non_empty_string(f"{record_label}.trace_support.target_scene_direction", trace["target_scene_direction"], errors)
            else:
                errors.append(f"{record_label}.trace_support missing key: target_scene_direction")
            if "label_count" in trace and require_integer(f"{record_label}.trace_support.label_count", trace["label_count"], errors):
                if trace["label_count"] > 5:
                    errors.append(f"{record_label}.trace_support.label_count must be at most 5")
            elif "label_count" not in trace:
                errors.append(f"{record_label}.trace_support missing key: label_count")
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if repair_count != 6:
        errors.append(f"{label} must mark all six pages repair_required")


def validate_run2_78_visual_quality_root_cause_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["primary_layer", "not_primary_layer"], errors)
    if value.get("primary_layer") != "renderer_art_direction_and_scene_realization":
        errors.append(f"{label}.primary_layer must be renderer_art_direction_and_scene_realization")
    if value.get("not_primary_layer") != "data_absence":
        errors.append(f"{label}.not_primary_layer must be data_absence")
    secondary = value.get("secondary_layers")
    if secondary is not None:
        validate_string_list(f"{label}.secondary_layers", secondary, errors)


def validate_run2_78_no_new_renderer_proof(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key in ["new_pptx_created", "new_html_created", "starts_renderer_rerun"]:
        if key not in value:
            errors.append(f"{label} missing key: {key}")
        elif value.get(key) is not False:
            errors.append(f"{label}.{key} must be false")
    if value.get("status") != "pass":
        errors.append(f"{label}.status must be pass")


def validate_run2_79_renderer_art_direction_repair_rerun_result(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_79_renderer_art_direction_repair_rerun_result.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_79_renderer_art_direction_repair_rerun_result"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "public_ready",
            "public_release_started",
            "quality_claim_boundary",
            "consumed_sources",
            "source_l_evaluation",
            "renderer_art_direction_repair_manifest",
            "rendered_pages",
            "renderer_art_direction_repair_checks",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part M":
        errors.append(f"{label}.part must be Part M")
    if data.get("run_id") != "2.79":
        errors.append(f"{label}.run_id must be 2.79")
    if data.get("status") != RUN2_79_RENDERER_ART_DIRECTION_REPAIR_STATUS:
        errors.append(f"{label}.status must be {RUN2_79_RENDERER_ART_DIRECTION_REPAIR_STATUS}")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("quality_claim_boundary") != "renderer_art_direction_repair_generated_viewer_check_only_no_part_n_quality_verdict":
        errors.append(f"{label}.quality_claim_boundary must be renderer_art_direction_repair_generated_viewer_check_only_no_part_n_quality_verdict")
    if "consumed_sources" in data:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            data["consumed_sources"],
            RUN2_79_RENDERER_ART_DIRECTION_REPAIR_CONSUMED_SOURCE_PATHS,
            errors,
        )
    validate_run2_79_source_l_evaluation(f"{label}.source_l_evaluation", data.get("source_l_evaluation", {}), errors)
    validate_run2_79_repair_manifest(
        f"{label}.renderer_art_direction_repair_manifest",
        data.get("renderer_art_direction_repair_manifest", {}),
        errors,
    )
    validate_run2_79_rendered_pages(f"{label}.rendered_pages", data.get("rendered_pages", []), errors)
    validate_run2_79_repair_checks(
        f"{label}.renderer_art_direction_repair_checks",
        data.get("renderer_art_direction_repair_checks", {}),
        errors,
    )
    if data.get("next_required_action") != "part_n_visual_quality_evaluation_for_run2_79":
        errors.append(f"{label}.next_required_action must be part_n_visual_quality_evaluation_for_run2_79")


def validate_run2_79_source_l_evaluation(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "top_blocker", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_78_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_78_VISUAL_QUALITY_EVALUATION_STATUS}")
    if value.get("top_blocker") != "thin_wireframe_product_surfaces_and_annotation_marks_still_read_as_internal_diagram":
        errors.append(f"{label}.top_blocker must match Run 2.78 visual quality top blocker")
    if value.get("next_required_action") != "part_m_renderer_art_direction_repair_from_l_evaluation":
        errors.append(f"{label}.next_required_action must be part_m_renderer_art_direction_repair_from_l_evaluation")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json":
        errors.append(f"{label}.source_result must reference run2_78_visual_quality_evaluation.json")


def validate_run2_79_repair_manifest(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["generator", "consumed_sources", "best_internal_arm", "outputs", "viewer_update"], errors)
    if value.get("generator") != "scripts/generate_ppt_run2_79_renderer_art_direction_repair_arms.mjs":
        errors.append(f"{label}.generator must be scripts/generate_ppt_run2_79_renderer_art_direction_repair_arms.mjs")
    if "consumed_sources" in value:
        validate_exact_string_set(
            f"{label}.consumed_sources",
            value["consumed_sources"],
            RUN2_79_RENDERER_ART_DIRECTION_REPAIR_CONSUMED_SOURCE_PATHS,
            errors,
        )
    if value.get("best_internal_arm") != "run2_79_full_renderer_art_direction_repair":
        errors.append(f"{label}.best_internal_arm must be run2_79_full_renderer_art_direction_repair")
    outputs = value.get("outputs", {})
    if require_non_empty_dict(f"{label}.outputs", outputs, errors):
        for key in ["html_viewer", "pptx", "ppt_run_viewer"]:
            if key not in outputs:
                errors.append(f"{label}.outputs missing key: {key}")
            else:
                require_non_empty_string(f"{label}.outputs.{key}", outputs[key], errors)
    viewer_update = value.get("viewer_update", {})
    if require_non_empty_dict(f"{label}.viewer_update", viewer_update, errors):
        if viewer_update.get("latest_run_id") != "2.79":
            errors.append(f"{label}.viewer_update.latest_run_id must be 2.79")
        if viewer_update.get("viewer_can_reference_new_run") is not True:
            errors.append(f"{label}.viewer_update.viewer_can_reference_new_run must be true")


def validate_run2_79_rendered_pages(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    art_direction_scenes: set[str] = set()
    for index, page in enumerate(value):
        page_label = f"{label}[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{page_label} must be an object")
            continue
        require_keys(
            page_label,
            page,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "art_direction_scene",
                "source_run2_77_page",
                "source_l_repair_instruction",
                "renderer_repair_directives_applied",
                "debug_annotation_count",
                "wireframe_dependency",
                "dominant_product_object_scale",
                "min_visible_label_font_size",
                "label_count",
                "source_trace_terms_visible_on_canvas",
                "public_polish_claimed",
            ],
            errors,
        )
        role = page.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in page and require_integer(f"{page_label}.slide_index", page["slide_index"], errors):
            if page["slide_index"] != index + 1:
                errors.append(f"{page_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if page.get("visual_grammar_module") != expected_module:
                errors.append(f"{page_label}.visual_grammar_module must be {expected_module} for {role}")
        scene = page.get("art_direction_scene")
        if require_non_empty_string(f"{page_label}.art_direction_scene", scene, errors):
            if scene in art_direction_scenes:
                errors.append(f"{page_label}.art_direction_scene duplicates {scene}")
            art_direction_scenes.add(scene)
        source_page = page.get("source_run2_77_page", {})
        if require_non_empty_dict(f"{page_label}.source_run2_77_page", source_page, errors):
            if "target_scene_direction" in source_page:
                require_non_empty_string(f"{page_label}.source_run2_77_page.target_scene_direction", source_page["target_scene_direction"], errors)
            else:
                errors.append(f"{page_label}.source_run2_77_page missing key: target_scene_direction")
        if "source_l_repair_instruction" in page:
            require_non_empty_string(f"{page_label}.source_l_repair_instruction", page["source_l_repair_instruction"], errors)
        if "renderer_repair_directives_applied" in page:
            validate_exact_string_set(
                f"{page_label}.renderer_repair_directives_applied",
                page["renderer_repair_directives_applied"],
                RUN2_79_RENDERER_ART_DIRECTION_REPAIR_DIRECTIVES,
                errors,
            )
        if "debug_annotation_count" in page and require_integer(f"{page_label}.debug_annotation_count", page["debug_annotation_count"], errors):
            if page["debug_annotation_count"] != 0:
                errors.append(f"{page_label}.debug_annotation_count must be 0")
        if "wireframe_dependency" in page and page["wireframe_dependency"] not in {"reduced", "minimal"}:
            errors.append(f"{page_label}.wireframe_dependency must be reduced or minimal")
        if "dominant_product_object_scale" in page and page["dominant_product_object_scale"] not in {"large", "hero", "full_frame"}:
            errors.append(f"{page_label}.dominant_product_object_scale must be large, hero, or full_frame")
        if "min_visible_label_font_size" in page and require_integer(f"{page_label}.min_visible_label_font_size", page["min_visible_label_font_size"], errors):
            if page["min_visible_label_font_size"] < 12:
                errors.append(f"{page_label}.min_visible_label_font_size must be at least 12")
        if "label_count" in page and require_integer(f"{page_label}.label_count", page["label_count"], errors):
            if page["label_count"] > 3:
                errors.append(f"{page_label}.label_count must be at most 3")
        if "source_trace_terms_visible_on_canvas" in page:
            visible = page["source_trace_terms_visible_on_canvas"]
            if not isinstance(visible, list):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be a list")
            elif visible:
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be empty")
        if page.get("public_polish_claimed") is not False:
            errors.append(f"{page_label}.public_polish_claimed must be false")
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if len(art_direction_scenes) != 6:
        errors.append(f"{label}.art_direction_scene values must be unique across six pages")


def validate_run2_79_repair_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key, expected in RUN2_79_RENDERER_ART_DIRECTION_REPAIR_REQUIRED_CHECKS.items():
        if key not in value:
            errors.append(f"{label} missing key: {key}")
            continue
        if require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")
    if value.get("public_quality_verdict_started") is not False:
        errors.append(f"{label}.public_quality_verdict_started must be false")


def validate_run2_80_visual_quality_evaluation(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_80_visual_quality_evaluation.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_80_visual_quality_evaluation"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "updates_html_viewer",
            "public_release_started",
            "public_ready",
            "quality_claim_boundary",
            "source_runs",
            "input_chain",
            "viewer_comparison_closure",
            "gemini_agent_review_summary",
            "evaluation_questions",
            "visual_quality_assessment",
            "role_assessments",
            "root_cause_summary",
            "no_new_renderer_proof",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part N":
        errors.append(f"{label}.part must be Part N")
    if data.get("run_id") != "2.80":
        errors.append(f"{label}.run_id must be 2.80")
    if data.get("status") != RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS}")
    if data.get("creates_new_ppt_deck") is not False:
        errors.append(f"{label}.creates_new_ppt_deck must be false")
    if data.get("starts_renderer_rerun") is not False:
        errors.append(f"{label}.starts_renderer_rerun must be false")
    if data.get("updates_html_viewer") is not False:
        errors.append(f"{label}.updates_html_viewer must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("quality_claim_boundary") != "part_n_evaluation_only_no_public_release_no_renderer_rerun":
        errors.append(f"{label}.quality_claim_boundary must be part_n_evaluation_only_no_public_release_no_renderer_rerun")
    validate_run2_80_visual_quality_source_runs(f"{label}.source_runs", data.get("source_runs", {}), errors)
    validate_run2_80_visual_quality_input_chain(f"{label}.input_chain", data.get("input_chain", {}), errors)
    validate_run2_80_visual_quality_viewer_closure(
        f"{label}.viewer_comparison_closure",
        data.get("viewer_comparison_closure", {}),
        errors,
    )
    validate_run2_80_gemini_summary(
        f"{label}.gemini_agent_review_summary",
        data.get("gemini_agent_review_summary", {}),
        errors,
    )
    validate_run2_80_visual_quality_questions(
        f"{label}.evaluation_questions",
        data.get("evaluation_questions", {}),
        errors,
    )
    validate_run2_80_visual_quality_assessment(
        f"{label}.visual_quality_assessment",
        data.get("visual_quality_assessment", {}),
        errors,
    )
    validate_run2_80_visual_quality_role_assessments(
        f"{label}.role_assessments",
        data.get("role_assessments", []),
        errors,
    )
    validate_run2_80_visual_quality_root_cause_summary(
        f"{label}.root_cause_summary",
        data.get("root_cause_summary", {}),
        errors,
    )
    validate_run2_80_no_new_renderer_proof(
        f"{label}.no_new_renderer_proof",
        data.get("no_new_renderer_proof", {}),
        errors,
    )
    if data.get("next_required_action") != "part_o_renderer_product_surface_repair_from_n_evaluation":
        errors.append(f"{label}.next_required_action must be part_o_renderer_product_surface_repair_from_n_evaluation")


def validate_run2_80_visual_quality_source_runs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["comparison_baseline", "evaluated_run", "prior_reference_run"], errors)
    if value.get("comparison_baseline") != "2.77":
        errors.append(f"{label}.comparison_baseline must be 2.77")
    if value.get("evaluated_run") != "2.79":
        errors.append(f"{label}.evaluated_run must be 2.79")
    if value.get("prior_reference_run") != "2.75":
        errors.append(f"{label}.prior_reference_run must be 2.75")


def validate_run2_80_visual_quality_input_chain(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    required = [
        "run2_79_result",
        "run2_78_l_evaluation",
        "run2_77_result",
        "run2_77_full_contact_sheet",
        "run2_79_full_contact_sheet",
        "ppt_run_viewer",
    ]
    require_keys(label, value, required, errors)
    for key in required:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_80_visual_quality_viewer_closure(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "viewer_latest_run_id",
            "viewer_can_compare_2_77_and_2_79",
            "run2_77_full_preview_count",
            "run2_79_full_preview_count",
            "browser_check_required_for_handoff",
        ],
        errors,
    )
    if value.get("viewer_latest_run_id") != "2.79":
        errors.append(f"{label}.viewer_latest_run_id must be 2.79")
    if value.get("viewer_can_compare_2_77_and_2_79") is not True:
        errors.append(f"{label}.viewer_can_compare_2_77_and_2_79 must be true")
    for key in ["run2_77_full_preview_count", "run2_79_full_preview_count"]:
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] != 6:
            errors.append(f"{label}.{key} must be 6")
    if value.get("browser_check_required_for_handoff") is not True:
        errors.append(f"{label}.browser_check_required_for_handoff must be true")


def validate_run2_80_gemini_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["tool", "model", "review_count", "used_for_verdict", "run2_79_findings", "run2_79_risks"], errors)
    if value.get("tool") != "mcp__gemini_agent.gemini_artifact_review":
        errors.append(f"{label}.tool must be mcp__gemini_agent.gemini_artifact_review")
    if value.get("model") != "gemini-3.5-flash":
        errors.append(f"{label}.model must be gemini-3.5-flash")
    if "review_count" in value and require_integer(f"{label}.review_count", value["review_count"], errors) and value["review_count"] != 1:
        errors.append(f"{label}.review_count must be 1")
    if value.get("used_for_verdict") is not True:
        errors.append(f"{label}.used_for_verdict must be true")
    if "run2_79_findings" in value:
        validate_string_list(f"{label}.run2_79_findings", value["run2_79_findings"], errors)
    if "run2_79_risks" in value:
        validate_string_list(f"{label}.run2_79_risks", value["run2_79_risks"], errors)


def validate_run2_80_visual_quality_questions(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for question_id in sorted(RUN2_80_VISUAL_QUALITY_QUESTION_IDS):
        if question_id not in value:
            errors.append(f"{label} missing key: {question_id}")
            continue
        question = value[question_id]
        question_label = f"{label}.{question_id}"
        if not require_non_empty_dict(question_label, question, errors):
            continue
        require_keys(question_label, question, ["answer"], errors)
        if "answer" in question:
            require_non_empty_string(f"{question_label}.answer", question["answer"], errors)
    for question_id, expected in RUN2_80_VISUAL_QUALITY_EXPECTED_ANSWERS.items():
        question = value.get(question_id)
        if isinstance(question, dict) and question.get("answer") != expected:
            errors.append(f"{label}.{question_id}.answer must be {expected}")


def validate_run2_80_visual_quality_assessment(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    expected_values = {
        "data_workflow_entry_gate": "pass_internal_only",
        "viewer_comparison_gate": "pass_internal_only",
        "design_quality_gate": "blocked",
        "public_video_readiness": "blocked",
        "global_delta_vs_2_77": "debug_annotations_down_but_product_surface_absent_and_small_labels_remain",
        "top_blocker": "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes",
        "next_layer_to_fix": "renderer_product_surface_realization",
    }
    require_keys(label, value, list(expected_values), errors)
    for key, expected in expected_values.items():
        if value.get(key) != expected:
            errors.append(f"{label}.{key} must be {expected}")


def validate_run2_80_visual_quality_role_assessments(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    repair_count = 0
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(
            record_label,
            record,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "delta_vs_2_77",
                "wireframe_reduction",
                "label_hierarchy",
                "product_surface_realization",
                "public_video_direction",
                "root_cause_layer",
                "repair_required",
                "next_repair_instruction",
                "trace_support",
            ],
            errors,
        )
        role = record.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in record and require_integer(f"{record_label}.slide_index", record["slide_index"], errors):
            if record["slide_index"] != index + 1:
                errors.append(f"{record_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if record.get("visual_grammar_module") != expected_module:
                errors.append(f"{record_label}.visual_grammar_module must be {expected_module} for {role}")
        if "delta_vs_2_77" in record:
            validate_choice(f"{record_label}.delta_vs_2_77", record["delta_vs_2_77"], RUN2_80_DELTA_VALUES, errors)
        if "wireframe_reduction" in record:
            validate_choice(f"{record_label}.wireframe_reduction", record["wireframe_reduction"], RUN2_78_WIREFRAME_REDUCTION_VALUES, errors)
        if "label_hierarchy" in record:
            validate_choice(f"{record_label}.label_hierarchy", record["label_hierarchy"], RUN2_78_LABEL_HIERARCHY_VALUES, errors)
        if "product_surface_realization" in record:
            validate_choice(
                f"{record_label}.product_surface_realization",
                record["product_surface_realization"],
                RUN2_80_PRODUCT_SURFACE_REALIZATION_VALUES,
                errors,
            )
        if "public_video_direction" in record:
            validate_choice(f"{record_label}.public_video_direction", record["public_video_direction"], RUN2_76_PUBLIC_VIDEO_DIRECTION_VALUES, errors)
        if "root_cause_layer" in record:
            validate_choice(
                f"{record_label}.root_cause_layer",
                record["root_cause_layer"],
                RUN2_74_VISUAL_QUALITY_ROOT_CAUSE_LAYERS,
                errors,
            )
        if record.get("repair_required") is not True:
            errors.append(f"{record_label}.repair_required must be true")
        else:
            repair_count += 1
        if "next_repair_instruction" in record:
            require_non_empty_string(f"{record_label}.next_repair_instruction", record["next_repair_instruction"], errors)
        trace = record.get("trace_support", {})
        if require_non_empty_dict(f"{record_label}.trace_support", trace, errors):
            if "art_direction_scene" in trace:
                require_non_empty_string(f"{record_label}.trace_support.art_direction_scene", trace["art_direction_scene"], errors)
            else:
                errors.append(f"{record_label}.trace_support missing key: art_direction_scene")
            if "label_count" in trace and require_integer(f"{record_label}.trace_support.label_count", trace["label_count"], errors):
                if trace["label_count"] > 3:
                    errors.append(f"{record_label}.trace_support.label_count must be at most 3")
            elif "label_count" not in trace:
                errors.append(f"{record_label}.trace_support missing key: label_count")
            if "debug_annotation_count" in trace and require_integer(f"{record_label}.trace_support.debug_annotation_count", trace["debug_annotation_count"], errors):
                if trace["debug_annotation_count"] != 0:
                    errors.append(f"{record_label}.trace_support.debug_annotation_count must be 0")
            elif "debug_annotation_count" not in trace:
                errors.append(f"{record_label}.trace_support missing key: debug_annotation_count")
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")
    if repair_count != 6:
        errors.append(f"{label} must mark all six pages repair_required")


def validate_run2_80_visual_quality_root_cause_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["primary_layer", "not_primary_layer"], errors)
    if value.get("primary_layer") != "renderer_product_surface_realization":
        errors.append(f"{label}.primary_layer must be renderer_product_surface_realization")
    if value.get("not_primary_layer") != "data_absence":
        errors.append(f"{label}.not_primary_layer must be data_absence")
    secondary = value.get("secondary_layers")
    if secondary is not None:
        validate_string_list(f"{label}.secondary_layers", secondary, errors)


def validate_run2_80_no_new_renderer_proof(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key in ["new_pptx_created", "new_html_created", "starts_renderer_rerun"]:
        if key not in value:
            errors.append(f"{label} missing key: {key}")
        elif value.get(key) is not False:
            errors.append(f"{label}.{key} must be false")
    if value.get("status") != "pass":
        errors.append(f"{label}.status must be pass")


def validate_run2_81_text_composition_typography_plan(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "run2_81_text_composition_typography_plan.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_81_text_composition_typography_plan"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "stage_policy",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "updates_html_viewer",
            "public_release_started",
            "public_ready",
            "consumed_sources",
            "source_inputs",
            "source_n_evaluation",
            "global_text_composition_contract",
            "page_text_composition_records",
            "traceability_summary",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part O1":
        errors.append(f"{label}.part must be Part O1")
    if data.get("run_id") != "2.81":
        errors.append(f"{label}.run_id must be 2.81")
    if data.get("status") != RUN2_81_TEXT_COMPOSITION_TYPOGRAPHY_PLAN_STATUS:
        errors.append(f"{label}.status must be {RUN2_81_TEXT_COMPOSITION_TYPOGRAPHY_PLAN_STATUS}")
    if data.get("stage_policy") != "part_o1_text_composition_typography_plan_only_no_renderer_rerun_no_public_release":
        errors.append(
            f"{label}.stage_policy must be part_o1_text_composition_typography_plan_only_no_renderer_rerun_no_public_release"
        )
    for key in ["creates_new_ppt_deck", "starts_renderer_rerun", "updates_html_viewer", "public_release_started", "public_ready"]:
        if data.get(key) is not False:
            errors.append(f"{label}.{key} must be false")
    validate_exact_string_set(
        f"{label}.consumed_sources",
        data.get("consumed_sources", []),
        RUN2_81_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_run2_81_source_inputs(f"{label}.source_inputs", data.get("source_inputs", []), errors)
    validate_run2_81_source_n_evaluation(f"{label}.source_n_evaluation", data.get("source_n_evaluation", {}), errors)
    validate_run2_81_global_text_contract(
        f"{label}.global_text_composition_contract",
        data.get("global_text_composition_contract", {}),
        errors,
    )
    validate_run2_81_page_text_composition_records(
        f"{label}.page_text_composition_records",
        data.get("page_text_composition_records", []),
        errors,
    )
    validate_run2_81_traceability_summary(
        f"{label}.traceability_summary",
        data.get("traceability_summary", {}),
        errors,
    )
    if data.get("next_required_action") != "part_o2_renderer_rerun_from_text_composition_and_product_surface_repair":
        errors.append(
            f"{label}.next_required_action must be part_o2_renderer_rerun_from_text_composition_and_product_surface_repair"
        )


def validate_run2_81_source_inputs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    paths: list[str] = []
    for index, source in enumerate(value):
        source_label = f"{label}[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{source_label} must be an object")
            continue
        require_keys(source_label, source, ["path", "available"], errors)
        path = source.get("path")
        if require_non_empty_string(f"{source_label}.path", path, errors):
            paths.append(path)
        if source.get("available") is not True:
            errors.append(f"{source_label}.available must be true")
    for path in sorted(RUN2_81_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS - set(paths)):
        errors.append(f"{label} missing path: {path}")


def validate_run2_81_source_n_evaluation(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "top_blocker", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS}")
    if value.get("top_blocker") != "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes":
        errors.append(f"{label}.top_blocker must match Run 2.80 visual quality top blocker")
    if value.get("next_required_action") != "part_o_renderer_product_surface_repair_from_n_evaluation":
        errors.append(f"{label}.next_required_action must be part_o_renderer_product_surface_repair_from_n_evaluation")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json":
        errors.append(f"{label}.source_result must reference run2_80_visual_quality_evaluation.json")


def validate_run2_81_global_text_contract(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "required_canvas_text_blocks",
            "global_forbidden_patterns",
            "traceability_default_route",
            "slide_canvas_traceability_allowed",
            "minimum_main_text_region_count",
        ],
        errors,
    )
    validate_exact_string_set(
        f"{label}.required_canvas_text_blocks",
        value.get("required_canvas_text_blocks", []),
        RUN2_81_REQUIRED_TEXT_BLOCKS,
        errors,
    )
    validate_exact_string_set(
        f"{label}.global_forbidden_patterns",
        value.get("global_forbidden_patterns", []),
        RUN2_81_FORBIDDEN_PATTERNS,
        errors,
    )
    if value.get("traceability_default_route") != "viewer_metadata_and_speaker_notes":
        errors.append(f"{label}.traceability_default_route must be viewer_metadata_and_speaker_notes")
    if value.get("slide_canvas_traceability_allowed") is not False:
        errors.append(f"{label}.slide_canvas_traceability_allowed must be false")
    if "minimum_main_text_region_count" in value and require_integer(
        f"{label}.minimum_main_text_region_count",
        value["minimum_main_text_region_count"],
        errors,
    ):
        if value["minimum_main_text_region_count"] < 1:
            errors.append(f"{label}.minimum_main_text_region_count must be at least 1")


def validate_run2_81_page_text_composition_records(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(
            record_label,
            record,
            [
                "text_composition_id",
                "role",
                "slide_index",
                "visual_grammar_module",
                "source_text_binding_id",
                "source_n_role_assessment",
                "headline_block",
                "subhead_block",
                "proof_sentence",
                "object_caption",
                "label_policy",
                "viewer_note_route",
                "forbidden_patterns",
                "renderer_constraints",
            ],
            errors,
        )
        role = record.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in record and require_integer(f"{record_label}.slide_index", record["slide_index"], errors):
            if record["slide_index"] != index + 1:
                errors.append(f"{record_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if record.get("visual_grammar_module") != expected_module:
                errors.append(f"{record_label}.visual_grammar_module must be {expected_module} for {role}")
            if record.get("text_composition_id") != f"text_composition_2_81_{role}":
                errors.append(f"{record_label}.text_composition_id must be text_composition_2_81_{role}")
            if record.get("source_text_binding_id") != f"text_binding_2_73_{role}":
                errors.append(f"{record_label}.source_text_binding_id must be text_binding_2_73_{role}")
        source_n = record.get("source_n_role_assessment", {})
        if require_non_empty_dict(f"{record_label}.source_n_role_assessment", source_n, errors):
            if source_n.get("repair_required") is not True:
                errors.append(f"{record_label}.source_n_role_assessment.repair_required must be true")
            if "next_repair_instruction" in source_n:
                require_non_empty_string(
                    f"{record_label}.source_n_role_assessment.next_repair_instruction",
                    source_n["next_repair_instruction"],
                    errors,
                )
            else:
                errors.append(f"{record_label}.source_n_role_assessment missing key: next_repair_instruction")
        for block_name in sorted(RUN2_81_REQUIRED_TEXT_BLOCKS):
            validate_run2_81_text_block(f"{record_label}.{block_name}", record.get(block_name, {}), errors)
        validate_run2_81_label_policy(f"{record_label}.label_policy", record.get("label_policy", {}), errors)
        validate_run2_81_viewer_note_route(f"{record_label}.viewer_note_route", record.get("viewer_note_route", {}), errors)
        validate_exact_string_set(
            f"{record_label}.forbidden_patterns",
            record.get("forbidden_patterns", []),
            RUN2_81_FORBIDDEN_PATTERNS,
            errors,
        )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")


def validate_run2_81_text_block(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "text_role",
            "copy_intent",
            "bound_visual_object_type",
            "object_anchor_required",
            "capacity",
            "typography",
            "canvas_route",
        ],
        errors,
    )
    if "copy_intent" in value:
        require_non_empty_string(f"{label}.copy_intent", value["copy_intent"], errors)
    if "bound_visual_object_type" in value:
        validate_choice(
            f"{label}.bound_visual_object_type",
            value["bound_visual_object_type"],
            RUN2_81_BOUND_VISUAL_OBJECT_TYPES,
            errors,
        )
    if value.get("object_anchor_required") is not True:
        errors.append(f"{label}.object_anchor_required must be true")
    capacity = value.get("capacity", {})
    if require_non_empty_dict(f"{label}.capacity", capacity, errors):
        for key in ["max_words", "max_lines"]:
            if key not in capacity:
                errors.append(f"{label}.capacity missing key: {key}")
            elif require_integer(f"{label}.capacity.{key}", capacity[key], errors) and capacity[key] <= 0:
                errors.append(f"{label}.capacity.{key} must be greater than 0")
    typography = value.get("typography", {})
    if require_non_empty_dict(f"{label}.typography", typography, errors):
        if "min_font_size" not in typography:
            errors.append(f"{label}.typography missing key: min_font_size")
        elif require_integer(f"{label}.typography.min_font_size", typography["min_font_size"], errors) and typography["min_font_size"] < 12:
            errors.append(f"{label}.typography.min_font_size must be at least 12")
    if value.get("canvas_route") != "slide_canvas":
        errors.append(f"{label}.canvas_route must be slide_canvas")


def validate_run2_81_label_policy(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        ["max_visible_labels", "min_font_size", "must_attach_to_visible_object", "floating_labels_allowed", "overflow_route"],
        errors,
    )
    if "max_visible_labels" in value and require_integer(f"{label}.max_visible_labels", value["max_visible_labels"], errors):
        if value["max_visible_labels"] > 3:
            errors.append(f"{label}.max_visible_labels must be at most 3")
    if "min_font_size" in value and require_integer(f"{label}.min_font_size", value["min_font_size"], errors):
        if value["min_font_size"] < 12:
            errors.append(f"{label}.min_font_size must be at least 12")
    if value.get("must_attach_to_visible_object") is not True:
        errors.append(f"{label}.must_attach_to_visible_object must be true")
    if value.get("floating_labels_allowed") is not False:
        errors.append(f"{label}.floating_labels_allowed must be false")
    if value.get("overflow_route") != "viewer_metadata_and_speaker_notes":
        errors.append(f"{label}.overflow_route must be viewer_metadata_and_speaker_notes")


def validate_run2_81_viewer_note_route(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["target", "traceability_on_canvas", "speaker_note_allowed"], errors)
    if value.get("target") != "viewer_metadata_and_speaker_notes":
        errors.append(f"{label}.target must be viewer_metadata_and_speaker_notes")
    if value.get("traceability_on_canvas") is not False:
        errors.append(f"{label}.traceability_on_canvas must be false")
    if value.get("speaker_note_allowed") is not True:
        errors.append(f"{label}.speaker_note_allowed must be true")


def validate_run2_81_traceability_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["page_text_composition_record_count", "source_input_count", "renderer_rerun_started"], errors)
    expected_ints = {
        "page_text_composition_record_count": 6,
        "source_input_count": len(RUN2_81_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS),
    }
    for key, expected in expected_ints.items():
        if key in value and require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")
    if value.get("renderer_rerun_started") is not False:
        errors.append(f"{label}.renderer_rerun_started must be false")


def validate_run2_82_renderer_product_surface_text_composition_rerun_result(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_82_renderer_product_surface_text_composition_rerun_result.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_82_renderer_product_surface_text_composition_rerun_result"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "public_ready",
            "public_release_started",
            "quality_claim_boundary",
            "consumed_sources",
            "source_n_evaluation",
            "source_o1_text_composition_plan",
            "renderer_product_surface_text_composition_manifest",
            "rendered_pages",
            "renderer_product_surface_text_composition_checks",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part O2":
        errors.append(f"{label}.part must be Part O2")
    if data.get("run_id") != "2.82":
        errors.append(f"{label}.run_id must be 2.82")
    if data.get("status") != RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_STATUS:
        errors.append(f"{label}.status must be {RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_STATUS}")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("quality_claim_boundary") != "renderer_product_surface_text_composition_generated_viewer_check_only_no_part_p_quality_verdict":
        errors.append(
            f"{label}.quality_claim_boundary must be renderer_product_surface_text_composition_generated_viewer_check_only_no_part_p_quality_verdict"
        )
    validate_exact_string_set(
        f"{label}.consumed_sources",
        data.get("consumed_sources", []),
        RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_run2_82_source_n_evaluation(f"{label}.source_n_evaluation", data.get("source_n_evaluation", {}), errors)
    validate_run2_82_source_o1_plan(
        f"{label}.source_o1_text_composition_plan",
        data.get("source_o1_text_composition_plan", {}),
        errors,
    )
    validate_run2_82_manifest(
        f"{label}.renderer_product_surface_text_composition_manifest",
        data.get("renderer_product_surface_text_composition_manifest", {}),
        errors,
    )
    validate_run2_82_rendered_pages(f"{label}.rendered_pages", data.get("rendered_pages", []), errors)
    validate_run2_82_checks(
        f"{label}.renderer_product_surface_text_composition_checks",
        data.get("renderer_product_surface_text_composition_checks", {}),
        errors,
    )
    if data.get("next_required_action") != "part_p_visual_quality_evaluation_for_run2_82":
        errors.append(f"{label}.next_required_action must be part_p_visual_quality_evaluation_for_run2_82")


def validate_run2_82_source_n_evaluation(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "top_blocker", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS:
        errors.append(f"{label}.status must be {RUN2_80_VISUAL_QUALITY_EVALUATION_STATUS}")
    if value.get("top_blocker") != "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes":
        errors.append(f"{label}.top_blocker must match Run 2.80 visual quality top blocker")
    if value.get("next_required_action") != "part_o_renderer_product_surface_repair_from_n_evaluation":
        errors.append(f"{label}.next_required_action must be part_o_renderer_product_surface_repair_from_n_evaluation")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json":
        errors.append(f"{label}.source_result must reference run2_80_visual_quality_evaluation.json")


def validate_run2_82_source_o1_plan(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_81_TEXT_COMPOSITION_TYPOGRAPHY_PLAN_STATUS:
        errors.append(f"{label}.status must be {RUN2_81_TEXT_COMPOSITION_TYPOGRAPHY_PLAN_STATUS}")
    if value.get("next_required_action") != "part_o2_renderer_rerun_from_text_composition_and_product_surface_repair":
        errors.append(f"{label}.next_required_action must be part_o2_renderer_rerun_from_text_composition_and_product_surface_repair")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json":
        errors.append(f"{label}.source_result must reference run2_81_text_composition_typography_plan.json")


def validate_run2_82_manifest(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["generator", "consumed_sources", "arms", "best_internal_arm", "outputs", "viewer_update"], errors)
    if value.get("generator") != "scripts/generate_ppt_run2_82_product_surface_text_composition_arms.mjs":
        errors.append(f"{label}.generator must be scripts/generate_ppt_run2_82_product_surface_text_composition_arms.mjs")
    validate_exact_string_set(
        f"{label}.consumed_sources",
        value.get("consumed_sources", []),
        RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_exact_string_set(
        f"{label}.arms",
        value.get("arms", []),
        {"prompt_only", "run1_5_skill", "run2_82_full_product_surface_text_composition", "bad_run2_82_without_text_composition"},
        errors,
    )
    if value.get("best_internal_arm") != "run2_82_full_product_surface_text_composition":
        errors.append(f"{label}.best_internal_arm must be run2_82_full_product_surface_text_composition")
    outputs = value.get("outputs", {})
    if require_non_empty_dict(f"{label}.outputs", outputs, errors):
        for key in ["html_viewer", "pptx", "ppt_run_viewer"]:
            if key not in outputs:
                errors.append(f"{label}.outputs missing key: {key}")
            else:
                require_non_empty_string(f"{label}.outputs.{key}", outputs[key], errors)
    viewer_update = value.get("viewer_update", {})
    if require_non_empty_dict(f"{label}.viewer_update", viewer_update, errors):
        if viewer_update.get("latest_run_id") != "2.82":
            errors.append(f"{label}.viewer_update.latest_run_id must be 2.82")
        if viewer_update.get("viewer_can_reference_new_run") is not True:
            errors.append(f"{label}.viewer_update.viewer_can_reference_new_run must be true")


def validate_run2_82_rendered_pages(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    for index, page in enumerate(value):
        page_label = f"{label}[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{page_label} must be an object")
            continue
        require_keys(
            page_label,
            page,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "source_o1_text_composition_id",
                "source_n_repair_instruction",
                "source_run2_79_page",
                "renderer_repair_directives_applied",
                "concrete_product_surface_visible",
                "product_surface_type",
                "text_hierarchy",
                "text_composition_blocks_applied",
                "floating_label_count",
                "label_count",
                "min_visible_label_font_size",
                "canvas_word_count",
                "source_trace_terms_visible_on_canvas",
                "public_polish_claimed",
            ],
            errors,
        )
        role = page.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in page and require_integer(f"{page_label}.slide_index", page["slide_index"], errors):
            if page["slide_index"] != index + 1:
                errors.append(f"{page_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if page.get("visual_grammar_module") != expected_module:
                errors.append(f"{page_label}.visual_grammar_module must be {expected_module} for {role}")
            if page.get("source_o1_text_composition_id") != f"text_composition_2_81_{role}":
                errors.append(f"{page_label}.source_o1_text_composition_id must be text_composition_2_81_{role}")
        if "source_n_repair_instruction" in page:
            require_non_empty_string(f"{page_label}.source_n_repair_instruction", page["source_n_repair_instruction"], errors)
        source_279 = page.get("source_run2_79_page", {})
        if require_non_empty_dict(f"{page_label}.source_run2_79_page", source_279, errors):
            if "art_direction_scene" in source_279:
                require_non_empty_string(f"{page_label}.source_run2_79_page.art_direction_scene", source_279["art_direction_scene"], errors)
            else:
                errors.append(f"{page_label}.source_run2_79_page missing key: art_direction_scene")
        validate_exact_string_set(
            f"{page_label}.renderer_repair_directives_applied",
            page.get("renderer_repair_directives_applied", []),
            RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_DIRECTIVES,
            errors,
        )
        if page.get("concrete_product_surface_visible") is not True:
            errors.append(f"{page_label}.concrete_product_surface_visible must be true")
        if "product_surface_type" in page:
            validate_choice(f"{page_label}.product_surface_type", page["product_surface_type"], RUN2_82_PRODUCT_SURFACE_TYPES, errors)
        if page.get("text_hierarchy") != "headline_subhead_proof_caption":
            errors.append(f"{page_label}.text_hierarchy must be headline_subhead_proof_caption")
        validate_exact_string_set(
            f"{page_label}.text_composition_blocks_applied",
            page.get("text_composition_blocks_applied", []),
            RUN2_81_REQUIRED_TEXT_BLOCKS,
            errors,
        )
        if "floating_label_count" in page and require_integer(f"{page_label}.floating_label_count", page["floating_label_count"], errors):
            if page["floating_label_count"] != 0:
                errors.append(f"{page_label}.floating_label_count must be 0")
        if "label_count" in page and require_integer(f"{page_label}.label_count", page["label_count"], errors):
            if page["label_count"] > 3:
                errors.append(f"{page_label}.label_count must be at most 3")
        if "min_visible_label_font_size" in page and require_integer(f"{page_label}.min_visible_label_font_size", page["min_visible_label_font_size"], errors):
            if page["min_visible_label_font_size"] < 12:
                errors.append(f"{page_label}.min_visible_label_font_size must be at least 12")
        if "canvas_word_count" in page and require_integer(f"{page_label}.canvas_word_count", page["canvas_word_count"], errors):
            if page["canvas_word_count"] < 24:
                errors.append(f"{page_label}.canvas_word_count must be at least 24")
        if "source_trace_terms_visible_on_canvas" in page:
            visible = page["source_trace_terms_visible_on_canvas"]
            if not isinstance(visible, list):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be a list")
            elif visible:
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be empty")
        if page.get("public_polish_claimed") is not False:
            errors.append(f"{page_label}.public_polish_claimed must be false")
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")


def validate_run2_82_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key, expected in RUN2_82_TEXT_COMPOSITION_REQUIRED_CHECKS.items():
        if key not in value:
            errors.append(f"{label} missing key: {key}")
            continue
        if require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")
    if value.get("public_quality_verdict_started") is not False:
        errors.append(f"{label}.public_quality_verdict_started must be false")


def validate_run2_83_workflow_taxonomy_bias_audit(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_83_workflow_taxonomy_bias_audit.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_83_workflow_taxonomy_bias_audit"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "stage_policy",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "updates_html_viewer",
            "public_release_started",
            "public_ready",
            "quality_claim_boundary",
            "consumed_sources",
            "source_inputs",
            "engineering_rigor_preservation",
            "taxonomy_bias_summary",
            "layer_bias_records",
            "run2_series_pattern",
            "missing_design_taxonomy",
            "required_next_layer",
            "no_new_renderer_proof",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part P0":
        errors.append(f"{label}.part must be Part P0")
    if data.get("run_id") != "2.83":
        errors.append(f"{label}.run_id must be 2.83")
    if data.get("status") != RUN2_83_WORKFLOW_TAXONOMY_BIAS_AUDIT_STATUS:
        errors.append(f"{label}.status must be {RUN2_83_WORKFLOW_TAXONOMY_BIAS_AUDIT_STATUS}")
    if data.get("stage_policy") != "part_p0_audit_only_no_renderer_rerun_no_viewer_update_no_public_release":
        errors.append(
            f"{label}.stage_policy must be part_p0_audit_only_no_renderer_rerun_no_viewer_update_no_public_release"
        )
    for key in [
        "creates_new_ppt_deck",
        "starts_renderer_rerun",
        "updates_html_viewer",
        "public_release_started",
        "public_ready",
    ]:
        if data.get(key) is not False:
            errors.append(f"{label}.{key} must be false")
    if data.get("quality_claim_boundary") != "workflow_taxonomy_bias_audit_only_no_visual_quality_pass_no_public_release":
        errors.append(
            f"{label}.quality_claim_boundary must be workflow_taxonomy_bias_audit_only_no_visual_quality_pass_no_public_release"
        )
    validate_exact_string_set(
        f"{label}.consumed_sources",
        data.get("consumed_sources", []),
        RUN2_83_WORKFLOW_TAXONOMY_BIAS_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_run2_83_source_inputs(f"{label}.source_inputs", data.get("source_inputs", []), errors)
    validate_run2_83_engineering_rigor_preservation(
        f"{label}.engineering_rigor_preservation",
        data.get("engineering_rigor_preservation", {}),
        errors,
    )
    validate_run2_83_taxonomy_bias_summary(
        f"{label}.taxonomy_bias_summary",
        data.get("taxonomy_bias_summary", {}),
        errors,
    )
    validate_run2_83_layer_bias_records(f"{label}.layer_bias_records", data.get("layer_bias_records", []), errors)
    validate_run2_83_series_pattern(f"{label}.run2_series_pattern", data.get("run2_series_pattern", []), errors)
    validate_run2_83_missing_design_taxonomy(
        f"{label}.missing_design_taxonomy",
        data.get("missing_design_taxonomy", []),
        errors,
    )
    validate_run2_83_required_next_layer(f"{label}.required_next_layer", data.get("required_next_layer", {}), errors)
    validate_run2_83_no_new_renderer_proof(f"{label}.no_new_renderer_proof", data.get("no_new_renderer_proof", {}), errors)
    if data.get("next_required_action") != "part_p1_design_motif_taxonomy_and_style_router_plan":
        errors.append(f"{label}.next_required_action must be part_p1_design_motif_taxonomy_and_style_router_plan")


def validate_run2_83_source_inputs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    paths: list[str] = []
    for index, source in enumerate(value):
        source_label = f"{label}[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{source_label} must be an object")
            continue
        require_keys(source_label, source, ["path", "available", "usage"], errors)
        path = source.get("path")
        if require_non_empty_string(f"{source_label}.path", path, errors):
            paths.append(path)
        if source.get("available") is not True:
            errors.append(f"{source_label}.available must be true")
        if "usage" in source:
            require_non_empty_string(f"{source_label}.usage", source["usage"], errors)
    for path in sorted(RUN2_83_WORKFLOW_TAXONOMY_BIAS_CONSUMED_SOURCE_PATHS - set(paths)):
        errors.append(f"{label} missing path: {path}")


def validate_run2_83_engineering_rigor_preservation(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "preserve_existing_gates",
            "do_not_weaken_traceability",
            "public_release_gate_remains_blocked",
            "design_layer_adds_to_engineering_layer",
        ],
        errors,
    )
    validate_exact_string_set(
        f"{label}.preserve_existing_gates",
        value.get("preserve_existing_gates", []),
        RUN2_83_ENGINEERING_GATES_TO_PRESERVE,
        errors,
    )
    for key in [
        "do_not_weaken_traceability",
        "public_release_gate_remains_blocked",
        "design_layer_adds_to_engineering_layer",
    ]:
        if value.get(key) is not True:
            errors.append(f"{label}.{key} must be true")


def validate_run2_83_taxonomy_bias_summary(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["primary_bias", "root_cause", "required_correction"], errors)
    if value.get("primary_bias") != "engineering_constraint_labels_over_design_motif_labels":
        errors.append(f"{label}.primary_bias must be engineering_constraint_labels_over_design_motif_labels")
    if value.get("root_cause") != "design_motif_taxonomy_missing_between_tutorial_memory_and_renderer_adapter":
        errors.append(f"{label}.root_cause must be design_motif_taxonomy_missing_between_tutorial_memory_and_renderer_adapter")
    correction = value.get("required_correction")
    if require_non_empty_string(f"{label}.required_correction", correction, errors) and "design_motif_layer" not in correction:
        errors.append(f"{label}.required_correction must mention design_motif_layer")


def validate_run2_83_layer_bias_records(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    layer_ids: list[str] = []
    for index, record in enumerate(value):
        record_label = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_keys(
            record_label,
            record,
            [
                "layer_id",
                "layer_name",
                "engineering_strength",
                "design_signal_loss",
                "bias_direction",
                "evidence",
                "impact_on_ppt",
                "must_preserve",
                "needs_new_design_layer",
            ],
            errors,
        )
        layer_id = record.get("layer_id")
        if require_non_empty_string(f"{record_label}.layer_id", layer_id, errors):
            layer_ids.append(layer_id)
        for key in ["layer_name", "engineering_strength", "design_signal_loss", "impact_on_ppt", "must_preserve"]:
            if key in record:
                require_non_empty_string(f"{record_label}.{key}", record[key], errors)
        if "bias_direction" in record:
            validate_choice(f"{record_label}.bias_direction", record["bias_direction"], RUN2_83_LAYER_BIAS_DIRECTIONS, errors)
        if "evidence" in record:
            validate_string_list(f"{record_label}.evidence", record["evidence"], errors)
        if record.get("needs_new_design_layer") is not True:
            errors.append(f"{record_label}.needs_new_design_layer must be true")
    actual = set(layer_ids)
    for layer_id in sorted(RUN2_83_LAYER_BIAS_IDS - actual):
        errors.append(f"{label} missing layer_id: {layer_id}")
    for layer_id in sorted(actual - RUN2_83_LAYER_BIAS_IDS):
        errors.append(f"{label} has unexpected layer_id: {layer_id}")


def validate_run2_83_series_pattern(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    stage_ranges: list[str] = []
    for index, stage in enumerate(value):
        stage_label = f"{label}[{index}]"
        if not isinstance(stage, dict):
            errors.append(f"{stage_label} must be an object")
            continue
        require_keys(stage_label, stage, ["stage_range", "dominant_work", "effect_on_ppt"], errors)
        stage_range = stage.get("stage_range")
        if require_non_empty_string(f"{stage_label}.stage_range", stage_range, errors):
            stage_ranges.append(stage_range)
        for key in ["dominant_work", "effect_on_ppt"]:
            if key in stage:
                require_non_empty_string(f"{stage_label}.{key}", stage[key], errors)
    if stage_ranges != RUN2_83_SERIES_STAGE_RANGES:
        errors.append(f"{label} stage_range values must be {', '.join(RUN2_83_SERIES_STAGE_RANGES)}")


def validate_run2_83_missing_design_taxonomy(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    fields: list[str] = []
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_label} must be an object")
            continue
        require_keys(item_label, item, ["field", "why_needed", "renderer_contract_implication"], errors)
        field = item.get("field")
        if require_non_empty_string(f"{item_label}.field", field, errors):
            fields.append(field)
        for key in ["why_needed", "renderer_contract_implication"]:
            if key in item:
                require_non_empty_string(f"{item_label}.{key}", item[key], errors)
    actual = set(fields)
    for field in sorted(RUN2_83_MISSING_DESIGN_TAXONOMY_FIELDS - actual):
        errors.append(f"{label} missing field: {field}")
    for field in sorted(actual - RUN2_83_MISSING_DESIGN_TAXONOMY_FIELDS):
        errors.append(f"{label} has unexpected field: {field}")


def validate_run2_83_required_next_layer(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        ["layer_id", "must_add_fields", "must_preserve_engineering_gates", "must_not_replace_validator"],
        errors,
    )
    if value.get("layer_id") != "design_motif_layer":
        errors.append(f"{label}.layer_id must be design_motif_layer")
    validate_exact_string_set(
        f"{label}.must_add_fields",
        value.get("must_add_fields", []),
        RUN2_83_MISSING_DESIGN_TAXONOMY_FIELDS,
        errors,
    )
    for key in ["must_preserve_engineering_gates", "must_not_replace_validator"]:
        if value.get(key) is not True:
            errors.append(f"{label}.{key} must be true")


def validate_run2_83_no_new_renderer_proof(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key in ["new_ppt_created", "new_html_created", "viewer_updated"]:
        if key not in value:
            errors.append(f"{label} missing key: {key}")
        elif value.get(key) is not False:
            errors.append(f"{label}.{key} must be false")


def validate_run2_84_design_motif_taxonomy_style_router_plan(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "run2_84_design_motif_taxonomy_style_router_plan.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_84_design_motif_taxonomy_style_router_plan"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "stage_policy",
            "creates_new_ppt_deck",
            "starts_renderer_rerun",
            "updates_html_viewer",
            "public_release_started",
            "public_ready",
            "quality_claim_boundary",
            "consumed_sources",
            "source_inputs",
            "source_p0_audit",
            "preserved_visual_effects",
            "design_motif_taxonomy",
            "style_router_rules",
            "page_role_motif_bindings",
            "engineering_gate_bridge",
            "renderer_contract_preview",
            "no_new_renderer_proof",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part P1":
        errors.append(f"{label}.part must be Part P1")
    if data.get("run_id") != "2.84":
        errors.append(f"{label}.run_id must be 2.84")
    if data.get("status") != RUN2_84_DESIGN_MOTIF_TAXONOMY_STYLE_ROUTER_STATUS:
        errors.append(f"{label}.status must be {RUN2_84_DESIGN_MOTIF_TAXONOMY_STYLE_ROUTER_STATUS}")
    if data.get("stage_policy") != "part_p1_design_motif_taxonomy_and_style_router_plan_only_no_renderer_rerun_no_public_release":
        errors.append(
            f"{label}.stage_policy must be part_p1_design_motif_taxonomy_and_style_router_plan_only_no_renderer_rerun_no_public_release"
        )
    for key in [
        "creates_new_ppt_deck",
        "starts_renderer_rerun",
        "updates_html_viewer",
        "public_release_started",
        "public_ready",
    ]:
        if data.get(key) is not False:
            errors.append(f"{label}.{key} must be false")
    if data.get("quality_claim_boundary") != "design_motif_contract_only_no_visual_quality_verdict_no_public_release":
        errors.append(f"{label}.quality_claim_boundary must be design_motif_contract_only_no_visual_quality_verdict_no_public_release")
    validate_exact_string_set(
        f"{label}.consumed_sources",
        data.get("consumed_sources", []),
        RUN2_84_DESIGN_MOTIF_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_run2_84_source_inputs(f"{label}.source_inputs", data.get("source_inputs", []), errors)
    validate_run2_84_source_p0_audit(f"{label}.source_p0_audit", data.get("source_p0_audit", {}), errors)
    validate_exact_string_set(
        f"{label}.preserved_visual_effects",
        data.get("preserved_visual_effects", []),
        RUN2_84_PRESERVED_VISUAL_EFFECTS,
        errors,
    )
    motif_ids = validate_run2_84_design_motif_taxonomy(
        f"{label}.design_motif_taxonomy",
        data.get("design_motif_taxonomy", []),
        errors,
    )
    validate_run2_84_style_router_rules(f"{label}.style_router_rules", data.get("style_router_rules", []), errors)
    validate_run2_84_page_role_motif_bindings(
        f"{label}.page_role_motif_bindings",
        data.get("page_role_motif_bindings", []),
        motif_ids,
        errors,
    )
    validate_run2_84_engineering_gate_bridge(
        f"{label}.engineering_gate_bridge",
        data.get("engineering_gate_bridge", {}),
        errors,
    )
    validate_run2_84_renderer_contract_preview(
        f"{label}.renderer_contract_preview",
        data.get("renderer_contract_preview", {}),
        errors,
    )
    validate_run2_83_no_new_renderer_proof(f"{label}.no_new_renderer_proof", data.get("no_new_renderer_proof", {}), errors)
    if data.get("next_required_action") != "part_p2_renderer_rerun_from_design_motif_layer_and_style_router":
        errors.append(f"{label}.next_required_action must be part_p2_renderer_rerun_from_design_motif_layer_and_style_router")


def validate_run2_84_source_inputs(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    paths: list[str] = []
    for index, source in enumerate(value):
        source_label = f"{label}[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{source_label} must be an object")
            continue
        require_keys(source_label, source, ["path", "available", "usage"], errors)
        path = source.get("path")
        if require_non_empty_string(f"{source_label}.path", path, errors):
            paths.append(path)
        if source.get("available") is not True:
            errors.append(f"{source_label}.available must be true")
        if "usage" in source:
            require_non_empty_string(f"{source_label}.usage", source["usage"], errors)
    for path in sorted(RUN2_84_DESIGN_MOTIF_CONSUMED_SOURCE_PATHS - set(paths)):
        errors.append(f"{label} missing path: {path}")


def validate_run2_84_source_p0_audit(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_83_WORKFLOW_TAXONOMY_BIAS_AUDIT_STATUS:
        errors.append(f"{label}.status must be {RUN2_83_WORKFLOW_TAXONOMY_BIAS_AUDIT_STATUS}")
    if value.get("next_required_action") != "part_p1_design_motif_taxonomy_and_style_router_plan":
        errors.append(f"{label}.next_required_action must be part_p1_design_motif_taxonomy_and_style_router_plan")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/results/run2_83_workflow_taxonomy_bias_audit.json":
        errors.append(f"{label}.source_result must reference run2_83_workflow_taxonomy_bias_audit.json")


def validate_run2_84_design_motif_taxonomy(label: str, value: Any, errors: list[str]) -> set[str]:
    if not require_non_empty_list(label, value, errors):
        return set()
    motif_ids: set[str] = set()
    motif_families: set[str] = set()
    for index, motif in enumerate(value):
        motif_label = f"{label}[{index}]"
        if not isinstance(motif, dict):
            errors.append(f"{motif_label} must be an object")
            continue
        require_keys(motif_label, motif, sorted(RUN2_83_MISSING_DESIGN_TAXONOMY_FIELDS) + ["source_trace"], errors)
        motif_id = motif.get("motif_id")
        if require_non_empty_string(f"{motif_label}.motif_id", motif_id, errors):
            motif_ids.add(motif_id)
            if not motif_id.startswith("motif_2_84_"):
                errors.append(f"{motif_label}.motif_id must start with motif_2_84_")
        motif_family = motif.get("motif_family")
        if validate_choice(f"{motif_label}.motif_family", motif_family, RUN2_84_DESIGN_MOTIF_FAMILIES, errors):
            motif_families.add(motif_family)
        if "style_family" in motif:
            validate_choice(f"{motif_label}.style_family", motif["style_family"], RUN2_84_STYLE_FAMILIES, errors)
        if "visual_density" in motif:
            validate_choice(f"{motif_label}.visual_density", motif["visual_density"], RUN2_84_VISUAL_DENSITIES, errors)
        if "scenario_fit" in motif:
            validate_run2_84_scenario_list(f"{motif_label}.scenario_fit", motif["scenario_fit"], errors)
        validate_run2_84_layout_recipe(f"{motif_label}.layout_recipe", motif.get("layout_recipe", {}), errors)
        validate_run2_84_spatial_relation(f"{motif_label}.spatial_relation", motif.get("spatial_relation", {}), errors)
        validate_run2_84_typography_treatment(f"{motif_label}.typography_treatment", motif.get("typography_treatment", {}), errors)
        validate_run2_84_renderer_recipe(f"{motif_label}.renderer_recipe", motif.get("renderer_recipe", {}), errors)
        validate_exact_string_set(
            f"{motif_label}.motif_fidelity_checks",
            motif.get("motif_fidelity_checks", []),
            RUN2_84_REQUIRED_MOTIF_FIDELITY_CHECKS,
            errors,
        )
        if "source_trace" in motif:
            validate_string_list(f"{motif_label}.source_trace", motif["source_trace"], errors)
    for motif_family in sorted(RUN2_84_DESIGN_MOTIF_FAMILIES - motif_families):
        errors.append(f"{label} missing motif_family: {motif_family}")
    return motif_ids


def validate_run2_84_scenario_list(label: str, value: Any, errors: list[str]) -> None:
    if not validate_string_list(label, value, errors):
        return
    for index, item in enumerate(value):
        if item not in RUN2_84_SCENARIOS:
            errors.append(f"{label}[{index}] must be one of {', '.join(sorted(RUN2_84_SCENARIOS))}")


def validate_run2_84_layout_recipe(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["composition_pattern", "reading_path", "focal_object_strategy"], errors)
    for key in ["composition_pattern", "reading_path", "focal_object_strategy"]:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_84_spatial_relation(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["text_to_object_relation", "object_to_background_relation", "evidence_relation"], errors)
    for key in ["text_to_object_relation", "object_to_background_relation", "evidence_relation"]:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_84_typography_treatment(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["hierarchy_model", "paragraph_behavior", "caption_behavior"], errors)
    for key in ["hierarchy_model", "paragraph_behavior", "caption_behavior"]:
        if key in value:
            require_non_empty_string(f"{label}.{key}", value[key], errors)


def validate_run2_84_renderer_recipe(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["native_ppt_primitives", "forbidden_renderer_shortcuts", "metadata_routes"], errors)
    if "native_ppt_primitives" in value:
        validate_string_list(f"{label}.native_ppt_primitives", value["native_ppt_primitives"], errors)
    validate_exact_string_set(
        f"{label}.forbidden_renderer_shortcuts",
        value.get("forbidden_renderer_shortcuts", []),
        RUN2_84_FORBIDDEN_RENDERER_SHORTCUTS,
        errors,
    )
    if "metadata_routes" in value:
        validate_string_list(f"{label}.metadata_routes", value["metadata_routes"], errors)


def validate_run2_84_style_router_rules(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    scenarios: set[str] = set()
    for index, rule in enumerate(value):
        rule_label = f"{label}[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{rule_label} must be an object")
            continue
        require_keys(
            rule_label,
            rule,
            ["scenario", "primary_style_family", "allowed_motif_families", "density_policy", "business_fit_rationale"],
            errors,
        )
        scenario = rule.get("scenario")
        if validate_choice(f"{rule_label}.scenario", scenario, RUN2_84_SCENARIOS, errors):
            scenarios.add(scenario)
        if "primary_style_family" in rule:
            validate_choice(f"{rule_label}.primary_style_family", rule["primary_style_family"], RUN2_84_STYLE_FAMILIES, errors)
        if "allowed_motif_families" in rule and validate_string_list(
            f"{rule_label}.allowed_motif_families",
            rule["allowed_motif_families"],
            errors,
        ):
            for family_index, family in enumerate(rule["allowed_motif_families"]):
                if family not in RUN2_84_DESIGN_MOTIF_FAMILIES:
                    errors.append(f"{rule_label}.allowed_motif_families[{family_index}] must be one of {', '.join(sorted(RUN2_84_DESIGN_MOTIF_FAMILIES))}")
        for key in ["density_policy", "business_fit_rationale"]:
            if key in rule:
                require_non_empty_string(f"{rule_label}.{key}", rule[key], errors)
    for scenario in sorted(RUN2_84_SCENARIOS - scenarios):
        errors.append(f"{label} missing scenario: {scenario}")


def validate_run2_84_page_role_motif_bindings(
    label: str,
    value: Any,
    motif_ids: set[str],
    errors: list[str],
) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    for index, binding in enumerate(value):
        binding_label = f"{label}[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{binding_label} must be an object")
            continue
        require_keys(
            binding_label,
            binding,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "primary_motif_id",
                "fallback_motif_id",
                "style_family",
                "scenario",
                "required_motif_fidelity_checks",
            ],
            errors,
        )
        role = binding.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in binding and require_integer(f"{binding_label}.slide_index", binding["slide_index"], errors):
            if binding["slide_index"] != index + 1:
                errors.append(f"{binding_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if binding.get("visual_grammar_module") != expected_module:
                errors.append(f"{binding_label}.visual_grammar_module must be {expected_module} for {role}")
        for key in ["primary_motif_id", "fallback_motif_id"]:
            motif_id = binding.get(key)
            if require_non_empty_string(f"{binding_label}.{key}", motif_id, errors) and motif_id not in motif_ids:
                errors.append(f"{binding_label}.{key} references unknown motif: {motif_id}")
        if "style_family" in binding:
            validate_choice(f"{binding_label}.style_family", binding["style_family"], RUN2_84_STYLE_FAMILIES, errors)
        if "scenario" in binding:
            validate_choice(f"{binding_label}.scenario", binding["scenario"], RUN2_84_SCENARIOS, errors)
        validate_exact_string_set(
            f"{binding_label}.required_motif_fidelity_checks",
            binding.get("required_motif_fidelity_checks", []),
            RUN2_84_REQUIRED_MOTIF_FIDELITY_CHECKS,
            errors,
        )
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")


def validate_run2_84_engineering_gate_bridge(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(
        label,
        value,
        [
            "preserve_existing_gates",
            "traceability_route",
            "slide_canvas_traceability_allowed",
            "public_release_gate_remains_blocked",
            "validator_remains_authoritative",
        ],
        errors,
    )
    validate_exact_string_set(
        f"{label}.preserve_existing_gates",
        value.get("preserve_existing_gates", []),
        RUN2_83_ENGINEERING_GATES_TO_PRESERVE,
        errors,
    )
    if value.get("traceability_route") != "viewer_metadata_and_speaker_notes":
        errors.append(f"{label}.traceability_route must be viewer_metadata_and_speaker_notes")
    if value.get("slide_canvas_traceability_allowed") is not False:
        errors.append(f"{label}.slide_canvas_traceability_allowed must be false")
    if value.get("public_release_gate_remains_blocked") is not True:
        errors.append(f"{label}.public_release_gate_remains_blocked must be true")
    if value.get("validator_remains_authoritative") is not True:
        errors.append(f"{label}.validator_remains_authoritative must be true")


def validate_run2_84_renderer_contract_preview(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["next_renderer_must_consume_p1", "required_fields_for_next_rerun", "does_not_execute_renderer"], errors)
    if value.get("next_renderer_must_consume_p1") is not True:
        errors.append(f"{label}.next_renderer_must_consume_p1 must be true")
    validate_exact_string_set(
        f"{label}.required_fields_for_next_rerun",
        value.get("required_fields_for_next_rerun", []),
        RUN2_83_MISSING_DESIGN_TAXONOMY_FIELDS,
        errors,
    )
    if value.get("does_not_execute_renderer") is not True:
        errors.append(f"{label}.does_not_execute_renderer must be true")


def validate_run2_85_design_motif_renderer_rerun_result(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "results" / "run2_85_design_motif_renderer_rerun_result.json", errors)
    if not isinstance(data, dict):
        return
    label = "run2_85_design_motif_renderer_rerun_result"
    require_keys(
        label,
        data,
        [
            "artifact_id",
            "part",
            "run_id",
            "status",
            "public_ready",
            "public_release_started",
            "quality_claim_boundary",
            "consumed_sources",
            "source_p1_design_motif_plan",
            "source_o2_renderer_result",
            "renderer_design_motif_manifest",
            "rendered_pages",
            "renderer_design_motif_checks",
            "next_required_action",
        ],
        errors,
    )
    if data.get("artifact_id") != label:
        errors.append(f"{label}.artifact_id must be {label}")
    if data.get("part") != "Part P2":
        errors.append(f"{label}.part must be Part P2")
    if data.get("run_id") != "2.85":
        errors.append(f"{label}.run_id must be 2.85")
    if data.get("status") != RUN2_85_DESIGN_MOTIF_RENDERER_RERUN_STATUS:
        errors.append(f"{label}.status must be {RUN2_85_DESIGN_MOTIF_RENDERER_RERUN_STATUS}")
    if data.get("public_ready") is not False:
        errors.append(f"{label}.public_ready must be false")
    if data.get("public_release_started") is not False:
        errors.append(f"{label}.public_release_started must be false")
    if data.get("quality_claim_boundary") != "design_motif_renderer_generated_viewer_check_only_no_part_q_quality_verdict":
        errors.append(
            f"{label}.quality_claim_boundary must be design_motif_renderer_generated_viewer_check_only_no_part_q_quality_verdict"
        )
    validate_exact_string_set(
        f"{label}.consumed_sources",
        data.get("consumed_sources", []),
        RUN2_85_DESIGN_MOTIF_RENDERER_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_run2_85_source_p1_plan(f"{label}.source_p1_design_motif_plan", data.get("source_p1_design_motif_plan", {}), errors)
    validate_run2_85_source_o2_result(f"{label}.source_o2_renderer_result", data.get("source_o2_renderer_result", {}), errors)
    validate_run2_85_manifest(
        f"{label}.renderer_design_motif_manifest",
        data.get("renderer_design_motif_manifest", {}),
        errors,
    )
    validate_run2_85_rendered_pages(f"{label}.rendered_pages", data.get("rendered_pages", []), errors)
    validate_run2_85_checks(f"{label}.renderer_design_motif_checks", data.get("renderer_design_motif_checks", {}), errors)
    if data.get("next_required_action") != "part_q_visual_quality_evaluation_for_run2_85":
        errors.append(f"{label}.next_required_action must be part_q_visual_quality_evaluation_for_run2_85")


def validate_run2_85_source_p1_plan(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_84_DESIGN_MOTIF_TAXONOMY_STYLE_ROUTER_STATUS:
        errors.append(f"{label}.status must be {RUN2_84_DESIGN_MOTIF_TAXONOMY_STYLE_ROUTER_STATUS}")
    if value.get("next_required_action") != "part_p2_renderer_rerun_from_design_motif_layer_and_style_router":
        errors.append(f"{label}.next_required_action must be part_p2_renderer_rerun_from_design_motif_layer_and_style_router")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json":
        errors.append(f"{label}.source_result must reference run2_84_design_motif_taxonomy_style_router_plan.json")


def validate_run2_85_source_o2_result(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["status", "next_required_action", "source_result"], errors)
    if value.get("status") != RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_STATUS:
        errors.append(f"{label}.status must be {RUN2_82_RENDERER_PRODUCT_SURFACE_TEXT_COMPOSITION_STATUS}")
    if value.get("next_required_action") != "part_p_visual_quality_evaluation_for_run2_82":
        errors.append(f"{label}.next_required_action must be part_p_visual_quality_evaluation_for_run2_82")
    if value.get("source_result") != "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json":
        errors.append(f"{label}.source_result must reference run2_82_renderer_product_surface_text_composition_rerun_result.json")


def validate_run2_85_manifest(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    require_keys(label, value, ["generator", "consumed_sources", "arms", "best_internal_arm", "outputs", "viewer_update"], errors)
    if value.get("generator") != "scripts/generate_ppt_run2_85_design_motif_renderer_arms.mjs":
        errors.append(f"{label}.generator must be scripts/generate_ppt_run2_85_design_motif_renderer_arms.mjs")
    validate_exact_string_set(
        f"{label}.consumed_sources",
        value.get("consumed_sources", []),
        RUN2_85_DESIGN_MOTIF_RENDERER_CONSUMED_SOURCE_PATHS,
        errors,
    )
    validate_exact_string_set(f"{label}.arms", value.get("arms", []), RUN2_85_DESIGN_MOTIF_RENDERER_ARMS, errors)
    if value.get("best_internal_arm") != "run2_85_full_design_motif_style_router":
        errors.append(f"{label}.best_internal_arm must be run2_85_full_design_motif_style_router")
    outputs = value.get("outputs", {})
    if require_non_empty_dict(f"{label}.outputs", outputs, errors):
        for key in ["html_viewer", "pptx", "ppt_run_viewer", "four_arm_contact_sheet"]:
            if key not in outputs:
                errors.append(f"{label}.outputs missing key: {key}")
            else:
                require_non_empty_string(f"{label}.outputs.{key}", outputs[key], errors)
    viewer_update = value.get("viewer_update", {})
    if require_non_empty_dict(f"{label}.viewer_update", viewer_update, errors):
        if viewer_update.get("latest_run_id") != "2.85":
            errors.append(f"{label}.viewer_update.latest_run_id must be 2.85")
        if viewer_update.get("viewer_can_reference_new_run") is not True:
            errors.append(f"{label}.viewer_update.viewer_can_reference_new_run must be true")


def validate_run2_85_rendered_pages(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_list(label, value, errors):
        return
    roles: list[str] = []
    for index, page in enumerate(value):
        page_label = f"{label}[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{page_label} must be an object")
            continue
        require_keys(
            page_label,
            page,
            [
                "role",
                "slide_index",
                "visual_grammar_module",
                "source_p1_primary_motif_id",
                "source_p1_fallback_motif_id",
                "source_o2_product_surface_type",
                "motif_family",
                "style_family",
                "scenario",
                "visual_density",
                "renderer_repair_directives_applied",
                "preserved_visual_effects_rendered",
                "motif_fidelity_checks",
                "motif_family_visible",
                "not_rectangle_only",
                "text_integrated_with_shape",
                "concrete_product_surface_visible",
                "text_hierarchy",
                "floating_label_count",
                "label_count",
                "min_visible_label_font_size",
                "source_trace_terms_visible_on_canvas",
                "public_polish_claimed",
            ],
            errors,
        )
        role = page.get("role")
        if isinstance(role, str):
            roles.append(role)
        if "slide_index" in page and require_integer(f"{page_label}.slide_index", page["slide_index"], errors):
            if page["slide_index"] != index + 1:
                errors.append(f"{page_label}.slide_index must be {index + 1}")
        if role in RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP:
            expected_module = RUN2_73_VISUAL_GRAMMAR_PAGE_MODULE_MAP[role]
            if page.get("visual_grammar_module") != expected_module:
                errors.append(f"{page_label}.visual_grammar_module must be {expected_module} for {role}")
        for key in ["source_p1_primary_motif_id", "source_p1_fallback_motif_id"]:
            motif_id = page.get(key)
            if require_non_empty_string(f"{page_label}.{key}", motif_id, errors) and not motif_id.startswith("motif_2_84_"):
                errors.append(f"{page_label}.{key} must reference a motif_2_84_ id")
        if "source_o2_product_surface_type" in page:
            validate_choice(f"{page_label}.source_o2_product_surface_type", page["source_o2_product_surface_type"], RUN2_82_PRODUCT_SURFACE_TYPES, errors)
        if "motif_family" in page:
            validate_choice(f"{page_label}.motif_family", page["motif_family"], RUN2_84_DESIGN_MOTIF_FAMILIES, errors)
        if "style_family" in page:
            validate_choice(f"{page_label}.style_family", page["style_family"], RUN2_84_STYLE_FAMILIES, errors)
        if "scenario" in page:
            validate_choice(f"{page_label}.scenario", page["scenario"], RUN2_84_SCENARIOS, errors)
        if "visual_density" in page:
            validate_choice(f"{page_label}.visual_density", page["visual_density"], RUN2_84_VISUAL_DENSITIES, errors)
        validate_exact_string_set(
            f"{page_label}.renderer_repair_directives_applied",
            page.get("renderer_repair_directives_applied", []),
            RUN2_85_DESIGN_MOTIF_RENDERER_DIRECTIVES,
            errors,
        )
        validate_exact_string_set(
            f"{page_label}.preserved_visual_effects_rendered",
            page.get("preserved_visual_effects_rendered", []),
            RUN2_84_PRESERVED_VISUAL_EFFECTS,
            errors,
        )
        validate_exact_string_set(
            f"{page_label}.motif_fidelity_checks",
            page.get("motif_fidelity_checks", []),
            RUN2_84_REQUIRED_MOTIF_FIDELITY_CHECKS,
            errors,
        )
        for key in [
            "motif_family_visible",
            "not_rectangle_only",
            "text_integrated_with_shape",
            "concrete_product_surface_visible",
        ]:
            if page.get(key) is not True:
                errors.append(f"{page_label}.{key} must be true")
        if page.get("text_hierarchy") != "motif_aware_headline_subhead_proof_caption":
            errors.append(f"{page_label}.text_hierarchy must be motif_aware_headline_subhead_proof_caption")
        if "floating_label_count" in page and require_integer(f"{page_label}.floating_label_count", page["floating_label_count"], errors):
            if page["floating_label_count"] != 0:
                errors.append(f"{page_label}.floating_label_count must be 0")
        if "label_count" in page and require_integer(f"{page_label}.label_count", page["label_count"], errors):
            if page["label_count"] > 3:
                errors.append(f"{page_label}.label_count must be at most 3")
        if "min_visible_label_font_size" in page and require_integer(f"{page_label}.min_visible_label_font_size", page["min_visible_label_font_size"], errors):
            if page["min_visible_label_font_size"] < 12:
                errors.append(f"{page_label}.min_visible_label_font_size must be at least 12")
        if "source_trace_terms_visible_on_canvas" in page:
            visible = page["source_trace_terms_visible_on_canvas"]
            if not isinstance(visible, list):
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be a list")
            elif visible:
                errors.append(f"{page_label}.source_trace_terms_visible_on_canvas must be empty")
        if page.get("public_polish_claimed") is not False:
            errors.append(f"{page_label}.public_polish_claimed must be false")
    if roles != RUN2_73_VISUAL_GRAMMAR_ROLES:
        errors.append(f"{label} roles must be {', '.join(RUN2_73_VISUAL_GRAMMAR_ROLES)}")


def validate_run2_85_checks(label: str, value: Any, errors: list[str]) -> None:
    if not require_non_empty_dict(label, value, errors):
        return
    for key, expected in RUN2_85_DESIGN_MOTIF_REQUIRED_CHECKS.items():
        if key not in value:
            errors.append(f"{label} missing key: {key}")
            continue
        if require_integer(f"{label}.{key}", value[key], errors) and value[key] != expected:
            errors.append(f"{label}.{key} must be {expected}")
    if value.get("public_quality_verdict_started") is not False:
        errors.append(f"{label}.public_quality_verdict_started must be false")


def validate_run1_design_memory_observations(observations: list[Any], errors: list[str]) -> None:
    required = ["id", "source_ids", "principle", "code_generation_rule", "do_not_copy"]
    seen_ids: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"design_memory.observations[{index}] must be an object")
            continue
        require_keys(f"design_memory.observations[{index}]", observation, required, errors)
        for key in ["id", "principle", "code_generation_rule", "do_not_copy"]:
            if key in observation:
                require_non_empty_string(f"design_memory.observations[{index}].{key}", observation[key], errors)
        observation_id = observation.get("id")
        if isinstance(observation_id, str) and observation_id.strip():
            if observation_id in seen_ids:
                errors.append(f"design_memory.observations[{index}].id duplicates {observation_id}")
            seen_ids.add(observation_id)
        if "source_ids" in observation:
            validate_string_list(f"design_memory.observations[{index}].source_ids", observation["source_ids"], errors)


def validate_run1_5_design_memory_contract(data: dict[str, Any], errors: list[str]) -> None:
    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("design_memory.contract must be an object")
        return

    require_keys(
        "design_memory.contract",
        contract,
        ["required_fields", "allowed_source_roles", "allowed_slide_primitives"],
        errors,
    )
    if "required_fields" in contract:
        validate_exact_string_set(
            "design_memory.contract.required_fields",
            contract["required_fields"],
            set(RUN1_5_REQUIRED_MEMORY_FIELDS),
            errors,
        )
    if "allowed_source_roles" in contract:
        validate_exact_string_set(
            "design_memory.contract.allowed_source_roles",
            contract["allowed_source_roles"],
            RUN1_5_SOURCE_ROLES,
            errors,
        )
    if "allowed_slide_primitives" in contract:
        validate_exact_string_set(
            "design_memory.contract.allowed_slide_primitives",
            contract["allowed_slide_primitives"],
            RUN1_5_SLIDE_PRIMITIVES,
            errors,
        )


def validate_run1_5_design_memory_observations(observations: list[Any], errors: list[str]) -> None:
    required = [*RUN1_5_REQUIRED_MEMORY_FIELDS, "source_ids", "do_not_copy"]
    seen_ids: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"design_memory.observations[{index}] must be an object")
            continue
        require_keys(f"design_memory.observations[{index}]", observation, required, errors)
        for key in [*RUN1_5_REQUIRED_MEMORY_FIELDS, "do_not_copy"]:
            if key in observation and key not in {"source_role", "slide_primitive"}:
                require_non_empty_string(f"design_memory.observations[{index}].{key}", observation[key], errors)
        if "source_role" in observation:
            validate_choice(
                f"design_memory.observations[{index}].source_role",
                observation["source_role"],
                RUN1_5_SOURCE_ROLES,
                errors,
            )
        if "slide_primitive" in observation:
            validate_choice(
                f"design_memory.observations[{index}].slide_primitive",
                observation["slide_primitive"],
                RUN1_5_SLIDE_PRIMITIVES,
                errors,
            )
        evidence_id = observation.get("evidence_id")
        if isinstance(evidence_id, str) and evidence_id.strip():
            if evidence_id in seen_ids:
                errors.append(f"design_memory.observations[{index}].evidence_id duplicates {evidence_id}")
            seen_ids.add(evidence_id)
        if "source_ids" in observation:
            validate_string_list(f"design_memory.observations[{index}].source_ids", observation["source_ids"], errors)


def validate_design_memory(pack_dir: Path, errors: list[str], profile: str = "run1") -> None:
    data = load_json(pack_dir / "design_memory.json", errors)
    required_top_level = ["schema_version", "observations"]
    if profile == "run1_5":
        required_top_level.append("contract")
    require_keys("design_memory.json", data, required_top_level, errors)
    if "schema_version" in data:
        require_integer("design_memory.schema_version", data["schema_version"], errors)
    observations = data.get("observations", [])
    if not isinstance(observations, list) or not observations:
        errors.append("design_memory.observations must be a non-empty list")
        return

    if profile == "run1_5":
        validate_run1_5_design_memory_contract(data, errors)
        validate_run1_5_design_memory_observations(observations, errors)
    else:
        validate_run1_design_memory_observations(observations, errors)


def validate_markdown_not_empty(pack_dir: Path, errors: list[str], required_files: list[str]) -> None:
    for rel in required_files:
        if not rel.endswith(".md"):
            continue
        path = pack_dir / rel
        body = read_text_file(path, rel, errors)
        if body is not None and not body.strip():
            errors.append(f"{rel} must not be empty")


def validate_case_pack(pack_dir: str | Path, profile: str = "default") -> ValidationResult:
    root = Path(pack_dir)
    errors: list[str] = []
    try:
        required_files = required_files_for_profile(profile)
    except ValueError as exc:
        return ValidationResult(False, [str(exc)])
    if not root.exists():
        return ValidationResult(False, [f"case pack directory does not exist: {root}"])
    run2_8_enabled = profile == "run2"
    for rel in required_files:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif not path.is_file():
            errors.append(f"required path is not a file: {rel}")
    if errors:
        return ValidationResult(False, errors)

    validate_markdown_not_empty(root, errors, required_files)
    if profile == "run2":
        source_ids = validate_sources(root, errors)
        card_ids = collect_run2_card_ids(root, source_ids, errors)
        multimodal_record_ids, multimodal_anchor_ids = validate_run2_multimodal_database(root, source_ids, errors)
        visual_target_ids = validate_run2_visual_learning_targets(
            root,
            multimodal_record_ids,
            multimodal_anchor_ids,
            errors,
        )
        visual_component_ids = validate_run2_visual_target_components(root, visual_target_ids, errors)
        beat_ids = validate_run2_video_demo_beat_map(
            root,
            source_ids,
            multimodal_record_ids,
            multimodal_anchor_ids,
            card_ids,
            errors,
        )
        motion_target_ids = validate_run2_motion_learning_targets(
            root,
            beat_ids,
            visual_target_ids,
            visual_component_ids,
            errors,
        )
        validate_run2_presentation_sequence_components(root, motion_target_ids, visual_component_ids, errors)
        validate_run2_evidence_memory(root, card_ids, errors)
        move_ids = validate_run2_aesthetic_memory(root, card_ids, errors)
        validate_run2_asset_memory(root, card_ids, errors)
        validate_run2_narrative_spine(root, move_ids, errors)
        validate_run2_slide_archetypes(root, move_ids, errors)
        validate_run2_skill_workflow(root, errors)
        visual_repair_ids = validate_run2_visual_repair_policy(root, errors)
        run2_7_usecase_ids = validate_run2_7_commercial_usecase(root, errors)
        run2_7_source_record_ids = validate_run2_7_source_records(root, source_ids, errors)
        run2_7_memory_ids = validate_run2_7_design_memory(
            root,
            run2_7_source_record_ids,
            run2_7_usecase_ids,
            errors,
        )
        validate_run2_7_workflow_policy(
            root,
            run2_7_source_record_ids,
            run2_7_usecase_ids,
            run2_7_memory_ids,
            visual_repair_ids,
            errors,
        )
        if run2_8_enabled:
            trace_fields = validate_run2_8_trace_manifest_contract(root, errors)
            run2_8_decomposition_unit_ids = validate_run2_8_tutorial_decomposition(
                root,
                source_ids,
                run2_7_source_record_ids,
                errors,
            )
            run2_8_memory_binding_ids, run2_8_code_binding_ids = validate_run2_8_executable_design_memory(
                root,
                run2_8_decomposition_unit_ids,
                errors,
            )
            validate_run2_8_workflow_gate_matrix(
                root,
                run2_8_decomposition_unit_ids,
                run2_8_memory_binding_ids,
                run2_8_code_binding_ids,
                trace_fields,
                errors,
            )
            validate_run2_73_visual_grammar_modules(root, errors)
            validate_run2_73_renderer_adapter_contracts(root, errors)
            validate_run2_73_text_binding_strategy(root, errors)
            validate_run2_73_validated_scene_renderer_result(root, errors)
            validate_run2_74_visual_quality_evaluation(root, errors)
            validate_run2_75_renderer_repair_rerun_result(root, errors)
            validate_run2_76_visual_quality_evaluation(root, errors)
            validate_run2_76_visual_grammar_renderer_repair_plan(root, errors)
            validate_run2_77_visual_grammar_renderer_repair_rerun_result(root, errors)
            validate_run2_78_visual_quality_evaluation(root, errors)
            validate_run2_79_renderer_art_direction_repair_rerun_result(root, errors)
            validate_run2_80_visual_quality_evaluation(root, errors)
            validate_run2_81_text_composition_typography_plan(root, errors)
            validate_run2_82_renderer_product_surface_text_composition_rerun_result(root, errors)
            validate_run2_83_workflow_taxonomy_bias_audit(root, errors)
            validate_run2_84_design_motif_taxonomy_style_router_plan(root, errors)
            validate_run2_85_design_motif_renderer_rerun_result(root, errors)
        return ValidationResult(not errors, errors)

    validate_sources(root, errors)
    validate_narrative_rules(root, errors)
    validate_style_tokens(root, errors)
    validate_asset_rules(root, errors)
    pattern_ids = validate_slide_patterns(root, errors)
    validate_deck_outline(root, pattern_ids, errors)
    if profile in {"run1", "run1_5"}:
        validate_design_memory(root, errors, profile=profile)
    return ValidationResult(not errors, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Vulca PPT case pack.")
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--profile", choices=["default", "run1", "run1_5", "run2"], default="default")
    args = parser.parse_args()
    result = validate_case_pack(args.pack_dir, profile=args.profile)
    if result.ok:
        print(f"case pack ok: {args.pack_dir}")
        return 0
    for error in result.errors:
        print(f"error: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
