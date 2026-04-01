"""Tests for LayerGenerateNode parallel generation."""
import asyncio
import pytest
from vulca.pipeline.nodes.layer_generate import LayerGenerateNode
from vulca.pipeline.node import NodeContext
from vulca.layers.types import LayerInfo


def _make_ctx(layers, **kwargs):
    ctx = NodeContext(
        subject="mountain",
        intent="山水画",
        tradition="chinese_xieyi",
        provider="mock",
        api_key="",
        round_num=1,
        max_rounds=3,
    )
    ctx.data["planned_layers"] = layers
    for k, v in kwargs.items():
        ctx.data[k] = v
    return ctx


@pytest.mark.asyncio
async def test_layers_generate_all():
    node = LayerGenerateNode()
    layers = [
        LayerInfo(name="bg", description="Background wash", z_index=0, content_type="background"),
        LayerInfo(name="mid", description="Midground subject", z_index=1, content_type="subject"),
        LayerInfo(name="fore", description="Foreground detail", z_index=2, content_type="foreground"),
    ]
    ctx = _make_ctx(layers)

    result = await node.run(ctx)
    assert result["layers_generated"] == 3
    assert result["layers_kept"] == 0
    assert len(result["layer_results"]) == 3
    # Verify sorted by z_index
    z_indices = [r.info.z_index for r in result["layer_results"]]
    assert z_indices == sorted(z_indices)


@pytest.mark.asyncio
async def test_single_layer_no_parallel():
    node = LayerGenerateNode()
    layers = [LayerInfo(name="only", description="Single layer", z_index=0, content_type="background")]
    ctx = _make_ctx(layers)

    result = await node.run(ctx)
    assert result["layers_generated"] == 1
    assert result["layers_kept"] == 0
    assert len(result["layer_results"]) == 1


@pytest.mark.asyncio
async def test_parallel_results_sorted_by_z_index():
    """Remaining layers generated in parallel must be sorted by z_index at the end."""
    node = LayerGenerateNode()
    # Deliberately provide layers in non-z_index order in the 'remaining' pool
    layers = [
        LayerInfo(name="bg", description="Background", z_index=0, content_type="background"),
        LayerInfo(name="fore", description="Foreground", z_index=5, content_type="foreground"),
        LayerInfo(name="mid", description="Midground", z_index=2, content_type="subject"),
    ]
    ctx = _make_ctx(layers)

    result = await node.run(ctx)
    assert result["layers_generated"] == 3
    z_indices = [r.info.z_index for r in result["layer_results"]]
    assert z_indices == sorted(z_indices)


@pytest.mark.asyncio
async def test_empty_layers():
    """Empty layer list returns empty results without error."""
    node = LayerGenerateNode()
    ctx = _make_ctx([])

    result = await node.run(ctx)
    assert result["layers_generated"] == 0
    assert result["layers_kept"] == 0
    assert result["layer_results"] == []


@pytest.mark.asyncio
async def test_two_layers_parallel():
    """With exactly 2 layers: first sequential, second in 'parallel' gather."""
    node = LayerGenerateNode()
    layers = [
        LayerInfo(name="base", description="Base layer", z_index=0, content_type="background"),
        LayerInfo(name="top", description="Top layer", z_index=1, content_type="subject"),
    ]
    ctx = _make_ctx(layers)

    result = await node.run(ctx)
    assert result["layers_generated"] == 2
    assert len(result["layer_results"]) == 2
    names = [r.info.name for r in result["layer_results"]]
    assert set(names) == {"base", "top"}
