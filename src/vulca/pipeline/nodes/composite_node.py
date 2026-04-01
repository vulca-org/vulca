"""CompositeNode — blend layers into composite + write Artifact V3."""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from vulca.pipeline.node import PipelineNode, NodeContext
from vulca.layers.types import LayerResult
from vulca.layers.composite import composite_layers
from vulca.layers.artifact import write_artifact_v3


class CompositeNode(PipelineNode):
    """Blend all layers → composite image + Artifact V3 document."""

    name = "composite"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        layer_results: list[LayerResult] = ctx.get("layer_results", [])
        import tempfile
        output_dir = ctx.get("output_dir", tempfile.mkdtemp(prefix="vulca_composite_"))
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        size = ctx.get("size", "1024x1024")
        w, h = _parse_size(size)

        valid = [r for r in layer_results if r.image_path and Path(r.image_path).exists()]
        failed = [r for r in layer_results if not r.image_path or not Path(r.image_path).exists()]

        composite_path = str(Path(output_dir) / "composite.png")
        if valid:
            composite_layers(valid, width=w, height=h, output_path=composite_path)
        else:
            from PIL import Image
            Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(composite_path)

        with open(composite_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        # Build cultural context from pipeline data
        cultural_context = ctx.get("cultural_context")
        if not cultural_context:
            tradition_order = ctx.get("tradition_layer_order", [])
            cultural_context = {}
            if tradition_order:
                cultural_context["tradition_layer_order"] = tradition_order

        # Build rounds history
        rounds_history = ctx.get("rounds_history", [])
        if not rounds_history:
            rounds_history = [{
                "round": ctx.round_num or 1,
                "layers_generated": [r.info.name for r in layer_results if r.image_path],
                "layers_kept": [],
                "decision": "pending",
            }]

        # Collect per-layer scores
        layer_scores = {r.info.name: r.scores for r in layer_results if r.scores}

        artifact_path = write_artifact_v3(
            layers=[r.info for r in layer_results],
            output_dir=output_dir,
            width=w, height=h,
            intent=ctx.intent or ctx.subject,
            tradition=ctx.tradition,
            composite_file="composite.png",
            composite_scores=ctx.get("composite_scores"),
            cultural_context=cultural_context,
            rounds=rounds_history,
            session_id=ctx.get("session_id", ""),
            layer_scores=layer_scores,
        )

        return {
            "image_b64": image_b64,
            "composite_path": composite_path,
            "artifact_path": artifact_path,
            "failed_layers": [r.info.name for r in failed],
        }


def _parse_size(size: str) -> tuple[int, int]:
    if "x" in size:
        parts = size.split("x")
        return int(parts[0]), int(parts[1])
    s = int(size)
    return s, s
