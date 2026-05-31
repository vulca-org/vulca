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


def test_product_pillars_pattern_matches_five_pillar_outline() -> None:
    outline = load_json(PACK / "deck_outline.json")
    patterns = load_json(PACK / "slide_patterns.json")

    product_pillars_slide = next(slide for slide in outline["slides"] if slide["pattern_id"] == "product_pillars")
    product_pillars_pattern = next(pattern for pattern in patterns["patterns"] if pattern["id"] == "product_pillars")

    assert "Five pillars" in product_pillars_slide["proof_object"]
    assert "five_pillars" in product_pillars_pattern["layout_shape"]


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


def test_baseline_prompt_defines_launch_deck_request() -> None:
    prompt = (PACK / "baseline_prompt.md").read_text(encoding="utf-8")

    required_phrases = [
        "Create a 10-slide product launch presentation for Vulca.",
        "the problem with generic AI presentation generation",
        "how Vulca uses real design references",
        "how Vulca turns design knowledge into reusable skills",
        "how Vulca generates editable PPT content mostly through code",
        "how Gemini reviews visual quality",
        "builders, designers, and platform reviewers",
        "premium, modern, and suitable for a product launch video",
    ]

    for phrase in required_phrases:
        assert phrase in prompt


def test_vulca_generation_brief_defines_editable_case_pack_constraints() -> None:
    brief = (PACK / "vulca_generation_brief.md").read_text(encoding="utf-8")

    required_phrases = [
        "`commercial_brief.md`",
        "`design_notes.md`",
        "`narrative_rules.json`",
        "`slide_patterns.json`",
        "`style_tokens.json`",
        "`asset_rules.json`",
        "`deck_outline.json`",
        "`evaluation_rubric.md`",
        "Use artifact-tool presentation JSX for editable PPTX generation.",
        "Use one slide module per slide.",
        "Keep all titles, body copy, labels, and diagram text editable.",
        "Use native shapes or editable SVG for diagrams.",
        "Do not use bitmap images for text.",
        "Do not copy reference-case visuals.",
        "Use a restrained warm-neutral base with signal accents from `style_tokens.json`.",
        "Avoid a generic dark-blue AI SaaS palette.",
        "Each slide must include one claim and one proof object.",
        "Generate rendered previews, layout JSON, and a contact sheet before review.",
    ]

    for phrase in required_phrases:
        assert phrase in brief


def test_gemini_review_prompt_defines_scores_and_outputs() -> None:
    prompt = (PACK / "gemini_review_prompt.md").read_text(encoding="utf-8")

    required_phrases = [
        "Score 0-5:",
        "commercial clarity",
        "narrative flow",
        "technical understandability",
        "visual hierarchy",
        "brand coherence",
        "cultural/design intent",
        "slide-to-slide consistency",
        "premium versus template-like feel",
        "editability risk visible from screenshots",
        "reference-case alignment without copying",
        "three highest-priority design issues",
        "three slide-specific fixes",
        "whether the deck is video-demo ready",
        "whether it looks materially stronger than a prompt-only deck",
    ]

    for phrase in required_phrases:
        assert phrase in prompt
