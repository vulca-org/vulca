# Vulca PPT Run 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and evaluate the first formal Vulca PPT Run 1 case pack for an AI presentation product launch deck.

**Architecture:** Extend the existing PPT case-pack validator with a `run1` profile, then create `docs/product/ppt-run1-ai-presentation-launch/` as a self-contained, source-grounded case pack. Deck generation remains local under `outputs/$THREAD_ID/presentations/`, while committed result files record manifests, Gemini reviews, render checks, scores, product decision, and demo-script readiness.

**Tech Stack:** Python stdlib validator, pytest, ruff, Codex bundled Node runtime, `@oai/artifact-tool/presentation-jsx`, optional headless office renderer if available, Gemini-agent visual review.

**Generation Boundary:** Do not use Gemini to generate PPT slide modules, layout math, or final deck code. Codex writes deterministic artifact-tool slide modules; Gemini only critiques contact sheets and plans. Do not use `python-pptx` for generation; OpenXML/PPTX integrity is checked with `unzip -t`, and layout is checked with artifact-tool layout JSON.

---

## File Map

- Modify `scripts/validate_ppt_case_pack.py`: add profile-aware validation for the Run 1 extra files and `design_memory.json`.
- Modify `tests/test_ppt_case_pack_validator.py`: cover the default profile and the new `run1` profile.
- Create `tests/test_ppt_run1_case_pack.py`: repository contract tests for `docs/product/ppt-run1-ai-presentation-launch/`.
- Create `docs/product/ppt-run1-ai-presentation-launch/README.md`: Run 1 entry point and artifact map.
- Create `docs/product/ppt-run1-ai-presentation-launch/sources.json`: public source registry with reference-analysis-only permissions.
- Create `docs/product/ppt-run1-ai-presentation-launch/source_summaries.md`: original summaries of selected public references.
- Create `docs/product/ppt-run1-ai-presentation-launch/tutorial_notes.md`: original design teaching notes extracted from public articles/case studies.
- Create `docs/product/ppt-run1-ai-presentation-launch/commercial_brief.md`: buyer, problem, use case, constraints, and demo promise.
- Create `docs/product/ppt-run1-ai-presentation-launch/design_notes.md`: design analysis for the launch-deck direction.
- Create `docs/product/ppt-run1-ai-presentation-launch/design_memory.json`: reusable, source-grounded design rules for code generation.
- Create `docs/product/ppt-run1-ai-presentation-launch/narrative_rules.json`: story grammar.
- Create `docs/product/ppt-run1-ai-presentation-launch/slide_patterns.json`: 10 reusable slide patterns.
- Create `docs/product/ppt-run1-ai-presentation-launch/style_tokens.json`: code-friendly visual system.
- Create `docs/product/ppt-run1-ai-presentation-launch/asset_rules.json`: native/SVG/bitmap constraints and provenance policy.
- Create `docs/product/ppt-run1-ai-presentation-launch/evaluation_rubric.md`: copy the ten-dimension scoring rubric and Run 1 scoring rule.
- Create `docs/product/ppt-run1-ai-presentation-launch/vulca_ppt_skill.md`: Run 1 skill draft.
- Create `docs/product/ppt-run1-ai-presentation-launch/deck_outline.json`: exact 10-slide deck outline.
- Create `docs/product/ppt-run1-ai-presentation-launch/baseline_prompt.md`: prompt-only baseline input.
- Create `docs/product/ppt-run1-ai-presentation-launch/vulca_generation_brief.md`: case-pack-driven generation input.
- Create `docs/product/ppt-run1-ai-presentation-launch/gemini_review_prompt.md`: contact-sheet review prompt.
- Create `docs/product/ppt-run1-ai-presentation-launch/results/README.md`: result folder guide.
- Create `docs/product/ppt-run1-ai-presentation-launch/results/asset_provenance.json`: asset lifecycle manifest.
- Create `docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md`: baseline, Vulca, Gemini, score, and decision report.
- Create `docs/product/ppt-run1-ai-presentation-launch/results/iteration_log.md`: repair-pass log.
- Create `docs/product/ppt-run1-ai-presentation-launch/results/render_check.md`: renderer availability and render notes.
- Create `docs/product/ppt-run1-ai-presentation-launch/results/demo_video_outline.md`: created only if gates pass.

---

