"""Simulated user agent that exercises the VULCA API like a real person.

Each ``SimUserAgent`` is driven by a :class:`~.personas.Persona` which
determines what intents it sends and how it rates the results.

A single ``run_cycle`` performs:
1. Pick a random sample intent from the persona.
2. Call ``client.evaluate()`` with the intent.
3. Decide on a rating based on ``feedback_tendency``.
4. Call ``client.submit_feedback()``.
5. Log the full action.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field

from app.prototype.community.api_client import VulcaAPIClient
from app.prototype.community.base_agent import BaseAgent
from app.prototype.community.personas import PERSONAS, Persona

logger = logging.getLogger(__name__)

# Placeholder image URL used when no real image is available.
_PLACEHOLDER_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"

# Rating probabilities per feedback_tendency.
_TENDENCY_WEIGHTS: dict[str, dict[str, float]] = {
    "positive": {"thumbs_up": 0.85, "thumbs_down": 0.15},
    "negative": {"thumbs_up": 0.25, "thumbs_down": 0.75},
    "balanced": {"thumbs_up": 0.55, "thumbs_down": 0.45},
    "critical": {"thumbs_up": 0.35, "thumbs_down": 0.65},
}


def _pick_rating(tendency: str) -> str:
    """Return ``"thumbs_up"`` or ``"thumbs_down"`` weighted by *tendency*."""
    weights = _TENDENCY_WEIGHTS.get(tendency, _TENDENCY_WEIGHTS["balanced"])
    return random.choices(
        list(weights.keys()),
        weights=list(weights.values()),
        k=1,
    )[0]


@dataclass
class SimUserAgent(BaseAgent):
    """Agent that simulates a real user interacting with the VULCA API."""

    persona: Persona = field(default=None)  # type: ignore[assignment]
    image_url: str = _PLACEHOLDER_IMAGE

    def __init__(
        self,
        persona_name: str = "casual_creator",
        *,
        base_url: str = "http://localhost:8001",
        api_key: str = "",
        image_url: str = _PLACEHOLDER_IMAGE,
    ) -> None:
        persona = PERSONAS.get(persona_name)
        if persona is None:
            raise ValueError(
                f"Unknown persona {persona_name!r}. "
                f"Available: {', '.join(PERSONAS)}"
            )

        client = VulcaAPIClient(base_url=base_url, api_key=api_key)

        # Initialise BaseAgent via __init__ then set extra fields.
        super().__init__(name=f"sim_{persona_name}", client=client)
        self.persona = persona
        self.image_url = image_url

    # ------------------------------------------------------------------
    # Core cycle
    # ------------------------------------------------------------------

    async def run_cycle(self) -> dict:
        """Execute one evaluate + feedback cycle."""
        intent = random.choice(self.persona.sample_intents)
        tradition = self.persona.evaluation_preferences.get("tradition", "default")

        # 1. Evaluate
        try:
            eval_result = await self.client.evaluate(
                image_url=self.image_url,
                intent=intent,
                tradition=tradition,
            )
        except Exception as exc:
            self.log_action("evaluate_error", {"intent": intent, "error": str(exc)})
            return {"status": "error", "phase": "evaluate", "error": str(exc)}

        evaluation_id = eval_result.get("evaluation_id", "unknown")

        # 2. Decide rating
        rating = _pick_rating(self.persona.feedback_tendency)

        # 3. Submit feedback
        try:
            feedback_result = await self.client.submit_feedback(
                evaluation_id=evaluation_id,
                rating=rating,
                comment=f"[sim] {intent}",
                feedback_type="implicit",
            )
        except Exception as exc:
            # Feedback API (WU-08) may not be deployed yet — non-fatal.
            logger.debug("Feedback submission failed (WU-08 may not be deployed): %s", exc)
            feedback_result = {"status": "skipped", "reason": str(exc)}

        # 4. Log & return
        summary = {
            "status": "ok",
            "persona": self.persona.name,
            "intent": intent,
            "tradition": tradition,
            "rating": rating,
            "evaluation_id": evaluation_id,
            "weighted_total": eval_result.get("weighted_total"),
            "feedback": feedback_result,
        }
        self.log_action("run_cycle", summary)
        return summary
