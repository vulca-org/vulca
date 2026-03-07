"""PreferenceModel - Simple weighted learning from feedback JSONL.

Reads user feedback records, aggregates preferences by tradition / skill /
feedback_type, and suggests L1-L5 weight adjustments based on observed patterns.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default feedback data location (WU-08 convention)
_DEFAULT_FEEDBACK_PATH = Path(__file__).parent.parent / "data" / "feedback.jsonl"
_DEFAULT_CACHE_PATH = Path(__file__).parent.parent / "data" / "preference_cache.json"


class PreferenceModel:
    """Aggregates feedback to derive preference signals."""

    def __init__(
        self,
        feedback_path: Path | None = None,
        cache_path: Path | None = None,
    ) -> None:
        self.feedback_path = feedback_path or _DEFAULT_FEEDBACK_PATH
        self.cache_path = cache_path or _DEFAULT_CACHE_PATH
        self._records: list[dict[str, Any]] = []
        self._preferences: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_feedback(self, path: Path | None = None) -> list[dict[str, Any]]:
        """Read feedback JSONL and return the list of records.

        Each line is expected to be a JSON object with at least:
          - feedback_type: "thumbs_up" | "thumbs_down" | "rating" | ...
          - tradition: cultural tradition identifier (optional)
          - skill: skill name (optional)
          - score: numeric score (optional)
        """
        source = path or self.feedback_path
        self._records = []

        if not source.exists():
            logger.warning("Feedback file not found: %s", source)
            return self._records

        with open(source, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    self._records.append(record)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed line %d in %s", lineno, source)

        logger.info("Loaded %d feedback records from %s", len(self._records), source)
        return self._records

    def compute_preferences(self) -> dict[str, Any]:
        """Aggregate preferences by tradition, skill, and feedback_type.

        Returns a nested dict:
          {
            "by_tradition": { tradition: { "positive": N, "negative": N, "avg_score": X } },
            "by_skill":     { skill:     { "positive": N, "negative": N, "avg_score": X } },
            "by_type":      { ftype:     count },
            "total":        N,
          }
        """
        by_tradition: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"positive": 0, "negative": 0, "scores": []}
        )
        by_skill: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"positive": 0, "negative": 0, "scores": []}
        )
        by_type: dict[str, int] = defaultdict(int)

        for rec in self._records:
            ftype = rec.get("feedback_type", "unknown")
            tradition = rec.get("tradition", "unknown")
            skill = rec.get("skill", "unknown")
            score = rec.get("score")
            is_positive = ftype in ("thumbs_up", "positive", "approve")

            by_type[ftype] += 1

            bucket_t = by_tradition[tradition]
            bucket_s = by_skill[skill]

            if is_positive:
                bucket_t["positive"] += 1
                bucket_s["positive"] += 1
            else:
                bucket_t["negative"] += 1
                bucket_s["negative"] += 1

            if score is not None:
                try:
                    bucket_t["scores"].append(float(score))
                    bucket_s["scores"].append(float(score))
                except (ValueError, TypeError):
                    pass

        # Compute averages and drop raw scores list
        def _finalize(bucket: dict[str, Any]) -> dict[str, Any]:
            scores = bucket.pop("scores", [])
            bucket["avg_score"] = round(sum(scores) / len(scores), 3) if scores else None
            return bucket

        self._preferences = {
            "by_tradition": {k: _finalize(v) for k, v in by_tradition.items()},
            "by_skill": {k: _finalize(v) for k, v in by_skill.items()},
            "by_type": dict(by_type),
            "total": len(self._records),
        }
        return self._preferences

    def get_weight_adjustments(self) -> dict[str, float]:
        """Suggest L1-L5 weight changes based on feedback patterns.

        Uses a simple heuristic:
          - Traditions with high positive ratio get a positive weight bump.
          - Traditions with high negative ratio get a negative weight bump.
        Returns {tradition: delta_weight} where delta is in [-0.1, +0.1].
        """
        if not self._preferences:
            self.compute_preferences()

        adjustments: dict[str, float] = {}
        for tradition, stats in self._preferences.get("by_tradition", {}).items():
            total = stats["positive"] + stats["negative"]
            if total == 0:
                continue
            ratio = stats["positive"] / total  # 0..1
            # Map [0, 1] → [-0.1, +0.1]
            delta = round((ratio - 0.5) * 0.2, 4)
            adjustments[tradition] = delta

        return adjustments

    def get_skill_rankings(self) -> list[dict[str, Any]]:
        """Rank skills by user preference (positive ratio, then total count).

        Returns a list of dicts sorted descending:
          [{"skill": str, "positive": N, "negative": N, "ratio": float, "avg_score": X}, ...]
        """
        if not self._preferences:
            self.compute_preferences()

        rankings: list[dict[str, Any]] = []
        for skill, stats in self._preferences.get("by_skill", {}).items():
            total = stats["positive"] + stats["negative"]
            ratio = stats["positive"] / total if total > 0 else 0.0
            rankings.append(
                {
                    "skill": skill,
                    "positive": stats["positive"],
                    "negative": stats["negative"],
                    "ratio": round(ratio, 3),
                    "avg_score": stats.get("avg_score"),
                }
            )

        rankings.sort(key=lambda r: (r["ratio"], r["positive"]), reverse=True)
        return rankings

    def save_cache(self) -> None:
        """Persist computed preferences to a cache file."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._preferences, f, indent=2, ensure_ascii=False)
        logger.info("Preference cache saved to %s", self.cache_path)

    def load_cache(self) -> dict[str, Any] | None:
        """Load preferences from cache if available."""
        if not self.cache_path.exists():
            return None
        with open(self.cache_path, "r", encoding="utf-8") as f:
            self._preferences = json.load(f)
        return self._preferences