### Task 1: Add Run 1 Validator Profile

**Files:**
- Modify: `scripts/validate_ppt_case_pack.py`
- Modify: `tests/test_ppt_case_pack_validator.py`

- [ ] **Step 1: Add failing validator-profile tests**

Append these tests to `tests/test_ppt_case_pack_validator.py`:

```python
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
```

- [ ] **Step 2: Run the new tests to verify failure**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: fail because `validate_case_pack()` does not accept `profile`.

- [ ] **Step 3: Implement profile-aware validation**

Update `scripts/validate_ppt_case_pack.py`:

```python
RUN1_REQUIRED_FILES = [
    "tutorial_notes.md",
    "design_memory.json",
    "results/asset_provenance.json",
    "results/iteration_log.md",
    "results/render_check.md",
]


def required_files_for_profile(profile: str) -> list[str]:
    if profile == "default":
        return REQUIRED_FILES
    if profile == "run1":
        return [*REQUIRED_FILES, *RUN1_REQUIRED_FILES]
    raise ValueError(f"unknown case-pack profile: {profile}")
```

Add this validator:

```python
def validate_design_memory(pack_dir: Path, errors: list[str]) -> None:
    data = load_json(pack_dir / "design_memory.json", errors)
    require_keys("design_memory.json", data, ["schema_version", "observations"], errors)
    if "schema_version" in data:
        require_integer("design_memory.schema_version", data["schema_version"], errors)
    observations = data.get("observations", [])
    if not isinstance(observations, list) or not observations:
        errors.append("design_memory.observations must be a non-empty list")
        return

    required = ["id", "source_ids", "principle", "code_generation_rule", "do_not_copy"]
    seen_ids: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"design_memory.observations[{index}] must be an object")
            continue
        require_keys(f"design_memory.observations[{index}]", observation, required, errors)
        for key in ["id", "principle", "code_generation_rule", "do_not_copy"]:
            if key in observation:
                require_non_empty_string(f"design_memory.observations[{index}].{key}", observation[key], errors)
        observation_id = observation.get("id")
        if isinstance(observation_id, str) and observation_id.strip():
            if observation_id in seen_ids:
                errors.append(f"design_memory.observations[{index}].id duplicates {observation_id}")
            seen_ids.add(observation_id)
        if "source_ids" in observation:
            validate_string_list(f"design_memory.observations[{index}].source_ids", observation["source_ids"], errors)
```

Change the public function and CLI:

```python
def validate_case_pack(pack_dir: str | Path, profile: str = "default") -> ValidationResult:
    root = Path(pack_dir)
    errors: list[str] = []
    try:
        required_files = required_files_for_profile(profile)
    except ValueError as exc:
        return ValidationResult(False, [str(exc)])
    if not root.exists():
        return ValidationResult(False, [f"case pack directory does not exist: {root}"])
    for rel in required_files:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif not path.is_file():
            errors.append(f"required path is not a file: {rel}")
    if errors:
        return ValidationResult(False, errors)

    validate_sources(root, errors)
    validate_narrative_rules(root, errors)
    validate_style_tokens(root, errors)
    validate_asset_rules(root, errors)
    pattern_ids = validate_slide_patterns(root, errors)
    validate_deck_outline(root, pattern_ids, errors)
    validate_markdown_not_empty(root, errors, required_files)
    if profile == "run1":
        validate_design_memory(root, errors)
    return ValidationResult(not errors, errors)
```

Also change `validate_markdown_not_empty` to accept `required_files`, and add:

```python
parser.add_argument("--profile", choices=["default", "run1"], default="default")
result = validate_case_pack(args.pack_dir, profile=args.profile)
```

- [ ] **Step 4: Run validator tests**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: all validator tests pass.

- [ ] **Step 5: Check formatting and commit**

```bash
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git add scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git commit -m "test: add PPT Run 1 validator profile"
```

---

### Task 2: Create Run 1 Case-Pack Skeleton

**Files:**
- Create: `tests/test_ppt_run1_case_pack.py`
- Create: `docs/product/ppt-run1-ai-presentation-launch/**`

- [ ] **Step 1: Write repository contract tests**

Create `tests/test_ppt_run1_case_pack.py`:

```python
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
    assert EXPECTED_SOURCE_IDS <= ids
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
```

- [ ] **Step 2: Run test to verify failure**

