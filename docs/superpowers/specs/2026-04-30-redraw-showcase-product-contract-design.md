# Redraw Showcase Product Contract Design

## Status

Approved direction from product discussion on 2026-04-30. This document turns the redraw/showcase motivation into a stable product and interface contract for webapp and showcase consumers.

## Context

The v0.22 redraw work proves that Vulca can refine a broad semantic mask into smaller child masks, route those child masks through masked edits, and preserve source-local alpha. That is necessary but not sufficient for a user-facing showcase.

The key product issue is output interpretation. A redrawn RGBA layer is an editable asset. It is not the final user preview by itself, especially when it is sparse, transparent, or alpha-bounded. A real user judges the edit in the source image context: did the selected area improve, and did the rest of the image remain intact?

## Product Decision

Redraw has two outputs with different purposes:

1. **Editable layer asset:** the `file` returned by `layers_redraw`. This remains the canonical layer output for later edits, compositing, layer tree inspection, and debugging.
2. **Source pasteback preview:** the `source_pasteback_path` returned when the manifest has a resolvable `source_image`. This is the canonical webapp/showcase preview for user review.

The webapp and showcase should display `source_pasteback_path` as the primary "after" image whenever it exists. The transparent layer asset should be shown only in an inspector/debug panel or in layer editing contexts.

## User Motivation Timeline

Redraw should be presented as a capability ladder, not one flat feature.

| Phase | User Promise | Product Meaning | Required Proof | Showcase Role |
| --- | --- | --- | --- | --- |
| Phase 1: Precision Retouching | "Change this exact local thing without damaging the source." | Trust, locality, source preservation. | Masked edit, alpha-bound pasteback, surrounding pixels preserved, quality advisory returned. | Engineering baseline and regression gate. |
| Phase 2: Local Art Direction | "Make this selected object carry a deliberate style, story, or design role." | Taste and controlled creative intent on top of Phase 1 locality. | Strong prompt motive, designed local result, source pasteback preview, no sticker edge. | Next public-facing showcase. |
| Phase 3: Scene Recomposition | "Use layers as instruments to redesign the whole image coherently." | Multi-layer direction and whole-scene orchestration. | Concept prompt, layer roles, edit order, consistency checks, final-canvas evaluation. | Future flagship capability. |

Phase 1 is the reliability contract. Phase 2 is the current showcase narrative. Phase 3 should not be sold until multi-layer orchestration is explicit.

## Prompt Contract

Showcase prompts should explain the user's motive, not just describe replacement pixels.

A redraw prompt should contain:

- **User motive:** why the user wants this local edit.
- **Target scope:** which selected layer or child mask may change.
- **Visual role:** what the local object should contribute to the image.
- **Preservation constraints:** what must remain unchanged.
- **Anti-goals:** visible failure modes to avoid.

For the roadside flower showcase, the Phase 2 prompt is:

> The user likes the roadside composition, but this flower cluster feels random and visually flat. Redraw only the selected flower-cluster child masks as a deliberate storybook botanical accent. Preserve the hedge texture, source lighting, and spatial depth. Add rhythmic small white blossoms with subtle warm yellow centers and hand-painted detail. Blend naturally into the hedge; avoid sticker-like edges, oversized flowers, or changes outside the selected masks.

Weak prompts such as "small bright white wildflowers" are allowed for unit tests, but should not be used for product showcases because they express pixel content without user intent.

## API Contract

`layers_redraw(...)` returns a layer payload. The stable product interpretation is:

| Field | Presence | Meaning | Webapp Use |
| --- | --- | --- | --- |
| `name` | Always on success | Output layer name. | Layer tree label. |
| `file` | Always on success | Editable RGBA layer asset. | Layer inspector, subsequent edit input, debug display. |
| `z_index` | Always on success | Layer stack ordering. | Layer tree and closed-loop composite. |
| `content_type` | Always on success | Semantic layer category. | Layer grouping/filtering. |
| `source_pasteback_path` | When `source_image` resolves and pasteback succeeds | Flat preview of the redrawn layer composited onto the original source. | Primary after-image in webapp/showcase. |
| `source_pasteback_blend_mode` | With `source_pasteback_path` | Blend mode used for pasteback, currently `alpha`. | Optional debug metadata. |
| `source_pasteback_error` | When pasteback was attempted and failed | Non-fatal preview generation failure. | Show warning and fall back to layer/composite view. |
| `redraw_route`, `route_requested`, `route_chosen` | Advisory | How the provider path was selected. | Badge/debug metadata. |
| `quality_gate_passed`, `quality_failures` | Advisory | Local quality gate result. | Review state and rerun cue. |
| `refinement_applied`, `refined_child_count`, `refinement_reason`, `refinement_strategy`, `mask_granularity_score` | Advisory when v0.22 refinement is evaluated | Whether target-aware refinement transformed a broad mask into child masks. | Explain why multiple edits occurred and whether granularity is trustworthy. |

