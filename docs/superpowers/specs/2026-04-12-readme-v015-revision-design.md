# README v0.15.0 Major Revision

**Date:** 2026-04-12
**Status:** Approved
**Type:** Documentation (README.md rewrite)

## Background

The README (758 lines) was last substantially updated around v0.12. Since then:
- v0.13.x: Layer validation, keying, caching, retry architecture
- v0.14.0: Defense 3 — serial-first style-ref anchoring
- v0.14.1: Gemma 4 JSON parse fallbacks, sdist fix, prompt engineering
- v0.15.0: E2E phases 2-7 full wiring, CJK-aware prompts, provider-agnostic inpaint

The README still leads with `export GOOGLE_API_KEY`, references only `assets/demo/v2/` images, and doesn't mention the local stack (ComfyUI + Ollama) that now runs all 8 E2E phases.

## Goals

1. **Reorient the narrative from "cloud API required" to "local-first, cloud optional"** — the Install section should make ComfyUI + Ollama the default path, Gemini the alternative.
2. **Showcase v0.14-v0.15 capabilities** — Defense 3 style-ref, CJK-aware multilingual prompts, provider-agnostic inpaint, E2E 8/8 local validation.
3. **Tighten the structure from ~15 fuzzy sections to 12 clean sections** — eliminate duplication between overview and deep-dive sections.
4. **Mix v2 and v3 image assets** — keep v2's polished demos/GIFs/master paintings, add v3 hero images from real E2E runs in hero area and a validation showcase.
5. **Keep total length under 800 lines** — push detailed setup guides to `docs/`, not README.

## Non-Goals

- Not creating new demo images, GIFs, or visual assets (use what exists in v2 + v3).
- Not rewriting CLI help text or SDK docstrings.
- Not updating the MCP plugin README (separate repo).
- Not adding automated README verification (the `scripts/verify-readme.py` already exists).

## Architecture

### 12-Section Structure

```
1.  Hero (visual hook + one-line positioning)
2.  Install + Quick Start (merged: two paths + first command)
3.  What You Can Do (6-capability index, 2-3 lines each)
4.  Create (layered + style-ref + CJK-aware callout)
5.  Evaluate (three modes)
6.  Edit + Inpaint (merged, two subheadings with visual demos)
7.  Decompose (v2 master paintings preserved)
8.  Studio (Brief-driven)
9.  Tools (algorithmic analysis)
10. Architecture (updated diagram + provider matrix + self-evolution collapsed)
11. 13 Traditions
12. Entry Points + Research + Citation
```

### Section Details

#### 1. Hero

**Keep:** Badge row, one-line description, 3-image showcase, CLI evaluation demo.

**Change:**
- Replace one or more hero images with v3 E2E gallery outputs if they're visually competitive. Candidates: `assets/demo/v3/gallery/chinese_xieyi.png`, `assets/demo/v3/gallery/japanese_traditional.png`. If v3 images are not display-quality (raw SDXL 1024x1024), keep v2 images.
- Update the one-line description to mention "local-first" or "zero-cost local stack".
- Add version badge or link to CHANGELOG.

#### 2. Install + Quick Start (merged)

**Structure:**
```markdown
## Install

pip install vulca

### Local (free, no API key)
[3 lines: ComfyUI + Ollama env vars, link to docs/local-provider-setup.md]
vulca create "Misty mountains" -t chinese_xieyi --provider comfyui -o art.png

### Cloud (Gemini)
export GOOGLE_API_KEY=your-key
vulca create "Misty mountains" -t chinese_xieyi -o art.png

### No GPU? Try mock mode
vulca create "Misty mountains" -t chinese_xieyi --provider mock -o art.png
```

**Key decisions:**
- Local path first, cloud second, mock as fallback.
- Do NOT claim "30 seconds" — be honest: mock is instant, Gemini ~10s, local SDXL ~2 min.
- Local Stack deep setup (ComfyUI installation, model downloads, Ollama model pull) stays in `docs/local-provider-setup.md`. README gets a one-line link.
- Optional extras (`pip install vulca[mcp]`, etc.) stay in `<details>` block as-is.

#### 3. What You Can Do

**6 capabilities, each 2-3 lines + one CLI example. No images. No duplication with sections below.**

1. **Generate** — 13 traditions, structured layers, local or cloud
2. **Evaluate** — L1-L5 scoring, three modes (strict/reference/fusion)
3. **Edit** — layer redraw + region inpaint, provider-agnostic
4. **Decompose** — split any image into transparent layers
5. **Studio** — brief-driven multi-round creative sessions
6. **Analyze** — 5 algorithmic tools, zero API cost

Each links to its deep-dive section via anchor.

#### 4. Create

**Keep:** Structured creation (`--layered`), tradition examples, layer-driven design transfer.

**Add:**
- Defense 3 style-ref anchoring explanation (currently in "What You Can Do" layered section, move here as the authoritative location).
- CJK-aware prompt callout: "VULCA automatically translates CJK prompts to English for CLIP-based providers (ComfyUI/SDXL) while preserving CJK natively for multilingual providers (Gemini)."
- Provider choice: `--provider comfyui` vs `--provider gemini`.

**Remove:** Duplicate layered explanation from "What You Can Do" section.

#### 5. Evaluate