```bash
python3 -m pytest tests/test_ppt_run1_case_pack.py -q
```

Expected: fail because the Run 1 pack does not exist.

- [ ] **Step 3: Create the Run 1 directory**

```bash
mkdir -p docs/product/ppt-run1-ai-presentation-launch/results
```

- [ ] **Step 4: Create source registry and summaries**

Create `docs/product/ppt-run1-ai-presentation-launch/sources.json` with four sources:

```json
{
  "schema_version": 1,
  "sources": [
    {
      "id": "geo_figma_slides",
      "title": "GEO / Figma Slides case study",
      "url": "https://geo-nyc.com/projects/figma-slides/",
      "role": "presentation_product_launch_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of presentation-product launch framing. Do not copy proprietary visuals, screenshots, layouts, brand marks, template files, or full prose."
    },
    {
      "id": "figma_config_2024",
      "title": "Inside Config 2024",
      "url": "https://www.figma.com/blog/inside-config-2024/",
      "role": "product_event_context_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of product-launch context and event storytelling. Do not copy proprietary visuals, screenshots, layouts, brand marks, or full prose."
    },
    {
      "id": "figma_config_2025_identity",
      "title": "How we shaped the visual identity for Config 2025",
      "url": "https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/",
      "role": "visual_identity_system_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of identity-system thinking. Do not copy proprietary visuals, glyphs, screenshots, layouts, brand marks, or full prose."
    },
    {
      "id": "supervity_ai_keynote",
      "title": "MUSE Creatives / Supervity AI keynote presentation case",
      "url": "https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/",
      "role": "ai_keynote_commercial_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis of AI keynote communication and commercial clarity. Do not copy proprietary visuals, screenshots, layouts, brand marks, or full prose."
    }
  ]
}
```

Create `source_summaries.md` with one original paragraph per source and a final `## Use Boundary` section saying reference analysis only.

- [ ] **Step 5: Create core markdown files**

Create these files with concrete Run 1 content:

```text
README.md
commercial_brief.md
design_notes.md
tutorial_notes.md
evaluation_rubric.md
vulca_ppt_skill.md
baseline_prompt.md
vulca_generation_brief.md
gemini_review_prompt.md
results/README.md
results/comparison_report.md
results/iteration_log.md
results/render_check.md
```

Minimum required content:

- `README.md`: state Run 1 status, source boundary, expected outputs, and local artifact rule.
- `commercial_brief.md`: audience, buyer problem, promise, constraints, proof standard.
- `design_notes.md`: original observations about launch identity, AI explainability, modular slide systems, and editability.
- `tutorial_notes.md`: original teaching notes for hierarchy, rhythm, proof objects, diagram labels, and repair loops.
- `evaluation_rubric.md`: ten scoring dimensions from the spec, each using integer scores from zero through five.
- `vulca_ppt_skill.md`: reusable steps for source analysis, design memory, code-generated deck, Gemini review, repair pass.
- `baseline_prompt.md`: a plain prompt-only request for a 10-slide AI presentation product launch deck.
- `vulca_generation_brief.md`: exact sources, constraints, and outputs for the case-pack-driven deck.
- `gemini_review_prompt.md`: require numeric zero-through-five scores, design issues, slide-specific fixes, editability risks, accessibility risks, and cross-platform risks.
- result files: initial `not generated`, `not started`, and `not checked` status language.

- [ ] **Step 6: Create JSON rule files**

Create `design_memory.json`, `narrative_rules.json`, `slide_patterns.json`, `style_tokens.json`, `asset_rules.json`, and `deck_outline.json`.

Use the exact 10-slide pattern IDs from the test:

```json
[
  "cover",
  "problem",
  "reference_shift",
  "workflow",
  "design_memory",
  "code_generation",
  "review_loop",
  "comparison",
  "product_decision",
  "closing"
]
```

Every `deck_outline.slides[*].pattern_id` must exist in `slide_patterns.patterns[*].id`.

- [ ] **Step 7: Create initial asset provenance**

Create `docs/product/ppt-run1-ai-presentation-launch/results/asset_provenance.json`:

```json
{
  "schema_version": 1,
  "status": "not-run",
  "assets": [],
  "external_assets": [],
  "generated_assets": [],
  "copied_assets": [],
  "notes": "Run 1 deck has not been generated. No external images, generated bitmap assets, or copied reference visuals have been used."
}
```

