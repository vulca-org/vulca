"""VULCA MCP Server v2 -- agent-native tools returning full structured JSON.

Usage:
    vulca-mcp                   # stdio transport (default)
    python -m vulca.mcp_server  # same
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

mcp = FastMCP("VULCA", instructions="AI-native cultural art creation & evaluation")

# Auto-register Tool Protocol tools (whitespace_analyze, color_correct, etc.)
try:
    from vulca.tools.registry import ToolRegistry
    from vulca.tools.adapters.mcp import register_tools_on_mcp
    _tool_registry = ToolRegistry()
    _tool_registry.discover()
    register_tools_on_mcp(mcp, _tool_registry)
except ImportError:
    pass


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


_TOOL_TIERS: dict[str, str] = {
    "create_artwork": "core", "evaluate_artwork": "core",
    "list_traditions": "core", "get_tradition_guide": "core",
    "studio_create_brief": "core",
    "inpaint_artwork": "standard",
    "sync_data": "standard", "studio_generate_concepts": "standard",
    "studio_accept": "standard",
    "layers_split": "standard", "layers_composite": "standard",
    "layers_edit": "advanced", "layers_redraw": "advanced",
    "layers_evaluate": "advanced",
    "layers_export": "advanced",
    "generate_image": "core",
    "view_image": "core",
    "layers_list": "standard",
}

_DESC_LIMITS: dict[str, int] = {"core": 300, "standard": 100, "advanced": 50}


def _tier_description(tool_name: str, full_desc: str) -> str:
    """Truncate tool description based on tier assignment."""
    tier = _TOOL_TIERS.get(tool_name, "advanced")
    limit = _DESC_LIMITS[tier]
    if len(full_desc) <= limit:
        return full_desc
    return full_desc[:limit - 3] + "..."


@mcp.tool()
async def create_artwork(
    intent: str,
    tradition: str = "default",
    provider: str = "mock",
    hitl: bool = False,
    weights: str = "",
    mode: str = "strict",
    reference_path: str = "",
    ref_type: str = "full",
    layered: bool = False,
) -> dict:
    """Create cultural artwork through the VULCA pipeline.

    When layered=True: generates independent layers (plan + generate only).
    The agent should review each layer visually, then use layers_composite
    and layers_redraw to compose the final artwork with user participation.

    Args:
        intent: Natural language description of what to create.
        tradition: Cultural tradition (e.g. chinese_xieyi, western_academic).
            Also accepts a file path to a custom YAML tradition.
        provider: Image generation provider (mock | gemini | nb2 | openai | comfyui).
        hitl: Enable human-in-the-loop (pipeline pauses before decide node).
        weights: Custom L1-L5 weights as string "L1=0.3,L2=0.2,...".
        mode: Evaluation mode — "strict" (judge, default), "reference" (advisor, no forced reruns).
        reference_path: Path or base64 of a reference image for style/composition guidance.
            Also serves as sketch input -- providers treat both identically.
        ref_type: Reference type — "style", "composition", or "full" (default).
        layered: Generate structured layers instead of flat image.
            Returns artifact.json + per-layer PNGs. Agent orchestrates composition.

    Returns:
        Full result: session_id, status, tradition, weighted_total, best_image_url,
        best_candidate_id, scores, rationales, rounds, cost_usd, summary, risk_flags,
        recommendations.
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
        layered=layered,
    )

    if hitl and layered:
        import logging
        logging.getLogger("vulca.mcp").warning(
            "hitl=True ignored with layered=True — agent orchestrates iteration via MCP tools"
        )
    interrupt_before = {"decide"} if (hitl and not layered) else None

    if layered:
        from vulca.pipeline.templates import LAYERED
        template = LAYERED
    else:
        template = DEFAULT
    output = await execute(template, pipeline_input, interrupt_before=interrupt_before)

    # Build rationales from events if available (mock may not populate them)
    rationales: dict[str, str] = {}
    for event in output.events:
        if event.event_type.value == "stage_completed" and event.stage == "evaluate":
            raw_rationales = event.payload.get("rationales", {})
            if raw_rationales:
                rationales = raw_rationales
                break

    result: dict = {
        "session_id": output.session_id,
        "status": output.status,
        "tradition": output.tradition,
        "weighted_total": output.weighted_total,
        "best_image_url": output.best_image_url,
        "best_candidate_id": output.best_candidate_id,
        "interrupted_at": output.interrupted_at,
        "scores": output.final_scores,
        "rationales": rationales,
        "rounds": [r.to_dict() for r in output.rounds],
        "total_rounds": output.total_rounds,
        "cost_usd": output.total_cost_usd,
        "summary": output.summary,
        "risk_flags": output.risk_flags,
        "recommendations": output.recommendations,
    }
    return result


