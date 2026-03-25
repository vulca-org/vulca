"""Layer 3 Evolution — cross-session pattern detection and weight evolution.

Replaces the old ContextEvolver that was contaminated by mock data.
Only uses sessions with explicit user_feedback (accepted/rejected).
"""
from __future__ import annotations

from typing import Any

from vulca.digestion.storage import JsonlStudioStorage

_DEFAULT_WEIGHTS = {"L1": 0.2, "L2": 0.2, "L3": 0.2, "L4": 0.2, "L5": 0.2}
_DIMENSIONS = ["L1", "L2", "L3", "L4", "L5"]


def detect_patterns(store: JsonlStudioStorage) -> list[dict[str, Any]]:
    """Detect patterns across sessions (e.g., 'L2 consistently weak for xieyi').

    Returns list of pattern dicts.
    """
    sessions = store.get_sessions()
    if not sessions:
        return []

    # Group by tradition
    by_tradition: dict[str, list[dict]] = {}
    for s in sessions:
        for t in s.get("traditions", []):
            by_tradition.setdefault(t, []).append(s)

    patterns = []
    for tradition, sess_list in by_tradition.items():
        if len(sess_list) < 3:
            continue

        # Compute average scores per dimension
        dim_totals: dict[str, float] = {d: 0.0 for d in _DIMENSIONS}
        dim_counts: dict[str, int] = {d: 0 for d in _DIMENSIONS}

        for s in sess_list:
            scores = s.get("final_scores", {})
            for d in _DIMENSIONS:
                if d in scores:
                    dim_totals[d] += scores[d]
                    dim_counts[d] += 1

        dim_avgs = {}
        for d in _DIMENSIONS:
            if dim_counts[d] > 0:
                dim_avgs[d] = round(dim_totals[d] / dim_counts[d], 3)

        if dim_avgs:
            weakest = min(dim_avgs, key=dim_avgs.get)
            strongest = max(dim_avgs, key=dim_avgs.get)
            patterns.append({
                "pattern_type": "dimension_tendency",
                "tradition": tradition,
                "sample_count": len(sess_list),
                "weakest": weakest,
                "weakest_avg": dim_avgs[weakest],
                "strongest": strongest,
                "strongest_avg": dim_avgs[strongest],
                "all_avgs": dim_avgs,
            })

    return patterns


def evolve_weights(
    store: JsonlStudioStorage,
    tradition: str = "",
) -> dict[str, float]:
    """Evolve L1-L5 weights from REAL accept/reject feedback.

    Only considers sessions with explicit user_feedback.
    Returns equal weights if insufficient data.
    """
    sessions = store.get_sessions(tradition=tradition) if tradition else store.get_sessions()

    # Filter to sessions with explicit feedback
    accepted = [s for s in sessions if s.get("user_feedback") == "accepted"]
    rejected = [s for s in sessions if s.get("user_feedback") == "rejected"]

    if not accepted:
        return dict(_DEFAULT_WEIGHTS)

    # Compute average accepted scores
    acc_totals = {d: 0.0 for d in _DIMENSIONS}
    acc_counts = {d: 0 for d in _DIMENSIONS}
    for s in accepted:
        scores = s.get("final_scores", {})
        for d in _DIMENSIONS:
            if d in scores:
                acc_totals[d] += scores[d]
                acc_counts[d] += 1

    # Compute average rejected scores (if any)
    rej_avgs = {}
    if rejected:
        rej_totals = {d: 0.0 for d in _DIMENSIONS}
        rej_counts = {d: 0 for d in _DIMENSIONS}
        for s in rejected:
            scores = s.get("final_scores", {})
            for d in _DIMENSIONS:
                if d in scores:
                    rej_totals[d] += scores[d]
                    rej_counts[d] += 1
        for d in _DIMENSIONS:
            if rej_counts[d] > 0:
                rej_avgs[d] = rej_totals[d] / rej_counts[d]

    # Weight = how much each dimension differentiates accepted from rejected
    raw_weights = {}
    for d in _DIMENSIONS:
        acc_avg = acc_totals[d] / max(acc_counts[d], 1)
        rej_avg = rej_avgs.get(d, 0.5)  # Default rejected average
        # Higher gap = more important dimension
        raw_weights[d] = max(0.01, acc_avg - rej_avg * 0.5)

    # Normalize to sum to 1.0
    total = sum(raw_weights.values())
    return {d: round(v / total, 3) for d, v in raw_weights.items()}
