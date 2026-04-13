# World Masterworks Showcase — "VULCA Scores the World's Greatest Art"

**Date:** 2026-04-13
**Status:** Draft
**Type:** Marketing showcase + Technical demonstration

## Overview

A showcase series where VULCA evaluates 9 iconic world masterworks (photographs + paintings) across cultural traditions, demonstrating the L1-L5 evaluation system's depth. The showcase tells a user-journey story: download an image → evaluate it → cross-culture compare → generate a cultural translation → compare scores.

**Core narrative:** "What does a cultural AI think about the world's most famous art?"

## Goals

1. **Demonstrate VULCA's evaluate capability** on universally recognized images — not AI-generated art, real masterworks.
2. **Show cross-cultural scoring** — same artwork evaluated against different traditions reveals how cultures "see" differently.
3. **Drive user acquisition** — every showcase ends with "try it yourself: `pip install vulca`".
4. **Establish credibility** — scoring Pulitzer winners and museum masterworks positions VULCA as serious, research-backed tool.

## Non-Goals

- Not demonstrating decompose/edit/composite (known bugs, not showcase-ready).
- Not using copyrighted or ethically sensitive images.
- Not claiming VULCA's scores are "correct" — framing is "here's how different cultural lenses read the same artwork."

---

## Source Images (9 works, all public domain)

### Photographs (3)

| # | Title | Artist | Year | Download Source | Primary Tradition |
|---|-------|--------|------|---------------|------------------|
| 1 | Earthrise | William Anders / NASA | 1968 | NASA official (AS08-14-2383) | photography |
| 2 | Migrant Mother | Dorothea Lange | 1936 | Library of Congress (LC-DIG-ppmsca-12883) | photography |
| 3 | The Blue Marble | NASA / Apollo 17 | 1972 | NASA Science (AS17-148-22727) | photography |

### Western Paintings (3)

| # | Title | Artist | Year | Download Source | Primary Tradition |
|---|-------|--------|------|---------------|------------------|
| 4 | The Starry Night | Vincent van Gogh | 1889 | Rawpixel CC0 (8000x6415) | western_academic |
| 5 | Girl with a Pearl Earring | Johannes Vermeer | c.1665 | Rawpixel CC0 (5068x6000) | western_academic |
| 6 | Water Lilies | Claude Monet | 1919 | Rawpixel CC0 / Met Open Access | watercolor |

### Non-Western Masterworks (3)

| # | Title | Artist | Year | Download Source | Primary Tradition |
|---|-------|--------|------|---------------|------------------|
| 7 | Great Wave off Kanagawa | Katsushika Hokusai | c.1831 | Wikimedia Commons (8561x6037) | japanese_traditional |
| 8 | Along the River During Qingming Festival (清明上河图) | Zhang Zeduan | c.12th c. | Wikimedia Commons (bridge section crop) | chinese_gongbi |
| 9 | Padmapani Bodhisattva (Ajanta Cave 1) | Unknown | c.5th c. CE | Wikimedia Commons / Internet Archive | south_asian |

---

## Showcase Structure — 4 Acts

### Act 1: "Scoring the Masterworks" (Primary Tradition Evaluation)

Each image evaluated against its **own** tradition using `--mode reference` (Cultural Mentor mode).

**User journey:**
```bash
# Download image (user provides their own or uses our provided script)
# Evaluate against its native tradition
vulca evaluate earthrise.jpg -t photography --mode reference
vulca evaluate starry-night.jpg -t western_academic --mode reference
vulca evaluate great-wave.jpg -t japanese_traditional --mode reference
vulca evaluate qingming-bridge.jpg -t chinese_gongbi --mode reference
vulca evaluate padmapani.jpg -t south_asian --mode reference
```

**What to show for each evaluation:**
1. The artwork image
2. The L1-L5 bar chart scores
3. 2-3 key quotes from the VLM's reference-mode feedback (e.g., "L2 Technical Execution: 95% — The impasto technique achieves remarkable texture depth...")
4. The algorithmic tool results where applicable:
   ```bash
   vulca tools run brushstroke_analyze --image starry-night.jpg -t western_academic
   vulca tools run whitespace_analyze --image great-wave.jpg -t japanese_traditional
   vulca tools run composition_analyze --image earthrise.jpg -t photography
   ```

