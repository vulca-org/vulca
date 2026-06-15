# Layer Redraw And Mask Gates

Vault status: protected technical memory.

## The Core Problem

Layer redraw looked simple but became one of the most important technical
workstreams. The recurring failure was this:

> A sparse or semantically broad layer was sent to a provider without enough
> spatial evidence. The provider painted the wrong thing or changed too much,
> then alpha preservation hid the full failure until pasteback.

## Historical Repairs

### Native Mask Inpaint

`inpaint_artwork(mask_path=...)` added a native masked-edit route for providers
that support it.

### Safer Redraw Defaults

`layers_redraw` moved away from destructive defaults:

- do not overwrite input layer by default
- flatten alpha-sparse layers onto safer reference backgrounds
- preserve original alpha
- write separate redrawn output

### Mask-Aware Routing

Sparse alpha layers route to masked edit paths when provider capabilities allow.
This prevents unmasked img2img from painting a whole canvas with no target cue.

### Crop-Aware Geometry

v0.21 added geometry classification:

- dense full-canvas path
- sparse bbox crop path
- bounded per-component path
- all-edit mask shim for models requiring masks

MCP responses expose advisory fields so the operator can see what happened.

### Target-Aware Mask Refinement

v0.22 identified another defect: sometimes the parent mask is too broad for the
user's target. The system can infer a target profile, create child masks, redraw
child patches, and paste them back through tighter alpha.

## Quality Gates

Known gate signals include:

- `area_pct`
- `bbox_fill`
- `component_count`
- `redraw_route`
- `geometry_redraw_route`
- `quality_gate_passed`
- `quality_failures`
- `refinement_applied`
- `refined_child_count`
- `mask_granularity_score`
- alpha expansion
- background bleed
- large white component
- target color identity loss
- pasteback mismatch

## Product Boundary

Redraw is implemented and heavily tested at the contract level. That does not
make every real-provider output public-ready.

Allowed public phrasing:

> VULCA exposes mask-aware redraw routes, pasteback previews, and quality
> advisory signals for review.

Disallowed public phrasing:

> VULCA has solved image editing quality.

## Sources

- `CHANGELOG.md`
- `docs/superpowers/specs/2026-04-26-v0.18-layers-redraw-split-design.md`
- `docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md`
- `docs/superpowers/specs/2026-04-30-v0.22-target-aware-mask-refinement-design.md`
- `tests/test_layers_redraw_mask_aware.py`
- `tests/test_layers_redraw_crop_pipeline.py`
- `tests/test_layers_redraw_quality_gates.py`
- `tests/test_mask_refine.py`
- `tests/test_paste_back.py`
