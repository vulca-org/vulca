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
