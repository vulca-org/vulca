# Phase 1: Agent-Native Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Vulca from "self-driving pipeline" to "agent's hands + eyes" — expose atomic MCP tools, delete brain/UI code that competes with the calling agent.

**Architecture:** Three passes: (1) delete dead code and brain conflicts to shrink surface area, (2) strip human-UI parameters so all tools return structured JSON, (3) add missing agent-native MCP tools (`view_image`, `generate_image`, `layers_list`). The pipeline engine stays for `create_artwork` backward compat but loses its decide loop — agent calls generate→evaluate→decide itself.

**Tech Stack:** Python 3.10+, FastMCP, pytest, litellm, Pillow

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| Delete | `src/vulca/pipeline/residuals.py` | AgentResiduals (128 lines, 0 production value) |
| Delete | `src/vulca/scoring/sparse.py` | BriefIndexer + DimensionActivation |
| Delete | `src/vulca/cultural/engram.py` | CulturalEngram hash-indexed retrieval |
| Delete | `src/vulca/scoring/model_router.py` | ModelRouter dead routing |
| Delete | `src/vulca/pipeline/parallel.py` | explore_parallel dead code |
| Delete | `tests/test_agent_residuals.py` | Tests for deleted AgentResiduals |
| Delete | `tests/test_sparse_eval.py` | Tests for deleted BriefIndexer |
| Delete | `tests/test_cultural_engram.py` | Tests for deleted CulturalEngram |
| Delete | `tests/test_scoring.py` | Tests for deleted ModelRouter |
| Delete | `tests/test_parallel_agents.py` | Tests for deleted explore_parallel |
| Delete | `tests/test_vlm_integration.py` | Tests for deleted sparse+engram integration |
| Modify | `src/vulca/pipeline/engine.py` | Remove residuals, sparse_eval, execute_stream |
| Modify | `src/vulca/pipeline/__init__.py` | Remove deleted re-exports |
| Modify | `src/vulca/scoring/__init__.py` | Remove deleted re-exports |
| Modify | `src/vulca/cultural/__init__.py` | Remove engram re-exports |
| Modify | `src/vulca/pipeline/nodes/evaluate.py` | Remove sparse_eval + engram code paths |
| Modify | `src/vulca/pipeline/nodes/decide.py` | Simplify: remove residual_context injection |
| Modify | `src/vulca/pipeline/types.py` | Remove `residuals`, `sparse_eval` from PipelineInput |
| Modify | `src/vulca/create.py` | Remove `residuals`, `sparse_eval` params |
| Modify | `src/vulca/evaluate.py` | Remove BriefIndexer import |
| Modify | `src/vulca/intent/agent.py` | Remove MODELS import from model_router |
| Modify | `src/vulca/mcp_server.py` | Strip view/format, add generate_image/view_image/layers_list, update descriptions |
| Modify | `src/vulca/layers/plan_prompt.py` | Move tradition layer order data to get_tradition_guide; deprecate build_plan_prompt |

---

### Task 1: Delete AgentResiduals + all references

**Files:**
- Delete: `src/vulca/pipeline/residuals.py`
- Delete: `tests/test_agent_residuals.py`
- Modify: `src/vulca/pipeline/engine.py:16-18,279,391-401,453-454,605`
- Modify: `src/vulca/pipeline/__init__.py:7`
- Modify: `src/vulca/pipeline/types.py` (remove `residuals` field from PipelineInput)
- Modify: `src/vulca/create.py:26` (remove `residuals` param)

- [ ] **Step 1: Run baseline tests**

```bash
pytest tests/test_agent_residuals.py tests/vulca/pipeline/ -x -q 2>&1 | tail -5
```

Record pass count for regression comparison.

- [ ] **Step 2: Delete the residuals module**

```bash
rm src/vulca/pipeline/residuals.py
rm tests/test_agent_residuals.py
```

- [ ] **Step 3: Remove residuals from engine.py**

In `src/vulca/pipeline/engine.py`, remove:

```python
# Line 16-18: conditional import
    from vulca.pipeline.residuals import AgentResiduals
except ImportError:
    AgentResiduals = None  # type: ignore[assignment,misc]
```

Remove line 279:
```python
    _residuals = AgentResiduals() if (AgentResiduals is not None and pipeline_input.residuals) else None
```

Remove lines 391-401 (residual context injection before decide):
```python
            # Inject residual context before decide node
            if _residuals is not None and node_name in ("decide", "queen"):
                _history = _residuals.get_history()
                ...
                    ctx.data["residual_context"] = _residuals.aggregate(_weights, _history)
                    ctx.data["residual_weights"] = _asdict(_weights)
```

