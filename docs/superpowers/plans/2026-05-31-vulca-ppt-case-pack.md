# Vulca PPT Case Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first Vulca PPT case pack and use it to produce a baseline-vs-Vulca product launch deck comparison.

**Architecture:** The case pack lives under `docs/product/ppt-case-pack-v1/` as structured source notes, design rules, slide patterns, and evaluation criteria. Repository scripts validate the case pack and generation inputs; actual deck creation uses the bundled Presentations artifact-tool runtime in `outputs/$THREAD_ID/presentations/`, with final reports copied back into the case-pack result folder only after QA.

**Tech Stack:** Python stdlib for case-pack validation, pytest for tests, Codex bundled Node runtime plus `@oai/artifact-tool/presentation-jsx` for PPTX generation, Gemini-agent for visual review.

---

## File Map

- Create `scripts/validate_ppt_case_pack.py`: validates required files, JSON shape, source-use constraints, slide-pattern references, and result manifest shape.
- Create `tests/test_ppt_case_pack_validator.py`: unit tests for the validator using temporary case-pack fixtures.
- Create `tests/test_ppt_case_pack_v1.py`: repository test that validates the real `docs/product/ppt-case-pack-v1/` pack.
- Create `docs/product/ppt-case-pack-v1/README.md`: human entry point for the case pack.
- Create `docs/product/ppt-case-pack-v1/sources.json`: public reference registry with copyright and usage notes.
- Create `docs/product/ppt-case-pack-v1/source_summaries.md`: short original summaries and why each reference matters.
- Create `docs/product/ppt-case-pack-v1/commercial_brief.md`: real business/design need for the Vulca launch deck.
- Create `docs/product/ppt-case-pack-v1/design_notes.md`: original design analysis from the reference set.
- Create `docs/product/ppt-case-pack-v1/narrative_rules.json`: reusable story rules.
- Create `docs/product/ppt-case-pack-v1/slide_patterns.json`: slide-role grammar and layout constraints.
- Create `docs/product/ppt-case-pack-v1/style_tokens.json`: code-friendly design system.
- Create `docs/product/ppt-case-pack-v1/asset_rules.json`: SVG/image/editability rules.
- Create `docs/product/ppt-case-pack-v1/evaluation_rubric.md`: scoring rubric for commercial and design quality.
- Create `docs/product/ppt-case-pack-v1/vulca_ppt_skill.md`: first reusable prompt/skill draft for Vulca PPT generation.
- Create `docs/product/ppt-case-pack-v1/deck_outline.json`: exact 10-slide Vulca product launch deck outline.
- Create `docs/product/ppt-case-pack-v1/baseline_prompt.md`: ordinary prompt used to generate the baseline deck.
- Create `docs/product/ppt-case-pack-v1/vulca_generation_brief.md`: case-pack-informed prompt and generation constraints.
- Create `docs/product/ppt-case-pack-v1/gemini_review_prompt.md`: compact review prompt for Gemini visual QA.
- Create `docs/product/ppt-case-pack-v1/results/README.md`: where final outputs and comparison records are documented.
- Create `docs/product/ppt-case-pack-v1/results/comparison_report.md`: baseline vs Vulca evaluation record after decks are generated.

---

### Task 1: Case-Pack Validator

**Files:**
- Create: `scripts/validate_ppt_case_pack.py`
- Create: `tests/test_ppt_case_pack_validator.py`

- [ ] **Step 1: Write validator unit tests**

Create `tests/test_ppt_case_pack_validator.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.validate_ppt_case_pack'`.

- [ ] **Step 3: Implement the validator**

Create `scripts/validate_ppt_case_pack.py`:

