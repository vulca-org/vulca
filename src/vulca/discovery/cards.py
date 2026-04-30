"""Direction-card generation for visual discovery."""
from __future__ import annotations

from vulca.discovery.terms import expand_terms
from vulca.discovery.types import (
    DirectionCard,
    EvaluationFocus,
    ProviderTarget,
    TasteProfile,
    VisualOps,
)


def _provider_hint() -> dict[str, ProviderTarget]:
    return {
        "sketch": ProviderTarget(
            provider="gemini", model="gemini-3.1-flash-image-preview"
        ),
        "final": ProviderTarget(provider="openai", model="gpt-image-2"),
        "local": ProviderTarget(provider="comfyui"),
    }


def _card_from_expansion(
    profile: TasteProfile,
    idx: int,
    expansion: dict,
) -> DirectionCard:
    ops = expansion["visual_ops"]
    focus = expansion["evaluation_focus"]
    label = f"{expansion['term']} direction for {profile.domain_primary}"
    return DirectionCard(
        id=f"{profile.slug}-{idx + 1}-{expansion['term'].replace(' ', '-')}",
        label=label,
        summary=(
            f"Use {expansion['term']} as the governing visual idea for "
            f"{profile.initial_intent}."
        ),
        culture_terms=[expansion["term"]],
        visual_ops=VisualOps(
            composition=ops["composition"],
            color=ops["color"],
            texture=ops["texture"],
            lighting="soft diffuse lighting unless the brief asks for drama",
            camera="clear product or subject hierarchy",
            typography="restrained and legible when text is required",
            symbol_strategy=ops["symbol_strategy"],
            avoid=list(ops["avoid"]),
        ),
        provider_hint=_provider_hint(),
        evaluation_focus=EvaluationFocus.from_dict(focus),
        risk=(
            "Direction may become generic if the visual operations are dropped "
            "from the prompt."
        ),
    )


def _fallback_card(
    profile: TasteProfile,
    idx: int,
    label: str,
    composition: str,
) -> DirectionCard:
    return DirectionCard(
        id=f"{profile.slug}-{idx + 1}-{label.lower().replace(' ', '-')}",
        label=label,
        summary=f"A {label.lower()} route for {profile.initial_intent}.",
        culture_terms=list(profile.culture_terms),
        visual_ops=VisualOps(
            composition=composition,
            color="limited palette aligned to the brand and medium",
            texture="material treatment supports the selected direction",
            lighting="clear subject readability",
            camera="stable hierarchy with no accidental crop",
            typography="legible and secondary to the visual concept",
            symbol_strategy="specific visual behavior over decorative symbols",
            avoid=["generic ai aesthetic", "literal cliché symbolism"],
        ),
        provider_hint=_provider_hint(),
        evaluation_focus=EvaluationFocus(
            L1="composition is readable",
            L2="execution supports the visual direction",
            L3="cultural references are grounded",
            L4="interpretation matches the project intent",
            L5="the visual idea has depth beyond styling",
        ),
        risk="Needs a selected culture term or reference to become more specific.",
    )


def generate_direction_cards(
    profile: TasteProfile,
    count: int = 3,
) -> list[DirectionCard]:
    count = max(3, min(count, 5))
    tradition = (
        profile.candidate_traditions[0]
        if profile.candidate_traditions
        else "brand_design"
    )
    expansions = expand_terms(tradition, profile.culture_terms)
    cards = [
        _card_from_expansion(profile, idx, expansion)
        for idx, expansion in enumerate(expansions)
    ]

    fallback_specs = [
        (
            "Commercial clarity",
            "large readable subject, product-first hierarchy, high scan speed",
        ),
        ("Editorial atmosphere", "more negative space, slower reading, stronger mood"),
        ("Modern restraint", "simple geometry, low ornament, sharp hierarchy"),
    ]
    while len(cards) < count:
        label, composition = fallback_specs[len(cards) % len(fallback_specs)]
        cards.append(_fallback_card(profile, len(cards), label, composition))

    return cards[:count]
