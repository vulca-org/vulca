"""P0 #5: native dispatch falls back to legacy when provider can't emit PNG.

The built-in mock provider returns SVG bytes. Before P0 #5, LayerGenerateNode
would still route native traditions through layered_generate and every layer
would fail at PIL decode. Now it detects the mock provider and falls back to
the legacy VLM-mask code path, so manifest.generation_path should be "b".
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput


def test_mock_provider_on_native_tradition_falls_back_to_legacy(tmp_path):
    inp = PipelineInput(
        subject="远山薄雾",
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="mock",
        layered=True,
        output_dir=str(tmp_path),
    )
    asyncio.run(execute(LAYERED, inp))

    manifest = json.loads((Path(tmp_path) / "manifest.json").read_text())
    assert manifest["version"] == 3
    assert manifest["layerability"] == "native"
    # Mock provider → legacy (B-path) because it can't emit real PNG bytes.
    assert manifest["generation_path"] == "b"