Advisory fields are additive diagnostics. Consumers must tolerate missing advisory keys, especially for legacy or merge paths. Missing advisory metadata should degrade to an "unknown quality" review state; it should not hide a valid `source_pasteback_path`.

`source_pasteback_path` is a side-car preview artifact. It does not replace `file`, does not mutate the manifest layer entry, and should not be treated as an editable layer.

If `source_pasteback_path` is missing, the webapp should not silently treat `file` as the final after-image. It should choose one explicit fallback:

- call `layers_paste_back` if a source image is available but not resolved by `layers_redraw`;
- call `layers_composite` when the user is reviewing the closed-loop layer stack rather than the original source image;
- show the transparent layer asset with a clear "layer asset" label and checkerboard background.

## Webapp Display Contract

For redraw result review, the default webapp view should be:

1. **Before:** original source image, not the isolated layer.
2. **After:** `source_pasteback_path` when present.
3. **Selection context:** layer name, route badge, refinement count, and quality gate state.
4. **Inspector:** `file`, masks, crops, raw provider outputs, and patch assets.

The main result view should never promote a sparse transparent layer as the final outcome. That made the previous showcase look incomplete because the user saw the layer artifact rather than the source-context edit.

## Review States

The webapp can derive a simple product state from the payload:

| State | Condition | UI Meaning |
| --- | --- | --- |
| Ready for review | `source_pasteback_path` exists and `quality_gate_passed` is true | Show before/after as the main result. |
| Technical preview | `source_pasteback_path` exists and `quality_gate_passed` is false | Show before/after, but mark as needing rerun or manual review. |
| Unknown quality preview | `source_pasteback_path` exists and `quality_gate_passed` is missing | Show before/after, but keep quality metadata neutral. |
| Layer-only result | `source_pasteback_path` is missing and no pasteback error exists | Show layer inspector; do not frame as final image. |
| Pasteback warning | `source_pasteback_error` exists | Show warning and offer explicit pasteback/composite fallback. |

These states are intentionally conservative. They prevent the UI from overselling technically valid but visually unfinished outputs.

## Data Flow

1. User selects a layer or target region.
2. Webapp calls `layers_redraw` with a motive-rich instruction.
3. Redraw produces an editable RGBA layer.
4. Redraw attempts source pasteback when `source_image` is available.
5. Webapp displays `source_pasteback_path` as the primary after-image.
6. Webapp shows advisory metadata as review/debug context.
7. User accepts, reruns with a stronger prompt, or escalates to a future scene-level workflow.

## Implementation Hooks

- `vulca.layers.redraw_review.classify_redraw_review(payload)` is the canonical in-repo state classifier for redraw payloads.
- External webapps should mirror the classifier's state names: `ready_for_review`, `technical_preview`, `unknown_quality_preview`, `layer_only_result`, `pasteback_warning`.
- `scripts/build_redraw_review.py` is the static showcase dogfood path. It reads a `summary.json`, chooses the best available source-context after-image, and renders a before/after HTML page.
- `source_pasteback_path` remains the highest-priority after-image input. A transparent `file` should be rendered as an inspector asset unless no pasteback exists.

## Acceptance Criteria

- A redraw response with `source_pasteback_path` causes the webapp/showcase to display that path as the main after-image.
- The `file` field remains available and is not reinterpreted as the final source-context image.
- The Phase 2 showcase prompt includes user motive, target scope, visual role, preservation constraints, and anti-goals.
- A failed or missing pasteback is visible in UI state instead of silently showing a sparse layer as a final result.
- Phase 3 language is kept future-facing until multi-layer orchestration exists.

## Non-Goals

- This contract does not replace `layers_composite`; stack compositing remains useful for closed-loop layered artworks.
- This contract does not require every legacy manifest to have `source_image`.
- This contract does not define the full Phase 3 orchestration engine.
- This contract does not guarantee provider visual quality; it defines how to present and evaluate the result honestly.
