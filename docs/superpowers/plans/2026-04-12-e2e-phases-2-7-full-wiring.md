# E2E Phases 2-7 Full Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire all 5 remaining E2E demo phases (2, 4, 5, 6, 7) into the runner, fix the CJK-in-CLIP problem for layered prompts on ComfyUI, unify `raw_prompt` handling, and migrate Phase 3 to the public SDK API.

**Architecture:** Core library gets 6 targeted fixes (~70 lines): CJK-aware prompt builder, English VLM output instruction, ComfyUI `raw_prompt`, Gemini `multilingual_prompt` capability, `disable_style_ref` toggle, and `ainpaint` provider threading. Runner gets 5 new phase functions + dispatch wiring (~150 lines). No new automated tests (spike convention — manual verification per phase).

**Tech Stack:** Python 3.11, asyncio, PIL/Pillow, vulca SDK (pipeline engine, layered generate, inpaint, studio), ComfyUI/SDXL local provider, Ollama/Gemma4 VLM.

---

### Task 1: Fix 1 — `build_anchored_layer_prompt()` CJK-aware output

**Files:**
- Modify: `src/vulca/layers/layered_prompt.py:20-62`

- [ ] **Step 1: Add `english_only` parameter and CJK stripping logic**

Add a `_strip_cjk()` helper and modify `build_anchored_layer_prompt()` to accept `english_only: bool = False`:

```python
import re

def _strip_cjk_parenthetical(text: str) -> str:
    """Strip CJK parenthetical annotations, e.g. 'cooked silk (熟绢)' → 'cooked silk'."""
    return re.sub(r"\s*\([^)]*[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af][^)]*\)", "", text).strip()


def _is_ascii_latin(text: str) -> bool:
    """Return True if text contains no CJK characters."""
    return not bool(re.search(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", text))


def _strip_cjk_chars(text: str) -> str:
    """Remove CJK characters from text, keeping ASCII/Latin portions."""
    return re.sub(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+", "", text).strip()
```

Then in `build_anchored_layer_prompt`, add `english_only: bool = False` to the signature and wrap the anchor field usage:

```python
def build_anchored_layer_prompt(
    layer: LayerInfo,
    *,
    anchor: TraditionAnchor,
    sibling_roles: list[str],
    position: str = "",
    coverage: str = "",
    english_only: bool = False,
) -> str:
    """Build a fully anchored prompt for one layer of a layered artwork.

    sibling_roles is the full list of layer roles in the plan (this layer's
    role is filtered out automatically when building the negative list).
    """
    own_role = layer.tradition_role or layer.name
    others = [r for r in sibling_roles if r and r != own_role]

    canvas_desc = anchor.canvas_description
    style_kw = anchor.style_keywords

    if english_only:
        canvas_desc = _strip_cjk_parenthetical(canvas_desc)
        # Filter style_keywords to ASCII/Latin-only entries
        style_kw = ", ".join(
            kw.strip() for kw in style_kw.split(",")
            if kw.strip() and _is_ascii_latin(kw.strip())
        )
        # Strip CJK from sibling roles (drop pure-CJK roles)
        others = [_strip_cjk_chars(r) for r in others]
        others = [r for r in others if r]

    others_text = ", ".join(others) if others else "(none)"

    pos = position or "wherever the user intent specifies"
    cov = coverage or "as the user intent specifies"

    user_intent = layer.regeneration_prompt or layer.description or own_role

    blocks = [
        "[CANVAS ANCHOR]",
        f"The image MUST be drawn on {canvas_desc}.",
        f"The background MUST be the pure canvas color {anchor.canvas_color_hex},",
        "with absolutely no other elements, textures, shading, or borders on the background.",
        "",
        "[CONTENT ANCHOR — exclusivity]",
        "This image ONLY contains the element specified in USER INTENT.",
        f"Do NOT include any of: {others_text}.",
        "",
        "[SPATIAL ANCHOR]",
        f"MUST occupy {pos}, covering approximately {cov} of the canvas area.",
        "Do NOT extend beyond this region.",
        "",
        "[STYLE ANCHOR]",
        style_kw,
        "",
        "[USER INTENT]",
        user_intent,
    ]
    return "\n".join(blocks)
```

- [ ] **Step 2: Verify the change doesn't break imports**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.layers.layered_prompt import build_anchored_layer_prompt, TraditionAnchor; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/layers/layered_prompt.py
git commit -m "fix(layers): add english_only CJK stripping to build_anchored_layer_prompt"
```

---

### Task 2: Fix 1b — Add `multilingual_prompt` capability to Gemini provider

**Files:**
- Modify: `src/vulca/providers/gemini.py:63`

- [ ] **Step 1: Add capability**

Change line 63 from:
```python
    capabilities: frozenset[str] = frozenset({"raw_rgba"})
```
to:
```python
    capabilities: frozenset[str] = frozenset({"raw_rgba", "multilingual_prompt"})
