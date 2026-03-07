"""QualityAgent - Monitors evaluation quality and detects drift / anomalies.

On each cycle:
1. Reads recent evaluation logs
2. Computes quality metrics (avg score, variance, tradition distribution)
3. Detects drift compared to baseline
4. Flags anomalies (scores outside 2 standard deviations)
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.prototype.evolution.base_agent import BaseAgent

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"
_EVAL_LOG_PATH = _DATA_DIR / "evaluation_logs.jsonl"
_BASELINE_PATH = _DATA_DIR / "quality_baseline.json"


@dataclass
class QualityAgent(BaseAgent):
    """Autonomous agent that monitors evaluation quality."""

    name: str = "quality"

    async def run_cycle(self) -> dict:
        """Execute one quality monitoring cycle.

        Returns
        -------
        dict with keys:
          - avg_score: float | None
          - drift_detected: bool
          - anomalies: int
        """
        self.log_action("cycle_start")

        # 1. Read recent evaluation logs
        records = self._read_eval_logs()
        self.log_action("logs_read", {"count": len(records)})

        if not records:
            result = {"avg_score": None, "drift_detected": False, "anomalies": 0}
            self.log_action("cycle_complete", result)
            return result

        # 2. Compute quality metrics
        metrics = self._compute_metrics(records)
        self.log_action("metrics_computed", metrics)

        # 3. Detect drift
        drift_detected = self._detect_drift(metrics)

        # 4. Flag anomalies
        anomalies = self._flag_anomalies(records, metrics)

        result = {
            "avg_score": metrics.get("avg_score"),
            "drift_detected": drift_detected,
            "anomalies": len(anomalies),
        }
        self.log_action("cycle_complete", result)
        return result

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _read_eval_logs(self) -> list[dict[str, Any]]:
        """Read evaluation log entries from JSONL."""
        records: list[dict[str, Any]] = []
        if not _EVAL_LOG_PATH.exists():
            logger.warning("Evaluation log not found: %s", _EVAL_LOG_PATH)
            return records

        with open(_EVAL_LOG_PATH, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed line %d", lineno)

        return records

    def _compute_metrics(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Compute aggregate quality metrics."""
        scores: list[float] = []
        tradition_dist: dict[str, int] = defaultdict(int)

        for rec in records:
            score = rec.get("score")
            if score is not None:
                try:
                    scores.append(float(score))
                except (ValueError, TypeError):
                    pass
            tradition = rec.get("tradition", "unknown")
            tradition_dist[tradition] += 1

        avg_score = round(sum(scores) / len(scores), 3) if scores else None
        variance = (
            round(sum((s - avg_score) ** 2 for s in scores) / len(scores), 3)
            if scores and avg_score is not None
            else None
        )
        std_dev = round(math.sqrt(variance), 3) if variance is not None else None

        return {
            "avg_score": avg_score,
            "variance": variance,
            "std_dev": std_dev,
            "score_count": len(scores),
            "tradition_distribution": dict(tradition_dist),
        }

    def _detect_drift(self, current_metrics: dict[str, Any]) -> bool:
        """Compare current metrics against saved baseline.

        Drift is flagged when average score shifts by more than 0.5
        from the baseline.
        """
        if not _BASELINE_PATH.exists():
            # First run — save current as baseline
            self._save_baseline(current_metrics)
            return False

        try:
            with open(_BASELINE_PATH, "r", encoding="utf-8") as f:
                baseline = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._save_baseline(current_metrics)
            return False

        baseline_avg = baseline.get("avg_score")
        current_avg = current_metrics.get("avg_score")

        if baseline_avg is None or current_avg is None:
            return False

        drift_magnitude = abs(current_avg - baseline_avg)
        drift_detected = drift_magnitude > 0.5

        if drift_detected:
            logger.warning(
                "Quality drift detected: baseline=%.3f current=%.3f delta=%.3f",
                baseline_avg, current_avg, drift_magnitude,
            )
            self.log_action(
                "drift_detected",
                {"baseline": baseline_avg, "current": current_avg, "delta": drift_magnitude},
            )

        return drift_detected

    def _flag_anomalies(
        self, records: list[dict[str, Any]], metrics: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify records with scores outside 2 standard deviations."""
        avg = metrics.get("avg_score")
        std = metrics.get("std_dev")
        if avg is None or std is None or std == 0:
            return []

        threshold_low = avg - 2 * std
        threshold_high = avg + 2 * std
        anomalies: list[dict[str, Any]] = []

        for rec in records:
            score = rec.get("score")
            if score is None:
                continue
            try:
                s = float(score)
            except (ValueError, TypeError):
                continue
            if s < threshold_low or s > threshold_high:
                anomalies.append(
                    {"record": rec, "score": s, "reason": "outside_2_std"}
                )

        if anomalies:
            self.log_action(
                "anomalies_flagged",
                {"count": len(anomalies), "threshold": [threshold_low, threshold_high]},
            )

        return anomalies

    def _save_baseline(self, metrics: dict[str, Any]) -> None:
        """Persist current metrics as the quality baseline."""
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(_BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        logger.info("Quality baseline saved to %s", _BASELINE_PATH)
