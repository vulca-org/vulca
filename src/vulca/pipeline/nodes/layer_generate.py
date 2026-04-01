"""LayerGenerateNode — per-layer generation with style consistency."""
from __future__ import annotations

import base64
import io
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

from vulca.pipeline.node import PipelineNode, NodeContext
from vulca.layers.types import LayerInfo, LayerResult


class LayerGenerateNode(PipelineNode):
    """Generate each layer as a full-scene image focused on that layer's content."""

    name = "layer_generate"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        layers: list[LayerInfo] = ctx.get("planned_layers", [])
        round_num = ctx.round_num or 1
        layer_decisions: dict[str, str] = ctx.get("layer_decisions", {})
        prev_results: list[LayerResult] = ctx.get("layer_results", [])

        prev_map = {r.info.name: r for r in prev_results}

        to_generate = []
        kept = []
        for info in sorted(layers, key=lambda l: l.z_index):
            decision = layer_decisions.get(info.name, "rerun")
            if round_num > 1 and decision == "accept" and info.name in prev_map:
                kept.append(prev_map[info.name])
            else:
                to_generate.append(info)

        new_results = await self._generate_layers(to_generate, ctx)
        all_results = sorted(kept + new_results, key=lambda r: r.info.z_index)

        return {
            "layer_results": all_results,
            "layers_generated": len(new_results),
            "layers_kept": len(kept),
        }

    async def _generate_layers(
        self, layers: list[LayerInfo], ctx: NodeContext
    ) -> list[LayerResult]:
        results = []
        output_dir = ctx.get("output_dir", tempfile.mkdtemp(prefix="vulca_layered_"))
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        style_ref = ctx.get("composite_b64") or ctx.get("image_b64")

        for info in layers:
            try:
                result = await self._generate_single(info, ctx, output_dir, style_ref)
                results.append(result)
                if style_ref is None and result.image_path:
                    style_ref = _path_to_b64(result.image_path)
            except Exception:
                info.status = "failed"
                results.append(LayerResult(info=info, image_path=""))
        return results

    async def _generate_single(
        self, info: LayerInfo, ctx: NodeContext, output_dir: str, style_ref: str | None,
    ) -> LayerResult:
        prompt = self._build_prompt(info, ctx)

        if ctx.provider == "mock":
            return self._mock_generate(info, output_dir, ctx)

        from vulca.providers import get_provider
        provider = ctx.image_provider or get_provider(ctx.provider, api_key=ctx.api_key)

        kwargs: dict[str, Any] = {"prompt": prompt}
        if style_ref:
            kwargs["reference_image"] = style_ref

        img_b64 = await provider.generate(**kwargs)

        out_path = str(Path(output_dir) / f"{info.name}.png")
        img_data = base64.b64decode(img_b64)
        Image.open(io.BytesIO(img_data)).save(out_path)

        info.status = "accepted"
        info.generation_round = ctx.round_num or 1
        return LayerResult(info=info, image_path=out_path)

    def _build_prompt(self, info: LayerInfo, ctx: NodeContext) -> str:
        intent = ctx.intent or ctx.subject
        base = info.regeneration_prompt or info.description
        prompt = (
            f"Complete scene: {intent}. "
            f"Focus on rendering the {info.name} ({base}) with exceptional detail. "
            f"Other elements may be simplified or absent."
        )
        weakness = info.weakness or ctx.get("improvement_focus", "")
        if weakness:
            prompt += f" Improvement focus: {weakness}"
        return prompt

    def _mock_generate(self, info: LayerInfo, output_dir: str, ctx: NodeContext) -> LayerResult:
        colors = {
            "background": (240, 230, 220),
            "atmosphere": (180, 190, 200),
            "subject": (100, 120, 100),
            "text": (30, 30, 30),
            "effect": (200, 200, 220),
        }
        color = colors.get(info.content_type, (128, 128, 128))
        img = Image.new("RGB", (64, 64), color)
        out_path = str(Path(output_dir) / f"{info.name}.png")
        img.save(out_path)
        info.status = "accepted"
        info.generation_round = ctx.round_num or 1
        return LayerResult(info=info, image_path=out_path)


def _path_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