```python
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "README.md",
    "sources.json",
    "source_summaries.md",
    "commercial_brief.md",
    "design_notes.md",
    "narrative_rules.json",
    "slide_patterns.json",
    "style_tokens.json",
    "asset_rules.json",
    "evaluation_rubric.md",
    "vulca_ppt_skill.md",
    "deck_outline.json",
    "baseline_prompt.md",
    "vulca_generation_brief.md",
    "gemini_review_prompt.md",
    "results/README.md",
    "results/comparison_report.md",
]


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} is not valid JSON: {exc.msg}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a JSON object")
        return {}
    return value


def require_keys(label: str, value: dict[str, Any], keys: list[str], errors: list[str]) -> None:
    for key in keys:
        if key not in value:
            errors.append(f"{label} missing key: {key}")


def validate_sources(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "sources.json", errors)
    require_keys("sources.json", data, ["schema_version", "sources"], errors)
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("sources.json sources must be a non-empty list")
        return
    required = ["id", "title", "url", "role", "accessed_on", "allowed_use", "copyright_note"]
    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        require_keys(f"sources[{index}]", source, required, errors)
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in seen_ids:
                errors.append(f"sources[{index}].id duplicates {source_id}")
            seen_ids.add(source_id)
        url = source.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"sources[{index}].url must be https")
        if source.get("allowed_use") != "reference_analysis_only":
            errors.append(f"sources[{index}].allowed_use must be reference_analysis_only")
        note = str(source.get("copyright_note", "")).lower()
        if "copy" not in note and "proprietary" not in note:
            errors.append(f"sources[{index}].copyright_note must mention copy or proprietary limits")


def validate_narrative_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "narrative_rules.json", errors)
    require_keys("narrative_rules.json", data, ["schema_version", "opening", "progression", "technical_depth", "closing"], errors)
    progression = data.get("progression", [])
    if not isinstance(progression, list) or len(progression) < 5:
        errors.append("narrative_rules.progression must include at least five stages")


def validate_style_tokens(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "style_tokens.json", errors)
    require_keys("style_tokens.json", data, ["schema_version", "palette", "font_stack", "spacing", "corner_radius", "stroke_widths"], errors)
    font_stack = data.get("font_stack", [])
    if not isinstance(font_stack, list) or len(font_stack) < 3:
        errors.append("style_tokens.font_stack must include at least three fonts")
    palette = data.get("palette", {})
    if not isinstance(palette, dict) or len(palette) < 3:
        errors.append("style_tokens.palette must include at least three colors")


def validate_asset_rules(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_rules.json", errors)
    require_keys("asset_rules.json", data, ["schema_version", "preferred_assets", "bitmap_use", "forbidden", "provenance_required"], errors)
    forbidden = data.get("forbidden", [])
    if "rasterized_text" not in forbidden:
        errors.append("asset_rules.forbidden must include rasterized_text")
    if data.get("provenance_required") is not True:
        errors.append("asset_rules.provenance_required must be true")


def validate_slide_patterns(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "slide_patterns.json", errors)
    require_keys("slide_patterns.json", data, ["schema_version", "patterns"], errors)
    patterns = data.get("patterns", [])
    if not isinstance(patterns, list) or not patterns:
        errors.append("slide_patterns.patterns must be a non-empty list")
        return set()
    required = ["id", "role", "content_density", "layout_shape", "visual_asset_type", "editability_requirements"]
    ids: set[str] = set()
    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            errors.append(f"slide_patterns.patterns[{index}] must be an object")
            continue
        require_keys(f"slide_patterns.patterns[{index}]", pattern, required, errors)
        pattern_id = pattern.get("id")
        if isinstance(pattern_id, str):
            ids.add(pattern_id)
        requirements = pattern.get("editability_requirements", [])
        if not isinstance(requirements, list) or not requirements:
            errors.append(f"slide_patterns.patterns[{index}].editability_requirements must be non-empty")
    return ids


def validate_deck_outline(pack_dir: Path, pattern_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "deck_outline.json", errors)
    require_keys("deck_outline.json", data, ["schema_version", "title", "slides"], errors)
    slides = data.get("slides", [])
    if not isinstance(slides, list) or not slides:
        errors.append("deck_outline.slides must be a non-empty list")
        return
    required = ["id", "pattern_id", "title", "claim", "proof_object"]
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            errors.append(f"deck_outline.slides[{index}] must be an object")
            continue
        require_keys(f"deck_outline.slides[{index}]", slide, required, errors)
        pattern_id = slide.get("pattern_id")
        if isinstance(pattern_id, str) and pattern_id not in pattern_ids:
            errors.append(f"deck_outline.slides[{index}].pattern_id {pattern_id} is not defined in slide_patterns.json")


def validate_markdown_not_empty(pack_dir: Path, errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not rel.endswith(".md"):
            continue
        path = pack_dir / rel
        if path.exists() and len(path.read_text(encoding="utf-8").strip()) < 20:
            errors.append(f"{rel} must contain at least 20 non-whitespace characters")


def validate_case_pack(pack_dir: str | Path) -> ValidationResult:
    root = Path(pack_dir)
    errors: list[str] = []
    if not root.exists():
        return ValidationResult(False, [f"case pack directory does not exist: {root}"])
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")
    if errors:
        return ValidationResult(False, errors)
    validate_sources(root, errors)
    validate_narrative_rules(root, errors)
    validate_style_tokens(root, errors)
    validate_asset_rules(root, errors)
    pattern_ids = validate_slide_patterns(root, errors)
    validate_deck_outline(root, pattern_ids, errors)
    validate_markdown_not_empty(root, errors)
    return ValidationResult(not errors, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Vulca PPT case pack.")
    parser.add_argument("pack_dir", type=Path)
    args = parser.parse_args()
    result = validate_case_pack(args.pack_dir)
    if result.ok:
        print(f"case pack ok: {args.pack_dir}")
        return 0
    for error in result.errors:
        print(f"error: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run validator tests**

Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: PASS, `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git commit -m "test: add PPT case pack validator"
```

---

### Task 2: Case-Pack Source Registry And Core Rules

**Files:**
- Create: `docs/product/ppt-case-pack-v1/README.md`
- Create: `docs/product/ppt-case-pack-v1/sources.json`
- Create: `docs/product/ppt-case-pack-v1/source_summaries.md`
- Create: `docs/product/ppt-case-pack-v1/commercial_brief.md`
- Create: `docs/product/ppt-case-pack-v1/design_notes.md`
- Create: `docs/product/ppt-case-pack-v1/narrative_rules.json`
- Create: `docs/product/ppt-case-pack-v1/slide_patterns.json`
- Create: `docs/product/ppt-case-pack-v1/style_tokens.json`
- Create: `docs/product/ppt-case-pack-v1/asset_rules.json`
- Create: `docs/product/ppt-case-pack-v1/evaluation_rubric.md`
- Create: `docs/product/ppt-case-pack-v1/vulca_ppt_skill.md`
- Create: `docs/product/ppt-case-pack-v1/deck_outline.json`
- Create: `docs/product/ppt-case-pack-v1/baseline_prompt.md`
- Create: `docs/product/ppt-case-pack-v1/vulca_generation_brief.md`
- Create: `docs/product/ppt-case-pack-v1/gemini_review_prompt.md`
- Create: `docs/product/ppt-case-pack-v1/results/README.md`
- Create: `docs/product/ppt-case-pack-v1/results/comparison_report.md`
- Create: `tests/test_ppt_case_pack_v1.py`

- [ ] **Step 1: Write repository contract test**

Create `tests/test_ppt_case_pack_v1.py`:

```python
from __future__ import annotations

from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-case-pack-v1"


