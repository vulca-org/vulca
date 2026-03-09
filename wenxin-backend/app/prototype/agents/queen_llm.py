"""Queen LLM Agent — LLM-enhanced decision layer with RAG from trajectory history.

Layer 3: Wraps the rule-based QueenAgent with optional LLM reasoning.
When enabled, retrieves similar past trajectories via FAISS, builds a
few-shot prompt, and asks an LLM to recommend accept/rerun/stop with
confidence scoring.

Falls back to rule-based QueenAgent if:
  - LLM call fails (network, timeout, parse error)
  - No trajectory data available
  - LLM confidence is too low (below min_confidence)
  - Cost/round limits would be violated (hard guardrails preserved)

Usage::

    queen = QueenLLMAgent(config=queen_config, llm_config=queen_llm_config)
    queen.build_trajectory_index()  # once at startup
    output = queen.decide(critique_dict, plan_state)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.prototype.agents.model_router import MODEL_DECISION
from app.prototype.agents.queen_agent import QueenAgent
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.agents.queen_types import (
    PlanState,
    QueenDecision,
    QueenOutput,
)
from app.prototype.agents.trajectory_rag import TrajectoryRAGService

logger = logging.getLogger(__name__)

__all__ = [
    "QueenLLMAgent",
    "QueenLLMConfig",
]


@dataclass
class QueenLLMConfig:
    """Configuration for the LLM-enhanced Queen."""

    model: str = MODEL_DECISION
    temperature: float = 0.3
    max_tokens: int = 512
    top_k_trajectories: int = 3
    min_confidence: float = 0.4  # below this → fall back to rule-based
    enable_rag: bool = True
    cost_per_call_usd: float = 0.002  # estimated LLM call cost

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_k_trajectories": self.top_k_trajectories,
            "min_confidence": self.min_confidence,
            "enable_rag": self.enable_rag,
            "cost_per_call_usd": self.cost_per_call_usd,
        }


def _try_llm_call(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str | None:
    """Attempt an LLM call via LiteLLM (Gemini direct). Returns response text or None."""
    api_key = (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or ""
    )
    if not api_key:
        logger.warning("No API key found (GOOGLE_API_KEY / GEMINI_API_KEY)")
        return None

    try:
        import litellm
        resp = litellm.completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30.0,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        logger.warning("LLM call failed (%s): %s", model, exc)

    return None


class QueenLLMAgent:
    """Queen Agent enhanced with LLM reasoning and trajectory RAG.

    Preserves all hard guardrails from QueenAgent (budget, rounds,
    early-stop) while adding learned decision-making for ambiguous
    cases.
    """

    def __init__(
        self,
        config: QueenConfig | None = None,
        llm_config: QueenLLMConfig | None = None,
    ) -> None:
        self._config = config or QueenConfig()
        self._llm_config = llm_config or QueenLLMConfig()
        self._rule_agent = QueenAgent(config=self._config)
        self._rag = TrajectoryRAGService()
        self._llm_decisions: int = 0
        self._rule_fallbacks: int = 0

    def build_trajectory_index(self) -> int:
        """Build the trajectory FAISS index. Call once at startup."""
        return self._rag.build_index()

    def decide(
        self,
        critique_output_dict: dict,
        plan_state: PlanState,
    ) -> QueenOutput:
        """Make a decision using LLM + RAG when beneficial, rule-based otherwise.

        Decision flow:
        1. Check hard guardrails (budget, rounds) — if triggered, use rule-based
        2. If score is clearly high (>= early_stop) or clearly low — use rule-based
        3. For ambiguous range: query LLM with RAG context
        4. Parse LLM response; if confidence < threshold → fallback to rules
        """
        t0 = time.monotonic()
        cfg = self._config

        # Extract current state
        scored = critique_output_dict.get("scored_candidates", [])
        best_id = critique_output_dict.get("best_candidate_id")
        best_score = 0.0
        best_gate = False
        for sc in scored:
            if sc.get("candidate_id") == best_id:
                best_score = sc.get("weighted_total", 0.0)
                best_gate = sc.get("gate_passed", False)
                break
        if not best_id and scored:
            best_score = scored[0].get("weighted_total", 0.0)
            best_gate = scored[0].get("gate_passed", False)

        # --- Hard guardrails: always rule-based ---
        # These are non-negotiable budget/round constraints
        budget = plan_state.budget
        next_round = budget.rounds_used + 1

        if next_round > cfg.max_rounds:
            return self._rule_decide(critique_output_dict, plan_state, t0, "max_rounds")

        if budget.total_cost_usd >= cfg.max_cost_usd:
            return self._rule_decide(critique_output_dict, plan_state, t0, "budget_exhausted")

        # Clear-cut cases: no need for LLM
        if best_gate and best_score >= cfg.early_stop_threshold:
            return self._rule_decide(critique_output_dict, plan_state, t0, "early_stop")

        # --- Ambiguous range: try LLM ---
        llm_decision = self._try_llm_decide(
            critique_output_dict, plan_state, best_score, best_gate
        )

        if llm_decision is not None:
            # Update budget state (same as rule-based)
            budget.rounds_used += 1
            budget.total_cost_usd += cfg.mock_cost_per_round + self._llm_config.cost_per_call_usd
            budget.critic_calls += 1
            budget.llm_calls += 1
            budget.candidates_generated += len(scored)
            plan_state.current_round = budget.rounds_used

            plan_state.history.append({
                "round": budget.rounds_used,
                "best_score": round(best_score, 4),
                "best_gate_passed": best_gate,
                "best_candidate_id": best_id,
                "rerun_hint": critique_output_dict.get("rerun_hint", []),
                "cost_usd": round(budget.total_cost_usd, 6),
                "queen_mode": "llm",
            })

            # Update confirmed/pending
            if llm_decision.action == "accept":
                plan_state.confirmed_dimensions = list(
                    set(plan_state.confirmed_dimensions) | set(plan_state.pending_dimensions)
                )
                plan_state.pending_dimensions = []
            elif llm_decision.action == "rerun":
                plan_state.pending_dimensions = llm_decision.rerun_dimensions

            elapsed_ms = int((time.monotonic() - t0) * 1000)
            self._llm_decisions += 1

            return QueenOutput(
                task_id=plan_state.task_id,
                decision=llm_decision,
                plan_state=plan_state,
                created_at=datetime.now(timezone.utc).isoformat(),
                latency_ms=elapsed_ms,
                success=True,
                error=None,
            )

        # --- Fallback to rule-based ---
        return self._rule_decide(critique_output_dict, plan_state, t0, "llm_fallback")

    def _rule_decide(
        self,
        critique_output_dict: dict,
        plan_state: PlanState,
        t0: float,
        reason_tag: str,
    ) -> QueenOutput:
        """Delegate to the rule-based QueenAgent."""
        self._rule_fallbacks += 1
        output = self._rule_agent.decide(critique_output_dict, plan_state)
        output.decision.reason = f"[rule:{reason_tag}] {output.decision.reason}"
        output.latency_ms = int((time.monotonic() - t0) * 1000)
        return output

    def _try_llm_decide(
        self,
        critique_output_dict: dict,
        plan_state: PlanState,
        best_score: float,
        best_gate: bool,
    ) -> QueenDecision | None:
        """Attempt LLM-based decision with RAG context.

        Returns QueenDecision if successful, None if should fall back.
        """
        lcfg = self._llm_config

        # Retrieve similar trajectories
        subject = ""
        tradition = ""
        if plan_state.intent_card:
            subject = getattr(plan_state.intent_card, "subject", "")
            tradition = getattr(plan_state.intent_card, "tradition", "")
        if not subject and plan_state.history:
            # Try to infer from task_id
            subject = plan_state.task_id

        examples_prompt = ""
        if lcfg.enable_rag and self._rag.available:
            similar, patterns = self._rag.retrieve(
                subject=subject,
                tradition=tradition,
                current_score=best_score,
                top_k=lcfg.top_k_trajectories,
            )
            examples_prompt = self._rag.build_examples_prompt(similar, patterns)

        # Build prompt
        prompt = self._build_prompt(
            critique_output_dict, plan_state, best_score, best_gate, examples_prompt
        )

        # Call LLM
        messages = [
            {"role": "system", "content": self._system_prompt(tradition=tradition)},
            {"role": "user", "content": prompt},
        ]

        response = _try_llm_call(
            model=lcfg.model,
            messages=messages,
            temperature=lcfg.temperature,
            max_tokens=lcfg.max_tokens,
        )

        if response is None:
            logger.info("LLM call failed, falling back to rules")
            return None

        # Parse response
        decision = self._parse_response(response, critique_output_dict)
        if decision is None:
            logger.warning("Failed to parse LLM response, falling back to rules")
            return None

        # Check confidence threshold
        if decision.expected_gain_per_cost < lcfg.min_confidence:
            logger.info(
                "LLM confidence %.2f < threshold %.2f, falling back to rules",
                decision.expected_gain_per_cost, lcfg.min_confidence,
            )
            return None

        return decision

    def _system_prompt(self, tradition: str = "default") -> str:
        base = (
            "You are the Queen decision agent in the VULCA art evaluation pipeline. "
            "Your job is to decide whether to ACCEPT the current best candidate or "
            "RERUN specific dimensions for improvement.\n\n"
            "Rules:\n"
            "- ACCEPT: The candidate quality is sufficient, or further rounds are unlikely to help\n"
            "- RERUN: Specific L1-L5 dimensions need improvement and another round would help\n\n"
            "Available dimensions: visual_perception, technical_analysis, cultural_context, "
            "critical_interpretation, philosophical_aesthetic\n\n"
        )

        # Inject evolved context before JSON format instructions
        evolved = ""
        try:
            from app.prototype.cultural_pipelines.cultural_weights import get_evolved_prompt_context
            evolved = get_evolved_prompt_context(tradition)
        except Exception:
            pass  # Zero regression — on any error, skip evolved context

        json_instruction = (
            "Respond with a JSON object:\n"
            '{"action": "accept|rerun", "rerun_dimensions": [...], '
            '"confidence": 0.0-1.0, "reason": "brief explanation"}'
        )

        return base + evolved + "\n" + json_instruction if evolved else base + json_instruction

    def _build_prompt(
        self,
        critique_output_dict: dict,
        plan_state: PlanState,
        best_score: float,
        best_gate: bool,
        examples_prompt: str,
    ) -> str:
        """Build the user prompt with current state and RAG context."""
        scored = critique_output_dict.get("scored_candidates", [])
        rerun_hint = critique_output_dict.get("rerun_hint", [])

        # Current state summary
        lines = [
            "## Current Evaluation State",
            f"- Round: {plan_state.budget.rounds_used + 1}/{self._config.max_rounds}",
            f"- Budget used: ${plan_state.budget.total_cost_usd:.4f} / ${self._config.max_cost_usd:.4f}",
            f"- Best score: {best_score:.3f} (gate: {'PASS' if best_gate else 'FAIL'})",
            f"- Accept threshold: {self._config.accept_threshold}",
        ]

        # Score history
        if plan_state.history:
            scores = [h.get("best_score", 0) for h in plan_state.history]
            lines.append(f"- Score history: {' → '.join(f'{s:.3f}' for s in scores)}")
            if len(scores) >= 2:
                delta = scores[-1] - scores[-2]
                lines.append(f"- Last improvement: {delta:+.3f}")

        # Dimension breakdown
        if scored:
            best = scored[0]
            for sc in scored:
                if sc.get("candidate_id") == critique_output_dict.get("best_candidate_id"):
                    best = sc
                    break
            dim_scores = best.get("dimension_scores", [])
            if dim_scores:
                lines.append("\n## Dimension Scores (best candidate)")
                for ds in dim_scores:
                    dim = ds.get("dimension", "?")
                    score = ds.get("score", 0)
                    flag = " ⚠" if score < 0.5 else ""
                    lines.append(f"  - {dim}: {score:.3f}{flag}")

        # Rerun hints from Critic
        if rerun_hint:
            lines.append(f"\n## Critic Recommendation: rerun {rerun_hint}")

        # Cross-layer signals
        if plan_state.cross_layer_signals:
            lines.append("\n## Cross-Layer Signals")
            for sig in plan_state.cross_layer_signals:
                lines.append(
                    f"  - {sig.source_layer}→{sig.target_layer}: "
                    f"{sig.signal_type.value} (strength={sig.strength:.2f}) — {sig.message[:60]}"
                )

        # RAG examples
        if examples_prompt:
            lines.append(f"\n{examples_prompt}")

        lines.append("\nBased on the above, what is your decision? Respond with JSON only.")

        return "\n".join(lines)

    def _parse_response(self, response: str, critique_output_dict: dict) -> QueenDecision | None:
        """Parse the LLM response into a QueenDecision."""
        try:
            # Handle markdown code blocks
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[-1]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            data = json.loads(text)
            action = data.get("action", "accept")
            if action not in ("accept", "rerun"):
                # LLM "stop"/"downgrade" are not allowed — fall back to accept
                # to avoid premature pipeline termination bypassing threshold logic
                action = "accept"

            rerun_dims = data.get("rerun_dimensions", [])
            valid_dims = {
                "visual_perception", "technical_analysis", "cultural_context",
                "critical_interpretation", "philosophical_aesthetic",
            }
            rerun_dims = [d for d in rerun_dims if d in valid_dims]

            # If action is rerun but no dims specified, use critic hints
            if action == "rerun" and not rerun_dims:
                rerun_dims = critique_output_dict.get("rerun_hint", [])

            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))

            reason = data.get("reason", "LLM decision")

            all_dims = sorted(valid_dims)
            preserve = [d for d in all_dims if d not in rerun_dims]

            return QueenDecision(
                action=action,
                rerun_dimensions=rerun_dims,
                preserve_dimensions=preserve if action == "rerun" else [],
                reason=f"[llm] {reason}",
                expected_gain_per_cost=confidence,  # reuse field for confidence
            )

        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.warning("Failed to parse LLM response: %s — %s", exc, response[:200])
            return None

    def get_metrics(self) -> dict:
        """Return LLM queen usage metrics."""
        total = self._llm_decisions + self._rule_fallbacks
        return {
            "total_decisions": total,
            "llm_decisions": self._llm_decisions,
            "rule_fallbacks": self._rule_fallbacks,
            "llm_rate": round(self._llm_decisions / total, 3) if total > 0 else 0.0,
            "rag_available": self._rag.available,
        }
