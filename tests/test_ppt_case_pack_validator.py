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
                    }
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
    (pack / "results" / "delivery_gate.md").write_text(
        "# Delivery Gate\n\nPublic publishing is blocked before native render and human review.\n",
        encoding="utf-8",
    )


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
                        "role": "cover",
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
    assert "missing required file: source_cards/README.md" in result.errors
    assert "missing required file: video_cards/README.md" in result.errors
    assert "missing required file: aesthetic_memory.json" in result.errors
    assert "missing required file: asset_memory.json" in result.errors
    assert "missing required file: generation_briefs/run2_skill.md" in result.errors


def test_run2_profile_validates_memory_contracts(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is True, result.errors


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
