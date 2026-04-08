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

        from vulca.cultural.loader import get_tradition
        try:
            trad = get_tradition(ctx.tradition or "default")
        except Exception:
            trad = None
        layerability = getattr(trad, "layerability", "split") if trad else "split"

        if layerability == "native":
            return await self._generate_layers_native(layers, ctx, trad)
        return await self._generate_layers_legacy(layers, ctx)

    async def _generate_layers_legacy(
        self, layers: list[LayerInfo], ctx: NodeContext
    ) -> list[LayerResult]:
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

    async def _generate_layers_native(
        self, layers: list[LayerInfo], ctx: NodeContext, trad
    ) -> list[LayerResult]:
        from vulca.layers import layered_generate as lg_mod
        from vulca.layers.layered_prompt import TraditionAnchor
        from vulca.layers.keying import CanvasSpec

        output_dir = ctx.get("output_dir") or tempfile.mkdtemp(prefix="vulca_layered_")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        canvas_hex = getattr(trad, "canvas_color", "#ffffff") or "#ffffff"
        anchor = TraditionAnchor(
            canvas_color_hex=canvas_hex,
            canvas_description=getattr(trad, "canvas_description", "") or "white canvas",
            style_keywords=getattr(trad, "style_keywords", "") or "",
        )
        canvas = CanvasSpec.from_hex(canvas_hex)
        key_strategy_name = getattr(trad, "key_strategy", "luminance") or "luminance"

        positions: dict[str, str] = {l.name: getattr(l, "_position", "") for l in layers}
        coverages: dict[str, str] = {l.name: getattr(l, "_coverage", "") for l in layers}

        cache_enabled = not bool(ctx.get("no_cache", False))

        from vulca.providers import get_image_provider
        provider_instance = ctx.image_provider or get_image_provider(
            ctx.provider, api_key=ctx.api_key
        )

        result = await lg_mod.layered_generate(
            plan=layers,
            tradition_anchor=anchor,
            canvas=canvas,
            key_strategy_name=key_strategy_name,
            provider=provider_instance,
            output_dir=output_dir,
            positions=positions,
            coverages=coverages,
            parallelism=int(os.environ.get("VULCA_LAYERED_PARALLELISM", "4")),
            cache_enabled=cache_enabled,
        )

        out: list[LayerResult] = []
        for o in result.layers:
            o.info.status = "accepted"
            o.info.generation_round = ctx.round_num or 1
            out.append(LayerResult(info=o.info, image_path=o.rgba_path))
        for f in result.failed:
            for l in layers:
                if l.id == f.layer_id:
                    l.status = "failed"
                    l.weakness = f.reason
                    out.append(LayerResult(info=l, image_path=""))
                    break

        try:
            ctx.set("layered_result", result)
        except Exception:
            pass

        # P0 #4: --strict mode — any failed layer fails the whole run.
        if ctx.get("strict", False) and result.failed:
            names = ", ".join(f.role for f in result.failed)
            raise RuntimeError(
                f"strict mode: {len(result.failed)} layer(s) failed ({names})"
            )

        return sorted(out, key=lambda r: r.info.z_index)

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

        # Step 1: Generate content
        kwargs: dict[str, Any] = {"prompt": prompt, "raw_prompt": True}
        if style_ref:
            kwargs["reference_image_b64"] = style_ref

        result = await provider_instance.generate(**kwargs)
        content_b64 = result.image_b64 if hasattr(result, 'image_b64') else result

        out_path = str(Path(output_dir) / f"{info.name}.png")
        img_data = base64.b64decode(content_b64)
        content_img = Image.open(io.BytesIO(img_data))

        # Step 2: Generate mask (skip for background — it's fully opaque)
        if info.content_type != "background":
            content_img = await self._apply_mask(
                content_img, content_b64, provider_instance, info,
            )

        content_img.save(out_path)

        info.status = "accepted"
        info.generation_round = ctx.round_num or 1
        return LayerResult(info=info, image_path=out_path)

    async def _apply_mask(
        self,
        content_img: Image.Image,
        content_b64: str,
        provider,
        info: LayerInfo,
    ) -> Image.Image:
        """Two-pass alpha: generate mask from content image, apply as alpha.

        Uses the shared vlm_mask module (same logic as split_regenerate).
        """
        from vulca.layers.vlm_mask import apply_vlm_mask, VLM_MASK_PROMPT

        try:
            mask_result = await provider.generate(
                prompt=VLM_MASK_PROMPT,
                raw_prompt=True,
                reference_image_b64=content_b64,
            )
            mask_b64 = mask_result.image_b64 if hasattr(mask_result, 'image_b64') else mask_result
            mask_img = Image.open(io.BytesIO(base64.b64decode(mask_b64)))
            mask_gray = mask_img.convert("L")
            return apply_vlm_mask(content_img, mask_gray)
        except Exception as exc:
            logger.warning("Mask generation failed for %s: %s — falling back to RGB", info.name, exc)
            return content_img

    def _build_prompt(self, info: LayerInfo, ctx: NodeContext) -> str:
        """Build prompt for isolated layer generation.

        Background layers get a texture-only prompt (no scene content).
        Non-background layers get "Digital design asset" framing.
        """
        # Get other layer names to explicitly exclude
        all_layers: list[LayerInfo] = ctx.get("planned_layers", [])
        other_names = [l.name for l in all_layers if l.name != info.name]

        # Background layer: texture only, override any VLM-planned scene content
        if info.content_type == "background":
            tradition = ctx.tradition or "default"
            _MEDIUM = {
                "chinese_xieyi": "warm-toned aged xuan rice paper with subtle fiber texture",
                "chinese_gongbi": "smooth sized silk with fine weave texture",
                "japanese_traditional": "traditional washi paper texture",
                "watercolor": "cold-pressed watercolor paper with visible grain",
                "photography": "neutral matte surface",
            }
            medium = _MEDIUM.get(tradition, "plain paper texture")
            parts = [
                f"Digital design asset for layer compositing. ONLY the base medium texture: {medium}.",
                "Do NOT include ANY scene elements: no mountains, no trees, no buildings, no water, no figures, no landscape.",
                "Pure texture filling the entire canvas.",
                "Flat 2D, 1024x1024.",
            ]
            return " ".join(parts)

        base = info.regeneration_prompt or info.description

        # Select background color based on blend mode
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
