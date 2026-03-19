"""FastAPI router for the prototype pipeline API.

Endpoints:
    POST /api/v1/prototype/runs              Create a pipeline run
    GET  /api/v1/prototype/runs/{id}         Get run status
    GET  /api/v1/prototype/runs/{id}/events  SSE event stream
    POST /api/v1/prototype/runs/{id}/action  Submit HITL action
    GET  /api/v1/prototype/classify-tradition  Classify tradition from subject text
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
import uuid
from threading import Thread

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.prototype.api.auth import verify_api_key
from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.api.schemas import (
    AgentInfo,
    CreateRunRequest,
    ExecuteGraphRequest,
    ExecuteGraphResponse,
    GraphValidateRequest,
    GraphValidateResponse,
    NodeRuntimeToggleResponse,
    RunStatusResponse,
    SubmitActionRequest,
    SubmitActionResponse,
    ValidateTopologyRequest,
    ValidationResponse,
)
from app.prototype.checkpoints.pipeline_checkpoint import load_pipeline_output
from app.prototype.orchestrator.events import EventType, PipelineEvent
from app.prototype.orchestrator.run_state import RunStatus
from app.prototype.pipeline.pipeline_types import PipelineInput

# Lazy import for LangGraph orchestrator (only when use_graph=True)
# Orchestrator Architecture Decision (Route B+, 2026-03-10):
# Default path (use_graph=False) → PipelineOrchestrator (production)
# Opt-in path (use_graph=True)   → GraphOrchestrator (experimental)
# Unified entry point: app.prototype.orchestrator.get_orchestrator()
_GraphOrchestrator = None

def _get_graph_orchestrator_class():
    global _GraphOrchestrator
    if _GraphOrchestrator is None:
        try:
            from app.prototype.graph.graph_orchestrator import GraphOrchestrator
            _GraphOrchestrator = GraphOrchestrator
        except ImportError:
            return None
    return _GraphOrchestrator

router = APIRouter(prefix="/api/v1/prototype", tags=["prototype"])

# In-memory stores (sufficient for prototype stage)
_orchestrators: dict = {}  # task_id -> reserved for future use
_run_metadata: dict[str, dict] = {}   # task_id -> {subject, tradition, created_at, ...}
_event_buffers: dict[str, list[PipelineEvent]] = {}
_idempotency_map: dict[str, str] = {}  # idempotency_key -> task_id
_buffer_lock = threading.Lock()  # Protects _event_buffers writes/reads

# Guest rate limit (simple counter)
_guest_runs_today: dict[str, int] = {}  # date_str -> count
_GUEST_DAILY_LIMIT = int(os.environ.get("VULCA_DAILY_LIMIT", "50"))
_TASK_RETENTION_SEC = 3600  # 1 hour TTL for completed runs
_TASK_HARD_TIMEOUT_SEC = 14400  # 4 hours: force-clean even incomplete runs
_EVOLUTION_INTERVAL_SEC = 300  # Throttle: evolve at most once per 5 minutes


def _cleanup_expired_runs() -> None:
    """Remove completed runs older than retention period to prevent memory leak.

    Also force-cleans any run (including incomplete) older than hard timeout.
    """
    now = time.time()
    expired = [
        tid for tid, meta in _run_metadata.items()
        if (
            now - meta.get("created_at", now) > _TASK_RETENTION_SEC
            and meta.get("completed", False)
        )
        or now - meta.get("created_at", now) > _TASK_HARD_TIMEOUT_SEC
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

    # Resolve provider: "auto" detects API key availability
    api_key = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    provider = req.provider
    if provider == "auto":
        provider = "nb2" if api_key else "mock"
    elif provider == "nb2" and not api_key:
        raise HTTPException(400, "GOOGLE_API_KEY/GEMINI_API_KEY not configured on server")
    elif provider == "mock":
        api_key = ""

    # Auto-enable LLM features when API key is available
    # Disable LLM-heavy features for mock provider (scoring colored rectangles is pointless)
    has_api_key = bool(api_key)
    is_mock = (provider == "mock")
    enable_prompt_enhancer = req.enable_prompt_enhancer and has_api_key and not is_mock
    enable_llm_queen = req.enable_llm_queen and has_api_key and not is_mock

    d_cfg = DraftConfig(
        provider=provider, api_key=api_key,
        n_candidates=req.n_candidates, seed_base=42,
    )
    # Disable VLM for mock provider (scoring colored rectangles is pointless)
    cr_cfg = CriticConfig(use_vlm=(provider != "mock"))
    q_cfg = QueenConfig(max_rounds=req.max_rounds)

    # ONE PIPELINE: use vulca/ engine directly (Phase 9B)
    from vulca.pipeline.templates import DEFAULT, TEMPLATES
    from vulca.pipeline.types import PipelineInput as VulcaPipelineInput

    # Resolve pipeline definition: custom topology > template > default
    from vulca.pipeline.types import PipelineDefinition
    if req.custom_nodes and req.custom_edges:
        # Validate: all nodes must be known builtins or aliases
        _KNOWN_NODES = {"generate", "evaluate", "decide", "scout", "draft", "critic", "queen"}
        unknown = set(req.custom_nodes) - _KNOWN_NODES
        if unknown:
            raise HTTPException(400, f"Unknown node(s): {unknown}. Available: {sorted(_KNOWN_NODES)}")
        if not req.custom_edges:
            raise HTTPException(400, "custom_edges required when custom_nodes provided")
        definition = PipelineDefinition(
            name="custom",
            display_name="Custom Topology",
            entry_point=req.custom_nodes[0],
            nodes=tuple(req.custom_nodes),
            edges=tuple(tuple(e) for e in req.custom_edges),
            enable_loop=True,
        )
    else:
        template_name = req.template or "default"
        definition = TEMPLATES.get(template_name, DEFAULT)

    # Extract custom L1-L5 weights from node_params (Canvas weight sliders)
    _node_params: dict[str, dict] = {}
    if req.node_params:
        critic_params = req.node_params.get("critic", {})
        custom_weights: dict[str, float] = {}
        for i in range(1, 6):
            key = f"w_l{i}"
            if key in critic_params:
                custom_weights[f"L{i}"] = float(critic_params[key])
        if custom_weights:
            _node_params["evaluate"] = {"custom_weights": custom_weights}

    vulca_input = VulcaPipelineInput(
        subject=req.subject,
        intent=req.intent or req.subject,
        tradition=req.tradition,
        provider=provider,
        max_rounds=req.max_rounds,
        node_params=_node_params,
    )
    _run_metadata[task_id] = {
        "subject": req.subject,
        "tradition": req.tradition,
        "provider": provider,
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
      try:
        from vulca.pipeline.engine import execute
        from app.prototype.api.create_routes import _build_implicit_feedback
        from app.prototype.digestion.feature_extractor import extract_cultural_features
        from app.prototype.session.store import SessionStore
        from app.prototype.session.types import SessionDigest

        t0 = time.monotonic()

        def _emit_event(event) -> None:
            with _buffer_lock:
                _event_buffers.setdefault(task_id, []).append(event)

        _interrupt_before = {"decide"} if req.enable_hitl else None

        loop = asyncio.new_event_loop()
        try:
            output = loop.run_until_complete(
                execute(definition, vulca_input, event_callback=_emit_event, interrupt_before=_interrupt_before)
            )
        finally:
            loop.close()

        # Store pipeline output for submit_action to read real scores
        if task_id in _run_metadata:
            _run_metadata[task_id]["pipeline_output"] = {
                "scores": output.final_scores,
                "weighted_total": output.weighted_total,
                "best_candidate_id": output.best_candidate_id,
                "total_rounds": output.total_rounds,
                "total_cost_usd": output.total_cost_usd,
                "total_latency_ms": output.total_latency_ms,
            }

        # Mark this run as completed (unless waiting for human input)
        is_waiting = output.status == "waiting_human"
        if task_id in _run_metadata and not is_waiting:
            _run_metadata[task_id]["completed"] = True

        # Persist session digest for Gallery (skip if waiting for human)
        if not is_waiting and (output.final_scores or output.total_rounds > 0):
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            digest = SessionDigest(
                session_id=task_id,
                mode="create",
                intent=req.intent or req.subject,
                tradition=req.tradition,
                subject=req.subject,
                rounds=[],
                final_scores=output.final_scores,
                final_weighted_total=output.weighted_total,
                best_image_url=output.best_image_url,
                total_rounds=output.total_rounds,
                total_latency_ms=elapsed_ms,
                total_cost_usd=output.total_cost_usd,
                feedback=_build_implicit_feedback(
                    {"best_candidate_id": output.best_candidate_id, "total_rounds": output.total_rounds},
                    output.final_scores,
                ),
            )
            digest.cultural_features = extract_cultural_features(
                tradition=req.tradition,
                final_scores=output.final_scores,
                risk_flags=[],
            )
            SessionStore.get().append(digest)

            # Auto-trigger evolution (throttled, shared with SDK/CLI)
            # Also capture evolution suggestion for the frontend
            evolution_suggestion = ""
            try:
                from vulca.pipeline.hooks import _maybe_evolve
                import asyncio as _asyncio
                _evo_loop = _asyncio.new_event_loop()
                _evo_loop.run_until_complete(_maybe_evolve(task_id))
                _evo_loop.close()

                # Lightweight fallback: generate suggestion from weakest dimension
                # of this session (no 5-session gate — works for new users too)
                if not evolution_suggestion and output.final_scores:
                    dim_names = {"L1": "Visual Perception", "L2": "Technical Execution",
                                 "L3": "Cultural Context", "L4": "Critical Interpretation",
                                 "L5": "Philosophical Aesthetics"}
                    weakest = min(output.final_scores, key=lambda k: output.final_scores.get(k, 1.0))
                    weakest_score = output.final_scores.get(weakest, 0.0)
                    if weakest_score < 0.7:
                        evolution_suggestion = (
                            f"Focus on {dim_names.get(weakest, weakest)}: "
                            f"scored {weakest_score:.0%}, consider increasing {weakest} weight"
                        )
            except Exception:
                pass  # Non-fatal

            # Emit evolution suggestion via a supplementary event
            if evolution_suggestion:
                from vulca.pipeline.types import PipelineEvent as VulcaEvent
                from vulca.pipeline.types import EventType as VulcaEventType
                evo_event = VulcaEvent(
                    event_type=VulcaEventType.SESSION_DIGEST,
                    payload={"evolution_suggestion": evolution_suggestion},
                    timestamp_ms=int((time.monotonic() - t0) * 1000),
                )
                with _buffer_lock:
                    _event_buffers.setdefault(task_id, []).append(evo_event)

        _cleanup_expired_runs()
      except Exception:
        logging.getLogger("vulca.pipeline").exception(
            "Background pipeline %s crashed", task_id,
        )

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
    if task_id not in _run_metadata:
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
    """Submit a human-in-the-loop action.

    Works with vulca/ engine's interrupt_before mechanism:
    - Pipeline pauses → status=waiting_human
    - Human submits action → stored + human_received event emitted
    - Pipeline completion event emitted reflecting the decision
    """
    meta = _run_metadata.get(task_id)
    if meta is None:
        raise HTTPException(404, f"Run {task_id} not found")

    # Action validation
    if req.action == "force_accept" and not req.candidate_id:
        raise HTTPException(400, "candidate_id is required for force_accept")

    # Check if run is actually waiting for human input
    with _buffer_lock:
        buffer = list(_event_buffers.get(task_id, []))
    is_waiting = any(
        (ev.event_type if isinstance(ev.event_type, str) else ev.event_type.value) == "human_required"
        for ev in buffer
    ) and not any(
        (ev.event_type if isinstance(ev.event_type, str) else ev.event_type.value) in ("human_received", "pipeline_completed", "pipeline_failed")
        for ev in buffer
    )

    if not is_waiting:
        return SubmitActionResponse(
            accepted=False,
            message="Run is not waiting for human input",
        )

    # Store the action
    meta["human_action"] = req.action
    meta["human_action_data"] = {
        "locked_dimensions": req.locked_dimensions,
        "rerun_dimensions": req.rerun_dimensions,
        "candidate_id": req.candidate_id,
        "reason": req.reason,
    }

    # Emit human_received event
    from vulca.pipeline.types import PipelineEvent as VulcaEvent
    from vulca.pipeline.types import EventType as VulcaEventType

    now_ms = int(time.monotonic() * 1000)
    received_event = VulcaEvent(
        event_type=VulcaEventType.HUMAN_RECEIVED,
        payload={"action": req.action, "reason": req.reason or ""},
        timestamp_ms=now_ms,
    )
    with _buffer_lock:
        _event_buffers.setdefault(task_id, []).append(received_event)

    # Read real pipeline data if available
    pipe_out = meta.get("pipeline_output", {})

    # For approve/force_accept: emit pipeline_completed
    # For reject/rerun: emit pipeline_completed with the action info
    final_decision = req.action
    completed_event = VulcaEvent(
        event_type=VulcaEventType.PIPELINE_COMPLETED,
        payload={
            "status": "completed",
            "decision": final_decision,
            "best_candidate_id": req.candidate_id or pipe_out.get("best_candidate_id", ""),
            "scores": pipe_out.get("scores", {}),
            "weighted_total": pipe_out.get("weighted_total", 0.0),
            "total_rounds": pipe_out.get("total_rounds", 0),
            "total_latency_ms": pipe_out.get("total_latency_ms", now_ms),
            "total_cost_usd": pipe_out.get("total_cost_usd", 0.0),
            "human_action": req.action,
        },
        timestamp_ms=now_ms,
    )
    with _buffer_lock:
        _event_buffers.setdefault(task_id, []).append(completed_event)

    meta["completed"] = True

    return SubmitActionResponse(accepted=True, message=f"Action '{req.action}' accepted")


@router.get("/datatypes")
async def list_datatypes():
    """List all DataType values with their socket colors."""
    from app.prototype.pipeline.socket_colors import get_all_socket_colors
    from app.prototype.pipeline.port_contract import DataType
    return {
        "datatypes": [
            {"value": dt.value, "color": get_all_socket_colors().get(dt.value, "#6B7B8D")}
            for dt in DataType
        ]
    }


# ---------------------------------------------------------------------------
# Graph execution API (Phase 5D)
# ---------------------------------------------------------------------------

# In-memory node runtime managers per task (capped to prevent unbounded growth)
_node_runtime_managers: dict[str, "NodeRuntimeManager"] = {}
_NODE_RUNTIME_MAX = 100


def _get_runtime_manager(task_id: str) -> "NodeRuntimeManager":
    """Get or create a NodeRuntimeManager, evicting oldest if over limit."""
    from app.prototype.graph.node_runtime import NodeRuntimeManager
    if task_id not in _node_runtime_managers:
        # Evict oldest entries if over limit
        while len(_node_runtime_managers) >= _NODE_RUNTIME_MAX:
            oldest = next(iter(_node_runtime_managers))
            del _node_runtime_managers[oldest]
        _node_runtime_managers[task_id] = NodeRuntimeManager()
    return _node_runtime_managers[task_id]


@router.post("/graph/execute")
async def execute_graph(req: ExecuteGraphRequest) -> ExecuteGraphResponse:
    """Execute a graph synchronously (headless mode)."""
    import uuid
    from app.prototype.graph.graph_orchestrator import GraphOrchestrator
    from app.prototype.pipeline.pipeline_types import PipelineInput

    task_id = f"graph-{uuid.uuid4().hex[:8]}"

    orch = GraphOrchestrator(
        enable_agent_critic=req.enable_agent_critic,
        max_rounds=req.max_rounds,
        template=req.template,
    )

    pipeline_input = PipelineInput(
        task_id=task_id,
        subject=req.subject,
        cultural_tradition=req.tradition,
    )

    result = orch.run_sync(pipeline_input)

    return ExecuteGraphResponse(
        task_id=task_id,
        success=result.get("success", False),
        error=result.get("error"),
        events=result.get("events", []),
    )


@router.post("/graph/validate")
async def validate_graph(req: GraphValidateRequest) -> GraphValidateResponse:
    """Validate graph topology with optional port contract checking."""
    try:
        from app.prototype.graph.templates.template_model import GraphTemplate
        from app.prototype.graph.templates.topology_validator import validate_template
        from app.prototype.pipeline.port_contract import get_contract, list_contracts

        temp_template = GraphTemplate(
            name="_validate",
            display_name="Validation",
            description="Topology for validation",
            entry_point=req.nodes[0] if req.nodes else "scout",
            nodes=req.nodes,
            edges=req.edges,
        )
        result = validate_template(temp_template)

        port_contracts = None
        if req.check_ports:
            contracts = list_contracts()
            port_contracts = {}
            for node_name in req.nodes:
                contract = contracts.get(node_name)
                if contract:
                    port_contracts[node_name] = {
                        "inputs": [{"name": p.name, "type": p.data_type.value, "required": p.required} for p in contract.input_ports],
                        "outputs": [{"name": p.name, "type": p.data_type.value} for p in contract.output_ports],
                    }

        return GraphValidateResponse(
            valid=result.valid,
            errors=result.errors,
            warnings=result.warnings,
            port_contracts=port_contracts,
        )
    except (ImportError, KeyError, ValueError) as e:
        return GraphValidateResponse(valid=False, errors=[str(e)])


@router.get("/graph/templates")
async def list_graph_templates_with_ports():
    """Enhanced template listing with port contract info."""
    try:
        from app.prototype.graph.templates.template_registry import TemplateRegistry
        from app.prototype.pipeline.port_contract import get_contract

        templates = []
        for t in TemplateRegistry.list_templates():
            tmpl_data = {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "nodes": t.nodes,
                "edges": t.edges,
                "enable_loop": t.enable_loop,
                "parallel_critic": t.parallel_critic,
                "port_contracts": {},
            }
            for node_name in t.nodes:
                contract = get_contract(node_name)
                if contract:
                    tmpl_data["port_contracts"][node_name] = {
                        "inputs": [{"name": p.name, "type": p.data_type.value, "required": p.required} for p in contract.input_ports],
                        "outputs": [{"name": p.name, "type": p.data_type.value} for p in contract.output_ports],
                    }
            templates.append(tmpl_data)
        return templates
    except ImportError:
        return []


@router.post("/graph/nodes/{node_name}/mute")
async def toggle_node_mute(node_name: str, task_id: str = Query(default="global")) -> NodeRuntimeToggleResponse:
    """Toggle mute state for a node."""
    mgr = _get_runtime_manager(task_id)
    value = mgr.toggle_mute(node_name)
    return NodeRuntimeToggleResponse(node_name=node_name, state="muted", value=value)


@router.post("/graph/nodes/{node_name}/bypass")
async def toggle_node_bypass(node_name: str, task_id: str = Query(default="global")) -> NodeRuntimeToggleResponse:
    """Toggle bypass state for a node."""
    mgr = _get_runtime_manager(task_id)
    value = mgr.toggle_bypass(node_name)
    return NodeRuntimeToggleResponse(node_name=node_name, state="bypassed", value=value)


@router.post("/graph/nodes/{node_name}/expand")
async def toggle_node_expand(node_name: str, task_id: str = Query(default="global")) -> NodeRuntimeToggleResponse:
    """Toggle expand state for a node."""
    mgr = _get_runtime_manager(task_id)
    value = mgr.toggle_expand(node_name)
    return NodeRuntimeToggleResponse(node_name=node_name, state="expanded", value=value)


def _build_status_response(task_id: str) -> RunStatusResponse:
    """Build status response from event buffer, metadata, or checkpoints."""
    # Check event buffer for status
    if task_id in _run_metadata:
        with _buffer_lock:
            buffer = list(_event_buffers.get(task_id, []))

        # Find completion event
        completion_event = None
        for ev in reversed(buffer):
            evt = ev.event_type if isinstance(ev.event_type, str) else ev.event_type.value
            if evt in ("pipeline_completed", "pipeline_failed"):
                completion_event = ev
                break

        if completion_event:
            p = completion_event.payload if isinstance(completion_event.payload, dict) else {}
            # Use .value for enum (str(enum) returns "ClassName.MEMBER" in Python 3.11+)
            evt_val = completion_event.event_type.value if hasattr(completion_event.event_type, 'value') else str(completion_event.event_type)
            status = "completed" if "completed" in evt_val else "failed"
            return RunStatusResponse(
                task_id=task_id,
                status=status,
                final_decision=p.get("decision"),
                best_candidate_id=p.get("best_candidate_id"),
                total_rounds=p.get("total_rounds", 0),
                total_latency_ms=p.get("total_latency_ms", 0),
                total_cost_usd=p.get("total_cost_usd", 0.0),
            )

        # Check for waiting_human (HITL)
        is_waiting = any(
            (ev.event_type if isinstance(ev.event_type, str) else ev.event_type.value) == "human_required"
            for ev in buffer
        )
        if is_waiting:
            return RunStatusResponse(task_id=task_id, status="waiting_human")

        # Still running
        return RunStatusResponse(task_id=task_id, status="running")

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


@router.get("/capabilities")
async def get_capabilities():
    """Report server AI capabilities so the frontend can adapt UI."""
    api_key = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    has_key = bool(api_key)

    # NOTE: ProviderRegistry (draft_provider.py) tracks registered providers,
    # but this list includes cost/availability metadata the registry doesn't track.
    # FLUX.2 Pro pricing: ~$0.05/image (vs $0.003 for Schnell).
    providers = [
        {"id": "mock", "label": "Mock", "cost": 0, "available": True},
        {"id": "nb2", "label": "NB2", "cost": 0.067, "available": has_key},
        {"id": "diffusers", "label": "Diffusers", "cost": 0, "available": True},
        {"id": "openai", "label": "DALL-E 3", "cost": 0.04, "available": bool(os.environ.get("OPENAI_API_KEY"))},
        {"id": "replicate", "label": "FLUX.2 Pro", "cost": 0.05, "available": bool(os.environ.get("REPLICATE_API_TOKEN"))},
    ]

    return {
        "has_api_key": has_key,
        "default_provider": "nb2" if has_key else "mock",
        "providers": providers,
        "features": {
            "real_image_generation": has_key,
            "vlm_critic": has_key,
            "llm_agent_critic": has_key,
            "prompt_enhancer": has_key,
            "llm_queen": has_key,
        },
    }


# ---------------------------------------------------------------------------
# Tradition Classification endpoint
# ---------------------------------------------------------------------------

@router.get("/classify-tradition")
async def classify_tradition(
    subject: str = Query(..., min_length=1, max_length=500, description="Subject text to classify"),
):
    """Classify the cultural tradition of a subject description.

    Uses a two-tier approach:
      1. Fast keyword matching (exact term lookup, instant)
      2. Rich heuristic scoring with weighted cultural indicators

    Returns tradition, confidence score (0-1), and classification method.
    """
    from app.prototype.cultural_pipelines.tradition_classifier import (
        classify_tradition as _classify,
    )

    result = _classify(subject)
    response: dict = {
        "tradition": result.tradition,
        "confidence": result.confidence,
        "method": result.method,
    }
    if result.runner_up:
        response["runner_up"] = result.runner_up
        response["runner_up_confidence"] = result.runner_up_confidence
    return response


# ---------------------------------------------------------------------------
# Gallery & Evolution endpoints
# ---------------------------------------------------------------------------

@router.get("/gallery")
async def list_gallery(
    limit: int = 50,
    offset: int = 0,
    tradition: str | None = None,
    subject: str | None = None,
    min_score: float | None = None,
    max_score: float | None = None,
    sort_by: str = "newest",
    sort_order: str = "desc",
    published_only: bool = False,
):
    """Return completed sessions for the Gallery page.

    Supports pagination via limit/offset, filtering, and sorting.

    Query params:
        limit:          Max items to return (default 50).
        offset:         Number of items to skip (default 0).
        tradition:      Filter by cultural tradition (optional).
        subject:        Full-text search on subject field (optional).
        min_score:      Minimum overall score filter (optional).
        max_score:      Maximum overall score filter (optional).
        sort_by:        Sort key — "newest" (created_at), "score" (overall),
                        "rounds" (total_rounds), "likes". Default "newest".
        sort_order:     "asc" or "desc" (default "desc").
        published_only: If true, only show published items (default false).
    """
    from app.prototype.session.store import SessionStore

    store = SessionStore.get()
    sessions = store.get_all()

    # Load like counts for likes_count field and sort_by=likes
    try:
        from app.prototype.api.gallery_social import _count_likes
        likes_map = _count_likes()
    except Exception:
        likes_map = {}

    # Build full list of gallery-eligible items (unsliced)
    gallery_items = []
    for s in sessions:
        if s.get("final_weighted_total") is None and not s.get("final_scores"):
            continue
        if tradition and s.get("tradition") != tradition:
            continue
        if published_only and not s.get("published"):
            continue

        item_subject = s.get("subject", s.get("intent", "Untitled"))
        if subject and subject.lower() not in item_subject.lower():
            continue

        overall = s.get("final_weighted_total", 0.0)
        if min_score is not None and overall < min_score:
            continue
        if max_score is not None and overall > max_score:
            continue

        scores = s.get("final_scores", {})
        session_id = s.get("session_id", "")
        gallery_items.append({
            "id": session_id,
            "subject": item_subject,
            "tradition": s.get("tradition", "default"),
            "media_type": s.get("media_type", "image"),
            "scores": scores,
            "overall": overall,
            "best_image_url": s.get("best_image_url", ""),
            "total_rounds": s.get("total_rounds", 0),
            "total_latency_ms": s.get("total_latency_ms", 0),
            "created_at": s.get("created_at", 0),
            "likes_count": likes_map.get(session_id, 0),
        })

    # Sort
    sort_key_map = {
        "newest": "created_at",
        "score": "overall",
        "rounds": "total_rounds",
        "likes": "likes_count",
    }
    key_field = sort_key_map.get(sort_by, "created_at")
    reverse = sort_order != "asc"
    gallery_items.sort(key=lambda x: x.get(key_field, 0), reverse=reverse)

    total = len(gallery_items)

    # Paginate
    paginated = gallery_items[offset : offset + limit]

    return {"items": paginated, "total": total}


@router.get("/evolution")
async def get_evolution_stats():
    """Return evolution/digestion statistics for the UI.

    Shows how many sessions the system has learned from, active traditions,
    emerged concepts, and latest evolution timestamp.
    """
    from pathlib import Path

    data_dir = Path(__file__).parent.parent / "data"
    evolved_path = data_dir / "evolved_context.json"

    stats: dict = {
        "total_sessions": 0,
        "traditions_active": [],
        "evolutions_count": 0,
        "emerged_concepts": [],
        "archetypes": [],
        "last_evolved_at": None,
        "agent_insights": {},
        "weight_changes": [],
    }

    # Session count
    from app.prototype.session.store import SessionStore
    store = SessionStore.get()
    stats["total_sessions"] = store.count()

    # Active traditions from sessions
    all_sessions = store.get_all()
    traditions = set()
    for s in all_sessions:
        t = s.get("tradition")
        if t and t != "default":
            traditions.add(t)
    stats["traditions_active"] = sorted(traditions)

    # Evolved context
    if evolved_path.exists():
        try:
            ctx = json.loads(evolved_path.read_text(encoding="utf-8"))
            stats["evolutions_count"] = ctx.get("evolutions", 0)
            stats["last_evolved_at"] = ctx.get("last_evolved_at")

            # Read cultures (emerged concepts from clustering + crystallization)
            cultures = ctx.get("cultures", {})
            stats["emerged_concepts"] = [
                {"name": name, "description": info.get("description", "")}
                for name, info in sorted(
                    cultures.items(),
                    key=lambda x: len(x[1].get("reference_sessions", [])),
                    reverse=True,
                )[:10]
            ]

            # Read prompt archetypes
            archetypes = ctx.get("prompt_contexts", {}).get("archetypes", [])
            stats["archetypes"] = [
                a.get("pattern", "") for a in archetypes[:10]
                if isinstance(a, dict) and a.get("pattern")
            ]

            # Agent insights (short summaries)
            agent_insights = ctx.get("agent_insights", {})
            stats["agent_insights"] = {
                k: v[:120] + "..." if isinstance(v, str) and len(v) > 120 else v
                for k, v in agent_insights.items()
            }

            stats["last_evolved_at"] = ctx.get("last_evolved_at")
        except (json.JSONDecodeError, OSError):
            pass

    return stats


@router.get("/evolution/timeline")
async def get_evolution_timeline():
    """Return cumulative evolution curve data for charting."""
    from pathlib import Path
    import datetime

    data_dir = Path(__file__).parent.parent / "data"
    evolved_path = data_dir / "evolved_context.json"

    result: dict = {"points": [], "total_evolutions": 0, "total_cultures": 0}

    if not evolved_path.exists():
        return result

    try:
        ctx = json.loads(evolved_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return result

    result["total_evolutions"] = ctx.get("evolutions", 0)

    cultures = ctx.get("cultures", {})
    if not cultures:
        return result

    entries: list[tuple[float, str]] = []
    for name, culture in cultures.items():
        emerged_at = culture.get("emerged_at")
        if emerged_at is not None:
            entries.append((float(emerged_at), name))

    if not entries:
        return result

    entries.sort(key=lambda e: e[0])
    result["total_cultures"] = len(entries)

    total_evolutions = result["total_evolutions"]
    points: list[dict] = []
    for idx, (ts, _name) in enumerate(entries, 1):
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        approx_evolutions = round(total_evolutions * idx / len(entries))
        points.append({
            "date": date_str,
            "cultures": idx,
            "evolutions": approx_evolutions,
        })

    result["points"] = points
    return result


# ---------------------------------------------------------------------------
# Traditions management endpoints
# ---------------------------------------------------------------------------

@router.get("/traditions")
async def list_traditions():
    """List all loaded cultural traditions with their metadata."""
    from app.prototype.cultural_pipelines.tradition_loader import (
        get_known_traditions,
        get_tradition,
    )

    traditions = []
    for name in get_known_traditions():
        t = get_tradition(name)
        if t is None:
            continue
        traditions.append({
            "name": name,
            "display_name": t.display_name.get("en", t.name),
            "dimension_count": len(t.weights_l) if t.weights_l else 0,
            "taboo_count": len(t.taboos) if t.taboos else 0,
            "terminology_count": len(t.terminology) if t.terminology else 0,
        })
    return {"traditions": traditions, "total": len(traditions)}


@router.post("/traditions/reload")
async def reload_traditions_endpoint(
    _key: str = Depends(verify_api_key),
):
    """Hot-reload all tradition YAML files without restarting the server.

    Requires Bearer token authentication.
    Useful during development or after adding new tradition definitions.
    """
    from app.prototype.cultural_pipelines.tradition_loader import reload_traditions

    count = reload_traditions()
    return {"reloaded": count, "message": f"Reloaded {count} traditions"}