@mcp.tool()
async def evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
    mock: bool = False,
    mode: str = "strict",
) -> dict:
    """Evaluate artwork on L1-L5 cultural dimensions.

    Args:
        image_path: Path to the image file.
        tradition: Cultural tradition (auto-detected if empty).
            Also accepts a file path to a custom YAML tradition.
        intent: Optional evaluation intent.
        mock: Use mock scoring (no API key required). Useful for testing.
        mode: Evaluation mode — "strict" (judge), "reference" (advisor, no judgment).

    Returns:
        Full result: score, tradition, dimensions, suggestions, summary, cost_usd,
        rationales, recommendations, deviation_types, risk_flags, risk_level.
    """
    from vulca import aevaluate

    result_obj = await aevaluate(
        image_path, tradition=tradition, intent=intent, mock=mock, mode=mode,
    )

    result: dict = {
        "score": result_obj.score,
        "tradition": result_obj.tradition,
        "dimensions": result_obj.dimensions,
        "suggestions": result_obj.suggestions,
        "eval_mode": result_obj.eval_mode,
        "summary": result_obj.summary,
        "cost_usd": result_obj.cost_usd,
        "rationales": result_obj.rationales,
        "recommendations": result_obj.recommendations,
        "deviation_types": result_obj.deviation_types,
        "risk_flags": result_obj.risk_flags,
        "risk_level": result_obj.risk_level,
    }
    return result


