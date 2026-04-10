# v0.14 E2E Testing + README Rewrite Design

**Date:** 2026-04-10
**Status:** Approved, ready for implementation plan

## Background

v0.14.0 shipped with all three A-path defenses (keying, validation, style_ref anchoring). The README still uses old v2 demo assets (synthetic/stale) and mixes old/new descriptions. 217 of 1495 tests fail due to environment issues (Python 3.9, missing deps), and zero tests hit a real provider API. There is no E2E coverage.

## Goals

1. **E2E test suite** — verify every README-advertised feature works end-to-end with real Gemini API calls.
2. **README rewrite** — restructure README around real E2E output artifacts. Every image shown is reproducible from the test script.
3. **Self-verifying documentation** — running the E2E script regenerates all demo assets, so README never goes stale.

## Non-Goals

- Fixing the 214 pre-existing test failures (Python 3.9 env, missing deps) — separate effort.
- CI/CD setup — separate effort.
- Performance benchmarking — not measuring latency or cost optimization.

## Architecture

### E2E Script

Single script `scripts/generate-e2e-demo.py` that:
1. Requires `GEMINI_API_KEY` env var (fail fast if missing).
2. Runs 8 phases sequentially, each producing artifacts in `assets/demo/v3/`.
3. Each phase has assertions (file exists, correct image mode, reasonable scores).
4. Outputs `assets/demo/v3/e2e-report.json` with status + artifact paths.
5. Idempotent — re-running overwrites existing artifacts.

### Phases

#### Phase 1: Single-Image Create (13 traditions)

For each of the 13 traditions, run `vulca.create()` with a tradition-appropriate prompt via Gemini provider. Save output to `assets/demo/v3/gallery/{tradition}.png`.

Prompts (one per tradition):
| Tradition | Prompt |
|-----------|--------|
| chinese_xieyi | 水墨山水，雨后春山，松间茅屋 |
| chinese_gongbi | 工笔牡丹，细腻勾线，三矾九染 |
| western_academic | Impressionist garden at golden hour, oil on canvas |
| japanese_traditional | 京都金閣寺の雪景色、墨絵風 |
| watercolor | English countryside cottage, loose wet-on-wet watercolor |
| islamic_geometric | Alhambra-inspired geometric pattern, turquoise and gold |
| african_traditional | Ndebele mural pattern, bold primary colors |
| south_asian | Mughal miniature, garden scene with lotus pond |
| ukiyo_e | 浮世絵、波と富士山、藍摺 |
| brand_design | Premium tea packaging, mountain watermark, Eastern aesthetics |
| photography | Misty mountain landscape at dawn, cinematic |
| default | Serene landscape with mountains and water |
| custom | (skip — requires user YAML, not testable in automated E2E) |

**12 traditions tested** (custom skipped). ~12 Gemini calls.

Assertions per image:
- File exists and is valid PNG
- Image dimensions > 0
- File size > 10KB (not an error placeholder)

#### Phase 2: Layered Create (chinese_xieyi)

Run `vulca.create()` with `--layered` equivalent (SDK `acreate` with layered mode) for chinese_xieyi. This exercises the full v0.14 pipeline: plan → serial first layer → style_ref → parallel rest → keying → validation.

Save to `assets/demo/v3/layered/`:
- `composite.png` — final composited image
- `{layer_name}.png` — each layer's RGBA output
- `manifest.json` — layer metadata

~3-5 Gemini calls (one per planned layer).

Assertions:
- At least 2 layers produced
- Each layer PNG is RGBA mode
- Background layer has high alpha coverage (>90%)
- Subject layers have partial alpha (some transparent, some opaque)
- `manifest.json` exists and is valid JSON
- Composite PNG exists

#### Phase 3: Evaluate (L1-L5 scoring)

Take 3 representative images from Phase 1 (chinese_xieyi, western_academic, brand_design) and evaluate each with `vulca.evaluate()`.

Save to `assets/demo/v3/eval/{tradition}_scores.json`.

~3 VLM calls (one per image × one evaluation each).

Assertions:
- Each evaluation returns 5 dimension scores (L1-L5)
- Scores are numeric, 0-100 range
- At least one dimension has a non-trivial feedback string

#### Phase 4: Defense 3 Showcase

Generate the same 3-layer plan twice:
1. **Without style_ref** — call `layered_generate` with `reference_image_b64=""`
2. **With style_ref** — call `layered_generate` normally (v0.14 default behavior)

Save to `assets/demo/v3/defense3/`:
- `no_ref/` — layers without style anchoring
- `with_ref/` — layers with style anchoring
- Both include layer PNGs + composite

~6 Gemini calls (3 per variant).

