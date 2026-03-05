"""FastAPI router for the prototype pipeline API.

Endpoints:
    POST /api/v1/prototype/runs              Create a pipeline run
    GET  /api/v1/prototype/runs/{id}         Get run status
    GET  /api/v1/prototype/runs/{id}/events  SSE event stream
    POST /api/v1/prototype/runs/{id}/action  Submit HITL action
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
import uuid
from threading import Thread

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.api.schemas import (
    AgentInfo,
    CreateRunRequest,
    RunStatusResponse,
    SubmitActionRequest,
    SubmitActionResponse,
    ValidateTopologyRequest,
    ValidationResponse,
)
from app.prototype.checkpoints.pipeline_checkpoint import load_pipeline_output
from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.orchestrator.run_state import RunStatus
from app.prototype.pipeline.pipeline_types import PipelineInput

# Lazy import for LangGraph orchestrator (only when use_graph=True)
_GraphOrchestrator = None

def _get_graph_orchestrator_class():
    global _GraphOrchestrator
    if _GraphOrchestrator is None:
        from app.prototype.graph.graph_orchestrator import GraphOrchestrator
        _GraphOrchestrator = GraphOrchestrator
    return _GraphOrchestrator

router = APIRouter(prefix="/api/v1/prototype", tags=["prototype"])

# In-memory stores (sufficient for prototype stage)
_orchestrators: dict[str, PipelineOrchestrator] = {}
_run_metadata: dict[str, dict] = {}   # task_id -> {subject, tradition, created_at, ...}
_event_buffers: dict[str, list[PipelineEvent]] = {}
_idempotency_map: dict[str, str] = {}  # idempotency_key -> task_id
_buffer_lock = threading.Lock()  # Protects _event_buffers writes/reads

# Guest rate limit (simple counter)
_guest_runs_today: dict[str, int] = {}  # date_str -> count
_GUEST_DAILY_LIMIT = 50
_TASK_RETENTION_SEC = 3600  # 1 hour TTL for completed runs


def _cleanup_expired_runs() -> None:
    """Remove completed runs older than retention period to prevent memory leak."""
    now = time.time()
    expired = [
        tid for tid, meta in _run_metadata.items()
        if now - meta.get("created_at", now) > _TASK_RETENTION_SEC
        and meta.get("completed", False)
    ]
    # Also clean stale idempotency entries pointing to expired tasks
    stale_idem = [k for k, v in _idempotency_map.items() if v in expired]
    for k in stale_idem:
        _idempotency_map.pop(k, None)
    for tid in expired:
        _orchestrators.pop(tid, None)
        _run_metadata.pop(tid, None)
        with _buffer_lock:
            _event_buffers.pop(tid, None)


@router.post("/runs")
async def create_run(req: CreateRunRequest) -> RunStatusResponse:
    """Create a new pipeline run."""
    # Idempotency check
    if req.idempotency_key and req.idempotency_key in _idempotency_map:
        existing_id = _idempotency_map[req.idempotency_key]
        return _build_status_response(existing_id)

    # Guest rate limiting
    today = time.strftime("%Y-%m-%d")
    count = _guest_runs_today.get(today, 0)
    if count >= _GUEST_DAILY_LIMIT:
        raise HTTPException(429, "Daily run limit reached. Please try again tomorrow.")
    _guest_runs_today[today] = count + 1

    task_id = f"api-{uuid.uuid4().hex[:8]}"

    # Resolve API key per provider (M0: unified to GOOGLE_API_KEY)
    if req.provider == "nb2":
        api_key = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise HTTPException(400, "GOOGLE_API_KEY/GEMINI_API_KEY not configured on server")
    elif req.provider == "mock":
        api_key = ""
    else:
        # Default: try Google API key for any provider
        api_key = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")

    d_cfg = DraftConfig(
        provider=req.provider, api_key=api_key,
        n_candidates=req.n_candidates, seed_base=42,
    )
    cr_cfg = CriticConfig()
    q_cfg = QueenConfig(max_rounds=req.max_rounds)

    # M3: custom topology forces LangGraph path
    use_graph = req.use_graph or req.custom_nodes is not None

    # Dual-track: use_graph selects LangGraph-based orchestrator
    if use_graph:
        GraphOrchestrator = _get_graph_orchestrator_class()
        template_name = req.template

        # If custom topology provided, register a transient template
        if req.custom_nodes is not None and req.custom_edges is not None:
            try:
                from app.prototype.graph.templates.template_model import GraphTemplate
                from app.prototype.graph.templates.template_registry import TemplateRegistry
                custom_tmpl = GraphTemplate(
                    name=f"_custom_{task_id}",
                    display_name="Custom Pipeline",
                    description="User-defined topology",
                    entry_point=req.custom_nodes[0] if req.custom_nodes else "scout",
                    nodes=req.custom_nodes,
                    edges=req.custom_edges,
                )
                TemplateRegistry.register(custom_tmpl)
                template_name = custom_tmpl.name
            except (ImportError, Exception):
                pass  # Fall back to default template

        orchestrator = GraphOrchestrator(
            draft_config=d_cfg.to_dict(),
            critic_config=cr_cfg.to_dict(),
            queen_config=q_cfg.to_dict(),
            enable_hitl=req.enable_hitl,
            enable_agent_critic=req.enable_agent_critic,
            max_rounds=req.max_rounds,
            template=template_name,
        )
    else:
        orchestrator = PipelineOrchestrator(
            draft_config=d_cfg,
            critic_config=cr_cfg,
            queen_config=q_cfg,
            enable_hitl=req.enable_hitl,
            enable_archivist=True,
            enable_agent_critic=req.enable_agent_critic,
            enable_fix_it_plan=req.enable_agent_critic,
            enable_parallel_critic=req.enable_parallel_critic,
        )
    _orchestrators[task_id] = orchestrator
    _run_metadata[task_id] = {
        "subject": req.subject,
        "tradition": req.tradition,
        "provider": req.provider,
        "created_at": time.time(),
        "node_params": req.node_params,
    }
    with _buffer_lock:
        _event_buffers[task_id] = []

    if req.idempotency_key:
        _idempotency_map[req.idempotency_key] = task_id

    # Run pipeline in background thread
    pipeline_input = PipelineInput(
        task_id=task_id, subject=req.subject, cultural_tradition=req.tradition,
    )

    def _run_in_background() -> None:
        for event in orchestrator.run_stream(pipeline_input):
            with _buffer_lock:
                _event_buffers.setdefault(task_id, []).append(event)
        # Mark this run as completed so cleanup won't remove it prematurely
        if task_id in _run_metadata:
            _run_metadata[task_id]["completed"] = True
        # Cleanup expired runs after pipeline completes
        _cleanup_expired_runs()

    thread = Thread(target=_run_in_background, daemon=True)
    thread.start()

    return RunStatusResponse(
        task_id=task_id,
        status="running",
    )


@router.get("/templates")
async def list_templates() -> list[dict]:
    """List available graph templates."""
    try:
        from app.prototype.graph.templates.template_registry import TemplateRegistry
        return [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "nodes": t.nodes,
                "edges": t.edges,
                "conditional_edges": [
                    {"source": ce.source, "targets": ce.destinations}
                    for ce in (t.conditional_edges or [])
                ] if hasattr(t, "conditional_edges") and t.conditional_edges else [],
                "enable_loop": t.enable_loop,
                "parallel_critic": t.parallel_critic,
            }
            for t in TemplateRegistry.list_templates()
        ]
    except ImportError:
        return [{"name": "default", "display_name": "Standard Pipeline", "description": "Full pipeline", "nodes": ["scout", "router", "draft", "critic", "queen", "archivist"], "edges": [["scout", "router"], ["router", "draft"], ["draft", "critic"], ["critic", "queen"], ["queen", "archivist"]], "conditional_edges": [], "enable_loop": True, "parallel_critic": False}]


@router.get("/agents")
async def list_agents() -> list[AgentInfo]:
    """List all registered agents with metadata."""
    try:
        from app.prototype.graph.registry import AgentRegistry
        import app.prototype.graph.nodes  # noqa: F401 — triggers @register decorators

        result = []
        for info in AgentRegistry.list_agents_with_metadata():
            meta = info.get("metadata") or {}
            result.append(AgentInfo(
                name=info["name"],
                display_name=meta.get("display_name", ""),
                description=info.get("description", ""),
                supports_hitl=meta.get("supports_hitl", False),
                estimated_latency_ms=meta.get("estimated_latency_ms", 0),
                input_keys=meta.get("input_keys", []),
                output_keys=meta.get("output_keys", []),
                tags=meta.get("tags", []),
            ))
        return result
    except ImportError:
        return []


@router.post("/topologies/validate")
async def validate_topology(req: ValidateTopologyRequest) -> ValidationResponse:
    """Validate a custom topology's I/O contracts."""
    try:
        from app.prototype.graph.templates.template_model import GraphTemplate
        from app.prototype.graph.templates.topology_validator import validate_template

        temp_template = GraphTemplate(
            name="_custom",
            display_name="Custom",
            description="User-defined topology for validation",
            entry_point=req.nodes[0] if req.nodes else "scout",
            nodes=req.nodes,
            edges=req.edges,
        )
        result = validate_template(temp_template)
        return ValidationResponse(
            valid=result.valid,
            errors=result.errors,
            warnings=result.warnings,
        )
    except ImportError:
        return ValidationResponse(valid=False, errors=["Topology validator not available"])
    except (KeyError, ValueError) as e:
        return ValidationResponse(valid=False, errors=[str(e)])


