"""GraphOrchestrator — LangGraph-based pipeline executor (**production-candidate**).

Orchestrator Architecture Decision (Route B+, 2026-03-10):
Status: PRODUCTION-CANDIDATE — feature-parity with PipelineOrchestrator.
Production orchestrator: app.prototype.orchestrator.PipelineOrchestrator
Unified entry point: app.prototype.orchestrator.get_orchestrator(mode="graph")

API-compatible with PipelineOrchestrator: same run_stream() -> Iterator[PipelineEvent]
interface, same submit_action() for HITL, same get_run_state() for status queries.

The key difference is that execution flows through a LangGraph StateGraph
instead of the monolithic orchestrator.py while loop. Extra capabilities:
- Template-based topology definitions (template_registry)
- Custom node/edge topologies via API
- Agent plugin registry (@AgentRegistry.register)

Production features (P3, 2026-03-14):
- Cost gate: hard USD limit per run (_MAX_COST_PER_RUN_USD)
- Checkpoint resume: resume_from parameter to skip completed stages
- Dynamic weights: compute_dynamic_weights() integration in critic scoring
- Trajectory recording: full execution history via TrajectoryRecorder
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any

from app.prototype.checkpoints.pipeline_checkpoint import (
    load_pipeline_stage,
    save_pipeline_stage,
)
from app.prototype.cultural_pipelines.dynamic_weights import compute_dynamic_weights
from app.prototype.graph.node_runtime import NodeRuntimeManager
from app.prototype.graph.pipeline_graph import build_default_graph
from app.prototype.graph.state import PipelineState, make_initial_state
from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.run_state import HumanAction, RunState, RunStatus
from app.prototype.pipeline.pipeline_types import PipelineInput
from app.prototype.trajectory.trajectory_recorder import TrajectoryRecorder
from app.prototype.trajectory.trajectory_types import CriticFindings, DecisionLog, DraftPlan, PromptTrace

logger = logging.getLogger(__name__)

# Cost per image for real providers (mirrored from PipelineOrchestrator)
_COST_PER_IMAGE: dict[str, float] = {
    "nb2": 0.067,  # Gemini 3.1 Flash image generation (~1K input tokens)
    "mock": 0.0,
}

# Hard cost gate per run (NB2 ~$0.067/image x 4 candidates x 3 rounds + Critic Pro calls)
_MAX_COST_PER_RUN_USD = 2.00

# Stage order for checkpoint resume
_STAGE_ORDER = ["scout", "draft", "critic", "queen"]


class GraphOrchestrator:
    """LangGraph-based orchestrator, API-compatible with PipelineOrchestrator.

    .. versionchanged:: P3 (2026-03-14)
        Upgraded from **experimental** to **production-candidate** status.
        Added: cost gate, checkpoint resume, dynamic weight integration,
        and trajectory recording — achieving feature parity with
        :class:`~app.prototype.orchestrator.PipelineOrchestrator`.
        Access via ``get_orchestrator(mode="graph")``.

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
        enable_skill_hook: bool = False,
        skill_hook_names: list[str] | None = None,
    ) -> None:
        self._draft_config = draft_config
        self._critic_config = critic_config
        self._queen_config = queen_config
        self._enable_hitl = enable_hitl
        self._enable_agent_critic = enable_agent_critic
        self._max_rounds = max_rounds
        self._template_name = template
        self._enable_skill_hook = enable_skill_hook
        self._skill_hook_names = skill_hook_names or []

        # Resolve template (graceful fallback to None → uses build_default_graph)
        self._template = None
        try:
            from app.prototype.graph.templates.template_registry import TemplateRegistry
            self._template = TemplateRegistry.get(template)
        except (ImportError, KeyError):
            pass

        # Optional Langfuse observer (same pattern as PipelineOrchestrator)
        self._langfuse = None
        try:
            from langfuse import Langfuse
            self._langfuse = Langfuse()
        except (ImportError, Exception):
            pass

        # Active runs tracking
        self._runs: dict[str, RunState] = {}
        # Compiled graph instances per task (for HITL resume)
        self._graphs: dict[str, Any] = {}
        self._configs: dict[str, dict] = {}
        # Node runtime managers per task (mute/bypass/expand)
        self._node_runtimes: dict[str, NodeRuntimeManager] = {}

    def get_run_state(self, task_id: str) -> RunState | None:
        """Get the RunState for an active run."""
        return self._runs.get(task_id)

    def set_node_runtime(self, task_id: str, manager: NodeRuntimeManager) -> None:
        """Attach a NodeRuntimeManager for mute/bypass checks during execution."""
        self._node_runtimes[task_id] = manager

    def run_stream(self, pipeline_input: PipelineInput) -> Iterator[PipelineEvent]:
        """Execute pipeline as an event stream, compatible with SSE routes.

        Yields PipelineEvent objects for each stage transition, matching
        the exact same protocol as PipelineOrchestrator.run_stream().

        Supports ``resume_from`` via PipelineInput.resume_from to skip
        completed stages and reload their outputs from checkpoints.
        """
        t0 = time.monotonic()
        task_id = pipeline_input.task_id
        resume_from = pipeline_input.resume_from

        run_state = RunState(task_id=task_id, status=RunStatus.RUNNING)
        self._runs[task_id] = run_state

        # Running cost accumulator
        run_cost_usd = 0.0
        images_generated = 0

        # Trajectory recorder
        trajectory_recorder = TrajectoryRecorder()

        try:
            # ── Checkpoint resume validation ──────────────────────────
            if resume_from and resume_from in _STAGE_ORDER:
                resume_idx = _STAGE_ORDER.index(resume_from)
                for prior_stage in _STAGE_ORDER[:resume_idx]:
                    ckpt = load_pipeline_stage(task_id, prior_stage)
                    if ckpt is None:
                        raise RuntimeError(
                            f"Cannot resume from '{resume_from}': "
                            f"checkpoint for '{prior_stage}' not found"
                        )
                logger.info(
                    "Resuming task %s from stage '%s' (skipping %s)",
                    task_id, resume_from,
                    _STAGE_ORDER[:resume_idx],
                )

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

            # ── Checkpoint resume: pre-populate state from checkpoints ──
            if resume_from and resume_from in _STAGE_ORDER:
                resume_idx = _STAGE_ORDER.index(resume_from)
                for prior_stage in _STAGE_ORDER[:resume_idx]:
                    ckpt = load_pipeline_stage(task_id, prior_stage)
                    if ckpt and prior_stage == "scout":
                        initial_state["scout_output"] = ckpt
                        initial_state["evidence_pack"] = ckpt.get("evidence_pack")
                    elif ckpt and prior_stage == "draft":
                        initial_state["draft_output"] = ckpt
                        # Account for already-generated images in cost tracking
                        prev_candidates = ckpt.get("candidates", [])
                        images_generated += len(prev_candidates)
                    elif ckpt and prior_stage == "critic":
                        initial_state["critique_output"] = ckpt

            # Config for LangGraph (thread_id needed for checkpointer)
            config = {"configurable": {"thread_id": task_id}}
            self._configs[task_id] = config

            # Start trajectory recording
            trajectory_recorder.start(
                subject=pipeline_input.subject,
                tradition=pipeline_input.cultural_tradition,
                evidence_pack_dict=initial_state.get("scout_output"),
            )

            # Determine provider for cost calculation
            provider = "mock"
            if self._draft_config and isinstance(self._draft_config, dict):
                provider = self._draft_config.get("provider", "mock")

            # Stream through graph nodes
            seen_events = 0
            nrt = self._node_runtimes.get(task_id)
            for chunk in compiled.stream(initial_state, config=config):
                # LangGraph stream yields: {node_name: state_update}
                for node_name, state_update in chunk.items():
                    if node_name == "__end__":
                        continue

                    # ── Mute/Bypass runtime checks ─────────────────────
                    if nrt is not None:
                        if nrt.is_muted(node_name):
                            logger.info("Node '%s' is muted — skipping effects", node_name)
                            yield PipelineEvent(
                                event_type=EventType.STAGE_STARTED,
                                stage=node_name,
                                round_num=0,
                                payload={"muted": True},
                                timestamp_ms=int((time.monotonic() - t0) * 1000),
                            )
                            continue
                        if nrt.is_bypassed(node_name):
                            logger.info("Node '%s' is bypassed — pass-through", node_name)
                            yield PipelineEvent(
                                event_type=EventType.STAGE_STARTED,
                                stage=node_name,
                                round_num=0,
                                payload={"bypassed": True},
                                timestamp_ms=int((time.monotonic() - t0) * 1000),
                            )
                            continue

                    # Update run_state for API queries
                    run_state.current_stage = node_name

                    # ── Cost gate check after draft node ──────────────
                    if node_name == "draft":
                        new_candidates = (state_update.get("draft_output") or {}).get("candidates", [])
                        images_generated += len(new_candidates)
                        cost_per_image = _COST_PER_IMAGE.get(provider, 0.0)
                        run_cost_usd = images_generated * cost_per_image
                        if run_cost_usd > _MAX_COST_PER_RUN_USD:
                            raise RuntimeError(
                                f"Cost gate exceeded: ${run_cost_usd:.3f} > ${_MAX_COST_PER_RUN_USD}"
                            )

                    # ── Dynamic weights after critic node ─────────────
                    if node_name == "critic" and self._enable_agent_critic:
                        self._apply_dynamic_weights(state_update, initial_state)

                    # ── Skill hook after critic ────────────────────────
                    if node_name == "critic" and self._enable_skill_hook:
                        try:
                            from app.prototype.skills.pipeline_hook import run_pipeline_skills
                            candidates = state_update.get("candidates") or initial_state.get("candidates") or []
                            tradition = initial_state.get("cultural_tradition", "default")
                            for cand in (candidates if isinstance(candidates, list) else []):
                                img = cand.get("image_path", "") if isinstance(cand, dict) else ""
                                if img:
                                    run_pipeline_skills(
                                        image_path=img,
                                        tradition=tradition,
                                        stage="post_critic",
                                        skill_names=self._skill_hook_names or None,
                                    )
                        except Exception:
                            pass  # skill hook is best-effort

                    # ── Trajectory recording per node ─────────────────
                    self._record_node_trajectory(
                        trajectory_recorder, node_name, state_update,
                        provider=provider,
                    )

                    # ── Save checkpoint for each completed stage ──────
                    if node_name in _STAGE_ORDER:
                        stage_data = state_update.get(f"{node_name}_output") or state_update
                        save_pipeline_stage(task_id, node_name, stage_data)

                    # Extract events emitted by this node
                    new_events = state_update.get("events", [])
                    for evt_dict in new_events[seen_events:]:
                        yield _dict_to_pipeline_event(evt_dict, t0)
                    seen_events = 0  # events are per-node, not cumulative

            # Emit PIPELINE_COMPLETED
            total_ms = int((time.monotonic() - t0) * 1000)

            # Get final state for completion payload
            final_state = compiled.get_state(config).values if self._enable_hitl else {}

            total_cost = run_cost_usd or (
                round(final_state.get("total_cost_usd", 0.0), 6) if final_state else 0.0
            )
            final_decision = final_state.get("final_decision", "stop") if final_state else "stop"
            final_score = 0.0
            if final_state:
                # Extract best score from last critique
                critique = final_state.get("critique_output") or {}
                scores = critique.get("scores", [])
                if scores:
                    final_score = max(
                        (s.get("weighted_score", 0.0) for s in scores),
                        default=0.0,
                    )

            completion_payload = {
                "task_id": task_id,
                "final_decision": final_decision,
                "best_candidate_id": final_state.get("best_candidate_id") if final_state else None,
                "total_rounds": final_state.get("current_round", 1) if final_state else 1,
                "total_latency_ms": total_ms,
                "success": True,
                "total_cost_usd": round(total_cost, 6),
                "candidates_generated": final_state.get("candidates_generated", 0) if final_state else images_generated,
                "stages": [],
            }

            # Finalize trajectory
            if trajectory_recorder.active:
                trajectory_recorder.finish(
                    final_score=final_score,
                    final_action=final_decision,
                    total_latency_ms=total_ms,
                    total_cost=total_cost,
                )

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

            # Finalize trajectory on failure too
            if trajectory_recorder.active:
                try:
                    trajectory_recorder.finish(
                        final_score=0.0,
                        final_action="failed",
                        total_latency_ms=total_ms,
                        total_cost=run_cost_usd,
                    )
                except Exception:
                    logger.warning("Failed to save trajectory on error for %s", task_id)

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
        finally:
            if self._langfuse:
                try:
                    self._langfuse.flush()
                except Exception:
                    pass
            # Cleanup graphs/configs/runtimes
            self._graphs.pop(task_id, None)
            self._configs.pop(task_id, None)
            self._node_runtimes.pop(task_id, None)

    # ------------------------------------------------------------------
    # Dynamic weights integration
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_dynamic_weights(
        state_update: dict[str, Any],
        initial_state: dict[str, Any],
    ) -> None:
        """Apply dynamic weight modulation to critic output.

        Reads base weights from the pipeline route / critic config,
        computes modulated weights via compute_dynamic_weights(), and
        injects them into the critique output for downstream consumers
        (Queen, radar chart, trajectory).
        """
        critique_output = state_update.get("critique_output") or {}
        route = initial_state.get("pipeline_route") or {}
        critic_cfg_dict = route.get("critic_config") or initial_state.get("critic_config") or {}
        base_weights = critic_cfg_dict.get("weights", {})

        if not base_weights:
            # Fall back to uniform weights
            from app.prototype.agents.critic_config import DIMENSIONS
            base_weights = {d: 1.0 / len(DIMENSIONS) for d in DIMENSIONS}

        # Build minimal layer_states from critique scores
        from app.prototype.agents.layer_state import LayerState
        layer_states: dict[str, LayerState] = {}
        for score_entry in critique_output.get("scores", []):
            dim_scores = score_entry.get("dimension_scores", {})
            for dim, val in dim_scores.items():
                if dim not in layer_states:
                    layer_states[dim] = LayerState(
                        score=val if isinstance(val, (int, float)) else 0.5,
                    )

        current_round = initial_state.get("current_round", 1)

        dyn_weights = compute_dynamic_weights(
            base_weights=base_weights,
            layer_states=layer_states,
            round_num=current_round,
        )

        # Inject dynamic weights into the critique output
        critique_output["dynamic_weights"] = dyn_weights
        state_update["critique_output"] = critique_output

    # ------------------------------------------------------------------
    # Trajectory recording helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _record_node_trajectory(
        recorder: TrajectoryRecorder,
        node_name: str,
        state_update: dict[str, Any],
        provider: str = "mock",
    ) -> None:
        """Record trajectory data for a completed graph node."""
        if not recorder.active:
            return

        current_round = state_update.get("current_round", 1)

        if node_name == "draft":
            draft_out = state_update.get("draft_output") or {}
            candidates = draft_out.get("candidates", [])
            prompt_text = draft_out.get("prompt", "")
            recorder.record_draft(
                DraftPlan(
                    prompt_trace=PromptTrace(
                        raw_prompt=prompt_text,
                        enhanced_prompt=draft_out.get("enhanced_prompt", prompt_text),
                        prompt_hash="",
                        model_ref=provider,
                    ),
                    provider=provider,
                    latency_ms=draft_out.get("latency_ms", 0),
                    n_candidates=len(candidates),
                ),
                round_num=current_round,
            )

        elif node_name == "critic":
            critique = state_update.get("critique_output") or {}
            scores = critique.get("scores", [])
            layer_scores: dict[str, float] = {}
            best_weighted = 0.0
            for s in scores:
                ws = s.get("weighted_score", 0.0)
                if ws > best_weighted:
                    best_weighted = ws
                for dim, val in s.get("dimension_scores", {}).items():
                    layer_scores[dim] = val if isinstance(val, (int, float)) else 0.0
            recorder.record_critic(
                CriticFindings(
                    layer_scores=layer_scores,
                    weighted_score=best_weighted,
                ),
                round_num=current_round,
            )

        elif node_name == "queen":
            queen_dec = state_update.get("queen_decision") or state_update.get("queen_output") or {}
            recorder.record_decision(
                DecisionLog(
                    action=queen_dec.get("action", "stop"),
                    reason=queen_dec.get("reason", ""),
                    round_num=current_round,
                    threshold=queen_dec.get("threshold", 0.0),
                ),
                round_num=current_round,
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

    def run_sync(self, pipeline_input: PipelineInput) -> dict[str, Any]:
        """Execute pipeline synchronously, returning final state.

        Collects all events and returns a dict with:
        - events: list of all PipelineEvent dicts
        - final_state: last known state
        - success: bool
        - error: str or None
        """
        events = []
        final_event = None
        for event in self.run_stream(pipeline_input):
            events.append(event.to_dict())
            final_event = event

        success = final_event is not None and final_event.event_type == EventType.PIPELINE_COMPLETED
        error = None
        if final_event and final_event.event_type == EventType.PIPELINE_FAILED:
            error = final_event.payload.get("error", "Unknown error")

        return {
            "events": events,
            "success": success,
            "error": error,
            "task_id": pipeline_input.task_id,
        }


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
