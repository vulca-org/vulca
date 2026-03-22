"""Pipeline execution engine -- run a PipelineDefinition to completion."""

from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any, Callable

from vulca.pipeline.node import NodeContext, PipelineNode
from vulca.pipeline.types import (
    EventType,
    PipelineDefinition,
    PipelineEvent,
    PipelineInput,
    PipelineOutput,
    RoundSnapshot,
    RunStatus,
)

logger = logging.getLogger("vulca")

# Cost per image by provider (USD)
_COST_PER_IMAGE: dict[str, float] = {
    "nb2": 0.067,
    "mock": 0.0,
    "openai": 0.04,
    "replicate": 0.05,
}


def _resolve_nodes(
    definition: PipelineDefinition,
) -> dict[str, PipelineNode]:
    """Instantiate built-in nodes from a pipeline definition."""
    from vulca.pipeline.nodes import DecideNode, EvaluateNode, GenerateNode

    _BUILTINS: dict[str, type[PipelineNode]] = {
        "generate": GenerateNode,
        "evaluate": EvaluateNode,
        "decide": DecideNode,
    }

    _ALIASES: dict[str, str] = {
        "draft": "generate",
        "critic": "evaluate",
        "queen": "decide",
        "scout": "generate",
    }

    nodes: dict[str, PipelineNode] = {}
    for node_name in definition.nodes:
        canonical = _ALIASES.get(node_name, node_name)
        cls = _BUILTINS.get(canonical)
        if cls is None:
            raise ValueError(
                f"Unknown node {node_name!r} (canonical: {canonical!r}). "
                f"Available: {list(_BUILTINS)}"
            )
        specs = definition.node_specs.get(node_name, {})
        if specs and canonical == "decide":
            nodes[node_name] = cls(**specs)
        else:
            nodes[node_name] = cls()
    return nodes


def _topo_order(definition: PipelineDefinition) -> list[str]:
    """Return nodes in topological execution order (BFS from entry_point)."""
    adjacency: dict[str, list[str]] = {n: [] for n in definition.nodes}
    for src, dst in definition.edges:
        if src in adjacency:
            adjacency[src].append(dst)

    visited: set[str] = set()
    order: list[str] = []
    queue = [definition.entry_point]

    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in adjacency.get(node, []):
            if neighbor not in visited:
                queue.append(neighbor)

    for n in definition.nodes:
        if n not in visited:
            order.append(n)

    return order


def _resolve_api_key(pipeline_input: PipelineInput) -> str:
    """Resolve API key from input, then environment."""
    return (
        pipeline_input.api_key
        or os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("GOOGLE_API_KEY", "")
    )


