from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run1-5-product-lab"
EXPECTED_ARMS = {"prompt_only", "full_vulca", "bad_data"}
EXPECTED_PRIMITIVES = {"cockpit", "learning_map", "comparison_delta", "qa_gate", "decision_table"}
EXPECTED_PATTERN_IDS = [
    "experiment_cover",
    "brief_cockpit",
    "source_tutorial_intake",
    "design_memory_compiler",
    "skill_workflow_surface",
    "code_generation_anatomy",
    "baseline_vs_vulca",
    "ablation_proof",
    "qa_publish_gate",
    "product_decision",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def assert_contains(body: str, terms: list[str]) -> None:
    normalized = normalize(body)
    for term in terms:
        assert normalize(term) in normalized


def test_run1_5_case_pack_is_valid() -> None:
    result = validate_case_pack(PACK, profile="run1_5")

    assert result.ok is True, result.errors


def test_run1_5_experiment_protocol_has_three_blocking_arms() -> None:
    protocol = load_json(PACK / "experiment_protocol.md.json")

    assert len(protocol["arms"]) == 3
    assert {arm["id"] for arm in protocol["arms"]} == EXPECTED_ARMS
    assert all(arm["blocking"] is True for arm in protocol["arms"])
    assert protocol["deferred_arms"] == ["source_only", "tutorial_only"]


def test_prompt_only_arm_forbids_vulca_specific_inputs() -> None:
    protocol = load_json(PACK / "experiment_protocol.md.json")
    prompt_only = next(arm for arm in protocol["arms"] if arm["id"] == "prompt_only")

    assert set(prompt_only["forbidden_inputs"]) >= {
        "design_memory.json",
        "tutorial_notes.md",
        "vulca_generation_brief.md",
        "vulca_ppt_skill.md",
    }


def test_run1_5_design_memory_uses_strict_contract() -> None:
    memory = load_json(PACK / "design_memory.json")

    assert memory["schema_version"] == 2
    assert set(memory["contract"]["allowed_slide_primitives"]) == EXPECTED_PRIMITIVES
    assert len(memory["observations"]) >= 5
    for observation in memory["observations"]:
        assert observation["slide_primitive"] in EXPECTED_PRIMITIVES
        assert observation["source_role"] in {"brief", "source", "tutorial", "review"}
        assert_contains(observation["design_rule"], ["use"])
        assert_contains(observation["layout_constraint"], ["slide"])
        assert_contains(observation["qa_signal"], ["review"])
        assert_contains(observation["do_not_copy"], ["do not copy"])


def test_run1_5_deck_outline_uses_product_lab_sequence() -> None:
    outline = load_json(PACK / "deck_outline.json")

    assert [slide["pattern_id"] for slide in outline["slides"]] == EXPECTED_PATTERN_IDS
    assert len(outline["slides"]) == 10
    assert outline["slides"][1]["proof_object"].lower().count("brief") >= 1
    assert outline["slides"][7]["proof_object"].lower().count("bad-data") >= 1


def test_run1_5_generation_briefs_define_separate_arms() -> None:
    baseline = (PACK / "baseline_prompt.md").read_text(encoding="utf-8")
    full_vulca = (PACK / "vulca_generation_brief.md").read_text(encoding="utf-8")
    bad_data = (PACK / "bad_data_generation_brief.md").read_text(encoding="utf-8")

    assert_contains(baseline, ["prompt-only", "do not use design memory"])
    assert_contains(full_vulca, ["full Vulca", "design memory", "product lab"])
    assert_contains(bad_data, ["bad-data", "corrupted rules", "negative control"])


def test_run1_5_results_reviewed_and_public_blocked() -> None:
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    comparison_json = load_json(PACK / "results" / "comparison_report.json")
    ablation = (PACK / "results" / "ablation_report.md").read_text(encoding="utf-8")
    ablation_json = load_json(PACK / "results" / "ablation_report.json")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")

    assert_contains(comparison, ["Status", "reviewed-public-blocked"])
    assert comparison_json["status"] == "reviewed-public-blocked"
    assert_contains(ablation, ["prompt-only", "full Vulca", "bad-data", "Gemini review is qualitative evidence"])
    assert ablation_json["status"] == "reviewed"
    assert_contains(delivery, ["Public publishing", "blocked"])


def test_run1_5_pack_does_not_commit_generated_artifacts() -> None:
    blocked_suffixes = {".jpeg", ".jpg", ".mp4", ".pdf", ".png", ".pptx"}
    blocked = [
        str(path.relative_to(PACK))
        for path in PACK.rglob("*")
        if path.is_file() and path.suffix.lower() in blocked_suffixes
    ]

    assert blocked == []
