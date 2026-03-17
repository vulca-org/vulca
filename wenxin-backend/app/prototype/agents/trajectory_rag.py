"""Trajectory RAG Service — retrieves and summarizes similar past executions.

Layer 3: Provides context from historical trajectories to enhance Queen
decision-making via few-shot examples and pattern extraction.

Usage::

    rag = TrajectoryRAGService()
    rag.build_index()  # call once at startup or periodically
    examples, patterns = rag.retrieve(subject, tradition, current_score)
"""

from __future__ import annotations

import logging
from pathlib import Path

try:
    from app.prototype.trajectory.trajectory_recorder import TrajectoryRecorder
    from app.prototype.trajectory.trajectory_types import TrajectoryRecord
except ImportError:
    TrajectoryRecorder = None  # type: ignore[misc,assignment]
    TrajectoryRecord = dict  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)

__all__ = [
    "TrajectoryPatterns",
    "TrajectoryRAGService",
]

_DEFAULT_STORAGE_DIR = Path(__file__).resolve().parent.parent / "data" / "trajectories"


class TrajectoryPatterns:
    """Summarized patterns from similar trajectories."""

    def __init__(
        self,
        avg_rounds: float = 0.0,
        avg_final_score: float = 0.0,
        accept_rate: float = 0.0,
        common_rerun_dims: list[str] | None = None,
        score_improvement_per_round: float = 0.0,
        n_trajectories: int = 0,
    ) -> None:
        self.avg_rounds = avg_rounds
        self.avg_final_score = avg_final_score
        self.accept_rate = accept_rate
        self.common_rerun_dims = common_rerun_dims or []
        self.score_improvement_per_round = score_improvement_per_round
        self.n_trajectories = n_trajectories

    def to_dict(self) -> dict:
        return {
            "avg_rounds": round(self.avg_rounds, 2),
            "avg_final_score": round(self.avg_final_score, 3),
            "accept_rate": round(self.accept_rate, 2),
            "common_rerun_dims": self.common_rerun_dims,
            "score_improvement_per_round": round(self.score_improvement_per_round, 3),
            "n_trajectories": self.n_trajectories,
        }


class TrajectoryRAGService:
    """Retrieves similar trajectories and extracts decision patterns."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self._storage_dir = Path(storage_dir) if storage_dir else _DEFAULT_STORAGE_DIR
        self._recorder = TrajectoryRecorder(self._storage_dir)
        self._faiss_svc = None
        self._index_built = False

    def build_index(self) -> int:
        """Load all trajectories and build FAISS index.

        Returns number of indexed records.
        """
        try:
            from app.prototype.tools.faiss_index_service import FaissIndexService
        except ImportError:
            logger.debug("FAISS not available, RAG disabled")
            return 0

        records = self._recorder.load_all()
        if not records:
            logger.info("No trajectories found, RAG index empty")
            return 0

        self._faiss_svc = FaissIndexService()
        n = self._faiss_svc.build_trajectory_index(records)
        self._index_built = n > 0
        logger.info("Trajectory RAG index built: %d records", n)
        return n

    @property
    def available(self) -> bool:
        return self._index_built and self._faiss_svc is not None

    def retrieve(
        self,
        subject: str,
        tradition: str,
        current_score: float = 0.0,
        top_k: int = 3,
    ) -> tuple[list[TrajectoryRecord], TrajectoryPatterns]:
        """Retrieve similar trajectories and extract patterns.

        Returns (similar_records, patterns).
        """
        if not self.available:
            return [], TrajectoryPatterns()

        query = f"Subject: {subject} | Tradition: {tradition} | Score: {current_score:.2f}"
        similar = self._faiss_svc.search_trajectories(query, top_k=top_k)

        patterns = self._extract_patterns(similar)
        return similar, patterns

    def _extract_patterns(self, records: list[TrajectoryRecord]) -> TrajectoryPatterns:
        """Extract aggregate patterns from a set of trajectories."""
        if not records:
            return TrajectoryPatterns()

        n = len(records)
        total_rounds = sum(len(r.rounds) for r in records)
        avg_rounds = total_rounds / n if n > 0 else 0.0

        avg_score = sum(r.final_score for r in records) / n
        accept_count = sum(1 for r in records if r.final_action == "accept")
        accept_rate = accept_count / n if n > 0 else 0.0

        # Find common rerun dimensions across all trajectories
        dim_freq: dict[str, int] = {}
        for rec in records:
            for rnd in rec.rounds:
                if rnd.decision and rnd.decision.action == "rerun":
                    # Parse rerun dims from reason string
                    reason = rnd.decision.reason
                    for dim in [
                        "visual_perception", "technical_analysis",
                        "cultural_context", "critical_interpretation",
                        "philosophical_aesthetic",
                    ]:
                        if dim in reason:
                            dim_freq[dim] = dim_freq.get(dim, 0) + 1

        common_dims = sorted(dim_freq, key=dim_freq.get, reverse=True)[:3]

        # Score improvement per round
        improvements = []
        for rec in records:
            scores = []
            for rnd in rec.rounds:
                if rnd.critic_findings:
                    scores.append(rnd.critic_findings.weighted_score)
            if len(scores) >= 2:
                improvements.append((scores[-1] - scores[0]) / len(scores))

        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0

        return TrajectoryPatterns(
            avg_rounds=avg_rounds,
            avg_final_score=avg_score,
            accept_rate=accept_rate,
            common_rerun_dims=common_dims,
            score_improvement_per_round=avg_improvement,
            n_trajectories=n,
        )

    def build_examples_prompt(
        self,
        records: list[TrajectoryRecord],
        patterns: TrajectoryPatterns,
    ) -> str:
        """Build a prompt section with few-shot examples from similar trajectories.

        Returns formatted text suitable for injection into LLM prompt.
        """
        if not records:
            return ""

        lines = [
            "## Similar Past Evaluations",
            f"Based on {patterns.n_trajectories} similar cases:",
            f"- Average rounds used: {patterns.avg_rounds:.1f}",
            f"- Average final score: {patterns.avg_final_score:.3f}",
            f"- Accept rate: {patterns.accept_rate:.0%}",
            f"- Common rerun dimensions: {', '.join(patterns.common_rerun_dims) or 'none'}",
            f"- Score improvement per round: {patterns.score_improvement_per_round:+.3f}",
            "",
        ]

        for i, rec in enumerate(records[:3], 1):
            lines.append(f"### Example {i}: {rec.subject} ({rec.tradition})")
            lines.append(f"- Final: score={rec.final_score:.3f}, action={rec.final_action}")
            lines.append(f"- Rounds: {len(rec.rounds)}, Cost: ${rec.total_cost:.4f}")
            for rnd in rec.rounds:
                if rnd.decision:
                    score_str = f" (score={rnd.critic_findings.weighted_score:.3f})" if rnd.critic_findings else ""
                    lines.append(
                        f"  Round {rnd.round_num}: {rnd.decision.action}{score_str} — {rnd.decision.reason[:80]}"
                    )
            lines.append("")

        return "\n".join(lines)
