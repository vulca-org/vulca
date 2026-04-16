"""PlanLayersNode — plan layer structure from intent + tradition knowledge."""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from vulca.pipeline.node import PipelineNode, NodeContext
from vulca.providers.capabilities import LLM_TEXT, provider_capabilities
from vulca.layers.coarse_bucket import is_background
from vulca.layers.types import LayerInfo
from vulca.layers.plan_prompt import build_plan_prompt, get_tradition_layer_order
from vulca.layers.prompt import parse_v2_response

logger = logging.getLogger("vulca.layers")

_DEFAULT_MAX_LAYERS = 10  # legacy cap when ctx.max_layers is unset
_MIN_LAYERS = 2


def _extract_json(text: str) -> dict:
    """Extract and parse JSON from VLM response text."""
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not parse layer plan: {text[:200]}")
    return json.loads(text[start:end + 1])


class PlanLayersNode(PipelineNode):
    """Plan layer structure from intent using VLM or manual specification."""

    name = "plan_layers"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        manual = ctx.get("planned_layers")
        if manual and isinstance(manual, list) and len(manual) > 0:
            layers = manual
        elif ctx.get("source_image_b64"):
            layers = await self._analyze_existing(ctx)
        else:
            layers = await self._plan_from_intent(ctx)

        max_layers = int(ctx.get("max_layers", _DEFAULT_MAX_LAYERS))
        layers = self._validate(layers, ctx.tradition, max_layers)

        return {
            "planned_layers": layers,
            "layer_count": len(layers),
            "tradition_layer_order": [
                o["role"] for o in get_tradition_layer_order(ctx.tradition)
            ],
        }

    async def _plan_from_intent(self, ctx: NodeContext) -> list[LayerInfo]:
        intent = ctx.intent or ctx.subject
        prompt = build_plan_prompt(intent, ctx.tradition)

        if LLM_TEXT not in provider_capabilities(ctx.provider):
            return self._mock_plan(ctx.tradition)

        for attempt in range(3):
            try:
                import litellm
                response = await litellm.acompletion(
                    model=os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash"),
                    messages=[{"role": "user", "content": prompt}],
                    api_key=ctx.api_key or None,
                )
                raw_text = response.choices[0].message.content or ""
                raw_dict = _extract_json(raw_text)
                return parse_v2_response(raw_dict)
            except Exception as exc:
                logger.warning("PlanLayersNode attempt %d failed: %s", attempt + 1, exc)
                if attempt == 2:
                    return self._fallback_layers(ctx.tradition)
        return self._fallback_layers(ctx.tradition)

    async def _analyze_existing(self, ctx: NodeContext) -> list[LayerInfo]:
        from vulca.layers import analyze_layers
        return await analyze_layers(ctx.get("source_image_path", ""), api_key=ctx.api_key)

    def _mock_plan(self, tradition: str) -> list[LayerInfo]:
        order = get_tradition_layer_order(tradition)
        return [
            LayerInfo(
                name=o["role"].replace("/", "_").replace(" ", "_").lower(),
                description=f"Layer: {o['role']}",
                z_index=i,
                content_type=o["content_type"],
                blend_mode=o["blend"],
                tradition_role=o["role"],
            )
            for i, o in enumerate(order)
        ]

    def _fallback_layers(self, tradition: str) -> list[LayerInfo]:
        return self._mock_plan(tradition)

    def _validate(
        self, layers: list[LayerInfo], tradition: str, max_layers: int = _DEFAULT_MAX_LAYERS
    ) -> list[LayerInfo]:
        if len(layers) < _MIN_LAYERS:
            if not any(is_background(l.content_type) for l in layers):
                layers.insert(0, LayerInfo(
                    name="background", description="Background layer",
                    z_index=0, content_type="background",
                ))
            while len(layers) < _MIN_LAYERS:
                layers.append(LayerInfo(
                    name=f"foreground_{len(layers)}",
                    description="Foreground element",
                    z_index=len(layers),
                    content_type="subject",
                ))

        if len(layers) > max_layers:
            layers = sorted(layers, key=lambda l: l.z_index)[:max_layers]

        for i, layer in enumerate(sorted(layers, key=lambda l: l.z_index)):
            layer.z_index = i

        order = get_tradition_layer_order(tradition)
        for layer in layers:
            if not layer.tradition_role and layer.z_index < len(order):
                layer.tradition_role = order[layer.z_index]["role"]

        return layers
