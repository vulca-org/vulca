"""PipelineState — LangGraph TypedDict state definition.

This replaces the ad-hoc dict passing in the old orchestrator with
a strongly-typed state that LangGraph tracks and checkpoints.

Key design decisions:
- All stage outputs are stored as plain dicts (serializable for checkpointing)
- events list uses Annotated[..., operator.add] for append-only accumulation
- human_action is transient: consumed after each interrupt resume
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class PipelineState(TypedDict, total=False):
    """Full state flowing through the LangGraph pipeline.

    Fields marked total=False are optional — LangGraph will
    merge partial updates from each node.
    """

    # --- Identity ---
    task_id: str
    subject: str
    cultural_tradition: str

    # --- Loop control ---
    current_round: int
    max_rounds: int

    # --- Stage outputs (plain dicts for serializability) ---
    scout_output: dict[str, Any] | None
    evidence_pack: dict[str, Any] | None
    draft_output: dict[str, Any] | None
    critique_output: dict[str, Any] | None
    queen_decision: dict[str, Any] | None
    queen_output: dict[str, Any] | None
    archivist_output: dict[str, Any] | None

    # --- Cultural routing ---
    pipeline_route: dict[str, Any] | None

    # --- Multi-round history ---
    critique_history: list[dict[str, Any]]
    queen_history: list[dict[str, Any]]
    draft_history: list[dict[str, Any]]

    # --- HITL ---
    human_action: dict[str, Any] | None
    pending_interrupt: str | None  # which node requested pause

    # --- Budget tracking ---
    total_cost_usd: float
    candidates_generated: int

    # --- Event buffer (append-only via operator.add) ---
    events: Annotated[list[dict[str, Any]], operator.add]

    # --- Plan state for Queen ---
    plan_state: dict[str, Any] | None

    # --- Pipeline config (passed through for Archivist) ---
    draft_config: dict[str, Any] | None
    critic_config: dict[str, Any] | None
    queen_config: dict[str, Any] | None

    # --- Error tracking ---
    error: str | None

    # --- Pipeline result ---
    final_decision: str | None
    best_candidate_id: str | None
    success: bool | None


def make_initial_state(
    task_id: str,
    subject: str,
    cultural_tradition: str,
    max_rounds: int = 3,
    draft_config: dict | None = None,
    critic_config: dict | None = None,
    queen_config: dict | None = None,
) -> PipelineState:
    """Create the initial state for a new pipeline run."""
    return PipelineState(
        task_id=task_id,
        subject=subject,
        cultural_tradition=cultural_tradition,
        current_round=0,
        max_rounds=max_rounds,
        scout_output=None,
        evidence_pack=None,
        draft_output=None,
        critique_output=None,
        queen_decision=None,
        queen_output=None,
        archivist_output=None,
        pipeline_route=None,
        critique_history=[],
        queen_history=[],
        draft_history=[],
        human_action=None,
        pending_interrupt=None,
        total_cost_usd=0.0,
        candidates_generated=0,
        events=[],
        plan_state=None,
        draft_config=draft_config,
        critic_config=critic_config,
        queen_config=queen_config,
        error=None,
        final_decision=None,
        best_candidate_id=None,
        success=None,
    )
