# General Redraw Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the botanical showcase findings into a named first redraw strategy while preserving a general product architecture for future UI, poster, product, and texture strategies.

**Architecture:** Keep shared redraw routing, provider calls, debug artifacts, pasteback, and quality gates in the core. Add strategy naming and target-aware refinement for `small_botanical_subject_replacement`, and keep broad texture edits gated until a dedicated broad-texture strategy exists.

**Tech Stack:** Python 3.11, Pillow, NumPy, pytest, Vulca layers redraw pipeline.

---

## File Map

- Modify: `src/vulca/layers/mask_refine.py`
  - Rename the current `bright_small_subject` profile to `small_botanical_subject_replacement`.
  - Keep the extraction implementation local to the refinement module.
  - Preserve white and yellow evidence extraction.

- Modify: `src/vulca/layers/redraw.py`
  - Report the new strategy name in `redraw_advisory`.
  - Rename user-facing matte labels from flower-only wording to small botanical wording where safe.
  - Keep existing source-context replacement behavior unchanged.

- Modify: `src/vulca/layers/redraw_quality.py`
  - Keep broad texture repaint detection.
  - Make metrics/advisory serve the broader product contract.

- Modify: `tests/test_mask_refine.py`
  - Update strategy-name expectations.
  - Add yellow/buttercup/dandelion coverage assertions.

- Modify: `tests/test_layers_redraw_refinement.py`
  - Update advisory expectations.
  - Keep provider-call refusal test for broad hedge texture.

- Modify: `tests/test_layers_redraw_quality_gates.py`
  - Keep broad texture quality gate coverage.

- Create: `docs/superpowers/specs/2026-05-04-general-redraw-strategy-design.md`
  - Product architecture and scope.

- Create: `docs/superpowers/plans/2026-05-04-general-redraw-strategy.md`
  - This implementation plan.

## Task 1: Rename The Refinement Strategy Contract

**Files:**
- Modify: `tests/test_mask_refine.py`
- Modify: `src/vulca/layers/mask_refine.py`

- [x] **Step 1: Write failing tests**

Change strategy assertions in `tests/test_mask_refine.py` to expect:

```python
assert result.strategy == "small_botanical_subject_replacement"
```

Add or keep a yellow subject test:

```python
def test_refines_yellow_dandelion_heads_without_flower_keyword():
    source = Image.new("RGB", (320, 220), (76, 112, 52))
    draw = ImageDraw.Draw(source)
    centers = (
        (58, 42),
        (104, 56),
        (152, 48),
        (214, 78),
        (260, 96),
        (90, 138),
        (184, 152),
        (250, 166),
    )
    for cx, cy in centers:
        draw.line((cx, cy + 5, cx - 4, cy + 34), fill=(64, 105, 48), width=2)
        draw.ellipse((cx - 7, cy - 6, cx + 7, cy + 6), fill=(232, 190, 31))
        draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(176, 130, 18))

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((20, 18, 300, 190), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="roadside dandelion heads in grass",
        instruction="turn the yellow dots into buttercup meadow rhythm",
    )

    assert result.applied is True
    assert result.strategy == "small_botanical_subject_replacement"
    assert len(result.child_masks) >= 4
    assert result.metrics["refined_coverage_pct"] < 0.25
```

- [x] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_mask_refine.py -q
```

Expected: strategy-name assertions fail while existing extraction behavior still works.

- [x] **Step 3: Implement minimal rename**

In `src/vulca/layers/mask_refine.py`:

```python
SMALL_BOTANICAL_SUBJECT_REPLACEMENT = "small_botanical_subject_replacement"
```

Use it for `TargetRefinementProfile.kind`, `MaskRefinementResult.strategy`, and the formerly bright-small-subject profile.

- [x] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_mask_refine.py -q
```

Expected: all tests in `tests/test_mask_refine.py` pass.

## Task 2: Update Redraw Advisory To Match Strategy Product Language

**Files:**
- Modify: `tests/test_layers_redraw_refinement.py`
- Modify: `src/vulca/layers/redraw.py`

