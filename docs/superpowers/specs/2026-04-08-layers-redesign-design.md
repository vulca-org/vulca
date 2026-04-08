# Layers Redesign — Dual-Path Layered Generation

**Date:** 2026-04-08
**Target version:** v0.13.0
**Status:** Design approved, pending implementation plan

---

## Problem

The `layers/` module in v0.12.0 produces unsatisfying cutout quality, especially for ink-wash traditions (chinese_xieyi). The root cause is **flow direction, not algorithm choice**: the current pipeline generates a single full image and then tries to segment it post-hoc with SAM/VLM masks. Ink-wash content (flying-white 飞白, soft ink gradients, ambient washes) lives in the very edges that hard binary masks destroy. No amount of matting on top of the wrong starting representation will recover the aesthetic.

The fix is to **move layer extraction from a post-processing problem to a generation-time problem**, while keeping the existing post-hoc path as a fallback for inputs we did not generate.

## Goals

Primary user value, in priority order:

1. **B (asset export) — main line.** A user runs `vulca create "..." -t chinese_xieyi --layered`, drops the resulting "远山" layer onto a deep-blue Figma background, and the ink wash, flying-white, and soft gradients are intact. The output looks like Photoshop hand-work, not an AI cutout.
2. **A (local redraw) — rides on top of B.** Re-generating one layer ("change the far mountains to snowy peaks") preserves the rest of the artwork. Naturally enabled once each layer has its own clean alpha and provider call.
3. **C, D, E (analysis, mid-pipeline, all-of-the-above)** — supported but not optimized.

External-image inputs (B-path) are explicitly **best-effort** ("差一点也行").

## Non-goals (explicitly deferred)

- ViTMatte / true alpha-matting models. `[matting]` extra interface is reserved but not implemented.
- Reference-image consistency anchoring (`--with-reference`). Interface designed for, not shipped.
- Rewriting `split_vlm` / `split_sam3`. They are repositioned, not rewritten.
- Adding new traditions or modifying existing tradition non-layerability fields.
- Layered mode in studio / batch flows. v0.14+.
- Manifest migration tooling. New `schema_version` is read-compatible only.

---

## Architecture

`layers/` becomes **two parallel paths sharing one downstream**, dispatched statically by the tradition's `layerability` field. Users do not see the A/B distinction.

```
                       ┌────────── A-path (main, VULCA-generated images) ──────────┐
                       │                                                            │
intent ─→ plan_layers ─┤   layered_generate (concurrent N provider calls)           │
                       │     │                                                      │
                       │     ├─ inject canvas + style + spatial anchored prompt     │
                       │     └─→ N images on canonical canvas                       │
                       │                │                                           │
                       │                ▼                                           │
                       │           keying (per-tradition strategy dispatch)         │
                       │                │                                           │
                       │                ▼                                           │
                       │        validate (spatial / optional semantic)              │
                       │                │                                           │
                       │                ▼                                           │
                       │       list[(LayerInfo, RGBA)] ──────────────┐             │
                       └─────────────────────────────────────────────┤             │
                                                                      │             │
external_image ──→ plan_from_image (VLM) ──┐                          │             │
                                            │                          │             │
                       ┌── B-path ──────────┤                          │             │
                       │                    ▼                          │             │
                       │     split_vlm / split_sam3 (unchanged)        │             │
                       │              │                                 │             │
                       │              ▼                                 │             │
                       │     soften_mask (guided filter + feather +    │             │
                       │                  despill, OpenCV optional)    │             │
                       │              │                                 │             │
                       │              ▼                                 │             │
                       │   list[(LayerInfo, RGBA)] ─────────────┐      │             │
                       └─────────────────────────────────────────┤      │             │
                                                                  │      │             │
                                                                  ▼      ▼             │
              shared downstream: composite / blend / transform / redraw / regenerate /
              manifest / export / artifact / alpha / analyze / edit / ops / prompt
```

### Dispatch (single source of truth)

```python
# layers/dispatch.py
def select_path(*, has_intent, tradition, user_forced_path=None):
    if user_forced_path:
        return user_forced_path                    # debug escape hatch
    if not has_intent or tradition is None:
        return "b"
    return {
        "native":      "a",
        "split":       "b",
        "discouraged": "b_with_warning",
    }[tradition.layerability]
```

The CLI / MCP / SDK all call one high-level entrypoint `vulca.layers.layered_create(...)` which dispatches internally. **Users never see A vs B as a concept.**

### Module map