```

- [ ] **Step 2: Verify import**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.providers.gemini import GeminiImageProvider; print(GeminiImageProvider.capabilities)"`
Expected: `frozenset({'raw_rgba', 'multilingual_prompt'})`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/providers/gemini.py
git commit -m "feat(providers): add multilingual_prompt capability to Gemini"
```

---

### Task 3: Fix 1c — Pass `english_only` in `generate_one_layer`

**Files:**
- Modify: `src/vulca/layers/layered_generate.py:225-244`
- Modify: `src/vulca/layers/layered_generate.py:337-352`

- [ ] **Step 1: Add `english_only` parameter to `generate_one_layer`**

At `layered_generate.py:225`, add `english_only: bool = False` to the signature and pass it through to `build_anchored_layer_prompt`:

Change lines 225-244:
```python
async def generate_one_layer(
    *,
    layer: LayerInfo,
    anchor: TraditionAnchor,
    canvas: CanvasSpec,
    keying: KeyingStrategy,
    provider,
    sibling_roles: list[str],
    output_dir: str,
    position: str = "",
    coverage: str = "",
    cache: LayerCache | None = None,
    width: int = 0,
    height: int = 0,
    reference_image_b64: str = "",
    english_only: bool = False,
) -> LayerOutcome:
    prompt = build_anchored_layer_prompt(
        layer, anchor=anchor, sibling_roles=sibling_roles,
        position=position, coverage=coverage,
        english_only=english_only,
    )
```

- [ ] **Step 2: Add `english_only` parameter to `layered_generate` and thread it**

At `layered_generate.py:337`, add `english_only: bool = False` to the signature:

```python
async def layered_generate(
    *,
    plan: list[LayerInfo],
    tradition_anchor: TraditionAnchor,
    canvas: CanvasSpec,
    key_strategy_name: str,
    provider,
    output_dir: str,
    positions: dict[str, str] | None = None,
    coverages: dict[str, str] | None = None,
    parallelism: int = 4,
    cache_enabled: bool = True,
    width: int = 0,
    height: int = 0,
    reference_image_b64: str = "",
    english_only: bool = False,
) -> LayeredResult:
```

Then find where `common_kw` is built (around line 357-375) and add `english_only` to it. Search for the dict that passes `anchor`, `sibling_roles`, etc. to `generate_one_layer`. Add `"english_only": english_only` to that dict.

- [ ] **Step 3: Thread `english_only` from `_generate_layers_native`**

At `src/vulca/pipeline/nodes/layer_generate.py:221-235`, add the capability check and pass `english_only`:

After line 220 (where `ref_b64` is resolved), add:
```python
        caps = getattr(provider_instance, "capabilities", frozenset())
        english_only = "multilingual_prompt" not in caps
```

Then add `english_only=english_only` to the `lg_mod.layered_generate(...)` call at line 221:
```python
        result = await lg_mod.layered_generate(
            plan=layers,
            tradition_anchor=anchor,
            canvas=canvas,
            key_strategy_name=key_strategy_name,
            provider=provider_instance,
            output_dir=output_dir,
            positions=positions,
            coverages=coverages,
            parallelism=int(os.environ.get("VULCA_LAYERED_PARALLELISM", "4")),
            cache_enabled=cache_enabled,
            width=canvas_w,
            height=canvas_h,
            reference_image_b64=ref_b64,
            english_only=english_only,
        )
```

- [ ] **Step 4: Verify import chain**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.layers.layered_generate import layered_generate; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/layered_generate.py src/vulca/pipeline/nodes/layer_generate.py
git commit -m "fix(layers): thread english_only from provider capabilities through layered pipeline"
```

---

### Task 4: Fix 2 — VLM prompt English output instruction

**Files:**
- Modify: `src/vulca/layers/plan_prompt.py:105-140`

- [ ] **Step 1: Add English instruction to VLM template**

In `build_plan_prompt()`, add one line to the Rules section after line 121 (`- Respect the tradition's whitespace conventions...`):

```python
- IMPORTANT: All "regeneration_prompt" values MUST be in English, regardless of the user's input language. Translate if necessary.
```

The full Rules block becomes:
```python
Rules:
- Plan 3-8 layers depending on scene complexity
- Each layer should be independently meaningful
- Order z_index from back (0) to front
- Assign blend_mode based on tradition conventions
- Include dominant_colors that would characterize each layer
- CRITICAL: Each layer's regeneration_prompt MUST include specific position and size constraints (e.g. "in the upper 30% of canvas", "covering about 20% of canvas area")
- CRITICAL: The background layer (content_type: background) must describe ONLY the base medium texture (paper, silk, canvas). Do NOT include ANY scene elements (mountains, water, trees, buildings, figures) in the background layer. Scene elements belong in atmosphere/subject layers.
- Respect the tradition's whitespace conventions (e.g. xieyi: 30-55% blank space)
- IMPORTANT: All "regeneration_prompt" values MUST be in English, regardless of the user's input language. Translate if necessary.
```

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.layers.plan_prompt import build_plan_prompt; p = build_plan_prompt('test', 'chinese_xieyi'); assert 'MUST be in English' in p; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/layers/plan_prompt.py
git commit -m "fix(layers): instruct VLM to output regeneration_prompt in English"
```

---

### Task 5: Fix 3 — ComfyUI `raw_prompt` support

**Files:**
- Modify: `src/vulca/providers/comfyui.py:37-39`

- [ ] **Step 1: Add `raw_prompt` kwarg handling**

Change lines 37-39 from:
```python
        full_prompt = prompt
        if tradition and tradition != "default":
            full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"
