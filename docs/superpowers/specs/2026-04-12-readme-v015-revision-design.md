# README v0.15.0 Major Revision + Visual Asset Pipeline

**Date:** 2026-04-12
**Status:** Approved (revised after codex + superpowers visual asset audit)
**Type:** Bug fix + Asset production + Documentation

## Background

The README (758 lines) was last substantially updated around v0.12. The E2E phases 2-7 wiring (v0.15.0) validated all 8 phases on the local stack — but a post-hoc visual audit of v3 artifacts revealed **3 bugs** that produce broken display assets:

1. **"Anchor" hallucination** — SDXL interprets `[CANVAS ANCHOR]` / `[STYLE ANCHOR]` section headers in `build_anchored_layer_prompt()` as content instructions, painting literal ship anchors on layers.
2. **Background layer keying** — `generate_one_layer()` runs luminance keying on `content_type="background"` layers, making white rice paper transparent. The composite then has holes.
3. **Provider noise** — ComfyUI intermittently returns corrupted pixel data (defense3 8/8 layers are noise, studio all outputs are noise). Likely caused by reading incomplete responses after timeouts.

These must be fixed before producing README-quality visual assets.

## Goals

1. **Fix 3 generation bugs** that produce broken v3 assets.
2. **Regenerate Phases 2, 4, 5, 7** to produce clean display-quality artifacts.
3. **Build `scripts/make-readme-assets.py`** to produce 7 composite display images from v3 artifacts.
4. **Rewrite README** with 12-section local-first structure, mixing v2 polished demos + v3 real local-stack outputs.
5. **Keep README under 800 lines.**

## Non-Goals

- Not creating new GIFs or animated demos (keep v2 GIFs).
- Not rewriting CLI help text, SDK docstrings, or MCP plugin README.
- Not fixing Gemini billing (still blocked).
- Not adding CI for README verification.

---

## Part 1: Bug Fixes (3 fixes, prerequisite for everything else)

### Fix A: Remove "ANCHOR" from prompt section headers

**File:** `src/vulca/layers/layered_prompt.py`

**Problem:** The per-layer prompt sent to SDXL/CLIP contains section headers like `[CANVAS ANCHOR]`, `[CONTENT ANCHOR — exclusivity]`, `[SPATIAL ANCHOR]`, `[STYLE ANCHOR]`. SDXL's CLIP encoder interprets "ANCHOR" as a content token and generates literal ship anchors. Confirmed in v3/layered — `base_rice_paper_texture.png` and `calligraphy_and_seal.png` both contain painted anchors.

**Fix:** Rename the section headers:
- `[CANVAS ANCHOR]` → `[CANVAS]`
- `[CONTENT ANCHOR — exclusivity]` → `[CONTENT — exclusivity]`
- `[SPATIAL ANCHOR]` → `[SPATIAL]`
- `[STYLE ANCHOR]` → `[STYLE]`

The docstring and function name `build_anchored_layer_prompt` stay (they describe the strategy, not the prompt content). Only the literal text injected into the prompt changes.

**Lines affected:** ~74-89 in the current file (the `blocks = [...]` list).

### Fix B: Skip keying for background layers

**File:** `src/vulca/layers/layered_generate.py`

**Problem:** `generate_one_layer()` runs `keying.extract_alpha(rgb, canvas)` on ALL layers, including `content_type="background"`. For a white rice paper background on a white canvas, luminance keying makes the entire layer transparent (alpha ≈ 0). The composite then shows through to nothing.

**Fix:** Around line 300 (after raw image is received, before keying), add:
```python
if layer.content_type == "background":
    alpha = np.ones(rgb.shape[:2], dtype=np.float32)
else:
    alpha = keying.extract_alpha(rgb, canvas)
```

