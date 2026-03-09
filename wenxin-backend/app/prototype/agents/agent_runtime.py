"""Agent Runtime — unified ReAct execution loop for Critic Agents.

Implements the core Agent pattern:
    LLM → tool_calls → tool_results → LLM → ... → submit_evaluation

The runtime is model-agnostic (via LiteLLM) and supports:
- Per-layer system prompts
- Dynamic tool selection by the LLM
- Budget and step limits
- Fallback to rule-based scoring on failure
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.prototype.agents.layer_state import LayerState
from app.prototype.agents.model_router import ModelRouter, ModelSpec
from app.prototype.agents.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

__all__ = [
    "AgentContext",
    "AgentResult",
    "AgentRuntime",
]


# ---------------------------------------------------------------------------
# AgentContext — everything the runtime needs for one evaluation
# ---------------------------------------------------------------------------

@dataclass
class AgentContext:
    """Context passed to the Agent runtime for a single layer evaluation."""

    task_id: str
    layer_id: str                    # e.g. "cultural_context"
    layer_label: str                 # e.g. "L3"
    subject: str
    cultural_tradition: str
    candidate_summary: str           # text summary of the candidate being evaluated
    evidence_summary: str            # text summary of Scout evidence
    layer_state: LayerState
    image_url: str | None = None     # for VLM layers (L1/L2)
    locked_layers: list[str] | None = None  # layers confirmed by HITL, skip re-evaluation


# ---------------------------------------------------------------------------
# AgentResult
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    """Result of an Agent evaluation for one layer."""

    layer_id: str
    score: float | None = None  # None = not yet scored; valid scores are [0, 1]
    confidence: float = 0.0
    rationale: str = ""
    evidence_refs: list[dict] = field(default_factory=list)
    tool_calls_made: int = 0
    llm_calls_made: int = 0
    cost_usd: float = 0.0
    model_used: str = ""
    fallback_used: bool = False
    latency_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "score": round(self.score, 4) if self.score is not None else None,
            "confidence": round(self.confidence, 4),
            "rationale": self.rationale,
            "evidence_refs": self.evidence_refs,
            "tool_calls_made": self.tool_calls_made,
            "llm_calls_made": self.llm_calls_made,
            "cost_usd": round(self.cost_usd, 6),
            "model_used": self.model_used,
            "fallback_used": self.fallback_used,
            "latency_ms": self.latency_ms,
        }


# ---------------------------------------------------------------------------
# System prompts per layer
# ---------------------------------------------------------------------------

_BASE_SYSTEM_PROMPTS: dict[str, str] = {
    "visual_perception": (
        "You are an expert art critic evaluating L1 (Visual Perception). "
        "Analyze the composition, color, form, and spatial arrangement. "
        "Use available tools to gather evidence. When ready, call submit_evaluation."
    ),
    "technical_analysis": (
        "You are an expert art critic evaluating L2 (Technical Analysis). "
        "Analyze brushwork, medium, technique, and material quality. "
        "Use available tools to gather evidence. When ready, call submit_evaluation."
    ),
    "cultural_context": (
        "You are an expert art critic evaluating L3 (Cultural Context). "
        "Assess historical accuracy, cultural grounding, and tradition adherence. "
        "Use search_cultural_references and lookup_terminology to find evidence. "
        "Read prior layer analyses with read_layer_analysis. "
        "When ready, call submit_evaluation with score, rationale, and evidence_refs."
    ),
    "critical_interpretation": (
        "You are an expert art critic evaluating L4 (Critical Interpretation). "
        "Analyze deeper meaning, symbolism, and critical discourse. "
        "Read prior layer analyses for context. Use tools to verify claims. "
        "When ready, call submit_evaluation."
    ),
    "philosophical_aesthetic": (
        "You are an expert art critic evaluating L5 (Philosophical & Aesthetic). "
        "Assess worldview, aesthetic theory, and philosophical depth. "
        "This is the deepest evaluation layer — synthesize findings from L1-L4. "
        "Read prior layer analyses with read_layer_analysis. "
        "When ready, call submit_evaluation."
    ),
}


def _get_system_prompt(layer_id: str, tradition: str = "default") -> str:
    """Get system prompt with evolved context appended.

    When no evolved data is available (evolutions == 0), returns the base
    prompt unchanged (zero regression).
    """
    base = _BASE_SYSTEM_PROMPTS.get(layer_id, _BASE_SYSTEM_PROMPTS.get("cultural_context", ""))

    try:
        from app.prototype.cultural_pipelines.cultural_weights import get_evolved_prompt_context
        evolved = get_evolved_prompt_context(tradition)
    except Exception:
        evolved = ""

    return base + evolved if evolved else base


# ---------------------------------------------------------------------------
# AgentRuntime
# ---------------------------------------------------------------------------

class AgentRuntime:
    """Execute a single-layer evaluation using the ReAct pattern.

    The LLM autonomously decides:
    1. Which tools to call (not a fixed pipeline)
    2. How many times to call them (1-N rounds)
    3. When to stop and submit the final evaluation

    Parameters
    ----------
    tool_registry : ToolRegistry
        Available tools for this evaluation.
    model_router : ModelRouter
        Routes to the appropriate LLM.
    max_steps : int
        Maximum number of LLM round-trips before forcing fallback.
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        model_router: ModelRouter,
        max_steps: int = 5,
    ) -> None:
        self._tools = tool_registry
        self._router = model_router
        self._max_steps = max_steps

    async def evaluate(self, ctx: AgentContext) -> AgentResult:
        """Run the ReAct loop for a single layer evaluation.

        Returns AgentResult with score, confidence, rationale, and evidence.
        Falls back to rule-based scoring if LLM fails.
        """
        t0 = time.monotonic()
        result = AgentResult(layer_id=ctx.layer_id)

        # Select model
        requires_vlm = ctx.layer_id in ("visual_perception", "technical_analysis")
        model_spec = self._router.select_model(
            ctx.layer_id, requires_vlm=requires_vlm,
        )
        if model_spec is None:
            logger.warning("No affordable model for %s — fallback to rules", ctx.layer_id)
            result.fallback_used = True
            result.latency_ms = int((time.monotonic() - t0) * 1000)
            return result

        result.model_used = model_spec.litellm_id

        # Build initial messages
        system_prompt = _get_system_prompt(ctx.layer_id, ctx.cultural_tradition)
        user_content = self._build_user_message(ctx)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # Two-phase ReAct loop:
        # Phase 1: Exploration (steps 0..max_steps-2) — gather evidence
        # Phase 2: Submission — clean call with only submit_evaluation
        explore_steps = max(1, self._max_steps - 1)
        collected_evidence: list[str] = []

        try:
            # Phase 1: Exploration
            for step in range(explore_steps):
                tc_mode = "required" if step == 0 else "auto"
                response = await self._call_llm(
                    model_spec, messages,
                    tools=self._tools.all_schemas(),
                    tool_choice=tc_mode,
                )
                result.llm_calls_made += 1
                result.cost_usd += model_spec.cost_per_call_usd

                if response is None:
                    logger.warning("LLM returned None at step %d for %s", step, ctx.layer_id)
                    break

                message = response.get("message", {})
                tool_calls = message.get("tool_calls")
                logger.debug(
                    "Explore %d/%d for %s: tool_calls=%s, finish=%s",
                    step, explore_steps, ctx.layer_id,
                    bool(tool_calls), response.get("finish_reason"),
                )

                if not tool_calls:
                    content = message.get("content", "")
                    parsed = self._try_parse_final_answer(content)
                    if parsed:
                        result.score = parsed.get("score", 0.5)
                        result.confidence = parsed.get("confidence", 0.5)
                        result.rationale = parsed.get("rationale", content)
                        result.evidence_refs = parsed.get("evidence_refs", [])
                        break
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user",
                        "content": "Please call submit_evaluation with your score, confidence, rationale, and evidence_refs.",
                    })
                    continue

                messages.append(message)

                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name", "")
                    fn_args_str = tc.get("function", {}).get("arguments", "{}")
                    tc_id = tc.get("id", "")

                    try:
                        fn_args = json.loads(fn_args_str)
                    except json.JSONDecodeError:
                        fn_args = {}

                    tool_result = await self._tools.execute(fn_name, fn_args)
                    result.tool_calls_made += 1

                    # Check terminal submit_evaluation
                    if fn_name == "submit_evaluation" and isinstance(tool_result, dict):
                        if tool_result.get("status") == "submitted":
                            result.score = tool_result.get("score", 0.5)
                            result.confidence = tool_result.get("confidence", 0.5)
                            result.rationale = tool_result.get("rationale", "")
                            result.evidence_refs = tool_result.get("evidence_refs", [])
                            result.latency_ms = int((time.monotonic() - t0) * 1000)
                            ctx.layer_state.record_score(result.score)
                            ctx.layer_state.confidence = result.confidence
                            ctx.layer_state.escalated = True
                            ctx.layer_state.cost_spent_usd += result.cost_usd
                            self._router.record_cost(result.cost_usd)
                            return result

                    # Collect evidence for submission phase
                    tool_str = json.dumps(tool_result, ensure_ascii=False, default=str)
                    collected_evidence.append(f"{fn_name}: {tool_str[:200]}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": tool_str,
                    })

            # Phase 2: Force submission with clean context
            if result.score is None:
                submit_result = await self._force_submit(
                    model_spec, ctx, collected_evidence,
                )
                if submit_result:
                    result.score = submit_result.get("score", 0.5)
                    result.confidence = submit_result.get("confidence", 0.5)
                    result.rationale = submit_result.get("rationale", "")
                    result.evidence_refs = submit_result.get("evidence_refs", [])
                    result.llm_calls_made += 1
                    result.cost_usd += model_spec.cost_per_call_usd
                    result.tool_calls_made += 1
                    result.latency_ms = int((time.monotonic() - t0) * 1000)
                    ctx.layer_state.record_score(result.score)
                    ctx.layer_state.confidence = result.confidence
                    ctx.layer_state.escalated = True
                    ctx.layer_state.cost_spent_usd += result.cost_usd
                    self._router.record_cost(result.cost_usd)
                    return result

            # Max steps reached without submit_evaluation
            if result.score is None:
                logger.warning(
                    "Max steps (%d) reached for %s without evaluation — fallback",
                    self._max_steps, ctx.layer_id,
                )
                result.fallback_used = True
            # Write back whatever result we have to LayerState
            if result.score is not None:
                ctx.layer_state.record_score(result.score)
                ctx.layer_state.confidence = result.confidence
                ctx.layer_state.escalated = not result.fallback_used
                ctx.layer_state.cost_spent_usd += result.cost_usd

        except Exception as exc:  # noqa: BLE001
            logger.error("Agent runtime error for %s: %s", ctx.layer_id, exc, exc_info=True)
            result.fallback_used = True

        result.latency_ms = int((time.monotonic() - t0) * 1000)
        self._router.record_cost(result.cost_usd)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _force_submit(
        self,
        model_spec: ModelSpec,
        ctx: AgentContext,
        collected_evidence: list[str],
    ) -> dict | None:
        """Make a clean LLM call with only submit_evaluation tool.

        Uses a fresh message context (no prior tool_call history)
        to avoid conversation momentum from exploration phase.
        """
        evidence_text = "\n".join(collected_evidence[-5:]) if collected_evidence else "(none)"
        submit_schema = [
            t for t in self._tools.all_schemas()
            if t.get("function", {}).get("name") == "submit_evaluation"
        ]

        fresh_messages = [
            {
                "role": "system",
                "content": (
                    "You are an art evaluation expert. Based on the evidence below, "
                    "you MUST call submit_evaluation with your score, confidence, "
                    "rationale, and evidence_refs. Do NOT call any other tool."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Layer: {ctx.layer_label} ({ctx.layer_id})\n"
                    f"Subject: {ctx.subject}\n"
                    f"Tradition: {ctx.cultural_tradition}\n\n"
                    f"Evidence gathered:\n{evidence_text}\n\n"
                    "Call submit_evaluation NOW with your assessment."
                ),
            },
        ]

        response = await self._call_llm(
            model_spec, fresh_messages,
            tools=submit_schema,
            tool_choice="required",
        )
        if response is None:
            return None

        message = response.get("message", {})
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return None

        for tc in tool_calls:
            fn_name = tc.get("function", {}).get("name", "")
            if fn_name == "submit_evaluation":
                fn_args_str = tc.get("function", {}).get("arguments", "{}")
                try:
                    fn_args = json.loads(fn_args_str)
                except json.JSONDecodeError:
                    fn_args = {}
                tool_result = await self._tools.execute("submit_evaluation", fn_args)
                if isinstance(tool_result, dict) and tool_result.get("status") == "submitted":
                    logger.debug("Force submit succeeded for %s", ctx.layer_id)
                    return tool_result

        return None

    @staticmethod
    def _build_user_message(ctx: AgentContext) -> str | list[dict]:
        """Compose the initial user message from context.

        For VLM layers (L1/L2) with an image_url, returns a multimodal
        content list (text + image). Otherwise returns a plain string.
        """
        parts = [
            f"## Task: {ctx.task_id}",
            f"**Subject**: {ctx.subject}",
            f"**Cultural Tradition**: {ctx.cultural_tradition}",
            f"**Layer**: {ctx.layer_label} ({ctx.layer_id})",
            "",
            "### Candidate Summary",
            ctx.candidate_summary or "(no summary available)",
            "",
            "### Scout Evidence",
            ctx.evidence_summary or "(no evidence gathered yet)",
        ]
        if ctx.layer_state.score > 0:
            parts.extend([
                "",
                "### Previous Score for this Layer",
                f"Score: {ctx.layer_state.score:.4f}, "
                f"Confidence: {ctx.layer_state.confidence:.4f}, "
                f"Evidence Coverage: {ctx.layer_state.evidence_coverage:.4f}",
            ])
        if ctx.locked_layers:
            parts.extend([
                "",
                "### Locked Layers (do NOT re-evaluate)",
                ", ".join(ctx.locked_layers),
            ])
        parts.extend([
            "",
            "### Instructions",
            "Use available tools to gather evidence. "
            "When you have enough evidence, call submit_evaluation with:",
            "- score: [0, 1]",
            "- confidence: [0, 1]",
            "- rationale: your reasoning",
            "- evidence_refs: [{source_id, contribution}, ...]",
        ])

        text = "\n".join(parts)

        # VLM layers: attach image as multimodal content
        is_vlm_layer = ctx.layer_id in ("visual_perception", "technical_analysis")
        if is_vlm_layer and ctx.image_url:
            image_content = AgentRuntime._encode_image_content(ctx.image_url)
            if image_content:
                return [
                    {"type": "text", "text": text},
                    image_content,
                ]

        return text

    @staticmethod
    def _encode_image_content(image_url: str) -> dict | None:
        """Encode an image path/URL into a multimodal content block.

        Supports:
        - data: URIs (pass through)
        - http/https URLs (pass through)
        - Local file paths (encode as base64 data URI)
        """
        if not image_url:
            return None

        # Already a data URI or remote URL — pass through
        if image_url.startswith("data:") or image_url.startswith("http"):
            return {
                "type": "image_url",
                "image_url": {"url": image_url},
            }

        # Local file path — encode as base64
        path = Path(image_url)
        if not path.is_file():
            # Try resolving relative to checkpoints
            ckpt_root = Path(__file__).resolve().parent.parent / "checkpoints" / "draft"
            alt = ckpt_root / image_url.lstrip("/")
            if alt.is_file():
                path = alt
            else:
                logger.warning("Image file not found: %s", image_url)
                return None

        try:
            raw = path.read_bytes()
            # Detect MIME type from header bytes
            if raw[:8].startswith(b"\x89PNG"):
                mime = "image/png"
            elif raw[:3] == b"\xff\xd8\xff":
                mime = "image/jpeg"
            elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
                mime = "image/webp"
            else:
                mime = "image/png"  # fallback
            b64 = base64.b64encode(raw).decode("ascii")
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to encode image %s: %s", image_url, exc)
            return None

    @staticmethod
    async def _call_llm(
        model_spec: ModelSpec,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str | dict = "auto",
    ) -> dict | None:
        """Call LLM via LiteLLM. Returns the response choice dict or None."""
        try:
            import litellm
            logger.debug(
                "LLM call: model=%s, tool_choice=%s, tools=%d, msgs=%d",
                model_spec.litellm_id, tool_choice,
                len(tools) if tools else 0, len(messages),
            )
            # Build optional kwargs for proxy routing
            extra_kwargs: dict = {}
            api_base = model_spec.get_api_base()
            api_key = model_spec.get_api_key()
            if api_base:
                extra_kwargs["api_base"] = api_base
            if api_key:
                extra_kwargs["api_key"] = api_key

            response = await litellm.acompletion(
                model=model_spec.litellm_id,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice if tools else None,
                max_tokens=model_spec.max_tokens,
                temperature=model_spec.temperature,
                **extra_kwargs,
            )
            if not (response and response.choices):
                logger.warning("LLM returned empty response for model=%s", model_spec.litellm_id)
                return None
            choice = response.choices[0]
            has_tc = bool(choice.message.tool_calls)
            logger.debug(
                "LLM response: finish=%s, has_tool_calls=%s, content_len=%d",
                choice.finish_reason, has_tc,
                len(choice.message.content or ""),
            )
            return {
                "message": {
                    "role": "assistant",
                    "content": getattr(choice.message, "content", None),
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in (choice.message.tool_calls or [])
                    ] if choice.message.tool_calls else None,
                },
                "finish_reason": choice.finish_reason,
            }
        except ImportError:
            logger.warning("litellm not installed — cannot call LLM")
            return None
        except Exception as exc:  # noqa: BLE001
            logger.error("LLM call failed: %s", exc, exc_info=True)
            return None

    @staticmethod
    def _try_parse_final_answer(content: str) -> dict | None:
        """Try to parse a JSON evaluation from free-form LLM output."""
        if not content:
            return None
        # Look for JSON block
        try:
            # Try direct parse
            data = json.loads(content)
            if "score" in data:
                return data
        except (json.JSONDecodeError, TypeError):
            pass

        # Try to find JSON in markdown code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                if "score" in data:
                    return data
            except (json.JSONDecodeError, TypeError):
                pass

        return None