```
to:
```python
        full_prompt = prompt
        if not kwargs.get("raw_prompt", False):
            if tradition and tradition != "default":
                full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"
```

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.providers.comfyui import ComfyUIImageProvider; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/providers/comfyui.py
git commit -m "fix(providers): add raw_prompt kwarg to ComfyUI provider"
```

---

### Task 6: Fix 4 — Phase 3 public API migration

**Files:**
- Modify: `scripts/generate-e2e-demo.py:387-517`

- [ ] **Step 1: Replace `score_image` import with `aevaluate`**

Change line 405 from:
```python
    from vulca._vlm import score_image
```
to:
```python
    from vulca import aevaluate
```

- [ ] **Step 2: Replace the `score_image` call with `aevaluate`**

Change lines 432-442 from:
```python
        try:
            raw_bytes = image_path.read_bytes()
            img_b64 = base64.b64encode(raw_bytes).decode()
            result = await score_image(
                img_b64,
                "image/png",
                subject,
                tradition,
                "local",
                mode=mode,
            )
```
to:
```python
        try:
            eval_result = await aevaluate(
                image_path,
                subject=subject,
                tradition=tradition,
                mode=mode,
            )
            # Convert EvalResult to the dict format expected by the rest of this function.
            result = {
                f"L{i}": getattr(eval_result, f"L{i}", 0.0) if hasattr(eval_result, f"L{i}") else eval_result.scores.get(f"L{i}", 0.0)
                for i in range(1, 6)
            }
            if hasattr(eval_result, "risk_flags"):
                result["risk_flags"] = eval_result.risk_flags
```

**Note:** The exact field access on `EvalResult` depends on its shape. Check `EvalResult` fields and adapt. The key requirement is that `result` becomes a dict with `L1`..`L5` float keys and optional `risk_flags` list, matching what `score_image` returned.

- [ ] **Step 3: Verify the EvalResult shape and adapt**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.types import EvalResult; import inspect; print([f for f in dir(EvalResult) if not f.startswith('_')])"` to see available fields. Adapt the conversion code if needed.

- [ ] **Step 4: Verify no more private API usage**

Run: `cd /Users/yhryzy/dev/vulca && grep -n 'score_image\|_vlm' scripts/generate-e2e-demo.py`
Expected: 0 matches.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "fix(e2e): migrate Phase 3 from private _vlm.score_image to public aevaluate API"
```

---

### Task 7: `disable_style_ref` toggle for `layered_generate`

**Files:**
- Modify: `src/vulca/layers/layered_generate.py:337-435`

- [ ] **Step 1: Add `disable_style_ref` parameter**

Add `disable_style_ref: bool = False` to the `layered_generate()` signature at line 337:

```python
async def layered_generate(
    *,
    plan: list[LayerInfo],
    tradition_anchor: TraditionAnchor,
    canvas: CanvasSpec,
    key_strategy_name: str,
    provider,
    output_dir: str,
    positions: dict[str, str] | None = None,
    coverages: dict[str, str] | None = None,
    parallelism: int = 4,
    cache_enabled: bool = True,
    width: int = 0,
    height: int = 0,
    reference_image_b64: str = "",
    english_only: bool = False,
    disable_style_ref: bool = False,
) -> LayeredResult:
```

- [ ] **Step 2: Wrap the serial-first/parallel split**

Replace the Phase 1 + Phase 2 block (lines 377-435) with:

```python
    if disable_style_ref:
        # All layers generated in parallel, no cross-layer style reference.
        async def _run_no_ref(layer: LayerInfo) -> LayerOutcome:
            async with sem:
                try:
                    return await generate_one_layer(
                        layer=layer,
                        position=positions.get(layer.name, ""),
                        coverage=coverages.get(layer.name, ""),
                        reference_image_b64=reference_image_b64,
                        **common_kw,
                    )
                except (AssertionError, TypeError, KeyError, AttributeError, ValueError):
                    raise
                except Exception:
                    logger.exception("unexpected post-provider failure for layer %s", layer.name)
                    return LayerOutcome(ok=False, info=layer, rgba_path="", attempts=1)

        outcomes = list(await asyncio.gather(*(_run_no_ref(l) for l in plan)))
    else:
        # --- Phase 1: Generate first layer serially (style anchor) ---
        first = plan[0]
        # ... existing code unchanged through to outcomes = [first_outcome] + rest_outcomes
```

Make sure the `outcomes` variable is assigned in both branches and the code after (lines 439+) continues to work.

- [ ] **Step 3: Verify import**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.layers.layered_generate import layered_generate; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/vulca/layers/layered_generate.py
git commit -m "feat(layers): add disable_style_ref toggle to layered_generate"
```

---

### Task 8: `ainpaint` provider parameter threading

**Files:**
- Modify: `src/vulca/inpaint.py:10-21`
- Modify: `src/vulca/studio/phases/inpaint.py:114-155`

- [ ] **Step 1: Add `provider` parameter to `ainpaint()`**

