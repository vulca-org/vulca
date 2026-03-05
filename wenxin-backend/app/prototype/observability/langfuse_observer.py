"""Langfuse observer for VULCA pipeline tracing.

Hooks into the PipelineOrchestrator event stream to create
Langfuse traces, spans, and generations. Gracefully degrades
when Langfuse is unavailable (no API key or import failure).

NOTE: This module avoids importing from app.prototype.orchestrator
at module level to prevent circular imports. It uses duck-typed
event objects (any object with event_type, stage, round_num, payload).

Langfuse SDK v3 API pattern:
  - Root span: span = client.start_span(name=...)
  - Child span: child = root_span.start_span(name=...)
  - Generation: gen = parent_span.start_generation(name=..., model=...)
  - Event: parent_span.create_event(name=..., metadata=...)
  - No trace_id parameter — use parent-child nesting instead.

Usage:
    from app.prototype.observability.langfuse_observer import LangfuseObserver

    observer = LangfuseObserver()  # auto-detects availability
    observer.on_event(event)       # call for each PipelineEvent
    observer.flush()               # ensure all data is sent
"""

from __future__ import annotations

import logging
import os
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# Cost estimates per provider per image
_COST_TABLE: dict[str, float] = {
    "nb2": 0.067,
    "diffusers": 0.0,
    "mock": 0.0,
    "controlnet_canny": 0.0,
    "controlnet_depth": 0.0,
    "diffusers_inpaint": 0.0,
    "mock_inpaint": 0.0,
}


class _EventLike(Protocol):
    """Duck-typed protocol for PipelineEvent to avoid circular imports."""
    event_type: Any  # EventType enum or has .value
    stage: str
    round_num: int
    payload: dict
    timestamp_ms: int


def _event_type_value(event: _EventLike) -> str:
    """Extract event type string regardless of Enum or str."""
    et = event.event_type
    return et.value if hasattr(et, "value") else str(et)


def _try_import_langfuse():
    """Try to import Langfuse SDK. Returns (Langfuse class, available bool)."""
    try:
        from langfuse import Langfuse  # type: ignore[import-untyped]
        return Langfuse, True
    except ImportError:
        return None, False


