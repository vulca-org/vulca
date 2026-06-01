from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

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
        "select_visual_production_modules",
        "generate_code_first_ppt",
        "run_structural_and_aesthetic_qa",
        "recommend_repairs",
        "refresh_trace_qa_outcomes",
        "emit_release_decision",
    ]
    assert [stage["order"] for stage in workflow["stages"]] == list(range(1, 14))
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
    assert_contains(workflow_text, ["all required modalities covered", "no copied source media stored"])
    assert_contains(
        workflow_text, ["visual targets reference valid multimodal anchors", "selected visual learning targets"]
    )
    assert_contains(workflow_text, ["native visual components", "selected visual target components"])
    assert_contains(workflow_text, ["motion grammar", "selected motion targets", "sequence components"])
    assert_contains(workflow_text, ["production reference", "aesthetic memory v2", "visual production modules"])
    assert_contains(workflow_text, ["fallback", "visual validation"])
    assert_contains(workflow_text, ["schema validation", "aesthetic memory constraints"])
    assert_contains(workflow_text, ["provenance metadata", "copyright boundary"])
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
        ["Run 2.4", "motion grammar", "video_demo_beat_map", "presentation_sequence_components"],
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
    assert "video_beat_ids" in trace_contract["per_slide_required_fields"]
    assert "motion_target_ids" in trace_contract["per_slide_required_fields"]
    assert "sequence_component_ids" in trace_contract["per_slide_required_fields"]
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
