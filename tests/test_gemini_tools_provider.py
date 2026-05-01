"""Tests for the Gemini tool-enabled image provider."""
from __future__ import annotations

import asyncio

import pytest

from vulca.providers.base import ImageProvider, ImageResult
from vulca.providers.gemini import GeminiImageProvider
from vulca.providers.gemini_tools import GeminiToolsImageProvider, tools_for_profile


def test_protocol_compliance():
    p = GeminiToolsImageProvider(api_key="test-key")
    assert isinstance(p, ImageProvider)


def test_tool_profiles_build_google_genai_tools():
    pytest.importorskip("google.genai")
    assert tools_for_profile("none") == []
    assert tools_for_profile("") == []
    assert tools_for_profile("web")[0].google_search is not None
    assert tools_for_profile("url")[0].url_context is not None
    assert tools_for_profile("code")[0].code_execution is not None


def test_generate_passes_profile_tools_to_gemini_config(monkeypatch):
    pytest.importorskip("google.genai")
    captured = {}

    async def fake_generate(self, prompt, **kwargs):
        captured["prompt"] = prompt
        captured["kwargs"] = kwargs
        return ImageResult(
            image_b64="aW1n",
            metadata={"tools": len(kwargs["tools"])},
        )

    monkeypatch.setattr(GeminiImageProvider, "generate", fake_generate)

    provider = GeminiToolsImageProvider(api_key="test-key")
    result = asyncio.run(provider.generate("make a poster", tool_profile="web"))

    assert result.image_b64 == "aW1n"
    assert result.metadata == {"tools": 1}
    assert captured["prompt"] == "make a poster"
    assert captured["kwargs"]["tools"][0].google_search is not None


def test_generate_accepts_explicit_tools(monkeypatch):
    captured = {}

    async def fake_generate(self, prompt, **kwargs):
        captured["kwargs"] = kwargs
        return ImageResult(image_b64="aW1n")

    monkeypatch.setattr(GeminiImageProvider, "generate", fake_generate)
    explicit_tools = [{"type": "custom"}]

    provider = GeminiToolsImageProvider(api_key="test-key")
    asyncio.run(
        provider.generate(
            "make a poster",
            tool_profile="web",
            tools=explicit_tools,
        )
    )

    assert captured["kwargs"]["tools"] is explicit_tools
