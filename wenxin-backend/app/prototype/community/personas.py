"""Pre-defined personas for SimUserAgent.

Each persona encodes a user archetype with:
- evaluation preferences (tradition, evidence toggle, …)
- feedback tendency (how likely to be positive / negative)
- skill interests (which future Skills the persona would use)
- sample intents (natural-language evaluation requests)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Persona:
    """Simulated user profile that drives agent behaviour."""

    name: str
    description: str
    evaluation_preferences: dict = field(default_factory=dict)
    feedback_tendency: str = "balanced"  # positive | negative | balanced | critical
    skill_interests: list[str] = field(default_factory=list)
    sample_intents: list[str] = field(default_factory=list)


PERSONAS: dict[str, Persona] = {
    "casual_creator": Persona(
        name="casual_creator",
        description="Hobbyist digital artist exploring AI tools",
        evaluation_preferences={"tradition": "default", "include_evidence": False},
        feedback_tendency="positive",
        skill_interests=["trend_alignment", "audience_fit"],
        sample_intents=[
            "How does my digital art look?",
            "Is this good for Instagram?",
        ],
    ),
    "pro_designer": Persona(
        name="pro_designer",
        description="Professional graphic designer checking brand work",
        evaluation_preferences={"tradition": "western_academic", "include_evidence": True},
        feedback_tendency="critical",
        skill_interests=["brand_consistency"],
        sample_intents=[
            "Check brand consistency for client deliverable",
            "Evaluate typography quality",
        ],
    ),
    "cultural_researcher": Persona(
        name="cultural_researcher",
        description="Academic studying cross-cultural art evaluation",
        evaluation_preferences={"include_evidence": True},
        feedback_tendency="balanced",
        skill_interests=["brand_consistency", "audience_fit", "trend_alignment"],
        sample_intents=[
            "Evaluate this Japanese woodblock print",
            "Analyze cultural elements in this painting",
        ],
    ),
    "brand_manager": Persona(
        name="brand_manager",
        description="Corporate brand manager ensuring visual consistency",
        evaluation_preferences={"tradition": "default"},
        feedback_tendency="negative",
        skill_interests=["brand_consistency", "audience_fit"],
        sample_intents=[
            "Does this match our brand guidelines?",
            "Score this for our target audience",
        ],
    ),
}