| File | New / Old | Role |
|---|---|---|
| `layers/plan_prompt.py` | unchanged | A & B shared upstream |
| `layers/layered_generate.py` | **new** | A-path: concurrent provider calls + prompt anchoring |
| `layers/keying/__init__.py` | **new** | strategy dispatch |
| `layers/keying/luminance.py` | **new** | Tier 0 default |
| `layers/keying/chroma.py` | **new** | Tier 1 |
| `layers/keying/delta_e.py` | **new** | Tier 1 (perceptual) |
| `layers/keying/_lab.py` | **new** | hand-rolled sRGB→LAB (no scikit-image dep) |
| `layers/validate.py` | **new** | coverage / position / emptiness checks |
| `layers/dispatch.py` | **new** | path selection |
| `layers/matting.py` | **new** | `soften_mask` (guided + feather + despill) |
| `layers/split.py` / `split_vlm` / `split_sam3` / `sam.py` / `sam3.py` / `vlm_mask.py` | unchanged | repositioned as B-path core |
| `layers/composite.py` / `blend.py` / `transform.py` / `ops.py` / `manifest.py` / `redraw.py` / `regenerate.py` / `export.py` / `alpha.py` / `artifact.py` / `analyze.py` / `edit.py` / `prompt.py` / `types.py` | unchanged | shared downstream |
| `cultural/data/traditions/*.yaml` | **+5 fields** per tradition | configuration |

**Estimated change volume:** ~600–900 LOC added (incl. tests), ~50–100 LOC modified for downstream wire-up, **0 LOC deleted**.

---

## Keying subsystem

### Contract

Keying does exactly one thing: given an RGB image and a `CanvasSpec`, return a float alpha in [0,1]. It does **not** do semantic segmentation, multi-layer splitting, or post-processing. Semantics are guaranteed upstream by `layered_generate`'s prompt anchoring (each image contains one element on a canonical canvas). Keying just converts "content vs canvas" into alpha.

```python
class KeyingStrategy(Protocol):
    def extract_alpha(
        self,
        rgb: np.ndarray,        # H×W×3 uint8
        canvas: CanvasSpec,
    ) -> np.ndarray:            # H×W float32 in [0,1]
        ...

class CanvasSpec(NamedTuple):
    color: tuple[int, int, int]
    tolerance: float = 0.05
    invert: bool = False
```

### Tier 0 — Luminance (default, zero config)

```python
def extract_alpha(rgb, canvas):
    L = 0.299*R + 0.587*G + 0.114*B
    L_canvas = luminance(canvas.color)            # usually 255
    alpha = 1.0 - (L / L_canvas)
    return clip(alpha, 0, 1)
```

For chinese_xieyi this is the WOW unlock: dense ink → high alpha, pale ink → low alpha, flying-white → semi-transparent, white paper → fully transparent, edge gradients → soft alpha. **Ink darkness physically equals alpha**, so the mathematical inversion is the correct extraction. Four lines of numpy.

### Tier 1 — Chroma key & Delta-E

For colored content on colored canvases (gongbi on cooked-silk yellow, ukiyo-e on gold-leaf): convert RGB → LAB (hand-rolled, no scikit-image), compute distance to canvas color, smoothstep to alpha. Delta-E variant uses perceptual distance for low-contrast cases like gongbi color washes; ~3× slower but acceptable at low layer counts.

### Tier 2 — Custom callable (escape hatch)

```yaml
key_strategy: "vulca.layers.keying.custom:oil_impasto_alpha"
```

Reserved for traditions Tier 0/1 cannot handle (heavy impasto oil, etc). **If more than 3 traditions need Tier 2, that is a health signal that those traditions should be re-classified as `layerability: split` instead.**

### Tradition YAML increment

Each tradition gains five fields:

```yaml
canvas_color: "#ffffff"                   # for keying
canvas_description: "pure white rice paper (生宣纸)"   # for prompt
key_strategy: luminance                   # luminance | chroma | delta_e | <dotted.path:fn>
layerability: native                      # native | split | discouraged
style_keywords: "水墨写意, 淡墨为主, 飞白笔触, 大量留白, 宣纸质感, 不画任何彩色"
```

Defaults when not set: `canvas_color="#ffffff"`, `key_strategy="luminance"`, `layerability="split"` (conservative), `style_keywords=""`. **A new tradition with zero config still works**, just without WOW.

### Initial layerability assignment for the 13 traditions

