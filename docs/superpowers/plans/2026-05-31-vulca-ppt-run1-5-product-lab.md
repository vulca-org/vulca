# Vulca PPT Run 1.5 Product Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 1.5 as a product-lab proof that tutorial and case evidence becomes design memory, drives code-generated PPT choices, and creates a visible output difference across prompt-only, full Vulca, and bad-data experiment arms.

**Architecture:** Add a `run1_5` validation profile and a self-contained `docs/product/ppt-run1-5-product-lab/` package with a strict design-memory contract, three-arm experiment protocol, generation briefs, and result reports. Generated decks remain local under `outputs/$THREAD_ID/presentations/`; committed files are tests, validators, source-grounded docs, Gemini summaries, and Markdown evidence reports.

**Tech Stack:** Python stdlib validator, pytest, ruff, Codex bundled Node runtime, `@oai/artifact-tool/presentation-jsx`, Presentations skill workflow, Gemini-agent artifact review, existing structural PPTX delivery validator.

---

## File Map

- Modify `scripts/validate_ppt_case_pack.py`: add `run1_5` profile, profile-specific required files, and design-memory contract validation.
- Modify `tests/test_ppt_case_pack_validator.py`: add unit tests for `run1_5` required files and design-memory contract fields.
- Create `tests/test_ppt_run1_5_product_lab.py`: repository contract tests for the Run 1.5 package.
- Create `docs/product/ppt-run1-5-product-lab/README.md`: entry point, experiment purpose, artifact map, and public-publish status.
- Create `docs/product/ppt-run1-5-product-lab/sources.json`: source registry inherited from Run 1 with reference-analysis-only policy.
- Create `docs/product/ppt-run1-5-product-lab/source_summaries.md`: concise original summaries of public references.
- Create `docs/product/ppt-run1-5-product-lab/tutorial_notes.md`: original tutorial/design teaching notes.
- Create `docs/product/ppt-run1-5-product-lab/commercial_brief.md`: real commercial brief cockpit content.
- Create `docs/product/ppt-run1-5-product-lab/design_notes.md`: product-lab visual direction and layout controls.
- Create `docs/product/ppt-run1-5-product-lab/design_memory.json`: strict contract instances showing evidence -> rule -> primitive -> QA signal.
- Create `docs/product/ppt-run1-5-product-lab/narrative_rules.json`: story grammar for the 10-slide product-lab deck.
- Create `docs/product/ppt-run1-5-product-lab/slide_patterns.json`: 10 product-lab slide patterns.
- Create `docs/product/ppt-run1-5-product-lab/style_tokens.json`: code-friendly visual system and grid rules.
- Create `docs/product/ppt-run1-5-product-lab/asset_rules.json`: native/SVG/bitmap/provenance policy.
- Create `docs/product/ppt-run1-5-product-lab/evaluation_rubric.md`: Run 1.5 scoring rubric with bad-data signal.
- Create `docs/product/ppt-run1-5-product-lab/vulca_ppt_skill.md`: skill workflow draft for Run 1.5.
- Create `docs/product/ppt-run1-5-product-lab/deck_outline.json`: exact 10-slide product-lab deck outline.
- Create `docs/product/ppt-run1-5-product-lab/experiment_protocol.md`: three-arm experiment contract.
- Create `docs/product/ppt-run1-5-product-lab/baseline_prompt.md`: prompt-only generation input.
- Create `docs/product/ppt-run1-5-product-lab/vulca_generation_brief.md`: full Vulca generation input.
- Create `docs/product/ppt-run1-5-product-lab/bad_data_generation_brief.md`: corrupted-rules generation input.
- Create `docs/product/ppt-run1-5-product-lab/gemini_review_prompt.md`: product-lab contact-sheet review prompt.
- Create `docs/product/ppt-run1-5-product-lab/results/README.md`: result folder contract.
- Create `docs/product/ppt-run1-5-product-lab/results/asset_provenance.json`: committed provenance status for generated decks.
- Create `docs/product/ppt-run1-5-product-lab/results/comparison_report.md`: three-arm score and product decision report.
- Create `docs/product/ppt-run1-5-product-lab/results/comparison_report.json`: machine-readable three-arm score summary.
- Create `docs/product/ppt-run1-5-product-lab/results/iteration_log.md`: Gemini critique and repair-pass log.
- Create `docs/product/ppt-run1-5-product-lab/results/render_check.md`: renderer availability and native-render status.
- Create `docs/product/ppt-run1-5-product-lab/results/ablation_report.md`: learning-signal report for prompt-only, full Vulca, and bad-data arms.
- Create `docs/product/ppt-run1-5-product-lab/results/ablation_report.json`: machine-readable learning-signal summary.
- Create `docs/product/ppt-run1-5-product-lab/results/delivery_gate.md`: structural delivery QA summary.
- Modify `docs/product/roadmap.md`: add Run 1.5 product-lab status and keep renderer/native QA as the publishing blocker.

