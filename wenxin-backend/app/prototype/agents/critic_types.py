"""Critic Agent data types — CritiqueInput, DimensionScore, CandidateScore, CritiqueOutput."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "CandidateScore",
    "CritiqueInput",
    "CritiqueOutput",
    "DimensionScore",
]


@dataclass
class CritiqueInput:
    """Input for the Critic Agent — derived from DraftOutput + ScoutEvidence."""

    task_id: str
    subject: str
    cultural_tradition: str
    evidence: dict                    # ScoutEvidence.to_dict()
    candidates: list[dict] = field(default_factory=list)  # [DraftCandidate.to_dict(), ...]

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "cultural_tradition": self.cultural_tradition,
            "evidence": self.evidence,
            "candidates": self.candidates,
        }


@dataclass
class DimensionScore:
    """Score for a single L1-L5 dimension."""

    dimension: str    # "visual_perception" | ... | "philosophical_aesthetic"
    score: float      # [0.0, 1.0]
    rationale: str    # scoring rationale
    summary: str = ""  # one-sentence human-readable summary
    agent_metadata: dict | None = None  # AgentResult details when escalated

    def to_dict(self) -> dict:
        d = {
            "dimension": self.dimension,
            "score": round(self.score, 4),
            "rationale": self.rationale,
        }
        if self.summary:
            d["summary"] = self.summary
        if self.agent_metadata:
            d["agent_metadata"] = self.agent_metadata
        return d


@dataclass
class CandidateScore:
    """Scored candidate with L1-L5 dimensions, risk tags, and gate decision."""

    candidate_id: str
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    weighted_total: float = 0.0
    risk_tags: list[str] = field(default_factory=list)
    gate_passed: bool = False
    rejected_reasons: list[str] = field(default_factory=list)
    agentic_insights: dict | None = None  # AgenticInsights.to_dict() when enabled

    def to_dict(self) -> dict:
        d = {
            "candidate_id": self.candidate_id,
            "dimension_scores": [d_.to_dict() for d_ in self.dimension_scores],
            "weighted_total": round(self.weighted_total, 4),
            "risk_tags": self.risk_tags,
            "gate_passed": self.gate_passed,
            "rejected_reasons": self.rejected_reasons,
        }
        if self.agentic_insights:
            d["agentic_insights"] = self.agentic_insights
        return d


@dataclass
class CritiqueOutput:
    """Output of the Critic Agent — scored candidates with gate decisions."""

    task_id: str
    scored_candidates: list[CandidateScore] = field(default_factory=list)
    best_candidate_id: str | None = None
    rerun_hint: list[str] = field(default_factory=list)
    evaluation_summary: str = ""      # human-readable 1-2 sentence overall summary
    created_at: str = ""              # ISO 8601
    latency_ms: int = 0
    success: bool = True
    error: str | None = None
    agent_metrics: dict | None = None  # CriticLLM.get_agent_metrics()
    cross_layer_signals: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "task_id": self.task_id,
            "scored_candidates": [s.to_dict() for s in self.scored_candidates],
            "best_candidate_id": self.best_candidate_id,
            "rerun_hint": self.rerun_hint,
            "created_at": self.created_at,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
        }
        if self.evaluation_summary:
            d["evaluation_summary"] = self.evaluation_summary
        if self.agent_metrics:
            d["agent_metrics"] = self.agent_metrics
        if self.cross_layer_signals:
            d["cross_layer_signals"] = self.cross_layer_signals
        return d