def test_ppt_case_pack_v1_is_valid() -> None:
    result = validate_case_pack(PACK)

    assert result.ok is True, result.errors
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_v1.py -q
```

Expected: FAIL with `case pack directory does not exist`.

- [ ] **Step 3: Create `sources.json`**

Create `docs/product/ppt-case-pack-v1/sources.json`:

```json
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
      "copyright_note": "Use for original analysis of B2B AI keynote goals and visual quality. Do not copy proprietary visuals, layouts, screenshots, or full text."
    },
    {
      "id": "figma_config_2025_identity",
      "title": "How Figma Shaped the Visual Identity for Config 2025",
      "url": "https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/",
      "role": "visual_system_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of product-launch identity systems. Do not copy proprietary visuals, event artwork, or article text."
    },
    {
      "id": "figma_slides_geo",
      "title": "Figma Slides Case by GEO",
      "url": "https://geo-nyc.com/projects/figma-slides/",
      "role": "product_slide_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of presentation-product launch framing. Do not copy proprietary images, layouts, or campaign copy."
    },
    {
      "id": "launch_labs_sales_deck",
      "title": "Launch Labs Presentation Case",
      "url": "https://www.whitepage.studio/portfolio/launch-lab",
      "role": "commercial_deck_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of sales-deck clarity and modularity. Do not copy proprietary slides, visuals, or client materials."
    },
    {
      "id": "google_cloud_next_keynote",
      "title": "Google Cloud Next Keynote Case",
      "url": "https://www.wearesparks.com/our-work/google-cloud-next/",
      "role": "high_end_keynote_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of large-scale technology keynote production. Do not copy proprietary stage visuals, branding, or event assets."
    }
  ]
}
```

- [ ] **Step 4: Create core markdown files**

Create `docs/product/ppt-case-pack-v1/README.md`:

```markdown
# Vulca PPT Case Pack v1

This pack turns public commercial presentation references into reusable Vulca PPT design knowledge. It is not a training dataset and does not contain copied reference slides, full article text, video transcripts, or proprietary assets.

The pack supports one first deliverable: a Vulca Product Launch Deck generated mostly through editable presentation code, with SVG and generated bitmap assets used only as supporting visuals.

Primary use:

```text
sources -> original analysis -> rules/tokens/patterns -> deck outline -> baseline/Vulca generation -> Gemini review -> comparison report
```
```

Create `docs/product/ppt-case-pack-v1/source_summaries.md`:

```markdown
# Source Summaries

## Supervity AI Presentation Case

Role: main commercial reference.

Why it matters: this is the closest reference for a B2B AI presentation that must turn technical complexity into executive confidence. The case is useful for studying commercial clarity, premium tone, and how an AI product can be positioned without becoming a generic feature list.

Use boundary: use only as reference analysis. Do not copy slides, layouts, images, or full prose.

## Figma Config 2025 Identity

Role: visual system reference.

Why it matters: this reference shows how a product/event identity can create a coherent launch world through typography, shape behavior, color, motion logic, and design-system constraints.

Use boundary: use only as reference analysis. Do not copy event artwork or proprietary identity assets.

## Figma Slides Case by GEO

Role: product-slide reference.

Why it matters: this reference is directly relevant to presentation software and helps anchor the deck in user confidence, craft, and editable communication rather than raw image generation.

Use boundary: use only as reference analysis. Do not copy campaign visuals or page layouts.

## Launch Labs Presentation Case

Role: commercial deck reference.

Why it matters: this reference provides a sales-deck lens: the deck must explain value, support conversion, remain editable, and avoid overdesigned pages that cannot survive real business use.

Use boundary: use only as reference analysis. Do not copy client slides or assets.

## Google Cloud Next Keynote Case

Role: high-end keynote reference.

Why it matters: this reference sets the upper bound for enterprise technology launch polish, multi-audience storytelling, and consistent visual grammar across a large event narrative.

Use boundary: use only as reference analysis. Do not copy Google event visuals, marks, or stage design.
```

Create `docs/product/ppt-case-pack-v1/commercial_brief.md`:

```markdown
# Commercial Brief

## Audience

Builders, designers, AI platform reviewers, and early technical adopters who understand presentation tools but need to see why Vulca is different from a one-shot deck generator.

## Decision The Deck Must Win

The audience should believe Vulca can turn real design knowledge into repeatable, editable presentation code, and that this workflow is more defensible than prompt-only deck generation.

## Business Context

The deck supports a product-launch narrative for Vulca's PPT wedge. It is meant to be used in a demo video, product page, and platform-review context.

## Design Need

The deck must feel commercially credible, not like a generic SaaS template. It needs a clear claim spine, visible design system, restrained visual language, and proof that the output remains editable.

## Technical Complexity

Medium-high. The deck must explain case packs, skills, code generation, auxiliary assets, Gemini review, and layout QA without turning into an engineering architecture document.

## Emotional Tone

Precise, premium, controlled, culturally aware, and builder-oriented.

## Call To Action

Run the Vulca PPT workflow on a real commercial deck need, compare it against a prompt-only baseline, and decide which slide primitives should become product features.
```

Create `docs/product/ppt-case-pack-v1/design_notes.md`:

```markdown
# Design Notes

## Shared Lessons From The References

The references suggest a launch deck should not be a grid of feature cards. It needs a clear story arc, strong section rhythm, and proof objects that make the system tangible.

## Narrative

Lead with the workflow problem: teams can generate slides quickly, but the result often lacks design reasoning, commercial fit, and editable structure. Introduce Vulca as the layer that turns references and design rules into code-generated presentation systems.

## Information Hierarchy

Each slide should carry one claim. Supporting text should be short. Diagrams should replace long explanations when the audience needs to understand process, architecture, or evaluation.

## Visual Rhythm

Alternate between high-impact claim slides, structured diagrams, comparison pages, and proof/result pages. Avoid ten slides with the same card-grid layout.

## Typography

Use a system-safe font stack so the deck survives PowerPoint, Keynote, and Google Slides. Type should feel intentional through scale, weight, spacing, and alignment rather than through fragile custom font dependency.

## Color

Use a restrained base palette with a small number of signal colors. The palette should not collapse into a one-hue blue/purple AI theme. Signal color should mark workflow transitions, proof objects, or evaluation status.

## Assets

Prefer editable SVGs and native shapes for systems, diagrams, flows, and abstract product metaphors. Use generated bitmap images only where an atmospheric or illustrative moment improves the story.

## Anti-Patterns

- Feature-card grids that could belong to any SaaS product.
- Screenshot-like images containing important text.
- Pseudo-logos or copied brand marks.
- Decorative diagrams whose arrows do not encode real relationships.
- Slide titles that label a topic instead of making a claim.
```

Create `docs/product/ppt-case-pack-v1/evaluation_rubric.md`:

```markdown
# Evaluation Rubric

