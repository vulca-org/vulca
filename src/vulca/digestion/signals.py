"""Extract learning signals from completed Studio sessions."""
from __future__ import annotations

from vulca.studio.brief import Brief


def extract_signals(brief: Brief, *, user_feedback: str = "") -> dict:
    """Extract structured learning signals from a completed session.

    Signals are used for future session improvement:
    - concept_preference: which concept was chosen (index + total)
    - dimension_difficulty: which L dimension was weakest
    - style_mix: what style combination was used
    - user_feedback: accept/reject/quit
    """
    signals: dict = {
        "session_id": brief.session_id,
        "intent": brief.intent,
        "user_feedback": user_feedback,
    }

    # Concept preference
    if brief.concept_candidates and brief.selected_concept:
        try:
            idx = brief.concept_candidates.index(brief.selected_concept)
        except ValueError:
            idx = -1
        signals["concept_preference"] = {
            "selected_index": idx,
            "total_candidates": len(brief.concept_candidates),
            "had_notes": bool(brief.concept_notes),
        }
    else:
        signals["concept_preference"] = {
            "selected_index": -1,
            "total_candidates": 0,
            "had_notes": False,
        }

    # Dimension difficulty (weakest dimension across generations)
    if brief.generations:
        last_scores = brief.generations[-1].scores
        if last_scores:
            weakest = min(last_scores, key=last_scores.get)
            signals["dimension_difficulty"] = {
                "weakest": weakest,
                "weakest_score": last_scores[weakest],
                "strongest": max(last_scores, key=last_scores.get),
                "strongest_score": last_scores[max(last_scores, key=last_scores.get)],
            }
        else:
            signals["dimension_difficulty"] = {"weakest": None}
    else:
        signals["dimension_difficulty"] = {"weakest": None}

    # Style mix
    if brief.style_mix:
        signals["style_mix"] = [
            {"tradition": s.tradition, "tag": s.tag, "weight": s.weight}
            for s in brief.style_mix
        ]
    else:
        signals["style_mix"] = []

    # Update frequency
    signals["update_count"] = len(brief.updates)
    signals["generation_count"] = len(brief.generations)

    return signals