- [ ] **Step 8: Validate and commit**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_case_pack.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1 docs/product/ppt-run1-ai-presentation-launch
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_case_pack.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_case_pack.py
git add docs/product/ppt-run1-ai-presentation-launch tests/test_ppt_run1_case_pack.py
git commit -m "docs: add PPT Run 1 case pack"
```

---

### Task 3: Define Run 1 Generation Inputs

**Files:**
- Modify: `docs/product/ppt-run1-ai-presentation-launch/deck_outline.json`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/baseline_prompt.md`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/vulca_generation_brief.md`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/gemini_review_prompt.md`
- Modify: `tests/test_ppt_run1_case_pack.py`

- [ ] **Step 1: Add tests for generation contracts**

Append tests that assert:

```python
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
```

- [ ] **Step 2: Run tests to verify failure if contracts are missing**

```bash
python3 -m pytest tests/test_ppt_run1_case_pack.py -q
```

Expected: fail only if Task 2 files are missing the required contract language.

- [ ] **Step 3: Finalize deck outline**

Update `deck_outline.json` so each slide has:

```json
{
  "id": "01",
  "pattern_id": "cover",
  "title": "Vulca turns presentation taste into editable code",
  "claim": "Prompt-only decks are not enough for commercial AI product launches.",
  "proof_object": "A code-generated system mark plus three artifact labels: case pack, PPTX, Gemini review."
}
```

Slides 02-10 must cover: problem, reference shift, workflow, design memory, code generation, review loop, comparison, product decision, closing.

- [ ] **Step 4: Finalize prompts and review prompt**

Update:

- `baseline_prompt.md`: ask for a 10-slide deck without case-pack rules.
- `vulca_generation_brief.md`: require one slide module per outline slide, editable text, native shapes, no copied reference visuals, artifact outputs, renderer record, and asset provenance.
- `gemini_review_prompt.md`: require the ten scoring dimensions, three issues, three fixes, and explicit caveat that Gemini is not final approval.

- [ ] **Step 5: Validate and commit**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_case_pack.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1 docs/product/ppt-run1-ai-presentation-launch
git add docs/product/ppt-run1-ai-presentation-launch tests/test_ppt_run1_case_pack.py
git commit -m "docs: define PPT Run 1 generation inputs"
```

---

### Task 4: Generate Prompt-Only Baseline Deck

**Files:**
- Create local artifacts under: `outputs/$THREAD_ID/presentations/ppt-run1-baseline/`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/render_check.md`

- [ ] **Step 1: Set workspace variables**

```bash
THREAD_ID=${CODEX_THREAD_ID:-manual-$(date +%Y%m%d%H%M%S)}
WORKSPACE="$PWD/outputs/$THREAD_ID/presentations/ppt-run1-baseline"
SLIDES_DIR="$WORKSPACE/slides"
PREVIEW_DIR="$WORKSPACE/preview"
LAYOUT_DIR="$WORKSPACE/layout"
OUTPUT_DIR="$WORKSPACE/output"
mkdir -p "$SLIDES_DIR" "$PREVIEW_DIR" "$LAYOUT_DIR" "$OUTPUT_DIR"
```

- [ ] **Step 2: Generate baseline slide modules**

Use only `docs/product/ppt-run1-ai-presentation-launch/baseline_prompt.md`. Create ten slide modules in `$SLIDES_DIR`, one file per slide. Use artifact-tool presentation JSX with editable text and native shapes.

- [ ] **Step 3: Build baseline deck**

```bash
SKILL_DIR="/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.521.10419/skills/presentations"
NODE="/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
"$NODE" "$SKILL_DIR/scripts/build_artifact_deck.mjs" \
  --workspace "$WORKSPACE" \
  --slides-dir "$SLIDES_DIR" \
  --out "$OUTPUT_DIR/ppt-run1-baseline.pptx" \
  --preview-dir "$PREVIEW_DIR" \
  --layout-dir "$LAYOUT_DIR/final" \
  --contact-sheet "$PREVIEW_DIR/contact-sheet.png" \
  --slide-count 10
```

Expected:

```text
created PPTX: ppt-run1-baseline.pptx
created contact sheet: preview/contact-sheet.png
created layout JSON under layout/final
```

- [ ] **Step 4: Run QA checks**

