"""Critic Agent — rule-based L1-L5 scoring, risk tagging, and gate decision."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.critic_risk import RiskTagger
from app.prototype.agents.critic_rules import CriticRules
from app.prototype.agents.critic_types import (
    CandidateScore,
    CritiqueInput,
    CritiqueOutput,
    DimensionScore,
)
from app.prototype.checkpoints.critic_checkpoint import save_critic_checkpoint

__all__ = [
    "CriticAgent",
    "build_critique_output",
]


# Type alias for a scorer callable that both CriticRules.score() and
# ParallelDimensionScorer.score_all_dimensions() satisfy.
ScorerFn = Callable[..., list[DimensionScore]]


def build_critique_output(
    task_id: str,
    candidates: list[dict[str, Any]],
    evidence: dict[str, Any],
    cultural_tradition: str,
    subject: str,
    cfg: CriticConfig,
    score_fn: ScorerFn,
    t0: float,
) -> CritiqueOutput:
    """Score candidates, apply risk/gate logic, and assemble CritiqueOutput.

    This is the shared assembly function used by both the serial
    ``CriticAgent`` and the parallel ``CriticNode._run_parallel`` path.
    Centralising the business rules (gate thresholds, risk blocking, top-k,
    rerun hints) prevents silent divergence between the two paths.

    Parameters
    ----------
    score_fn : callable
        ``(candidate, evidence, cultural_tradition, subject, use_vlm) -> list[DimensionScore]``
    """
    risk_tagger = RiskTagger()

    if not candidates:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        output = CritiqueOutput(
            task_id=task_id, scored_candidates=[],
            best_candidate_id=None, rerun_hint=[],
            created_at=datetime.now(timezone.utc).isoformat(),
            latency_ms=elapsed_ms, success=False,
            error="no candidates provided",
        )
        save_critic_checkpoint(output)
        return output

    scored: list[CandidateScore] = []

    for candidate in candidates:
        dim_scores = score_fn(
            candidate=candidate,
            evidence=evidence,
            cultural_tradition=cultural_tradition,
            subject=subject,
            use_vlm=cfg.use_vlm,
        )

        risk_tuples = risk_tagger.tag(
            candidate=candidate,
            evidence=evidence,
            cultural_tradition=cultural_tradition,
        )
        risk_tag_names = [t[0] for t in risk_tuples]
        risk_severities = {t[0]: t[1] for t in risk_tuples}

        weighted_total = sum(
            cfg.weights.get(ds.dimension, 0.0) * ds.score
            for ds in dim_scores
        )

        rejected_reasons: list[str] = []
        if weighted_total < cfg.pass_threshold:
            rejected_reasons.append(
                f"weighted_total {weighted_total:.4f} < threshold {cfg.pass_threshold}"
            )
        for ds in dim_scores:
            if ds.score < cfg.min_dimension_score:
                rejected_reasons.append(
                    f"{ds.dimension} score {ds.score:.4f} < min {cfg.min_dimension_score}"
                )
        if cfg.critical_risk_blocks:
            for tag_name, severity in risk_severities.items():
                if severity == "critical":
                    rejected_reasons.append(f"critical risk: {tag_name}")

        scored.append(CandidateScore(
            candidate_id=candidate.get("candidate_id", "unknown"),
            dimension_scores=dim_scores,
            weighted_total=weighted_total,
            risk_tags=risk_tag_names,
            gate_passed=len(rejected_reasons) == 0,
            rejected_reasons=rejected_reasons,
        ))

    scored.sort(key=lambda s: s.weighted_total, reverse=True)
    scored = scored[:cfg.top_k]

    best_id: str | None = None
    for s in scored:
        if s.gate_passed:
            best_id = s.candidate_id
            break

    low_dims: set[str] = set()
    for s in scored:
        for ds in s.dimension_scores:
            if ds.score < 0.3:
                low_dims.add(ds.dimension)

    elapsed_ms = int((time.monotonic() - t0) * 1000)

    output = CritiqueOutput(
        task_id=task_id,
        scored_candidates=scored,
        best_candidate_id=best_id,
        rerun_hint=sorted(low_dims),
        created_at=datetime.now(timezone.utc).isoformat(),
        latency_ms=elapsed_ms,
        success=True,
    )
    save_critic_checkpoint(output)
    return output


class CriticAgent:
    """Score candidates on L1-L5, apply risk tags, and emit gate decisions."""

    def __init__(self, config: CriticConfig | None = None) -> None:
        self._config = config or CriticConfig()
        self._rules = CriticRules()

    def run(self, critique_input: CritiqueInput) -> CritiqueOutput:
        """Execute the critique pipeline on all candidates."""
        return build_critique_output(
            task_id=critique_input.task_id,
            candidates=critique_input.candidates,
            evidence=critique_input.evidence,
            cultural_tradition=critique_input.cultural_tradition,
            subject=critique_input.subject,
            cfg=self._config,
            score_fn=self._rules.score,
            t0=time.monotonic(),
        )
