"""Condition generation for the real-brief benchmark."""
from __future__ import annotations

from typing import Any

from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.real_brief.types import CONDITION_IDS, RealBriefFixture


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _deliverable_list(fixture: RealBriefFixture) -> str:
    return "\n".join(
        (
            f"- {item.name}: {item.format} for {item.channel}"
            f"{' (required)' if item.required else ''}"
        )
        for item in fixture.deliverables
    )


def brief_digest(fixture: RealBriefFixture) -> str:
    """Return a readable normalized digest for a real-brief fixture."""
    fixture.validate()
    source_brief = fixture.source_brief.strip() or fixture.context
    return "\n".join(
        [
            f"Brief: {fixture.title}",
            f"Client: {fixture.client}",
            f"Context: {fixture.context}",
            f"Source brief: {source_brief}",
            "Audience:",
            _bullet_list(fixture.audience),
            "Required deliverables:",
            _deliverable_list(fixture),
            "Constraints:",
            _bullet_list(fixture.constraints),
            f"Budget: {fixture.budget}",
            f"Timeline: {fixture.timeline}",
            f"Source deadline: {fixture.source.deadline or 'not specified'}",
            "Required outputs:",
            _bullet_list(fixture.required_outputs),
            "Risks:",
            _bullet_list(fixture.risks),
            "Avoid:",
            _bullet_list(fixture.avoid),
            f"AI policy: {fixture.ai_policy}",
            f"simulation_only: {fixture.simulation_only}",
        ]
    )


def _success_criteria(fixture: RealBriefFixture) -> str:
    return "\n".join(
        [
            "Success criteria:",
            "- Address every required deliverable and output package.",
            "- Preserve all constraints and avoid known failure modes.",
            "- Make production assumptions explicit for budget and timeline.",
            "- Support evaluation dimensions: "
            + ", ".join(fixture.evaluation_dimensions),
        ]
    )


def _missing_questions(fixture: RealBriefFixture) -> str:
    questions = [
        "Which brand assets, copy, logos, or required text are final?",
        "Which production format and review milestone should be optimized first?",
        "What editability handoff standard will the client actually use?",
    ]
    if fixture.ai_policy == "unspecified":
        questions.append("What AI-use disclosure or usage limit should apply?")
    return "Missing questions:\n" + _bullet_list(questions)


def _condition(
    condition_id: str,
    label: str,
    workflow_stage: str,
    purpose: str,
    prompt: str,
    **extra: Any,
) -> dict[str, Any]:
    payload = {
        "id": condition_id,
        "label": label,
        "workflow_stage": workflow_stage,
        "purpose": purpose,
        "prompt": prompt,
    }
    payload.update(extra)
    return payload


def build_real_brief_conditions(fixture: RealBriefFixture) -> list[dict[str, Any]]:
    """Build A/B/C/D benchmark condition prompts from a fixture."""
    fixture.validate()
    digest = brief_digest(fixture)
    profile = infer_taste_profile(fixture.slug, digest)
    direction_cards = generate_direction_cards(profile, count=3)
    selected_card = direction_cards[0]
    card_payload = selected_card.to_dict()
    final_prompt = compose_prompt_from_direction_card(selected_card, target="final")
    prompt_payload = final_prompt.to_dict()

    card_details = "\n".join(
        [
            f"Selected direction card: {card_payload['label']}",
            f"Summary: {card_payload['summary']}",
            "Visual ops:",
            f"- Composition: {card_payload['visual_ops']['composition']}",
            f"- Color: {card_payload['visual_ops']['color']}",
            f"- Texture/material: {card_payload['visual_ops']['texture']}",
            f"- Typography: {card_payload['visual_ops']['typography']}",
            f"- Symbol strategy: {card_payload['visual_ops']['symbol_strategy']}",
            "Evaluation focus:",
            _bullet_list(
                [
                    f"{key}: {value}"
                    for key, value in card_payload["evaluation_focus"].items()
                ]
            ),
        ]
    )

    preview_plan = "\n".join(
        [
            "Preview plan:",
            "- Generate low-risk preview prompts from the selected direction card.",
            "- Critique against deliverables, constraints, risks, and editability.",
            "- Refine the chosen route before final production prompting.",
        ]
    )

    return [
        _condition(
            CONDITION_IDS[0],
            "One-shot model baseline",
            "one-shot",
            "Raw real brief broad ask without structured planning.",
            "\n\n".join(
                [
                    "Create the requested creative work from this raw real brief.",
                    digest,
                ]
            ),
        ),
        _condition(
            CONDITION_IDS[1],
            "Structured brief baseline",
            "structured-brief",
            "Normalized fields and success criteria before generation.",
            "\n\n".join(
                [
                    "Use the normalized brief fields below to produce a complete response.",
                    digest,
                    _success_criteria(fixture),
                ]
            ),
        ),
        _condition(
            CONDITION_IDS[2],
            "Vulca planning workflow",
            "vulca-planning",
            (
                "Ambiguity handling, direction cards, visual operations, and "
                "evaluation focus before generation."
            ),
            "\n\n".join(
                [
                    digest,
                    _missing_questions(fixture),
                    card_details,
                    "Plan a candidate route before making final assets.",
                ]
            ),
            taste_profile=profile.to_dict(),
            direction_cards=[card.to_dict() for card in direction_cards],
        ),
        _condition(
            CONDITION_IDS[3],
            "Vulca preview-and-iterate workflow",
            "vulca-preview-iterate",
            (
                "Preview prompts, critique, refinement, and editability checks "
                "before final composition."
            ),
            "\n\n".join(
                [
                    digest,
                    preview_plan,
                    card_details,
                    f"Final comp prompt: {prompt_payload['prompt']}",
                    f"Negative prompt: {prompt_payload['negative_prompt']}",
                ]
            ),
            taste_profile=profile.to_dict(),
            selected_direction_card=card_payload,
            final_prompt=prompt_payload,
        ),
    ]
