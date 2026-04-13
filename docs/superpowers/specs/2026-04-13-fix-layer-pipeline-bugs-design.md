# Fix Layer Pipeline Bugs — Composite, img2img, Decompose

**Date:** 2026-04-13
**Status:** Approved
**Type:** Bug fix (3 bugs)

## Background

Three bugs in the layer pipeline prevent the showcase from demonstrating the full user journey (evaluate → decompose → edit → composite → re-evaluate):

1. Composite produces solid black images
2. ComfyUI redraw is txt2img only (no img2img)
3. Decompose extract mode produces poor quality masks

## Bug 1: Black Composite (P0)

**Root cause:** `blend.py:175` initializes canvas as `(0,0,0,0)` (transparent black). When the first layer uses multiply blend: `(0,0,0) * anything = (0,0,0)` → black forever.

**Fix:** Change canvas to `(255, 255, 255, 0)` (transparent white). Multiply on white is identity. Screen on white = white (acceptable — screen layers are overlays, not base).

**File:** `src/vulca/layers/blend.py:175`
**Lines changed:** 1

## Bug 2: ComfyUI No img2img (P1)

**Root cause:** `comfyui.py:42-62` builds a txt2img-only workflow. `reference_image_b64` is accepted by the method signature but never wired into the workflow. KSampler always uses `denoise=1.0` and `EmptyLatentImage`.

**Fix:** When `reference_image_b64` is provided:
1. Save reference image to ComfyUI's input directory via API
2. Add `LoadImage` node pointing to the saved file
3. Add `VAEEncode` node to convert pixels → latent
4. Wire KSampler's `latent_image` to VAEEncode output (not EmptyLatentImage)
5. Set `denoise=0.75` (retain 25% of reference structure)

When `reference_image_b64` is empty: existing txt2img behavior unchanged.

**File:** `src/vulca/providers/comfyui.py`
**Lines changed:** ~25

**ComfyUI image upload:** ComfyUI requires images to be uploaded to its `/upload/image` endpoint before they can be referenced by `LoadImage`. The workflow references images by filename, not base64.

## Bug 3: Decompose Extract Quality (P2)

**Root cause:** `mask.py:50-59` uses Euclidean color-distance with tolerance=30. This fails on gradients, similar-hue regions, and complex paintings.

**Fix:** Two-part approach:
1. **Improve extract mode:** Increase tolerance for `subject`/`effect` content types (30→50). Add saturation-based fallback when color matching fails.
2. **Default to `regenerate` mode in showcase scripts:** For complex artworks, `split_regenerate()` produces much better results by re-generating each layer via the image provider.

**Files:** `src/vulca/layers/mask.py`, `src/vulca/layers/split.py`
**Lines changed:** ~10

## Non-Goals

- Not redesigning the blend engine (just fixing the canvas init)
- Not adding ControlNet or IP-Adapter support (just basic img2img)
- Not implementing SAM3 integration (future work)

## Success Criteria

1. `composite_layers()` on v3/layered artifacts produces a visible composite (not black)
2. `redraw_layer()` with `--provider comfyui` produces an image influenced by the reference
3. `vulca layers split --mode extract` on Starry Night produces distinguishable layers
4. All existing mock tests still pass

## Files Changed

- `src/vulca/layers/blend.py` — canvas init (1 line)
- `src/vulca/providers/comfyui.py` — img2img workflow (~25 lines)
- `src/vulca/layers/mask.py` — tolerance + saturation fallback (~10 lines)