```bash
"$NODE" "$SKILL_DIR/scripts/check_layout_quality.mjs" --layout "$LAYOUT_DIR/final"
unzip -t "$OUTPUT_DIR/ppt-run1-baseline.pptx"
```

Expected: `0 error(s)` from layout QA and `No errors detected` from unzip.

- [ ] **Step 5: Check renderer availability**

```bash
if command -v libreoffice >/dev/null 2>&1; then
  echo "Renderer: libreoffice available" > /tmp/ppt-run1-render-check.txt
else
  echo "Renderer: not available; artifact-tool preview and layout JSON used for Run 1 automated review" > /tmp/ppt-run1-render-check.txt
fi
```

- [ ] **Step 6: Update result reports and commit**

Update `comparison_report.md` with baseline artifact paths and initial assessment. Update `render_check.md` with renderer availability, baseline layout QA result, and baseline PPTX integrity result from `unzip -t`.

```bash
git add docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md docs/product/ppt-run1-ai-presentation-launch/results/render_check.md
git commit -m "docs: record PPT Run 1 baseline generation"
```

Do not commit `outputs/` unless the user explicitly approves generated artifact commits.

---

### Task 5: Generate Vulca Case-Pack Deck

**Files:**
- Create local artifacts under: `outputs/$THREAD_ID/presentations/ppt-run1-vulca/`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/asset_provenance.json`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/render_check.md`

- [ ] **Step 1: Set workspace variables**

```bash
THREAD_ID=${CODEX_THREAD_ID:-manual-$(date +%Y%m%d%H%M%S)}
WORKSPACE="$PWD/outputs/$THREAD_ID/presentations/ppt-run1-vulca"
SLIDES_DIR="$WORKSPACE/slides"
PREVIEW_DIR="$WORKSPACE/preview"
LAYOUT_DIR="$WORKSPACE/layout"
OUTPUT_DIR="$WORKSPACE/output"
mkdir -p "$SLIDES_DIR" "$PREVIEW_DIR" "$LAYOUT_DIR" "$OUTPUT_DIR"
```

- [ ] **Step 2: Write deck profile plan**

Create `$WORKSPACE/profile-plan.txt`:

```text
task mode: create
primary deck-profile: product-platform
case pack: docs/product/ppt-run1-ai-presentation-launch
core promise: code-generated editable PPT beats prompt-only deck on commercial clarity and design coherence
source boundary: reference-analysis-only; no copied visuals, screenshots, layouts, brand marks, or full prose
asset rule: native PPT shapes and editable SVG first; generated bitmap only as auxiliary with provenance
required artifacts: PPTX, contact sheet, layout JSON, asset provenance, render check, comparison report
review gate: Gemini can critique taste but is not final human approval
```

- [ ] **Step 3: Generate case-pack slide modules**

Use:

```text
docs/product/ppt-run1-ai-presentation-launch/commercial_brief.md
docs/product/ppt-run1-ai-presentation-launch/design_notes.md
docs/product/ppt-run1-ai-presentation-launch/tutorial_notes.md
docs/product/ppt-run1-ai-presentation-launch/design_memory.json
docs/product/ppt-run1-ai-presentation-launch/narrative_rules.json
docs/product/ppt-run1-ai-presentation-launch/slide_patterns.json
docs/product/ppt-run1-ai-presentation-launch/style_tokens.json
docs/product/ppt-run1-ai-presentation-launch/asset_rules.json
docs/product/ppt-run1-ai-presentation-launch/deck_outline.json
docs/product/ppt-run1-ai-presentation-launch/vulca_generation_brief.md
```

Create ten artifact-tool slide modules in `$SLIDES_DIR`. Each module must keep slide text editable and use native shapes for diagrams.

- [ ] **Step 4: Build Vulca deck**

```bash
SKILL_DIR="/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.521.10419/skills/presentations"
NODE="/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
"$NODE" "$SKILL_DIR/scripts/build_artifact_deck.mjs" \
  --workspace "$WORKSPACE" \
  --slides-dir "$SLIDES_DIR" \
  --out "$OUTPUT_DIR/ppt-run1-vulca.pptx" \
  --preview-dir "$PREVIEW_DIR" \
  --layout-dir "$LAYOUT_DIR/final" \
  --contact-sheet "$PREVIEW_DIR/contact-sheet.png" \
  --slide-count 10
```

