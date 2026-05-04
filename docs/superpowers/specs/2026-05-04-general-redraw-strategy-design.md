# General Redraw Strategy Design

## Status

Draft for v0.23 implementation. This document turns the roadside botanical
showcase findings into a general redraw product architecture, while keeping the
current branch scoped to the first production strategy.

## Product Direction

Vulca redraw should not become a pile of case-specific prompt patches. The
general product should be a strategy-routed edit system:

1. Diagnose the requested edit and current mask.
2. Choose a strategy with explicit constraints.
3. Run a provider edit with source context and mask contracts.
4. Apply quality gates before accepting the pasteback.
5. Return advisory when the request is unsafe for the selected strategy.

The generality comes from shared contracts and routing. Specialized behavior is
allowed only inside named strategies with tests and quality gates.

## Strategy Model

### Shared Redraw Core

The shared core owns provider routing, source crop padding, mask diagnostics,
debug artifacts, cost/usage reporting, pasteback, and quality reporting.
Strategies should not duplicate these responsibilities.

### Strategy Registry

Each strategy declares:

- Intent class: remove, replace, add, local style, global style, layout edit,
  text edit, or product/background edit.
- Target class: small object, large texture, UI element, poster element,
  product object, text block, or unknown.
- Mask policy: allowed coverage, component count, child split policy, and
  source-context padding.
- Matte contract: edit matte, removal matte, generation matte, and output alpha.
- Provider contract: endpoint, model knobs, prompt constraints, and fallback.
- Quality gates: artifact checks, preservation checks, and refusal conditions.

The current branch should add the first production strategy:

```text
small_botanical_subject_replacement
```

This strategy covers small repeated botanical objects such as white flower
heads, yellow dandelion heads, buttercups, blossoms, petals, and similar small
visual targets. It does not cover broad hedge, grass, foliage, tree, or leaf
texture redraw.

## Current Findings

The roadside showcase produced three important observations:

- White flower and yellow flower edits work when the target is split into small
  child masks and the model edits source-context crops.
- Old flower residue is reduced when removal matte and generation matte are
  separated instead of using one alpha mask for every stage.
- Broad leaf/hedge texture repaint is unsafe. A temporary green-leaf probe had
  roughly 57% crop mask coverage and produced a dark pasted texture block.

These findings mean botanical small-object replacement is worth productizing,
but broad plant texture redraw must be gated until a dedicated strategy exists.

## v0.23 Scope

This branch should land the following only:

- General naming and advisory framing for a small botanical strategy.
- Target-aware refinement for white and yellow small botanical subjects.
- Broad texture preflight skip/advisory when the mask is too wide for local
  redraw.
- Tests covering white flowers, yellow flowers, and broad hedge refusal.
- Documentation that explains why this is the first strategy, not the whole
  general redraw product.
- A record that local showcase artifacts were used as evidence, without making
  the full generated artifact directory part of the default source commit.

This branch should not attempt:

- UI redraw.
- Poster/layout redraw.
- Product photo retouching.
- Text editing.
- Broad hedge/grass/tree style transfer.

## Artifact Policy

The local roadside showcase directory
`docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_23_gpt_image_2/`
contains generated provider outputs and intermediate debug files. It is useful
for visual evidence, but it is not part of the default v0.23 source patch: the
directory can be multiple gigabytes and contains many repeated run artifacts.

For review, keep only curated paths in the written summary or a deliberately
selected visual appendix. Do not commit every child crop, raw output, and replay
directory unless a release or artifact-storage decision explicitly asks for it.

## Product Roadmap

### Phase 1: Strategy Infrastructure

Define strategy metadata and diagnostics without changing user-facing behavior
too much. Add a registry once there are at least two production strategies.

Minimum shared diagnostics:

- mask area percentage
- mask bbox percentage
- bbox fill ratio
- component count
- refined child count
- refined coverage percentage
- mask granularity score
- output luma delta
- artifact ratios such as dark fill and olive fill

### Phase 2: Small Object Replacement

Make small object replacement the stable local-edit lane. Botanical subjects are
the first instance. Later targets can include small icons, stickers, fruit,
jewelry, props, and other repeated objects if their masks are precise.

### Phase 3: UI and Layout Strategies

UI and poster redraw require different contracts:

- preserve text or force OCR-safe regeneration
- preserve layout grids and alignment
- protect icons and logos
- evaluate outside-mask layout drift
- avoid source-photo botanical color heuristics

They should be separate strategies, not extensions of botanical replacement.

### Phase 4: Broad Texture and Global Style

Broad texture redraw needs a dedicated strategy with structure preservation,
style reference control, and stronger outside-mask metrics. Until then, broad
texture masks should return advisory instead of being silently edited.

## Success Criteria

For v0.23:

- White flower and yellow flower targets infer the same small botanical strategy.
- Broad hedge/leaf texture requests with broad masks skip provider calls in auto
  route and return advisory.
- Quality gates report why a result is risky.
- Debug artifacts preserve child input, mask, raw, patch, and pasteback.
- Tests cover the intended behavior without relying on real provider calls.
