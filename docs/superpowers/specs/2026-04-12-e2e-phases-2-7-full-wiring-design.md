# E2E Runner Full Wiring: Phases 2-7 + Core Library Fixes

**Date:** 2026-04-12
**Status:** Revised after codex + superpowers review (3 BLOCKERs + 4 MAJORs fixed)
**Type:** Feature (runner wiring) + Fix (core library CJK-aware prompts + provider responsibility)

## Background

### The Wiring Gap

The E2E demo runner (`scripts/generate-e2e-demo.py`) currently implements 3 of 8 phases from the E2E spec (`docs/superpowers/specs/2026-04-10-e2e-readme-rewrite-design.md`):

| Phase | Status | Entry Point |
|---|---|---|
| 1 Gallery | Wired | `run_phase1_gallery()` — calls `provider.generate()` directly |
| 2 Layered | **Unwired** | SDK: `execute(LAYERED, PipelineInput(...))` exists and works |
| 3 Evaluate | Wired | `run_phase3_evaluate()` — calls `vulca._vlm.score_image()` (private API) |
| 4 Defense 3 | **Unwired** | SDK: same as Phase 2, called twice with ±style_ref |
| 5 Edit | **Unwired** | SDK: `redraw_layer()` exists and works |
| 6 Inpaint | **Unwired** | SDK: `ainpaint()` exists and works |
| 7 Studio | **Unwired** | SDK: `run_studio(auto=True)` exists and works |
| 8 Tools | Wired | `run_phase8_tools()` — local CV analysis |

A parallel codex + superpowers audit (2026-04-12) confirmed that **all 5 unwired phases have fully working underlying implementations**. The gap is purely runner plumbing (~20-40 lines per phase).

### The CJK Prompt Path Problem

A deeper investigation revealed that the project has **two independent prompt-building paths**, and only one was validated by the 2026-04-11 prompt engineering experiment:

**Path A (Phase 1 runner — validated):**
```
TRADITION_PROMPTS[entry]["prompt"]  (hand-crafted English)
  → provider.generate(prompt, tradition="", negative_prompt=...)
  → ComfyUI/SDXL CLIP receives English text ✅
```

**Path B (SDK pipeline — NOT validated on ComfyUI/SDXL):**
```
PipelineInput(intent="工笔牡丹", tradition="chinese_gongbi")
  → PlanLayersNode → VLM plans layers → per-layer regeneration_prompt (language uncontrolled)
  → build_anchored_layer_prompt() → injects YAML CJK:
      canvas: "cooked silk (熟绢)"
      sibling roles: "白描勾线", "分染罩染"
      style_keywords: "工笔, 白描勾线, 分染罩染"
  → ComfyUI.generate(mixed CJK/English prompt) → CLIP receives CJK noise ❌
```

**Root causes identified (codex + superpowers audit):**
1. `build_anchored_layer_prompt()` (`src/vulca/layers/layered_prompt.py`) unconditionally injects CJK from tradition YAML (`term_zh`, `tradition_layers[].role`, `style_keywords`) into per-layer prompts, regardless of whether the downstream provider can handle CJK.
2. `PlanLayersNode`'s VLM prompt template (`src/vulca/layers/plan_prompt.py`) does not instruct the VLM to output `regeneration_prompt` in English.
3. ComfyUI's provider lacks a `raw_prompt` mechanism (Gemini has one at `gemini.py:109`), so there's no way for callers to bypass its auto-suffix.
4. Phase 3 runner calls the private `vulca._vlm.score_image()` instead of the public `vulca.aevaluate()`.

