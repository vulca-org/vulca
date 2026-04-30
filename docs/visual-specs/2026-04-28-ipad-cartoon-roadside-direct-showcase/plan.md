---
slug: 2026-04-28-ipad-cartoon-roadside-direct-showcase
status: running
domain: brand_visual
tradition: null
schema_version: "0.1"
generated_by: visual-plan@0.1.0
design_ref: docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/design.md
created: 2026-04-28
updated: 2026-04-28
---

# IMG_6847 Direct iPad-Cartoon Showcase - Execution Plan

## A. Execution Parameters

```yaml
reviewed: true
provider: openai
primary_model: gpt-image-2
fallback_model: gpt-image-1.5
quality: high
size: 1536x1024
output_format: png
reference_path: docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/source/IMG_6847.jpg
output_dir: docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/iters/1
```

## B. Iteration Plan

```yaml
reviewed: true
strategy: direct_showcase
seed_list: [null]
variant_count: 1
batch_size: 1
fallback_allowed: true
```

## C. Prompt Composition

```yaml
reviewed: true
composed_prompts:
  - |
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
negative_prompt: "white blocks, cream mask fill, pasted cutouts, layer seams, photorealistic texture, muddy colors, low contrast, blank background, distorted vehicles"
```

## D. Gating Decisions

```yaml
reviewed: true
thresholds:
  L1: {value: 0.70, source: assumed, gate_class: soft}
  L2: {value: 0.70, source: assumed, gate_class: soft}
  L3: {value: 0.50, source: assumed, gate_class: soft}
  L4: {value: 0.60, source: assumed, gate_class: soft}
  L5: {value: 0.50, source: assumed, gate_class: soft}
user_elevated: []
soft_gate_warn_count: 0
```

## E. Fail-Fast Budget + Rollback

```yaml
reviewed: true
fail_fast_consecutive: 1
rollback_trigger: "primary provider/model fails; fallback to gpt-image-1.5 once if the error is model-contract related, not policy related"
rollback_action: "fallback_once_then_partial"
```

## F. Cost Ledger

```yaml
reviewed: true
initial_budget:
  max_real_calls: 2
  per_gen_sec: {value: 120, source: assumed, confidence: low}
  total_session_sec: {value: 240, source: derived, confidence: low}
actual:
  total_calls: 0
  total_cost_usd: 0
  total_wall_time_sec: 0
  provider: null
  model: null
overage_pct: null
```

## Results

provider-blocked; see `plan.md.results.jsonl` and `iters/1/errors.json`.

## A/B Comparison Contract

| arm | prompt file | provider/model | reference | mask | output |
|---|---|---|---|---|---|
| A naive | `prompts/naive_prompt.txt` | `openai/gpt-image-2` | `source/reference_1536x1024.png` | `source/full_edit_mask_1536x1024.png` | `iters/ab/naive_gpt_image_2.png` |
| B Vulca structured | `prompts/vulca_structured_prompt.txt` | `openai/gpt-image-2` | `source/reference_1536x1024.png` | `source/full_edit_mask_1536x1024.png` | `iters/ab/vulca_structured_gpt_image_2.png` |

Fairness rules:
- same source-derived reference image
- same full-edit mask
- same model, endpoint, size, output format, quality where supported
- no decompose, no layers_redraw, no manual retouching
- if provider billing blocks either arm, mark the whole experiment blocked

## Notes

[superpowers] User requested Superpowers-backed execution and recorded output. The current run follows executing-plans discipline in a lightweight form: review existing plan evidence, execute the bounded direct path, then verify generated files before reporting.

[scope] This is not a decompose/redraw run. It is the Scottish-style prompt-planning path for showcase-quality output.

[ab-comparison] Added 2026-04-28 per user request: compare plain prompt vs Vulca structured prompt under the same source/reference/mask/provider/model constraints.

[provider-blocked] OpenAI `/v1/images/edits` returned `Billing hard limit has been reached.` for both `gpt-image-2` and `gpt-image-1.5` attempts. This is not rate limiting and not a prompt/mask/model-contract failure.
