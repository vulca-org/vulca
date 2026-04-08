"""A-path end-to-end test on chinese_xieyi using the mock provider.

The mock provider returns non-PNG bytes, so every layer call inside
`layered_generate` fails at the PIL decode step. That is OK for this test:
we only assert that the pipeline wires up the library path correctly and
produces a valid v3 manifest.json with generation_path=="a" and
layerability=="native".
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput


def test_xieyi_layered_e2e_mock(tmp_path):
    inp = PipelineInput(
        subject="远山薄雾",
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="mock",
        layered=True,
        output_dir=str(tmp_path),
    )
    output = asyncio.run(execute(LAYERED, inp))
    assert output is not None

    manifest_path = Path(tmp_path) / "manifest.json"
    assert manifest_path.exists(), "CompositeNode must write manifest.json"
    data = json.loads(manifest_path.read_text())

    assert data["version"] == 3
    assert data["generation_path"] == "a"
    assert data["layerability"] == "native"
    assert len(data.get("layers", [])) > 0