Score each dimension from 0 to 5.

## Commercial Clarity

The deck states the user problem, audience, product role, and next action without requiring verbal explanation.

## Narrative Flow

The slide sequence has a clear arc: pain, market shift, Vulca approach, workflow, proof, decision.

## Technical Understandability

Case packs, skills, code generation, visual review, and layout QA are explained through diagrams or concise proof objects.

## Visual Hierarchy

The viewer can identify the slide claim, proof object, and supporting detail within five seconds.

## Brand Coherence

The deck uses consistent typography, spacing, colors, and visual grammar across slides.

## Cultural And Design Intent

The deck shows that Vulca can encode design reasoning and cultural/design context rather than only rearranging content.

## Slide-To-Slide Consistency

Repeated patterns retain their grammar while still allowing rhythm changes.

## Editability

Titles, body copy, diagrams, and key shapes remain editable. No important text is rasterized into an image.

## Accessibility

Text contrast, reading order, and density are suitable for a live presentation and exported PDF.

## Cross-Platform Rendering Risk

The deck avoids fragile font, image, and layout choices that are likely to break across PowerPoint, Keynote, or Google Slides.
```

- [ ] **Step 5: Create JSON rule files**

Create `docs/product/ppt-case-pack-v1/narrative_rules.json`:

```json
{
  "schema_version": 1,
  "opening": "Name the workflow problem before naming the feature.",
  "progression": ["pain", "market_shift", "approach", "workflow", "proof", "call_to_action"],
  "technical_depth": "Expose technical control through diagrams, not long prose.",
  "closing": "End with a concrete next workflow."
}
```

Create `docs/product/ppt-case-pack-v1/style_tokens.json`:

```json
{
  "schema_version": 1,
  "palette": {
    "ink": "#171717",
    "paper": "#F7F4EE",
    "warm_gray": "#D8D1C5",
    "signal": "#E24A2A",
    "teal": "#147C72",
    "violet": "#6B5CFF",
    "dark_panel": "#22201D"
  },
  "font_stack": ["Aptos", "Arial", "sans-serif"],
  "spacing": {
    "xs": 8,
    "sm": 16,
    "md": 24,
    "lg": 40,
    "xl": 64
  },
  "corner_radius": {
    "small": 4,
    "medium": 8
  },
  "stroke_widths": {
    "hairline": 1,
    "strong": 2
  }
}
```

Create `docs/product/ppt-case-pack-v1/asset_rules.json`:

```json
{
  "schema_version": 1,
  "preferred_assets": ["editable_svg", "native_shapes"],
  "bitmap_use": "background_or_illustrative_only",
  "forbidden": ["rasterized_text", "copied_reference_visuals", "pseudo_logos"],
  "provenance_required": true
}
```

Create `docs/product/ppt-case-pack-v1/slide_patterns.json`:

```json
{
  "schema_version": 1,
  "patterns": [
    {
      "id": "cover",
      "role": "cover",
      "content_density": "low",
      "layout_shape": "hero_claim_with_system_mark",
      "visual_asset_type": "editable_svg",
      "editability_requirements": ["title_text_is_editable", "subtitle_text_is_editable"]
    },
    {
      "id": "problem",
      "role": "problem",
      "content_density": "medium",
      "layout_shape": "claim_plus_three_failures",
      "visual_asset_type": "native_shapes",
      "editability_requirements": ["failure_labels_are_editable", "no_rasterized_copy"]
    },
    {
      "id": "market_shift",
      "role": "market_shift",
      "content_density": "medium",
      "layout_shape": "before_after_system_shift",
      "visual_asset_type": "editable_svg",
      "editability_requirements": ["axis_labels_are_editable", "transition_copy_is_editable"]
    },
    {
      "id": "workflow",
      "role": "workflow_diagram",
      "content_density": "medium",
      "layout_shape": "left_to_right_process",
      "visual_asset_type": "native_shapes",
      "editability_requirements": ["nodes_are_editable", "connectors_are_attached"]
    },
    {
      "id": "product_pillars",
      "role": "product_pillars",
      "content_density": "medium",
      "layout_shape": "four_pillars_with_proof_labels",
      "visual_asset_type": "native_shapes",
      "editability_requirements": ["pillar_titles_are_editable", "proof_labels_are_editable"]
    },
    {
      "id": "case_pack_method",
      "role": "case_pack_method",
      "content_density": "medium_high",
      "layout_shape": "source_to_rules_to_deck_pipeline",
      "visual_asset_type": "editable_svg",
      "editability_requirements": ["pipeline_stages_are_editable", "source_names_are_editable"]
    },
    {
      "id": "proof",
      "role": "generated_output_proof",
      "content_density": "medium",
      "layout_shape": "artifact_grid_with_quality_checks",
      "visual_asset_type": "native_shapes",
      "editability_requirements": ["artifact_labels_are_editable", "status_labels_are_editable"]
    },
    {
      "id": "comparison",
      "role": "benchmark_comparison",
      "content_density": "medium_high",
      "layout_shape": "baseline_vs_vulca_matrix",
      "visual_asset_type": "native_shapes",
      "editability_requirements": ["matrix_cells_are_editable", "scores_are_editable"]
    },
    {
      "id": "roadmap",
      "role": "roadmap",
      "content_density": "medium",
      "layout_shape": "three_stage_product_path",
      "visual_asset_type": "native_shapes",
      "editability_requirements": ["stage_labels_are_editable", "timing_copy_is_editable"]
    },
    {
      "id": "closing",
      "role": "closing",
      "content_density": "low",
      "layout_shape": "final_claim_and_next_action",
      "visual_asset_type": "editable_svg",
      "editability_requirements": ["claim_text_is_editable", "call_to_action_is_editable"]
    }
  ]
}
```

- [ ] **Step 6: Create minimal generation input files**

Create `docs/product/ppt-case-pack-v1/deck_outline.json`:

```json
{
  "schema_version": 1,
  "title": "Vulca Product Launch Deck",
  "slides": [
    {
      "id": "slide_01",
      "pattern_id": "cover",
      "title": "Vulca",
      "claim": "Design knowledge becomes editable presentation code.",
      "proof_object": "A simple system mark showing case pack, skill, code, review, and deck output."
    }
  ]
}
```

Create `docs/product/ppt-case-pack-v1/baseline_prompt.md`:

```markdown
# Baseline Prompt

