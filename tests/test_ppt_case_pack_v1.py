from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-case-pack-v1"
REQUIRED_PATTERN_IDS = {
    "cover",
    "problem",
    "market_shift",
    "workflow",
    "product_pillars",
    "case_pack_method",
    "proof",
    "comparison",
    "roadmap",
    "closing",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_ppt_case_pack_v1_is_valid() -> None:
    result = validate_case_pack(PACK)

    assert result.ok is True, result.errors


def test_deck_outline_contains_full_ten_slide_sequence() -> None:
    outline = load_json(PACK / "deck_outline.json")

    pattern_ids = [slide["pattern_id"] for slide in outline["slides"]]

    assert len(outline["slides"]) == 10
    assert pattern_ids == [
        "cover",
        "problem",
        "market_shift",
        "workflow",
        "product_pillars",
        "case_pack_method",
        "proof",
        "comparison",
        "roadmap",
        "closing",
    ]


def test_deck_outline_uses_defined_slide_patterns() -> None:
    outline = load_json(PACK / "deck_outline.json")
    patterns = load_json(PACK / "slide_patterns.json")

    defined_pattern_ids = {pattern["id"] for pattern in patterns["patterns"]}
    outline_pattern_ids = {slide["pattern_id"] for slide in outline["slides"]}

    assert outline_pattern_ids <= defined_pattern_ids


def test_all_required_slide_patterns_exist() -> None:
    patterns = load_json(PACK / "slide_patterns.json")

    pattern_ids = {pattern["id"] for pattern in patterns["patterns"]}

    assert REQUIRED_PATTERN_IDS <= pattern_ids


def test_source_summaries_mentions_every_source_id() -> None:
    sources = load_json(PACK / "sources.json")
    summaries = (PACK / "source_summaries.md").read_text(encoding="utf-8")

    for source in sources["sources"]:
        assert source["id"] in summaries


def test_asset_provenance_record_exists() -> None:
    provenance = load_json(PACK / "results" / "asset_provenance.json")

    assert provenance["schema_version"] == 1
    assert provenance["status"] == "not-run"
    assert provenance["assets"] == []
