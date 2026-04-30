from __future__ import annotations

import pytest


def test_direction_card_to_dict_round_trip():
    from vulca.discovery.types import (
        DirectionCard,
        EvaluationFocus,
        ProviderTarget,
        VisualOps,
    )

    card = DirectionCard(
        id="song-negative-space-premium-tea",
        label="Song negative space + premium tea restraint",
        summary="Quiet premium tea direction.",
        culture_terms=["reserved white space", "spirit resonance and vitality"],
        visual_ops=VisualOps(
            composition="large negative space, off-center subject",
            color="warm off-white, ink gray",
            texture="subtle rice paper grain",
            lighting="soft diffuse",
            camera="front-facing product hierarchy",
            typography="small restrained serif",
            symbol_strategy="abstract atmosphere over literal icons",
            avoid=["dragon motifs", "busy ornament"],
        ),
        provider_hint={
            "sketch": ProviderTarget(
                provider="gemini", model="gemini-3.1-flash-image-preview"
            ),
            "final": ProviderTarget(provider="openai", model="gpt-image-2"),
            "local": ProviderTarget(provider="comfyui"),
        },
        evaluation_focus=EvaluationFocus(
            L1="negative space reads intentional",
            L2="texture stays subtle",
            L3="xieyi terms are respected",
            L4="not a generic luxury ad",
            L5="quietness creates resonance",
        ),
        risk="May be too quiet for high-conversion social ads.",
    )

    payload = card.to_dict()

    assert payload["provider_hint"]["final"]["provider"] == "openai"
    assert payload["provider_hint"]["final"]["model"] == "gpt-image-2"
    assert payload["visual_ops"]["avoid"] == ["dragon motifs", "busy ornament"]
    assert DirectionCard.from_dict(payload).to_dict() == payload


def test_provider_target_rejects_unknown_provider():
    from vulca.discovery.types import ProviderTarget

    with pytest.raises(ValueError, match="unknown provider"):
        ProviderTarget(provider="midjourney")


def test_sketch_prompt_requires_known_provider():
    from vulca.discovery.types import SketchPrompt

    prompt = SketchPrompt(
        card_id="card-a",
        provider="mock",
        model="",
        prompt="quiet tea packaging",
        negative_prompt="busy ornament",
        size="1024x1024",
        purpose="thumbnail exploration",
    )

    assert prompt.to_dict()["provider"] == "mock"

    with pytest.raises(ValueError, match="unknown provider"):
        SketchPrompt(
            card_id="card-a",
            provider="unknown",
            model="",
            prompt="quiet tea packaging",
            negative_prompt="",
            size="1024x1024",
            purpose="thumbnail exploration",
        )