Remove lines 453-454 (recording):
```python
            if _residuals is not None:
                _residuals.record(node_name, round_num, output)
```

Remove line 605:
```python
        residual_context=ctx.data.get("residual_context"),
```

- [ ] **Step 4: Remove residuals from PipelineInput**

In `src/vulca/pipeline/types.py`, remove field:
```python
    residuals: bool = False
```

Remove `residual_context` from PipelineOutput if present.

- [ ] **Step 5: Remove residuals from create.py**

In `src/vulca/create.py`, remove the `residuals: bool = False` parameter from `acreate()` and any forwarding to PipelineInput.

- [ ] **Step 6: Remove re-exports from pipeline/__init__.py**

In `src/vulca/pipeline/__init__.py`, remove:
```python
from vulca.pipeline.residuals import AgentResiduals, NodeSnapshot, ResidualWeights
```

- [ ] **Step 7: Run tests to verify no regressions**

```bash
pytest tests/vulca/pipeline/ -x -q 2>&1 | tail -5
```

Expected: same pass count minus deleted test file. No new failures.

- [ ] **Step 8: Commit**

```bash
git add -u src/vulca/pipeline/residuals.py tests/test_agent_residuals.py \
  src/vulca/pipeline/engine.py src/vulca/pipeline/__init__.py \
  src/vulca/pipeline/types.py src/vulca/create.py
git commit -m "refactor: delete AgentResiduals — agent drives its own attention"
```

---

### Task 2: Delete sparse_eval + BriefIndexer + CulturalEngram

**Files:**
- Delete: `src/vulca/scoring/sparse.py`
- Delete: `src/vulca/cultural/engram.py`
- Delete: `tests/test_sparse_eval.py`
- Delete: `tests/test_cultural_engram.py`
- Delete: `tests/test_vlm_integration.py`
- Modify: `src/vulca/scoring/__init__.py:17-18`
- Modify: `src/vulca/cultural/__init__.py:34`
- Modify: `src/vulca/pipeline/nodes/evaluate.py:39-62`
- Modify: `src/vulca/pipeline/engine.py:274-276`
- Modify: `src/vulca/pipeline/types.py` (remove `sparse_eval` field)
- Modify: `src/vulca/create.py` (remove `sparse_eval` param)
- Modify: `src/vulca/evaluate.py:82`

- [ ] **Step 1: Delete modules and test files**

```bash
rm src/vulca/scoring/sparse.py
rm src/vulca/cultural/engram.py
rm tests/test_sparse_eval.py
rm tests/test_cultural_engram.py
rm tests/test_vlm_integration.py
```

- [ ] **Step 2: Remove re-exports from scoring/__init__.py**

In `src/vulca/scoring/__init__.py`, remove:
```python
from vulca.scoring.sparse import BriefIndexer, DimensionActivation
```

- [ ] **Step 3: Remove re-exports from cultural/__init__.py**

In `src/vulca/cultural/__init__.py`, remove:
```python
from vulca.cultural.engram import CulturalEngram, CulturalFragment, EngramQuery, EngramResult
```

- [ ] **Step 4: Strip sparse_eval from EvaluateNode**

In `src/vulca/pipeline/nodes/evaluate.py`, remove the entire sparse_eval branch (lines ~34-68) that imports BriefIndexer and CulturalEngram and builds dimension_activation. Keep only the VLM scoring + algorithmic tool merge path.

- [ ] **Step 5: Strip sparse_eval from engine.py**

Remove lines 274-276:
```python
    if pipeline_input.sparse_eval:
        ctx.set("sparse_eval", True)
```

- [ ] **Step 6: Remove sparse_eval from PipelineInput**

In `src/vulca/pipeline/types.py`, remove:
```python
    sparse_eval: bool = False
```

- [ ] **Step 7: Remove sparse_eval from create.py and evaluate.py**

In `src/vulca/create.py`, remove `sparse_eval` parameter and forwarding.

In `src/vulca/evaluate.py`, remove:
```python
from vulca.scoring.sparse import BriefIndexer
```
and any usage.

- [ ] **Step 8: Run tests**

```bash
pytest tests/vulca/pipeline/nodes/ tests/vulca/ -x -q 2>&1 | tail -5
```

Expected: no new failures beyond deleted files.

- [ ] **Step 9: Commit**

```bash
git add -u && git commit -m "refactor: delete sparse_eval + BriefIndexer + CulturalEngram — agent owns dimension routing"
```

---

### Task 3: Delete ModelRouter + explore_parallel + execute_stream