**Display format:** Card layout per artwork:
```
┌─────────────────────────────────────────────┐
│  [Image thumbnail]                           │
│  The Starry Night — Vincent van Gogh, 1889   │
│  Tradition: western_academic                 │
│                                              │
│  L1 Visual Perception    ████████████████ 92% │
│  L2 Technical Execution  █████████████████ 95% │
│  L3 Cultural Context     ████████████████ 90% │
│  L4 Critical Interpret.  ██████████████ 85%   │
│  L5 Philosophical Aesth. █████████████████ 95% │
│                                              │
│  "The swirling sky achieves extraordinary    │
│   qiyun shengdong — spirit resonance and     │
│   vitality — through impasto brushwork..."   │
│                                              │
│  Brushstroke Energy: 0.94 | Composition: 0.88│
└─────────────────────────────────────────────┘
```

### Act 2: "Cross-Cultural Lenses" (Fusion Mode)

The same artwork evaluated against 3-5 **different** traditions. This is the viral hook — shows how cultures see differently.

**Most interesting cross-evaluations:**

| Artwork | Cross-Tradition | Why It's Interesting |
|---------|----------------|---------------------|
| Starry Night | chinese_xieyi | Van Gogh's brushwork has striking parallels to 写意 spontaneity and qi-yun |
| Starry Night | japanese_traditional | Van Gogh was deeply influenced by ukiyo-e — how much did it absorb? |
| Great Wave | western_academic | How does ukiyo-e score under Western perspective/composition rules? |
| Great Wave | chinese_xieyi | Shared East Asian ink tradition but fundamentally different aesthetics |
| Earthrise | japanese_traditional | ma (間) — the negative space of the void around Earth |
| Earthrise | chinese_xieyi | liu bai (留白) — reserved white space reading of cosmic void |
| Water Lilies | chinese_xieyi | Monet's late work converges with ink-wash abstraction and atmospheric poetry |
| Qingming Festival | chinese_xieyi | Gongbi vs xieyi — internal dialogue between meticulous and freehand traditions |
| Padmapani | western_academic | Fresco technique comparison (Ajanta ↔ Giotto/Michelangelo) |
| Padmapani | chinese_gongbi | Buddhist art transmission along the Silk Road |

**User journey:**
```bash
# Single artwork, multiple traditions
vulca evaluate starry-night.jpg \
  -t western_academic,chinese_xieyi,japanese_traditional,photography \
  --mode fusion

# Expected output: comparison table
#   Tradition             L1    L2    L3    L4    L5    Overall
#   western_academic      92%   95%   90%   85%   95%   92%
#   chinese_xieyi         75%   60%   35%   70%   80%   58%
#   japanese_traditional  80%   55%   40%   75%   85%   63%
#   photography           30%   20%   10%   40%   50%   28%
```

**Display format:** Radar chart or heatmap per artwork showing scores across traditions.

```
                 Starry Night — Cross-Cultural Scores

              western_academic  chinese_xieyi  japanese_trad  photography
  L1 Visual      ████ 92%        ███ 75%        ███ 80%       █ 30%
  L2 Technical   █████ 95%       ██ 60%         ██ 55%        █ 20%
  L3 Cultural    ████ 90%        █ 35%          █ 40%         ░ 10%
  L4 Critical    ███ 85%         ██ 70%         ███ 75%       █ 40%
  L5 Philosophy  █████ 95%       ███ 80%        ███ 85%       ██ 50%
```

### Act 3: "Cultural Translation" (Generate + Re-evaluate)

Take the most compelling cross-evaluation result (e.g., Starry Night scored against chinese_xieyi at L3=35%) and generate a VULCA version in that tradition. Then re-evaluate to show the score difference.

