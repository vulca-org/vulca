"""ResultFormatter — transforms EvaluateResponse into a frontend-friendly ResultCard."""

from __future__ import annotations

from app.prototype.api.evaluate_schemas import EvaluateResponse
from app.prototype.intent.types import IntentResult, ResultCard

__all__ = ["ResultFormatter"]


class ResultFormatter:
    """Formats raw evaluation responses into presentation-ready ResultCards."""

    @staticmethod
    def format(
        response: EvaluateResponse,
        intent_result: IntentResult | None = None,
    ) -> ResultCard:
        """Build a ResultCard from an EvaluateResponse.

        Parameters
        ----------
        response : EvaluateResponse
            The raw evaluation result from the evaluate endpoint.
        intent_result : IntentResult | None
            Optional resolved intent (used for tradition_used fallback).

        Returns
        -------
        ResultCard
            A frontend-friendly summary of the evaluation.
        """
        # Risk level mapping: 0 flags = low, 1-2 = medium, 3+ = high
        num_flags = len(response.risk_flags)
        if num_flags == 0:
            risk_level = "low"
        elif num_flags <= 2:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Build summary from cultural diagnosis or fallback
        summary = response.cultural_diagnosis or (
            f"Evaluation completed with weighted score {response.weighted_total:.2f}"
        )

        # Determine tradition_used
        tradition_used = response.tradition_used
        if intent_result is not None and tradition_used == "default":
            tradition_used = intent_result.tradition

        return ResultCard(
            score=response.weighted_total,
            summary=summary,
            risk_level=risk_level,
            dimensions=response.scores,
            recommendations=response.recommendations,
            tradition_used=tradition_used,
        )