**Files:**
- Delete: `src/vulca/scoring/model_router.py`
- Delete: `src/vulca/pipeline/parallel.py`
- Delete: `tests/test_scoring.py`
- Delete: `tests/test_parallel_agents.py`
- Modify: `src/vulca/scoring/__init__.py:17` (remove ModelRouter, ModelSpec)
- Modify: `src/vulca/pipeline/__init__.py:6` (remove explore_parallel, rank_results)
- Modify: `src/vulca/pipeline/engine.py:636-704` (remove execute_stream)
- Modify: `src/vulca/intent/agent.py:15` (remove MODELS import)

- [ ] **Step 1: Delete modules and tests**

```bash
rm src/vulca/scoring/model_router.py
rm src/vulca/pipeline/parallel.py
rm tests/test_scoring.py
rm tests/test_parallel_agents.py
```

- [ ] **Step 2: Remove re-exports**

In `src/vulca/scoring/__init__.py`, remove:
```python
from vulca.scoring.model_router import ModelRouter, ModelSpec
```

In `src/vulca/pipeline/__init__.py`, remove:
```python
from vulca.pipeline.parallel import explore_parallel, rank_results
```

- [ ] **Step 3: Remove execute_stream from engine.py**

Delete the entire `execute_stream` async generator function (lines ~636-704).

- [ ] **Step 4: Fix intent/agent.py import**

In `src/vulca/intent/agent.py`, remove:
```python
from vulca.scoring.model_router import MODELS
```

Replace any usage with a hardcoded default or remove the dependent code path.

- [ ] **Step 5: Run tests**

```bash
pytest tests/ -x -q --ignore=tests/test_scoring.py --ignore=tests/test_parallel_agents.py 2>&1 | tail -10
```

- [ ] **Step 6: Commit**

```bash
git add -u && git commit -m "refactor: delete ModelRouter, explore_parallel, execute_stream — dead code"
```

---

### Task 4: Strip view/format parameters from all MCP tools

**Files:**
- Modify: `src/vulca/mcp_server.py` (every tool with `view`/`format` params)

**Rationale:** Agents always want full structured JSON. `view="summary"` hides data; `format="markdown"` is for human terminals. Remove both — always return the full dict. This is a breaking change for human CLI users, but agents are the target consumer.

- [ ] **Step 1: Write test for always-JSON returns**

Create `tests/test_mcp_always_json.py`:

```python
"""Verify all MCP tools return dict, never str."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_evaluate_returns_dict():
    """evaluate_artwork always returns dict (no markdown path)."""
    from vulca.mcp_server import evaluate_artwork

    mock_result = type("R", (), {
        "score": 0.75, "tradition": "default", "dimensions": {"L1": 0.8},
        "suggestions": [], "eval_mode": "strict", "summary": "ok",
        "cost_usd": 0.001, "rationales": {"L1": "good"}, "recommendations": [],
        "deviation_types": {}, "risk_flags": [], "risk_level": "low",
    })()
    with patch("vulca.mcp_server.aevaluate", new_callable=AsyncMock, return_value=mock_result):
        result = await evaluate_artwork(image_path="/tmp/test.png", tradition="default")
    assert isinstance(result, dict)
    # Always includes detailed fields now
    assert "rationales" in result


@pytest.mark.asyncio
async def test_list_traditions_returns_dict():
    """list_traditions always returns dict."""
    from vulca.mcp_server import list_traditions
    result = await list_traditions()
    assert isinstance(result, dict)
```

- [ ] **Step 2: Run test — verify it fails**

```bash
pytest tests/test_mcp_always_json.py -x -v
```

Expected: FAIL because current code returns str when `format="markdown"` and omits rationales when `view="summary"`.

- [ ] **Step 3: Remove view/format from create_artwork**

In `src/vulca/mcp_server.py`, `create_artwork` (line 174):
- Remove `view: str = "summary"` and `format: str = "json"` parameters
- Remove the `if view == "detailed"` branch — always include all fields
- Remove the `if format == "markdown"` branch
- Always return `dict`
- Update docstring: remove view/format docs, change return type

- [ ] **Step 4: Remove view/format from evaluate_artwork**

In `src/vulca/mcp_server.py`, `evaluate_artwork` (line 293):
- Remove `view` and `format` parameters
- Always include rationales, recommendations, deviation_types, risk_flags, risk_level
- Always return `dict`

- [ ] **Step 5: Remove view/format from list_traditions, get_tradition_guide, get_evolution_status**

Same pattern for each: remove `view`/`format` params, always return full dict.

- [ ] **Step 6: Remove view/format from resume_artwork**

Remove `view`/`format`, always return dict.

- [ ] **Step 7: Delete _to_markdown and _format_response helpers**