**Keep as-is.** The three-mode showcase (strict/reference/fusion) with CLI output examples is well-written and current. No changes needed beyond minor version references.

#### 6. Edit + Inpaint (merged)

**Two subheadings:**

```markdown
## Edit + Inpaint

### Layer-Based Editing
[v2 sky comparison image]
[Scenario 1 code: split → lock → redraw → composite]
Note: Now provider-agnostic (v0.15) — works with ComfyUI, Gemini, or any provider.

### Region-Based Inpainting
[v2 inpaint before/after image]
[Inpaint CLI code]
Note: Provider parameter added in v0.15 — no longer Gemini-only.

<details>
<summary>More editing workflows</summary>
[Scenario 2: poster design]
[Scenario 3: parallax — consider cutting if over 800 lines]
</details>
```

**Key change:** Both now highlight provider-agnostic as a v0.15 feature.

#### 7. Decompose

**Keep as-is.** The Qi Baishi and Mona Lisa decomposition demos with v2 images are the README's strongest visual content. No changes.

#### 8. Studio

**Keep as-is.** The concept grid → final output showcase is effective. Minor: add `--provider comfyui` example alongside existing `--provider gemini`.

#### 9. Tools

**Keep as-is.** 5 tools with CLI output examples. No changes needed.

#### 10. Architecture

**Update the ASCII diagram** to reflect:
- Provider capability system (`multilingual_prompt`, `raw_rgba`, `raw_prompt`)
- Local VLM path (Ollama + Gemma 4) alongside cloud VLM
- Self-Evolution section collapsed inside Architecture (move from standalone section)
- E2E validation status: "8/8 phases validated on local stack (ComfyUI + Ollama, Apple Silicon MPS)"

**Add provider capability matrix:**
```
| Provider | Generate | Inpaint | Layered | Multilingual |
|----------|----------|---------|---------|-------------|
| ComfyUI  | ✓        | ✓ (v0.15) | ✓    | English-only |
| Gemini   | ✓        | ✓       | ✓       | CJK native  |
| OpenAI   | ✓        | —       | —       | English-only |
| Mock     | ✓        | ✓       | ✓       | —           |
```

**Self-Evolution** becomes a `<details>` block inside Architecture, not a top-level section.

#### 11. 13 Traditions

**Keep as-is.** Image row + tradition list + custom YAML example. No changes needed.

#### 12. Entry Points + Research + Citation

**Merge** the current "Four Entry Points" and "Research" sections into one closing section.

**Structure:**
```
## Integration & Research

### CLI / SDK / MCP / ComfyUI
[Keep existing 4 subsections, but move full CLI reference to docs/ and link]

### Research
[Keep paper table + citation blocks]
```

**Trim:** Full CLI reference (`<details>` block, 50 lines) → link to a dedicated docs page or keep collapsed.

### Image Asset Decisions

| Location | Current | New |
|----------|---------|-----|
| Hero 3-image row | v2 (xieyi, western, brand) | Try v3 `gallery/chinese_xieyi.png` for first slot; keep v2 for others if v3 isn't display-quality |
| CLI eval demo | v2 output | Keep (not a real screenshot) |
| Layer decomposition | v2 masters (Qi Baishi, Mona Lisa) | Keep v2 |
| Sky redraw comparison | v2 scenario1-comparison | Keep v2 |
| Inpaint before/after | v2 hero-xieyi → inpaint-after | Keep v2 |
| Studio concepts | v2 studio-c1..c4 | Keep v2 |
| GIFs | v2 vhs-create, vhs-layers, vhs-tools, vhs-studio | Keep v2 |
| Poster workflow | v2 scenario2-poster | Keep v2 |
| Tools viz | v2 tools-viz | Keep v2 |

**Mark all v2 images with `<!-- v2-asset -->` HTML comments** for future replacement tracking.

### Badges

Update the badge row:
- PyPI version: keep (dynamic)
- Python version: keep
- License: keep
- Tests: remove hardcoded count or link to CI
- MCP tools: update count if changed

### TOC

Add a table of contents after the hero section (GitHub auto-generates one, but an explicit one above the fold helps scanners).

## Success Criteria

1. README is under 800 lines.
2. First runnable command is within 15 lines of "## Install".
3. Local path (ComfyUI) appears before cloud path (Gemini) in Install.
4. No duplicate content between "What You Can Do" and deep-dive sections.
5. All v2 image references have `<!-- v2-asset -->` comments.
6. Provider capability matrix present in Architecture.
7. Self-Evolution is inside Architecture, not standalone.
8. CJK-aware prompt feature mentioned in Create section.
9. Edit + Inpaint merged with provider-agnostic callout.
10. `docs/local-provider-setup.md` linked, not duplicated.

## Files Changed

- `README.md` — full rewrite (~800 lines, down from 758 but restructured)
- No other files changed. Image assets are referenced, not created.

## Risk

**Risk: v3 hero image not display-quality.**
Mitigated: inspect first, fall back to v2 if raw SDXL output isn't competitive. The spec explicitly allows keeping v2.

**Risk: exceeds 800 lines.**
Mitigated: push CLI reference and local stack setup guide to docs/. Use `<details>` aggressively for secondary content.

**Risk: broken image links after restructure.**
Mitigated: do not rename or move any image files. Only change README references.