| Tradition class | layerability | key_strategy | Expected |
|---|---|---|---|
| chinese_xieyi, water-ink, calligraphy, line-art, sketch, pen-illustration | native | luminance | **WOW** |
| chinese_gongbi | native | delta_e | good |
| japanese_traditional / ukiyoe | native | delta_e | good |
| commercial brand design | native | luminance | medium |
| photography | **discouraged** | — | B-path + warn |
| realist / impasto oil painting | **discouraged** | — | B-path + warn |

(Initial `style_keywords` strings to be authored alongside the YAML edits, mixing CN/EN per provider responsiveness.)

---

## Layered generation flow

`layered_generate` orchestrates plan → concurrent provider calls → keying → validation → output. It does not handle prompt building or alpha extraction itself; it composes the other modules.

```python
async def layered_generate(
    plan: LayerPlan,
    tradition: Tradition,
    provider: Provider,
    *,
    parallelism: int = 4,
    cache: LayerCache | None = None,
    on_progress: Callable | None = None,
) -> LayeredResult:
    canvas = CanvasSpec.from_tradition(tradition)
    keying = get_keying_strategy(tradition.key_strategy)
    sem = asyncio.Semaphore(parallelism)

    async def run_one(spec):
        async with sem:
            return await _generate_one_layer(spec, canvas, keying, provider, cache, plan)

    outcomes = await asyncio.gather(*(run_one(l) for l in plan.layers))
    return LayeredResult(
        layers=[o for o in outcomes if o.ok],
        failed=[o for o in outcomes if not o.ok],
        plan=plan,
    )
```

### Per-layer pipeline

```
LayerSpec
   → build_layer_prompt(spec, tradition, plan)        ← anchored prompt (see Consistency)
   → cache_key = sha256(provider, model, prompt, canvas, seed, schema_version)
   → cache hit? return cached RGBA
   → provider.generate(prompt)                         ← retry from existing providers/ layer
   → keying.extract_alpha(rgb, canvas)                 ← Section: Keying
   → validate(alpha, spec)                             ← Section: Consistency
   → LayerOutcome(ok=True, layer_info, rgba, warnings=[...])
```

Any step raising → `LayerOutcome(ok=False, layer_id, reason, attempts)`.

### Concurrency, retries, throttling

- `asyncio.gather` + `Semaphore(4)` default. Single layer failure does not abort siblings.
- Per-layer retry/backoff reuses the existing `providers/` retry layer; not reinvented here.
- Provider RPS limiting is the provider layer's job; `layered_generate` only controls concurrency count.
- Wall-clock time is approximately 1× a single generation; bill is N×.

### Cache

- **Default ON.** `--no-cache` disables.
- Key: `sha256(provider_id || model_id || regeneration_prompt || canvas.color || canvas.tolerance || seed || schema_version)`.
- Storage: `<artifact_dir>/.layered_cache/<key>.png` + sidecar JSON. Lives inside the artifact, deleted with it.
- Strict matching — any prompt change is a miss. We prefer correctness over hit rate.
- No LRU, no global cache, no eviction. YAGNI for v0.13.
- The real cost win is **single-layer re-runs** after iterative editing: a 5-layer artwork edited at one layer is a 1× provider call, not 5×. This amortizes the nominal 5× cost of layered generation toward a long-run ~1.x×.
- Manual clear: `vulca layers cache clear <artifact_id>`.

### Partial-failure contract

```python
@dataclass
class LayeredResult:
    layers: list[LayerOutcome]
    failed: list[LayerFailure]
    plan: LayerPlan

    @property
    def is_complete(self) -> bool: return not self.failed

    @property
    def is_usable(self) -> bool:
        return any(l.role == 'background' for l in self.layers) \
           and any(l.content_type == 'subject' for l in self.layers)
```

CLI exit semantics:

| State | Behavior | Exit code |
|---|---|---|
| `is_complete` | normal output + manifest | 0 |
| `not is_complete and is_usable` | partial output + manifest with `partial=True` + stderr warning | **0** |
| `not is_usable` | write skeleton artifact for retry, error to stderr | 2 |
| `--strict` set | any incompletion → exit 2 | 2 |

**Default is non-blocking.** A creative tool should hand the user a usable thing whenever it can.

### Single-layer retry

```bash
vulca layers retry <artifact_id> --layer "题款印章"
vulca layers retry <artifact_id> --all-failed
```

Retries only failed layers, others are cache hits. This is the practical mechanism for the "edit one part" workflow.

### Pipeline integration

A new node `layered_generate_node` is added as a sibling to the existing `generate_node`. It is **not** a replacement. Pipeline orchestration picks one based on `--layered` flag and tradition:

```python
if cli.layered_flag and tradition.layerability == "native":
    use layered_generate_node
else:
    use generate_node    # current behavior
```

`layered_generate_node` produces an `Artifact` carrying an extra `layers` field. The shared downstream (composite/blend/transform/manifest) consumes it without modification.

---

## Plan / generation consistency — three-layer defense

The most dangerous failure mode of A-path: plan says one thing, provider draws another, five images stack into a collage instead of an artwork. Three defenses, applied cheap to expensive. **Defenses 1 and 2 are default ON. Defense 3 is interface-only for v0.13.**

### Defense 1 — Prompt anchoring (default on, zero cost)

`build_layer_prompt(spec, tradition, plan)` wraps the plan's `regeneration_prompt` in a four-block constraint template:

```
[CANVAS ANCHOR]
The image MUST be drawn on {tradition.canvas_description}.
The background MUST be pure {canvas_color_name} ({canvas_color_hex}),
with absolutely no other elements, textures, or shading on the background.

[CONTENT ANCHOR — exclusivity]
The ONLY element in this image is: {layer.role} — {layer.description}.
Do NOT draw {comma-separated other layer roles from plan} —
draw ONLY the {layer.role}.

[SPATIAL ANCHOR]
The {layer.role} MUST occupy {layer.position}, covering approximately
{layer.coverage} of the canvas area. Do NOT extend beyond this region.

[STYLE ANCHOR — from tradition]
{tradition.style_keywords}     (shared verbatim across all layers)

[USER INTENT]
{layer.regeneration_prompt}
```

Key design:

- **Canvas anchor** guarantees keying can work (background must be the configured color).
- **Content anchor's negative list** is auto-generated from the *other* layer roles in the same plan. Empirically, "draw only X" is insufficient; "do not draw Y, Z, W" is required.
- **Spatial anchor** reuses the plan's existing position/coverage fields.
- **Style anchor** comes from `tradition.style_keywords` and is **identical across all layers in the same artwork**. This is the inter-layer style coherence insurance.

### Defense 2 — Post-generation validation (default on, cheap)

`validate(alpha, layer_spec) -> ValidationReport` with three checks:

| Check | Severity | Action |
|---|---|---|
| **Coverage drift** — `actual_coverage` outside `[expected_lo*0.5, expected_hi*2.0]` | warning | record in manifest |
| **Position drift** — IoU(alpha bbox, expected region) < 0.3 | warning | record in manifest |
| **Emptiness** — `(alpha > 0.05).sum() < canvas_area * 0.001` | **failure** | trigger single-layer retry |

The 2× tolerance on coverage is intentional: plan estimates are loose, only flag severe drift.

Optional check (off by default, `--strict` enables):

| Check | Cost | Action |
|---|---|---|
| **Semantic match** — VLM "is this a {layer.description}?" | +1 provider call/layer | partial/no → warning |

Validation results land in `LayerOutcome.warnings` and the manifest. **They do not block** (except emptiness). The user sees diagnostics in the manifest and decides.

### Defense 3 — Reference-image anchoring (v0.13: interface only)

Not implemented in v0.13. Shape sketched here so the interface can be reserved:

```
Step 0: generate one full reference image           (1 extra call)
Step 1: for each layer, prompt becomes
        "From this reference image, redraw ONLY {layer.role} on
         {canvas_description}, preserving its EXACT shape, position,
         color, and style. Do not redraw anything else."
        + reference_image as image input
Step 2: keying / validate as normal
```

This converts the plan from an authoring instruction into an extraction guide; consistency falls out of the shared visual source. Cost: 1+N vs N provider calls.

**Trigger to ship Defense 3**: if `validation_warnings_total{kind=position_drift|coverage_drift}` runs high in production telemetry, promote it to opt-in then default. Until then, the hooks exist in `layered_generate.py` but the call site is gated to no-op.

### Expected effect

| Scenario | Defense 1 only | Defense 1+2 | Defense 1+2+3 (future) |
|---|---|---|---|
| Xieyi (α-strong) | already WOW | WOW + occasional drift warning | near-perfect |
| Gongbi | good | good + auto-diagnosis | WOW |
| Commercial illustration | medium, occasional inconsistency | medium + visible diagnostics | good |
| Photography | not on A-path | — | — |

---

## B-path fallback

B-path's promise is **low; implementation must be stable**. The "差一点也行" contract permits conservatism.