- [x] **Step 1: Write failing advisory tests**

Update refinement advisory expectations:

```python
assert advisory["refinement_strategy"] == "small_botanical_subject_replacement"
assert advisory["refinement_edit_matte"] == "small_botanical_evidence"
assert advisory["refinement_replacement_matte"] == "small_botanical_removal"
assert advisory["refinement_composition"] == "small_botanical_evidence_paint_cover"
```

Keep the broad hedge test expectation:

```python
assert advisory["redraw_skip_reason"] == "broad_texture_repaint_risk"
assert provider.calls == []
```

- [x] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layers_redraw_refinement.py::test_refined_flower_layer_uses_one_masked_edit_per_child tests/test_layers_redraw_refinement.py::test_auto_redraw_skips_broad_leaf_texture_risk -q
```

Expected: advisory string assertions fail before implementation.

- [x] **Step 3: Implement advisory rename**

In `src/vulca/layers/redraw.py`, change only advisory labels. Do not change the image generation behavior:

```python
"refinement_edit_matte": "small_botanical_evidence"
"refinement_replacement_matte": "small_botanical_removal"
"refinement_composition": "small_botanical_evidence_paint_cover"
```

- [x] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layers_redraw_refinement.py::test_refined_flower_layer_uses_one_masked_edit_per_child tests/test_layers_redraw_refinement.py::test_auto_redraw_skips_broad_leaf_texture_risk -q
```

Expected: both tests pass.

## Task 3: Keep Broad Texture Edits Gated

**Files:**
- Modify: `tests/test_layers_redraw_quality_gates.py`
- Modify: `src/vulca/layers/redraw_quality.py`

- [x] **Step 1: Preserve broad texture tests**

Keep this behavior:

```python
report = evaluate_redraw_quality(
    source,
    output,
    description="leafy hedge texture",
    instruction="redraw leaf highlights as hand-painted botanical texture",
    refinement_applied=False,
    refined_child_count=0,
)

assert not report.passed
assert "broad_texture_repaint" in report.failures
assert report.metrics["src_area_pct"] > 50
assert report.metrics["output_luma_delta_pct"] < -25
```

- [x] **Step 2: Verify**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layers_redraw_quality_gates.py -q
```

Expected: quality gate tests pass after the strategy rename.

## Task 4: Full Targeted Regression

**Files:**
- Verify only.

- [x] **Step 1: Run targeted redraw regression**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layers_redraw_refinement.py tests/test_mask_refine.py tests/test_layers_redraw.py tests/test_layers_redraw_crop_pipeline.py tests/test_layers_redraw_mask_aware.py tests/test_layers_redraw_strategy.py tests/test_inpaint_mask.py tests/test_mcp_layers_redraw_advisory.py tests/test_layers_redraw_quality_gates.py -q
```

Expected: all targeted tests pass.

- [x] **Step 2: Run diff check**

Run:

```bash
git diff --check
```

Expected: no whitespace errors.

## Task 5: Product Follow-Up Tracking

**Files:**
- No code changes.

- [x] **Step 1: Record next strategy candidates**

After the v0.23 patch is verified, track future strategy candidates outside
this branch:

- `ui_element_redraw`
- `poster_layout_redraw`
- `product_photo_retouch`
- `broad_texture_style_edit`
- `text_region_edit`

- [x] **Step 2: Do not implement future strategies in this branch**

This branch stays scoped to the first production strategy and the broad-texture
safety gate.

## Execution Evidence

- RED verified for `tests/test_mask_refine.py`: strategy-name assertions failed
  against the old `bright_small_subject` contract.
- RED verified for
  `tests/test_layers_redraw_refinement.py::test_refined_flower_layer_uses_one_masked_edit_per_child`:
  advisory strategy assertion failed against the old contract.
- GREEN verified for `tests/test_mask_refine.py`: `8 passed`.
- GREEN verified for the targeted redraw advisory tests: `2 passed`.
- Full targeted regression:
  `90 passed, 5 warnings`.
- `git diff --check`: passed.