Create a product launch deck for Vulca that explains how AI agents can generate editable presentation code from design knowledge.
```

Create `docs/product/ppt-case-pack-v1/vulca_generation_brief.md`:

```markdown
# Vulca Generation Brief

Use the case-pack rules, slide patterns, style tokens, and asset rules to generate an editable Vulca product launch presentation.
```

Create `docs/product/ppt-case-pack-v1/gemini_review_prompt.md`:

```markdown
# Gemini Review Prompt

Review the rendered Vulca PPT contact sheet for commercial clarity, visual hierarchy, brand coherence, editability risk, and whether it looks stronger than a prompt-only deck.
```

- [ ] **Step 7: Create first skill draft and result folder**

Create `docs/product/ppt-case-pack-v1/vulca_ppt_skill.md`:

```markdown
# Vulca PPT Skill v1

Use this skill when generating a commercial product-launch deck from the Vulca PPT case pack.

## Input

- `commercial_brief.md`
- `design_notes.md`
- `narrative_rules.json`
- `slide_patterns.json`
- `style_tokens.json`
- `asset_rules.json`
- `deck_outline.json`

## Rules

1. Generate editable slide code, not screenshots.
2. Keep title, body copy, diagrams, and labels editable.
3. Use generated bitmap images only as supporting atmosphere or illustration.
4. Use SVG or native shapes for workflows, diagrams, matrices, and product metaphors.
5. Do not copy reference visuals, brand marks, or layouts.
6. Each slide needs one claim and one proof object.
7. Run Gemini review on rendered screenshots before finalizing the deck.
8. Run layout and editability checks before claiming the deck is ready.

## Output

- baseline prompt record;
- Vulca generation brief;
- PPTX or HTML slide artifact;
- rendered screenshots or PDF;
- Gemini review notes;
- comparison report.
```

Create `docs/product/ppt-case-pack-v1/results/README.md`:

```markdown
# Results

Generated deck artifacts and comparison records are documented here after the case pack is used.

Scratch files stay under `outputs/$THREAD_ID/presentations/`. Only final, reviewed artifacts should be copied into this folder.
```

Create `docs/product/ppt-case-pack-v1/results/comparison_report.md`:

```markdown
# Comparison Report

**Status:** not-run

## Baseline

The baseline deck has not been generated yet.

## Vulca Case-Pack Deck

The Vulca case-pack deck has not been generated yet.

## Evaluation

Scores will be recorded after both decks have exported screenshots and editable presentation files.
```

- [ ] **Step 8: Run repository validation**

Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_case_pack_v1.py -q
python3 scripts/validate_ppt_case_pack.py docs/product/ppt-case-pack-v1
```

Expected:

```text
10 passed
case pack ok: docs/product/ppt-case-pack-v1
```

- [ ] **Step 9: Commit**

```bash
git add docs/product/ppt-case-pack-v1 tests/test_ppt_case_pack_v1.py
git commit -m "docs: add PPT case pack v1"
```

---

### Task 3: Deck Outline And Generation Inputs

**Files:**
- Modify: `docs/product/ppt-case-pack-v1/deck_outline.json`
- Modify: `docs/product/ppt-case-pack-v1/baseline_prompt.md`
- Modify: `docs/product/ppt-case-pack-v1/vulca_generation_brief.md`
- Modify: `docs/product/ppt-case-pack-v1/gemini_review_prompt.md`

- [ ] **Step 1: Replace minimal deck outline with 10-slide outline**

Update `docs/product/ppt-case-pack-v1/deck_outline.json`:

```json
{
  "schema_version": 1,
  "title": "Vulca Product Launch Deck",
  "audience": "builders, designers, AI platform reviewers, and early technical adopters",
  "slides": [
    {
      "id": "slide_01",
      "pattern_id": "cover",
      "title": "Vulca",
      "claim": "Design knowledge becomes editable presentation code.",
      "proof_object": "A simple system mark showing case pack, skill, code, review, and deck output."
    },
    {
      "id": "slide_02",
      "pattern_id": "problem",
      "title": "Fast decks are not the same as designed decks",
      "claim": "Prompt-only presentation tools collapse design intent into generic templates.",
      "proof_object": "Three failure modes: weak hierarchy, opaque design logic, fragile editability."
    },
    {
      "id": "slide_03",
      "pattern_id": "market_shift",
      "title": "The next presentation system needs design memory",
      "claim": "The opportunity is not faster slide generation; it is reusable design reasoning.",
      "proof_object": "Before/after shift from prompt-to-deck to case-pack-to-editable-code."
    },
    {
      "id": "slide_04",
      "pattern_id": "workflow",
      "title": "Vulca turns references into a workflow",
      "claim": "Public commercial references become structured rules before any slide is generated.",
      "proof_object": "Pipeline diagram: sources, summaries, rules, slide patterns, style tokens, generation brief."
    },
    {
      "id": "slide_05",
      "pattern_id": "product_pillars",
      "title": "The product is a control layer",
      "claim": "Vulca controls story, visual system, assets, code generation, and review.",
      "proof_object": "Five pillars with one proof label each."
    },
    {
      "id": "slide_06",
      "pattern_id": "case_pack_method",
      "title": "Case packs make taste inspectable",
      "claim": "A case pack stores design decisions as files that agents and humans can review.",
      "proof_object": "File-to-decision map linking each case-pack artifact to a deck decision."
    },
    {
      "id": "slide_07",
      "pattern_id": "proof",
      "title": "Generation is code-first",
      "claim": "The deck is built from editable text, shapes, SVGs, and diagrams, with images as support.",
      "proof_object": "Artifact grid showing PPTX, screenshots, layout JSON, and review notes."
    },
    {
      "id": "slide_08",
      "pattern_id": "comparison",
      "title": "The benchmark is baseline versus Vulca",
      "claim": "The case-pack deck should beat an ordinary prompt deck on story, hierarchy, coherence, and editability.",
      "proof_object": "Comparison matrix with the rubric dimensions."
    },
    {
      "id": "slide_09",
      "pattern_id": "roadmap",
      "title": "The first wedge becomes product primitives",
      "claim": "Evidence from this deck decides whether to productize the skill, schema, layout engine, or review loop.",
      "proof_object": "Three-stage path: case pack, reliable slide primitives, reusable PPT workflow."
    },
    {
      "id": "slide_10",
      "pattern_id": "closing",
      "title": "Design work should leave evidence",
      "claim": "Vulca makes presentation design reusable, reviewable, and editable.",
      "proof_object": "Final call to run the workflow on the next real commercial deck."
    }
  ]
}
```