**User journey:**
```bash
# Step 1: See the gap
vulca evaluate starry-night.jpg -t chinese_xieyi --mode reference
# L3 Cultural Context: 35%
# "Missing liu bai (reserved white space). Color palette over-saturated
#  for ink wash tradition. No evidence of cun fa (texture strokes)."

# Step 2: Generate the same scene in chinese_xieyi
vulca create "Swirling night sky over a village, cypress tree, crescent moon, stars" \
  -t chinese_xieyi --provider comfyui -o starry-night-xieyi.png

# Step 3: Re-evaluate
vulca evaluate starry-night-xieyi.png -t chinese_xieyi --mode reference
# L3 Cultural Context: 82%
# "Effective use of liu bai. Ink gradation suggests mist and atmosphere.
#  The cypress rendered with spontaneous brushwork (xieyi)."

# Step 4: Algorithmic comparison
vulca tools run whitespace_analyze --image starry-night.jpg -t chinese_xieyi
# "Whitespace: 3% — far below ideal range (30-55%)"
vulca tools run whitespace_analyze --image starry-night-xieyi.png -t chinese_xieyi
# "Whitespace: 42% — within ideal range"
```

**Display format:** Side-by-side comparison with score overlay:
```
┌──────────────────────┐    ┌──────────────────────┐
│  [Starry Night orig] │ →  │  [VULCA xieyi ver.]  │
│  chinese_xieyi: 35%  │    │  chinese_xieyi: 82%  │
│  Whitespace: 3%      │    │  Whitespace: 42%     │
│  "No liu bai"        │    │  "Effective liu bai"  │
└──────────────────────┘    └──────────────────────┘
```

### Act 4: "Your Turn" (CTA)

**Content:**
```
Every image in this showcase was scored with 6 commands.
No cloud API key needed. No subscription. Just pip install.

pip install vulca
vulca evaluate your-image.jpg -t chinese_xieyi --mode reference

13 cultural traditions. 5 evaluation dimensions.
Self-evolving weights that learn from your sessions.
Built on peer-reviewed research (EMNLP 2025 Findings).

⭐ Star us: https://github.com/vulca-org/vulca
📦 Install: pip install vulca
📄 Paper: https://arxiv.org/abs/2601.07986
```

---

## Technical Implementation

### Image Acquisition Script

Create `scripts/download-showcase-images.py`:
```python
# Downloads all 9 public domain images from verified sources
# Saves to assets/showcase/originals/
# Resizes to 1024x1024 for consistent evaluation
# Records source URL, license, and attribution in manifest.json
```

### Evaluation Script

Create `scripts/run-showcase-evaluation.py`:
```python
# For each image:
#   1. Run primary tradition evaluation (--mode reference)
#   2. Run 3-4 cross-tradition evaluations (--mode fusion or individual --mode reference)
#   3. Run applicable algorithmic tools
#   4. Save all results to assets/showcase/results/{image_name}/
#       - evaluation.json (L1-L5 scores + rationales)
#       - cross_cultural.json (fusion mode results)
#       - tools.json (brushstroke, whitespace, composition)
```

### Display Image Production

Create additions to `scripts/make-readme-assets.py` or a new `scripts/make-showcase-assets.py`:
```python
# For each image, produce:
#   1. Score card (image + L1-L5 bars + key quote)
#   2. Cross-cultural heatmap (image + multi-tradition score table)
#   3. Cultural translation comparison (original + VULCA version + score diff)
# Output to assets/showcase/display/
```

### Cultural Translation Generation

For Act 3, generate VULCA versions of selected masterworks:
```bash
# Starry Night → chinese_xieyi
vulca create "Swirling night sky over village, cypress tree, crescent moon, ink wash" \
  -t chinese_xieyi --provider comfyui -o assets/showcase/translations/starry-night-xieyi.png

# Great Wave → chinese_xieyi
vulca create "Towering ocean wave with small boats, mountain in distance, ink wash" \
  -t chinese_xieyi --provider comfyui -o assets/showcase/translations/great-wave-xieyi.png

# Earthrise → chinese_xieyi (most provocative)
vulca create "Earth rising over lunar horizon, vast cosmic void, ink wash minimalist" \
  -t chinese_xieyi --provider comfyui -o assets/showcase/translations/earthrise-xieyi.png
```

---

## UX / Display Design