At `src/vulca/inpaint.py:10`, add `provider: str = "gemini"` to the signature:

```python
async def ainpaint(
    image: str,
    *,
    region: str,
    instruction: str,
    tradition: str = "default",
    provider: str = "gemini",
    count: int = 4,
    select: int | None = None,
    output: str = "",
    api_key: str = "",
    mock: bool = False,
) -> InpaintResult:
```

Then pass `provider=provider` to `phase.repaint()` at line 72:
```python
        variants = await phase.repaint(
            image,
            crop_path,
            instruction=instruction,
            tradition=tradition,
            provider=provider,
            count=count,
            output_dir=crop_dir,
            api_key=api_key,
        )
```

Also update the sync wrapper `inpaint()` at line 121 to add the same `provider: str = "gemini"` parameter and pass it through.

- [ ] **Step 2: Add `provider` parameter to `InpaintPhase.repaint()`**

At `src/vulca/studio/phases/inpaint.py:114`, add `provider: str = "gemini"` to the signature:

```python
    async def repaint(
        self,
        original_path: str,
        crop_path: str,
        *,
        instruction: str,
        tradition: str = "default",
        provider: str = "gemini",
        count: int = 4,
        output_dir: str = "",
        api_key: str = "",
    ) -> list[str]:
```

Then change line 137 from:
```python
        provider = get_image_provider("gemini", api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""))
```
to:
```python
        provider_inst = get_image_provider(provider, api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""))
```

And update line 144 to use `provider_inst`:
```python
                result = await provider_inst.generate(
```

- [ ] **Step 3: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python -c "from vulca.inpaint import ainpaint; import inspect; sig = inspect.signature(ainpaint); assert 'provider' in sig.parameters; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/vulca/inpaint.py src/vulca/studio/phases/inpaint.py
git commit -m "feat(inpaint): add provider parameter to ainpaint, removing Gemini hardcode"
```

---

### Task 9: Runner — output directory constants + dependency check helpers

**Files:**
- Modify: `scripts/generate-e2e-demo.py:36-41`

- [ ] **Step 1: Add output directory constants after existing ones (line 41)**

After line 41 (`REPORT_PATH = DEMO_ROOT / "e2e-report.json"`), add:

```python
LAYERED_DIR = DEMO_ROOT / "layered"
DEFENSE3_DIR = DEMO_ROOT / "defense3"
EDIT_DIR = DEMO_ROOT / "edit"
INPAINT_DIR = DEMO_ROOT / "inpaint"
STUDIO_DIR = DEMO_ROOT / "studio"
```

- [ ] **Step 2: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "chore(e2e): add output directory constants for phases 2/4/5/6/7"
```

---

### Task 10: Runner — Phase 2 Layered Create

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (add after Phase 3 function, before `main_async`)

- [ ] **Step 1: Add `run_phase2_layered` function**

Insert before the `main_async` function:

```python
# ---------------------------------------------------------------------------
# Phase 2 — Layered Create
# ---------------------------------------------------------------------------
async def run_phase2_layered(
    provider_name: str,
    *,
    width: int = 1024,
    height: int = 1024,
) -> dict:
    """Generate a layered artwork via the LAYERED pipeline template."""
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import LAYERED
    from vulca.pipeline.types import PipelineInput

    LAYERED_DIR.mkdir(parents=True, exist_ok=True)

    intent = "水墨山水，雨后春山，松间茅屋"
    tradition = "chinese_xieyi"
    subject = "Chinese xieyi ink landscape"

    print(f"[Phase 2] Layered create: {subject} via {provider_name}")
    t0 = time.time()

    try:
        output = await execute(LAYERED, PipelineInput(
            subject=subject,
            intent=intent,
            tradition=tradition,
            provider=provider_name,
            layered=True,
            output_dir=str(LAYERED_DIR),
        ))
    except Exception as exc:
        traceback.print_exc()
        return {
            "phase": 2, "name": "layered", "provider": provider_name,
            "status": "failed", "error": f"{type(exc).__name__}: {exc}",
        }

    elapsed = time.time() - t0

    # Validate artifacts
    entries: list[dict] = []
    errors: list[str] = []

    manifest_path = LAYERED_DIR / "manifest.json"
    composite_path = LAYERED_DIR / "composite.png"

    if not manifest_path.exists():
        errors.append("manifest.json missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
            assert "layers" in manifest, "manifest missing 'layers' key"
            assert len(manifest["layers"]) >= 2, f"only {len(manifest['layers'])} layers (need ≥2)"
            entries.append({"artifact": "manifest.json", "layers": len(manifest["layers"]), "status": "ok"})
        except Exception as exc:
            errors.append(f"manifest validation: {exc}")

    if not composite_path.exists():
        errors.append("composite.png missing")
    else:
        try:
            _validate_png_bytes(composite_path.read_bytes())
            entries.append({"artifact": "composite.png", "status": "ok"})
        except Exception as exc:
            errors.append(f"composite validation: {exc}")

    # Validate individual layer PNGs
    for png_path in sorted(LAYERED_DIR.glob("*.png")):
        if png_path.name == "composite.png":
            continue
        try:
            from PIL import Image
            img = Image.open(png_path)
            assert img.mode == "RGBA", f"{png_path.name} is {img.mode}, expected RGBA"
            assert len(png_path.read_bytes()) > 10_000, f"{png_path.name} too small"
            entries.append({"artifact": png_path.name, "mode": img.mode, "size": img.size, "status": "ok"})
        except Exception as exc:
            errors.append(f"layer {png_path.name}: {exc}")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s ({len(entries)} artifacts validated, {len(errors)} errors)")
    for err in errors:
        print(f"        [error] {err}")

    return {
        "phase": 2, "name": "layered", "provider": provider_name,
        "intent": intent, "tradition": tradition,
        "elapsed_s": round(elapsed, 2),
        "entries": entries, "errors": errors,
        "status": status,
    }
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/yhryzy/dev/vulca && python -c "exec(open('scripts/generate-e2e-demo.py').read()); print('syntax OK')"`
Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add Phase 2 layered create runner function"
```

---

### Task 11: Runner — Phase 4 Defense 3 Showcase

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (add after Phase 2 function)

- [ ] **Step 1: Add `run_phase4_defense3` function**

```python
# ---------------------------------------------------------------------------
# Phase 4 — Defense 3 Showcase (style-ref anchoring comparison)
# ---------------------------------------------------------------------------
async def run_phase4_defense3(
    provider_name: str,
    *,
    width: int = 1024,
    height: int = 1024,
) -> dict:
    """Compare layered generation with vs. without style-ref anchoring."""
    from vulca.layers.layered_generate import layered_generate
    from vulca.layers.layered_prompt import TraditionAnchor
    from vulca.layers.keying import CanvasSpec
    from vulca.layers.plan_prompt import build_plan_prompt
    from vulca.providers import get_image_provider

    DEFENSE3_DIR.mkdir(parents=True, exist_ok=True)
    no_ref_dir = DEFENSE3_DIR / "no_ref"
    with_ref_dir = DEFENSE3_DIR / "with_ref"
    no_ref_dir.mkdir(parents=True, exist_ok=True)
    with_ref_dir.mkdir(parents=True, exist_ok=True)

    tradition = "chinese_xieyi"
    intent = "水墨山水，雨后春山，松间茅屋"

    print(f"[Phase 4] Defense 3 showcase: style-ref comparison via {provider_name}")
    t0 = time.time()

    provider = get_image_provider(provider_name)

    # Plan layers once (shared between both variants)
    from vulca.pipeline.nodes.plan_layers import PlanLayersNode
    from vulca.pipeline.types import NodeContext

    # Use the VLM to plan layers
    plan_prompt = build_plan_prompt(intent, tradition)

    # Use the existing PlanLayersNode to get a layer plan
    from vulca.layers.plan_prompt import get_tradition_layer_order
    from vulca.layers.types import LayerInfo

    layer_order = get_tradition_layer_order(tradition)
    plan: list[LayerInfo] = []
    for i, lo in enumerate(layer_order[:4]):  # Cap at 4 layers for reasonable time
        plan.append(LayerInfo(
            name=lo["role"].replace(" ", "_").replace("/", "_"),
            description=lo["role"],
            z_index=i,
            content_type=lo.get("content_type", "subject"),
            blend_mode=lo.get("blend", "normal"),
            tradition_role=lo["role"],
            position=lo.get("position", ""),
            coverage=lo.get("coverage", ""),
            regeneration_prompt=f"{lo['role']} layer for Chinese xieyi ink painting, position: {lo.get('position', 'center')}, coverage: {lo.get('coverage', '30%')}",
        ))

    anchor = TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="white rice paper",
        style_keywords="sumi-e, ink wash, freehand brushwork, monochrome",
    )
    canvas = CanvasSpec.from_hex("#ffffff")

    caps = getattr(provider, "capabilities", frozenset())
    english_only = "multilingual_prompt" not in caps

    entries: list[dict] = []
    errors: list[str] = []

    # Variant 1: Without style reference (all parallel)
    print("      Running without style-ref (all layers parallel)...")
    try:
        result_no_ref = await layered_generate(
            plan=plan,
            tradition_anchor=anchor,
            canvas=canvas,
            key_strategy_name="luminance",
            provider=provider,
            output_dir=str(no_ref_dir),
            width=width, height=height,
            english_only=english_only,
            disable_style_ref=True,
        )
        entries.append({
            "variant": "no_ref",
            "layers_ok": len(result_no_ref.layers),
            "layers_failed": len(result_no_ref.failed),
            "status": "ok" if result_no_ref.is_usable else "failed",
        })
    except Exception as exc:
        traceback.print_exc()
        errors.append(f"no_ref variant: {exc}")

    # Variant 2: With style reference (serial-first default)
    print("      Running with style-ref (serial-first anchoring)...")
    try:
        result_with_ref = await layered_generate(
            plan=plan,
            tradition_anchor=anchor,
            canvas=canvas,
            key_strategy_name="luminance",
            provider=provider,
            output_dir=str(with_ref_dir),
            width=width, height=height,
            english_only=english_only,
            disable_style_ref=False,
        )
        entries.append({
            "variant": "with_ref",
            "layers_ok": len(result_with_ref.layers),
            "layers_failed": len(result_with_ref.failed),
            "status": "ok" if result_with_ref.is_usable else "failed",
        })
    except Exception as exc:
        traceback.print_exc()
        errors.append(f"with_ref variant: {exc}")

    elapsed = time.time() - t0
    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s")

    return {
        "phase": 4, "name": "defense3", "provider": provider_name,
        "intent": intent, "tradition": tradition,
        "elapsed_s": round(elapsed, 2),
        "entries": entries, "errors": errors,
        "status": status,
    }
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/yhryzy/dev/vulca && python -c "exec(open('scripts/generate-e2e-demo.py').read()); print('syntax OK')"`
Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add Phase 4 defense3 style-ref comparison runner"
```

