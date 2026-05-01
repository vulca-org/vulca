"""Gemini image provider with optional Google GenAI tools."""
from __future__ import annotations

from typing import Any

from vulca.providers.gemini import GeminiImageProvider


def tools_for_profile(profile: str) -> list[Any]:
    """Build google-genai Tool objects for a named opt-in profile."""
    normalized = (profile or "none").strip().lower().replace("_", "-")
    if normalized in {"none", "off", "false", "0"}:
        return []

    from google.genai import types

    if normalized in {"web", "search", "google-search"}:
        return [types.Tool(google_search=types.GoogleSearch())]
    if normalized in {"url", "url-context"}:
        return [types.Tool(url_context=types.UrlContext())]
    if normalized in {"code", "code-execution"}:
        return [types.Tool(code_execution=types.ToolCodeExecution())]

    raise ValueError(
        "Unknown Gemini tool_profile "
        f"{profile!r}. Expected one of: none, web, url, code."
    )


class GeminiToolsImageProvider(GeminiImageProvider):
    """Gemini image generation with opt-in tool profiles."""

    capabilities: frozenset[str] = GeminiImageProvider.capabilities | frozenset(
        {"tool_profile"}
    )

    async def generate(self, prompt: str, **kwargs):
        tool_profile = kwargs.pop("tool_profile", "none")
        if "tools" not in kwargs:
            kwargs["tools"] = tools_for_profile(tool_profile)
        return await super().generate(prompt, **kwargs)


__all__ = ["GeminiToolsImageProvider", "tools_for_profile"]
