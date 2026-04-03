"""LayerGenerateNode — per-layer generation with style consistency."""
from __future__ import annotations

import asyncio
import base64
import io
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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
        if not layers:
            return []

        output_dir = ctx.get("output_dir") or tempfile.mkdtemp(prefix="vulca_layered_")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        style_ref = ctx.get("composite_b64") or ctx.get("image_b64") or ""

        # Phase 1: Generate first layer (provides style reference for others)
        first = layers[0]
        first_result = await self._generate_single(first, ctx, output_dir, style_ref or None)
        if first_result.image_path and not style_ref:
            style_ref = _path_to_b64(first_result.image_path)

        if len(layers) <= 1:
            return [first_result]

        # Phase 2: Generate remaining layers in parallel with rate limiting
        remaining = layers[1:]
        max_concurrent = int(os.environ.get("VULCA_MAX_LAYER_CONCURRENCY", "3"))
        sem = asyncio.Semaphore(max_concurrent)

        async def _gen_with_limit(info: LayerInfo) -> LayerResult:
            async with sem:
                try:
                    return await self._generate_single(info, ctx, output_dir, style_ref or None)
                except Exception as e:
                    logger.warning("Layer %s failed: %s", info.name, e)
                    info.status = "failed"
                    return LayerResult(info=info, image_path="")

        parallel_results = await asyncio.gather(*[_gen_with_limit(info) for info in remaining])

        all_results = [first_result] + list(parallel_results)
        return sorted(all_results, key=lambda r: r.info.z_index)

    async def _generate_single(
        self, info: LayerInfo, ctx: NodeContext, output_dir: str, style_ref: str | None,
    ) -> LayerResult:
        prompt = self._build_prompt(info, ctx)

        if ctx.provider == "mock":
            return self._mock_generate(info, output_dir, ctx)

        from vulca.providers import get_image_provider
        provider_instance = ctx.image_provider or get_image_provider(
            ctx.provider, api_key=ctx.api_key
        )

        kwargs: dict[str, Any] = {"prompt": prompt, "raw_prompt": True}
        if style_ref:
            kwargs["reference_image_b64"] = style_ref

        result = await provider_instance.generate(**kwargs)
        img_b64 = result.image_b64 if hasattr(result, 'image_b64') else result

        out_path = str(Path(output_dir) / f"{info.name}.png")
        img_data = base64.b64decode(img_b64)
        Image.open(io.BytesIO(img_data)).save(out_path)

        info.status = "accepted"
        info.generation_round = ctx.round_num or 1
        return LayerResult(info=info, image_path=out_path)

    def _build_prompt(self, info: LayerInfo, ctx: NodeContext) -> str:
        """Build prompt for isolated layer generation.

        Uses "Digital design asset" framing instead of "Generate artwork" —
        this prevents Gemini from adding paper textures, scroll mountings,
        and environmental context that break layer compositing.
        """
        base = info.regeneration_prompt or info.description

        # Get other layer names to explicitly exclude
        all_layers: list[LayerInfo] = ctx.get("planned_layers", [])
        other_names = [l.name for l in all_layers if l.name != info.name]

        # Select background color based on blend mode:
        # - white for normal/multiply (white is identity for multiply)
        # - black for screen (black is identity for screen)
        if info.blend_mode == "screen":
            bg_instruction = "Isolated element on pure black (#000000) background."
        else:
            bg_instruction = "Isolated element on pure white (#FFFFFF) background."

        parts = [
            f"Digital design asset for layer compositing. {base}",
            bg_instruction,
            "No environment, no paper texture, no borders, no frames, no scroll.",
            "Flat 2D, 1024x1024.",
        ]

        # Inject position/size constraint if not already in regeneration_prompt
        _POSITION_DEFAULTS = {
            "atmosphere": "Position: upper portion of canvas, covering 15-25%.",
            "effect": "Position: overlay effect, covering 10-20%.",
            "subject": "Position: center or lower portion of canvas, covering 20-35%.",
            "text": "Position: small, in a corner of canvas, covering at most 5-10%.",
            "detail": "Position: focal area only, covering 5-15%.",
            "line_art": "Position: full canvas outline.",
            "decoration": "Position: accent areas, covering 5-15%.",
        }
        has_position = any(kw in base.lower() for kw in [
            "position", "upper", "lower", "corner", "center", "covering", "% of canvas",
        ])
        if not has_position and info.content_type != "background":
            pos = _POSITION_DEFAULTS.get(info.content_type, "")
            if pos:
                parts.append(pos)

        if other_names:
            names_str = ", ".join(other_names)
            parts.append(f"DO NOT include elements from: {names_str}.")

        weakness = info.weakness or ctx.get("improvement_focus", "")
        if weakness:
            parts.append(f"Improvement focus: {weakness}")

        return " ".join(parts)

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
