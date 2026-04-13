# VULCA v0.15 Launch Post Design

**Date:** 2026-04-13
**Status:** Approved
**Type:** Content (technical article)

## Overview

A 3000-5000 word deep technical article announcing VULCA v0.15.x, published to dev.to (full), Medium (condensed), and GitHub Discussion (full).

**Title:** "I Built a Free Local AI Art Pipeline on My Mac — Here's What Broke"

**Angle:** Product story hook + technical deep dives + CTA. Not marketing — real code, real war stories, real bugs.

**Audience:** Developers interested in AI art, Apple Silicon, local-first tools, Stable Diffusion.

## Structure (7 Sections)

### 1. Hook + Visual Proof (~300 words)

"What if you could run a complete AI art creation pipeline — 13 cultural traditions, 5-dimension scoring, structured layer generation — entirely on your MacBook, for free?"

Content:
- 3 generated images inline (v3 gallery: chinese_xieyi, japanese_traditional, brand_design)
- CLI evaluation bar chart output
- "No cloud API key. No GPU server. Just `pip install vulca`."

### 2. What is VULCA + The Local Stack (~500 words)

One-liner positioning: "AI-native cultural art creation SDK — generate, evaluate, decompose, and evolve visual art across 13 cultural traditions."

Content:
- Architecture diagram (text-based, from README)
- `pip install vulca` + 3-command quickstart
- Why ComfyUI + Ollama (not locked to any backend)
- Provider pluggable architecture — show ComfyUI workflow JSON construction (comfyui.py lines 42-60)
- Capability system: `multilingual_prompt`, `raw_rgba`
- "VULCA is not a ComfyUI plugin. ComfyUI is one of several image providers."

Academic grounding: EMNLP 2025 Findings + VULCA-Bench (7,410 samples).

### 3. L1-L5 Cultural Evaluation (~400 words)

"Most AI art tools generate. VULCA evaluates."

Content:
- The 5-dimension framework (L1 Visual Perception → L5 Philosophical Aesthetics)
- 13 tradition YAML definitions with custom weights
- Three modes: strict (judge), reference (mentor), fusion (cross-cultural)
- Code: `vulca.aevaluate()` API — 3 lines to score any image
- CLI output example with bar chart
- Self-evolving weights from session history

### 4. Deep Dive: Structured Layer Generation (~800 words)

"VULCA doesn't generate images. It generates layers."

Content:
- Full pipeline: intent → VLM planning (Gemma 4) → per-layer generation → luminance keying → alpha composite
- Serial-first style anchoring (Defense 3, v0.14): first layer → style_ref → parallel rest
- Code: `build_anchored_layer_prompt()` — the full function showing canvas/content/spatial/style blocks
- Code: `LayerPromptResult` — the CLIP-aware flat prompt for SDXL
- Image: layered exploded view (assets/demo/v3/readme/layered_exploded.png or v2/layered-showcase.png)
- CJK-aware prompt handling: "VULCA automatically translates CJK prompts to English for CLIP-based providers"

### 5. Deep Dive: Making SDXL Work Locally (~800 words)

"Two traps we fell into — and how we climbed out."

**Trap 1: The ANCHOR Hallucination** (lead story)
- Our prompt had `[CANVAS ANCHOR]` section headers
- SDXL's CLIP encoder interpreted "ANCHOR" as content
- Result: literal ship anchors painted on rice paper (include the actual image if available)
- Fix: renamed to `[CANVAS]`, `[STYLE]`, etc.

**Trap 1b: The 77-Token CLIP Ceiling**
- Structured prompt was 120+ tokens
- CLIP truncates at 77 — actual subject description never reached the encoder
- Gallery images (simple prompts, ~30 tokens) worked perfectly
- Fix: `LayerPromptResult` — flat subject-first prompt <70 tokens + separate negative_prompt
- Code: the `english_only` branch in `build_anchored_layer_prompt()`

