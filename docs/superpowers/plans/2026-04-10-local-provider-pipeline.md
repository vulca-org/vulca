# Local Provider Pipeline Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unblock the pipeline for local providers (ComfyUI + Ollama) so E2E validation can run without cloud API keys.

**Architecture:** Three surgical changes to bypass Gemini-specific key gates, plus pytest infrastructure and 6 integration tests (including a pipeline-level `execute()` test). No provider code is modified.

**Tech Stack:** Python 3.10+, pytest, asyncio, LiteLLM, ComfyUI REST API, Ollama

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `src/vulca/pipeline/engine.py:144-150` | Modify | `_resolve_api_key()` returns `"local"` for Ollama VLM setups |
| `src/vulca/_engine.py:28-35` | Modify | `Engine.__init__()` skips key check for Ollama VLM setups |
| `src/vulca/_vlm.py:644-656` | Modify | `score_image()` passes `api_base` for Ollama models |
| `tests/conftest.py` | Modify | Add `--run-local-provider` flag and `local_provider` marker |
| `tests/test_package.py:444-459` | Modify | Fix existing engine test to clear `VULCA_VLM_MODEL` |
| `tests/test_local_provider_e2e.py` | Create | 6 integration tests for local pipeline validation |
| `docs/local-provider-setup.md` | Create | Setup guide for ComfyUI + Ollama |

---

### Task 1: Add `_is_local_vlm()` helper and update `_resolve_api_key()`

**Files:**
- Modify: `src/vulca/pipeline/engine.py:144-150`
- Test: `tests/test_local_provider_e2e.py` (new file)

- [ ] **Step 1: Write failing test for local key resolution**

```python
# tests/test_local_provider_e2e.py
"""Local provider pipeline validation tests (ComfyUI + Ollama)."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest


def test_resolve_api_key_returns_local_for_ollama():
    """_resolve_api_key returns 'local' when VULCA_VLM_MODEL starts with 'ollama'."""
    from vulca.pipeline.engine import _resolve_api_key
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(subject="test", provider="comfyui")
    with patch.dict(os.environ, {
        "VULCA_VLM_MODEL": "ollama_chat/gemma3:12b",
    }, clear=False):
        # Remove any Gemini keys that might be set
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            result = _resolve_api_key(inp)
            assert result == "local"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_local_provider_e2e.py::test_resolve_api_key_returns_local_for_ollama -v`
Expected: FAIL — returns `""` instead of `"local"`

- [ ] **Step 3: Implement `_is_local_vlm()` and update `_resolve_api_key()`**

In `src/vulca/pipeline/engine.py`, add helper and modify `_resolve_api_key`:

```python
def _is_local_vlm() -> bool:
    """Check if the configured VLM model is a local provider (e.g. Ollama)."""
    model = os.environ.get("VULCA_VLM_MODEL", "")
    return model.startswith("ollama")


def _resolve_api_key(pipeline_input: PipelineInput) -> str:
    """Resolve API key from input, then environment."""
    key = (
        pipeline_input.api_key
        or os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("GOOGLE_API_KEY", "")
    )
    if not key and _is_local_vlm():
        return "local"
    return key
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_local_provider_e2e.py::test_resolve_api_key_returns_local_for_ollama -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/vulca/pipeline/engine.py tests/test_local_provider_e2e.py
git commit -m "feat: _resolve_api_key returns 'local' for Ollama VLM setups"
```

---

### Task 2: Update `Engine.__init__()` to allow local VLM

**Files:**
- Modify: `src/vulca/_engine.py:28-35`
- Test: `tests/test_local_provider_e2e.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_local_provider_e2e.py`:

```python
def test_engine_init_no_raise_for_ollama():
    """Engine() does not raise ValueError when VULCA_VLM_MODEL is ollama-based."""
    with patch.dict(os.environ, {
        "VULCA_VLM_MODEL": "ollama_chat/gemma3:12b",
    }, clear=False):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            # Reset singleton
            import vulca._engine as eng_mod
            eng_mod._instance = None
            from vulca._engine import Engine
            engine = Engine()
            assert engine.api_key == "local"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_local_provider_e2e.py::test_engine_init_no_raise_for_ollama -v`
Expected: FAIL — `ValueError: No API key found`

- [ ] **Step 3: Update `Engine.__init__()` and `get_instance()`**

In `src/vulca/_engine.py`, modify the `__init__` method:

