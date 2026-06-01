from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

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


def test_run2_four_arm_isolation_mentions_multimodal_and_target_boundaries() -> None:
    prompt_only = (PACK / "generation_briefs" / "prompt_only.md").read_text(encoding="utf-8")
    run1_5 = (PACK / "generation_briefs" / "run1_5_skill.md").read_text(encoding="utf-8")
    run2 = (PACK / "generation_briefs" / "run2_skill.md").read_text(encoding="utf-8")
    bad = (PACK / "generation_briefs" / "bad_aesthetic_memory.md").read_text(encoding="utf-8")

    assert_contains(
        prompt_only, ["Do not use multimodal database", "visual learning targets", "visual target components"]
    )
    assert_contains(
        run1_5,
        ["Do not use Run 2.2 multimodal database", "visual learning targets", "visual target components"],
    )
    assert_contains(run2, ["multimodal_database.json", "visual_learning_targets.json", "visual_target_components.json"])
    assert_contains(bad, ["multimodal_database.json", "visual_learning_targets.json", "visual_target_components.json"])
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
        "select_slide_archetypes",
        "generate_code_first_ppt",
        "run_structural_and_aesthetic_qa",
        "recommend_repairs",
        "refresh_trace_qa_outcomes",
        "emit_release_decision",
    ]
    assert [stage["order"] for stage in workflow["stages"]] == list(range(1, 11))
    assert workflow["repair_triggers"]
    workflow_text = json.dumps(workflow)
    assert "multimodal_database.json" in workflow_text
    assert "visual_learning_targets.json" in workflow_text
    assert "visual_target_components.json" in workflow_text
    assert_contains(workflow_text, ["all required modalities covered", "no copied source media stored"])
    assert_contains(
        workflow_text, ["visual targets reference valid multimodal anchors", "selected visual learning targets"]
    )
    assert_contains(workflow_text, ["native visual components", "selected visual target components"])
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
        ["multimodal database", "visual learning targets", "visual target components", "aesthetic memory"],
    )
    assert_contains(
        (PACK / "generation_briefs" / "bad_aesthetic_memory.md").read_text(encoding="utf-8"), ["negative control"]
    )


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

    assert_contains(comparison, ["Status", "rerun-reviewed-public-blocked"])
    assert_contains(comparison, ["prompt_only", "run1_5_skill", "run2_skill", "bad_aesthetic_memory"])
    assert_contains(
        comparison,
        ["Run 2.3", "run2_3_full_skill", "visual_component_execution", "native visual components"],
    )
    assert_contains(
        comparison,
        ["Run 2.2", "run2_2_full_skill", "multimodal_learning", "visual_learning_target_execution"],
    )
    assert_contains(comparison, ["Run 2.1", "run2_1_full_skill", "product learning", "not public-release claims"])
    assert "0.00" not in comparison
    assert_contains(delivery, ["public publishing", "blocked", "native render", "human approval", "trace manifest"])
    assert_contains(delivery, ["Run 2.3", "pass for local Run 2.3 arms", "native visual components"])
    assert_contains(delivery, ["Run 2.2", "run2-2-four-arm-contact-sheet", "public-video-grade visual proof"])
    assert trace_contract["required_output_name"] == "trace_manifest.json"
    assert "aesthetic_move_ids" in trace_contract["per_slide_required_fields"]
    assert "visual_component_ids" in trace_contract["per_slide_required_fields"]
    assert "runtime_isolation" in trace_contract["arm_required_fields"]
    assert "native_ppt_checks" in trace_contract["per_slide_required_fields"]
    assert "layout_geometry_checks" in trace_contract["per_slide_required_fields"]
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
