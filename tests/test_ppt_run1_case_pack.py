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
EXPECTED_SOURCE_URLS = {
    "geo_figma_slides": "https://geo-nyc.com/projects/figma-slides/",
    "figma_config_2024": "https://www.figma.com/blog/config-2024-recap/",
    "figma_config_2025_identity": "https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/",
    "supervity_ai_keynote": "https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/",
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
GENERATED_ARTIFACT_DIRS = {
    "artifacts",
    "contact_sheets",
    "generated",
    "generated_artifacts",
    "presentations",
    "rendered",
    "renders",
}
GENERATED_ARTIFACT_SUFFIXES = {".jpeg", ".jpg", ".mp4", ".pdf", ".png", ".pptx"}


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


def test_run1_sources_use_canonical_urls() -> None:
    data = load_json(PACK / "sources.json")

    urls_by_id = {source["id"]: source["url"] for source in data["sources"]}
    assert urls_by_id == EXPECTED_SOURCE_URLS


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


def test_run1_generation_brief_requires_artifact_outputs() -> None:
    brief = (PACK / "vulca_generation_brief.md").read_text(encoding="utf-8")

    assert_contains(
        brief,
        [
            "PPTX",
            "contact sheet",
            "layout JSON",
            "asset provenance",
            "iteration log",
            "renderer availability",
        ],
    )


def test_run1_gemini_prompt_is_not_final_approval() -> None:
    prompt = (PACK / "gemini_review_prompt.md").read_text(encoding="utf-8")

    assert_contains(prompt, ["not final approval", "human review", "numeric zero-through-five score"])


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


def test_run1_pack_does_not_commit_generated_artifacts() -> None:
    blocked: list[str] = []
    for path in PACK.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(PACK)
        suffix = path.suffix.lower()
        if suffix in GENERATED_ARTIFACT_SUFFIXES:
            blocked.append(str(rel_path))
            continue
        in_generated_dir = any(part in GENERATED_ARTIFACT_DIRS for part in rel_path.parts[:-1])
        if in_generated_dir and suffix == ".json" and "layout" in path.stem.lower():
            blocked.append(str(rel_path))

    assert blocked == []
