# Vulca Palette Mask Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first Vulca palette-mask split mode that asks an image provider such as NB2/Gemini for a color-coded ownership image, decodes it into editable layer masks, and writes the normal layer stack.

**Architecture:** Add a focused `vulca.layers.palette_mask` module for prompt construction, provider call, RGB color decoding, and layer extraction. Wire it into existing `layers_split` CLI/MCP surfaces as `mode="palette"` while preserving the existing analyze-first layer planning flow.

**Tech Stack:** Python 3.10+, Pillow, NumPy, existing Vulca provider registry, existing manifest writer, pytest.

---

### Task 1: Palette Mask Core

**Files:**
- Create: `src/vulca/layers/palette_mask.py`
- Test: `tests/test_palette_mask.py`

- [ ] **Step 1: Write failing decoder tests**

Add tests for prompt content, exact-color decoding, nearest-color tolerance, and layer PNG extraction.

- [ ] **Step 2: Run tests to verify failure**

Run: `python3 -m pytest tests/test_palette_mask.py -q`
Expected: import failure for `vulca.layers.palette_mask`.

- [ ] **Step 3: Implement palette mask module**

Define:
- `DEFAULT_PALETTE`
- `build_palette_mask_prompt(layers, palette=None)`
- `decode_palette_mask(mask_image, layers, palette=None, tolerance=48)`
- `split_palette(image_path, layers, output_dir, provider="nb2", api_key="", palette=None, tolerance=48)`

`split_palette` should call provider once with `raw_prompt=True`, decode the returned RGB image into per-layer masks, apply masks to the source image, write full-canvas RGBA PNGs, and write `manifest.json` with `split_mode="palette"`.

- [ ] **Step 4: Run tests to verify pass**

Run: `python3 -m pytest tests/test_palette_mask.py -q`
Expected: all tests pass.

- [ ] **Step 5: Commit core**

Run:
```bash
git add src/vulca/layers/palette_mask.py tests/test_palette_mask.py
git commit -m "feat: add palette mask split core"
```

### Task 2: CLI and MCP Wiring

**Files:**
- Modify: `src/vulca/cli.py`
- Modify: `src/vulca/mcp_server.py`
- Modify: `src/vulca/layers/__init__.py`
- Test: `tests/test_palette_mask.py`

- [ ] **Step 1: Add failing surface tests**

Extend tests to assert:
- CLI help includes `palette`.
- MCP `layers_split` docstring mentions `palette`.
- `split_palette` is importable from `vulca.layers`.

- [ ] **Step 2: Run tests to verify failure**

Run: `python3 -m pytest tests/test_palette_mask.py -q`
Expected: failures for missing CLI/MCP/export wiring.

- [ ] **Step 3: Wire mode**

Add `palette` to CLI choices and help. In CLI split handler, route `args.mode == "palette"` to `split_palette`. In MCP `layers_split`, add docstring text and route `mode == "palette"` to `split_palette`.

- [ ] **Step 4: Run focused tests**

Run: `python3 -m pytest tests/test_palette_mask.py -q`
Expected: all tests pass.

- [ ] **Step 5: Commit wiring**

Run:
```bash
git add src/vulca/cli.py src/vulca/mcp_server.py src/vulca/layers/__init__.py tests/test_palette_mask.py
git commit -m "feat: expose palette mask split mode"
```

### Task 3: Local Smoke

**Files:**
- No source changes expected.

- [ ] **Step 1: Run focused regression tests**

Run: `python3 -m pytest tests/test_palette_mask.py tests/test_v012_split_vlm.py -q`
Expected: pass.

- [ ] **Step 2: Run mock provider smoke**

Run a temporary script that creates a two-object source image, patches a mock provider to return a two-color palette mask, and confirms the output manifest/layers.

- [ ] **Step 3: Run real Gemini/NB2 smoke if key exists**

Check only whether `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set. If present, run `split_palette(... provider="nb2")` against a tiny synthetic slide-like image. If absent, report the smoke as blocked without printing secrets.

- [ ] **Step 4: Commit plan**

Run:
```bash
git add docs/superpowers/plans/2026-06-09-vulca-palette-mask.md
git commit -m "docs: plan palette mask split mode"
```

### Self-Review

- Spec coverage: covers palette mask protocol, decoding, `layers_split(mode="palette")`, Redraw/PPT-compatible layers, and Gemini/NB2 smoke attempt.
- Placeholder scan: no placeholders remain.
- Type consistency: functions are consistently named `build_palette_mask_prompt`, `decode_palette_mask`, and `split_palette`.
