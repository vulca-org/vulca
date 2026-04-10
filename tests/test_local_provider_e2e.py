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