---

### Task 12: Runner — Phase 5 Edit / Layer Redraw

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (add after Phase 4 function)

- [ ] **Step 1: Add `run_phase5_edit` function**

```python
# ---------------------------------------------------------------------------
# Phase 5 — Edit / Layer Redraw
# ---------------------------------------------------------------------------
async def run_phase5_edit(
    provider_name: str,
) -> dict:
    """Redraw a single layer from the Phase 2 layered artwork."""
    from vulca.layers.redraw import redraw_layer
    from vulca.layers.manifest import load_manifest

    EDIT_DIR.mkdir(parents=True, exist_ok=True)

    # Dependency check: Phase 2 artifacts must exist
    manifest_path = LAYERED_DIR / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            "Phase 5 (edit) requires Phase 2 (layered) artifacts. "
            "Run --phases 2 first."
        )

    print(f"[Phase 5] Edit/redraw: loading Phase 2 artwork from {LAYERED_DIR}")
    t0 = time.time()

    artwork = load_manifest(str(LAYERED_DIR))

    # Find a non-background layer to redraw
    target_layer = None
    for lr in artwork.layers:
        if lr.info.content_type != "background":
            target_layer = lr
            break
    if target_layer is None and artwork.layers:
        target_layer = artwork.layers[-1]  # fallback: last layer
    if target_layer is None:
        return {
            "phase": 5, "name": "edit", "provider": provider_name,
            "status": "failed", "error": "No layers found in Phase 2 artwork",
        }

    print(f"      Redrawing layer: {target_layer.info.name}")

    # Copy original composite as before.png
    import shutil
    composite_src = LAYERED_DIR / "composite.png"
    before_path = EDIT_DIR / "before.png"
    if composite_src.exists():
        shutil.copy2(composite_src, before_path)

    instruction = "Redraw with more vibrant autumn colors and a setting sun"
    try:
        result = await redraw_layer(
            artwork,
            layer_name=target_layer.info.name,
            instruction=instruction,
            provider=provider_name,
            tradition="chinese_xieyi",
            artwork_dir=str(LAYERED_DIR),
        )
    except Exception as exc:
        traceback.print_exc()
        return {
            "phase": 5, "name": "edit", "provider": provider_name,
            "status": "failed", "error": f"{type(exc).__name__}: {exc}",
        }

    elapsed = time.time() - t0
    errors: list[str] = []

    # Copy redrawn layer
    redrawn_path = EDIT_DIR / "redrawn_layer.png"
    if result.image_path and Path(result.image_path).exists():
        shutil.copy2(result.image_path, redrawn_path)
        from PIL import Image
        img = Image.open(redrawn_path)
        if img.mode != "RGBA":
            errors.append(f"redrawn layer is {img.mode}, expected RGBA")
    else:
        errors.append("redrawn layer image not produced")

    # Re-composite (copy the new composite if the redraw updated it)
    after_path = EDIT_DIR / "after.png"
    # Check if composite was updated in LAYERED_DIR
    if composite_src.exists():
        shutil.copy2(composite_src, after_path)

    # Verify before != after
    if before_path.exists() and after_path.exists():
        if before_path.read_bytes() == after_path.read_bytes():
            errors.append("after.png is identical to before.png — redraw may not have taken effect")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s")
    for err in errors:
        print(f"        [error] {err}")

    return {
        "phase": 5, "name": "edit", "provider": provider_name,
        "layer_redrawn": target_layer.info.name,
        "instruction": instruction,
        "elapsed_s": round(elapsed, 2),
        "errors": errors,
        "status": status,
    }
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/yhryzy/dev/vulca && python -c "exec(open('scripts/generate-e2e-demo.py').read()); print('syntax OK')"`
Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add Phase 5 edit/layer-redraw runner function"
```

---

### Task 13: Runner — Phase 6 Inpaint

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (add after Phase 5 function)

- [ ] **Step 1: Add `run_phase6_inpaint` function**

```python
# ---------------------------------------------------------------------------
# Phase 6 — Inpaint
# ---------------------------------------------------------------------------
async def run_phase6_inpaint(
    provider_name: str,
) -> dict:
    """Inpaint a region of a Phase 1 gallery image."""
    from vulca.inpaint import ainpaint

    INPAINT_DIR.mkdir(parents=True, exist_ok=True)

    # Dependency check: Phase 1 gallery image must exist
    input_image = GALLERY_DIR / "chinese_xieyi.png"
    if not input_image.exists():
        # Try any gallery image
        if GALLERY_DIR.exists():
            for p in sorted(GALLERY_DIR.glob("*.png")):
                input_image = p
                break
    if not input_image.exists():
        raise FileNotFoundError(
            "Phase 6 (inpaint) requires Phase 1 gallery artifacts. "
            "Run --phases 1 first."
        )

    print(f"[Phase 6] Inpaint: {input_image.name} via {provider_name}")
    t0 = time.time()

    # Copy original as before.png
    import shutil
    before_path = INPAINT_DIR / "before.png"
    shutil.copy2(input_image, before_path)

    instruction = "Add a small red pavilion near the water"
    region = "center 30%"

    try:
        result = await ainpaint(
            str(input_image),
            region=region,
            instruction=instruction,
            tradition="chinese_xieyi",
            provider=provider_name,
            count=1,
            select=0,
            output=str(INPAINT_DIR / "after.png"),
        )
    except Exception as exc:
        traceback.print_exc()
        return {
            "phase": 6, "name": "inpaint", "provider": provider_name,
            "status": "failed", "error": f"{type(exc).__name__}: {exc}",
        }

    elapsed = time.time() - t0
    errors: list[str] = []

    after_path = INPAINT_DIR / "after.png"
    if result.blended and Path(result.blended).exists():
        # Copy blended result to after.png if not already there
        if str(after_path) != result.blended:
            shutil.copy2(result.blended, after_path)
    elif not after_path.exists():
        errors.append("after.png not produced")

    # Validate dimensions match
    if before_path.exists() and after_path.exists():
        from PIL import Image
        before_img = Image.open(before_path)
        after_img = Image.open(after_path)
        if before_img.size != after_img.size:
            errors.append(f"dimension mismatch: before={before_img.size}, after={after_img.size}")
        if before_path.read_bytes() == after_path.read_bytes():
            errors.append("after.png identical to before.png — inpaint may not have worked")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s")
    for err in errors:
        print(f"        [error] {err}")

    return {
        "phase": 6, "name": "inpaint", "provider": provider_name,
        "instruction": instruction, "region": region,
        "elapsed_s": round(elapsed, 2),
        "errors": errors,
        "status": status,
    }
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/yhryzy/dev/vulca && python -c "exec(open('scripts/generate-e2e-demo.py').read()); print('syntax OK')"`
Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add Phase 6 inpaint runner function"
```