- [ ] **Step 2: Write baseline prompt**

Update `docs/product/ppt-case-pack-v1/baseline_prompt.md`:

```markdown
# Baseline Prompt

Create a 10-slide product launch presentation for Vulca.

Vulca is an AI-native visual workflow tool. It helps users turn fuzzy visual intent into structured creative artifacts, prompts, evaluations, and editable outputs.

The deck should explain:

- the problem with generic AI presentation generation;
- how Vulca uses real design references;
- how Vulca turns design knowledge into reusable skills;
- how Vulca generates editable PPT content mostly through code;
- how Gemini reviews visual quality;
- why this is useful for builders, designers, and platform reviewers.

Make the deck look premium, modern, and suitable for a product launch video.
```

- [ ] **Step 3: Write Vulca generation brief**

Update `docs/product/ppt-case-pack-v1/vulca_generation_brief.md`:

```markdown
# Vulca Generation Brief

Generate the Vulca Product Launch Deck using the full case pack.

## Required Inputs

- `commercial_brief.md`
- `design_notes.md`
- `narrative_rules.json`
- `slide_patterns.json`
- `style_tokens.json`
- `asset_rules.json`
- `deck_outline.json`
- `evaluation_rubric.md`

## Design Constraints

- Use artifact-tool presentation JSX for editable PPTX generation.
- Use one slide module per slide.
- Keep all titles, body copy, labels, and diagram text editable.
- Use native shapes or editable SVG for diagrams.
- Do not use bitmap images for text.
- Do not copy reference-case visuals.
- Use a restrained warm-neutral base with signal accents from `style_tokens.json`.
- Avoid a generic dark-blue AI SaaS palette.
- Each slide must include one claim and one proof object.
- Generate rendered previews, layout JSON, and a contact sheet before review.

## Expected Output

- editable PPTX;
- rendered slide PNGs;
- contact sheet;
- layout JSON;
- Gemini review notes;
- comparison report against the baseline deck.
```

- [ ] **Step 4: Write Gemini review prompt**

Update `docs/product/ppt-case-pack-v1/gemini_review_prompt.md`:

```markdown
# Gemini Review Prompt

Review the rendered Vulca Product Launch Deck screenshots as a commercial product-launch presentation.

Score 0-5:

- commercial clarity;
- narrative flow;
- technical understandability;
- visual hierarchy;
- brand coherence;
- cultural/design intent;
- slide-to-slide consistency;
- premium versus template-like feel;
- editability risk visible from screenshots;
- reference-case alignment without copying.

Return:

- three highest-priority design issues;
- three slide-specific fixes;
- one judgment on whether the deck is video-demo ready;
- one judgment on whether it looks materially stronger than a prompt-only deck.

Do not praise the deck generically. Focus on visible issues, hierarchy, taste, and commercial credibility.
```

- [ ] **Step 5: Validate updated pack**

Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_v1.py -q
python3 scripts/validate_ppt_case_pack.py docs/product/ppt-case-pack-v1
```

Expected:

```text
1 passed
case pack ok: docs/product/ppt-case-pack-v1
```

- [ ] **Step 6: Commit**

```bash
git add docs/product/ppt-case-pack-v1
git commit -m "docs: define Vulca PPT launch deck inputs"
```

---

### Task 4: Baseline Deck Generation

**Files:**
- Create final artifacts under: `outputs/$THREAD_ID/presentations/vulca-ppt-baseline/`
- Copy final summary to: `docs/product/ppt-case-pack-v1/results/comparison_report.md`

- [ ] **Step 1: Use Presentations skill in create mode**

Set the workspace variables:

```bash
THREAD_ID=${CODEX_THREAD_ID:-manual-$(date +%Y%m%d%H%M%S)}
WORKSPACE="$PWD/outputs/$THREAD_ID/presentations/vulca-ppt-baseline"
SLIDES_DIR="$WORKSPACE/slides"
PREVIEW_DIR="$WORKSPACE/preview"
LAYOUT_DIR="$WORKSPACE/layout"
QA_DIR="$WORKSPACE/qa"
OUTPUT_DIR="$WORKSPACE/output"
mkdir -p "$SLIDES_DIR" "$PREVIEW_DIR" "$LAYOUT_DIR" "$QA_DIR" "$OUTPUT_DIR"
```

Task mode: `create`.

Primary deck profile: `product-platform`.

Use only `docs/product/ppt-case-pack-v1/baseline_prompt.md` as the source story. Do not use the case-pack rules for this baseline.

- [ ] **Step 2: Write baseline profile plan**

Create `$WORKSPACE/profile-plan.txt`:

```text
task mode: create
primary deck-profile: product-platform
secondary gates: engineering-platform clarity, commercial product-launch credibility
required proof objects: workflow diagram, product pillars, comparison matrix, roadmap
source requirements: use baseline_prompt.md only
asset requirements: editable text and shapes; no copied reference visuals
brand authenticity constraints: do not invent a Vulca pseudo-logo beyond simple text mark and abstract editable system shapes
profile-specific QA gates: no generic feature-card grid; every slide has a claim and proof object
known missing inputs: no external metrics; use qualitative proof only
```

- [ ] **Step 3: Build baseline deck with artifact-tool**

Use the Presentations skill workflow:

```bash
SKILL_DIR="/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.521.10419/skills/presentations"
NODE="/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
```

Create one artifact-tool slide module per slide in `$SLIDES_DIR`. Export a 10-slide PPTX:

```bash
"$NODE" "$SKILL_DIR/scripts/build_artifact_deck.mjs" \
  --workspace "$WORKSPACE" \
  --slides-dir "$SLIDES_DIR" \
  --out "$OUTPUT_DIR/vulca-prompt-baseline.pptx" \
  --preview-dir "$PREVIEW_DIR" \
  --layout-dir "$LAYOUT_DIR/final" \
  --contact-sheet "$PREVIEW_DIR/contact-sheet.png" \
  --slide-count 10
