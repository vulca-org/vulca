---
slug: 2026-04-28-ipad-cartoon-roadside-direct-showcase
status: resolved
schema_version: "0.1"
domain: brand_visual
tradition: null
generated_by: visual-spec@0.1.0
proposal_ref: docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/proposal.md
created: 2026-04-28
updated: 2026-04-28
---

# IMG_6847 Direct iPad-Cartoon Showcase - Technical Design

## A. Provider + Generation Params

```yaml
reviewed: true
provider: openai
model_primary: gpt-image-2
model_fallback: gpt-image-1.5
quality: high
input_fidelity: null
size: 1536x1024
seed: null
steps: null
cfg_scale: null
output_format: png
reference_path: docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/source/IMG_6847.jpg
```

## B. Composition Strategy

```yaml
reviewed: true
strategy: direct_showcase
variation_axis: "single structured prompt"
variant_count: 1
```

## C. Prompt Composition

```yaml
reviewed: true
style_treatment: unified
base_prompt: |
  Transform the provided roadside photo into a polished iPad Procreate cartoon illustration.
  Keep the same camera angle, road layout, guardrail placement, roadside hedge, trees,
  sky, yellow maintenance truck, red car, and small white wildflowers as recognizable
  scene anchors. Redraw the whole image as one coherent illustration, not as separate
  pasted layer cutouts.

  Visual style: vibrant pastel iPad illustration, soft rounded outlines, clean flat
  shading, simple readable shapes, cheerful roadside atmosphere, crisp but gentle linework,
  no photorealistic texture.

  Critical constraints:
  - no large white or cream blank blocks
  - no mask-shaped halos
  - no pasted stickers
  - no muddy green/brown color drift on flower regions
  - no global low-contrast wash
  - keep the roadside scene composition legible
negative_prompt: |
  white blocks, cream mask fill, pasted cutouts, layer seams, photorealistic texture,
  muddy colors, low contrast, blank background, distorted vehicles
tradition_tokens: []
color_constraint_tokens:
  - vibrant pastel palette
  - soft rounded outlines
  - clean flat shading
  - preserve roadside color readability
sketch_integration: reference
ref_integration: reference_image
```

## D2. Thresholds + Batch + Rollback

```yaml
reviewed: true
L1_threshold:          {value: 0.70, source: assumed, confidence: low}
L2_threshold:          {value: 0.70, source: assumed, confidence: low}
L3_threshold:          {value: 0.50, source: assumed, confidence: low}
L4_threshold:          {value: 0.60, source: assumed, confidence: low}
L5_threshold:          {value: 0.50, source: assumed, confidence: low}
batch_size:            {value: 1, source: derived, confidence: high}
rollback_trigger:      {value: "primary model fails due provider contract or rate limit; try fallback once if safe", source: user-confirmed, confidence: high}
override_rationale: "Direct showcase path intentionally minimizes calls after image2 rate-limit pressure."
```

## F. Cost Budget

```yaml
reviewed: true
per_gen_sec:                  {value: 120, source: assumed, confidence: low}
total_session_sec:            {value: 240, source: derived, confidence: low}
fail_fast_consecutive:        {value: 1, source: user-confirmed, confidence: high}
provider_used_for_calibration: none
provider_multiplier_applied: null
max_real_calls: 2
```

## Open Questions

none

## Notes

[decision] This design deliberately changes the treatment from the old layered additive strategy to a unified whole-image illustration. That is the point of the experiment: avoid sparse-alpha mask artifacts and test the Scottish-style structured prompt path.

[superpowers] Execution will record commands, outputs, generated image path, provider metadata, and verification evidence before reporting completion.
