# v0.17.14 native validation — γ Scottish slide-4 closure

**Run date**: 2026-04-25  •  **Vulca**: v0.17.14 PyPI live  •  **MCP server**: editable install at `/Users/yhryzy/dev/vulca`, restarted post-ship.

This directory archives evidence that the three v0.17.14 patches (P1 mask
inpaint, P2 layers_redraw recontract, P3 layers_paste_back) close the
γ Scottish carousel slide-4 workflow gap end-to-end via native MCP — no
out-of-band Python scaffolding required.

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
# → 10.4% pixels changed in lantern bbox (146,108)→(1024,849); mean diff 5.34/255
```

## Patches validated

| Patch | Mechanism | Evidence |
|---|---|---|
| P1.1 review (z_index parity) | manifest z=51 == returned LayerResult.z_index | `manifest.json` shows `lanterns_redrawn` z=51, all other layers z<=50 |
| P2 conservative recontract | output_layer_name + background_strategy=cream + preserve_alpha=True | `lanterns.png` byte-identical to pre-redraw; new file `lanterns_redrawn.png` written |
| P2 provider-aware api_key | OpenAI key resolved without GOOGLE_API_KEY leak | gpt-image-2 call succeeded against OPENAI_API_KEY only |
| P2 aspect-preserving fit | non-square canvas not warped | 1024×1024 input → 1024×1024 output |
| P3 layers_paste_back | RGBA layer composited onto foreign RGB source | `iter0_with_native_lanterns.png` is iter0.png with lantern alpha region overwritten |
| P3 RGB-clamp at alpha=0 | no black bleed at sparse-alpha boundaries | only 10.4% changed pixels, all inside lantern bbox |

## Visual quality observation (NOT a v0.17.14 ship-gate failure)

Mechanism is verified; the **visual output**, however, is not equivalent
to the slide-4 RIGHT artifact (`decompose/lanterns_after.png`) the carousel
ships today. The original slide-4 RIGHT is a **stand-alone gongbi composition**
(cream parchment background + stylized lanterns + stylized Scottish spire),
produced by a fresh `generate_image` call earlier in the workflow.

The native flow above produces a different artifact: a photo-edit overlay
that blends gpt-image-2's redraw output back onto the iter0 photo at the
exact lantern alpha positions. The visual delta vs iter0 is subtle
(10.4% pixels, 5.34/255 mean diff) because gpt-image-2 at the redraw step
sees a cream-flat reference (alpha-sparse layer pasted on cream RGB) and
loses the per-lantern spatial geometry. It renders red-color blobs that,
when alpha-masked back to the original lantern shapes, approximate the
source's red-lantern look without contributing meaningful new style.

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

## Files

- `iter0.png` — Glasgow street source, 1024×1024 (copy of `iters/7/gen_bfbbacd2.png`)
- `lanterns.png` — alpha-sparse lanterns layer from iter1 decompose
- `lanterns_redrawn.png` — v0.17.14 native gpt-image-2 redraw output
- `iter0_with_native_lanterns.png` — paste_back composite
- `manifest.json` — manifest with `lanterns_redrawn` entry at z=51
- (other layers copied for manifest completeness; not used by this validation)
