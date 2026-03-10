"""PipelineOrchestrator — single source of truth for pipeline execution.

Orchestrator Architecture Decision (Route B+, 2026-03-10):
Status: **PRODUCTION** — all API routes use this orchestrator by default.
Alternative: app.prototype.graph.GraphOrchestrator (experimental, LangGraph-based)
Unified entry point: app.prototype.orchestrator.get_orchestrator(mode="pipeline")

All entry points (CLI, Gradio, API, benchmark, AB test) use this class.
Supports both synchronous and streaming (generator) modes.
"""

from __future__ import annotations

import dataclasses
import logging
import time
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from app.prototype.agents.archivist_agent import ArchivistAgent
from app.prototype.agents.archivist_types import ArchivistInput
from app.prototype.agents.critic_agent import CriticAgent, build_critique_output
from app.prototype.agents.critic_config import CriticConfig, DIMENSIONS
from app.prototype.agents.critic_types import CandidateScore, CritiqueInput, CritiqueOutput
from app.prototype.agents.draft_agent import DraftAgent
from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.draft_types import DraftInput
from app.prototype.agents.layer_state import LocalRerunRequest
from app.prototype.agents.queen_agent import QueenAgent
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.agents.queen_types import PlanState
from app.prototype.checkpoints.pipeline_checkpoint import (
    load_pipeline_stage,
    save_pipeline_output,
    save_pipeline_stage,
    update_runs_index,
)
from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.run_state import HumanAction, RunState, RunStatus
from app.prototype.pipeline.pipeline_types import (
    PipelineInput,
    PipelineOutput,
    StageResult,
)
from app.prototype.cultural_pipelines.dynamic_weights import compute_dynamic_weights
from app.prototype.cultural_pipelines.pipeline_router import CulturalPipelineRouter
from app.prototype.agents.prompt_enhancer import PromptEnhancer
from app.prototype.tools.scout_service import ScoutService, get_scout_service
from app.prototype.trajectory.trajectory_recorder import TrajectoryRecorder
from app.prototype.trajectory.trajectory_types import (
    CriticFindings,
    DecisionLog,
    DraftPlan,
    PromptTrace,
)

logger = logging.getLogger(__name__)

# Cost per image for real providers
_COST_PER_IMAGE: dict[str, float] = {
    "nb2": 0.067,  # Gemini 3.1 Flash image generation (~1K input tokens)
    "mock": 0.0,
}

# Hard cost gate per run
_MAX_COST_PER_RUN_USD = 0.50
_DRAFT_CHECKPOINT_ROOT = (Path(__file__).resolve().parent.parent / "checkpoints" / "draft").resolve()


