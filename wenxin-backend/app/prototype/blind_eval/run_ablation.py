#!/usr/bin/env python3
"""Ablation experiment runner — v1 (6 conditions) + v2 (3 conditions) + v3 (4 conditions) + v4 (3 conditions).

v1 Conditions (original, accept_threshold=0.80):
  A: SD1.5 + rule-only + single round + no routing   (baseline-weak)
  B: SD1.5 + rule+LLM  + multi-round + routing       (agent-weak)
  C: FLUX  + rule-only + single round + no routing    (baseline-strong)
  D: FLUX  + rule+LLM  + multi-round + routing       (agent-strong)
  E: FLUX  + rule-only + multi-round + routing        (loop-no-llm)
  F: FLUX  + rule+LLM  + single round + routing       (llm-no-loop)

v2 Conditions (tightened thresholds, accept_threshold=0.90):
  Cp: FLUX + rule-only + single round + routing       (routing-baseline)
  Dp: FLUX + rule+LLM  + multi-round + routing       (full-system-v2)
  Ep: FLUX + rule-only + multi-round + routing        (loop-only-v2)

v3 Conditions (VLM critic, accept_threshold=0.90):
  H: FLUX + VLM + rule-only + single round + routing  (vlm-single)
  I: FLUX + VLM + rule-only + multi-round + routing   (vlm-loop)
  J: FLUX + VLM + LLM + Enhancer + multi-round + routing (full-system-v3)
  K: FLUX + VLM + LLM + multi-round + routing         (vlm-llm)

v4 Conditions (NB2 generator, gemini-3.1-flash-image-preview):
  G:   NB2 + VLM + rule-only + single round + routing (nb2-single)
       — isolates: NB2 internal thinking loop vs FLUX (same compressed prompt as H)
  Gp:  NB2 + VLM + rule-only + single round + full EvidencePack 32K (nb2-fullctx)
       — isolates: full cultural context injection (32K vs FLUX T5 512 tokens)
  Gpp: NB2 + VLM + rule-only + multi-round + full EvidencePack 32K (nb2-fullctx-loop)
       — isolates: iterative NB2 generation with full context

Comparison chains:
  v1: A→B (SD1.5 agent), C→D (FLUX agent), C→E (loop), C→F→D (LLM)
  v3: C→H (VLM), H→I (loop), I→K (LLM), K→J (Enhancer)
  v4: H→G (generator swap), G→Gp (32K context), Gp→Gpp (iteration)

Usage:
  # Dry run with mock provider (free, fast)
  python3 -m app.prototype.blind_eval.run_ablation --mode mock

  # Real run with FLUX (needs TOGETHER_API_KEY + DEEPSEEK_API_KEY)
  python3 -m app.prototype.blind_eval.run_ablation --mode real

  # Run specific conditions only
  python3 -m app.prototype.blind_eval.run_ablation --mode mock --conditions A C D

  # Run v2 conditions only
  python3 -m app.prototype.blind_eval.run_ablation --mode real --conditions Cp Dp Ep

  # Run v3 conditions only
  python3 -m app.prototype.blind_eval.run_ablation --mode real --conditions H I J K

  # Limit tasks for testing
  python3 -m app.prototype.blind_eval.run_ablation --mode mock --max-tasks 3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.blind_eval.experiment_config import BlindTask
from app.prototype.blind_eval.experiment_runner import (
    _deterministic_seed,
    _save_run_output,
)
from app.prototype.blind_eval.task_sampler import sample_tasks, get_category_counts
from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.pipeline.pipeline_types import PipelineInput, PipelineOutput

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_RESULTS_ROOT = Path(__file__).resolve().parent / "results" / "ablation"


# ── Ablation condition dataclass ──────────────────────────────────────

@dataclass
class AblationCondition:
    """One ablation condition with all pipeline parameters."""

    name: str
    label: str
    provider: str           # "mock" | "diffusers" | "together_flux"
    enable_agent_critic: bool
    max_rounds: int
    use_cultural_routing: bool  # If False, override tradition→"default"
    description: str = ""
    # v2 threshold overrides (None = use QueenConfig defaults)
    accept_threshold: float | None = None
    min_improvement: float | None = None
    early_stop_threshold: float | None = None
    # v3 enhancements (Line A-D upgrades)
    provider_model: str = ""            # Override model ID (e.g. "black-forest-labs/FLUX.1-dev")
    enable_prompt_enhancer: bool = False  # Line D: LLM prompt expansion
    use_vlm: bool = False               # Line A: VLM critic (True=VLM, False=CLIP)
    # NB2 conditions: full EvidencePack injection into 32K context window
    enable_full_evidence_injection: bool = False  # Gp/Gpp: full EvidencePack → NB2

    @property
    def short(self) -> str:
        return self.name


# ── 6 conditions ──────────────────────────────────────────────────────

def _make_conditions(mode: str) -> dict[str, AblationCondition]:
    """Create ablation conditions: 6 v1 + 3 v2.

    mode='mock' uses mock provider for all.
    mode='real' uses diffusers for SD1.5 and together_flux for FLUX.
    """
    sd_provider = "diffusers" if mode == "real" else "mock"
    flux_provider = "together_flux" if mode == "real" else "mock"
    nb2_provider = "nb2" if mode == "real" else "mock"

    # v2 thresholds — tightened to ensure multi-round actually triggers
    V2_ACCEPT = 0.90       # was 0.80 — too lenient, 0/180 reached Round 2
    V2_MIN_IMPROVE = 0.02  # was 0.05 — too aggressive early stop
    V2_EARLY_STOP = 0.95   # was 0.93

    return {
        # ── v1 conditions (original thresholds, preserved for comparison) ──
        "A": AblationCondition(
            name="A", label="baseline-weak",
            provider=sd_provider,
            enable_agent_critic=False,
            max_rounds=1,
            use_cultural_routing=False,
            description="SD1.5 + Rule-Only + Single Round + No Routing",
        ),
        "B": AblationCondition(
            name="B", label="agent-weak",
            provider=sd_provider,
            enable_agent_critic=True,
            max_rounds=3,
            use_cultural_routing=True,
            description="SD1.5 + Rule+LLM + Multi-Round + Cultural Routing",
        ),
        "C": AblationCondition(
            name="C", label="baseline-strong",
            provider=flux_provider,
            enable_agent_critic=False,
            max_rounds=1,
            use_cultural_routing=False,
            description="FLUX + Rule-Only + Single Round + No Routing",
        ),
        "D": AblationCondition(
            name="D", label="agent-strong",
            provider=flux_provider,
            enable_agent_critic=True,
            max_rounds=3,
            use_cultural_routing=True,
            description="FLUX + Rule+LLM + Multi-Round + Cultural Routing",
        ),
        "E": AblationCondition(
            name="E", label="loop-no-llm",
            provider=flux_provider,
            enable_agent_critic=False,
            max_rounds=3,
            use_cultural_routing=True,
            description="FLUX + Rule-Only + Multi-Round + Cultural Routing",
        ),
        "F": AblationCondition(
            name="F", label="llm-no-loop",
            provider=flux_provider,
            enable_agent_critic=True,
            max_rounds=1,
            use_cultural_routing=True,
            description="FLUX + Rule+LLM + Single Round + Cultural Routing",
        ),
        # ── v2 conditions (tightened thresholds, multi-round activates) ──
        "Cp": AblationCondition(
            name="Cp", label="routing-baseline",
            provider=flux_provider,
            enable_agent_critic=False,
            max_rounds=1,
            use_cultural_routing=True,
            accept_threshold=V2_ACCEPT,
            description="FLUX + Rule-Only + Single Round + Routing (v2 baseline)",
        ),
        "Dp": AblationCondition(
            name="Dp", label="full-system-v2",
            provider=flux_provider,
            enable_agent_critic=True,
            max_rounds=3,
            use_cultural_routing=True,
            accept_threshold=V2_ACCEPT,
            min_improvement=V2_MIN_IMPROVE,
            early_stop_threshold=V2_EARLY_STOP,
            description="FLUX + Rule+LLM + Multi-Round + Routing (v2 thresholds)",
        ),
        "Ep": AblationCondition(
            name="Ep", label="loop-only-v2",
            provider=flux_provider,
            enable_agent_critic=False,
            max_rounds=3,
            use_cultural_routing=True,
            accept_threshold=V2_ACCEPT,
            min_improvement=V2_MIN_IMPROVE,
            early_stop_threshold=V2_EARLY_STOP,
            description="FLUX + Rule-Only + Multi-Round + Routing (v2 thresholds)",
        ),
        # ── v3 conditions (VLM + Fill upgrades, isolate each factor) ──
        # R7-5: H/I have enable_agent_critic=False so rerun_local (FLUX Fill)
        # is unreachable — labels corrected to remove "Fill" claim.
        # Fill is only active in J/K (enable_agent_critic=True + FixItPlan).
        "H": AblationCondition(
            name="H", label="vlm-single",
            provider=flux_provider,
            enable_agent_critic=False,
            max_rounds=1,
            use_cultural_routing=True,
            use_vlm=True,
            # Single-round: queen decision doesn't affect output scores.
            # Use QueenConfig defaults (0.80/0.93) to match C condition.
            description="FLUX + VLM + Rule-Only + Single Round + Routing",
        ),
        "I": AblationCondition(
            name="I", label="vlm-loop",
            provider=flux_provider,
            enable_agent_critic=False,
            max_rounds=3,
            use_cultural_routing=True,
            use_vlm=True,
            accept_threshold=V2_ACCEPT,
            min_improvement=V2_MIN_IMPROVE,
            early_stop_threshold=V2_EARLY_STOP,
            description="FLUX + VLM + Rule-Only + Multi-Round + Routing",
        ),
        "J": AblationCondition(
            name="J", label="full-system-v3",
            provider=flux_provider,
            enable_agent_critic=True,
            max_rounds=3,
            use_cultural_routing=True,
            use_vlm=True,
            enable_prompt_enhancer=True,
            accept_threshold=V2_ACCEPT,
            min_improvement=V2_MIN_IMPROVE,
            early_stop_threshold=V2_EARLY_STOP,
            description="FLUX + VLM + Fill + LLM + Multi-Round + Enhancer + Routing (full v3)",
        ),
        "K": AblationCondition(
            name="K", label="vlm-fill-llm",
            provider=flux_provider,
            enable_agent_critic=True,
            max_rounds=3,
            use_cultural_routing=True,
            use_vlm=True,
            accept_threshold=V2_ACCEPT,
            min_improvement=V2_MIN_IMPROVE,
            early_stop_threshold=V2_EARLY_STOP,
            description="FLUX + VLM + Fill + LLM + Multi-Round + Routing (no Enhancer)",
        ),
        # ── v4 conditions: NB2 generator (gemini-3.1-flash-image-preview) ──
        # Ablation chain: H→G (generator swap), G→Gp (32K context), Gp→Gpp (loop)
        #
        # G:   NB2 + VLM + Rule-Only + Single Round + Routing (basic NB2, same prompt as H)
        #      Isolates: does NB2's internal thinking loop improve over FLUX with same prompt?
        # Gp:  NB2 + VLM + Rule-Only + Single Round + Routing + Full EvidencePack
        #      Isolates: does 32K context with full cultural knowledge improve over G?
        # Gpp: NB2 + VLM + Rule-Only + Multi-Round + Routing + Full EvidencePack
        #      Isolates: does iterative NB2 generation (new call per round) improve over Gp?
        "G": AblationCondition(
            name="G", label="nb2-single",
            provider=nb2_provider,
            enable_agent_critic=False,
            max_rounds=1,
            use_cultural_routing=True,
            use_vlm=True,
            description=(
                "NB2 + VLM + Rule-Only + Single Round + Routing "
                "(NB2 replaces FLUX, same compressed prompt as H)"
            ),
        ),
        "Gp": AblationCondition(
            name="Gp", label="nb2-fullctx",
            provider=nb2_provider,
            enable_agent_critic=False,
            max_rounds=1,
            use_cultural_routing=True,
            use_vlm=True,
            enable_full_evidence_injection=True,
            description=(
                "NB2 + VLM + Rule-Only + Single Round + Full EvidencePack (32K context) "
                "(tests if full cultural context in generation helps vs. G)"
            ),
        ),
        "Gpp": AblationCondition(
            name="Gpp", label="nb2-fullctx-loop",
            provider=nb2_provider,
            enable_agent_critic=False,
            max_rounds=3,
            use_cultural_routing=True,
            use_vlm=True,
            enable_full_evidence_injection=True,
            accept_threshold=V2_ACCEPT,
            min_improvement=V2_MIN_IMPROVE,
            early_stop_threshold=V2_EARLY_STOP,
            description=(
                "NB2 + VLM + Rule-Only + Multi-Round + Full EvidencePack "
                "(each round: new NB2 call with full EvidencePack, not chat refinement)"
            ),
        ),
    }


# ── Orchestrator builder ──────────────────────────────────────────────

def _build_ablation_orchestrator(
    cond: AblationCondition,
    seed: int,
    n_candidates: int = 4,
) -> PipelineOrchestrator:
    """Build an orchestrator for the given ablation condition."""
    draft_cfg = DraftConfig(
        provider=cond.provider,
        n_candidates=n_candidates,
        seed_base=seed,
        provider_model=cond.provider_model,
        enable_full_evidence_injection=cond.enable_full_evidence_injection,
    )
    critic_cfg = CriticConfig(use_vlm=cond.use_vlm)

    # Build QueenConfig with optional v2 threshold overrides
    queen_kwargs: dict = {"max_rounds": cond.max_rounds}
    if cond.accept_threshold is not None:
        queen_kwargs["accept_threshold"] = cond.accept_threshold
    if cond.min_improvement is not None:
        queen_kwargs["min_improvement"] = cond.min_improvement
    if cond.early_stop_threshold is not None:
        queen_kwargs["early_stop_threshold"] = cond.early_stop_threshold
    queen_cfg = QueenConfig(**queen_kwargs)

    return PipelineOrchestrator(
        draft_config=draft_cfg,
        critic_config=critic_cfg,
        queen_config=queen_cfg,
        enable_hitl=False,
        enable_archivist=False,
        enable_agent_critic=cond.enable_agent_critic,
        enable_evidence_loop=True,
        enable_fix_it_plan=True,
        enable_prompt_enhancer=cond.enable_prompt_enhancer,
    )


# ── Single run ────────────────────────────────────────────────────────

@dataclass
class RunResult:
    """Result of a single (condition, task) run."""

    condition: str
    task_id: str
    category: str
    tradition: str
    success: bool
    final_decision: str
    best_weighted_total: float
    total_rounds: int
    total_latency_ms: int
    seed: int
    error: str = ""
    dimension_scores: dict[str, float] = field(default_factory=dict)
    vlm_used: bool = False  # D2: track whether VLM was actually used (vs CLIP fallback)


def _run_single(
    cond: AblationCondition,
    task: BlindTask,
    results_dir: Path,
    seed_base: int = 42,
    n_candidates: int = 4,
) -> RunResult:
    """Run a single (condition, task) pair."""
    seed = _deterministic_seed(task.task_id, cond.name, seed_base)
    orch = _build_ablation_orchestrator(cond, seed, n_candidates)

    # Override tradition if cultural routing disabled
    tradition = task.tradition if cond.use_cultural_routing else "default"
    pipeline_task_id = f"abl-{cond.name}_{task.task_id}"

    pi = PipelineInput(
        task_id=pipeline_task_id,
        subject=task.subject,
        cultural_tradition=tradition,
    )

    t0 = time.monotonic()
    output = orch.run_sync(pi)
    latency_ms = int((time.monotonic() - t0) * 1000)

    # Save raw output
    _save_run_output(
        results_dir, f"condition_{cond.name}", task.task_id,
        pipeline_task_id, output, None, latency_ms, seed,
    )

    # Extract best score from output_summary or checkpoint
    best_score: float | None = None
    dim_scores: dict[str, float] = {}

    # Try output_summary first (has best_weighted_total).
    # R7-4 + R8-3: Use last critic stage's score (multi-round: last round wins).
    # Allow 0.0 through — only skip if key is truly absent (None).
    for stage in output.stages:
        if stage.stage == "critic" and stage.output_summary:
            v = stage.output_summary.get("best_weighted_total")
            if v is not None:
                best_score = v

    # Get dimension scores from checkpoint (most reliable source)
    ckpt_path = (
        Path(__file__).resolve().parent.parent
        / "checkpoints" / "pipeline" / pipeline_task_id / "stage_critic.json"
    )
    vlm_used = False
    if ckpt_path.exists():
        try:
            ckpt = json.loads(ckpt_path.read_text(encoding="utf-8"))
            scored = ckpt.get("scored_candidates", [])
            # Scan all candidates for VLM usage markers
            for sc in scored:
                for ds in sc.get("dimension_scores", []):
                    if not vlm_used and "VLM_L" in ds.get("rationale", ""):
                        vlm_used = True
            # Extract dim_scores from best candidate only
            if scored:
                best = scored[0]
                if best_score is None:
                    best_score = best.get("weighted_total", 0.0)
                for ds in best.get("dimension_scores", []):
                    dim_scores[ds["dimension"]] = ds["score"]
        except Exception:
            pass

    # D1-note: For multi-round conditions, stage_critic.json only stores the last
    # round. If R8-1 circuit breaker disables VLM mid-run, vlm_used may be False
    # even though earlier rounds used VLM. As a conservative fallback, trust the
    # condition config for VLM-configured conditions when checkpoint has no markers.
    if not vlm_used and cond.use_vlm:
        logger.warning(
            "VLM configured but not detected in checkpoint for %s/%s — "
            "circuit breaker may have fired; keeping vlm_used=False for accurate data",
            cond.name, task.task_id,
        )

    if best_score is None:
        best_score = 0.0

    return RunResult(
        condition=cond.name,
        task_id=task.task_id,
        category=task.category,
        tradition=tradition,
        success=output.success,
        final_decision=output.final_decision or "error",
        best_weighted_total=best_score,
        total_rounds=output.total_rounds or 1,
        total_latency_ms=latency_ms,
        seed=seed,
        error=output.error or "",
        dimension_scores=dim_scores,
        vlm_used=vlm_used,
    )


# ── Analysis ──────────────────────────────────────────────────────────

@dataclass
class ConditionSummary:
    """Aggregate statistics for one condition."""

    condition: str
    label: str
    n_tasks: int
    n_success: int
    avg_score: float
    avg_rounds: float
    avg_latency_ms: float
    p95_latency_ms: int
    accept_rate: float
    rerun_rate: float
    dimension_avgs: dict[str, float]
    total_cost_usd: float
    vlm_usage_rate: float = 0.0  # D2: fraction of tasks that actually used VLM


def _summarize_condition(
    cond: AblationCondition,
    results: list[RunResult],
    cost_per_image: float,
    n_candidates: int,
) -> ConditionSummary:
    """Compute aggregate stats for one condition."""
    successful = [r for r in results if r.success]
    n = len(successful)
    if n == 0:
        return ConditionSummary(
            condition=cond.name, label=cond.label,
            n_tasks=len(results), n_success=0,
            avg_score=0.0, avg_rounds=0.0, avg_latency_ms=0.0,
            p95_latency_ms=0, accept_rate=0.0, rerun_rate=0.0,
            dimension_avgs={}, total_cost_usd=0.0,
        )

    scores = [r.best_weighted_total for r in successful]
    rounds = [r.total_rounds for r in successful]
    latencies = sorted([r.total_latency_ms for r in successful])
    accepts = sum(1 for r in successful if r.final_decision == "accept")
    reruns = sum(1 for r in successful if r.total_rounds > 1)

    # Dimension averages
    dim_sums: dict[str, list[float]] = {}
    for r in successful:
        for dim, score in r.dimension_scores.items():
            dim_sums.setdefault(dim, []).append(score)
    dim_avgs = {d: sum(v) / len(v) for d, v in dim_sums.items()}

    # Cost: images per task = n_candidates × total_rounds
    total_images = sum(r.total_rounds * n_candidates for r in successful)
    # D2: VLM usage rate
    vlm_count = sum(1 for r in successful if r.vlm_used)

    return ConditionSummary(
        condition=cond.name,
        label=cond.label,
        n_tasks=len(results),
        n_success=n,
        avg_score=sum(scores) / n,
        avg_rounds=sum(rounds) / n,
        avg_latency_ms=sum(latencies) / n,
        p95_latency_ms=latencies[min(int((n - 1) * 0.95), n - 1)] if n > 1 else latencies[0],
        accept_rate=accepts / n,
        rerun_rate=reruns / n,
        dimension_avgs=dim_avgs,
        total_cost_usd=total_images * cost_per_image,
        vlm_usage_rate=vlm_count / n,
    )


def _generate_report(
    summaries: list[ConditionSummary],
    all_results: dict[str, list[RunResult]],
    mode: str,
    report_path: Path,
    condition_defs: dict[str, AblationCondition] | None = None,
) -> None:
    """Generate a markdown analysis report."""
    lines: list[str] = []
    lines.append("# VULCA Ablation Experiment Results\n")
    lines.append(f"**Mode**: {mode}")
    lines.append(f"**Date**: {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Conditions**: {len(summaries)}")
    total_tasks = sum(s.n_tasks for s in summaries)
    lines.append(f"**Total Runs**: {total_tasks}\n")

    # Summary table
    lines.append("## Condition Summary\n")
    lines.append("| Cond | Label | Tasks | Avg Score | Avg Rounds | Accept% | Rerun% | Avg Latency | Cost |")
    lines.append("|:----:|:------|:-----:|:---------:|:----------:|:-------:|:------:|:-----------:|:----:|")
    for s in summaries:
        lines.append(
            f"| {s.condition} | {s.label} | {s.n_success}/{s.n_tasks} | "
            f"{s.avg_score:.3f} | {s.avg_rounds:.1f} | "
            f"{s.accept_rate*100:.0f}% | {s.rerun_rate*100:.0f}% | "
            f"{s.avg_latency_ms:.0f}ms | ${s.total_cost_usd:.3f} |"
        )

    # Dimension breakdown
    lines.append("\n## L1-L5 Dimension Averages\n")
    dims = ["visual_perception", "technical_analysis", "cultural_context",
            "critical_interpretation", "philosophical_aesthetic"]
    dim_labels = ["L1 Visual", "L2 Technical", "L3 Cultural", "L4 Critical", "L5 Aesthetic"]
    header = "| Cond | " + " | ".join(dim_labels) + " |"
    sep = "|:----:|" + "|:------:" * 5 + "|"
    lines.append(header)
    lines.append(sep)
    for s in summaries:
        vals = [f"{s.dimension_avgs.get(d, 0):.3f}" for d in dims]
        lines.append(f"| {s.condition} | " + " | ".join(vals) + " |")

    # D2: Data Integrity — VLM usage rate check
    has_vlm_issue = False
    for s in summaries:
        cond_def = (condition_defs or {}).get(s.condition)
        if cond_def and cond_def.use_vlm and s.vlm_usage_rate < 0.8:
            has_vlm_issue = True
            break
    if has_vlm_issue:
        lines.append("\n## Data Integrity Warning\n")
        lines.append("| Cond | use_vlm | VLM Usage | Status |")
        lines.append("|:----:|:-------:|:---------:|:------:|")
        for s in summaries:
            cond_def = (condition_defs or {}).get(s.condition)
            if cond_def is None:
                continue
            expected = cond_def.use_vlm
            actual_pct = f"{s.vlm_usage_rate*100:.0f}%"
            if expected and s.vlm_usage_rate < 0.8:
                status = "CONTAMINATED"
            elif expected and s.vlm_usage_rate >= 0.8:
                status = "OK"
            else:
                status = "N/A (CLIP)"
            lines.append(f"| {s.condition} | {expected} | {actual_pct} | {status} |")
        lines.append("")

    # Key comparisons
    lines.append("\n## Key Comparisons\n")
    sm = {s.condition: s for s in summaries}

    comparisons = [
        # v1 comparisons
        ("A vs B", "SD1.5: Agent loop impact", "A", "B"),
        ("C vs D", "FLUX: Agent loop impact (v1)", "C", "D"),
        ("C vs E", "FLUX: Loop alone (no LLM, v1)", "C", "E"),
        ("C vs F", "FLUX: LLM alone (no loop)", "C", "F"),
        ("E vs D", "LLM incremental value in loop (v1)", "E", "D"),
        ("A vs C", "Model upgrade (SD1.5→FLUX)", "A", "C"),
        # v2 comparisons (tightened thresholds)
        ("C vs Cp", "Routing alone (v2)", "C", "Cp"),
        ("C vs Dp", "Full system (v2, CORE)", "C", "Dp"),
        ("C vs Ep", "Loop+Routing (no LLM, v2)", "C", "Ep"),
        ("Cp vs Ep", "Loop effect given routing (v2)", "Cp", "Ep"),
        ("Ep vs Dp", "LLM incremental in loop (v2)", "Ep", "Dp"),
        # v3 comparisons (VLM + Fill upgrades)
        ("C vs H", "VLM upgrade (single, no Fill)", "C", "H"),
        ("H vs I", "Loop effect with VLM", "H", "I"),
        ("I vs K", "LLM incremental with VLM", "I", "K"),
        ("K vs J", "Enhancer incremental (Line D)", "K", "J"),
        ("C vs J", "Full v3 system vs v1 baseline (CORE)", "C", "J"),
        ("D vs J", "v3 vs v1 full system", "D", "J"),
    ]
    for title, desc, c1, c2 in comparisons:
        if c1 in sm and c2 in sm:
            delta = sm[c2].avg_score - sm[c1].avg_score
            sign = "+" if delta >= 0 else ""
            lines.append(f"- **{title}** ({desc}): {sign}{delta:.3f} score delta")
            # Per-dimension deltas
            for d, dl in zip(dims, dim_labels):
                v1 = sm[c1].dimension_avgs.get(d, 0)
                v2 = sm[c2].dimension_avgs.get(d, 0)
                dd = v2 - v1
                if abs(dd) > 0.01:
                    sign_d = "+" if dd >= 0 else ""
                    lines.append(f"  - {dl}: {sign_d}{dd:.3f}")

    # Category breakdown
    lines.append("\n## Category Breakdown\n")
    for cat in ["poetic", "cultural", "taboo"]:
        lines.append(f"\n### {cat.title()}\n")
        lines.append("| Cond | Avg Score | Avg Rounds | Accept% |")
        lines.append("|:----:|:---------:|:----------:|:-------:|")
        for s in summaries:
            cat_results = [r for r in all_results.get(s.condition, []) if r.category == cat and r.success]
            if not cat_results:
                continue
            cat_score = sum(r.best_weighted_total for r in cat_results) / len(cat_results)
            cat_rounds = sum(r.total_rounds for r in cat_results) / len(cat_results)
            cat_accept = sum(1 for r in cat_results if r.final_decision == "accept") / len(cat_results)
            lines.append(f"| {s.condition} | {cat_score:.3f} | {cat_rounds:.1f} | {cat_accept*100:.0f}% |")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Report saved: %s", report_path)


# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="VULCA Ablation Experiment")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock",
                        help="mock=free instant, real=GPU+API")
    parser.add_argument("--conditions", nargs="*", default=None,
                        help="Run only these conditions (e.g. A C D)")
    parser.add_argument("--max-tasks", type=int, default=None,
                        help="Limit tasks per condition (for testing)")
    parser.add_argument("--skip-tasks", type=str, default="",
                        help="Skip first N tasks globally or per-condition (e.g. '5' or 'A:3,K:5')")
    parser.add_argument("--n-candidates", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=42)
    args = parser.parse_args()

    # Build conditions
    all_conditions = _make_conditions(args.mode)
    if args.conditions:
        conditions = {k: all_conditions[k] for k in args.conditions if k in all_conditions}
    else:
        conditions = all_conditions

    # Parse per-condition skip specs
    skip_per_condition: dict[str, int] = {}
    _global_skip = 0
    if args.skip_tasks:
        try:
            if ":" in args.skip_tasks:
                for spec in args.skip_tasks.split(","):
                    spec = spec.strip()
                    if not spec:
                        continue
                    cond_name, n = spec.split(":", 1)
                    skip_per_condition[cond_name.strip()] = int(n.strip())
            else:
                _global_skip = int(args.skip_tasks)
        except (ValueError, TypeError) as exc:
            logger.error("Invalid --skip-tasks format %r: %s (use '5' or 'A:3,K:5')", args.skip_tasks, exc)
            return

    # Sample tasks
    tasks = sample_tasks(n_per_category=10)
    if _global_skip:
        tasks = tasks[_global_skip:]
    if args.max_tasks:
        tasks = tasks[:args.max_tasks]

    cat_counts = get_category_counts(tasks)
    logger.info("Tasks: %d (%s)", len(tasks), cat_counts)
    logger.info("Conditions: %s", list(conditions.keys()))
    logger.info("Mode: %s", args.mode)

    # Cost estimate (accounting for per-condition skips)
    cost_per_image = {"mock": 0.0, "diffusers": 0.0, "together_flux": 0.003}
    est_images = sum(
        max(0, len(tasks) - skip_per_condition.get(ck, 0)) * args.n_candidates * c.max_rounds
        for ck, c in conditions.items()
    )
    est_flux = sum(
        max(0, len(tasks) - skip_per_condition.get(ck, 0)) * args.n_candidates * c.max_rounds
        for ck, c in conditions.items()
        if c.provider == "together_flux"
    )
    est_cost = est_flux * cost_per_image["together_flux"]
    logger.info("Estimated images: %d (FLUX: %d, est cost: $%.2f)", est_images, est_flux, est_cost)

    if args.mode == "real" and est_cost > 0:
        logger.info("Real mode — ensure TOGETHER_API_KEY and DEEPSEEK_API_KEY are set")
        if not os.environ.get("TOGETHER_API_KEY"):
            logger.error("TOGETHER_API_KEY not set!")
            sys.exit(1)

    # R6-4: Check FAL_KEY for conditions that need FluxFill (rerun_local).
    # FluxFill is only reachable when enable_agent_critic=True (triggers FixItPlan
    # → targeted_inpaint → rerun_local), AND provider is FLUX, AND multi-round.
    needs_fal = args.mode == "real" and any(
        c.enable_agent_critic and c.max_rounds > 1 and c.provider == "together_flux"
        for c in conditions.values()
    )
    if needs_fal and not os.environ.get("FAL_KEY"):
        logger.error(
            "FAL_KEY not set! Conditions %s use FluxFill for rerun_local inpainting. "
            "Without FAL_KEY, FluxFill silently falls back to MockInpaintProvider.",
            [c.name for c in conditions.values() if c.enable_agent_critic and c.max_rounds > 1],
        )
        sys.exit(1)

    # Create results dir
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_dir = _RESULTS_ROOT / f"run_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save config
    config_dict = {
        "mode": args.mode,
        "conditions": {k: asdict(v) for k, v in conditions.items()},
        "n_tasks": len(tasks),
        "n_candidates": args.n_candidates,
        "seed_base": args.seed_base,
        "tasks": [asdict(t) for t in tasks],
    }
    (results_dir / "experiment_config.json").write_text(
        json.dumps(config_dict, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Run experiments
    all_results: dict[str, list[RunResult]] = {}

    for cond_key, cond in conditions.items():
        # R7-6 + R8-2: Reset singletons between conditions to prevent
        # state leakage (e.g., VLMCritic._available or ImageScorer._available
        # cached from a previous condition).
        try:
            from app.prototype.agents.vlm_critic import VLMCritic
            VLMCritic._instance = None
        except ImportError:
            pass
        try:
            from app.prototype.agents.image_scorer import ImageScorer
            ImageScorer._instance = None
        except ImportError:
            pass

        logger.info("=" * 60)
        logger.info("Condition %s: %s", cond.name, cond.description)
        logger.info("=" * 60)

        cond_results: list[RunResult] = []
        cond_tasks = tasks[skip_per_condition.get(cond_key, 0):]
        for i, task in enumerate(cond_tasks):
            logger.info(
                "  [%s] %d/%d: %s (%s)",
                cond.name, i + 1, len(cond_tasks), task.task_id, task.category,
            )
            try:
                result = _run_single(
                    cond, task, results_dir,
                    seed_base=args.seed_base,
                    n_candidates=args.n_candidates,
                )
                cond_results.append(result)
                logger.info(
                    "    → %s | score=%.3f | rounds=%d | %dms",
                    result.final_decision, result.best_weighted_total,
                    result.total_rounds, result.total_latency_ms,
                )
            except Exception:
                logger.exception("    FAILED: %s", task.task_id)
                cond_results.append(RunResult(
                    condition=cond.name, task_id=task.task_id,
                    category=task.category, tradition=task.tradition,
                    success=False, final_decision="error",
                    best_weighted_total=0.0, total_rounds=0,
                    total_latency_ms=0, seed=0, error="exception",
                ))

        all_results[cond_key] = cond_results

    # Save raw results JSON
    results_json = {
        cond_key: [asdict(r) for r in results]
        for cond_key, results in all_results.items()
    }
    (results_dir / "all_results.json").write_text(
        json.dumps(results_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Generate summaries
    summaries: list[ConditionSummary] = []
    for cond_key, cond in conditions.items():
        cpi = cost_per_image.get(cond.provider, 0.0)
        s = _summarize_condition(cond, all_results[cond_key], cpi, args.n_candidates)
        summaries.append(s)

    # Print summary table
    print("\n" + "=" * 80)
    print("  ABLATION RESULTS")
    print("=" * 80)
    print(f"{'Cond':<6} {'Label':<18} {'Score':>7} {'Rounds':>7} {'Accept%':>8} {'Latency':>9} {'Cost':>8}")
    print("-" * 80)
    for s in summaries:
        print(
            f"{s.condition:<6} {s.label:<18} {s.avg_score:>7.3f} {s.avg_rounds:>7.1f} "
            f"{s.accept_rate*100:>7.0f}% {s.avg_latency_ms:>8.0f}ms ${s.total_cost_usd:>6.3f}"
        )
    print("=" * 80)

    # Generate report
    report_path = results_dir / "ablation_report.md"
    _generate_report(summaries, all_results, args.mode, report_path, conditions)

    # Also save to prototype reports
    proto_report = (
        Path(__file__).resolve().parent.parent
        / "reports" / f"ablation-{args.mode}-{timestamp}.md"
    )
    _generate_report(summaries, all_results, args.mode, proto_report, conditions)

    total = sum(s.n_tasks for s in summaries)
    success = sum(s.n_success for s in summaries)
    print(f"\nTotal: {success}/{total} successful runs")
    print(f"Results: {results_dir}")
    print(f"Report:  {report_path}")


if __name__ == "__main__":
    main()