Generated local-only workspaces:

- `outputs/$THREAD_ID/presentations/ppt-run1-5-prompt-only/`
- `outputs/$THREAD_ID/presentations/ppt-run1-5-full-vulca/`
- `outputs/$THREAD_ID/presentations/ppt-run1-5-bad-data/`

Do not commit generated `.pptx`, preview images, layout JSON, local slide modules, or contact sheets unless the user explicitly approves release packaging.

---

### Task 1: Add Run 1.5 Validator Profile

**Files:**
- Modify: `tests/test_ppt_case_pack_validator.py`
- Modify: `scripts/validate_ppt_case_pack.py`

- [ ] **Step 1: Add failing tests for the `run1_5` profile**

Append these helpers and tests to `tests/test_ppt_case_pack_validator.py`:

```python
def write_run1_5_required_files(pack: Path) -> None:
    (pack / "tutorial_notes.md").write_text("# Tutorial Notes\n\nOriginal teaching notes.\n", encoding="utf-8")
    (pack / "experiment_protocol.md").write_text(
        "# Experiment Protocol\n\nThree arms: prompt-only, full Vulca, bad-data.\n",
        encoding="utf-8",
    )
    (pack / "bad_data_generation_brief.md").write_text(
        "# Bad Data Generation Brief\n\nUse intentionally mismatched design rules for the negative control.\n",
        encoding="utf-8",
    )
    (pack / "results" / "asset_provenance.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "assets": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "iteration_log.md").write_text("# Iteration Log\n\nNo repair pass yet.\n", encoding="utf-8")
    (pack / "results" / "render_check.md").write_text("# Render Check\n\nRenderer not checked yet.\n", encoding="utf-8")
    (pack / "results" / "ablation_report.md").write_text(
        "# Ablation Report\n\nPrompt-only, full Vulca, and bad-data arms not run yet.\n",
        encoding="utf-8",
    )
    (pack / "results" / "ablation_report.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "arms": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "comparison_report.json").write_text(
        json.dumps({"schema_version": 1, "status": "not-run", "scores": []}, indent=2),
        encoding="utf-8",
    )
    (pack / "results" / "delivery_gate.md").write_text(
        "# Delivery Gate\n\nPublic publishing is blocked before native render and human review.\n",
        encoding="utf-8",
    )


def valid_run1_5_design_memory() -> dict:
    return {
        "schema_version": 2,
        "contract": {
            "required_fields": [
                "evidence_id",
                "source_role",
                "observation",
                "design_rule",
                "slide_primitive",
                "layout_constraint",
                "qa_signal",
            ],
            "allowed_source_roles": ["brief", "source", "tutorial", "review"],
            "allowed_slide_primitives": [
                "cockpit",
                "learning_map",
                "comparison_delta",
                "qa_gate",
                "decision_table",
            ],
        },
        "observations": [
            {
                "evidence_id": "tutorial_hierarchy_to_delta",
                "source_role": "tutorial",
                "source_ids": ["supervity_ai_keynote"],
                "observation": "Dense AI stories become clearer when a single outcome anchors each process step.",
                "design_rule": "Use one dominant proof object per slide and replace full rubric tables with large comparison deltas.",
                "slide_primitive": "comparison_delta",
                "layout_constraint": "Main score delta must occupy the largest visual zone on comparison slides.",
                "qa_signal": "Gemini must comment on whether the comparison is understandable from the contact sheet.",
                "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks.",
            }
        ],
    }


def test_run1_5_profile_requires_product_lab_files(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert "missing required file: tutorial_notes.md" in result.errors
    assert "missing required file: experiment_protocol.md" in result.errors
    assert "missing required file: bad_data_generation_brief.md" in result.errors
    assert "missing required file: results/ablation_report.md" in result.errors
    assert "missing required file: results/ablation_report.json" in result.errors
    assert "missing required file: results/delivery_gate.md" in result.errors


def test_run1_5_profile_validates_design_memory_contract(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    (pack / "design_memory.json").write_text(json.dumps(valid_run1_5_design_memory(), indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is True, result.errors


def test_run1_5_profile_rejects_invalid_design_memory_primitive(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run1_5_required_files(pack)
    memory = valid_run1_5_design_memory()
    memory["observations"][0]["slide_primitive"] = "generic_card_grid"
    (pack / "design_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run1_5")

    assert result.ok is False
    assert "design_memory.observations[0].slide_primitive must be one of cockpit, comparison_delta, decision_table, learning_map, qa_gate" in result.errors
```

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: fail because `run1_5` is not an accepted profile.

- [ ] **Step 3: Add profile constants and allowed values**

Modify `scripts/validate_ppt_case_pack.py`:

```python
RUN1_5_REQUIRED_FILES = [
    *RUN1_REQUIRED_FILES,
    "experiment_protocol.md",
    "bad_data_generation_brief.md",
    "results/ablation_report.md",
    "results/ablation_report.json",
    "results/comparison_report.json",
    "results/delivery_gate.md",
]

RUN1_5_REQUIRED_MEMORY_FIELDS = [
    "evidence_id",
    "source_role",
    "observation",
    "design_rule",
    "slide_primitive",
    "layout_constraint",
    "qa_signal",
]

RUN1_5_SOURCE_ROLES = {"brief", "source", "tutorial", "review"}
RUN1_5_SLIDE_PRIMITIVES = {"cockpit", "learning_map", "comparison_delta", "qa_gate", "decision_table"}
```

Update `required_files_for_profile`:

```python
def required_files_for_profile(profile: str) -> list[str]:
    if profile == "default":
        return REQUIRED_FILES
    if profile == "run1":
        return [*REQUIRED_FILES, *RUN1_REQUIRED_FILES]
    if profile == "run1_5":
        return [*REQUIRED_FILES, *RUN1_5_REQUIRED_FILES]
    raise ValueError(f"unknown case-pack profile: {profile}")
```

- [ ] **Step 4: Add contract validation**

Add these helpers to `scripts/validate_ppt_case_pack.py`:

```python
def validate_choice(label: str, value: Any, allowed: set[str], errors: list[str]) -> bool:
    if not require_non_empty_string(label, value, errors):
        return False
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        errors.append(f"{label} must be one of {choices}")
        return False
    return True


def validate_run1_5_design_memory_contract(data: dict[str, Any], errors: list[str]) -> None:
    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("design_memory.contract must be an object")
        return

    required_fields = contract.get("required_fields")
    if not isinstance(required_fields, list) or required_fields != RUN1_5_REQUIRED_MEMORY_FIELDS:
        errors.append("design_memory.contract.required_fields must match the Run 1.5 design-memory contract")

    allowed_roles = contract.get("allowed_source_roles")
    if not isinstance(allowed_roles, list) or set(allowed_roles) != RUN1_5_SOURCE_ROLES:
        errors.append("design_memory.contract.allowed_source_roles must match the Run 1.5 source roles")

    allowed_primitives = contract.get("allowed_slide_primitives")
    if not isinstance(allowed_primitives, list) or set(allowed_primitives) != RUN1_5_SLIDE_PRIMITIVES:
        errors.append("design_memory.contract.allowed_slide_primitives must match the Run 1.5 slide primitives")
```

Replace the existing `validate_design_memory` body with logic that supports both profile versions:

```python
def validate_design_memory(pack_dir: Path, errors: list[str], profile: str = "run1") -> None:
    data = load_json(pack_dir / "design_memory.json", errors)
    require_keys("design_memory.json", data, ["schema_version", "observations"], errors)
    if "schema_version" in data:
        require_integer("design_memory.schema_version", data["schema_version"], errors)
    if profile == "run1_5":
        require_keys("design_memory.json", data, ["contract"], errors)
        validate_run1_5_design_memory_contract(data, errors)

    observations = data.get("observations", [])
    if not isinstance(observations, list) or not observations:
        errors.append("design_memory.observations must be a non-empty list")
        return

    base_required = ["source_ids", "do_not_copy"]
    run1_required = ["id", "principle", "code_generation_rule"]
    run1_5_required = [*RUN1_5_REQUIRED_MEMORY_FIELDS]
    required = [*base_required, *(run1_5_required if profile == "run1_5" else run1_required)]

    seen_ids: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"design_memory.observations[{index}] must be an object")
            continue
        require_keys(f"design_memory.observations[{index}]", observation, required, errors)

        id_key = "evidence_id" if profile == "run1_5" else "id"
        for key in required:
            if key == "source_ids":
                validate_string_list(f"design_memory.observations[{index}].source_ids", observation.get("source_ids"), errors)
            elif key in observation:
                require_non_empty_string(f"design_memory.observations[{index}].{key}", observation[key], errors)

        observation_id = observation.get(id_key)
        if isinstance(observation_id, str) and observation_id.strip():
            if observation_id in seen_ids:
                errors.append(f"design_memory.observations[{index}].{id_key} duplicates {observation_id}")
            seen_ids.add(observation_id)

        if profile == "run1_5":
            validate_choice(
                f"design_memory.observations[{index}].source_role",
                observation.get("source_role"),
                RUN1_5_SOURCE_ROLES,
                errors,
            )
            validate_choice(
                f"design_memory.observations[{index}].slide_primitive",
                observation.get("slide_primitive"),
                RUN1_5_SLIDE_PRIMITIVES,
                errors,
            )
```

Update the caller:

```python
if profile in {"run1", "run1_5"}:
    validate_design_memory(root, errors, profile=profile)
```

