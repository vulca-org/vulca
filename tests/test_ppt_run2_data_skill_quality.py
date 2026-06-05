from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

from scripts.build_ppt_contact_sheet import build_contact_sheet
from scripts.build_ppt_run_html_viewer import build_data
from scripts.check_ppt_layout_quality import check_layout, write_report
from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
EXPECTED_ARMS = {"prompt_only", "run1_5_skill", "run2_skill", "bad_aesthetic_memory"}
EXPECTED_SOURCE_CARD_IDS = {
    "card_cinematic_cover",
    "card_low_density_claim",
    "card_big_object_layout",
    "card_editorial_comparison",
    "card_proof_reveal",
    "card_visual_climax",
    "card_premium_closing",
    "card_appendix_absorption",
}
EXPECTED_VIDEO_CARD_IDS = {
    "video_keynote_rhythm",
    "video_transition_pacing",
}
EXPECTED_MULTIMODAL_MODALITIES = {"text", "image_reference", "video", "audio", "transcript", "interaction"}
EXPECTED_MULTIMODAL_RECORD_IDS = {
    "mm_text_visual_hierarchy_tutorial",
    "mm_text_whitespace_tutorial",
    "mm_video_audio_keynote_rhythm",
    "mm_interaction_presentation_product_reference",
    "mm_case_public_keynote_reference",
    "mm_duarte_visual_storytelling_webinar",
    "mm_duarte_slide_design_course",
    "mm_udel_design_principles_video",
}
EXPECTED_VISUAL_TARGET_IDS = {
    "target_report_to_visual_delta",
    "target_slide_mini_preview",
    "target_audio_rhythm_budget",
    "target_transcript_headline_compression",
    "target_public_demo_climax",
}
EXPECTED_VISUAL_COMPONENT_IDS = {
    "component_before_after_thumbnail",
    "component_slide_mini_preview",
    "component_rhythm_budget_strip",
    "component_transcript_headline_route",
    "component_public_demo_climax_object",
}
EXPECTED_VIDEO_BEAT_IDS = {
    "beat_opening_scale_reset",
    "beat_before_after_transformation",
    "beat_proof_reveal_cadence",
    "beat_climax_scale_up",
    "beat_close_release_handoff",
}
EXPECTED_MOTION_TARGET_IDS = {
    "motion_target_opening_attention_reset",
    "motion_target_before_after_reveal",
    "motion_target_proof_build",
    "motion_target_climax_scale_emphasis",
    "motion_target_release_gate_handoff",
}
EXPECTED_SEQUENCE_COMPONENT_IDS = {
    "sequence_component_opening_reset",
    "sequence_component_before_after_reveal",
    "sequence_component_proof_build",
    "sequence_component_climax_scale",
    "sequence_component_release_gate",
}
EXPECTED_PRODUCTION_REFERENCE_IDS = {
    "prod_ref_cinematic_cover_field",
    "prod_ref_editorial_before_after_delta",
    "prod_ref_product_system_mini_preview",
    "prod_ref_climax_handoff_sequence",
}
EXPECTED_PRODUCTION_MODULE_IDS = {
    "module_cinematic_cover_field",
    "module_editorial_before_after_delta",
    "module_proof_route_choreography",
    "module_system_mini_preview",
    "module_climax_hero_object",
    "module_release_handoff_gate",
}
EXPECTED_AESTHETIC_V2_MOVE_IDS = {
    "aesthetic_v2_cinematic_cover_field",
    "aesthetic_v2_editorial_before_after_delta",
    "aesthetic_v2_proof_route_choreography",
    "aesthetic_v2_system_mini_preview",
    "aesthetic_v2_climax_hero_object",
    "aesthetic_v2_release_handoff_gate",
}
EXPECTED_PRODUCTION_REFERENCE_FIELDS = {
    "id",
    "source_ids",
    "visual_component_ids",
    "motion_target_ids",
    "sequence_component_ids",
    "visual_observations",
    "composition_primitives",
    "typography_primitives",
    "spacing_primitives",
    "motion_or_sequence_primitives",
    "module_implications",
    "extraction_notes",
    "do_not_copy",
    "qa_probe",
    "release_boundary",
}
EXPECTED_AESTHETIC_V2_FIELDS = {
    "id",
    "production_reference_ids",
    "visual_component_ids",
    "motion_target_ids",
    "sequence_component_ids",
    "slide_roles",
    "composition_contract",
    "typography_contract",
    "spacing_contract",
    "density_budget",
    "provenance_boundary",
    "code_generation_contract",
    "trace_fields",
    "forbidden_report_patterns",
    "qa_probe",
    "release_boundary",
}
EXPECTED_VISUAL_PRODUCTION_MODULE_FIELDS = {
    "id",
    "production_reference_ids",
    "aesthetic_memory_v2_ids",
    "slide_roles",
    "native_ppt_primitives",
    "layout_recipe",
    "typography_recipe",
    "spacing_recipe",
    "fallback_policy",
    "provenance_boundary",
    "trace_fields",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_6_SOURCE_IDS = {
    "figma_config_2025_platform_launch",
    "figma_config_2025_recap",
    "figma_slides_product",
    "figma_slides_help",
    "stripe_sessions_2025_product_keynote",
    "google_cloud_next_2025_wrap",
    "google_cloud_next_2025_sundar",
    "apple_liquid_glass_newsroom",
    "apple_liquid_glass_developer",
    "duarte_slide_design",
    "duarte_visual_storytelling",
    "slidemodel_visual_hierarchy",
}
EXPECTED_RUN2_6_USECASE_IDS = {
    "usecase_design_to_production_platform_launch",
    "usecase_fintech_product_keynote",
    "usecase_ai_cloud_keynote_demo",
    "usecase_design_language_public_reveal",
}
EXPECTED_RUN2_6_BENCHMARK_IDS = {
    "benchmark_design_to_production_grid_precision",
    "benchmark_visual_fidelity_interactive_slide_surface",
    "benchmark_fintech_product_keynote_breadth_without_grid",
    "benchmark_ai_platform_demo_climax",
    "benchmark_content_first_dynamic_material",
    "benchmark_glance_test_visual_hierarchy",
    "benchmark_story_driven_data_emphasis",
}
EXPECTED_RUN2_6_TRACE_FIELDS = {
    "commercial_usecase_id",
    "aesthetic_benchmark_ids",
    "theme_policy_id",
    "typography_system_id",
    "spacing_token_set_id",
    "workflow_decision_ids",
    "source_brand_sanitization",
    "benchmark_validation_probe",
    "theme_validation_probe",
}
EXPECTED_RUN2_6R_REPAIR_IDS = {
    "repair_editorial_typography_system",
    "repair_spacing_token_visibility",
    "repair_climax_editorial_spread",
    "repair_theme_differentiation_from_run2_5",
    "repair_mini_preview_fidelity",
}
EXPECTED_RUN2_6R_REPAIR_FIELDS = {
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
}
EXPECTED_RUN2_6R_TRACE_FIELDS = {
    "visual_repair_policy_ids",
    "visual_delta_from_run2_5",
    "visual_repair_validation_probe",
}
EXPECTED_RUN2_7_USECASE_IDS = {
    "usecase_ai_design_to_production_platform_launch",
}
EXPECTED_RUN2_7_SOURCE_RECORD_IDS = {
    "mm_2_7_design_system_launch_case",
    "mm_2_7_video_climax_single_object",
    "mm_2_7_typography_hierarchy_tutorial",
    "mm_2_7_spacing_editorial_grid_tutorial",
    "mm_2_7_motion_demo_pacing_reference",
    "mm_2_7_product_surface_interaction_reference",
}
EXPECTED_RUN2_7_MEMORY_IDS = {
    "memory_typography_editorial_launch",
    "memory_spacing_climax_proof_grid",
    "memory_composition_single_object_climax",
    "memory_rhythm_six_slide_launch",
    "memory_source_brand_sanitization_v2",
}
EXPECTED_RUN2_7_SOURCE_RECORD_FIELDS = {
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
}
EXPECTED_RUN2_7_MEMORY_FIELDS = {
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
}
EXPECTED_RUN2_7_TRACE_FIELDS = {
    "run2_7_usecase_id",
    "run2_7_source_record_ids",
    "run2_7_design_memory_ids",
    "run2_7_workflow_decision_ids",
    "run2_7_delta_from_run2_6r",
    "run2_7_quality_gate",
}
EXPECTED_RUN2_8_DECOMPOSITION_IDS = {
    "decomp_2_8_duarte_remove_nonessential_data",
    "decomp_2_8_type_hierarchy_readability_stack",
    "decomp_2_8_makeover_split_text_into_visual_steps",
    "decomp_2_8_design_first_code_second_pipeline",
    "decomp_2_8_climax_object_scale_and_pause",
    "decomp_2_8_source_brand_sanitized_case_evidence",
}
EXPECTED_RUN2_8_MEMORY_BINDING_IDS = {
    "binding_type_scale_readability",
    "binding_spacing_zone_grid",
    "binding_climax_hero_object",
    "binding_before_after_delta",
    "binding_public_gate_legibility",
}
EXPECTED_RUN2_8_TRACE_FIELDS = {
    "run2_8_decomposition_unit_ids",
    "run2_8_memory_binding_ids",
    "run2_8_gate_matrix_ids",
    "run2_8_code_binding_ids",
    "run2_8_layout_budget",
    "run2_8_visual_delta_from_run2_7",
}
EXPECTED_RUN2_9_VISUAL_PRIMITIVE_IDS = {
    "primitive_2_9_editorial_spread_composition",
    "primitive_2_9_product_surface_depth",
    "primitive_2_9_motion_storyboard_sequence",
    "primitive_2_9_climax_stage_composition",
    "primitive_2_9_typographic_field_composition",
}
EXPECTED_RUN2_9_VISUAL_MODULE_IDS = {
    "module_2_9_editorial_spread",
    "module_2_9_layered_product_surface",
    "module_2_9_motion_storyboard",
    "module_2_9_climax_stage",
    "module_2_9_typographic_field",
}
EXPECTED_RUN2_9_TRACE_FIELDS = {
    "run2_9_visual_primitive_ids",
    "run2_9_visual_module_ids",
    "run2_9_gate_matrix_ids",
    "run2_9_code_module_ids",
    "run2_9_boxiness_failure_probe",
    "run2_9_visual_delta_from_run2_8",
}
EXPECTED_RUN2_10_SOURCE_IDS = {
    "vs_source_2_10_editorial_keynote_system",
    "vs_source_2_10_product_theater_demo",
    "vs_source_2_10_typographic_launch_field",
    "vs_source_2_10_kinetic_climax_sequence",
    "vs_source_2_10_non_rectangular_proof_path",
}
EXPECTED_RUN2_10_MEMORY_IDS = {
    "visual_system_editorial_cinema",
    "visual_system_product_theater",
    "visual_system_typographic_field",
    "visual_system_kinetic_demo",
    "visual_system_non_rectangular_proof",
}
EXPECTED_RUN2_10_TRACE_FIELDS = {
    "run2_10_visual_system_source_ids",
    "run2_10_visual_system_memory_ids",
    "run2_10_gate_matrix_ids",
    "run2_10_code_module_ids",
    "run2_10_visual_delta_from_run2_9",
    "run2_10_sameness_failure_probe",
    "run2_10_public_demo_first_read_probe",
    "run2_10_shape_count_budget",
    "run2_10_asymmetry_whitespace_rule",
}
EXPECTED_RUN2_11_AUDIT_FIELDS = {
    "schema_version",
    "status",
    "stage_policy",
    "audit_scope",
    "source_inventory",
    "workflow_inventory",
    "chain_records",
    "arm_trace_evidence",
    "negative_control_checks",
    "gate_summary",
    "next_required_action",
}
EXPECTED_RUN2_11_CHAIN_STATUSES = {"pass", "weak", "missing", "blocked"}
EXPECTED_RUN2_11_RUN_IDS = {"2.8", "2.9", "2.10"}
EXPECTED_RUN2_11_CONTROL_ARMS = {
    "prompt_only",
    "run1_5_skill",
    "negative_control",
}
EXPECTED_RUN2_12_EVIDENCE_IDS = {
    "thick_2_12_figma_platform_launch_arc",
    "thick_2_12_figma_design_to_code_surface",
    "thick_2_12_stripe_agentic_commerce_demo",
    "thick_2_12_stripe_product_keynote_metric_reframe",
    "thick_2_12_present_partners_whitespace_hierarchy",
    "thick_2_12_slidecow_powerpoint_whitespace",
}
EXPECTED_RUN2_12_MEMORY_IDS = {
    "memory_2_12_launch_arc_to_six_slide_route",
    "memory_2_12_product_demo_sequence_pacing",
    "memory_2_12_typographic_whitespace_system",
    "memory_2_12_metric_to_climax_object",
}
EXPECTED_RUN2_12_GATE_IDS = {
    "gate_2_12_evidence_source_integrity",
    "gate_2_12_memory_selection_before_generation",
    "gate_2_12_visual_density_and_whitespace",
    "gate_2_12_demo_sequence_climax",
}
EXPECTED_RUN2_12_EVIDENCE_FIELDS = {
    "id",
    "source_ids",
    "source_urls",
    "verified_accessed_on",
    "source_role",
    "modality_mix",
    "segment_locator",
    "frame_or_visual_observations",
    "spoken_or_text_claim_paraphrases",
    "derived_design_method",
    "native_ppt_code_obligations",
    "workflow_gate_obligations",
    "memory_seed_targets",
    "anti_copy_boundary",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_12_MEMORY_FIELDS = {
    "id",
    "evidence_record_ids",
    "memory_type",
    "applies_to_slide_roles",
    "design_constraints",
    "native_ppt_contract",
    "required_trace_fields",
    "failure_probe",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_12_GATE_FIELDS = {
    "id",
    "gate_type",
    "evidence_record_ids",
    "memory_seed_ids",
    "slide_roles",
    "pass_fail_checks",
    "required_before_next_rerun",
    "trace_fields",
    "release_boundary",
}
EXPECTED_RUN2_13_TRACE_FIELDS = {
    "run2_12_evidence_record_ids",
    "run2_12_memory_seed_ids",
    "run2_12_workflow_gate_ids",
    "run2_12_code_module_ids",
    "run2_12_density_whitespace_gate",
    "run2_12_demo_sequence_gate",
    "run2_12_climax_object_gate",
    "run2_13_visual_delta_from_run2_10",
    "run2_13_negative_control_probe",
}
EXPECTED_RUN2_14_TRACE_FIELDS = {
    "run2_12_evidence_record_ids",
    "run2_12_memory_seed_ids",
    "run2_12_workflow_gate_ids",
    "run2_14_aesthetic_source_run_id",
    "run2_14_aesthetic_shell_input_ids",
    "run2_14_surface_policy",
    "run2_14_visible_workflow_suppression",
    "run2_14_visual_delta_from_run2_13",
    "run2_14_code_module_ids",
    "run2_14_bad_control_probe",
}
EXPECTED_RUN2_15_TRACE_FIELDS = {
    "run2_15_selected_layout_module_ids",
    "run2_15_selector_gate_ids",
    "run2_15_trace_visibility_policy",
    "run2_15_text_resilience_result",
    "run2_15_trace_hidden_result",
    "run2_15_product_surface_probe",
    "run2_15_metric_reveal_climax_probe",
    "run2_15_bad_selector_control_probe",
}
EXPECTED_RUN2_16_TRACE_FIELDS = {
    "run2_16_aesthetic_source_run_id",
    "run2_16_aesthetic_shell_input_ids",
    "run2_16_selector_input_ids",
    "run2_16_selector_execution_status",
    "run2_16_surface_policy",
    "run2_16_visible_workflow_suppression",
    "run2_16_visual_delta_from_run2_13",
    "run2_16_code_module_ids",
    "run2_16_bad_control_probe",
}
EXPECTED_RUN2_6_USECASE_FIELDS = {
    "id",
    "source_ids",
    "audience",
    "business_decision",
    "deck_mission",
    "slide_arc",
    "must_show",
    "must_not_show",
    "failure_modes",
    "visual_risk",
    "workflow_implications",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_6_BENCHMARK_FIELDS = {
    "id",
    "source_ids",
    "allowed_use",
    "composition_rules",
    "typography_rules",
    "spacing_rules",
    "theme_rules",
    "motion_or_interaction_rules",
    "native_ppt_implications",
    "anti_copy_rules",
    "qa_probe",
    "trace_fields",
    "release_boundary",
}
EXPECTED_CLAIM_IDS = {
    "claim_data_changes_deck_quality",
    "claim_aesthetic_memory_controls_rhythm",
    "claim_asset_memory_preserves_editability",
    "claim_bad_aesthetic_memory_is_negative_control",
    "claim_appendix_absorbs_proof_detail",
    "claim_public_release_requires_render_and_human_gate",
}
EXPECTED_ASSET_IDS = {
    "asset_launch_atmosphere_background",
    "asset_system_svg_mark",
    "asset_evidence_flow_diagram",
    "asset_comparison_delta_chart",
}
EXPECTED_MOVES = {
    "cinematic_cover",
    "low_density_claim",
    "big_object_layout",
    "editorial_comparison",
    "proof_reveal",
    "visual_climax",
    "premium_closing",
    "appendix_absorption",
}
EXPECTED_BAD_MEMORY_FIELDS = {
    "id",
    "replaces",
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
    "expected_failure",
}
EXPECTED_RHYTHM_ROLES = {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}
RUN2_8_FORBIDDEN_MEDIA_MARKERS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".mp4",
    ".mov",
    "http://",
    "https://",
    "data:image",
    "base64,",
)
RUN2_8_CODE_BINDING_TERMS = {"fontSize", "bbox", "spacing", "heroObject", "beforeAfter", "workflowGate"}
RUN2_18_EVIDENCE_FIELDS = {
    "record_id",
    "source_family",
    "commercial_usecase_ids",
    "source_ids",
    "modality_mix",
    "source_locator",
    "observed_design_method",
    "business_requirement",
    "derived_generation_constraint",
    "memory_targets",
    "workflow_gate_targets",
    "anti_copy_boundary",
    "bad_control_probe",
    "release_boundary",
}
RUN2_18_MEMORY_FIELDS = {
    "memory_id",
    "memory_family",
    "slide_roles",
    "evidence_record_ids",
    "composition_contract",
    "typography_contract",
    "spacing_contract",
    "motion_or_sequence_contract",
    "proof_object_contract",
    "code_generation_binding",
    "trace_fields_required",
    "negative_control_failure",
    "release_boundary",
}
RUN2_18_WORKFLOW_GATE_FIELDS = {
    "gate_id",
    "required_before_next_rerun",
    "evidence_record_ids",
    "memory_ids",
    "selection_rules",
    "rejection_rules",
    "trace_fields",
    "qa_probe",
    "bad_control_probe",
    "release_boundary",
}
EXPECTED_RUN2_19_TRACE_FIELDS = {
    "run2_18_selected_evidence_ids",
    "run2_18_selected_memory_ids",
    "run2_18_selected_gate_ids",
    "run2_18_bad_control_probe",
    "run2_18_release_boundary",
    "run2_19_code_module_ids",
    "run2_19_trace_thickness_status",
    "run2_19_visual_delta_from_run2_16",
}
EXPECTED_RUN2_22_TRACE_FIELDS = {
    "run2_21_visual_decision_memory_id",
    "run2_21_primary_evidence_id",
    "run2_21_secondary_evidence_ids",
    "run2_21_rejected_evidence_reasons",
    "run2_21_selector_gate_id",
    "run2_21_visual_decision_delta",
    "run2_22_selector_execution_status",
    "run2_22_code_module_ids",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def assert_contains(body: str, terms: list[str]) -> None:
    normalized = normalize(body)
    for term in terms:
        assert normalize(term) in normalized, f"missing term: {term!r}"


def assert_mentions_any(body: str, terms: set[str]) -> None:
    normalized = normalize(body)
    assert any(normalize(term) in normalized for term in terms), f"missing one of: {sorted(terms)!r}"


def iter_string_values(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_string_values(item)


def json_files(directory: str) -> list[Path]:
    return sorted((PACK / directory).glob("*.json"))


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def test_run2_case_pack_is_valid() -> None:
    result = validate_case_pack(PACK, profile="run2")

    assert result.ok is True, result.errors


def test_run2_commercial_case_is_concrete_and_public_demo_oriented() -> None:
    body = (PACK / "commercial_case.md").read_text(encoding="utf-8")

    assert_contains(body, ["audience", "decision", "failed deck", "public-demo", "six slides"])
    assert "generic beautiful PPT" not in body


def test_run2_has_thick_source_and_video_cards() -> None:
    source_cards = json_files("source_cards")
    video_cards = json_files("video_cards")
    source_card_bodies = [load_json(path) for path in source_cards]
    video_card_bodies = [load_json(path) for path in video_cards]

    assert len(source_cards) >= 8
    assert len(video_cards) >= 2
    assert EXPECTED_SOURCE_CARD_IDS <= {card["card_id"] for card in source_card_bodies}
    assert EXPECTED_VIDEO_CARD_IDS <= {card["card_id"] for card in video_card_bodies}

    for card in [*source_card_bodies, *video_card_bodies]:
        assert_contains(card["do_not_copy"], ["do not copy"])
        assert card["allowed_use"] in {
            "short_analysis",
            "derived_rules_only",
            "visual_inspiration",
            "timestamped_observation_only",
        }

    for card in source_card_bodies:
        assert_mentions_any(
            card["ppt_translation"],
            {"editable", "native", "PPT", "PowerPoint", "shape", "text", "SVG", "diagram", "chart"},
        )
        assert_mentions_any(
            card["quality_risk"],
            {"generic", "report", "dashboard", "degrade", "weak", "thin", "overdesigned"},
        )


def test_run2_has_multimodal_lesson_database() -> None:
    database = load_json(PACK / "multimodal_database.json")
    sources = load_json(PACK / "sources.json")
    records = database["records"]
    source_ids = {source["id"] for source in sources["sources"]}
    record_ids = {record["id"] for record in records}
    covered_modalities = {modality for record in records for modality in record["modalities"]}

    assert database["status"] == "run2_2_multimodal_contract_public_blocked"
    assert EXPECTED_MULTIMODAL_RECORD_IDS <= record_ids
    assert {
        "duarte_persuasive_visual_storytelling",
        "duarte_slide_design_course",
        "udel_design_principles_video",
    } <= source_ids
    assert set(database["required_modalities"]) == EXPECTED_MULTIMODAL_MODALITIES
    assert covered_modalities == EXPECTED_MULTIMODAL_MODALITIES
    assert database["storage_policy"]["raw_media"] == "forbidden"
    assert_contains(
        json.dumps(database["storage_policy"]),
        ["Do not store", "audio", "video", "full transcripts", "screenshots", "source assets"],
    )

    for record in records:
        assert record["allowed_storage"] == "derived_observations_only"
        assert record["anchors"]
        assert set(record["modalities"]) <= EXPECTED_MULTIMODAL_MODALITIES
        assert record["do_not_store"]
        for anchor in record["anchors"]:
            assert anchor["modality"] in record["modalities"]
            assert anchor["allowed_use"] in {
                "short_analysis",
                "derived_rules_only",
                "visual_inspiration",
                "timestamped_observation_only",
            }
            assert_mentions_any(
                anchor["extracted_design_signal"],
                {"slide", "Generate", "Reject", "Convert", "Reduce", "Use"},
            )

    anchors_by_modality = {"transcript": [], "interaction": []}
    for record in records:
        for anchor in record["anchors"]:
            if anchor["modality"] in anchors_by_modality:
                anchors_by_modality[anchor["modality"]].append(anchor)
    assert anchors_by_modality["transcript"]
    assert anchors_by_modality["interaction"]
    assert_contains(
        " ".join(anchor["extracted_design_signal"] for anchor in anchors_by_modality["transcript"]),
        ["native headline", "do not place full transcript text"],
    )
    assert_contains(
        " ".join(anchor["extracted_design_signal"] for anchor in anchors_by_modality["interaction"]),
        ["selected memory", "density budget", "release gate"],
    )

    tasks = database["cross_modal_design_tasks"]
    assert {task["id"] for task in tasks} >= {
        "before_after_visual_delta",
        "audio_to_rhythm_budget",
        "transcript_to_native_headline",
        "interaction_to_skill_surface",
    }
    assert_contains(json.dumps(tasks), ["visible transformation", "density", "native", "generator behavior"])


def test_run2_has_visual_learning_targets_for_next_rerun() -> None:
    database = load_json(PACK / "multimodal_database.json")
    targets = load_json(PACK / "visual_learning_targets.json")
    record_ids = {record["id"] for record in database["records"]}
    anchor_ids = {anchor["anchor_id"] for record in database["records"] for anchor in record["anchors"]}

    assert targets["status"] == "run2_2_visual_learning_targets_public_blocked"
    assert targets["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert_contains(" ".join(targets["native_editable_definition"]), ["native", "editable", "must not contain"])
    assert EXPECTED_VISUAL_TARGET_IDS <= {target["id"] for target in targets["targets"]}

    for target in targets["targets"]:
        assert set(target["source_record_ids"]) <= record_ids
        assert set(target["anchor_ids"]) <= anchor_ids
        assert_contains(target["release_boundary"], ["public blocked"])
        assert_mentions_any(
            target["desired_behavior"], {"before/after", "mini-preview", "rhythm", "headline", "climax"}
        )
        requirements = " ".join(target["code_generation_requirements"])
        assert_contains(requirements, ["native"])
        assert_mentions_any(requirements, {"editable", "record", "trace"})
        assert_mentions_any(
            target["qa_probe"],
            {"contact sheet", "headline", "rhythm", "climax", "mini-preview"},
        )


def test_run2_has_visual_target_components_for_native_generation() -> None:
    targets = load_json(PACK / "visual_learning_targets.json")
    components = load_json(PACK / "visual_target_components.json")
    target_ids = {target["id"] for target in targets["targets"]}
    component_ids = {component["id"] for component in components["components"]}

    assert components["status"] == "run2_3_native_visual_components_public_blocked"
    assert components["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert EXPECTED_VISUAL_COMPONENT_IDS <= component_ids

    covered_targets = {target_id for component in components["components"] for target_id in component["target_ids"]}
    assert EXPECTED_VISUAL_TARGET_IDS <= covered_targets

    for component in components["components"]:
        assert set(component["target_ids"]) <= target_ids
        assert component["slide_roles"]
        assert_contains(" ".join(component["native_ppt_primitives"]), ["native", "editable"])
        assert_contains(component["layout_contract"], ["object", "canvas"])
        assert_mentions_any(
            component["layout_contract"],
            {"thumbnail", "mini-preview", "rhythm", "headline", "climax", "gate"},
        )
        assert_contains(component["density_contract"], ["visible words", "panels"])
        assert_mentions_any(
            " ".join(component["trace_fields"]),
            {"visual_learning_target_ids", "visual_component_ids", "density_counts", "native_ppt_checks"},
        )
        assert_mentions_any(
            component["qa_probe"],
            {"contact sheet", "thumbnail", "rhythm", "climax", "before/after"},
        )
        assert_contains(component["release_boundary"], ["public_blocked"])


def test_run2_has_video_demo_beat_map_for_motion_learning() -> None:
    database = load_json(PACK / "multimodal_database.json")
    beat_map = load_json(PACK / "video_demo_beat_map.json")
    record_ids = {record["id"] for record in database["records"]}
    anchor_ids = {anchor["anchor_id"] for record in database["records"] for anchor in record["anchors"]}
    video_card_ids = {card["card_id"] for card in (load_json(path) for path in json_files("video_cards"))}

    assert beat_map["status"] == "run2_4_video_demo_beat_map_public_blocked"
    assert beat_map["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert beat_map["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_VIDEO_BEAT_IDS <= {beat["id"] for beat in beat_map["beats"]}

    for beat in beat_map["beats"]:
        assert set(beat["source_record_ids"]) <= record_ids
        assert set(beat["anchor_ids"]) <= anchor_ids
        assert set(beat["video_card_ids"]) <= video_card_ids
        assert_contains(beat["locator"], [":"])
        assert_mentions_any(beat["motion_role"], {"attention_reset", "reveal", "build", "scale", "handoff"})
        assert_contains(" ".join(beat["reveal_sequence"]), ["native"])
        assert_contains(" ".join(beat["do_not_store"]), ["video", "frames", "audio", "transcript"])
        assert_contains(beat["release_boundary"], ["public_blocked"])


def test_run2_has_motion_learning_targets_and_sequence_components() -> None:
    beat_map = load_json(PACK / "video_demo_beat_map.json")
    motion_targets = load_json(PACK / "motion_learning_targets.json")
    visual_components = load_json(PACK / "visual_target_components.json")
    sequence_components = load_json(PACK / "presentation_sequence_components.json")
    beat_ids = {beat["id"] for beat in beat_map["beats"]}
    visual_component_ids = {component["id"] for component in visual_components["components"]}
    motion_target_ids = {target["id"] for target in motion_targets["targets"]}

    assert motion_targets["status"] == "run2_4_motion_learning_targets_public_blocked"
    assert sequence_components["status"] == "run2_4_sequence_components_public_blocked"
    assert EXPECTED_MOTION_TARGET_IDS <= motion_target_ids
    assert EXPECTED_SEQUENCE_COMPONENT_IDS <= {component["id"] for component in sequence_components["components"]}

    for target in motion_targets["targets"]:
        assert set(target["beat_ids"]) <= beat_ids
        assert set(target["visual_component_ids"]) <= visual_component_ids
        assert_contains(" ".join(target["code_generation_requirements"]), ["native", "metadata", "trace"])
        assert_mentions_any(target["desired_behavior"], {"reveal", "scale", "build", "handoff", "pause"})
        assert_contains(target["release_boundary"], ["public_blocked"])

    for component in sequence_components["components"]:
        assert set(component["motion_target_ids"]) <= motion_target_ids
        assert set(component["visual_component_ids"]) <= visual_component_ids
        assert component["sequence_steps"]
        assert [step["order"] for step in component["sequence_steps"]] == list(
            range(1, len(component["sequence_steps"]) + 1)
        )
        assert_contains(" ".join(component["native_ppt_primitives"]), ["native", "editable"])
        assert_contains(" ".join(component["trace_fields"]), ["motion_target_ids", "sequence_component_ids"])
        assert_contains(component["qa_probe"], ["reveal"])
        assert_contains(component["release_boundary"], ["public_blocked"])


def test_run2_5_has_production_reference_decompositions() -> None:
    references = load_json(PACK / "production_reference_decompositions.json")
    sources = load_json(PACK / "sources.json")
    source_ids = {source["id"] for source in sources["sources"]}
    visual_component_ids = {component["id"] for component in load_json(PACK / "visual_target_components.json")["components"]}
    motion_target_ids = {target["id"] for target in load_json(PACK / "motion_learning_targets.json")["targets"]}
    sequence_component_ids = {
        component["id"] for component in load_json(PACK / "presentation_sequence_components.json")["components"]
    }

    assert references["status"] == "run2_5_production_reference_decomposition_public_blocked"
    assert references["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert references["storage_policy"]["raw_media"] == "forbidden"
    assert_contains(json.dumps(references["extraction_policy"]), ["derived observation", "no automatic frame extraction"])
    assert EXPECTED_PRODUCTION_REFERENCE_IDS <= {record["id"] for record in references["references"]}

    for record in references["references"]:
        assert EXPECTED_PRODUCTION_REFERENCE_FIELDS <= set(record), record["id"]
        assert set(record["source_ids"]) <= source_ids
        assert set(record["visual_component_ids"]) <= visual_component_ids
        assert set(record["motion_target_ids"]) <= motion_target_ids
        assert set(record["sequence_component_ids"]) <= sequence_component_ids
        assert_contains(" ".join(record["visual_observations"]), ["native", "composition"])
        assert_contains(" ".join(record["composition_primitives"]), ["canvas"])
        assert_contains(" ".join(record["typography_primitives"]), ["headline", "hierarchy"])
        assert_contains(" ".join(record["spacing_primitives"]), ["whitespace", "margin"])
        assert_contains(" ".join(record["motion_or_sequence_primitives"]), ["sequence"])
        assert_contains(" ".join(record["module_implications"]), ["code", "module", "trace"])
        assert_contains(" ".join(record["do_not_copy"]), ["do not copy", "screenshot", "brand"])
        assert_contains(" ".join(record["extraction_notes"]), ["derived", "not copied"])
        assert_contains(record["qa_probe"], ["contact sheet"])
        assert_contains(record["release_boundary"], ["public_blocked"])


def test_run2_5_has_aesthetic_memory_v2_and_visual_production_modules() -> None:
    references = load_json(PACK / "production_reference_decompositions.json")
    aesthetic_v2 = load_json(PACK / "aesthetic_memory_v2.json")
    modules = load_json(PACK / "visual_production_modules.json")
    reference_ids = {record["id"] for record in references["references"]}
    visual_component_ids = {component["id"] for component in load_json(PACK / "visual_target_components.json")["components"]}
    motion_target_ids = {target["id"] for target in load_json(PACK / "motion_learning_targets.json")["targets"]}
    sequence_component_ids = {
        component["id"] for component in load_json(PACK / "presentation_sequence_components.json")["components"]
    }

    assert aesthetic_v2["status"] == "run2_5_aesthetic_memory_v2_public_blocked"
    assert modules["status"] == "run2_5_visual_production_modules_public_blocked"
    assert EXPECTED_AESTHETIC_V2_MOVE_IDS <= {move["id"] for move in aesthetic_v2["moves"]}
    assert EXPECTED_PRODUCTION_MODULE_IDS <= {module["id"] for module in modules["modules"]}

    for move in aesthetic_v2["moves"]:
        assert EXPECTED_AESTHETIC_V2_FIELDS <= set(move), move["id"]
        assert set(move["production_reference_ids"]) <= reference_ids
        assert set(move["visual_component_ids"]) <= visual_component_ids
        assert set(move["motion_target_ids"]) <= motion_target_ids
        assert set(move["sequence_component_ids"]) <= sequence_component_ids
        assert move["density_budget"]["max_words"] <= 52
        assert_contains(move["composition_contract"], ["canvas", "focal"])
        assert_contains(move["typography_contract"], ["headline", "hierarchy"])
        assert_contains(move["spacing_contract"], ["whitespace", "margin"])
        assert_contains(move["provenance_boundary"], ["derived", "do not copy"])
        assert_contains(" ".join(move["code_generation_contract"]), ["native", "PPT", "module"])
        assert_contains(" ".join(move["trace_fields"]), ["aesthetic_memory_v2_ids", "visual_production_module_ids"])
        assert_mentions_any(" ".join(move["forbidden_report_patterns"]), {"dashboard", "equal grid", "report", "tiny"})
        assert_contains(move["qa_probe"], ["contact sheet"])

    module_ids_by_move = {move_id for module in modules["modules"] for move_id in module["aesthetic_memory_v2_ids"]}
    assert EXPECTED_AESTHETIC_V2_MOVE_IDS <= module_ids_by_move
    for module in modules["modules"]:
        assert EXPECTED_VISUAL_PRODUCTION_MODULE_FIELDS <= set(module), module["id"]
        assert set(module["production_reference_ids"]) <= reference_ids
        assert set(module["aesthetic_memory_v2_ids"]) <= {move["id"] for move in aesthetic_v2["moves"]}
        assert_contains(" ".join(module["native_ppt_primitives"]), ["native", "editable"])
        assert_contains(module["layout_recipe"], ["canvas"])
        assert_contains(module["typography_recipe"], ["headline"])
        assert_contains(module["spacing_recipe"], ["margin"])
        assert_contains(" ".join(module["trace_fields"]), ["visual_production_module_ids", "aesthetic_memory_v2_ids"])
        assert_contains(module["fallback_policy"], ["native", "public_blocked"])
        assert_contains(module["provenance_boundary"], ["derived", "do not copy"])
        assert_contains(module["qa_probe"], ["contact sheet"])
        assert_contains(module["release_boundary"], ["public_blocked"])


def test_run2_6_has_commercial_usecase_bank() -> None:
    sources = load_json(PACK / "sources.json")
    usecases = load_json(PACK / "commercial_usecase_bank.json")
    source_ids = {source["id"] for source in sources["sources"]}

    assert EXPECTED_RUN2_6_SOURCE_IDS <= source_ids
    assert usecases["status"] == "run2_6_commercial_usecase_bank_public_blocked"
    assert usecases["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert usecases["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_6_USECASE_IDS <= {item["id"] for item in usecases["usecases"]}

    for item in usecases["usecases"]:
        assert EXPECTED_RUN2_6_USECASE_FIELDS <= set(item), item["id"]
        assert set(item["source_ids"]) <= source_ids
        assert_contains(" ".join(item["must_not_show"]), ["copy", "brand"])
        assert_contains(" ".join(item["workflow_implications"]), ["select", "benchmark"])
        assert_contains(item["qa_probe"], ["contact sheet"])
        assert_contains(item["release_boundary"], ["public_blocked"])


def test_run2_6_has_aesthetic_benchmark_bank() -> None:
    sources = load_json(PACK / "sources.json")
    benchmarks = load_json(PACK / "aesthetic_benchmark_bank.json")
    source_ids = {source["id"] for source in sources["sources"]}

    assert benchmarks["status"] == "run2_6_aesthetic_benchmark_bank_public_blocked"
    assert benchmarks["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert benchmarks["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_6_BENCHMARK_IDS <= {item["id"] for item in benchmarks["benchmarks"]}

    for item in benchmarks["benchmarks"]:
        assert EXPECTED_RUN2_6_BENCHMARK_FIELDS <= set(item), item["id"]
        assert set(item["source_ids"]) <= source_ids
        assert item["allowed_use"] == "derived_rules_only"
        assert_contains(" ".join(item["composition_rules"]), ["native"])
        assert_contains(" ".join(item["typography_rules"]), ["hierarchy"])
        assert_contains(" ".join(item["spacing_rules"]), ["spacing"])
        assert_contains(" ".join(item["anti_copy_rules"]), ["do not copy"])
        assert EXPECTED_RUN2_6_TRACE_FIELDS & set(item["trace_fields"])
        assert_contains(item["release_boundary"], ["public_blocked"])


def test_run2_6_has_workflow_decision_policy_and_trace_contract() -> None:
    usecases = load_json(PACK / "commercial_usecase_bank.json")
    benchmarks = load_json(PACK / "aesthetic_benchmark_bank.json")
    policy = load_json(PACK / "workflow_decision_policy.json")
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    usecase_ids = {item["id"] for item in usecases["usecases"]}
    benchmark_ids = {item["id"] for item in benchmarks["benchmarks"]}

    assert policy["status"] == "run2_6_workflow_decision_policy_public_blocked"
    assert policy["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert set(policy["selection_chain"]) == {
        "commercial_case",
        "usecase_id",
        "benchmark_ids",
        "theme_policy_id",
        "typography_system_id",
        "spacing_token_set_id",
        "visual_production_module_ids",
        "qa_probes",
    }
    for mapping in policy["usecase_benchmark_map"]:
        assert mapping["usecase_id"] in usecase_ids
        assert set(mapping["benchmark_ids"]) <= benchmark_ids
        assert mapping["theme_policy_id"]
        assert mapping["typography_system_id"]
        assert mapping["spacing_token_set_id"]
        assert_contains(" ".join(mapping["source_brand_sanitization"]), ["do not copy"])

    workflow_stage_ids = {stage["id"] for stage in workflow["stages"]}
    assert {
        "select_commercial_usecase",
        "select_aesthetic_benchmarks",
        "select_theme_typography_spacing_policy",
    } <= workflow_stage_ids
    assert EXPECTED_RUN2_6_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])


def test_run2_6r_has_visual_repair_policy() -> None:
    policy = load_json(PACK / "visual_repair_policy.json")
    workflow_policy = load_json(PACK / "workflow_decision_policy.json")
    workflow_policy_ids = {
        mapping["theme_policy_id"] for mapping in workflow_policy["usecase_benchmark_map"]
    } | {
        mapping["typography_system_id"] for mapping in workflow_policy["usecase_benchmark_map"]
    } | {
        mapping["spacing_token_set_id"] for mapping in workflow_policy["usecase_benchmark_map"]
    } | {
        benchmark_id
        for mapping in workflow_policy["usecase_benchmark_map"]
        for benchmark_id in mapping["benchmark_ids"]
    }

    assert policy["status"] == "run2_6r_visual_repair_policy_public_blocked"
    assert policy["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert policy["default_visual_direction"] == "light_first_editorial_graphite_with_vivid_proof_color"
    assert EXPECTED_RUN2_6R_REPAIR_IDS <= {repair["id"] for repair in policy["repairs"]}
    policy_delta_text = " ".join(
        repair[field]
        for repair in policy["repairs"]
        for field in ("typography_delta", "spacing_delta", "composition_delta", "theme_delta")
    )
    assert_contains(policy_delta_text, ["Run 2.5", "native", "forest-green", "source-brand"])

    for repair in policy["repairs"]:
        assert EXPECTED_RUN2_6R_REPAIR_FIELDS <= set(repair), repair["id"]
        assert repair["target_slide_roles"]
        assert set(repair["target_slide_roles"]) <= {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert set(repair["source_policy_ids"]) <= workflow_policy_ids | {"workflow_decision_policy.json"}
        assert_contains(repair["composition_delta"], ["native"])
        assert_contains(repair["theme_delta"], ["forest-green", "source-brand"])
        assert "ppt-run2-5-full-vulca" in repair["must_differ_from"]
        assert "ppt-run2-6-full-vulca" in repair["must_differ_from"]
        assert_contains(" ".join(repair["native_ppt_requirements"]), ["native", "editable"])
        assert_contains(repair["qa_probe"], ["contact sheet"])
        assert_contains(repair["release_boundary"], ["public_blocked"])


def test_run2_6r_workflow_and_trace_contract_include_visual_repair() -> None:
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    workflow_stage_ids = {stage["id"] for stage in workflow["stages"]}
    assert "select_visual_repair_policy" in workflow_stage_ids
    workflow_text = json.dumps(workflow)
    assert_contains(workflow_text, ["visual_repair_policy.json", "visual repair", "not Run 3.0"])
    assert EXPECTED_RUN2_6R_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])


def test_run2_7_has_real_usecase_and_multimodal_source_records() -> None:
    usecase = load_json(PACK / "run2_7_commercial_usecase.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    sources = load_json(PACK / "sources.json")
    source_ids = {source["id"] for source in sources["sources"]}

    assert usecase["status"] == "run2_7_commercial_usecase_public_blocked"
    assert usecase["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert EXPECTED_RUN2_7_USECASE_IDS <= {usecase["id"]}
    assert usecase["primary_usecase"] == "AI design-to-production platform launch deck"
    assert len(usecase["six_slide_arc"]) == 6
    assert [slide["rhythm_role"] for slide in usecase["six_slide_arc"]] == [
        "cover",
        "setup",
        "contrast",
        "proof",
        "climax",
        "close",
    ]
    assert_contains(json.dumps(usecase), ["AI product builders", "design engineering leaders", "technical founders"])
    assert_contains(json.dumps(usecase["business_job"]), ["product-system learning", "not one-shot prompting"])
    assert_contains(" ".join(usecase["must_not_show"]), ["copy", "source brand", "full-slide raster"])
    assert_contains(" ".join(usecase["proof_questions"]), ["data", "memory", "workflow", "PPT"])
    assert_contains(usecase["release_boundary"], ["public_blocked"])

    assert source_records["status"] == "run2_7_multimodal_source_records_public_blocked"
    assert source_records["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert source_records["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_7_SOURCE_RECORD_IDS <= {record["id"] for record in source_records["records"]}

    covered_modalities = {modality for record in source_records["records"] for modality in record["modalities"]}
    assert {"text", "image_reference", "video", "audio", "transcript", "interaction"} <= covered_modalities

    for record in source_records["records"]:
        assert EXPECTED_RUN2_7_SOURCE_RECORD_FIELDS <= set(record), record["id"]
        assert record["source_id"] in source_ids
        assert record["allowed_use"] == "derived_rules_only"
        assert set(record["slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert_contains(record["native_ppt_implication"], ["native", "editable"])
        assert_contains(record["anti_copy_boundary"], ["do not copy"])
        assert_contains(record["qa_probe"], ["contact sheet"])
        assert_contains(record["release_boundary"], ["public_blocked"])


def test_run2_7_has_serializable_design_memory() -> None:
    usecase = load_json(PACK / "run2_7_commercial_usecase.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    memory = load_json(PACK / "run2_7_design_memory.json")
    source_record_ids = {record["id"] for record in source_records["records"]}

    assert memory["status"] == "run2_7_design_memory_public_blocked"
    assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert memory["memory_type"] == "deterministic_serializable_rules"
    assert EXPECTED_RUN2_7_MEMORY_IDS <= {record["id"] for record in memory["memories"]}

    for record in memory["memories"]:
        assert EXPECTED_RUN2_7_MEMORY_FIELDS <= set(record), record["id"]
        assert set(record["source_record_ids"]) <= source_record_ids
        assert usecase["id"] in record["applicable_usecases"]
        assert set(record["applicable_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert record["typography_rules"]
        assert record["spacing_rules"]
        assert record["composition_rules"]
        assert record["rhythm_rules"]
        assert_contains(" ".join(record["native_ppt_generation_requirements"]), ["native", "editable", "trace"])
        assert_mentions_any(
            " ".join(record["forbidden_patterns"]),
            {"report", "dashboard", "equal card", "source brand", "full-slide raster"},
        )
        assert_contains(" ".join(record["qa_probes"]), ["contact sheet"])
        assert_contains(record["release_boundary"], ["public_blocked"])

    climax_memory = next(
        record for record in memory["memories"] if record["id"] == "memory_composition_single_object_climax"
    )
    assert "climax" in climax_memory["applicable_slide_roles"]
    assert_contains(" ".join(climax_memory["composition_rules"]), ["40-55%", "one native proof object"])


def test_run2_7_workflow_and_trace_contract_include_memory_selection() -> None:
    usecase = load_json(PACK / "run2_7_commercial_usecase.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    memory = load_json(PACK / "run2_7_design_memory.json")
    policy = load_json(PACK / "run2_7_workflow_policy.json")
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    source_record_ids = {record["id"] for record in source_records["records"]}
    memory_ids = {record["id"] for record in memory["memories"]}

    assert policy["status"] == "run2_7_workflow_policy_public_blocked"
    assert policy["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert policy["commercial_usecase_id"] == usecase["id"]
    assert set(policy["selection_chain"]) == {
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
    }

    for mapping in policy["slide_role_memory_map"]:
        assert mapping["commercial_usecase_id"] == usecase["id"]
        assert set(mapping["source_record_ids"]) <= source_record_ids
        assert set(mapping["design_memory_ids"]) <= memory_ids
        assert EXPECTED_RUN2_7_TRACE_FIELDS <= set(mapping["trace_fields"])
        assert_contains(" ".join(mapping["workflow_gates"]), ["public_blocked", "native", "source-brand"])

    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    assert "select_run2_7_design_memory" in workflow_stage_ids
    assert workflow_stage_ids.index("select_run2_7_design_memory") < workflow_stage_ids.index(
        "select_visual_production_modules"
    )
    workflow_text = json.dumps(workflow)
    assert_contains(
        workflow_text,
        [
            "run2_7_commercial_usecase.json",
            "run2_7_multimodal_source_records.json",
            "run2_7_design_memory.json",
            "run2_7_workflow_policy.json",
        ],
    )
    assert EXPECTED_RUN2_7_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])


def test_run2_8_has_tutorial_video_decomposition_units() -> None:
    decomposition_path = PACK / "run2_8_tutorial_decomposition.json"
    assert decomposition_path.exists(), "missing Run 2.8 tutorial decomposition data"
    decomposition = load_json(decomposition_path)
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    sources = load_json(PACK / "sources.json")
    source_record_ids = {record["id"] for record in source_records["records"]}
    source_ids = {source["id"] for source in sources["sources"]}

    assert decomposition["status"] == "run2_8_tutorial_decomposition_public_blocked"
    assert decomposition["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert decomposition["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_8_DECOMPOSITION_IDS <= {unit["id"] for unit in decomposition["units"]}

    required = {
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
    }
    derived_modalities = {"video", "audio", "transcript", "image_reference", "interaction"}
    for unit in decomposition["units"]:
        assert required <= set(unit), unit["id"]
        assert unit["source_record_ids"]
        assert unit["source_ids"]
        assert unit["modality_mix"]
        assert set(unit["source_record_ids"]) <= source_record_ids
        assert set(unit["source_ids"]) <= source_ids
        assert set(unit["modality_mix"]) & derived_modalities
        assert_contains(json.dumps(unit["code_generation_binding"]), ["native"])
        assert isinstance(unit["layout_budget"], dict) and unit["layout_budget"]
        for field_value in iter_string_values(unit):
            lowered = field_value.lower()
            for marker in RUN2_8_FORBIDDEN_MEDIA_MARKERS:
                assert marker not in lowered, f"{unit['id']} contains copied media marker {marker!r}"


def test_run2_8_has_executable_design_memory_bindings() -> None:
    memory_path = PACK / "run2_8_executable_design_memory.json"
    decomposition_path = PACK / "run2_8_tutorial_decomposition.json"
    assert memory_path.exists(), "missing Run 2.8 executable design memory"
    assert decomposition_path.exists(), "missing Run 2.8 tutorial decomposition data"
    memory = load_json(memory_path)
    decomposition = load_json(decomposition_path)
    decomposition_unit_ids = {unit["id"] for unit in decomposition["units"]}

    assert memory["status"] == "run2_8_executable_design_memory_public_blocked"
    assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert memory["memory_type"] == "executable_schema_bindings"
    assert EXPECTED_RUN2_8_MEMORY_BINDING_IDS <= {binding["id"] for binding in memory["bindings"]}

    required = {
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
    }
    for binding in memory["bindings"]:
        assert required <= set(binding), binding["id"]
        assert binding["decomposition_unit_ids"]
        assert binding["applies_to_slide_roles"]
        assert set(binding["decomposition_unit_ids"]) <= decomposition_unit_ids
        assert set(binding["applies_to_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert isinstance(binding["code_binding"], dict), binding["id"]
        assert {"function_name", "params", "layout_budget"} <= set(binding["code_binding"]), binding["id"]
        assert isinstance(binding["code_binding"]["params"], dict) and binding["code_binding"]["params"]
        assert isinstance(binding["code_binding"]["layout_budget"], dict) and binding["code_binding"]["layout_budget"]
        code_binding_text = json.dumps(binding["code_binding"])
        assert any(term in code_binding_text for term in RUN2_8_CODE_BINDING_TERMS), binding["id"]


def test_run2_8_workflow_gate_matrix_connects_schema_to_trace() -> None:
    matrix_path = PACK / "run2_8_workflow_gate_matrix.json"
    decomposition_path = PACK / "run2_8_tutorial_decomposition.json"
    memory_path = PACK / "run2_8_executable_design_memory.json"
    assert matrix_path.exists(), "missing Run 2.8 workflow gate matrix"
    assert decomposition_path.exists(), "missing Run 2.8 tutorial decomposition data"
    assert memory_path.exists(), "missing Run 2.8 executable design memory"
    matrix = load_json(matrix_path)
    decomposition = load_json(decomposition_path)
    memory = load_json(memory_path)
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")
    decomposition_unit_ids = {unit["id"] for unit in decomposition["units"]}
    memory_binding_ids = {binding["id"] for binding in memory["bindings"]}
    code_binding_ids = {binding["code_binding"]["function_name"] for binding in memory["bindings"]}

    assert matrix["status"] == "run2_8_workflow_gate_matrix_public_blocked"
    assert matrix["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert set(matrix["selection_chain"]) == {
        "commercial_usecase",
        "run2_8_decomposition_units",
        "run2_8_executable_memory_bindings",
        "run2_8_gate_matrix",
        "native_ppt_code_generation",
        "layout_quality_gate",
        "delivery_gate",
        "visual_qa_gate",
    }
    assert EXPECTED_RUN2_8_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])

    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    run2_8_stages = [
        "decompose_run2_8_tutorial_video_units",
        "select_run2_8_executable_design_memory",
        "apply_run2_8_workflow_gate_matrix",
    ]
    for stage_id in run2_8_stages:
        assert stage_id in workflow_stage_ids
        assert workflow_stage_ids.index(stage_id) < workflow_stage_ids.index("generate_code_first_ppt")
    assert workflow_stage_ids.index(run2_8_stages[0]) < workflow_stage_ids.index(run2_8_stages[1])
    assert workflow_stage_ids.index(run2_8_stages[1]) < workflow_stage_ids.index(run2_8_stages[2])
    workflow_text = json.dumps(workflow)
    assert_contains(
        workflow_text,
        [
            "run2_8_tutorial_decomposition.json",
            "run2_8_executable_design_memory.json",
            "run2_8_workflow_gate_matrix.json",
        ],
    )

    required = {
        "id",
        "slide_role",
        "decomposition_unit_ids",
        "memory_binding_ids",
        "required_code_bindings",
        "layout_budget",
        "pass_fail_checks",
        "trace_fields",
        "public_release_gate",
    }
    covered_trace_fields = set()
    covered_decomposition_unit_ids = set()
    covered_memory_binding_ids = set()
    covered_code_binding_ids = set()
    for gate in matrix["gates"]:
        assert required <= set(gate), gate.get("id", gate["slide_role"])
        assert gate["slide_role"] in EXPECTED_RHYTHM_ROLES
        assert gate["decomposition_unit_ids"]
        assert gate["memory_binding_ids"]
        assert gate["required_code_bindings"]
        assert set(gate["decomposition_unit_ids"]) <= decomposition_unit_ids
        assert set(gate["memory_binding_ids"]) <= memory_binding_ids
        assert set(gate["required_code_bindings"]) <= code_binding_ids
        assert set(gate["trace_fields"]) <= set(trace_contract["per_slide_required_fields"])
        covered_decomposition_unit_ids.update(gate["decomposition_unit_ids"])
        covered_memory_binding_ids.update(gate["memory_binding_ids"])
        covered_code_binding_ids.update(gate["required_code_bindings"])
        covered_trace_fields.update(gate["trace_fields"])
    assert EXPECTED_RUN2_8_DECOMPOSITION_IDS <= covered_decomposition_unit_ids
    assert EXPECTED_RUN2_8_MEMORY_BINDING_IDS <= covered_memory_binding_ids
    assert code_binding_ids <= covered_code_binding_ids
    assert EXPECTED_RUN2_8_TRACE_FIELDS <= covered_trace_fields


def test_run2_9_has_visual_primitive_repair_data() -> None:
    repair_path = PACK / "run2_9_visual_primitive_repair.json"
    assert repair_path.exists(), "missing Run 2.9 visual primitive repair data"
    repair = load_json(repair_path)
    sources = load_json(PACK / "sources.json")
    run2_8_decomposition = load_json(PACK / "run2_8_tutorial_decomposition.json")
    source_ids = {source["id"] for source in sources["sources"]}
    decomposition_ids = {unit["id"] for unit in run2_8_decomposition["units"]}

    assert repair["status"] == "run2_9_visual_primitive_repair_public_blocked"
    assert repair["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert repair["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_9_VISUAL_PRIMITIVE_IDS <= {item["id"] for item in repair["primitive_repairs"]}

    required = {
        "id",
        "source_ids",
        "decomposition_unit_ids",
        "target_slide_roles",
        "visual_problem",
        "reference_method",
        "extracted_visual_primitive",
        "native_ppt_translation",
        "code_module_obligation",
        "layout_recipe",
        "typography_recipe",
        "motion_or_sequence_recipe",
        "forbidden_box_patterns",
        "boxiness_failure_probe",
        "qa_probe",
        "anti_copy_boundary",
        "release_boundary",
    }
    for primitive in repair["primitive_repairs"]:
        assert required <= set(primitive), primitive["id"]
        assert set(primitive["source_ids"]) <= source_ids
        assert set(primitive["decomposition_unit_ids"]) <= decomposition_ids
        assert set(primitive["target_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert_contains(primitive["native_ppt_translation"], ["native", "editable"])
        assert_contains(primitive["code_module_obligation"], ["function", "trace"])
        assert_mentions_any(
            " ".join(primitive["forbidden_box_patterns"]),
            {"dashboard", "card", "equal panel", "rectangle", "grid"},
        )
        assert_contains(primitive["boxiness_failure_probe"], ["box"])
        for field_value in iter_string_values(primitive):
            lowered = field_value.lower()
            for marker in RUN2_8_FORBIDDEN_MEDIA_MARKERS:
                assert marker not in lowered, f"{primitive['id']} contains copied media marker {marker!r}"


def test_run2_9_has_executable_visual_modules_and_gate_matrix() -> None:
    repair_path = PACK / "run2_9_visual_primitive_repair.json"
    modules_path = PACK / "run2_9_executable_visual_modules.json"
    matrix_path = PACK / "run2_9_visual_gate_matrix.json"
    trace_contract_path = PACK / "results" / "trace_manifest_contract.json"
    workflow_path = PACK / "skill_workflow.json"
    assert repair_path.exists(), "missing Run 2.9 visual primitive repair data"
    assert modules_path.exists(), "missing Run 2.9 executable visual modules"
    assert matrix_path.exists(), "missing Run 2.9 visual gate matrix"
    modules = load_json(modules_path)
    matrix = load_json(matrix_path)
    repair = load_json(repair_path)
    trace_contract = load_json(trace_contract_path)
    workflow = load_json(workflow_path)
    primitive_ids = {item["id"] for item in repair["primitive_repairs"]}
    module_ids = {module["id"] for module in modules["modules"]}
    code_module_ids = {module["code_binding"]["function_name"] for module in modules["modules"]}

    assert modules["status"] == "run2_9_executable_visual_modules_public_blocked"
    assert modules["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert modules["memory_type"] == "visual_primitive_code_modules"
    assert EXPECTED_RUN2_9_VISUAL_MODULE_IDS <= module_ids
    assert EXPECTED_RUN2_9_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])

    module_required = {
        "id",
        "primitive_repair_ids",
        "applies_to_slide_roles",
        "code_binding",
        "composition_contract",
        "native_ppt_primitives",
        "negative_control_failure",
        "qa_probe",
        "release_boundary",
    }
    for module in modules["modules"]:
        assert module_required <= set(module), module["id"]
        assert set(module["primitive_repair_ids"]) <= primitive_ids
        assert set(module["applies_to_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert {"function_name", "params", "layout_budget"} <= set(module["code_binding"]), module["id"]
        assert module["code_binding"]["function_name"].startswith("drawRun29")
        assert_contains(" ".join(module["native_ppt_primitives"]), ["native", "editable"])
        assert_mentions_any(
            module["negative_control_failure"],
            {"box", "dashboard", "card", "grid", "report"},
        )

    assert matrix["status"] == "run2_9_visual_gate_matrix_public_blocked"
    assert matrix["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert set(matrix["selection_chain"]) == {
        "run2_8_visual_diagnosis",
        "run2_9_visual_primitive_repairs",
        "run2_9_executable_visual_modules",
        "run2_9_visual_gate_matrix",
        "native_ppt_code_generation",
        "visual_delta_gate",
        "delivery_gate",
    }
    gate_required = {
        "id",
        "slide_role",
        "visual_primitive_ids",
        "visual_module_ids",
        "required_code_modules",
        "boxiness_failure_probe",
        "pass_fail_checks",
        "trace_fields",
        "public_release_gate",
    }
    covered_trace_fields = set()
    for gate in matrix["gates"]:
        assert gate_required <= set(gate), gate["id"]
        assert gate["slide_role"] in EXPECTED_RHYTHM_ROLES
        assert set(gate["visual_primitive_ids"]) <= primitive_ids
        assert set(gate["visual_module_ids"]) <= module_ids
        assert set(gate["required_code_modules"]) <= code_module_ids
        assert set(gate["trace_fields"]) <= set(trace_contract["per_slide_required_fields"])
        assert_contains(gate["boxiness_failure_probe"], ["box"])
        covered_trace_fields |= set(gate["trace_fields"])
    assert EXPECTED_RUN2_9_TRACE_FIELDS <= covered_trace_fields

    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    run2_9_stages = [
        "repair_run2_9_visual_primitives",
        "select_run2_9_executable_visual_modules",
        "apply_run2_9_visual_gate_matrix",
    ]
    for stage_id in run2_9_stages:
        assert stage_id in workflow_stage_ids
        assert workflow_stage_ids.index(stage_id) < workflow_stage_ids.index("generate_code_first_ppt")
    assert workflow_stage_ids.index(run2_9_stages[0]) < workflow_stage_ids.index(run2_9_stages[1])
    assert workflow_stage_ids.index(run2_9_stages[1]) < workflow_stage_ids.index(run2_9_stages[2])
    assert_contains(
        json.dumps(workflow),
        [
            "run2_9_visual_primitive_repair.json",
            "run2_9_executable_visual_modules.json",
            "run2_9_visual_gate_matrix.json",
            "visual primitive",
            "boxiness",
        ],
    )


def test_run2_10_has_visual_system_sources_memory_and_gate_matrix() -> None:
    sources_path = PACK / "run2_10_visual_system_sources.json"
    memory_path = PACK / "run2_10_visual_system_memory.json"
    matrix_path = PACK / "run2_10_visual_system_gate_matrix.json"
    trace_contract_path = PACK / "results" / "trace_manifest_contract.json"
    workflow_path = PACK / "skill_workflow.json"

    assert sources_path.exists(), "missing Run 2.10 visual-system sources"
    assert memory_path.exists(), "missing Run 2.10 visual-system memory"
    assert matrix_path.exists(), "missing Run 2.10 visual-system gate matrix"

    sources = load_json(sources_path)
    memory = load_json(memory_path)
    matrix = load_json(matrix_path)
    trace_contract = load_json(trace_contract_path)
    workflow = load_json(workflow_path)

    assert sources["status"] == "run2_10_visual_system_sources_public_blocked"
    assert memory["status"] == "run2_10_visual_system_memory_public_blocked"
    assert matrix["status"] == "run2_10_visual_system_gate_matrix_public_blocked"
    assert sources["storage_policy"]["raw_media"] == "forbidden"
    assert sources["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert matrix["stage_policy"] == "repeat_same_five_layers_not_run3"

    source_ids = {item["id"] for item in sources["sources"]}
    memory_ids = {item["visual_system_id"] for item in memory["visual_systems"]}
    assert EXPECTED_RUN2_10_SOURCE_IDS <= source_ids
    assert EXPECTED_RUN2_10_MEMORY_IDS <= memory_ids
    assert EXPECTED_RUN2_10_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])

    required_source_fields = {
        "id",
        "source_ids",
        "reference_type",
        "allowed_use",
        "visual_system_direction",
        "typography_observation",
        "spatial_composition_observation",
        "asset_strategy_observation",
        "motion_or_sequence_observation",
        "climax_grammar_observation",
        "native_ppt_implication",
        "anti_copy_boundary",
        "public_demo_probe",
        "release_boundary",
    }
    for source in sources["sources"]:
        assert required_source_fields <= set(source), source["id"]
        assert source["allowed_use"] == "derived_observations_only"
        assert_contains(source["native_ppt_implication"], ["native", "editable"])
        for field_value in iter_string_values(source):
            lowered = field_value.lower()
            for marker in RUN2_8_FORBIDDEN_MEDIA_MARKERS:
                assert marker not in lowered, f"{source['id']} contains copied media marker {marker!r}"

    required_memory_fields = {
        "visual_system_id",
        "source_record_ids",
        "applicable_slide_roles",
        "typography_contract",
        "composition_contract",
        "asset_strategy_contract",
        "motion_sequence_contract",
        "native_ppt_module_implications",
        "forbidden_sameness_patterns",
        "public_demo_first_read_probe",
        "anti_copy_boundary",
        "release_boundary",
    }
    for entry in memory["visual_systems"]:
        assert required_memory_fields <= set(entry), entry["visual_system_id"]
        assert set(entry["source_record_ids"]) <= source_ids
        assert set(entry["applicable_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert_mentions_any(
            " ".join(entry["forbidden_sameness_patterns"]),
            {"rectangle", "same visual family", "palette-only", "dashboard"},
        )

    gate_required_fields = {
        "id",
        "slide_role",
        "visual_system_source_ids",
        "visual_system_memory_ids",
        "required_code_modules",
        "visual_delta_from_run2_9",
        "sameness_failure_probe",
        "public_demo_first_read_probe",
        "shape_count_budget",
        "asymmetry_whitespace_rule",
        "trace_fields",
        "public_release_gate",
    }
    covered_trace_fields = set()
    for gate in matrix["gates"]:
        assert gate_required_fields <= set(gate), gate["id"]
        assert gate["slide_role"] in EXPECTED_RHYTHM_ROLES
        assert set(gate["visual_system_source_ids"]) <= source_ids
        assert set(gate["visual_system_memory_ids"]) <= memory_ids
        assert set(gate["trace_fields"]) <= set(trace_contract["per_slide_required_fields"])
        assert_contains(gate["sameness_failure_probe"], ["Run 2.9"])
        assert_contains(gate["asymmetry_whitespace_rule"], ["asymmetry", "whitespace"])
        assert gate["shape_count_budget"]["max_native_shapes"] <= 72
        covered_trace_fields |= set(gate["trace_fields"])
    assert EXPECTED_RUN2_10_TRACE_FIELDS <= covered_trace_fields

    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    run2_10_stages = [
        "select_run2_10_visual_system_sources",
        "compile_run2_10_visual_system_memory",
        "apply_run2_10_visual_system_gate_matrix",
    ]
    for stage_id in run2_10_stages:
        assert stage_id in workflow_stage_ids
        assert workflow_stage_ids.index(stage_id) < workflow_stage_ids.index("generate_code_first_ppt")
    assert workflow_stage_ids.index(run2_10_stages[0]) < workflow_stage_ids.index(run2_10_stages[1])
    assert workflow_stage_ids.index(run2_10_stages[1]) < workflow_stage_ids.index(run2_10_stages[2])


def test_run2_11_data_workflow_audit_artifact_has_required_chains() -> None:
    audit_path = PACK / "results" / "run2_11_data_workflow_audit.json"
    assert audit_path.exists(), "missing Run 2.11 data/workflow audit"

    audit = load_json(audit_path)
    assert EXPECTED_RUN2_11_AUDIT_FIELDS <= set(audit)
    assert audit["status"] == "run2_11_data_workflow_audit_public_blocked"
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["audit_scope"]["creates_new_ppt_deck"] is False
    assert audit["audit_scope"]["primary_quality_target"] == "data_workflow_evidence"

    chains = audit["chain_records"]
    assert chains, "audit must contain source-to-trace chains"

    run28_decomposition_units_by_id = {
        unit["id"]: unit for unit in load_json(PACK / "run2_8_tutorial_decomposition.json")["units"]
    }
    trace_fields_by_run = {
        "2.8": {
            "decomposition_ids": "run2_8_decomposition_unit_ids",
            "memory_ids": "run2_8_memory_binding_ids",
            "gate_ids": "run2_8_gate_matrix_ids",
            "code_ids": "run2_8_code_binding_ids",
        },
        "2.9": {
            "decomposition_ids": "run2_9_visual_primitive_ids",
            "memory_ids": "run2_9_visual_module_ids",
            "gate_ids": "run2_9_gate_matrix_ids",
            "code_ids": "run2_9_code_module_ids",
        },
        "2.10": {
            "source_ids": "run2_10_visual_system_source_ids",
            "memory_ids": "run2_10_visual_system_memory_ids",
            "gate_ids": "run2_10_gate_matrix_ids",
            "code_ids": "run2_10_code_module_ids",
        },
    }
    required_non_empty_chain_fields_by_run = {
        "2.8": {"source_ids", "decomposition_ids", "memory_ids", "gate_ids"},
        "2.9": {"decomposition_ids", "memory_ids", "gate_ids"},
        "2.10": {"source_ids", "memory_ids", "gate_ids"},
    }
    collected_run_ids = set()
    for chain in chains:
        assert {
            "chain_id",
            "run_id",
            "layer",
            "source_ids",
            "decomposition_ids",
            "memory_ids",
            "gate_ids",
            "required_code_module_ids",
            "actual_code_module_ids",
            "slide_roles",
            "trace_manifest_paths",
            "control_boundary",
            "status",
            "reason",
            "next_fix",
        } <= set(chain), chain.get("chain_id")
        assert chain["status"] in EXPECTED_RUN2_11_CHAIN_STATUSES
        assert chain["run_id"] in EXPECTED_RUN2_11_RUN_IDS
        collected_run_ids.add(chain["run_id"])
        if chain["status"] in {"weak", "missing", "blocked"}:
            assert chain["next_fix"], chain["chain_id"]
        if chain["status"] == "pass":
            assert chain["required_code_module_ids"], chain["chain_id"]
            assert chain["actual_code_module_ids"], chain["chain_id"]
            assert set(chain["required_code_module_ids"]) <= set(chain["actual_code_module_ids"])
            for field in required_non_empty_chain_fields_by_run[chain["run_id"]]:
                assert chain[field], f"{chain['chain_id']} missing {field}"
            assert chain["trace_manifest_paths"], chain["chain_id"]
            trace_values = {
                chain_field: set()
                for chain_field in trace_fields_by_run[chain["run_id"]]
            }
            for relative_path in chain["trace_manifest_paths"]:
                trace_path = ROOT / relative_path
                assert trace_path.exists(), relative_path
                trace = load_json(trace_path)
                for slide in trace.get("slides", []):
                    for chain_field, trace_field in trace_fields_by_run[chain["run_id"]].items():
                        trace_values[chain_field].update(slide.get(trace_field, []))
            for chain_field, actual_ids_from_trace in trace_values.items():
                if chain_field == "code_ids":
                    continue
                assert set(chain[chain_field]) <= actual_ids_from_trace
            if chain["run_id"] == "2.8":
                source_record_ids_from_decomposition = {
                    source_record_id
                    for decomposition_id in chain["decomposition_ids"]
                    for source_record_id in run28_decomposition_units_by_id[decomposition_id][
                        "source_record_ids"
                    ]
                }
                assert set(chain["source_ids"]) <= source_record_ids_from_decomposition
            assert set(chain["actual_code_module_ids"]) <= trace_values["code_ids"]
            assert set(chain["required_code_module_ids"]) <= trace_values["code_ids"]

    assert EXPECTED_RUN2_11_RUN_IDS <= collected_run_ids
    assert any(chain["run_id"] == "2.8" and chain["status"] == "pass" for chain in chains)
    assert any(chain["run_id"] == "2.9" and chain["status"] == "pass" for chain in chains)
    assert any(chain["run_id"] == "2.10" and chain["status"] == "pass" for chain in chains)


def test_run2_11_audit_references_existing_data_memory_gate_and_trace_fields() -> None:
    audit = load_json(PACK / "results" / "run2_11_data_workflow_audit.json")
    workflow = load_json(PACK / "skill_workflow.json")
    run27_sources = load_json(PACK / "run2_7_multimodal_source_records.json")
    run28_decomp = load_json(PACK / "run2_8_tutorial_decomposition.json")
    run28_memory = load_json(PACK / "run2_8_executable_design_memory.json")
    run28_gate = load_json(PACK / "run2_8_workflow_gate_matrix.json")
    run29_primitives = load_json(PACK / "run2_9_visual_primitive_repair.json")
    run29_modules = load_json(PACK / "run2_9_executable_visual_modules.json")
    run29_gate = load_json(PACK / "run2_9_visual_gate_matrix.json")
    run210_sources = load_json(PACK / "run2_10_visual_system_sources.json")
    run210_memory = load_json(PACK / "run2_10_visual_system_memory.json")
    run210_gate = load_json(PACK / "run2_10_visual_system_gate_matrix.json")

    assert audit["source_inventory"] == {
        "run2_7_source_records": len(run27_sources["records"]),
        "run2_8_tutorial_decomposition_units": len(run28_decomp["units"]),
        "run2_9_visual_primitives": len(run29_primitives["primitive_repairs"]),
        "run2_10_visual_system_sources": len(run210_sources["sources"]),
        "run2_10_visual_system_memory_records": len(run210_memory["visual_systems"]),
    }
    assert audit["workflow_inventory"] == {
        "skill_workflow_stages": 31,
        "run2_8_workflow_gates": len(run28_gate["gates"]),
        "run2_9_visual_gates": len(run29_gate["gates"]),
        "run2_10_visual_system_gates": len(run210_gate["gates"]),
    }
    assert audit["workflow_inventory"]["skill_workflow_stages"] <= len(workflow["stages"])

    known_source_ids = {record["id"] for record in run27_sources["records"]}
    known_decomposition_ids = {unit["id"] for unit in run28_decomp["units"]}
    known_memory_ids = {binding["id"] for binding in run28_memory["bindings"]}
    known_gate_ids = {gate["id"] for gate in run28_gate["gates"]}
    known_run29_primitive_ids = {item["id"] for item in run29_primitives["primitive_repairs"]}
    known_run29_module_ids = {item["id"] for item in run29_modules["modules"]}
    known_run29_gate_ids = {gate["id"] for gate in run29_gate["gates"]}
    known_run210_source_ids = {item["id"] for item in run210_sources["sources"]}
    known_run210_memory_ids = {item["visual_system_id"] for item in run210_memory["visual_systems"]}
    known_run210_gate_ids = {gate["id"] for gate in run210_gate["gates"]}

    for chain in audit["chain_records"]:
        if chain["run_id"] == "2.8":
            assert set(chain["source_ids"]) <= known_source_ids
            assert set(chain["decomposition_ids"]) <= known_decomposition_ids
            assert set(chain["memory_ids"]) <= known_memory_ids
            assert set(chain["gate_ids"]) <= known_gate_ids
        elif chain["run_id"] == "2.9":
            assert chain["source_ids"] == []
            assert set(chain["decomposition_ids"]) <= known_run29_primitive_ids
            assert set(chain["memory_ids"]) <= known_run29_module_ids
            assert set(chain["gate_ids"]) <= known_run29_gate_ids
        elif chain["run_id"] == "2.10":
            assert set(chain["source_ids"]) <= known_run210_source_ids
            assert chain["decomposition_ids"] == []
            assert set(chain["memory_ids"]) <= known_run210_memory_ids
            assert set(chain["gate_ids"]) <= known_run210_gate_ids


def test_run2_11_audit_records_trace_evidence_and_control_boundaries() -> None:
    audit = load_json(PACK / "results" / "run2_11_data_workflow_audit.json")

    trace_evidence = audit["arm_trace_evidence"]
    assert {"run2_8_full_skill", "run2_9_full_skill", "run2_10_full_skill"} <= set(trace_evidence)

    assert trace_evidence["run2_8_full_skill"]["trace_origin"] == "actual_native_module_calls"
    assert trace_evidence["run2_9_full_skill"]["trace_origin"] == "actual_native_visual_module_calls"
    assert trace_evidence["run2_10_full_skill"]["trace_origin"] == "actual_native_visual_module_calls"

    controls = audit["negative_control_checks"]
    control_arms = {item["arm_role"] for item in controls}
    assert EXPECTED_RUN2_11_CONTROL_ARMS <= control_arms
    for check in controls:
        assert check["status"] in {"pass", "weak", "missing", "blocked"}
        assert check["forbidden_fields"]
        assert check["observed_boundary"]


def test_run2_11_audit_is_embedded_in_html_viewer(tmp_path: Path) -> None:
    presentations_dir = tmp_path / "presentations"
    presentations_dir.mkdir()
    out = presentations_dir / "ppt-run-viewer.html"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_ppt_run_html_viewer.py",
            "--presentations-dir",
            str(presentations_dir),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    body = out.read_text(encoding="utf-8")
    assert "Data/Workflow Audit" in body
    assert 'data-view="audit"' in body
    assert "run2_11_data_workflow_audit_public_blocked" in body
    assert "Source-to-slide chains" in body


def test_run2_12_has_thick_multimodal_evidence_records() -> None:
    evidence_path = PACK / "run2_12_thick_multimodal_evidence.json"
    assert evidence_path.exists(), "missing Run 2.12 thick multimodal evidence"

    evidence = load_json(evidence_path)
    sources = load_json(PACK / "sources.json")
    source_ids = {source["id"] for source in sources["sources"]}
    source_urls = {source["id"]: source["url"] for source in sources["sources"]}

    assert evidence["status"] == "run2_12_thick_multimodal_evidence_public_blocked"
    assert evidence["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert evidence["audit_response_to"] == "run2_11_data_workflow_chain_gate"
    assert evidence["storage_policy"]["raw_media"] == "forbidden"
    assert evidence["run_scope"]["creates_new_ppt_deck"] is False

    records = evidence["records"]
    assert EXPECTED_RUN2_12_EVIDENCE_IDS <= {record["id"] for record in records}
    covered_modalities = {modality for record in records for modality in record["modality_mix"]}
    assert EXPECTED_MULTIMODAL_MODALITIES <= covered_modalities

    for record in records:
        assert EXPECTED_RUN2_12_EVIDENCE_FIELDS <= set(record), record["id"]
        assert record["source_ids"]
        assert set(record["source_ids"]) <= source_ids
        assert record["source_urls"]
        assert record["verified_accessed_on"] == "2026-06-03"
        assert set(record["modality_mix"]) <= EXPECTED_MULTIMODAL_MODALITIES
        assert len(record["frame_or_visual_observations"]) >= 2
        assert len(record["spoken_or_text_claim_paraphrases"]) >= 1
        assert len(record["native_ppt_code_obligations"]) >= 2
        assert len(record["workflow_gate_obligations"]) >= 2
        assert record["memory_seed_targets"]
        assert_contains(record["anti_copy_boundary"], ["do not copy"])
        assert_contains(record["release_boundary"], ["public_blocked"])
        for source_url in record["source_urls"]:
            assert source_url["source_id"] in record["source_ids"]
            assert source_url["url"] == source_urls[source_url["source_id"]]
            assert source_url["retrieval_status"] == "verified_public_page"
        locator = record["segment_locator"]
        assert {"locator_type", "public_locator", "derived_only_note"} <= set(locator)
        assert_contains(locator["derived_only_note"], ["derived", "no raw media"])


def test_run2_12_memory_and_workflow_gate_seeds_are_referentially_integrated() -> None:
    evidence = load_json(PACK / "run2_12_thick_multimodal_evidence.json")
    memory = load_json(PACK / "run2_12_design_memory_seed.json")
    gate_seed = load_json(PACK / "run2_12_workflow_gate_seed.json")
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    evidence_ids = {record["id"] for record in evidence["records"]}
    memory_ids = {record["id"] for record in memory["memory_seeds"]}
    trace_fields = set(trace_contract["per_slide_required_fields"])

    assert memory["status"] == "run2_12_design_memory_seed_public_blocked"
    assert memory["derived_from"] == "run2_12_thick_multimodal_evidence.json"
    assert memory["run_scope"]["creates_new_ppt_deck"] is False
    assert EXPECTED_RUN2_12_MEMORY_IDS <= memory_ids
    for record in memory["memory_seeds"]:
        assert EXPECTED_RUN2_12_MEMORY_FIELDS <= set(record), record["id"]
        assert set(record["evidence_record_ids"]) <= evidence_ids
        assert set(record["applies_to_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert record["design_constraints"]
        assert_contains(json.dumps(record["native_ppt_contract"]), ["native", "editable"])
        assert set(record["required_trace_fields"]) <= trace_fields
        assert_contains(record["release_boundary"], ["public_blocked"])

    assert gate_seed["status"] == "run2_12_workflow_gate_seed_public_blocked"
    assert gate_seed["gate_policy"] == "required_before_next_four_arm_rerun"
    assert gate_seed["run_scope"]["creates_new_ppt_deck"] is False
    assert EXPECTED_RUN2_12_GATE_IDS <= {gate["id"] for gate in gate_seed["gates"]}
    for gate in gate_seed["gates"]:
        assert EXPECTED_RUN2_12_GATE_FIELDS <= set(gate), gate["id"]
        assert set(gate["evidence_record_ids"]) <= evidence_ids
        assert set(gate["memory_seed_ids"]) <= memory_ids
        assert set(gate["slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert gate["pass_fail_checks"]
        assert gate["required_before_next_rerun"] is True
        assert set(gate["trace_fields"]) <= trace_fields
        assert_contains(gate["release_boundary"], ["public_blocked"])

    workflow_text = json.dumps(workflow)
    assert_contains(
        workflow_text,
        [
            "run2_12_thick_multimodal_evidence.json",
            "run2_12_design_memory_seed.json",
            "run2_12_workflow_gate_seed.json",
            "required before next four-arm rerun",
        ],
    )


def test_run2_four_arm_isolation_mentions_multimodal_and_target_boundaries() -> None:
    prompt_only = (PACK / "generation_briefs" / "prompt_only.md").read_text(encoding="utf-8")
    run1_5 = (PACK / "generation_briefs" / "run1_5_skill.md").read_text(encoding="utf-8")
    run2 = (PACK / "generation_briefs" / "run2_skill.md").read_text(encoding="utf-8")
    bad = (PACK / "generation_briefs" / "bad_aesthetic_memory.md").read_text(encoding="utf-8")

    assert_contains(
        prompt_only, ["Do not use multimodal database", "visual learning targets", "visual target components"]
    )
    assert_contains(prompt_only, ["video demo beat map", "motion learning targets", "presentation sequence components"])
    assert_contains(
        run1_5,
        ["Do not use Run 2.2 multimodal database", "visual learning targets", "visual target components"],
    )
    assert_contains(
        run1_5, ["video_demo_beat_map.json", "motion_learning_targets.json", "presentation_sequence_components.json"]
    )
    assert_contains(
        run2,
        [
            "multimodal_database.json",
            "visual_learning_targets.json",
            "visual_target_components.json",
            "video_demo_beat_map.json",
            "motion_learning_targets.json",
            "presentation_sequence_components.json",
            "production_reference_decompositions.json",
            "aesthetic_memory_v2.json",
            "visual_production_modules.json",
        ],
    )
    assert_contains(
        bad,
        [
            "multimodal_database.json",
            "visual_learning_targets.json",
            "visual_target_components.json",
            "video_demo_beat_map.json",
            "motion_learning_targets.json",
            "presentation_sequence_components.json",
        ],
    )
    assert_contains(bad, ["Good aesthetic_memory.json", "Good slide_archetypes.json"])


def test_run2_cards_have_executable_extraction_units() -> None:
    required = {"unit_id", "source_anchor", "derived_rule", "slide_role", "execution_guard", "qa_probe"}
    allowed_roles = {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}

    cards = [load_json(path) for path in [*json_files("source_cards"), *json_files("video_cards")]]

    for card in cards:
        units = card.get("extraction_units")
        assert isinstance(units, list) and len(units) >= 2, card["card_id"]
        for unit in units:
            assert required <= set(unit), card["card_id"]
            assert unit["slide_role"] in allowed_roles
            for key in required - {"slide_role"}:
                assert isinstance(unit[key], str) and unit[key].strip(), f"{card['card_id']} {key}"


def test_run2_evidence_memory_has_required_claims() -> None:
    memory = load_json(PACK / "evidence_memory.json")
    claims = memory["claims"]

    assert len(claims) >= 6
    assert EXPECTED_CLAIM_IDS <= {claim["id"] for claim in claims}
    for claim in claims:
        assert claim["source_card_ids"]
        assert claim["qa_checks"]


def test_run2_asset_memory_has_required_editable_assets() -> None:
    memory = load_json(PACK / "asset_memory.json")
    assets = memory["assets"]

    assert len(assets) >= 4
    assert EXPECTED_ASSET_IDS <= {asset["id"] for asset in assets}
    for asset in assets:
        assert asset["provenance_state"]
        assert asset["text_editability"]
        assert asset["render_risks"]
        assert asset["accessibility_risks"]


def test_run2_aesthetic_memory_has_required_public_demo_moves() -> None:
    memory = load_json(PACK / "aesthetic_memory.json")
    moves = {move["aesthetic_move"] for move in memory["moves"]}

    assert EXPECTED_MOVES <= moves
    assert len(memory["moves"]) >= 8
    for move in memory["moves"]:
        assert move["source_card_ids"]
        assert move["negative_rules"]
        assert move["density_budget"]["max_words"] <= 80
        assert move["rhythm_role"] in {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}


def test_run2_narrative_spine_is_six_slide_public_demo() -> None:
    spine = load_json(PACK / "narrative_spine.json")

    assert spine["deck_length"] == 6
    assert [slide["rhythm_role"] for slide in spine["slides"]] == [
        "cover",
        "setup",
        "contrast",
        "proof",
        "climax",
        "close",
    ]


def test_run2_skill_is_a_staged_deck_director() -> None:
    body = (PACK / "vulca_ppt_skill.md").read_text(encoding="utf-8")

    assert_contains(
        body,
        [
            "compile the multimodal database",
            "select the narrative spine",
            "compile evidence memory",
            "compile aesthetic memory",
            "select assets",
            "generate code-first PPT modules",
            "run structural QA",
            "run aesthetic QA",
            "repair",
            "release decision",
        ],
    )
    assert_contains(body, ["move detail to appendix", "not compress the same content into smaller text"])
    assert_contains(
        body,
        [
            "trace manifest",
            "per slide",
            "Selected multimodal record ids",
            "density counts",
            "deleted or routed content",
            "asset provenance",
            "QA outcomes",
        ],
    )
    assert_contains(body, ["text, image-reference, video, audio, transcript, and interaction anchors"])
    assert_contains(body, ["visual_learning_targets.json", "before/after visual deltas", "slide mini-previews"])
    assert_contains(body, ["visual_target_components.json", "before/after thumbnail", "visual component ids"])
    assert_contains(
        body,
        [
            "video_demo_beat_map.json",
            "motion_learning_targets.json",
            "presentation_sequence_components.json",
            "motion target ids",
            "sequence component ids",
        ],
    )
    assert_contains(
        body,
        [
            "production_reference_decompositions.json",
            "aesthetic_memory_v2.json",
            "visual_production_modules.json",
            "production modules",
            "run2_10_visual_system_sources.json",
            "run2_10_visual_system_memory.json",
            "run2_10_visual_system_gate_matrix.json",
            "sameness failure probes",
        ],
    )


def test_run2_skill_workflow_is_declarative_and_gated() -> None:
    workflow = load_json(PACK / "skill_workflow.json")
    stage_ids = [stage["id"] for stage in workflow["stages"]]

    assert workflow["workflow_type"] == "declarative_skill_director"
    assert workflow["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert workflow["five_layer_loop"] == [
        "real_commercial_case",
        "multimodal_tutorial_case_data",
        "evidence_aesthetic_asset_memory",
        "skill_workflow",
        "rerun_and_evaluation",
    ]
    assert stage_ids == [
        "read_commercial_case",
        "compile_multimodal_database",
        "compile_evidence_memory",
        "compile_aesthetic_memory",
        "compile_production_reference_decompositions",
        "compile_aesthetic_memory_v2",
        "select_slide_archetypes",
        "select_commercial_usecase",
        "select_aesthetic_benchmarks",
        "select_theme_typography_spacing_policy",
        "select_visual_repair_policy",
        "select_run2_7_design_memory",
        "select_visual_production_modules",
        "decompose_run2_8_tutorial_video_units",
        "select_run2_8_executable_design_memory",
        "apply_run2_8_workflow_gate_matrix",
        "repair_run2_9_visual_primitives",
        "select_run2_9_executable_visual_modules",
        "apply_run2_9_visual_gate_matrix",
        "select_run2_10_visual_system_sources",
        "compile_run2_10_visual_system_memory",
        "apply_run2_10_visual_system_gate_matrix",
        "apply_run2_15_layout_selector_gate_matrix",
        "generate_code_first_ppt",
        "run_structural_and_aesthetic_qa",
        "recommend_repairs",
        "refresh_trace_qa_outcomes",
        "emit_release_decision",
        "expand_run2_18_multimodal_evidence",
        "expand_run2_18_design_memory",
        "apply_run2_18_workflow_gate_expansion",
        "lock_run2_24_single_usecase_content_memory",
        "compile_run2_24_visual_evidence_asset_memory",
        "apply_run2_24_content_visual_workflow_gates",
        "compile_run2_35_visual_evidence_asset_realism_memory",
        "compile_run2_35_editorial_composition_memory",
        "apply_run2_35_visual_evidence_workflow_gates",
    ]
    assert [stage["order"] for stage in workflow["stages"]] == list(range(1, 38))
    assert workflow["repair_triggers"]
    workflow_text = json.dumps(workflow)
    assert "multimodal_database.json" in workflow_text
    assert "visual_learning_targets.json" in workflow_text
    assert "visual_target_components.json" in workflow_text
    assert "video_demo_beat_map.json" in workflow_text
    assert "motion_learning_targets.json" in workflow_text
    assert "presentation_sequence_components.json" in workflow_text
    assert "production_reference_decompositions.json" in workflow_text
    assert "aesthetic_memory_v2.json" in workflow_text
    assert "visual_production_modules.json" in workflow_text
    assert "commercial_usecase_bank.json" in workflow_text
    assert "run2_7_commercial_usecase.json" in workflow_text
    assert "run2_7_multimodal_source_records.json" in workflow_text
    assert "run2_7_design_memory.json" in workflow_text
    assert "run2_7_workflow_policy.json" in workflow_text
    assert "run2_8_tutorial_decomposition.json" in workflow_text
    assert "run2_8_executable_design_memory.json" in workflow_text
    assert "run2_8_workflow_gate_matrix.json" in workflow_text
    assert "run2_9_visual_primitive_repair.json" in workflow_text
    assert "run2_9_executable_visual_modules.json" in workflow_text
    assert "run2_9_visual_gate_matrix.json" in workflow_text
    assert "run2_10_visual_system_sources.json" in workflow_text
    assert "run2_10_visual_system_memory.json" in workflow_text
    assert "run2_10_visual_system_gate_matrix.json" in workflow_text
    assert "run2_24_single_usecase_content_memory.json" in workflow_text
    assert "run2_24_visual_evidence_asset_memory.json" in workflow_text
    assert "run2_24_content_visual_workflow_gates.json" in workflow_text
    assert "run2_35_visual_evidence_asset_realism_memory.json" in workflow_text
    assert "run2_35_editorial_composition_memory.json" in workflow_text
    assert "run2_35_visual_evidence_workflow_gates.json" in workflow_text
    assert "run2_15_layout_selector_sources.json" in workflow_text
    assert "run2_15_layout_module_memory.json" in workflow_text
    assert "run2_15_layout_selector_gate_matrix.json" in workflow_text
    assert "aesthetic_benchmark_bank.json" in workflow_text
    assert "workflow_decision_policy.json" in workflow_text
    assert "visual_repair_policy.json" in workflow_text
    assert_contains(workflow_text, ["all required modalities covered", "no copied source media stored"])
    assert_contains(
        workflow_text, ["visual targets reference valid multimodal anchors", "selected visual learning targets"]
    )
    assert_contains(workflow_text, ["native visual components", "selected visual target components"])
    assert_contains(workflow_text, ["motion grammar", "selected motion targets", "sequence components"])
    assert_contains(workflow_text, ["production reference", "aesthetic memory v2", "visual production modules"])
    assert_contains(workflow_text, ["commercial usecase", "aesthetic benchmark", "theme policy"])
    assert_contains(workflow_text, ["visual repair", "Run 2.6R"])
    assert_contains(workflow_text, ["fallback", "visual validation"])
    assert_contains(workflow_text, ["schema validation", "aesthetic memory constraints"])
    assert_contains(workflow_text, ["provenance metadata", "copyright boundary"])
    assert_contains(workflow_text, ["visual system", "sameness failure", "asymmetry", "whitespace"])
    assert_contains(workflow_text, ["layout module selector", "text resilience", "trace visibility", "product theater realism"])
    assert "public_blocked" in workflow["release_decisions"]
    assert "public_ready" not in workflow["release_decisions"]
    assert "automated repair without human gate" not in normalize(json.dumps(workflow))


def test_run2_generation_briefs_define_four_arms() -> None:
    briefs = {path.stem for path in (PACK / "generation_briefs").glob("*.md") if path.name != "README.md"}

    assert briefs == EXPECTED_ARMS
    readme = (PACK / "generation_briefs" / "README.md").read_text(encoding="utf-8")
    assert_contains(readme, ["runtime isolation", "fresh prompt", "separate output directory", "forbidden input"])
    for arm in EXPECTED_ARMS:
        body = (PACK / "generation_briefs" / f"{arm}.md").read_text(encoding="utf-8")
        assert_contains(body, ["Allowed Inputs", "Forbidden Inputs", "Trace Output"])

    assert_contains(
        (PACK / "generation_briefs" / "prompt_only.md").read_text(encoding="utf-8"), ["commercial brief only"]
    )
    assert_contains((PACK / "generation_briefs" / "run1_5_skill.md").read_text(encoding="utf-8"), ["evidence-heavy"])
    assert_contains(
        (PACK / "generation_briefs" / "run2_skill.md").read_text(encoding="utf-8"),
        [
            "multimodal database",
            "visual learning targets",
            "visual target components",
            "video demo beat map",
            "motion learning targets",
            "presentation sequence components",
            "production reference decompositions",
            "aesthetic memory v2",
            "visual production modules",
            "aesthetic memory",
        ],
    )
    assert_contains(
        (PACK / "generation_briefs" / "bad_aesthetic_memory.md").read_text(encoding="utf-8"), ["negative control"]
    )


def test_run2_4_generator_preserves_motion_trace_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_4_arms.mjs").read_text(encoding="utf-8")

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_4_full_skill",
            "bad_aesthetic_memory",
            "no_cross_arm_reuse",
            "layout JSON",
            "contact sheets",
        ],
    )
    assert 'if (!["run2_4_full_skill", "bad_aesthetic_memory"].includes(arm.armId)) return [];' in body
    assert 'const goodOrBad = ["run2_4_full_skill", "bad_aesthetic_memory"].includes(arm.armId);' in body
    assert re.search(r"multimodal_record_ids:\s*goodOrBad\s*\?", body)
    assert re.search(r"visual_learning_target_ids:\s*goodOrBad\s*\?", body)
    assert re.search(r"visual_component_ids:\s*goodOrBad\s*\?", body)
    assert "video_beat_ids: motion.video_beat_ids ?? []" in body
    assert "motion_target_ids: motion.motion_target_ids ?? []" in body
    assert "sequence_component_ids: motion.sequence_component_ids ?? []" in body
    assert "ordered_reveal_steps: sequenceSteps.map" in body
    assert_contains(
        body,
        [
            "beat_opening_scale_reset",
            "motion_target_climax_scale_emphasis",
            "sequence_component_release_gate",
        ],
    )


def test_run2_5_generator_consumes_production_data_and_preserves_control_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_5_arms.mjs").read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_5_full_skill", "bad_aesthetic_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else body.index("function sequenceStepsForSlide", start)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_production_inputs = [
        "production_reference_decompositions.json",
        "aesthetic_memory_v2.json",
        "visual_production_modules.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_5_full_skill",
            "bad_aesthetic_memory",
            "production_reference_decompositions.json",
            "aesthetic_memory_v2.json",
            "visual_production_modules.json",
            "no_cross_arm_reuse",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_5_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_5_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_aesthetic_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_aesthetic_memory"), "forbidden:", "palette:")

    for term in restricted_production_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
    assert "production_reference_decompositions.json" in bad_allowed
    assert "aesthetic_memory_v2.json" not in bad_allowed
    assert "visual_production_modules.json" not in bad_allowed
    assert "aesthetic_memory_v2.json" in bad_forbidden
    assert "visual_production_modules.json" in bad_forbidden
    assert 'if (!["run2_5_full_skill", "bad_aesthetic_memory"].includes(arm.armId)) return [];' in body
    assert 'const productionEligible = ["run2_5_full_skill", "bad_aesthetic_memory"].includes(arm.armId);' in body
    assert 'const fullProduction = arm.armId === "run2_5_full_skill";' in body
    assert re.search(r"production_reference_ids:\s*productionEligible\s*\?", body)
    assert re.search(r"aesthetic_memory_v2_ids:\s*fullProduction\s*\?", body)
    assert re.search(r"visual_production_module_ids:\s*fullProduction\s*\?", body)
    assert "fallback_policy:" in body
    assert "visual_validation_probe:" in body
    assert_contains(
        body,
        [
            "module_cinematic_cover_field",
            "module_editorial_before_after_delta",
            "module_proof_route_choreography",
            "module_system_mini_preview",
            "module_climax_hero_object",
            "module_release_handoff_gate",
        ],
    )


def test_run2_6_generator_consumes_workflow_policy_and_preserves_control_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_6_arms.mjs").read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_6_full_skill", "bad_aesthetic_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else body.index("function sequenceStepsForSlide", start)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_workflow_inputs = [
        "commercial_usecase_bank.json",
        "aesthetic_benchmark_bank.json",
        "workflow_decision_policy.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_6_full_skill",
            "bad_aesthetic_memory",
            "commercial_usecase_bank.json",
            "aesthetic_benchmark_bank.json",
            "workflow_decision_policy.json",
            "source_brand_sanitization",
            "no_cross_arm_reuse",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_6_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_6_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_aesthetic_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_aesthetic_memory"), "forbidden:", "palette:")

    for term in restricted_workflow_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
    assert "commercial_usecase_bank.json" in bad_allowed
    assert "aesthetic_benchmark_bank.json" not in bad_allowed
    assert "workflow_decision_policy.json" not in bad_allowed
    assert "aesthetic_benchmark_bank.json" in bad_forbidden
    assert "workflow_decision_policy.json" in bad_forbidden
    assert "visual_repair_policy.json" not in full_allowed
    assert "run2_6r_visual_repair_full_skill" not in body
    assert 'const workflowEligible = ["run2_6_full_skill", "bad_aesthetic_memory"].includes(arm.armId);' in body
    assert 'const fullWorkflow = arm.armId === "run2_6_full_skill";' in body
    assert re.search(r"commercial_usecase_id:\s*workflowEligible\s*\?", body)
    assert re.search(r"aesthetic_benchmark_ids:\s*fullWorkflow\s*\?", body)
    assert re.search(r"theme_policy_id:\s*fullWorkflow\s*\?", body)
    assert re.search(r"typography_system_id:\s*fullWorkflow\s*\?", body)
    assert re.search(r"spacing_token_set_id:\s*fullWorkflow\s*\?", body)
    assert re.search(r"workflow_decision_ids:\s*fullWorkflow\s*\?", body)
    assert "source_brand_sanitization:" in body
    assert "visual_repair_policy_ids: []" in body
    assert 'visual_delta_from_run2_5: "not-applicable; existing Run 2.6 generator does not apply visual repair policy"' in body
    assert (
        'visual_repair_validation_probe: "not-applicable; existing Run 2.6 generator does not select visual repair"'
        in body
    )


def test_run2_6r_generator_consumes_visual_repair_policy_and_preserves_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_6r_visual_repair_arms.mjs").read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_6r_visual_repair_full_skill", "bad_aesthetic_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else body.index("function sequenceStepsForSlide", start)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    assert_contains(
        body,
        [
            "run2_6r_visual_repair_full_skill",
            "visual_repair_policy.json",
            "visual_repair_policy_ids",
            "visual_delta_from_run2_5",
            "visual_repair_validation_probe",
            "renderFullRepair",
            "drawEditorialClimaxSpread",
            "no_cross_arm_reuse",
        ],
    )
    assert "function renderFull(" not in body
    assert re.search(
        r'if \(arm\.armId === "run2_6r_visual_repair_full_skill"\) \{\s*'
        r"renderFullRepair\(slide, spec, arm, n\);\s*"
        r"\} else \{\s*"
        r"renderControl\(slide, spec, arm\);",
        body,
    )
    repair_start = body.index("function renderFullRepair")
    repair_end = body.index("function renderSlide", repair_start)
    repair_body = body[repair_start:repair_end]
    assert re.search(
        r'if \(spec\.role === "climax"\) \{\s*'
        r"drawEditorialClimaxSpread\(slide, arm\);\s*"
        r"return;\s*"
        r"\}\s*"
        r"simpleTitle\(slide, spec, arm, true\);",
        repair_body,
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_6r_visual_repair_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_6r_visual_repair_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_aesthetic_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_aesthetic_memory"), "forbidden:", "palette:")

    assert "visual_repair_policy.json" not in prompt_allowed
    assert "visual_repair_policy.json" in prompt_forbidden
    assert "visual_repair_policy.json" not in run1_allowed
    assert "visual_repair_policy.json" in run1_forbidden
    assert "visual_repair_policy.json" in full_allowed
    assert "visual_repair_policy.json" not in full_forbidden
    assert "commercial_usecase_bank.json" in bad_allowed
    assert "visual_repair_policy.json" not in bad_allowed
    assert "visual_repair_policy.json" in bad_forbidden
    assert 'const repairEligible = arm.armId === "run2_6r_visual_repair_full_skill";' in body
    assert re.search(r"visual_repair_policy_ids:\s*repairEligible\s*\?", body)
    assert re.search(r"visual_delta_from_run2_5:\s*repairEligible\s*\?", body)
    assert re.search(r"visual_repair_validation_probe:\s*repairEligible\s*\?", body)


def test_run2_7_generator_consumes_design_memory_and_preserves_control_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_7_data_workflow_arms.mjs").read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_7_full_skill", "bad_workflow_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else body.index("function sequenceStepsForSlide", start)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_7_inputs = [
        "run2_7_commercial_usecase.json",
        "run2_7_multimodal_source_records.json",
        "run2_7_design_memory.json",
        "run2_7_workflow_policy.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_7_full_skill",
            "bad_workflow_memory",
            "run2_7_commercial_usecase.json",
            "run2_7_multimodal_source_records.json",
            "run2_7_design_memory.json",
            "run2_7_workflow_policy.json",
            "renderRun27Full",
            "drawRun27Climax",
            "assertRun27MemorySelfCheck",
            "run27VisualSelfCheck",
            "run27Eligible",
            "run2_7_design_memory_ids",
            "run2_7_delta_from_run2_6r",
            "no_cross_arm_reuse",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_7_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_7_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_workflow_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_workflow_memory"), "forbidden:", "palette:")

    for term in restricted_run2_7_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_7_commercial_usecase.json" in bad_allowed
    assert "run2_7_multimodal_source_records.json" in bad_allowed
    assert "run2_7_design_memory.json" not in bad_allowed
    assert "run2_7_workflow_policy.json" not in bad_allowed
    assert "run2_7_design_memory.json" in bad_forbidden
    assert "run2_7_workflow_policy.json" in bad_forbidden
    assert re.search(r"run2_7_usecase_id:\s*run27Eligible\s*\?", body)
    assert re.search(r"run2_7_source_record_ids:\s*run27Eligible\s*\?", body)
    assert re.search(r"run2_7_design_memory_ids:\s*fullRun27\s*\?", body)
    assert re.search(r"run2_7_workflow_decision_ids:\s*fullRun27\s*\?", body)
    assert re.search(r"run2_7_delta_from_run2_6r:\s*fullRun27\s*\?", body)
    assert re.search(r"run2_7_quality_gate:\s*fullRun27\s*\?", body)
    assert (PACK / "generation_briefs" / "bad_aesthetic_memory.md").exists()
    assert "bad_workflow_memory.md" not in body
    assert 'if (armId === "bad_workflow_memory") return "bad_aesthetic_memory";' in body
    assert re.search(r"generation_brief:\s*`\$\{pack\}/generation_briefs/\$\{generationBriefArmId\(arm\.armId\)\}\.md`", body)


def test_run2_8_generator_uses_executable_memory_and_preserves_boundaries() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_8_executable_memory_arms.mjs"
    assert script_path.exists(), "missing Run 2.8 executable-memory generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_8_full_skill", "bad_memory_schema"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_8_inputs = [
        "run2_8_tutorial_decomposition.json",
        "run2_8_executable_design_memory.json",
        "run2_8_workflow_gate_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_8_full_skill",
            "bad_memory_schema",
            "run2_8_tutorial_decomposition.json",
            "run2_8_executable_design_memory.json",
            "run2_8_workflow_gate_matrix.json",
            "renderRun28Full",
            "drawRun28Climax",
            "run28MemoryBindingsByRole",
            "assertRun28GateMatrixSelfCheck",
            "run2_8_memory_binding_ids",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_8_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_8_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_memory_schema"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_memory_schema"), "forbidden:", "palette:")

    for term in restricted_run2_8_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_8_tutorial_decomposition.json" in bad_allowed
    assert "run2_8_executable_design_memory.json" not in bad_allowed
    assert "run2_8_workflow_gate_matrix.json" not in bad_allowed
    assert "run2_8_executable_design_memory.json" in bad_forbidden
    assert "run2_8_workflow_gate_matrix.json" in bad_forbidden
    assert 'const fullRun28 = arm.armId === "run2_8_full_skill";' in body
    for field in EXPECTED_RUN2_8_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun28\s*\?", body), field
    assert not re.search(r"run2_8_memory_binding_ids:\s*bad", body)
    for function_name in [
        "drawRun28TypeScale",
        "drawRun28SpacingZones",
        "drawRun28BeforeAfterDelta",
        "drawRun28WorkflowGate",
        "drawRun28Climax",
    ]:
        assert f'registerNativeModule(metrics, "{function_name}")' in body
    assert "const actualCodeBindingIds = Array.from(roleMetrics.codeBindingIds);" in body
    assert "run2_8_code_binding_ids: fullRun28" in body
    assert "actualCodeBindingIds" in body
    assert "gate objects ${metrics.gateObjects}" in body
    assert "metrics.workflowObjects > layoutBudget.max_gate_objects" not in body
    assert "full_arm_contract_preview_not_rendered" in body
    assert "full_arm_native_generator_rendered" in body
    render_start = body.index("function renderRun28FullSlide")
    contrast_start = body.index('} else if (spec.role === "contrast")', render_start)
    proof_start = body.index('} else if (spec.role === "proof")', render_start)
    climax_start = body.index('} else if (spec.role === "climax")', render_start)
    close_start = body.index('} else {', climax_start)
    contrast_block = body[contrast_start:proof_start]
    proof_block = body[proof_start:climax_start]
    climax_block = body[climax_start:close_start]
    assert "drawRun28SpacingZones" in contrast_block
    assert "drawRun28BeforeAfterDelta" in contrast_block
    assert "drawRun28BeforeAfterDelta" in proof_block
    assert "drawRun28SpacingZones" in proof_block
    assert "drawRun28WorkflowGate" in proof_block
    assert "drawRun28Climax(slide, heroBinding, arm, spec, metrics, { typeBinding })" in climax_block


def test_run2_9_generator_uses_visual_primitive_modules_and_preserves_boundaries() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_9_visual_primitive_arms.mjs"
    assert script_path.exists(), "missing Run 2.9 visual-primitive generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_9_full_skill", "bad_visual_primitive_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_9_inputs = [
        "run2_9_visual_primitive_repair.json",
        "run2_9_executable_visual_modules.json",
        "run2_9_visual_gate_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_9_full_skill",
            "bad_visual_primitive_memory",
            "run2_9_visual_primitive_repair.json",
            "run2_9_executable_visual_modules.json",
            "run2_9_visual_gate_matrix.json",
            "drawRun29EditorialSpread",
            "drawRun29LayeredProductSurface",
            "drawRun29MotionStoryboard",
            "drawRun29ClimaxStage",
            "drawRun29TypographicField",
            "run29VisualModulesByRole",
            "assertRun29VisualGateSelfCheck",
            "registerVisualModule",
            "run2_9_code_module_ids",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_9_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_9_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_visual_primitive_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_visual_primitive_memory"), "forbidden:", "palette:")

    for term in restricted_run2_9_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_9_visual_primitive_repair.json" in bad_allowed
    assert "run2_9_executable_visual_modules.json" not in bad_allowed
    assert "run2_9_visual_gate_matrix.json" not in bad_allowed
    assert "run2_9_executable_visual_modules.json" in bad_forbidden
    assert "run2_9_visual_gate_matrix.json" in bad_forbidden
    assert 'const fullRun29 = arm.armId === "run2_9_full_skill";' in body
    for field in EXPECTED_RUN2_9_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun29\s*\?", body), field
    assert "const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);" in body
    assert "run2_9_code_module_ids: fullRun29" in body
    for function_name in [
        "drawRun29EditorialSpread",
        "drawRun29LayeredProductSurface",
        "drawRun29MotionStoryboard",
        "drawRun29ClimaxStage",
        "drawRun29TypographicField",
    ]:
        assert f'registerVisualModule(metrics, "{function_name}")' in body
    render_start = body.index("function renderRun29FullSlide")
    setup_start = body.index('} else if (spec.role === "setup")', render_start)
    contrast_start = body.index('} else if (spec.role === "contrast")', render_start)
    proof_start = body.index('} else if (spec.role === "proof")', render_start)
    climax_start = body.index('} else if (spec.role === "climax")', render_start)
    close_start = body.index('} else {', climax_start)
    cover_block = body[render_start:setup_start]
    setup_block = body[setup_start:contrast_start]
    proof_block = body[proof_start:climax_start]
    climax_block = body[climax_start:close_start]
    assert "drawRun29TypographicField" in cover_block
    assert "drawRun29EditorialSpread" in cover_block
    assert "drawRun29LayeredProductSurface" in setup_block
    assert "drawRun29MotionStoryboard" in proof_block
    assert "drawRun29ClimaxStage" in climax_block


def test_run2_10_generator_uses_visual_system_modules_and_preserves_boundaries() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_10_visual_system_arms.mjs"
    assert script_path.exists(), "missing Run 2.10 visual-system generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_10_full_skill", "bad_visual_system_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_10_inputs = [
        "run2_10_visual_system_sources.json",
        "run2_10_visual_system_memory.json",
        "run2_10_visual_system_gate_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_10_full_skill",
            "bad_visual_system_memory",
            "drawRun210FullBleedVisualField",
            "drawRun210ProductTheater",
            "drawRun210KineticSequence",
            "drawRun210EditorialTypeSystem",
            "drawRun210NonRectangularProofPath",
            "drawRun210CinematicClimax",
            "run210VisualSystemsByRole",
            "assertRun210VisualSystemGateSelfCheck",
            "registerRun210VisualModule",
            "run2_10_code_module_ids",
            "run2_10_shape_count_budget",
            "run2_10_asymmetry_whitespace_rule",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_10_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_10_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_visual_system_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_visual_system_memory"), "forbidden:", "palette:")

    for term in restricted_run2_10_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_10_visual_system_sources.json" in bad_allowed
    assert "run2_10_visual_system_memory.json" not in bad_allowed
    assert "run2_10_visual_system_gate_matrix.json" not in bad_allowed
    assert "run2_10_visual_system_memory.json" in bad_forbidden
    assert "run2_10_visual_system_gate_matrix.json" in bad_forbidden
    assert 'const fullRun210 = arm.armId === "run2_10_full_skill";' in body
    for field in EXPECTED_RUN2_10_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun210\s*\?", body), field
    assert "const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);" in body
    assert "run2_10_code_module_ids: fullRun210" in body
    for function_name in [
        "drawRun210FullBleedVisualField",
        "drawRun210ProductTheater",
        "drawRun210KineticSequence",
        "drawRun210EditorialTypeSystem",
        "drawRun210NonRectangularProofPath",
        "drawRun210CinematicClimax",
    ]:
        assert f'registerRun210VisualModule(metrics, "{function_name}")' in body
    render_start = body.index("function renderRun210FullSlide")
    setup_start = body.index('} else if (spec.role === "setup")', render_start)
    contrast_start = body.index('} else if (spec.role === "contrast")', render_start)
    proof_start = body.index('} else if (spec.role === "proof")', render_start)
    climax_start = body.index('} else if (spec.role === "climax")', render_start)
    close_start = body.index('} else {', climax_start)
    cover_block = body[render_start:setup_start]
    setup_block = body[setup_start:contrast_start]
    contrast_block = body[contrast_start:proof_start]
    proof_block = body[proof_start:climax_start]
    climax_block = body[climax_start:close_start]
    assert "drawRun210EditorialTypeSystem" in cover_block
    assert "drawRun210FullBleedVisualField" in cover_block
    assert "drawRun210ProductTheater" in setup_block
    assert "drawRun210NonRectangularProofPath" in setup_block
    assert "drawRun210FullBleedVisualField" in contrast_block
    assert "drawRun210NonRectangularProofPath" in contrast_block
    assert "drawRun210ProductTheater" in proof_block
    assert "drawRun210KineticSequence" in proof_block
    assert "drawRun210CinematicClimax" in climax_block
    assert "drawRun210KineticSequence" in climax_block


def test_run2_13_generator_uses_thick_data_seeds_and_preserves_boundaries() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_13_thick_data_arms.mjs"
    assert script_path.exists(), "missing Run 2.13 thick-data generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_13_full_skill", "bad_thick_data_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_12_inputs = [
        "run2_12_thick_multimodal_evidence.json",
        "run2_12_design_memory_seed.json",
        "run2_12_workflow_gate_seed.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_13_full_skill",
            "bad_thick_data_memory",
            "drawRun213LaunchArcRoute",
            "drawRun213TypeWhitespaceSystem",
            "drawRun213ProductDemoSequence",
            "drawRun213MetricClimaxObject",
            "drawRun213WorkflowGateRail",
            "run213MemorySeedsByRole",
            "assertRun213ThickDataGateSelfCheck",
            "registerRun213Module",
            "run2_12_code_module_ids",
            "run2_12_density_whitespace_gate",
            "run2_12_demo_sequence_gate",
            "run2_12_climax_object_gate",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_13_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_13_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_thick_data_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_thick_data_memory"), "forbidden:", "palette:")

    for term in restricted_run2_12_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_12_thick_multimodal_evidence.json" in bad_allowed
    assert "run2_12_design_memory_seed.json" not in bad_allowed
    assert "run2_12_workflow_gate_seed.json" not in bad_allowed
    assert "skill_workflow.json" not in bad_allowed
    assert "run2_12_design_memory_seed.json" in bad_forbidden
    assert "run2_12_workflow_gate_seed.json" in bad_forbidden
    assert "skill_workflow.json" in bad_forbidden
    assert 'const fullRun213 = arm.armId === "run2_13_full_skill";' in body
    for field in EXPECTED_RUN2_13_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun213\s*\?", body), field
    assert "const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);" in body
    assert "run2_12_code_module_ids: fullRun213" in body
    for function_name in [
        "drawRun213LaunchArcRoute",
        "drawRun213TypeWhitespaceSystem",
        "drawRun213ProductDemoSequence",
        "drawRun213MetricClimaxObject",
        "drawRun213WorkflowGateRail",
    ]:
        assert f'registerRun213Module(metrics, "{function_name}")' in body
    render_start = body.index("function renderRun213FullSlide")
    setup_start = body.index('} else if (spec.role === "setup")', render_start)
    contrast_start = body.index('} else if (spec.role === "contrast")', render_start)
    proof_start = body.index('} else if (spec.role === "proof")', render_start)
    climax_start = body.index('} else if (spec.role === "climax")', render_start)
    close_start = body.index('} else {', climax_start)
    cover_block = body[render_start:setup_start]
    setup_block = body[setup_start:contrast_start]
    proof_block = body[proof_start:climax_start]
    climax_block = body[climax_start:close_start]
    close_block = body[close_start:]
    assert "drawRun213LaunchArcRoute" in cover_block
    assert "drawRun213TypeWhitespaceSystem" in cover_block
    assert "drawRun213LaunchArcRoute" in setup_block
    assert "drawRun213WorkflowGateRail" in setup_block
    assert "drawRun213ProductDemoSequence" in proof_block
    assert "drawRun213WorkflowGateRail" in proof_block
    assert "drawRun213MetricClimaxObject" in climax_block
    assert "drawRun213ProductDemoSequence" in climax_block
    assert "drawRun213WorkflowGateRail" in close_block


def test_run2_14_generator_hides_trace_inside_210_aesthetic_shell() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_14_aesthetic_trace_arms.mjs"
    assert script_path.exists(), "missing Run 2.14 aesthetic-trace generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_14_full_skill", "bad_visible_workflow_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    run2_12_inputs = [
        "run2_12_thick_multimodal_evidence.json",
        "run2_12_design_memory_seed.json",
        "run2_12_workflow_gate_seed.json",
    ]
    run2_10_aesthetic_inputs = [
        "run2_10_visual_system_sources.json",
        "run2_10_visual_system_memory.json",
        "run2_10_visual_system_gate_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_14_full_skill",
            "bad_visible_workflow_memory",
            "drawRun214PresentationShell",
            "drawRun214CinematicProductTheater",
            "drawRun214HiddenWorkflowRoute",
            "drawRun214MetricRevealStage",
            "drawRun214QuietReleaseHandoff",
            "assertRun214AestheticTraceGateSelfCheck",
            "registerRun214Module",
            "manifest_only_trace_public_surface",
            "visible_workflow_suppression",
            "run2_14_code_module_ids",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_14_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_14_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_visible_workflow_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_visible_workflow_memory"), "forbidden:", "palette:")

    for term in [*run2_12_inputs, *run2_10_aesthetic_inputs]:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden

    for term in [*run2_12_inputs, *run2_10_aesthetic_inputs]:
        assert term in full_allowed
        assert term not in full_forbidden

    for term in run2_12_inputs:
        assert term in bad_allowed
        assert term not in bad_forbidden
    for term in run2_10_aesthetic_inputs:
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun214 = arm.armId === "run2_14_full_skill";' in body
    for field in EXPECTED_RUN2_14_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun214\s*\?", body), field
    assert "const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);" in body
    assert "run2_14_code_module_ids: fullRun214" in body
    for function_name in [
        "drawRun214PresentationShell",
        "drawRun214CinematicProductTheater",
        "drawRun214HiddenWorkflowRoute",
        "drawRun214MetricRevealStage",
        "drawRun214QuietReleaseHandoff",
    ]:
        assert f'registerRun214Module(metrics, "{function_name}")' in body
    render_start = body.index("function renderRun214FullSlide")
    setup_start = body.index('} else if (spec.role === "setup")', render_start)
    contrast_start = body.index('} else if (spec.role === "contrast")', render_start)
    proof_start = body.index('} else if (spec.role === "proof")', render_start)
    climax_start = body.index('} else if (spec.role === "climax")', render_start)
    close_start = body.index('} else {', climax_start)
    cover_block = body[render_start:setup_start]
    setup_block = body[setup_start:contrast_start]
    proof_block = body[proof_start:climax_start]
    climax_block = body[climax_start:close_start]
    close_block = body[close_start:]
    assert "drawRun214PresentationShell" in cover_block
    assert "drawRun214HiddenWorkflowRoute" in cover_block
    assert "drawRun214CinematicProductTheater" in setup_block
    assert "drawRun214HiddenWorkflowRoute" in setup_block
    assert "drawRun214CinematicProductTheater" in proof_block
    assert "drawRun214HiddenWorkflowRoute" in proof_block
    assert "drawRun214MetricRevealStage" in climax_block
    assert "drawRun214QuietReleaseHandoff" in close_block


def test_run2_15_layout_selector_artifacts_define_reusable_workflow() -> None:
    sources = load_json(PACK / "run2_15_layout_selector_sources.json")
    memory = load_json(PACK / "run2_15_layout_module_memory.json")
    gates = load_json(PACK / "run2_15_layout_selector_gate_matrix.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    assert sources["status"] == "run2_15_layout_selector_sources_ready"
    assert memory["status"] == "run2_15_layout_module_memory_ready"
    assert gates["status"] == "run2_15_layout_selector_gate_matrix_ready"

    source_records = sources["records"]
    memory_records = memory["modules"]
    gate_records = gates["gates"]

    assert len(source_records) >= 6
    assert len(memory_records) >= 6
    assert len(gate_records) >= 5

    required_source_fields = {
        "record_id",
        "source_family",
        "derived_from_run_ids",
        "modality_mix",
        "commercial_need",
        "design_observation",
        "layout_selector_obligation",
        "typography_obligation",
        "spacing_obligation",
        "product_theater_obligation",
        "motion_beat_obligation",
        "trace_visibility_obligation",
        "anti_copy_boundary",
    }
    for record in source_records:
        assert required_source_fields <= record.keys()
        assert record["anti_copy_boundary"]
        assert record["layout_selector_obligation"]
        assert not record.get("raw_media_path")
        assert not record.get("copied_source_layout")

    source_ids = {record["record_id"] for record in source_records}
    required_module_families = {
        "editorial_cover_field",
        "product_theater_stage",
        "before_after_route",
        "metric_reveal_stage",
        "quiet_release_handoff",
        "dense_evidence_compression",
    }
    module_families = {module["module_family"] for module in memory_records}
    assert required_module_families <= module_families

    required_memory_fields = {
        "module_id",
        "module_family",
        "slide_roles",
        "source_record_ids",
        "selection_trigger",
        "composition_contract",
        "typography_contract",
        "spacing_contract",
        "asset_contract",
        "trace_visibility_contract",
        "fallback_contract",
        "native_ppt_obligations",
        "forbidden_patterns",
    }
    for module in memory_records:
        assert required_memory_fields <= module.keys()
        assert set(module["source_record_ids"]) <= source_ids
        assert module["slide_roles"]
        assert module["trace_visibility_contract"] == "manifest_viewer_qa_only_for_public_surface"
        assert module["native_ppt_obligations"]

    module_ids = {module["module_id"] for module in memory_records}
    required_gate_ids = {
        "gate_2_15_role_to_module_selection",
        "gate_2_15_text_resilience",
        "gate_2_15_trace_hidden_from_surface",
        "gate_2_15_product_theater_realism",
        "gate_2_15_metric_reveal_climax",
        "gate_2_15_bad_selector_control_boundary",
    }
    gate_ids = {gate["gate_id"] for gate in gate_records}
    assert required_gate_ids <= gate_ids
    trace_fields = set(trace_contract["per_slide_required_fields"])
    assert EXPECTED_RUN2_15_TRACE_FIELDS <= trace_fields

    for gate in gate_records:
        assert set(gate["candidate_module_ids"]) <= module_ids
        assert gate["required_selector_inputs"]
        assert gate["selection_rules"]
        assert gate["rejection_rules"]
        assert gate["trace_fields"]
        assert set(gate["trace_fields"]) <= trace_fields
        assert "run2_15_selected_layout_module_ids" in gate["trace_fields"]
        assert gate["text_resilience_probe"]
        assert gate["bad_control_probe"]


def test_run2_16_generator_uses_run2_15_selector_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_16_selector_rerun_arms.mjs"
    assert script_path.exists(), "missing Run 2.16 selector-driven rerun generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_16_full_skill", "bad_selector_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    run2_15_selector_inputs = [
        "run2_15_layout_selector_sources.json",
        "run2_15_layout_module_memory.json",
        "run2_15_layout_selector_gate_matrix.json",
    ]
    run2_14_aesthetic_inputs = [
        "run2_10_visual_system_sources.json",
        "run2_10_visual_system_memory.json",
        "run2_10_visual_system_gate_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_16_full_skill",
            "bad_selector_memory",
            "validateRun215SelectorSchemas",
            "assertArmInputBoundaries",
            "readRun216SelectorJsonForArm",
            "selectRun215LayoutModulesForSlide",
            "assertRun216SelectorGateSelfCheck",
            "drawRun216EditorialCoverField",
            "drawRun216ProductTheaterStage",
            "drawRun216BeforeAfterRoute",
            "drawRun216MetricRevealStage",
            "drawRun216QuietReleaseHandoff",
            "drawRun216DenseEvidenceCompression",
            "manifest_viewer_qa_only_for_public_surface",
            "selector_gate_matrix_executed_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_16_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_16_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_selector_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_selector_memory"), "forbidden:", "palette:")

    for term in [*run2_15_selector_inputs, *run2_14_aesthetic_inputs]:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_15_layout_selector_sources.json" in bad_allowed
    assert "run2_15_layout_module_memory.json" not in bad_allowed
    assert "run2_15_layout_selector_gate_matrix.json" not in bad_allowed
    assert "run2_15_layout_module_memory.json" in bad_forbidden
    assert "run2_15_layout_selector_gate_matrix.json" in bad_forbidden

    assert 'const fullRun216 = arm.armId === "run2_16_full_skill";' in body
    for field in EXPECTED_RUN2_15_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun216\s*\?", body), field
    for function_name in [
        "drawRun216EditorialCoverField",
        "drawRun216ProductTheaterStage",
        "drawRun216BeforeAfterRoute",
        "drawRun216MetricRevealStage",
        "drawRun216QuietReleaseHandoff",
        "drawRun216DenseEvidenceCompression",
    ]:
        assert f'registerRun216Module(metrics, "{function_name}")' in body
    assert "throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`)" in body
    assert "run2_15_layout_module_memory.json" in arm_block("bad_selector_memory")
    assert "run2_15_layout_selector_gate_matrix.json" in arm_block("bad_selector_memory")


def test_run2_16_selector_runtime_guards_block_bad_arm_and_select_gates() -> None:
    node_script = """
import fs from "node:fs";
import path from "node:path";
const mod = await import("./scripts/generate_ppt_run2_16_selector_rerun_arms.mjs");
const badArm = mod.armSpecs.find((arm) => arm.armId === "bad_selector_memory");
const fullArm = mod.armSpecs.find((arm) => arm.armId === "run2_16_full_skill");
let blocked = false;
try {
  mod.readRun216SelectorJsonForArm(badArm, mod.RUN2_16_INPUTS.selectorGateMatrix);
} catch (error) {
  blocked = String(error.message).includes("input boundary does not permit reading");
}
if (!blocked) throw new Error("bad selector arm was able to read selector gate matrix");
const root = process.cwd();
const sources = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_16_INPUTS.selectorSources), "utf8"));
const memory = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_16_INPUTS.selectorMemory), "utf8"));
const gates = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_16_INPUTS.selectorGateMatrix), "utf8"));
mod.validateRun215SelectorSchemas(sources, memory, gates);
const climax = mod.selectRun215LayoutModulesForSlide("climax", memory, gates);
const moduleIds = climax.modules.map((item) => item.module_id);
const gateIds = climax.gates.map((item) => item.gate_id);
if (!moduleIds.includes("module_2_15_metric_reveal_stage")) throw new Error("climax did not select metric reveal module");
if (!gateIds.includes("gate_2_15_metric_reveal_climax")) throw new Error("climax did not consume metric reveal gate");
if (!fullArm.allowed.includes(mod.RUN2_16_INPUTS.selectorGateMatrix)) throw new Error("full arm does not allow selector gate matrix");
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_19_generator_consumes_run2_18_thickness_pack_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_19_thickness_rerun_arms.mjs"
    assert script_path.exists(), "missing Run 2.19 thickness rerun generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_19_full_skill", "bad_thickness_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    run2_18_inputs = [
        "run2_18_multimodal_evidence_expansion.json",
        "run2_18_design_memory_expansion.json",
        "run2_18_workflow_gate_expansion.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_19_full_skill",
            "bad_thickness_memory",
            "validateRun218ThicknessSchemas",
            "assertArmInputBoundaries",
            "readRun219ThicknessJsonForArm",
            "selectRun218ThicknessForSlide",
            "assertRun219ThicknessGateSelfCheck",
            "drawRun219LaunchIdentityField",
            "drawRun219ProductSurfaceTheater",
            "drawRun219DemoSequenceRoute",
            "drawRun219MetricClimaxObject",
            "drawRun219DensityGate",
            "thickness_pack_executed_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_19_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_19_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_thickness_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_thickness_memory"), "forbidden:", "palette:")

    for term in run2_18_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_18_multimodal_evidence_expansion.json" in bad_allowed
    assert "run2_18_design_memory_expansion.json" not in bad_allowed
    assert "run2_18_workflow_gate_expansion.json" not in bad_allowed
    assert "run2_18_design_memory_expansion.json" in bad_forbidden
    assert "run2_18_workflow_gate_expansion.json" in bad_forbidden

    assert 'const fullRun219 = arm.armId === "run2_19_full_skill";' in body
    for field in EXPECTED_RUN2_19_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun219\s*\?", body), field
    for function_name in [
        "drawRun219LaunchIdentityField",
        "drawRun219ProductSurfaceTheater",
        "drawRun219DemoSequenceRoute",
        "drawRun219MetricClimaxObject",
        "drawRun219DensityGate",
    ]:
        assert f'registerRun219Module(metrics, "{function_name}")' in body


def test_run2_19_thickness_runtime_guards_block_bad_arm_and_select_gates() -> None:
    node_script = """
import fs from "node:fs";
import path from "node:path";
const mod = await import("./scripts/generate_ppt_run2_19_thickness_rerun_arms.mjs");
const badArm = mod.armSpecs.find((arm) => arm.armId === "bad_thickness_memory");
const fullArm = mod.armSpecs.find((arm) => arm.armId === "run2_19_full_skill");
let blocked = false;
try {
  mod.readRun219ThicknessJsonForArm(badArm, mod.RUN2_19_INPUTS.workflowGates);
} catch (error) {
  blocked = String(error.message).includes("input boundary does not permit reading");
}
if (!blocked) throw new Error("bad thickness arm was able to read workflow gates");
const root = process.cwd();
const evidence = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_19_INPUTS.evidence), "utf8"));
const memory = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_19_INPUTS.memory), "utf8"));
const gates = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_19_INPUTS.workflowGates), "utf8"));
mod.validateRun218ThicknessSchemas(evidence, memory, gates);
const climax = mod.selectRun218ThicknessForSlide("climax", evidence, memory, gates);
const memoryIds = climax.memories.map((item) => item.memory_id);
const gateIds = climax.gates.map((item) => item.gate_id);
if (!memoryIds.includes("memory_2_18_metric_climax_object")) throw new Error("climax did not select metric climax memory");
if (!gateIds.includes("gate_2_18_metric_climax_selection")) throw new Error("climax did not consume metric climax gate");
if (!fullArm.allowed.includes(mod.RUN2_19_INPUTS.workflowGates)) throw new Error("full arm does not allow Run 2.18 workflow gates");
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_19_records_thickness_rerun_result() -> None:
    result = (PACK / "results" / "run2_19_thickness_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_19_thickness_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["run_id"] == "2.19"
    assert result_json["rerun"]["best_internal_arm"] == "run2_19_full_skill"
    assert result_json["rerun"]["best_internal_arm_verdict"] == "thickness_pack_executed_before_native_ppt_generation"
    assert result_json["input_chain"]["evidence"] == "docs/product/ppt-run2-data-skill-quality/run2_18_multimodal_evidence_expansion.json"
    assert result_json["input_chain"]["memory"] == "docs/product/ppt-run2-data-skill-quality/run2_18_design_memory_expansion.json"
    assert result_json["input_chain"]["workflow_gates"] == "docs/product/ppt-run2-data-skill-quality/run2_18_workflow_gate_expansion.json"
    assert result_json["control_boundary"]["bad_thickness_memory"].startswith("evidence_only")
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-19-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert_contains(
        result,
        [
            "Run 2.19",
            "Run 2.18 thickness pack",
            "four-arm rerun",
            "bad_thickness_memory",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_19_generated_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.19",
            "ppt-run2-19-prompt-only",
            "ppt-run2-19-run1-5-skill",
            "ppt-run2-19-full-vulca",
            "ppt-run2-19-bad-thickness-memory",
            "run2_19_thickness_rerun_result.json",
        ],
    )


def test_run2_20_trace_effectiveness_audit_script_computes_2_19_data_use(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "audit_ppt_run2_20_trace_effectiveness.py"
    assert script_path.exists(), "missing Run 2.20 trace effectiveness audit script"

    result_json = tmp_path / "run2_20_trace_effectiveness_audit.json"
    result_md = tmp_path / "run2_20_trace_effectiveness_audit.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    audit = load_json(result_json)
    report = result_md.read_text(encoding="utf-8")

    assert audit["status"] == "run2_20_trace_effectiveness_audit_public_blocked"
    assert audit["run_id"] == "2.20"
    assert audit["source_generated_run"] == "2.19"
    assert audit["creates_new_ppt_deck"] is False
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["public_ready"] is False

    coverage = audit["trace_effectiveness"]
    assert coverage["full_arm"]["slide_count"] == 6
    assert coverage["full_arm"]["evidence_records_selected"] == coverage["inventory"]["run2_18_evidence_records"] == 8
    assert coverage["full_arm"]["memory_records_selected"] == coverage["inventory"]["run2_18_memory_records"] == 6
    assert coverage["full_arm"]["workflow_gates_selected"] == coverage["inventory"]["run2_18_workflow_gates"] == 6
    assert coverage["full_arm"]["all_slides_have_memory_gate_and_code"] is True
    assert coverage["full_arm"]["layout_budget_passed_all_slides"] is True
    assert coverage["full_arm"]["selected_code_module_count"] >= 5
    assert not coverage["full_arm"]["unused_evidence_record_ids"]
    assert not coverage["full_arm"]["unused_memory_ids"]
    assert not coverage["full_arm"]["unused_gate_ids"]

    bad = audit["control_boundary"]["bad_thickness_memory"]
    assert bad["uses_evidence_only"] is True
    assert bad["selected_evidence_slide_count"] == 6
    assert bad["selected_memory_ids"] == []
    assert bad["selected_workflow_gate_ids"] == []
    assert bad["selected_code_module_ids"] == []
    assert audit["gate_summary"]["data_workflow_trace_effectiveness_gate"] == "pass_internal_only"
    assert audit["gate_summary"]["public_release_gate"] == "blocked"
    assert "Run 2.20" in report
    assert "trace effectiveness" in report
    assert "Run 2.19" in report
    assert "public blocked" in report


def test_run2_20_records_trace_effectiveness_audit_result() -> None:
    result = (PACK / "results" / "run2_20_trace_effectiveness_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_20_trace_effectiveness_audit.json")

    assert result_json["status"] == "run2_20_trace_effectiveness_audit_public_blocked"
    assert result_json["source_generated_run"] == "2.19"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["trace_effectiveness"]["full_arm"]["all_slides_have_memory_gate_and_code"] is True
    assert result_json["control_boundary"]["bad_thickness_memory"]["uses_evidence_only"] is True
    assert result_json["next_required_action"].startswith("thicken_visual_decision")
    assert_contains(
        result,
        [
            "Run 2.20",
            "trace effectiveness",
            "Run 2.19",
            "Run 2.18 thickness pack",
            "bad_thickness_memory",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_20_trace_effectiveness_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_20_trace_effectiveness_audit.json",
            "Run 2.20 trace effectiveness audit",
            "trace effectiveness",
            "bad_thickness_memory",
        ],
    )


def test_run2_21_builder_writes_visual_decision_memory_artifacts(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "build_ppt_run2_21_visual_decision_memory.py"
    assert script_path.exists(), "missing Run 2.21 visual-decision memory builder"

    result_json = tmp_path / "run2_21_visual_decision_memory_result.json"
    result_md = tmp_path / "run2_21_visual_decision_memory_result.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--out-dir",
            str(tmp_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    decision_memory = load_json(tmp_path / "run2_21_visual_decision_memory.json")
    selector_gates = load_json(tmp_path / "run2_21_per_role_selector_gates.json")
    rejection_matrix = load_json(tmp_path / "run2_21_evidence_rejection_matrix.json")
    result = load_json(result_json)

    assert decision_memory["status"] == "run2_21_visual_decision_memory_ready_public_blocked"
    assert decision_memory["creates_new_ppt_deck"] is False
    assert decision_memory["derived_from"] == [
        "run2_18_multimodal_evidence_expansion.json",
        "run2_18_design_memory_expansion.json",
        "run2_18_workflow_gate_expansion.json",
        "results/run2_20_trace_effectiveness_audit.json",
    ]
    assert len(decision_memory["visual_decision_memory"]) == 6
    all_evidence_ids = {record["record_id"] for record in load_json(PACK / "run2_18_multimodal_evidence_expansion.json")["records"]}
    for record in decision_memory["visual_decision_memory"]:
        assert record["role"] in {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert record["primary_evidence_id"] in all_evidence_ids
        assert 1 <= len(record["secondary_evidence_ids"]) <= 2
        assert set(record["secondary_evidence_ids"]).issubset(all_evidence_ids)
        rejected_ids = {item["evidence_id"] for item in record["rejected_evidence"]}
        assert rejected_ids
        assert rejected_ids.isdisjoint({record["primary_evidence_id"], *record["secondary_evidence_ids"]})
        assert {record["primary_evidence_id"], *record["secondary_evidence_ids"], *rejected_ids} == all_evidence_ids
        assert all(item["reason"] for item in record["rejected_evidence"])
        assert record["selected_memory_ids"]
        assert record["selected_gate_ids"]
        for field in [
            "typography_decision",
            "spacing_decision",
            "composition_decision",
            "proof_object_decision",
            "code_generation_obligation",
            "visual_quality_risk",
            "source_boundary",
        ]:
            assert record[field], f"{record['decision_id']} missing {field}"

    assert selector_gates["status"] == "run2_21_per_role_selector_gates_ready_public_blocked"
    assert len(selector_gates["gates"]) == 6
    for gate in selector_gates["gates"]:
        assert gate["required_primary_evidence_count"] == 1
        assert gate["max_secondary_evidence_count"] == 2
        assert gate["required_visual_decision_memory_id"].startswith("vdm_2_21_")
        assert "run2_21_primary_evidence_id" in gate["required_trace_fields"]
        assert "run2_21_rejected_evidence_reasons" in gate["required_trace_fields"]
        assert gate["public_surface_policy"] == "trace_suppressed_from_public_slide_surface"
        assert gate["release_boundary"].startswith("public_blocked")

    assert rejection_matrix["status"] == "run2_21_evidence_rejection_matrix_ready_public_blocked"
    assert len(rejection_matrix["role_records"]) == 6
    for role_record in rejection_matrix["role_records"]:
        assert role_record["all_evidence_accounted_for"] is True
        assert role_record["primary_evidence_id"] in all_evidence_ids
        assert role_record["rejected_evidence"]
        assert all(item["reason"] for item in role_record["rejected_evidence"])

    assert result["status"] == "run2_21_visual_decision_memory_ready_public_blocked"
    assert result["creates_new_ppt_deck"] is False
    assert result["delivery_artifacts"] == {
        "pptx_paths": [],
        "rendered_slide_paths": [],
        "contact_sheet_paths": [],
        "html_motion_renderer_paths": [],
    }
    assert result["public_ready"] is False
    assert result["next_required_action"].startswith("consume_run2_21_visual_decision_memory")
    assert not list(tmp_path.glob("*.pptx"))


def test_run2_21_records_visual_decision_memory_result() -> None:
    result = (PACK / "results" / "run2_21_visual_decision_memory_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_21_visual_decision_memory_result.json")
    decision_memory = load_json(PACK / "run2_21_visual_decision_memory.json")
    selector_gates = load_json(PACK / "run2_21_per_role_selector_gates.json")
    rejection_matrix = load_json(PACK / "run2_21_evidence_rejection_matrix.json")

    assert result_json["status"] == "run2_21_visual_decision_memory_ready_public_blocked"
    assert result_json["source_audit_run"] == "2.20"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["delivery_artifacts"]["pptx_paths"] == []
    assert result_json["delivery_artifacts"]["rendered_slide_paths"] == []
    assert result_json["artifact_counts"] == {
        "visual_decision_memory": 6,
        "per_role_selector_gates": 6,
        "evidence_rejection_records": 6,
    }
    assert len(decision_memory["visual_decision_memory"]) == 6
    assert len(selector_gates["gates"]) == 6
    assert len(rejection_matrix["role_records"]) == 6
    assert_contains(
        result,
        [
            "Run 2.21",
            "visual-decision memory",
            "per-role selector",
            "evidence rejection matrix",
            "Run 2.20",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_21_visual_decision_memory() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_21_visual_decision_memory.json",
            "run2_21_per_role_selector_gates.json",
            "run2_21_evidence_rejection_matrix.json",
            "run2_21_visual_decision_memory_result.json",
            "Run 2.21 visual-decision memory",
        ],
    )


def test_run2_22_generator_consumes_run2_21_selector_memory_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_22_selector_memory_arms.mjs"
    assert script_path.exists(), "missing Run 2.22 selector-memory rerun generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_22_full_selector_memory", "bad_selector_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    run2_21_inputs = [
        "run2_21_visual_decision_memory.json",
        "run2_21_per_role_selector_gates.json",
        "run2_21_evidence_rejection_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_22_full_selector_memory",
            "bad_selector_memory",
            "validateRun221SelectorSchemas",
            "assertArmInputBoundaries",
            "readRun222SelectorJsonForArm",
            "selectRun221ForSlide",
            "assertRun222SelectorGateSelfCheck",
            "drawRun222CinematicSelectorField",
            "drawRun222ProductTheaterSurface",
            "drawRun222EvidenceRoute",
            "drawRun222ClimaxEditorialStage",
            "selector_memory_executed_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_22_full_selector_memory"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_22_full_selector_memory"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_selector_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_selector_memory"), "forbidden:", "palette:")

    for term in run2_21_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_21_visual_decision_memory.json" in bad_allowed
    assert "run2_21_per_role_selector_gates.json" not in bad_allowed
    assert "run2_21_evidence_rejection_matrix.json" not in bad_allowed
    assert "run2_21_per_role_selector_gates.json" in bad_forbidden
    assert "run2_21_evidence_rejection_matrix.json" in bad_forbidden

    assert 'const fullRun222 = arm.armId === "run2_22_full_selector_memory";' in body
    for field in EXPECTED_RUN2_22_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun222\s*\?", body), field
    for function_name in [
        "drawRun222CinematicSelectorField",
        "drawRun222ProductTheaterSurface",
        "drawRun222EvidenceRoute",
        "drawRun222ClimaxEditorialStage",
    ]:
        assert f'registerRun222Module(metrics, "{function_name}")' in body


def test_run2_22_selector_runtime_guards_block_bad_arm_and_select_role_memory() -> None:
    node_script = """
import fs from "node:fs";
import path from "node:path";
const mod = await import("./scripts/generate_ppt_run2_22_selector_memory_arms.mjs");
const badArm = mod.armSpecs.find((arm) => arm.armId === "bad_selector_memory");
const fullArm = mod.armSpecs.find((arm) => arm.armId === "run2_22_full_selector_memory");
let blocked = false;
try {
  mod.readRun222SelectorJsonForArm(badArm, mod.RUN2_22_INPUTS.selectorGates);
} catch (error) {
  blocked = String(error.message).includes("input boundary does not permit reading");
}
if (!blocked) throw new Error("bad selector arm was able to read Run 2.21 selector gates");
let rejectionBlocked = false;
try {
  mod.readRun222SelectorJsonForArm(badArm, mod.RUN2_22_INPUTS.rejectionMatrix);
} catch (error) {
  rejectionBlocked = String(error.message).includes("input boundary does not permit reading");
}
if (!rejectionBlocked) throw new Error("bad selector arm was able to read Run 2.21 rejection matrix");
const badTrace = mod.traceFor(badArm);
for (const slide of badTrace.slides) {
  if (slide.run2_21_selector_gate_id) throw new Error("bad selector trace leaked selector gate id");
  if ((slide.run2_21_rejected_evidence_reasons || []).length) throw new Error("bad selector trace leaked rejection reasons");
  if ((slide.run2_22_code_module_ids || []).length) throw new Error("bad selector trace leaked Run 2.22 code modules");
}
const root = process.cwd();
const decisionMemory = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_22_INPUTS.decisionMemory), "utf8"));
const selectorGates = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_22_INPUTS.selectorGates), "utf8"));
const rejectionMatrix = JSON.parse(fs.readFileSync(path.join(root, mod.RUN2_22_INPUTS.rejectionMatrix), "utf8"));
mod.validateRun221SelectorSchemas(decisionMemory, selectorGates, rejectionMatrix);
const cover = mod.selectRun221ForSlide("cover", decisionMemory, selectorGates, rejectionMatrix);
if (cover.decision.decision_id !== "vdm_2_21_cover") throw new Error("cover did not select the Run 2.21 cover memory");
if (cover.gate.gate_id !== "gate_2_21_cover_selector") throw new Error("cover did not select the Run 2.21 cover selector gate");
if (cover.decision.primary_evidence_id !== cover.rejection.primary_evidence_id) throw new Error("cover primary evidence mismatch");
if (!fullArm.allowed.includes(mod.RUN2_22_INPUTS.rejectionMatrix)) throw new Error("full arm does not allow Run 2.21 rejection matrix");
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_22_records_selector_rerun_result() -> None:
    result = (PACK / "results" / "run2_22_selector_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_22_selector_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["run_id"] == "2.22"
    assert result_json["rerun"]["best_internal_arm"] == "run2_22_full_selector_memory"
    assert result_json["rerun"]["best_internal_arm_verdict"] == "selector_memory_executed_before_native_ppt_generation"
    assert result_json["input_chain"]["visual_decision_memory"] == "docs/product/ppt-run2-data-skill-quality/run2_21_visual_decision_memory.json"
    assert result_json["input_chain"]["selector_gates"] == "docs/product/ppt-run2-data-skill-quality/run2_21_per_role_selector_gates.json"
    assert result_json["input_chain"]["rejection_matrix"] == "docs/product/ppt-run2-data-skill-quality/run2_21_evidence_rejection_matrix.json"
    assert result_json["control_boundary"]["bad_selector_memory"].startswith("decision_memory_only")
    assert result_json["remaining_public_release_gates"] == [
        "human_visual_review",
        "native_or_cross_platform_render_inspection",
        "motion_or_video_review",
        "source_boundary_review",
        "human_release_approval",
    ]
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-22-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert_contains(
        result,
        [
            "Run 2.22",
            "Run 2.21 visual-decision memory",
            "four-arm rerun",
            "bad_selector_memory",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_22_generated_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.22",
            "ppt-run2-22-prompt-only",
            "ppt-run2-22-run1-5-skill",
            "ppt-run2-22-full-vulca",
            "ppt-run2-22-bad-selector-memory",
            "run2_22_selector_rerun_result.json",
        ],
    )


def test_run2_23_selector_effectiveness_audit_compares_2_19_and_2_22(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "audit_ppt_run2_23_selector_effectiveness.py"
    assert script_path.exists(), "missing Run 2.23 selector effectiveness audit script"

    result_json = tmp_path / "run2_23_selector_effectiveness_audit.json"
    result_md = tmp_path / "run2_23_selector_effectiveness_audit.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    audit = load_json(result_json)
    report = result_md.read_text(encoding="utf-8")

    assert audit["status"] == "run2_23_selector_effectiveness_audit_public_blocked"
    assert audit["run_id"] == "2.23"
    assert audit["source_generated_run"] == "2.22"
    assert audit["comparison_baseline_run"] == "2.19"
    assert audit["source_selector_layer"] == "2.21"
    assert audit["creates_new_ppt_deck"] is False
    assert audit["public_ready"] is False
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"

    selector = audit["selector_effectiveness"]
    assert selector["full_arm"]["arm_id"] == "run2_22_full_selector_memory"
    assert selector["full_arm"]["slide_count"] == 6
    assert selector["full_arm"]["visual_decision_memory_records_selected"] == 6
    assert selector["full_arm"]["selector_gates_selected"] == 6
    assert selector["full_arm"]["all_slides_have_selector_gate_and_code"] is True
    assert selector["full_arm"]["primary_evidence_per_slide_all"] is True
    assert selector["full_arm"]["secondary_evidence_within_cap_all"] is True
    assert selector["full_arm"]["rejection_reasons_present_all"] is True
    assert selector["full_arm"]["public_surface_policy_suppressed_all"] is True
    assert selector["comparison_to_run2_19"]["roles_with_code_module_delta"] >= 5
    assert len(selector["full_arm"]["role_records"]) == 6

    bad = audit["control_boundary"]["bad_selector_memory"]
    assert bad["decision_memory_only"] is True
    assert bad["blocks_selector_gates"] is True
    assert bad["blocks_rejection_matrix"] is True
    assert bad["selected_selector_gate_ids"] == []
    assert bad["selected_rejected_evidence_reasons"] == []
    assert bad["selected_code_module_ids"] == []

    assert len(audit["chain_records"]) == 6
    assert audit["gate_summary"]["selector_memory_gate"] == "pass_internal_only"
    assert audit["gate_summary"]["public_release_gate"] == "blocked"
    assert_contains(
        report,
        [
            "Run 2.23",
            "selector effectiveness",
            "Run 2.22",
            "Run 2.19",
            "bad_selector_memory",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_23_records_selector_effectiveness_audit_result() -> None:
    result = (PACK / "results" / "run2_23_selector_effectiveness_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_23_selector_effectiveness_audit.json")

    assert result_json["status"] == "run2_23_selector_effectiveness_audit_public_blocked"
    assert result_json["source_generated_run"] == "2.22"
    assert result_json["comparison_baseline_run"] == "2.19"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["selector_effectiveness"]["full_arm"]["all_slides_have_selector_gate_and_code"] is True
    assert result_json["control_boundary"]["bad_selector_memory"]["decision_memory_only"] is True
    assert result_json["next_required_action"].startswith("human_review_run2_22_visual_delta")
    assert_contains(
        result,
        [
            "Run 2.23",
            "selector effectiveness",
            "Run 2.22",
            "Run 2.19",
            "bad_selector_memory",
            "public blocked",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_23_selector_effectiveness_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_23_selector_effectiveness_audit.json",
            "Run 2.23 selector effectiveness audit",
            "selector effectiveness",
            "bad_selector_memory",
        ],
    )


def test_run2_24_builder_writes_single_usecase_content_visual_evidence_pack(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "build_ppt_run2_24_single_usecase_content_evidence.py"
    assert script_path.exists(), "missing Run 2.24 single-usecase content/evidence builder"

    result_json = tmp_path / "run2_24_single_usecase_thickening_result.json"
    result_md = tmp_path / "run2_24_single_usecase_thickening_result.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--out-dir",
            str(tmp_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    content_memory = load_json(tmp_path / "run2_24_single_usecase_content_memory.json")
    visual_assets = load_json(tmp_path / "run2_24_visual_evidence_asset_memory.json")
    workflow_gates = load_json(tmp_path / "run2_24_content_visual_workflow_gates.json")
    result = load_json(result_json)
    report = result_md.read_text(encoding="utf-8")

    assert result["status"] == "run2_24_single_usecase_content_visual_evidence_ready_public_blocked"
    assert result["run_id"] == "2.24"
    assert result["source_audit_run"] == "2.23"
    assert result["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert result["creates_new_ppt_deck"] is False
    assert result["public_ready"] is False
    assert result["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result["next_required_action"].startswith("consume_run2_24_single_usecase_pack")
    assert result["delivery_artifacts"] == {
        "pptx_paths": [],
        "rendered_slide_paths": [],
        "contact_sheet_paths": [],
        "html_motion_renderer_paths": [],
    }

    assert content_memory["status"] == "run2_24_single_usecase_content_memory_ready_public_blocked"
    assert content_memory["selected_usecase"]["id"] == "usecase_design_to_production_platform_launch"
    assert content_memory["story_policy"]["single_primary_usecase"] is True
    assert len(content_memory["slide_content_memory"]) == 6
    for record in content_memory["slide_content_memory"]:
        assert record["role"] in {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert record["content_memory_id"].startswith("content_2_24_")
        assert record["headline"]
        assert record["support_line"]
        assert len(record["business_proof_points"]) >= 2
        assert len(record["visual_evidence_slot_ids"]) >= 2
        assert record["trace_fields_required"] == [
            "run2_24_selected_usecase_id",
            "run2_24_content_memory_id",
            "run2_24_visual_evidence_slot_ids",
            "run2_24_content_density_gate_id",
        ]
        assert "screenshots" in record["forbidden_source_materials"]
        assert "brand marks" in record["forbidden_source_materials"]

    assert visual_assets["status"] == "run2_24_visual_evidence_asset_memory_ready_public_blocked"
    assert visual_assets["storage_policy"]["raw_media"] == "forbidden"
    assert len(visual_assets["visual_evidence_assets"]) == 12
    for asset in visual_assets["visual_evidence_assets"]:
        assert asset["asset_id"].startswith("asset_2_24_")
        assert asset["role"] in {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert asset["native_ppt_strategy"]
        assert asset["content_payload"]
        assert asset["source_boundary"].startswith("Derived")
        assert asset["public_surface_allowed"] is True

    assert workflow_gates["status"] == "run2_24_content_visual_workflow_gates_ready_public_blocked"
    assert len(workflow_gates["gates"]) == 6
    for gate in workflow_gates["gates"]:
        assert gate["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
        assert gate["min_business_proof_points"] >= 2
        assert gate["min_visual_evidence_slots"] >= 2
        assert gate["forbid_cross_case_primary_story"] is True
        assert "run2_24_selected_usecase_id" in gate["required_trace_fields"]
        assert gate["public_release_gate"] == "blocked"

    assert_contains(
        report,
        [
            "Run 2.24",
            "single usecase",
            "content memory",
            "visual evidence",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
    assert not list(tmp_path.glob("*.pptx"))


def test_run2_24_records_single_usecase_content_visual_evidence_pack() -> None:
    result = (PACK / "results" / "run2_24_single_usecase_thickening_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_24_single_usecase_thickening_result.json")
    content_memory = load_json(PACK / "run2_24_single_usecase_content_memory.json")
    visual_assets = load_json(PACK / "run2_24_visual_evidence_asset_memory.json")
    workflow_gates = load_json(PACK / "run2_24_content_visual_workflow_gates.json")
    workflow = load_json(PACK / "skill_workflow.json")

    assert result_json["status"] == "run2_24_single_usecase_content_visual_evidence_ready_public_blocked"
    assert result_json["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["public_ready"] is False
    assert result_json["artifact_counts"] == {
        "slide_content_memory": 6,
        "visual_evidence_assets": 12,
        "content_visual_workflow_gates": 6,
    }
    assert content_memory["story_policy"]["single_primary_usecase"] is True
    assert len(content_memory["slide_content_memory"]) == 6
    assert len(visual_assets["visual_evidence_assets"]) == 12
    assert len(workflow_gates["gates"]) == 6
    assert workflow["status"] == "run2_35_visual_evidence_realism_workflow_directed_public_blocked"
    assert {stage["id"] for stage in workflow["stages"]} >= {
        "lock_run2_24_single_usecase_content_memory",
        "compile_run2_24_visual_evidence_asset_memory",
        "apply_run2_24_content_visual_workflow_gates",
        "compile_run2_35_visual_evidence_asset_realism_memory",
        "compile_run2_35_editorial_composition_memory",
        "apply_run2_35_visual_evidence_workflow_gates",
    }
    assert any(
        trigger["id"] == "run2_24_single_usecase_pack_required_before_next_rerun"
        for trigger in workflow["repair_triggers"]
    )
    assert any(
        trigger["id"] == "run2_35_visual_evidence_realism_required_before_run2_36_rerun"
        for trigger in workflow["repair_triggers"]
    )
    assert_contains(
        result,
        [
            "Run 2.24",
            "usecase_design_to_production_platform_launch",
            "content memory",
            "visual evidence",
            "public blocked",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_24_single_usecase_content_visual_evidence_pack() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_24_single_usecase_content_memory.json",
            "run2_24_visual_evidence_asset_memory.json",
            "run2_24_content_visual_workflow_gates.json",
            "run2_24_single_usecase_thickening_result.json",
            "Run 2.24 single-usecase content + visual evidence",
        ],
    )


def test_run2_25_generator_consumes_run2_24_pack_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_25_single_usecase_arms.mjs"
    assert script_path.exists(), "missing Run 2.25 single-usecase rerun generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_25_full_single_usecase_content_visual",
        "bad_content_visual_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    run2_24_inputs = [
        "run2_24_single_usecase_content_memory.json",
        "run2_24_visual_evidence_asset_memory.json",
        "run2_24_content_visual_workflow_gates.json",
    ]

    assert_contains(
        body,
        [
            "validateRun224SingleUsecaseSchemas",
            "assertRun225ArmInputBoundaries",
            "readRun225PackJsonForArm",
            "selectRun224ForSlide",
            "assertRun225ContentVisualGateSelfCheck",
            "drawRun225LaunchField",
            "drawRun225SelectedRouteMap",
            "drawRun225ContentEvidenceSurface",
            "drawRun225ClimaxProofObject",
            "run2_24_pack_executed_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_25_full_single_usecase_content_visual"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_25_full_single_usecase_content_visual"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_content_visual_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_content_visual_memory"), "forbidden:", "palette:")

    for term in run2_24_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun225 = arm.armId === "run2_25_full_single_usecase_content_visual";' in body
    for field in [
        "run2_24_selected_usecase_id",
        "run2_24_content_memory_id",
        "run2_24_visual_evidence_slot_ids",
        "run2_24_content_density_gate_id",
        "run2_25_content_visual_execution_status",
        "run2_25_code_module_ids",
    ]:
        assert re.search(fr"{field}:\s*fullRun225\s*\?", body), field
    for function_name in [
        "drawRun225LaunchField",
        "drawRun225SelectedRouteMap",
        "drawRun225ContentEvidenceSurface",
        "drawRun225ClimaxProofObject",
    ]:
        assert f'registerRun225Module(metrics, "{function_name}")' in body


def test_run2_25_runtime_guards_block_bad_arm_and_select_single_usecase_pack() -> None:
    node_script = """
const mod = await import("./scripts/generate_ppt_run2_25_single_usecase_arms.mjs");
const badArm = mod.armSpecs.find((arm) => arm.armId === "bad_content_visual_memory");
const fullArm = mod.armSpecs.find((arm) => arm.armId === "run2_25_full_single_usecase_content_visual");
for (const input of mod.RUN2_25_DATA_INPUTS) {
  let blocked = false;
  try {
    mod.readRun225PackJsonForArm(badArm, input);
  } catch (error) {
    blocked = String(error.message).includes("input boundary does not permit reading");
  }
  if (!blocked) throw new Error(`bad content/visual arm was able to read ${input}`);
}
const badTrace = mod.traceFor(badArm);
for (const slide of badTrace.slides) {
  if (slide.run2_24_content_memory_id) throw new Error("bad control trace leaked Run 2.24 content memory id");
  if ((slide.run2_24_visual_evidence_slot_ids || []).length) throw new Error("bad control trace leaked Run 2.24 visual evidence slots");
  if (slide.run2_24_content_density_gate_id) throw new Error("bad control trace leaked Run 2.24 density gate");
  if ((slide.run2_25_code_module_ids || []).length) throw new Error("bad control trace leaked Run 2.25 code modules");
}
const fullTrace = mod.traceFor(fullArm);
if (fullTrace.selected_usecase_id !== "usecase_design_to_production_platform_launch") throw new Error("full trace did not lock the selected usecase");
for (const slide of fullTrace.slides) {
  if (slide.run2_24_selected_usecase_id !== "usecase_design_to_production_platform_launch") throw new Error(`slide ${slide.slide_id} selected the wrong usecase`);
  if (!slide.run2_24_content_memory_id.startsWith("content_2_24_")) throw new Error(`slide ${slide.slide_id} missing content memory`);
  if ((slide.run2_24_visual_evidence_slot_ids || []).length < 2) throw new Error(`slide ${slide.slide_id} missing visual evidence slots`);
  if (!slide.run2_24_content_density_gate_id.startsWith("gate_2_24_")) throw new Error(`slide ${slide.slide_id} missing density gate`);
  if (slide.run2_25_content_visual_execution_status !== "run2_24_pack_executed_before_native_ppt_generation") throw new Error(`slide ${slide.slide_id} missing execution status`);
  if ((slide.run2_25_code_module_ids || []).length === 0) throw new Error(`slide ${slide.slide_id} missing code module ids`);
}
const selected = mod.selectRun224ForSlide("climax", mod.loadRun225ContractData(fullArm));
if (selected.content.content_memory_id !== "content_2_24_climax") throw new Error("climax did not select Run 2.24 content memory");
if (selected.assets.length < 2) throw new Error("climax did not select visual evidence assets");
if (!fullArm.allowed.includes(mod.RUN2_25_INPUTS.visualAssets)) throw new Error("full arm does not allow Run 2.24 visual assets");
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_25_content_evidence_surface_geometry_prevents_crushed_text() -> None:
    node_script = """
const mod = await import("./scripts/generate_ppt_run2_25_single_usecase_arms.mjs");
for (const width of [458, 552, 760, 870]) {
  const geom = mod.run225ContentEvidenceSurfaceGeometry({ x: 0, y: 0, w: width, h: 242 });
  if (geom.headline.w < 180) throw new Error(`headline width crushed for ${width}: ${geom.headline.w}`);
  if (geom.proofPoint.w < 150) throw new Error(`proof point width crushed for ${width}: ${geom.proofPoint.w}`);
  if (geom.rail.w < 176) throw new Error(`visual rail width crushed for ${width}: ${geom.rail.w}`);
  if (geom.assetCard.w < 140) throw new Error(`asset card width crushed for ${width}: ${geom.assetCard.w}`);
}
const medium = mod.run225ContentEvidenceSurfaceGeometry({ x: 0, y: 0, w: 640, h: 346 });
if (medium.mode !== "medium") throw new Error(`640px surface should use medium geometry: ${medium.mode}`);
if (medium.headline.h < 92) throw new Error(`medium headline height too short: ${medium.headline.h}`);
if (medium.proofPoint.y < medium.headline.y + medium.headline.h + 16) throw new Error("medium proof points collide with headline");
if (medium.proofPoint.compress !== true) throw new Error("medium proof points should use compressed copy");
if (medium.proofPoint.count !== 2) throw new Error(`medium surface should show two proof points, got ${medium.proofPoint.count}`);
const compact = mod.run225ContentEvidenceSurfaceGeometry({ x: 0, y: 0, w: 458, h: 242 });
if (compact.mode !== "compact") throw new Error("458px surface should use compact geometry");
const wide = mod.run225ContentEvidenceSurfaceGeometry({ x: 0, y: 0, w: 870, h: 368 });
if (wide.mode !== "wide") throw new Error("870px surface should use wide geometry");
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_25_records_single_usecase_generated_rerun_result() -> None:
    result = (PACK / "results" / "run2_25_single_usecase_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_25_single_usecase_rerun_result.json")

    assert result_json["status"] == "run2_25_single_usecase_rerun_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["run_id"] == "2.25"
    assert result_json["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert result_json["rerun"]["best_internal_arm"] == "run2_25_full_single_usecase_content_visual"
    assert result_json["rerun"]["best_internal_arm_verdict"] == "run2_24_pack_executed_before_native_ppt_generation"
    assert result_json["input_chain"]["content_memory"] == "docs/product/ppt-run2-data-skill-quality/run2_24_single_usecase_content_memory.json"
    assert result_json["input_chain"]["visual_evidence_asset_memory"] == "docs/product/ppt-run2-data-skill-quality/run2_24_visual_evidence_asset_memory.json"
    assert result_json["input_chain"]["content_visual_workflow_gates"] == "docs/product/ppt-run2-data-skill-quality/run2_24_content_visual_workflow_gates.json"
    assert result_json["control_boundary"]["bad_content_visual_memory"].startswith("selected_usecase_label_only")
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-25-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert_contains(
        result,
        [
            "Run 2.25",
            "Run 2.24 single-usecase content memory",
            "four-arm rerun",
            "bad_content_visual_memory",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_25_generated_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.25",
            "ppt-run2-25-prompt-only",
            "ppt-run2-25-run1-5-skill",
            "ppt-run2-25-full-vulca",
            "ppt-run2-25-bad-content-visual-memory",
            "run2_25_single_usecase_rerun_result.json",
        ],
    )


def test_run2_26_visual_module_quality_audit_scores_run2_25_outputs(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "audit_ppt_run2_26_visual_module_quality.py"
    assert script_path.exists(), "missing Run 2.26 visual module quality audit script"

    result_json = tmp_path / "run2_26_visual_module_quality_audit.json"
    result_md = tmp_path / "run2_26_visual_module_quality_audit.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    audit = load_json(result_json)
    report = result_md.read_text(encoding="utf-8")

    assert audit["status"] == "run2_26_visual_module_quality_audit_public_blocked"
    assert audit["run_id"] == "2.26"
    assert audit["source_generated_run"] == "2.25"
    assert audit["creates_new_ppt_deck"] is False
    assert audit["public_ready"] is False
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["input_chain"]["run2_25_full_trace_manifest"].endswith("ppt-run2-25-full-vulca/trace_manifest.json")
    assert audit["input_chain"]["run2_25_full_layout_dir"].endswith("ppt-run2-25-full-vulca/layout/final")
    assert audit["no_new_deck_proof"]["status"] == "pass"
    assert audit["no_new_deck_proof"]["matched_run2_26_outputs"] == []
    assert audit["no_new_deck_proof"]["new_pptx_created"] is False
    assert audit["quality_summary"]["module_quality_gate"] == "pass_internal_only"
    assert audit["quality_summary"]["public_release_gate"] == "blocked"
    assert audit["quality_summary"]["top_next_module_to_thicken"] == "drawRun225ContentEvidenceSurface"
    assert audit["quality_summary"]["roles_with_visible_layout_defects"] == []
    assert audit["quality_summary"]["roles_with_compressed_proof_surface"]
    assert audit["issue_categories"] == [
        "layout_geometry",
        "content_density",
        "visual_evidence_visibility",
        "composition_hierarchy",
        "climax_impact",
    ]
    assert len(audit["role_records"]) == 6
    for record in audit["role_records"]:
        assert record["role"] in {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert record["geometry"]["crushed_text_box_count"] == 0
        assert record["geometry"]["max_line_count"] <= 14
        assert record["content_density"]["visual_evidence_slot_count"] >= 2
        assert record["visual_evidence_visibility"]["trace_slots_present"] is True
        assert record["status"] in {"pass_internal_only", "needs_next_module_thickening"}
        assert record["recommended_next_action"]

    assert_contains(
        report,
        [
            "Run 2.26",
            "visual module quality",
            "Run 2.25",
            "drawRun225ContentEvidenceSurface",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_26_records_visual_module_quality_audit_result() -> None:
    result = (PACK / "results" / "run2_26_visual_module_quality_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_26_visual_module_quality_audit.json")

    assert result_json["status"] == "run2_26_visual_module_quality_audit_public_blocked"
    assert result_json["source_generated_run"] == "2.25"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["public_ready"] is False
    assert result_json["no_new_deck_proof"]["status"] == "pass"
    assert result_json["no_new_deck_proof"]["matched_run2_26_outputs"] == []
    assert result_json["no_new_deck_proof"]["new_pptx_created"] is False
    assert result_json["quality_summary"]["top_next_module_to_thicken"] == "drawRun225ContentEvidenceSurface"
    assert result_json["next_required_action"].startswith("thicken_drawRun225ContentEvidenceSurface")
    assert_contains(
        result,
        [
            "Run 2.26",
            "visual module quality",
            "Run 2.25",
            "public blocked",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_26_visual_module_quality_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_26_visual_module_quality_audit.json",
            "Run 2.26 visual module quality audit",
            "drawRun225ContentEvidenceSurface",
            "roles_with_compressed_proof_surface",
            "no_new_deck_proof",
        ],
    )


def test_run2_27_generator_consumes_run2_26_audit_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_27_content_surface_thickening_arms.mjs"
    assert script_path.exists(), "missing Run 2.27 content surface thickening generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_27_full_content_surface_thickening",
        "bad_surface_thickening_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    required_inputs = [
        "run2_24_single_usecase_content_memory.json",
        "run2_24_visual_evidence_asset_memory.json",
        "run2_24_content_visual_workflow_gates.json",
        "run2_26_visual_module_quality_audit.json",
    ]

    assert_contains(
        body,
        [
            "validateRun226VisualModuleAudit",
            "loadRun227ContractData",
            "drawRun227ContentEvidenceSurface",
            "run227ContentEvidenceSurfaceGeometry",
            "run2_27_content_surface_thickening_execution_status",
            "run2_27_code_module_ids",
            "thicken_drawRun225ContentEvidenceSurface_before_run2_27_rerun",
            "run2_26_visual_module_quality_audit_public_blocked",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_27_full_content_surface_thickening"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_27_full_content_surface_thickening"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_surface_thickening_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_surface_thickening_memory"), "forbidden:", "palette:")

    for term in required_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun227 = arm.armId === "run2_27_full_content_surface_thickening";' in body
    assert 'registerRun227Module(metrics, "drawRun227ContentEvidenceSurface")' in body
    for field in [
        "run2_26_source_audit_status",
        "run2_26_roles_with_compressed_proof_surface",
        "run2_27_content_surface_thickening_execution_status",
        "run2_27_required_code_module_ids",
        "run2_27_code_module_ids",
    ]:
        assert re.search(fr"{field}:\s*fullRun227\s*\?", body), field


def test_run2_27_surface_geometry_shows_all_proof_points_without_compression() -> None:
    node_script = """
const mod = await import("./scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs");
for (const width of [540, 604, 760, 870]) {
  const geom = mod.run227ContentEvidenceSurfaceGeometry({ x: 0, y: 0, w: width, h: 360 });
  if (geom.proofPoint.count !== 3) throw new Error(`Run 2.27 must show all three proof points for ${width}, got ${geom.proofPoint.count}`);
  if (geom.proofPoint.compress !== false) throw new Error(`Run 2.27 must not compress proof copy for ${width}`);
  if (geom.proofPoint.w < 280) throw new Error(`Run 2.27 proof row width too small for ${width}: ${geom.proofPoint.w}`);
  if (geom.proofPoint.h < 32) throw new Error(`Run 2.27 proof row height too short for ${width}: ${geom.proofPoint.h}`);
  if (geom.assetCard.w < 132) throw new Error(`Run 2.27 asset card width too small for ${width}: ${geom.assetCard.w}`);
}
const compact = mod.run227ContentEvidenceSurfaceGeometry({ x: 0, y: 0, w: 540, h: 342 });
if (compact.mode !== "compact-thick") throw new Error(`540px surface should use compact-thick geometry: ${compact.mode}`);
if (compact.proofPoint.y < compact.headline.y + compact.headline.h + 12) throw new Error("proof rows collide with headline in compact-thick geometry");
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_27_runtime_guards_block_bad_arm_and_select_audit_targets() -> None:
    node_script = """
const mod = await import("./scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs");
const badArm = mod.armSpecs.find((arm) => arm.armId === "bad_surface_thickening_memory");
const fullArm = mod.armSpecs.find((arm) => arm.armId === "run2_27_full_content_surface_thickening");
for (const input of mod.RUN2_27_DATA_INPUTS) {
  let blocked = false;
  try {
    mod.readRun227PackJsonForArm(badArm, input);
  } catch (error) {
    blocked = String(error.message).includes("input boundary does not permit reading");
  }
  if (!blocked) throw new Error(`bad surface-thickening arm was able to read ${input}`);
}
const audit = mod.loadRun226VisualModuleAudit(fullArm);
if (audit.quality_summary.top_next_module_to_thicken !== "drawRun225ContentEvidenceSurface") throw new Error("Run 2.27 loaded wrong audit target");
if (!audit.quality_summary.roles_with_compressed_proof_surface.includes("setup")) throw new Error("Run 2.27 audit target missing setup");
const badTrace = mod.traceFor(badArm);
for (const slide of badTrace.slides) {
  if (slide.run2_26_source_audit_status) throw new Error("bad control trace leaked Run 2.26 audit");
  if ((slide.run2_27_code_module_ids || []).length) throw new Error("bad control trace leaked Run 2.27 code modules");
}
const fullTrace = mod.traceFor(fullArm);
if (fullTrace.source_audit_run_id !== "2.26") throw new Error("full trace did not bind Run 2.26 audit");
for (const slide of fullTrace.slides) {
  if (slide.role === "setup" || slide.role === "contrast" || slide.role === "close") {
    if (!slide.run2_27_required_code_module_ids.includes("drawRun227ContentEvidenceSurface")) throw new Error(`${slide.role} missing thickened surface requirement`);
    if (!slide.run2_27_code_module_ids.includes("drawRun227ContentEvidenceSurface")) throw new Error(`${slide.role} missing thickened surface trace`);
  }
}
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr


def test_run2_27_records_content_surface_thickening_rerun_result() -> None:
    result = (PACK / "results" / "run2_27_content_surface_thickening_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_27_content_surface_thickening_rerun_result.json")

    assert result_json["status"] == "run2_27_content_surface_thickening_rerun_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["source_audit_run_id"] == "2.26"
    assert result_json["rerun"]["best_internal_arm"] == "run2_27_full_content_surface_thickening"
    assert result_json["rerun"]["best_internal_arm_verdict"] == "run2_26_audit_target_executed_before_native_ppt_generation"
    assert result_json["quality_delta"]["target_module"] == "drawRun225ContentEvidenceSurface"
    assert result_json["quality_delta"]["replacement_module"] == "drawRun227ContentEvidenceSurface"
    assert result_json["quality_delta"]["roles_with_compressed_proof_surface_after"] == []
    assert result_json["visual_quality_boundary"] == (
        "content_surface_thickening_proof_only_not_public_video_grade_aesthetic_or_human_release_approval"
    )
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-27-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")
    assert_contains(
        result,
        [
            "Run 2.27",
            "Run 2.26 visual module quality audit",
            "drawRun227ContentEvidenceSurface",
            "four-arm rerun",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_27_content_surface_thickening_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.27",
            "ppt-run2-27-prompt-only",
            "ppt-run2-27-run1-5-skill",
            "ppt-run2-27-full-vulca",
            "ppt-run2-27-bad-surface-thickening-memory",
            "run2_27_content_surface_thickening_rerun_result.json",
            "drawRun227ContentEvidenceSurface",
        ],
    )


def test_run2_28_evidence_chain_view_model_binds_source_data_workflow_and_slide_surface() -> None:
    model = load_json(PACK / "run2_28_evidence_chain_view_model.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    content_memory = load_json(PACK / "run2_24_single_usecase_content_memory.json")
    workflow_gates = load_json(PACK / "run2_24_content_visual_workflow_gates.json")

    assert model["status"] == "run2_28_evidence_chain_view_model_ready_public_blocked"
    assert model["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert model["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert model["source_layer"] == "run2_7_multimodal_source_records.json"
    assert model["content_layer"] == "run2_24_single_usecase_content_memory.json"
    assert model["workflow_layer"] == "run2_24_content_visual_workflow_gates.json"

    source_ids = {record["id"] for record in source_records["records"]}
    content_by_role = {record["role"]: record for record in content_memory["slide_content_memory"]}
    gate_by_role = {gate["role"]: gate for gate in workflow_gates["gates"]}
    chains = model["slide_evidence_chains"]

    assert [chain["role"] for chain in chains] == ["cover", "setup", "contrast", "proof", "climax", "close"]
    for chain in chains:
        role = chain["role"]
        content = content_by_role[role]
        gate = gate_by_role[role]

        assert chain["content_memory_id"] == content["content_memory_id"]
        assert chain["workflow_gate_id"] == gate["gate_id"]
        assert set(chain["visual_evidence_slot_ids"]) == set(content["visual_evidence_slot_ids"])
        assert set(chain["multimodal_source_record_ids"]) <= source_ids
        assert chain["extracted_design_rule"]
        assert chain["workflow_decision"]
        assert chain["native_ppt_surface_instruction"]
        assert chain["viewer_inspection_prompt"]
        assert chain["negative_control_failure_mode"]
        assert set(chain["required_trace_fields"]) >= {
            "run2_28_evidence_chain_id",
            "run2_28_multimodal_source_record_ids",
            "run2_28_extracted_design_rule",
            "run2_28_workflow_decision",
            "run2_28_native_surface_module_id",
        }

    assert model["viewer_contract"]["show_chain_in_html_viewer"] is True
    assert model["viewer_contract"]["chain_order"] == [
        "source evidence",
        "extracted design rule",
        "workflow decision",
        "generated slide surface",
    ]
    assert model["public_release_gate"] == "blocked"


def test_run2_28_generator_consumes_evidence_chain_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_28_evidence_chain_arms.mjs"
    assert script_path.exists(), "missing Run 2.28 evidence-chain generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_28_full_evidence_chain",
        "bad_evidence_chain_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    required_inputs = [
        "run2_28_evidence_chain_view_model.json",
        "run2_24_single_usecase_content_memory.json",
        "run2_24_visual_evidence_asset_memory.json",
        "run2_24_content_visual_workflow_gates.json",
        "run2_27_content_surface_thickening_rerun_result.json",
    ]

    assert_contains(
        body,
        [
            "validateRun228EvidenceChainViewModel",
            "loadRun228ContractData",
            "drawRun228EvidenceChainSurface",
            "drawRun228WorkflowTracePanel",
            "run228EvidenceChainSurfaceGeometry",
            "run2_28_evidence_chain_execution_status",
            "run2_28_native_surface_module_id",
            "source evidence",
            "extracted design rule",
            "workflow decision",
            "generated slide surface",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_28_full_evidence_chain"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_28_full_evidence_chain"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_evidence_chain_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_evidence_chain_memory"), "forbidden:", "palette:")

    for term in required_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun228 = arm.armId === "run2_28_full_evidence_chain";' in body
    assert 'registerRun228Module(metrics, "drawRun228EvidenceChainSurface")' in body
    for field in [
        "run2_28_evidence_chain_id",
        "run2_28_multimodal_source_record_ids",
        "run2_28_extracted_design_rule",
        "run2_28_workflow_decision",
        "run2_28_native_surface_module_id",
        "run2_28_evidence_chain_execution_status",
    ]:
        assert re.search(fr"{field}:\s*fullRun228\s*\?", body), field


def test_ppt_run_html_viewer_mentions_run2_28_evidence_chain_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.28",
            "ppt-run2-28-prompt-only",
            "ppt-run2-28-run1-5-skill",
            "ppt-run2-28-full-vulca",
            "ppt-run2-28-bad-evidence-chain-memory",
            "run2_28_evidence_chain_view_model.json",
            "run2_28_evidence_chain_rerun_result.json",
            "source evidence",
            "extracted design rule",
            "workflow decision",
            "generated slide surface",
        ],
    )


def test_run2_29_presentation_synthesis_memory_compresses_evidence_chain_without_dropping_trace() -> None:
    memory = load_json(PACK / "run2_29_presentation_synthesis_memory.json")
    evidence_chain = load_json(PACK / "run2_28_evidence_chain_view_model.json")
    prior_result = load_json(PACK / "results" / "run2_28_evidence_chain_rerun_result.json")

    assert memory["status"] == "run2_29_presentation_synthesis_memory_ready_public_blocked"
    assert memory["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert memory["source_evidence_chain_layer"] == "run2_28_evidence_chain_view_model.json"
    assert memory["prior_rerun_result"] == "run2_28_evidence_chain_rerun_result.json"
    assert prior_result["status"] == "run2_28_evidence_chain_rerun_public_blocked"
    assert memory["surface_policy"]["primary_reader_experience"] == "presentation_first_surface"
    assert memory["surface_policy"]["secondary_reviewer_experience"] == "compressed_evidence_spine"
    assert memory["surface_policy"]["forbidden_primary_surface"] == "four_column_audit_table"

    chains_by_role = {chain["role"]: chain for chain in evidence_chain["slide_evidence_chains"]}
    records = memory["slide_synthesis_records"]
    assert [record["role"] for record in records] == ["cover", "setup", "contrast", "proof", "climax", "close"]
    assert {record["evidence_chain_id"] for record in records} == {
        chain["evidence_chain_id"] for chain in evidence_chain["slide_evidence_chains"]
    }

    required_trace_fields = {
        "run2_28_evidence_chain_id",
        "run2_28_multimodal_source_record_ids",
        "run2_28_extracted_design_rule",
        "run2_28_workflow_decision",
        "run2_28_native_surface_module_id",
        "run2_29_synthesis_record_id",
        "run2_29_public_surface_mode",
        "run2_29_trace_surface_mode",
        "run2_29_presentation_module_id",
        "run2_29_chain_compression_policy",
    }
    for record in records:
        chain = chains_by_role[record["role"]]
        assert record["evidence_chain_id"] == chain["evidence_chain_id"]
        assert record["source_native_surface_module_id"] == chain["native_surface_module_id"]
        assert record["trace_surface_mode"] == "manifest_and_html_viewer_full_chain_visible"
        assert record["presentation_module_id"].startswith("drawRun229")
        assert record["visible_on_slide_evidence_spine_steps"] == [
            "source evidence",
            "extracted design rule",
            "workflow decision",
            "generated slide surface",
        ]
        assert "do_not_render_four_column_audit_table_as_primary_surface" in record["chain_compression_policy"]
        assert "make_evidence_chain_secondary_to_editorial_claim_and_proof_object" in record["chain_compression_policy"]
        assert set(record["preserved_trace_fields"]) >= required_trace_fields
        assert record["primary_slide_surface_contract"]
        assert record["reviewer_inspection_prompt"]

    assert memory["public_release_gate"] == "blocked"


def test_run2_29_generator_consumes_presentation_synthesis_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_29_presentation_synthesis_arms.mjs"
    assert script_path.exists(), "missing Run 2.29 presentation-synthesis generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_29_full_presentation_synthesis",
        "bad_presentation_synthesis_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    required_inputs = [
        "run2_29_presentation_synthesis_memory.json",
        "run2_28_evidence_chain_view_model.json",
        "run2_24_single_usecase_content_memory.json",
        "run2_24_visual_evidence_asset_memory.json",
        "run2_24_content_visual_workflow_gates.json",
        "run2_28_evidence_chain_rerun_result.json",
    ]

    assert_contains(
        body,
        [
            "validateRun229PresentationSynthesisMemory",
            "loadRun229ContractData",
            "drawRun229CompressedEvidenceSpine",
            "drawRun229EditorialLaunchFrame",
            "drawRun229HeroProofScene",
            "drawRun229DecisionHandoff",
            "run2_29_presentation_synthesis_execution_status",
            "run2_29_public_surface_mode",
            "run2_29_trace_surface_mode",
            "run2_29_presentation_module_id",
            "presentation_first_surface_rendered_with_secondary_evidence_spine",
            "do_not_render_four_column_audit_table_as_primary_surface",
            "compressed evidence spine",
            "presentation-first surface",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_29_full_presentation_synthesis"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_29_full_presentation_synthesis"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_presentation_synthesis_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_presentation_synthesis_memory"), "forbidden:", "palette:")

    for term in required_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun229 = arm.armId === "run2_29_full_presentation_synthesis";' in body
    assert 'registerRun229Module(metrics, "drawRun229CompressedEvidenceSpine")' in body
    for field in [
        "run2_29_synthesis_record_id",
        "run2_29_public_surface_mode",
        "run2_29_trace_surface_mode",
        "run2_29_presentation_module_id",
        "run2_29_chain_compression_policy",
        "run2_29_presentation_synthesis_execution_status",
    ]:
        assert re.search(fr"{field}:\s*fullRun229\s*\?", body), field


def test_ppt_run_html_viewer_mentions_run2_29_presentation_synthesis_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.29",
            "ppt-run2-29-prompt-only",
            "ppt-run2-29-run1-5-skill",
            "ppt-run2-29-full-vulca",
            "ppt-run2-29-bad-presentation-synthesis-memory",
            "run2_29_presentation_synthesis_memory.json",
            "run2_29_presentation_synthesis_rerun_result.json",
            "presentation-first surface",
            "compressed evidence spine",
            "four-column audit table",
            "manifest_and_html_viewer_full_chain_visible",
        ],
    )


def test_run2_30_presentation_synthesis_audit_scores_run2_29_outputs(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "audit_ppt_run2_30_presentation_synthesis.py"
    assert script_path.exists(), "missing Run 2.30 presentation-synthesis audit script"

    result_json = tmp_path / "run2_30_presentation_synthesis_audit.json"
    result_md = tmp_path / "run2_30_presentation_synthesis_audit.md"
    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        check=True,
    )

    audit = load_json(result_json)
    assert audit["schema_version"] == "ppt_run2_presentation_synthesis_audit.v1"
    assert audit["run_id"] == "2.30"
    assert audit["status"] == "run2_30_presentation_synthesis_audit_public_blocked"
    assert audit["source_generated_run"] == "2.29"
    assert audit["comparison_baseline_run"] == "2.28"
    assert audit["source_synthesis_layer"] == "2.29"
    assert audit["creates_new_ppt_deck"] is False
    assert audit["public_ready"] is False
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["input_chain"]["run2_29_full_trace_manifest"].endswith("ppt-run2-29-full-vulca/trace_manifest.json")
    assert audit["input_chain"]["run2_29_bad_trace_manifest"].endswith(
        "ppt-run2-29-bad-presentation-synthesis-memory/trace_manifest.json"
    )
    assert audit["input_chain"]["run2_28_full_trace_manifest"].endswith("ppt-run2-28-full-vulca/trace_manifest.json")
    assert audit["no_new_deck_proof"]["new_pptx_created"] is False
    assert audit["no_new_deck_proof"]["status"] == "pass"

    trace = audit["trace_closure"]
    assert trace["full_arm"]["arm_id"] == "run2_29_full_presentation_synthesis"
    assert trace["full_arm"]["slide_count"] == 6
    assert trace["full_arm"]["presentation_synthesis_records_selected"] == 6
    assert trace["full_arm"]["compressed_evidence_spine_modules_called"] == 6
    assert trace["full_arm"]["presentation_first_execution_status_slides"] == 6
    assert trace["full_arm"]["run2_28_chain_fields_preserved"] == 6
    assert trace["bad_control"]["arm_id"] == "bad_presentation_synthesis_memory"
    assert trace["bad_control"]["presentation_synthesis_fields_leaked"] == 0

    comparison = audit["comparison_to_run2_28"]
    assert comparison["audit_table_demoted_to_secondary_spine"] is True
    assert comparison["full_chain_preserved_in_trace"] is True
    assert comparison["primary_surface_delta"] == "four_column_audit_table_to_presentation_first_surface"

    summary = audit["quality_summary"]
    assert summary["presentation_synthesis_gate"] == "pass_internal_only"
    assert summary["public_release_gate"] == "blocked"
    assert summary["top_next_layer_to_thicken"] == "spine_readability_and_climax_consistency"
    assert set(summary["roles_with_dense_spine_text"]) == {"cover", "setup", "contrast", "proof", "climax", "close"}
    assert summary["roles_with_climax_style_shift"] == ["climax"]

    assert len(audit["role_records"]) == 6
    for record in audit["role_records"]:
        assert record["presentation_first_surface"]["status"] == "pass"
        assert record["trace_closure"]["run2_28_chain_preserved"] is True
        assert record["trace_closure"]["synthesis_record_selected"] is True
        assert record["evidence_spine"]["compressed_spine_module_called"] is True
        assert record["evidence_spine"]["min_spine_font_size"] < 8
        assert "spine_readability" in record["issue_categories"]


def test_run2_30_records_presentation_synthesis_audit_result() -> None:
    result = (PACK / "results" / "run2_30_presentation_synthesis_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_30_presentation_synthesis_audit.json")

    assert result_json["status"] == "run2_30_presentation_synthesis_audit_public_blocked"
    assert result_json["source_generated_run"] == "2.29"
    assert result_json["comparison_baseline_run"] == "2.28"
    assert result_json["quality_summary"]["top_next_layer_to_thicken"] == "spine_readability_and_climax_consistency"
    assert result_json["next_required_action"] == "thicken_run2_29_spine_readability_and_climax_consistency_before_run2_31_rerun"
    assert_contains(
        result,
        [
            "Run 2.30 Presentation Synthesis Audit",
            "audit-only",
            "2.29",
            "2.28",
            "compressed evidence spine",
            "presentation-first surface",
            "spine_readability_and_climax_consistency",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_30_presentation_synthesis_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_30_presentation_synthesis_audit.json",
            "Run 2.30 presentation synthesis audit",
            "audit_table_demoted_to_secondary_spine",
            "spine_readability_and_climax_consistency",
            "presentation_synthesis_gate",
            "full_chain_preserved_in_trace",
            "creates no new PPT deck",
        ],
    )


def test_run2_31_generator_consumes_run2_30_audit_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_31_spine_climax_repair_arms.mjs"
    assert script_path.exists(), "missing Run 2.31 spine/climax repair generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_31_full_spine_climax_repair",
        "bad_spine_climax_repair_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    required_inputs = [
        "run2_30_presentation_synthesis_audit.json",
        "run2_29_presentation_synthesis_memory.json",
        "run2_28_evidence_chain_view_model.json",
        "run2_24_single_usecase_content_memory.json",
        "run2_24_visual_evidence_asset_memory.json",
        "run2_24_content_visual_workflow_gates.json",
        "run2_29_presentation_synthesis_rerun_result.json",
    ]

    assert_contains(
        body,
        [
            "validateRun230PresentationSynthesisAudit",
            "loadRun231ContractData",
            "drawRun231ReadableEvidenceSpine",
            "drawRun231HeroProofScene",
            "spine_readability_and_climax_consistency",
            "run2_30_source_audit_status",
            "run2_30_top_next_layer_to_thicken",
            "run2_31_spine_min_font_size_target",
            "run2_31_climax_style_policy",
            "run2_31_spine_climax_repair_execution_status",
            "spine_readability_and_climax_consistency_repaired_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_31_full_spine_climax_repair"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_31_full_spine_climax_repair"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_spine_climax_repair_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_spine_climax_repair_memory"), "forbidden:", "palette:")

    for term in required_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun231 = arm.armId === "run2_31_full_spine_climax_repair";' in body
    assert 'registerRun231Module(metrics, "drawRun231ReadableEvidenceSpine")' in body
    for field in [
        "run2_30_source_audit_status",
        "run2_30_top_next_layer_to_thicken",
        "run2_31_spine_min_font_size_target",
        "run2_31_climax_style_policy",
        "run2_31_spine_climax_repair_execution_status",
    ]:
        assert re.search(fr"{field}:\s*fullRun231\s*\?", body), field


def test_run2_31_records_spine_climax_repair_rerun_result() -> None:
    result = (PACK / "results" / "run2_31_spine_climax_repair_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_31_spine_climax_repair_rerun_result.json")

    assert result_json["status"] == "run2_31_spine_climax_repair_rerun_public_blocked"
    assert result_json["source_audit_run_id"] == "2.30"
    assert result_json["input_chain"]["presentation_synthesis_audit"].endswith(
        "run2_30_presentation_synthesis_audit.json"
    )
    assert result_json["rerun"]["best_internal_arm"] == "run2_31_full_spine_climax_repair"
    assert result_json["rerun"]["best_internal_arm_verdict"] == (
        "spine_readability_and_climax_consistency_repaired_before_native_ppt_generation"
    )
    assert result_json["quality_delta"]["target_layer"] == "spine_readability_and_climax_consistency"
    assert result_json["quality_delta"]["spine_min_font_size_target"] >= 8
    assert result_json["quality_delta"]["climax_style_policy"] == "high_contrast_climax_with_shared_light_editorial_frame"
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-31-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")
    assert_contains(
        result,
        [
            "Run 2.31",
            "Run 2.30 presentation synthesis audit",
            "drawRun231ReadableEvidenceSpine",
            "drawRun231HeroProofScene",
            "spine_readability_and_climax_consistency",
            "four-arm rerun",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_31_spine_climax_repair_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.31",
            "ppt-run2-31-prompt-only",
            "ppt-run2-31-run1-5-skill",
            "ppt-run2-31-full-vulca",
            "ppt-run2-31-bad-spine-climax-repair-memory",
            "run2_31_spine_climax_repair_rerun_result.json",
            "drawRun231ReadableEvidenceSpine",
            "drawRun231HeroProofScene",
            "spine_readability_and_climax_consistency",
        ],
    )


def test_run2_32_spine_climax_repair_audit_scores_run2_31_outputs(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "audit_ppt_run2_32_spine_climax_repair.py"
    assert script_path.exists(), "missing Run 2.32 spine/climax repair audit script"

    result_json = tmp_path / "run2_32_spine_climax_repair_audit.json"
    result_md = tmp_path / "run2_32_spine_climax_repair_audit.md"
    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        check=True,
    )

    audit = load_json(result_json)
    assert audit["schema_version"] == "ppt_run2_spine_climax_repair_audit.v1"
    assert audit["run_id"] == "2.32"
    assert audit["status"] == "run2_32_spine_climax_repair_audit_public_blocked"
    assert audit["source_generated_run"] == "2.31"
    assert audit["source_audit_run"] == "2.30"
    assert audit["source_repair_run"] == "2.31"
    assert audit["creates_new_ppt_deck"] is False
    assert audit["public_ready"] is False
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["input_chain"]["run2_31_full_trace_manifest"].endswith("ppt-run2-31-full-vulca/trace_manifest.json")
    assert audit["input_chain"]["run2_31_bad_trace_manifest"].endswith(
        "ppt-run2-31-bad-spine-climax-repair-memory/trace_manifest.json"
    )
    assert audit["input_chain"]["run2_30_presentation_synthesis_audit"].endswith(
        "run2_30_presentation_synthesis_audit.json"
    )
    assert audit["input_chain"]["run2_31_spine_climax_repair_rerun_result"].endswith(
        "run2_31_spine_climax_repair_rerun_result.json"
    )
    assert audit["no_new_deck_proof"]["new_pptx_created"] is False
    assert audit["no_new_deck_proof"]["status"] == "pass"

    trace = audit["trace_closure"]
    assert trace["full_arm"]["arm_id"] == "run2_31_full_spine_climax_repair"
    assert trace["full_arm"]["slide_count"] == 6
    assert trace["full_arm"]["run2_30_audit_consumed_slides"] == 6
    assert trace["full_arm"]["repair_execution_status_slides"] == 6
    assert trace["full_arm"]["readable_evidence_spine_modules_called"] == 6
    assert trace["full_arm"]["climax_style_policy_slides"] == 6
    assert trace["bad_control"]["arm_id"] == "bad_spine_climax_repair_memory"
    assert trace["bad_control"]["repair_fields_leaked"] == 0

    repair = audit["repair_verification"]
    assert repair["spine_font_target_met_by_contract"] is True
    assert repair["spine_min_font_size_target"] >= 8
    assert repair["climax_style_policy_enforced"] is True
    assert repair["climax_hero_object_canvas_share"] > 0.5
    assert repair["repair_target_closed"] is True

    summary = audit["quality_summary"]
    assert summary["repair_gate"] == "pass_internal_only"
    assert summary["public_release_gate"] == "blocked"
    assert summary["top_next_layer_to_thicken"] == "main_surface_information_density_and_visual_evidence_realism"
    assert set(summary["roles_with_low_visual_evidence_density"]) == {"cover", "setup", "contrast", "close"}
    assert "spine_readability_and_climax_consistency" in summary["closed_target_layers"]

    assert len(audit["role_records"]) == 6
    climax_records = [record for record in audit["role_records"] if record["role"] == "climax"]
    assert len(climax_records) == 1
    for record in audit["role_records"]:
        assert record["repair_trace_closure"]["run2_30_audit_status_present"] is True
        assert record["spine_repair"]["readable_spine_module_called"] is True
        assert record["spine_repair"]["spine_min_font_size_target"] >= 8
        assert record["climax_repair"]["climax_style_policy"] == "high_contrast_climax_with_shared_light_editorial_frame"
    assert climax_records[0]["climax_repair"]["hero_object_canvas_share"] > 0.5


def test_run2_32_records_spine_climax_repair_audit_result() -> None:
    result = (PACK / "results" / "run2_32_spine_climax_repair_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_32_spine_climax_repair_audit.json")

    assert result_json["status"] == "run2_32_spine_climax_repair_audit_public_blocked"
    assert result_json["source_generated_run"] == "2.31"
    assert result_json["quality_summary"]["top_next_layer_to_thicken"] == (
        "main_surface_information_density_and_visual_evidence_realism"
    )
    assert result_json["next_required_action"] == (
        "thicken_run2_31_main_surface_information_density_and_visual_evidence_realism_before_run2_33_rerun"
    )
    assert_contains(
        result,
        [
            "Run 2.32 Spine/Climax Repair Audit",
            "audit-only",
            "2.31",
            "2.30",
            "drawRun231ReadableEvidenceSpine",
            "drawRun231HeroProofScene",
            "main_surface_information_density_and_visual_evidence_realism",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_32_spine_climax_repair_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_32_spine_climax_repair_audit.json",
            "Run 2.32 spine/climax repair audit",
            "repair_target_closed",
            "main_surface_information_density_and_visual_evidence_realism",
            "roles_with_low_visual_evidence_density",
            "creates no new PPT deck",
        ],
    )


def test_run2_33_generator_consumes_run2_32_audit_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_33_main_surface_visual_evidence_arms.mjs"
    assert script_path.exists(), "missing Run 2.33 main-surface visual-evidence generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_33_full_main_surface_visual_evidence",
        "bad_main_surface_visual_evidence_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    required_inputs = [
        "run2_32_spine_climax_repair_audit.json",
        "run2_31_spine_climax_repair_rerun_result.json",
        "run2_30_presentation_synthesis_audit.json",
        "run2_29_presentation_synthesis_memory.json",
        "run2_28_evidence_chain_view_model.json",
        "run2_24_single_usecase_content_memory.json",
        "run2_24_visual_evidence_asset_memory.json",
        "run2_24_content_visual_workflow_gates.json",
    ]

    assert_contains(
        body,
        [
            "validateRun232SpineClimaxRepairAudit",
            "loadRun233ContractData",
            "drawRun233MainSurfaceEvidenceLayer",
            "drawRun233VisualEvidenceStoryboard",
            "drawRun233ReadableEvidenceSpine",
            "main_surface_information_density_and_visual_evidence_realism",
            "run2_32_source_audit_status",
            "run2_32_top_next_layer_to_thicken",
            "run2_33_visual_evidence_object_min_target",
            "run2_33_main_surface_visual_evidence_execution_status",
            "main_surface_information_density_and_visual_evidence_realism_thickened_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_33_full_main_surface_visual_evidence"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_33_full_main_surface_visual_evidence"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_main_surface_visual_evidence_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_main_surface_visual_evidence_memory"), "forbidden:", "palette:")

    for term in required_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun233 = arm.armId === "run2_33_full_main_surface_visual_evidence";' in body
    assert 'registerRun233Module(metrics, "drawRun233MainSurfaceEvidenceLayer")' in body
    for field in [
        "run2_32_source_audit_status",
        "run2_32_top_next_layer_to_thicken",
        "run2_33_visual_evidence_object_min_target",
        "run2_33_main_surface_visual_evidence_execution_status",
    ]:
        assert re.search(fr"{field}:\s*fullRun233\s*\?", body), field


def test_run2_33_records_main_surface_visual_evidence_rerun_result() -> None:
    result = (PACK / "results" / "run2_33_main_surface_visual_evidence_rerun_result.md").read_text(
        encoding="utf-8"
    )
    result_json = load_json(PACK / "results" / "run2_33_main_surface_visual_evidence_rerun_result.json")
    presentations = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
    full_trace = load_json(presentations / "ppt-run2-33-full-vulca" / "trace_manifest.json")

    assert result_json["status"] == "run2_33_main_surface_visual_evidence_rerun_public_blocked"
    assert result_json["source_audit_run_id"] == "2.32"
    assert result_json["input_chain"]["spine_climax_repair_audit"].endswith(
        "run2_32_spine_climax_repair_audit.json"
    )
    assert result_json["rerun"]["best_internal_arm"] == "run2_33_full_main_surface_visual_evidence"
    assert result_json["rerun"]["best_internal_arm_verdict"] == (
        "main_surface_information_density_and_visual_evidence_realism_thickened_before_native_ppt_generation"
    )
    assert result_json["quality_delta"]["target_layer"] == "main_surface_information_density_and_visual_evidence_realism"
    assert result_json["quality_delta"]["visual_evidence_object_min_target"] >= 2
    assert result_json["quality_delta"]["source_repair_target_closed"] is True
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-33-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")

    assert full_trace["arm_id"] == "run2_33_full_main_surface_visual_evidence"
    assert len(full_trace["slides"]) == 6
    for slide in full_trace["slides"]:
        assert slide["run2_32_top_next_layer_to_thicken"] == "main_surface_information_density_and_visual_evidence_realism"
        assert slide["run2_33_visual_evidence_object_min_target"] >= 2
        assert slide["run2_33_main_surface_visual_evidence_execution_status"] == (
            "main_surface_information_density_and_visual_evidence_realism_thickened_before_native_ppt_generation"
        )
        assert slide["layout_metrics"]["visual_evidence_objects"] >= 2
        assert "drawRun233MainSurfaceEvidenceLayer" in slide["run2_33_code_module_ids"]

    assert_contains(
        result,
        [
            "Run 2.33",
            "Run 2.32 spine/climax repair audit",
            "drawRun233MainSurfaceEvidenceLayer",
            "drawRun233VisualEvidenceStoryboard",
            "main_surface_information_density_and_visual_evidence_realism",
            "four-arm rerun",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_33_main_surface_visual_evidence_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.33",
            "ppt-run2-33-prompt-only",
            "ppt-run2-33-run1-5-skill",
            "ppt-run2-33-full-vulca",
            "ppt-run2-33-bad-main-surface-visual-evidence-memory",
            "run2_33_main_surface_visual_evidence_rerun_result.json",
            "drawRun233MainSurfaceEvidenceLayer",
            "drawRun233VisualEvidenceStoryboard",
            "main_surface_information_density_and_visual_evidence_realism",
        ],
    )


def test_run2_34_main_surface_visual_evidence_audit_scores_run2_33_outputs(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "audit_ppt_run2_34_main_surface_visual_evidence.py"
    assert script_path.exists(), "missing Run 2.34 main-surface visual-evidence audit script"

    result_json = tmp_path / "run2_34_main_surface_visual_evidence_audit.json"
    result_md = tmp_path / "run2_34_main_surface_visual_evidence_audit.md"
    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        check=True,
    )

    audit = load_json(result_json)
    assert audit["schema_version"] == "ppt_run2_main_surface_visual_evidence_audit.v1"
    assert audit["run_id"] == "2.34"
    assert audit["status"] == "run2_34_main_surface_visual_evidence_audit_public_blocked"
    assert audit["source_generated_run"] == "2.33"
    assert audit["source_audit_run"] == "2.32"
    assert audit["source_rerun_run"] == "2.33"
    assert audit["creates_new_ppt_deck"] is False
    assert audit["public_ready"] is False
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["input_chain"]["run2_33_full_trace_manifest"].endswith("ppt-run2-33-full-vulca/trace_manifest.json")
    assert audit["input_chain"]["run2_33_bad_trace_manifest"].endswith(
        "ppt-run2-33-bad-main-surface-visual-evidence-memory/trace_manifest.json"
    )
    assert audit["input_chain"]["run2_33_rerun_result"].endswith(
        "run2_33_main_surface_visual_evidence_rerun_result.json"
    )
    assert audit["input_chain"]["run2_32_spine_climax_repair_audit"].endswith(
        "run2_32_spine_climax_repair_audit.json"
    )
    assert audit["no_new_deck_proof"]["new_pptx_created"] is False
    assert audit["no_new_deck_proof"]["status"] == "pass"

    trace = audit["trace_closure"]
    assert trace["full_arm"]["arm_id"] == "run2_33_full_main_surface_visual_evidence"
    assert trace["full_arm"]["slide_count"] == 6
    assert trace["full_arm"]["run2_32_audit_consumed_slides"] == 6
    assert trace["full_arm"]["main_surface_execution_status_slides"] == 6
    assert trace["full_arm"]["main_surface_evidence_layer_modules_called"] == 6
    assert trace["full_arm"]["visual_evidence_storyboard_modules_called"] == 6
    assert trace["full_arm"]["visual_evidence_object_target_slides"] == 6
    assert trace["bad_control"]["arm_id"] == "bad_main_surface_visual_evidence_memory"
    assert trace["bad_control"]["main_surface_fields_leaked"] == 0

    verification = audit["main_surface_verification"]
    assert verification["source_audit_target"] == "main_surface_information_density_and_visual_evidence_realism"
    assert verification["source_rerun_verdict"] == (
        "main_surface_information_density_and_visual_evidence_realism_thickened_before_native_ppt_generation"
    )
    assert verification["visual_evidence_object_target_met"] is True
    assert verification["main_surface_modules_called_by_contract"] is True
    assert verification["delivery_gate"] == "internal-demo-ok-public-blocked"
    assert verification["static_no_animation"] is True
    assert verification["human_review_required"] is True

    summary = audit["quality_summary"]
    assert summary["main_surface_visual_evidence_gate"] == "pass_internal_only"
    assert summary["public_release_gate"] == "blocked"
    assert "main_surface_information_density_and_visual_evidence_realism" in summary["closed_target_layers"]
    assert summary["top_next_layer_to_thicken"] == (
        "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
    )
    assert set(summary["roles_with_weak_editorial_anchor"]) == {"cover", "setup", "contrast", "close"}
    assert set(summary["roles_with_schematic_visual_evidence"]) == {
        "cover",
        "setup",
        "contrast",
        "proof",
        "climax",
        "close",
    }

    assert len(audit["role_records"]) == 6
    for record in audit["role_records"]:
        assert record["main_surface_trace_closure"]["run2_32_audit_status_present"] is True
        assert record["main_surface_trace_closure"]["execution_status_present"] is True
        assert record["main_surface_modules"]["main_surface_evidence_layer_called"] is True
        assert record["main_surface_modules"]["visual_evidence_storyboard_called"] is True
        assert record["main_surface_density"]["visual_evidence_objects"] >= 2
        assert record["main_surface_density"]["visual_evidence_object_target_met"] is True
        assert record["visual_evidence_realism"]["schematic_visual_evidence"] is True
        assert record["bad_control_leaked_field_count"] == 0


def test_run2_34_records_main_surface_visual_evidence_audit_result() -> None:
    result = (PACK / "results" / "run2_34_main_surface_visual_evidence_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_34_main_surface_visual_evidence_audit.json")

    assert result_json["status"] == "run2_34_main_surface_visual_evidence_audit_public_blocked"
    assert result_json["source_generated_run"] == "2.33"
    assert result_json["quality_summary"]["top_next_layer_to_thicken"] == (
        "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
    )
    assert result_json["next_required_action"] == (
        "thicken_run2_33_visual_evidence_asset_realism_and_editorial_composition_before_run2_35_data_workflow"
    )
    assert_contains(
        result,
        [
            "Run 2.34 Main Surface Visual Evidence Audit",
            "audit-only",
            "2.33",
            "2.32",
            "drawRun233MainSurfaceEvidenceLayer",
            "drawRun233VisualEvidenceStoryboard",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
            "Run 2.35 data/workflow",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_34_main_surface_visual_evidence_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_34_main_surface_visual_evidence_audit.json",
            "Run 2.34 main-surface visual-evidence audit",
            "creates no new PPT deck",
            "main_surface_visual_evidence_gate",
            "roles_with_schematic_visual_evidence",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
            "Run 2.35 data/workflow",
        ],
    )


def test_run2_35_builder_writes_visual_evidence_realism_workflow_pack(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "build_ppt_run2_35_visual_evidence_realism_workflow.py"
    assert script_path.exists(), "missing Run 2.35 visual-evidence realism workflow builder"

    result_json = tmp_path / "run2_35_visual_evidence_realism_workflow_result.json"
    result_md = tmp_path / "run2_35_visual_evidence_realism_workflow_result.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--out-dir",
            str(tmp_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    realism_memory = load_json(tmp_path / "run2_35_visual_evidence_asset_realism_memory.json")
    composition_memory = load_json(tmp_path / "run2_35_editorial_composition_memory.json")
    workflow_gates = load_json(tmp_path / "run2_35_visual_evidence_workflow_gates.json")
    result = load_json(result_json)
    report = result_md.read_text(encoding="utf-8")

    assert result["status"] == "run2_35_visual_evidence_realism_workflow_ready_public_blocked"
    assert result["run_id"] == "2.35"
    assert result["source_audit_run"] == "2.34"
    assert result["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert result["creates_new_ppt_deck"] is False
    assert result["public_ready"] is False
    assert result["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result["next_required_action"] == "consume_run2_35_visual_evidence_realism_workflow_before_run2_36_rerun"
    assert result["delivery_artifacts"] == {
        "pptx_paths": [],
        "rendered_slide_paths": [],
        "contact_sheet_paths": [],
        "html_motion_renderer_paths": [],
    }

    assert realism_memory["status"] == "run2_35_visual_evidence_asset_realism_memory_ready_public_blocked"
    assert realism_memory["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert realism_memory["source_audit_target"] == "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
    assert realism_memory["storage_policy"]["raw_media"] == "forbidden"
    assert realism_memory["storage_policy"]["copied_screenshots"] == "forbidden"
    assert len(realism_memory["visual_evidence_asset_realism_records"]) == 12
    for record in realism_memory["visual_evidence_asset_realism_records"]:
        assert record["realism_memory_id"].startswith("realism_2_35_")
        assert record["role"] in {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert record["parent_run2_24_asset_id"].startswith("asset_2_24_")
        assert record["source_ids"]
        assert record["observable_product_state"]
        assert record["business_context_caption"]
        assert record["audience_question_answered"]
        assert record["native_ppt_realism_strategy"]
        assert record["anti_schematic_constraints"]
        assert "generic block diagram" in " ".join(record["anti_schematic_constraints"])
        assert "run2_35_visual_evidence_asset_realism_ids" in record["required_trace_fields"]
        assert record["public_surface_allowed"] is True
        assert record["source_boundary"].startswith("Derived")

    assert composition_memory["status"] == "run2_35_editorial_composition_memory_ready_public_blocked"
    assert len(composition_memory["editorial_composition_records"]) == 6
    weak_roles = {"cover", "setup", "contrast", "close"}
    for record in composition_memory["editorial_composition_records"]:
        assert record["composition_memory_id"].startswith("composition_2_35_")
        assert record["role"] in {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert record["editorial_anchor_object"]
        assert record["hero_canvas_share_target"] >= 0.35
        assert record["composition_obligations"]
        assert "equal-weight schematic panels" in record["forbidden_patterns"]
        assert "run2_35_editorial_composition_memory_id" in record["required_trace_fields"]
        if record["role"] in weak_roles:
            assert record["repairs_run2_34_weak_editorial_anchor"] is True

    assert workflow_gates["status"] == "run2_35_visual_evidence_workflow_gates_ready_public_blocked"
    assert len(workflow_gates["gates"]) == 6
    for gate in workflow_gates["gates"]:
        assert gate["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
        assert gate["required_realism_memory_ids"]
        assert gate["required_editorial_composition_memory_id"].startswith("composition_2_35_")
        assert gate["min_realistic_visual_evidence_objects"] >= 2
        assert gate["forbid_generic_block_diagrams"] is True
        assert "run2_35_visual_evidence_asset_realism_ids" in gate["required_trace_fields"]
        assert "run2_35_realism_gate_id" in gate["required_trace_fields"]
        assert gate["next_rerun_contract"] == "must_be_consumed_before_run2_36_four_arm_rerun"
        assert gate["public_release_gate"] == "blocked"

    assert_contains(
        report,
        [
            "Run 2.35",
            "visual evidence asset realism",
            "editorial composition",
            "workflow gates",
            "Run 2.35 data/workflow",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
    assert not list(tmp_path.glob("*.pptx"))


def test_run2_35_records_visual_evidence_realism_workflow_result() -> None:
    result = (PACK / "results" / "run2_35_visual_evidence_realism_workflow_result.md").read_text(
        encoding="utf-8"
    )
    result_json = load_json(PACK / "results" / "run2_35_visual_evidence_realism_workflow_result.json")
    realism_memory = load_json(PACK / "run2_35_visual_evidence_asset_realism_memory.json")
    composition_memory = load_json(PACK / "run2_35_editorial_composition_memory.json")
    workflow_gates = load_json(PACK / "run2_35_visual_evidence_workflow_gates.json")
    workflow = load_json(PACK / "skill_workflow.json")

    assert result_json["status"] == "run2_35_visual_evidence_realism_workflow_ready_public_blocked"
    assert result_json["source_audit_run"] == "2.34"
    assert result_json["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["public_ready"] is False
    assert result_json["artifact_counts"] == {
        "visual_evidence_asset_realism_records": 12,
        "editorial_composition_records": 6,
        "visual_evidence_workflow_gates": 6,
    }
    assert len(realism_memory["visual_evidence_asset_realism_records"]) == 12
    assert len(composition_memory["editorial_composition_records"]) == 6
    assert len(workflow_gates["gates"]) == 6
    assert workflow["status"] == "run2_35_visual_evidence_realism_workflow_directed_public_blocked"
    assert {stage["id"] for stage in workflow["stages"]} >= {
        "compile_run2_35_visual_evidence_asset_realism_memory",
        "compile_run2_35_editorial_composition_memory",
        "apply_run2_35_visual_evidence_workflow_gates",
    }
    assert any(
        trigger["id"] == "run2_35_visual_evidence_realism_required_before_run2_36_rerun"
        for trigger in workflow["repair_triggers"]
    )
    assert_contains(
        result,
        [
            "Run 2.35",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
            "visual evidence asset realism",
            "editorial composition",
            "Run 2.36",
            "public blocked",
        ],
    )


def test_ppt_run_html_viewer_embeds_run2_35_visual_evidence_realism_workflow() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_35_visual_evidence_asset_realism_memory.json",
            "run2_35_editorial_composition_memory.json",
            "run2_35_visual_evidence_workflow_gates.json",
            "run2_35_visual_evidence_realism_workflow_result.json",
            "Run 2.35 visual evidence realism workflow",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
            "Run 2.36",
        ],
    )


def test_ppt_run_html_viewer_loads_run2_35_reference_data(tmp_path: Path) -> None:
    presentations = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
    data = build_data(presentations, tmp_path / "ppt-run-viewer.html")
    refs = data["references"]

    assert refs["run235ResultStatus"] == "run2_35_visual_evidence_realism_workflow_ready_public_blocked"
    assert refs["run235Result"]["target_layer"] == (
        "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
    )
    assert refs["run235Result"]["creates_new_ppt_deck"] is False
    assert refs["run235Result"]["next_required_action"] == (
        "consume_run2_35_visual_evidence_realism_workflow_before_run2_36_rerun"
    )
    assert len(refs["run235RealismMemory"]) == 12
    assert len(refs["run235CompositionMemory"]) == 6
    assert len(refs["run235WorkflowGates"]) == 6
    assert {
        "run2_35_visual_evidence_asset_realism_ids",
        "run2_35_editorial_composition_memory_id",
        "run2_35_realism_gate_id",
    } <= set(refs["run235WorkflowGates"][0]["required_trace_fields"])


def test_run2_36_generator_consumes_run2_35_realism_workflow_before_native_ppt_code() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_36_visual_evidence_realism_arms.mjs"
    assert script_path.exists(), "missing Run 2.36 visual-evidence realism generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = [
        "prompt_only",
        "run1_5_skill",
        "run2_36_full_visual_evidence_realism",
        "bad_visual_evidence_realism_memory",
    ]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    required_inputs = [
        "run2_35_visual_evidence_asset_realism_memory.json",
        "run2_35_editorial_composition_memory.json",
        "run2_35_visual_evidence_workflow_gates.json",
        "run2_35_visual_evidence_realism_workflow_result.json",
        "run2_34_main_surface_visual_evidence_audit.json",
        "run2_33_main_surface_visual_evidence_rerun_result.json",
    ]

    assert_contains(
        body,
        [
            "validateRun235VisualEvidenceRealismWorkflow",
            "loadRun236ContractData",
            "drawRun236RealisticProductState",
            "drawRun236EditorialAnchorObject",
            "drawRun236RealismGateRibbon",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
            "run2_35_visual_evidence_asset_realism_ids",
            "run2_35_editorial_composition_memory_id",
            "run2_35_realism_gate_id",
            "run2_35_observable_product_state",
            "run2_35_hero_canvas_share_target",
            "run2_35_visual_evidence_realism_execution_status",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_36_full_visual_evidence_realism"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_36_full_visual_evidence_realism"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_visual_evidence_realism_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_visual_evidence_realism_memory"), "forbidden:", "palette:")

    for term in required_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden
        assert term not in bad_allowed
        assert term in bad_forbidden

    assert 'const fullRun236 = arm.armId === "run2_36_full_visual_evidence_realism";' in body
    assert 'registerRun236Module(metrics, "drawRun236RealisticProductState")' in body
    for field in [
        "run2_35_visual_evidence_asset_realism_ids",
        "run2_35_editorial_composition_memory_id",
        "run2_35_realism_gate_id",
        "run2_35_observable_product_state",
        "run2_35_hero_canvas_share_target",
        "run2_35_visual_evidence_realism_execution_status",
    ]:
        assert re.search(fr"{field}:\s*fullRun236\s*\?", body), field


def test_run2_36_records_visual_evidence_realism_rerun_result() -> None:
    result = (PACK / "results" / "run2_36_visual_evidence_realism_rerun_result.md").read_text(
        encoding="utf-8"
    )
    result_json = load_json(PACK / "results" / "run2_36_visual_evidence_realism_rerun_result.json")
    presentations = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
    full_trace = load_json(presentations / "ppt-run2-36-full-vulca" / "trace_manifest.json")
    bad_trace = load_json(
        presentations / "ppt-run2-36-bad-visual-evidence-realism-memory" / "trace_manifest.json"
    )

    assert result_json["status"] == "run2_36_visual_evidence_realism_rerun_public_blocked"
    assert result_json["source_data_workflow_run_id"] == "2.35"
    assert result_json["input_chain"]["visual_evidence_asset_realism_memory"].endswith(
        "run2_35_visual_evidence_asset_realism_memory.json"
    )
    assert result_json["input_chain"]["editorial_composition_memory"].endswith(
        "run2_35_editorial_composition_memory.json"
    )
    assert result_json["input_chain"]["visual_evidence_workflow_gates"].endswith(
        "run2_35_visual_evidence_workflow_gates.json"
    )
    assert result_json["rerun"]["best_internal_arm"] == "run2_36_full_visual_evidence_realism"
    assert result_json["rerun"]["best_internal_arm_verdict"] == (
        "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation"
    )
    assert result_json["quality_delta"]["target_layer"] == (
        "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
    )
    assert result_json["quality_delta"]["run2_35_realism_records_consumed"] == 12
    assert result_json["quality_delta"]["run2_35_composition_records_consumed"] == 6
    assert result_json["quality_delta"]["run2_35_workflow_gates_consumed"] == 6
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-36-four-arm-contact-sheet.png")
    assert result_json["rerun"]["full_skill_series_sheet"].endswith("run2-full-skill-series-horizontal.png")

    assert full_trace["arm_id"] == "run2_36_full_visual_evidence_realism"
    assert full_trace["run2_35_workflow_status"] == "run2_35_visual_evidence_realism_workflow_ready_public_blocked"
    assert len(full_trace["slides"]) == 6
    for slide in full_trace["slides"]:
        assert len(slide["run2_35_visual_evidence_asset_realism_ids"]) >= 2
        assert slide["run2_35_editorial_composition_memory_id"].startswith("composition_2_35_")
        assert slide["run2_35_realism_gate_id"].startswith("gate_2_35_")
        assert slide["run2_35_observable_product_state"]
        assert slide["run2_35_hero_canvas_share_target"] >= 0.35
        assert slide["run2_35_visual_evidence_realism_execution_status"] == (
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation"
        )
        assert slide["layout_metrics"]["realistic_visual_evidence_objects"] >= 2
        assert slide["layout_metrics"]["hero_object_canvas_share"] >= 0.35
        assert "drawRun236RealisticProductState" in slide["run2_36_code_module_ids"]
        assert "drawRun236EditorialAnchorObject" in slide["run2_36_code_module_ids"]
        assert "drawRun236RealismGateRibbon" in slide["run2_36_code_module_ids"]

    assert bad_trace["arm_id"] == "bad_visual_evidence_realism_memory"
    for slide in bad_trace["slides"]:
        assert slide["run2_35_visual_evidence_asset_realism_ids"] == []
        assert slide["run2_35_editorial_composition_memory_id"] == ""
        assert slide["run2_35_realism_gate_id"] == ""

    assert_contains(
        result,
        [
            "Run 2.36",
            "Run 2.35 visual evidence realism workflow",
            "drawRun236RealisticProductState",
            "drawRun236EditorialAnchorObject",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
            "four-arm rerun",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_ppt_run_html_viewer_mentions_run2_36_visual_evidence_realism_rerun() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.36",
            "ppt-run2-36-prompt-only",
            "ppt-run2-36-run1-5-skill",
            "ppt-run2-36-full-vulca",
            "ppt-run2-36-bad-visual-evidence-realism-memory",
            "run2_36_visual_evidence_realism_rerun_result.json",
            "drawRun236RealisticProductState",
            "drawRun236EditorialAnchorObject",
            "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
        ],
    )


def test_ppt_layout_quality_checker_flags_geometry_failures(tmp_path: Path) -> None:
    layout_dir = tmp_path / "layout"
    layout_dir.mkdir()
    ok_path = layout_dir / "slide-01.layout.json"
    bad_path = layout_dir / "slide-02.layout.json"
    out_path = tmp_path / "layout-report.txt"

    ok_path.write_text(
        json.dumps(
            {
                "slide": {"frame": {"width": 1280, "height": 720}},
                "elements": [
                    {
                        "id": "headline",
                        "text": "One clear headline",
                        "bbox": [80, 80, 520, 64],
                        "resolvedFontSize": 28,
                        "textLayout": {"lineCount": 1},
                    },
                    {"id": "proof-object", "bbox": [760, 120, 320, 240]},
                ],
            }
        ),
        encoding="utf-8",
    )
    bad_path.write_text(
        json.dumps(
            {
                "slide": {"frame": {"width": 1280, "height": 720}},
                "elements": [
                    {
                        "id": "escaped",
                        "text": "Escaped box",
                        "bbox": [-10, 20, 200, 40],
                        "resolvedFontSize": 18,
                        "textLayout": {"lineCount": 1},
                    },
                    {
                        "id": "overlap-a",
                        "text": "Overlap A",
                        "bbox": [50, 50, 200, 40],
                        "resolvedFontSize": 18,
                        "textLayout": {"lineCount": 1},
                    },
                    {
                        "id": "overlap-b",
                        "text": "Overlap B",
                        "bbox": [60, 55, 190, 38],
                        "resolvedFontSize": 18,
                        "textLayout": {"lineCount": 1},
                    },
                    {
                        "id": "microtype",
                        "text": "Fine print",
                        "bbox": [300, 300, 100, 5],
                        "resolvedFontSize": 6,
                        "textLayout": {"lineCount": 1},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    issue_codes = {issue.code for issue in check_layout(bad_path)}
    assert {"out-of-bounds", "text-overlap", "microtype", "tight-text"} <= issue_codes

    report = write_report(layout_dir, out_path)

    assert report == {"layout_files": 2, "layout_errors": 2, "layout_warnings": 2}
    assert "text-overlap" in out_path.read_text(encoding="utf-8")


def test_ppt_contact_sheet_supports_custom_labels(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    out = tmp_path / "sheet.png"
    Image.new("RGB", (160, 90), "#ffffff").save(first)
    Image.new("RGB", (160, 90), "#111318").save(second)

    build_contact_sheet([first, second], out, "Two arm sheet", cols=2, labels=["Prompt-only", "Full arm"])

    assert out.exists()
    sheet = Image.open(out)
    assert sheet.size[0] > 0
    assert sheet.size[1] > 0


def test_run2_bad_aesthetic_memory_has_structured_replacement() -> None:
    replacement = load_json(PACK / "generation_briefs" / "bad_aesthetic_memory_replacement.json")

    assert replacement["replacement_for"] == "aesthetic_memory.json"
    assert replacement["status"] == "negative-control-only"
    assert EXPECTED_MOVES <= {move["aesthetic_move"] for move in replacement["moves"]}
    for move in replacement["moves"]:
        assert EXPECTED_BAD_MEMORY_FIELDS <= set(move)
        assert move["rhythm_role"] in EXPECTED_RHYTHM_ROLES
        assert move["negative_rules"]
        assert {"max_claims", "max_panels", "max_words"} <= set(move["density_budget"])
    assert_contains(json.dumps(replacement), ["dashboard", "dense", "small labels", "no visual climax"])


def test_run2_results_reviewed_and_public_blocked() -> None:
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    assert_contains(comparison, ["Status", "run2_18-thickness-pack-public-blocked"])
    assert_contains(comparison, ["Prior delivery status", "motion-renderer-proof-public-blocked"])
    assert_contains(
        comparison,
        [
            "Run 2.17 Motion Proof",
            "run2_17_motion_renderer_proof_result.json",
            "separate HTML motion renderer",
            "cover_attention_reset",
            "before_after_reveal",
            "climax_scale_emphasis",
        ],
    )
    assert_contains(
        comparison,
        [
            "Run 2.17",
            "run2_17_motion_delivery_audit.json",
            "HTML viewer is static",
            "Keynote readout",
        ],
    )
    assert_contains(comparison, ["Run 2.16", "latest reviewed generated PPT result"])
    assert_contains(
        comparison,
        [
            "Run 2.13",
            "run2_13_full_skill",
            "run2_12_thick_multimodal_evidence.json",
            "bad_thick_data_memory",
        ],
    )
    assert_contains(
        comparison,
        [
            "Run 2.12",
            "run2_12_thick_multimodal_evidence.json",
            "run2_12_design_memory_seed.json",
            "run2_12_workflow_gate_seed.json",
        ],
    )
    assert_contains(comparison, ["prompt_only", "run1_5_skill", "run2_skill", "bad_aesthetic_memory"])
    assert_contains(
        comparison,
        ["Run 2.3", "run2_3_full_skill", "visual_component_execution", "native visual components"],
    )
    assert_contains(
        comparison,
        ["Run 2.4", "motion grammar", "video_demo_beat_map", "presentation_sequence_components"],
    )
    assert_contains(
        comparison,
        ["Run 2.6", "run2_6_full_skill", "data_workflow_policy_execution", "workflow_decision_policy"],
    )
    assert_contains(
        comparison,
        [
            "Run 2.10",
            "run2_10_full_skill",
            "run2_10_visual_system_memory.json",
            "actual code module ids",
        ],
    )
    assert_contains(
        comparison,
        [
            "Run 2.8",
            "run2_8_full_skill",
            "run2_8_executable_design_memory.json",
            "actual native module calls",
        ],
    )
    assert_contains(
        comparison,
        ["Run 2.2", "run2_2_full_skill", "multimodal_learning", "visual_learning_target_execution"],
    )
    assert_contains(comparison, ["Run 2.1", "run2_1_full_skill", "product learning", "not public-release claims"])
    assert "0.00" not in comparison
    assert_contains(delivery, ["public publishing", "blocked", "native render", "human approval", "trace manifest"])
    assert_contains(delivery, ["Run 2.3", "pass for local Run 2.3 arms", "native visual components"])
    assert_contains(delivery, ["Run 2.6", "run2-6-four-arm-contact-sheet", "workflow_decision_policy"])
    assert_contains(
        delivery,
        ["Run 2.8", "run2-8-four-arm-contact-sheet", "actual native module calls"],
    )
    assert_contains(
        delivery,
        ["Run 2.10", "run2-10-four-arm-contact-sheet", "actual native visual-system module calls"],
    )
    assert_contains(
        delivery,
        ["Run 2.13", "run2-13-four-arm-contact-sheet", "Run 2.13 full-arm trace includes Run 2.12 evidence"],
    )
    assert_contains(delivery, ["Run 2.2", "run2-2-four-arm-contact-sheet", "public-video-grade visual proof"])
    assert trace_contract["required_output_name"] == "trace_manifest.json"
    assert "aesthetic_move_ids" in trace_contract["per_slide_required_fields"]
    assert "visual_component_ids" in trace_contract["per_slide_required_fields"]
    assert "video_beat_ids" in trace_contract["per_slide_required_fields"]
    assert "motion_target_ids" in trace_contract["per_slide_required_fields"]
    assert "sequence_component_ids" in trace_contract["per_slide_required_fields"]
    assert "runtime_isolation" in trace_contract["arm_required_fields"]
    assert "native_ppt_checks" in trace_contract["per_slide_required_fields"]
    assert "layout_geometry_checks" in trace_contract["per_slide_required_fields"]
    assert "commercial_usecase_id" in trace_contract["per_slide_required_fields"]
    assert "aesthetic_benchmark_ids" in trace_contract["per_slide_required_fields"]
    assert "theme_policy_id" in trace_contract["per_slide_required_fields"]
    assert EXPECTED_RUN2_13_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
    assert EXPECTED_RUN2_14_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
    assert EXPECTED_RUN2_15_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
    assert EXPECTED_RUN2_16_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
    assert trace_contract["native_ppt_thresholds"]["full_slide_rasterized_allowed"] is False


def test_run2_3_records_native_component_rerun_result() -> None:
    result = (PACK / "results" / "run2_3_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_3_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_3_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert (
        result_json["rerun"]["best_internal_arm_verdict"]
        == "native_visual_components_visible_but_not_public_release_ready"
    )
    assert result_json["next_required_action"] == "turn_component_execution_into_public_grade_visual_system"
    assert_contains(
        json.dumps(result_json["native_component_learning"]),
        ["native_component_visible", "layout_errors_zero", "still_internal_demo_grade"],
    )
    assert_contains(
        result,
        [
            "Run 2.3",
            "visual_target_components.json",
            "native visual components",
            "before/after thumbnail",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_4_records_motion_sequence_rerun_result() -> None:
    result = (PACK / "results" / "run2_4_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_4_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_4_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert result_json["rerun"]["best_internal_arm_verdict"] == "motion_sequence_visible_but_not_public_video_grade"
    assert (
        result_json["next_required_action"]
        == "thicken_public_grade_visual_system_and_motion_rendering_then_rerun_same_five_layers"
    )
    assert_contains(
        json.dumps(result_json["motion_sequence_learning"]),
        [
            "native_sequence_visible",
            "video_beat_ids_motion_target_ids_sequence_component_ids_ordered_reveal_steps_present",
            "still_schematic_internal_demo_grade",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.4",
            "motion",
            "sequence",
            "run2_4_full_skill",
            "public-video-grade",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_5_records_production_design_rerun_result() -> None:
    result = (PACK / "results" / "run2_5_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_5_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_5_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert (
        result_json["rerun"]["best_internal_arm_verdict"]
        == "production_modules_visible_but_not_public_release_ready"
    )
    assert result_json["next_required_action"] == "native_render_and_human_review_then_deepen_visual_polish_if_needed"
    assert_contains(
        json.dumps(result_json["production_design_learning"]),
        [
            "production_reference_ids",
            "aesthetic_memory_v2_ids",
            "visual_production_module_ids",
            "fallback_policy_recorded",
            "still_internal_demo_grade",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.5",
            "production_reference_decompositions.json",
            "aesthetic_memory_v2.json",
            "visual_production_modules.json",
            "run2_5_full_skill",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_6_records_data_workflow_rerun_result() -> None:
    result = (PACK / "results" / "run2_6_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_6_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_6_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert (
        result_json["rerun"]["best_internal_arm_verdict"]
        == "data_workflow_policy_visible_but_not_public_release_ready"
    )
    assert result_json["next_required_action"] == "deepen_same_five_layers_with_visual_quality_not_run3"
    assert_contains(
        json.dumps(result_json["data_workflow_learning"]),
        [
            "commercial_usecase_id",
            "aesthetic_benchmark_ids",
            "theme_policy_id",
            "typography_system_id",
            "spacing_token_set_id",
            "source_brand_sanitization",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.6",
            "commercial_usecase_bank.json",
            "aesthetic_benchmark_bank.json",
            "workflow_decision_policy.json",
            "run2_6_full_skill",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_6r_records_visual_repair_rerun_result() -> None:
    result = (PACK / "results" / "run2_6r_visual_repair_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_6r_visual_repair_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_6r_visual_repair_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert result_json["rerun"]["best_internal_arm_verdict"] in {
        "visual_repair_visible_but_not_public_release_ready",
        "visual_repair_insufficient_same_stage_repeat_required",
    }
    assert result_json["next_required_action"] in {
        "native_render_and_human_review_then_continue_same_five_layers_if_needed",
        "repeat_same_stage_visual_repair_before_native_review",
    }
    assert_contains(
        json.dumps(result_json["visual_repair_learning"]),
        [
            "visual_repair_policy_ids",
            "visual_delta_from_run2_5",
            "visual_repair_validation_probe",
            "typography",
            "spacing",
            "climax",
            "theme",
        ],
    )
    assert result_json["qa_summary"]["arm_isolation_guard"] == "passed"
    assert result_json["qa_summary"]["run2_6r_full_media_entries"] == 0
    assert result_json["qa_summary"]["run2_6r_full_picture_shapes"] == 0
    assert result_json["qa_summary"]["run2_6r_full_native_shape_minimum_passed"] is True
    assert_contains(
        result,
        [
            "Run 2.6R",
            "visual_repair_policy.json",
            "run2_6r_visual_repair_full_skill",
            "full-skill-series",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_8_records_executable_design_memory_rerun_result() -> None:
    result = (PACK / "results" / "run2_8_executable_design_memory_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_8_executable_design_memory_result.json")
    gate_json = load_json(PACK / "results" / "run2_8_visual_qa_gate.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_8_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert result_json["qa_summary"]["arm_isolation_guard"] == "passed"
    assert result_json["qa_summary"]["trace_truthfulness_guard"] == "passed"
    assert result_json["qa_summary"]["run2_8_full_media_entries"] == 0
    assert result_json["qa_summary"]["run2_8_full_picture_shapes"] == 0
    assert result_json["control_boundary"]["bad_memory_schema"].startswith("commercial_case_plus_decomposition_only")
    assert "run2-8-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert gate_json["status"] == "run2_8_visual_qa_gate_public_blocked"
    assert gate_json["observed"]["full_arm_trace_origin"] == "actual_native_module_calls"
    assert gate_json["observed"]["full_arm_required_code_bindings_missing"] == 0
    assert gate_json["observed"]["full_arm_budget_failures"] == 0
    assert gate_json["decision"] == "public_blocked"
    assert_contains(
        json.dumps(result_json["five_layer_learning"]),
        [
            "run2_8_tutorial_decomposition.json",
            "run2_8_executable_design_memory.json",
            "run2_8_workflow_gate_matrix.json",
            "actual native module calls",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.8",
            "executable design memory",
            "HTML viewer",
            "workflow gate matrix",
            "actual native module calls",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_9_records_visual_primitive_rerun_result() -> None:
    result = (PACK / "results" / "run2_9_visual_primitive_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_9_visual_primitive_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_9_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert "run2-9-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert result_json["qa_summary"]["trace_truthfulness_guard"].startswith("passed")
    assert result_json["qa_summary"]["case_pack_validator"] == "passed with --profile run2"
    assert result_json["control_boundary"]["bad_visual_primitive_memory"].startswith("commercial_case_plus_visual_primitive_repair_only")
    assert_contains(
        json.dumps(result_json["actual_full_arm_modules_by_role"]),
        [
            "drawRun29TypographicField",
            "drawRun29EditorialSpread",
            "drawRun29LayeredProductSurface",
            "drawRun29MotionStoryboard",
            "drawRun29ClimaxStage",
        ],
    )
    assert_contains(
        json.dumps(result_json["five_layer_learning"]),
        [
            "run2_9_visual_primitive_repair.json",
            "run2_9_executable_visual_modules.json",
            "run2_9_visual_gate_matrix.json",
            "actual drawRun29 visual module calls",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.9",
            "visual primitive",
            "HTML viewer",
            "drawRun29ClimaxStage",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_10_records_visual_system_rerun_result() -> None:
    result = (PACK / "results" / "run2_10_visual_system_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_10_visual_system_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_10_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert "run2-10-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert result_json["qa_summary"]["trace_truthfulness_guard"].startswith("passed")
    assert result_json["qa_summary"]["case_pack_validator"] == "passed with --profile run2"
    assert result_json["qa_summary"]["browser_viewer_check"].startswith("passed")
    assert_contains(
        json.dumps(result_json["actual_full_arm_modules_by_role"]),
        [
            "drawRun210FullBleedVisualField",
            "drawRun210ProductTheater",
            "drawRun210KineticSequence",
            "drawRun210EditorialTypeSystem",
            "drawRun210NonRectangularProofPath",
            "drawRun210CinematicClimax",
        ],
    )
    assert_contains(
        json.dumps(result_json["visual_learning"]),
        [
            "structural asymmetry",
            "not merely recolored",
            "public blocked",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.10",
            "visual system",
            "HTML viewer",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_13_records_thick_data_rerun_result() -> None:
    result = (PACK / "results" / "run2_13_thick_data_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_13_thick_data_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_13_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert "run2-13-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert result_json["qa_summary"]["trace_truthfulness_guard"].startswith("passed")
    assert result_json["qa_summary"]["case_pack_validator"] == "passed with --profile run2"
    assert result_json["control_boundary"]["bad_thick_data_memory"].startswith(
        "commercial_case_plus_thick_evidence_only"
    )
    assert_contains(
        json.dumps(result_json["actual_full_arm_modules_by_role"]),
        [
            "drawRun213LaunchArcRoute",
            "drawRun213TypeWhitespaceSystem",
            "drawRun213ProductDemoSequence",
            "drawRun213MetricClimaxObject",
            "drawRun213WorkflowGateRail",
        ],
    )
    assert_contains(
        json.dumps(result_json["thick_data_learning"]),
        [
            "run2_12_thick_multimodal_evidence.json",
            "run2_12_design_memory_seed.json",
            "run2_12_workflow_gate_seed.json",
            "evidence_only_negative_control",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.13",
            "thick data",
            "run2_12_thick_multimodal_evidence.json",
            "HTML viewer",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_14_records_aesthetic_trace_rerun_result() -> None:
    result = (PACK / "results" / "run2_14_aesthetic_trace_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_14_aesthetic_trace_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_14_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert "run2-14-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert result_json["qa_summary"]["trace_truthfulness_guard"].startswith("passed")
    assert result_json["qa_summary"]["case_pack_validator"] == "passed with --profile run2"
    assert result_json["control_boundary"]["bad_visible_workflow_memory"].startswith(
        "run2_12_data_workflow_without_run2_10_aesthetic_shell"
    )
    assert_contains(
        json.dumps(result_json["actual_full_arm_modules_by_role"]),
        [
            "drawRun214PresentationShell",
            "drawRun214CinematicProductTheater",
            "drawRun214HiddenWorkflowRoute",
            "drawRun214MetricRevealStage",
            "drawRun214QuietReleaseHandoff",
        ],
    )
    assert_contains(
        json.dumps(result_json["aesthetic_trace_learning"]),
        [
            "2.10 visual system aesthetic shell",
            "2.13 thick data trace core",
            "manifest_only_trace_public_surface",
            "workflow_hidden_from_slide_surface",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.14",
            "2.10 visual system aesthetic",
            "2.13 thick data trace",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_15_records_layout_selector_data_workflow_result() -> None:
    result = (PACK / "results" / "run2_15_layout_selector_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_15_layout_selector_result.json")
    readme = (PACK / "results" / "README.md").read_text(encoding="utf-8")
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")

    assert result_json["status"] == "selector_data_workflow_ready_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["run_id"] == "2.15"
    assert result_json["creates_new_ppt_outputs"] is False
    assert result_json["next_generation_gate"] == "run2_15_selector_gate_matrix_must_drive_next_four_arm_rerun"
    assert_contains(
        json.dumps(result_json["selector_artifacts"]),
        [
            "run2_15_layout_selector_sources.json",
            "run2_15_layout_module_memory.json",
            "run2_15_layout_selector_gate_matrix.json",
        ],
    )
    assert_contains(
        json.dumps(result_json["learning"]),
        [
            "layout module selector",
            "text resilience",
            "trace hidden from public slide surface",
            "product theater realism",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.15",
            "layout module selector",
            "data/workflow-only",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
    assert "ppt-run2-15-" not in json.dumps(result_json)
    assert_contains(
        readme,
        [
            "Run 2.15 intentionally adds no new `ppt-run2-15-*` output folders",
            "Run 2.16 is the selector-driven generated rerun that consumes the Run 2.15 artifacts",
        ],
    )
    assert_contains(
        comparison,
        [
            "It does not generate a new deck",
            "latest reviewed generated PPT result",
        ],
    )
    assert_contains(
        delivery,
        [
            "Run 2.15 is data/workflow-only and does not create PPTX artifacts",
            "Run 2.16 is the generated rerun that consumes it",
        ],
    )


def test_run2_16_records_selector_driven_rerun_result() -> None:
    result = (PACK / "results" / "run2_16_selector_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_16_selector_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_16_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert "run2-16-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert result_json["qa_summary"]["trace_truthfulness_guard"].startswith("passed")
    assert result_json["qa_summary"]["case_pack_validator"] == "passed with --profile run2"
    assert result_json["control_boundary"]["bad_selector_memory"].startswith(
        "selector_sources_without_module_memory_or_gate_matrix"
    )
    assert_contains(
        json.dumps(result_json["actual_full_arm_modules_by_role"]),
        [
            "drawRun216EditorialCoverField",
            "drawRun216ProductTheaterStage",
            "drawRun216BeforeAfterRoute",
            "drawRun216MetricRevealStage",
            "drawRun216QuietReleaseHandoff",
            "drawRun216DenseEvidenceCompression",
        ],
    )
    assert_contains(
        json.dumps(result_json["selector_learning"]),
        [
            "run2_15_layout_selector_sources.json",
            "run2_15_layout_module_memory.json",
            "run2_15_layout_selector_gate_matrix.json",
            "selector_gate_matrix_executed_before_native_ppt_generation",
            "bad_selector_memory",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.16",
            "selector-driven",
            "run2_15_layout_selector_gate_matrix.json",
            "HTML viewer",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_17_records_motion_delivery_audit() -> None:
    result = (PACK / "results" / "run2_17_motion_delivery_audit.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_17_motion_delivery_audit.json")

    assert result_json["status"] == "motion_delivery_audit_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["source_generated_run_id"] == "2.16"
    assert result_json["delivery_truth"]["html_viewer_mode"] == "static_slide_preview_only"
    assert result_json["delivery_truth"]["keynote_expected_behavior"] == "editable_static_slides_no_native_animation"
    assert result_json["delivery_truth"]["native_ppt_animation_status"] == "absent_in_current_pptx"
    assert result_json["delivery_truth"]["motion_xml_scan_scope"] == "tag_presence_only_not_playback_verification"
    assert result_json["motion_renderer_gap"]["next_run_recommendation"] == "run2_17_motion_renderer_proof"
    assert result_json["motion_renderer_gap"]["keep_static_ppt_as"] == "editable_product_output"
    assert result_json["motion_renderer_gap"]["public_video_path"] == "separate_html_or_video_motion_renderer_until_pptx_animation_is_verified"

    arm_audits = result_json["arm_audits"]
    assert {arm["arm_id"] for arm in arm_audits} == {
        "prompt_only",
        "run1_5_skill",
        "run2_16_full_skill",
        "bad_selector_memory",
    }
    for arm in arm_audits:
        assert arm["pptx_path"].endswith(".pptx")
        assert "ppt-run2-16" in arm["pptx_path"]
        assert arm["slide_count"] == 6
        assert arm["media_entry_count"] == 0
        assert arm["motion"]["has_motion_xml"] is False
        assert arm["motion"]["scan_scope"] == "motion_xml_tag_presence_only_not_playback_verification"
        assert arm["motion"]["slides_with_motion_xml"] == []
        assert arm["keynote_readout"] == "static_editable_slides_only"

    assert_contains(
        result,
        [
            "Run 2.17",
            "HTML viewer is static",
            "Keynote",
            "no transition/timing/animation",
            "Run 2.16",
            "Do not advance to Run 3.0",
        ],
    )


def test_run2_17_records_motion_renderer_proof_contract() -> None:
    result = (PACK / "results" / "run2_17_motion_renderer_proof_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_17_motion_renderer_proof_result.json")

    assert result_json["status"] == "motion_renderer_proof_created_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["source_generated_run_id"] == "2.16"
    assert result_json["source_audit"] == "run2_17_motion_delivery_audit.json"
    assert result_json["delivery_boundary"]["static_ppt_role"] == "editable_product_output"
    assert result_json["delivery_boundary"]["motion_proof_role"] == "separate_html_motion_renderer"
    assert result_json["delivery_boundary"]["native_pptx_animation_claim"] == "not_claimed"
    assert result_json["delivery_boundary"]["keynote_animation_claim"] == "not_claimed"
    assert result_json["local_outputs"]["html"].endswith("run2-17-motion-renderer-proof.html")
    assert result_json["local_outputs"]["manifest"].endswith("run2-17-motion-renderer-proof-manifest.json")

    scenes = result_json["scenes"]
    assert [scene["scene_id"] for scene in scenes] == [
        "cover_attention_reset",
        "before_after_reveal",
        "climax_scale_emphasis",
    ]
    for scene in scenes:
        assert scene["source_motion_contract_ids"]
        assert scene["animation_steps"]
        assert scene["reduced_motion_fallback"]
        assert scene["public_release_gate"] == "blocked_until_human_review_and_video_export_gate"

    assert_contains(
        result,
        [
            "Run 2.17 motion renderer proof",
            "separate HTML motion renderer",
            "not Keynote animation",
            "cover_attention_reset",
            "before_after_reveal",
            "climax_scale_emphasis",
            "public blocked",
        ],
    )


def test_run2_17_motion_renderer_proof_script_is_code_generated_and_bounded() -> None:
    script = (ROOT / "scripts" / "build_ppt_run2_17_motion_renderer_proof.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2-17-motion-renderer-proof.html",
            "run2-17-motion-renderer-proof-manifest.json",
            "cover_attention_reset",
            "before_after_reveal",
            "climax_scale_emphasis",
            "not_pptx_not_keynote_animation",
            "prefers-reduced-motion",
            "Play",
            "Pause",
            "Restart",
        ],
    )
    assert ".pptx" not in script.lower()


def test_run2_18_records_data_memory_workflow_thickness_pack() -> None:
    evidence = load_json(PACK / "run2_18_multimodal_evidence_expansion.json")
    memory = load_json(PACK / "run2_18_design_memory_expansion.json")
    workflow_gates = load_json(PACK / "run2_18_workflow_gate_expansion.json")

    assert evidence["status"] == "run2_18_multimodal_evidence_expansion_ready"
    assert memory["status"] == "run2_18_design_memory_expansion_ready"
    assert workflow_gates["status"] == "run2_18_workflow_gate_expansion_ready"
    for payload in [evidence, memory, workflow_gates]:
        assert payload["stage_policy"] == "repeat_same_five_layers_not_run3"
        assert payload["public_ready"] is False
        assert payload["creates_new_ppt_deck"] is False

    records = evidence["records"]
    assert len(records) >= 8
    assert {record["record_id"] for record in records} >= {
        "thick_2_18_figma_launch_identity_system",
        "thick_2_18_stripe_keynote_business_demo",
        "thick_2_18_apple_liquid_glass_motion_surface",
        "thick_2_18_duarte_slide_design_method",
    }
    for record in records:
        assert RUN2_18_EVIDENCE_FIELDS <= set(record)
        assert record["commercial_usecase_ids"]
        assert record["source_ids"]
        assert record["modality_mix"]
        assert record["memory_targets"]
        assert record["workflow_gate_targets"]
        assert_contains(record["anti_copy_boundary"], ["derived", "no copied"])
        assert "raw_transcript" not in record
        for marker in RUN2_8_FORBIDDEN_MEDIA_MARKERS:
            assert marker not in " ".join(iter_string_values(record)).lower()

    memories = memory["memory_expansions"]
    assert len(memories) >= 6
    evidence_ids = {record["record_id"] for record in records}
    for item in memories:
        assert RUN2_18_MEMORY_FIELDS <= set(item)
        assert set(item["evidence_record_ids"]) <= evidence_ids
        assert item["trace_fields_required"]
        assert_contains(item["code_generation_binding"], ["native PPT", "code"])
        assert_contains(item["negative_control_failure"], ["bad control", "fails"])

    gates = workflow_gates["gates"]
    assert len(gates) >= 6
    memory_ids = {item["memory_id"] for item in memories}
    for gate in gates:
        assert RUN2_18_WORKFLOW_GATE_FIELDS <= set(gate)
        assert gate["required_before_next_rerun"] is True
        assert set(gate["evidence_record_ids"]) <= evidence_ids
        assert set(gate["memory_ids"]) <= memory_ids
        assert gate["trace_fields"]
        assert_contains(gate["bad_control_probe"], ["bad control", "fail"])
        assert_contains(gate["release_boundary"], ["public", "blocked"])


def test_run2_18_records_thickness_result_and_no_new_ppt_output() -> None:
    result = (PACK / "results" / "run2_18_thickness_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_18_thickness_result.json")
    workflow = load_json(PACK / "skill_workflow.json")

    assert result_json["status"] == "run2_18_thickness_pack_ready_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["creates_new_ppt_deck"] is False
    assert result_json["latest_generated_ppt_run"] == "2.16"
    assert result_json["next_required_action"] == "consume_run2_18_thickness_pack_in_next_four_arm_rerun"
    assert result_json["artifact_counts"] == {
        "evidence_records": 8,
        "memory_expansions": 6,
        "workflow_gates": 6,
    }
    assert "ppt-run2-18-" not in result
    assert_contains(
        result,
        [
            "Run 2.18",
            "thickness pack",
            "data",
            "design memory",
            "workflow gate",
            "not generate a new PPT",
            "Do not advance to Run 3.0",
        ],
    )

    assert workflow["status"] == "run2_35_visual_evidence_realism_workflow_directed_public_blocked"
    assert {stage["id"] for stage in workflow["stages"]} >= {
        "expand_run2_18_multimodal_evidence",
        "expand_run2_18_design_memory",
        "apply_run2_18_workflow_gate_expansion",
    }
    assert any(trigger["id"] == "run2_18_thickness_pack_required_before_next_rerun" for trigger in workflow["repair_triggers"])


def test_ppt_run_html_viewer_mentions_run2_18_thickness_pack() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_18_multimodal_evidence_expansion.json",
            "run2_18_design_memory_expansion.json",
            "run2_18_workflow_gate_expansion.json",
            "Run 2.18 thickness pack",
            "data/workflow thickness",
            "not a new PPT",
        ],
    )
    assert "Run 2.18" not in script.split("RUN_SPECS", 1)[1].split("def rel", 1)[0]
    assert "ppt-run2-18-" not in script


def test_ppt_run_html_viewer_mentions_run2_15_selector_artifacts() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_15_layout_selector_sources.json",
            "run2_15_layout_module_memory.json",
            "run2_15_layout_selector_gate_matrix.json",
            "Run 2.15 selector",
            "layout module selector",
        ],
    )
    assert "ppt-run2-15-" not in script


def test_ppt_run_html_viewer_mentions_run2_17_motion_delivery_audit() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_17_motion_delivery_audit.json",
            "Run 2.17 motion delivery audit",
            "HTML viewer is static",
            "Keynote readout",
            "static_slide_preview_only",
        ],
    )
    assert "ppt-run2-17-" not in script


def test_ppt_run_html_viewer_mentions_run2_17_motion_renderer_proof() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_17_motion_renderer_proof_result.json",
            "Run 2.17 motion renderer proof",
            "run2-17-motion-renderer-proof.html",
            "separate_html_motion_renderer",
            "not_claimed",
        ],
    )
    assert "Run 2.17" not in script.split("RUN_SPECS", 1)[1].split("def rel", 1)[0]


def test_ppt_run_html_viewer_builder_tracks_latest_outputs() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "ppt-run-viewer.html",
            "Run 2.8",
            "ppt-run2-8-prompt-only",
            "ppt-run2-8-run1-5-skill",
            "ppt-run2-8-full-vulca",
            "ppt-run2-8-bad-memory-schema",
            "Run 2.9",
            "ppt-run2-9-prompt-only",
            "ppt-run2-9-run1-5-skill",
            "ppt-run2-9-full-vulca",
            "ppt-run2-9-bad-visual-primitive-memory",
            "Run 2.10",
            "ppt-run2-10-prompt-only",
            "ppt-run2-10-run1-5-skill",
            "ppt-run2-10-full-vulca",
            "ppt-run2-10-bad-visual-system-memory",
            "Run 2.13",
            "ppt-run2-13-prompt-only",
            "ppt-run2-13-run1-5-skill",
            "ppt-run2-13-full-vulca",
            "ppt-run2-13-bad-thick-data-memory",
            "Run 2.14",
            "ppt-run2-14-prompt-only",
            "ppt-run2-14-run1-5-skill",
            "ppt-run2-14-full-vulca",
            "ppt-run2-14-bad-visible-workflow-memory",
            "Run 2.16",
            "ppt-run2-16-prompt-only",
            "ppt-run2-16-run1-5-skill",
            "ppt-run2-16-full-vulca",
            "ppt-run2-16-bad-selector-memory",
            "Full skill series",
            "Data / Skill",
            "renderData",
            "safeHref",
            "sources.json",
            "run2_7_multimodal_source_records.json",
            "run2_8_tutorial_decomposition.json",
            "run2_8_executable_design_memory.json",
            "run2_8_workflow_gate_matrix.json",
            "run2_9_visual_primitive_repair.json",
            "run2_9_executable_visual_modules.json",
            "run2_9_visual_gate_matrix.json",
            "run2_10_visual_system_sources.json",
            "run2_10_visual_system_memory.json",
            "run2_10_visual_system_gate_matrix.json",
            "run2_12_thick_multimodal_evidence.json",
            "run2_12_design_memory_seed.json",
            "run2_12_workflow_gate_seed.json",
            "Run 2.9 visual primitive repair",
            "Run 2.10 visual-system sources",
            "Run 2.10 visual-system memory",
            "Run 2.10 visual-system gate matrix",
            "Run 2.12 thick multimodal evidence",
            "Run 2.12 design memory seeds",
            "Run 2.12 workflow gate seeds",
            "vulca_ppt_skill.md",
            "Why 2.8 still looks close to 2.7",
        ],
    )


def test_run2_audit_records_trace_and_native_render_blockers() -> None:
    audit = (PACK / "results" / "audit_review.md").read_text(encoding="utf-8")
    audit_json = load_json(PACK / "results" / "audit_review.json")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")

    assert audit_json["status"] == "reviewed-public-blocked"
    assert audit_json["run2_skill_verdict"] == "best_internal_arm_not_public_ready"
    assert "trace_qa_outcome_refresh_required" in audit_json["blocking_issues"]
    assert "native_render_inspection_blocked" in audit_json["blocking_issues"]
    assert_contains(audit, ["trace QA outcome refresh required", "native render inspection blocked"])
    assert_contains(audit, ["Keynote -609 recovery", "manual export"])
    assert_contains(delivery, ["trace QA outcome fields refreshed", "blocked"])
    assert_contains(comparison, ["Trace QA outcome refresh", "not public-release claims"])


def test_run2_2_records_visual_target_rerun_result() -> None:
    result = (PACK / "results" / "run2_2_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_2_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_2_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert (
        result_json["rerun"]["best_internal_arm_verdict"]
        == "visible_learning_targets_present_but_not_public_video_grade"
    )
    assert result_json["next_required_action"] == "turn_visual_targets_into_real_native_slide_thumbnails_and_rerun"
    assert_contains(
        json.dumps(result_json["visible_learning"]),
        ["schematic", "not_high_fidelity", "traceable", "placeholder"],
    )
    assert_contains(
        result,
        [
            "Run 2.2",
            "multimodal database",
            "visual learning targets",
            "schematic",
            "not public-video-grade",
            "Do not advance to Run 3.0",
            "native-PPT components",
        ],
    )


def test_run2_1_records_rerun_result_and_next_visual_depth_gate() -> None:
    readiness = (PACK / "results" / "run2_1_readiness.md").read_text(encoding="utf-8")
    readiness_json = load_json(PACK / "results" / "run2_1_readiness.json")

    assert readiness_json["status"] == "rerun_completed_public_blocked"
    assert readiness_json["next_required_action"] == "thicken_visual_taste_evidence_and_rerun"
    assert readiness_json["public_ready"] is False
    assert "extraction_units" in readiness_json["completed_depth_layers"]
    assert "skill_workflow" in readiness_json["completed_depth_layers"]
    assert "trace_refresh_utility" in readiness_json["completed_depth_layers"]
    assert readiness_json["rerun"]["status"] == "completed"
    assert readiness_json["rerun"]["best_internal_arm"] == "run2_1_full_skill"
    assert readiness_json["rerun"]["generated_outputs_committed"] is False
    assert readiness_json["rerun"]["best_internal_arm_verdict"] == "stronger_product_learning_not_public_video_grade"
    assert readiness_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert_contains(
        readiness,
        [
            "Run 2.1",
            "rerun four arms",
            "public blocked",
            "not a new stage",
            "does not advance",
            "realistic slide diffs",
            "visual transformation",
        ],
    )


def test_run2_generation_protocol_blocks_leakage_and_rasterized_report_failures() -> None:
    body = (PACK / "generation_protocol.md").read_text(encoding="utf-8")

    assert_contains(
        body,
        [
            "runtime isolation",
            "fresh generation prompt",
            "cache directory",
            "full-slide raster",
            "image-to-native-object ratio",
            "visible text overlap",
            "clipped text",
            "default-styled tables",
        ],
    )


def test_run2_pack_does_not_commit_generated_artifacts() -> None:
    blocked_suffixes = {".jpeg", ".jpg", ".mp4", ".pdf", ".png", ".pptx"}
    blocked = [
        str(path.relative_to(PACK))
        for path in PACK.rglob("*")
        if path.is_file() and path.suffix.lower() in blocked_suffixes
    ]

    assert blocked == []

    tracked = tracked_files()
    pack_prefix = "docs/product/ppt-run2-data-skill-quality/"
    tracked_pack_artifact_suffixes = (
        ".ppt",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg",
        ".mp4",
        ".pdf",
        ".layout.json",
    )
    tracked_generated = [
        path
        for path in tracked
        if path.startswith("outputs/")
        or (path.startswith(pack_prefix) and path.lower().endswith(tracked_pack_artifact_suffixes))
        or "contact-sheet" in path
        or "/preview/" in path
    ]

    assert tracked_generated == []