```

Expected:

```text
created PPTX: vulca-prompt-baseline.pptx
created contact sheet: preview/contact-sheet.png
created layout JSON under layout/final
```

- [ ] **Step 4: Run visual and layout QA**

Run artifact-tool layout quality check:

```bash
"$NODE" "$SKILL_DIR/scripts/check_layout_quality.mjs" \
  --layout-dir "$LAYOUT_DIR/final" \
  --preview-dir "$PREVIEW_DIR" \
  --qa-dir "$QA_DIR"
```

Expected: PASS or a short list of layout failures. If failures occur, revise the weakest slides before continuing.

- [ ] **Step 5: Update comparison report with baseline manifest**

Update `docs/product/ppt-case-pack-v1/results/comparison_report.md` with:

```markdown
## Baseline

Status: generated

Source: `baseline_prompt.md`

Artifacts:

- PPTX: `outputs/$THREAD_ID/presentations/vulca-ppt-baseline/output/vulca-prompt-baseline.pptx`
- Contact sheet: `outputs/$THREAD_ID/presentations/vulca-ppt-baseline/preview/contact-sheet.png`
- Layout JSON: `outputs/$THREAD_ID/presentations/vulca-ppt-baseline/layout/final/`

Initial assessment: baseline exists for comparison only. It is not the product-quality target.
```

- [ ] **Step 6: Commit report update**

```bash
git add docs/product/ppt-case-pack-v1/results/comparison_report.md
git commit -m "docs: record PPT baseline generation"
```

Do not commit the full `outputs/` workspace unless the user explicitly approves committing generated binary artifacts.

---

### Task 5: Vulca Case-Pack Deck Generation

**Files:**
- Create final artifacts under: `outputs/$THREAD_ID/presentations/vulca-ppt-case-pack/`
- Modify: `docs/product/ppt-case-pack-v1/results/comparison_report.md`

- [ ] **Step 1: Use Presentations skill in create mode with the case pack**

Set the workspace variables:

```bash
THREAD_ID=${CODEX_THREAD_ID:-manual-$(date +%Y%m%d%H%M%S)}
WORKSPACE="$PWD/outputs/$THREAD_ID/presentations/vulca-ppt-case-pack"
SLIDES_DIR="$WORKSPACE/slides"
PREVIEW_DIR="$WORKSPACE/preview"
LAYOUT_DIR="$WORKSPACE/layout"
QA_DIR="$WORKSPACE/qa"
OUTPUT_DIR="$WORKSPACE/output"
mkdir -p "$SLIDES_DIR" "$PREVIEW_DIR" "$LAYOUT_DIR" "$QA_DIR" "$OUTPUT_DIR"
```

Task mode: `create`.

Primary deck profile: `product-platform`.

Use these source files:

```text
docs/product/ppt-case-pack-v1/commercial_brief.md
docs/product/ppt-case-pack-v1/design_notes.md
docs/product/ppt-case-pack-v1/narrative_rules.json
docs/product/ppt-case-pack-v1/slide_patterns.json
docs/product/ppt-case-pack-v1/style_tokens.json
docs/product/ppt-case-pack-v1/asset_rules.json
docs/product/ppt-case-pack-v1/deck_outline.json
docs/product/ppt-case-pack-v1/vulca_generation_brief.md
docs/product/ppt-case-pack-v1/evaluation_rubric.md
```

- [ ] **Step 2: Write case-pack profile plan**

Create `$WORKSPACE/profile-plan.txt`:

```text
task mode: create
primary deck-profile: product-platform
secondary gates: engineering-platform clarity, premium product-launch rhythm
required proof objects: source-to-rules pipeline, editable-code proof, baseline-vs-Vulca matrix, product primitive roadmap
source requirements: use ppt-case-pack-v1 files; no copied reference visuals
asset requirements: native shapes and editable SVG first; bitmap images only for support
brand authenticity constraints: do not invent brand marks; use Vulca wordmark text and abstract system graphics
profile-specific QA gates: every slide must map to deck_outline.json; every diagram label remains editable
known missing inputs: no customer metrics; product proof is workflow evidence rather than quantitative adoption
```

- [ ] **Step 3: Build case-pack deck with artifact-tool**

Use:

```bash
SKILL_DIR="/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.521.10419/skills/presentations"
NODE="/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
"$NODE" "$SKILL_DIR/scripts/build_artifact_deck.mjs" \
  --workspace "$WORKSPACE" \
  --slides-dir "$SLIDES_DIR" \
  --out "$OUTPUT_DIR/vulca-case-pack-launch.pptx" \
  --preview-dir "$PREVIEW_DIR" \
  --layout-dir "$LAYOUT_DIR/final" \
  --contact-sheet "$PREVIEW_DIR/contact-sheet.png" \
  --slide-count 10
```

Expected:

```text
created PPTX: vulca-case-pack-launch.pptx
created contact sheet: preview/contact-sheet.png
created layout JSON under layout/final
```

- [ ] **Step 4: Run artifact-tool QA**

Run:

```bash
"$NODE" "$SKILL_DIR/scripts/check_layout_quality.mjs" \
  --layout-dir "$LAYOUT_DIR/final" \
  --preview-dir "$PREVIEW_DIR" \
  --qa-dir "$QA_DIR"