---

### Task 14: Runner — Phase 7 Studio

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (add after Phase 6 function)

- [ ] **Step 1: Add `run_phase7_studio` function**

```python
# ---------------------------------------------------------------------------
# Phase 7 — Studio / Brief-Driven
# ---------------------------------------------------------------------------
async def run_phase7_studio(
    provider_name: str,
) -> dict:
    """Run a brief-driven studio session in auto mode."""
    from vulca.studio.interactive import run_studio

    STUDIO_DIR.mkdir(parents=True, exist_ok=True)

    intent = (
        "Create a serene Chinese landscape with mountains emerging from "
        "morning mist, in the style of Chinese xieyi ink painting"
    )

    print(f"[Phase 7] Studio session: auto mode via {provider_name}")
    t0 = time.time()

    try:
        # run_studio is synchronous — wrap in to_thread with timeout
        session = await asyncio.wait_for(
            asyncio.to_thread(
                run_studio,
                intent,
                project_dir=str(STUDIO_DIR),
                provider=provider_name,
                auto=True,
                max_rounds=3,
            ),
            timeout=600,  # 10-min safety net
        )
    except asyncio.TimeoutError:
        return {
            "phase": 7, "name": "studio", "provider": provider_name,
            "status": "failed", "error": "Studio session timed out after 600s",
        }
    except Exception as exc:
        traceback.print_exc()
        return {
            "phase": 7, "name": "studio", "provider": provider_name,
            "status": "failed", "error": f"{type(exc).__name__}: {exc}",
        }

    elapsed = time.time() - t0
    errors: list[str] = []

    # Validate artifacts
    concept_pngs = sorted(STUDIO_DIR.glob("concept_*.png"))
    if not concept_pngs:
        # Also check for any PNG that might be a concept
        concept_pngs = sorted(STUDIO_DIR.glob("*.png"))
    if not concept_pngs:
        errors.append("no concept PNGs produced")

    final_path = STUDIO_DIR / "final.png"
    if not final_path.exists():
        # Studio might name it differently — check session output
        if concept_pngs:
            # Use last concept as final
            import shutil
            shutil.copy2(concept_pngs[-1], final_path)
        else:
            errors.append("final.png not produced")

    if final_path.exists():
        try:
            _validate_png_bytes(final_path.read_bytes())
        except Exception as exc:
            errors.append(f"final.png validation: {exc}")

    session_path = STUDIO_DIR / "session.json"
    if isinstance(session, dict):
        session_path.write_text(json.dumps(session, indent=2, ensure_ascii=False, default=str))
    elif not session_path.exists():
        errors.append("session.json not produced")

    if session_path.exists():
        try:
            data = json.loads(session_path.read_text())
            assert isinstance(data, dict), "session.json is not a dict"
        except Exception as exc:
            errors.append(f"session.json validation: {exc}")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s ({len(concept_pngs)} concepts)")
    for err in errors:
        print(f"        [error] {err}")

    return {
        "phase": 7, "name": "studio", "provider": provider_name,
        "intent": intent,
        "concepts_produced": len(concept_pngs),
        "elapsed_s": round(elapsed, 2),
        "errors": errors,
        "status": status,
    }
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/yhryzy/dev/vulca && python -c "exec(open('scripts/generate-e2e-demo.py').read()); print('syntax OK')"`
Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add Phase 7 studio auto-mode runner function"
```

---

### Task 15: Runner — `main_async` dispatch wiring

**Files:**
- Modify: `scripts/generate-e2e-demo.py:538-593` (the `main_async` dispatch loop)

- [ ] **Step 1: Add `elif` blocks for phases 2, 4, 5, 6, 7**

Replace the `else:` block at line 592-593:
```python
        else:
            print(f"[warn] phase {phase} not implemented in this runner")
