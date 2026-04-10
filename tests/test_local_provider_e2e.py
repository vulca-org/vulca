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
    env = {k: v for k, v in os.environ.items()
           if k not in {"GEMINI_API_KEY", "GOOGLE_API_KEY"}}
    env["VULCA_VLM_MODEL"] = "ollama_chat/gemma4"
    with patch.dict(os.environ, env, clear=True):
        result = _resolve_api_key(inp)
        assert result == "local"


def test_engine_init_no_raise_for_ollama():
    """Engine() does not raise ValueError when VULCA_VLM_MODEL is ollama-based."""
    env = {k: v for k, v in os.environ.items()
           if k not in {"GEMINI_API_KEY", "GOOGLE_API_KEY"}}
    env["VULCA_VLM_MODEL"] = "ollama_chat/gemma4"
    with patch.dict(os.environ, env, clear=True):
        # Reset singleton
        import vulca._engine as eng_mod
        eng_mod._instance = None
        from vulca._engine import Engine
        engine = Engine()
        assert engine.api_key == "local"


def test_resolve_api_key_explicit_key_takes_precedence():
    """Explicit pipeline_input.api_key takes precedence over 'local' sentinel."""
    from vulca.pipeline.engine import _resolve_api_key
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(subject="test", provider="comfyui", api_key="my-explicit-key")
    with patch.dict(os.environ, {"VULCA_VLM_MODEL": "ollama_chat/gemma4"}, clear=False):
        result = _resolve_api_key(inp)
        assert result == "my-explicit-key"


def test_resolve_api_key_non_ollama_returns_empty():
    """Non-ollama VLM model without Gemini key returns empty string."""
    from vulca.pipeline.engine import _resolve_api_key
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(subject="test", provider="comfyui")
    env = {k: v for k, v in os.environ.items()
           if k not in {"GEMINI_API_KEY", "GOOGLE_API_KEY"}}
    env["VULCA_VLM_MODEL"] = "gemini/gemini-2.5-flash"
    with patch.dict(os.environ, env, clear=True):
        result = _resolve_api_key(inp)
        assert result == ""


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
        "VULCA_VLM_MODEL": "ollama_chat/gemma4",
        "OLLAMA_API_BASE": "http://localhost:11434",
    }):
        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_response) as mock_call:
            from vulca._vlm import score_image
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


@pytest.mark.asyncio
async def test_score_image_api_base_default_fallback():
    """score_image() uses default localhost:11434 when OLLAMA_API_BASE is not set."""
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

    env = {k: v for k, v in os.environ.items() if k != "OLLAMA_API_BASE"}
    env["VULCA_VLM_MODEL"] = "ollama_chat/gemma4"
    with patch.dict(os.environ, env, clear=True):
        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_response) as mock_call:
            from vulca._vlm import score_image
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


import asyncio
import base64
import io

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


@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_ollama_vlm_score():
    """Ollama scores an image via score_image() — returns valid L1-L5."""
    _require_local_env()
    from vulca._vlm import score_image
    from PIL import Image

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
    rationales = [result.get(f"L{i}_rationale", "") for i in range(1, 6)]
    assert any(r for r in rationales), "All rationales are empty"


@pytest.mark.local_provider
@pytest.mark.asyncio
async def test_local_e2e_create_then_evaluate():
    """Full chain: ComfyUI create → Ollama evaluate → valid scores."""
    _require_local_env()
    from vulca.providers import get_image_provider
    from vulca._vlm import score_image

    provider = get_image_provider("comfyui")
    gen_result = await provider.generate(
        "水墨山水，雨后春山",
        tradition="chinese_xieyi",
        width=1024,
        height=1024,
    )
    assert gen_result.image_b64
    _decode_and_validate_png(gen_result.image_b64)

    eval_result = await score_image(
        gen_result.image_b64, "image/png",
        "ink wash landscape", "chinese_xieyi", "local",
    )
    assert "error" not in eval_result, f"VLM scoring failed: {eval_result.get('error')}"
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = eval_result[level]
        assert 0.0 <= score <= 1.0, f"{level} score out of range: {score}"


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

    assert output.status == "completed", f"Pipeline status: {output.status}"
    if output.rounds:
        last = output.rounds[-1]
        scores = last.dimension_scores
        if scores:
            for level in ("L1", "L2", "L3", "L4", "L5"):
                if level in scores:
                    assert 0.0 <= scores[level] <= 1.0
