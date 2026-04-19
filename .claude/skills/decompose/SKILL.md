---
name: decompose
description: Decompose an image into editable semantic layers using Vulca SDK. Invoke when the user asks to "decompose", "split into layers", "拆图", or mentions layer extraction from a specific image path.
---

You are decomposing an image into semantic layers via the Vulca SDK. The pipeline stitches YOLO + Grounding DINO + SAM + SegFormer; you (the agent) author a JSON plan and call the MCP tool. No LLM runs inside the SDK.

## Step 1: Read the image

Use the Read tool on the user's image path. Identify:
- Major subjects (persons, objects, background elements)
- Lighting / domain (portrait, news, painting, concert, etc.)
- Visible occlusions or crowded regions

## Step 2: Author a minimal plan

Start simple. Minimum viable shape:

```json
{
  "domain": "portrait_photograph",
  "entities": [
    {"name": "subject", "label": "short description", "detector": "auto"},
    {"name": "background", "label": "short description",
     "semantic_path": "background", "detector": "dino", "threshold": 0.2}
  ]
}
```

Pick `domain` from: `portrait_photograph`, `concert_photograph`, `news_photograph_2024`, `renaissance_painting`, `post_impressionist_painting`, `american_regionalist_painting`, `booking_photograph`, or `photograph` as fallback. `domain` picks `DOMAIN_PROFILES` (thresholds, person chain, tiling) — get it right.

Start with 2-4 entities. Add more only if residual > 20% AND the previous iteration did not increase residual.

## Step 3: Call the MCP tool

```
layers_split(
  image_path="/abs/path/to/img.jpg",
  output_dir="/abs/path/to/output",
  mode="orchestrated",
  plan='<inline JSON string>'
)
```

Use `plan` (inline) unless you already have a file; then use `plan_path`. Passing both returns an error.

## Step 4: Inspect the result

The return dict has: `status`, `manifest_path`, `output_dir`, `reason`, `detection_report`, `stage_timings`, `layers`.

**status enum:** `ok` | `partial` | `error` | `skipped` | `unknown`

Walk this decision tree in order; take the FIRST match.

### Per-entity signals (highest priority)

| Branch | Condition | Fix |
|---|---|---|
| A | any `detection_report[entity].status == "missed"` | rewrite label or switch detector (`auto` → `dino` → `sam_bbox`) |
| B | any `status == "suspect"` (from `empty_mask`, `low_bbox_fill`, `mask_outside_bbox` — sam_bbox only) | adjust `bbox_hint_pct` or tighten label |
| C | any layer `quality_flag == "area_ballooned"` (pre 0.01%-0.5% AND post > pre×3) | tighten bbox or raise threshold |
| D | any layer `quality_flag == "over_eroded"` (pre > 0.1% AND post/pre < 0.5) | promote `order: 10` or move `semantic_path` to `foreground.*` |
| E | any person `quality_flag == "face_parse_skipped"` AND that person's `pct > 3%` | **head+body split** (exactly TWO entities per occluded person — one head bbox + one body bbox, composite with PIL `alpha_composite` after). Different from the E3 ban below. Alternative: crop face region + 2× upscale + ~20% brightness + re-decompose. |

### Delta-residual guard

| Branch | Condition | Fix |
|---|---|---|
| F | residual layer exists AND `pct > prev_residual.pct + 1pp` | **revert** to the prior entity set; do not continue decomposing that region |

### Residual-driven additions

| Branch | Condition | Action |
|---|---|---|
| G | residual layer `pct > 20%` | Look at the emitted `residual.png` under `layers[]`. Add the missing entity. |
| H | residual `pct` in 5-20% | Judgment call: add if payoff clear. |
| I | residual layer absent OR `pct < 5%` | **STOP adding.** (Over-decomposition guard — splitting further will reduce coverage.) |

### Honesty signal

| Branch | Condition | Action |
|---|---|---|
| J | `detection_report["warning"]` present (requested > 2 AND hint ratio > 0.5) | Surface to user: plan is hint-heavy and fragile. |

## Face-parse rescue ladder

The pipeline does not return a `face_parts_count` field. To count, filter `layers[]` where `semantic_path` starts with `subject.person[N].` followed by one of: `{eyes, nose, lips, eyebrows, ears, hair, neck, skin, cloth, hat}`. If any person's count < 6 AND you judge (via Read tool on the original) the face is small/dark, try in order — accept only when the count increases:

1. Crop face region → new slug → re-decompose
2. Add 2× upscale
3. Add ~20% brightness/contrast

`face_parse_skipped` flag is distinct from sparse face parts — it fires only when SegFormer returns zero parts.

## Error handling

| Error | Response |
|---|---|
| `{"error": "pass either plan (inline JSON) or plan_path, not both"}` | Fix call, pass only one. |
| `{"error": "orchestrated mode requires 'plan' (inline JSON) or 'plan_path'"}` | Author plan, retry. |
| `{"error": "plan validation failed: ..."}` | Read details, fix specific field. |
| `{"error": "pipeline error: MemoryError: ..."}` | (1) Call `unload_models()`. (2) Reduce image to ≤2 MP (resize or crop). (3) Reduce to 2-3 entities. Then retry ONCE. |
| `{"error": "pipeline error: ConnectionError: ..."}` | HuggingFace weights failed to download. Report to user. **Do not auto-retry.** |
| `{"error": "pipeline error: RuntimeError: ...MPS..."}` | 1 soft retry after `unload_models()`; if it recurs, suggest session restart. |
| `{"error": "pipeline error: PermissionError: ..."}` | Change `output_dir`. |
| `{"error": "pipeline error: FileNotFoundError: ..."}` | Verify `image_path`. |
| `{"error": "pipeline error: ...decode..."}` | Convert WebP/HEIC to PNG/JPG. |
| `{"error": "pipeline error: <other>: ..."}` | Report full error. **Do not auto-retry.** |
| `status == "error"` | Read `reason`. If `image_load: ...` → fix image. If `pipeline produced no manifest` → stop, no retry. |
| `status == "skipped"` | Cached manifest returned; ensure `force=True` when retrying. |
| `status == "unknown"` | Manifest missing status; treat as error. |
| all entities `status == "missed"` | Retry ONCE with swapped `domain` first, then with rewritten labels. |

## Hard iteration cap

- **Maximum 5 `layers_split` calls per source image.**
- Also stop early if the previous iteration improved residual by < 2 percentage points (diminishing returns).
- Cap is **per-image**, not per-session.

## Skill bans (rules the pipeline cannot enforce; you must)

- **E1 — No per-person face-part entities.** Never author `face_person_a`, `face_person_b`, etc. The Phase 1.11 sibling-mask only isolates face parts within a `face_person_N` subtree — it cannot deduplicate across entities you author manually. Declare `subject.person[N]`; face parts are auto-generated when `expand_face_parts` is true.
- **E2 — No foreground objects under `background.*`.** The person-overlap leak-fix skips any entry whose `semantic_path` starts with `background`. If an object overlaps a person, put it under `foreground.*` or `subject.*`, not `background.*`.
- **E3 — No manual head/torso/limbs split (3+ entities per person).** `body_remainder` auto-generates only when `subparts_kept` is populated by face-parsing. Manually splitting into head + torso + legs will produce holes. **Exception:** the Branch E head+body split (exactly TWO entities per person) is allowed — it applies when face-parsing itself failed and no `body_remainder` exists to preserve.
- **E4 — Surface hint-heavy warning.** If `detection_report["warning"]` fires (requested > 2 AND bbox_hint ratio > 0.5), tell the user their plan is over-hinted and fragile. Do not silently iterate.
- **E5 — Never dispatch two `layers_split` calls in parallel.** The pipeline mutates module-global state (`cop.ORIG_DIR`, `OUT_DIR`, `PLANS_DIR`); concurrent calls corrupt each other.

## Memory management

If the session has been running for hours and new decompose calls slow down or OOM, call `unload_models()` to free ~3GB. Next decompose will cold-start (~3-4s).

## Out of scope

- Do not modify the Vulca SDK code. Iterate by changing the plan.
- If the user wants a capability the SDK cannot produce, say so plainly.
- The skill's decision tree covers ~90% of cases; when a 6th iteration is tempting, stop and show the user what you have.

## Reference

Full thesis + rescue-pattern writeup: [`docs/agent-native-workflow.md`](/Users/yhryzy/dev/vulca/docs/agent-native-workflow.md).