- [ ] **Step 5: Run QA checks**

```bash
"$NODE" "$SKILL_DIR/scripts/check_layout_quality.mjs" --layout "$LAYOUT_DIR/final"
unzip -t "$OUTPUT_DIR/ppt-run1-vulca.pptx"
```

Expected: `0 error(s)` from layout QA and `No errors detected` from unzip. If either command fails, stop and repair the slide modules before updating committed result reports.

- [ ] **Step 6: Update reports and commit**

Update:

- `comparison_report.md`: case-pack artifact paths and initial assessment.
- `asset_provenance.json`: set `status` to `generated-no-external-assets` if no generated/external assets were used; otherwise record every generated bitmap/SVG with prompt, license/source status, and purpose.
- `render_check.md`: case-pack layout QA result, case-pack PPTX integrity result from `unzip -t`, and renderer availability.

```bash
git add docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md docs/product/ppt-run1-ai-presentation-launch/results/asset_provenance.json docs/product/ppt-run1-ai-presentation-launch/results/render_check.md
git commit -m "docs: record PPT Run 1 case-pack generation"
```

---

### Task 6: Run Gemini Review and Repair Pass

**Files:**
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md`
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/iteration_log.md`

- [ ] **Step 1: Review baseline contact sheet with Gemini**

Use `mcp__gemini_agent.gemini_artifact_review`:

```text
cwd: /Users/yhryzy/.codex/worktrees/031a/vulca
file: outputs/$THREAD_ID/presentations/ppt-run1-baseline/preview/contact-sheet.png
kind: presentation contact sheet
write_artifact: true
```

Expected: compact structured review with commercial clarity, hierarchy, template risk, and top fixes.

If Gemini returns malformed output, no structured artifact, or an unusable review, record `Gemini review status: failed` in `comparison_report.md`, do not count Gemini as positive evidence, and continue only with layout QA, artifact evidence, and human review requirement.

- [ ] **Step 2: Review Vulca contact sheet with Gemini**

Use `mcp__gemini_agent.gemini_artifact_review`:

```text
cwd: /Users/yhryzy/.codex/worktrees/031a/vulca
file: outputs/$THREAD_ID/presentations/ppt-run1-vulca/preview/contact-sheet.png
kind: presentation contact sheet
write_artifact: true
```

Expected: compact structured review with whether the Vulca deck is stronger on narrative specificity and design coherence.

If Gemini returns malformed output, no structured artifact, or an unusable review, record `Gemini review status: failed` in `comparison_report.md`, skip the repair pass that depends on Gemini suggestions, and mark the quality gate as not passed.

- [ ] **Step 3: Update comparison report**

Add `## Gemini Review` to `comparison_report.md`. Each bullet must be a concrete sentence grounded in Gemini's review artifact:

- baseline commercial clarity;
- baseline visual hierarchy;
- baseline most important fix;
- Vulca commercial clarity;
- Vulca visual hierarchy;
- Vulca most important fix;
- review conflict, written as `none` only when Gemini, layout QA, and artifact evidence do not disagree;
- decision caveat that Gemini is qualitative evidence, not final human approval.

- [ ] **Step 4: Apply one focused repair pass**

Choose no more than three slide-specific fixes from Gemini. Modify only the Vulca deck slide modules under `outputs/$THREAD_ID/presentations/ppt-run1-vulca/slides/`, rebuild the Vulca deck, rerun layout QA and unzip, then record the fixes in `iteration_log.md`. Do not ask Gemini to rewrite slide code; convert its critique into deterministic edits yourself.

Use this iteration log shape, replacing the three fix lines with the actual slide numbers and concrete repair actions:

```markdown
## Repair Pass 1

- Status: completed
- Source: Gemini contact-sheet review
- Fix 1: Slide NN changed [specific visual hierarchy/layout/copy action].
- Fix 2: Slide NN changed [specific visual hierarchy/layout/copy action].
- Fix 3: Slide NN changed [specific visual hierarchy/layout/copy action].
- Rebuild result: PPTX generated
- Layout QA: 0 hard errors
- PPTX integrity: passed
- Human approval: still required before public publishing
```

- [ ] **Step 5: Commit report update**

```bash
git add docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md docs/product/ppt-run1-ai-presentation-launch/results/iteration_log.md
git commit -m "docs: add PPT Run 1 Gemini review"
```