```python
def __init__(self, api_key: str = "", mock: bool = False) -> None:
    self.mock = mock
    self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    if not self.api_key and not self.mock:
        # Allow keyless operation when VLM is a local provider (e.g. Ollama)
        vlm_model = os.environ.get("VULCA_VLM_MODEL", "")
        if vlm_model.startswith("ollama"):
            self.api_key = "local"
        else:
            raise ValueError(
                "No API key found. Set GOOGLE_API_KEY environment variable, "
                "pass api_key='...' to vulca.evaluate(), or use mock=True."
            )
```

Also update `get_instance()` similarly:

```python
@classmethod
def get_instance(cls, api_key: str = "", mock: bool = False) -> Engine:
    global _instance
    key = api_key or os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    if not key and not mock:
        vlm_model = os.environ.get("VULCA_VLM_MODEL", "")
        if vlm_model.startswith("ollama"):
            key = "local"
    if _instance is None or (api_key and _instance.api_key != key) or (mock != (_instance.mock if _instance else False)):
        _instance = cls(api_key=key, mock=mock)
    return _instance
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_local_provider_e2e.py::test_engine_init_no_raise_for_ollama -v`
Expected: PASS

- [ ] **Step 5: Fix existing engine test to clear `VULCA_VLM_MODEL`**

The existing test at `tests/test_package.py:444` (`test_engine_requires_api_key`) asserts that `Engine()` raises `ValueError` when no Gemini key exists. With our change, if `VULCA_VLM_MODEL` happens to be set to an ollama model, this test would pass instead of raising. Fix by explicitly clearing `VULCA_VLM_MODEL`:

In `tests/test_package.py`, modify `test_engine_requires_api_key`:

```python
def test_engine_requires_api_key():
    import os
    # Temporarily remove API key and local VLM model
    orig = os.environ.pop("GOOGLE_API_KEY", None)
    orig2 = os.environ.pop("GEMINI_API_KEY", None)
    orig3 = os.environ.pop("VULCA_VLM_MODEL", None)

    from vulca._engine import Engine
    import vulca._engine as _eng
    _eng._instance = None  # Reset singleton

    with pytest.raises(ValueError, match="No API key"):
        Engine.get_instance()

    # Restore
    if orig:
        os.environ["GOOGLE_API_KEY"] = orig
    if orig2:
        os.environ["GEMINI_API_KEY"] = orig2
    if orig3:
        os.environ["VULCA_VLM_MODEL"] = orig3
```

- [ ] **Step 6: Add edge-case unit tests**

Append to `tests/test_local_provider_e2e.py`:

```python
def test_resolve_api_key_explicit_key_takes_precedence():
    """Explicit pipeline_input.api_key takes precedence over 'local' sentinel."""
    from vulca.pipeline.engine import _resolve_api_key
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(subject="test", provider="comfyui", api_key="my-explicit-key")
    with patch.dict(os.environ, {"VULCA_VLM_MODEL": "ollama_chat/gemma3:12b"}, clear=False):
        result = _resolve_api_key(inp)
        assert result == "my-explicit-key"


def test_resolve_api_key_non_ollama_returns_empty():
    """Non-ollama VLM model without Gemini key returns empty string."""
    from vulca.pipeline.engine import _resolve_api_key
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(subject="test", provider="comfyui")
    with patch.dict(os.environ, {"VULCA_VLM_MODEL": "gemini/gemini-2.5-flash"}, clear=False):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            result = _resolve_api_key(inp)
            assert result == ""
```

- [ ] **Step 7: Run all engine-related tests to verify no regressions**

Run: `pytest tests/test_package.py::test_engine_requires_api_key tests/test_local_provider_e2e.py -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add src/vulca/_engine.py tests/test_local_provider_e2e.py tests/test_package.py
git commit -m "feat: Engine allows keyless init for Ollama VLM setups"
```

---

### Task 3: Pass `api_base` in `score_image()` for Ollama

**Files:**
- Modify: `src/vulca/_vlm.py:644-656`
- Test: `tests/test_local_provider_e2e.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_local_provider_e2e.py`:

```python
@pytest.mark.asyncio
async def test_score_image_passes_api_base_for_ollama():
    """score_image() passes api_base to litellm when model is ollama-based."""
    from unittest.mock import AsyncMock, MagicMock

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
<scoring>
{"L1": 0.7, "L2": 0.6, "L3": 0.8, "L4": 0.5, "L5": 0.6,
 "L1_rationale": "test", "L2_rationale": "", "L3_rationale": "",
 "L4_rationale": "", "L5_rationale": ""}
</scoring>
"""
    mock_response.choices[0].finish_reason = "stop"

    with patch.dict(os.environ, {
        "VULCA_VLM_MODEL": "ollama_chat/gemma3:12b",
        "OLLAMA_API_BASE": "http://localhost:11434",
    }):
        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_response) as mock_call:
            from vulca._vlm import score_image
            # Minimal valid base64 PNG (1x1 pixel)
            import base64
            pixel = base64.b64encode(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
                b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
                b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
            ).decode()
            await score_image(pixel, "image/png", "test", "default", "local")

            call_kwargs = mock_call.call_args[1]
            assert call_kwargs.get("api_base") == "http://localhost:11434"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_local_provider_e2e.py::test_score_image_passes_api_base_for_ollama -v`
