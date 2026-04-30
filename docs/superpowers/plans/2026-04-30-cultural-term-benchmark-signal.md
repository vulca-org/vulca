# Cultural-Term Benchmark Signal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure all cultural-term efficacy benchmark projects produce non-empty selected culture terms and concrete visual operations before real-provider generation.

**Architecture:** Keep the fix narrow: add benchmark contract tests, let the harness seed terms from each `ExperimentProject.tradition_terms` only when profile extraction is empty, and add concrete visual-operation mappings for the benchmark-specific spiritual/material terms. Provider execution, credentials, and artifact schemas stay unchanged.

**Tech Stack:** Python standard library, dataclasses, existing Vulca discovery modules, pytest.

---

## File Map

- Modify `tests/test_visual_discovery_benchmark.py`: add benchmark signal contract tests.
- Modify `scripts/visual_discovery_benchmark.py`: add a benchmark-scoped taste-profile helper and use it in `select_direction_card()`.
- Modify `src/vulca/discovery/terms.py`: add concrete visual-operation entries for benchmark spiritual/material terms.

## Task 1: Add Benchmark Signal Contract Tests

**Files:**
- Modify: `tests/test_visual_discovery_benchmark.py`

- [ ] **Step 1: Add test that every benchmark project has usable direction-card signal**

Append this test after `test_build_conditions_a_through_d`:

```python
def test_all_experiment_projects_have_nonempty_direction_signal():
    from scripts.visual_discovery_benchmark import (
        build_conditions,
        build_experiment_projects,
        select_direction_card,
    )

    for project in build_experiment_projects():
        card = select_direction_card(project)
        conditions = build_conditions(project.prompt, card)
        by_id = {condition["id"]: condition for condition in conditions}

        assert card.culture_terms, project.slug
        assert by_id["B"]["culture_terms"], project.slug
        assert by_id["C"]["culture_terms"], project.slug
        assert by_id["D"]["culture_terms"], project.slug
        assert "Culture terms:\n\n" not in by_id["D"]["prompt"], project.slug
        assert by_id["D"]["negative_prompt"], project.slug
        assert by_id["D"]["evaluation_focus"]["L3"], project.slug
```

- [ ] **Step 2: Add test that benchmark-specific projects avoid generic fallback ops**

Append this test after the previous test:

```python
def test_spiritual_and_material_projects_use_specific_visual_ops():
    from scripts.visual_discovery_benchmark import (
        get_experiment_project,
        select_direction_card,
    )

    spiritual = select_direction_card(
        get_experiment_project("spiritual-editorial-poster")
    )
    material = select_direction_card(
        get_experiment_project("cultural-material-campaign")
    )

    assert spiritual.culture_terms == ["sacred atmosphere"]
    assert "ritualized stillness" in spiritual.visual_ops.composition
    assert "literal religious iconography" in spiritual.visual_ops.avoid

    assert material.culture_terms == ["material culture"]
    assert "macro material detail" in material.visual_ops.composition
    assert "generic product render" in material.visual_ops.avoid
```

- [ ] **Step 3: Verify RED**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py::test_all_experiment_projects_have_nonempty_direction_signal tests/test_visual_discovery_benchmark.py::test_spiritual_and_material_projects_use_specific_visual_ops -q
```

Expected: fail because spiritual/material projects currently produce empty terms or generic fallback visual ops.

## Task 2: Seed Benchmark Terms When Profile Extraction Is Empty

**Files:**
- Modify: `scripts/visual_discovery_benchmark.py`

- [ ] **Step 1: Add `replace` import**

Change:

```python
from dataclasses import dataclass
```

to:

```python
from dataclasses import dataclass, replace
```

- [ ] **Step 2: Add helper before `select_direction_card()`**

Add:

```python
def _taste_profile_for_project(project: ExperimentProject):
    profile = infer_taste_profile(
        slug=project.slug,
        intent=f"{project.prompt}; {'; '.join(project.tradition_terms)}",
    )
    if profile.culture_terms:
        return profile
    return replace(
        profile,
        culture_terms=list(project.tradition_terms),
        confidence="med",
    )
```

- [ ] **Step 3: Use helper in `select_direction_card()`**

Replace the inline `infer_taste_profile()` call with:

```python
profile = _taste_profile_for_project(project)
```

- [ ] **Step 4: Verify first test improves**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py::test_all_experiment_projects_have_nonempty_direction_signal -q
```

Expected: pass, while the specific-ops test still fails until Task 3.

## Task 3: Add Concrete Visual Ops for Benchmark Terms

**Files:**
- Modify: `src/vulca/discovery/terms.py`

- [ ] **Step 1: Add `sacred atmosphere` visual ops**

Add an entry to `TERM_VISUAL_OPS`:

```python
"sacred atmosphere": {
    "composition": (
        "ritualized stillness, centered breathing space, slow vertical hierarchy"
    ),
    "color": "quiet deep neutrals with a restrained warm focal glow",
    "texture": "soft grain, matte paper, or stone-like surfaces with low noise",
    "symbol_strategy": (
        "suggest reverence through light, spacing, and posture rather than doctrine"
    ),
    "avoid": [
        "literal religious iconography",
        "fantasy magic glow",
        "generic wellness poster symbolism",
    ],
    "evaluation_focus": {
        "L1": "the focal hierarchy feels calm and intentional",
        "L2": "light and spacing create atmosphere without clutter",
        "L3": "spiritual tone is non-denominational and culturally careful",
        "L4": "the poster feels contemplative rather than decorative",
        "L5": "quietness creates depth beyond mood styling",
    },
},
```

- [ ] **Step 2: Add `quiet symbolism` visual ops**

Add:

```python
"quiet symbolism": {
    "composition": "small symbolic cue held by generous surrounding space",
    "color": "muted palette with one low-saturation symbolic accent",
    "texture": "subtle surface detail that rewards close reading",
    "symbol_strategy": "use implication, shadow, alignment, or absence as the sign",
    "avoid": [
        "obvious icon collage",
        "mystical cliché symbols",
        "overexplained visual metaphors",
    ],
    "evaluation_focus": {
        "L1": "symbolic cue is readable but not loud",
        "L2": "composition supports slow discovery",
        "L3": "symbol avoids borrowed sacred cliches",
        "L4": "meaning emerges through restraint",
        "L5": "the image sustains interpretation after first glance",
    },
},
```

- [ ] **Step 3: Add material/craft visual ops**

Add:

```python
"material culture": {
    "composition": (
        "macro material detail paired with a clear product or campaign anchor"
    ),
    "color": "earth, fiber, clay, metal, or dye colors tied to the material story",
    "texture": "visible weave, grain, patina, tool marks, or handmade irregularity",
    "symbol_strategy": (
        "let material behavior carry cultural specificity instead of motifs"
    ),
    "avoid": [
        "generic product render",
        "surface pattern pasted onto an object",
        "unexplained ethnic ornament",
    ],
    "evaluation_focus": {
        "L1": "material is visually legible",
        "L2": "craft detail affects composition and lighting",
        "L3": "cultural reference comes from material behavior",
        "L4": "campaign intent and material story reinforce each other",
        "L5": "the visual has specificity beyond styling",
    },
},
"specific craft": {
    "composition": "process-aware framing with tool, hand, join, fold, or edge detail",
    "color": "palette follows real craft materials and production residue",
    "texture": "worked surfaces, seams, brush drag, fibers, or carved edges",
    "symbol_strategy": "show evidence of making instead of generic craft labels",
    "avoid": [
        "fake handmade filter",
        "decorative craft props",
        "perfect plastic surfaces",
    ],
    "evaluation_focus": {
        "L1": "the craft cue is visible",
        "L2": "execution shows process evidence",
        "L3": "craft specificity is grounded",
        "L4": "making process supports the campaign idea",
        "L5": "craft detail gives the image lasting substance",
    },
},
"local texture": {
    "composition": "environmental texture supports the product without visual clutter",
    "color": "local material colors with controlled contrast",
    "texture": "weathering, fibers, stone, paper, soil, or finish variations",
    "symbol_strategy": "use place-specific material evidence, not postcard symbols",
    "avoid": [
        "tourist landmark shorthand",
        "generic rustic texture",
        "random background grit",
    ],
    "evaluation_focus": {
        "L1": "texture is clear and organized",
        "L2": "texture supports product hierarchy",
        "L3": "locality is implied through material evidence",
        "L4": "texture choice matches campaign intent",
        "L5": "place specificity deepens the concept",
    },
},
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py::test_all_experiment_projects_have_nonempty_direction_signal tests/test_visual_discovery_benchmark.py::test_spiritual_and_material_projects_use_specific_visual_ops -q
```

Expected: pass.

## Task 4: Final Verification and Commit

**Files:**
- All files above.

- [ ] **Step 1: Run focused benchmark tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py -q
```

Expected: pass.

- [ ] **Step 2: Verify dry-run prompts**

Run:

```bash
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --output-root /private/tmp/vulca-cultural-term-signal-dry-run --date 2026-04-30
```

Expected: exits 0 and writes three dry-run directories.

- [ ] **Step 3: Inspect D prompts for empty culture term blocks**

Run:

```bash
grep -RIn "Culture terms:$" /private/tmp/vulca-cultural-term-signal-dry-run/2026-04-30-*/prompts/D.txt
```

Expected: no matches.

- [ ] **Step 4: Check whitespace**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 5: Commit**

Run:

```bash
git add scripts/visual_discovery_benchmark.py src/vulca/discovery/terms.py tests/test_visual_discovery_benchmark.py docs/superpowers/specs/2026-04-30-cultural-term-benchmark-signal-design.md docs/superpowers/plans/2026-04-30-cultural-term-benchmark-signal.md
git commit -m "fix: strengthen cultural term benchmark signal"
```
