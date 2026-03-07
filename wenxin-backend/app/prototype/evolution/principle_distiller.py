"""PrincipleDistiller - Extracts actionable rules from feedback patterns.

Groups feedback by common keywords and themes, then generates human-readable
principles such as "Users prefer detailed L3 cultural context explanations".
"""

from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from typing import Any

logger = logging.getLogger(__name__)

# Keyword categories that map feedback tokens to L1-L5 levels
_LEVEL_KEYWORDS: dict[str, list[str]] = {
    "L1_surface": ["color", "style", "visual", "appearance", "aesthetic"],
    "L2_technique": ["technique", "brushwork", "composition", "perspective", "medium"],
    "L3_context": ["cultural", "context", "historical", "tradition", "background", "meaning"],
    "L4_symbolism": ["symbol", "metaphor", "allegory", "motif", "iconography"],
    "L5_philosophy": ["philosophy", "worldview", "cosmology", "dao", "zen", "wabi-sabi"],
}

# Sentiment words for polarity detection
_POSITIVE_WORDS = {"good", "great", "excellent", "detailed", "accurate", "helpful", "clear", "prefer"}
_NEGATIVE_WORDS = {"bad", "poor", "wrong", "inaccurate", "shallow", "missing", "confusing", "vague"}


class PrincipleDistiller:
    """Distills feedback records into actionable evaluation principles."""

    def distill(self, feedback_records: list[dict[str, Any]]) -> list[str]:
        """Extract rules from feedback patterns.

        Parameters
        ----------
        feedback_records:
            List of feedback dicts. Relevant fields:
            - comment / text: free-text user feedback (optional)
            - feedback_type: thumbs_up / thumbs_down / etc.
            - tradition: cultural tradition identifier
            - skill: skill name
            - score: numeric score

        Returns
        -------
        Top 10 distilled principles as human-readable strings.
        """
        if not feedback_records:
            return ["No feedback data available for principle distillation."]

        principles: list[tuple[float, str]] = []

        # 1. Level-preference principles (from keyword analysis)
        principles.extend(self._distill_level_preferences(feedback_records))

        # 2. Tradition-preference principles
        principles.extend(self._distill_tradition_preferences(feedback_records))

        # 3. Skill-preference principles
        principles.extend(self._distill_skill_preferences(feedback_records))

        # 4. Feedback-type distribution principles
        principles.extend(self._distill_feedback_distribution(feedback_records))

        # Sort by confidence (weight) descending, take top 10
        principles.sort(key=lambda p: p[0], reverse=True)
        return [text for _, text in principles[:10]]

    # ------------------------------------------------------------------
    # Internal distillation strategies
    # ------------------------------------------------------------------

    def _distill_level_preferences(
        self, records: list[dict[str, Any]]
    ) -> list[tuple[float, str]]:
        """Detect which L1-L5 levels users care about most."""
        level_sentiment: dict[str, dict[str, int]] = defaultdict(
            lambda: {"positive": 0, "negative": 0}
        )

        for rec in records:
            text = self._extract_text(rec).lower()
            is_positive = rec.get("feedback_type") in ("thumbs_up", "positive", "approve")
            polarity = "positive" if is_positive else "negative"

            for level, keywords in _LEVEL_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    level_sentiment[level][polarity] += 1

        results: list[tuple[float, str]] = []
        for level, counts in level_sentiment.items():
            total = counts["positive"] + counts["negative"]
            if total < 2:
                continue
            ratio = counts["positive"] / total
            level_label = level.replace("_", " ").title()
            if ratio > 0.65:
                results.append(
                    (ratio * total, f"Users prefer detailed {level_label} analysis.")
                )
            elif ratio < 0.35:
                results.append(
                    ((1 - ratio) * total, f"Users find current {level_label} evaluations lacking.")
                )
        return results

    def _distill_tradition_preferences(
        self, records: list[dict[str, Any]]
    ) -> list[tuple[float, str]]:
        """Identify tradition-specific preference patterns."""
        tradition_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: {"positive": 0, "negative": 0}
        )

        for rec in records:
            tradition = rec.get("tradition", "").strip()
            if not tradition or tradition == "unknown":
                continue
            is_positive = rec.get("feedback_type") in ("thumbs_up", "positive", "approve")
            key = "positive" if is_positive else "negative"
            tradition_counts[tradition][key] += 1

        results: list[tuple[float, str]] = []
        for tradition, counts in tradition_counts.items():
            total = counts["positive"] + counts["negative"]
            if total < 2:
                continue
            ratio = counts["positive"] / total
            if ratio > 0.7:
                results.append(
                    (ratio * total, f"Evaluations for '{tradition}' tradition are well-received (approval rate: {ratio:.0%}).")
                )
            elif ratio < 0.4:
                results.append(
                    ((1 - ratio) * total, f"Evaluations for '{tradition}' tradition need improvement (approval rate: {ratio:.0%}).")
                )
        return results

    def _distill_skill_preferences(
        self, records: list[dict[str, Any]]
    ) -> list[tuple[float, str]]:
        """Detect which skills users prefer."""
        skill_scores: dict[str, list[float]] = defaultdict(list)

        for rec in records:
            skill = rec.get("skill", "").strip()
            score = rec.get("score")
            if not skill or skill == "unknown" or score is None:
                continue
            try:
                skill_scores[skill].append(float(score))
            except (ValueError, TypeError):
                continue

        results: list[tuple[float, str]] = []
        for skill, scores in skill_scores.items():
            if len(scores) < 2:
                continue
            avg = sum(scores) / len(scores)
            if avg >= 4.0:
                results.append(
                    (avg * len(scores), f"Skill '{skill}' consistently receives high ratings (avg: {avg:.1f}).")
                )
            elif avg <= 2.0:
                results.append(
                    ((5 - avg) * len(scores), f"Skill '{skill}' receives low ratings and may need redesign (avg: {avg:.1f}).")
                )
        return results

    def _distill_feedback_distribution(
        self, records: list[dict[str, Any]]
    ) -> list[tuple[float, str]]:
        """Generate principles about overall feedback health."""
        type_counts = Counter(rec.get("feedback_type", "unknown") for rec in records)
        total = len(records)

        results: list[tuple[float, str]] = []

        positive = sum(
            type_counts.get(t, 0) for t in ("thumbs_up", "positive", "approve")
        )
        negative = sum(
            type_counts.get(t, 0) for t in ("thumbs_down", "negative", "reject")
        )

        if total > 0:
            pos_ratio = positive / total
            if pos_ratio > 0.7:
                results.append(
                    (pos_ratio * total, f"Overall positive feedback ratio is high ({pos_ratio:.0%}), system is well-calibrated.")
                )
            elif pos_ratio < 0.4:
                results.append(
                    ((1 - pos_ratio) * total, f"Overall positive feedback ratio is low ({pos_ratio:.0%}), system needs calibration.")
                )

        # Detect if any single feedback type dominates
        for ftype, count in type_counts.most_common(1):
            dominance = count / total if total > 0 else 0
            if dominance > 0.6 and total >= 5:
                results.append(
                    (dominance * total, f"Feedback type '{ftype}' dominates at {dominance:.0%}; consider diversifying collection methods.")
                )

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(record: dict[str, Any]) -> str:
        """Pull free text from a feedback record."""
        for key in ("comment", "text", "feedback_text", "message", "note"):
            val = record.get(key)
            if val and isinstance(val, str):
                return val
        return ""