Expected: FAIL — `api_base` not in call kwargs

- [ ] **Step 3: Update `score_image()` to pass `api_base`**

In `src/vulca/_vlm.py`, modify the `litellm.acompletion()` call inside `score_image()` (around line 644-656):

Replace:
```python
        model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")

        # Adaptive token budget: start at _DEFAULT_MAX_TOKENS, escalate on truncation
        max_tokens = _DEFAULT_MAX_TOKENS
        resp = None
        for attempt in range(_MAX_ESCALATION_ATTEMPTS + 1):
            resp = await litellm.acompletion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1,
                api_key=api_key,
                timeout=55,
            )
```

With:
```python
        model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")

        # Resolve api_base for local providers (e.g. Ollama)
        api_base = None
        if model.startswith("ollama"):
            api_base = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")

        # Adaptive token budget: start at _DEFAULT_MAX_TOKENS, escalate on truncation
        max_tokens = _DEFAULT_MAX_TOKENS
        resp = None
        for attempt in range(_MAX_ESCALATION_ATTEMPTS + 1):
            call_kwargs = dict(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1,
                api_key=api_key,
                timeout=55,
            )
            if api_base:
                call_kwargs["api_base"] = api_base
            resp = await litellm.acompletion(**call_kwargs)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_local_provider_e2e.py::test_score_image_passes_api_base_for_ollama -v`
Expected: PASS

- [ ] **Step 5: Write test that non-ollama models do NOT receive `api_base`**

Append to `tests/test_local_provider_e2e.py`:

```python
@pytest.mark.asyncio
async def test_score_image_no_api_base_for_gemini():
    """score_image() does NOT pass api_base for non-Ollama models."""
    from unittest.mock import AsyncMock, MagicMock

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
<scoring>
{"L1": 0.7, "L2": 0.6, "L3": 0.8, "L4": 0.5, "L5": 0.6,
 "L1_rationale": "test", "L2_rationale": "", "L3_rationale": "",
 "L4_rationale": "", "L5_rationale": ""}
</scoring>
"""
    mock_response.choices[0].finish_reason = "stop"

    with patch.dict(os.environ, {"VULCA_VLM_MODEL": "gemini/gemini-2.5-flash"}):
        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_response) as mock_call:
            from vulca._vlm import score_image
            import base64
            pixel = base64.b64encode(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
                b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
                b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
            ).decode()
            await score_image(pixel, "image/png", "test", "default", "fake-key")

            call_kwargs = mock_call.call_args[1]
            assert "api_base" not in call_kwargs
```

- [ ] **Step 6: Run tests to verify both pass**

Run: `pytest tests/test_local_provider_e2e.py -k "api_base" -v`
Expected: 2 PASS

- [ ] **Step 7: Commit**

```bash
git add src/vulca/_vlm.py tests/test_local_provider_e2e.py
git commit -m "feat: score_image passes api_base for Ollama VLM models"
```

---

### Task 4: Add pytest `--run-local-provider` infrastructure

**Files:**
- Modify: `tests/conftest.py`
- Test: `tests/test_local_provider_e2e.py`

- [ ] **Step 1: Update conftest.py**

In `tests/conftest.py`, add the `--run-local-provider` option and marker alongside the existing `--run-real-provider`:

```python
def pytest_addoption(parser):
    parser.addoption(
        "--run-real-provider",
        action="store_true",
        default=False,
        help="Run tests marked real_provider (hits live APIs, requires credentials)",
    )
    parser.addoption(
        "--run-local-provider",
        action="store_true",
        default=False,
        help="Run tests marked local_provider (requires local ComfyUI + Ollama)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "real_provider: test that hits a real image provider")
    config.addinivalue_line("markers",
                            "local_provider: test that requires local ComfyUI + Ollama")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-real-provider"):
        skip_real = pytest.mark.skip(reason="needs --run-real-provider")
        for item in items:
            if "real_provider" in item.keywords:
                item.add_marker(skip_real)
    if not config.getoption("--run-local-provider"):
        skip_local = pytest.mark.skip(reason="needs --run-local-provider")
        for item in items:
            if "local_provider" in item.keywords:
                item.add_marker(skip_local)
```

