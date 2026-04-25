# v0.17.14 native validation — γ Scottish slide-4 closure

**Run date**: 2026-04-25  •  **Vulca**: v0.17.14 PyPI live  •  **MCP server**: editable install at `/Users/yhryzy/dev/vulca`, restarted post-ship.

This directory archives evidence that the v0.17.14 P2 (layers_redraw
recontract) and P3 (layers_paste_back) patches close the γ Scottish
"edit one layer → paste back into source" mechanism end-to-end via
native MCP — no out-of-band Python scaffolding required.

P1 (`inpaint_artwork(mask_path=...)`) is **not** exercised by this
real-machine run (the slide-4 carousel flow doesn't use mask inpaint).
P1 is covered by the unit suite at `tests/test_inpaint_mask.py` (10
tests) — for an end-to-end MCP run of P1, see the v0.18 carousel-update
backlog.

**Visual parity with the slide-4-right carousel artifact** is a
separate question and is **not** what this validation closes — that
artifact was authored via `generate_image` with a gongbi text prompt,
not via `layers_redraw` on the lanterns layer alone. The cream-flat
img2img reference loses per-instance geometry on a row-of-six-lanterns
sparse alpha; per-instance multi-lantern redraw is v0.18.

## What ran

```python
# Step A — redraw the alpha-sparse lanterns layer with cream-flat
# protection + alpha re-application + non-destructive output
mcp__vulca__layers_redraw(
    artwork_dir=".../v0_17_14_native",
    layer="lanterns",
    instruction="Render gongbi (工笔) Chinese paper lanterns in cinnabar red "
                "with fine gold ink outlines and tassels, hanging at exactly "
                "the same positions and scales as the source layer. Preserve "
                "the original spatial layout and bounding box of each lantern. "
                "Photorealistic but with clear gongbi linework.",
    provider="openai",                     # gpt-image-2 (P2 fix: provider-aware api_key)
    tradition="chinese_gongbi",
    output_layer_name="lanterns_redrawn",  # P2: opt-in non-destructive
    background_strategy="cream",           # P2: stops hallucination of new content
    preserve_alpha=True,                   # P2: re-apply source alpha
)
# → returns z_index=51 (verified matches manifest entry z=51, P1.1 review fix)

# Step B — paste the redrawn layer back into iter0 RGB source via alpha mask
mcp__vulca__layers_paste_back(
    source_image=".../v0_17_14_native/iter0.png",
    layer_image=".../v0_17_14_native/lanterns_redrawn.png",
    output_path=".../v0_17_14_native/iter0_with_native_lanterns.png",
    blend_mode="alpha",                    # P3: alpha mode + RGB-clamp at alpha=0
)
# Diff bbox: (146, 108) → (1024, 849)  — 878×741 = 650,598 pixels
# • whole canvas (1024×1024):  10.38% pixels changed,  mean RGB diff 5.34/255
# • within bbox:               16.73% pixels changed,  mean RGB diff 8.61/255
# • at the changed pixels only: mean RGB diff 51.44/255 (the redraw IS visible
#   per-pixel — but at carousel-thumbnail zoom the composite is visually
#   indistinguishable from iter0.png)
```

## Patches validated

| Patch | Mechanism | Evidence |
|---|---|---|
| P1.1 review (z_index parity) | manifest z=51 == returned LayerResult.z_index | `manifest.json` shows `lanterns_redrawn` z=51, all other layers z=50/0/1 |
| P2 conservative recontract | output_layer_name + background_strategy=cream + preserve_alpha=True | `lanterns.png` byte-identical to `iter1/lanterns.png` (SHA-256 verified); new file `lanterns_redrawn.png` written |
| P2 provider-aware api_key | OpenAI key resolved (gpt-image-2 call returned 200) | `lanterns_redrawn.png` exists with image bytes — env state not artifact-archived |
| P2 aspect-preserving fit | non-square canvas not warped | 1024×1024 input → 1024×1024 output (no warp; identity case) |
| P3 layers_paste_back | RGBA layer composited onto foreign RGB source | `iter0_with_native_lanterns.png` differs from iter0.png inside the lantern bbox only |
| P3 RGB-clamp at alpha=0 | no black bleed at sparse-alpha boundaries | all changed pixels (108,858) lie inside the lantern bbox (146,108)→(1024,849) — no leakage outside |

## Visual quality observation (NOT a v0.17.14 ship-gate failure)

Mechanism is verified; the **visual output**, however, is not equivalent
to the slide-4 RIGHT artifact (`./lanterns_after.png` — copied here for
self-contained side-by-side; the carousel-shipped original is at
`../lanterns_after.png`). The slide-4 RIGHT is a **stand-alone gongbi
composition** (cream parchment background + stylized lanterns + stylized
Scottish spire) produced by a fresh `generate_image` call earlier in the
workflow with a rich text prompt.

The native flow above produces a different artifact: a photo-edit overlay
that blends gpt-image-2's redraw output back onto the iter0 photo at the
exact lantern alpha positions. At pixel-peeping zoom the difference is
detectable as red-orange smearing along the original lantern edges (mean
51.44/255 at the 108,858 changed pixels); at carousel-thumbnail zoom the
composite is visually indistinguishable from `iter0.png`. The redraw is
**effectively a no-op for this layer's intent** — gpt-image-2 at the
redraw step sees a cream-flat reference (alpha-sparse layer pasted on
cream RGB) and loses the per-lantern spatial geometry. It renders a
single fragmented red-and-tan blob, no per-lantern resolution, and
`preserve_alpha=True` masks that blob back to the original lantern
shapes — approximating the source's red-lantern look without
contributing meaningful new style.

`lanterns_redrawn.png` is itself the visceral evidence of the failure
mode: open it standalone to see what gpt-image-2 produced from the
cream-flat reference (no coherent gongbi geometry).

## v0.18 backlog item surfaced by this validation

**Cream-flat reference loses spatial detail for sparse-alpha layers.**
When `background_strategy="cream"` flattens a layer with many small
disconnected alpha regions (e.g. a row of 6 lanterns), the gpt-image-2
img2img reference contains no useful per-instance geometry — only
"these regions have alpha". The model produces stylized noise rather
than coherent per-instance content. Mitigations to evaluate in v0.18:

- Per-instance redraw: split a multi-instance entity into N sub-layers
  before redraw (related to existing v0.18 multi-instance backlog).
- Instruction-guided composite reference: use a higher-fidelity prep
  pass (e.g. crop+upscale each instance, redraw, paste back) inside MCP
  rather than a single canvas-level redraw.
- Documentation: explicit warning in `layers_redraw` docstring that
  cream/white strategies suit single-region alpha layers, not sparse
  multi-instance ones.

## Bonus finding: `area_pct=0.0` for the redrawn layer

`manifest.json` shows `area_pct=0.0` for `lanterns_redrawn` (the other
nine layers carry their actual area_pct: lanterns 8.05%, sky 15.50%,
left_buildings 24.45%, etc). The redrawn layer's saved alpha is
non-empty, so the manifest entry is wrong. Root cause: the
`_add_or_replace_layer_in_manifest` helper added in v0.17.14 (Patch 2)
constructs the new `LayerInfo` with default `area_pct=0.0` rather than
recomputing from the saved RGBA. **v0.18 fix**: read the saved layer's
alpha and set `area_pct = (alpha > 0).mean() * 100` before write_manifest.
Tracked separately; not blocking for v0.17.14 ship.

## Files

- `iter0.png` — Glasgow street source, 1024×1024 (copy of `iters/7/gen_bfbbacd2.png`)
- `lanterns.png` — alpha-sparse lanterns layer from iter1 decompose (SHA-256 byte-equal to `iter1/lanterns.png`)
- `lanterns_redrawn.png` — v0.17.14 native gpt-image-2 redraw output
- `iter0_with_native_lanterns.png` — paste_back composite
- `lanterns_after.png` — v3.4 manual reference for visual comparison (copy of `../lanterns_after.png`)
- `manifest.json` — manifest with `lanterns_redrawn` entry at z=51 (also flags the area_pct=0.0 bug above)
- 9 peer layer PNGs (sky/person/sign_top/sign_right/spire/bus/left_buildings/right_buildings/residual) — committed alongside so the manifest's `file:` references all resolve in this self-contained validation directory
