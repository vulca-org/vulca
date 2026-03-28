"""VULCA MCP Server v2 -- 6 production-quality tools with view/format params.

Usage:
    vulca-mcp                   # stdio transport (default)
    python -m vulca.mcp_server  # same
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

mcp = FastMCP("VULCA", instructions="AI-native cultural art creation & evaluation")

# Module-level store for HITL sessions pending human action.
# Maps session_id -> PipelineOutput (or similar dict)
_pending_sessions: dict[str, object] = {}

# Dimension display names
_DIM_NAMES: dict[str, str] = {
    "L1": "Visual Perception",
    "L2": "Technical Execution",
    "L3": "Cultural Context",
    "L4": "Critical Interpretation",
    "L5": "Philosophical Aesthetics",
}


def _parse_weights_str(raw: str) -> dict[str, float]:
    """Parse "L1=0.3,L2=0.2,..." into a weights dict.

    Returns empty dict if raw is empty or invalid.
    """
    if not raw or not raw.strip():
        return {}
    weights: dict[str, float] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        key, val = pair.split("=", 1)
        key = key.strip().upper()
        if key in ("L1", "L2", "L3", "L4", "L5"):
            try:
                weights[key] = float(val.strip())
            except ValueError:
                continue
    return weights


def _to_markdown(data: dict, title: str = "") -> str:
    """Convert a result dict to Style A markdown table format."""
    lines: list[str] = []

    if title:
        lines.append(f"## {title}")
        lines.append("")

    # Handle create_artwork detailed response
    if "session_id" in data and "tradition" in data and "weighted_total" in data:
        session_id = data.get("session_id", "")
        status = data.get("status", "")
        tradition = data.get("tradition", "")
        total_rounds = data.get("total_rounds", 0)
        cost_usd = data.get("cost_usd", 0.0)
        weighted_total = data.get("weighted_total", 0.0)
        best_image_url = data.get("best_image_url", "")

        lines.append(f"## VULCA Creation: {session_id}")
        lines.append(
            f"- Status: **{status}** | Tradition: {tradition} | "
            f"Rounds: {total_rounds} | Cost: ${cost_usd:.4f}"
        )
        lines.append("")

        # Scores + rationales table
        scores = data.get("scores", {})
        rationales = data.get("rationales", {})
        if scores:
            lines.append("| Dim | Score | Rationale |")
            lines.append("|-----|-------|-----------|")
            for dim in ("L1", "L2", "L3", "L4", "L5"):
                score_val = scores.get(dim, 0.0)
                rationale = rationales.get(dim, "—") if rationales else "—"
                lines.append(f"| {dim} | {score_val:.2f} | {rationale} |")
            lines.append("")

        lines.append(f"**Weighted Total**: {weighted_total:.2f}")
        if best_image_url:
            lines.append(f"**Image**: {best_image_url}")
        return "\n".join(lines)

    # Handle evaluate_artwork response
    if "score" in data and "tradition" in data and "dimensions" in data:
        score = data.get("score", 0.0)
        tradition = data.get("tradition", "")
        summary = data.get("summary", "")
        dimensions = data.get("dimensions", {})
        rationales = data.get("rationales", {})
        recommendations = data.get("recommendations", [])

        lines.append(f"## VULCA Evaluation")
        lines.append(f"- Tradition: {tradition} | Score: **{score:.2f}**")
        if summary:
            lines.append(f"- Summary: {summary}")
        lines.append("")

        if dimensions:
            lines.append("| Dim | Score | Rationale |")
            lines.append("|-----|-------|-----------|")
            for dim in ("L1", "L2", "L3", "L4", "L5"):
                score_val = dimensions.get(dim, 0.0)
                rationale = rationales.get(dim, "—") if rationales else "—"
                lines.append(f"| {dim} | {score_val:.2f} | {rationale} |")
            lines.append("")

        if recommendations:
            lines.append("**Recommendations**:")
            for rec in recommendations:
                lines.append(f"- {rec}")
        return "\n".join(lines)

    # Generic fallback: just format as key-value pairs
    for key, val in data.items():
        if isinstance(val, dict):
            lines.append(f"**{key}**:")
            for k, v in val.items():
                lines.append(f"  - {k}: {v}")
        elif isinstance(val, list):
            lines.append(f"**{key}**: {', '.join(str(x) for x in val)}")
        else:
            lines.append(f"**{key}**: {val}")
    return "\n".join(lines)


@mcp.tool()
async def create_artwork(
    intent: str,
    tradition: str = "default",
    provider: str = "mock",
    hitl: bool = False,
    weights: str = "",
    mode: str = "strict",
    view: str = "summary",
    format: str = "json",
    sketch_path: str = "",
    reference_path: str = "",
    ref_type: str = "full",
) -> dict | str:
    """Create cultural artwork through the VULCA pipeline.

    Args:
        intent: Natural language description of what to create.
        tradition: Cultural tradition (e.g. chinese_xieyi, western_academic).
            Also accepts a file path to a custom YAML tradition.
        provider: Image generation provider (mock | gemini | nb2 | openai | comfyui).
        hitl: Enable human-in-the-loop (pipeline pauses before decide node).
        weights: Custom L1-L5 weights as string "L1=0.3,L2=0.2,...".
        mode: Evaluation mode — "strict" (judge, default), "reference" (advisor, no forced reruns).
        view: Response verbosity — "summary" (default) or "detailed".
        format: Output format — "json" (default) or "markdown".
        sketch_path: Path or base64 of a sketch image to guide generation.
        reference_path: Path or base64 of a reference image for style/composition guidance.
        ref_type: Reference type — "style", "composition", or "full" (default).

    Returns:
        Summary: session_id, status, tradition, weighted_total, best_image_url, best_candidate_id.
        Detailed adds: scores, rationales, suggestions, rounds, cost_usd, summary, risk_flags.
    """
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import DEFAULT
    from vulca.pipeline.types import PipelineInput

    parsed_weights = _parse_weights_str(weights)

    node_params: dict[str, dict] = {}
    if parsed_weights:
        node_params["evaluate"] = {"custom_weights": parsed_weights}

    pipeline_input = PipelineInput(
        subject=intent,
        intent=intent,
        tradition=tradition,
        provider=provider,
        node_params=node_params,
        eval_mode=mode,
    )

    interrupt_before = {"decide"} if hitl else None

    output = await execute(DEFAULT, pipeline_input, interrupt_before=interrupt_before)

    # Store HITL sessions for resume_artwork
    if output.status == "waiting_human" or output.interrupted_at:
        _pending_sessions[output.session_id] = output

    # Build rationales from events if available (mock may not populate them)
    rationales: dict[str, str] = {}
    for event in output.events:
        if event.event_type.value == "stage_completed" and event.stage == "evaluate":
            raw_rationales = event.payload.get("rationales", {})
            if raw_rationales:
                rationales = raw_rationales
                break

    # Summary view fields
    result: dict = {
        "session_id": output.session_id,
        "status": output.status,
        "tradition": output.tradition,
        "weighted_total": output.weighted_total,
        "best_image_url": output.best_image_url,
        "best_candidate_id": output.best_candidate_id,
        "interrupted_at": output.interrupted_at,
    }

    if view == "detailed":
        result.update({
            "scores": output.final_scores,
            "rationales": rationales,
            "rounds": [r.to_dict() for r in output.rounds],
            "total_rounds": output.total_rounds,
            "cost_usd": output.total_cost_usd,
            "summary": output.summary,
            "risk_flags": output.risk_flags,
            "recommendations": output.recommendations,
        })
    else:
        # Summary still gets cost and rounds count
        result["total_rounds"] = output.total_rounds
        result["cost_usd"] = output.total_cost_usd

    if format == "markdown":
        return _to_markdown(result)
    return result


@mcp.tool()
async def evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
    mock: bool = False,
    mode: str = "strict",
    view: str = "summary",
    format: str = "json",
) -> dict | str:
    """Evaluate artwork on L1-L5 cultural dimensions.

    Args:
        image_path: Path to the image file.
        tradition: Cultural tradition (auto-detected if empty).
            Also accepts a file path to a custom YAML tradition.
        intent: Optional evaluation intent.
        mock: Use mock scoring (no API key required). Useful for testing.
        mode: Evaluation mode — "strict" (judge), "reference" (advisor, no judgment).
        view: Response verbosity — "summary" (default) or "detailed".
        format: Output format — "json" (default) or "markdown".

    Returns:
        Summary: score, tradition, dimensions, suggestions, summary, cost_usd.
        Detailed adds: rationales, recommendations, deviation_types, risk_flags.
    """
    from vulca import aevaluate

    result_obj = await aevaluate(
        image_path, tradition=tradition, intent=intent, mock=mock, mode=mode,
    )

    # Summary fields
    result: dict = {
        "score": result_obj.score,
        "tradition": result_obj.tradition,
        "dimensions": result_obj.dimensions,
        "suggestions": result_obj.suggestions,
        "eval_mode": result_obj.eval_mode,
        "summary": result_obj.summary,
        "cost_usd": result_obj.cost_usd,
    }

    if view == "detailed":
        result.update({
            "rationales": result_obj.rationales,
            "recommendations": result_obj.recommendations,
            "deviation_types": result_obj.deviation_types,
            "risk_flags": result_obj.risk_flags,
            "risk_level": result_obj.risk_level,
        })

    if format == "markdown":
        return _to_markdown(result)
    return result


@mcp.tool()
async def list_traditions(
    view: str = "summary",
    format: str = "json",
) -> dict | str:
    """List available cultural traditions with their L1-L5 weights and emphasis.

    Args:
        view: Response verbosity — "summary" (default) or "detailed".
        format: Output format — "json" (default) or "markdown".

    Returns:
        Dictionary mapping tradition names to weight vectors, emphasis, and description.
    """
    from vulca.cultural.loader import get_all_traditions, get_known_traditions

    traditions_info: dict[str, dict] = {}
    loaded = get_all_traditions()

    dim_names = {
        "L1": "Visual", "L2": "Technical",
        "L3": "Cultural", "L4": "Critical", "L5": "Philosophical",
    }

    if loaded:
        for name, tc in loaded.items():
            # Find emphasis (highest weighted dimension)
            emphasis_dim = max(tc.weights_l, key=tc.weights_l.get) if tc.weights_l else "L3"
            emphasis = dim_names.get(emphasis_dim, emphasis_dim)
            display = tc.display_name.get("en", name.replace("_", " ").title())

            entry: dict = {
                "weights": dict(tc.weights_l),
                "emphasis": emphasis,
                "description": display,
            }
            if view == "detailed":
                entry["terminology_count"] = len(tc.terminology)
                entry["taboos_count"] = len(tc.taboos)
                entry["pipeline_variant"] = tc.pipeline.variant
            traditions_info[name] = entry
    else:
        # Fallback to hardcoded weights
        from vulca.cultural import TRADITION_WEIGHTS
        for name, wts in TRADITION_WEIGHTS.items():
            emphasis_dim = max(wts, key=wts.get) if wts else "L3"
            emphasis = dim_names.get(emphasis_dim, emphasis_dim)
            traditions_info[name] = {
                "weights": dict(wts),
                "emphasis": emphasis,
                "description": name.replace("_", " ").title(),
            }

    result = {"traditions": traditions_info, "count": len(traditions_info)}

    if format == "markdown":
        lines = ["## Available Cultural Traditions", ""]
        lines.append(f"Total: {len(traditions_info)} traditions")
        lines.append("")
        lines.append("| Tradition | Emphasis | L1 | L2 | L3 | L4 | L5 |")
        lines.append("|-----------|----------|----|----|----|----|-----|")
        for name, info in traditions_info.items():
            w = info["weights"]
            lines.append(
                f"| {name} | {info['emphasis']} | "
                f"{w.get('L1', 0):.2f} | {w.get('L2', 0):.2f} | "
                f"{w.get('L3', 0):.2f} | {w.get('L4', 0):.2f} | {w.get('L5', 0):.2f} |"
            )
        return "\n".join(lines)
    return result


@mcp.tool()
async def get_tradition_guide(
    tradition: str,
    view: str = "summary",
    format: str = "json",
) -> dict | str:
    """Get full cultural context guide for a tradition.

    Args:
        tradition: Tradition name (e.g. chinese_xieyi).
        view: Response verbosity — "summary" (default) or "detailed".
        format: Output format — "json" (default) or "markdown".

    Returns:
        Full cultural context: weights, evolved_weights, emphasis, terminology, taboos.
        Returns {"error": "..."} for unknown traditions.
    """
    from vulca.cultural.loader import get_tradition_guide as _get_guide

    guide = _get_guide(tradition)
    if guide is None:
        return {"error": f"Unknown tradition: {tradition!r}. Use list_traditions() to see available traditions."}

    if view == "summary":
        # Summary still includes terminology/taboos (core value of this tool)
        # but truncates long lists
        result = dict(guide)
        if result.get("terminology") and len(result["terminology"]) > 5:
            result["terminology"] = result["terminology"][:5]
        if result.get("taboos") and len(result["taboos"]) > 3:
            result["taboos"] = result["taboos"][:3]
    else:
        result = dict(guide)

    if format == "markdown":
        lines = [f"## Cultural Guide: {tradition}", ""]
        lines.append(f"**Description**: {result.get('description', '')}")
        lines.append(f"**Emphasis**: {result.get('emphasis', '')}")
        lines.append("")
        weights = result.get("weights", {})
        evolved = result.get("evolved_weights")
        lines.append("| Dim | Weight | Evolved |")
        lines.append("|-----|--------|---------|")
        for dim in ("L1", "L2", "L3", "L4", "L5"):
            w = weights.get(dim, 0.0)
            e = evolved.get(dim, "—") if evolved else "—"
            evo_str = f"{e:.2f}" if isinstance(e, float) else str(e)
            lines.append(f"| {dim} | {w:.2f} | {evo_str} |")

        if view == "detailed":
            terminology = result.get("terminology", [])
            if terminology:
                lines.append("")
                lines.append("**Terminology**:")
                for t in terminology[:10]:  # Cap at 10 for readability
                    term = t.get("term", "")
                    defn = t.get("definition", "")
                    lines.append(f"- **{term}**: {defn}")

            taboos = result.get("taboos", [])
            if taboos:
                lines.append("")
                lines.append("**Taboos**:")
                for tb in taboos:
                    lines.append(f"- {tb}")
        return "\n".join(lines)
    return result


@mcp.tool()
async def resume_artwork(
    session_id: str,
    action: str,
    feedback: str = "",
    locked_dimensions: str = "",
    view: str = "summary",
    format: str = "json",
) -> dict | str:
    """Resume a HITL-paused artwork session.

    Args:
        session_id: Session ID from a create_artwork call with hitl=True.
        action: One of "accept", "refine", or "reject".
        feedback: Optional feedback text (used for "refine" to guide rerun).
        locked_dimensions: Comma-separated locked dims for "refine" (e.g. "L3,L5").
        view: Response verbosity — "summary" (default) or "detailed".
        format: Output format — "json" (default) or "markdown".

    Returns:
        Status of the resumed run. "refine" creates a new pipeline run.
        Returns {"error": "..."} for invalid session IDs.
    """
    if session_id not in _pending_sessions:
        result = {"error": f"Session not found: {session_id!r}. Only waiting_human sessions can be resumed."}
        if format == "markdown":
            return f"## Resume Error\n\n**Error**: {result['error']}"
        return result

    pending = _pending_sessions[session_id]

    if action == "reject":
        del _pending_sessions[session_id]
        result = {
            "session_id": session_id,
            "status": "rejected",
            "message": "Session rejected. No further action taken.",
        }
        if format == "markdown":
            return f"## Session Rejected\n\n- Session: `{session_id}`\n- Status: **rejected**"
        return result

    if action == "accept":
        del _pending_sessions[session_id]
        # Return the pending output as completed
        if hasattr(pending, "final_scores"):
            # It's a PipelineOutput
            result = {
                "session_id": session_id,
                "status": "completed",
                "tradition": getattr(pending, "tradition", ""),
                "weighted_total": getattr(pending, "weighted_total", 0.0),
                "best_image_url": getattr(pending, "best_image_url", ""),
                "best_candidate_id": getattr(pending, "best_candidate_id", ""),
                "message": "Session accepted.",
            }
            if view == "detailed":
                result["scores"] = getattr(pending, "final_scores", {})
                result["recommendations"] = getattr(pending, "recommendations", [])
        else:
            result = {
                "session_id": session_id,
                "status": "accepted",
                "message": "Session accepted.",
            }
        if format == "markdown":
            lines = [
                f"## Session Accepted: {session_id}",
                "",
                f"- Status: **completed**",
                f"- Tradition: {result.get('tradition', '')}",
                f"- Weighted Total: {result.get('weighted_total', 0.0):.2f}",
            ]
            if result.get("best_image_url"):
                lines.append(f"- Image: {result['best_image_url']}")
            return "\n".join(lines)
        return result

    if action == "refine":
        # Parse locked dimensions
        locked_dims: list[str] = []
        if locked_dimensions:
            locked_dims = [d.strip().upper() for d in locked_dimensions.split(",") if d.strip()]

        # Get original pipeline input info from pending output
        original_tradition = getattr(pending, "tradition", "default")
        original_provider = "mock"  # Safe default for refine

        # Build refined intent with feedback injected
        original_subject = getattr(pending, "summary", "artwork")
        refined_intent = original_subject
        if feedback:
            refined_intent = f"{original_subject}\n\nRefinement feedback: {feedback}"

        from vulca.pipeline.engine import execute
        from vulca.pipeline.templates import DEFAULT
        from vulca.pipeline.types import PipelineInput

        node_params: dict[str, dict] = {}
        if locked_dims:
            node_params["evaluate"] = {"locked_dimensions": locked_dims}

        pipeline_input = PipelineInput(
            subject=refined_intent,
            intent=refined_intent,
            tradition=original_tradition,
            provider=original_provider,
            node_params=node_params,
        )

        new_output = await execute(DEFAULT, pipeline_input)

        # Remove old pending session
        del _pending_sessions[session_id]

        result = {
            "session_id": new_output.session_id,
            "original_session_id": session_id,
            "status": new_output.status,
            "tradition": new_output.tradition,
            "weighted_total": new_output.weighted_total,
            "best_image_url": new_output.best_image_url,
            "message": "Refinement run created.",
        }
        if view == "detailed":
            result["scores"] = new_output.final_scores
            result["total_rounds"] = new_output.total_rounds
            result["cost_usd"] = new_output.total_cost_usd

        if format == "markdown":
            lines = [
                f"## Refinement Run: {new_output.session_id}",
                f"_(original: {session_id})_",
                "",
                f"- Status: **{new_output.status}**",
                f"- Weighted Total: {new_output.weighted_total:.2f}",
            ]
            if new_output.best_image_url:
                lines.append(f"- Image: {new_output.best_image_url}")
            return "\n".join(lines)
        return result

    # Unknown action
    result = {"error": f"Unknown action: {action!r}. Use 'accept', 'refine', or 'reject'."}
    if format == "markdown":
        return f"## Resume Error\n\n**Error**: {result['error']}"
    return result


@mcp.tool()
async def get_evolution_status(
    tradition: str = "chinese_xieyi",
    view: str = "summary",
    format: str = "json",
) -> dict | str:
    """Get evolution status and weight changes for a tradition.

    Args:
        tradition: Cultural tradition name (default: chinese_xieyi).
        view: Response verbosity — "summary" (default) or "detailed".
        format: Output format — "json" (default) or "markdown".

    Returns:
        tradition, sessions_count, original_weights, evolved_weights, changes, insight.
    """
    from vulca.cultural.loader import (
        _load_evolved_weights,
        get_tradition,
        _DEFAULT_WEIGHTS,
    )

    # Get original YAML weights
    tc = get_tradition(tradition)
    original_weights: dict[str, float]
    if tc:
        original_weights = dict(tc.weights_l)
    else:
        original_weights = dict(_DEFAULT_WEIGHTS)

    # Get evolved weights
    evolved_weights = _load_evolved_weights(tradition)

    # Calculate changes
    changes: dict[str, float] = {}
    if evolved_weights:
        for dim in ("L1", "L2", "L3", "L4", "L5"):
            orig = original_weights.get(dim, 0.0)
            evolved = evolved_weights.get(dim, orig)
            delta = evolved - orig
            if abs(delta) > 0.001:
                changes[dim] = round(delta, 4)

    # Insight text
    insight = ""
    if changes:
        most_changed = max(changes, key=lambda k: abs(changes[k]))
        delta = changes[most_changed]
        direction = "increased" if delta > 0 else "decreased"
        insight = (
            f"{_DIM_NAMES.get(most_changed, most_changed)} ({most_changed}) {direction} "
            f"by {abs(delta):.3f} — indicating evolved aesthetic preference."
        )
    else:
        insight = "No evolution detected — using original YAML weights."

    # Try to get sessions count from evolved context
    sessions_count = 0
    try:
        import json, os
        from pathlib import Path
        loader_path = Path(__file__).resolve()
        candidates = [
            loader_path.parent.parent.parent.parent / "wenxin-backend" / "app" / "prototype" / "data" / "evolved_context.json",
        ]
        env_path = os.environ.get("VULCA_EVOLVED_CONTEXT")
        if env_path:
            candidates.insert(0, Path(env_path))
        for p in candidates:
            if p.is_file():
                with open(p, "r", encoding="utf-8") as f:
                    ctx = json.load(f)
                sessions_count = ctx.get("total_sessions", 0)
                break
    except Exception:
        logging.getLogger("vulca").debug("Failed to load evolved context for evolution status")

    result: dict = {
        "tradition": tradition,
        "sessions_count": sessions_count,
        "original_weights": original_weights,
        "evolved_weights": evolved_weights,
        "has_evolution": evolved_weights is not None,
        "changes": changes,
        "insight": insight,
    }

    if view == "detailed" and tc:
        result["display_name"] = tc.display_name.get("en", tradition)
        result["pipeline_variant"] = tc.pipeline.variant

    if format == "markdown":
        lines = [f"## Evolution Status: {tradition}", ""]
        lines.append(f"- Sessions processed: **{sessions_count}**")
        lines.append(f"- Has evolution: **{'Yes' if evolved_weights else 'No'}**")
        lines.append("")
        lines.append("| Dim | Original | Evolved | Change |")
        lines.append("|-----|----------|---------|--------|")
        for dim in ("L1", "L2", "L3", "L4", "L5"):
            orig = original_weights.get(dim, 0.0)
            evo = evolved_weights.get(dim, orig) if evolved_weights else orig
            delta = changes.get(dim, 0.0)
            delta_str = f"+{delta:.3f}" if delta > 0 else f"{delta:.3f}" if delta != 0 else "—"
            lines.append(f"| {dim} | {orig:.3f} | {evo:.3f} | {delta_str} |")
        lines.append("")
        lines.append(f"**Insight**: {insight}")
        return "\n".join(lines)
    return result


# ── Studio Tools ────────────────────────────────────────────────────


def _format_response(data: dict, fmt: str = "json") -> str:
    """Format a dict as JSON string."""
    import json
    return json.dumps(data, ensure_ascii=False, indent=2)


async def _studio_create_brief_impl(
    intent: str, mood: str = "", project_dir: str = "",
) -> dict:
    """Implementation for studio_create_brief."""
    from pathlib import Path
    from vulca.studio.brief import Brief
    from vulca.studio.phases.intent import IntentPhase

    b = Brief.new(intent, mood=mood)
    phase = IntentPhase()
    phase.parse_intent(b)

    if project_dir:
        b.save(Path(project_dir))

    return {
        "session_id": b.session_id,
        "intent": b.intent,
        "mood": b.mood,
        "style_mix": [{"tradition": s.tradition, "tag": s.tag, "weight": s.weight} for s in b.style_mix],
        "project_dir": project_dir,
    }


async def _studio_update_brief_impl(
    project_dir: str, instruction: str,
) -> dict:
    """Implementation for studio_update_brief."""
    from pathlib import Path
    from vulca.studio.brief import Brief
    from vulca.studio.nl_update import parse_nl_update, apply_update

    b = Brief.load(Path(project_dir))
    result = parse_nl_update(instruction, b)
    apply_update(b, result)
    b.save(Path(project_dir))

    return {
        "rollback_to": result.rollback_to.value,
        "field_updates": {k: str(v) for k, v in result.field_updates.items()},
        "explanation": result.explanation,
    }


async def _studio_generate_concepts_impl(
    project_dir: str, count: int = 4, provider: str = "mock",
) -> dict:
    """Implementation for studio_generate_concepts."""
    from pathlib import Path
    from vulca.studio.brief import Brief
    from vulca.studio.phases.concept import ConceptPhase

    b = Brief.load(Path(project_dir))
    phase = ConceptPhase()
    paths = await phase.generate_concepts(b, count=count, provider=provider, project_dir=project_dir)
    b.save(Path(project_dir))

    return {"concepts": paths, "count": len(paths)}


async def _studio_select_concept_impl(
    project_dir: str, index: int, notes: str = "",
) -> dict:
    """Implementation for studio_select_concept."""
    from pathlib import Path
    from vulca.studio.brief import Brief
    from vulca.studio.phases.concept import ConceptPhase

    b = Brief.load(Path(project_dir))
    phase = ConceptPhase()
    phase.select(b, index=index - 1, notes=notes)  # User-facing 1-based
    b.save(Path(project_dir))

    return {"selected": b.selected_concept, "notes": b.concept_notes}


# Register MCP tools
@mcp.tool()
async def studio_create_brief(
    intent: str,
    mood: str = "",
    project_dir: str = "",
) -> str:
    """Create a new Studio creative brief.

    Args:
        intent: Creative vision description (e.g., "赛博朋克水墨山水")
        mood: Emotional target (e.g., "epic-solitary", "serene", "mystical")
        project_dir: Directory to save brief (optional)
    """
    result = await _studio_create_brief_impl(intent, mood, project_dir)
    return _format_response(result, "json")


@mcp.tool()
async def studio_update_brief(
    project_dir: str,
    instruction: str,
) -> str:
    """Update a Brief with natural language instruction.

    Args:
        project_dir: Path to project directory containing brief.yaml
        instruction: Natural language update (e.g., "把山改成更高更陡的")
    """
    result = await _studio_update_brief_impl(project_dir, instruction)
    return _format_response(result, "json")


@mcp.tool()
async def studio_generate_concepts(
    project_dir: str,
    count: int = 4,
    provider: str = "mock",
) -> str:
    """Generate concept design images from a Brief.

    Args:
        project_dir: Path to project with brief.yaml
        count: Number of concepts (default 4)
        provider: Image provider (mock, gemini, openai)
    """
    result = await _studio_generate_concepts_impl(project_dir, count, provider)
    return _format_response(result, "json")


@mcp.tool()
async def studio_select_concept(
    project_dir: str,
    index: int,
    notes: str = "",
) -> str:
    """Select a concept and optionally add refinement notes.

    Args:
        project_dir: Path to project with brief.yaml
        index: Concept number to select (1-based)
        notes: Optional refinement notes (e.g., "mountain taller")
    """
    result = await _studio_select_concept_impl(project_dir, index, notes)
    return _format_response(result, "json")


async def _studio_accept_impl(project_dir: str) -> dict:
    """Implementation for studio_accept."""
    from vulca.studio.session import StudioSession
    session = StudioSession.load(project_dir)
    return await session.accept(data_dir=project_dir)


@mcp.tool()
async def studio_accept(
    project_dir: str,
) -> str:
    """Accept the current artwork and finalize the Studio session.

    Saves session data and triggers digestion (signal extraction).

    Args:
        project_dir: Path to project with brief.yaml and session.yaml
    """
    result = await _studio_accept_impl(project_dir)
    return _format_response(result, "json")


if __name__ == "__main__":
    mcp.run()
