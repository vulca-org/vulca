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
    env["VULCA_VLM_MODEL"] = "ollama_chat/gemma3:12b"
    with patch.dict(os.environ, env, clear=True):
        result = _resolve_api_key(inp)
        assert result == "local"


def test_engine_init_no_raise_for_ollama():
    """Engine() does not raise ValueError when VULCA_VLM_MODEL is ollama-based."""
    env = {k: v for k, v in os.environ.items()
           if k not in {"GEMINI_API_KEY", "GOOGLE_API_KEY"}}
    env["VULCA_VLM_MODEL"] = "ollama_chat/gemma3:12b"
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
    with patch.dict(os.environ, {"VULCA_VLM_MODEL": "ollama_chat/gemma3:12b"}, clear=False):
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
        "VULCA_VLM_MODEL": "ollama_chat/gemma3:12b",
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
