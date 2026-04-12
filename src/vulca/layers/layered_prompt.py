"""Anchored layer prompt builder — Defense layer 1 of consistency strategy.

Wraps the plan's regeneration_prompt in four mandatory anchor blocks:
canvas, content (with negative list), spatial, style. Pure function.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from vulca.layers.types import LayerInfo


@dataclass(frozen=True)
class TraditionAnchor:
    canvas_color_hex: str
    canvas_description: str
    style_keywords: str


_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")
_CJK_PAREN_RE = re.compile(r"\s*\([^)]*[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af][^)]*\)")


def _strip_cjk_parenthetical(text: str) -> str:
    """Strip CJK parenthetical annotations, e.g. 'cooked silk (熟绢)' → 'cooked silk'."""
    return _CJK_PAREN_RE.sub("", text).strip()


def _is_ascii_latin(text: str) -> bool:
    """Return True if text contains no CJK characters."""
    return not bool(_CJK_RE.search(text))


def _strip_cjk_chars(text: str) -> str:
    """Remove CJK characters from text, keeping ASCII/Latin portions."""
    return _CJK_RE.sub("", text).strip()


def build_anchored_layer_prompt(
    layer: LayerInfo,
    *,
    anchor: TraditionAnchor,
    sibling_roles: list[str],
    position: str = "",
    coverage: str = "",
    english_only: bool = False,
) -> str:
    """Build a fully anchored prompt for one layer of a layered artwork.

    sibling_roles is the full list of layer roles in the plan (this layer's
    role is filtered out automatically when building the negative list).
    """
    canvas_description = anchor.canvas_description
    style_keywords = anchor.style_keywords
    effective_siblings = list(sibling_roles)
    own_role = layer.tradition_role or layer.name

    if english_only:
        canvas_description = _strip_cjk_parenthetical(canvas_description)
        style_keywords = ", ".join(
            kw.strip() for kw in style_keywords.split(",")
            if kw.strip() and _is_ascii_latin(kw.strip())
        ) or style_keywords  # fallback to original if all keywords are CJK
        effective_siblings = [
            _strip_cjk_parenthetical(r) for r in sibling_roles
            if _strip_cjk_parenthetical(r)
        ]
        own_role = _strip_cjk_parenthetical(own_role)

    others = [r for r in effective_siblings if r and r != own_role]
    others_text = ", ".join(others) if others else "(none)"

    pos = position or "wherever the user intent specifies"
    cov = coverage or "as the user intent specifies"

    user_intent = layer.regeneration_prompt or layer.description or own_role
    if english_only and not _is_ascii_latin(user_intent):
        user_intent = _strip_cjk_parenthetical(user_intent)

    blocks = [
        "[CANVAS ANCHOR]",
        f"The image MUST be drawn on {canvas_description}.",
        f"The background MUST be the pure canvas color {anchor.canvas_color_hex},",
        "with absolutely no other elements, textures, shading, or borders on the background.",
        "",
        "[CONTENT ANCHOR — exclusivity]",
        "This image ONLY contains the element specified in USER INTENT.",
        f"Do NOT include any of: {others_text}.",
        "",
        "[SPATIAL ANCHOR]",
        f"MUST occupy {pos}, covering approximately {cov} of the canvas area.",
        "Do NOT extend beyond this region.",
        "",
        "[STYLE ANCHOR]",
        style_keywords,
        "",
        "[USER INTENT]",
        user_intent,
    ]
    return "\n".join(blocks)