@router.get("/runs/{task_id}")
async def get_run_status(task_id: str) -> RunStatusResponse:
    """Get the current status of a pipeline run."""
    return _build_status_response(task_id)


@router.get("/runs/{task_id}/events")
async def stream_events(task_id: str) -> StreamingResponse:
    """SSE event stream for a pipeline run."""
    if task_id not in _orchestrators and task_id not in _run_metadata:
        raise HTTPException(404, f"Run {task_id} not found")

    async def generate():
        seen = 0
        max_wait = 300  # 5 minutes timeout
        start = time.monotonic()

        while time.monotonic() - start < max_wait:
            with _buffer_lock:
                buffer = list(_event_buffers.get(task_id, []))
            while seen < len(buffer):
                event = buffer[seen]
                seen += 1
                data = json.dumps(event.to_dict(), ensure_ascii=False)
                yield f"data: {data}\n\n"

                if event.event_type in (EventType.PIPELINE_COMPLETED, EventType.PIPELINE_FAILED):
                    return

            # Brief async sleep
            await asyncio.sleep(0.1)

        yield f"data: {json.dumps({'event_type': 'timeout', 'payload': {}})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/runs/{task_id}/action")
async def submit_action(task_id: str, req: SubmitActionRequest) -> SubmitActionResponse:
    """Submit a human-in-the-loop action."""
    orchestrator = _orchestrators.get(task_id)
    if orchestrator is None:
        raise HTTPException(404, f"Run {task_id} not found")

    # Action validation handled by Pydantic Literal in SubmitActionRequest
    if req.action == "force_accept" and not req.candidate_id:
        raise HTTPException(400, "candidate_id is required for force_accept")

    success = orchestrator.submit_action(
        task_id=task_id,
        action=req.action,
        locked_dimensions=req.locked_dimensions,
        rerun_dimensions=req.rerun_dimensions,
        candidate_id=req.candidate_id,
        reason=req.reason,
    )

    if not success:
        return SubmitActionResponse(
            accepted=False,
            message="Run is not waiting for human input",
        )

    return SubmitActionResponse(accepted=True, message=f"Action '{req.action}' accepted")


