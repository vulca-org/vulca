from __future__ import annotations

import asyncio
import argparse
import sys
import types
from unittest.mock import AsyncMock

from PIL import Image


def _run(coro):
    return asyncio.run(coro)


class _FastMCPStub:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, *args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    def run(self):
        pass


def _install_fastmcp_stub(monkeypatch):
    module = types.ModuleType("fastmcp")
    module.FastMCP = _FastMCPStub
    monkeypatch.setitem(sys.modules, "fastmcp", module)


def test_layers_split_mock_provider_uses_mock_analysis(tmp_path, monkeypatch):
    """MCP layers_split(provider='mock') must not call Gemini during analysis."""
    _install_fastmcp_stub(monkeypatch)

    from vulca.layers import analyze as analyze_mod
    from vulca.mcp_server import layers_split

    source = tmp_path / "source.png"
    Image.new("RGB", (6, 4), (120, 160, 200)).save(source)
    out_dir = tmp_path / "layers"
    observed: dict[str, str] = {}
    original_analyze = analyze_mod.analyze_layers

    async def _recording_analyze(image_path: str, **kwargs):
        observed.update(kwargs)
        return await original_analyze(image_path, **kwargs)

    monkeypatch.setattr(analyze_mod, "analyze_layers", _recording_analyze)
    monkeypatch.setattr(
        analyze_mod.litellm,
        "acompletion",
        AsyncMock(side_effect=AssertionError("mock provider called LiteLLM")),
    )

    result = _run(
        layers_split(
            image_path=str(source),
            output_dir=str(out_dir),
            mode="extract",
            provider="mock",
        )
    )

    assert observed["provider"] == "mock"
    assert result["split_mode"] == "extract"
    assert (out_dir / "manifest.json").exists()


def test_cli_layers_split_mock_provider_uses_mock_analysis(tmp_path, monkeypatch):
    """CLI layers split --provider mock must keep analysis offline too."""
    from vulca.cli import _cmd_layers
    from vulca.layers import analyze as analyze_mod

    source = tmp_path / "source.png"
    Image.new("RGB", (6, 4), (120, 160, 200)).save(source)
    out_dir = tmp_path / "layers"
    observed: dict[str, str] = {}
    original_analyze = analyze_mod.analyze_layers

    async def _recording_analyze(image_path: str, **kwargs):
        observed.update(kwargs)
        return await original_analyze(image_path, **kwargs)

    monkeypatch.setattr(analyze_mod, "analyze_layers", _recording_analyze)
    monkeypatch.setattr(
        analyze_mod.litellm,
        "acompletion",
        AsyncMock(side_effect=AssertionError("mock provider called LiteLLM")),
    )

    _cmd_layers(
        argparse.Namespace(
            layers_command="split",
            image=str(source),
            output=str(out_dir),
            mode="extract",
            provider="mock",
            tradition="default",
            case_log="",
        )
    )

    assert observed["provider"] == "mock"
    assert (out_dir / "manifest.json").exists()
