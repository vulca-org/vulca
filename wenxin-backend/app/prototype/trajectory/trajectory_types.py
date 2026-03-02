"""Trajectory data types — complete execution history records.

Layer 2: Each pipeline run produces a TrajectoryRecord that captures
the full decision chain from Scout → Draft → Critic → Queen,
enabling experience-based retrieval for future runs.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class PromptTrace:
    """Records prompt construction details."""

    raw_prompt: str  # original subject-based prompt
    enhanced_prompt: str  # after EvidencePack enrichment
    prompt_hash: str  # for dedup
    model_ref: str  # which generation model
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.prompt_hash:
            self.prompt_hash = hashlib.md5(self.enhanced_prompt.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "raw_prompt": self.raw_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "prompt_hash": self.prompt_hash,
            "model_ref": self.model_ref,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PromptTrace:
        return cls(
            raw_prompt=d.get("raw_prompt", ""),
            enhanced_prompt=d.get("enhanced_prompt", ""),
            prompt_hash=d.get("prompt_hash", ""),
            model_ref=d.get("model_ref", ""),
            timestamp=d.get("timestamp", 0.0),
        )


@dataclass
class DraftPlan:
    """Records draft generation parameters and outcome."""

    prompt_trace: PromptTrace
    provider: str
    generation_params: dict = field(default_factory=dict)  # seed, steps, width, height
    latency_ms: int = 0
    n_candidates: int = 0
    success: bool = True

    def to_dict(self) -> dict:
        return {
            "prompt_trace": self.prompt_trace.to_dict(),
            "provider": self.provider,
            "generation_params": self.generation_params,
            "latency_ms": self.latency_ms,
            "n_candidates": self.n_candidates,
            "success": self.success,
        }

    @classmethod
    def from_dict(cls, d: dict) -> DraftPlan:
        return cls(
            prompt_trace=PromptTrace.from_dict(d.get("prompt_trace", {})),
            provider=d.get("provider", ""),
            generation_params=d.get("generation_params", {}),
            latency_ms=d.get("latency_ms", 0),
            n_candidates=d.get("n_candidates", 0),
            success=d.get("success", True),
        )


@dataclass
class CriticFindings:
    """Records critic evaluation results."""

    layer_scores: dict[str, float] = field(default_factory=dict)  # dim -> score
    weighted_score: float = 0.0
    fix_it_plan_dict: dict | None = None
    need_more_evidence_dict: dict | None = None
    model_ref: str = ""

    def to_dict(self) -> dict:
        return {
            "layer_scores": {k: round(v, 4) for k, v in self.layer_scores.items()},
            "weighted_score": round(self.weighted_score, 4),
            "fix_it_plan": self.fix_it_plan_dict,
            "need_more_evidence": self.need_more_evidence_dict,
            "model_ref": self.model_ref,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CriticFindings:
        return cls(
            layer_scores=d.get("layer_scores", {}),
            weighted_score=d.get("weighted_score", 0.0),
            fix_it_plan_dict=d.get("fix_it_plan"),
            need_more_evidence_dict=d.get("need_more_evidence"),
            model_ref=d.get("model_ref", ""),
        )


@dataclass
class DecisionLog:
    """Records a single Queen decision."""

    action: str  # accept/rerun/rerun_local/stop
    reason: str
    round_num: int
    threshold: float = 0.0

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "reason": self.reason,
            "round_num": self.round_num,
            "threshold": self.threshold,
        }

    @classmethod
    def from_dict(cls, d: dict) -> DecisionLog:
        return cls(
            action=d.get("action", ""),
            reason=d.get("reason", ""),
            round_num=d.get("round_num", 0),
            threshold=d.get("threshold", 0.0),
        )


@dataclass
class RoundRecord:
    """A single round within a trajectory."""

    round_num: int
    draft_plan: DraftPlan | None = None
    critic_findings: CriticFindings | None = None
    decision: DecisionLog | None = None

    def to_dict(self) -> dict:
        return {
            "round_num": self.round_num,
            "draft_plan": self.draft_plan.to_dict() if self.draft_plan else None,
            "critic_findings": self.critic_findings.to_dict() if self.critic_findings else None,
            "decision": self.decision.to_dict() if self.decision else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> RoundRecord:
        return cls(
            round_num=d.get("round_num", 0),
            draft_plan=DraftPlan.from_dict(d["draft_plan"]) if d.get("draft_plan") else None,
            critic_findings=CriticFindings.from_dict(d["critic_findings"]) if d.get("critic_findings") else None,
            decision=DecisionLog.from_dict(d["decision"]) if d.get("decision") else None,
        )


@dataclass
class TrajectoryRecord:
    """Complete execution history for one pipeline run.

    This is the core data structure for Layer 2: trajectories are
    recorded, serialized to JSON, indexed via FAISS, and retrieved
    for RAG-based decision making.
    """

    trajectory_id: str = ""
    subject: str = ""
    tradition: str = ""
    evidence_pack_dict: dict | None = None
    rounds: list[RoundRecord] = field(default_factory=list)
    final_score: float = 0.0
    final_action: str = ""
    total_latency_ms: int = 0
    total_cost: float = 0.0
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if not self.trajectory_id:
            self.trajectory_id = str(uuid.uuid4())
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_search_text(self) -> str:
        """Build a text representation for FAISS indexing.

        Combines subject, tradition, key decisions, and outcome
        into a searchable string.
        """
        parts = [
            f"Subject: {self.subject}",
            f"Tradition: {self.tradition}",
            f"Score: {self.final_score:.2f}",
            f"Action: {self.final_action}",
            f"Rounds: {len(self.rounds)}",
        ]

        # Add key decisions
        for r in self.rounds:
            if r.decision:
                parts.append(f"Round {r.round_num}: {r.decision.action} ({r.decision.reason[:60]})")
            if r.critic_findings:
                low_layers = [
                    k for k, v in r.critic_findings.layer_scores.items() if v < 0.5
                ]
                if low_layers:
                    parts.append(f"Low: {', '.join(low_layers)}")

        return " | ".join(parts)

    def to_dict(self) -> dict:
        return {
            "trajectory_id": self.trajectory_id,
            "subject": self.subject,
            "tradition": self.tradition,
            "evidence_pack": self.evidence_pack_dict,
            "rounds": [r.to_dict() for r in self.rounds],
            "final_score": round(self.final_score, 4),
            "final_action": self.final_action,
            "total_latency_ms": self.total_latency_ms,
            "total_cost": round(self.total_cost, 6),
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> TrajectoryRecord:
        return cls(
            trajectory_id=d.get("trajectory_id", ""),
            subject=d.get("subject", ""),
            tradition=d.get("tradition", ""),
            evidence_pack_dict=d.get("evidence_pack"),
            rounds=[RoundRecord.from_dict(r) for r in d.get("rounds", [])],
            final_score=d.get("final_score", 0.0),
            final_action=d.get("final_action", ""),
            total_latency_ms=d.get("total_latency_ms", 0),
            total_cost=d.get("total_cost", 0.0),
            timestamp=d.get("timestamp", 0.0),
        )
