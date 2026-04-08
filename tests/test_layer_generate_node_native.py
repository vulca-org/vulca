import asyncio

from vulca.layers.types import LayerInfo
from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.layer_generate import LayerGenerateNode


def _ctx(tradition, output_dir):
    ctx = NodeContext(tradition=tradition, provider="mock", api_key="", round_num=1)
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