This ensures background layers are always fully opaque, matching the intent of `ensure_alpha()` in `composite.py` (which has a background check at line 86 but can't fix already-keyed images).

### Fix C: Validate provider response before saving

**File:** `src/vulca/providers/comfyui.py`

**Problem:** When ComfyUI generation times out or returns an error, the provider may read incomplete/corrupted image data from the `/view` endpoint. This data gets base64-encoded and returned as `ImageResult.image_b64`, which downstream code saves as a PNG. The result is noise images.

**Fix:** After receiving image bytes from ComfyUI's `/view` endpoint (around line 82), validate before returning:
```python
img_resp = await client.get(...)
raw_bytes = img_resp.content
# Validate PNG signature and minimum size
if len(raw_bytes) < 1000 or raw_bytes[:4] != b'\x89PNG':
    raise ValueError(f"ComfyUI returned invalid image data ({len(raw_bytes)} bytes)")
img_b64 = base64.b64encode(raw_bytes).decode()
```

This won't prevent timeouts, but it ensures corrupted data raises an error instead of silently producing noise images that pass through the pipeline.

---

## Part 2: Regenerate E2E Phases

After fixing the 3 bugs, regenerate the affected phases:

```bash
# Clear old artifacts
rm -rf assets/demo/v3/layered assets/demo/v3/defense3 assets/demo/v3/edit assets/demo/v3/studio

# Phase 2: Layered (fix A + B produce clean layers + composite)
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 2 --provider comfyui

# Phase 5: Edit (depends on Phase 2 artifacts)
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 5 --provider comfyui

# Phase 4: Defense 3 (fix C prevents noise layers)
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 4 --provider comfyui

# Phase 7: Studio (fix C prevents noise outputs)
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 7 --provider comfyui
```

**Expected outputs after regeneration:**
- `layered/`: 5 RGBA layers (no anchors) + clean composite + manifest.json
- `defense3/no_ref/`: 4 clean layers + composite (all parallel, no style-ref)
- `defense3/with_ref/`: 4 clean layers + composite (serial-first + style-ref)
- `edit/`: before.png (clean composite), after.png (redrawn layer composited), redrawn_layer.png
- `studio/concepts/`: 4 concept PNGs, `studio/output/`: 3 round PNGs, `studio/final.png`

**Verification:** Visually inspect each output. If any are still noise, investigate ComfyUI's response for that specific run (check `/tmp/comfyui.log`).

---

## Part 3: Visual Asset Production Script

### Script: `scripts/make-readme-assets.py`

Produces 7 display-quality composite images from v3 artifacts. All output to `assets/demo/v3/readme/`.

#### Asset 1: Hero Gallery Strip

**Shows:** "13 traditions, all generated locally" — breadth of capability at a glance.

**Source files:**
- `assets/demo/v3/gallery/chinese_xieyi.png`
- `assets/demo/v3/gallery/japanese_traditional.png`
- `assets/demo/v3/gallery/watercolor.png`
- `assets/demo/v3/gallery/islamic_geometric.png`
- `assets/demo/v3/gallery/african_traditional.png`

**Production logic:**
1. Load 5 images, resize each to 200x200 with LANCZOS
2. Create white canvas 1040x200
3. Paste side by side with 8px gaps
4. No labels (caption in README handles this)

**Output:** `assets/demo/v3/readme/gallery_strip.png` (1040x200)
**README location:** Section 3 (What You Can Do) or Section 11 (13 Traditions)

#### Asset 2: Layered Exploded View

**Shows:** "How structured layered generation works" — the core v0.14+ feature.

**Logical flow:** Paper → Mist → Mountains → Cottage → Calligraphy → Composite

**Source files:** `assets/demo/v3/layered/*.png` (5 layers + composite, post-regeneration)

**Production logic:**
1. Load 5 layer PNGs + composite, resize each to 160x160
2. Create dark gray canvas (#2d2d2d) 1200x250
3. For each layer: paste on checkerboard background (shows transparency), add layer name label below in white text
4. Between each pair: draw right arrow (→) in white
5. After last layer: draw equals sign (=) + paste composite

**Output:** `assets/demo/v3/readme/layered_exploded.png` (1200x250)
**README location:** Section 4 (Create — Layered creation subsection)

#### Asset 3: Defense 3 Style-Ref Comparison

**Shows:** "Style-ref anchoring produces visually consistent layers" — the Defense 3 feature.

**Logical flow:** Left panel (no style-ref, inconsistent) vs Right panel (with style-ref, consistent)

**Source files:**
- `assets/demo/v3/defense3/no_ref/composite.png`
- `assets/demo/v3/defense3/with_ref/composite.png`

**Production logic:**
1. Load both composites, resize to 400x400
2. Create white canvas 880x480
3. Paste no_ref left, with_ref right, 40px gap
4. Add labels: "Without style-ref" / "With style-ref (v0.14)" above each
5. Optional: add red border around no_ref, green around with_ref

**Output:** `assets/demo/v3/readme/defense3_comparison.png` (880x480)
**README location:** Section 4 (Create — Style-ref anchoring subsection)

#### Asset 4: Edit Before/After

**Shows:** "Non-destructive single-layer redraw" — edit capability.

**Source files:**
- `assets/demo/v3/edit/before.png` (composite before redraw)
- `assets/demo/v3/edit/after.png` (composite after redraw)

**Production logic:**
1. Load both, resize to 400x400
2. Create white canvas 880x480
3. Paste before left, after right, arrow between
4. Labels: "Before" / "After (layer redrawn with autumn colors)"

**Output:** `assets/demo/v3/readme/edit_comparison.png` (880x480)
**README location:** Section 6 (Edit + Inpaint — Layer-based editing)

#### Asset 5: Inpaint Before/After

**Shows:** "Region-based inpainting, locally" — inpaint capability.

**Source files:**
- `assets/demo/v3/inpaint/before.png`
- `assets/demo/v3/inpaint/after.png`

**Production logic:** Same as Asset 4 layout.
Labels: "Original" / "After (pavilion inpainted, center 30%)"

**Output:** `assets/demo/v3/readme/inpaint_comparison.png` (880x480)
**README location:** Section 6 (Edit + Inpaint — Region-based inpainting)

#### Asset 6: Studio Concept Grid

**Shows:** "Brief-driven multi-round creative session" — studio workflow.

**Source files:**
- `assets/demo/v3/studio/concepts/c1.png` through `c4.png`
- `assets/demo/v3/studio/output/r3.png` (final round output, or `final.png`)

**Production logic:**
1. Load 4 concepts, resize to 200x200 each
2. Load final output, resize to 200x200
3. Create white canvas 1100x250
4. Paste c1-c4 in a row, then arrow (→), then final
5. Labels: "Concept 1-4" / "Final"

**Output:** `assets/demo/v3/readme/studio_grid.png` (1100x250)
**README location:** Section 8 (Studio)

#### Asset 7: 13 Traditions Full Grid

**Shows:** Complete tradition coverage — all 13 in one image.

**Source files:** All 13 `assets/demo/v3/gallery/*.png`

**Production logic:**
1. Load all 13, resize to 180x180
2. Create white canvas 980x600 (5 cols × 3 rows, last row has 3)
3. Paste in grid, add tradition name label below each
4. Font: small, gray (#666)

**Output:** `assets/demo/v3/readme/tradition_grid.png` (980x600)
**README location:** Section 11 (13 Traditions) inside `<details>` block

### Script CLI

```bash
python scripts/make-readme-assets.py                    # build all 7
python scripts/make-readme-assets.py --only gallery,inpaint  # build subset
python scripts/make-readme-assets.py --check            # verify inputs exist
```

---

## Part 4: README Structure (12 sections)

### Section-by-Section Image Map

| # | Section | Images | Source | Feature Demonstrated |
|---|---------|--------|--------|---------------------|
| 1 | Hero | 3 gallery images inline | v3/gallery (xieyi, japanese, brand) | "Three traditions, generated locally" |
| 2 | Install + Quick Start | None | — | Code blocks only |
| 3 | What You Can Do | gallery_strip.png (optional) | Asset 1 | Breadth of 13 traditions |
| 4 | Create | layered_exploded.png + defense3_comparison.png | Assets 2+3 | Layered generation + style-ref anchoring |
| 5 | Evaluate | None | — | CLI output blocks (keep v2 style) |
| 6 | Edit + Inpaint | edit_comparison.png + inpaint_comparison.png | Assets 4+5 | Non-destructive edit + region inpaint |
| 7 | Decompose | Qi Baishi + Mona Lisa decomposition | v2 masters (keep) | Layer extraction from existing art |
| 8 | Studio | studio_grid.png OR v2 studio images | Asset 6 or v2 fallback | Brief-driven workflow |
| 9 | Tools | tools-viz.png | v2 (keep) | Algorithmic analysis |
| 10 | Architecture | ASCII diagram (text) + provider matrix (table) | Updated text | System overview |
| 11 | 13 Traditions | 5 inline + tradition_grid.png in details | v3/gallery + Asset 7 | Full tradition coverage |
| 12 | Entry Points + Research | None | — | Integration + academic |

### Visual Storytelling Flow

Each image answers a progressive question:

```
"What does it produce?"      → Hero (3 traditions, locally generated)
"How many styles?"           → Gallery strip (5 more traditions)
"How does it work inside?"   → Layered exploded view (5 layers → composite)
"Does style-ref matter?"     → Defense 3 comparison (with vs without)
"Can I edit surgically?"     → Edit before/after (one layer redrawn)
"Can I fix regions?"         → Inpaint before/after (pavilion added)
"Can it analyze existing?"   → Qi Baishi decomposition (v2, free/local)
"What about full sessions?"  → Studio concept grid (4 concepts → final)
"All 13 traditions?"         → Full grid (comprehensive coverage)
```

### Key Narrative Changes

**Install section:**
- Local path first: `--provider comfyui` (free, no API key)
- Cloud path second: `export GOOGLE_API_KEY` (Gemini)
- Mock fallback: `--provider mock` (no GPU needed)
- Honest timing: "~2 min on Apple Silicon MPS" for local, "~10s" for Gemini

**Create section:**
- CJK-aware callout: "VULCA automatically strips CJK from prompts for CLIP-based providers while preserving CJK natively for multilingual providers"
- Style-ref anchoring: first layer serial → style reference → rest parallel
- Provider choice shown in every example

**Architecture section:**
- Provider capability matrix (generate/inpaint/layered/multilingual)
- Local VLM path (Ollama + Gemma 4) alongside cloud
- Self-Evolution collapsed in `<details>`
- E2E validation: "8/8 phases validated on local stack"

### v2 Assets Retained

| Asset | Section | Why Keep |
|-------|---------|---------|
| v2 GIFs (create, layers, tools, studio) | Various `<details>` | Polished workflow demos, no v3 equivalent |
| v2 Qi Baishi + Mona Lisa decomposition | Decompose | Iconic master paintings, extraction is free/local |
| v2 scenario1-comparison.png | Edit (fallback) | Clean sky-redraw comparison if v3 edit is weak |
| v2 scenario2-poster.png | Edit `<details>` | Design transfer workflow |
| v2 tools-viz.png | Tools | Brushstroke/composition visualization |

All v2 references get `<!-- v2-asset -->` HTML comments for future tracking.

### Badges

- PyPI version: keep (dynamic via shields.io)
- Python version: keep
- License: keep
- Tests: remove hardcoded "1252" — either link to CI or remove
- MCP tools: verify count, update if changed

---

## Success Criteria

### Bug fixes
1. No "ANCHOR" text in generated prompt (grep `build_anchored_layer_prompt` output)
2. Background layers have alpha ≈ 1.0 (not keyed transparent)
3. ComfyUI provider rejects <1KB responses

### Regeneration
4. `assets/demo/v3/layered/composite.png` — clean Chinese ink wash landscape, no anchors
5. `assets/demo/v3/defense3/*/composite.png` — non-noise composites showing style difference
6. `assets/demo/v3/edit/after.png` — visible color change from before
7. `assets/demo/v3/studio/final.png` — non-noise final artwork

### Asset production
8. All 7 assets in `assets/demo/v3/readme/` exist and are display-quality
9. `scripts/make-readme-assets.py` runs without errors

### README
10. Under 800 lines
11. Local path before cloud path in Install
12. No duplicate content between overview and deep-dive
13. Provider capability matrix in Architecture
14. All image links resolve (no broken references)

---

## Files Changed

### Bug fixes (~15 lines)
- `src/vulca/layers/layered_prompt.py` — remove "ANCHOR" from section headers
- `src/vulca/layers/layered_generate.py` — skip keying for background layers
- `src/vulca/providers/comfyui.py` — validate PNG response before returning

### New script (~150 lines)
- `scripts/make-readme-assets.py` — produces 7 display images

### Generated assets (not hand-written)
- `assets/demo/v3/readme/*.png` — 7 composite display images
- `assets/demo/v3/layered/` — regenerated layers + composite
- `assets/demo/v3/defense3/` — regenerated defense3 variants
- `assets/demo/v3/edit/` — regenerated edit comparison
- `assets/demo/v3/studio/` — regenerated studio session

### Documentation
- `README.md` — full rewrite (~800 lines)

---

## Risk & Mitigation

**Risk: Regenerated phases still produce noise.**
Mitigated: Fix C (PNG validation) ensures corrupted data raises an error rather than silently saving noise. If ComfyUI is fundamentally unstable, fall back to v2 assets for those sections.

**Risk: Regenerated layered composite has new artifacts.**
Mitigated: Visual inspection after each regeneration. If quality is poor, use v2 `layered-showcase.png` and individual v2 layer images.

**Risk: README exceeds 800 lines.**
Mitigated: Full CLI reference moved to docs. `<details>` blocks for secondary content. Scenarios 3-4 cut if needed.

**Risk: Studio still times out or produces 0% scores.**
Mitigated: VLM timeout issue is pre-existing (Ollama). Studio runs functionally (generates images, iterates, accepts). Use v2 studio images as fallback if v3 quality is poor.

## Estimated Effort

| Phase | Time |
|-------|------|
| Bug fixes (3) | ~30 min |
| Regenerate phases 2/4/5/7 | ~45 min wall time (mostly waiting for ComfyUI) |
| Visual inspection + re-runs if needed | ~15 min |
| `make-readme-assets.py` script | ~30 min |
| README rewrite | ~2 hours |
| Review + polish | ~30 min |
| **Total** | ~4 hours |
