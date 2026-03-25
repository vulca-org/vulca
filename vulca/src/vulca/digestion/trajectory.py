"""Layer 2 Trajectory Analysis — session completion digestion.

Computes trajectory metrics from a completed session's Brief and score history.
Used to understand how creative intent evolved through the pipeline.
"""
from __future__ import annotations

from typing import Any

from vulca.studio.brief import Brief


def compute_mood_drift(intent_mood: str, generations_moods: list[str]) -> float:
    """Compute mood drift between intended mood and generation trajectory.

    Returns 0.0 (no drift) to 1.0 (complete change).
    Uses simple string comparison — identical = 0, different = 1,
    averaged across generations.
    """
    if not intent_mood or not generations_moods:
        return 0.0

    intent_lower = intent_mood.lower().strip()
    drifts = []
    for mood in generations_moods:
        mood_lower = mood.lower().strip()
        if mood_lower == intent_lower:
            drifts.append(0.0)
        elif intent_lower in mood_lower or mood_lower in intent_lower:
            drifts.append(0.3)  # Partial overlap
        else:
            drifts.append(1.0)

    return round(sum(drifts) / len(drifts), 3)


def compute_cultural_fidelity(
    intended_traditions: list[str],
    scores_trajectory: list[dict[str, float]],
) -> float:
    """Compute cultural fidelity — how well L3 was preserved across rounds.

    Returns 0.0 (lost) to 1.0 (perfectly preserved).
    Based on L3 score trend: stable or improving = high fidelity.
    """
    if not scores_trajectory:
        return 1.0

    l3_scores = [s.get("L3", 0.0) for s in scores_trajectory]
    if not l3_scores:
        return 1.0

    first = l3_scores[0]
    last = l3_scores[-1]

    if first == 0.0:
        return 1.0

    # Ratio of final to initial L3 score
    ratio = last / first
    return round(min(1.0, max(0.0, ratio)), 3)


def compute_composition_preservation(
    scores_trajectory: list[dict[str, float]],
) -> float:
    """Compute composition preservation — how well L1 was maintained.

    Returns 0.0 (lost) to 1.0 (perfectly preserved).
    """
    if not scores_trajectory:
        return 1.0

    l1_scores = [s.get("L1", 0.0) for s in scores_trajectory]
    if not l1_scores or l1_scores[0] == 0.0:
        return 1.0

    ratio = l1_scores[-1] / l1_scores[0]
    return round(min(1.0, max(0.0, ratio)), 3)


def build_session_digest(brief: Brief, *, user_feedback: str = "") -> dict[str, Any]:
    """Build a full session digest from a completed Brief."""
    digest: dict[str, Any] = {
        "session_id": brief.session_id,
        "intent": brief.intent,
        "user_feedback": user_feedback,
        "iteration_count": len(brief.generations),
        "update_count": len(brief.updates),
        "style_mix": [
            {"tradition": s.tradition, "tag": s.tag, "weight": s.weight}
            for s in brief.style_mix
        ],
    }

    # Score trajectory
    scores_trajectory = [g.scores for g in brief.generations if g.scores]

    # Mood drift
    gen_moods = []  # Would come from artifact analysis L5 in full version
    # Simplified: use brief mood as constant (no per-generation mood yet)
    if brief.mood and scores_trajectory:
        gen_moods = [brief.mood] * len(scores_trajectory)
        # If L5 changed significantly across rounds, infer mood drift
        l5_scores = [s.get("L5", 0.0) for s in scores_trajectory]
        if len(l5_scores) >= 2 and l5_scores[0] > 0:
            l5_drift = abs(l5_scores[-1] - l5_scores[0]) / l5_scores[0]
            digest["mood_drift"] = round(min(1.0, l5_drift), 3)
        else:
            digest["mood_drift"] = 0.0
    else:
        digest["mood_drift"] = 0.0

    # Cultural fidelity (L3 preservation)
    intended = [s.tradition for s in brief.style_mix if s.tradition]
    digest["cultural_fidelity"] = compute_cultural_fidelity(intended, scores_trajectory)

    # Composition preservation (L1)
    digest["composition_preservation"] = compute_composition_preservation(scores_trajectory)

    # Dimension difficulty
    if scores_trajectory:
        final = scores_trajectory[-1]
        if final:
            weakest = min(final, key=final.get)
            strongest = max(final, key=final.get)
            digest["dimension_difficulty"] = {
                "weakest": weakest,
                "weakest_score": final[weakest],
                "strongest": strongest,
                "strongest_score": final[strongest],
            }
        else:
            digest["dimension_difficulty"] = {"weakest": None}
    else:
        digest["dimension_difficulty"] = {"weakest": None}

    # Final scores
    if scores_trajectory:
        digest["final_scores"] = scores_trajectory[-1]

    return digest