```

Expected: PASS. If it fails, revise slide modules until there are no hard layout failures.

- [ ] **Step 5: Update comparison report with case-pack artifact paths**

Update `docs/product/ppt-case-pack-v1/results/comparison_report.md`:

```markdown
## Vulca Case-Pack Deck

Status: generated

Sources:

- `commercial_brief.md`
- `design_notes.md`
- `narrative_rules.json`
- `slide_patterns.json`
- `style_tokens.json`
- `asset_rules.json`
- `deck_outline.json`
- `vulca_generation_brief.md`

Artifacts:

- PPTX: `outputs/$THREAD_ID/presentations/vulca-ppt-case-pack/output/vulca-case-pack-launch.pptx`
- Contact sheet: `outputs/$THREAD_ID/presentations/vulca-ppt-case-pack/preview/contact-sheet.png`
- Layout JSON: `outputs/$THREAD_ID/presentations/vulca-ppt-case-pack/layout/final/`
```

- [ ] **Step 6: Commit report update**

```bash
git add docs/product/ppt-case-pack-v1/results/comparison_report.md
git commit -m "docs: record PPT case-pack generation"
```

Do not commit the full `outputs/` workspace unless the user explicitly approves committing generated binary artifacts.

---

### Task 6: Gemini Visual Review

**Files:**
- Modify: `docs/product/ppt-case-pack-v1/results/comparison_report.md`

- [ ] **Step 1: Review the baseline deck artifact**

Use `mcp__gemini_agent.gemini_artifact_review`:

```json
{
  "cwd": "/Users/yhryzy/.codex/worktrees/031a/vulca",
  "file": "/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/$THREAD_ID/presentations/vulca-ppt-baseline/preview/contact-sheet.png",
  "kind": "presentation contact sheet",
  "write_artifact": true
}
```

Expected: compact structured review artifact with design issues and quality notes.

- [ ] **Step 2: Review the Vulca case-pack deck artifact**

Use `mcp__gemini_agent.gemini_artifact_review`:

```json
{
  "cwd": "/Users/yhryzy/.codex/worktrees/031a/vulca",
  "file": "/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/$THREAD_ID/presentations/vulca-ppt-case-pack/preview/contact-sheet.png",
  "kind": "presentation contact sheet",
  "write_artifact": true
}
```

Expected: compact structured review artifact with slide-specific fixes and judgment on commercial credibility.

- [ ] **Step 3: Update comparison report with Gemini findings**

Add a `## Gemini Review` section to `docs/product/ppt-case-pack-v1/results/comparison_report.md`.

Required labels:

```text
Baseline commercial clarity
Baseline visual hierarchy
Baseline template-like risks
Baseline most important fix
Vulca commercial clarity
Vulca visual hierarchy
Vulca reference-case alignment
Vulca most important fix
Decision
```

For each label, copy one concrete sentence from the Gemini artifact or write a one-sentence paraphrase that preserves Gemini's critique. Do not commit a label without a value. The `Decision` sentence must state whether the case-pack deck is stronger than the baseline on narrative specificity, design coherence, and editability.

- [ ] **Step 4: Commit report update**

```bash
git add docs/product/ppt-case-pack-v1/results/comparison_report.md
git commit -m "docs: add Gemini PPT deck review"
```

---

### Task 7: P2 Comparison And Product Decision

**Files:**
- Modify: `docs/product/ppt-case-pack-v1/results/comparison_report.md`
- Modify: `docs/product/roadmap.md`

- [ ] **Step 1: Score both decks**

Update `docs/product/ppt-case-pack-v1/results/comparison_report.md` with a `## Score Table` section.

Required dimensions:

```text
Commercial clarity
Narrative flow
Technical understandability
Visual hierarchy
Brand coherence
Cultural/design intent
Slide-to-slide consistency
Editability
Accessibility
Cross-platform rendering risk
```

For each dimension, record an integer score from 0 to 5 for the baseline deck, an integer score from 0 to 5 for the Vulca case-pack deck, and one evidence sentence grounded in screenshots, layout JSON, or Gemini review. Do not commit unscored rows.

- [ ] **Step 2: Record product primitive decision**

Add:

```markdown
## Product Primitive Decision

Recommended next primitive: case-pack schema plus Gemini-assisted deck review loop.

Reason: the first run should prove whether structured design knowledge and aesthetic review improve deck quality before investing in a larger slide layout engine.

Next product question: which slide patterns are reliable enough to become reusable generation primitives.
```

If generated evidence points to a different primitive, write that primitive and one evidence-backed reason.

- [ ] **Step 3: Update roadmap**

Modify `docs/product/roadmap.md` under `## Next`:

```markdown
- PPT case-pack wedge: real commercial references -> structured design knowledge -> editable code-generated launch deck -> Gemini and layout QA.
```

Modify `docs/product/roadmap.md` under `## Later`:

```markdown
- PPT slide layout engine or reusable slide primitives, gated on the PPT case-pack P2 comparison.
```

- [ ] **Step 4: Validate and commit**

Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_case_pack_v1.py -q
python3 scripts/validate_ppt_case_pack.py docs/product/ppt-case-pack-v1
```

Expected:

```text
5 passed
case pack ok: docs/product/ppt-case-pack-v1
```

Commit:

```bash
git add docs/product/ppt-case-pack-v1/results/comparison_report.md docs/product/roadmap.md
git commit -m "docs: record PPT case-pack product decision"
```

---

## Self-Review Checklist

- Spec coverage: Tasks 1-3 implement case-pack structure, source boundaries, rules, prompts, and evaluation rubric. Tasks 4-6 implement baseline generation, case-pack generation, and Gemini review. Task 7 implements P2 comparison and roadmap decision.
- Copyright boundary: `sources.json`, `source_summaries.md`, and validator rules keep sources as reference analysis only and prohibit copied proprietary visuals.
- PPT generation boundary: Tasks 4-5 use artifact-tool presentation JSX through the bundled Presentations runtime, not `python-pptx`.
- Visual quality boundary: Gemini reviews contact sheets, while artifact-tool layout checks guard against overlap and clipping.
- Generated artifact boundary: `outputs/` is not committed unless the user explicitly approves binary artifacts.