### Format 1: dev.to Article

**Title:** "I Let a Cultural AI Score the World's Greatest Art — The Results Were Humbling"

**Structure:**
1. Hook image: 3x3 grid of all 9 masterworks with overall scores overlaid
2. "What is VULCA" (2 paragraphs + install command)
3. Act 1: Score cards for 4-5 most interesting works (not all 9 — keep it focused)
4. Act 2: Cross-cultural heatmap for 2-3 works
5. Act 3: Starry Night cultural translation (before/after with scores)
6. CTA

**Word count:** 2000-2500 words (shorter than launch post — more visual, less code)

### Format 2: Twitter/X Thread

**Thread structure (10 posts):**

Post 1 (hook): 3x3 masterworks grid + "I let a cultural AI score the world's greatest art. Thread 🧵"

Post 2: Earthrise score card — "NASA's Earthrise: L5 Philosophical Aesthetics 97%. The AI noted 'cosmic negative space that echoes Japanese ma (間).'"

Post 3: Starry Night cross-cultural — "Van Gogh's Starry Night scored 92% in Western Academic... but only 35% in Chinese Xieyi. Why? 'No liu bai (留白). Over-saturated for ink wash.'"

Post 4: Starry Night cultural translation — before/after side-by-side

Post 5: Great Wave cross-cultural — "Hokusai in his own tradition: 95%. Under Western rules: 65%. The 'flat' perspective that breaks Western rules IS the Japanese aesthetic."

Post 6: Qingming Festival — "The world's most complex painting: 清明上河图. VULCA identified 5 layers and found a gongbi score of 98%."

Post 7: Tool analysis — whitespace/brushstroke comparisons

Post 8: "What about YOUR art?" — pip install vulca

Post 9: GitHub link + star request

Post 10: Academic credentials — EMNLP 2025

### Format 3: GitHub Discussion / Showcase Page

Full results for all 9 works with complete JSON outputs, hosted as a permanent showcase page linked from README.

---

## Content Ethics

### What we claim
- "Here's how VULCA's L1-L5 framework reads these masterworks through different cultural lenses"
- NOT "This is the correct score" or "VULCA judges art better than humans"

### Framing
- Educational, not authoritative
- "Different traditions value different qualities" — no hierarchy of cultures
- Always attribute works properly with artist, date, museum/collection, license
- Acknowledge the framework is a model, not truth

### What we avoid
- War/disaster Pulitzer photos (scoring suffering)
- Living artists' work (perceived judgment)
- Political figures or controversial subjects
- Claiming cultural superiority ("Western art scores low in Chinese tradition" → frame as "different values", not "Western art is bad")

---

## Success Criteria

1. Twitter thread gets >500 impressions within 48 hours
2. dev.to article gets >200 views within 1 week
3. At least 1 new GitHub star from showcase traffic
4. PyPI daily downloads increase >20% vs baseline (140/day)
5. All 9 evaluations produce plausible, non-trivial L1-L5 scores
6. Cross-cultural scores show meaningful differentiation (not all high or all low)
7. Cultural translation (Act 3) produces visible score improvement

---

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/download-showcase-images.py` | Download + resize 9 public domain images |
| `scripts/run-showcase-evaluation.py` | Run all evaluations + save JSON results |
| `scripts/make-showcase-assets.py` | Produce display images (score cards, heatmaps, comparisons) |
| `assets/showcase/originals/` | 9 source images |
| `assets/showcase/results/` | JSON evaluation results per image |
| `assets/showcase/translations/` | VULCA-generated cultural translations |
| `assets/showcase/display/` | Final display-ready composite images |
| `docs/blog/2026-04-13-world-masterworks-showcase.md` | dev.to article |

## Estimated Time

| Task | Time |
|------|------|
| Download + resize 9 images | 30 min |
| Run all evaluations (9 × ~4 traditions) | 1-2 hours (VLM bound) |
| Generate 2-3 cultural translations | 30 min (ComfyUI bound) |
| Produce display assets | 1 hour |
| Write dev.to article | 2 hours |
| Write Twitter thread | 30 min |
| **Total** | **~6 hours** |
