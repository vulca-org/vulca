import asyncio
import base64
import io
import json
from pathlib import Path

from PIL import Image

from vulca.layers.types import LayerInfo
from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.composite_node import CompositeNode
from vulca.pipeline.nodes.layer_generate import LayerGenerateNode


class _FakePNGProvider:
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


async def _run_native(tmp_path):
    ctx = NodeContext(tradition="chinese_xieyi", provider="fake", api_key="", round_num=1)
    ctx.image_provider = _FakePNGProvider()
    ctx.set("planned_layers", [
        LayerInfo(name="bg", description="paper", z_index=0,
                  content_type="background", tradition_role="纸"),
        LayerInfo(name="far", description="far mtns", z_index=1,
                  content_type="subject", tradition_role="远景淡墨",
                  regeneration_prompt="distant mountains"),
    ])
    ctx.set("layer_decisions", {})
    ctx.set("layer_results", [])
    ctx.set("output_dir", str(tmp_path))

    gen_out = await LayerGenerateNode().run(ctx)
    ctx.set("layer_results", gen_out["layer_results"])

    await CompositeNode().run(ctx)


def test_layered_manifest_records_native_metadata(tmp_path):
    asyncio.run(_run_native(tmp_path))
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["version"] == 3
    assert manifest["generation_path"] == "a"
    assert manifest["layerability"] == "native"
    assert manifest["partial"] is False
    # Per-layer extras: source=a, cache_hit/attempts/validation populated
    layers = {l["name"]: l for l in manifest["layers"]}
    assert "far" in layers
    far = layers["far"]
    assert far.get("source") == "a"
    assert "attempts" in far
    assert "validation" in far
    # P0.1 #3: A-path extras always record canvas_color and key_strategy.
    assert far.get("canvas_color") == "#ffffff"
    assert far.get("key_strategy") == "luminance"
