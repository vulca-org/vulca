import asyncio
import base64
import io

from PIL import Image

from vulca.layers.types import LayerInfo
from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.layer_generate import LayerGenerateNode


class _FakePNGProvider:
    id = "fake"
    model = "fake-1"

    async def generate(self, *, prompt, raw_prompt=False, reference_image_b64=None, **kw):
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def _ctx(tradition, output_dir):
    ctx = NodeContext(tradition=tradition, provider="fake", api_key="", round_num=1)
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
    ctx.set("output_dir", str(output_dir))
    return ctx


def test_native_tradition_routes_through_library(tmp_path, monkeypatch):
    """When tradition has layerability=native, the node uses layered_generate."""
    called = {"used_library": False}
    from vulca.layers import layered_generate as lg_mod
    real_fn = lg_mod.layered_generate

    async def spy(**kw):
        called["used_library"] = True
        return await real_fn(**kw)

    monkeypatch.setattr(lg_mod, "layered_generate", spy)

    node = LayerGenerateNode()
    asyncio.run(node.run(_ctx("chinese_xieyi", tmp_path)))
    assert called["used_library"]
