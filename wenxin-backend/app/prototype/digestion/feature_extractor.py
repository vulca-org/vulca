"""Shared cultural feature extraction — used by both create_routes and bootstrap.

Tier-1 rule-based extraction: numeric features only, zero-latency, synchronous.
Tier-2 LLM extraction: semantic features via litellm, used during backfill.
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
    total_rounds: int = 0,
    max_rounds: int = 0,
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

    # --- New dimensions (5→8 expansion) ---

    # Dimension variance: std dev of L1-L5 scores (measures balance)
    if len(score_values) >= 2:
        mean = sum(score_values) / len(score_values)
        variance = sum((v - mean) ** 2 for v in score_values) / len(score_values)
        features["dimension_variance"] = round(variance ** 0.5, 4)

    # L4 emphasis: L4 / max_score ratio (mirrors l5_emphasis)
    if score_values:
        max_score = max(score_values)
        l4 = final_scores.get("L4", final_scores.get("critical_interpretation", 0.0))
        if isinstance(l4, (int, float)) and max_score > 0:
            features["l4_emphasis"] = round(l4 / max_score, 4)

    # Generation efficiency: 1.0 - total_rounds/max_rounds
    if total_rounds > 0 and max_rounds > 0:
        features["generation_efficiency"] = round(1.0 - total_rounds / max_rounds, 4)

    return features


def _extract_semantic_features_llm(intent: str, tradition: str) -> dict[str, Any]:
    """Tier-2: Extract semantic cultural features via LLM (synchronous).

    Uses litellm.completion() with MODEL_FAST to extract:
    - style_elements, emotional_tone, technique_markers, cultural_references

    On any failure, returns empty dict (graceful degradation).
    """
    if not intent or not intent.strip():
        return {}

    try:
        import litellm  # noqa: E402

        prompt = (
            "You are a cultural art analyst. Given the following creation intent "
            "and cultural tradition, extract semantic cultural features as JSON.\n\n"
            f"Intent: {intent}\n"
            f"Tradition: {tradition}\n\n"
            "Return ONLY a JSON object with these four keys "
            "(each value is a list of short strings):\n"
            '{\n'
            '  "style_elements": ["...", "..."],\n'
            '  "emotional_tone": ["...", "..."],\n'
            '  "technique_markers": ["...", "..."],\n'
            '  "cultural_references": ["...", "..."]\n'
            '}\n\n'
            "Rules:\n"
            "- Each list should have 1-5 items\n"
            "- Items can be in any language (Chinese, English, Japanese, etc.)\n"
            "- If a category doesn't apply, use an empty list []\n"
            "- Return ONLY the JSON, no markdown fences, no explanation"
        )

        from app.prototype.agents.model_router import MODEL_FAST

        response = litellm.completion(
            model=MODEL_FAST,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )

        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3].strip()
            elif "```" in raw:
                raw = raw[:raw.rfind("```")].strip()

        parsed = json.loads(raw)

        # Validate structure — only accept expected keys with list values
        valid_keys = {"style_elements", "emotional_tone", "technique_markers", "cultural_references"}
        result: dict[str, Any] = {}
        for key in valid_keys:
            val = parsed.get(key)
            if isinstance(val, list):
                result[key] = [str(item) for item in val if item]
            else:
                result[key] = []

        return result

    except Exception as exc:
        logger.debug("Tier-2 LLM feature extraction failed (graceful degradation): %s", exc)
        return {}


def backfill_missing_features(use_llm: bool = True) -> int:
    """Scan sessions.jsonl for entries with empty/incomplete cultural_features and backfill.

    Two-tier backfill:
    1. Tier-1 (rule-based): Always applied from final_scores — zero latency.
    2. Tier-2 (LLM): If *use_llm* is True, enrich with semantic features
       (style_elements, emotional_tone, etc.) for sessions that have an intent
       but lack semantic features.

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

        cf = session.get("cultural_features") or {}
        has_tier1 = cf.get("avg_score") is not None
        has_tier2 = bool(cf.get("style_elements"))

        # Skip if both tiers are already populated
        if has_tier1 and has_tier2:
            new_lines.append(line)
            continue

        tradition = session.get("tradition", "default")
        changed = False

        # --- Tier-1: rule-based numeric features ---
        if not has_tier1:
            final_scores = session.get("final_scores") or session.get("dimension_scores") or {}

            # Also try round_snapshots for scores
            if not final_scores:
                rounds = session.get("round_snapshots", [])
                if rounds:
                    last_round = rounds[-1] if isinstance(rounds[-1], dict) else {}
                    final_scores = last_round.get("dimension_scores", {})

            risk_flags = session.get("risk_flags", [])

            tier1 = extract_cultural_features(tradition, final_scores, risk_flags)
            if tier1:
                cf.update(tier1)
                changed = True

        # --- Tier-2: LLM semantic features ---
        if use_llm and not has_tier2:
            intent = session.get("intent", "")
            if intent:
                tier2 = _extract_semantic_features_llm(intent, tradition)
                if tier2:
                    cf.update(tier2)
                    changed = True

        if changed:
            session["cultural_features"] = cf
            new_lines.append(json.dumps(session, ensure_ascii=False))
            updated += 1
        else:
            new_lines.append(line)

    if updated > 0:
        sessions_path.write_text("\n".join(new_lines) + "\n")
        logger.info("Backfilled cultural_features for %d sessions", updated)

    return updated
