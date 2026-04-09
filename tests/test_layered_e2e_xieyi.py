"""A-path end-to-end test on chinese_xieyi with an injected fake PNG provider.

The built-in mock provider returns SVG, so native dispatch falls back to the
legacy VLM-mask path for it (P0 #5). To verify the A-path end-to-end we
monkeypatch `get_image_provider` to return a fake provider that emits real
PNG bytes.
"""
from __future__ import annotations

import asyncio
import base64
import io
import json
from pathlib import Path

from PIL import Image

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput


class _FakePNG:
    id = "fake"
    model = "fake-1"
    capabilities = frozenset({"raw_rgba"})

    async def generate(self, *, prompt, raw_prompt=False, reference_image_b64=None, **kw):
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def test_xieyi_layered_e2e_mock(tmp_path, monkeypatch):
    import vulca.providers as providers_mod
    import vulca.pipeline.nodes.layer_generate as lg_mod
    from vulca.pipeline.nodes.plan_layers import PlanLayersNode
    monkeypatch.setattr(providers_mod, "get_image_provider",
                        lambda *a, **k: _FakePNG())
    # Let _provider_supports_native find raw_rgba via the class lookup.
    monkeypatch.setattr(lg_mod, "_lookup_provider_class", lambda name: _FakePNG)
    # Avoid real litellm calls — use the built-in mock plan instead.
    async def _mock_plan_from_intent(self, ctx):
        return self._mock_plan(ctx.tradition)
    monkeypatch.setattr(PlanLayersNode, "_plan_from_intent", _mock_plan_from_intent)

    inp = PipelineInput(
        subject="远山薄雾",
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="fake",
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