async def execute(
    definition: PipelineDefinition,
    pipeline_input: PipelineInput,
    *,
    event_callback: Callable[[PipelineEvent], None] | None = None,
    on_complete: Callable[[PipelineOutput], Any] | None = None,
    interrupt_before: set[str] | None = None,
) -> PipelineOutput:
    """Execute a pipeline definition to completion.

    Parameters
    ----------
    definition:
        The pipeline topology (nodes, edges, conditional edges).
    pipeline_input:
        Input parameters (subject, provider, max_rounds, etc.).
    event_callback:
        Optional callback invoked for each event (for SSE streaming).
    on_complete:
        Optional async callback invoked after successful completion.
        Receives the PipelineOutput. Errors are logged but not raised.
    interrupt_before:
        Set of node names to pause before executing (HITL).
        When a node in this set is reached, the pipeline returns with
        status="waiting_human" and interrupted_at set to that node name.

    Returns
    -------
    PipelineOutput
        Complete execution result.
    """
    session_id = str(uuid.uuid4())[:8]
    t0 = time.monotonic()
    events: list[PipelineEvent] = []
    rounds: list[RoundSnapshot] = []
    node_instances = _resolve_nodes(definition)
    exec_order = _topo_order(definition)

    api_key = _resolve_api_key(pipeline_input)

    def _emit(event: PipelineEvent) -> None:
        events.append(event)
        if event_callback:
            event_callback(event)

    def _emit_progress(message: str) -> None:
        """Emit a progress event from within a node (e.g., generation steps)."""
        _emit(PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage="generate",
            payload={"message": message},
            timestamp_ms=int((time.monotonic() - t0) * 1000),
        ))

    ctx = NodeContext(
        subject=pipeline_input.subject,
        intent=pipeline_input.intent or pipeline_input.subject,
        tradition=pipeline_input.tradition,
        provider=pipeline_input.provider,
        api_key=api_key,
        max_rounds=pipeline_input.max_rounds,
        max_cost_usd=pipeline_input.max_cost_usd,
        emit_progress=_emit_progress,
    )

    # Inject node_params so individual nodes can read them
    if pipeline_input.node_params:
        ctx.set("node_params", pipeline_input.node_params)

    status = RunStatus.RUNNING
    final_decision = "stop"

    for round_num in range(1, pipeline_input.max_rounds + 1):
        ctx.round_num = round_num
        round_t0 = time.monotonic()

        for node_name in exec_order:
            # HITL: pause before this node if requested
            if interrupt_before and node_name in interrupt_before:
                _emit(
                    PipelineEvent(
                        event_type=EventType.HUMAN_REQUIRED,
                        stage=node_name,
                        round_num=round_num,
                        payload={"reason": f"Human review required before {node_name}"},
                        timestamp_ms=int((time.monotonic() - t0) * 1000),
                    )
                )
                total_ms = int((time.monotonic() - t0) * 1000)
                return PipelineOutput(
                    session_id=session_id,
                    status=RunStatus.WAITING_HUMAN.value,
                    tradition=ctx.tradition,
                    best_candidate_id=ctx.get("candidate_id", ""),
                    best_image_url=ctx.get("image_url", ""),
                    final_scores=ctx.get("scores", {}),
                    weighted_total=ctx.get("weighted_total", 0.0),
                    rounds=rounds,
                    events=events,
                    total_rounds=len(rounds),
                    total_latency_ms=total_ms,
                    total_cost_usd=ctx.cost_usd,
                    interrupted_at=node_name,
                    summary=f"Pipeline paused before '{node_name}' for human review.",
                )

            node = node_instances[node_name]
            _emit(
                PipelineEvent(
                    event_type=EventType.STAGE_STARTED,
                    stage=node_name,
                    round_num=round_num,
                    timestamp_ms=int((time.monotonic() - t0) * 1000),
                )
            )

            try:
                output = await node.run(ctx)
            except Exception as exc:
                logger.error("Node %s failed: %s", node_name, exc)
                _emit(
                    PipelineEvent(
                        event_type=EventType.PIPELINE_FAILED,
                        stage=node_name,
                        round_num=round_num,
                        payload={"error": str(exc)},
                        timestamp_ms=int((time.monotonic() - t0) * 1000),
                    )
                )
                status = RunStatus.FAILED
                break

            # Merge node output into context
            if output:
                ctx.data.update(output)

            # Include node output in stage_completed payload
            # WU-1: Inject candidates array for generate/draft nodes
            stage_payload = dict(output) if output else {}
            if node_name in ("generate", "draft") and output and "image_b64" in output:
                stage_payload["candidates"] = [{
                    "candidate_id": output.get("candidate_id", ""),
                    "image_url": output.get("image_url", ""),
                    "image_b64": output.get("image_b64", ""),
                    "image_mime": output.get("image_mime", "image/png"),
                    "round_num": round_num,
                }]
            _emit(
                PipelineEvent(
                    event_type=EventType.STAGE_COMPLETED,
                    stage=node_name,
                    round_num=round_num,
                    payload=stage_payload,
                    timestamp_ms=int((time.monotonic() - t0) * 1000),
                )
            )

            # Cost gate: check after generate nodes
            if node_name in ("generate", "draft") and ctx.provider != "mock":
                cost_per = _COST_PER_IMAGE.get(ctx.provider, 0.067)
                ctx.cost_usd += cost_per
                if ctx.cost_usd > ctx.max_cost_usd:
                    logger.warning(
                        "Cost gate: $%.2f > $%.2f limit",
                        ctx.cost_usd,
                        ctx.max_cost_usd,
                    )
                    _emit(
                        PipelineEvent(
                            event_type=EventType.PIPELINE_FAILED,
                            stage=node_name,
                            round_num=round_num,
                            payload={"error": "Cost gate exceeded", "cost_usd": ctx.cost_usd},
                            timestamp_ms=int((time.monotonic() - t0) * 1000),
                        )
                    )
                    status = RunStatus.FAILED
                    break

        if status == RunStatus.FAILED:
            break

        # Record round snapshot
        decision = ctx.get("decision", "stop")
        final_decision = decision
        round_ms = int((time.monotonic() - round_t0) * 1000)
        rounds.append(
            RoundSnapshot(
                round_num=round_num,
                candidates_generated=1,
                best_candidate_id=ctx.get("candidate_id", ""),
                weighted_total=ctx.get("weighted_total", 0.0),
                dimension_scores=ctx.get("scores", {}),
                decision=decision,
                latency_ms=round_ms,
            )
        )

        _emit(
            PipelineEvent(
                event_type=EventType.DECISION_MADE,
                stage="decide",
                round_num=round_num,
                payload={
                    "decision": decision,
                    "weighted_total": ctx.get("weighted_total", 0.0),
                    "round": round_num,
                    "budget_state": {
                        "rounds_used": round_num,
                        "max_rounds": ctx.max_rounds,
                        "cost_usd": ctx.cost_usd,
                    },
                },
                timestamp_ms=int((time.monotonic() - t0) * 1000),
            )
        )

        if decision == "accept":
            status = RunStatus.COMPLETED
            break
        elif decision == "stop":
            status = RunStatus.COMPLETED
            break

    if status == RunStatus.RUNNING:
        status = RunStatus.COMPLETED

    total_ms = int((time.monotonic() - t0) * 1000)

    _emit(
        PipelineEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            round_num=len(rounds),
            payload={
                "status": status.value,
                "decision": final_decision,
                "total_cost_usd": ctx.cost_usd,
                "total_rounds": len(rounds),
                "total_latency_ms": total_ms,
                "best_candidate_id": ctx.get("candidate_id", ""),
            },
            timestamp_ms=total_ms,
        )
    )

    summary = (
        f"Pipeline '{definition.name}' completed in {len(rounds)} round(s). "
        f"Decision: {final_decision}. "
        f"Weighted total: {ctx.get('weighted_total', 0.0):.3f}"
    )

    output = PipelineOutput(
        session_id=session_id,
        status=status.value,
        tradition=ctx.tradition,
        best_candidate_id=ctx.get("candidate_id", ""),
        best_image_url=ctx.get("image_url", ""),
        final_scores=ctx.get("scores", {}),
        weighted_total=ctx.get("weighted_total", 0.0),
        rounds=rounds,
        events=events,
        total_rounds=len(rounds),
        total_latency_ms=total_ms,
        total_cost_usd=ctx.cost_usd,
        summary=summary,
    )

    # Fire on_complete hook (non-fatal)
    if on_complete and status != RunStatus.FAILED:
        try:
            result = on_complete(output)
            if hasattr(result, "__await__"):
                await result
        except Exception as exc:
            logger.warning("on_complete hook failed: %s", exc)

    return output