---

### Task 7: Score Run 1 and Decide Next Primitive

**Files:**
- Modify: `docs/product/ppt-run1-ai-presentation-launch/results/comparison_report.md`
- Create: `docs/product/ppt-run1-ai-presentation-launch/results/demo_video_outline.md`
- Modify: `docs/product/roadmap.md`

- [ ] **Step 1: Add score table**

Add `## Score Table` to `comparison_report.md` with ten rows. Each row must have a concrete integer score from zero through five for the baseline deck, a concrete integer score from zero through five for the Vulca deck, and an evidence sentence citing generated artifacts, layout QA, Gemini review, or source-grounded case-pack files. Required dimensions:

- Commercial clarity
- Narrative flow
- Technical understandability
- Visual hierarchy
- Brand coherence
- Cultural/design intent
- Slide-to-slide consistency
- Editability
- Accessibility
- Cross-platform rendering risk

- [ ] **Step 2: Add quality-gate decision**

Add `## Quality Gate Decision` with concrete outcomes for case-pack validation, baseline PPTX generation, Vulca PPTX generation, Vulca hard layout error count, PPTX integrity, renderer availability record, reference-analysis-only provenance, average score delta, Gemini narrative/design judgment, and public publishing status. Public publishing status must remain blocked until human review.

The PPTX integrity outcome must cite `unzip -t` for both generated decks. If either PPTX fails integrity, the quality gate fails regardless of Gemini review or rubric score.

- [ ] **Step 3: Add product primitive decision**

Add `## Product Primitive Decision` with one selected next primitive, one evidence-backed reason, and one concrete implementation question for the next run. The selected primitive must be one of: case-pack schema plus Gemini-assisted review loop; slide layout primitives; renderer/cross-platform QA; or asset provenance tooling.

- [ ] **Step 4: Create demo video outline only if gates pass**

If gates pass, create `results/demo_video_outline.md`:

```markdown
# Demo Video Outline

**Status:** draft; not public until human approval.

## Story

1. Show prompt-only baseline limitation.
2. Show source-grounded case pack.
3. Show code-generated editable PPT.
4. Show Gemini review and repair pass.
5. Show score delta and next product primitive.

## Required Captures

- Baseline contact sheet.
- Vulca contact sheet.
- Case-pack file tree.
- Layout QA output.
- Gemini review excerpt.
- Final comparison table.
```

If gates do not pass, create the same file with `Status: blocked` and explain which gate failed.

- [ ] **Step 5: Update roadmap**

Modify `docs/product/roadmap.md` under `## Next`:

```markdown
- PPT Run 1: AI presentation product launch deck case pack -> baseline/Vulca deck -> Gemini review -> repair pass -> score-gated demo script.
```

Modify `## Later` only if Run 1 evidence points to slide primitives or layout engine as the next bottleneck.

- [ ] **Step 6: Validate and commit**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_case_pack.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1 docs/product/ppt-run1-ai-presentation-launch
git add docs/product/ppt-run1-ai-presentation-launch/results docs/product/roadmap.md
git commit -m "docs: record PPT Run 1 product decision"
```

---

## Final Verification

Run these before presenting the branch as complete:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_case_pack_v1.py tests/test_ppt_run1_case_pack.py -q
python3 scripts/validate_ppt_case_pack.py docs/product/ppt-case-pack-v1
python3 scripts/validate_ppt_case_pack.py --profile run1 docs/product/ppt-run1-ai-presentation-launch
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_case_pack_v1.py tests/test_ppt_run1_case_pack.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_case_pack_v1.py tests/test_ppt_run1_case_pack.py
git status --short
```

Expected:

- pytest passes;
- both validators pass;
- ruff passes;
- only `outputs/` remains untracked unless generated artifacts were explicitly approved for commit.

## Self-Review

- Spec coverage: This plan covers the Run 1 data shape, generation boundary, Gemini role, pipeline, quality gates, deliverables, and non-goals.
- Placeholder scan: No commit-ready result section in this plan contains fake scores or fake review findings. Generated artifact paths use `$THREAD_ID`, which is defined in the generation tasks.
- Type consistency: `validate_case_pack(pack_dir, profile="run1")` is introduced in Task 1 and used consistently in repository tests and CLI commands.
