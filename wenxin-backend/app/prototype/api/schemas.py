"""Pydantic request/response schemas for the prototype API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class CreateRunRequest(BaseModel):
    """Request body for POST /runs."""

    subject: str = Field(..., min_length=1, max_length=500, description="Artwork subject")
    intent: str | None = Field(default=None, max_length=500, description="Creative intent (defaults to subject if omitted)")

    @model_validator(mode="before")
    @classmethod
    def _accept_cultural_intent(cls, data: dict) -> dict:
        """Accept 'cultural_intent' as alias for 'intent' (frontend compatibility)."""
        if isinstance(data, dict) and "cultural_intent" in data and "intent" not in data:
            data["intent"] = data.pop("cultural_intent")
        return data
    tradition: str = Field(
        default="default",
        description="Cultural tradition",
    )
    provider: str = Field(default="auto", description="Image provider: auto | nb2 | mock (auto detects API key)")
    n_candidates: int = Field(default=4, ge=1, le=8, description="Candidates per round")
    max_rounds: int = Field(default=3, ge=1, le=5, description="Max Queen rounds")
    enable_hitl: bool = Field(default=False, description="Enable human-in-the-loop")
    enable_agent_critic: bool = Field(default=True, description="[Deprecated: always enabled] Use LLM-based Critic")
    enable_prompt_enhancer: bool = Field(default=True, description="[Deprecated: auto-detected from API key] Inject evolved context into Draft prompts")
    enable_llm_queen: bool = Field(default=False, description="[Deprecated: auto-detected from API key] Use LLM+RAG Queen")
    template: str = Field(default="default", description="Pipeline template: default | fast | critique_only")
    enable_parallel_critic: bool = Field(default=False, description="[Deprecated: not supported in vulca engine] Parallel L1-L5 scoring")
    idempotency_key: str | None = Field(default=None, description="Optional idempotency key")

    # M3: custom topology support
    custom_nodes: list[str] | None = Field(default=None, description="Custom topology node list (overrides template)")
    custom_edges: list[tuple[str, str]] | None = Field(default=None, description="Custom topology edges (overrides template)")
    node_params: dict[str, dict] | None = Field(default=None, description="Per-node config overrides keyed by agent id")
    reference_image_base64: str | None = Field(default=None, description="Base64-encoded reference image for style guidance")


class RunStatusResponse(BaseModel):
    """Response for GET /runs/{id}."""

    task_id: str
    status: str                         # pending | running | waiting_human | completed | failed
    current_stage: str = ""
    current_round: int = 0
    final_decision: str | None = None
    best_candidate_id: str | None = None
    best_image_url: str | None = None
    total_rounds: int = 0
    total_latency_ms: int = 0
    total_cost_usd: float = 0.0
    final_scores: dict = Field(default_factory=dict)
    weighted_total: float = 0.0
    rounds: list[dict] = Field(default_factory=list)
    success: bool | None = None
    error: str | None = None
    stages: list[dict] = Field(default_factory=list)


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
    new_task_id: str | None = None


