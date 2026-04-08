"""Anchored layer prompt builder — Defense layer 1 of consistency strategy.

Wraps the plan's regeneration_prompt in four mandatory anchor blocks:
canvas, content (with negative list), spatial, style. Pure function.
"""
from __future__ import annotations

from dataclasses import dataclass

from vulca.layers.types import LayerInfo


@dataclass(frozen=True)
class TraditionAnchor:
    canvas_color_hex: str
    canvas_description: str
    style_keywords: str


def build_anchored_layer_prompt(
    layer: LayerInfo,
    *,
    anchor: TraditionAnchor,
    sibling_roles: list[str],
    position: str = "",
    coverage: str = "",
) -> str:
    """Build a fully anchored prompt for one layer of a layered artwork.

    sibling_roles is the full list of layer roles in the plan (this layer's
    role is filtered out automatically when building the negative list).
    """
    own_role = layer.tradition_role or layer.name
    others = [r for r in sibling_roles if r and r != own_role]
    others_text = ", ".join(others) if others else "(none)"

    pos = position or "wherever the user intent specifies"
    cov = coverage or "as the user intent specifies"

    user_intent = layer.regeneration_prompt or layer.description or own_role

    blocks = [
        "[CANVAS ANCHOR]",
        f"The image MUST be drawn on {anchor.canvas_description}.",
        f"The background MUST be the pure canvas color {anchor.canvas_color_hex},",
        "with absolutely no other elements, textures, shading, or borders on the background.",
        "",
        "[CONTENT ANCHOR — exclusivity]",
        f"This image ONLY contains the element specified in USER INTENT.",
        f"Do NOT include any of: {others_text}.",
        "",
        "[SPATIAL ANCHOR]",
        f"MUST occupy {pos}, covering approximately {cov} of the canvas area.",
        "Do NOT extend beyond this region.",
        "",
        "[STYLE ANCHOR]",
        anchor.style_keywords,
        "",
        "[USER INTENT]",
        user_intent,
    ]
    return "\n".join(blocks)
