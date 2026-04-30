"""Artifact writing for visual discovery sessions."""
from __future__ import annotations

import json
import re
from pathlib import Path

from vulca.discovery.types import DirectionCard, SketchPrompt, TasteProfile


_SAFE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _validate_slug(slug: str) -> str:
    if (
        not slug
        or slug in {".", ".."}
        or "/" in slug
        or "\\" in slug
        or ".." in slug
        or Path(slug).is_absolute()
        or not _SAFE_SLUG_RE.match(slug)
    ):
        raise ValueError(
            "slug must be a safe project id using lowercase letters, digits, '.', '_' or '-'"
        )
    return slug


def _project_dir(root: Path, slug: str) -> Path:
    return root / "docs" / "visual-specs" / _validate_slug(slug) / "discovery"


def _selected_card(cards: list[DirectionCard], recommended_card_id: str) -> DirectionCard:
    if not cards:
        raise ValueError("cards must not be empty")
    for card in cards:
        if card.id == recommended_card_id:
            return card
    raise ValueError(f"recommended_card_id not found: {recommended_card_id}")


def build_brainstorm_handoff(profile: TasteProfile, card: DirectionCard) -> str:
    ops = card.visual_ops
    traditions = ", ".join(profile.candidate_traditions) or "unspecified"
    culture_terms = (
        ", ".join(card.culture_terms)
        or ", ".join(profile.culture_terms)
        or "unspecified"
    )
    audience = profile.to_dict()["commercial_context"].get("audience") or "unspecified"
    brief = (
        f"{profile.initial_intent}; selected direction: {card.label}; "
        f"target audience: {audience}; traditions: {traditions}; "
        f"culture terms: {culture_terms}; domain: {profile.domain_primary}; "
        f"visual operations: composition={ops.composition}; color={ops.color}; "
        f"texture={ops.texture}; lighting={ops.lighting}; camera={ops.camera}; "
        f"typography={ops.typography}; symbol_strategy={ops.symbol_strategy}; "
        f"avoid: {', '.join(ops.avoid)}; output: static 2D visual brief."
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
    selected = _selected_card(cards, recommended_card_id)
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
{selected.label}

## Handoff
{build_brainstorm_handoff(profile, selected)}

## Notes
generated_by: visual-discovery@0.1.0
"""


def _sketch_prompt_to_dict(sketch_prompt: SketchPrompt | dict) -> dict:
    if isinstance(sketch_prompt, SketchPrompt):
        return sketch_prompt.to_dict()
    return dict(sketch_prompt)


def write_discovery_artifacts(
    *,
    root: str | Path,
    slug: str,
    title: str,
    original_intent: str,
    profile: TasteProfile,
    cards: list[DirectionCard],
    recommended_card_id: str,
    sketch_prompts: list[SketchPrompt | dict] | None = None,
) -> dict[str, str]:
    root_path = Path(root)
    out_dir = _project_dir(root_path, slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    discovery_md = out_dir / "discovery.md"
    taste_profile_json = out_dir / "taste_profile.json"
    direction_cards_json = out_dir / "direction_cards.json"
    sketch_prompts_json = out_dir / "sketch_prompts.json"

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
    result = {
        "discovery_md": str(discovery_md),
        "taste_profile_json": str(taste_profile_json),
        "direction_cards_json": str(direction_cards_json),
    }
    if sketch_prompts is not None:
        sketch_prompts_json.write_text(
            json.dumps(
                {
                    "schema_version": "0.1",
                    "slug": slug,
                    "sketch_prompts": [
                        _sketch_prompt_to_dict(item) for item in sketch_prompts
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        result["sketch_prompts_json"] = str(sketch_prompts_json)

    return result