Assertions:
- Both runs produce valid layer PNGs
- With-ref variant: provider calls for layers 2+ include non-empty `reference_image_b64`
- (Visual quality comparison is subjective — human reviews the output)

#### Phase 5: Edit (Layer Redraw)

Take the layered output from Phase 2. Redraw one non-background layer with a new prompt.

Save to `assets/demo/v3/edit/`:
- `before.png` — original composite
- `after.png` — composite with redrawn layer
- `redrawn_layer.png` — the new layer

~1 Gemini call.

Assertions:
- Redrawn layer PNG exists, RGBA mode
- New composite differs from original (pixel comparison)

#### Phase 6: Inpaint

Take one image from Phase 1. Inpaint a region with a new instruction.

Save to `assets/demo/v3/inpaint/`:
- `before.png` — original
- `after.png` — inpainted

~1 Gemini call.

Assertions:
- Output image exists, same dimensions as input
- Output differs from input (pixel comparison in target region)

#### Phase 7: Studio (Brief-Driven)

Run a non-interactive studio session (`--auto` equivalent) with Gemini.

Save to `assets/demo/v3/studio/`:
- `concept_*.png` — concept variants
- `final.png` — selected final output
- `session.json` — studio session log

~5-10 Gemini calls.

Assertions:
- At least 1 concept image produced
- Final output exists
- Session log records state transitions

#### Phase 8: Tools (Local, Zero API)

Run algorithmic analysis tools on one of the Phase 1 outputs. No Gemini calls.

Save to `assets/demo/v3/tools/`:
- `brushstroke.json` — brushstroke analysis
- `composition.json` — composition analysis

Assertions:
- Each JSON has expected keys (energy, confidence, etc.)
- Values are numeric and in expected ranges

### Total Gemini Calls

| Phase | Calls |
|-------|-------|
| 1. Gallery | 12 |
| 2. Layered | 3-5 |
| 3. Evaluate | 3 |
| 4. Defense 3 | 6 |
| 5. Edit | 1 |
| 6. Inpaint | 1 |
| 7. Studio | 5-10 |
| 8. Tools | 0 |
| **Total** | **~31-38** |

### README Structure

Based on Phase outputs:

```
# VULCA

[badges: PyPI, Python 3.10+, License, Tests]

**Tagline** — one sentence

[Hero image: Phase 2 composite — layered xieyi landscape]

## Install
pip install vulca + GEMINI_API_KEY

## Quick Start
vulca create "水墨山水" -t chinese_xieyi --layered --provider gemini
→ [Phase 2 composite image]

## The VULCA Workflow

### Create — Single Image
[Phase 1 best example + CLI command]

### Create — Structured Layers (v0.14)
[Phase 2 layer breakdown: individual layers + composite]
Explain: serial first → style anchor → parallel rest

### Evaluate — L1-L5 Cultural Scoring
[Phase 3 score output — formatted terminal screenshot or rendered table]

### Edit — Redraw Layers
[Phase 5 before/after comparison]

### Inpaint — Region Repaint
[Phase 6 before/after comparison]

## Style Consistency (Defense 3, v0.14)
[Phase 4 side-by-side: without vs with style_ref]

## 13 Cultural Traditions
[Phase 1 gallery grid: 4×3 images]
[Table: tradition name + one-line description]

## Tools — Algorithmic Analysis (Zero API Cost)
[Phase 8 output examples]

## Studio — Brief-Driven Session
[Phase 7: concepts → final]

## Architecture
[Keep existing diagram, simplify]

## Entry Points
CLI / Python SDK / MCP Server (concise)

## Research
[Keep existing citations]
```

### Error Handling

- If a Phase fails (API error, timeout), the script logs the error, marks that phase as FAILED in the report, and continues to the next phase.
- README generation only uses artifacts from PASSED phases.
- Script exits with non-zero status if any phase failed.

### Environment

- Requires: `GEMINI_API_KEY` env var
- Requires: `pip install vulca[layers]` (PIL, numpy, rembg)
- Optional: cv2 for tools (Phase 8 degrades gracefully)
- Python 3.10+ (matching project requirement)

## Risks

| Risk | Mitigation |
|------|-----------|
| Gemini rate limiting | Add 2s delay between calls; retry with backoff on 429 |
| Gemini output quality varies | Run E2E, human reviews artifacts, re-run bad ones |
| Large assets in git | `assets/demo/v3/` added to git (these ARE the product demo) |
| Script takes long to run | Sequential is fine (~5-10 min); not a CI test |

## Out of Scope

- Fixing pre-existing 214 test failures (Python 3.9 env issue)
- CI/CD pipeline
- ComfyUI E2E (requires local ComfyUI server)
- OpenAI provider E2E (Gemini is the primary provider)
