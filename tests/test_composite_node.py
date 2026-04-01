"""Tests for CompositeNode — blend layers + write Artifact V3."""
import pytest
import json
from pathlib import Path
from PIL import Image

from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.composite_node import CompositeNode
from vulca.layers.types import LayerInfo, LayerResult


def _make_layer_results(tmp_path):
    results = []
    for i, (name, color) in enumerate([("bg", (240, 230, 220)), ("fg", (100, 120, 100))]):
        info = LayerInfo(name=name, description=name, z_index=i, content_type="background" if i == 0 else "subject")
        img = Image.new("RGBA", (64, 64), color + (255,))
        path = str(tmp_path / f"{name}.png")
        img.save(path)
        results.append(LayerResult(info=info, image_path=path))
    return results


class TestCompositeNode:
    @pytest.mark.asyncio
    async def test_composites_and_writes_artifact(self, tmp_path):
        node = CompositeNode()
        results = _make_layer_results(tmp_path)
        ctx = NodeContext(intent="test", tradition="default")
        ctx.set("layer_results", results)
        ctx.set("output_dir", str(tmp_path))
        ctx.set("size", "64x64")

        output = await node.run(ctx)

        assert output["composite_path"]
        assert Path(output["composite_path"]).exists()
        assert output["artifact_path"]
        assert Path(output["artifact_path"]).exists()
        assert "image_b64" in output
        assert output["failed_layers"] == []

        data = json.loads(Path(output["artifact_path"]).read_text())
        assert data["artifact_version"] == "3.0"
        assert len(data["layers"]) == 2

    @pytest.mark.asyncio
    async def test_skips_failed_layers(self, tmp_path):
        node = CompositeNode()
        results = _make_layer_results(tmp_path)
        failed = LayerResult(
            info=LayerInfo(name="broken", description="broken", z_index=2),
            image_path="",
        )
        results.append(failed)
        ctx = NodeContext(intent="test", tradition="default")
        ctx.set("layer_results", results)
        ctx.set("output_dir", str(tmp_path))
        ctx.set("size", "64x64")

        output = await node.run(ctx)
        assert "broken" in output["failed_layers"]
        assert Path(output["composite_path"]).exists()