These are not new bugs — they've always existed. They were invisible because:
- Gemini's text encoder handles CJK natively (no tokenization problem)
- Phase 2-7 were never run on ComfyUI before (the runner didn't have them)
- Phase 3 worked fine with the private API (just a coupling concern)

## Goals

1. **Wire all 5 remaining phases** (2, 4, 5, 6, 7) into the E2E runner with the same pattern as existing phases (async function → save artifacts → validate → return report dict → merge into scoped report).
2. **Fix the CJK-in-CLIP problem for the LAYERED pipeline path** so Phase 2/4/5 produce correct results on ComfyUI/SDXL, not just Gemini.
3. **Unify provider `raw_prompt` handling** — add to ComfyUI so both providers support caller-controlled prompts without auto-suffix injection.
4. **Migrate Phase 3 to the public SDK API** — `vulca.aevaluate()` instead of `vulca._vlm.score_image()`.
5. **Produce a complete set of E2E demo artifacts** — `assets/demo/v3/` gains `layered/`, `defense3/`, `edit/`, `inpaint/`, `studio/` subdirectories alongside the existing `gallery/`, `eval/`, `tools/`.

## Non-Goals

- Not rewriting Phase 1 to use `vulca.create()`. The Phase 1 runner's direct `provider.generate()` call is intentional for the gallery sweep use case (no multi-round evaluate/decide loop).
- Not removing the prompt engineering scaffolding (CLI flags, empty override map). It's documented as future-experiment infrastructure.
- Not redesigning the pipeline engine or template system.
- Not adding automated tests (continuing the spike convention; manual verification at each phase).
- Not running the full 8-phase suite end-to-end in one go (wall time ~45 min on ComfyUI). Phases are independently runnable via `--phases`.
- Not fixing Gemini API billing (blocked on wangjindong).
- Not modifying tradition YAML content (the fix is in the code that READS the YAML, not the YAML itself).

## Architecture

### Part 1: Core Library Fixes (4 changes, ~40 lines total)

These fixes are prerequisites for Phase 2/4/5 working correctly on ComfyUI.

#### Fix 1: `build_anchored_layer_prompt()` — CJK-aware output

**File:** `src/vulca/layers/layered_prompt.py`

**Current behavior:** Receives `anchor: TraditionAnchor` (which contains `canvas_description`, `style_keywords`), `sibling_roles: list[str]`, and `LayerInfo` (which contains `regeneration_prompt`). Unconditionally embeds all values — including CJK content from `anchor.canvas_description` (e.g., "cooked silk (熟绢)"), `anchor.style_keywords` (e.g., "工笔, 白描勾线"), and `sibling_roles` (e.g., "白描勾线", "分染罩染") — into the per-layer prompt string sent to the image provider.

**New behavior:** Accept an optional `english_only: bool = False` parameter. When `True`:
- `anchor.canvas_description`: strip CJK parentheticals via regex (e.g., "cooked silk (熟绢)" → "cooked silk")
- `anchor.style_keywords`: filter to ASCII/Latin-only entries (drop any keyword containing CJK characters)
- `sibling_roles`: strip CJK characters from each role string, keeping the English portion (or drop the role if it's pure CJK)
- `LayerInfo.regeneration_prompt`: leave unchanged (Fix 2 ensures the VLM produces English here)

The `english_only` flag is set by `LayerGenerateNode._generate_layers_native()` based on a new provider capability flag `"multilingual_prompt"`. Providers that understand CJK natively (Gemini) declare this capability; providers that don't (ComfyUI/SDXL) omit it. The check is: `english_only = "multilingual_prompt" not in provider.capabilities`.

**Provider capability addition:**
- `src/vulca/providers/gemini.py`: add `"multilingual_prompt"` to `capabilities: frozenset`
- `src/vulca/providers/comfyui.py`: no change (omitting = "needs English")
- This follows the existing pattern (`"raw_rgba"` capability for native layer generation)

#### Fix 2: `PlanLayersNode` — instruct VLM to output English `regeneration_prompt`

**File:** `src/vulca/layers/plan_prompt.py`

**Current behavior:** The VLM prompt template does not specify the output language for `regeneration_prompt`.

**New behavior:** Add one line to the VLM prompt template:
```
IMPORTANT: All "regeneration_prompt" values MUST be in English, regardless of the user's input language. Translate if necessary.
```

This ensures the VLM (Gemma 4 or Gemini) always produces English per-layer prompts, even when the user intent is CJK. The VLM naturally acts as a translator.

#### Fix 3: ComfyUI `raw_prompt` support

**File:** `src/vulca/providers/comfyui.py`

**Current behavior:** Always appends `, {tradition.replace('_', ' ')} style` when `tradition` is non-empty and not `"default"` (lines 38-39). No way to bypass.

**New behavior:** Accept `raw_prompt: bool` via `**kwargs`. When `True`, skip the tradition suffix:

```python
full_prompt = prompt
if not kwargs.get("raw_prompt", False):
    if tradition and tradition != "default":
        full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"
```

This aligns with Gemini's existing `raw_prompt` mechanism (`gemini.py:109`).

**Note:** In LAYERED native calls, `layered_generate()` already passes `raw_prompt=True` to the provider (codex confirmed at `layered_generate.py:88`). So this fix makes the existing intent explicit rather than relying on `tradition` being empty.

#### Fix 4: Phase 3 public API migration

**File:** `scripts/generate-e2e-demo.py` (the `run_phase3_evaluate` function)

**Current behavior:** Calls `from vulca._vlm import score_image` (private API).

**New behavior:** Calls `from vulca import aevaluate` (public API). Adapts the return value from `EvalResult` fields to the existing report dict format.

### Part 2: Runner Wiring (5 phases, ~150 lines total)

Each phase follows the same pattern as existing Phase 1/3/8:
1. `async def run_phaseN_*()` function
2. Calls existing SDK entry point
3. Saves artifacts to `assets/demo/v3/<subdir>/`
4. Validates outputs (assertions from the E2E spec)
5. Returns a report dict with phase metadata + entries + status
6. Report merges into `scoped_report_path` via the existing merge block in `main_async`

#### Phase 2: Layered Create (`run_phase2_layered`)

**SDK call:**
```python
from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput

output = await execute(LAYERED, PipelineInput(
    subject=subject,
    intent=intent,
    tradition="chinese_xieyi",
    provider=provider_name,
    layered=True,
    output_dir=str(layered_dir),
))
```

**Output dir:** `assets/demo/v3/layered/`

**Artifacts:**
- `composite.png` — final blended image
- `{layer_name}.png` — each layer as RGBA PNG (3-5 layers expected)
- `manifest.json` — layer metadata (names, blend modes, positions, coverage)

**Assertions:**
- ≥ 2 layers produced
- Each layer is a valid RGBA PNG (4-channel, >10 KB)
- Background layer: alpha coverage > 90%
- Subject layers: partial alpha (mixed transparent/opaque regions)
- `manifest.json` exists and parses as valid JSON with a `layers` array
- `composite.png` exists and is a valid PNG

**Default intent:** `"水墨山水，雨后春山，松间茅屋"` (same as Phase 1's `chinese_xieyi` entry, but the pipeline will translate via VLM planning)

**Default tradition:** `chinese_xieyi`

**Provider calls:** ~3-5 (one per planned layer, serial first + parallel rest)

#### Phase 4: Defense 3 Showcase (`run_phase4_defense3`)

**What this demonstrates:** The v0.14.0 style-ref anchoring feature. Shows the visual difference between layered generation with vs. without the serial-first style reference chain.

**SDK call:** Two calls to `layered_generate()` (the lower-level function, not the full pipeline engine):
1. **Without style_ref:** Call `layered_generate()` with `reference_image_b64=""` AND a flag/mechanism to skip the serial-first style derivation (all layers generated in parallel, no cross-layer reference). This requires either:
   - A `disable_style_ref=True` parameter on `layered_generate()` (~5 lines to add)
   - Or running all layers through individual `provider.generate()` calls without the reference chain
2. **With style_ref:** Call `layered_generate()` normally (v0.14 default behavior — serial first, derive RGB, pass as reference to parallel rest)

Both calls use the same layer plan (generated once by PlanLayersNode or hardcoded from tradition YAML).

**Output dir:** `assets/demo/v3/defense3/`
- `no_ref/` — layers + composite without style anchoring
- `with_ref/` — layers + composite with style anchoring

**Assertions:**
- Both runs produce valid layer PNGs
- Both produce a composite
- With-ref variant's provider calls for layers 2+ include non-empty `reference_image_b64` (verifiable via pipeline event callback or by inspecting the LayerOutcome metadata)
- Visual comparison is subjective (human reviews)

**Provider calls:** ~6 (3 per variant for a 3-layer plan)

**Implementation note:** The `disable_style_ref` toggle needs a small addition to `layered_generate()` in `src/vulca/layers/layered_generate.py`. When enabled (`disable_style_ref=True`), the function must **skip the serial-first step entirely** and schedule ALL layers through the parallel path without any cross-layer `reference_image_b64`. This is NOT just blanking the style_ref — it requires bypassing the serial/parallel split at lines ~377-414 so all layers generate independently. Estimated ~15 lines of conditional logic wrapping the existing split.

**Layer plan sharing:** Both with-ref and no-ref variants must use the **same layer plan** for a fair visual comparison. The runner will call `PlanLayersNode` (or the plan-building function) ONCE to generate the plan, then pass it to `layered_generate(plan=...)` twice. `layered_generate()` already accepts `plan: list[LayerInfo]` as a parameter, so this is straightforward.

**Dependency:** Phase 4 is **independent of Phase 2** (generates its own layers + plan). The execution order `2 → 4` is a suggestion for natural progression, not a hard dependency.

#### Phase 5: Edit / Layer Redraw (`run_phase5_edit`)

**Dependency:** Phase 2 must have run first (needs `assets/demo/v3/layered/` artifacts).

**SDK call:**
```python
from vulca.layers.redraw import redraw_layer
from vulca.layers.types import LayeredArtwork

# Load the Phase 2 artifact into a LayeredArtwork object
artwork = LayeredArtwork.load(str(layered_dir))  # or construct from manifest.json
target_layer = next(
    l for l in artwork.layers if l.info.content_type != "background"
)

result = await redraw_layer(
    artwork=artwork,
    layer_name=target_layer.info.name,
    instruction="Redraw with more vibrant autumn colors and a setting sun",
    provider=provider_name,
    tradition="chinese_xieyi",
    artwork_dir=str(layered_dir),
)
```

Then recomposite using the existing composite function.

**Implementation note:** Verify `LayeredArtwork.load()` exists (or implement manifest.json → LayeredArtwork construction if it doesn't). The `redraw_layer()` signature at `src/vulca/layers/redraw.py:35` requires a `LayeredArtwork` object, not a directory path string.

**Output dir:** `assets/demo/v3/edit/`
- `before.png` — original composite (copied from Phase 2)
- `after.png` — composite with redrawn layer
- `redrawn_layer.png` — the new layer

**Assertions:**
- `redrawn_layer.png` exists and is RGBA mode
- `after.png` differs from `before.png` (pixel comparison)

**Provider calls:** ~1

#### Phase 6: Inpaint (`run_phase6_inpaint`)

**Dependency:** Phase 1 must have run first (needs a gallery image as input).

**SDK call:**
```python
from vulca.inpaint import ainpaint

result = await ainpaint(
    image=str(input_image_path),  # e.g., gallery/chinese_xieyi.png
    region="center 30%",          # natural-language region spec
    instruction="Add a small red pavilion near the water",
    tradition="chinese_xieyi",
)
```

**IMPORTANT (codex BLOCKER fix):** `ainpaint()` does NOT accept a `provider` parameter. Internally it hardcodes `get_image_provider("gemini")` at `src/vulca/studio/phases/inpaint.py:137`. This means **Phase 6 currently only works with Gemini, not ComfyUI.**

Options (decide at implementation time):
1. **Add `provider` parameter to `ainpaint()`** — ~10 lines in `inpaint.py` to thread the provider name through. Preferred if we want ComfyUI support.
2. **Accept Phase 6 as Gemini-only** — mark it as skipped when `--provider comfyui` and Gemini billing is unavailable. Simpler but limits local testing.
3. **Defer Phase 6** to when Gemini billing is enabled.

Recommendation: Option 1 (add provider param) — it's a small change and makes Phase 6 provider-agnostic like the other phases.

**Output dir:** `assets/demo/v3/inpaint/`
- `before.png` — original (copied from gallery)
- `after.png` — inpainted result

**Assertions:**
- `after.png` exists, same dimensions as `before.png`
- `after.png` differs from `before.png` (pixel comparison)

**Provider calls:** ~1

#### Phase 7: Studio / Brief-Driven (`run_phase7_studio`)

**SDK call:**
```python
import asyncio
from vulca.studio.interactive import run_studio

# run_studio() is SYNCHRONOUS (wraps its own event loop internally).
# Must be called via asyncio.to_thread() from the async runner, with a timeout.
session = await asyncio.wait_for(
    asyncio.to_thread(
        run_studio,
        intent="Create a serene Chinese landscape with mountains emerging from morning mist",
        project_dir=str(studio_dir),
        provider=provider_name,
        auto=True,
        max_rounds=3,
    ),
    timeout=600,  # 10-min safety net
)
```

**IMPORTANT (codex + superpowers BLOCKER fix):** `run_studio()` is **synchronous** (not async). It does NOT accept a `tradition` parameter — tradition steering must be embedded in the `intent` string (e.g., "in the style of Chinese xieyi ink painting"). The `asyncio.to_thread()` wrapper is required because the runner's `main_async` is async.

**Parameters verified** against `src/vulca/studio/interactive.py:52`: `intent, *, project_dir, provider, concept_count, api_key, data_dir, auto, max_rounds`.

**Output dir:** `assets/demo/v3/studio/`
- `concept_*.png` — concept variant images
- `final.png` — selected final output
- `session.json` — studio session log (state transitions, scores, decisions)

**Assertions:**
- At least 1 concept PNG produced
- `final.png` exists and is a valid PNG
- `session.json` exists and parses as valid JSON with recognizable state transition records

**Provider calls:** ~5-10 (concept generation + evaluation + iteration)

### Part 3: Runner Integration

#### Dependency-aware execution order

When multiple phases are requested via `--phases`, the runner executes them in dependency order:

```
Phase 2 (layered) ← must run before Phase 4 and Phase 5
Phase 4 (defense3) ← uses its own layer plan, but benefits from Phase 2's plan as reference
Phase 5 (edit) ← REQUIRES Phase 2's layered artifact
Phase 6 (inpaint) ← requires Phase 1's gallery (already exists)
Phase 7 (studio) ← fully independent
```

Execution order when all 5 are requested: `6 → 7 → 2 → 5 → 4` (independent phases first, then the Phase 2→5 chain, then Phase 4 last since it's the longest single run).

**Hard dependency:** Phase 5 REQUIRES Phase 2 artifacts. If Phase 5 is requested without Phase 2 having run (in this session or any prior session), the runner checks for `assets/demo/v3/layered/manifest.json`. If missing, fail fast: `"Phase 5 (edit) requires Phase 2 (layered) artifacts. Run --phases 2 first."`

**Soft dependency:** Phase 6 requires Phase 1 gallery artifacts (already exist from prior runs). If `assets/demo/v3/gallery/chinese_xieyi.png` is missing, fail fast with a similar message.

**No dependency:** Phases 4 and 7 are fully independent. Phase 4 generates its own layer plan and layers. Phase 7 runs a complete studio session from intent text alone.

#### `main_async` dispatch additions

Add `elif phase == N:` blocks for phases 2, 4, 5, 6, 7 in `main_async`'s phase dispatch loop, following the same try/except/report pattern as phases 1, 3, 8.

#### CLI flag compatibility

All existing flags compose naturally:
- `--provider comfyui` (or `gemini`) → passed to each phase
- `--gallery-subdir` → only affects Phase 1 (unchanged)
- `--traditions` → only affects Phase 1 (unchanged)
- `--phases 2,5,6` → runs those 3 phases in dependency order

No new CLI flags are needed.

### Wall Time Estimates (ComfyUI, Apple Silicon MPS)

| Phase | Provider calls | Estimated time |
|---|---|---|
| 2 Layered | 3-5 | ~6-10 min |
| 4 Defense 3 | 6 | ~12 min |
| 5 Edit | 1 | ~2 min |
| 6 Inpaint | 1 | ~2 min |
| 7 Studio | 5-10 | ~10-20 min |
| **Total** | **16-23** | **~32-46 min** |

Recommended: run phases individually (`--phases 2`, then `--phases 5`, etc.) rather than all at once. Each phase produces independent artifacts and a scoped report.

## Success Criteria

### Per-fix verification

| Fix | Verification |
|---|---|
| Fix 1 (layered_prompt CJK) | Run Phase 2 with `--provider comfyui`. Inspect the per-layer prompts in logs — no CJK characters should appear in CLIP-bound text. Chinese xieyi layers should have English descriptions. |
| Fix 2 (PlanLayersNode English) | Same run — check that VLM-generated `regeneration_prompt` fields in the layer plan are in English, not CJK. |
| Fix 3 (ComfyUI raw_prompt) | `grep -n 'raw_prompt' src/vulca/providers/comfyui.py` shows the new kwarg. Existing tests pass. |
| Fix 4 (Phase 3 API) | `grep -n 'score_image\|_vlm' scripts/generate-e2e-demo.py` returns 0 matches (no more private API usage). Phase 3 still produces valid score reports. |

### Per-phase verification

Each phase's assertions (listed above) are checked programmatically by the runner after the SDK call completes. The runner prints a summary and the report JSON records pass/fail per assertion.

### Overall verification

After all 5 phases run successfully:
- `assets/demo/v3/` has 8 subdirectories: `gallery/`, `eval/`, `tools/`, `layered/`, `defense3/`, `edit/`, `inpaint/`, `studio/`
- `e2e-report.json` (or scoped variant) records all 8 phases with `status: ok`
- Total artifact size is reasonable (~50-80 MB including all PNGs)

## Risk & Rollback

**Risk: Phase 2 CJK fix breaks Gemini path.**
Mitigated: the `english_only` flag defaults to `False`, so Gemini (which handles CJK natively) is unaffected. Only triggered when provider is ComfyUI/SDXL.

**Risk: `raw_prompt` changes ComfyUI's default behavior.**
Mitigated: `raw_prompt` defaults to `False`. Existing callers that don't pass it see zero behavioral change.

**Risk: `disable_style_ref` in layered_generate changes default behavior.**
Mitigated: defaults to `False` (current behavior). Only Phase 4's "no_ref" variant passes `True`.

**Risk: Phase 3 API migration introduces regressions.**
Mitigated: `vulca.aevaluate()` wraps the same underlying `score_image()` call with additional features. If `aevaluate()` fails, the runner can fall back to the direct call (add a try/except with a deprecation warning).

**Risk: Studio session hangs in auto mode.**
Mitigated: `run_studio(auto=True)` has built-in timeouts and max_rounds limits. The runner adds an outer `asyncio.wait_for(timeout=600)` as a safety net.

**Risk: VLM plans 0 layers or >10 layers.**
Mitigated: runner clamps the plan to 2-5 layers. If VLM returns 0 layers, fail fast with a clear error. If >5, truncate to 5 and log a warning. This prevents both "empty output" and "45-minute runaway generation."

**Risk: `ainpaint()` hardcodes Gemini provider.**
Mitigated: spec recommends adding `provider` parameter to `ainpaint()` (~10 lines). If not done, Phase 6 is Gemini-only and skipped when `--provider comfyui`.

**Risk: Tradition YAML schema changes break Fix 1.**
Mitigated: Fix 1 uses field names (`canvas_description`, `style_keywords`) that are load-bearing for the existing Gemini path too. Schema changes would break Gemini as well, so they're unlikely without a coordinated migration.

**Rollback:** Each phase's artifacts are in a separate subdirectory. Deleting a subdirectory reverts that phase. Code changes are across ~7 files but each is small and independently revertible.

## Pre-requisites

- ComfyUI running at `http://localhost:8188` with `sd_xl_base_1.0.safetensors` loaded (for ComfyUI provider runs)
- OR Gemini API key with paid-tier billing enabled (for Gemini provider runs)
- Ollama running with `gemma4` model loaded (for VLM scoring in Phase 2/4/5/7's layer planning step)
- `VULCA_VLM_MODEL=ollama_chat/gemma4` and `OLLAMA_API_BASE=http://localhost:11434` environment variables set
- Phase 1 gallery artifacts exist in `assets/demo/v3/gallery/` (prerequisite for Phase 6)
- Python with vulca deps available: `/opt/homebrew/opt/python@3.11/bin/python3.11` with `PYTHONPATH=./src`

## Test Plan

**No new automated tests** (continuing the spike convention). Manual verification at implementation time:

1. **Fix 1-3 unit verification:** After each fix, run existing `pytest tests/test_local_provider_e2e.py -x` to confirm no regressions.
2. **Phase 2 smoke:** Run `--phases 2 --provider comfyui` and visually inspect:
   - Does `composite.png` look like a Chinese landscape?
   - Do individual layer PNGs have correct alpha channels?
   - Are log-printed per-layer prompts in English (not CJK)?
3. **Phase 4 smoke:** Run `--phases 4 --provider comfyui` and compare `no_ref/composite.png` vs `with_ref/composite.png` — the with-ref version should show more stylistic consistency across layers.
4. **Phase 5 smoke:** Run `--phases 5 --provider comfyui` (after Phase 2) — `after.png` should visibly differ from `before.png`.
5. **Phase 6 smoke:** Run `--phases 6 --provider comfyui` — `after.png` should have a visible change in the specified region.
6. **Phase 7 smoke:** Run `--phases 7 --provider comfyui` — at least 1 concept + final should exist.
7. **Full suite:** Run `--phases 1,2,3,4,5,6,7,8 --provider comfyui` and verify all 8 phases report `ok`.

## Files Changed

### Core library (~70 lines)
- `src/vulca/layers/layered_prompt.py` — Fix 1: `english_only` parameter (CJK stripping from anchor fields)
- `src/vulca/layers/plan_prompt.py` — Fix 2: English-output instruction in VLM template
- `src/vulca/providers/comfyui.py` — Fix 3: `raw_prompt` kwarg
- `src/vulca/providers/gemini.py` — Fix 1 capability: add `"multilingual_prompt"` to capabilities frozenset
- `src/vulca/layers/layered_generate.py` — Phase 4: `disable_style_ref` parameter (~15 lines bypassing serial-first)
- `src/vulca/pipeline/nodes/layer_generate.py` — Fix 1: pass `english_only` based on provider capabilities
- `src/vulca/inpaint.py` (or `src/vulca/studio/phases/inpaint.py`) — Phase 6: add `provider` parameter threading

### Runner (~150 lines)
- `scripts/generate-e2e-demo.py` — 5 new `run_phaseN_*()` functions + `main_async` dispatch + Fix 4 (Phase 3 migration)

### Artifacts (generated, not hand-written)
- `assets/demo/v3/layered/` — Phase 2 outputs
- `assets/demo/v3/defense3/` — Phase 4 outputs
- `assets/demo/v3/edit/` — Phase 5 outputs
- `assets/demo/v3/inpaint/` — Phase 6 outputs
- `assets/demo/v3/studio/` — Phase 7 outputs

## Estimated Implementation Time

- Core library fixes (Part 1): ~45 min (4 fixes + `ainpaint()` provider param + `disable_style_ref` toggle, each requires reading the existing code carefully)
- Runner wiring (Part 2): ~75 min (5 phases, each ~15 min including the `LayeredArtwork` loading for Phase 5 and the `asyncio.to_thread` wrapping for Phase 7)
- Verification runs (Part 3): ~45 min (wall time dominated by ComfyUI generation, phases run individually)
- Total: ~3-4 hours in one session

## Dependency on External Services

| Service | Required for | Can substitute? |
|---|---|---|
| ComfyUI (local) | Image generation in all phases | Gemini (if billing enabled) |
| Ollama + Gemma 4 (local) | VLM layer planning + evaluation | Gemini VLM (if billing enabled) |
| Gemini API (cloud) | Alternative to local stack | Only if wangjindong enables billing |

The local stack (ComfyUI + Ollama) is the primary target. Gemini compatibility is maintained by not breaking any existing Gemini code paths.
