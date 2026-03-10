"""Pydantic request/response schemas for the prototype API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CreateRunRequest(BaseModel):
    """Request body for POST /runs."""

    subject: str = Field(..., min_length=1, max_length=500, description="Artwork subject")
    intent: str | None = Field(default=None, max_length=500, description="Creative intent (defaults to subject if omitted)")
    tradition: str = Field(
        default="default",
        description="Cultural tradition",
    )
    provider: str = Field(default="auto", description="Image provider: auto | nb2 | mock (auto detects API key)")
    n_candidates: int = Field(default=4, ge=1, le=8, description="Candidates per round")
    max_rounds: int = Field(default=3, ge=1, le=5, description="Max Queen rounds")
    enable_hitl: bool = Field(default=False, description="Enable human-in-the-loop")
    enable_agent_critic: bool = Field(default=True, description="Use LLM-based Critic (CriticLLM) instead of rule-only scoring")
    enable_prompt_enhancer: bool = Field(default=True, description="Inject evolved context into Draft prompts")
    enable_llm_queen: bool = Field(default=False, description="Use LLM+RAG Queen for ambiguous decisions")
    use_graph: bool = Field(default=False, description="Use LangGraph-based pipeline (experimental) instead of classic PipelineOrchestrator (production)")
    template: str = Field(default="default", description="Graph template: default | fast_draft | critique_only | interactive_full | batch_eval")
    enable_parallel_critic: bool = Field(default=False, description="Use parallel L1-L5 scoring (ThreadPoolExecutor) for faster Critic")
    idempotency_key: str | None = Field(default=None, description="Optional idempotency key")

    # M3: custom topology support
    custom_nodes: list[str] | None = Field(default=None, description="Custom topology node list (overrides template)")
    custom_edges: list[tuple[str, str]] | None = Field(default=None, description="Custom topology edges (overrides template)")
    node_params: dict[str, dict] | None = Field(default=None, description="Per-node config overrides keyed by agent id")


class RunStatusResponse(BaseModel):
    """Response for GET /runs/{id}."""

    task_id: str
    status: str                         # pending | running | waiting_human | completed | failed
    current_stage: str = ""
    current_round: int = 0
    final_decision: str | None = None
    best_candidate_id: str | None = None
    total_rounds: int = 0
    total_latency_ms: int = 0
    total_cost_usd: float = 0.0
    success: bool | None = None
    error: str | None = None
    stages: list[dict] = []


class SubmitActionRequest(BaseModel):
    """Request body for POST /runs/{id}/action."""

    action: Literal["approve", "reject", "rerun", "lock_dimensions", "force_accept"] = Field(
        ..., description="HITL action type",
    )
    locked_dimensions: list[str] = Field(default_factory=list)
    rerun_dimensions: list[str] = Field(default_factory=list)
    candidate_id: str = ""
    reason: str = ""


class SubmitActionResponse(BaseModel):
    """Response for POST /runs/{id}/action."""

    accepted: bool
    message: str = ""


# ── Agent + Topology schemas ─────────────────────────────────────────


class AgentInfo(BaseModel):
    """Agent metadata returned by GET /agents."""

    name: str
    display_name: str = ""
    description: str = ""
    supports_hitl: bool = False
    estimated_latency_ms: int = 0
    input_keys: list[str] = []
    output_keys: list[str] = []
    tags: list[str] = []


class ValidateTopologyRequest(BaseModel):
    """Request body for POST /topologies/validate."""

    nodes: list[str] = Field(..., min_length=1)
    edges: list[tuple[str, str]] = Field(..., min_length=1)


class ValidationResponse(BaseModel):
    """Response for POST /topologies/validate."""

    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