Update the CLI choices:

```python
parser.add_argument("--profile", choices=["default", "run1", "run1_5"], default="default")
```

- [ ] **Step 5: Run validator tests**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Lint and commit**

```bash
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git add scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git commit -m "test: add PPT Run 1.5 case-pack profile"
```

---

### Task 2: Add Run 1.5 Repository Contract Tests

**Files:**
- Create: `tests/test_ppt_run1_5_product_lab.py`

- [ ] **Step 1: Write failing repository tests**

Create `tests/test_ppt_run1_5_product_lab.py`:

```python
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


def test_run1_5_results_start_blocked_until_generated() -> None:
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    comparison_json = load_json(PACK / "results" / "comparison_report.json")
    ablation = (PACK / "results" / "ablation_report.md").read_text(encoding="utf-8")
    ablation_json = load_json(PACK / "results" / "ablation_report.json")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")

    assert_contains(comparison, ["Status", "not-run"])
    assert comparison_json["status"] == "not-run"
    assert_contains(ablation, ["prompt-only", "full Vulca", "bad-data"])
    assert ablation_json["status"] == "not-run"
    assert_contains(delivery, ["Public publishing", "blocked"])


def test_run1_5_pack_does_not_commit_generated_artifacts() -> None:
    blocked_suffixes = {".jpeg", ".jpg", ".mp4", ".pdf", ".png", ".pptx"}
    blocked = [str(path.relative_to(PACK)) for path in PACK.rglob("*") if path.is_file() and path.suffix.lower() in blocked_suffixes]

    assert blocked == []
```