class PipelineOrchestrator:
    """Unified pipeline execution engine.

    Parameters
    ----------
    draft_config : DraftConfig
        Image generation configuration.
    critic_config : CriticConfig
        L1-L5 scoring configuration.
    queen_config : QueenConfig
        Decision and budget configuration.
    enable_hitl : bool
        If True, pause at Queen decisions for human input.
    enable_archivist : bool
        If True, run Archivist after pipeline completes.
    """

    def __init__(
        self,
        draft_config: DraftConfig | None = None,
        critic_config: CriticConfig | None = None,
        queen_config: QueenConfig | None = None,
        enable_hitl: bool = False,
        enable_archivist: bool = True,
        enable_agent_critic: bool = False,
        enable_evidence_loop: bool = True,
        enable_fix_it_plan: bool = True,
        enable_llm_queen: bool = False,
        enable_prompt_enhancer: bool = False,
        enable_parallel_critic: bool = False,
    ) -> None:
        self.d_cfg = draft_config or DraftConfig(provider="nb2", n_candidates=4, seed_base=42)
        self.cr_cfg = critic_config or CriticConfig()
        self.q_cfg = queen_config or QueenConfig()
        self.enable_hitl = enable_hitl
        self.enable_archivist = enable_archivist
        self.enable_agent_critic = enable_agent_critic
        self.enable_evidence_loop = enable_evidence_loop
        self.enable_fix_it_plan = enable_fix_it_plan
        self.enable_llm_queen = enable_llm_queen
        self.enable_prompt_enhancer = enable_prompt_enhancer
        self.enable_parallel_critic = enable_parallel_critic

        # Lazy import to avoid circular dependency
        from app.prototype.observability.langfuse_observer import LangfuseObserver
        self._langfuse = LangfuseObserver()

        # Layer 3: LLM Queen with trajectory RAG
        self._queen_llm = None
        if enable_llm_queen:
            try:
                from app.prototype.agents.queen_llm import QueenLLMAgent
                self._queen_llm = QueenLLMAgent(config=self.q_cfg)
                self._queen_llm.build_trajectory_index()
            except Exception as exc:
                logger.warning("LLM Queen init failed, using rules: %s", exc)
                self._queen_llm = None

        # Active runs (task_id -> RunState) for HITL
        self._runs: dict[str, RunState] = {}

    def get_run_state(self, task_id: str) -> RunState | None:
        """Get the RunState for an active run."""
        return self._runs.get(task_id)

    # ------------------------------------------------------------------
    # Public API: synchronous mode
    # ------------------------------------------------------------------

    def run_sync(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Execute pipeline synchronously, consuming all events.

        Returns the final PipelineOutput.
        """
        self._langfuse.start_trace(
            task_id=pipeline_input.task_id,
            subject=pipeline_input.subject,
            tradition=pipeline_input.cultural_tradition,
            provider=self.d_cfg.provider,
        )
        output: PipelineOutput | None = None
        for event in self.run_stream(pipeline_input):
            self._langfuse.on_event(event)
            if event.event_type == EventType.PIPELINE_COMPLETED:
                output = self._output_from_payload(event.payload)
            elif event.event_type == EventType.PIPELINE_FAILED:
                output = self._output_from_payload(event.payload)

        self._langfuse.flush()

        if output is None:
            return PipelineOutput(
                task_id=pipeline_input.task_id,
                success=False,
                error="No completion event received",
            )
        return output

    # ------------------------------------------------------------------
    # Public API: streaming mode
    # ------------------------------------------------------------------

    def run_stream(self, pipeline_input: PipelineInput) -> Iterator[PipelineEvent]:
        """Execute pipeline as an event stream (generator).

        Yields PipelineEvent objects for each stage transition.
        Supports ``resume_from`` to skip stages before the resume point,
        loading their outputs from checkpoints.
        """
        t0 = time.monotonic()
        task_id = pipeline_input.task_id
        stages: list[StageResult] = []
        run_state = RunState(task_id=task_id, status=RunStatus.RUNNING)
        self._runs[task_id] = run_state

        # Track per-round data for Archivist
        critique_dicts: list[dict] = []
        queen_dicts: list[dict] = []
        images_generated = 0
        total_cost = 0.0
        cost_per_image = _COST_PER_IMAGE.get(self.d_cfg.provider, 0.0)
        provider_used = self.d_cfg.provider

        # Resume support
        resume_from = pipeline_input.resume_from
        _STAGE_ORDER = ["scout", "draft", "critic", "queen"]

        try:
            # Validate resume checkpoints exist
            if resume_from and resume_from in _STAGE_ORDER:
                resume_idx = _STAGE_ORDER.index(resume_from)
                for prior_stage in _STAGE_ORDER[:resume_idx]:
                    ckpt = load_pipeline_stage(task_id, prior_stage)
                    if ckpt is None:
                        raise RuntimeError(
                            f"Cannot resume from '{resume_from}': "
                            f"checkpoint for '{prior_stage}' not found"
                        )

            # Layer 2: Trajectory recorder
            trajectory_recorder = TrajectoryRecorder()
            evidence_pack = None  # Layer 1a: will be set after Scout

            # ==== SCOUT ====
            if resume_from and resume_from in _STAGE_ORDER and _STAGE_ORDER.index(resume_from) > 0:
                # Skip scout — load from checkpoint
                evidence_dict = load_pipeline_stage(task_id, "scout") or {}
                scout_svc = get_scout_service()  # needed for supplementary evidence loop
                # Reconstruct evidence_pack from checkpoint (E-2 fix)
                if "evidence_pack" in evidence_dict:
                    try:
                        from app.prototype.tools.evidence_pack import EvidencePack
                        evidence_pack = EvidencePack.from_dict(evidence_dict["evidence_pack"])
                    except Exception as exc:
                        logger.warning(
                            "Failed to reconstruct EvidencePack from checkpoint for %s: %s",
                            task_id, exc,
                        )
                stages.append(StageResult(stage="scout", status="skipped"))
            else:
                yield self._event(EventType.STAGE_STARTED, "scout", 0, t0)
                run_state.current_stage = "scout"

                st = time.monotonic()
                scout_svc = get_scout_service()
                evidence = scout_svc.gather_evidence(
                    subject=pipeline_input.subject,
                    cultural_tradition=pipeline_input.cultural_tradition,
                )
                evidence_dict = evidence.to_dict()
                evidence_dict["evidence_coverage"] = scout_svc.compute_evidence_coverage(evidence)

                # Layer 1a: Build structured EvidencePack
                evidence_pack = scout_svc.build_evidence_pack(
                    subject=pipeline_input.subject,
                    tradition=pipeline_input.cultural_tradition,
                    evidence=evidence,
                )
                evidence_dict["evidence_pack"] = evidence_pack.to_dict()

                scout_ms = int((time.monotonic() - st) * 1000)
                save_pipeline_stage(task_id, "scout", evidence_dict)

                stages.append(StageResult(
                    stage="scout", status="completed", latency_ms=scout_ms,
                    output_summary={
                        "sample_matches": len(evidence_dict.get("sample_matches", [])),
                        "terminology_hits": len(evidence_dict.get("terminology_hits", [])),
                        "taboo_violations": len(evidence_dict.get("taboo_violations", [])),
                        "evidence_pack_anchors": len(evidence_pack.anchors) if evidence_pack else 0,
                    },
                ))
                yield self._event(EventType.STAGE_COMPLETED, "scout", 0, t0, {
                    "latency_ms": scout_ms,
                    "evidence": evidence_dict,
                })

                # HITL: Scout — let human review/edit evidence before Draft
                if self.enable_hitl:
                    yield self._event(EventType.HUMAN_REQUIRED, "scout", 0, t0, {
                        "stage": "scout",
                        "evidence": evidence_dict,
                    })
                    human_action = run_state.wait_for_human(timeout=300)
                    if human_action is not None:
                        yield self._event(EventType.HUMAN_RECEIVED, "scout", 0, t0, {
                            "action": human_action.action,
                            "reason": human_action.reason,
                        })
                        # Merge human edits into evidence (via reason field as JSON or free text)
                        if human_action.reason:
                            evidence_dict["human_notes"] = human_action.reason

            # Layer 2: Start trajectory recording
            trajectory_recorder.start(
                subject=pipeline_input.subject,
                tradition=pipeline_input.cultural_tradition,
                evidence_pack_dict=evidence_pack.to_dict() if evidence_pack else None,
            )

            # ==== CULTURAL ROUTING ====
            router = CulturalPipelineRouter()
            route = router.route(pipeline_input.cultural_tradition)
            # Merge: keep caller's CriticConfig but override weights from router.
            # This ensures all caller fields (use_vlm, thresholds, etc.) are
            # preserved — no risk of silently losing fields added in the future.
            routed_critic_cfg = dataclasses.replace(
                self.cr_cfg, weights=route.critic_config.weights,
            )
            pipeline_variant = route.variant

            # ==== CRITIC → QUEEN LOOP ====
            plan_state = PlanState(task_id=task_id)
            queen = QueenAgent(config=self.q_cfg)
            final_decision = "stop"
            best_candidate_id: str | None = None
            draft_candidates: list[dict] = []
            round_num = 0
            prev_dimension_scores: dict[str, dict[str, tuple[float, str]]] = {}
            rerun_prompt_delta: str = ""  # FixItPlan prompt enhancement for next round

            # Track whether first-round skip is needed
            _skip_draft_first_round = (
                resume_from is not None
                and resume_from in _STAGE_ORDER
                and _STAGE_ORDER.index(resume_from) > _STAGE_ORDER.index("draft")
            )
            # R6-1: Skip Draft after successful rerun_local — the refined
            # image is already in draft_candidates, go straight to Critic.
            _skip_draft_after_refine = False

            while True:
                round_num += 1
                run_state.current_round = round_num

                # ==== DRAFT ====
                if _skip_draft_after_refine:
                    # R6-1: After successful rerun_local, the refined image
                    # is already in draft_candidates — skip Draft, go to Critic.
                    stages.append(StageResult(stage="draft", status="skipped_after_refine"))
                    _skip_draft_after_refine = False
                    rerun_prompt_delta = ""  # Clear stale delta (already applied in rerun_local)
                    # Record skipped draft in trajectory for completeness
                    if draft_candidates:
                        trajectory_recorder.record_draft(
                            DraftPlan(
                                prompt_trace=PromptTrace(
                                    raw_prompt=pipeline_input.subject,
                                    enhanced_prompt=draft_candidates[0].get("prompt", ""),
                                    prompt_hash="",
                                    model_ref=draft_candidates[0].get("model_ref", ""),
                                ),
                                provider=self.d_cfg.provider,
                                generation_params={"reused_from_rerun_local": True},
                                latency_ms=0,
                                n_candidates=len(draft_candidates),
                                success=True,
                            ),
                            round_num=round_num,
                        )
                elif _skip_draft_first_round and round_num == 1:
                    # Skip draft — load from checkpoint
                    draft_ckpt = load_pipeline_stage(task_id, "draft")
                    draft_candidates = draft_ckpt.get("candidates", []) if draft_ckpt else []
                    stages.append(StageResult(stage="draft", status="skipped"))
                    _skip_draft_first_round = False  # Only skip once
                    rerun_prompt_delta = ""  # Defensive: clear in case of future changes
                else:
                    yield self._event(EventType.STAGE_STARTED, "draft", round_num, t0)
                    run_state.current_stage = "draft"

                    current_seed = self.d_cfg.seed_base + (round_num - 1) * 100
                    round_cfg = DraftConfig(
                        provider=self.d_cfg.provider,
                        api_key=self.d_cfg.api_key,
                        n_candidates=self.d_cfg.n_candidates,
                        seed_base=current_seed,
                        steps=self.d_cfg.steps,
                        width=self.d_cfg.width,
                        height=self.d_cfg.height,
                        provider_model=self.d_cfg.provider_model,
                    )
                    draft_agent = DraftAgent(config=round_cfg)
                    # Apply FixItPlan prompt_delta from previous round's Critic
                    effective_subject = pipeline_input.subject
                    if rerun_prompt_delta:
                        effective_subject = f"{pipeline_input.subject}, {rerun_prompt_delta}"
                        rerun_prompt_delta = ""  # consumed

                    # Line D: LLM Prompt Enhancement (first round only)
                    prompt_enhanced = False
                    if self.enable_prompt_enhancer and round_num == 1:
                        pre_enhance = effective_subject
                        enhancer = PromptEnhancer(enabled=True)
                        effective_subject = enhancer.enhance(
                            subject=effective_subject,
                            cultural_tradition=pipeline_input.cultural_tradition,
                            evidence=evidence_dict,
                        )
                        # R8-4: Track whether enhancement actually changed the prompt
                        # so post-hoc analysis can detect silent failures.
                        prompt_enhanced = (effective_subject != pre_enhance)
                        if not prompt_enhanced:
                            logger.warning(
                                "PromptEnhancer returned original subject for %s "
                                "(API key missing or timeout)", task_id,
                            )
                    draft_input = DraftInput(
                        task_id=task_id,
                        subject=effective_subject,
                        cultural_tradition=pipeline_input.cultural_tradition,
                        evidence=evidence_dict,
                        config=round_cfg,
                    )

                    st = time.monotonic()
                    # Layer 1a: Pass EvidencePack to Draft for enriched prompts
                    draft_output = draft_agent.run(draft_input, evidence_pack=evidence_pack)
                    draft_candidates = [c.to_dict() for c in draft_output.candidates]
                    self._attach_candidate_image_urls(draft_candidates)
                    draft_ms = int((time.monotonic() - st) * 1000)
                    images_generated += len(draft_candidates)

                    # Cost check
                    cost_per_image = _COST_PER_IMAGE.get(self.d_cfg.provider, 0.0)
                    run_cost = images_generated * cost_per_image
                    if run_cost > _MAX_COST_PER_RUN_USD:
                        raise RuntimeError(
                            f"Cost gate exceeded: ${run_cost:.3f} > ${_MAX_COST_PER_RUN_USD}"
                        )

                    draft_ckpt_data: dict = {
                        "candidates": draft_candidates, "latency_ms": draft_ms,
                    }
                    if self.enable_prompt_enhancer and round_num == 1:
                        draft_ckpt_data["prompt_enhanced"] = prompt_enhanced
                    save_pipeline_stage(task_id, "draft", draft_ckpt_data)
                    stages.append(StageResult(
                        stage="draft", status="completed", latency_ms=draft_ms,
                        output_summary={
                            "n_candidates": len(draft_candidates),
                            "round": round_num,
                            "model_ref": draft_output.candidates[0].model_ref if draft_output.candidates else None,
                        },
                    ))
                    yield self._event(EventType.STAGE_COMPLETED, "draft", round_num, t0, {
                        "latency_ms": draft_ms,
                        "n_candidates": len(draft_candidates),
                        "candidates": draft_candidates,
                    })

                    # HITL: Draft — let human select/reject candidates
                    if self.enable_hitl:
                        yield self._event(EventType.HUMAN_REQUIRED, "draft", round_num, t0, {
                            "stage": "draft",
                            "candidates": draft_candidates,
                        })
                        human_action = run_state.wait_for_human(timeout=300)
                        if human_action is not None:
                            yield self._event(EventType.HUMAN_RECEIVED, "draft", round_num, t0, {
                                "action": human_action.action,
                                "candidate_id": human_action.candidate_id,
                                "reason": human_action.reason,
                            })
                            # Filter candidates if human selected specific ones
                            if human_action.candidate_id:
                                selected_ids = {cid.strip() for cid in human_action.candidate_id.split(",")}
                                draft_candidates = [
                                    c for c in draft_candidates
                                    if c.get("candidate_id") in selected_ids
                                ]

                    # Layer 2: Record draft in trajectory
                    if draft_output.candidates:
                        first_cand = draft_output.candidates[0]
                        trajectory_recorder.record_draft(
                            DraftPlan(
                                prompt_trace=PromptTrace(
                                    raw_prompt=pipeline_input.subject,
                                    enhanced_prompt=first_cand.prompt,
                                    prompt_hash="",
                                    model_ref=first_cand.model_ref,
                                ),
                                provider=self.d_cfg.provider,
                                generation_params={
                                    "seed": current_seed,
                                    "steps": self.d_cfg.steps,
                                    "width": self.d_cfg.width,
                                    "height": self.d_cfg.height,
                                },
                                latency_ms=draft_ms,
                                n_candidates=len(draft_candidates),
                                success=draft_output.success,
                            ),
                            round_num=round_num,
                        )

                # ==== CRITIC ====
                yield self._event(EventType.STAGE_STARTED, "critic", round_num, t0)
                run_state.current_stage = "critic"

                dyn_weights = None  # initialized before conditional assignment
                st = time.monotonic()
                if self.enable_agent_critic:
                    from app.prototype.agents.critic_llm import CriticLLM
                    critic = CriticLLM(config=routed_critic_cfg)
                    critique_input = CritiqueInput(
                        task_id=task_id,
                        subject=pipeline_input.subject,
                        cultural_tradition=pipeline_input.cultural_tradition,
                        evidence=evidence_dict,
                        candidates=draft_candidates,
                    )
                    critique_output = critic.run(critique_input)
                elif self.enable_parallel_critic:
                    # Parallel L1-L5 scoring via ThreadPoolExecutor
                    from app.prototype.agents.parallel_scorer import ParallelDimensionScorer
                    scorer = ParallelDimensionScorer(max_workers=5)
                    critique_output = build_critique_output(
                        task_id=task_id,
                        candidates=draft_candidates,
                        evidence=evidence_dict,
                        cultural_tradition=pipeline_input.cultural_tradition,
                        subject=pipeline_input.subject,
                        cfg=routed_critic_cfg,
                        score_fn=scorer.score_all_dimensions,
                        t0=st,
                    )
                    critic = None  # no CriticAgent instance in parallel path
                else:
                    critic = CriticAgent(config=routed_critic_cfg)
                    critique_input = CritiqueInput(
                        task_id=task_id,
                        subject=pipeline_input.subject,
                        cultural_tradition=pipeline_input.cultural_tradition,
                        evidence=evidence_dict,
                        candidates=draft_candidates,
                    )
                    critique_output = critic.run(critique_input)
                # R7-2: Replace (not extend) cross_layer_signals each round
                # to prevent stale signals from prior rounds distorting
                # dynamic weight modulation.
                if critic is not None and hasattr(critic, "cross_layer_signals") and critic.cross_layer_signals:
                    plan_state.cross_layer_signals = critic.cross_layer_signals[:]
                    critic.cross_layer_signals = []  # consumed
                else:
                    plan_state.cross_layer_signals = []
                hitl_constraints = self._apply_hitl_constraints(
                    critique_output=critique_output,
                    previous_dimension_scores=prev_dimension_scores,
                    plan_state=plan_state,
                    critic_config=routed_critic_cfg,
                )
                # Apply dynamic weight modulation (v2)
                if self.enable_agent_critic:
                    dyn_weights = compute_dynamic_weights(
                        base_weights=routed_critic_cfg.weights,
                        layer_states=plan_state.layer_states,
                        round_num=round_num,
                        cross_layer_signals=plan_state.cross_layer_signals,
                    )
                    # Recompute weighted_total with dynamic weights
                    for scored in critique_output.scored_candidates:
                        scored.weighted_total = sum(
                            dyn_weights.get(ds.dimension, 0.0) * ds.score
                            for ds in scored.dimension_scores
                        )
                    critique_output.scored_candidates.sort(
                        key=lambda c: c.weighted_total, reverse=True,
                    )
                    # Update best_candidate
                    critique_output.best_candidate_id = None
                    for scored in critique_output.scored_candidates:
                        if scored.gate_passed:
                            critique_output.best_candidate_id = scored.candidate_id
                            break

                critique_dict = critique_output.to_dict()
                if hitl_constraints:
                    critique_dict["hitl_constraints"] = hitl_constraints
                critic_ms = int((time.monotonic() - st) * 1000)
                prev_dimension_scores = self._snapshot_dimension_scores(critique_output)

                save_pipeline_stage(task_id, "critic", critique_dict)
                critique_dicts.append(critique_dict)

                stages.append(StageResult(
                    stage="critic", status="completed", latency_ms=critic_ms,
                    output_summary={
                        "best_candidate_id": critique_output.best_candidate_id,
                        "best_weighted_total": (
                            critique_output.scored_candidates[0].weighted_total
                            if critique_output.scored_candidates else 0.0
                        ),
                        "rerun_hint": critique_output.rerun_hint,
                        "hitl_constraints_applied": bool(hitl_constraints),
                    },
                ))
                # Build enhanced critic event payload (Phase 2)
                # Determine agent mode for frontend transparency
                agent_mode = "rule_only"
                if self.enable_agent_critic:
                    agent_mode = "agent_llm" if getattr(critic, "_has_any_api_key", lambda: False)() else "agent_fallback_rules"
                critic_event_payload = {
                    "latency_ms": critic_ms,
                    "critique": critique_dict,
                    "hitl_constraints": hitl_constraints,
                    "agent_mode": agent_mode,
                }
                # Add dynamic weights (always include for radar chart)
                dyn_weights_snapshot = dyn_weights if self.enable_agent_critic else None
                if dyn_weights_snapshot:
                    critic_event_payload["dynamic_weights"] = dyn_weights_snapshot
                elif hasattr(routed_critic_cfg, 'weights'):
                    critic_event_payload["dynamic_weights"] = routed_critic_cfg.weights
                # Add cross-layer signals
                if plan_state.cross_layer_signals:
                    critic_event_payload["cross_layer_signals"] = [
                        s.to_dict() if hasattr(s, 'to_dict') else s
                        for s in plan_state.cross_layer_signals
                    ]
                # Add FixItPlan if available
                if (self.enable_agent_critic
                        and hasattr(critic, "fix_it_plan") and critic.fix_it_plan):
                    critic_event_payload["fix_it_plan"] = critic.fix_it_plan.to_dict()
                # Add NeedMoreEvidence if available
                if (self.enable_agent_critic
                        and hasattr(critic, "need_more_evidence") and critic.need_more_evidence):
                    critic_event_payload["need_more_evidence"] = critic.need_more_evidence.to_dict()
                yield self._event(EventType.STAGE_COMPLETED, "critic", round_num, t0,
                                  critic_event_payload)

                # HITL: Critic — let human override scores or adjust dimensions
                if self.enable_hitl:
                    yield self._event(EventType.HUMAN_REQUIRED, "critic", round_num, t0, {
                        "stage": "critic",
                        "scored_candidates": [sc.to_dict() for sc in critique_output.scored_candidates],
                    })
                    human_action = run_state.wait_for_human(timeout=300)
                    if human_action is not None:
                        yield self._event(EventType.HUMAN_RECEIVED, "critic", round_num, t0, {
                            "action": human_action.action,
                            "locked_dimensions": human_action.locked_dimensions,
                            "reason": human_action.reason,
                        })
                        # Apply score overrides from human (locked dimensions preserve scores)
                        for dim in human_action.locked_dimensions:
                            if dim and dim not in plan_state.human_locked_dimensions:
                                plan_state.human_locked_dimensions.append(dim)

                # Layer 1c: Supplementary evidence retrieval if Critic detected gaps
                if (self.enable_agent_critic
                        and self.enable_evidence_loop
                        and hasattr(critic, "need_more_evidence")
                        and critic.need_more_evidence is not None
                        and critic.need_more_evidence.urgency in ("high", "medium")
                        and evidence_pack is not None
                        and round_num <= 2):  # max 2 supplementary rounds
                    try:
                        evidence_pack = scout_svc.gather_supplementary(
                            need=critic.need_more_evidence,
                            existing_pack=evidence_pack,
                        )
                        evidence_dict["evidence_pack"] = evidence_pack.to_dict()
                        evidence_dict["evidence_coverage"] = evidence_pack.coverage
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Supplementary retrieval failed: %s", exc)

                # Layer 2: Record critic findings in trajectory
                if critique_output.scored_candidates:
                    best_scored = critique_output.scored_candidates[0]
                    fix_plan_dict = None
                    need_evidence_dict = None
                    if self.enable_agent_critic and hasattr(critic, "fix_it_plan") and critic.fix_it_plan:
                        fix_plan_dict = critic.fix_it_plan.to_dict()
                    if self.enable_agent_critic and hasattr(critic, "need_more_evidence") and critic.need_more_evidence:
                        need_evidence_dict = critic.need_more_evidence.to_dict()
                    trajectory_recorder.record_critic(
                        CriticFindings(
                            layer_scores={
                                ds.dimension: ds.score
                                for ds in best_scored.dimension_scores
                            },
                            weighted_score=best_scored.weighted_total,
                            fix_it_plan_dict=fix_plan_dict,
                            need_more_evidence_dict=need_evidence_dict,
                        ),
                        round_num=round_num,
                    )

                # ==== QUEEN ====
                yield self._event(EventType.STAGE_STARTED, "queen", round_num, t0)
                run_state.current_stage = "queen"

                st = time.monotonic()
                # Layer 3: Use LLM Queen when enabled, fall back to rule-based
                if self._queen_llm is not None:
                    queen_output = self._queen_llm.decide(critique_dict, plan_state)
                else:
                    queen_output = queen.decide(critique_dict, plan_state)
                queen_ms = int((time.monotonic() - st) * 1000)

                save_pipeline_stage(task_id, "queen", queen_output.to_dict())
                queen_dicts.append(queen_output.to_dict())

                stages.append(StageResult(
                    stage="queen", status="completed", latency_ms=queen_ms,
                    output_summary={
                        "action": queen_output.decision.action,
                        "reason": queen_output.decision.reason,
                        "round": plan_state.current_round,
                    },
                ))

                # Emit decision (enhanced for Phase 2)
                decision_payload = {
                    "action": queen_output.decision.action,
                    "reason": queen_output.decision.reason,
                    "rerun_dimensions": queen_output.decision.rerun_dimensions,
                    "preserve_dimensions": getattr(queen_output.decision, "preserve_dimensions", []),
                    "round": round_num,
                    "latency_ms": queen_ms,
                    "budget_state": {
                        "rounds_used": round_num,
                        "max_rounds": self.q_cfg.max_rounds,
                        "total_cost_usd": round(images_generated * cost_per_image, 6),
                        "candidates_generated": images_generated,
                    },
                }
                yield self._event(EventType.DECISION_MADE, "queen", round_num, t0, decision_payload)

                # Layer 2: Record Queen decision in trajectory
                trajectory_recorder.record_decision(
                    DecisionLog(
                        action=queen_output.decision.action,
                        reason=queen_output.decision.reason,
                        round_num=round_num,
                        threshold=self.q_cfg.accept_threshold,
                    ),
                    round_num=round_num,
                )

                final_decision = queen_output.decision.action
                best_candidate_id = critique_output.best_candidate_id

                # Layer 1b: Upgrade rerun → rerun_local when FixItPlan recommends inpainting
                if (
                    final_decision == "rerun"
                    and self.enable_agent_critic
                    and self.enable_fix_it_plan
                    and hasattr(critic, "fix_it_plan")
                    and critic.fix_it_plan
                    and critic.fix_it_plan.overall_strategy == "targeted_inpaint"
                ):
                    final_decision = "rerun_local"

                # HITL: if enabled, pause for human decision
                if self.enable_hitl and final_decision in ("accept", "rerun", "rerun_local", "stop"):
                    yield self._event(EventType.HUMAN_REQUIRED, "queen", round_num, t0, {
                        "queen_decision": decision_payload,
                        "plan_state": plan_state.to_dict(),
                    })

                    human_action = run_state.wait_for_human(timeout=300)
                    if human_action is not None:
                        yield self._event(EventType.HUMAN_RECEIVED, "queen", round_num, t0, {
                            "action": human_action.action,
                            "locked_dimensions": human_action.locked_dimensions,
                            "rerun_dimensions": human_action.rerun_dimensions,
                            "candidate_id": human_action.candidate_id,
                            "reason": human_action.reason,
                        })

                        # Record in plan_state
                        for dim in human_action.locked_dimensions:
                            if dim and dim not in plan_state.human_locked_dimensions:
                                plan_state.human_locked_dimensions.append(dim)
                        plan_state.human_override_history.append({
                            "action": human_action.action,
                            "dimensions": human_action.locked_dimensions or human_action.rerun_dimensions,
                            "candidate_id": human_action.candidate_id,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "reason": human_action.reason,
                        })

                        # Apply human decision
                        final_decision = self._apply_human_action(
                            human_action, final_decision, plan_state
                        )
                        if human_action.action == "force_accept" and human_action.candidate_id:
                            current_ids = {c.get("candidate_id") for c in draft_candidates}
                            if human_action.candidate_id in current_ids:
                                best_candidate_id = human_action.candidate_id
                    else:
                        # Timeout — proceed with Queen's decision
                        pass

                if final_decision in ("accept", "stop"):
                    break

                # ==== RERUN_LOCAL: targeted inpainting ====
                # Cultural variant may prohibit local rerun (e.g. chinese_xieyi)
                if final_decision == "rerun_local" and not pipeline_variant.allow_local_rerun:
                    final_decision = "rerun"
                if final_decision == "rerun_local" and not best_candidate_id:
                    # Fallback: no best candidate for local rerun, use global rerun instead
                    final_decision = "rerun"
                if final_decision == "rerun_local" and best_candidate_id:
                    yield self._event(EventType.STAGE_STARTED, "draft_refine", round_num, t0)
                    run_state.current_stage = "draft_refine"

                    st = time.monotonic()
                    # Find the best candidate's image path
                    base_image_path = self._find_candidate_image(
                        draft_candidates, best_candidate_id,
                    )
                    refined = None
                    if base_image_path:
                        # Layer 1b: Use FixItPlan for targeted repair if available
                        critic_fix_plan = getattr(critic, "fix_it_plan", None) if (self.enable_agent_critic and self.enable_fix_it_plan) else None
                        if critic_fix_plan is not None:
                            # Use FixItPlan-guided rerun
                            draft_agent = DraftAgent(config=self.d_cfg)
                            inpaint_name = self._resolve_inpaint_provider_name(
                                queen_output.decision.rerun_dimensions,
                            )
                            # Use best candidate's prompt, not first candidate
                            best_prompt = next(
                                (c.get("prompt", "") for c in draft_candidates if c.get("candidate_id") == best_candidate_id),
                                draft_candidates[0].get("prompt", "") if draft_candidates else pipeline_input.subject,
                            )
                            refined = draft_agent.rerun_with_fix(
                                original_prompt=best_prompt,
                                fix_plan=critic_fix_plan,
                                evidence_pack=evidence_pack,
                                base_image_path=base_image_path,
                                inpaint_provider_name=inpaint_name,
                                preserve_layers=queen_output.decision.preserve_dimensions or None,
                            )
                        else:
                            # Legacy path: LocalRerunRequest
                            local_rerun = LocalRerunRequest(
                                base_candidate_id=best_candidate_id,
                                target_layers=queen_output.decision.rerun_dimensions,
                                preserve_layers=queen_output.decision.preserve_dimensions,
                                prompt_delta=(
                                    f"improve {', '.join(queen_output.decision.rerun_dimensions)}"
                                ),
                            )
                            plan_state.local_rerun_request = local_rerun

                            inpaint_name = self._resolve_inpaint_provider_name(
                                queen_output.decision.rerun_dimensions,
                            )
                            draft_agent = DraftAgent(config=self.d_cfg)
                            refined = draft_agent.refine_candidate(
                                local_rerun_request=local_rerun,
                                base_image_path=base_image_path,
                                inpaint_provider_name=inpaint_name,
                            )
                    refine_ok = refined is not None and refined.image_path
                    if refine_ok:
                        refined_dict = refined.to_dict()
                        self._attach_candidate_image_urls([refined_dict])
                        draft_candidates = [refined_dict]
                        best_candidate_id = refined_dict["candidate_id"]
                        images_generated += 1
                        # R7-1: Persist refined image to draft checkpoint so
                        # crash-resume picks up the refined (not original) candidates.
                        save_pipeline_stage(task_id, "draft", {
                            "candidates": draft_candidates,
                            "source": "rerun_local",
                            "round": round_num,
                        })

                    refine_ms = int((time.monotonic() - st) * 1000)
                    stages.append(StageResult(
                        stage="draft_refine",
                        status="completed" if refine_ok else "failed",
                        latency_ms=refine_ms,
                        output_summary={
                            "base_candidate_id": best_candidate_id,
                            "target_layers": queen_output.decision.rerun_dimensions,
                            "round": round_num,
                        },
                    ))
                    yield self._event(
                        EventType.STAGE_COMPLETED, "draft_refine", round_num, t0,
                        {"latency_ms": refine_ms, "candidates": draft_candidates},
                    )

                    if refine_ok:
                        # R6-1: Set flag so next iteration skips Draft and
                        # goes directly to Critic with the refined image.
                        # Note: rerun_prompt_delta is NOT set here — the skip_draft
                        # path clears it anyway, and the refined image already
                        # incorporates the fix.
                        _skip_draft_after_refine = True
                        continue
                    # Local refine failed (empty image) — fall through to global rerun
                    logger.warning(
                        "rerun_local failed for %s round %d, falling through to global rerun",
                        task_id, round_num,
                    )

                # Rerun global — extract FixItPlan prompt_delta for next round
                if (
                    self.enable_agent_critic
                    and self.enable_fix_it_plan
                    and hasattr(critic, "fix_it_plan")
                    and critic.fix_it_plan
                ):
                    rerun_prompt_delta = critic.fix_it_plan.to_prompt_delta()

            # ==== ARCHIVIST ====
            if self.enable_archivist:
                yield self._event(EventType.STAGE_STARTED, "archivist", round_num, t0)
                run_state.current_stage = "archivist"

                total_ms_so_far = int((time.monotonic() - t0) * 1000)
                pipeline_out_dict = {
                    "task_id": task_id,
                    "final_decision": final_decision,
                    "best_candidate_id": best_candidate_id,
                    "total_rounds": round_num,
                    "total_latency_ms": total_ms_so_far,
                    "success": True,
                }
                arch_input = ArchivistInput(
                    task_id=task_id,
                    subject=pipeline_input.subject,
                    cultural_tradition=pipeline_input.cultural_tradition,
                    pipeline_output_dict=pipeline_out_dict,
                    scout_evidence_dict=evidence_dict,
                    critique_dicts=critique_dicts,
                    queen_dicts=queen_dicts,
                    draft_config_dict=self.d_cfg.to_dict(),
                    critic_config_dict=routed_critic_cfg.to_dict(),
                    queen_config_dict=self.q_cfg.to_dict(),
                )
                archivist = ArchivistAgent()
                arch_out = archivist.run(arch_input)

                stages.append(StageResult(
                    stage="archivist",
                    status="completed" if arch_out.success else "failed",
                    output_summary={
                        "evidence_chain_path": arch_out.evidence_chain_path,
                        "critique_card_path": arch_out.critique_card_path,
                    },
                ))
                yield self._event(EventType.STAGE_COMPLETED, "archivist", round_num, t0, {
                    "success": arch_out.success,
                    "evidence_chain_path": arch_out.evidence_chain_path,
                    "error": arch_out.error,
                })

            # ==== PIPELINE COMPLETED ====
            total_ms = int((time.monotonic() - t0) * 1000)
            total_cost = images_generated * cost_per_image

            # Layer 2: Finalize trajectory
            best_score = 0.0
            if critique_dicts:
                last_critique = critique_dicts[-1]
                scored_list = last_critique.get("scored_candidates", [])
                if scored_list:
                    best_score = scored_list[0].get("weighted_total", 0.0)
            trajectory_recorder.finish(
                final_score=best_score,
                final_action=final_decision,
                total_latency_ms=total_ms,
                total_cost=total_cost,
            )

            output = PipelineOutput(
                task_id=task_id,
                stages=stages,
                final_decision=final_decision,
                best_candidate_id=best_candidate_id,
                total_latency_ms=total_ms,
                total_rounds=round_num,
                success=True,
            )
            save_pipeline_output(task_id, output.to_dict())
            update_runs_index(task_id, {
                "status": "completed",
                "final_decision": final_decision,
                "total_rounds": round_num,
                "total_cost_usd": round(total_cost, 6),
                "total_latency_ms": total_ms,
                "provider": provider_used,
                "images_generated": images_generated,
            })

            run_state.status = RunStatus.COMPLETED
            yield self._event(EventType.PIPELINE_COMPLETED, "", round_num, t0, {
                **output.to_dict(),
                "total_cost_usd": round(total_cost, 6),
                "images_generated": images_generated,
                "provider_used": provider_used,
                "cultural_route": route.to_dict(),
            })

        except Exception as exc:
            total_ms = int((time.monotonic() - t0) * 1000)
            output = PipelineOutput(
                task_id=task_id,
                stages=stages,
                total_latency_ms=total_ms,
                success=False,
                error=str(exc),
            )
            save_pipeline_output(task_id, output.to_dict())
            update_runs_index(task_id, {
                "status": "failed",
                "error": str(exc),
                "total_latency_ms": total_ms,
            })
            run_state.status = RunStatus.FAILED

            yield self._event(EventType.PIPELINE_FAILED, "", 0, t0, {
                **output.to_dict(),
            })

        finally:
            # Clean up run state after a delay (keep for API queries)
            pass

    # ------------------------------------------------------------------
    # Public API: HITL action submission
    # ------------------------------------------------------------------

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

        Returns True if the action was delivered.
        """
        run_state = self._runs.get(task_id)
        if run_state is None or run_state.status != RunStatus.WAITING_HUMAN:
            return False

        ha = HumanAction(
            action=action,
            locked_dimensions=locked_dimensions or [],
            rerun_dimensions=rerun_dimensions or [],
            candidate_id=candidate_id,
            reason=reason,
        )
        run_state.submit_human_action(ha)
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _event(
        event_type: EventType,
        stage: str,
        round_num: int,
        t0: float,
        payload: dict | None = None,
    ) -> PipelineEvent:
        return PipelineEvent(
            event_type=event_type,
            stage=stage,
            round_num=round_num,
            payload=payload or {},
            timestamp_ms=int((time.monotonic() - t0) * 1000),
        )

    @staticmethod
    def _output_from_payload(payload: dict) -> PipelineOutput:
        """Reconstruct PipelineOutput from event payload."""
        stages_raw = payload.get("stages", [])
        stages = []
        for s in stages_raw:
            if isinstance(s, dict):
                stages.append(StageResult(
                    stage=s.get("stage", ""),
                    status=s.get("status", ""),
                    latency_ms=s.get("latency_ms", 0),
                    output_summary=s.get("output_summary", {}),
                ))
            elif isinstance(s, StageResult):
                stages.append(s)

        return PipelineOutput(
            task_id=payload.get("task_id", ""),
            stages=stages,
            final_decision=payload.get("final_decision", ""),
            best_candidate_id=payload.get("best_candidate_id"),
            total_latency_ms=payload.get("total_latency_ms", 0),
            total_rounds=payload.get("total_rounds", 0),
            success=payload.get("success", False),
            error=payload.get("error"),
        )

    @staticmethod
    def _apply_human_action(
        human_action: HumanAction,
        queen_decision: str,
        plan_state: PlanState,
    ) -> str:
        """Map a human action to an effective pipeline decision."""
        action = human_action.action

        if action == "approve":
            return "accept"
        elif action == "reject":
            return "stop"
        elif action == "rerun":
            # Set pending_dimensions from human's selection
            if human_action.rerun_dimensions:
                plan_state.pending_dimensions = human_action.rerun_dimensions
            return "rerun"
        elif action == "lock_dimensions":
            # Lock dimensions but continue with Queen's decision
            return queen_decision
        elif action == "force_accept":
            # Only allow if no taboo violations (checked at API layer)
            return "accept"
        else:
            return queen_decision

    def _apply_hitl_constraints(
        self,
        critique_output: CritiqueOutput,
        previous_dimension_scores: dict[str, dict[str, tuple[float, str]]],
        plan_state: PlanState,
        critic_config: CriticConfig | None = None,
    ) -> dict:
        """Apply human lock/rerun constraints to current round Critic scores."""
        if not previous_dimension_scores:
            return {}
        if not plan_state.human_override_history:
            return {}

        locked_dimensions = {
            d for d in plan_state.human_locked_dimensions if d in DIMENSIONS
        }
        rerun_dimensions = {
            d for d in plan_state.pending_dimensions if d in DIMENSIONS
        }
        if not locked_dimensions and not rerun_dimensions:
            return {}

        if rerun_dimensions:
            preserved_dimensions = (set(DIMENSIONS) - rerun_dimensions) | locked_dimensions
        else:
            preserved_dimensions = set(locked_dimensions)

        if not preserved_dimensions:
            return {}

        applied_scores = 0
        candidates_touched = 0
        for scored in critique_output.scored_candidates:
            prev_scores = previous_dimension_scores.get(scored.candidate_id)
            if not prev_scores:
                continue

            touched = False
            for ds in scored.dimension_scores:
                if ds.dimension not in preserved_dimensions:
                    continue
                prev = prev_scores.get(ds.dimension)
                if prev is None:
                    continue
                prev_score, prev_rationale = prev
                ds.score = prev_score
                ds.rationale = f"{prev_rationale}; hitl_preserved"
                applied_scores += 1
                touched = True

            if touched:
                candidates_touched += 1
                cfg = critic_config or self.cr_cfg
                self._recompute_candidate_gate(scored, cfg)

        critique_output.scored_candidates.sort(
            key=lambda c: c.weighted_total,
            reverse=True,
        )
        cfg = critic_config or self.cr_cfg
        critique_output.scored_candidates = critique_output.scored_candidates[: cfg.top_k]

        critique_output.best_candidate_id = None
        for scored in critique_output.scored_candidates:
            if scored.gate_passed:
                critique_output.best_candidate_id = scored.candidate_id
                break

        low_dims: set[str] = set()
        for scored in critique_output.scored_candidates:
            for ds in scored.dimension_scores:
                if ds.score < 0.3:
                    low_dims.add(ds.dimension)
        critique_output.rerun_hint = sorted(low_dims)

        return {
            "locked_dimensions": sorted(locked_dimensions),
            "rerun_dimensions": sorted(rerun_dimensions),
            "preserved_dimensions": sorted(preserved_dimensions),
            "applied_scores": applied_scores,
            "candidates_touched": candidates_touched,
        }

    def _recompute_candidate_gate(self, scored: CandidateScore, critic_config: CriticConfig | None = None) -> None:
        """Recompute weighted_total + gate decision after HITL score overrides."""
        cfg = critic_config or self.cr_cfg
        weighted_total = sum(
            cfg.weights.get(ds.dimension, 0.0) * ds.score
            for ds in scored.dimension_scores
        )
        scored.weighted_total = weighted_total

        critical_reasons = [
            reason for reason in scored.rejected_reasons if reason.startswith("critical risk:")
        ]
        rejected = list(critical_reasons)

        if weighted_total < cfg.pass_threshold:
            rejected.append(
                f"weighted_total {weighted_total:.4f} < threshold {cfg.pass_threshold}"
            )

        for ds in scored.dimension_scores:
            if ds.score < cfg.min_dimension_score:
                rejected.append(
                    f"{ds.dimension} score {ds.score:.4f} < min {cfg.min_dimension_score}"
                )

        scored.rejected_reasons = rejected
        scored.gate_passed = len(rejected) == 0

    @staticmethod
    def _snapshot_dimension_scores(
        critique_output: CritiqueOutput,
    ) -> dict[str, dict[str, tuple[float, str]]]:
        """Capture candidate dimension scores for use in the next rerun round."""
        snapshot: dict[str, dict[str, tuple[float, str]]] = {}
        for scored in critique_output.scored_candidates:
            snapshot[scored.candidate_id] = {
                ds.dimension: (ds.score, ds.rationale)
                for ds in scored.dimension_scores
            }
        return snapshot

    def _resolve_inpaint_provider_name(self, rerun_dimensions: list[str] | None) -> str:
        """Resolve inpaint provider name from draft config + rerun context.

        M0: NB2 doesn't support targeted inpaint. Since Loop is ineffective
        (+0.002 ns, Ghost Loop 30/30), rerun uses full NB2 regeneration.
        """
        if self.d_cfg.provider == "nb2":
            return "nb2_regenerate"
        if self.d_cfg.provider == "diffusers":
            if self.d_cfg.controlnet_enabled and rerun_dimensions:
                from app.prototype.agents.controlnet_provider import get_controlnet_type_for_layer
                cn_type = get_controlnet_type_for_layer(rerun_dimensions[0])
                return f"controlnet_{cn_type}" if cn_type else "diffusers_inpaint"
            return "diffusers_inpaint"
        return "mock_inpaint"

    @staticmethod
    def _find_candidate_image(
        candidates: list[dict], candidate_id: str,
    ) -> str | None:
        """Find the image path for a candidate by ID."""
        for c in candidates:
            if c.get("candidate_id") == candidate_id:
                path = c.get("image_path", "")
                return path if path else None
        # No fallback — returning wrong candidate's image is worse than skipping
        logger.warning(
            "candidate_id %s not found in %d candidates",
            candidate_id, len(candidates),
        )
        return None

    @staticmethod
    def _attach_candidate_image_urls(candidates: list[dict]) -> None:
        """Attach frontend-consumable image URLs to candidate dicts."""
        for candidate in candidates:
            image_path = str(candidate.get("image_path", ""))
            image_url = PipelineOrchestrator._candidate_image_url(image_path)
            if image_url:
                candidate["image_url"] = image_url

    @staticmethod
    def _candidate_image_url(image_path: str) -> str | None:
        """Map local checkpoint path to a static URL served by FastAPI."""
        if not image_path:
            return None
        if image_path.startswith("data:") or image_path.startswith("http://") or image_path.startswith("https://"):
            return image_path
        if image_path.startswith("/static/") or image_path.startswith("static/"):
            return image_path if image_path.startswith("/") else f"/{image_path}"

        try:
            rel = Path(image_path).resolve().relative_to(_DRAFT_CHECKPOINT_ROOT)
        except Exception:  # noqa: BLE001
            return None
        return f"/static/prototype/draft/{rel.as_posix()}"