- [ ] **Step 2: Add marker to existing unit tests in test file**

The 3 unit tests from Tasks 1-3 should NOT have the `local_provider` marker (they use mocks, not real services). Verify they still pass without the flag:

Run: `pytest tests/test_local_provider_e2e.py -v`
Expected: 3 PASS (the mock-based tests from Tasks 1-3)

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "feat: add --run-local-provider pytest flag and local_provider marker"
```

---

### Task 5: Add live integration tests

**Files:**
- Modify: `tests/test_local_provider_e2e.py`

- [ ] **Step 1: Add ComfyUI single-create tests**

Append to `tests/test_local_provider_e2e.py`:

```python
import asyncio
import base64

# ---------------------------------------------------------------------------
# Live integration tests — require running ComfyUI + Ollama
# ---------------------------------------------------------------------------

def _decode_and_validate_png(image_b64: str) -> bytes:
    """Decode base64, assert valid PNG with dimensions > 0 and size > 10KB."""
    raw = base64.b64decode(image_b64)
    assert raw[:8] == b'\x89PNG\r\n\x1a\n', "Not a valid PNG"
    assert len(raw) > 10_000, f"Image too small: {len(raw)} bytes"
    # Validate dimensions > 0
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(raw))
    assert img.width > 0 and img.height > 0, f"Invalid dimensions: {img.size}"
    return raw


def _require_local_env():
    """Skip test if local provider env vars are not set."""
    model = os.environ.get("VULCA_VLM_MODEL", "")
    if not model.startswith("ollama"):
        pytest.skip("VULCA_VLM_MODEL not set to ollama — set env vars per docs/local-provider-setup.md")


@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_comfyui_single_create_xieyi():
    """ComfyUI generates a chinese_xieyi image — valid PNG, >10KB."""
    _require_local_env()
    from vulca.providers import get_image_provider

    provider = get_image_provider("comfyui")
    result = await provider.generate(
        "水墨山水，雨后春山，松间茅屋",
        tradition="chinese_xieyi",
        width=1024,
        height=1024,
    )
    assert result.image_b64
    _decode_and_validate_png(result.image_b64)


@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_comfyui_single_create_western():
    """ComfyUI generates a western_academic image — valid PNG, >10KB."""
    _require_local_env()
    from vulca.providers import get_image_provider

    provider = get_image_provider("comfyui")
    result = await provider.generate(
        "Impressionist garden at golden hour, oil on canvas",
        tradition="western_academic",
        width=1024,
        height=1024,
    )
    assert result.image_b64
    _decode_and_validate_png(result.image_b64)
```

- [ ] **Step 2: Add Ollama VLM score test**

Append to `tests/test_local_provider_e2e.py`:

```python
@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_ollama_vlm_score():
    """Ollama scores an image via score_image() — returns valid L1-L5."""
    _require_local_env()
    from vulca._vlm import score_image

    # Use a real test image: 1x1 red pixel PNG (minimal but valid)
    from PIL import Image
    import io
    img = Image.new("RGB", (64, 64), color=(180, 60, 40))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    result = await score_image(
        img_b64, "image/png", "test artwork", "default", "local"
    )
    assert "error" not in result, f"VLM scoring failed: {result.get('error')}"
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = result[level]
        assert 0.0 <= score <= 1.0, f"{level} score out of range: {score}"
    # At least one rationale should be non-empty
    rationales = [result.get(f"L{i}_rationale", "") for i in range(1, 6)]
    assert any(r for r in rationales), "All rationales are empty"
```

- [ ] **Step 3: Add full e2e chain test**

Append to `tests/test_local_provider_e2e.py`:

```python
@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_local_e2e_create_then_evaluate():
    """Full chain: ComfyUI create → Ollama evaluate → valid scores."""
    _require_local_env()
    from vulca.providers import get_image_provider
    from vulca._vlm import score_image

    # Step 1: Generate image with ComfyUI
    provider = get_image_provider("comfyui")
    gen_result = await provider.generate(
        "水墨山水，雨后春山",
        tradition="chinese_xieyi",
        width=1024,
        height=1024,
    )
    assert gen_result.image_b64
    raw = _decode_and_validate_png(gen_result.image_b64)

    # Step 2: Score with Ollama VLM
    eval_result = await score_image(
        gen_result.image_b64, "image/png",
        "ink wash landscape", "chinese_xieyi", "local",
    )
    assert "error" not in eval_result, f"VLM scoring failed: {eval_result.get('error')}"
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = eval_result[level]
        assert 0.0 <= score <= 1.0, f"{level} score out of range: {score}"