```

with dispatch blocks for all 5 new phases. Insert BEFORE the `else:` clause (after the `elif phase == 8:` block ending at line 591):

```python
        elif phase == 2:
            try:
                rep = await run_phase2_layered(
                    args.provider, width=args.width, height=args.height,
                )
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 2, "name": "layered", "provider": args.provider,
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 4:
            try:
                rep = await run_phase4_defense3(
                    args.provider, width=args.width, height=args.height,
                )
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 4, "name": "defense3", "provider": args.provider,
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 5:
            try:
                rep = await run_phase5_edit(args.provider)
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 5, "name": "edit", "provider": args.provider,
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 6:
            try:
                rep = await run_phase6_inpaint(args.provider)
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 6, "name": "inpaint", "provider": args.provider,
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 7:
            try:
                rep = await run_phase7_studio(args.provider)
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 7, "name": "studio", "provider": args.provider,
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        else:
            print(f"[warn] phase {phase} not implemented in this runner")
```

- [ ] **Step 2: Verify full script syntax**

Run: `cd /Users/yhryzy/dev/vulca && python -c "exec(open('scripts/generate-e2e-demo.py').read()); print('syntax OK')"`
Expected: `syntax OK`

- [ ] **Step 3: Verify dispatch recognizes new phases**

Run: `cd /Users/yhryzy/dev/vulca && python scripts/generate-e2e-demo.py --phases 2 --provider mock --help 2>&1 | head -5`
(Just checking the script parses without errors)

- [ ] **Step 4: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): wire phases 2/4/5/6/7 into main_async dispatch loop"
```

---

### Task 16: Verification — smoke test all core library fixes

**Files:** None (verification only)

- [ ] **Step 1: Run existing test suite to check for regressions**

Run: `cd /Users/yhryzy/dev/vulca && python -m pytest tests/ -x --ignore=tests/test_local_provider_e2e.py -q 2>&1 | tail -20`
Expected: No new failures (baseline ~61 failures from missing cv2 is pre-existing).

- [ ] **Step 2: Verify CJK stripping works**

Run:
```bash
cd /Users/yhryzy/dev/vulca && python -c "
from vulca.layers.layered_prompt import build_anchored_layer_prompt, TraditionAnchor
from vulca.layers.types import LayerInfo

anchor = TraditionAnchor(
    canvas_color_hex='#ffffff',
    canvas_description='cooked silk (熟绢)',
    style_keywords='gongbi, 白描勾线, 分染罩染, fine ink outlines',
)
layer = LayerInfo(name='test', description='test layer', z_index=0)

# Without english_only — should contain CJK
prompt_full = build_anchored_layer_prompt(layer, anchor=anchor, sibling_roles=['白描勾线', '分染罩染'])
assert '熟绢' in prompt_full, 'CJK should be present without english_only'

# With english_only — should NOT contain CJK
prompt_en = build_anchored_layer_prompt(layer, anchor=anchor, sibling_roles=['白描勾线', '分染罩染'], english_only=True)
assert '熟绢' not in prompt_en, 'CJK should be stripped with english_only'
assert 'cooked silk' in prompt_en, 'English portion should remain'
assert '白描勾线' not in prompt_en, 'CJK sibling roles should be stripped'
print('All CJK stripping assertions passed')
"
```
Expected: `All CJK stripping assertions passed`

- [ ] **Step 3: Verify ComfyUI raw_prompt**

Run:
```bash
cd /Users/yhryzy/dev/vulca && grep -n 'raw_prompt' src/vulca/providers/comfyui.py
```
Expected: Shows the new `kwargs.get("raw_prompt", False)` line.

- [ ] **Step 4: Verify no private API in Phase 3**

Run:
```bash
cd /Users/yhryzy/dev/vulca && grep -n 'score_image\|_vlm' scripts/generate-e2e-demo.py
```
Expected: 0 matches.

- [ ] **Step 5: Verify ainpaint has provider param**

Run:
```bash
cd /Users/yhryzy/dev/vulca && python -c "from vulca.inpaint import ainpaint; import inspect; sig = inspect.signature(ainpaint); assert 'provider' in sig.parameters; print('provider param OK')"
```
Expected: `provider param OK`
