"""GraphOrchestrator — LangGraph-based pipeline executor.

API-compatible with PipelineOrchestrator: same run_stream() → Iterator[PipelineEvent]
interface, same submit_action() for HITL, same get_run_state() for status queries.

The key difference is that execution flows through a LangGraph StateGraph
instead of the monolithic orchestrator.py while loop.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any

from app.prototype.graph.pipeline_graph import build_default_graph
from app.prototype.graph.state import PipelineState, make_initial_state
from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.run_state import HumanAction, RunState, RunStatus
from app.prototype.pipeline.pipeline_types import PipelineInput

logger = logging.getLogger(__name__)


class GraphOrchestrator:
    """LangGraph-based orchestrator, API-compatible with PipelineOrchestrator.

    Parameters
    ----------
    draft_config : dict, optional
        DraftConfig as dict.
    critic_config : dict, optional
        CriticConfig as dict.
    queen_config : dict, optional
        QueenConfig as dict.
    enable_hitl : bool
        Enable human-in-the-loop interrupt points.
    enable_agent_critic : bool
        Use LLM-based CriticLLM instead of rule-only scoring.
    max_rounds : int
        Maximum evaluation rounds.
    """

    def __init__(
        self,
        draft_config: dict | None = None,
        critic_config: dict | None = None,
        queen_config: dict | None = None,
        enable_hitl: bool = False,
        enable_agent_critic: bool = False,
        max_rounds: int = 3,
        template: str = "default",
    ) -> None:
        self._draft_config = draft_config
        self._critic_config = critic_config
        self._queen_config = queen_config
        self._enable_hitl = enable_hitl
        self._enable_agent_critic = enable_agent_critic
        self._max_rounds = max_rounds
        self._template_name = template

        # Resolve template (graceful fallback to None → uses build_default_graph)
        self._template = None
        try:
            from app.prototype.graph.templates.template_registry import TemplateRegistry
            self._template = TemplateRegistry.get(template)
        except (ImportError, KeyError):
            pass

        # Active runs tracking
        self._runs: dict[str, RunState] = {}
        # Compiled graph instances per task (for HITL resume)
        self._graphs: dict[str, Any] = {}
        self._configs: dict[str, dict] = {}

    def get_run_state(self, task_id: str) -> RunState | None:
        """Get the RunState for an active run."""
        return self._runs.get(task_id)

    def run_stream(self, pipeline_input: PipelineInput) -> Iterator[PipelineEvent]:
        """Execute pipeline as an event stream, compatible with SSE routes.

        Yields PipelineEvent objects for each stage transition, matching
        the exact same protocol as PipelineOrchestrator.run_stream().
        """
        t0 = time.monotonic()
        task_id = pipeline_input.task_id

        run_state = RunState(task_id=task_id, status=RunStatus.RUNNING)
        self._runs[task_id] = run_state

        try:
            # Build graph — use template if available, otherwise default
            if self._template is not None:
                from app.prototype.graph.template_builder import build_graph_from_template
                compiled = build_graph_from_template(
                    template=self._template,
                    draft_config=self._draft_config,
                    queen_config=self._queen_config,
                    enable_agent_critic=self._enable_agent_critic,
                    enable_hitl=self._enable_hitl,
                    use_checkpointer=self._enable_hitl,
                )
            else:
                compiled = build_default_graph(
                    draft_config=self._draft_config,
                    queen_config=self._queen_config,
                    enable_agent_critic=self._enable_agent_critic,
                    enable_hitl=self._enable_hitl,
                    use_checkpointer=self._enable_hitl,  # checkpointer needed for HITL resume
                )
            self._graphs[task_id] = compiled

            # Build initial state
            initial_state = make_initial_state(
                task_id=task_id,
                subject=pipeline_input.subject,
                cultural_tradition=pipeline_input.cultural_tradition,
                max_rounds=self._max_rounds,
                draft_config=self._draft_config,
                critic_config=self._critic_config,
                queen_config=self._queen_config,
            )

            # Config for LangGraph (thread_id needed for checkpointer)
            config = {"configurable": {"thread_id": task_id}}
            self._configs[task_id] = config

            # Stream through graph nodes
            seen_events = 0
            for chunk in compiled.stream(initial_state, config=config):
                # LangGraph stream yields: {node_name: state_update}
                for node_name, state_update in chunk.items():
                    if node_name == "__end__":
                        continue

                    # Update run_state for API queries
                    run_state.current_stage = node_name

                    # Extract events emitted by this node
                    new_events = state_update.get("events", [])
                    for evt_dict in new_events[seen_events:]:
                        yield _dict_to_pipeline_event(evt_dict, t0)
                    seen_events = 0  # events are per-node, not cumulative

            # Emit PIPELINE_COMPLETED
            total_ms = int((time.monotonic() - t0) * 1000)

            # Get final state for completion payload
            final_state = compiled.get_state(config).values if self._enable_hitl else {}

            completion_payload = {
                "task_id": task_id,
                "final_decision": final_state.get("final_decision", "stop") if final_state else "stop",
                "best_candidate_id": final_state.get("best_candidate_id") if final_state else None,
                "total_rounds": final_state.get("current_round", 1) if final_state else 1,
                "total_latency_ms": total_ms,
                "success": True,
                "total_cost_usd": round(final_state.get("total_cost_usd", 0.0), 6) if final_state else 0.0,
                "candidates_generated": final_state.get("candidates_generated", 0) if final_state else 0,
                "stages": [],
            }

            run_state.status = RunStatus.COMPLETED
            yield PipelineEvent(
                event_type=EventType.PIPELINE_COMPLETED,
                stage="",
                round_num=completion_payload.get("total_rounds", 1),
                payload=completion_payload,
                timestamp_ms=total_ms,
            )

        except Exception as exc:
            total_ms = int((time.monotonic() - t0) * 1000)
            run_state.status = RunStatus.FAILED

            yield PipelineEvent(
                event_type=EventType.PIPELINE_FAILED,
                stage="",
                round_num=0,
                payload={
                    "task_id": task_id,
                    "success": False,
                    "error": str(exc),
                    "total_latency_ms": total_ms,
                    "stages": [],
                },
                timestamp_ms=total_ms,
            )

    def submit_action(
        self,
        task_id: str,
        action: str,
        locked_dimensions: list[str] | None = None,
        rerun_dimensions: list[str] | None = None,
        candidate_id: str = "",
        reason: str = "",
    ) -> bool:
        """Submit a human action for an active run.

        For the graph orchestrator, this updates the state and resumes
        the compiled graph from its interrupt point.
        """
        run_state = self._runs.get(task_id)
        if run_state is None or run_state.status != RunStatus.WAITING_HUMAN:
            return False

        compiled = self._graphs.get(task_id)
        config = self._configs.get(task_id)
        if compiled is None or config is None:
            return False

        # Update state with human action
        human_action = {
            "action": action,
            "locked_dimensions": locked_dimensions or [],
            "rerun_dimensions": rerun_dimensions or [],
            "candidate_id": candidate_id,
            "reason": reason,
        }

        # Resume graph with human action injected into state
        compiled.update_state(config, {"human_action": human_action})

        # Also update internal run state for the old-style HITL flow
        ha = HumanAction(
            action=action,
            locked_dimensions=locked_dimensions or [],
            rerun_dimensions=rerun_dimensions or [],
            candidate_id=candidate_id,
            reason=reason,
        )
        run_state.submit_human_action(ha)
        return True


def _dict_to_pipeline_event(evt_dict: dict, t0: float) -> PipelineEvent:
    """Convert a plain dict event to a PipelineEvent object.

    The event dicts emitted by graph nodes use the same schema as
    PipelineEvent.to_dict(), so we just reconstruct the dataclass.
    """
    # Map string event_type back to EventType enum
    evt_type_str = evt_dict.get("event_type", "stage_started")
    try:
        evt_type = EventType(evt_type_str)
    except ValueError:
        evt_type = EventType.STAGE_STARTED

    # Adjust timestamp to be relative to pipeline start
    node_ts = evt_dict.get("timestamp_ms", 0)
    absolute_ts = int((time.monotonic() - t0) * 1000) if node_ts == 0 else node_ts

    return PipelineEvent(
        event_type=evt_type,
        stage=evt_dict.get("stage", ""),
        round_num=evt_dict.get("round_num", 0),
        payload=evt_dict.get("payload", {}),
        timestamp_ms=absolute_ts,
    )
