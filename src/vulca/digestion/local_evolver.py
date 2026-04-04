"""Local evolution -- reads JSONL sessions, writes evolved_context.json + per-tradition insights."""
from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger("vulca.digestion")

_DEFAULT_DATA_DIR = Path.home() / ".vulca" / "data"
_MIN_SESSIONS = 5
_MIN_FEEDBACK = 3
_MIN_NEW_SESSIONS = 3
_ADJUSTMENT = 0.05


class LocalEvolver:
    """Lightweight evolver that reads local JSONL and writes evolved_context.json."""

    def __init__(self, *, data_dir: str = ""):
        self.data_dir = Path(data_dir) if data_dir else _DEFAULT_DATA_DIR

    def evolve(self) -> dict | None:
        """Run evolution on local sessions. Returns evolved context or None if insufficient data."""
        sessions = self._load_sessions()
        if not sessions:
            return None

        # Session count gate: skip if fewer than _MIN_NEW_SESSIONS sessions since last evolution.
        # If never evolved before (last_evolved_at == 0.0), treat all sessions as new.
        last_evolved_at = self._load_last_evolved_at()
        if last_evolved_at == 0.0:
            new_sessions = sessions
        else:
            new_sessions = [s for s in sessions if s.get("timestamp", 0) > last_evolved_at]
        if len(new_sessions) < _MIN_NEW_SESSIONS:
            logger.debug(
                "Skipping evolution: only %d new sessions since last run (need %d)",
                len(new_sessions), _MIN_NEW_SESSIONS,
            )
            return None

        # Filter sessions with real feedback
        feedback_sessions = [s for s in sessions if s.get("user_feedback") in ("accepted", "rejected")]
        if len(feedback_sessions) < _MIN_FEEDBACK:
            return None
        if len(sessions) < _MIN_SESSIONS:
            return None

        # Group by tradition
        by_tradition: dict[str, list[dict]] = defaultdict(list)
        for s in feedback_sessions:
            tradition = s.get("tradition", "default")
            by_tradition[tradition].append(s)

        # Build evolved context
        evolved: dict = {"traditions": {}}
        for tradition, tradition_sessions in by_tradition.items():
            if len(tradition_sessions) < 2:
                continue

            # Split by eval_mode (iteration 2)
            strict_sessions = [s for s in tradition_sessions if s.get("eval_mode", "strict") == "strict"]
            reference_sessions = [s for s in tradition_sessions if s.get("eval_mode") == "reference"]

            # Compute dimension averages from ALL sessions (for backward compat)
            # Support both "final_scores" (canonical) and "scores" (legacy/test format)
            dim_totals: dict[str, float] = defaultdict(float)
            dim_counts: dict[str, int] = defaultdict(int)
            for s in tradition_sessions:
                scores = s.get("final_scores") or s.get("scores", {})
                for dim, score in scores.items():
                    if isinstance(score, (int, float)):
                        dim_totals[dim] += score
                        dim_counts[dim] += 1

            dim_avgs = {d: dim_totals[d] / dim_counts[d] for d in dim_totals if dim_counts[d] > 0}

            # Relative weak: bottom 2 dimensions by average
            sorted_dims = sorted(dim_avgs.items(), key=lambda x: x[1])
            weak_dims = [d for d, _ in sorted_dims[:2]]

            # Strict-only weak dims
            strict_weak = self._relative_weak(strict_sessions) if len(strict_sessions) >= 2 else weak_dims

            # Reference exploration trends (dims with lowest scores = where users experiment)
            reference_trends = self._relative_weak(reference_sessions) if len(reference_sessions) >= 2 else []

            # Iteration 3: filter out dimensions with high intentional_departure ratio
            intentional_counts: dict[str, int] = defaultdict(int)
            total_strict = len(strict_sessions) if strict_sessions else len(tradition_sessions)
            for s in (strict_sessions or tradition_sessions):
                for dim, dev_type in s.get("deviation_types", {}).items():
                    if dev_type == "intentional_departure":
                        intentional_counts[dim] += 1

            intentional_ratio = {d: intentional_counts.get(d, 0) / max(total_strict, 1) for d in dim_avgs}
            innovation_signals = [d for d, ratio in intentional_ratio.items() if ratio >= 0.3]

            # Exclude high-departure dims from weak (>30% intentional = creative choice)
            weak_dims = [d for d in weak_dims if intentional_ratio.get(d, 0) < 0.3]
            strict_weak = [d for d in strict_weak if intentional_ratio.get(d, 0) < 0.3]

            # If all weak dims were excluded, take next-lowest that isn't excluded
            if not weak_dims:
                remaining = [d for d, _ in sorted_dims if intentional_ratio.get(d, 0) < 0.3]
                weak_dims = remaining[:2]

            # Overall average
            all_scores = [v for v in dim_avgs.values()]
            overall_avg = round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.0

            # Deviation pattern counts per dimension
            deviation_patterns: dict[str, dict[str, int]] = {}
            for s in tradition_sessions:
                for dim, dev_type in s.get("deviation_types", {}).items():
                    if dim not in deviation_patterns:
                        deviation_patterns[dim] = defaultdict(int)
                    deviation_patterns[dim][dev_type] += 1
            # Convert defaultdicts to plain dicts
            deviation_patterns = {d: dict(counts) for d, counts in deviation_patterns.items()}

            # Strict ratio
            strict_ratio = round(len(strict_sessions) / max(len(tradition_sessions), 1), 3)

            # Score history (all feedback sessions for this tradition)
            score_history = [
                {
                    "session_id": s.get("session_id", ""),
                    "weighted_total": s.get("weighted_total", 0.0),
                    "timestamp": s.get("timestamp", 0.0),
                }
                for s in tradition_sessions
            ]

            evolved["traditions"][tradition] = {
                "session_count": len(tradition_sessions),
                "strict_count": len(strict_sessions),
                "reference_count": len(reference_sessions),
                "dimension_averages": {d: round(v, 3) for d, v in dim_avgs.items()},
                "weak_dimensions": weak_dims,
                "strict_weak": strict_weak,
                "reference_trends": reference_trends,
                "innovation_signals": innovation_signals,
                "overall_avg": overall_avg,
                "weight_adjustments": {d: _ADJUSTMENT for d in weak_dims},
            }

            # Write per-tradition insight file (topic layer)
            self._write_tradition_insights(
                tradition=tradition,
                sessions=tradition_sessions,
                evolved_data={
                    "dimension_averages": {d: round(v, 3) for d, v in dim_avgs.items()},
                    "weak_dimensions": weak_dims,
                    "innovation_signals": innovation_signals,
                    "strict_ratio": strict_ratio,
                    "deviation_patterns": deviation_patterns,
                    "score_history": score_history,
                },
            )

        # Aggregate total session count at root level
        evolved["total_sessions"] = sum(
            t.get("session_count", 0) for t in evolved["traditions"].values()
        )

        # Record evolution timestamp in _meta
        evolved["_meta"] = {"last_evolved_at": time.time()}

        # Write to file
        evolved_path = self.data_dir / "evolved_context.json"
        evolved_path.parent.mkdir(parents=True, exist_ok=True)
        evolved_path.write_text(json.dumps(evolved, indent=2, ensure_ascii=False))
        logger.debug("Local evolution written to %s", evolved_path)

        return evolved

    def _write_tradition_insights(
        self,
        tradition: str,
        sessions: list[dict],
        evolved_data: dict,
    ) -> None:
        """Write per-tradition detailed insight file to the topic layer.

        Creates ``{data_dir}/evolved/{tradition}/insights.json`` with rich
        per-tradition data that is too verbose to keep in the index layer.
        """
        tradition_dir = self.data_dir / "evolved" / tradition
        tradition_dir.mkdir(parents=True, exist_ok=True)
        insights = {
            "tradition": tradition,
            "updated_at": time.time(),
            "session_count": len(sessions),
            "score_history": evolved_data.get("score_history", []),
            "dimension_averages": evolved_data.get("dimension_averages", {}),
            "deviation_patterns": evolved_data.get("deviation_patterns", {}),
            "weak_dimensions": evolved_data.get("weak_dimensions", []),
            "innovation_signals": evolved_data.get("innovation_signals", []),
            "strict_ratio": evolved_data.get("strict_ratio", 0.0),
        }
        insights_path = tradition_dir / "insights.json"
        insights_path.write_text(json.dumps(insights, indent=2, ensure_ascii=False))
        logger.debug("Tradition insights written to %s", insights_path)

    def load_tradition_insights(self, tradition: str) -> dict | None:
        """Load per-tradition insights from the topic layer.

        Returns parsed dict if ``{data_dir}/evolved/{tradition}/insights.json``
        exists, otherwise returns ``None``.
        """
        insights_path = self.data_dir / "evolved" / tradition / "insights.json"
        if not insights_path.exists():
            return None
        try:
            return json.loads(insights_path.read_text())
        except Exception:
            return None

    def load_evolved(self, tradition: str) -> dict | None:
        """Load evolved data for a specific tradition (read-only, no evolution trigger)."""
        evolved_path = self.data_dir / "evolved_context.json"
        if not evolved_path.exists():
            return None
        try:
            ctx = json.loads(evolved_path.read_text())
            return ctx.get("traditions", {}).get(tradition)
        except Exception:
            return None

    @staticmethod
    def _relative_weak(sessions: list[dict]) -> list[str]:
        """Get bottom 2 dimensions by average score from a set of sessions."""
        dim_totals: defaultdict[str, float] = defaultdict(float)
        dim_counts: defaultdict[str, int] = defaultdict(int)
        for s in sessions:
            # Support both "final_scores" (canonical) and "scores" (legacy/test format)
            scores = s.get("final_scores") or s.get("scores", {})
            for dim, score in scores.items():
                if isinstance(score, (int, float)):
                    dim_totals[dim] += score
                    dim_counts[dim] += 1
        dim_avgs = {d: dim_totals[d] / dim_counts[d] for d in dim_totals if dim_counts[d] > 0}
        sorted_dims = sorted(dim_avgs.items(), key=lambda x: x[1])
        return [d for d, _ in sorted_dims[:2]]

    def _load_last_evolved_at(self) -> float:
        """Return the timestamp of the last successful evolution, or 0.0 if never run."""
        evolved_path = self.data_dir / "evolved_context.json"
        if not evolved_path.exists():
            return 0.0
        try:
            ctx = json.loads(evolved_path.read_text())
            return float(ctx.get("_meta", {}).get("last_evolved_at", 0.0))
        except Exception:
            return 0.0

    def _load_sessions(self) -> list[dict]:
        """Load sessions from UnifiedSessionStore and merge explicit feedback signals."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=self.data_dir)
        sessions = store.load_all()
        feedback_map = {f["session_id"]: f["signal"] for f in store.load_feedback()}
        for s in sessions:
            if s.get("session_id") in feedback_map:
                s["user_feedback"] = feedback_map[s["session_id"]]
        return sessions
