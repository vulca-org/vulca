"""Pipeline execution engine -- run a PipelineDefinition to completion."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

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

    # Also accept legacy names
    _ALIASES: dict[str, str] = {
        "draft": "generate",
        "critic": "evaluate",
        "queen": "decide",
        "scout": "generate",  # Scout → just generate in slim mode
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
        # Pass node_specs if available
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

    # Add any unvisited nodes at the end
    for n in definition.nodes:
        if n not in visited:
            order.append(n)

    return order


async def execute(
    definition: PipelineDefinition,
    pipeline_input: PipelineInput,
) -> PipelineOutput:
    """Execute a pipeline definition to completion.

    Parameters
    ----------
    definition:
        The pipeline topology (nodes, edges, conditional edges).
    pipeline_input:
        Input parameters (subject, provider, max_rounds, etc.).

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

    ctx = NodeContext(
        subject=pipeline_input.subject,
        intent=pipeline_input.intent or pipeline_input.subject,
        tradition=pipeline_input.tradition,
        provider=pipeline_input.provider,
        api_key="",
        max_rounds=pipeline_input.max_rounds,
    )

    status = RunStatus.RUNNING
    final_decision = "stop"

    for round_num in range(1, pipeline_input.max_rounds + 1):
        ctx.round_num = round_num
        round_t0 = time.monotonic()

        for node_name in exec_order:
            node = node_instances[node_name]
            events.append(
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
                events.append(
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

            events.append(
                PipelineEvent(
                    event_type=EventType.STAGE_COMPLETED,
                    stage=node_name,
                    round_num=round_num,
                    timestamp_ms=int((time.monotonic() - t0) * 1000),
                )
            )

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

        events.append(
            PipelineEvent(
                event_type=EventType.DECISION_MADE,
                stage="decide",
                round_num=round_num,
                payload={"decision": decision},
                timestamp_ms=int((time.monotonic() - t0) * 1000),
            )
        )

        if decision == "accept":
            status = RunStatus.COMPLETED
            break
        elif decision == "stop":
            status = RunStatus.COMPLETED
            break
        # decision == "rerun" → continue loop

    if status == RunStatus.RUNNING:
        status = RunStatus.COMPLETED

    total_ms = int((time.monotonic() - t0) * 1000)

    events.append(
        PipelineEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            round_num=len(rounds),
            payload={"status": status.value, "decision": final_decision},
            timestamp_ms=total_ms,
        )
    )

    summary = (
        f"Pipeline '{definition.name}' completed in {len(rounds)} round(s). "
        f"Decision: {final_decision}. "
        f"Weighted total: {ctx.get('weighted_total', 0.0):.3f}"
    )

    return PipelineOutput(
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
        summary=summary,
    )
