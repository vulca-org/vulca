"""TrajectoryRecorder — records and persists pipeline execution histories.

Layer 2: Provides a session-scoped recorder that agents call at each
pipeline stage. On finish(), the complete TrajectoryRecord is saved
to disk as JSON for future retrieval and RAG indexing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.prototype.trajectory.trajectory_types import (
    CriticFindings,
    DecisionLog,
    DraftPlan,
    RoundRecord,
    TrajectoryRecord,
)

logger = logging.getLogger(__name__)

_DEFAULT_STORAGE_DIR = Path(__file__).resolve().parent.parent / "data" / "trajectories"


class TrajectoryRecorder:
    """Records a single pipeline run as a TrajectoryRecord.

    Usage::

        recorder = TrajectoryRecorder()
        recorder.start(subject, tradition, evidence_pack_dict)
        recorder.record_draft(draft_plan)
        recorder.record_critic(findings)
        recorder.record_decision(decision)
        record = recorder.finish(final_score, final_action)
    """

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self._storage_dir = Path(storage_dir) if storage_dir else _DEFAULT_STORAGE_DIR
        self._storage_dir.mkdir(parents=True, exist_ok=True)

        self._record: TrajectoryRecord | None = None
        self._current_round: RoundRecord | None = None

    @property
    def active(self) -> bool:
        return self._record is not None

    def start(
        self,
        subject: str,
        tradition: str,
        evidence_pack_dict: dict | None = None,
    ) -> None:
        """Begin recording a new trajectory."""
        self._record = TrajectoryRecord(
            subject=subject,
            tradition=tradition,
            evidence_pack_dict=evidence_pack_dict,
        )
        self._current_round = None

    def _ensure_round(self, round_num: int) -> RoundRecord:
        """Get or create RoundRecord for the given round number."""
        assert self._record is not None, "Call start() first"

        if self._current_round is not None and self._current_round.round_num == round_num:
            return self._current_round

        # Save previous round if it exists
        if self._current_round is not None:
            if round_num != self._current_round.round_num + 1:
                logger.warning(
                    "Non-sequential round transition: %d -> %d",
                    self._current_round.round_num, round_num,
                )
            self._record.rounds.append(self._current_round)

        self._current_round = RoundRecord(round_num=round_num)
        return self._current_round

    def record_draft(self, draft_plan: DraftPlan, round_num: int = 1) -> None:
        """Record a Draft stage result."""
        rr = self._ensure_round(round_num)
        rr.draft_plan = draft_plan

    def record_critic(self, findings: CriticFindings, round_num: int = 1) -> None:
        """Record a Critic stage result."""
        rr = self._ensure_round(round_num)
        rr.critic_findings = findings

    def record_decision(self, decision: DecisionLog, round_num: int = 1) -> None:
        """Record a Queen decision."""
        rr = self._ensure_round(round_num)
        rr.decision = decision

    def finish(
        self,
        final_score: float,
        final_action: str,
        total_latency_ms: int = 0,
        total_cost: float = 0.0,
    ) -> TrajectoryRecord:
        """Finalize and save the trajectory to disk.

        Returns the completed TrajectoryRecord.
        """
        assert self._record is not None, "Call start() first"

        # Append the last round
        if self._current_round is not None:
            self._record.rounds.append(self._current_round)
            self._current_round = None

        self._record.final_score = final_score
        self._record.final_action = final_action
        self._record.total_latency_ms = total_latency_ms
        self._record.total_cost = total_cost

        # Save to JSON (atomic write for crash safety)
        out_path = self._storage_dir / f"{self._record.trajectory_id}.json"
        try:
            from app.prototype.checkpoints.utils import atomic_write as _atomic_write
            _atomic_write(out_path, json.dumps(self._record.to_dict(), indent=2, ensure_ascii=False))
            logger.info("Trajectory saved: %s (score=%.2f)", out_path.name, final_score)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to save trajectory: %s", exc)

        record = self._record
        self._record = None
        return record

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def load_all(self) -> list[TrajectoryRecord]:
        """Load all trajectory records from storage."""
        records: list[TrajectoryRecord] = []
        for json_path in sorted(self._storage_dir.glob("*.json")):
            try:
                with open(json_path, encoding="utf-8") as f:
                    data = json.load(f)
                records.append(TrajectoryRecord.from_dict(data))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to load trajectory %s: %s", json_path.name, exc)
        return records

    def get_high_score_trajectories(self, min_score: float = 7.0) -> list[TrajectoryRecord]:
        """Filter trajectories by minimum final score (0-10 scale).

        Note: VULCA scores are [0, 1] internally; this method accepts
        the 0-10 display scale and converts accordingly.
        """
        threshold = min_score / 10.0  # convert to [0, 1]
        return [r for r in self.load_all() if r.final_score >= threshold]

    def count(self) -> int:
        """Count trajectory files without loading them all."""
        return len(list(self._storage_dir.glob("*.json")))