def _build_status_response(task_id: str) -> RunStatusResponse:
    """Build status response from orchestrator state and checkpoints."""
    orchestrator = _orchestrators.get(task_id)

    # Try to get from orchestrator run state
    if orchestrator:
        run_state = orchestrator.get_run_state(task_id)
        if run_state:
            # Check event buffer for completion
            with _buffer_lock:
                buffer = list(_event_buffers.get(task_id, []))
            completion_event = None
            for ev in reversed(buffer):
                if ev.event_type in (EventType.PIPELINE_COMPLETED, EventType.PIPELINE_FAILED):
                    completion_event = ev
                    break

            if completion_event:
                p = completion_event.payload
                return RunStatusResponse(
                    task_id=task_id,
                    status=run_state.status.value,
                    current_stage=run_state.current_stage,
                    current_round=run_state.current_round,
                    final_decision=p.get("final_decision"),
                    best_candidate_id=p.get("best_candidate_id"),
                    total_rounds=p.get("total_rounds", 0),
                    total_latency_ms=p.get("total_latency_ms", 0),
                    total_cost_usd=p.get("total_cost_usd", 0.0),
                    success=p.get("success"),
                    error=p.get("error"),
                    stages=[s.to_dict() if hasattr(s, 'to_dict') else s for s in p.get("stages", [])],
                )

            return RunStatusResponse(
                task_id=task_id,
                status=run_state.status.value,
                current_stage=run_state.current_stage,
                current_round=run_state.current_round,
            )

    # Fallback: check checkpoint
    saved = load_pipeline_output(task_id)
    if saved:
        return RunStatusResponse(
            task_id=task_id,
            status="completed" if saved.get("success") else "failed",
            final_decision=saved.get("final_decision"),
            best_candidate_id=saved.get("best_candidate_id"),
            total_rounds=saved.get("total_rounds", 0),
            total_latency_ms=saved.get("total_latency_ms", 0),
            success=saved.get("success"),
            error=saved.get("error"),
            stages=saved.get("stages", []),
        )

    raise HTTPException(404, f"Run {task_id} not found")
