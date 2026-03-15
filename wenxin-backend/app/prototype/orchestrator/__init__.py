"""PipelineOrchestrator — unified pipeline execution core.

.. deprecated:: Phase 5D
    The default orchestrator mode has changed from "pipeline" to "graph".
    The PipelineOrchestrator is still available via mode="pipeline" but
    is deprecated. Use GraphOrchestrator (mode="graph", now default).
"""

import warnings

from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.orchestrator.run_state import RunState, RunStatus


def get_orchestrator(mode: str = "graph", **kwargs):
    """Unified entry point for obtaining an orchestrator instance.

    .. versionchanged:: Phase 5D
        Default mode changed from "pipeline" to "graph".

    Parameters
    ----------
    mode : str
        "graph" (default) — Returns GraphOrchestrator (production).
        "pipeline" — Returns PipelineOrchestrator (deprecated).
        "auto" — Same as "graph".
    **kwargs
        Forwarded to the orchestrator constructor.

    Returns
    -------
    GraphOrchestrator or PipelineOrchestrator
    """
    if mode == "pipeline":
        warnings.warn(
            "mode='pipeline' is deprecated since Phase 5D. "
            "Use mode='graph' (now default) instead. "
            "PipelineOrchestrator will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return PipelineOrchestrator(**kwargs)
    elif mode in ("graph", "auto"):
        from app.prototype.graph.graph_orchestrator import GraphOrchestrator
        return GraphOrchestrator(**kwargs)
    else:
        raise ValueError(
            f"Unknown orchestrator mode '{mode}'. Choose 'graph', 'pipeline', or 'auto'."
        )


__all__ = [
    "EventType",
    "PipelineEvent",
    "PipelineOrchestrator",
    "RunState",
    "RunStatus",
    "get_orchestrator",
]
