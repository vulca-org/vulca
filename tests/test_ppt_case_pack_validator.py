from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


REQUIRED_MARKDOWN = {
    "README.md": "# Pack\n",
    "source_summaries.md": "# Source Summaries\n\nOriginal notes.\n",
    "commercial_brief.md": "# Commercial Brief\n\nAudience: builders.\n",
    "design_notes.md": "# Design Notes\n\nOriginal analysis.\n",
    "evaluation_rubric.md": "# Evaluation Rubric\n\n- commercial clarity\n",
    "vulca_ppt_skill.md": "# Vulca PPT Skill\n\nUse the case pack.\n",
    "baseline_prompt.md": "# Baseline Prompt\n\nCreate a product launch deck for Vulca.\n",
    "vulca_generation_brief.md": "# Vulca Generation Brief\n\nUse structured case-pack rules.\n",
    "gemini_review_prompt.md": "# Gemini Review Prompt\n\nScore commercial design quality.\n",
}


def write_pack(root: Path) -> None:
    root.mkdir(parents=True)
    for name, body in REQUIRED_MARKDOWN.items():
        (root / name).write_text(body, encoding="utf-8")
    (root / "sources.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": "supervity_ai_keynote",
                        "title": "Supervity AI Presentation Case",
                        "url": "https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/",
                        "role": "main_commercial_reference",
                        "accessed_on": "2026-05-31",
                        "allowed_use": "reference_analysis_only",
                        "copyright_note": "Use for analysis; do not copy proprietary visuals or full text.",
                    },
                    {
                        "id": "schema_2025_keynote_video",
                        "title": "Schema 2025 Keynote Video",
                        "url": "https://example.com/schema-2025-keynote-video",
                        "role": "video_rhythm_reference",
                        "accessed_on": "2026-05-31",
                        "allowed_use": "reference_analysis_only",
                        "copyright_note": "Use for timestamped observation only; do not copy proprietary visuals.",
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "narrative_rules.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "opening": "Name the workflow problem before naming the feature.",
                "progression": ["pain", "market_shift", "approach", "workflow", "proof", "call_to_action"],
                "technical_depth": "Expose technical control through diagrams, not long prose.",
                "closing": "End with a concrete next workflow.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "slide_patterns.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "patterns": [
                    {
                        "id": "cover",
                        "role": "cover",
                        "content_density": "low",
                        "layout_shape": "hero_claim_with_system_mark",
                        "visual_asset_type": "editable_svg",
                        "editability_requirements": ["title_text_is_editable", "subtitle_text_is_editable"],
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "style_tokens.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "palette": {"ink": "#171717", "paper": "#F7F4EE", "signal": "#E24A2A"},
                "font_stack": ["Aptos", "Arial", "sans-serif"],
                "spacing": {"xs": 8, "sm": 16, "md": 24, "lg": 40},
                "corner_radius": {"small": 4, "medium": 8},
                "stroke_widths": {"hairline": 1, "strong": 2},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "asset_rules.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "preferred_assets": ["editable_svg", "native_shapes"],
                "bitmap_use": "background_or_illustrative_only",
                "forbidden": ["rasterized_text", "copied_reference_visuals", "pseudo_logos"],
                "provenance_required": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "deck_outline.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Vulca Product Launch Deck",
                "slides": [
                    {
                        "id": "slide_01",
                        "pattern_id": "cover",
                        "title": "Vulca",
                        "claim": "Design knowledge becomes editable presentation code.",
                        "proof_object": "system mark",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    results = root / "results"
    results.mkdir()
    (results / "README.md").write_text("# Results\n\nGenerated outputs are recorded here.\n", encoding="utf-8")
    (results / "comparison_report.md").write_text(
        "# Comparison Report\n\nStatus: not-run\n\nBaseline and Vulca deck comparison will be recorded after generation.\n",
        encoding="utf-8",
    )


def test_valid_pack_passes(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack)

    assert result.ok is True
    assert result.errors == []


def test_missing_required_file_fails(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    (pack / "style_tokens.json").unlink()

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "missing required file: style_tokens.json" in result.errors


def test_source_must_be_reference_only(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    sources_path = pack / "sources.json"
    data = json.loads(sources_path.read_text(encoding="utf-8"))
    data["sources"][0]["allowed_use"] = "training_data"
    sources_path.write_text(json.dumps(data), encoding="utf-8")

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "sources[0].allowed_use must be reference_analysis_only" in result.errors


def test_source_title_must_be_string(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    sources_path = pack / "sources.json"
    data = json.loads(sources_path.read_text(encoding="utf-8"))
    data["sources"][0]["title"] = []
    sources_path.write_text(json.dumps(data), encoding="utf-8")

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "sources[0].title must be a non-empty string" in result.errors


def test_sources_json_directory_fails_without_raising(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    sources_path = pack / "sources.json"
    sources_path.unlink()
    sources_path.mkdir()

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "required path is not a file: sources.json" in result.errors


def test_readme_directory_fails_without_raising(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    readme_path = pack / "README.md"
    readme_path.unlink()
    readme_path.mkdir()

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "required path is not a file: README.md" in result.errors


def test_slide_pattern_role_must_be_string(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    patterns_path = pack / "slide_patterns.json"
    data = json.loads(patterns_path.read_text(encoding="utf-8"))
    data["patterns"][0]["role"] = []
    patterns_path.write_text(json.dumps(data), encoding="utf-8")

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "slide_patterns.patterns[0].role must be a non-empty string" in result.errors


def test_deck_outline_claim_must_be_string(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    outline_path = pack / "deck_outline.json"
    data = json.loads(outline_path.read_text(encoding="utf-8"))
    data["slides"][0]["claim"] = []
    outline_path.write_text(json.dumps(data), encoding="utf-8")

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "deck_outline.slides[0].claim must be a non-empty string" in result.errors


def test_deck_outline_references_existing_patterns(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    outline_path = pack / "deck_outline.json"
    data = json.loads(outline_path.read_text(encoding="utf-8"))
    data["slides"][0]["pattern_id"] = "unknown_pattern"
    outline_path.write_text(json.dumps(data), encoding="utf-8")

    result = validate_case_pack(pack)

    assert result.ok is False
    assert "deck_outline.slides[0].pattern_id unknown_pattern is not defined in slide_patterns.json" in result.errors


def test_default_profile_does_not_require_run1_extra_files(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack)

    assert result.ok is True, result.errors


def test_run1_profile_requires_extra_files(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack, profile="run1")

    assert result.ok is False
    assert "missing required file: tutorial_notes.md" in result.errors
    assert "missing required file: design_memory.json" in result.errors
    assert "missing required file: results/asset_provenance.json" in result.errors
    assert "missing required file: results/iteration_log.md" in result.errors
    assert "missing required file: results/render_check.md" in result.errors


def test_run1_profile_validates_design_memory(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    (pack / "tutorial_notes.md").write_text("# Tutorial Notes\n\nOriginal teaching notes.\n", encoding="utf-8")
    (pack / "results" / "asset_provenance.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "assets": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "iteration_log.md").write_text("# Iteration Log\n\nNo repair pass yet.\n", encoding="utf-8")
    (pack / "results" / "render_check.md").write_text("# Render Check\n\nRenderer not checked yet.\n", encoding="utf-8")
    (pack / "design_memory.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "observations": [
                    {
                        "id": "launch_system_language",
                        "source_ids": ["supervity_ai_keynote"],
                        "principle": "Turn technical AI claims into a visible workflow.",
                        "code_generation_rule": "Use native shapes and editable labels for workflow diagrams.",
                        "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks.",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = validate_case_pack(pack, profile="run1")

    assert result.ok is True, result.errors


def write_run1_5_required_files(pack: Path) -> None:
    (pack / "tutorial_notes.md").write_text("# Tutorial Notes\n\nOriginal teaching notes.\n", encoding="utf-8")
    (pack / "experiment_protocol.md").write_text(
        "# Experiment Protocol\n\nThree arms: prompt-only, full Vulca, bad-data.\n",
        encoding="utf-8",
    )
    (pack / "bad_data_generation_brief.md").write_text(
        "# Bad Data Generation Brief\n\nUse intentionally mismatched design rules for the negative control.\n",
        encoding="utf-8",
    )
    (pack / "results" / "asset_provenance.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "assets": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "iteration_log.md").write_text("# Iteration Log\n\nNo repair pass yet.\n", encoding="utf-8")
    (pack / "results" / "render_check.md").write_text("# Render Check\n\nRenderer not checked yet.\n", encoding="utf-8")
    (pack / "results" / "ablation_report.md").write_text(
        "# Ablation Report\n\nPrompt-only, full Vulca, and bad-data arms not run yet.\n",
        encoding="utf-8",
    )
    (pack / "results" / "ablation_report.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "arms": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "comparison_report.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "scores": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "delivery_gate.md").write_text(
        "# Delivery Gate\n\nPublic publishing is blocked before native render and human review.\n",
        encoding="utf-8",
    )


def valid_run1_5_design_memory() -> dict:
    return {
        "schema_version": 2,
        "contract": {
            "required_fields": [
                "evidence_id",
                "source_role",
                "observation",
                "design_rule",
                "slide_primitive",
                "layout_constraint",
                "qa_signal",
            ],
            "allowed_source_roles": ["brief", "source", "tutorial", "review"],
            "allowed_slide_primitives": [
                "cockpit",
                "learning_map",
                "comparison_delta",
                "qa_gate",
                "decision_table",
            ],
        },
        "observations": [
            {
                "evidence_id": "tutorial_hierarchy_to_delta",
                "source_role": "tutorial",
                "source_ids": ["supervity_ai_keynote"],
                "observation": "Dense AI stories become clearer when a single outcome anchors each process step.",
                "design_rule": "Use one dominant proof object per slide and replace full rubric tables with large comparison deltas.",
                "slide_primitive": "comparison_delta",
                "layout_constraint": "Main score delta must occupy the largest visual zone on comparison slides.",
                "qa_signal": "Gemini must comment on whether the comparison is understandable from the contact sheet.",
                "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks.",
            }
        ],
    }


def test_run1_5_profile_requires_product_lab_files(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert "missing required file: tutorial_notes.md" in result.errors
    assert "missing required file: experiment_protocol.md" in result.errors
    assert "missing required file: bad_data_generation_brief.md" in result.errors
    assert "missing required file: results/ablation_report.md" in result.errors
    assert "missing required file: results/ablation_report.json" in result.errors
    assert "missing required file: results/delivery_gate.md" in result.errors


def test_run1_5_profile_validates_design_memory_contract(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    (pack / "design_memory.json").write_text(json.dumps(valid_run1_5_design_memory(), indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is True, result.errors


def test_run1_5_profile_rejects_invalid_design_memory_primitive(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    memory = valid_run1_5_design_memory()
    memory["observations"][0]["slide_primitive"] = "generic_card_grid"
    (pack / "design_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert (
        "design_memory.observations[0].slide_primitive must be one of cockpit, comparison_delta, decision_table, "
        "learning_map, qa_gate"
    ) in result.errors


def test_run1_5_profile_rejects_invalid_contract_field_type_without_raising(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    memory = valid_run1_5_design_memory()
    memory["contract"]["required_fields"] = 7
    (pack / "design_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert "design_memory.contract.required_fields must be a non-empty list" in result.errors


def test_run1_5_profile_rejects_extra_contract_required_field(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    memory = valid_run1_5_design_memory()
    memory["contract"]["required_fields"].append("extra_field")
    (pack / "design_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert "design_memory.contract.required_fields has unexpected value: extra_field" in result.errors


def test_run1_5_profile_rejects_extra_contract_source_role(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    memory = valid_run1_5_design_memory()
    memory["contract"]["allowed_source_roles"].append("blog")
    (pack / "design_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert "design_memory.contract.allowed_source_roles has unexpected value: blog" in result.errors


def test_run1_5_profile_rejects_extra_contract_slide_primitive(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    memory = valid_run1_5_design_memory()
    memory["contract"]["allowed_slide_primitives"].append("generic_card_grid")
    (pack / "design_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert ("design_memory.contract.allowed_slide_primitives has unexpected value: generic_card_grid") in result.errors


def write_run2_required_files(pack: Path) -> None:
    for dirname in ["source_cards", "video_cards", "generation_briefs"]:
        directory = pack / dirname
        directory.mkdir()
        (directory / "README.md").write_text(f"# {dirname}\n\nRun 2.0 case-pack data.\n", encoding="utf-8")
    (pack / "commercial_case.md").write_text("# Commercial Case\n\nCommercial product narrative.\n", encoding="utf-8")
    (pack / "aesthetic_rubric.md").write_text("# Aesthetic Rubric\n\nQuality bar.\n", encoding="utf-8")
    (pack / "vulca_ppt_skill.md").write_text("# Vulca PPT Skill\n\nRun 2.0 workflow.\n", encoding="utf-8")
    (pack / "skill_workflow.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workflow_type": "declarative_skill_director",
                "stages": [
                    {
                        "id": "read_commercial_case",
                        "order": 1,
                        "layer": "real_commercial_case",
                        "inputs": ["commercial_case.md"],
                        "outputs": ["decision context"],
                        "gates": ["case is concrete"],
                    }
                ],
                "repair_triggers": [
                    {
                        "id": "trace_qa_pending",
                        "trigger": "trace QA fields remain pending after validation",
                        "recommendation": "refresh trace QA outcomes before scoring",
                        "human_gate": "required before public release",
                    }
                ],
                "release_decisions": ["internal_only", "public_blocked"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (pack / "generation_briefs" / "prompt_only.md").write_text(
        "# Prompt Only\n\nBaseline generation arm.\n",
        encoding="utf-8",
    )
    (pack / "generation_briefs" / "run1_5_skill.md").write_text(
        "# Run 1.5 Skill\n\nPrior workflow arm.\n",
        encoding="utf-8",
    )
    (pack / "generation_briefs" / "run2_skill.md").write_text(
        "# Run 2 Skill\n\nDeep product-layer workflow arm.\n",
        encoding="utf-8",
    )
    (pack / "generation_briefs" / "bad_aesthetic_memory.md").write_text(
        "# Bad Aesthetic Memory\n\nNegative control arm.\n",
        encoding="utf-8",
    )
    (pack / "multimodal_database.json").write_text(
        json.dumps(valid_run2_multimodal_database(), indent=2),
        encoding="utf-8",
    )
    (pack / "visual_learning_targets.json").write_text(
        json.dumps(valid_run2_visual_learning_targets(), indent=2),
        encoding="utf-8",
    )
    (pack / "visual_target_components.json").write_text(
        json.dumps(valid_run2_visual_target_components(), indent=2),
        encoding="utf-8",
    )
    (pack / "video_demo_beat_map.json").write_text(
        json.dumps(valid_run2_video_demo_beat_map(), indent=2),
        encoding="utf-8",
    )
    (pack / "motion_learning_targets.json").write_text(
        json.dumps(valid_run2_motion_learning_targets(), indent=2),
        encoding="utf-8",
    )
    (pack / "presentation_sequence_components.json").write_text(
        json.dumps(valid_run2_presentation_sequence_components(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "delivery_gate.md").write_text(
        "# Delivery Gate\n\nPublic publishing is blocked before native render and human review.\n",
        encoding="utf-8",
    )


def valid_run2_multimodal_database() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_2_multimodal_contract_public_blocked",
        "storage_policy": {
            "default": "derived_observations_only",
            "raw_media": "forbidden",
            "copyright_boundary": "Store derived observations only; do not store copied source media.",
        },
        "required_modalities": ["text", "image_reference", "video", "audio", "transcript", "interaction"],
        "records": [
            {
                "id": "mm_text_image_interaction",
                "source_id": "supervity_ai_keynote",
                "source_kind": "case_study",
                "modalities": ["text", "image_reference", "interaction"],
                "allowed_storage": "derived_observations_only",
                "ingestion_status": "metadata_and_derived_observations_recorded",
                "anchors": [
                    {
                        "anchor_id": "text_case_hierarchy",
                        "modality": "text",
                        "locator": "case-study summary",
                        "observation": "Commercial case text can become a slide hierarchy rule.",
                        "extracted_design_signal": "Use one dominant claim and one proof object.",
                        "allowed_use": "derived_rules_only",
                    },
                    {
                        "anchor_id": "image_reference_case_surface",
                        "modality": "image_reference",
                        "locator": "page-level visual reference",
                        "observation": "Image references can guide focal scale without copying layout.",
                        "extracted_design_signal": "Generate original editable surfaces with a clear focal object.",
                        "allowed_use": "visual_inspiration",
                    },
                    {
                        "anchor_id": "interaction_case_handoff",
                        "modality": "interaction",
                        "locator": "audience decision journey",
                        "observation": "The close should hand the audience to a decision.",
                        "extracted_design_signal": "End with one release gate and one decision handoff.",
                        "allowed_use": "derived_rules_only",
                    },
                ],
                "derived_outputs": ["aesthetic_memory_candidates", "layout_qa_probes"],
                "do_not_store": ["screenshots", "source layouts", "brand marks"],
                "qa_gates": ["source boundary recorded", "no copied media stored"],
            },
            {
                "id": "mm_video_audio_transcript",
                "source_id": "schema_2025_keynote_video",
                "source_kind": "video_tutorial_or_keynote",
                "modalities": ["video", "audio", "transcript"],
                "allowed_storage": "derived_observations_only",
                "ingestion_status": "timestamped_observations_recorded_no_media_saved",
                "anchors": [
                    {
                        "anchor_id": "video_opening_rhythm",
                        "modality": "video",
                        "locator": "00:00-00:45 visual beat",
                        "observation": "Video opening rhythm can become a low-density cover rule.",
                        "extracted_design_signal": "Start with one wide visual field before proof panels appear.",
                        "allowed_use": "timestamped_observation_only",
                    },
                    {
                        "anchor_id": "audio_density_pause",
                        "modality": "audio",
                        "locator": "00:00-00:45 speech cadence",
                        "observation": "Audio pacing can become a density budget.",
                        "extracted_design_signal": "Reduce visible words on orientation beats.",
                        "allowed_use": "timestamped_observation_only",
                    },
                    {
                        "anchor_id": "transcript_headline_compression",
                        "modality": "transcript",
                        "locator": "short paraphrase only",
                        "observation": "Spoken explanation should become a native headline, not slide transcript text.",
                        "extracted_design_signal": "Route long explanation to speaker notes.",
                        "allowed_use": "derived_rules_only",
                    },
                ],
                "derived_outputs": ["rhythm_roles", "speaker_note_routes"],
                "do_not_store": ["video frames", "audio files", "full transcripts"],
                "qa_gates": ["timestamps are anchors only", "no raw media stored"],
            },
        ],
        "cross_modal_design_tasks": [
            {
                "id": "before_after_visual_delta",
                "input_modalities": ["text", "image_reference"],
                "task": "Convert observations into a before/after slide target.",
                "required_generator_behavior": "Show a visible transformation from report layout to hierarchy.",
            }
        ],
        "qa_gates": ["all required modalities covered", "no copied media stored"],
    }


def valid_run2_visual_learning_targets() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_2_visual_learning_targets_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "native_editable_definition": [
            "Targets must use native editable PPT text and native shapes.",
            "Targets must not contain external media URLs or copied source assets.",
        ],
        "targets": [
            {
                "id": "target_report_to_visual_delta",
                "source_record_ids": ["mm_text_image_interaction", "mm_video_audio_transcript"],
                "anchor_ids": ["text_case_hierarchy", "video_opening_rhythm"],
                "slide_roles": ["contrast", "proof"],
                "failure_pattern": "A report-like slide has equal visual weight everywhere.",
                "desired_behavior": "The generated slide shows a native before/after hierarchy change.",
                "code_generation_requirements": [
                    "Use native editable PPT text.",
                    "Use native shapes for the mini-preview.",
                ],
                "qa_probe": "The contact sheet shows the before/after difference.",
                "release_boundary": "internal_analysis_public_blocked_until_render_provenance_and_human_approval",
            }
        ],
    }


def valid_run2_visual_target_components() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_3_native_visual_components_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "components": [
            {
                "id": "component_before_after_thumbnail",
                "target_ids": ["target_report_to_visual_delta"],
                "slide_roles": ["contrast", "proof"],
                "native_ppt_primitives": [
                    "native editable text boxes",
                    "native editable rectangle and line groups",
                ],
                "layout_contract": "A before/after thumbnail pair must reserve most of the canvas for one changed object.",
                "density_contract": "Use one claim, two preview panels, and fewer than 45 visible words.",
                "trace_fields": [
                    "visual_learning_target_ids",
                    "visual_component_ids",
                    "density_counts",
                    "native_ppt_checks",
                ],
                "generator_prompt": "Build the before/after from native editable PowerPoint shapes and labels.",
                "qa_probe": "The contact sheet shows which side is before and which side is after.",
                "failure_modes": ["screenshot preview", "equal dashboard grid"],
                "release_boundary": "internal_analysis_public_blocked_until_render_provenance_and_human_approval",
            }
        ],
        "qa_gates": ["components reference known visual targets", "no copied media in component contracts"],
    }


def valid_run2_video_demo_beat_map() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_4_video_demo_beat_map_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "storage_policy": {
            "default": "derived_observations_only",
            "raw_media": "forbidden",
            "copyright_boundary": "Store derived beat observations only; do not store raw media.",
        },
        "beats": [
            {
                "id": "beat_opening_scale_reset",
                "source_id": "schema_2025_keynote_video",
                "source_record_ids": ["mm_video_audio_transcript"],
                "anchor_ids": ["video_opening_rhythm", "audio_density_pause"],
                "video_card_ids": ["video_keynote_rhythm"],
                "locator": "00:00-00:45 opening beat",
                "observed_demo_move": "The opening holds one large field before proof appears.",
                "derived_presentation_rule": "Start with a sparse native opening object before adding proof panels.",
                "motion_role": "attention_reset",
                "reveal_sequence": ["native opening field", "native headline", "native proof marker"],
                "pacing_signal": "Hold before adding proof density.",
                "do_not_store": ["source video", "video frames", "audio", "full transcript"],
                "qa_probe": "The contact sheet shows a sparse opening before proof density.",
                "release_boundary": "internal_analysis_public_blocked_until_render_provenance_and_human_approval",
            }
        ],
        "qa_gates": ["beat ids reference known anchors", "raw media remains forbidden"],
    }


def valid_run2_motion_learning_targets() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_4_motion_learning_targets_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "targets": [
            {
                "id": "motion_target_opening_attention_reset",
                "beat_ids": ["beat_opening_scale_reset"],
                "visual_target_ids": ["target_report_to_visual_delta"],
                "visual_component_ids": ["component_before_after_thumbnail"],
                "slide_roles": ["cover", "proof"],
                "motion_role": "attention_reset",
                "failure_pattern": "The deck opens with report density and no attention reset.",
                "desired_behavior": "Pause on a sparse native field before proof objects reveal.",
                "code_generation_requirements": [
                    "Use native editable PPT objects.",
                    "Record motion metadata and trace ids.",
                ],
                "qa_probe": "Opening beat has a visible reveal order.",
                "release_boundary": "internal_analysis_public_blocked_until_render_provenance_and_human_approval",
            }
        ],
        "qa_gates": ["motion targets reference known beats and components"],
    }


def valid_run2_presentation_sequence_components() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_4_sequence_components_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "components": [
            {
                "id": "sequence_component_opening_reset",
                "motion_target_ids": ["motion_target_opening_attention_reset"],
                "visual_component_ids": ["component_before_after_thumbnail"],
                "slide_roles": ["cover", "proof"],
                "native_ppt_primitives": ["native editable text boxes", "native editable shape groups"],
                "sequence_steps": [
                    {
                        "step_id": "field_first",
                        "order": 1,
                        "reveal_object": "native opening field",
                        "trigger": "on slide start",
                        "duration": "short hold",
                        "purpose": "Create attention space before proof.",
                    },
                    {
                        "step_id": "proof_second",
                        "order": 2,
                        "reveal_object": "native proof marker",
                        "trigger": "after hold",
                        "duration": "quick reveal",
                        "purpose": "Add proof after orientation.",
                    },
                ],
                "trace_fields": ["motion_target_ids", "sequence_component_ids", "visual_component_ids"],
                "qa_probe": "The reveal order is visible in the static sequence notes.",
                "failure_modes": ["all objects visible with no staged order"],
                "release_boundary": "internal_analysis_public_blocked_until_render_provenance_and_human_approval",
            }
        ],
        "qa_gates": ["sequence steps are ordered", "native editable primitives are required"],
    }


def write_run2_source_card(pack: Path, card_id: str = "card_cinematic_cover") -> None:
    (pack / "source_cards" / f"{card_id}.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "card_id": card_id,
                "source_id": "supervity_ai_keynote",
                "source_type": "commercial_case",
                "allowed_use": "derived_rules_only",
                "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks.",
                "observed_move": "A product case opens with a cinematic, low-density claim.",
                "why_it_works": "It gives technical material a memorable commercial first impression.",
                "ppt_translation": "Use editable title text over a generated abstract background.",
                "quality_risk": "Avoid illegible title contrast and copied case-study composition.",
                "extraction_units": [
                    {
                        "unit_id": "cover_claim_before_detail",
                        "source_anchor": "commercial opening pattern",
                        "derived_rule": "Lead with one commercial claim before proof detail appears.",
                        "slide_role": "cover",
                        "execution_guard": "Do not add a dashboard grid or dense status strip.",
                        "qa_probe": "The contact sheet should read as a launch moment before body text is readable.",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def write_run2_video_card(pack: Path, card_id: str = "video_keynote_rhythm") -> None:
    (pack / "video_cards" / f"{card_id}.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "card_id": card_id,
                "source_id": "schema_2025_keynote_video",
                "source_type": "video",
                "allowed_use": "timestamped_observation_only",
                "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks.",
                "timestamp_map": ["00:00 cover", "00:16 proof shift"],
                "keyframe_descriptions": ["Dark cinematic cover with one edited claim."],
                "pacing_notes": "The opening holds before proof density increases.",
                "transition_observations": "Motion is reserved for transitions between roles.",
                "derived_aesthetic_cards": ["aesthetic_cinematic_cover"],
                "extraction_units": [
                    {
                        "unit_id": "video_opening_scale",
                        "source_anchor": "00:00 cover",
                        "derived_rule": "Use a large opening field before introducing proof panels.",
                        "slide_role": "cover",
                        "execution_guard": "Do not explain mechanism layers in the first beat.",
                        "qa_probe": "The cover has one dominant field and no explanatory panel row.",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def valid_run2_aesthetic_memory() -> dict:
    return {
        "schema_version": 1,
        "moves": [
            {
                "id": "aesthetic_cinematic_cover",
                "source_card_ids": ["card_cinematic_cover", "video_keynote_rhythm"],
                "aesthetic_move": "cinematic_cover",
                "trigger": "Use when a deck needs a commercial opening slide.",
                "composition_rule": "Place one dominant claim over a generated background.",
                "typography_rule": "Keep title and subtitle editable with strong contrast.",
                "density_budget": {"max_claims": 1, "max_panels": 1, "max_words": 18},
                "rhythm_role": "cover",
                "ppt_primitive": "editable text over generated background",
                "negative_rules": ["Do not rasterize title text.", "Do not copy the reference layout."],
                "qa_signal": "The cover reads clearly in a contact sheet.",
            }
        ],
    }


def valid_run2_evidence_memory() -> dict:
    return {
        "schema_version": 1,
        "claims": [
            {
                "id": "claim_commercial_opening",
                "source_card_ids": ["card_cinematic_cover"],
                "claim": "A cinematic cover can make a technical product feel commercially legible.",
                "business_relevance": "Improves executive scanability before technical proof.",
                "allowed_use": "derived_rules_only",
                "qa_checks": ["Claim is traceable to source card.", "No copied source wording."],
            }
        ],
    }


def valid_run2_asset_memory() -> dict:
    return {
        "schema_version": 1,
        "assets": [
            {
                "id": "asset_cinematic_cover_bg",
                "asset_type": "generated_background",
                "source_card_ids": ["card_cinematic_cover"],
                "allowed_slide_roles": ["cover", "close"],
                "provenance_state": "generated_from_derived_rules",
                "text_editability": "all text remains native PPT text",
                "license_state": "generated asset, no copied source material",
                "render_risks": ["Background may reduce text contrast."],
                "accessibility_risks": ["Low contrast if overlay is too transparent."],
            }
        ],
    }


def write_run2_memory_files(pack: Path) -> None:
    (pack / "aesthetic_memory.json").write_text(
        json.dumps(valid_run2_aesthetic_memory(), indent=2),
        encoding="utf-8",
    )
    (pack / "evidence_memory.json").write_text(
        json.dumps(valid_run2_evidence_memory(), indent=2),
        encoding="utf-8",
    )
    (pack / "asset_memory.json").write_text(
        json.dumps(valid_run2_asset_memory(), indent=2),
        encoding="utf-8",
    )
    (pack / "narrative_spine.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "deck_length": 6,
                "slides": [
                    {
                        "id": "slide_01",
                        "rhythm_role": "cover",
                        "aesthetic_move_ids": ["aesthetic_cinematic_cover"],
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (pack / "slide_archetypes.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "archetypes": [
                    {
                        "id": "cinematic_cover",
                        "rhythm_role": "cover",
                        "aesthetic_move_ids": ["aesthetic_cinematic_cover"],
                        "density_budget": {"max_claims": 1, "max_panels": 1, "max_words": 18},
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_run2_profile_requires_data_skill_quality_files(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "missing required file: commercial_case.md" in result.errors
    assert "missing required file: multimodal_database.json" in result.errors
    assert "missing required file: visual_learning_targets.json" in result.errors
    assert "missing required file: visual_target_components.json" in result.errors
    assert "missing required file: video_demo_beat_map.json" in result.errors
    assert "missing required file: motion_learning_targets.json" in result.errors
    assert "missing required file: presentation_sequence_components.json" in result.errors
    assert "missing required file: source_cards/README.md" in result.errors
    assert "missing required file: video_cards/README.md" in result.errors
    assert "missing required file: aesthetic_memory.json" in result.errors
    assert "missing required file: asset_memory.json" in result.errors
    assert "missing required file: skill_workflow.json" in result.errors
    assert "missing required file: generation_briefs/run2_skill.md" in result.errors


def test_run2_profile_rejects_skill_workflow_without_repair_triggers(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    (pack / "skill_workflow.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workflow_type": "declarative_skill_director",
                "stages": [
                    {
                        "id": "read_commercial_case",
                        "order": 1,
                        "layer": "real_commercial_case",
                        "inputs": ["commercial_case.md"],
                        "outputs": ["narrative intent"],
                        "gates": ["commercial case exists"],
                    }
                ],
                "release_decisions": ["internal_only", "public_blocked"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "skill_workflow.json missing key: repair_triggers" in result.errors


def test_run2_profile_validates_memory_contracts(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is True, result.errors


def test_run2_profile_rejects_multimodal_missing_audio_coverage(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    database_path = pack / "multimodal_database.json"
    database = json.loads(database_path.read_text(encoding="utf-8"))
    database["records"][1]["modalities"] = ["video", "transcript"]
    database["records"][1]["anchors"] = [
        anchor for anchor in database["records"][1]["anchors"] if anchor["modality"] != "audio"
    ]
    database_path.write_text(json.dumps(database, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "multimodal_database.records missing modality coverage: audio" in result.errors


def test_run2_profile_rejects_multimodal_unknown_source(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    database_path = pack / "multimodal_database.json"
    database = json.loads(database_path.read_text(encoding="utf-8"))
    database["records"][0]["source_id"] = "missing_source"
    database_path.write_text(json.dumps(database, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "multimodal_database.records[0].source_id missing_source is not defined in sources.json" in result.errors


def test_run2_profile_rejects_multimodal_anchor_outside_parent_modalities(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    database_path = pack / "multimodal_database.json"
    database = json.loads(database_path.read_text(encoding="utf-8"))
    database["records"][0]["modalities"] = ["text", "interaction"]
    database_path.write_text(json.dumps(database, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "multimodal_database.records[0].anchors[1].modality image_reference is not listed in the parent record "
        "modalities"
    ) in result.errors


def test_run2_profile_rejects_visual_target_unknown_anchor(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "visual_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["anchor_ids"] = ["missing_anchor"]
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "visual_learning_targets.targets[0].anchor_ids references unknown multimodal anchor: missing_anchor"
        in result.errors
    )


def test_run2_profile_rejects_visual_target_without_native_editable_requirement(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "visual_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["code_generation_requirements"] = ["Use a screenshot preview."]
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "visual_learning_targets.targets[0].code_generation_requirements must require native editable output"
        in result.errors
    )


def test_run2_profile_rejects_visual_target_with_external_media_reference(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "visual_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["desired_behavior"] = "Use https://example.com/copied-slide.png as the after state."
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "visual_learning_targets.targets[0].desired_behavior must not include external media URLs or file references"
        in result.errors
    )


def test_run2_profile_rejects_visual_target_without_public_blocked_boundary(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "visual_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["release_boundary"] = "public_ready_after_generation"
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "visual_learning_targets.targets[0].release_boundary must keep public_blocked status" in result.errors


def test_run2_profile_rejects_visual_component_unknown_target(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "visual_target_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["target_ids"] = ["missing_target"]
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "visual_target_components.components[0].target_ids[0] references unknown visual target: missing_target"
        in result.errors
    )


def test_run2_profile_rejects_visual_component_without_native_editable_primitives(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "visual_target_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["native_ppt_primitives"] = ["screenshot crop"]
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "visual_target_components.components[0].native_ppt_primitives must require native editable PPT output"
        in result.errors
    )


def test_run2_profile_rejects_visual_component_external_media_reference(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "visual_target_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["generator_prompt"] = "Paste https://example.com/reference.png as the preview."
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "visual_target_components.components[0].generator_prompt must not include external media URLs or file references"
        in result.errors
    )


def test_run2_profile_rejects_visual_component_without_public_blocked_boundary(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "visual_target_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["release_boundary"] = "public_ready_after_generation"
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "visual_target_components.components[0].release_boundary must keep public_blocked status" in result.errors


def test_run2_profile_rejects_video_beat_unknown_anchor(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    beat_map_path = pack / "video_demo_beat_map.json"
    beat_map = json.loads(beat_map_path.read_text(encoding="utf-8"))
    beat_map["beats"][0]["anchor_ids"] = ["missing_anchor"]
    beat_map_path.write_text(json.dumps(beat_map, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "video_demo_beat_map.beats[0].anchor_ids references unknown multimodal anchor: missing_anchor" in result.errors
    )


def test_run2_profile_rejects_video_beat_unknown_video_card(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    beat_map_path = pack / "video_demo_beat_map.json"
    beat_map = json.loads(beat_map_path.read_text(encoding="utf-8"))
    beat_map["beats"][0]["video_card_ids"] = ["missing_card"]
    beat_map_path.write_text(json.dumps(beat_map, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "video_demo_beat_map.beats[0].video_card_ids references unknown source or video card: missing_card"
        in result.errors
    )


def test_run2_profile_rejects_video_beat_external_media_reference(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    beat_map_path = pack / "video_demo_beat_map.json"
    beat_map = json.loads(beat_map_path.read_text(encoding="utf-8"))
    beat_map["beats"][0]["locator"] = "https://example.com/source-video.mp4"
    beat_map_path.write_text(json.dumps(beat_map, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "video_demo_beat_map.beats[0].locator must not include external media URLs or file references" in result.errors
    )


def test_run2_profile_rejects_video_beat_without_public_blocked_boundary(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    beat_map_path = pack / "video_demo_beat_map.json"
    beat_map = json.loads(beat_map_path.read_text(encoding="utf-8"))
    beat_map["beats"][0]["release_boundary"] = "public_ready_after_generation"
    beat_map_path.write_text(json.dumps(beat_map, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "video_demo_beat_map.beats[0].release_boundary must keep public_blocked status" in result.errors


def test_run2_profile_rejects_motion_target_unknown_beat(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "motion_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["beat_ids"] = ["missing_beat"]
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "motion_learning_targets.targets[0].beat_ids references unknown video beat: missing_beat" in result.errors


def test_run2_profile_rejects_motion_target_without_trace_metadata_requirement(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "motion_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["code_generation_requirements"] = ["Use native editable PPT objects."]
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "motion_learning_targets.targets[0].code_generation_requirements must mention metadata" in result.errors
    assert "motion_learning_targets.targets[0].code_generation_requirements must mention trace" in result.errors


def test_run2_profile_rejects_motion_target_external_media_reference(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    targets_path = pack / "motion_learning_targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    targets["targets"][0]["desired_behavior"] = "Use https://example.com/demo-frame.png as reveal reference."
    targets_path.write_text(json.dumps(targets, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "motion_learning_targets.targets[0].desired_behavior must not include external media URLs or file references"
        in result.errors
    )


def test_run2_profile_rejects_sequence_component_unknown_motion_target(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "presentation_sequence_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["motion_target_ids"] = ["missing_motion_target"]
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "presentation_sequence_components.components[0].motion_target_ids references unknown motion target: "
        "missing_motion_target"
    ) in result.errors


def test_run2_profile_rejects_sequence_component_nonsequential_steps(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "presentation_sequence_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["sequence_steps"][1]["order"] = 3
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "presentation_sequence_components.components[0].sequence_steps order must be sequential starting at 1"
        in result.errors
    )


def test_run2_profile_rejects_sequence_component_missing_trace_fields(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "presentation_sequence_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["trace_fields"] = ["visual_component_ids"]
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "presentation_sequence_components.components[0].trace_fields missing value: motion_target_ids" in result.errors
    )
    assert (
        "presentation_sequence_components.components[0].trace_fields missing value: sequence_component_ids"
        in result.errors
    )


def test_run2_profile_rejects_sequence_component_external_media_reference(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    components_path = pack / "presentation_sequence_components.json"
    components = json.loads(components_path.read_text(encoding="utf-8"))
    components["components"][0]["sequence_steps"][0]["reveal_object"] = "local copied frame demo.png"
    components_path.write_text(json.dumps(components, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "presentation_sequence_components.components[0].sequence_steps[0].reveal_object must not include external "
        "media URLs or file references"
    ) in result.errors


def test_run2_profile_rejects_untraced_aesthetic_move(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    memory = valid_run2_aesthetic_memory()
    memory["moves"][0]["source_card_ids"] = ["missing_card"]
    (pack / "aesthetic_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "aesthetic_memory.moves[0].source_card_ids[0] missing_card is not defined by source_cards or video_cards"
    ) in result.errors


def test_run2_profile_rejects_asset_without_provenance_state(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    memory = valid_run2_asset_memory()
    del memory["assets"][0]["provenance_state"]
    (pack / "asset_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "asset_memory.assets[0] missing key: provenance_state" in result.errors


def test_run2_profile_rejects_invalid_narrative_spine_json(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    (pack / "narrative_spine.json").write_text("{", encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "narrative_spine.json is not valid JSON: Expecting property name enclosed in double quotes" in result.errors


def test_run2_profile_rejects_wrong_shape_slide_archetypes(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    (pack / "slide_archetypes.json").write_text(
        json.dumps({"schema_version": 1, "archetypes": []}, indent=2),
        encoding="utf-8",
    )

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "slide_archetypes.archetypes must be a non-empty list" in result.errors


def test_run2_profile_rejects_card_source_id_absent_from_sources(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    source_card_path = pack / "source_cards" / "card_cinematic_cover.json"
    source_card = json.loads(source_card_path.read_text(encoding="utf-8"))
    source_card["source_id"] = "missing_source"
    source_card_path.write_text(json.dumps(source_card, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "source_cards/card_cinematic_cover.json.source_id missing_source is not defined in sources.json"
        in result.errors
    )


def test_run2_profile_rejects_source_card_without_extraction_units(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    source_card_path = pack / "source_cards" / "card_cinematic_cover.json"
    source_card = json.loads(source_card_path.read_text(encoding="utf-8"))
    source_card.pop("extraction_units", None)
    source_card_path.write_text(json.dumps(source_card, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "source_cards/card_cinematic_cover.json missing key: extraction_units" in result.errors


def test_run2_profile_rejects_malformed_extraction_unit(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    video_card_path = pack / "video_cards" / "video_keynote_rhythm.json"
    video_card = json.loads(video_card_path.read_text(encoding="utf-8"))
    video_card["extraction_units"] = [
        {
            "unit_id": "video_opening_scale",
            "source_anchor": "00:00-00:45 opening",
            "derived_rule": "Use a large opening field.",
            "slide_role": "cover",
            "execution_guard": "No explanatory panels on the cover.",
        }
    ]
    video_card_path.write_text(json.dumps(video_card, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "video_cards/video_keynote_rhythm.json.extraction_units[0] missing key: qa_probe" in result.errors


def test_run2_profile_rejects_narrative_spine_unknown_aesthetic_move(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    spine_path = pack / "narrative_spine.json"
    spine = json.loads(spine_path.read_text(encoding="utf-8"))
    spine["slides"][0]["aesthetic_move_ids"] = ["missing_move"]
    spine_path.write_text(json.dumps(spine, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "narrative_spine.slides[0].aesthetic_move_ids[0] missing_move is not defined in aesthetic_memory.json"
        in result.errors
    )


def test_run2_profile_rejects_slide_archetype_unknown_aesthetic_move(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    archetypes_path = pack / "slide_archetypes.json"
    archetypes = json.loads(archetypes_path.read_text(encoding="utf-8"))
    archetypes["archetypes"][0]["aesthetic_move_ids"] = ["missing_move"]
    archetypes_path.write_text(json.dumps(archetypes, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "slide_archetypes.archetypes[0].aesthetic_move_ids[0] missing_move is not defined in aesthetic_memory.json"
        in result.errors
    )