Delete `_to_markdown()` (lines 88-170) and `_format_response()` (line 740) — no longer called.

- [ ] **Step 8: Run tests**

```bash
pytest tests/test_mcp_always_json.py tests/ -x -q 2>&1 | tail -10
```

- [ ] **Step 9: Commit**

```bash
git add -u tests/test_mcp_always_json.py && git commit -m "refactor: strip view/format from MCP tools — always return structured JSON"
```

---

### Task 5: Strip inpaint count/select — single result per call

**Files:**
- Modify: `src/vulca/mcp_server.py:912` (inpaint_artwork)

**Rationale:** `count` generates N variants for a human to pick by number. Agent should call once, view result, re-call if unhappy. Simpler, cheaper, agent-native.

- [ ] **Step 1: Write test**

Create `tests/test_mcp_inpaint_single.py`:

```python
"""Verify inpaint_artwork returns single result, no count/select."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_inpaint_single_result():
    from vulca.mcp_server import inpaint_artwork
    import inspect
    sig = inspect.signature(inpaint_artwork)
    assert "count" not in sig.parameters
    assert "select" not in sig.parameters
```

- [ ] **Step 2: Run test — verify it fails**

```bash
pytest tests/test_mcp_inpaint_single.py -x -v
```

- [ ] **Step 3: Remove count/select from inpaint_artwork**

In `src/vulca/mcp_server.py`, `inpaint_artwork`:
- Remove `count: int = 4` and `select: int = 1` params
- Hardcode `count=1, select=0` in the internal `ainpaint()` call
- Update return: remove `variants` and `selected` fields — return single `{"image_path": ..., "bbox": ..., "cost_usd": ...}`
- Update docstring

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_inpaint_single.py tests/ -x -q 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
git add -u tests/test_mcp_inpaint_single.py && git commit -m "refactor: inpaint returns single result — agent re-calls if unhappy"
```

---

### Task 6: Strip studio_select_concept number-based selection

**Files:**
- Modify: `src/vulca/mcp_server.py:873` (studio_select_concept)

**Rationale:** 1-based index is for human "type a number" UX. Agent should pass concept name or ID.

- [ ] **Step 1: Write test**

```python
# tests/test_mcp_studio_select.py
"""Verify studio_select_concept uses concept_id, not 1-based index."""
import pytest
import inspect


def test_studio_select_concept_no_index():
    from vulca.mcp_server import studio_select_concept
    sig = inspect.signature(studio_select_concept)
    # Should have concept_id, not index
    assert "concept_id" in sig.parameters or "concept_name" in sig.parameters
    assert "index" not in sig.parameters
```

- [ ] **Step 2: Run test — verify fails**

```bash
pytest tests/test_mcp_studio_select.py -x -v
```

- [ ] **Step 3: Replace index with concept_id**

In `src/vulca/mcp_server.py`, `studio_select_concept`:
- Replace `index: int` with `concept_id: str`
- In `_studio_select_concept_impl`, look up concept by ID/name instead of `index - 1`
- Update docstring

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_studio_select.py tests/ -x -q 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
git add -u tests/test_mcp_studio_select.py && git commit -m "refactor: studio_select_concept uses concept_id, not 1-based index"
```

---

### Task 7: Add `generate_image` standalone MCP tool

**Files:**
- Modify: `src/vulca/mcp_server.py` (add new tool)
- Test: `tests/test_mcp_generate_image.py`

**Rationale:** Currently `create_artwork` runs the full generate→evaluate→decide loop. Agent needs a raw "generate one image" primitive it can call independently, then evaluate and decide itself.

- [ ] **Step 1: Write test**

```python
# tests/test_mcp_generate_image.py
"""Verify generate_image returns image_path + metadata, no pipeline loop."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_generate_image_returns_path():
    from vulca.mcp_server import generate_image

    mock_provider = AsyncMock()
    mock_provider.generate.return_value = type("R", (), {
        "image_b64": "iVBOR...",
        "cost_usd": 0.002,
        "latency_ms": 1200,
    })()

    with patch("vulca.mcp_server._get_provider", return_value=mock_provider):
        result = await generate_image(
            prompt="A mountain landscape in ink wash style",
            provider="mock",
        )
    assert isinstance(result, dict)
    assert "image_path" in result
    assert "cost_usd" in result


@pytest.mark.asyncio
async def test_generate_image_no_evaluate():
    """generate_image must NOT call evaluate."""
    import inspect
    from vulca.mcp_server import generate_image
    src = inspect.getsource(generate_image)
    assert "evaluate" not in src.lower() or "aevaluate" not in src
```

