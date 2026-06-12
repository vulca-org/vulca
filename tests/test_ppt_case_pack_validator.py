from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
RUN2_PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RUN2_8_TRACE_FIELDS = {
    "run2_8_decomposition_unit_ids",
    "run2_8_memory_binding_ids",
    "run2_8_gate_matrix_ids",
    "run2_8_code_binding_ids",
    "run2_8_layout_budget",
    "run2_8_visual_delta_from_run2_7",
}
RUN2_8_RELEASE_BOUNDARY = "public_blocked_until_native_render_trace_and_human_review"
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


def copy_run2_pack(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    shutil.copytree(RUN2_PACK, pack)
    return pack


def write_minimal_run2_8_fixture(pack: Path) -> None:
    decomposition_ids = [
        "decomp_2_8_duarte_remove_nonessential_data",
        "decomp_2_8_type_hierarchy_readability_stack",
        "decomp_2_8_makeover_split_text_into_visual_steps",
        "decomp_2_8_design_first_code_second_pipeline",
        "decomp_2_8_climax_object_scale_and_pause",
        "decomp_2_8_source_brand_sanitized_case_evidence",
    ]
    binding_specs = [
        ("binding_type_scale_readability", "drawRun28TypeScale", "fontSize"),
        ("binding_spacing_zone_grid", "drawRun28SpacingZones", "spacing"),
        ("binding_climax_hero_object", "drawRun28ClimaxHero", "heroObject"),
        ("binding_before_after_delta", "drawRun28BeforeAfterDelta", "beforeAfter"),
        ("binding_public_gate_legibility", "drawRun28WorkflowGate", "workflowGate"),
    ]
    source_record_ids = [
        "mm_2_7_video_climax_single_object",
        "mm_2_7_typography_hierarchy_tutorial",
        "mm_2_7_spacing_editorial_grid_tutorial",
        "mm_2_7_product_surface_interaction_reference",
    ]
    source_ids = [
        "supervity_ai_keynote",
        "schema_2025_keynote_video",
    ]
    decomposition = {
        "schema_version": 1,
        "status": "run2_8_tutorial_decomposition_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "storage_policy": {"raw_media": "forbidden"},
        "units": [
            {
                "id": unit_id,
                "source_record_ids": [source_record_ids[index % len(source_record_ids)]],
                "source_ids": [source_ids[index % len(source_ids)]],
                "modality_mix": ["video", "transcript"],
                "tutorial_anchor": f"derived tutorial anchor {index + 1}",
                "observed_design_move": "Remove nonessential detail and make one visual decision visible.",
                "derived_rule": "Bind the observed move to a native PPT layout decision before drawing.",
                "code_generation_binding": "native PPT binding required before slide code generation",
                "native_ppt_obligation": "Use editable text and native shapes only.",
                "layout_budget": {"max_text_boxes": 9, "max_visible_words": 52},
                "failure_probe": "Fails if the result reads as a report page.",
                "anti_copy_boundary": "Do not copy source visuals, source brand, frames, audio, or transcripts.",
                "qa_probe": "contact sheet review must show the derived move",
                "release_boundary": RUN2_8_RELEASE_BOUNDARY,
            }
            for index, unit_id in enumerate(decomposition_ids)
        ],
    }
    (pack / "run2_8_tutorial_decomposition.json").write_text(
        json.dumps(decomposition, indent=2),
        encoding="utf-8",
    )

    memory = {
        "schema_version": 1,
        "status": "run2_8_executable_design_memory_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "memory_type": "executable_schema_bindings",
        "bindings": [
            {
                "id": binding_id,
                "decomposition_unit_ids": [decomposition_ids[index % len(decomposition_ids)]],
                "applies_to_slide_roles": ["cover", "setup", "contrast", "proof", "climax", "close"],
                "design_token": token,
                "code_binding": {
                    "function_name": function_name,
                    "params": {token: True},
                    "layout_budget": {"max_text_boxes": 9, "max_visible_words": 52},
                },
                "native_ppt_constraints": ["native editable shapes", "trace recorded"],
                "typography_constraints": ["fontSize hierarchy must be readable"],
                "spacing_constraints": ["spacing zones must be explicit"],
                "composition_constraints": ["heroObject or beforeAfter must be visible"],
                "negative_control_failure": "bad memory schema weakens hierarchy",
                "qa_probe": "contact sheet review",
                "release_boundary": RUN2_8_RELEASE_BOUNDARY,
            }
            for index, (binding_id, function_name, token) in enumerate(binding_specs)
        ],
    }
    (pack / "run2_8_executable_design_memory.json").write_text(
        json.dumps(memory, indent=2),
        encoding="utf-8",
    )

    matrix = {
        "schema_version": 1,
        "status": "run2_8_workflow_gate_matrix_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "selection_chain": [
            "commercial_usecase",
            "run2_8_decomposition_units",
            "run2_8_executable_memory_bindings",
            "run2_8_gate_matrix",
            "native_ppt_code_generation",
            "layout_quality_gate",
            "delivery_gate",
            "visual_qa_gate",
        ],
        "gates": [
            {
                "id": f"gate_2_8_{role}",
                "slide_role": role,
                "decomposition_unit_ids": [decomposition_ids[index % len(decomposition_ids)]],
                "memory_binding_ids": [binding_specs[index % len(binding_specs)][0]],
                "required_code_bindings": [binding_specs[index % len(binding_specs)][1]],
                "layout_budget": {"max_text_boxes": 9, "max_visible_words": 52},
                "pass_fail_checks": ["layout QA passes", "native shape trace exists"],
                "trace_fields": sorted(RUN2_8_TRACE_FIELDS),
                "public_release_gate": RUN2_8_RELEASE_BOUNDARY,
            }
            for index, role in enumerate(["cover", "setup", "contrast", "proof", "climax", "close"])
        ],
    }
    (pack / "run2_8_workflow_gate_matrix.json").write_text(
        json.dumps(matrix, indent=2),
        encoding="utf-8",
    )

    trace_path = pack / "results" / "trace_manifest_contract.json"
    if trace_path.exists():
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
    else:
        trace = {"schema_version": 1, "per_slide_required_fields": []}
    for field in sorted(RUN2_8_TRACE_FIELDS):
        if field not in trace["per_slide_required_fields"]:
            trace["per_slide_required_fields"].append(field)
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    workflow_path = pack / "skill_workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    addition_ids = {
        "decompose_run2_8_tutorial_video_units",
        "select_run2_8_executable_design_memory",
        "apply_run2_8_workflow_gate_matrix",
    }
    workflow["stages"] = [stage for stage in workflow["stages"] if stage.get("id") not in addition_ids]
    stage_ids = [stage["id"] for stage in workflow["stages"]]
    insert_at = stage_ids.index("generate_code_first_ppt") if "generate_code_first_ppt" in stage_ids else len(stage_ids)
    additions = [
        {
            "id": "decompose_run2_8_tutorial_video_units",
            "layer": "multimodal_tutorial_case_data",
            "inputs": [
                "run2_8_tutorial_decomposition.json",
                "run2_7_multimodal_source_records.json",
                "sources.json",
            ],
            "outputs": ["Run 2.8 decomposition units"],
            "gates": ["raw media remains forbidden"],
        },
        {
            "id": "select_run2_8_executable_design_memory",
            "layer": "evidence_aesthetic_asset_memory",
            "inputs": ["run2_8_tutorial_decomposition.json", "run2_8_executable_design_memory.json"],
            "outputs": ["Run 2.8 executable design memory bindings"],
            "gates": ["code bindings reference valid decomposition units"],
        },
        {
            "id": "apply_run2_8_workflow_gate_matrix",
            "layer": "skill_workflow",
            "inputs": [
                "run2_8_tutorial_decomposition.json",
                "run2_8_executable_design_memory.json",
                "run2_8_workflow_gate_matrix.json",
                "results/trace_manifest_contract.json",
            ],
            "outputs": ["Run 2.8 workflow gate decisions"],
            "gates": ["gate matrix references valid memory bindings"],
        },
    ]
    workflow["stages"] = workflow["stages"][:insert_at] + additions + workflow["stages"][insert_at:]
    for order, stage in enumerate(workflow["stages"], start=1):
        stage["order"] = order
    workflow_path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")


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
                    },
                    {
                        "id": "generate_code_first_ppt",
                        "order": 2,
                        "layer": "code_generated_native_ppt",
                        "inputs": ["skill_workflow.json"],
                        "outputs": ["native PPT generation plan"],
                        "gates": ["Run 2.8 stages complete before generation"],
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
    (pack / "visual_repair_policy.json").write_text(
        json.dumps(valid_run2_visual_repair_policy(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_7_commercial_usecase.json").write_text(
        json.dumps(valid_run2_7_commercial_usecase(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_7_multimodal_source_records.json").write_text(
        json.dumps(valid_run2_7_multimodal_source_records(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_7_design_memory.json").write_text(
        json.dumps(valid_run2_7_design_memory(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_7_workflow_policy.json").write_text(
        json.dumps(valid_run2_7_workflow_policy(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "delivery_gate.md").write_text(
        "# Delivery Gate\n\nPublic publishing is blocked before native render and human review.\n",
        encoding="utf-8",
    )
    write_minimal_run2_8_fixture(pack)


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


def valid_run2_visual_repair_policy() -> dict:
    repair_fields = {
        "target_slide_roles": ["cover", "setup"],
        "source_policy_ids": ["workflow_decision_policy.json"],
        "typography_delta": "Run 2.5 type scale is the negative baseline.",
        "spacing_delta": "Run 2.5 spacing is the negative baseline.",
        "composition_delta": "Use native editable PPT shapes.",
        "theme_delta": "Avoid forest-green and source-brand mimicry.",
        "must_differ_from": ["ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"],
        "native_ppt_requirements": ["native editable text", "native editable shapes"],
        "qa_probe": "Review the contact sheet for visible repair.",
        "release_boundary": "public_blocked_until_native_render_human_approval_and_visual_delta_review",
    }
    repair_ids = [
        "repair_editorial_typography_system",
        "repair_spacing_token_visibility",
        "repair_climax_editorial_spread",
        "repair_theme_differentiation_from_run2_5",
        "repair_mini_preview_fidelity",
    ]
    return {
        "schema_version": 1,
        "status": "run2_6r_visual_repair_policy_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "default_visual_direction": "light_first_editorial_graphite_with_vivid_proof_color",
        "repairs": [{"id": repair_id, **repair_fields} for repair_id in repair_ids],
    }


def valid_run2_7_commercial_usecase() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_7_commercial_usecase_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "id": "usecase_ai_design_to_production_platform_launch",
        "primary_usecase": "AI design-to-production platform launch deck",
        "audience": ["AI product builders", "design engineering leaders", "technical founders"],
        "business_job": ["Show product-system learning", "Reject not one-shot prompting"],
        "business_decision": "Decide whether the platform can replace ad hoc deck drafting.",
        "deck_mission": "Make the data, memory, workflow, and editable PPT path legible.",
        "six_slide_arc": [
            {
                "slide_id": "slide_01",
                "rhythm_role": "cover",
                "job": "Name the launch.",
                "must_show": ["Launch promise"],
                "must_not_show": ["Source brand"],
            },
            {
                "slide_id": "slide_02",
                "rhythm_role": "setup",
                "job": "Frame the current workflow gap.",
                "must_show": ["Workflow gap"],
                "must_not_show": ["One-off prompt"],
            },
            {
                "slide_id": "slide_03",
                "rhythm_role": "contrast",
                "job": "Show prompt-only versus system learning.",
                "must_show": ["System learning contrast"],
                "must_not_show": ["Equal card wall"],
            },
            {
                "slide_id": "slide_04",
                "rhythm_role": "proof",
                "job": "Trace source data into memory.",
                "must_show": ["Source-to-memory trace"],
                "must_not_show": ["Opaque output"],
            },
            {
                "slide_id": "slide_05",
                "rhythm_role": "climax",
                "job": "Reveal one native proof object.",
                "must_show": ["Native proof object"],
                "must_not_show": ["Full-slide raster"],
            },
            {
                "slide_id": "slide_06",
                "rhythm_role": "close",
                "job": "Gate the release decision.",
                "must_show": ["Release gate"],
                "must_not_show": ["Public release claim"],
            },
        ],
        "must_show": ["data lineage", "selected design memory", "editable PPT trace"],
        "must_not_show": ["copy source layouts", "source brand mimicry", "full-slide raster"],
        "proof_questions": ["Which data?", "Which memory?", "Which workflow?", "Which PPT trace?"],
        "release_boundary": "public_blocked_until_native_render_and_human_review",
    }


def valid_run2_7_multimodal_source_records() -> dict:
    base = {
        "source_id": "supervity_ai_keynote",
        "source_type": "commercial_case",
        "allowed_use": "derived_rules_only",
        "native_ppt_implication": "Generate native editable PPT shapes and text only.",
        "anti_copy_boundary": "do not copy source media, brand, screenshots, or layouts.",
        "qa_probe": "Contact sheet confirms the derived rule is visible.",
        "release_boundary": "public_blocked_until_native_render_and_human_review",
    }
    records = [
        ("mm_2_7_design_system_launch_case", ["text", "image_reference"], ["cover", "setup"]),
        ("mm_2_7_video_climax_single_object", ["video", "audio"], ["climax"]),
        ("mm_2_7_typography_hierarchy_tutorial", ["text", "transcript"], ["setup", "proof"]),
        ("mm_2_7_spacing_editorial_grid_tutorial", ["image_reference", "text"], ["contrast", "proof"]),
        ("mm_2_7_motion_demo_pacing_reference", ["video", "audio", "transcript"], ["proof", "climax"]),
        ("mm_2_7_product_surface_interaction_reference", ["interaction", "text"], ["close"]),
    ]
    return {
        "schema_version": 1,
        "status": "run2_7_multimodal_source_records_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "storage_policy": {"raw_media": "forbidden"},
        "qa_gates": ["source boundary reviewed", "contact sheet reviewed"],
        "records": [
            {
                **base,
                "id": record_id,
                "anchor": f"{record_id} derived observation anchor",
                "modalities": modalities,
                "visual_observation": "A single hierarchy decision controls the slide role.",
                "transcript_or_teaching_claim": "Teaching claim is stored as a paraphrased design rule.",
                "extracted_design_rule": "Use one dominant native editable object before adding supporting detail.",
                "slide_roles": slide_roles,
            }
            for record_id, modalities, slide_roles in records
        ],
    }


def valid_run2_7_design_memory() -> dict:
    common = {
        "source_record_ids": ["mm_2_7_design_system_launch_case"],
        "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
        "applicable_slide_roles": ["cover", "proof"],
        "typography_rules": ["Use editable headline hierarchy."],
        "spacing_rules": ["Reserve visible margin and whitespace."],
        "composition_rules": ["Use native proof objects with clear focal weight."],
        "rhythm_rules": ["Preserve the six-slide launch rhythm."],
        "native_ppt_generation_requirements": ["native editable output", "trace selected memory ids"],
        "forbidden_patterns": ["report density", "dashboard grid", "equal card rows"],
        "qa_probes": ["Contact sheet confirms selected memory is visible."],
        "release_boundary": "public_blocked_until_native_render_and_human_review",
    }
    return {
        "schema_version": 1,
        "status": "run2_7_design_memory_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "memory_type": "deterministic_serializable_rules",
        "qa_gates": ["contact sheet reviewed", "native render trace reviewed"],
        "memories": [
            {"id": "memory_typography_editorial_launch", **common},
            {
                "id": "memory_spacing_climax_proof_grid",
                **common,
                "source_record_ids": ["mm_2_7_spacing_editorial_grid_tutorial"],
            },
            {
                "id": "memory_composition_single_object_climax",
                **common,
                "source_record_ids": ["mm_2_7_video_climax_single_object"],
                "applicable_slide_roles": ["climax"],
                "composition_rules": ["Allocate 40-55% of the canvas to one native proof object."],
                "forbidden_patterns": ["full-slide raster", "source brand mimicry"],
            },
            {
                "id": "memory_rhythm_six_slide_launch",
                **common,
                "source_record_ids": ["mm_2_7_motion_demo_pacing_reference"],
            },
            {
                "id": "memory_source_brand_sanitization_v2",
                **common,
                "source_record_ids": ["mm_2_7_product_surface_interaction_reference"],
                "forbidden_patterns": ["source brand mimicry", "copy source layout"],
            },
        ],
    }


def valid_run2_7_workflow_policy() -> dict:
    trace_fields = [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate",
    ]
    return {
        "schema_version": 1,
        "status": "run2_7_workflow_policy_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
        "selection_chain": [
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
        ],
        "qa_gates": ["workflow trace reviewed", "native PPT output reviewed"],
        "slide_role_memory_map": [
            {
                "rhythm_role": "cover",
                "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
                "source_record_ids": ["mm_2_7_design_system_launch_case"],
                "design_memory_ids": ["memory_typography_editorial_launch"],
                "workflow_decision_ids": ["decision_run2_7_cover_memory"],
                "visual_repair_policy_ids": ["repair_editorial_typography_system"],
                "native_ppt_generation": "native editable PPT objects with trace",
                "workflow_gates": ["public_blocked gate", "native output gate", "source-brand copying blocked"],
                "trace_fields": trace_fields,
            }
        ],
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
    (pack / "run2_66_reference_first_design_grammar.json").write_text(
        json.dumps(valid_run2_66_reference_first_design_grammar(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_43_semantic_visual_asset_memory.json").write_text(
        json.dumps(valid_run2_43_semantic_visual_asset_memory(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_46_visual_object_grammar_memory.json").write_text(
        json.dumps(valid_run2_46_visual_object_grammar_memory(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_73_visual_grammar_modules.json").write_text(
        json.dumps(valid_run2_73_visual_grammar_modules(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_73_scene_plan_expansion.json").write_text(
        json.dumps(valid_run2_73_scene_plan_expansion(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_73_renderer_input_validation.json").write_text(
        json.dumps(valid_run2_73_renderer_input_validation(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_73_renderer_adapter_contracts.json").write_text(
        json.dumps(valid_run2_73_renderer_adapter_contracts(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_74_slide_story.json").write_text(
        json.dumps(valid_run2_74_slide_story(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_74_content_quality_audit.json").write_text(
        json.dumps(valid_run2_74_content_quality_audit(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_73_text_binding_strategy.json").write_text(
        json.dumps(valid_run2_73_text_binding_strategy(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_73_validated_scene_renderer_rerun_result.json").write_text(
        json.dumps(valid_run2_73_validated_scene_renderer_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_74_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_74_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_75_renderer_repair_rerun_result.json").write_text(
        json.dumps(valid_run2_75_renderer_repair_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_76_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_76_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_76_visual_grammar_renderer_repair_plan.json").write_text(
        json.dumps(valid_run2_76_visual_grammar_renderer_repair_plan(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_77_visual_grammar_renderer_repair_rerun_result.json").write_text(
        json.dumps(valid_run2_77_visual_grammar_renderer_repair_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_78_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_78_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_79_renderer_art_direction_repair_rerun_result.json").write_text(
        json.dumps(valid_run2_79_renderer_art_direction_repair_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_80_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_80_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_81_text_composition_typography_plan.json").write_text(
        json.dumps(valid_run2_81_text_composition_typography_plan(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_82_renderer_product_surface_text_composition_rerun_result.json").write_text(
        json.dumps(valid_run2_82_renderer_product_surface_text_composition_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_83_workflow_taxonomy_bias_audit.json").write_text(
        json.dumps(valid_run2_83_workflow_taxonomy_bias_audit(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_84_design_motif_taxonomy_style_router_plan.json").write_text(
        json.dumps(valid_run2_84_design_motif_taxonomy_style_router_plan(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_85_design_motif_renderer_rerun_result.json").write_text(
        json.dumps(valid_run2_85_design_motif_renderer_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_86_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_86_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )
    (pack / "run2_87_best_layout_recovery_visual_primitive_plan.json").write_text(
        json.dumps(valid_run2_87_best_layout_recovery_visual_primitive_plan(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_88_best_layout_visual_primitive_rerun_result.json").write_text(
        json.dumps(valid_run2_88_best_layout_visual_primitive_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_89_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_89_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_90_renderer_asset_surface_composition_rerun_result.json").write_text(
        json.dumps(valid_run2_90_renderer_asset_surface_composition_rerun_result(), indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "run2_91_visual_quality_evaluation.json").write_text(
        json.dumps(valid_run2_91_visual_quality_evaluation(), indent=2),
        encoding="utf-8",
    )


def valid_run2_66_reference_first_design_grammar() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "schema_version": "ppt_run2_66_reference_first_design_grammar.v1",
        "status": "run2_66_reference_first_design_grammar_ready_public_blocked",
        "role_design_grammar_records": [
            {
                "reference_archetype_id": f"reference_first_archetype_2_66_{role}",
                "role": role,
            }
            for role in roles
        ],
    }


def valid_run2_43_semantic_visual_asset_memory() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "schema_version": "ppt_run2_semantic_visual_asset_memory.v1",
        "status": "run2_43_semantic_visual_asset_memory_ready_public_blocked",
        "semantic_visual_asset_records": [
            {
                "semantic_asset_id": f"semantic_asset_2_43_{role}_{index}",
                "role": role,
            }
            for role in roles
            for index in range(1, 4)
        ],
    }


def valid_run2_46_visual_object_grammar_memory() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "schema_version": "ppt_run2_visual_object_grammar_memory.v1",
        "status": "run2_46_visual_object_grammar_memory_ready_public_blocked",
        "visual_object_grammar_records": [
            {
                "visual_object_grammar_id": f"visual_object_grammar_2_46_{role}",
                "role": role,
            }
            for role in roles
        ],
    }


def valid_run2_73_visual_grammar_modules() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    modules = [
        "hero_field",
        "before_after_theater",
        "evidence_workspace",
        "product_reveal",
        "decision_map",
    ]
    return {
        "artifact_id": "run2_73_visual_grammar_modules",
        "part": "Part E",
        "schema_version": "ppt_run2_73_visual_grammar_modules.v1",
        "status": "run2_73_visual_grammar_modules_ready_public_blocked",
        "selected_usecase_id": "usecase_design_to_production_platform_launch",
        "objective": "Assign each page role a content-serving non-card visual grammar.",
        "artifact_scope": {
            "starts": ["map_page_roles_to_advanced_visual_grammar"],
            "does_not_start": ["renderer_rerun", "pptx_output", "html_viewer", "public_release"],
            "quality_gate": "Every page role has a non-card primary structure.",
        },
        "source_inputs": [
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_66_reference_first_design_grammar.json",
                "required": True,
                "available": True,
                "record_count": 6,
                "id_field": "role_design_grammar_records[].reference_archetype_id",
                "use_in_this_artifact": "Source layout archetype.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_43_semantic_visual_asset_memory.json",
                "required": True,
                "available": True,
                "record_count": 18,
                "id_field": "semantic_visual_asset_records[].semantic_asset_id",
                "use_in_this_artifact": "Source semantic objects.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_46_visual_object_grammar_memory.json",
                "required": True,
                "available": True,
                "record_count": 6,
                "id_field": "visual_object_grammar_records[].visual_object_grammar_id",
                "use_in_this_artifact": "Source object grammar.",
            },
        ],
        "stage_policy": "part_e_visual_grammar_modules_only_no_renderer_rerun_no_public_release",
        "global_visual_grammar_contract": {
            "must_do": ["draw the primary structure before labels"],
            "must_not_do": ["use three equal feature cards as the primary structure"],
            "minimum_non_card_signals_per_page": ["dominant composed object", "connective structure"],
        },
        "page_type_to_visual_grammar": [
            {
                "page_type": role,
                "slide_index": index,
                "visual_role": f"{role}_visual_role",
                "primary_visual_grammar_module": module_by_role[role],
                "module_variant": f"{role}_variant",
                "source_reference_archetype_id": f"reference_first_archetype_2_66_{role}",
                "source_visual_object_grammar_id": f"visual_object_grammar_2_46_{role}",
                "source_semantic_asset_ids": [
                    f"semantic_asset_2_43_{role}_1",
                    f"semantic_asset_2_43_{role}_2",
                    f"semantic_asset_2_43_{role}_3",
                ],
                "main_structure": {
                    "name": f"{role}_non_card_structure",
                    "non_rectangular_or_non_card_basis": [
                        "freeform field or route carries hierarchy",
                        "support objects attach to the structure",
                        "labels sit in negative space rather than cards",
                    ],
                    "serves_content_by": "The structure carries the proof object.",
                },
                "draw_order": [
                    "draw the primary structure",
                    "attach the proof object",
                    "add labels after the structure reads",
                ],
                "forbidden_fallbacks": ["three equal cards", "generic dashboard grid"],
                "success_probe": "The structure reads before labels.",
            }
            for index, role in enumerate(roles, start=1)
        ],
        "visual_grammar_modules": [
            {
                "module_id": module,
                "display_name": module.replace("_", " ").title(),
                "use_when": ["the page needs this grammar"],
                "primary_structure": "A non-card structure that carries the content.",
                "how_to_draw": [
                    "draw a non-rectangular primary structure",
                    "attach semantic objects to the structure",
                    "place text after the visual read",
                ],
                "content_service": "The structure explains the content.",
                "native_ppt_primitives": ["freeform path", "mask", "connector"],
                "avoid": ["equal cards", "generic grid"],
            }
            for module in modules
        ],
        "module_geometry_blueprints": [
            {
                "module_id": module,
                "coordinate_system": "normalized_16_9_canvas_0_100",
                "primary_structure_is_not": "a card or rectangle",
                "primary_structure_is": "a non-card path, field, theater, workspace, reveal, or map",
                "native_ppt_shape_plan": [
                    {
                        "shape_id": f"{module}_shape_1",
                        "primitive": "freeform_closed_path",
                        "path_hint": "M 5 70 C 30 40, 70 50, 95 20",
                        "semantic_role": "primary content carrier",
                        "why_not_card": "curved path and attachment points prevent a card read",
                    },
                    {
                        "shape_id": f"{module}_shape_2",
                        "primitive": "connector",
                        "path_hint": "C 20 60, 50 45, 80 30",
                        "semantic_role": "content connection",
                    },
                    {
                        "shape_id": f"{module}_shape_3",
                        "primitive": "attached_surface",
                        "bounds_hint": "x=60 y=30 w=20 h=14",
                        "semantic_role": "proof object",
                    },
                ],
                "content_attachment_points": ["proof object attaches to primary structure"],
            }
            for module in modules
        ],
        "module_selection_rules": [
            {
                "rule_id": f"select_{module}",
                "condition": f"Page requires {module}.",
                "select_module": module,
                "applies_to_page_types": [
                    role for role, role_module in module_by_role.items() if role_module == module
                ],
            }
            for module in modules
        ],
        "coverage_matrix": {
            "page_roles_covered": roles,
            "modules_covered": modules,
            "source_reference_archetype_ids_covered": [
                f"reference_first_archetype_2_66_{role}" for role in roles
            ],
            "source_visual_object_grammar_ids_covered": [
                f"visual_object_grammar_2_46_{role}" for role in roles
            ],
            "source_semantic_asset_ids_covered": [
                f"semantic_asset_2_43_{role}_{index}" for role in roles for index in range(1, 4)
            ],
        },
        "success_criteria_check": {
            "every_page_has_non_rectangular_or_non_card_main_structure": True,
            "every_main_structure_serves_content": True,
            "all_requested_modules_defined": True,
            "no_module_depends_on_copied_source_media": True,
            "public_surface_trace_terms_hidden": True,
        },
        "traceability_summary": {
            "page_type_count": 6,
            "visual_grammar_module_count": 5,
            "semantic_asset_count_bound": 18,
            "reference_archetype_count_bound": 6,
            "visual_object_grammar_count_bound": 6,
            "primary_structure_policy": "non_rectangular_or_non_card_structure_must_carry_page_proof_object",
        },
    }


def valid_run2_73_scene_plan_expansion() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "artifact_id": "run2_73_scene_plan_expansion",
        "stage_policy": "part_d2_scene_plan_expansion_only",
        "scene_structures": [
            {
                "expansion_id": f"scene_expansion_2_73_{role}",
                "role": role,
                "slide_index": index,
            }
            for index, role in enumerate(roles, start=1)
        ],
    }


def valid_run2_73_renderer_input_validation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "artifact_id": "run2_73_renderer_input_validation",
        "stage_policy": "part_d3_renderer_input_validation_only",
        "scene_validation_results": [
            {
                "validation_id": f"renderer_input_validation_2_73_{role}",
                "role": role,
                "status": "pass",
                "renderer_handoff": {
                    "can_handoff_to_renderer": True,
                    "must_not_render_in_d3": True,
                },
            }
            for role in roles
        ],
    }


def valid_run2_73_renderer_adapter_contracts() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    return {
        "artifact_id": "run2_73_renderer_adapter_contracts",
        "part": "Part E2",
        "schema_version": "ppt_run2_73_renderer_adapter_contracts.v1",
        "status": "run2_73_renderer_adapter_contracts_ready_public_blocked",
        "stage_policy": "part_e2_renderer_adapter_contracts_only_no_renderer_rerun_no_public_release",
        "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
        "source_renderer_input_validation": "run2_73_renderer_input_validation.json",
        "source_visual_grammar_modules": "run2_73_visual_grammar_modules.json",
        "source_inputs": [
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
                "available": True,
                "use_in_this_artifact": "D2 scene expansion.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
                "available": True,
                "use_in_this_artifact": "D3 renderer input validation.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
                "available": True,
                "use_in_this_artifact": "Part E visual grammar.",
            },
        ],
        "artifact_scope": {
            "starts": ["prepare_renderer_adapter_manifest_from_d2_d3_e_inputs"],
            "does_not_start": ["renderer_rerun", "pptx_output", "html_viewer", "public_release"],
        },
        "execution_guard": {
            "mode": "adapter_contract_only",
            "rendering_subprocesses_allowed": False,
            "forbidden_invocations": ["renderer_rerun", "pptx_output", "html_viewer", "public_release"],
        },
        "adapter_scene_records": [
            {
                "adapter_scene_id": f"renderer_adapter_2_73_{role}",
                "role": role,
                "slide_index": index,
                "source_expansion_id": f"scene_expansion_2_73_{role}",
                "source_validation_id": f"renderer_input_validation_2_73_{role}",
                "source_visual_grammar_page_type": role,
                "validation_status": "pass",
                "adapter_blocking_issues": [],
                "visual_grammar_binding": {
                    "module_id": module_by_role[role],
                    "main_structure": {"name": f"{role}_structure"},
                },
                "geometry_blueprint_binding": {
                    "module_id": module_by_role[role],
                    "coordinate_system": "normalized_16_9_canvas_0_100",
                },
                "adapter_renderer_instructions": {
                    "renderer_execution_allowed_in_this_artifact": False,
                    "public_release_allowed_in_this_artifact": False,
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "traceability_summary": {
            "scene_count": 6,
            "validated_scene_count": 6,
            "visual_grammar_module_count": 5,
            "geometry_blueprint_count": 5,
            "adapter_blocking_issue_count": 0,
            "sources_consumed": [
                "run2_73_scene_plan_expansion.json",
                "run2_73_renderer_input_validation.json",
                "run2_73_visual_grammar_modules.json",
            ],
        },
        "next_required_action": "renderer_execute_from_d2_d3_e_adapter_manifest",
    }


def valid_run2_74_slide_story() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "artifact_id": "run2_74_slide_story",
        "slides": [
            {
                "slide_id": f"slide_story_2_74_{role}",
                "role": role,
                "slide_index": index,
                "on_canvas_copy": {
                    "headline": f"{role} headline",
                    "supporting_line": f"{role} supporting copy",
                    "proof_labels": ["proof one", "proof two", "proof three"],
                },
                "speaker_note_or_viewer_route": {
                    "speaker_note": f"{role} speaker note",
                    "viewer_only": [f"{role} viewer metadata"],
                },
                "text_budget": {
                    "max_public_words": 42,
                    "max_proof_labels": 3,
                    "density_reason": "Fixture budget.",
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
    }


def valid_run2_74_content_quality_audit() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    return {
        "artifact_id": "run2_74_content_quality_audit",
        "slide_quality_audits": [
            {
                "audit_id": f"content_qa_2_74_{role}",
                "role": role,
                "source_slide_story_id": f"slide_story_2_74_{role}",
                "approved_content_units": [f"{role}_headline", f"{role}_supporting"],
                "scene_compiler_constraints": ["keep text bound to visual objects"],
            }
            for role in roles
        ],
    }


def valid_run2_73_text_binding_strategy() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    forbidden_patterns = [
        "empty text box",
        "generic rectangle label",
        "duplicated headline/supporting copy",
        "text floating without bound visual object",
        "all slides using the same text layout",
    ]

    def socket(role: str, suffix: str, binding_role: str, target: str) -> dict:
        return {
            "socket_id": f"{role}_{suffix}_socket",
            "binding_role": binding_role,
            "bound_visual_object_type": target,
            "bound_source_artifact": "run2_73_renderer_adapter_contracts",
            "bound_source_id": f"renderer_adapter_2_73_{role}",
            "bound_source_path": f"adapter_scene_records.{role}",
            "binding_rationale": "Text inherits position from a named visual object, not a generic box.",
            "capacity": {
                "max_words": 8 if binding_role == "headline" else 14,
                "max_lines": 2,
                "hierarchy_level": "h1" if binding_role == "headline" else binding_role,
                "allowed_font_scale": {"min": 0.72, "max": 1.0},
                "overflow_behavior": "truncate_with_route_to_viewer",
            },
        }

    return {
        "artifact_id": "run2_73_text_binding_strategy",
        "part": "Part F",
        "schema_version": "ppt_run2_73_text_binding_strategy.v1",
        "status": "run2_73_text_binding_strategy_ready_public_blocked",
        "stage_policy": "part_f_text_binding_strategy_only_no_renderer_rerun_no_public_release",
        "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
        "source_renderer_adapter_contracts": "run2_73_renderer_adapter_contracts.json",
        "source_visual_grammar_modules": "run2_73_visual_grammar_modules.json",
        "source_slide_story": "run2_74_slide_story.json",
        "source_content_quality_audit": "run2_74_content_quality_audit.json",
        "source_inputs": [
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
                "available": True,
                "use_in_this_artifact": "D2 semantic components and visual containers.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
                "available": True,
                "use_in_this_artifact": "E2 adapter scenes and visual grammar binding.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
                "available": True,
                "use_in_this_artifact": "Part E text-to-structure grammar.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_74_slide_story.json",
                "available": True,
                "use_in_this_artifact": "Run 2.74 text budgets and on-canvas copy roles.",
            },
            {
                "path": "docs/product/ppt-run2-data-skill-quality/run2_74_content_quality_audit.json",
                "available": True,
                "use_in_this_artifact": "Run 2.74 content quality constraints.",
            },
        ],
        "artifact_scope": {
            "starts": ["bind_copy_roles_to_visual_sockets"],
            "does_not_start": ["renderer_rerun", "pptx_output", "html_viewer", "public_release"],
        },
        "execution_guard": {
            "mode": "text_binding_strategy_only",
            "rendering_subprocesses_allowed": False,
            "forbidden_invocations": ["renderer_rerun", "pptx_output", "html_viewer", "public_release"],
        },
        "global_text_binding_contract": {
            "must_bind_text_to_visual_object": True,
            "must_define_socket_capacity_before_render": True,
            "must_route_overflow_off_canvas": True,
            "must_preserve_distinct_layout_signature_per_role": True,
        },
        "global_forbidden_text_patterns": forbidden_patterns,
        "page_text_binding_records": [
            {
                "text_binding_id": f"text_binding_2_73_{role}",
                "role": role,
                "slide_index": index,
                "layout_signature": f"{role}_text_socket_layout",
                "source_expansion_id": f"scene_expansion_2_73_{role}",
                "source_adapter_scene_id": f"renderer_adapter_2_73_{role}",
                "source_visual_grammar_module": module_by_role[role],
                "source_slide_story_id": f"slide_story_2_74_{role}",
                "source_content_audit_id": f"content_qa_2_74_{role}",
                "text_socket_strategy": {
                    "headline_socket": socket(role, "headline", "headline", "negative space pocket"),
                    "proof_label_sockets": [
                        socket(role, "proof_a", "proof_label", "evidence rail"),
                        socket(role, "proof_b", "proof_label", "connector endpoint"),
                    ],
                    "supporting_copy_socket": socket(role, "supporting_copy", "supporting_copy", "field route"),
                    "callout_sockets": [
                        socket(role, "callout_a", "callout", "product edge"),
                        socket(role, "callout_b", "callout", "decision node"),
                    ],
                    "viewer_note_socket": socket(role, "viewer_note", "viewer_note", "connector endpoint"),
                },
                "overflow_policy": {
                    "max_canvas_words": 30,
                    "max_proof_labels_on_canvas": 3,
                    "route_excess_to": ["speaker_note", "html_viewer_metadata"],
                    "never_create_empty_text_box": True,
                },
                "text_routing": {
                    "canvas_text": ["headline_socket", "supporting_copy_socket", "proof_label_sockets"],
                    "speaker_note_text": ["viewer_note_socket"],
                    "html_viewer_metadata": ["overflow_payload", "source_trace"],
                },
                "forbidden_text_patterns": forbidden_patterns,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "traceability_summary": {
            "page_text_binding_count": 6,
            "socket_count": 42,
            "layout_signature_count": 6,
            "sources_consumed": [
                "run2_73_scene_plan_expansion.json",
                "run2_73_renderer_adapter_contracts.json",
                "run2_73_visual_grammar_modules.json",
                "run2_74_slide_story.json",
                "run2_74_content_quality_audit.json",
            ],
        },
        "next_required_action": "part_g_renderer_rerun_from_validated_text_binding_strategy",
    }


def valid_run2_73_validated_scene_renderer_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
    ]
    forbidden_patterns = [
        "empty text box",
        "generic rectangle label",
        "duplicated headline/supporting copy",
        "text floating without bound visual object",
        "all slides using the same text layout",
    ]

    def binding(role: str, key: str, target: str) -> dict:
        return {
            "socket_id": f"{role}_{key}",
            "socket_key": key,
            "bound_visual_object_type": target,
            "bound_source_id": f"renderer_adapter_2_73_{role}",
            "capacity": {
                "max_words": 10,
                "max_lines": 2,
                "hierarchy_level": "h1" if key == "headline_socket" else "callout",
                "allowed_font_scale": {"min": 0.72, "max": 1.0},
                "overflow_behavior": "truncate_with_route_to_viewer",
            },
        }

    return {
        "artifact_id": "run2_73_validated_scene_renderer_rerun_result",
        "part": "Part G",
        "run_id": "2.73",
        "status": "run2_73_validated_scene_renderer_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "generated_viewer_check_only_no_part_h_quality_verdict",
        "consumed_sources": consumed_sources,
        "rerun_manifest": {
            "generator": "scripts/generate_ppt_run2_73_validated_scene_renderer_arms.mjs",
            "consumed_sources": consumed_sources,
            "best_internal_arm": "run2_73_full_validated_scene_renderer",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-73-full-vulca/output/run2-73-validated-scene-renderer.html",
                "pptx": "outputs/thread/presentations/ppt-run2-73-full-vulca/output/ppt-run2-73-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
            },
            "viewer_update": {
                "latest_run_id": "2.73",
                "viewer_can_reference_new_run": True,
            },
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "layout_signature": f"{role}_validated_scene_renderer",
                "source_text_binding_id": f"text_binding_2_73_{role}",
                "text_sockets_used": [
                    "headline_socket",
                    "proof_label_sockets",
                    "supporting_copy_socket",
                    "callout_sockets",
                    "viewer_note_socket",
                ],
                "text_socket_bindings": [
                    binding(role, "headline_socket", "negative space pocket"),
                    binding(role, "proof_label_sockets", "evidence rail"),
                    binding(role, "supporting_copy_socket", "field route"),
                    binding(role, "callout_sockets", "product edge"),
                    binding(role, "viewer_note_socket", "connector endpoint"),
                ],
                "visual_containers": [
                    {
                        "container_id": f"{role}_main_structure",
                        "visual_object_type": "product edge",
                        "bound_text_socket_ids": [f"{role}_headline_socket"],
                        "empty": False,
                    }
                ],
                "source_trace_terms_visible_on_canvas": [],
                "forbidden_text_patterns_absent": forbidden_patterns,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "render_quality_checks": {
            "empty_visual_container_count": 0,
            "floating_text_without_bound_visual_object_count": 0,
            "generic_rectangle_label_count": 0,
            "source_trace_terms_visible_on_canvas_count": 0,
            "distinct_text_layout_signatures": 6,
            "pages_using_expected_visual_grammar": 6,
            "pages_using_required_text_sockets": 6,
        },
        "next_required_action": "part_h_visual_quality_evaluation",
    }


def valid_run2_74_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    return {
        "artifact_id": "run2_74_visual_quality_evaluation",
        "part": "Part H",
        "schema_version": "ppt_run2_74_visual_quality_evaluation.v1",
        "run_id": "2.74",
        "status": "run2_74_visual_quality_evaluation_public_blocked",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "public_ready": False,
        "quality_claim_boundary": "part_h_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.72",
            "evaluated_run": "2.73",
        },
        "input_chain": {
            "run2_72_result": "docs/product/ppt-run2-data-skill-quality/results/run2_72_shape_bound_text_rerun_result.json",
            "run2_73_result": "docs/product/ppt-run2-data-skill-quality/results/run2_73_validated_scene_renderer_rerun_result.json",
            "run2_72_full_trace_manifest": "outputs/thread/presentations/ppt-run2-72-full-vulca/trace_manifest.json",
            "run2_73_full_trace_manifest": "outputs/thread/presentations/ppt-run2-73-full-vulca/trace_manifest.json",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "viewer_latest_run_id": "2.73",
            "viewer_can_compare_2_72_and_2_73": True,
            "run2_72_full_preview_count": 6,
            "run2_73_full_preview_count": 6,
            "browser_check_required_for_handoff": True,
        },
        "evaluation_questions": {
            "is_2_73_better_than_2_72": {"answer": "mixed_not_public_quality_pass"},
            "is_text_fused_with_visual_structure": {"answer": "partial"},
            "does_it_still_feel_like_engineering_report": {"answer": "yes_but_different_failure_mode"},
            "do_six_pages_have_distinct_visual_grammar": {"answer": "yes_trace_and_thumbnail"},
            "which_pages_need_repair_and_which_layer": {"answer": "renderer_first"},
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_72": "structural_variety_up_public_polish_down",
            "top_blocker": "thin_abstract_renderer_placeholders_do_not_read_as_product_presentation",
            "next_layer_to_fix": "renderer",
        },
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "delta_vs_2_72": "more_distinct_but_less_polished",
                "text_visual_fusion": "partial",
                "report_like_risk": "high",
                "root_cause_layer": "renderer",
                "repair_required": True,
                "repair_instruction": "Redraw as a concrete product surface instead of thin abstract placeholders.",
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "renderer",
            "not_primary_layer": "data_absence",
            "secondary_layers": ["visual_grammar", "text_binding"],
        },
        "next_required_action": "part_i_renderer_repair_from_visual_quality_evaluation",
    }


def valid_run2_75_renderer_repair_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
        "docs/product/ppt-run2-data-skill-quality/results/run2_74_visual_quality_evaluation.json",
    ]
    repair_flags = [
        "h_repair_instruction_consumed",
        "concrete_product_surface",
        "higher_visual_density",
        "stronger_text_visual_attachment",
        "public_polish_not_claimed",
    ]
    return {
        "artifact_id": "run2_75_renderer_repair_rerun_result",
        "part": "Part I",
        "schema_version": "ppt_run2_75_renderer_repair_rerun_result.v1",
        "run_id": "2.75",
        "status": "run2_75_renderer_repair_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "renderer_repair_generated_viewer_check_only_no_part_j_quality_verdict",
        "consumed_sources": consumed_sources,
        "source_h_evaluation": {
            "status": "run2_74_visual_quality_evaluation_public_blocked",
            "top_blocker": "thin_abstract_renderer_placeholders_do_not_read_as_product_presentation",
            "next_required_action": "part_i_renderer_repair_from_visual_quality_evaluation",
        },
        "renderer_repair_manifest": {
            "generator": "scripts/generate_ppt_run2_75_renderer_repair_arms.mjs",
            "consumed_sources": consumed_sources,
            "best_internal_arm": "run2_75_full_renderer_repair",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-75-full-vulca/output/run2-75-renderer-repair.html",
                "pptx": "outputs/thread/presentations/ppt-run2-75-full-vulca/output/ppt-run2-75-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
            },
            "viewer_update": {
                "latest_run_id": "2.75",
                "viewer_can_reference_new_run": True,
            },
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "visual_density_profile": f"{role}_repaired_density_profile",
                "source_text_binding_id": f"text_binding_2_73_{role}",
                "text_sockets_used": [
                    "headline_socket",
                    "proof_label_sockets",
                    "supporting_copy_socket",
                    "callout_sockets",
                    "viewer_note_socket",
                ],
                "h_repair_source": {
                    "root_cause_layer": "renderer",
                    "repair_instruction": "Redraw as a concrete product surface.",
                },
                "renderer_repair_directives_applied": repair_flags,
                "product_surface_detail_count": 6,
                "connector_or_edge_binding_count": 4,
                "source_trace_terms_visible_on_canvas": [],
                "forbidden_text_patterns_absent": [
                    "empty text box",
                    "generic rectangle label",
                    "duplicated headline/supporting copy",
                    "text floating without bound visual object",
                    "all slides using the same text layout",
                ],
            }
            for index, role in enumerate(roles, start=1)
        ],
        "renderer_repair_checks": {
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
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_j_visual_quality_evaluation_for_run2_75",
    }


def valid_run2_76_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    return {
        "artifact_id": "run2_76_visual_quality_evaluation",
        "part": "Part J",
        "schema_version": "ppt_run2_76_visual_quality_evaluation.v1",
        "run_id": "2.76",
        "status": "run2_76_visual_quality_evaluation_public_blocked",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "public_ready": False,
        "quality_claim_boundary": "part_j_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.73",
            "evaluated_run": "2.75",
        },
        "input_chain": {
            "run2_73_result": "docs/product/ppt-run2-data-skill-quality/results/run2_73_validated_scene_renderer_rerun_result.json",
            "run2_75_result": "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json",
            "run2_74_h_evaluation": "docs/product/ppt-run2-data-skill-quality/results/run2_74_visual_quality_evaluation.json",
            "run2_73_full_contact_sheet": "outputs/thread/presentations/ppt-run2-73-full-vulca/preview/contact-sheet.png",
            "run2_75_full_contact_sheet": "outputs/thread/presentations/ppt-run2-75-full-vulca/preview/contact-sheet.png",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "viewer_latest_run_id": "2.75",
            "viewer_can_compare_2_73_and_2_75": True,
            "run2_73_full_preview_count": 6,
            "run2_75_full_preview_count": 6,
            "browser_check_required_for_handoff": True,
        },
        "gemini_agent_review_summary": {
            "tool": "mcp__gemini_agent.gemini_artifact_review",
            "model": "gemini-3.5-flash",
            "review_count": 2,
            "used_for_verdict": True,
            "run2_75_findings": [
                "product_surface_detail_up",
                "page_differentiation_regression_for_01_02_04_05",
            ],
            "shared_risks": ["engineering blueprint risk remains"],
        },
        "evaluation_questions": {
            "is_2_75_better_than_2_73": {
                "answer": "mixed_product_surface_up_page_differentiation_down_public_blocked"
            },
            "does_2_75_have_stronger_product_feel": {"answer": "yes_but_still_wireframe"},
            "are_page_differences_stronger_or_weaker": {"answer": "weaker_for_core_product_surface_pages"},
            "is_text_binding_better": {"answer": "slightly_stronger_but_small_labels_remain"},
            "does_2_75_reach_public_video_presentation_direction": {"answer": "no_internal_blueprint_risk_remains"},
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_73": "product_surface_up_page_differentiation_down_public_readiness_still_blocked",
            "top_blocker": "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams",
            "next_layer_to_fix": "visual_grammar_and_renderer",
        },
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "product_feel_delta": "improved_but_wireframe",
                "page_differentiation_delta": "weaker" if role in {"cover", "setup", "proof", "climax"} else "same",
                "text_binding_delta": "slightly_stronger_but_small",
                "engineering_report_risk": "high",
                "public_video_direction": "no",
                "root_cause_layer": "visual_grammar",
                "repair_required": True,
                "repair_instruction": "Break repeated wireframe surfaces and add public-facing product context.",
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "visual_grammar_and_renderer",
            "not_primary_layer": "data_absence",
            "secondary_layers": ["text_binding"],
        },
        "next_required_action": "part_k_visual_grammar_and_renderer_repair_from_j_evaluation",
    }


def valid_run2_76_visual_grammar_renderer_repair_plan() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    target_by_role = {
        "cover": "finished product hero emerging from source memory",
        "setup": "source-to-memory transformation field",
        "contrast": "asymmetric before-after product theater",
        "proof": "evidence inspection scene with active proof lane",
        "climax": "completion reveal of editable PPT result",
        "close": "decision / release gate handoff map",
    }
    return {
        "artifact_id": "run2_76_visual_grammar_renderer_repair_plan",
        "part": "Part K1",
        "schema_version": "ppt_run2_76_visual_grammar_renderer_repair_plan.v1",
        "run_id": "2.76",
        "status": "run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked",
        "stage_policy": "part_k1_repair_contract_only_no_renderer_rerun_no_public_release",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_k1_repair_contract_only_no_renderer_rerun_no_public_release",
        "consumed_sources": [
            "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json",
            "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
            "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
            "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
            "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
        ],
        "source_j_evaluation": {
            "source_path": "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
            "status": "run2_76_visual_quality_evaluation_public_blocked",
            "top_blocker": "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams",
            "primary_layer_to_fix": "visual_grammar_and_renderer",
            "secondary_layers": ["text_binding"],
            "next_required_action": "part_k_visual_grammar_and_renderer_repair_from_j_evaluation",
        },
        "source_run2_75_renderer_repair": {
            "source_path": "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json",
            "status": "run2_75_renderer_repair_rerun_generated_public_blocked",
            "public_ready": False,
        },
        "source_trace": {
            "visual_grammar_modules": "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
            "renderer_adapter_contracts": "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
            "text_binding_strategy": "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
            "scene_plan_expansion": "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
        },
        "global_repair_strategy": {
            "from_failure_mode": "wireframe blueprint aesthetic and repeated product surfaces",
            "target_shift": "public-video presentation scene with differentiated page rhythm",
            "primary_layers_to_fix": ["visual_grammar", "renderer"],
            "secondary_layers_to_fix": ["text_binding"],
            "not_data_layer_reason": "data inputs are present; visible failure is visual grammar and renderer expression",
            "page_differentiation_mandates": [
                "cover and climax must not both read as product surface diagrams",
                "setup must not borrow proof workspace structure",
                "proof must become an evidence inspection scene rather than a grid",
                "close must resolve as a decision / release gate rather than a summary page",
            ],
            "renderer_capabilities_required": [
                "hero crop",
                "editorial mask",
                "asymmetric foreground/background depth",
                "larger proof object",
                "fewer but more meaningful labels",
                "scene-specific connectors",
                "non-grid evidence arrangement",
            ],
            "forbidden_renderer_fallbacks": [
                "debug-like outlines",
                "uniform small label wall",
                "same product window skeleton on every page",
                "schematic blueprint as final visual unless it is the actual proof object",
            ],
            "quality_gate": "K2 may start a renderer rerun only after every page has a unique target scene direction.",
        },
        "page_repair_plans": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "source_j_assessment": {
                    "root_cause_layer": "visual_grammar",
                    "repair_instruction": "Break repeated wireframe surfaces and add public-facing product context.",
                },
                "current_failure": "too close to repeated wireframe product surface",
                "target_scene_direction": target_by_role[role],
                "visual_grammar_change": "differentiate scene-specific primary structure",
                "renderer_change": "use hero crop, editorial mask, scene-specific connectors, and non-grid evidence arrangement",
                "text_binding_adjustment": "use fewer but more meaningful labels attached to scene objects",
                "must_preserve_from_2_75": ["expected visual grammar module", "stronger connector binding"],
                "must_remove_from_2_75": ["debug-like outlines", "uniform small label wall"],
                "acceptance_checks": {
                    "page_differentiation_check": "target scene direction is unique",
                    "wireframe_reduction_check": "no debug-like outlines or uniform small label wall",
                    "renderer_capability_check": "uses at least one required renderer capability",
                    "no_renderer_rerun_in_k1": True,
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "next_required_action": "part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan",
    }


def valid_run2_77_visual_grammar_renderer_repair_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    target_by_role = {
        "cover": "finished product hero emerging from source memory",
        "setup": "source-to-memory transformation field",
        "contrast": "asymmetric before-after product theater",
        "proof": "evidence inspection scene with active proof lane",
        "climax": "completion reveal of editable PPT result",
        "close": "decision / release gate handoff map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
        "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
        "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
    ]
    capabilities = [
        "hero crop",
        "editorial mask",
        "asymmetric foreground/background depth",
        "larger proof object",
        "fewer but more meaningful labels",
        "scene-specific connectors",
        "non-grid evidence arrangement",
    ]
    forbidden = [
        "debug-like outlines",
        "uniform small label wall",
        "same product window skeleton on every page",
        "schematic blueprint as final visual unless it is the actual proof object",
    ]
    return {
        "artifact_id": "run2_77_visual_grammar_renderer_repair_rerun_result",
        "part": "Part K2",
        "schema_version": "ppt_run2_77_visual_grammar_renderer_repair_rerun_result.v1",
        "run_id": "2.77",
        "status": "run2_77_visual_grammar_renderer_repair_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "visual_grammar_renderer_repair_generated_viewer_check_only_no_part_l_quality_verdict",
        "consumed_sources": consumed_sources,
        "source_k1_repair_plan": {
            "status": "run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked",
            "top_blocker": "wireframe_blueprint_aesthetic_and_repeated_product_surfaces_still_read_as_internal_engineering_diagrams",
            "next_required_action": "part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan",
            "source_result": "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
        },
        "visual_grammar_renderer_repair_manifest": {
            "generator": "scripts/generate_ppt_run2_77_visual_grammar_renderer_repair_arms.mjs",
            "consumed_sources": consumed_sources,
            "best_internal_arm": "run2_77_full_visual_grammar_renderer_repair",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-77-full-vulca/index.html",
                "pptx": "outputs/thread/presentations/ppt-run2-77-full-vulca/output/ppt-run2-77-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
                "combined_contact_sheet": "outputs/thread/presentations/run2-77-four-arm-contact-sheet.png",
                "full_contact_sheet": "outputs/thread/presentations/ppt-run2-77-full-vulca/preview/contact-sheet.png",
            },
            "viewer_update": {
                "latest_run_id": "2.77",
                "viewer_can_reference_new_run": True,
            },
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "source_text_binding_id": f"text_binding_2_73_{role}",
                "target_scene_direction": target_by_role[role],
                "source_k1_repair_plan": {
                    "target_scene_direction": target_by_role[role],
                    "current_failure": "too close to repeated wireframe product surface",
                },
                "renderer_repair_directives_applied": [
                    "k1_repair_plan_consumed",
                    "target_scene_direction_applied",
                    "page_differentiation_repaired",
                    "forbidden_fallbacks_removed",
                    "public_polish_not_claimed",
                ],
                "renderer_capabilities_applied": capabilities[index - 1 : index + 1] or [capabilities[0]],
                "forbidden_renderer_fallbacks_absent": forbidden,
                "label_count": 4,
                "source_trace_terms_visible_on_canvas": [],
                "visual_containers": [{"container_id": f"{role}_scene", "empty": False}],
                "k1_acceptance_checks": {
                    "page_differentiation_check": "target scene direction is unique",
                    "wireframe_reduction_check": "forbidden fallbacks absent",
                    "renderer_capability_check": "required capability used",
                    "no_renderer_rerun_in_k1": True,
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "visual_grammar_renderer_repair_checks": {
            "pages_with_k1_repair_plan_consumed": 6,
            "pages_using_expected_visual_grammar": 6,
            "distinct_target_scene_directions": 6,
            "pages_with_forbidden_fallbacks_absent": 6,
            "pages_with_reduced_label_count": 6,
            "required_renderer_capabilities_covered": sorted(capabilities),
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_l_visual_quality_evaluation_for_run2_77",
    }


def valid_run2_78_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    question_ids = [
        "is_2_77_better_than_2_75",
        "did_2_77_restore_page_differentiation",
        "did_2_77_reduce_wireframe_aesthetic",
        "did_2_77_reduce_small_label_problem",
        "does_2_77_improve_product_presentation_feel",
        "does_2_77_reach_public_video_presentation_direction",
    ]
    return {
        "artifact_id": "run2_78_visual_quality_evaluation",
        "part": "Part L",
        "schema_version": "ppt_run2_78_visual_quality_evaluation.v1",
        "run_id": "2.78",
        "status": "run2_78_visual_quality_evaluation_public_blocked",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_l_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.75",
            "evaluated_run": "2.77",
            "prior_reference_run": "2.73",
        },
        "input_chain": {
            "run2_77_result": "docs/product/ppt-run2-data-skill-quality/results/run2_77_visual_grammar_renderer_repair_rerun_result.json",
            "run2_76_j_evaluation": "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
            "run2_76_k1_repair_plan": "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
            "run2_75_full_contact_sheet": "outputs/thread/presentations/ppt-run2-75-full-vulca/preview/contact-sheet.png",
            "run2_77_full_contact_sheet": "outputs/thread/presentations/ppt-run2-77-full-vulca/preview/contact-sheet.png",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "viewer_latest_run_id": "2.77",
            "viewer_can_compare_2_75_and_2_77": True,
            "run2_75_full_preview_count": 6,
            "run2_77_full_preview_count": 6,
            "browser_check_required_for_handoff": True,
        },
        "gemini_agent_review_summary": {
            "tool": "mcp__gemini_agent.gemini_artifact_review",
            "model": "gemini-3.5-flash",
            "review_count": 1,
            "used_for_verdict": True,
            "run2_77_findings": ["moderate page differentiation", "technical abstract feel"],
            "run2_77_risks": ["wireframe aesthetic remains", "small labels remain"],
        },
        "evaluation_questions": {
            question_id: {"answer": "placeholder", "basis": "source-backed internal visual review"}
            for question_id in question_ids
        }
        | {
            "is_2_77_better_than_2_75": {
                "answer": "partial_page_differentiation_up_public_blocked",
                "basis": "2.77 improves role-specific scenes but remains public blocked.",
            },
            "did_2_77_restore_page_differentiation": {
                "answer": "moderately_improved_but_01_04_05_share_wireframe_family",
                "basis": "Target scenes differ, but several product pages still share a wireframe family.",
            },
            "did_2_77_reduce_wireframe_aesthetic": {
                "answer": "no_wireframe_still_dominant",
                "basis": "Thin outlines and red annotation marks remain dominant.",
            },
            "did_2_77_reduce_small_label_problem": {
                "answer": "partial_label_count_down_but_labels_still_tiny",
                "basis": "Label count is reduced, but labels are still too small for public video.",
            },
            "does_2_77_improve_product_presentation_feel": {
                "answer": "partial_more_scene_specific_but_abstract_product_surface",
                "basis": "Presentation scenes are clearer, but product surfaces are abstract.",
            },
            "does_2_77_reach_public_video_presentation_direction": {
                "answer": "no_public_blocked",
                "basis": "It remains an internal proof, not a public-ready presentation.",
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_75": "page_differentiation_up_label_count_down_wireframe_still_blocks_public_readiness",
            "top_blocker": "thin_wireframe_product_surfaces_and_annotation_marks_still_read_as_internal_diagram",
            "next_layer_to_fix": "renderer_art_direction_and_scene_realization",
        },
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "delta_vs_2_75": "partial",
                "page_differentiation": "partial",
                "wireframe_reduction": "weak",
                "label_hierarchy": "partial",
                "public_video_direction": "no",
                "root_cause_layer": "renderer",
                "repair_required": True,
                "visual_observation": "Still reads as a technical wireframe scene.",
                "next_repair_instruction": "Replace thin diagram surfaces with stronger public presentation art direction.",
                "trace_support": {
                    "target_scene_direction": f"{role} target scene",
                    "label_count": 4,
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "renderer_art_direction_and_scene_realization",
            "secondary_layers": ["text_binding", "visual_grammar"],
            "not_primary_layer": "data_absence",
            "rationale": "K2 consumed the data and K1 plan; visible blockers are rendering/art direction.",
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_m_renderer_art_direction_repair_from_l_evaluation",
    }


def valid_run2_79_renderer_art_direction_repair_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
        "docs/product/ppt-run2-data-skill-quality/results/run2_77_visual_grammar_renderer_repair_rerun_result.json",
        "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
    ]
    directives = [
        "l_repair_instruction_consumed",
        "wireframe_surface_replaced",
        "debug_annotation_removed",
        "dominant_product_object",
        "foreground_background_depth",
        "public_scene_hierarchy",
        "public_polish_not_claimed",
    ]
    scene_by_role = {
        "cover": "finished product hero crop with editorial depth",
        "setup": "source transformation field with solid product destination",
        "contrast": "asymmetric transformation theater with rich after surface",
        "proof": "inspection bench with one enlarged evidence object",
        "climax": "completion reveal with full-frame editable result",
        "close": "release gate scene with dominant blocked-public decision",
    }
    return {
        "artifact_id": "run2_79_renderer_art_direction_repair_rerun_result",
        "part": "Part M",
        "schema_version": "ppt_run2_79_renderer_art_direction_repair_rerun_result.v1",
        "run_id": "2.79",
        "status": "run2_79_renderer_art_direction_repair_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "renderer_art_direction_repair_generated_viewer_check_only_no_part_n_quality_verdict",
        "consumed_sources": consumed_sources,
        "source_l_evaluation": {
            "status": "run2_78_visual_quality_evaluation_public_blocked",
            "top_blocker": "thin_wireframe_product_surfaces_and_annotation_marks_still_read_as_internal_diagram",
            "next_required_action": "part_m_renderer_art_direction_repair_from_l_evaluation",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
        },
        "renderer_art_direction_repair_manifest": {
            "generator": "scripts/generate_ppt_run2_79_renderer_art_direction_repair_arms.mjs",
            "consumed_sources": consumed_sources,
            "best_internal_arm": "run2_79_full_renderer_art_direction_repair",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-79-full-vulca/output/run2-79-renderer-art-direction-repair.html",
                "pptx": "outputs/thread/presentations/ppt-run2-79-full-vulca/output/ppt-run2-79-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
            },
            "viewer_update": {
                "latest_run_id": "2.79",
                "viewer_can_reference_new_run": True,
            },
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "art_direction_scene": scene_by_role[role],
                "source_run2_77_page": {"target_scene_direction": f"{role} target scene"},
                "source_l_repair_instruction": "Repair renderer art direction.",
                "renderer_repair_directives_applied": directives,
                "debug_annotation_count": 0,
                "wireframe_dependency": "reduced",
                "dominant_product_object_scale": "large",
                "min_visible_label_font_size": 12,
                "label_count": 2,
                "source_trace_terms_visible_on_canvas": [],
                "public_polish_claimed": False,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "renderer_art_direction_repair_checks": {
            "pages_with_l_repair_instruction_consumed": 6,
            "pages_with_debug_annotations_removed": 6,
            "pages_with_dominant_product_object": 6,
            "pages_with_public_scene_hierarchy": 6,
            "pages_with_reduced_wireframe_dependency": 6,
            "pages_with_min_visible_label_size": 6,
            "source_trace_terms_visible_on_canvas_count": 0,
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_n_visual_quality_evaluation_for_run2_79",
    }


def valid_run2_80_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    question_ids = [
        "is_2_79_better_than_2_77",
        "did_2_79_reduce_wireframe_and_annotation",
        "did_2_79_fix_small_label_problem",
        "did_2_79_create_concrete_product_surface",
        "does_2_79_reach_public_video_presentation_direction",
        "which_layer_needs_next_repair",
    ]
    return {
        "artifact_id": "run2_80_visual_quality_evaluation",
        "part": "Part N",
        "schema_version": "ppt_run2_80_visual_quality_evaluation.v1",
        "run_id": "2.80",
        "status": "run2_80_visual_quality_evaluation_public_blocked",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_n_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.77",
            "evaluated_run": "2.79",
            "prior_reference_run": "2.75",
        },
        "input_chain": {
            "run2_79_result": "docs/product/ppt-run2-data-skill-quality/results/run2_79_renderer_art_direction_repair_rerun_result.json",
            "run2_78_l_evaluation": "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
            "run2_77_result": "docs/product/ppt-run2-data-skill-quality/results/run2_77_visual_grammar_renderer_repair_rerun_result.json",
            "run2_77_full_contact_sheet": "outputs/thread/presentations/ppt-run2-77-full-vulca/preview/contact-sheet.png",
            "run2_79_full_contact_sheet": "outputs/thread/presentations/ppt-run2-79-full-vulca/preview/contact-sheet.png",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "viewer_latest_run_id": "2.79",
            "viewer_can_compare_2_77_and_2_79": True,
            "run2_77_full_preview_count": 6,
            "run2_79_full_preview_count": 6,
            "browser_check_required_for_handoff": True,
        },
        "gemini_agent_review_summary": {
            "tool": "mcp__gemini_agent.gemini_artifact_review",
            "model": "gemini-3.5-flash",
            "review_count": 1,
            "used_for_verdict": True,
            "run2_79_findings": ["ultra minimalist layout", "sparse text wireframe"],
            "run2_79_risks": ["product surface absent", "small labels remain"],
        },
        "evaluation_questions": {
            question_id: {"answer": "placeholder", "basis": "source-backed internal visual review"}
            for question_id in question_ids
        }
        | {
            "is_2_79_better_than_2_77": {
                "answer": "mixed_annotation_down_but_product_surface_absent_public_blocked",
                "basis": "2.79 removes debug annotations but still lacks visible product surfaces.",
            },
            "did_2_79_reduce_wireframe_and_annotation": {
                "answer": "partial_debug_annotations_removed_but_typographic_wireframe_remains",
                "basis": "Debug marks are gone, but the pages remain sparse typographic wireframes.",
            },
            "did_2_79_fix_small_label_problem": {
                "answer": "no_labels_still_tiny_and_spatially_scattered",
                "basis": "Labels are more meaningful but still tiny at public-video scale.",
            },
            "did_2_79_create_concrete_product_surface": {
                "answer": "no_product_surface_not_visibly_realized",
                "basis": "The contact sheet does not show a concrete product interface or presentation object.",
            },
            "does_2_79_reach_public_video_presentation_direction": {
                "answer": "no_public_blocked",
                "basis": "It remains an internal visual proof.",
            },
            "which_layer_needs_next_repair": {
                "answer": "renderer_product_surface_realization",
                "basis": "The next issue is visible rendering of product surfaces, not source data.",
            },
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_77": "debug_annotations_down_but_product_surface_absent_and_small_labels_remain",
            "top_blocker": "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes",
            "next_layer_to_fix": "renderer_product_surface_realization",
        },
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "delta_vs_2_77": "partial",
                "wireframe_reduction": "partial",
                "label_hierarchy": "weak",
                "product_surface_realization": "weak",
                "public_video_direction": "no",
                "root_cause_layer": "renderer",
                "repair_required": True,
                "visual_observation": "Debug marks are reduced, but the slide still reads as a sparse wireframe.",
                "next_repair_instruction": "Render a visible product surface with public-facing hierarchy.",
                "trace_support": {
                    "art_direction_scene": f"{role} art direction scene",
                    "label_count": 2,
                    "debug_annotation_count": 0,
                    "wireframe_dependency": "reduced",
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "renderer_product_surface_realization",
            "secondary_layers": ["text_binding"],
            "not_primary_layer": "data_absence",
            "rationale": "2.79 consumed M inputs; visible blockers are product-surface rendering and public hierarchy.",
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_o_renderer_product_surface_repair_from_n_evaluation",
    }


def valid_run2_81_text_composition_typography_plan() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/run2_43_editorial_composition_typography_memory.json",
        "docs/product/ppt-run2-data-skill-quality/run2_49_readability_memory.json",
        "docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json",
        "docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json",
        "docs/product/ppt-run2-data-skill-quality/run2_64_text_fit_renderer_gates.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_tutorial_to_design_moves.json",
        "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
        "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
    ]
    forbidden = [
        "floating labels",
        "tiny labels without object anchors",
        "duplicate run tags",
        "traceability on slide canvas",
        "headline plus chips only",
    ]

    def block(role: str, name: str, max_words: int, font_size: int) -> dict:
        return {
            "text_role": name,
            "copy_intent": f"{role} {name} tells one public-facing idea tied to the product surface.",
            "bound_visual_object_type": "product surface" if name != "proof_sentence" else "evidence object",
            "object_anchor_required": True,
            "capacity": {"max_words": max_words, "max_lines": 2 if name == "headline_block" else 3},
            "typography": {
                "min_font_size": font_size,
                "line_height": 1.08 if name == "headline_block" else 1.24,
                "weight": "bold" if name in {"headline_block", "object_caption"} else "regular",
                "alignment": "left",
            },
            "canvas_route": "slide_canvas",
        }

    return {
        "artifact_id": "run2_81_text_composition_typography_plan",
        "part": "Part O1",
        "schema_version": "ppt_run2_81_text_composition_typography_plan.v1",
        "run_id": "2.81",
        "status": "run2_81_text_composition_typography_plan_ready_public_blocked",
        "stage_policy": "part_o1_text_composition_typography_plan_only_no_renderer_rerun_no_public_release",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "consumed_sources": consumed_sources,
        "source_inputs": [
            {"path": source, "available": True, "usage": "text_composition_rule_source"}
            for source in consumed_sources
        ],
        "source_n_evaluation": {
            "status": "run2_80_visual_quality_evaluation_public_blocked",
            "top_blocker": "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes",
            "next_required_action": "part_o_renderer_product_surface_repair_from_n_evaluation",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
        },
        "global_text_composition_contract": {
            "required_canvas_text_blocks": [
                "headline_block",
                "subhead_block",
                "proof_sentence",
                "object_caption",
            ],
            "global_forbidden_patterns": forbidden,
            "traceability_default_route": "viewer_metadata_and_speaker_notes",
            "slide_canvas_traceability_allowed": False,
            "minimum_main_text_region_count": 1,
        },
        "page_text_composition_records": [
            {
                "text_composition_id": f"text_composition_2_81_{role}",
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "source_text_binding_id": f"text_binding_2_73_{role}",
                "source_n_role_assessment": {
                    "repair_required": True,
                    "next_repair_instruction": "Render a visible product surface with public-facing hierarchy.",
                },
                "headline_block": block(role, "headline_block", 10, 30),
                "subhead_block": block(role, "subhead_block", 22, 16),
                "proof_sentence": block(role, "proof_sentence", 24, 14),
                "object_caption": block(role, "object_caption", 10, 12),
                "label_policy": {
                    "max_visible_labels": 3,
                    "min_font_size": 12,
                    "must_attach_to_visible_object": True,
                    "floating_labels_allowed": False,
                    "overflow_route": "viewer_metadata_and_speaker_notes",
                },
                "viewer_note_route": {
                    "target": "viewer_metadata_and_speaker_notes",
                    "traceability_on_canvas": False,
                    "speaker_note_allowed": True,
                },
                "forbidden_patterns": forbidden,
                "renderer_constraints": {
                    "must_create_main_reading_region": True,
                    "must_bind_caption_to_product_surface": True,
                    "must_not_render_traceability_terms": True,
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "traceability_summary": {
            "page_text_composition_record_count": 6,
            "source_input_count": len(consumed_sources),
            "renderer_rerun_started": False,
        },
        "next_required_action": "part_o2_renderer_rerun_from_text_composition_and_product_surface_repair",
    }


def valid_run2_82_renderer_product_surface_text_composition_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
        "docs/product/ppt-run2-data-skill-quality/results/run2_79_renderer_art_direction_repair_rerun_result.json",
        "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
    ]
    directives = [
        "n_repair_instruction_consumed",
        "o1_text_composition_consumed",
        "concrete_product_surface_rendered",
        "text_hierarchy_applied",
        "floating_labels_removed",
        "traceability_routed_off_canvas",
        "public_polish_not_claimed",
    ]
    surface_by_role = {
        "cover": "editable_ppt_product_mock",
        "setup": "source_to_memory_product_flow",
        "contrast": "before_after_product_theater",
        "proof": "evidence_product_workspace",
        "climax": "editable_ppt_product_mock",
        "close": "release_decision_product_map",
    }
    return {
        "artifact_id": "run2_82_renderer_product_surface_text_composition_rerun_result",
        "part": "Part O2",
        "schema_version": "ppt_run2_82_renderer_product_surface_text_composition_rerun_result.v1",
        "run_id": "2.82",
        "status": "run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "renderer_product_surface_text_composition_generated_viewer_check_only_no_part_p_quality_verdict",
        "consumed_sources": consumed_sources,
        "source_n_evaluation": {
            "status": "run2_80_visual_quality_evaluation_public_blocked",
            "top_blocker": "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes",
            "next_required_action": "part_o_renderer_product_surface_repair_from_n_evaluation",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
        },
        "source_o1_text_composition_plan": {
            "status": "run2_81_text_composition_typography_plan_ready_public_blocked",
            "next_required_action": "part_o2_renderer_rerun_from_text_composition_and_product_surface_repair",
            "source_result": "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
        },
        "renderer_product_surface_text_composition_manifest": {
            "generator": "scripts/generate_ppt_run2_82_product_surface_text_composition_arms.mjs",
            "consumed_sources": consumed_sources,
            "arms": [
                "prompt_only",
                "run1_5_skill",
                "run2_82_full_product_surface_text_composition",
                "bad_run2_82_without_text_composition",
            ],
            "best_internal_arm": "run2_82_full_product_surface_text_composition",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-82-full-vulca/output/run2-82-product-surface-text-composition.html",
                "pptx": "outputs/thread/presentations/ppt-run2-82-full-vulca/output/ppt-run2-82-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
            },
            "viewer_update": {
                "latest_run_id": "2.82",
                "viewer_can_reference_new_run": True,
            },
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "source_o1_text_composition_id": f"text_composition_2_81_{role}",
                "source_n_repair_instruction": "Render a visible product surface with public-facing hierarchy.",
                "source_run2_79_page": {"art_direction_scene": f"{role} art direction scene"},
                "renderer_repair_directives_applied": directives,
                "concrete_product_surface_visible": True,
                "product_surface_type": surface_by_role[role],
                "text_hierarchy": "headline_subhead_proof_caption",
                "text_composition_blocks_applied": [
                    "headline_block",
                    "subhead_block",
                    "proof_sentence",
                    "object_caption",
                ],
                "floating_label_count": 0,
                "label_count": 2,
                "min_visible_label_font_size": 12,
                "canvas_word_count": 28,
                "source_trace_terms_visible_on_canvas": [],
                "public_polish_claimed": False,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "renderer_product_surface_text_composition_checks": {
            "pages_with_o1_text_composition_consumed": 6,
            "pages_with_concrete_product_surface": 6,
            "pages_with_text_hierarchy_applied": 6,
            "pages_with_floating_labels_removed": 6,
            "pages_with_traceability_routed_off_canvas": 6,
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_p_visual_quality_evaluation_for_run2_82",
    }


def valid_run2_83_workflow_taxonomy_bias_audit() -> dict:
    consumed_sources = [
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
    ]
    preserved_gates = [
        "traceability",
        "source_availability",
        "validator_required_files",
        "public_release_block",
        "negative_controls",
        "viewer_metadata_routes",
        "reproducible_scripts",
    ]
    missing_taxonomy = [
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
    layer_ids = [
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
    ]
    return {
        "artifact_id": "run2_83_workflow_taxonomy_bias_audit",
        "part": "Part P0",
        "schema_version": "ppt_run2_83_workflow_taxonomy_bias_audit.v1",
        "run_id": "2.83",
        "status": "run2_83_workflow_taxonomy_bias_audit_ready_public_blocked",
        "stage_policy": "part_p0_audit_only_no_renderer_rerun_no_viewer_update_no_public_release",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "workflow_taxonomy_bias_audit_only_no_visual_quality_pass_no_public_release",
        "consumed_sources": consumed_sources,
        "source_inputs": [
            {"path": source, "available": True, "usage": "workflow_taxonomy_bias_source"}
            for source in consumed_sources
        ],
        "engineering_rigor_preservation": {
            "preserve_existing_gates": preserved_gates,
            "do_not_weaken_traceability": True,
            "public_release_gate_remains_blocked": True,
            "design_layer_adds_to_engineering_layer": True,
        },
        "taxonomy_bias_summary": {
            "primary_bias": "engineering_constraint_labels_over_design_motif_labels",
            "root_cause": "design_motif_taxonomy_missing_between_tutorial_memory_and_renderer_adapter",
            "required_correction": "add design_motif_layer without weakening traceability or release gates",
        },
        "layer_bias_records": [
            {
                "layer_id": layer_id,
                "layer_name": layer_id.replace("_", " "),
                "engineering_strength": "keeps traceable reproducible contracts",
                "design_signal_loss": "motif and style intent are not first class fields",
                "bias_direction": "engineering_gate_dominant",
                "evidence": ["fixture evidence"],
                "impact_on_ppt": "slides become clear but schematic",
                "must_preserve": "source trace and public blocked gate",
                "needs_new_design_layer": True,
            }
            for layer_id in layer_ids
        ],
        "run2_series_pattern": [
            {
                "stage_range": stage_range,
                "dominant_work": dominant_work,
                "effect_on_ppt": "increased rigor while design motif fidelity stayed under-specified",
            }
            for stage_range, dominant_work in [
                ("2.7-2.18", "evidence and workflow thickening"),
                ("2.24-2.42", "content and visual asset enrichment"),
                ("2.43-2.64", "typography, readability, and socket gates"),
                ("2.73-2.82", "validated A-F contracts and renderer repair loops"),
            ]
        ],
        "missing_design_taxonomy": [
            {
                "field": field,
                "why_needed": "turn tutorial observation into reusable design intent",
                "renderer_contract_implication": "renderer must preserve motif and style fidelity, not only gates",
            }
            for field in missing_taxonomy
        ],
        "required_next_layer": {
            "layer_id": "design_motif_layer",
            "must_add_fields": missing_taxonomy,
            "must_preserve_engineering_gates": True,
            "must_not_replace_validator": True,
        },
        "no_new_renderer_proof": {
            "new_ppt_created": False,
            "new_html_created": False,
            "viewer_updated": False,
        },
        "next_required_action": "part_p1_design_motif_taxonomy_and_style_router_plan",
    }


def valid_run2_84_design_motif_taxonomy_style_router_plan() -> dict:
    consumed_sources = [
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
    motif_families = [
        "editorial_text_field",
        "modular_matrix",
        "overlay_sticker_stack",
        "product_theater",
        "before_after_theater",
        "evidence_workspace",
        "decision_map",
    ]
    style_families = [
        "public_product_keynote",
        "technical_editorial",
        "dense_teaching_walkthrough",
        "financial_decision_brief",
        "high_contrast_demo",
    ]
    scenarios = [
        "product_pitch",
        "teaching_tutorial",
        "financial_product",
        "technical_proof",
        "public_video_demo",
    ]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    primary_by_role = {
        "cover": "motif_2_84_product_theater",
        "setup": "motif_2_84_editorial_text_field",
        "contrast": "motif_2_84_before_after_theater",
        "proof": "motif_2_84_modular_matrix",
        "climax": "motif_2_84_overlay_sticker_stack",
        "close": "motif_2_84_decision_map",
    }

    def motif(family: str, index: int) -> dict:
        return {
            "motif_id": f"motif_2_84_{family}",
            "motif_family": family,
            "layout_recipe": {
                "composition_pattern": f"{family} composition pattern",
                "reading_path": "headline_to_object_to_evidence_to_caption",
                "focal_object_strategy": "single dominant object with supporting layers",
            },
            "spatial_relation": {
                "text_to_object_relation": "anchored_to_visible_product_or_evidence_object",
                "object_to_background_relation": "foreground_surface_over_supporting_field",
                "evidence_relation": "attached_rail_or_matrix_cell",
            },
            "typography_treatment": {
                "hierarchy_model": "headline_subhead_proof_caption",
                "paragraph_behavior": "editorial_block_not_floating_label",
                "caption_behavior": "attached_to_object_edge",
            },
            "visual_density": ["balanced", "dense", "climax", "sparse"][index % 4],
            "style_family": style_families[index % len(style_families)],
            "scenario_fit": [scenarios[index % len(scenarios)], scenarios[(index + 1) % len(scenarios)]],
            "renderer_recipe": {
                "native_ppt_primitives": ["editable text", "native shape", "image placeholder"],
                "forbidden_renderer_shortcuts": ["generic rectangles only", "traceability labels on canvas"],
                "metadata_routes": ["source trace", "motif id", "fidelity checks"],
            },
            "motif_fidelity_checks": [
                "motif_family_visible",
                "not_rectangle_only",
                "text_integrated_with_shape",
            ],
            "source_trace": ["run2_73_tutorial_to_design_moves.json"],
        }

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
        "consumed_sources": consumed_sources,
        "source_inputs": [
            {"path": source, "available": True, "usage": "design_motif_style_router_source"}
            for source in consumed_sources
        ],
        "source_p0_audit": {
            "status": "run2_83_workflow_taxonomy_bias_audit_ready_public_blocked",
            "next_required_action": "part_p1_design_motif_taxonomy_and_style_router_plan",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_83_workflow_taxonomy_bias_audit.json",
        },
        "preserved_visual_effects": [
            "modular_matrix",
            "rectangle_layering",
            "overlay_sticker_stack",
            "product_theater",
            "editorial_text_density",
        ],
        "design_motif_taxonomy": [motif(family, index) for index, family in enumerate(motif_families)],
        "style_router_rules": [
            {
                "scenario": scenario,
                "primary_style_family": style_families[index % len(style_families)],
                "allowed_motif_families": motif_families[:3],
                "density_policy": "choose density by audience and proof burden",
                "business_fit_rationale": "scenario maps design motif to commercial communication job",
            }
            for index, scenario in enumerate(scenarios)
        ],
        "page_role_motif_bindings": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "primary_motif_id": primary_by_role[role],
                "fallback_motif_id": "motif_2_84_editorial_text_field",
                "style_family": style_families[(index - 1) % len(style_families)],
                "scenario": scenarios[(index - 1) % len(scenarios)],
                "required_motif_fidelity_checks": [
                    "motif_family_visible",
                    "not_rectangle_only",
                    "text_integrated_with_shape",
                ],
            }
            for index, role in enumerate(["cover", "setup", "contrast", "proof", "climax", "close"], start=1)
        ],
        "engineering_gate_bridge": {
            "preserve_existing_gates": [
                "traceability",
                "source_availability",
                "validator_required_files",
                "public_release_block",
                "negative_controls",
                "viewer_metadata_routes",
                "reproducible_scripts",
            ],
            "traceability_route": "viewer_metadata_and_speaker_notes",
            "slide_canvas_traceability_allowed": False,
            "public_release_gate_remains_blocked": True,
            "validator_remains_authoritative": True,
        },
        "renderer_contract_preview": {
            "next_renderer_must_consume_p1": True,
            "required_fields_for_next_rerun": [
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
            ],
            "does_not_execute_renderer": True,
        },
        "no_new_renderer_proof": {
            "new_ppt_created": False,
            "new_html_created": False,
            "viewer_updated": False,
        },
        "next_required_action": "part_p2_renderer_rerun_from_design_motif_layer_and_style_router",
    }


def valid_run2_85_design_motif_renderer_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    motif_by_role = {
        "cover": ("motif_2_84_product_theater", "product_theater", "balanced"),
        "setup": ("motif_2_84_editorial_text_field", "editorial_text_field", "dense"),
        "contrast": ("motif_2_84_before_after_theater", "before_after_theater", "balanced"),
        "proof": ("motif_2_84_modular_matrix", "modular_matrix", "dense"),
        "climax": ("motif_2_84_overlay_sticker_stack", "overlay_sticker_stack", "climax"),
        "close": ("motif_2_84_decision_map", "decision_map", "sparse"),
    }
    style_by_role = {
        "cover": "public_product_keynote",
        "setup": "technical_editorial",
        "contrast": "dense_teaching_walkthrough",
        "proof": "financial_decision_brief",
        "climax": "high_contrast_demo",
        "close": "public_product_keynote",
    }
    scenario_by_role = {
        "cover": "product_pitch",
        "setup": "teaching_tutorial",
        "contrast": "financial_product",
        "proof": "technical_proof",
        "climax": "public_video_demo",
        "close": "product_pitch",
    }
    surface_by_role = {
        "cover": "editable_ppt_product_mock",
        "setup": "source_to_memory_product_flow",
        "contrast": "before_after_product_theater",
        "proof": "evidence_product_workspace",
        "climax": "editable_ppt_product_mock",
        "close": "release_decision_product_map",
    }
    consumed_sources = [
        "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json",
        "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
    ]
    directives = [
        "p1_design_motif_layer_consumed",
        "style_router_applied",
        "motif_family_rendered",
        "preserved_visual_effects_rendered",
        "text_integrated_with_motif",
        "traceability_routed_off_canvas",
        "public_polish_not_claimed",
    ]
    preserved = [
        "modular_matrix",
        "rectangle_layering",
        "overlay_sticker_stack",
        "product_theater",
        "editorial_text_density",
    ]
    fidelity = [
        "motif_family_visible",
        "not_rectangle_only",
        "text_integrated_with_shape",
    ]
    return {
        "artifact_id": "run2_85_design_motif_renderer_rerun_result",
        "part": "Part P2",
        "schema_version": "ppt_run2_85_design_motif_renderer_rerun_result.v1",
        "run_id": "2.85",
        "status": "run2_85_design_motif_renderer_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "design_motif_renderer_generated_viewer_check_only_no_part_q_quality_verdict",
        "consumed_sources": consumed_sources,
        "source_p1_design_motif_plan": {
            "status": "run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked",
            "next_required_action": "part_p2_renderer_rerun_from_design_motif_layer_and_style_router",
            "source_result": "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json",
        },
        "source_o2_renderer_result": {
            "status": "run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked",
            "next_required_action": "part_p_visual_quality_evaluation_for_run2_82",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
        },
        "renderer_design_motif_manifest": {
            "generator": "scripts/generate_ppt_run2_85_design_motif_renderer_arms.mjs",
            "consumed_sources": consumed_sources,
            "arms": [
                "prompt_only",
                "run1_5_skill",
                "run2_85_full_design_motif_style_router",
                "bad_run2_85_without_design_motif_layer",
            ],
            "best_internal_arm": "run2_85_full_design_motif_style_router",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-85-full-vulca/output/run2-85-design-motif-renderer.html",
                "pptx": "outputs/thread/presentations/ppt-run2-85-full-vulca/output/ppt-run2-85-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
                "four_arm_contact_sheet": "outputs/thread/presentations/run2-85-four-arm-contact-sheet.png",
            },
            "viewer_update": {
                "latest_run_id": "2.85",
                "viewer_can_reference_new_run": True,
            },
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "source_p1_primary_motif_id": motif_by_role[role][0],
                "source_p1_fallback_motif_id": "motif_2_84_editorial_text_field",
                "source_o2_product_surface_type": surface_by_role[role],
                "motif_family": motif_by_role[role][1],
                "style_family": style_by_role[role],
                "scenario": scenario_by_role[role],
                "visual_density": motif_by_role[role][2],
                "renderer_repair_directives_applied": directives,
                "preserved_visual_effects_rendered": preserved,
                "motif_fidelity_checks": fidelity,
                "motif_family_visible": True,
                "not_rectangle_only": True,
                "text_integrated_with_shape": True,
                "concrete_product_surface_visible": True,
                "text_hierarchy": "motif_aware_headline_subhead_proof_caption",
                "floating_label_count": 0,
                "label_count": 2,
                "min_visible_label_font_size": 12,
                "source_trace_terms_visible_on_canvas": [],
                "public_polish_claimed": False,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "renderer_design_motif_checks": {
            "pages_with_p1_motif_consumed": 6,
            "pages_with_motif_family_visible": 6,
            "pages_with_not_rectangle_only": 6,
            "pages_with_text_integrated_with_shape": 6,
            "pages_with_traceability_routed_off_canvas": 6,
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_q_visual_quality_evaluation_for_run2_85",
    }


def valid_run2_86_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    motif_by_role = {
        "cover": "product_theater",
        "setup": "editorial_text_field",
        "contrast": "before_after_theater",
        "proof": "modular_matrix",
        "climax": "overlay_sticker_stack",
        "close": "decision_map",
    }
    questions = {
        "is_2_85_better_than_2_82": "partial_motif_trace_up_visual_delta_small_public_blocked",
        "did_2_85_restore_design_motif_visual_language": "partial_motif_metadata_visible_but_renderer_primitives_still_simple",
        "did_2_85_keep_text_heavy_layout_readability": "partial_text_hierarchy_present_but_composition_still_rigid",
        "did_2_85_preserve_modular_matrix_and_sticker_effects": "partial_effects_declared_and_some_visible_but_not_high_fidelity",
        "does_2_85_explain_why_late_2_series_lost_aesthetic": "yes_engineering_gates_and_contracts_overweighted_renderer_conservatism",
        "does_2_85_reach_public_video_presentation_direction": "no_public_blocked",
        "which_layer_needs_next_repair": "renderer_visual_primitive_and_composition_engine",
    }
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
            "run2_85_result": "docs/product/ppt-run2-data-skill-quality/results/run2_85_design_motif_renderer_rerun_result.json",
            "run2_84_p1_design_motif_plan": "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json",
            "run2_82_result": "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
            "run2_82_full_contact_sheet": "outputs/thread/presentations/ppt-run2-82-full-vulca/preview/contact-sheet.png",
            "run2_85_full_contact_sheet": "outputs/thread/presentations/ppt-run2-85-full-vulca/preview/contact-sheet.png",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "viewer_latest_run_id": "2.85",
            "viewer_can_compare_2_82_and_2_85": True,
            "run2_82_full_preview_count": 6,
            "run2_85_full_preview_count": 6,
            "browser_check_required_for_handoff": True,
        },
        "gemini_agent_review_summary": {
            "tool": "mcp__gemini_agent.gemini_artifact_review",
            "model": "gemini-3.5-flash",
            "review_count": 1,
            "used_for_verdict": True,
            "run2_85_findings": [
                "slide 05 colored borders improve scannability",
                "slide 04 modular matrix structure is clearer",
                "text-heavy layout still rigid",
            ],
            "run2_85_risks": [
                "renderer primitive ceiling",
                "composition engine still conservative",
                "layout collision avoidance still weak",
            ],
        },
        "evaluation_questions": {
            question_id: {"answer": answer, "basis": "fixture basis"}
            for question_id, answer in questions.items()
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
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "delta_vs_2_82": "partial",
                "motif_realization": "partial",
                "layout_distinctiveness": "partial",
                "text_composition": "rigid",
                "public_video_direction": "no",
                "root_cause_layer": "renderer_visual_primitives",
                "repair_required": True,
                "visual_observation": "motif is traceable but still rendered with simple primitives",
                "next_repair_instruction": "recover best historical layout and add richer native visual primitive",
                "trace_support": {
                    "motif_family": motif_by_role[role],
                    "style_family": "public_product_keynote",
                    "scenario": "product_pitch",
                    "source_p1_primary_motif_id": f"motif_2_84_{motif_by_role[role]}",
                    "label_count": 2,
                    "not_rectangle_only": True,
                    "text_integrated_with_shape": True,
                    "preserved_visual_effects_rendered": ["modular_matrix", "overlay_sticker_stack"],
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "renderer_visual_primitive_and_composition_engine",
            "secondary_layers": ["design_motif_binding", "text_composition"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": (
                "engineering_traceability_and_contract_layers_became_stronger_than_visual_execution_primitives"
            ),
            "rationale": "P1/P2 consumed the motif layer, but contact-sheet delta remains incremental.",
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_r_best_layout_recovery_and_visual_primitive_plan_from_q_evaluation",
    }


def valid_run2_87_best_layout_recovery_visual_primitive_plan() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    motif_by_role = {
        "cover": "product_theater",
        "setup": "editorial_text_field",
        "contrast": "before_after_theater",
        "proof": "modular_matrix",
        "climax": "overlay_sticker_stack",
        "close": "decision_map",
    }
    primitive_by_role = {
        "cover": "primitive_2_87_product_theater_surface",
        "setup": "primitive_2_87_editorial_text_field",
        "contrast": "primitive_2_87_before_after_surface",
        "proof": "primitive_2_87_modular_matrix_workspace",
        "climax": "primitive_2_87_overlay_sticker_stack",
        "close": "primitive_2_87_decision_map_board",
    }
    function_by_primitive = {
        "primitive_2_87_product_theater_surface": "drawRun287ProductTheaterSurface",
        "primitive_2_87_editorial_text_field": "drawRun287EditorialTextField",
        "primitive_2_87_before_after_surface": "drawRun287BeforeAfterSurface",
        "primitive_2_87_modular_matrix_workspace": "drawRun287ModularMatrixWorkspace",
        "primitive_2_87_overlay_sticker_stack": "drawRun287OverlayStickerStack",
        "primitive_2_87_decision_map_board": "drawRun287DecisionMapBoard",
    }
    return {
        "artifact_id": "run2_87_best_layout_recovery_visual_primitive_plan",
        "part": "Part R",
        "schema_version": "ppt_run2_87_best_layout_recovery_visual_primitive_plan.v1",
        "run_id": "2.87",
        "status": "run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked",
        "stage_policy": "part_r_plan_only_best_layout_recovery_visual_primitive_contract_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_r_plan_only_no_renderer_rerun_no_public_release",
        "consumed_sources": [
            "docs/product/ppt-run2-data-skill-quality/results/run2_86_visual_quality_evaluation.json",
            "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json",
            "docs/product/ppt-run2-data-skill-quality/run2_9_visual_primitive_repair.json",
            "docs/product/ppt-run2-data-skill-quality/run2_9_executable_visual_modules.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_10_visual_system_rerun_result.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_16_selector_rerun_result.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_67_reference_first_rerun_result.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_68_targeted_debug_rerun_result.json",
        ],
        "source_q_evaluation": {
            "status": "run2_86_visual_quality_evaluation_public_blocked",
            "next_required_action": "part_r_best_layout_recovery_and_visual_primitive_plan_from_q_evaluation",
            "top_blocker": "renderer_visual_primitives_are_too_simple_to_realize_design_motifs",
            "primary_layer": "renderer_visual_primitive_and_composition_engine",
        },
        "historical_recovery_scope": {
            "candidate_runs": ["2.9", "2.10", "2.16", "2.67", "2.68"],
            "source_primitive_ids": [
                "primitive_2_9_editorial_spread_composition",
                "primitive_2_9_product_surface_depth",
                "primitive_2_9_motion_storyboard_sequence",
                "primitive_2_9_climax_stage_composition",
                "primitive_2_9_typographic_field_composition",
            ],
            "recovery_principle": "recover best historical layout before drawing new motif primitive",
        },
        "page_layout_recovery_records": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "motif_family": motif_by_role[role],
                "source_q_root_cause_layer": "renderer_visual_primitives",
                "source_q_repair_instruction": "recover best historical layout and add richer native visual primitive",
                "historical_layout_sources": ["2.10", "2.16", "2.67"],
                "recovered_layout_pattern": "historical best layout recovery",
                "renderer_primitive_id": primitive_by_role[role],
                "composition_engine_obligation": {
                    "recover_best_historical_layout": True,
                    "preserve_text_heavy_readability": True,
                    "avoid_generic_box_layout": True,
                },
                "forbidden_patterns": [
                    "floating labels",
                    "traceability labels on slide canvas",
                    "generic rectangles only",
                ],
            }
            for index, role in enumerate(roles, start=1)
        ],
        "visual_primitive_contracts": [
            {
                "primitive_id": primitive_id,
                "motif_family": primitive_id.removeprefix("primitive_2_87_"),
                "renderer_function_name": function_name,
                "native_ppt_elements": ["editable text", "native shape group", "connector", "depth layer"],
                "composition_rules": ["recover source layout", "bind text to object", "vary primitive geometry"],
                "anti_regression_gates": [
                    "not_rectangle_only",
                    "text_integrated_with_shape",
                    "collision_avoidance",
                    "motif_fidelity_visible",
                ],
                "forbidden_shortcuts": ["generic rectangles only", "floating trace labels"],
            }
            for primitive_id, function_name in function_by_primitive.items()
        ],
        "composition_engine_repair_plan": {
            "layout_selection_order": [
                "historical_best_layout_recovery",
                "run2_67_reference_first_archetype",
                "run2_10_visual_system_module",
                "run2_84_design_motif_router",
            ],
            "collision_policy": {"reject_visible_text_overlap": True},
            "traceability_policy": {"slide_canvas_traceability_allowed": False},
            "text_density_policy": {"text_heavy_layout_allowed": True},
        },
        "next_renderer_contract": {
            "next_run_id": "2.88",
            "next_renderer_script": "scripts/generate_ppt_run2_88_best_layout_visual_primitive_arms.mjs",
            "must_consume_part_r": True,
            "public_quality_verdict_deferred": True,
            "arms": [
                "prompt_only",
                "run1_5_skill",
                "run2_88_full_best_layout_visual_primitives",
                "bad_without_best_layout_visual_primitives",
            ],
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan",
    }


def valid_run2_88_best_layout_visual_primitive_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    primitive_by_role = {
        "cover": "primitive_2_87_product_theater_surface",
        "setup": "primitive_2_87_editorial_text_field",
        "contrast": "primitive_2_87_before_after_surface",
        "proof": "primitive_2_87_modular_matrix_workspace",
        "climax": "primitive_2_87_overlay_sticker_stack",
        "close": "primitive_2_87_decision_map_board",
    }
    function_by_role = {
        "cover": "drawRun287ProductTheaterSurface",
        "setup": "drawRun287EditorialTextField",
        "contrast": "drawRun287BeforeAfterSurface",
        "proof": "drawRun287ModularMatrixWorkspace",
        "climax": "drawRun287OverlayStickerStack",
        "close": "drawRun287DecisionMapBoard",
    }
    directives = [
        "part_r_best_layout_plan_consumed",
        "historical_best_layout_recovered",
        "run2_87_visual_primitive_rendered",
        "composition_engine_repair_applied",
        "text_heavy_readability_preserved",
        "traceability_routed_off_canvas",
        "public_polish_not_claimed",
    ]
    gates = ["not_rectangle_only", "text_integrated_with_shape", "collision_avoidance", "motif_fidelity_visible"]
    return {
        "artifact_id": "run2_88_best_layout_visual_primitive_rerun_result",
        "part": "Part S",
        "schema_version": "ppt_run2_88_best_layout_visual_primitive_rerun_result.v1",
        "run_id": "2.88",
        "status": "run2_88_best_layout_visual_primitive_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "best_layout_visual_primitive_renderer_generated_viewer_check_only_no_quality_verdict",
        "consumed_sources": [
            "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_85_design_motif_renderer_rerun_result.json",
        ],
        "source_part_r_plan": {
            "status": "run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked",
            "next_required_action": "part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan",
            "source_result": "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
        },
        "source_run2_85_renderer_result": {
            "status": "run2_85_design_motif_renderer_rerun_generated_public_blocked",
            "next_required_action": "part_q_visual_quality_evaluation_for_run2_85",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_85_design_motif_renderer_rerun_result.json",
        },
        "renderer_best_layout_visual_primitive_manifest": {
            "generator": "scripts/generate_ppt_run2_88_best_layout_visual_primitive_arms.mjs",
            "consumed_sources": [
                "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
                "docs/product/ppt-run2-data-skill-quality/results/run2_85_design_motif_renderer_rerun_result.json",
            ],
            "arms": ["prompt_only", "run1_5_skill", "run2_88_full_best_layout_visual_primitives", "bad_without_best_layout_visual_primitives"],
            "best_internal_arm": "run2_88_full_best_layout_visual_primitives",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-88-full-vulca/output/run2-88-best-layout-visual-primitives.html",
                "pptx": "outputs/thread/presentations/ppt-run2-88-full-vulca/output/ppt-run2-88-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
                "four_arm_contact_sheet": "outputs/thread/presentations/run2-88-four-arm-contact-sheet.png",
            },
            "viewer_update": {"latest_run_id": "2.88", "viewer_can_reference_new_run": True},
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "renderer_primitive_id": primitive_by_role[role],
                "renderer_function_name": function_by_role[role],
                "renderer_repair_directives_applied": directives,
                "anti_regression_gates": gates,
                "historical_layout_recovered": True,
                "not_rectangle_only": True,
                "text_integrated_with_shape": True,
                "collision_avoidance_passed": True,
                "traceability_on_canvas": False,
                "floating_label_count": 0,
                "label_count": 2,
                "min_visible_label_font_size": 12,
                "public_polish_claimed": False,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "renderer_best_layout_visual_primitive_checks": {
            "pages_with_part_r_consumed": 6,
            "pages_with_historical_layout_recovered": 6,
            "pages_with_visual_primitive_rendered": 6,
            "pages_with_collision_avoidance": 6,
            "pages_with_traceability_routed_off_canvas": 6,
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_t_visual_quality_evaluation_for_run2_88",
    }


def valid_run2_89_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    primitive_by_role = {
        "cover": "primitive_2_87_product_theater_surface",
        "setup": "primitive_2_87_editorial_text_field",
        "contrast": "primitive_2_87_before_after_surface",
        "proof": "primitive_2_87_modular_matrix_workspace",
        "climax": "primitive_2_87_overlay_sticker_stack",
        "close": "primitive_2_87_decision_map_board",
    }
    function_by_role = {
        "cover": "drawRun287ProductTheaterSurface",
        "setup": "drawRun287EditorialTextField",
        "contrast": "drawRun287BeforeAfterSurface",
        "proof": "drawRun287ModularMatrixWorkspace",
        "climax": "drawRun287OverlayStickerStack",
        "close": "drawRun287DecisionMapBoard",
    }
    questions = {
        "is_2_88_better_than_2_85": "partial_semantic_framing_up_visual_delta_small_public_blocked",
        "did_2_88_recover_best_layout_visual_primitives": "partial_primitives_named_but_layout_engine_positions_remain_similar",
        "did_2_88_keep_text_heavy_readability": "yes_text_hierarchy_readable_but_sparse_and_wireframe",
        "did_2_88_preserve_modular_matrix_and_sticker_effects": "partial_slide_04_05_preserved_but_not_high_fidelity",
        "does_2_88_fix_late_2_series_aesthetic_bottleneck": "no_visual_execution_still_wireframe_like",
        "does_2_88_reach_public_video_presentation_direction": "no_public_blocked",
        "which_layer_needs_next_repair": "renderer_asset_surface_and_composition_detail",
    }
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
            "run2_88_result": "docs/product/ppt-run2-data-skill-quality/results/run2_88_best_layout_visual_primitive_rerun_result.json",
            "run2_87_plan": "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
            "run2_85_result": "docs/product/ppt-run2-data-skill-quality/results/run2_85_design_motif_renderer_rerun_result.json",
            "run2_85_full_contact_sheet": "outputs/thread/presentations/ppt-run2-85-full-vulca/preview/contact-sheet.png",
            "run2_88_full_contact_sheet": "outputs/thread/presentations/ppt-run2-88-full-vulca/preview/contact-sheet.png",
            "run2_88_four_arm_contact_sheet": "outputs/thread/presentations/run2-88-four-arm-contact-sheet.png",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "viewer_latest_run_id": "2.88",
            "viewer_can_compare_2_85_and_2_88": True,
            "run2_85_full_preview_count": 6,
            "run2_88_full_preview_count": 6,
            "run2_88_arm_count": 4,
            "browser_check_required_for_handoff": True,
        },
        "gemini_agent_review_summary": {
            "tool": "gemini-agent artifact-review",
            "model": "gemini-3.5-flash",
            "review_count": 1,
            "used_for_verdict": True,
            "run2_88_findings": [
                "layout templates are structurally identical",
                "terminology and conceptual framing changed",
                "slide 04 and 05 preserve matrix and sticker hints",
            ],
            "run2_88_risks": [
                "slides remain wireframe-like",
                "Slide 06 has a text collision near review",
                "abstract boxes still do not read as public product surfaces",
            ],
        },
        "evaluation_questions": {
            question_id: {"answer": answer, "basis": "fixture basis"}
            for question_id, answer in questions.items()
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
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "delta_vs_2_85": "partial",
                "best_layout_recovery": "partial",
                "visual_primitive_fidelity": "partial",
                "text_composition": "rigid",
                "public_video_direction": "no",
                "root_cause_layer": "renderer_asset_surface",
                "repair_required": True,
                "visual_observation": "2.88 changes primitive framing but still reads as wireframe composition",
                "next_repair_instruction": "replace abstract labeled boxes with richer asset surface and composition detail",
                "trace_support": {
                    "renderer_primitive_id": primitive_by_role[role],
                    "renderer_function_name": function_by_role[role],
                    "label_count": 2,
                    "not_rectangle_only": True,
                    "text_integrated_with_shape": True,
                    "collision_or_overlap_risk": role == "close",
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "renderer_asset_surface_and_composition_detail",
            "secondary_layers": ["visual_primitive_fidelity", "layout_engine_reuse", "text_composition"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": "semantic_contracts_and_primitive_names_changed_faster_than_visible_composition",
            "rationale": "2.88 consumes Part R but the visible contact-sheet structure remains close to 2.85.",
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_u_renderer_asset_surface_composition_repair_from_t_evaluation",
    }


def valid_run2_90_renderer_asset_surface_composition_rerun_result() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    function_by_role = {
        "cover": "drawRun290ProductSurfaceHero",
        "setup": "drawRun290EditorialSurfaceSpread",
        "contrast": "drawRun290BeforeAfterProductStage",
        "proof": "drawRun290EvidenceMatrixSurface",
        "climax": "drawRun290StickerStageSurface",
        "close": "drawRun290DecisionBoardSurface",
    }
    directives = [
        "part_t_visual_quality_evaluation_consumed",
        "asset_surface_rendered",
        "composition_detail_added",
        "wireframe_reduced",
        "collision_repair_applied",
        "text_heavy_readability_preserved",
        "traceability_routed_off_canvas",
        "public_polish_not_claimed",
    ]
    gates = [
        "product_surface_materiality",
        "visual_density_above_wireframe",
        "no_floating_labels",
        "collision_avoidance",
        "text_integrated_with_surface",
    ]
    return {
        "artifact_id": "run2_90_renderer_asset_surface_composition_rerun_result",
        "part": "Part U",
        "schema_version": "ppt_run2_90_renderer_asset_surface_composition_rerun_result.v1",
        "run_id": "2.90",
        "status": "run2_90_renderer_asset_surface_composition_rerun_generated_public_blocked",
        "public_ready": False,
        "public_release_started": False,
        "quality_claim_boundary": "asset_surface_composition_renderer_generated_viewer_check_only_no_quality_verdict",
        "consumed_sources": [
            "docs/product/ppt-run2-data-skill-quality/results/run2_89_visual_quality_evaluation.json",
            "docs/product/ppt-run2-data-skill-quality/results/run2_88_best_layout_visual_primitive_rerun_result.json",
            "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
        ],
        "source_t_evaluation": {
            "status": "run2_89_visual_quality_evaluation_public_blocked",
            "next_required_action": "part_u_renderer_asset_surface_composition_repair_from_t_evaluation",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_89_visual_quality_evaluation.json",
            "top_blocker": "layout_primitive_names_changed_but_visual_execution_remains_wireframe_like",
            "next_layer_to_fix": "renderer_asset_surface_and_composition_detail",
        },
        "source_run2_88_renderer_result": {
            "status": "run2_88_best_layout_visual_primitive_rerun_generated_public_blocked",
            "next_required_action": "part_t_visual_quality_evaluation_for_run2_88",
            "source_result": "docs/product/ppt-run2-data-skill-quality/results/run2_88_best_layout_visual_primitive_rerun_result.json",
        },
        "source_run2_87_plan": {
            "status": "run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked",
            "next_required_action": "part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan",
            "source_result": "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
        },
        "renderer_asset_surface_composition_manifest": {
            "generator": "scripts/generate_ppt_run2_90_renderer_asset_surface_composition_arms.mjs",
            "consumed_sources": [
                "docs/product/ppt-run2-data-skill-quality/results/run2_89_visual_quality_evaluation.json",
                "docs/product/ppt-run2-data-skill-quality/results/run2_88_best_layout_visual_primitive_rerun_result.json",
                "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
            ],
            "arms": ["prompt_only", "run1_5_skill", "run2_90_full_asset_surface_composition", "bad_without_asset_surface_composition"],
            "best_internal_arm": "run2_90_full_asset_surface_composition",
            "outputs": {
                "html_viewer": "outputs/thread/presentations/ppt-run2-90-full-vulca/output/run2-90-asset-surface-composition.html",
                "pptx": "outputs/thread/presentations/ppt-run2-90-full-vulca/output/ppt-run2-90-full-vulca.pptx",
                "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
                "four_arm_contact_sheet": "outputs/thread/presentations/run2-90-four-arm-contact-sheet.png",
            },
            "viewer_update": {"latest_run_id": "2.90", "viewer_can_reference_new_run": True},
        },
        "rendered_pages": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "source_t_root_cause_layer": "renderer_asset_surface",
                "asset_surface_composition_id": f"asset_surface_composition_2_90_{role}",
                "renderer_function_name": function_by_role[role],
                "renderer_repair_directives_applied": directives,
                "anti_regression_gates": gates,
                "asset_surface_rendered": True,
                "composition_detail_added": True,
                "wireframe_like": False,
                "collision_avoidance_passed": True,
                "traceability_on_canvas": False,
                "floating_label_count": 0,
                "label_count": 2,
                "min_visible_label_font_size": 12,
                "surface_detail_count": 10,
                "filled_surface_count": 5,
                "mock_asset_count": 2,
                "public_polish_claimed": False,
            }
            for index, role in enumerate(roles, start=1)
        ],
        "renderer_asset_surface_composition_checks": {
            "pages_with_t_evaluation_consumed": 6,
            "pages_with_asset_surface_rendered": 6,
            "pages_with_composition_detail_added": 6,
            "pages_with_wireframe_reduction": 6,
            "pages_with_collision_avoidance": 6,
            "pages_with_traceability_routed_off_canvas": 6,
            "public_quality_verdict_started": False,
        },
        "next_required_action": "part_v_visual_quality_evaluation_for_run2_90",
    }


def valid_run2_91_visual_quality_evaluation() -> dict:
    roles = ["cover", "setup", "contrast", "proof", "climax", "close"]
    module_by_role = {
        "cover": "product_reveal",
        "setup": "hero_field",
        "contrast": "before_after_theater",
        "proof": "evidence_workspace",
        "climax": "product_reveal",
        "close": "decision_map",
    }
    root_layers = {
        "cover": "object_bound_typography",
        "setup": "text_visual_integration",
        "contrast": "caption_anchor_binding",
        "proof": "proof_object_embedding",
        "climax": "composition_rhythm",
        "close": "object_bound_typography",
    }
    function_by_role = {
        "cover": "drawRun290ProductSurfaceHero",
        "setup": "drawRun290EditorialSurfaceSpread",
        "contrast": "drawRun290BeforeAfterProductStage",
        "proof": "drawRun290EvidenceMatrixSurface",
        "climax": "drawRun290StickerStageSurface",
        "close": "drawRun290DecisionBoardSurface",
    }
    questions = {
        "is_2_90_better_than_2_88": "yes_asset_surface_visibility_up_public_still_blocked",
        "did_2_90_fix_wireframe_surface_visibility": "yes_major_wireframe_surface_reduction",
        "did_2_90_keep_text_heavy_readability": "yes_readable_but_split_from_visuals",
        "did_2_90_integrate_text_with_visual_objects": "no_text_visual_binding_still_weak",
        "does_2_90_reduce_debug_label_aesthetic": "partial_labels_reduced_but_annotation_feel_remains",
        "does_2_90_reach_public_video_presentation_direction": "no_public_blocked",
        "which_layer_needs_next_repair": "object_bound_typography_and_text_visual_integration",
    }
    return {
        "artifact_id": "run2_91_visual_quality_evaluation",
        "part": "Part V",
        "schema_version": "ppt_run2_91_visual_quality_evaluation.v1",
        "run_id": "2.91",
        "status": "run2_91_visual_quality_evaluation_public_blocked",
        "stage_policy": "evaluation_only_after_part_u_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_v_evaluation_only_no_public_release_no_renderer_rerun",
        "source_runs": {
            "comparison_baseline": "2.88",
            "evaluated_run": "2.90",
            "repair_source_run": "2.89",
            "prior_reference_run": "2.85",
        },
        "input_chain": {
            "run2_90_result": "docs/product/ppt-run2-data-skill-quality/results/run2_90_renderer_asset_surface_composition_rerun_result.json",
            "run2_89_t_evaluation": "docs/product/ppt-run2-data-skill-quality/results/run2_89_visual_quality_evaluation.json",
            "run2_88_result": "docs/product/ppt-run2-data-skill-quality/results/run2_88_best_layout_visual_primitive_rerun_result.json",
            "run2_88_full_contact_sheet": "outputs/thread/presentations/ppt-run2-88-full-vulca/preview/contact-sheet.png",
            "run2_90_full_contact_sheet": "outputs/thread/presentations/ppt-run2-90-full-vulca/preview/contact-sheet.png",
            "run2_90_four_arm_contact_sheet": "outputs/thread/presentations/run2-90-four-arm-contact-sheet.png",
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
        },
        "viewer_comparison_closure": {
            "ppt_run_viewer": "outputs/thread/presentations/ppt-run-viewer.html",
            "viewer_latest_run_id": "2.90",
            "viewer_can_compare_2_88_and_2_90": True,
            "run2_88_full_preview_count": 6,
            "run2_90_full_preview_count": 6,
            "run2_90_arm_count": 4,
            "browser_check_required_for_handoff": True,
        },
        "gemini_agent_review_summary": {
            "tool": "gemini-agent artifact-review",
            "model": "gemini-3.5-flash",
            "review_count": 1,
            "used_for_verdict": True,
            "run2_90_findings": ["surface visibility is up", "asset surface materiality is visible"],
            "run2_90_risks": ["text-visual integration remains split", "caption anchors still feel annotation-like"],
            "limitations": ["Static contact-sheet review only."],
        },
        "evaluation_questions": {
            question_id: {"answer": answer, "basis": "fixture basis"}
            for question_id, answer in questions.items()
        },
        "visual_quality_assessment": {
            "data_workflow_entry_gate": "pass_internal_only",
            "viewer_comparison_gate": "pass_internal_only",
            "design_quality_gate": "blocked",
            "public_video_readiness": "blocked",
            "global_delta_vs_2_88": "asset_surface_visibility_up_text_visual_integration_still_split",
            "top_blocker": "text_blocks_and_product_surfaces_remain_parallel_not_integrated",
            "next_layer_to_fix": "object_bound_typography_and_text_visual_integration",
        },
        "role_assessments": [
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": module_by_role[role],
                "asset_surface_delta": "strong" if role in {"cover", "climax"} else "partial",
                "text_visual_integration": "weak" if role in {"setup", "proof", "close"} else "partial",
                "caption_anchor_quality": "partial",
                "proof_embedding_quality": "weak" if role == "proof" else "partial",
                "public_video_direction": "partial" if role in {"cover", "climax"} else "no",
                "root_cause_layer": root_layers[role],
                "repair_required": True,
                "visual_observation": "Text and product surface remain parallel layers.",
                "next_repair_instruction": "Bind headline, proof sentence, and caption into the visible object structure.",
                "trace_support": {
                    "asset_surface_composition_id": f"asset_surface_composition_2_90_{role}",
                    "renderer_function_name": function_by_role[role],
                    "asset_surface_rendered": True,
                    "composition_detail_added": True,
                    "traceability_on_canvas": False,
                    "label_count": 2,
                },
            }
            for index, role in enumerate(roles, start=1)
        ],
        "root_cause_summary": {
            "primary_layer": "object_bound_typography_and_text_visual_integration",
            "secondary_layers": ["text_visual_integration", "caption_anchor_binding", "proof_object_embedding"],
            "not_primary_layer": "data_absence",
            "late_2_series_failure_mode": "surface_layer_fixed_before_text_visual_binding_layer",
            "rationale": "2.90 surfaces are visible, but text still sits beside objects instead of becoming part of them.",
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_w_renderer_text_visual_binding_repair_from_v_evaluation",
    }


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
    assert "missing required file: visual_repair_policy.json" in result.errors
    assert "missing required file: run2_8_tutorial_decomposition.json" in result.errors
    assert "missing required file: run2_8_executable_design_memory.json" in result.errors
    assert "missing required file: run2_8_workflow_gate_matrix.json" in result.errors
    assert "missing required file: results/trace_manifest_contract.json" in result.errors
    assert "missing required file: run2_73_visual_grammar_modules.json" in result.errors
    assert "missing required file: run2_73_renderer_adapter_contracts.json" in result.errors
    assert "missing required file: run2_73_text_binding_strategy.json" in result.errors
    assert "missing required file: results/run2_73_validated_scene_renderer_rerun_result.json" in result.errors
    assert "missing required file: results/run2_74_visual_quality_evaluation.json" in result.errors
    assert "missing required file: results/run2_75_renderer_repair_rerun_result.json" in result.errors
    assert "missing required file: results/run2_76_visual_quality_evaluation.json" in result.errors
    assert "missing required file: run2_76_visual_grammar_renderer_repair_plan.json" in result.errors
    assert "missing required file: results/run2_77_visual_grammar_renderer_repair_rerun_result.json" in result.errors
    assert "missing required file: results/run2_78_visual_quality_evaluation.json" in result.errors
    assert "missing required file: results/run2_79_renderer_art_direction_repair_rerun_result.json" in result.errors
    assert "missing required file: results/run2_80_visual_quality_evaluation.json" in result.errors
    assert "missing required file: run2_81_text_composition_typography_plan.json" in result.errors
    assert (
        "missing required file: results/run2_82_renderer_product_surface_text_composition_rerun_result.json"
        in result.errors
    )
    assert "missing required file: results/run2_83_workflow_taxonomy_bias_audit.json" in result.errors
    assert "missing required file: run2_84_design_motif_taxonomy_style_router_plan.json" in result.errors
    assert "missing required file: results/run2_85_design_motif_renderer_rerun_result.json" in result.errors
    assert "missing required file: results/run2_86_visual_quality_evaluation.json" in result.errors
    assert "missing required file: run2_87_best_layout_recovery_visual_primitive_plan.json" in result.errors
    assert "missing required file: results/run2_88_best_layout_visual_primitive_rerun_result.json" in result.errors
    assert "missing required file: results/run2_89_visual_quality_evaluation.json" in result.errors
    assert "missing required file: results/run2_90_renderer_asset_surface_composition_rerun_result.json" in result.errors
    assert "missing required file: results/run2_91_visual_quality_evaluation.json" in result.errors


def test_run2_profile_requires_visual_repair_policy_file(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    (pack / "visual_repair_policy.json").unlink()

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "missing required file: visual_repair_policy.json" in result.errors


def test_run2_profile_rejects_invalid_visual_repair_policy(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    policy_path = pack / "visual_repair_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["repairs"][0]["theme_delta"] = "Use a graphite editorial theme."
    policy["repairs"][1]["target_slide_roles"] = ["run3"]
    policy["repairs"][2]["native_ppt_requirements"] = ["native shapes only"]
    policy["repairs"][3]["qa_probe"] = "Review visual delta."
    policy["repairs"][4]["release_boundary"] = "public_ready_after_generation"
    policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "visual_repair_policy.repairs[0].theme_delta must mention forest-green" in result.errors
    assert "visual_repair_policy.repairs[0].theme_delta must mention source-brand" in result.errors
    assert (
        "visual_repair_policy.repairs[1].target_slide_roles[0] must be one of "
        "climax, close, contrast, cover, proof, setup"
    ) in result.errors
    assert "visual_repair_policy.repairs[2].native_ppt_requirements must mention editable" in result.errors
    assert "visual_repair_policy.repairs[3].qa_probe must mention contact sheet" in result.errors
    assert "visual_repair_policy.repairs[4].release_boundary must keep public_blocked status" in result.errors


def test_run2_profile_rejects_visual_grammar_renderer_release_scope(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    modules_path = pack / "run2_73_visual_grammar_modules.json"
    modules = json.loads(modules_path.read_text(encoding="utf-8"))
    modules["stage_policy"] = "part_e_visual_grammar_modules_and_renderer_rerun"
    modules["artifact_scope"]["does_not_start"].remove("renderer_rerun")
    modules["success_criteria_check"]["every_main_structure_serves_content"] = False
    modules_path.write_text(json.dumps(modules, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_73_visual_grammar_modules.stage_policy must be part_e_visual_grammar_modules_only_no_renderer_rerun_no_public_release"
        in result.errors
    )
    assert (
        "run2_73_visual_grammar_modules.artifact_scope.does_not_start must include renderer_rerun"
        in result.errors
    )
    assert (
        "run2_73_visual_grammar_modules.success_criteria_check.every_main_structure_serves_content must be true"
        in result.errors
    )


def test_run2_profile_rejects_visual_grammar_selection_rule_mismatch(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    modules_path = pack / "run2_73_visual_grammar_modules.json"
    modules = json.loads(modules_path.read_text(encoding="utf-8"))
    modules["module_selection_rules"][0]["select_module"] = "hero_field"
    modules["module_selection_rules"][0]["applies_to_page_types"] = ["cover"]
    modules_path.write_text(json.dumps(modules, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_73_visual_grammar_modules.module_selection_rules[0].applies_to_page_types[0] "
        "must select product_reveal for cover"
    ) in result.errors


def test_run2_profile_rejects_renderer_adapter_execution_scope(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    adapter_path = pack / "run2_73_renderer_adapter_contracts.json"
    adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
    adapter["stage_policy"] = "part_e2_renderer_adapter_and_renderer_rerun"
    adapter["artifact_scope"]["does_not_start"].remove("renderer_rerun")
    adapter["execution_guard"]["rendering_subprocesses_allowed"] = True
    adapter["adapter_scene_records"][0]["adapter_renderer_instructions"][
        "renderer_execution_allowed_in_this_artifact"
    ] = True
    adapter_path.write_text(json.dumps(adapter, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_73_renderer_adapter_contracts.stage_policy must be part_e2_renderer_adapter_contracts_only_no_renderer_rerun_no_public_release"
        in result.errors
    )
    assert (
        "run2_73_renderer_adapter_contracts.artifact_scope.does_not_start must include renderer_rerun"
        in result.errors
    )
    assert (
        "run2_73_renderer_adapter_contracts.execution_guard.rendering_subprocesses_allowed must be false"
        in result.errors
    )
    assert (
        "run2_73_renderer_adapter_contracts.adapter_scene_records[0].adapter_renderer_instructions.renderer_execution_allowed_in_this_artifact must be false"
        in result.errors
    )


def test_run2_profile_rejects_renderer_adapter_source_trace_mismatch(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    adapter_path = pack / "run2_73_renderer_adapter_contracts.json"
    adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
    adapter["source_inputs"] = [
        source
        for source in adapter["source_inputs"]
        if not source["path"].endswith("run2_73_scene_plan_expansion.json")
    ]
    adapter["adapter_scene_records"][0]["source_expansion_id"] = "scene_expansion_2_73_wrong"
    adapter["adapter_scene_records"][0]["visual_grammar_binding"]["module_id"] = "hero_field"
    adapter["traceability_summary"]["sources_consumed"].remove("run2_73_scene_plan_expansion.json")
    adapter_path.write_text(json.dumps(adapter, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_73_renderer_adapter_contracts.source_inputs missing path: docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json"
        in result.errors
    )
    assert (
        "run2_73_renderer_adapter_contracts.adapter_scene_records[0].source_expansion_id must match D2 scene expansion id for cover"
        in result.errors
    )
    assert (
        "run2_73_renderer_adapter_contracts.adapter_scene_records[0].visual_grammar_binding.module_id must match Part E module for cover"
        in result.errors
    )
    assert (
        "run2_73_renderer_adapter_contracts.traceability_summary.sources_consumed missing value: run2_73_scene_plan_expansion.json"
        in result.errors
    )


def test_run2_profile_rejects_text_binding_unbound_socket_and_renderer_scope(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    strategy_path = pack / "run2_73_text_binding_strategy.json"
    strategy = json.loads(strategy_path.read_text(encoding="utf-8"))
    strategy["stage_policy"] = "part_f_text_binding_strategy_and_renderer_rerun"
    strategy["artifact_scope"]["does_not_start"].remove("renderer_rerun")
    strategy["execution_guard"]["rendering_subprocesses_allowed"] = True
    strategy["global_forbidden_text_patterns"].remove("empty text box")
    first_record = strategy["page_text_binding_records"][0]
    first_record["text_socket_strategy"]["headline_socket"]["bound_source_id"] = "missing_visual_binding"
    first_record["text_socket_strategy"]["headline_socket"]["capacity"]["max_words"] = 0
    first_record["text_socket_strategy"]["headline_socket"]["bound_visual_object_type"] = "upper left"
    strategy_path.write_text(json.dumps(strategy, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_73_text_binding_strategy.stage_policy must be part_f_text_binding_strategy_only_no_renderer_rerun_no_public_release"
        in result.errors
    )
    assert (
        "run2_73_text_binding_strategy.artifact_scope.does_not_start must include renderer_rerun"
        in result.errors
    )
    assert (
        "run2_73_text_binding_strategy.execution_guard.rendering_subprocesses_allowed must be false"
        in result.errors
    )
    assert (
        "run2_73_text_binding_strategy.global_forbidden_text_patterns missing value: empty text box"
        in result.errors
    )
    assert (
        "run2_73_text_binding_strategy.page_text_binding_records[0].text_socket_strategy.headline_socket.bound_visual_object_type must be one of comparison seam, connector endpoint, decision node, evidence rail, field route, negative space pocket, product edge"
        in result.errors
    )
    assert (
        "run2_73_text_binding_strategy.page_text_binding_records[0].text_socket_strategy.headline_socket.bound_source_id references unknown D2/E2 binding: missing_visual_binding"
        in result.errors
    )
    assert (
        "run2_73_text_binding_strategy.page_text_binding_records[0].text_socket_strategy.headline_socket.capacity.max_words must be greater than 0"
        in result.errors
    )


def test_run2_profile_rejects_validated_scene_renderer_bad_manifest_or_release_scope(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_73_validated_scene_renderer_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["rerun_manifest"]["viewer_update"]["viewer_can_reference_new_run"] = False
    result_json["rendered_pages"][0]["visual_grammar_module"] = "hero_field"
    result_json["rendered_pages"][0]["text_socket_bindings"][0]["bound_source_id"] = "missing_binding"
    result_json["rendered_pages"][0]["visual_containers"][0]["empty"] = True
    result_json["render_quality_checks"]["empty_visual_container_count"] = 1
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_73_validated_scene_renderer_rerun_result.public_release_started must be false"
        in result.errors
    )
    assert (
        "run2_73_validated_scene_renderer_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json"
        in result.errors
    )
    assert (
        "run2_73_validated_scene_renderer_rerun_result.rerun_manifest.viewer_update.viewer_can_reference_new_run must be true"
        in result.errors
    )
    assert (
        "run2_73_validated_scene_renderer_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_73_validated_scene_renderer_rerun_result.rendered_pages[0].text_socket_bindings[0].bound_source_id references unknown D2/E2 binding: missing_binding"
        in result.errors
    )
    assert (
        "run2_73_validated_scene_renderer_rerun_result.rendered_pages[0].visual_containers[0].empty must be false"
        in result.errors
    )
    assert (
        "run2_73_validated_scene_renderer_rerun_result.render_quality_checks.empty_visual_container_count must be 0"
        in result.errors
    )


def test_run2_profile_rejects_visual_quality_evaluation_public_release_or_missing_questions(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    audit_path = pack / "results" / "run2_74_visual_quality_evaluation.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["public_ready"] = True
    audit["starts_renderer_rerun"] = True
    audit["evaluation_questions"].pop("is_2_73_better_than_2_72")
    audit["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.72"
    audit["visual_quality_assessment"]["design_quality_gate"] = "pass"
    audit["role_assessments"][0]["visual_grammar_module"] = "hero_field"
    audit["role_assessments"][0]["root_cause_layer"] = "source_data"
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_74_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_74_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert (
        "run2_74_visual_quality_evaluation.evaluation_questions missing key: is_2_73_better_than_2_72"
        in result.errors
    )
    assert (
        "run2_74_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.73"
        in result.errors
    )
    assert (
        "run2_74_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked"
        in result.errors
    )
    assert (
        "run2_74_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_74_visual_quality_evaluation.role_assessments[0].root_cause_layer must be one of content, renderer, text_binding, visual_grammar"
        in result.errors
    )


def test_run2_profile_rejects_renderer_repair_missing_h_or_public_release(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_75_renderer_repair_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_h_evaluation"]["status"] = "missing"
    result_json["renderer_repair_manifest"]["viewer_update"]["latest_run_id"] = "2.73"
    result_json["rendered_pages"][0]["visual_grammar_module"] = "hero_field"
    result_json["rendered_pages"][0]["renderer_repair_directives_applied"] = [
        "h_repair_instruction_consumed"
    ]
    result_json["rendered_pages"][0]["product_surface_detail_count"] = 2
    result_json["renderer_repair_checks"]["pages_with_h_repair_directive_consumed"] = 5
    result_json["renderer_repair_checks"]["public_quality_verdict_started"] = True
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_75_renderer_repair_rerun_result.public_ready must be false" in result.errors
    assert "run2_75_renderer_repair_rerun_result.public_release_started must be false" in result.errors
    assert (
        "run2_75_renderer_repair_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_74_visual_quality_evaluation.json"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.source_h_evaluation.status must be run2_74_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.renderer_repair_manifest.viewer_update.latest_run_id must be 2.75"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: concrete_product_surface"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.rendered_pages[0].product_surface_detail_count must be at least 5"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.renderer_repair_checks.pages_with_h_repair_directive_consumed must be 6"
        in result.errors
    )
    assert (
        "run2_75_renderer_repair_rerun_result.renderer_repair_checks.public_quality_verdict_started must be false"
        in result.errors
    )


def test_run2_profile_rejects_part_j_public_release_or_missing_gemini(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    audit_path = pack / "results" / "run2_76_visual_quality_evaluation.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["public_ready"] = True
    audit["starts_renderer_rerun"] = True
    audit["source_runs"]["evaluated_run"] = "2.73"
    audit["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.73"
    audit["gemini_agent_review_summary"]["review_count"] = 1
    audit["gemini_agent_review_summary"]["model"] = "gemini-legacy"
    audit["evaluation_questions"].pop("is_2_75_better_than_2_73")
    audit["visual_quality_assessment"]["design_quality_gate"] = "pass"
    audit["role_assessments"][0]["visual_grammar_module"] = "hero_field"
    audit["role_assessments"][0]["root_cause_layer"] = "source_data"
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_76_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_76_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert "run2_76_visual_quality_evaluation.source_runs.evaluated_run must be 2.75" in result.errors
    assert (
        "run2_76_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.75"
        in result.errors
    )
    assert (
        "run2_76_visual_quality_evaluation.gemini_agent_review_summary.model must be gemini-3.5-flash"
        in result.errors
    )
    assert (
        "run2_76_visual_quality_evaluation.gemini_agent_review_summary.review_count must be 2"
        in result.errors
    )
    assert (
        "run2_76_visual_quality_evaluation.evaluation_questions missing key: is_2_75_better_than_2_73"
        in result.errors
    )
    assert (
        "run2_76_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked"
        in result.errors
    )
    assert (
        "run2_76_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_76_visual_quality_evaluation.role_assessments[0].root_cause_layer must be one of content, renderer, text_binding, visual_grammar"
        in result.errors
    )


def test_run2_profile_rejects_k1_repair_plan_rerun_scope_or_weak_differentiation(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    plan_path = pack / "run2_76_visual_grammar_renderer_repair_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["public_ready"] = True
    plan["starts_renderer_rerun"] = True
    plan["updates_html_viewer"] = True
    plan["consumed_sources"] = plan["consumed_sources"][1:]
    plan["source_j_evaluation"]["status"] = "pass"
    plan["global_repair_strategy"]["primary_layers_to_fix"] = ["data"]
    plan["global_repair_strategy"]["renderer_capabilities_required"].remove("hero crop")
    plan["page_repair_plans"][0]["visual_grammar_module"] = "hero_field"
    plan["page_repair_plans"][0]["target_scene_direction"] = plan["page_repair_plans"][1]["target_scene_direction"]
    plan["page_repair_plans"][0]["must_remove_from_2_75"] = []
    plan["page_repair_plans"][0]["acceptance_checks"].pop("wireframe_reduction_check")
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_76_visual_grammar_renderer_repair_plan.public_ready must be false" in result.errors
    assert "run2_76_visual_grammar_renderer_repair_plan.starts_renderer_rerun must be false" in result.errors
    assert "run2_76_visual_grammar_renderer_repair_plan.updates_html_viewer must be false" in result.errors
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.source_j_evaluation.status must be run2_76_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.global_repair_strategy.primary_layers_to_fix must be visual_grammar, renderer"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.global_repair_strategy.renderer_capabilities_required missing value: hero crop"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.page_repair_plans[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.page_repair_plans[1].target_scene_direction duplicates source-to-memory transformation field"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.page_repair_plans[0].must_remove_from_2_75 must be a non-empty list"
        in result.errors
    )
    assert (
        "run2_76_visual_grammar_renderer_repair_plan.page_repair_plans[0].acceptance_checks missing key: wireframe_reduction_check"
        in result.errors
    )


def test_run2_profile_rejects_k2_rerun_missing_k1_or_forbidden_fallbacks(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_77_visual_grammar_renderer_repair_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_k1_repair_plan"]["status"] = "missing"
    result_json["visual_grammar_renderer_repair_manifest"]["viewer_update"]["latest_run_id"] = "2.75"
    result_json["rendered_pages"][0]["visual_grammar_module"] = "hero_field"
    result_json["rendered_pages"][0]["target_scene_direction"] = result_json["rendered_pages"][1]["target_scene_direction"]
    result_json["rendered_pages"][0]["renderer_repair_directives_applied"] = ["k1_repair_plan_consumed"]
    result_json["rendered_pages"][0]["renderer_capabilities_applied"] = []
    result_json["rendered_pages"][0]["forbidden_renderer_fallbacks_absent"] = []
    result_json["rendered_pages"][0]["label_count"] = 8
    result_json["visual_grammar_renderer_repair_checks"]["pages_with_k1_repair_plan_consumed"] = 5
    result_json["visual_grammar_renderer_repair_checks"]["public_quality_verdict_started"] = True
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_77_visual_grammar_renderer_repair_rerun_result.public_ready must be false" in result.errors
    assert "run2_77_visual_grammar_renderer_repair_rerun_result.public_release_started must be false" in result.errors
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.source_k1_repair_plan.status must be run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.visual_grammar_renderer_repair_manifest.viewer_update.latest_run_id must be 2.77"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.rendered_pages[1].target_scene_direction duplicates source-to-memory transformation field"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: target_scene_direction_applied"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.rendered_pages[0].renderer_capabilities_applied must be a non-empty list"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.rendered_pages[0].forbidden_renderer_fallbacks_absent must be a non-empty list"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.rendered_pages[0].label_count must be at most 5"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.visual_grammar_renderer_repair_checks.pages_with_k1_repair_plan_consumed must be 6"
        in result.errors
    )
    assert (
        "run2_77_visual_grammar_renderer_repair_rerun_result.visual_grammar_renderer_repair_checks.public_quality_verdict_started must be false"
        in result.errors
    )


def test_run2_profile_rejects_l_visual_evaluation_public_ready_or_missing_findings(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_78_visual_quality_evaluation.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["starts_renderer_rerun"] = True
    result_json["updates_html_viewer"] = True
    result_json["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.75"
    result_json["viewer_comparison_closure"]["run2_77_full_preview_count"] = 5
    result_json["gemini_agent_review_summary"]["review_count"] = 0
    result_json["evaluation_questions"]["did_2_77_reduce_wireframe_aesthetic"]["answer"] = "fixed"
    result_json["visual_quality_assessment"]["design_quality_gate"] = "pass"
    result_json["role_assessments"][0]["visual_grammar_module"] = "hero_field"
    result_json["role_assessments"][0]["repair_required"] = False
    result_json["role_assessments"][0]["trace_support"]["label_count"] = 8
    result_json["root_cause_summary"]["primary_layer"] = "data_absence"
    result_json["no_new_renderer_proof"]["new_pptx_created"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_78_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_78_visual_quality_evaluation.public_release_started must be false" in result.errors
    assert "run2_78_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert "run2_78_visual_quality_evaluation.updates_html_viewer must be false" in result.errors
    assert (
        "run2_78_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.77"
        in result.errors
    )
    assert (
        "run2_78_visual_quality_evaluation.viewer_comparison_closure.run2_77_full_preview_count must be 6"
        in result.errors
    )
    assert "run2_78_visual_quality_evaluation.gemini_agent_review_summary.review_count must be 1" in result.errors
    assert (
        "run2_78_visual_quality_evaluation.evaluation_questions.did_2_77_reduce_wireframe_aesthetic.answer must be no_wireframe_still_dominant"
        in result.errors
    )
    assert "run2_78_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked" in result.errors
    assert (
        "run2_78_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert "run2_78_visual_quality_evaluation.role_assessments[0].repair_required must be true" in result.errors
    assert "run2_78_visual_quality_evaluation.role_assessments[0].trace_support.label_count must be at most 5" in result.errors
    assert (
        "run2_78_visual_quality_evaluation.root_cause_summary.primary_layer must be renderer_art_direction_and_scene_realization"
        in result.errors
    )
    assert "run2_78_visual_quality_evaluation.no_new_renderer_proof.new_pptx_created must be false" in result.errors
    assert (
        "run2_78_visual_quality_evaluation.next_required_action must be part_m_renderer_art_direction_repair_from_l_evaluation"
        in result.errors
    )


def test_run2_profile_rejects_m_renderer_art_direction_rerun_missing_repair_gates(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_79_renderer_art_direction_repair_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_l_evaluation"]["status"] = "missing"
    result_json["renderer_art_direction_repair_manifest"]["viewer_update"]["latest_run_id"] = "2.77"
    result_json["rendered_pages"][0]["visual_grammar_module"] = "hero_field"
    result_json["rendered_pages"][0]["renderer_repair_directives_applied"] = ["l_repair_instruction_consumed"]
    result_json["rendered_pages"][0]["debug_annotation_count"] = 2
    result_json["rendered_pages"][0]["wireframe_dependency"] = "dominant"
    result_json["rendered_pages"][0]["dominant_product_object_scale"] = "small"
    result_json["rendered_pages"][0]["min_visible_label_font_size"] = 9
    result_json["rendered_pages"][0]["label_count"] = 5
    result_json["rendered_pages"][0]["public_polish_claimed"] = True
    result_json["renderer_art_direction_repair_checks"]["pages_with_debug_annotations_removed"] = 5
    result_json["renderer_art_direction_repair_checks"]["public_quality_verdict_started"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_79_renderer_art_direction_repair_rerun_result.public_ready must be false" in result.errors
    assert "run2_79_renderer_art_direction_repair_rerun_result.public_release_started must be false" in result.errors
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.source_l_evaluation.status must be run2_78_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.renderer_art_direction_repair_manifest.viewer_update.latest_run_id must be 2.79"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: wireframe_surface_replaced"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].debug_annotation_count must be 0"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].wireframe_dependency must be reduced or minimal"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].dominant_product_object_scale must be large, hero, or full_frame"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].min_visible_label_font_size must be at least 12"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].label_count must be at most 3"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.rendered_pages[0].public_polish_claimed must be false"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.renderer_art_direction_repair_checks.pages_with_debug_annotations_removed must be 6"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.renderer_art_direction_repair_checks.public_quality_verdict_started must be false"
        in result.errors
    )
    assert (
        "run2_79_renderer_art_direction_repair_rerun_result.next_required_action must be part_n_visual_quality_evaluation_for_run2_79"
        in result.errors
    )


def test_run2_profile_rejects_n_visual_evaluation_public_ready_or_missing_blockers(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_80_visual_quality_evaluation.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["starts_renderer_rerun"] = True
    result_json["updates_html_viewer"] = True
    result_json["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.77"
    result_json["viewer_comparison_closure"]["run2_79_full_preview_count"] = 5
    result_json["gemini_agent_review_summary"]["review_count"] = 0
    result_json["evaluation_questions"]["did_2_79_create_concrete_product_surface"]["answer"] = "yes_fixed"
    result_json["visual_quality_assessment"]["design_quality_gate"] = "pass"
    result_json["visual_quality_assessment"]["public_video_readiness"] = "ready"
    result_json["role_assessments"][0]["visual_grammar_module"] = "hero_field"
    result_json["role_assessments"][0]["repair_required"] = False
    result_json["role_assessments"][0]["trace_support"]["label_count"] = 5
    result_json["role_assessments"][0]["trace_support"]["debug_annotation_count"] = 2
    result_json["role_assessments"][0]["product_surface_realization"] = "invalid"
    result_json["root_cause_summary"]["primary_layer"] = "data_absence"
    result_json["no_new_renderer_proof"]["new_html_created"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_80_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_80_visual_quality_evaluation.public_release_started must be false" in result.errors
    assert "run2_80_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert "run2_80_visual_quality_evaluation.updates_html_viewer must be false" in result.errors
    assert (
        "run2_80_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.79"
        in result.errors
    )
    assert (
        "run2_80_visual_quality_evaluation.viewer_comparison_closure.run2_79_full_preview_count must be 6"
        in result.errors
    )
    assert "run2_80_visual_quality_evaluation.gemini_agent_review_summary.review_count must be 1" in result.errors
    assert (
        "run2_80_visual_quality_evaluation.evaluation_questions.did_2_79_create_concrete_product_surface.answer must be no_product_surface_not_visibly_realized"
        in result.errors
    )
    assert "run2_80_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked" in result.errors
    assert (
        "run2_80_visual_quality_evaluation.visual_quality_assessment.public_video_readiness must be blocked"
        in result.errors
    )
    assert (
        "run2_80_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert "run2_80_visual_quality_evaluation.role_assessments[0].repair_required must be true" in result.errors
    assert (
        "run2_80_visual_quality_evaluation.role_assessments[0].product_surface_realization must be one of absent, partial, strong, weak"
        in result.errors
    )
    assert "run2_80_visual_quality_evaluation.role_assessments[0].trace_support.label_count must be at most 3" in result.errors
    assert (
        "run2_80_visual_quality_evaluation.role_assessments[0].trace_support.debug_annotation_count must be 0"
        in result.errors
    )
    assert (
        "run2_80_visual_quality_evaluation.root_cause_summary.primary_layer must be renderer_product_surface_realization"
        in result.errors
    )
    assert "run2_80_visual_quality_evaluation.no_new_renderer_proof.new_html_created must be false" in result.errors
    assert (
        "run2_80_visual_quality_evaluation.next_required_action must be part_o_renderer_product_surface_repair_from_n_evaluation"
        in result.errors
    )


def test_run2_profile_rejects_o1_text_composition_bad_scope_or_unbound_text(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    plan_path = pack / "run2_81_text_composition_typography_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["public_ready"] = True
    plan["starts_renderer_rerun"] = True
    plan["updates_html_viewer"] = True
    plan["consumed_sources"] = plan["consumed_sources"][:-1]
    plan["source_n_evaluation"]["status"] = "missing"
    plan["global_text_composition_contract"]["slide_canvas_traceability_allowed"] = True
    first = plan["page_text_composition_records"][0]
    first["visual_grammar_module"] = "hero_field"
    first["headline_block"]["object_anchor_required"] = False
    first["headline_block"]["capacity"]["max_words"] = 0
    first["headline_block"]["typography"]["min_font_size"] = 9
    first["subhead_block"].pop("canvas_route")
    first["label_policy"]["max_visible_labels"] = 5
    first["label_policy"]["floating_labels_allowed"] = True
    first["label_policy"]["overflow_route"] = "slide_canvas"
    first["viewer_note_route"]["traceability_on_canvas"] = True
    first["forbidden_patterns"] = ["generic bad pattern"]
    plan["traceability_summary"]["renderer_rerun_started"] = True
    plan["next_required_action"] = "part_o2_renderer_rerun"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_81_text_composition_typography_plan.public_ready must be false" in result.errors
    assert "run2_81_text_composition_typography_plan.starts_renderer_rerun must be false" in result.errors
    assert "run2_81_text_composition_typography_plan.updates_html_viewer must be false" in result.errors
    assert (
        "run2_81_text_composition_typography_plan.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.source_n_evaluation.status must be run2_80_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.global_text_composition_contract.slide_canvas_traceability_allowed must be false"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].headline_block.object_anchor_required must be true"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].headline_block.capacity.max_words must be greater than 0"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].headline_block.typography.min_font_size must be at least 12"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].subhead_block missing key: canvas_route"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].label_policy.max_visible_labels must be at most 3"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].label_policy.floating_labels_allowed must be false"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].label_policy.overflow_route must be viewer_metadata_and_speaker_notes"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].viewer_note_route.traceability_on_canvas must be false"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.page_text_composition_records[0].forbidden_patterns missing value: floating labels"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.traceability_summary.renderer_rerun_started must be false"
        in result.errors
    )
    assert (
        "run2_81_text_composition_typography_plan.next_required_action must be part_o2_renderer_rerun_from_text_composition_and_product_surface_repair"
        in result.errors
    )


def test_run2_profile_rejects_o2_rerun_missing_text_composition_or_public_gates(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_82_renderer_product_surface_text_composition_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_n_evaluation"]["status"] = "missing"
    result_json["source_o1_text_composition_plan"]["status"] = "missing"
    result_json["renderer_product_surface_text_composition_manifest"]["viewer_update"]["latest_run_id"] = "2.79"
    first = result_json["rendered_pages"][0]
    first["visual_grammar_module"] = "hero_field"
    first["renderer_repair_directives_applied"] = ["n_repair_instruction_consumed"]
    first["concrete_product_surface_visible"] = False
    first["product_surface_type"] = "abstract_wireframe"
    first["text_hierarchy"] = "headline_chips"
    first["text_composition_blocks_applied"] = ["headline_block"]
    first["floating_label_count"] = 2
    first["label_count"] = 5
    first["min_visible_label_font_size"] = 9
    first["canvas_word_count"] = 12
    first["source_trace_terms_visible_on_canvas"] = ["traceability"]
    first["public_polish_claimed"] = True
    checks = result_json["renderer_product_surface_text_composition_checks"]
    checks["pages_with_o1_text_composition_consumed"] = 5
    checks["pages_with_concrete_product_surface"] = 5
    checks["pages_with_text_hierarchy_applied"] = 5
    checks["pages_with_floating_labels_removed"] = 5
    checks["pages_with_traceability_routed_off_canvas"] = 5
    checks["public_quality_verdict_started"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_82_renderer_product_surface_text_composition_rerun_result.public_ready must be false" in result.errors
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.public_release_started must be false"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.source_n_evaluation.status must be run2_80_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.source_o1_text_composition_plan.status must be run2_81_text_composition_typography_plan_ready_public_blocked"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.renderer_product_surface_text_composition_manifest.viewer_update.latest_run_id must be 2.82"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: o1_text_composition_consumed"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].concrete_product_surface_visible must be true"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].product_surface_type must be one of before_after_product_theater, editable_ppt_product_mock, evidence_product_workspace, release_decision_product_map, source_to_memory_product_flow"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].text_hierarchy must be headline_subhead_proof_caption"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].text_composition_blocks_applied missing value: object_caption"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].floating_label_count must be 0"
        in result.errors
    )
    assert "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].label_count must be at most 3" in result.errors
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].min_visible_label_font_size must be at least 12"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].canvas_word_count must be at least 24"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].source_trace_terms_visible_on_canvas must be empty"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.rendered_pages[0].public_polish_claimed must be false"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.renderer_product_surface_text_composition_checks.pages_with_o1_text_composition_consumed must be 6"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.renderer_product_surface_text_composition_checks.public_quality_verdict_started must be false"
        in result.errors
    )
    assert (
        "run2_82_renderer_product_surface_text_composition_rerun_result.next_required_action must be part_p_visual_quality_evaluation_for_run2_82"
        in result.errors
    )


def test_run2_profile_rejects_p0_workflow_taxonomy_bias_audit_bad_scope_or_missing_design_layer(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    audit_path = pack / "results" / "run2_83_workflow_taxonomy_bias_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["public_ready"] = True
    audit["starts_renderer_rerun"] = True
    audit["updates_html_viewer"] = True
    audit["consumed_sources"] = audit["consumed_sources"][:-1]
    audit["engineering_rigor_preservation"]["preserve_existing_gates"].remove("traceability")
    audit["engineering_rigor_preservation"]["do_not_weaken_traceability"] = False
    audit["engineering_rigor_preservation"]["design_layer_adds_to_engineering_layer"] = False
    audit["taxonomy_bias_summary"]["primary_bias"] = "renderer_bug_only"
    audit["layer_bias_records"][0]["layer_id"] = "unknown_layer"
    audit["layer_bias_records"][0]["needs_new_design_layer"] = False
    audit["layer_bias_records"][0]["evidence"] = []
    audit["missing_design_taxonomy"] = audit["missing_design_taxonomy"][:-1]
    audit["required_next_layer"]["layer_id"] = "renderer_patch"
    audit["required_next_layer"]["must_preserve_engineering_gates"] = False
    audit["no_new_renderer_proof"]["new_html_created"] = True
    audit["next_required_action"] = "renderer_rerun"
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_83_workflow_taxonomy_bias_audit.public_ready must be false" in result.errors
    assert "run2_83_workflow_taxonomy_bias_audit.starts_renderer_rerun must be false" in result.errors
    assert "run2_83_workflow_taxonomy_bias_audit.updates_html_viewer must be false" in result.errors
    assert (
        "run2_83_workflow_taxonomy_bias_audit.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.engineering_rigor_preservation.preserve_existing_gates missing value: traceability"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.engineering_rigor_preservation.do_not_weaken_traceability must be true"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.engineering_rigor_preservation.design_layer_adds_to_engineering_layer must be true"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.taxonomy_bias_summary.primary_bias must be engineering_constraint_labels_over_design_motif_labels"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.layer_bias_records missing layer_id: source_quality_inventory"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.layer_bias_records[0].needs_new_design_layer must be true"
        in result.errors
    )
    assert "run2_83_workflow_taxonomy_bias_audit.layer_bias_records[0].evidence must be a non-empty list" in result.errors
    assert (
        "run2_83_workflow_taxonomy_bias_audit.missing_design_taxonomy missing field: motif_fidelity_checks"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.required_next_layer.layer_id must be design_motif_layer"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.required_next_layer.must_preserve_engineering_gates must be true"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.no_new_renderer_proof.new_html_created must be false"
        in result.errors
    )
    assert (
        "run2_83_workflow_taxonomy_bias_audit.next_required_action must be part_p1_design_motif_taxonomy_and_style_router_plan"
        in result.errors
    )


def test_run2_profile_rejects_p1_design_motif_plan_bad_scope_or_weak_motif_contract(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    plan_path = pack / "run2_84_design_motif_taxonomy_style_router_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["public_ready"] = True
    plan["starts_renderer_rerun"] = True
    plan["updates_html_viewer"] = True
    plan["consumed_sources"] = plan["consumed_sources"][:-1]
    plan["source_p0_audit"]["status"] = "missing"
    plan["preserved_visual_effects"].remove("overlay_sticker_stack")
    first_motif = plan["design_motif_taxonomy"][0]
    first_motif["motif_family"] = "generic_blocks"
    first_motif["layout_recipe"].pop("reading_path")
    first_motif["renderer_recipe"]["forbidden_renderer_shortcuts"] = ["none"]
    first_motif["motif_fidelity_checks"] = ["motif_family_visible"]
    first_motif["source_trace"] = []
    plan["style_router_rules"] = plan["style_router_rules"][:-1]
    first_binding = plan["page_role_motif_bindings"][0]
    first_binding["visual_grammar_module"] = "hero_field"
    first_binding["primary_motif_id"] = "missing_motif"
    first_binding["required_motif_fidelity_checks"] = ["motif_family_visible"]
    plan["engineering_gate_bridge"]["slide_canvas_traceability_allowed"] = True
    plan["engineering_gate_bridge"]["validator_remains_authoritative"] = False
    plan["renderer_contract_preview"]["next_renderer_must_consume_p1"] = False
    plan["renderer_contract_preview"]["required_fields_for_next_rerun"] = ["motif_id"]
    plan["renderer_contract_preview"]["does_not_execute_renderer"] = False
    plan["no_new_renderer_proof"]["viewer_updated"] = True
    plan["next_required_action"] = "public_release"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_84_design_motif_taxonomy_style_router_plan.public_ready must be false" in result.errors
    assert "run2_84_design_motif_taxonomy_style_router_plan.starts_renderer_rerun must be false" in result.errors
    assert "run2_84_design_motif_taxonomy_style_router_plan.updates_html_viewer must be false" in result.errors
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.source_p0_audit.status must be run2_83_workflow_taxonomy_bias_audit_ready_public_blocked"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.preserved_visual_effects missing value: overlay_sticker_stack"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.design_motif_taxonomy[0].motif_family must be one of before_after_theater, decision_map, editorial_text_field, evidence_workspace, modular_matrix, overlay_sticker_stack, product_theater"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.design_motif_taxonomy[0].layout_recipe missing key: reading_path"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.design_motif_taxonomy[0].renderer_recipe.forbidden_renderer_shortcuts missing value: generic rectangles only"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.design_motif_taxonomy[0].motif_fidelity_checks missing value: not_rectangle_only"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.design_motif_taxonomy[0].source_trace must be a non-empty list"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.style_router_rules missing scenario: public_video_demo"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.page_role_motif_bindings[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.page_role_motif_bindings[0].primary_motif_id references unknown motif: missing_motif"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.page_role_motif_bindings[0].required_motif_fidelity_checks missing value: text_integrated_with_shape"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.engineering_gate_bridge.slide_canvas_traceability_allowed must be false"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.engineering_gate_bridge.validator_remains_authoritative must be true"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.renderer_contract_preview.next_renderer_must_consume_p1 must be true"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.renderer_contract_preview.required_fields_for_next_rerun missing value: motif_fidelity_checks"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.renderer_contract_preview.does_not_execute_renderer must be true"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.no_new_renderer_proof.viewer_updated must be false"
        in result.errors
    )
    assert (
        "run2_84_design_motif_taxonomy_style_router_plan.next_required_action must be part_p2_renderer_rerun_from_design_motif_layer_and_style_router"
        in result.errors
    )


def test_run2_profile_rejects_p2_design_motif_renderer_bad_scope_or_missing_motif_layer(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_85_design_motif_renderer_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_p1_design_motif_plan"]["status"] = "missing"
    result_json["source_o2_renderer_result"]["status"] = "missing"
    manifest = result_json["renderer_design_motif_manifest"]
    manifest["viewer_update"]["latest_run_id"] = "2.82"
    manifest["arms"] = ["prompt_only", "run1_5_skill"]
    manifest["best_internal_arm"] = "run2_82_full_product_surface_text_composition"
    first = result_json["rendered_pages"][0]
    first["visual_grammar_module"] = "hero_field"
    first["source_p1_primary_motif_id"] = "missing_motif"
    first["motif_family"] = "generic_blocks"
    first["style_family"] = "generic_report"
    first["scenario"] = "generic_demo"
    first["visual_density"] = "unknown"
    first["renderer_repair_directives_applied"] = ["p1_design_motif_layer_consumed"]
    first["preserved_visual_effects_rendered"] = ["plain_rectangles"]
    first["motif_fidelity_checks"] = ["motif_family_visible"]
    first["motif_family_visible"] = False
    first["not_rectangle_only"] = False
    first["text_integrated_with_shape"] = False
    first["concrete_product_surface_visible"] = False
    first["text_hierarchy"] = "headline_chips"
    first["floating_label_count"] = 2
    first["label_count"] = 5
    first["min_visible_label_font_size"] = 9
    first["source_trace_terms_visible_on_canvas"] = ["motif_2_84_product_theater"]
    first["public_polish_claimed"] = True
    checks = result_json["renderer_design_motif_checks"]
    checks["pages_with_p1_motif_consumed"] = 5
    checks["pages_with_motif_family_visible"] = 5
    checks["pages_with_not_rectangle_only"] = 5
    checks["pages_with_text_integrated_with_shape"] = 5
    checks["pages_with_traceability_routed_off_canvas"] = 5
    checks["public_quality_verdict_started"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_85_design_motif_renderer_rerun_result.public_ready must be false" in result.errors
    assert "run2_85_design_motif_renderer_rerun_result.public_release_started must be false" in result.errors
    assert (
        "run2_85_design_motif_renderer_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.source_p1_design_motif_plan.status must be run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.source_o2_renderer_result.status must be run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.renderer_design_motif_manifest.viewer_update.latest_run_id must be 2.85"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.renderer_design_motif_manifest.arms missing value: run2_85_full_design_motif_style_router"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.renderer_design_motif_manifest.best_internal_arm must be run2_85_full_design_motif_style_router"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].motif_family must be one of before_after_theater, decision_map, editorial_text_field, evidence_workspace, modular_matrix, overlay_sticker_stack, product_theater"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].style_family must be one of dense_teaching_walkthrough, financial_decision_brief, high_contrast_demo, public_product_keynote, technical_editorial"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: motif_family_rendered"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].preserved_visual_effects_rendered missing value: overlay_sticker_stack"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].motif_fidelity_checks missing value: not_rectangle_only"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].motif_family_visible must be true"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].not_rectangle_only must be true"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].text_integrated_with_shape must be true"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.rendered_pages[0].source_trace_terms_visible_on_canvas must be empty"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.renderer_design_motif_checks.pages_with_p1_motif_consumed must be 6"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.renderer_design_motif_checks.public_quality_verdict_started must be false"
        in result.errors
    )
    assert (
        "run2_85_design_motif_renderer_rerun_result.next_required_action must be part_q_visual_quality_evaluation_for_run2_85"
        in result.errors
    )


def test_run2_profile_rejects_q_visual_quality_evaluation_bad_boundary_or_wrong_root_cause(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_86_visual_quality_evaluation.json"
    audit = json.loads(result_path.read_text(encoding="utf-8"))
    audit["public_ready"] = True
    audit["public_release_started"] = True
    audit["starts_renderer_rerun"] = True
    audit["updates_html_viewer"] = True
    audit["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.82"
    audit["viewer_comparison_closure"]["run2_85_full_preview_count"] = 5
    audit["gemini_agent_review_summary"]["review_count"] = 0
    audit["evaluation_questions"]["which_layer_needs_next_repair"]["answer"] = "more_data_contracts"
    audit["visual_quality_assessment"]["design_quality_gate"] = "pass"
    audit["visual_quality_assessment"]["top_blocker"] = "data_absence"
    audit["visual_quality_assessment"]["next_layer_to_fix"] = "more_workflow_contracts"
    first = audit["role_assessments"][0]
    first["visual_grammar_module"] = "hero_field"
    first["repair_required"] = False
    first["motif_realization"] = "absent"
    first["trace_support"]["label_count"] = 5
    first["trace_support"]["not_rectangle_only"] = False
    audit["root_cause_summary"]["primary_layer"] = "data_absence"
    audit["root_cause_summary"]["not_primary_layer"] = "renderer_visual_primitive_and_composition_engine"
    audit["root_cause_summary"]["late_2_series_failure_mode"] = "unknown"
    audit["no_new_renderer_proof"]["new_html_created"] = True
    audit["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_86_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_86_visual_quality_evaluation.public_release_started must be false" in result.errors
    assert "run2_86_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert "run2_86_visual_quality_evaluation.updates_html_viewer must be false" in result.errors
    assert (
        "run2_86_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.85"
        in result.errors
    )
    assert (
        "run2_86_visual_quality_evaluation.viewer_comparison_closure.run2_85_full_preview_count must be 6"
        in result.errors
    )
    assert "run2_86_visual_quality_evaluation.gemini_agent_review_summary.review_count must be 1" in result.errors
    assert (
        "run2_86_visual_quality_evaluation.evaluation_questions.which_layer_needs_next_repair.answer must be renderer_visual_primitive_and_composition_engine"
        in result.errors
    )
    assert "run2_86_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked" in result.errors
    assert (
        "run2_86_visual_quality_evaluation.visual_quality_assessment.top_blocker must be renderer_visual_primitives_are_too_simple_to_realize_design_motifs"
        in result.errors
    )
    assert (
        "run2_86_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert "run2_86_visual_quality_evaluation.role_assessments[0].repair_required must be true" in result.errors
    assert (
        "run2_86_visual_quality_evaluation.role_assessments[0].motif_realization must be one of partial, strong, weak"
        in result.errors
    )
    assert (
        "run2_86_visual_quality_evaluation.role_assessments[0].trace_support.label_count must be at most 3"
        in result.errors
    )
    assert (
        "run2_86_visual_quality_evaluation.role_assessments[0].trace_support.not_rectangle_only must be true"
        in result.errors
    )
    assert (
        "run2_86_visual_quality_evaluation.root_cause_summary.primary_layer must be renderer_visual_primitive_and_composition_engine"
        in result.errors
    )
    assert "run2_86_visual_quality_evaluation.no_new_renderer_proof.new_html_created must be false" in result.errors
    assert (
        "run2_86_visual_quality_evaluation.next_required_action must be part_r_best_layout_recovery_and_visual_primitive_plan_from_q_evaluation"
        in result.errors
    )


def test_run2_profile_rejects_r_best_layout_plan_bad_boundary_or_missing_primitives(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    plan_path = pack / "run2_87_best_layout_recovery_visual_primitive_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["public_ready"] = True
    plan["starts_renderer_rerun"] = True
    plan["updates_html_viewer"] = True
    plan["source_q_evaluation"]["status"] = "wrong"
    plan["historical_recovery_scope"]["candidate_runs"] = ["2.85"]
    plan["historical_recovery_scope"]["source_primitive_ids"] = ["missing"]
    first = plan["page_layout_recovery_records"][0]
    first["visual_grammar_module"] = "wrong"
    first["historical_layout_sources"] = ["2.85"]
    first["renderer_primitive_id"] = "missing"
    first["composition_engine_obligation"]["recover_best_historical_layout"] = False
    first["forbidden_patterns"] = ["generic rectangles only"]
    first_contract = plan["visual_primitive_contracts"][0]
    first_contract["renderer_function_name"] = "drawOldPrimitive"
    first_contract["anti_regression_gates"] = ["not_rectangle_only"]
    first_contract["forbidden_shortcuts"] = ["floating trace labels"]
    plan["composition_engine_repair_plan"]["layout_selection_order"] = ["run2_84_design_motif_router"]
    plan["composition_engine_repair_plan"]["collision_policy"]["reject_visible_text_overlap"] = False
    plan["composition_engine_repair_plan"]["traceability_policy"]["slide_canvas_traceability_allowed"] = True
    plan["next_renderer_contract"]["next_run_id"] = "2.90"
    plan["next_renderer_contract"]["next_renderer_script"] = "wrong.mjs"
    plan["next_renderer_contract"]["must_consume_part_r"] = False
    plan["next_renderer_contract"]["public_quality_verdict_deferred"] = False
    plan["next_renderer_contract"]["arms"] = ["prompt_only"]
    plan["no_new_renderer_proof"]["new_html_created"] = True
    plan["next_required_action"] = "public_release"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_87_best_layout_recovery_visual_primitive_plan.public_ready must be false" in result.errors
    assert "run2_87_best_layout_recovery_visual_primitive_plan.starts_renderer_rerun must be false" in result.errors
    assert "run2_87_best_layout_recovery_visual_primitive_plan.updates_html_viewer must be false" in result.errors
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.source_q_evaluation.status must be run2_86_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.historical_recovery_scope.candidate_runs missing value: 2.10"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.historical_recovery_scope.source_primitive_ids missing value: primitive_2_9_product_surface_depth"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.page_layout_recovery_records[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.page_layout_recovery_records[0].historical_layout_sources must include a recovery run before 2.85"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.page_layout_recovery_records[0].renderer_primitive_id references unknown primitive: missing"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.page_layout_recovery_records[0].composition_engine_obligation.recover_best_historical_layout must be true"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.page_layout_recovery_records[0].forbidden_patterns missing value: floating labels"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.visual_primitive_contracts[0].renderer_function_name must start with drawRun287"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.visual_primitive_contracts[0].anti_regression_gates missing value: collision_avoidance"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.visual_primitive_contracts[0].forbidden_shortcuts missing value: generic rectangles only"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.composition_engine_repair_plan.layout_selection_order[0] must be historical_best_layout_recovery"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.composition_engine_repair_plan.collision_policy.reject_visible_text_overlap must be true"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.composition_engine_repair_plan.traceability_policy.slide_canvas_traceability_allowed must be false"
        in result.errors
    )
    assert "run2_87_best_layout_recovery_visual_primitive_plan.next_renderer_contract.next_run_id must be 2.88" in result.errors
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.next_renderer_contract.next_renderer_script must be scripts/generate_ppt_run2_88_best_layout_visual_primitive_arms.mjs"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.next_renderer_contract.must_consume_part_r must be true"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.next_renderer_contract.public_quality_verdict_deferred must be true"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.no_new_renderer_proof.new_html_created must be false"
        in result.errors
    )
    assert (
        "run2_87_best_layout_recovery_visual_primitive_plan.next_required_action must be part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan"
        in result.errors
    )


def test_run2_profile_rejects_s_best_layout_renderer_bad_scope_or_missing_part_r(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_88_best_layout_visual_primitive_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_part_r_plan"]["status"] = "missing"
    result_json["source_run2_85_renderer_result"]["status"] = "missing"
    manifest = result_json["renderer_best_layout_visual_primitive_manifest"]
    manifest["viewer_update"]["latest_run_id"] = "2.85"
    manifest["arms"] = ["prompt_only", "run1_5_skill"]
    manifest["best_internal_arm"] = "run2_85_full_design_motif_style_router"
    first = result_json["rendered_pages"][0]
    first["visual_grammar_module"] = "hero_field"
    first["renderer_primitive_id"] = "missing"
    first["renderer_function_name"] = "drawOldPrimitive"
    first["renderer_repair_directives_applied"] = ["part_r_best_layout_plan_consumed"]
    first["anti_regression_gates"] = ["not_rectangle_only"]
    first["historical_layout_recovered"] = False
    first["not_rectangle_only"] = False
    first["text_integrated_with_shape"] = False
    first["collision_avoidance_passed"] = False
    first["traceability_on_canvas"] = True
    first["floating_label_count"] = 2
    first["label_count"] = 5
    first["min_visible_label_font_size"] = 9
    first["public_polish_claimed"] = True
    checks = result_json["renderer_best_layout_visual_primitive_checks"]
    checks["pages_with_part_r_consumed"] = 5
    checks["pages_with_historical_layout_recovered"] = 5
    checks["pages_with_visual_primitive_rendered"] = 5
    checks["pages_with_collision_avoidance"] = 5
    checks["pages_with_traceability_routed_off_canvas"] = 5
    checks["public_quality_verdict_started"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_88_best_layout_visual_primitive_rerun_result.public_ready must be false" in result.errors
    assert "run2_88_best_layout_visual_primitive_rerun_result.public_release_started must be false" in result.errors
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/results/run2_85_design_motif_renderer_rerun_result.json"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.source_part_r_plan.status must be run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.source_run2_85_renderer_result.status must be run2_85_design_motif_renderer_rerun_generated_public_blocked"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.renderer_best_layout_visual_primitive_manifest.viewer_update.latest_run_id must be 2.88"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.renderer_best_layout_visual_primitive_manifest.arms missing value: run2_88_full_best_layout_visual_primitives"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.renderer_best_layout_visual_primitive_manifest.best_internal_arm must be run2_88_full_best_layout_visual_primitives"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].renderer_primitive_id references unknown Run 2.87 primitive: missing"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].renderer_function_name must start with drawRun287"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: run2_87_visual_primitive_rendered"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].anti_regression_gates missing value: collision_avoidance"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].historical_layout_recovered must be true"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].collision_avoidance_passed must be true"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].traceability_on_canvas must be false"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].floating_label_count must be 0"
        in result.errors
    )
    assert "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].label_count must be at most 3" in result.errors
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.rendered_pages[0].min_visible_label_font_size must be at least 12"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.renderer_best_layout_visual_primitive_checks.pages_with_part_r_consumed must be 6"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.renderer_best_layout_visual_primitive_checks.public_quality_verdict_started must be false"
        in result.errors
    )
    assert (
        "run2_88_best_layout_visual_primitive_rerun_result.next_required_action must be part_t_visual_quality_evaluation_for_run2_88"
        in result.errors
    )


def test_run2_profile_rejects_t_visual_quality_evaluation_bad_boundary_or_false_pass(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_89_visual_quality_evaluation.json"
    audit = json.loads(result_path.read_text(encoding="utf-8"))
    audit["public_ready"] = True
    audit["public_release_started"] = True
    audit["starts_renderer_rerun"] = True
    audit["updates_html_viewer"] = True
    audit["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.85"
    audit["viewer_comparison_closure"]["run2_88_full_preview_count"] = 5
    audit["viewer_comparison_closure"]["run2_88_arm_count"] = 3
    audit["gemini_agent_review_summary"]["review_count"] = 0
    audit["evaluation_questions"]["which_layer_needs_next_repair"]["answer"] = "public_release"
    audit["visual_quality_assessment"]["design_quality_gate"] = "pass"
    audit["visual_quality_assessment"]["top_blocker"] = "none"
    audit["visual_quality_assessment"]["next_layer_to_fix"] = "none"
    first = audit["role_assessments"][0]
    first["visual_grammar_module"] = "hero_field"
    first["repair_required"] = False
    first["visual_primitive_fidelity"] = "absent"
    first["trace_support"]["renderer_primitive_id"] = "missing"
    first["trace_support"]["label_count"] = 5
    first["trace_support"]["not_rectangle_only"] = False
    audit["root_cause_summary"]["primary_layer"] = "data_absence"
    audit["root_cause_summary"]["not_primary_layer"] = "renderer_asset_surface_and_composition_detail"
    audit["root_cause_summary"]["late_2_series_failure_mode"] = "unknown"
    audit["no_new_renderer_proof"]["new_html_created"] = True
    audit["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_89_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_89_visual_quality_evaluation.public_release_started must be false" in result.errors
    assert "run2_89_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert "run2_89_visual_quality_evaluation.updates_html_viewer must be false" in result.errors
    assert (
        "run2_89_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.88"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.viewer_comparison_closure.run2_88_full_preview_count must be 6"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.viewer_comparison_closure.run2_88_arm_count must be 4"
        in result.errors
    )
    assert "run2_89_visual_quality_evaluation.gemini_agent_review_summary.review_count must be 1" in result.errors
    assert (
        "run2_89_visual_quality_evaluation.evaluation_questions.which_layer_needs_next_repair.answer must be renderer_asset_surface_and_composition_detail"
        in result.errors
    )
    assert "run2_89_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked" in result.errors
    assert (
        "run2_89_visual_quality_evaluation.visual_quality_assessment.top_blocker must be layout_primitive_names_changed_but_visual_execution_remains_wireframe_like"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert "run2_89_visual_quality_evaluation.role_assessments[0].repair_required must be true" in result.errors
    assert (
        "run2_89_visual_quality_evaluation.role_assessments[0].visual_primitive_fidelity must be one of partial, strong, weak"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.role_assessments[0].trace_support.renderer_primitive_id references unknown Run 2.87 primitive: missing"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.role_assessments[0].trace_support.label_count must be at most 3"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.role_assessments[0].trace_support.not_rectangle_only must be true"
        in result.errors
    )
    assert (
        "run2_89_visual_quality_evaluation.root_cause_summary.primary_layer must be renderer_asset_surface_and_composition_detail"
        in result.errors
    )
    assert "run2_89_visual_quality_evaluation.no_new_renderer_proof.new_html_created must be false" in result.errors
    assert (
        "run2_89_visual_quality_evaluation.next_required_action must be part_u_renderer_asset_surface_composition_repair_from_t_evaluation"
        in result.errors
    )


def test_run2_profile_rejects_u_asset_surface_renderer_bad_scope_or_wireframe_regression(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_90_renderer_asset_surface_composition_rerun_result.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["consumed_sources"] = result_json["consumed_sources"][:-1]
    result_json["source_t_evaluation"]["status"] = "missing"
    result_json["source_t_evaluation"]["next_layer_to_fix"] = "data_absence"
    result_json["source_run2_88_renderer_result"]["status"] = "missing"
    manifest = result_json["renderer_asset_surface_composition_manifest"]
    manifest["viewer_update"]["latest_run_id"] = "2.88"
    manifest["arms"] = ["prompt_only", "run1_5_skill"]
    manifest["best_internal_arm"] = "run2_88_full_best_layout_visual_primitives"
    first = result_json["rendered_pages"][0]
    first["visual_grammar_module"] = "hero_field"
    first["source_t_root_cause_layer"] = "data_absence"
    first["renderer_function_name"] = "drawRun287ProductTheaterSurface"
    first["renderer_repair_directives_applied"] = ["part_t_visual_quality_evaluation_consumed"]
    first["anti_regression_gates"] = ["collision_avoidance"]
    first["asset_surface_rendered"] = False
    first["composition_detail_added"] = False
    first["wireframe_like"] = True
    first["collision_avoidance_passed"] = False
    first["traceability_on_canvas"] = True
    first["floating_label_count"] = 2
    first["label_count"] = 5
    first["min_visible_label_font_size"] = 9
    first["surface_detail_count"] = 3
    first["filled_surface_count"] = 1
    first["mock_asset_count"] = 0
    first["public_polish_claimed"] = True
    checks = result_json["renderer_asset_surface_composition_checks"]
    checks["pages_with_t_evaluation_consumed"] = 5
    checks["pages_with_asset_surface_rendered"] = 5
    checks["pages_with_composition_detail_added"] = 5
    checks["pages_with_wireframe_reduction"] = 5
    checks["pages_with_collision_avoidance"] = 5
    checks["pages_with_traceability_routed_off_canvas"] = 5
    checks["public_quality_verdict_started"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_90_renderer_asset_surface_composition_rerun_result.public_ready must be false" in result.errors
    assert "run2_90_renderer_asset_surface_composition_rerun_result.public_release_started must be false" in result.errors
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.consumed_sources missing value: docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.source_t_evaluation.status must be run2_89_visual_quality_evaluation_public_blocked"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.source_t_evaluation.next_layer_to_fix must be renderer_asset_surface_and_composition_detail"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.source_run2_88_renderer_result.status must be run2_88_best_layout_visual_primitive_rerun_generated_public_blocked"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.renderer_asset_surface_composition_manifest.viewer_update.latest_run_id must be 2.90"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.renderer_asset_surface_composition_manifest.arms missing value: run2_90_full_asset_surface_composition"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.renderer_asset_surface_composition_manifest.best_internal_arm must be run2_90_full_asset_surface_composition"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].visual_grammar_module must be product_reveal for cover"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].source_t_root_cause_layer must be one of composition_engine, layout_engine_reuse, renderer_asset_surface, text_composition, visual_primitive_fidelity"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].renderer_function_name must start with drawRun290"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].renderer_repair_directives_applied missing value: asset_surface_rendered"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].anti_regression_gates missing value: product_surface_materiality"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].asset_surface_rendered must be true"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].wireframe_like must be false"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].surface_detail_count must be at least 8"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].filled_surface_count must be at least 4"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.rendered_pages[0].mock_asset_count must be at least 2"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.renderer_asset_surface_composition_checks.pages_with_asset_surface_rendered must be 6"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.renderer_asset_surface_composition_checks.public_quality_verdict_started must be false"
        in result.errors
    )
    assert (
        "run2_90_renderer_asset_surface_composition_rerun_result.next_required_action must be part_v_visual_quality_evaluation_for_run2_90"
        in result.errors
    )


def test_run2_profile_rejects_v_visual_evaluation_bad_scope_or_missing_text_visual_diagnosis(
    tmp_path: Path,
) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    result_path = pack / "results" / "run2_91_visual_quality_evaluation.json"
    result_json = json.loads(result_path.read_text(encoding="utf-8"))
    result_json["creates_new_ppt_deck"] = True
    result_json["starts_renderer_rerun"] = True
    result_json["updates_html_viewer"] = True
    result_json["public_ready"] = True
    result_json["public_release_started"] = True
    result_json["source_runs"]["evaluated_run"] = "2.88"
    result_json["viewer_comparison_closure"]["viewer_latest_run_id"] = "2.88"
    result_json["viewer_comparison_closure"]["run2_90_full_preview_count"] = 5
    result_json["gemini_agent_review_summary"]["review_count"] = 0
    result_json["evaluation_questions"]["did_2_90_integrate_text_with_visual_objects"]["answer"] = "yes"
    result_json["evaluation_questions"]["which_layer_needs_next_repair"]["answer"] = "public_release"
    result_json["visual_quality_assessment"]["design_quality_gate"] = "pass"
    result_json["visual_quality_assessment"]["top_blocker"] = "none"
    result_json["visual_quality_assessment"]["next_layer_to_fix"] = "public_release"
    first = result_json["role_assessments"][0]
    first["visual_grammar_module"] = "hero_field"
    first["text_visual_integration"] = "strong"
    first["root_cause_layer"] = "data_absence"
    first["repair_required"] = False
    first["trace_support"]["renderer_function_name"] = "drawRun287ProductTheaterSurface"
    first["trace_support"]["asset_surface_rendered"] = False
    first["trace_support"]["traceability_on_canvas"] = True
    result_json["root_cause_summary"]["primary_layer"] = "data_absence"
    result_json["no_new_renderer_proof"]["new_html_created"] = True
    result_json["next_required_action"] = "public_release"
    result_path.write_text(json.dumps(result_json, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_91_visual_quality_evaluation.creates_new_ppt_deck must be false" in result.errors
    assert "run2_91_visual_quality_evaluation.starts_renderer_rerun must be false" in result.errors
    assert "run2_91_visual_quality_evaluation.updates_html_viewer must be false" in result.errors
    assert "run2_91_visual_quality_evaluation.public_ready must be false" in result.errors
    assert "run2_91_visual_quality_evaluation.public_release_started must be false" in result.errors
    assert "run2_91_visual_quality_evaluation.source_runs.evaluated_run must be 2.90" in result.errors
    assert (
        "run2_91_visual_quality_evaluation.viewer_comparison_closure.viewer_latest_run_id must be 2.90"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.viewer_comparison_closure.run2_90_full_preview_count must be 6"
        in result.errors
    )
    assert "run2_91_visual_quality_evaluation.gemini_agent_review_summary.review_count must be 1" in result.errors
    assert (
        "run2_91_visual_quality_evaluation.evaluation_questions.did_2_90_integrate_text_with_visual_objects.answer must be no_text_visual_binding_still_weak"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.evaluation_questions.which_layer_needs_next_repair.answer must be object_bound_typography_and_text_visual_integration"
        in result.errors
    )
    assert "run2_91_visual_quality_evaluation.visual_quality_assessment.design_quality_gate must be blocked" in result.errors
    assert (
        "run2_91_visual_quality_evaluation.visual_quality_assessment.top_blocker must be text_blocks_and_product_surfaces_remain_parallel_not_integrated"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.visual_quality_assessment.next_layer_to_fix must be object_bound_typography_and_text_visual_integration"
        in result.errors
    )
    assert "run2_91_visual_quality_evaluation.role_assessments[0].visual_grammar_module must be product_reveal for cover" in result.errors
    assert (
        "run2_91_visual_quality_evaluation.role_assessments[0].text_visual_integration must be one of partial, weak"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.role_assessments[0].root_cause_layer must be one of caption_anchor_binding, composition_rhythm, object_bound_typography, proof_object_embedding, renderer_surface_materiality, text_visual_integration"
        in result.errors
    )
    assert "run2_91_visual_quality_evaluation.role_assessments[0].repair_required must be true" in result.errors
    assert (
        "run2_91_visual_quality_evaluation.role_assessments[0].trace_support.renderer_function_name must start with drawRun290"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.role_assessments[0].trace_support.asset_surface_rendered must be true"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.role_assessments[0].trace_support.traceability_on_canvas must be false"
        in result.errors
    )
    assert (
        "run2_91_visual_quality_evaluation.root_cause_summary.primary_layer must be object_bound_typography_and_text_visual_integration"
        in result.errors
    )
    assert "run2_91_visual_quality_evaluation.no_new_renderer_proof.new_html_created must be false" in result.errors
    assert (
        "run2_91_visual_quality_evaluation.next_required_action must be part_w_renderer_text_visual_binding_repair_from_v_evaluation"
        in result.errors
    )


def test_run2_profile_rejects_run2_7_unknown_visual_repair_policy_id(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    policy_path = pack / "run2_7_workflow_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["slide_role_memory_map"][0]["visual_repair_policy_ids"] = ["missing_repair_policy"]
    policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_7_workflow_policy.slide_role_memory_map[0].visual_repair_policy_ids references unknown visual repair policy: missing_repair_policy"
        in result.errors
    )


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


def test_run2_profile_rejects_run2_7_unknown_memory_source_record(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    memory_path = pack / "run2_7_design_memory.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    memory["memories"][0]["source_record_ids"] = ["missing_source_record"]
    memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_7_design_memory.memories[0].source_record_ids references unknown Run 2.7 source record: "
        "missing_source_record"
    ) in result.errors


def test_run2_profile_rejects_run2_7_empty_source_record_qa_gate(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    source_records_path = pack / "run2_7_multimodal_source_records.json"
    source_records = json.loads(source_records_path.read_text(encoding="utf-8"))
    source_records["qa_gates"] = ["contact sheet reviewed", ""]
    source_records_path.write_text(json.dumps(source_records, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_7_multimodal_source_records.qa_gates[1] must be a non-empty string" in result.errors


def test_run2_profile_rejects_run2_7_workflow_missing_trace_field(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    policy_path = pack / "run2_7_workflow_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["slide_role_memory_map"][0]["trace_fields"].remove("run2_7_quality_gate")
    policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_7_workflow_policy.slide_role_memory_map[0].trace_fields missing value: run2_7_quality_gate"
        in result.errors
    )


def test_run2_profile_rejects_run2_8_empty_decomposition_code_binding(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    write_minimal_run2_8_fixture(pack)
    decomposition_path = pack / "run2_8_tutorial_decomposition.json"
    decomposition = json.loads(decomposition_path.read_text(encoding="utf-8"))
    decomposition["units"][0]["code_generation_binding"] = ""
    decomposition_path.write_text(json.dumps(decomposition, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_8_tutorial_decomposition.units[0].code_generation_binding must be a non-empty string" in result.errors


def test_run2_profile_rejects_run2_8_unknown_decomposition_reference_in_memory(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    write_minimal_run2_8_fixture(pack)
    memory_path = pack / "run2_8_executable_design_memory.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    memory["bindings"][0]["decomposition_unit_ids"] = ["missing_decomposition_unit"]
    memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_8_executable_design_memory.bindings[0].decomposition_unit_ids references unknown "
        "Run 2.8 decomposition unit: missing_decomposition_unit"
    ) in result.errors


def test_run2_profile_rejects_run2_8_unknown_memory_binding_in_gate_matrix(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    write_minimal_run2_8_fixture(pack)
    matrix_path = pack / "run2_8_workflow_gate_matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["gates"][0]["memory_binding_ids"] = ["missing_memory_binding"]
    matrix_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_8_workflow_gate_matrix.gates[0].memory_binding_ids references unknown Run 2.8 memory binding: "
        "missing_memory_binding"
    ) in result.errors


def test_run2_profile_rejects_run2_8_trace_contract_missing_required_field(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    write_minimal_run2_8_fixture(pack)
    trace_path = pack / "results" / "trace_manifest_contract.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert "run2_8_memory_binding_ids" in trace["per_slide_required_fields"]
    trace["per_slide_required_fields"].remove("run2_8_memory_binding_ids")
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "trace_manifest_contract.per_slide_required_fields missing value: run2_8_memory_binding_ids" in result.errors


def test_run2_profile_rejects_run2_8_gate_without_id(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    matrix_path = pack / "run2_8_workflow_gate_matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["gates"][0].pop("id")
    matrix_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_8_workflow_gate_matrix.gates[0] missing key: id" in result.errors


def test_run2_profile_rejects_run2_8_gate_missing_required_trace_field(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    matrix_path = pack / "run2_8_workflow_gate_matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix["gates"][0]["trace_fields"].remove("run2_8_layout_budget")
    matrix_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "run2_8_workflow_gate_matrix.gates[0].trace_fields missing value: run2_8_layout_budget" in result.errors


def test_run2_profile_rejects_missing_run2_8_workflow_stage(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    workflow_path = pack / "skill_workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow["stages"] = [
        stage for stage in workflow["stages"] if stage["id"] != "decompose_run2_8_tutorial_video_units"
    ]
    for order, stage in enumerate(workflow["stages"], start=1):
        stage["order"] = order
    workflow_path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "skill_workflow.stages missing required Run 2.8 stage: decompose_run2_8_tutorial_video_units"
        in result.errors
    )


def test_run2_profile_rejects_run2_8_release_boundary_without_trace_gate(tmp_path: Path) -> None:
    pack = copy_run2_pack(tmp_path)
    memory_path = pack / "run2_8_executable_design_memory.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    memory["bindings"][0]["release_boundary"] = "public_blocked_until_native_render_and_human_review"
    memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_8_executable_design_memory.bindings[0].release_boundary must be "
        f"{RUN2_8_RELEASE_BOUNDARY}"
    ) in result.errors
