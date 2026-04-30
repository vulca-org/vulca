"""Artifact writing for visual discovery sessions."""
from __future__ import annotations

import json
from pathlib import Path

from vulca.discovery.types import DirectionCard, TasteProfile


def _project_dir(root: Path, slug: str) -> Path:
    return root / "docs" / "visual-specs" / slug / "discovery"


def build_brainstorm_handoff(profile: TasteProfile, card: DirectionCard) -> str:
    brief = (
        f"{profile.initial_intent}; selected direction: {card.label}; "
        f"visual operations: {card.visual_ops.composition}; "
        f"avoid: {', '.join(card.visual_ops.avoid)}; "
        f"domain: {profile.domain_primary}."
    )
    return f"Ready for /visual-brainstorm. Suggested topic:\n\"{brief}\""


def _discovery_markdown(
    title: str,
    original_intent: str,
    profile: TasteProfile,
    cards: list[DirectionCard],
    recommended_card_id: str,
) -> str:
    card_lines = "\n".join(
        f"- `{card.id}`: {card.label} - {card.summary}" for card in cards
    )
    selected = next((card for card in cards if card.id == recommended_card_id), None)
    selected_text = selected.label if selected else "none"
    return f"""# Visual Discovery: {title}

## Status
ready_for_brainstorm

## Original Intent
{original_intent}

## Scope Decision
accepted

## Uncertainty
{profile.confidence}

## Taste Profile Summary
Domain: {profile.domain_primary}. Traditions: {", ".join(profile.candidate_traditions)}.

## Direction Cards
{card_lines}

## User Preference Signals
recommended: {recommended_card_id}

## Recommended Direction
{selected_text}

## Handoff
{build_brainstorm_handoff(profile, selected or cards[0])}

## Notes
generated_by: visual-discovery@0.1.0
"""


def write_discovery_artifacts(
    *,
    root: str | Path,
    slug: str,
    title: str,
    original_intent: str,
    profile: TasteProfile,
    cards: list[DirectionCard],
    recommended_card_id: str,
) -> dict[str, str]:
    root_path = Path(root)
    out_dir = _project_dir(root_path, slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    discovery_md = out_dir / "discovery.md"
    taste_profile_json = out_dir / "taste_profile.json"
    direction_cards_json = out_dir / "direction_cards.json"

    discovery_md.write_text(
        _discovery_markdown(
            title,
            original_intent,
            profile,
            cards,
            recommended_card_id,
        ),
        encoding="utf-8",
    )
    taste_profile_json.write_text(
        json.dumps(profile.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    direction_cards_json.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "slug": slug,
                "cards": [card.to_dict() for card in cards],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "discovery_md": str(discovery_md),
        "taste_profile_json": str(taste_profile_json),
        "direction_cards_json": str(direction_cards_json),
    }