class LangfuseObserver:
    """Observes pipeline events and sends traces to Langfuse.

    Automatically detects availability via:
      1. langfuse package installed
      2. LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY env vars set

    If either is missing, all methods become no-ops.

    Uses Langfuse SDK v3 parent-child span nesting pattern.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._available = False
        self._root_span: Any = None
        self._spans: dict[str, Any] = {}  # stage_key -> span

        LangfuseCls, can_import = _try_import_langfuse()
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if can_import and public_key and secret_key:
            try:
                self._client = LangfuseCls(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host,
                )
                self._available = True
                logger.info("Langfuse observer initialized (host=%s)", host)
            except Exception as exc:
                logger.warning("Langfuse init failed, running without tracing: %s", exc)
        else:
            if not can_import:
                logger.debug("Langfuse not installed, tracing disabled")
            elif not public_key or not secret_key:
                logger.debug("Langfuse API keys not set, tracing disabled")

    @property
    def available(self) -> bool:
        return self._available

    def start_trace(
        self,
        task_id: str,
        subject: str,
        tradition: str,
        provider: str = "mock",
        metadata: dict | None = None,
    ) -> None:
        """Start a new Langfuse trace for a pipeline run.

        Creates a root span that serves as the trace container.
        All subsequent stage spans are children of this root span.
        """
        if not self._available:
            return

        try:
            trace_meta = {
                "task_id": task_id,
                "subject": subject,
                "tradition": tradition,
                "provider": provider,
                **(metadata or {}),
            }

            # v3 API: start_span() without trace_context creates a root span
            self._root_span = self._client.start_span(
                name=f"pipeline/{task_id}",
                metadata=trace_meta,
                input={"subject": subject, "tradition": tradition},
            )
            self._spans.clear()
        except Exception as exc:
            logger.warning("Failed to start Langfuse trace: %s", exc)
            self._root_span = None

    def on_event(self, event: _EventLike) -> None:
        """Process a single pipeline event."""
        if not self._available or self._root_span is None:
            return

        try:
            et = _event_type_value(event)
            if et == "stage_started":
                self._on_stage_started(event)
            elif et == "stage_completed":
                self._on_stage_completed(event)
            elif et == "decision_made":
                self._on_decision(event)
            elif et == "pipeline_completed":
                self._on_pipeline_completed(event)
            elif et == "pipeline_failed":
                self._on_pipeline_failed(event)
        except Exception as exc:
            logger.warning("Langfuse event processing failed: %s", exc)

    def flush(self) -> None:
        """Flush all pending Langfuse data."""
        if self._available and self._client:
            try:
                self._client.flush()
            except Exception as exc:
                logger.warning("Langfuse flush failed: %s", exc)

    def shutdown(self) -> None:
        """Shutdown Langfuse client."""
        if self._available and self._client:
            try:
                self._client.shutdown()
            except Exception:
                pass

    # ── Internal event handlers ────────────────────────────────────────

    def _on_stage_started(self, event: _EventLike) -> None:
        span_key = f"{event.stage}_{event.round_num}"
        # Create child span under the root span
        span = self._root_span.start_span(
            name=f"{event.stage}/round-{event.round_num}",
            metadata={"round": event.round_num},
        )
        self._spans[span_key] = span

    def _on_stage_completed(self, event: _EventLike) -> None:
        span_key = f"{event.stage}_{event.round_num}"
        span = self._spans.get(span_key)
        if span is None:
            return

        payload = event.payload
        latency_ms = payload.get("latency_ms", 0)

        if event.stage == "scout":
            span.update(
                output=_safe_summary(payload, ["evidence_coverage", "sample_count", "taboo_count"]),
                metadata={"latency_ms": latency_ms},
            )
        elif event.stage == "draft":
            n_candidates = payload.get("n_candidates", 0)
            provider = payload.get("provider", "mock")
            cost = n_candidates * _COST_TABLE.get(provider, 0.0)
            span.update(
                output={"n_candidates": n_candidates, "provider": provider},
                metadata={"latency_ms": latency_ms, "cost_usd": cost},
            )
        elif event.stage == "critic":
            critique = payload.get("critique", {})
            scored = critique.get("scored_candidates", [])
            best_score = scored[0].get("weighted_total", 0.0) if scored else 0.0
            span.update(
                output={
                    "best_score": best_score,
                    "n_candidates_scored": len(scored),
                    "rerun_hint": critique.get("rerun_hint", []),
                },
                metadata={"latency_ms": latency_ms},
            )
            # If LLM critic was used, record as a generation under this span
            model_ref = critique.get("model_ref")
            if model_ref:
                gen = span.start_generation(
                    name=f"critic-llm/round-{event.round_num}",
                    model=model_ref,
                    metadata={"best_score": best_score},
                )
                gen.end()
        elif event.stage == "queen":
            decision = payload.get("decision", {})
            span.update(
                output={
                    "action": decision.get("action", "unknown"),
                    "reason": decision.get("reason", ""),
                },
                metadata={"latency_ms": latency_ms},
            )
        elif event.stage == "draft_refine":
            span.update(
                output=_safe_summary(payload, ["base_candidate_id", "target_layers"]),
                metadata={"latency_ms": latency_ms},
            )

        span.end()

    def _on_decision(self, event: _EventLike) -> None:
        # Create event under root span
        self._root_span.create_event(
            name="queen_decision",
            metadata={
                "round": event.round_num,
                "action": event.payload.get("action", ""),
                "reason": event.payload.get("reason", ""),
            },
        )

    def _on_pipeline_completed(self, event: _EventLike) -> None:
        payload = event.payload
        if self._root_span:
            self._root_span.update(
                output={
                    "final_decision": payload.get("final_decision", ""),
                    "total_rounds": payload.get("total_rounds", 0),
                    "total_latency_ms": payload.get("total_latency_ms", 0),
                    "total_cost_usd": payload.get("total_cost_usd", 0.0),
                    "success": True,
                },
            )
            self._root_span.end()

    def _on_pipeline_failed(self, event: _EventLike) -> None:
        if self._root_span:
            self._root_span.update(
                output={
                    "success": False,
                    "error": event.payload.get("error", "unknown"),
                },
                level="ERROR",
            )
            self._root_span.end()


def _safe_summary(payload: dict, keys: list[str]) -> dict:
    """Extract selected keys from payload, handling missing gracefully."""
    return {k: payload.get(k) for k in keys if k in payload}