```
external_image
   → plan_from_image (VLM, existing)
   → split_vlm  OR  split_sam3  (existing v0.12, unchanged)
   → soften_mask (new layers/matting.py)
   → apply alpha to original RGB (no re-generation)
   → list[(LayerInfo, RGBA)]
   → shared downstream
```

**Key distinction from A-path**: B-path **does not call the provider to repaint**. It cuts the original image by mask and softens edges. So B-path has no 5× cost, but also no per-layer high-quality pixels.

### `layers/matting.py` (~150 LOC)

```python
def soften_mask(
    mask: np.ndarray,           # H×W bool/uint8
    rgb: np.ndarray,            # H×W×3 (for edge-aware smoothing)
    *,
    feather_px: int = 2,
    guided: bool = True,
    despill: bool = True,
) -> np.ndarray:                # H×W float32 alpha
```

Implementation choices, by cost-benefit:

1. **Guided filter** (default on) — uses `cv2.ximgproc.guidedFilter` if OpenCV is installed (`[tools]` extra), otherwise falls back to a numpy box-filter feather. **No new mandatory dependency.**
2. **Despill** (default on) — subtract background spill from edge pixels. A few lines of numpy.
3. **`[matting]` extra + ViTMatte** — **interface reserved, not implemented in v0.13.** Shipping it is gated on real user demand for production-quality external-image cutouts.

### Honest accounting of what is and isn't fixed

- The user's original "抠图效果不好" complaint about external images is **not truly fixed** — it is mitigated by softening, managed by the "差一点也行" expectation contract, and bypassed for VULCA-generated images by routing them to A-path. This is a deliberate scope decision, not an oversight.
- If users come back and say "I want A-path quality on my own photos too," the upgrade path is the `[matting]` extra, then ViTMatte or similar in v0.14+.

### `discouraged` UX

When `tradition.layerability == "discouraged"`, the CLI prints (TTY only):

```
⚠ Tradition 'photography' does not support high-quality layering.
  The result is best-effort and intended for analysis only,
  not for production use as standalone assets.
  Continue? [y/N]
```

`--yes` skips. **Non-interactive (pipe / CI) automatically continues** with a stderr warning. `discouraged` traditions still produce output, just labeled.

### Final user-facing promise table

| Class | Path | Promise |
|---|---|---|
| native (xieyi, water-ink, line-art, calligraphy, gongbi, ukiyoe, ...) | A | "ready to use as a standalone asset" |
| split (default fallback / unconfigured) | B | "best-effort layering, suitable for prototypes and analysis" |
| discouraged (photography, realist oil, ...) | B + warn | "not recommended for layering, results for reference only" |

Both CLI output and manifest carry this label so the user knows which tier they got.

---

## CLI / API surface

### CLI

**Main entry — flag on existing `vulca create`:**
```bash
vulca create "..." -t chinese_xieyi --layered
vulca create "..." -t chinese_xieyi --layered --no-cache
vulca create "..." -t chinese_xieyi --layered --strict
vulca create "..." -t chinese_xieyi --layered --max-layers 5
```

When `--layered` is absent, behavior is unchanged. **Zero existing-call breakage.**

**Retry subcommand:**
```bash
vulca layers retry <artifact_id> --layer "题款印章"
vulca layers retry <artifact_id> --all-failed
```

**External image (existing, unchanged):**
```bash
vulca layers split user_photo.jpg
```

**Cache management:**
```bash
vulca layers cache clear <artifact_id>
```

**Total new flags: 4** — `--layered`, `--no-cache`, `--strict`, `--max-layers`.
**Total new subcommands: 2** — `layers retry`, `layers cache`.

**Power-user controls via env vars** (no flags):
- `VULCA_LAYERED_PARALLELISM=2` — override default concurrency
- `VULCA_FORCE_LAYERS_PATH=a|b` — debug escape hatch

### MCP

New tools mirroring CLI:
- `vulca_layered_create` — equivalent to `create --layered`
- `vulca_layers_retry` — equivalent to `layers retry`

Existing `layers_split` / `layers_transform` / etc. unchanged. MCP progress uses structured `layer_progress` events, not stdout.

### High-level Python API

```python
from vulca.layers import layered_create, layered_retry

result: LayeredResult = await layered_create(
    intent="远山薄雾",
    tradition="chinese_xieyi",
    provider=...,
    parallelism=4,
    cache=True,
    strict=False,
    max_layers=8,
)
```

`layered_create` is the single dispatched entrypoint; it calls `select_path` internally and the user does not need to know which path ran.

---

## Manifest schema (v0.13)

