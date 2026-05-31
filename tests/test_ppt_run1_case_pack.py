from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run1-ai-presentation-launch"
EXPECTED_SOURCE_IDS = {
    "geo_figma_slides",
    "figma_config_2024",
    "figma_config_2025_identity",
    "supervity_ai_keynote",
}
EXPECTED_PATTERN_IDS = [
    "cover",
    "problem",
    "reference_shift",
    "workflow",
    "design_memory",
    "code_generation",
    "review_loop",
    "comparison",
    "product_decision",
    "closing",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def assert_contains(body: str, terms: list[str]) -> None:
    normalized = normalize(body)
    for term in terms:
        assert normalize(term) in normalized


def test_run1_case_pack_is_valid() -> None:
    result = validate_case_pack(PACK, profile="run1")

    assert result.ok is True, result.errors


def test_run1_sources_are_reference_analysis_only() -> None:
    data = load_json(PACK / "sources.json")

    ids = {source["id"] for source in data["sources"]}
    assert ids == EXPECTED_SOURCE_IDS
    for source in data["sources"]:
        assert source["allowed_use"] == "reference_analysis_only"
        assert source["url"].startswith("https://")
        assert "do not copy" in source["copyright_note"].lower()


def test_run1_deck_outline_uses_exact_pattern_sequence() -> None:
    outline = load_json(PACK / "deck_outline.json")

    assert [slide["pattern_id"] for slide in outline["slides"]] == EXPECTED_PATTERN_IDS
    assert len(outline["slides"]) == 10


def test_run1_design_memory_is_source_grounded() -> None:
    memory = load_json(PACK / "design_memory.json")
    source_ids = {source["id"] for source in load_json(PACK / "sources.json")["sources"]}

    assert len(memory["observations"]) >= 6
    for observation in memory["observations"]:
        assert set(observation["source_ids"]) <= source_ids
        assert_contains(observation["do_not_copy"], ["do not copy"])
        assert_contains(observation["code_generation_rule"], ["editable"])


def test_run1_prompts_keep_code_generation_primary() -> None:
    generation = (PACK / "vulca_generation_brief.md").read_text(encoding="utf-8")
    baseline = (PACK / "baseline_prompt.md").read_text(encoding="utf-8")

    assert_contains(generation, ["code-generated PPT", "editable", "native shapes", "layout JSON"])
    assert_contains(generation, ["image generation", "auxiliary"])
    assert_contains(baseline, ["prompt-only baseline", "10-slide", "product launch deck"])


def test_run1_results_start_as_not_run() -> None:
    provenance = load_json(PACK / "results" / "asset_provenance.json")
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    render_check = (PACK / "results" / "render_check.md").read_text(encoding="utf-8")
    iteration_log = (PACK / "results" / "iteration_log.md").read_text(encoding="utf-8")

    assert provenance["status"] == "not-run"
    assert provenance["assets"] == []
    assert_contains(comparison, ["Status", "not generated"])
    assert_contains(render_check, ["Renderer", "not checked"])
    assert_contains(iteration_log, ["Repair pass", "not started"])