```

- [ ] **Step 4: Add pipeline-level `execute()` integration test**

This is the critical test that validates the full pipeline path: `_resolve_api_key()` → `NodeContext` → `EvaluateNode` gate → `_vlm.score_image()`.

Append to `tests/test_local_provider_e2e.py`:

```python
@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_local_pipeline_execute_e2e():
    """Full pipeline execute(): ComfyUI + Ollama through pipeline.engine.execute()."""
    _require_local_env()
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import DEFAULT
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(
        subject="水墨山水，雨后春山",
        provider="comfyui",
        tradition="chinese_xieyi",
        max_rounds=1,
    )
    output = await execute(DEFAULT, inp, checkpoint=False)

    assert output.status == "complete", f"Pipeline status: {output.status}"
    # Verify we got real scores, not mock
    if output.rounds:
        last = output.rounds[-1]
        scores = last.get("scores", {})
        if scores:
            for level in ("L1", "L2", "L3", "L4", "L5"):
                if level in scores:
                    assert 0.0 <= scores[level] <= 1.0
```

- [ ] **Step 5: Verify skip behavior without flag**

Run: `pytest tests/test_local_provider_e2e.py -v`
Expected: Unit tests PASS, all `local_provider` tests SKIPPED

- [ ] **Step 6: Commit**

```bash
git add tests/test_local_provider_e2e.py
git commit -m "feat: add local_provider integration tests for ComfyUI + Ollama"
```

---

### Task 6: Add setup documentation

**Files:**
- Create: `docs/local-provider-setup.md`

- [ ] **Step 1: Write setup guide**

```markdown
# Local Provider Setup (ComfyUI + Ollama)

Zero-cost local pipeline for development and testing. No cloud API keys required.

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4/M5)
- Python 3.10+
- ~20GB disk (SDXL checkpoint + Gemma 3 model)
- 16GB+ unified memory recommended

## 1. ComfyUI (Image Generation)

```bash
# Clone and install
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3 -m venv venv && source venv/bin/activate
pip install torch torchvision torchaudio
pip install -r requirements.txt

# Download SDXL checkpoint (~7GB)
# Place sd_xl_base_1.0.safetensors in ComfyUI/models/checkpoints/
# Download from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

# Start server (--force-fp32 for MPS stability)
python main.py --force-fp32

# Verify
curl http://127.0.0.1:8188/system_stats
```

## 2. Ollama (VLM Scoring)

```bash
brew install ollama
ollama pull gemma3:12b    # ~8GB, includes vision encoder

# Verify
curl http://localhost:11434/api/tags
```

## 3. Environment Variables

```bash
export VULCA_IMAGE_BASE_URL=http://localhost:8188
export VULCA_VLM_MODEL=ollama_chat/gemma3:12b
export OLLAMA_API_BASE=http://localhost:11434
```

Add to your shell profile (~/.zshrc) for persistence.

## 4. Run Tests

```bash
# Unit tests only (no services needed)
pytest tests/test_local_provider_e2e.py -v

# Full integration tests (requires ComfyUI + Ollama running)
pytest tests/test_local_provider_e2e.py --run-local-provider -v
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ComfyUI black images | Use `--force-fp32` instead of `--force-fp16` |
| ComfyUI timeout | SDXL on MPS takes 60-120s; timeout is 300s |
| Ollama connection refused | Run `ollama serve` first |
| VLM returns empty scores | Ensure model is `ollama_chat/` not `ollama/` |
| `ValueError: No API key` | Ensure `VULCA_VLM_MODEL` starts with `ollama` |
```

- [ ] **Step 2: Commit**

```bash
git add docs/local-provider-setup.md
git commit -m "docs: add local provider setup guide for ComfyUI + Ollama"
```

---

### Task 7: Final validation

- [ ] **Step 1: Run the modified source files' related tests**

Run: `pytest tests/test_package.py tests/test_evaluate.py tests/test_local_provider_e2e.py -v`
Expected: All previously-passing tests still pass; no new failures introduced

- [ ] **Step 2: Run local provider unit tests (no services needed)**

Run: `pytest tests/test_local_provider_e2e.py -v`
Expected: 6 PASS (unit/mock tests), 5 SKIPPED (local_provider tests)

- [ ] **Step 3: (Manual) If ComfyUI + Ollama are running, run live tests**

Run: `pytest tests/test_local_provider_e2e.py --run-local-provider -v`
Expected: 11 PASS (6 unit + 5 live)