@mcp.tool()
async def list_traditions() -> dict:
    """List available cultural traditions with their L1-L5 weights and emphasis.

    Returns:
        Dictionary mapping tradition names to weight vectors, emphasis, description,
        terminology_count, taboos_count, pipeline_variant.
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

            traditions_info[name] = {
                "weights": dict(tc.weights_l),
                "emphasis": emphasis,
                "description": display,
                "terminology_count": len(tc.terminology),
                "taboos_count": len(tc.taboos),
                "pipeline_variant": tc.pipeline.variant,
            }
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

    return {"traditions": traditions_info, "count": len(traditions_info)}


@mcp.tool()
async def get_tradition_guide(
    tradition: str,
) -> dict:
    """Get full cultural context guide for a tradition.

    Args:
        tradition: Tradition name (e.g. chinese_xieyi).

    Returns:
        Full cultural context: weights, evolved_weights, emphasis, terminology, taboos.
        Returns {"error": "..."} for unknown traditions.
    """
    from vulca.cultural.loader import get_tradition_guide as _get_guide

    guide = _get_guide(tradition)
    if guide is None:
        return {"error": f"Unknown tradition: {tradition!r}. Use list_traditions() to see available traditions."}

    return dict(guide)





# ── Studio Tools ────────────────────────────────────────────────────


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


# Register MCP tools
@mcp.tool()
async def studio_create_brief(
    intent: str,
    mood: str = "",
    project_dir: str = "",
) -> dict:
    """Create a new Studio creative brief.

    Args:
        intent: Creative vision description (e.g., "赛博朋克水墨山水")
        mood: Emotional target (e.g., "epic-solitary", "serene", "mystical")
        project_dir: Directory to save brief (optional)
    """
    return await _studio_create_brief_impl(intent, mood, project_dir)


@mcp.tool()
async def studio_generate_concepts(
    project_dir: str,
    count: int = 4,
    provider: str = "mock",
) -> dict:
    """Generate concept design images from a Brief.

    Args:
        project_dir: Path to project with brief.yaml
        count: Number of concepts (default 4)
        provider: Image provider (mock, gemini, openai)
    """
    return await _studio_generate_concepts_impl(project_dir, count, provider)


async def _studio_accept_impl(project_dir: str) -> dict:
    """Implementation for studio_accept."""
    from vulca.studio.session import StudioSession
    session = StudioSession.load(project_dir)
    return await session.accept(data_dir=project_dir)


@mcp.tool()
async def studio_accept(
    project_dir: str,
) -> dict:
    """Accept the current artwork and finalize the Studio session.

    Saves session data and triggers digestion (signal extraction).

    Args:
        project_dir: Path to project with brief.yaml and session.yaml
    """
    return await _studio_accept_impl(project_dir)


@mcp.tool()
async def inpaint_artwork(
    image_path: str,
    region: str,
    instruction: str,
    tradition: str = "default",
) -> dict:
    """Repaint a region of an artwork. Returns a single result per call.

    Args:
        image_path: Path to the image file.
        region: NL description ("fix the sky") or coordinates ("0,0,100,35").
        instruction: What to change in the region.
        tradition: Cultural tradition for style consistency.
    """
    from vulca.inpaint import ainpaint

    result = await ainpaint(
        image_path,
        region=region,
        instruction=instruction,
        tradition=tradition,
        count=1,
        select=0,
    )
    return {
        "image_path": result.blended,
        "bbox": result.bbox,
        "cost_usd": result.cost_usd,
        "latency_ms": result.latency_ms,
    }



@mcp.tool()
async def layers_split(
    image_path: str,
    output_dir: str = "",
    mode: str = "regenerate",
    provider: str = "gemini",
    tradition: str = "default",
) -> dict:
    """Split an image into full-canvas RGBA layers.

    Args:
        image_path: Path to the image file.
        output_dir: Output directory (default: image parent/layers).
        mode: Split mode — "regenerate" (img2img), "extract" (color-range), "vlm" (VLM masks), or "sam3" (SAM3 text-prompted, GPU).
        provider: Image provider for regenerate mode.
        tradition: Cultural tradition for styling.

    Returns:
        layers list, manifest_path, split_mode.
    """
    from vulca.layers.analyze import analyze_layers as _analyze
    from vulca.layers.split import split_extract, split_regenerate
    from pathlib import Path

    layers = await _analyze(image_path)
    out = output_dir or str(Path(image_path).parent / "layers")

    if mode == "extract":
        results = split_extract(image_path, layers, output_dir=out)
    elif mode == "vlm":
        from vulca.layers.split import split_vlm
        results = await split_vlm(
            image_path, layers, output_dir=out,
            provider=provider,
        )
    elif mode == "sam3":
        from vulca.layers.sam3 import sam3_split
        results = sam3_split(
            image_path, layers, output_dir=out,
        )
    else:
        results = await split_regenerate(
            image_path, layers, output_dir=out,
            provider=provider, tradition=tradition,
        )

    return {
        "split_mode": mode,
        "manifest_path": str(Path(out) / "manifest.json"),
        "layers": [
            {
                "name": r.info.name,
                "file": r.image_path,
                "z_index": r.info.z_index,
                "content_type": r.info.content_type,
                "blend_mode": r.info.blend_mode,
            }
            for r in results
        ],
    }


@mcp.tool()
async def layers_redraw(
    artwork_dir: str,
    layer: str = "",
    layers: str = "",
    instruction: str = "",
    merge: bool = False,
    merged_name: str = "merged",
    provider: str = "gemini",
    tradition: str = "default",
) -> dict:
    """Redraw layer(s) via img2img with specific instructions.

    Be specific about position, scale, and style in the instruction:
    - Position: "upper 30% of canvas", "right third", "centered"
    - Scale: "smaller, covering 20% of canvas", "larger with more detail"
    - Style: "lighter ink wash", "bold strokes", "flat color block"
    - Content: "only mountains, nothing else", "add a boat on the river"

    Args:
        artwork_dir: Directory with layer PNGs + manifest.
        layer: Single layer name to redraw.
        layers: Comma-separated layer names to merge+redraw.
        instruction: What to change.
        merge: If true, merge selected layers before redraw.
        merged_name: Name for merged output layer.
        provider: Image provider.
        tradition: Cultural tradition.

    Returns:
        Redrawn layer info with file path.
    """
    from vulca.layers.manifest import load_manifest
    from vulca.layers.redraw import redraw_layer, redraw_merged

    artwork = load_manifest(artwork_dir)

    if layers and merge:
        layer_names = [n.strip() for n in layers.split(",")]
        result = await redraw_merged(
            artwork, layer_names=layer_names,
            instruction=instruction, merged_name=merged_name,
            provider=provider, tradition=tradition,
            artwork_dir=artwork_dir,
        )
    elif layer:
        result = await redraw_layer(
            artwork, layer_name=layer,
            instruction=instruction, provider=provider,
            tradition=tradition, artwork_dir=artwork_dir,
        )
    else:
        return {"error": "Specify 'layer' or 'layers' with merge=true"}

    return {
        "name": result.info.name,
        "file": result.image_path,
        "z_index": result.info.z_index,
        "content_type": result.info.content_type,
    }


@mcp.tool()
async def layers_edit(
    artwork_dir: str,
    operation: str,
    layer: str = "",
    layers: str = "",
    name: str = "",
    description: str = "",
    z_index: int = -1,
    content_type: str = "subject",
    semantic_path: str = "",
    visible: bool = True,
    locked: bool = True,
) -> dict:
    """Edit layers — add, remove, reorder, toggle, lock, merge, duplicate.

    Args:
        artwork_dir: Directory with layer PNGs + manifest.
        operation: One of: add, remove, reorder, toggle, lock, merge, duplicate.
        layer: Layer name (for remove/reorder/toggle/lock/duplicate).
        layers: Comma-separated layer names (for merge).
        name: New layer name (for add/merge/duplicate).
        description: Layer description (for add).
        z_index: Z-index (for add/reorder, -1 = top).
        content_type: Layer role label (e.g. background, subject, ui_header, decoration).
        semantic_path: Hierarchical dot-notation label (e.g. 'subject.face.eyes'), "" if none.
        visible: Visibility state (for toggle).
        locked: Lock state (for lock).

    Returns:
        Operation result with updated layer info.
    """
    from vulca.layers.manifest import load_manifest
    from vulca.layers.ops import (
        add_layer, remove_layer, reorder_layer, toggle_visibility,
        lock_layer, merge_layers, duplicate_layer,
    )

    artwork = load_manifest(artwork_dir)

    if operation == "add":
        result = add_layer(artwork, artwork_dir=artwork_dir, name=name,
                          description=description, z_index=z_index,
                          content_type=content_type,
                          semantic_path=semantic_path)
        return {
            "operation": "add",
            "name": result.info.name,
            "z_index": result.info.z_index,
            "semantic_path": result.info.semantic_path,
        }

    elif operation == "remove":
        remove_layer(artwork, artwork_dir=artwork_dir, layer_name=layer)
        return {"operation": "remove", "removed": layer}

    elif operation == "reorder":
        reorder_layer(artwork, artwork_dir=artwork_dir, layer_name=layer, new_z_index=z_index)
        return {"operation": "reorder", "layer": layer, "new_z_index": z_index}

    elif operation == "toggle":
        toggle_visibility(artwork, artwork_dir=artwork_dir, layer_name=layer, visible=visible)
        return {"operation": "toggle", "layer": layer, "visible": visible}

    elif operation == "lock":
        lock_layer(artwork, artwork_dir=artwork_dir, layer_name=layer, locked=locked)
        return {"operation": "lock", "layer": layer, "locked": locked}

    elif operation == "merge":
        layer_names = [n.strip() for n in layers.split(",")]
        result = merge_layers(artwork, artwork_dir=artwork_dir,
                             layer_names=layer_names, merged_name=name or "merged")
        return {"operation": "merge", "merged": result.info.name, "source": layer_names}

    elif operation == "duplicate":
        result = duplicate_layer(artwork, artwork_dir=artwork_dir,
                                layer_name=layer, new_name=name)
        return {"operation": "duplicate", "source": layer, "new": result.info.name}

    else:
        return {"error": f"Unknown operation: {operation}. Use: add/remove/reorder/toggle/lock/merge/duplicate"}


@mcp.tool()
async def layers_transform(
    artwork_dir: str,
    layer: str,
    dx: float = 0.0,
    dy: float = 0.0,
    scale: float = 1.0,
    rotate: float = 0.0,
    opacity: float = -1.0,
) -> dict:
    """Transform a layer — move, scale, rotate, change opacity.

    Args:
        artwork_dir: Directory with layer PNGs + manifest.
        layer: Layer name to transform.
        dx: Move X by this percentage (relative, e.g. 10 = move right 10%).
        dy: Move Y by this percentage (relative, e.g. -5 = move up 5%).
        scale: Scale factor (1.0 = no change, 0.5 = half size, 2.0 = double).
        rotate: Rotate by degrees (relative, clockwise).
        opacity: Set opacity (0.0-1.0). Use -1 to keep current value.

    Returns:
        Updated layer spatial info.
    """
    from vulca.layers.manifest import load_manifest
    from vulca.layers.ops import transform_layer

    artwork = load_manifest(artwork_dir)
    set_opacity = opacity if opacity >= 0 else None
    transform_layer(
        artwork, artwork_dir=artwork_dir, layer_name=layer,
        dx=dx, dy=dy, scale=scale, rotate=rotate, set_opacity=set_opacity,
    )

    layer_result = next(lr for lr in artwork.layers if lr.info.name == layer)
    return {
        "status": "ok",
        "layer": layer,
        "x": layer_result.info.x,
        "y": layer_result.info.y,
        "width": layer_result.info.width,
        "height": layer_result.info.height,
        "rotation": layer_result.info.rotation,
        "opacity": layer_result.info.opacity,
    }


@mcp.tool()
async def sync_data(push_only: bool = False, pull_only: bool = False) -> dict:
    """Sync local session data with cloud. Requires VULCA_API_URL env var.

    Args:
        push_only: Only push local sessions, skip pulling evolved weights.
        pull_only: Only pull evolved weights, skip pushing sessions.

    Returns:
        pushed_count, pulled_evolved (bool), api_url, error (if any).
    """
    import json as json_mod
    import os
    from pathlib import Path

    api_url = os.environ.get("VULCA_API_URL", "")
    api_key = os.environ.get("VULCA_API_KEY", "")
    if not api_url:
        return {
            "error": "VULCA_API_URL not set. "
            "Set VULCA_API_URL and optionally VULCA_API_KEY env vars.",
        }

    data_dir = Path.home() / ".vulca" / "data"
    pushed_count = 0
    pulled_evolved = False

    if not pull_only:
        sessions_file = data_dir / "sessions.jsonl"
        synced_file = data_dir / "synced.json"

        synced_ids: set[str] = set()
        if synced_file.exists():
            synced_ids = set(json_mod.loads(synced_file.read_text()))

        to_push: list[dict] = []
        if sessions_file.exists():
            for line in sessions_file.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json_mod.loads(line)
                    sid = entry.get("session_id", "")
                    if sid and sid not in synced_ids:
                        to_push.append(entry)
                        synced_ids.add(sid)
                except json_mod.JSONDecodeError:
                    continue

        if to_push:
            try:
                import httpx
                resp = httpx.post(
                    f"{api_url.rstrip('/')}/api/v1/sync",
                    json={"sessions": to_push},
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30,
                )
                resp.raise_for_status()
                synced_file.parent.mkdir(parents=True, exist_ok=True)
                synced_file.write_text(json_mod.dumps(sorted(synced_ids)))
                pushed_count = len(to_push)
            except Exception as exc:
                return {"error": f"Push failed: {exc}", "api_url": api_url}

    if not push_only:
        try:
            import httpx
            resp = httpx.get(
                f"{api_url.rstrip('/')}/api/v1/evolved-context",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            resp.raise_for_status()
            evolved_path = data_dir / "evolved_context.json"
            evolved_path.parent.mkdir(parents=True, exist_ok=True)
            evolved_path.write_text(resp.text)
            pulled_evolved = True
        except Exception as exc:
            return {
                "error": f"Pull failed: {exc}",
                "api_url": api_url,
                "pushed_count": pushed_count,
            }

    return {
        "api_url": api_url,
        "pushed_count": pushed_count,
        "pulled_evolved": pulled_evolved,
    }


@mcp.tool()
async def layers_composite(artwork_dir: str, output_path: str = "") -> dict:
    """Composite layers from an artwork directory into a single flat image.

    After compositing, review the result visually. If composition needs adjustment,
    use layers_redraw to modify individual layers, then re-composite.

    Args:
        artwork_dir: Directory containing layer PNGs and manifest.json.
        output_path: Output file path (default: <artwork_dir>/composite.png).

    Returns:
        composite_path: Absolute path to the composited image.
    """
    import json as json_mod
    from pathlib import Path
    from vulca.layers.edit import load_artwork
    from vulca.layers.composite import composite_layers as _composite

    artwork = load_artwork(artwork_dir)
    out = output_path or str(Path(artwork_dir) / "composite.png")

    # Read width/height from manifest if available
    manifest_path = Path(artwork_dir) / "manifest.json"
    width = height = 1024
    if manifest_path.exists():
        try:
            m = json_mod.loads(manifest_path.read_text())
            width = m.get("width", 1024)
            height = m.get("height", 1024)
        except Exception:
            pass

    _composite(artwork.layers, width=width, height=height, output_path=out)

    # Also write artifact.json for the LAYERED pipeline
    try:
        from vulca.layers.artifact import write_artifact_v3
        art_dir = Path(artwork_dir)
        write_artifact_v3(
            layers=[lr.info for lr in artwork.layers],
            output_dir=str(art_dir),
            width=width, height=height,
            composite_file=Path(out).name,
        )
    except Exception:
        pass  # Artifact writing is optional

    return {"composite_path": out}


@mcp.tool()
async def layers_export(
    artwork_dir: str,
    format: str = "png",
    output_path: str = "",
) -> dict:
    """Export layers as PNG directory or PSD file.

    Args:
        artwork_dir: Directory containing layer PNGs and manifest.json.
        format: Export format — "png" (default, PNG directory) or "psd".
        output_path: Output path (default: <artwork_dir>/export.<format>).

    Returns:
        export_path: Absolute path to exported file or directory.
    """
    import json as json_mod
    from pathlib import Path
    from vulca.layers.edit import load_artwork
    from vulca.layers.export import export_psd
    from vulca.layers.composite import composite_layers

    artwork = load_artwork(artwork_dir)

    # Read width/height from manifest if available
    manifest_path = Path(artwork_dir) / "manifest.json"
    width = height = 1024
    if manifest_path.exists():
        try:
            m = json_mod.loads(manifest_path.read_text())
            width = m.get("width", 1024)
            height = m.get("height", 1024)
        except Exception:
            pass

    if format == "psd":
        out = output_path or str(Path(artwork_dir) / "layers.psd")
        export_psd(artwork.layers, width=width, height=height, output_path=out)
    else:
        out = output_path or str(Path(artwork_dir) / "composite.png")
        composite_layers(artwork.layers, width=width, height=height, output_path=out)

    return {"export_path": out}


@mcp.tool()
async def layers_evaluate(
    artwork_dir: str,
    tradition: str = "default",
) -> dict:
    """Evaluate each layer independently with L1-L5 scoring.

    Args:
        artwork_dir: Directory containing layer PNGs and manifest.json.
        tradition: Cultural tradition for evaluation (default: auto-detect).

    Returns:
        layers: Dict mapping layer name to score and dimensions.
    """
    from vulca.layers.edit import load_artwork
    from vulca import aevaluate

    artwork = load_artwork(artwork_dir)
    results: dict[str, dict] = {}

    for layer in artwork.layers:
        try:
            r = await aevaluate(layer.image_path, tradition=tradition)
            results[layer.info.name] = {
                "score": r.score,
                "dimensions": r.dimensions,
            }
        except Exception as exc:
            results[layer.info.name] = {"error": str(exc)}

    return {"layers": results}


# ── Agent-Native Atomic Tools ─────────────────────────────────────


@mcp.tool()
async def generate_image(
    prompt: str,
    provider: str = "gemini",
    tradition: str = "default",
    reference_path: str = "",
    output_dir: str = "",
) -> dict:
    """Generate a single image from a text prompt — no evaluation, no loop.

    Use after get_tradition_guide for cultural context. Then use view_image to inspect
    and evaluate_artwork to score the result.

    Args:
        prompt: Text description of the image to generate.
        provider: Image generation provider (gemini | openai | comfyui | mock).
        tradition: Cultural tradition for prompt enrichment.
        reference_path: Optional reference/sketch image path.
        output_dir: Directory to save the generated image.

    Returns:
        image_path: Path to the generated PNG.
        cost_usd: Generation cost.
        latency_ms: Generation time in milliseconds.
        provider: Provider used.
    """
    import base64
    import time
    import uuid
    from pathlib import Path

    from vulca.providers import get_image_provider

    t0 = time.monotonic()

    prov = get_image_provider(provider)

    ref_b64 = ""
    if reference_path:
        ref_file = Path(reference_path)
        if not ref_file.exists():
            return {"error": f"Reference image not found: {reference_path}"}
        ref_b64 = base64.b64encode(ref_file.read_bytes()).decode()

    result = await prov.generate(
        prompt,
        tradition=tradition,
        subject=prompt,
        reference_image_b64=ref_b64,
    )

    elapsed_ms = round((time.monotonic() - t0) * 1000)

    # Save to disk
    out = Path(output_dir) if output_dir else Path.cwd()
    out.mkdir(parents=True, exist_ok=True)
    filename = f"gen_{uuid.uuid4().hex[:8]}.png"
    image_path = out / filename
    image_path.write_bytes(base64.b64decode(result.image_b64))

    cost = 0.0
    if result.metadata:
        cost = result.metadata.get("cost_usd", 0.0)

    return {
        "image_path": str(image_path),
        "cost_usd": cost,
        "latency_ms": elapsed_ms,
        "provider": provider,
    }


@mcp.tool()
async def view_image(
    image_path: str,
    max_dimension: int = 1024,
) -> dict:
    """View an image — returns base64-encoded thumbnail for agent inspection.

    Use after generate_image or layers_composite to visually inspect results.

    Args:
        image_path: Path to the image file.
        max_dimension: Maximum width/height in pixels. Default 1024.

    Returns:
        image_base64: Base64-encoded PNG.
        width: Thumbnail width.
        height: Thumbnail height.
        original_width: Original width.
        original_height: Original height.
        file_size_bytes: File size.
    """
    import base64
    import io
    from pathlib import Path

    from PIL import Image

    p = Path(image_path)
    if not p.exists():
        return {"error": f"Image not found: {image_path}"}

    file_size = p.stat().st_size

    img = Image.open(p)
    original_width, original_height = img.size

    img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    thumb_w, thumb_h = img.size

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "image_base64": b64,
        "width": thumb_w,
        "height": thumb_h,
        "original_width": original_width,
        "original_height": original_height,
        "file_size_bytes": file_size,
    }


@mcp.tool()
async def layers_list(artwork_dir: str) -> dict:
    """List all layers in an artwork directory with metadata.

    Returns structured inventory: name, z_index, content_type, visibility,
    blend_mode, and whether each layer's PNG file exists.

    Args:
        artwork_dir: Path to artwork directory with manifest.json.

    Returns:
        layers: List of layer metadata dicts.
        layer_count: Total layers.
        visible_count: Visible layers.
        has_composite: Whether composite.png exists.
    """
    import json as json_mod
    from pathlib import Path

    d = Path(artwork_dir)
    manifest_path = d / "manifest.json"

    if not manifest_path.exists():
        return {"error": f"No manifest.json in {artwork_dir}"}

    try:
        manifest = json_mod.loads(manifest_path.read_text())
    except Exception as exc:
        return {"error": f"Failed to read manifest: {exc}"}

    layers_out = []
    visible_count = 0
    for item in manifest.get("layers", []):
        name = item.get("name", "")
        visible = item.get("visible", True)
        png_file = item.get("file", f"{name}.png")
        png_exists = (d / png_file).exists()

        if visible:
            visible_count += 1

        layers_out.append({
            "name": name,
            "z_index": item.get("z_index", 0),
            "content_type": item.get("content_type", ""),
            "visible": visible,
            "blend_mode": item.get("blend_mode", "normal"),
            "locked": item.get("locked", False),
            "opacity": item.get("opacity", 1.0),
            "semantic_path": item.get("semantic_path", ""),
            "file": png_file,
            "file_exists": png_exists,
        })

    has_composite = (d / "composite.png").exists()

    return {
        "layers": layers_out,
        "layer_count": len(layers_out),
        "visible_count": visible_count,
        "has_composite": has_composite,
    }



if __name__ == "__main__":
    mcp.run()