Create `docs/product/ppt-run1-5-product-lab/experiment_protocol.md.json` as a machine-readable sidecar in Task 3. The Markdown file remains the human-readable protocol.

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest tests/test_ppt_run1_5_product_lab.py -q
```

Expected: fail because the Run 1.5 package does not exist.

- [ ] **Step 3: Commit the failing tests only if local workflow allows RED commits**

This repository usually commits verified GREEN changes, so keep the failing tests uncommitted until Task 3 makes them pass.

---

### Task 3: Create Run 1.5 Product-Lab Case Pack

**Files:**
- Create: `docs/product/ppt-run1-5-product-lab/**`
- Modify: `docs/product/roadmap.md`
- Test: `tests/test_ppt_run1_5_product_lab.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p docs/product/ppt-run1-5-product-lab/results
```

- [ ] **Step 2: Create the source registry**

Create `docs/product/ppt-run1-5-product-lab/sources.json` with the same canonical public sources used in Run 1:

```json
{
  "schema_version": 1,
  "sources": [
    {
      "id": "geo_figma_slides",
      "title": "GEO - Figma Slides",
      "url": "https://geo-nyc.com/projects/figma-slides/",
      "role": "presentation_product_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "figma_config_2024",
      "title": "Figma Config 2024 Recap",
      "url": "https://www.figma.com/blog/config-2024-recap/",
      "role": "product_event_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "figma_config_2025_identity",
      "title": "How Figma Shaped the Visual Identity for Config 2025",
      "url": "https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/",
      "role": "identity_system_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "supervity_ai_keynote",
      "title": "MUSE Creatives - Supervity AI Thought Leadership Presentation",
      "url": "https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/",
      "role": "commercial_ai_keynote_reference",
      "accessed_on": "2026-05-31",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    }
  ]
}
```

- [ ] **Step 3: Create the experiment protocol**

Create `docs/product/ppt-run1-5-product-lab/experiment_protocol.md`:

```markdown
# Experiment Protocol

Status: not-run

Run 1.5 compares three blocking arms:

| Arm | Input | Expected Signal |
| --- | --- | --- |
| `prompt_only` | Ordinary brief prompt with no case-pack files. | Coherent but generic deck, weaker proof surface, weaker provenance. |
| `full_vulca` | Commercial brief, source registry, tutorial notes, design memory, slide patterns, style tokens, and workflow rules. | Stronger specificity, visible design-memory influence, stronger QA evidence. |
| `bad_data` | Same commercial brief, but intentionally mismatched or corrupted design rules. | Visible degradation or review warnings proving the rules matter. |

Deferred arms: `source_only`, `tutorial_only`.

The main deck must show only the three blocking arms. The five-arm matrix is deferred until the three-arm experiment is stable.
```

Create `docs/product/ppt-run1-5-product-lab/experiment_protocol.md.json`:

```json
{
  "schema_version": 1,
  "status": "not-run",
  "arms": [
    {
      "id": "prompt_only",
      "input": "ordinary brief prompt with no case-pack files",
      "expected_signal": "coherent but generic deck, weaker proof surface, weaker provenance",
      "forbidden_inputs": [
        "design_memory.json",
        "tutorial_notes.md",
        "vulca_generation_brief.md",
        "vulca_ppt_skill.md"
      ],
      "blocking": true
    },
    {
      "id": "full_vulca",
      "input": "commercial brief, source registry, tutorial notes, design memory, slide patterns, style tokens, and workflow rules",
      "expected_signal": "stronger specificity, visible design-memory influence, stronger QA evidence",
      "forbidden_inputs": [],
      "blocking": true
    },
    {
      "id": "bad_data",
      "input": "same commercial brief with intentionally mismatched but structurally valid corrupted design rules",
      "expected_signal": "visible degradation or review warnings proving the rules matter",
      "forbidden_inputs": ["invalid_json", "malformed_pptx", "missing_required_files"],
      "blocking": true
    }
  ],
  "deferred_arms": ["source_only", "tutorial_only"]
}
```

- [ ] **Step 4: Create design memory**

Create `docs/product/ppt-run1-5-product-lab/design_memory.json` with at least these five observations:

```json
{
  "schema_version": 2,
  "contract": {
    "required_fields": [
      "evidence_id",
      "source_role",
      "observation",
      "design_rule",
      "slide_primitive",
      "layout_constraint",
      "qa_signal"
    ],
    "allowed_source_roles": ["brief", "source", "tutorial", "review"],
    "allowed_slide_primitives": ["cockpit", "learning_map", "comparison_delta", "qa_gate", "decision_table"]
  },
  "observations": [
    {
      "evidence_id": "brief_cockpit_input_surface",
      "source_role": "brief",
      "source_ids": ["geo_figma_slides", "supervity_ai_keynote"],
      "observation": "A commercial deck feels credible when the input constraints and buyer decision are visible before the solution claim.",
      "design_rule": "Use a brief cockpit slide with audience, business goal, must-win decision, constraints, source boundary, and do-not-copy rules.",
      "slide_primitive": "cockpit",
      "layout_constraint": "The brief cockpit slide must use one dominant input surface and no more than three secondary panels.",
      "qa_signal": "Gemini review must judge whether the slide reads as a product input surface rather than a generic explanation.",
      "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks."
    },
    {
      "evidence_id": "tutorial_rules_to_learning_map",
      "source_role": "tutorial",
      "source_ids": ["figma_config_2025_identity", "geo_figma_slides"],
      "observation": "Reusable visual systems become useful when small primitives can stretch across dense and expressive contexts.",
      "design_rule": "Use a learning-map slide that maps source evidence to design rule, slide primitive, layout constraint, and QA signal.",
      "slide_primitive": "learning_map",
      "layout_constraint": "The learning map must show four columns only when it is the central proof object; otherwise use two-column mappings.",
      "qa_signal": "Contact-sheet review must identify the data-to-rule transformation without reading body copy.",
      "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks."
    },
    {
      "evidence_id": "comparison_delta_over_full_table",
      "source_role": "review",
      "source_ids": ["supervity_ai_keynote"],
      "observation": "Dense AI capability is easier to believe when comparison evidence is simplified into visible outcomes.",
      "design_rule": "Use large score deltas and failure tags for the baseline comparison instead of a full rubric table in the main deck.",
      "slide_primitive": "comparison_delta",
      "layout_constraint": "Comparison delta slides must reserve the largest zone for the score difference and keep failure tags under four items.",
      "qa_signal": "Gemini review must comment on whether full Vulca wins for visible reasons, not only because the report says so.",
      "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks."
    },
    {
      "evidence_id": "publish_gate_as_product_feature",
      "source_role": "review",
      "source_ids": ["figma_config_2024", "supervity_ai_keynote"],
      "observation": "Review and delivery gates are product value when launch teams need reliable editable decks.",
      "design_rule": "Use a QA gate slide that separates structural QA, Gemini review, native renderer status, human approval, and public publish status.",
      "slide_primitive": "qa_gate",
      "layout_constraint": "The QA gate must show pass, caution, fail, or blocked states with consistent badge positions.",
      "qa_signal": "Delivery QA must record renderer status and never imply public readiness without native render and human approval.",
      "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks."
    },
    {
      "evidence_id": "evidence_selects_next_primitive",
      "source_role": "review",
      "source_ids": ["geo_figma_slides", "figma_config_2024"],
      "observation": "A product experiment should end with the next primitive selected from evidence, not taste preference.",
      "design_rule": "Use a decision table that maps score gaps and review warnings to renderer QA, layout primitives, data ingestion, repair workflow, or asset handling.",
      "slide_primitive": "decision_table",
      "layout_constraint": "The decision table must have one selected primitive and explicit rejected alternatives.",
      "qa_signal": "Comparison report must state which primitive is selected and why alternatives were not selected.",
      "do_not_copy": "Do not copy source visuals, layouts, screenshots, or brand marks."
    }
  ]
}
```

- [ ] **Step 5: Create remaining case-pack docs**

Create Markdown and JSON files listed in the File Map. They must satisfy these content rules:

- `README.md`: state `Status: not-run`, list the three arms, and state public publishing is blocked.
- `source_summaries.md`: contain one original paragraph per source and repeat the reference-analysis-only boundary.
- `tutorial_notes.md`: contain original notes for hierarchy, product surfaces, editable proof objects, and QA gates.
- `commercial_brief.md`: define audience, business goal, must-win decision, constraints, desired tone, and output promise.
- `design_notes.md`: define the three recurring product surfaces: Brief Cockpit, Learning Map, Experiment Lab.
- `narrative_rules.json`: use progression `brief`, `evidence_intake`, `memory_compilation`, `workflow`, `code_generation`, `comparison`, `ablation`, `qa_gate`, `decision`.
- `slide_patterns.json`: define the ten pattern ids from `EXPECTED_PATTERN_IDS`.
- `style_tokens.json`: define palette, font stack, spacing, corner radius, stroke widths, and a `layout_controls` object containing `dominant_proof_object_per_slide: true`, `max_secondary_panels: 3`, and `main_claim_contact_sheet_readable: true`.
- `asset_rules.json`: forbid copied reference visuals, logos, screenshots, copied layouts, rasterized text, and untracked media assets.
- `evaluation_rubric.md`: score prompt-only, full Vulca, and bad-data across commercial clarity, learning evidence, product-surface feel, visual hierarchy, editability, QA evidence, and rendering risk.
- `vulca_ppt_skill.md`: describe the Run 1.5 workflow without claiming post-training.
- `deck_outline.json`: use exactly 10 slides and the product-lab pattern sequence.
- `baseline_prompt.md`: explicitly say not to use case-pack files, design memory, tutorial notes, or Vulca workflow.
- `vulca_generation_brief.md`: explicitly say to use the Run 1.5 design-memory contract and product-lab slide primitives.
- `bad_data_generation_brief.md`: explicitly say to use corrupted rules such as generic card grids, mismatched visual hierarchy, and weak source boundaries as a negative control.
- `bad_data_generation_brief.md`: explicitly say that corrupted rules must remain structurally valid and must not use malformed JSON, missing required files, or intentionally broken PPTX packaging.
- `gemini_review_prompt.md`: ask Gemini whether the deck still feels like a generic GPT-generated explanatory deck.
- `results/*`: start at `not-run` and avoid claiming generated evidence before decks exist.
- `results/comparison_report.json`: start with `{"schema_version": 1, "status": "not-run", "scores": []}`.
- `results/ablation_report.json`: start with `{"schema_version": 1, "status": "not-run", "arms": []}`.

- [ ] **Step 6: Update roadmap**

Add a Run 1.5 line to `docs/product/roadmap.md` under `Next`:

```markdown
- PPT Run 1.5 product lab: three-arm proof that design evidence becomes design memory, affects code-generated PPT output, and exposes QA/publish gates.
```

- [ ] **Step 7: Run contract tests and validator**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1_5 docs/product/ppt-run1-5-product-lab
```

Expected: all tests pass and validator prints an OK status.

- [ ] **Step 8: Lint and commit**

```bash
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py
git add docs/product/ppt-run1-5-product-lab tests/test_ppt_run1_5_product_lab.py docs/product/roadmap.md
git commit -m "docs: add PPT Run 1.5 product lab package"
```

---

### Task 4: Generate Three Local Experiment Decks

**Files:**
- Local-only create: `outputs/$THREAD_ID/presentations/ppt-run1-5-prompt-only/**`
- Local-only create: `outputs/$THREAD_ID/presentations/ppt-run1-5-full-vulca/**`
- Local-only create: `outputs/$THREAD_ID/presentations/ppt-run1-5-bad-data/**`
- Modify committed docs after generation: `docs/product/ppt-run1-5-product-lab/results/comparison_report.md`
- Modify committed docs after generation: `docs/product/ppt-run1-5-product-lab/results/render_check.md`
- Modify committed docs after generation: `docs/product/ppt-run1-5-product-lab/results/asset_provenance.json`

- [ ] **Step 1: Load workspace dependencies**

Use the Codex app dependency helper before running artifact-tool generation:

```text
Call codex_app.load_workspace_dependencies
```

Record the bundled Node path and artifact-tool availability in the implementation notes.

- [ ] **Step 2: Create the prompt-only deck workspace**

Use the Presentations skill in `create` mode with primary profile `engineering-platform` and secondary gate `product-platform`.

Workspace:

```text
outputs/$THREAD_ID/presentations/ppt-run1-5-prompt-only
```

Generation constraints:

- Use only `baseline_prompt.md`.
- Do not read `design_memory.json`, `tutorial_notes.md`, or `vulca_generation_brief.md` while writing prompt-only slide modules.
- Record the prompt-only isolation boundary in the generation notes.
- Produce exactly 10 editable slides.
- Use native PowerPoint text and shapes for essential content.
- Export PPTX, preview PNGs, contact sheet, build manifest, and layout JSON.

Expected output paths:

```text
outputs/$THREAD_ID/presentations/ppt-run1-5-prompt-only/output/ppt-run1-5-prompt-only.pptx
outputs/$THREAD_ID/presentations/ppt-run1-5-prompt-only/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run1-5-prompt-only/layout/final
```

- [ ] **Step 3: Create the full Vulca deck workspace**

Use the Presentations skill in `create` mode with the same profile routing.

Workspace:

```text
outputs/$THREAD_ID/presentations/ppt-run1-5-full-vulca
```

Generation constraints:

- Use `vulca_generation_brief.md`.
- Use the design-memory contract and the 10-slide `deck_outline.json`.
- Make the deck look like a product lab run: Brief Cockpit, Learning Map, Experiment Lab, QA Gate, Product Decision.
- Produce exactly 10 editable slides.
- Export PPTX, preview PNGs, contact sheet, build manifest, and layout JSON.

Expected output paths:

```text
outputs/$THREAD_ID/presentations/ppt-run1-5-full-vulca/output/ppt-run1-5-full-vulca.pptx
outputs/$THREAD_ID/presentations/ppt-run1-5-full-vulca/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run1-5-full-vulca/layout/final
```

- [ ] **Step 4: Create the bad-data deck workspace**

Use the Presentations skill in `create` mode with the same profile routing.

Workspace:

```text
outputs/$THREAD_ID/presentations/ppt-run1-5-bad-data
```

Generation constraints:

- Use `bad_data_generation_brief.md`.
- Use deliberately weak or mismatched rules: generic cards, weak hierarchy, weak source boundaries, and poor product-surface feel.
- Keep the output editable and structurally valid. The negative control should be worse by design, not broken by malformed JSON, generator exceptions, invalid PPTX packaging, or missing required files.
- If generation crashes, record the crash as a failed experiment setup and fix the bad-data inputs until the arm generates a structurally valid but weaker deck.
- Produce exactly 10 editable slides.
- Export PPTX, preview PNGs, contact sheet, build manifest, and layout JSON.

Expected output paths:

```text
outputs/$THREAD_ID/presentations/ppt-run1-5-bad-data/output/ppt-run1-5-bad-data.pptx
outputs/$THREAD_ID/presentations/ppt-run1-5-bad-data/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run1-5-bad-data/layout/final
```

- [ ] **Step 5: Run structural checks for all three decks**

Run layout QA, PPTX integrity, and media checks for each workspace.

Commands for each arm:

```bash
unzip -t <workspace>/output/<deck>.pptx
zipinfo <workspace>/output/<deck>.pptx | rg '^ppt/media/' || true
```

Run artifact-tool layout QA using the same command pattern used in Run 1 workspaces. Expected: `0 error(s)` for each final deck.

- [ ] **Step 6: Run delivery QA for all three decks**

Use `scripts/validate_pptx_delivery.py`:

```bash
python3 scripts/validate_pptx_delivery.py \
  --pptx <workspace>/output/<deck>.pptx \
  --layout-dir <workspace>/layout/final \
  --contact-sheet <workspace>/preview/contact-sheet.png \
  --label "<human label>" \
  --out <workspace>/qa/delivery_report.md
```

Expected: each deck reports `internal-demo-ok-public-blocked` unless a hard structural error is found.

- [ ] **Step 7: Update committed run reports**

Update:

- `results/render_check.md`: record all three workspaces, slide counts, layout status, PPTX integrity, media entry count, and renderer availability.
- `results/asset_provenance.json`: record `status`, `arms`, `external_assets`, `generated_assets`, `copied_assets`, and `local_generated_workspaces`.
- `results/comparison_report.md`: record generation status and keep scoring pending until Gemini review.
- `results/comparison_report.json`: record each arm with `id`, `generation_status`, `pptx_path`, `contact_sheet_path`, `layout_dir`, `media_entries`, and `delivery_gate`.
- `results/ablation_report.json`: record each arm with `id`, `input_boundary`, `expected_signal`, `observed_signal`, and `warnings`.

- [ ] **Step 8: Verify and commit reports**

```bash
python3 -m pytest tests/test_ppt_run1_5_product_lab.py tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1_5 docs/product/ppt-run1-5-product-lab
git add docs/product/ppt-run1-5-product-lab/results
git commit -m "docs: record PPT Run 1.5 generation evidence"
```

---

### Task 5: Review, Score, Repair, And Finalize Run 1.5

**Files:**
- Modify: `docs/product/ppt-run1-5-product-lab/results/comparison_report.md`
- Modify: `docs/product/ppt-run1-5-product-lab/results/ablation_report.md`
- Modify: `docs/product/ppt-run1-5-product-lab/results/iteration_log.md`
- Modify: `docs/product/ppt-run1-5-product-lab/results/delivery_gate.md`
- Modify: `docs/product/roadmap.md`

- [ ] **Step 1: Run Gemini contact-sheet reviews**

Use Gemini-agent artifact review on all three contact sheets with this intent:

```text
Review whether this deck feels like a real product-lab output or a generic GPT-generated explanatory deck. Score content specificity, product-surface feel, learning evidence, visual hierarchy, editability cues, and QA/publish-gate clarity. For the bad-data arm, identify whether corrupted rules degraded the output or created review warnings.
```

Record artifact paths in `results/iteration_log.md`.

- [ ] **Step 2: Apply one focused repair pass to the full Vulca deck**

Repair only the weakest full-Vulca slides identified by Gemini and local visual inspection.

Allowed repairs:

- make the brief cockpit more like an input surface;
- make design-memory examples more concrete;
- replace dense tables with score deltas;
- make QA gate statuses more explicit;
- improve spacing and hierarchy without adding copied assets.

After repair, rebuild the full Vulca deck and rerun layout QA, PPTX integrity, media check, and delivery QA.

- [ ] **Step 3: Score the three arms**

Update `results/comparison_report.md` with integer 0-5 scores for:

- commercial clarity;
- learning evidence;
- product-surface feel;
- visual hierarchy;
- editability;
- QA evidence;
- rendering risk.

Expected decision logic:

```text
full Vulca must beat prompt-only on average;
bad-data must score lower than full Vulca or trigger explicit review warnings;
public publishing remains blocked until native render and human approval pass.
```

- [ ] **Step 4: Write ablation report**

Update `results/ablation_report.md` with:

- each arm's input boundary;
- expected signal;
- observed signal;
- whether the data-to-rule path appears to affect output;
- whether bad-data degraded output or triggered warnings;
- remaining uncertainty.

Also update `results/ablation_report.json` with the same arm ids and a compact machine-readable summary:

```json
{
  "schema_version": 1,
  "status": "reviewed",
  "arms": [
    {
      "id": "prompt_only",
      "input_boundary": "baseline_prompt.md only",
      "expected_signal": "generic but coherent",
      "observed_signal": "coherent deck with weaker product-surface evidence than full Vulca",
      "warnings": []
    }
  ]
}
```

- [ ] **Step 5: Write delivery gate summary**

Update `results/delivery_gate.md` with:

- structural QA status;
- native renderer availability;
- native render status;
- human review status;
- public publish status;
- next required action.

- [ ] **Step 6: Update roadmap**

Update `docs/product/roadmap.md` with the Run 1.5 outcome:

- keep Run 1.5 under active PPT wedge work if still blocked;
- move it to completed evidence only if comparison, ablation, and delivery reports are filled;
- keep renderer/native QA as a publishing blocker until native/manual inspection passes.

- [ ] **Step 7: Final verification and commit**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py tests/test_ppt_run1_case_pack.py tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1_5 docs/product/ppt-run1-5-product-lab
python3 scripts/validate_pptx_delivery.py --help
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
git status --short
git add docs/product/ppt-run1-5-product-lab docs/product/roadmap.md
git commit -m "docs: finalize PPT Run 1.5 product lab results"
```

Expected: tests and lint pass; generated `outputs/` remains untracked; committed reports do not claim public readiness unless native render and human review have actually passed.

---

## Final Verification

Run before pushing final Run 1.5 work:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py tests/test_ppt_run1_case_pack.py tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run1_5 docs/product/ppt-run1-5-product-lab
python3 scripts/validate_pptx_delivery.py --help
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
git status --short
```

Expected:

- all tests pass;
- Run 1.5 validator passes;
- delivery validator help exits 0;
- ruff check and format checks pass;
- `git ls-files outputs` returns no committed generated artifacts;
- `outputs/` is the only untracked generated artifact directory unless the user explicitly approves release artifacts.

## Self-Review

- Spec coverage: Tasks cover validator profile, product-lab package, three-arm experiment, prompt-only input isolation, structurally valid bad-data handling, design-memory contract, generated local decks, Gemini critique, ablation reporting, QA gate, and roadmap status.
- Scope control: The plan keeps the blocking experiment to prompt-only, full Vulca, and bad-data arms. Source-only, tutorial-only, full UI, visual regression templates, broad malformed-intake stress tests, and latency benchmarking are deferred.
- Placeholder scan: The plan contains no unfinished markers, unspecified file paths, or open-ended validation steps.
- Type consistency: The `run1_5` profile, design-memory fields, experiment arm ids, slide primitive ids, and expected pattern ids are consistent across tests, validators, package docs, and reports.
