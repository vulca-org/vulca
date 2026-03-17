"""ParallelDimensionScorer — concurrent L1-L5 scoring via ThreadPoolExecutor.

VLM calls are I/O-bound HTTP requests (~25-55s each).  Running all five
dimensions in parallel reduces Critic latency from ~250s to ~55s.

Usage::

    scorer = ParallelDimensionScorer(max_workers=5)
    scores = scorer.score_all_dimensions(candidate, evidence, ...)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from app.prototype.agents.critic_config import DIMENSIONS
from app.prototype.agents.critic_types import DimensionScore

logger = logging.getLogger(__name__)

# Per-dimension timeout (seconds) — generous to handle cold VLM starts
_DIM_TIMEOUT = 120


class ParallelDimensionScorer:
    """Score L1-L5 dimensions concurrently using a thread pool."""

    def __init__(self, max_workers: int = 5) -> None:
        self._max_workers = max_workers

    def score_all_dimensions(
        self,
        candidate: dict[str, Any],
        evidence: dict[str, Any],
        cultural_tradition: str,
        subject: str = "",
        use_vlm: bool = True,
    ) -> list[DimensionScore]:
        """Score a single candidate across all dimensions in parallel.

        Falls back to sequential scoring (via CriticRules.score) if the
        parallel execution encounters errors.
        """
        try:
            from app.prototype.agents.critic_rules import CriticRules
        except ImportError:
            raise RuntimeError("critic_rules module removed; use vulca.pipeline.nodes.evaluate instead")

        rules = CriticRules()

        # Each dimension scorer is independent — submit them all at once
        futures = {}
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            for idx, dim in enumerate(DIMENSIONS):
                future = executor.submit(
                    self._score_one_dimension,
                    rules=rules,
                    dim_index=idx,
                    candidate=candidate,
                    evidence=evidence,
                    cultural_tradition=cultural_tradition,
                    subject=subject,
                    use_vlm=use_vlm,
                )
                futures[dim] = future

            # Collect results in dimension order
            results: dict[str, DimensionScore] = {}
            for dim, future in futures.items():
                try:
                    results[dim] = future.result(timeout=_DIM_TIMEOUT)
                except Exception as exc:
                    logger.warning("Parallel scoring failed for %s: %s", dim, exc)
                    # Fallback: score all dimensions sequentially
                    return rules.score(
                        candidate, evidence, cultural_tradition, subject, use_vlm
                    )

        # Return scores in canonical DIMENSIONS order
        return [results[dim] for dim in DIMENSIONS]

    @staticmethod
    def _score_one_dimension(
        rules: Any,
        dim_index: int,
        candidate: dict[str, Any],
        evidence: dict[str, Any],
        cultural_tradition: str,
        subject: str,
        use_vlm: bool,
    ) -> DimensionScore:
        """Score a single dimension.

        We run the full CriticRules.score() and extract the one
        dimension we need.  This is slightly redundant for rule-based
        scoring but necessary because VLM/CLIP blending is applied
        per-score-call and produces different values each invocation.
        """
        all_scores = rules.score(
            candidate, evidence, cultural_tradition, subject, use_vlm
        )
        return all_scores[dim_index]
