from __future__ import annotations

import json
import re
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


def normalize_markdown_text(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def markdown_section(body: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(body)
    assert match is not None, f"missing section: {heading}"
    next_heading = re.search(r"^##\s+", body[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(body)
    return body[match.end() : end]


def assert_contains_terms(body: str, required_terms: list[str]) -> None:
    normalized = normalize_markdown_text(body)
    for term in required_terms:
        assert normalize_markdown_text(term) in normalized


def assert_contains_keyword_groups(body: str, required_groups: list[list[str]]) -> None:
    normalized = normalize_markdown_text(body)
    for group in required_groups:
        missing = [term for term in group if normalize_markdown_text(term) not in normalized]
        assert missing == [], f"missing concept terms: {missing}"


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

    required_concepts = [
        ["10-slide", "product launch"],
        ["generic", "AI", "presentation generation"],
        ["real design references"],
        ["reusable skills"],
        ["editable PPT", "code"],
        ["Gemini", "visual quality"],
        ["builders", "designers", "platform reviewers"],
        ["premium", "modern", "product launch video"],
    ]

    assert_contains_keyword_groups(prompt, required_concepts)


def test_vulca_generation_brief_defines_editable_case_pack_constraints() -> None:
    brief = (PACK / "vulca_generation_brief.md").read_text(encoding="utf-8")

    required_inputs = [
        "`commercial_brief.md`",
        "`design_notes.md`",
        "`narrative_rules.json`",
        "`slide_patterns.json`",
        "`style_tokens.json`",
        "`asset_rules.json`",
        "`deck_outline.json`",
        "`evaluation_rubric.md`",
    ]
    required_constraints = [
        ["artifact-tool", "presentation JSX", "editable PPTX"],
        ["one slide module", "per slide"],
        ["titles", "body copy", "labels", "diagram text", "editable"],
        ["native shapes", "editable SVG", "diagrams"],
        ["bitmap images", "text"],
        ["copy", "reference-case visuals"],
        ["warm-neutral base", "signal accents", "style_tokens.json"],
        ["generic dark-blue AI SaaS palette"],
        ["one claim", "one proof object"],
        ["rendered previews", "layout JSON", "contact sheet"],
    ]

    assert_contains_terms(markdown_section(brief, "Required Inputs"), required_inputs)
    assert_contains_keyword_groups(markdown_section(brief, "Design Constraints"), required_constraints)


def test_vulca_generation_brief_requires_asset_provenance_output() -> None:
    asset_rules = load_json(PACK / "asset_rules.json")
    brief = (PACK / "vulca_generation_brief.md").read_text(encoding="utf-8")
    expected_output = markdown_section(brief, "Expected Output")

    if asset_rules["provenance_required"]:
        assert_contains_terms(
            expected_output,
            [
                "asset provenance",
                "results asset_provenance json",
                "prompt",
                "license",
                "source status",
            ],
        )

    preferred_assets = " ".join(asset_rules["preferred_assets"])
    if "generated" in preferred_assets:
        assert_contains_terms(expected_output, ["generated", "bitmap", "prompt"])
    if "svg" in preferred_assets:
        assert_contains_terms(expected_output, ["SVG", "prompt"])


def test_gemini_review_prompt_defines_scores_and_outputs() -> None:
    prompt = (PACK / "gemini_review_prompt.md").read_text(encoding="utf-8")
    required_output_terms = [
        "score table",
        "numeric 0-5 score",
        "three highest-priority design issues",
        "three slide-specific fixes",
        "editability risks",
        "accessibility",
        "cross-platform rendering risks",
        "video-demo ready",
        "stronger than a prompt-only deck",
    ]

    assert_contains_terms(prompt, required_output_terms)


def test_gemini_review_prompt_scores_every_required_dimension() -> None:
    prompt = (PACK / "gemini_review_prompt.md").read_text(encoding="utf-8")
    rubric = (PACK / "evaluation_rubric.md").read_text(encoding="utf-8")
    rubric_dimensions = [
        heading
        for heading in re.findall(r"^## (.+)$", rubric, flags=re.MULTILINE)
        if heading != "Evaluation Rubric"
    ]
    additional_score_dimensions = [
        "premium versus template-like feel",
        "reference-case alignment without copying",
    ]

    assert_contains_terms(prompt, rubric_dimensions + additional_score_dimensions)


def test_gemini_review_prompt_requires_numeric_scores() -> None:
    prompt = normalize_markdown_text((PACK / "gemini_review_prompt.md").read_text(encoding="utf-8"))

    assert "score 0 5" in prompt
    assert "numeric 0 5 score" in prompt
    assert "score table" in prompt