- [ ] **Step 2: Run test — verify fails (function doesn't exist)**

```bash
pytest tests/test_mcp_generate_image.py -x -v
```

- [ ] **Step 3: Implement generate_image**

Add to `src/vulca/mcp_server.py`:

```python
@mcp.tool()
async def generate_image(
    prompt: str,
    provider: str = "gemini",
    tradition: str = "default",
    reference_path: str = "",
    output_dir: str = "",
) -> dict:
    """Generate a single image from a text prompt. No evaluation, no loop.

    The agent drives the creative loop: generate → view → evaluate → decide.
    Call this tool to produce one image, then use view_image to inspect it
    and evaluate_artwork to score it.

    Args:
        prompt: Text description of the image to generate.
        provider: Image generation provider (gemini | openai | comfyui | mock).
        tradition: Cultural tradition for prompt enrichment.
        reference_path: Optional reference/sketch image path.
        output_dir: Directory to save the generated image. Defaults to temp dir.

    Returns:
        image_path: Path to the generated PNG.
        cost_usd: Generation cost.
        latency_ms: Generation time in milliseconds.
        provider: Provider used.
    """
    import base64
    import os
    import time
    import tempfile
    from pathlib import Path

    provider_instance = _get_provider(provider)
    ref_b64 = ""
    if reference_path:
        ref_b64 = _read_image_b64(reference_path)

    start = time.monotonic()
    result = await provider_instance.generate(
        prompt=prompt,
        reference_image_b64=ref_b64,
    )
    elapsed_ms = int((time.monotonic() - start) * 1000)

    out_dir = output_dir or tempfile.mkdtemp(prefix="vulca_gen_")
    out_path = str(Path(out_dir) / "generated.png")
    _save_b64_image(result.image_b64, out_path)

    return {
        "image_path": out_path,
        "cost_usd": getattr(result, "cost_usd", 0.0),
        "latency_ms": elapsed_ms,
        "provider": provider,
    }
```

Also add helpers `_get_provider()` and `_save_b64_image()` if they don't already exist (extract from existing create_artwork code).

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_generate_image.py -x -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/mcp_server.py tests/test_mcp_generate_image.py
git commit -m "feat: add generate_image MCP tool — atomic image generation, agent drives loop"
```

---

### Task 8: Add `view_image` MCP tool

**Files:**
- Modify: `src/vulca/mcp_server.py` (add new tool)
- Test: `tests/test_mcp_view_image.py`

**Rationale:** Agent needs to "see" intermediate results. Returns base64 thumbnail + metadata so the agent can inspect images via its multimodal capability.

- [ ] **Step 1: Write test**

```python
# tests/test_mcp_view_image.py
"""Verify view_image returns base64 image data for agent inspection."""
import pytest
import tempfile
from pathlib import Path


@pytest.mark.asyncio
async def test_view_image_returns_b64():
    from vulca.mcp_server import view_image
    from PIL import Image

    # Create a test image
    img = Image.new("RGB", (200, 200), color="red")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f, "PNG")
        path = f.name

    result = await view_image(image_path=path)
    assert isinstance(result, dict)
    assert "image_base64" in result
    assert "width" in result
    assert "height" in result
    assert result["width"] <= 1024  # Thumbnail capped

    Path(path).unlink()


@pytest.mark.asyncio
async def test_view_image_missing_file():
    from vulca.mcp_server import view_image
    result = await view_image(image_path="/nonexistent/image.png")
    assert "error" in result