**Trap 2: PyTorch MPS — A Version Minefield**
- torch 2.11.0 produces black (4KB) or noise (2MB) images
- KSampler runs fine, VAEDecode outputs zeros
- `--force-fp32` doesn't help (correctness bug, not precision)
- 3 compounding bugs: SDPA stride (#163597), Conv2d chunk (#169342), Metal kernel migration (#155797)
- Version matrix table (2.9.0 works, 2.10+ broken)
- "We wrote a complete compatibility guide" → link to docs/apple-silicon-mps-comfyui-guide.md
- Link to our comments on PyTorch #163597 and ComfyUI #10681

### 6. What's Working, What's Next (~300 words)

Current state:
- "All 13 traditions generating locally on Apple Silicon"
- "8 E2E phases validated, 8 mock tests passing in 2.4 seconds"
- v0.15.0 (E2E wiring) + v0.15.1 (README + SDXL fixes) shipped

Roadmap:
- Gemini cloud path (when billing is enabled)
- SAM3 text-prompted segmentation
- Web UI / Gradio demo

### 7. Get Started + CTA (~300 words)

**5-minute quickstart:**
```bash
pip install vulca
export VULCA_IMAGE_BASE_URL=http://localhost:8188
vulca create "Misty mountains after spring rain" -t chinese_xieyi --provider comfyui -o art.png
vulca evaluate art.png -t chinese_xieyi --mode reference
```

**Product positioning:**
"VULCA is an open-source SDK for AI-native cultural art creation. It's not another Midjourney wrapper or ComfyUI plugin — it's a standalone framework that brings cultural intelligence to AI art generation. 13 traditions, each with its own L1-L5 scoring rubric, terminology, and taboos."

**Star + contribute CTA:**
- "If this resonates, star us on GitHub: https://github.com/vulca-org/vulca"
- "Try it, break it, tell us what failed: Issues welcome"
- "Built on peer-reviewed research: EMNLP 2025 Findings"
- PyPI badge + GitHub badge + Python 3.10+ badge

**Links:**
- GitHub: https://github.com/vulca-org/vulca
- PyPI: https://pypi.org/project/vulca/
- MPS Guide: link to docs
- Research: EMNLP 2025 + arXiv links

## Platform Adaptation

| Platform | Version | Notes |
|----------|---------|-------|
| dev.to | Full (3000-5000 words) | All code blocks, all images. Tags: #python #machinelearning #opensource #ai |
| Medium | Condensed (~2000 words) | Keep sections 1-3 + 5 (ANCHOR story) + 7. Link to dev.to for full version. Remove most code blocks. |
| GitHub Discussion | Full + internal links | Same as dev.to but with relative links to docs/, commits, issues |

## Images to Include

1. Hero: 3 gallery images (chinese_xieyi, japanese_traditional, brand_design) — from v3/gallery
2. CLI evaluation bar chart — text block from README
3. Layered exploded view — from v3/readme/layered_exploded.png or v2/layered-showcase.png
4. ANCHOR hallucination — v2 image if available, or describe with text
5. PyTorch version matrix — table (text)
6. Inpaint before/after — from v3/readme/inpaint_comparison.png

## dev.to Metadata

```yaml
---
title: "I Built a Free Local AI Art Pipeline on My Mac — Here's What Broke"
published: true
tags: python, machinelearning, opensource, ai
cover_image: # v3 gallery hero strip or tradition grid
---
```

## Success Criteria

1. Article is 3000-5000 words
2. Contains at least 5 code blocks with real VULCA code
3. Contains at least 4 images
4. Every technical claim is backed by specific code or commit reference
5. CTA section includes GitHub link, star request, and PyPI install
6. No marketing fluff — every paragraph has technical substance

## Files to Create

- `docs/blog/2026-04-13-launch-post.md` — full article (dev.to / GitHub Discussion version)
- `docs/blog/2026-04-13-launch-post-medium.md` — condensed Medium version (optional, can derive from full)
