"""Shared cultural feature extraction — used by both create_routes and bootstrap.

Tier-1 rule-based extraction: numeric features only, zero-latency, synchronous.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Data directory
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def extract_cultural_features(
    tradition: str,
    final_scores: dict[str, float] | None = None,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Tier-1 rule-based cultural feature extraction.

    Mirrors the logic from create_routes._extract_cultural_features
    but as a public, importable function.
    """
    features: dict[str, Any] = {}
    if not final_scores:
        return features

    # Tradition specificity: how specific is this tradition (non-default = more specific)
    features["tradition_specificity"] = 0.3 if tradition == "default" else 0.8

    # L5 emphasis: ratio of L5 to max score
    score_values = [v for v in final_scores.values() if isinstance(v, (int, float)) and v > 0]
    if score_values:
        max_score = max(score_values)
        l5 = final_scores.get("L5", final_scores.get("philosophical_aesthetic", 0.0))
        if isinstance(l5, (int, float)) and max_score > 0:
            features["l5_emphasis"] = round(l5 / max_score, 4)

        # Overall quality
        features["avg_score"] = round(sum(score_values) / len(score_values), 4)

    # Risk level
    features["risk_level"] = round(min(1.0, len(risk_flags or []) * 0.25), 4)

    # Cultural depth: based on L3 score
    l3 = final_scores.get("L3", final_scores.get("cultural_context", 0.0))
    if isinstance(l3, (int, float)):
        features["cultural_depth"] = round(l3, 4)

    return features


def backfill_missing_features() -> int:
    """Scan sessions.jsonl for entries with empty cultural_features and backfill them.

    Returns the number of sessions updated.
    """
    sessions_path = _DATA_DIR / "sessions.jsonl"
    if not sessions_path.exists():
        logger.warning("sessions.jsonl not found at %s", sessions_path)
        return 0

    lines = sessions_path.read_text().strip().split("\n")
    updated = 0
    new_lines: list[str] = []

    for line in lines:
        if not line.strip():
            new_lines.append(line)
            continue
        try:
            session = json.loads(line)
        except json.JSONDecodeError:
            new_lines.append(line)
            continue

        cf = session.get("cultural_features", {})
        if cf and cf.get("avg_score") is not None:
            # Already has features
            new_lines.append(line)
            continue

        # Extract features from session data
        tradition = session.get("tradition", "default")

        # Try to get scores from various session fields
        final_scores = session.get("final_scores") or session.get("dimension_scores") or {}

        # Also try round_snapshots for scores
        if not final_scores:
            rounds = session.get("round_snapshots", [])
            if rounds:
                last_round = rounds[-1] if isinstance(rounds[-1], dict) else {}
                final_scores = last_round.get("dimension_scores", {})

        risk_flags = session.get("risk_flags", [])

        new_features = extract_cultural_features(tradition, final_scores, risk_flags)
        if new_features:
            session["cultural_features"] = new_features
            new_lines.append(json.dumps(session, ensure_ascii=False))
            updated += 1
        else:
            new_lines.append(line)

    if updated > 0:
        sessions_path.write_text("\n".join(new_lines) + "\n")
        logger.info("Backfilled cultural_features for %d sessions", updated)

    return updated