```

- [ ] **Step 2: Run test — verify fails**

```bash
pytest tests/test_mcp_view_image.py -x -v
```

- [ ] **Step 3: Implement view_image**

Add to `src/vulca/mcp_server.py`:

```python
@mcp.tool()
async def view_image(
    image_path: str,
    max_dimension: int = 1024,
) -> dict:
    """View an image — returns base64-encoded thumbnail for agent inspection.

    Use this after generate_image or layers_composite to visually inspect
    the result before deciding next steps.

    Args:
        image_path: Path to the image file (PNG, JPEG, etc.).
        max_dimension: Maximum width or height in pixels. Larger images
            are downscaled to fit. Default 1024.

    Returns:
        image_base64: Base64-encoded PNG thumbnail.
        width: Thumbnail width in pixels.
        height: Thumbnail height in pixels.
        original_width: Original image width.
        original_height: Original image height.
        file_size_bytes: Original file size.
    """
    import base64
    import io
    import os
    from PIL import Image

    if not os.path.isfile(image_path):
        return {"error": f"File not found: {image_path}"}

    file_size = os.path.getsize(image_path)
    img = Image.open(image_path)
    orig_w, orig_h = img.size

    # Downscale if needed
    if max(orig_w, orig_h) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return {
        "image_base64": b64,
        "width": img.size[0],
        "height": img.size[1],
        "original_width": orig_w,
        "original_height": orig_h,
        "file_size_bytes": file_size,
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_view_image.py -x -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/mcp_server.py tests/test_mcp_view_image.py
git commit -m "feat: add view_image MCP tool — agent sees intermediate results"
```

---

### Task 9: Add `layers_list` MCP tool

**Files:**
- Modify: `src/vulca/mcp_server.py` (add new tool)
- Test: `tests/test_mcp_layers_list.py`

**Rationale:** Agent needs a quick structured inventory of layers in an artwork dir without parsing manifest.json itself.

- [ ] **Step 1: Write test**

```python
# tests/test_mcp_layers_list.py
"""Verify layers_list returns structured layer inventory."""
import json
import pytest
import tempfile
from pathlib import Path
from PIL import Image


def _make_artwork_dir() -> str:
    """Create a minimal artwork dir with manifest + layers."""
    d = tempfile.mkdtemp(prefix="vulca_test_")
    p = Path(d)

    # Create layer images
    for name in ["background", "subject"]:
        img = Image.new("RGBA", (100, 100), color="blue")
        img.save(p / f"{name}.png")

    manifest = {
        "layers": [
            {"name": "background", "z_index": 0, "content_type": "background",
             "description": "Paper texture", "visible": True, "blend_mode": "normal"},
            {"name": "subject", "z_index": 1, "content_type": "subject",
             "description": "Mountain scene", "visible": True, "blend_mode": "normal"},
        ]
    }
    (p / "manifest.json").write_text(json.dumps(manifest))
    return d


@pytest.mark.asyncio
async def test_layers_list_returns_inventory():
    from vulca.mcp_server import layers_list

    d = _make_artwork_dir()
    result = await layers_list(artwork_dir=d)

    assert isinstance(result, dict)
    assert "layers" in result
    assert len(result["layers"]) == 2
    assert result["layers"][0]["name"] == "background"
    assert result["layer_count"] == 2
```

- [ ] **Step 2: Run test — verify fails**

```bash
pytest tests/test_mcp_layers_list.py -x -v
```

- [ ] **Step 3: Implement layers_list**

Add to `src/vulca/mcp_server.py`:

```python
@mcp.tool()
async def layers_list(artwork_dir: str) -> dict:
    """List all layers in an artwork directory with their metadata.

    Returns a structured inventory of every layer: name, z_index,
    content_type, visibility, blend_mode, and whether the PNG file exists.

    Args:
        artwork_dir: Path to the artwork directory containing manifest.json.

    Returns:
        layers: List of layer metadata dicts.
        layer_count: Total number of layers.
        visible_count: Number of visible layers.
        has_composite: Whether composite.png exists.
    """
    import json
    import os
    from pathlib import Path

    manifest_path = Path(artwork_dir) / "manifest.json"
    if not manifest_path.exists():
        return {"error": f"No manifest.json in {artwork_dir}"}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_layers = manifest.get("layers", [])

    layers = []
    for la in raw_layers:
        name = la.get("name", "")
        png_path = Path(artwork_dir) / f"{name}.png"
        layers.append({
            "name": name,
            "z_index": la.get("z_index", 0),
            "content_type": la.get("content_type", ""),
            "description": la.get("description", ""),
            "visible": la.get("visible", True),
            "blend_mode": la.get("blend_mode", "normal"),
            "semantic_path": la.get("semantic_path", ""),
            "locked": la.get("locked", False),
            "has_image": png_path.is_file(),
        })

    has_composite = (Path(artwork_dir) / "composite.png").is_file()
    visible = sum(1 for la in layers if la["visible"])

    return {
        "layers": layers,
        "layer_count": len(layers),
        "visible_count": visible,
        "has_composite": has_composite,
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_layers_list.py -x -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/mcp_server.py tests/test_mcp_layers_list.py
git commit -m "feat: add layers_list MCP tool — structured layer inventory"
```

---

### Task 10: Absorb tradition layer order into get_tradition_guide

**Files:**
- Modify: `src/vulca/mcp_server.py` (get_tradition_guide tool)
- Modify: `src/vulca/layers/plan_prompt.py` (deprecate build_plan_prompt, keep get_tradition_layer_order)

**Rationale:** `build_plan_prompt` constructs a VLM prompt for Vulca's own brain to plan layers. In agent-native mode, the agent IS the planner — it just needs the tradition's canonical layer order data, not a VLM prompt. Fold layer order into `get_tradition_guide` so the agent gets everything in one call.

- [ ] **Step 1: Write test**

```python
# tests/test_tradition_guide_layers.py
"""Verify get_tradition_guide includes layer order data."""
import pytest


@pytest.mark.asyncio
async def test_tradition_guide_includes_layer_order():
    from vulca.mcp_server import get_tradition_guide

    result = await get_tradition_guide(tradition="chinese_xieyi")
    assert isinstance(result, dict)
    assert "tradition_layers" in result
    layers = result["tradition_layers"]
    assert len(layers) >= 3
    assert layers[0]["content_type"] == "background"
    # Each layer has role, content_type, blend, position, coverage
    for la in layers:
        assert "role" in la
        assert "content_type" in la
        assert "blend" in la
```

- [ ] **Step 2: Run test — verify fails**

```bash
pytest tests/test_tradition_guide_layers.py -x -v
```

- [ ] **Step 3: Add tradition_layers to get_tradition_guide response**

In `src/vulca/mcp_server.py`, in the `get_tradition_guide` function, after building the current result dict, add:

```python
    from vulca.layers.plan_prompt import get_tradition_layer_order
    result["tradition_layers"] = get_tradition_layer_order(tradition)
```

Update the docstring to mention the new field.

- [ ] **Step 4: Deprecate build_plan_prompt**

In `src/vulca/layers/plan_prompt.py`, add deprecation warning to `build_plan_prompt`:

```python
import warnings

def build_plan_prompt(intent: str, tradition: str = "default") -> str:
    """Build a VLM prompt to plan layer structure from text intent.

    .. deprecated:: 0.17.0
        Agent-native mode: agent plans layers itself using get_tradition_guide.
    """
    warnings.warn(
        "build_plan_prompt is deprecated — agent plans layers using get_tradition_guide data",
        DeprecationWarning,
        stacklevel=2,
    )
    # ... existing implementation unchanged for backward compat
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_tradition_guide_layers.py tests/ -x -q 2>&1 | tail -10
```

- [ ] **Step 6: Commit**

```bash
git add -u tests/test_tradition_guide_layers.py && git commit -m "feat: get_tradition_guide includes tradition_layers — agent plans its own layers"
```

---

### Task 11: Optimize tool descriptions for agent consumption

**Files:**
- Modify: `src/vulca/mcp_server.py` (all tool docstrings)

**Rationale:** Current docstrings explain params to humans. Agent-optimized descriptions should lead with what the tool does and when to use it, structured for LLM tool selection.

- [ ] **Step 1: Write test**

```python
# tests/test_mcp_descriptions.py
"""Verify tool descriptions follow agent-optimized pattern."""
import pytest
import inspect
from vulca import mcp_server


AGENT_TOOLS = [
    "generate_image", "view_image", "evaluate_artwork",
    "layers_list", "layers_split", "layers_composite",
    "layers_edit", "layers_redraw", "layers_transform",
    "get_tradition_guide", "list_traditions",
]


@pytest.mark.parametrize("tool_name", AGENT_TOOLS)
def test_tool_has_agent_description(tool_name):
    fn = getattr(mcp_server, tool_name, None)
    assert fn is not None, f"{tool_name} not found"
    doc = fn.__doc__ or ""
    # First line should be action-oriented (verb phrase)
    first_line = doc.strip().split("\n")[0]
    assert len(first_line) <= 120, f"{tool_name} first line too long for tool selection"
    assert len(first_line) >= 10, f"{tool_name} needs a description"
```

- [ ] **Step 2: Run test — check which pass**

```bash
pytest tests/test_mcp_descriptions.py -v
```

- [ ] **Step 3: Rewrite tool descriptions**

Update each tool's docstring in `src/vulca/mcp_server.py`. Pattern:
- **Line 1:** Verb phrase, ≤120 chars — what the tool does (for tool selection)
- **Lines 2-3:** When to use it in a typical agent workflow
- **Args:** Keep, but trim per-arg descriptions to essentials

Example for `generate_image`:
```python
"""Generate a single image from a text prompt — no evaluation, no loop.

Use after get_tradition_guide to get cultural context, then view_image to inspect the result.
"""
```

Example for `evaluate_artwork`:
```python
"""Score an image on L1-L5 cultural dimensions — returns structured scores + rationales.

Use after generate_image or layers_composite to decide whether to accept, retry, or edit.
"""
```

Example for `layers_split`:
```python
"""Decompose an image into full-canvas RGBA layers via segmentation or regeneration.

Use to break down a reference image into editable layers. Follow with layers_list to inspect results.
"""
```

Repeat for all tools in AGENT_TOOLS list.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_descriptions.py -v
```

- [ ] **Step 5: Commit**

```bash
git add -u tests/test_mcp_descriptions.py && git commit -m "docs: agent-optimized tool descriptions for MCP tool selection"
```

---

### Task 12: Deprecate resume_artwork — agent drives its own loop

**Files:**
- Modify: `src/vulca/mcp_server.py:491` (resume_artwork)
- Modify: `src/vulca/mcp_server.py:28` (_pending_sessions dict)

**Rationale:** `resume_artwork` exists for HITL: pipeline pauses at decide node, human picks accept/refine/reject. With agent-native, the agent never enters the pipeline loop — it calls generate_image/evaluate_artwork directly. The in-memory `_pending_sessions` dict is also broken across sessions.

- [ ] **Step 1: Write test**

```python
# tests/test_mcp_resume_deprecated.py
"""Verify resume_artwork emits deprecation warning."""
import pytest
import warnings


@pytest.mark.asyncio
async def test_resume_artwork_deprecated():
    from vulca.mcp_server import resume_artwork
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = await resume_artwork(session_id="fake-id", action="accept")
        assert len(w) == 1
        assert "deprecated" in str(w[0].message).lower()
    assert isinstance(result, dict)
    assert "deprecated" in result.get("warning", "").lower() or "error" in result
```

- [ ] **Step 2: Run test — verify fails**

```bash
pytest tests/test_mcp_resume_deprecated.py -x -v
```

- [ ] **Step 3: Add deprecation to resume_artwork**

In `src/vulca/mcp_server.py`, wrap `resume_artwork` body:

```python
@mcp.tool()
async def resume_artwork(
    session_id: str,
    action: str = "accept",
    feedback: str = "",
    locked_dimensions: str = "",
) -> dict:
    """[Deprecated] Resume a paused pipeline session.

    Deprecated in v0.17: use generate_image + evaluate_artwork directly.
    The agent drives the creative loop — no pipeline pause/resume needed.
    """
    import warnings
    warnings.warn(
        "resume_artwork is deprecated — use generate_image + evaluate_artwork. "
        "Agent drives the loop directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Keep existing implementation for backward compat
    if session_id not in _pending_sessions:
        return {"error": f"Session {session_id} not found", "warning": "Deprecated: use generate_image + evaluate_artwork"}
    # ... rest of existing code, add "warning": "deprecated" to return dict
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mcp_resume_deprecated.py tests/ -x -q 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
git add -u tests/test_mcp_resume_deprecated.py && git commit -m "deprecate: resume_artwork — agent drives loop via generate_image + evaluate_artwork"
```

---

### Task 13: Full regression test + version bump

**Files:**
- Modify: `pyproject.toml` (version bump to 0.17.0)

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -x -q 2>&1 | tail -20
```

Compare against Phase 0 baseline (1490 passed / 201 failed). Expected: fewer tests total (deleted dead code tests), no NEW failures beyond pre-existing cv2 baseline.

- [ ] **Step 2: Check for broken imports**

```bash
python -c "import vulca; print(vulca.__version__)"
python -c "from vulca.mcp_server import generate_image, view_image, layers_list; print('OK')"
```

- [ ] **Step 3: Verify MCP server starts**

```bash
timeout 5 python -m vulca.mcp_server 2>&1 || true
```

Should not crash on import.

- [ ] **Step 4: Bump version**

In `pyproject.toml`, change:
```toml
version = "0.17.0"
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml && git commit -m "chore: bump version to 0.17.0 — agent-native refactor"
```

---

## Execution Summary

| Task | Description | Type | Est. |
|------|-------------|------|------|
| 1 | Delete AgentResiduals | Delete dead code | 3 min |
| 2 | Delete sparse_eval + BriefIndexer + CulturalEngram | Delete dead code | 4 min |
| 3 | Delete ModelRouter + explore_parallel + execute_stream | Delete dead code | 3 min |
| 4 | Strip view/format from all MCP tools | Breaking refactor | 8 min |
| 5 | Strip inpaint count/select | Breaking refactor | 3 min |
| 6 | Strip studio_select_concept index | Breaking refactor | 3 min |
| 7 | Add generate_image tool | New feature | 5 min |
| 8 | Add view_image tool | New feature | 4 min |
| 9 | Add layers_list tool | New feature | 4 min |
| 10 | Absorb tradition layers into get_tradition_guide | Enhancement | 3 min |
| 11 | Agent-optimized tool descriptions | Docs | 5 min |
| 12 | Deprecate resume_artwork | Deprecation | 3 min |
| 13 | Full regression + version bump | QA | 3 min |

**Total: 13 tasks, 13 commits.**
