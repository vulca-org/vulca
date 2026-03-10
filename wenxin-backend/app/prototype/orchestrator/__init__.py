"""PipelineOrchestrator — unified pipeline execution core.

Orchestrator Architecture Decision (Route B+, 2026-03-10):
- PipelineOrchestrator: **Production** orchestrator, used by all API routes.
  Entry points: /api/v1/create, /api/v1/prototype/runs (default), CLI, Gradio.
- GraphOrchestrator (app.prototype.graph.graph_orchestrator): **Experimental**
  LangGraph-based orchestrator. Only activated when use_graph=True in
  /api/v1/prototype/runs. Has extra capabilities (templates, custom topologies,
  agent registry) but no test coverage and not used in production.
  Kept for future migration. If migrating, update create_routes.py and routes.py.

To get the production orchestrator, use:
    from app.prototype.orchestrator import get_orchestrator
    orch = get_orchestrator()  # Returns PipelineOrchestrator (default)
"""

from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.orchestrator.run_state import RunState, RunStatus


def get_orchestrator(mode: str = "pipeline", **kwargs):
    """Unified entry point for obtaining an orchestrator instance.

    Parameters
    ----------
    mode : str
        "pipeline" (default) — Returns PipelineOrchestrator (production).
        "graph" — Returns GraphOrchestrator (experimental, LangGraph-based).
        "auto" — Same as "pipeline" (reserved for future config-driven selection).
    **kwargs
        Forwarded to the orchestrator constructor.

    Returns
    -------
    PipelineOrchestrator or GraphOrchestrator
    """
    if mode in ("pipeline", "auto"):
        return PipelineOrchestrator(**kwargs)
    elif mode == "graph":
        from app.prototype.graph.graph_orchestrator import GraphOrchestrator
        return GraphOrchestrator(**kwargs)
    else:
        raise ValueError(
            f"Unknown orchestrator mode '{mode}'. Choose 'pipeline', 'graph', or 'auto'."
        )


__all__ = [
    "EventType",
    "PipelineEvent",
    "PipelineOrchestrator",
    "RunState",
    "RunStatus",
    "get_orchestrator",
]