`schema_version` bumps from v0.12 → v0.13. New top-level fields:

```yaml
schema_version: "0.13"
generation_path: "a" | "b" | "b_with_warning"
layerability: "native" | "split" | "discouraged"
partial: false
warnings: []
```

New per-layer fields:

```yaml
layer:
  source: "layered_generate" | "split_vlm" | "split_sam3"
  canvas_color: "#ffffff"
  key_strategy: "luminance"
  cache_hit: true | false
  attempts: 1
  validation:
    coverage_actual: 0.23
    coverage_expected: "20-30%"
    position_iou: 0.71
    warnings: ["coverage_drift"]
```

**Backward compatibility**: all new fields have defaults; v0.12 manifests load fine. No active migration tool — read-compat only.

---

## Testing

Three-tier pyramid:

### Unit (many, fast, offline)
- `test_keying_luminance.py` — dense ink / pale ink / flying-white / pure white cases
- `test_keying_chroma.py` — same/near/far chromatic distance
- `test_keying_dispatch.py` — YAML config → strategy selection
- `test_lab_handrolled.py` — sRGB→LAB roundtrip vs reference values
- `test_layered_validate.py` — coverage / position / emptiness triggers
- `test_layered_prompt_anchoring.py` — built prompt contains all four anchor blocks; negative list comes from sibling layers; style block identical across layers in plan
- `test_layered_dispatch.py` — `select_path` full case coverage
- `test_matting_soften.py` — guided / no-guided / despill combinations

### Integration (medium, mock provider)
- `test_layered_e2e_xieyi.py` — full A-path on xieyi via mock; manifest complete; all layers have alpha; `is_complete=True`
- `test_layered_partial_failure.py` — mock fails one layer; `is_usable=True`; `partial=True`; exit 0
- `test_layered_cache_hit.py` — run twice; second run zero provider calls
- `test_layered_retry.py` — engineer failure → retry single layer → success
- `test_b_path_dispatch_warning.py` — photography tradition → warning emitted
- `test_v012_split_*` (existing) — **must continue passing** (regression net)

### Golden (real provider, weekly CI only)
- `test_layered_golden_xieyi.py` — real Gemini, validate alpha histogram statistics against `tests/golden/` baselines (statistical, not pixel-exact)
- `test_layered_golden_gongbi.py` — exercises delta_e path
- Gated behind `--run-real-provider` flag. **Local + weekly CI, not per-PR.**

**Estimated**: ~25 new test files, ~60 test cases.

---

## Observability

Reuse `layers.stats`. New counters:

```
layers.stats.layered_generations_total
layers.stats.layered_layers_generated_total
layers.stats.layered_provider_calls_total           # cache misses only
layers.stats.layered_cache_hits_total
layers.stats.layered_layer_failures_total
layers.stats.layered_validation_warnings_total{kind=...}
layers.stats.keying_calls_total{strategy=...}
layers.stats.dispatch_path_total{path=a|b|b_warn}
```

**Two health metrics that drive future decisions:**

1. `cache_hits_total / provider_calls_total` — if persistently below 0.3, the cache key strategy is wrong (users aren't reaching cache hits in their actual workflow).
2. `validation_warnings_total{kind=coverage_drift|position_drift}` — high frequency means Defense 1's prompt anchoring is insufficient, and Defense 3 (`--with-reference`) should be promoted from interface-only to opt-in.

---

## Documentation

- README "What You Can Do" gets a ~30-line section showing `vulca create --layered` with a before/after image. No new top-level docs.
- This spec file is the architecture reference.

---

## Acceptance criteria for v0.13 release

1. `vulca create "..." -t chinese_xieyi --layered` produces an artifact whose individual layer PNGs, when composited onto a non-white background, preserve flying-white and ink gradients without visible halos. (Verified by unit, integration, and at least one golden test.)
2. All v0.12 tests continue to pass without modification.
3. `vulca layers split user_photo.jpg` (B-path) continues to work; result quality may be unchanged from v0.12 plus a soften pass.
4. `vulca create -t photography --layered` prints the discouraged warning, runs B-path, exit 0, manifest labeled `discouraged`.
5. Single-layer retry correctly re-runs only failed layers; other layers come from cache.
6. Partial-failure default behavior: 4-of-5 success exits 0 with stderr warning and `partial=true` manifest.
7. New CLI flags total exactly 4: `--layered`, `--no-cache`, `--strict`, `--max-layers`. New subcommands: `layers retry`, `layers cache`.
8. Mock provider completes the full A-path locally with zero network calls.
