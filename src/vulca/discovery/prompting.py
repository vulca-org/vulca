"""Prompt composition for visual discovery direction cards."""
from __future__ import annotations

from vulca.discovery.types import DirectionCard, PromptArtifact


def _join_nonempty(parts: list[str], sep: str = ". ") -> str:
    return sep.join(part.strip() for part in parts if part and part.strip())


def compose_prompt_from_direction_card(
    card: DirectionCard,
    target: str = "final",
) -> PromptArtifact:
    provider_target = card.provider_hint.get(target)
    if provider_target is None:
        raise ValueError(f"unknown provider target: {target!r}")

    ops = card.visual_ops
    base_parts = [
        card.summary,
        f"Composition: {ops.composition}",
        f"Color: {ops.color}",
        f"Texture/material: {ops.texture}",
        f"Lighting: {ops.lighting}",
        f"Camera/layout: {ops.camera}",
        f"Typography: {ops.typography}",
        f"Symbol strategy: {ops.symbol_strategy}",
        f"Culture terms: {', '.join(card.culture_terms)}",
    ]
    if target == "sketch":
        base_parts.insert(
            0,
            "Create an exploratory thumbnail for visual direction comparison",
        )
    elif target == "local":
        base_parts = [
            "CLIP-friendly local generation prompt",
            card.summary,
            ops.composition,
            ops.color,
            ops.texture,
            ops.symbol_strategy,
            f"Culture terms: {', '.join(card.culture_terms)}",
        ]
    else:
        base_parts.insert(0, "Create a high-fidelity commercial visual candidate")

    return PromptArtifact(
        provider=provider_target.provider,
        model=provider_target.model,
        prompt=_join_nonempty(base_parts),
        negative_prompt=", ".join(card.visual_ops.avoid),
        source_card_id=card.id,
    )
