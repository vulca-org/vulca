# Full 8-Capability Showcase — One Artwork, Complete Journey

**Date:** 2026-04-13
**Status:** Draft
**Type:** Marketing showcase

## Core Concept

**One artwork. Eight capabilities. One continuous story.**

Take Van Gogh's **Starry Night** through the entire VULCA pipeline — from first evaluation to cultural translation to layer editing — demonstrating every capability in a single narrative arc.

**Why Starry Night:** Universally recognized, already have evaluation data, rich cross-cultural story (Van Gogh was influenced by Japanese ukiyo-e), and the visual contrast between Western oil and Chinese ink wash is immediately compelling.

## The 8-Step User Journey

### Step 1: EVALUATE — "What does a cultural AI think of Starry Night?"

```bash
vulca evaluate starry-night.jpg -t western_academic --mode reference
```

**Show:** L1-L5 bar chart + key VLM quotes:
- L5=95%: "achieves profound aesthetic resonance by transforming a simple landscape into a meditation on the sublime"
- L3=50%: "rejects strict adherence to academic realism"
- Recommendation: "study the principles of linear perspective (透视法)"

**Point:** VULCA doesn't just generate — it understands art at a cultural level.

### Step 2: CROSS-TRADITION — "How do different cultures see the same painting?"

```bash
vulca evaluate starry-night.jpg \
  -t western_academic,chinese_xieyi,japanese_traditional,photography \
  --mode fusion
```

**Show:** Comparison table:
```
                 western  chinese_xieyi  japanese  photography
L1 Visual         80%       70%           60%       95%
L2 Technical      70%       60%           50%       100%
L3 Cultural       50%       20%           20%       90%
L4 Critical       80%       50%           60%       90%
L5 Philosophy     90%       90%           70%       100%
```

**Point:** L5 (philosophy) scores 90% in BOTH Western and Chinese traditions — Van Gogh's spiritual resonance transcends culture. But L3 (cultural context) drops to 20% in Chinese xieyi — different traditions demand different techniques.

### Step 3: TOOLS — "What do the algorithms say?"

```bash
vulca tools run whitespace_analyze --image starry-night.jpg -t chinese_xieyi
vulca tools run brushstroke_analyze --image starry-night.jpg -t western_academic
vulca tools run composition_analyze --image starry-night.jpg -t photography
```

**Show:** 
- Whitespace: 3% (xieyi ideal: 30-55%) — "the canvas is saturated, no liu bai"
- Brushstroke energy: 0.94 — "extremely high energy, aligns with expressionist tradition"
- Composition: 0.88 thirds alignment — "strong rule-of-thirds positioning"

**Point:** Zero-API-cost algorithmic analysis that quantifies what the VLM describes qualitatively.

### Step 4: DECOMPOSE — "Let's take it apart"

```bash
vulca layers split starry-night.jpg -o ./starry-layers/ --mode extract
```

**Show:** 3 layers on checkerboard background:
- Sky layer (swirling blue, 25% coverage)
- Stars + Moon layer (bright yellows, 1% coverage — precise extraction)
- Village + Cypress layer (dark silhouettes, 25% coverage)

**Point:** Any image can be decomposed into editable layers — not just VULCA-generated art.

### Step 5: REDRAW — "What if we repainted the sky in Chinese ink wash?"

```bash
vulca layers redraw ./starry-layers/ --layer sky \
  -i "misty ink wash sky, subtle gradients, reserved white space, sumi-e" \
  --provider comfyui
```

**Show:** Before/after of just the sky layer:
- Before: Van Gogh's swirling blue impasto
- After: Subtle ink wash with mist and liu bai (留白)

The village and stars layers are UNTOUCHED — only the sky changed.

**Point:** Non-destructive editing. Change one element, keep everything else pixel-identical.

### Step 6: COMPOSITE — "Put it back together"

```bash
vulca layers composite ./starry-layers/ -o starry-remixed.png
```

**Show:** The composited result — Van Gogh's village and stars with a Chinese ink wash sky.

**Point:** Layer-based workflow produces results impossible with single-image generation.

### Step 7: INPAINT — "One more touch"

```bash
vulca inpaint starry-remixed.png \
  --region "upper left corner" \
  --instruction "Add a Chinese calligraphy poem inscription about moonlit mountains" \
  -t chinese_xieyi --provider comfyui
```

**Show:** Before/after — the remixed painting now has a calligraphy inscription in the corner, completing the cultural translation.

**Point:** Region-specific editing preserves the rest of the artwork.

### Step 8: RE-EVALUATE — "Did we improve the cultural score?"

```bash
vulca evaluate starry-final.png -t chinese_xieyi --mode reference
```

**Show:** Score comparison:
```
                 Original    After Journey
L1 Visual          70%          75%
L2 Technical       60%          65%
L3 Cultural        20%          55%  ← biggest jump
L4 Critical        50%          60%
L5 Philosophy      90%          88%
```

**Point:** The full journey measurably improved cultural alignment (L3: 20% → 55%) while preserving philosophical depth (L5: 90% → 88%). VULCA guided the entire process — evaluate, understand, edit, verify.

## Visual Output Design

### Hero Image (Twitter/dev.to hook)
8 panels in a strip showing the journey:
```
[Original] → [Scores] → [Tools] → [Layers] → [Redraw] → [Composite] → [Inpaint] → [Re-score]
```

### Article Structure
```
Title: "8 Things I Did to Starry Night with a Cultural AI — A Complete Walkthrough"

1. The Setup (30 sec read) — pip install vulca + download image
2. Step 1-2: Understanding (evaluate + cross-tradition)
3. Step 3: Measuring (tools)
4. Step 4-6: Transforming (decompose → redraw → composite)
5. Step 7: Finishing (inpaint)
6. Step 8: Verifying (re-evaluate)
7. CTA — try it yourself
```

### Twitter Thread (8 posts)
Post 1: Hero strip image + hook
Post 2: Evaluate scores with VLM quote
Post 3: Cross-tradition table (the viral part)
Post 4: Decomposed layers on checkerboard
Post 5: Before/after sky redraw
Post 6: Final composite + inpaint
Post 7: Score improvement comparison
Post 8: CTA (pip install + star)

## Technical Prerequisites

- ComfyUI running (torch 2.9.0 in venv)
- Ollama + Gemma 4 (for evaluate)
- opencv-python-headless (for tools)
- Starry Night image downloaded (already in assets/showcase/originals/)

## Execution Script

Create `scripts/run-full-showcase.py` that runs all 8 steps sequentially, saves every intermediate artifact, and produces the display images automatically.

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/run-full-showcase.py` | Run all 8 steps, save artifacts |
| `assets/showcase/journey/` | All intermediate artifacts |
| `assets/showcase/display/journey-strip.png` | 8-panel hero image |
| `docs/blog/2026-04-13-8-things-starry-night.md` | dev.to article |
