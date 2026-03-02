"""Critic Agent — rule-based L1-L5 scoring, risk tagging, and gate decision."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.critic_risk import RiskTagger
from app.prototype.agents.critic_rules import CriticRules
from app.prototype.agents.critic_types import (
    CandidateScore,
    CritiqueInput,
    CritiqueOutput,
)
from app.prototype.checkpoints.critic_checkpoint import save_critic_checkpoint

__all__ = [
    "CriticAgent",
]


class CriticAgent:
    """Score candidates on L1-L5, apply risk tags, and emit gate decisions."""

    def __init__(self, config: CriticConfig | None = None) -> None:
        self._config = config or CriticConfig()
        self._rules = CriticRules()
        self._risk_tagger = RiskTagger()

    def run(self, critique_input: CritiqueInput) -> CritiqueOutput:
        """Execute the critique pipeline on all candidates."""
        t0 = time.monotonic()
        cfg = self._config

        # Empty candidates → immediate failure
        if not critique_input.candidates:
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            output = CritiqueOutput(
                task_id=critique_input.task_id,
                scored_candidates=[],
                best_candidate_id=None,
                rerun_hint=[],
                created_at=datetime.now(timezone.utc).isoformat(),
                latency_ms=elapsed_ms,
                success=False,
                error="no candidates provided",
            )
            save_critic_checkpoint(output)
            return output

        scored: list[CandidateScore] = []

        for candidate in critique_input.candidates:
            # 1. L1-L5 dimension scores (with image-aware CLIP blending)
            dim_scores = self._rules.score(
                candidate=candidate,
                evidence=critique_input.evidence,
                cultural_tradition=critique_input.cultural_tradition,
                subject=critique_input.subject,
                use_vlm=self._config.use_vlm,
            )

            # 2. Risk tags
            risk_tuples = self._risk_tagger.tag(
                candidate=candidate,
                evidence=critique_input.evidence,
                cultural_tradition=critique_input.cultural_tradition,
            )
            risk_tag_names = [t[0] for t in risk_tuples]
            risk_severities = {t[0]: t[1] for t in risk_tuples}

            # 3. Weighted total
            weighted_total = sum(
                cfg.weights.get(ds.dimension, 0.0) * ds.score
                for ds in dim_scores
            )

            # 4. Gate decision
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
                        rejected_reasons.append(
                            f"critical risk: {tag_name}"
                        )

            gate_passed = len(rejected_reasons) == 0

            scored.append(CandidateScore(
                candidate_id=candidate.get("candidate_id", "unknown"),
                dimension_scores=dim_scores,
                weighted_total=weighted_total,
                risk_tags=risk_tag_names,
                gate_passed=gate_passed,
                rejected_reasons=rejected_reasons,
            ))

        # 5. Sort by weighted_total descending
        scored.sort(key=lambda s: s.weighted_total, reverse=True)

        # 5b. Truncate to top_k
        scored = scored[:cfg.top_k]

        # 6. Select best candidate (highest score that passed gate)
        best_id: str | None = None
        for s in scored:
            if s.gate_passed:
                best_id = s.candidate_id
                break

        # 7. Rerun hint: collect dimensions with score < 0.3 across all candidates
        low_dims: set[str] = set()
        for s in scored:
            for ds in s.dimension_scores:
                if ds.score < 0.3:
                    low_dims.add(ds.dimension)
        rerun_hint = sorted(low_dims)

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        output = CritiqueOutput(
            task_id=critique_input.task_id,
            scored_candidates=scored,
            best_candidate_id=best_id,
            rerun_hint=rerun_hint,
            created_at=datetime.now(timezone.utc).isoformat(),
            latency_ms=elapsed_ms,
            success=True,
            error=None,
        )

        save_critic_checkpoint(output)
        return output
