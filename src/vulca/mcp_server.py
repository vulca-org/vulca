"""VULCA MCP Server — agent-native surface for cultural art creation, evaluation, and layer editing.

21 tools (including unload_models admin/diagnostic) organized into five workflow stages:
  1. Discovery:    list_traditions, search_traditions, get_tradition_guide, brief_parse
  2. Generation:   generate_image, create_artwork, generate_concepts, inpaint_artwork
  3. Evaluation:   evaluate_artwork, view_image
  4. Layer editing: layers_split, layers_list, layers_edit, layers_transform,
                    layers_redraw, layers_composite, layers_export, layers_evaluate
  5. Session:      archive_session, sync_data, unload_models

Typical agent loop: brief_parse → get_tradition_guide → generate_image → view_image
  → evaluate_artwork → (layers_split → layers_edit/redraw → layers_composite) → archive_session

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
    "search_traditions": "core",
    "brief_parse": "core",
    "inpaint_artwork": "standard",
    "sync_data": "standard", "generate_concepts": "standard",
    "archive_session": "standard",
    # unload_models: out-of-band admin/diagnostic (memory free); grouped with sync_data tier
    "unload_models": "standard",
    "layers_split": "standard", "layers_composite": "standard",
    "layers_edit": "advanced", "layers_redraw": "advanced",
    "layers_evaluate": "advanced",
    "layers_export": "advanced",
    "layers_transform": "advanced",
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
    weights: str = "",
    reference_path: str = "",
) -> dict:
    """Generate and evaluate an image in one call — convenience wrapper over generate_image + evaluate_artwork.

    Returns image + L1-L5 scores in a single round-trip. For fine-grained control
    (retry loop, custom prompts, separate scoring), use generate_image and evaluate_artwork separately.

    Args:
        intent: Natural language description of what to create.
        tradition: Cultural tradition (e.g. chinese_xieyi, western_academic) or path to custom YAML.
        provider: Image generation provider (mock | gemini | nb2 | openai | comfyui).
        weights: Custom L1-L5 weights as "L1=0.3,L2=0.2,...".
        reference_path: Path or base64 of a reference image for style/composition guidance.

    Returns:
        image_path, scores, rationales, recommendations, cost_usd, tradition, weighted_total.
    """
    # 1. Generate
    gen_result = await generate_image(
        prompt=intent,
        provider=provider,
        tradition=tradition,
        reference_path=reference_path,
    )
    if "error" in gen_result:
        return gen_result

    image_path = gen_result["image_path"]

    # 2. Evaluate
    use_mock = provider == "mock"
    try:
        eval_result = await evaluate_artwork(
            image_path=image_path,
            tradition=tradition,
            intent=intent,
            mock=use_mock,
        )
    except Exception as exc:
        return {**gen_result, "evaluation_error": str(exc)}

    # Apply custom weights if provided
    parsed_weights = _parse_weights_str(weights)
    weighted_total = eval_result.get("score", 0.0)
    if parsed_weights and eval_result.get("dimensions"):
        total = 0.0
        w_sum = sum(parsed_weights.values())
        if w_sum > 0:
            for dim_key, w in parsed_weights.items():
                dim_score = eval_result["dimensions"].get(dim_key, {})
                if isinstance(dim_score, dict):
                    total += dim_score.get("score", 0.0) * w
                else:
                    total += float(dim_score) * w
            weighted_total = round(total / w_sum, 4)

    return {
        "image_path": image_path,
        "tradition": eval_result.get("tradition", tradition),
        "weighted_total": weighted_total,
        "scores": eval_result.get("dimensions", {}),
        "rationales": eval_result.get("rationales", {}),
        "recommendations": eval_result.get("recommendations", []),
        "risk_flags": eval_result.get("risk_flags", []),
        "summary": eval_result.get("summary", ""),
        "cost_usd": gen_result.get("cost_usd", 0.0) + eval_result.get("cost_usd", 0.0),
    }


@mcp.tool()
async def evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
    mock: bool = False,
    mode: str = "strict",
    vlm_model: str = "",
) -> dict:
    """Score an image on L1-L5 cultural dimensions — returns scores, rationales, recommendations.

    Use after generate_image or layers_composite to decide: accept, retry, or edit layers.
    Combine with view_image to correlate visual inspection with numeric scores.

    Args:
        image_path: Path to the image file.
        tradition: Cultural tradition (auto-detected if empty) or path to custom YAML.
        intent: Optional description of what the artwork should express.
        mock: Use mock scoring (no API key required). Useful for testing.
        mode: "strict" (judge), "reference" (advisor), or "rubric_only" (no VLM call).
        vlm_model: Runtime VLM override. Takes precedence over VULCA_VLM_MODEL.

    Returns:
        score, tradition, dimensions, suggestions, summary, cost_usd,
        rationales, recommendations, deviation_types, risk_flags, risk_level.
    """
    from vulca import aevaluate

    result_obj = await aevaluate(
        image_path,
        tradition=tradition,
        intent=intent,
        mock=mock,
        mode=mode,
        vlm_model=vlm_model,
    )
    if isinstance(result_obj, dict):
        return result_obj

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
async def compose_prompt_from_design(
    design_path: str,
) -> dict:
    """Compose a generation prompt from a resolved visual-spec design.md artifact.

    Use when you want Vulca's structured prompt-assembly value without running the
    full visual-plan flow. Returns the composed prompt, negative prompt, and the
    tradition/color tokens that were applied.

    Pass an **absolute path**: the MCP server CWD typically differs from the calling
    agent's CWD, so relative paths resolve against the server, not the caller.
    """
    from pathlib import Path as _Path

    p = _Path(design_path)
    if not p.is_absolute() and not p.exists():
        raise ValueError(
            f"design_path {design_path!r} not found relative to MCP server CWD "
            f"({_Path.cwd()}). Pass an absolute path — the MCP server CWD differs "
            f"from the calling agent's CWD."
        )

    from vulca.prompting import compose_prompt_from_design as _compose_prompt

    return _compose_prompt(design_path)


@mcp.tool()
async def list_traditions() -> dict:
    """List all available cultural traditions with L1-L5 weights and emphasis — first step in tradition discovery.

    Use at the start of a workflow to pick the right tradition, or before search_traditions
    when you want a full overview. Follow with get_tradition_guide for deep context.

    Returns:
        traditions: Dict mapping name → weights, emphasis, description, terminology_count,
        taboos_count, pipeline_variant. count: total number of traditions.
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
    """Get full cultural context for a tradition — terminology, taboos, weights, layer order.

    Use after list_traditions or search_traditions to load context before generate_image.
    The returned tradition_layers list tells you the recommended layer stack for this tradition.

    Args:
        tradition: Tradition name (e.g. chinese_xieyi). Use list_traditions for valid names.

    Returns:
        weights, evolved_weights, emphasis, terminology, taboos, tradition_layers.
        Returns {"error": "..."} for unknown traditions.
    """
    from vulca.cultural.loader import get_tradition_guide as _get_guide
    from vulca.layers.plan_prompt import get_tradition_layer_order

    guide = _get_guide(tradition)
    if guide is None:
        return {"error": f"Unknown tradition: {tradition!r}. Use list_traditions() to see available traditions."}

    result = dict(guide)
    result["tradition_layers"] = get_tradition_layer_order(tradition)
    return result





@mcp.tool()
async def search_traditions(
    tags: list[str],
    limit: int = 5,
) -> dict:
    """Search across all cultural traditions by keyword tags — discover relevant traditions.

    Use before get_tradition_guide when you don't know which tradition fits the intent.
    Searches names, display names, terminology, taboos, and style keywords (bilingual).

    Args:
        tags: Keywords to search (e.g. ["ink wash", "留白", "negative space"]).
        limit: Max matched terms to return per tradition. Default 5.

    Returns:
        matches: List of {tradition, display_name, matched_terms, relevance_score}, sorted by relevance.
        query_tags: Echo of input tags.
    """
    from vulca.cultural.loader import get_all_traditions

    all_traditions = get_all_traditions()
    matches: list[dict] = []

    for name, tc in all_traditions.items():
        matched_terms: list[str] = []

        # Build searchable corpus for this tradition
        searchable: list[tuple[str, str]] = []

        # Tradition name and display names
        searchable.append((name, name))
        for lang_key in ("en", "zh", "ja"):
            dn = tc.display_name.get(lang_key, "")
            if dn:
                searchable.append((dn, f"display_name.{lang_key}"))

        # Terminology
        for t in tc.terminology:
            if t.term:
                searchable.append((t.term, t.term))
            if t.term_zh:
                searchable.append((t.term_zh, t.term_zh))
            for alias in t.aliases:
                searchable.append((alias, alias))
            if t.category:
                searchable.append((t.category, t.category))
            if isinstance(t.definition, dict):
                for dval in t.definition.values():
                    if dval:
                        searchable.append((dval, t.term or dval))
            elif isinstance(t.definition, str) and t.definition:
                searchable.append((t.definition, t.term or t.definition))

        # Taboos
        for tb in tc.taboos:
            if tb.rule:
                searchable.append((tb.rule, tb.rule))
            for pat in tb.trigger_patterns:
                searchable.append((pat, pat))

        # Style keywords
        if tc.style_keywords:
            searchable.append((tc.style_keywords, tc.style_keywords))

        # Match tags against corpus
        tags_matched = 0
        for tag in tags:
            tag_lower = tag.lower()
            found = False
            for text, label in searchable:
                if tag_lower in text.lower():
                    if label not in matched_terms and len(matched_terms) < limit:
                        matched_terms.append(label)
                    found = True
                    break
            if found:
                tags_matched += 1

        if tags_matched > 0:
            display = tc.display_name.get("en", name.replace("_", " ").title())
            matches.append({
                "tradition": name,
                "display_name": display,
                "matched_terms": matched_terms,
                "relevance_score": round(tags_matched / len(tags), 4) if tags else 0.0,
            })

    # Sort by relevance descending
    matches.sort(key=lambda m: m["relevance_score"], reverse=True)

    return {"matches": matches, "query_tags": tags}


# ── Stateless Brief / Concept / Archive Tools ──────────────────────


@mcp.tool()
async def brief_parse(
    intent: str,
    mood: str = "",
) -> dict:
    """Parse a creative intent into a structured brief — tradition, style mix, composition, palette.

    Use at the start of a workflow to translate natural language vision into a structured plan.
    The returned tradition and keywords feed directly into generate_image and get_tradition_guide.

    Args:
        intent: Natural language creative vision.
        mood: Emotional target (e.g. "serene", "epic", "mystical").

    Returns:
        intent, mood, tradition, style_mix, keywords, composition, palette.
    """
    from vulca.studio.brief import Brief
    from vulca.studio.phases.intent import IntentPhase

    try:
        b = Brief.new(intent, mood=mood)
        phase = IntentPhase()
        phase.parse_intent(b)

        # Determine primary tradition from style_mix
        tradition = "default"
        if b.style_mix:
            best = max(b.style_mix, key=lambda s: s.weight)
            tradition = best.tradition or best.tag or "default"

        return {
            "intent": b.intent,
            "mood": b.mood,
            "tradition": tradition,
            "style_mix": [
                {"tradition": s.tradition, "tag": s.tag, "weight": s.weight}
                for s in b.style_mix
            ],
            "keywords": [e.name for e in b.elements],
            "composition": {
                "layout": b.composition.layout,
                "focal_point": b.composition.focal_point,
                "aspect_ratio": b.composition.aspect_ratio,
                "negative_space": b.composition.negative_space,
            },
            "palette": {
                "primary": b.palette.primary,
                "accent": b.palette.accent,
                "mood": b.palette.mood,
            },
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def generate_concepts(
    prompt: str,
    count: int = 3,
    provider: str = "gemini",
) -> dict:
    """Generate multiple concept variation images from a prompt — explore visual directions sequentially.

    Use when the brief is ambiguous and you need options before committing. Call view_image
    on each result, then evaluate_artwork to pick the strongest concept.

    Args:
        prompt: Creative prompt.
        count: Number of concepts to generate (1-6).
        provider: Image generation provider.

    Returns:
        concepts: List of {image_path, cost_usd, latency_ms}. total_cost_usd: sum of all costs.
    """
    count = max(1, min(6, count))
    concepts: list[dict] = []
    total_cost = 0.0

    for _ in range(count):
        r = await generate_image(prompt=prompt, provider=provider)
        if "error" in r:
            concepts.append(r)
        else:
            concepts.append({
                "image_path": r["image_path"],
                "cost_usd": r.get("cost_usd", 0.0),
                "latency_ms": r.get("latency_ms", 0),
            })
            total_cost += r.get("cost_usd", 0.0)

    return {"concepts": concepts, "total_cost_usd": total_cost}


@mcp.tool()
async def archive_session(
    intent: str,
    tradition: str = "default",
    image_path: str = "",
    feedback: str = "",
) -> dict:
    """Archive a completed artwork session for tradition learning and evolution feedback.

    Call after the agent is satisfied with the final result — last step in the workflow.
    Feeds session data into tradition evolution; non-fatal if archive store is unavailable.

    Args:
        intent: Original creative intent.
        tradition: Cultural tradition used.
        image_path: Path to the final image.
        feedback: Agent's assessment (e.g. "accepted", "rejected: too dark").

    Returns:
        archived: Whether archival succeeded. session_id: Archive session identifier.
    """
    import uuid

    session_id = uuid.uuid4().hex[:8]
    archived = False

    try:
        from vulca.studio.brief import Brief
        from vulca.digestion.store import StudioStore
        from vulca.digestion.signals import extract_signals

        b = Brief.new(intent)
        b.session_id = session_id
        store = StudioStore()
        store.save_session(b, user_feedback=feedback or "accepted")
        extract_signals(b, user_feedback=feedback or "accepted")
        archived = True
    except Exception as exc:
        logging.getLogger("vulca.mcp").warning("Archive failed (non-fatal): %s", exc)

    return {
        "archived": archived,
        "session_id": session_id,
    }


@mcp.tool()
async def inpaint_artwork(
    image_path: str,
    region: str = "",
    instruction: str = "",
    mask_path: str = "",
    tradition: str = "default",
    provider: str = "openai",
    output_path: str = "",
) -> dict:
    """Repaint part of an image — native mask (precise) or NL region (legacy, imprecise).

    Two modes:
    - **mask_path** (preferred): RGBA PNG where alpha=0 marks pixels to edit and
      alpha=255 marks pixels to preserve. Routed to provider /v1/images/edits.
      Currently OpenAI gpt-image-2 only; Gemini/ComfyUI raise NotImplementedError.
    - **region** (legacy): NL ("fix the sky") or "x,y,w,h". Detects bbox via VLM,
      crops, regenerates, feathers a rectangular paste. Imprecise — prefer mask_path.

    Precedence: mask_path > region. Setting both logs a warning and uses mask_path.

    Args:
        image_path: Path to the image file.
        region: Legacy NL/coords region. Ignored when mask_path is set.
        instruction: What to paint in the masked / cropped region.
        mask_path: PNG with alpha (0=edit, 255=preserve). Must match image size.
        tradition: Cultural tradition for style consistency.
        provider: Image provider. Default "openai" (only one with native mask).
        output_path: Explicit output PNG path. Default: <image_dir>/inpainted_<stem>.png.

    Returns:
        image_path: Path to the blended result. bbox: Painted region (mask path
        returns full canvas {0,0,100,100}). cost_usd, latency_ms.
    """
    from vulca.inpaint import ainpaint

    if not mask_path and not region:
        return {"error": "inpaint_artwork: pass mask_path=<png> or region=<NL|x,y,w,h>"}

    try:
        result = await ainpaint(
            image_path,
            region=region,
            instruction=instruction,
            mask_path=mask_path,
            tradition=tradition,
            provider=provider,
            output_path=output_path,
            count=1,
            select=0,
        )
        return {
            "image_path": result.blended,
            "bbox": result.bbox,
            "cost_usd": result.cost_usd,
            "latency_ms": result.latency_ms,
        }
    except Exception as exc:
        return {"error": str(exc)}



@mcp.tool()
async def layers_split(
    image_path: str,
    output_dir: str = "",
    mode: str = "regenerate",
    provider: str = "gemini",
    tradition: str = "default",
    plan_path: str = "",
    plan: str = "",
) -> dict:
    """Decompose an image into full-canvas RGBA layers via segmentation or regeneration.

    Use to break a reference or generated image into editable layers. Follow with layers_list
    to inspect the stack, then layers_edit/layers_redraw for targeted modifications.

    Args:
        image_path: Path to the image file.
        output_dir: Output directory (default: image parent/layers).
        mode: "regenerate" (img2img), "extract" (color-range), "vlm" (VLM masks),
              "sam3" (SAM3, GPU), "orchestrated" (YOLO26 + Grounding DINO + SAM +
              SegFormer face-parsing; SOTA — requires plan_path).
        provider: Image provider for regenerate/vlm modes.
        tradition: Cultural tradition for styling.
        plan_path: For mode="orchestrated": path to semantic plan JSON
                   (see assets/showcase/plans/*.json for examples).
        plan: Inline JSON plan (alternative to plan_path). Used for mode="orchestrated".

    Returns:
        layers, manifest_path, split_mode. For orchestrated: detection_report
        with per-entity status and success_rate.
    """
    from pathlib import Path

    if mode == "orchestrated":
        # In-process orchestration with typed plan validation.
        # No subprocess, no polluting of assets/showcase.
        from vulca.pipeline.segment import run as _run_pipeline, Plan
        from pathlib import Path as _P

        img_p = _P(image_path).resolve()
        out = _P(output_dir) if output_dir else img_p.parent / "layers"

        # Plan can come from inline JSON (plan_path starting with '{')
        # or from a file path.
        try:
            if plan and plan_path:
                return {"error": "pass either plan (inline JSON) or plan_path, not both"}
            if plan:
                import json as _json
                plan_obj = Plan.model_validate(_json.loads(plan) if isinstance(plan, str) else plan)
            elif plan_path:
                plan_obj = Plan.from_file(plan_path)
            else:
                return {"error": "orchestrated mode requires 'plan' (inline JSON) or 'plan_path'"}
        except Exception as e:
            return {"error": f"plan validation failed: {e}"}

        try:
            result = _run_pipeline(plan_obj, img_p, out, force=True)
        except Exception as e:
            return {"error": f"pipeline error: {type(e).__name__}: {e}"}

        return {
            "split_mode": "orchestrated",
            "status": result.status,
            "manifest_path": str(result.manifest_path),
            "output_dir": str(result.output_dir),
            "reason": result.reason,
            "detection_report": result.detection_report,
            "stage_timings": result.stage_timings,
            "layers": [
                {"name": l["name"], "file": str(result.output_dir / l["file"]),
                 "z_index": l["z_index"],
                 "content_type": l.get("content_type", l["name"]),
                 "semantic_path": l.get("semantic_path", ""),
                 "blend_mode": l.get("blend_mode", "normal")}
                for l in result.layers
            ],
        }

    from vulca.layers.analyze import analyze_layers as _analyze
    from vulca.layers.split import split_extract, split_regenerate

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
    output_layer_name: str = "",
    background_strategy: str = "transparent",
    preserve_alpha: bool = False,
) -> dict:
    """Redraw a layer via img2img with explicit content/style instructions — targeted layer regeneration.

    Use after layers_list identifies a weak layer, or after evaluate_artwork flags a specific issue.
    Be specific about position ("upper 30%"), scale ("covering 20%"), and style ("lighter ink wash").

    v0.17.14: opt into the hallucination-free flow by passing
    ``background_strategy="cream"`` (or "white"/"sample_median") plus
    ``preserve_alpha=True``; pass ``output_layer_name="..."`` to write a new
    layer file + manifest entry instead of overwriting in place. Defaults
    keep the legacy contract for back-compat.

    Args:
        artwork_dir: Directory with layer PNGs + manifest.
        layer: Single layer name to redraw (mutually exclusive with layers+merge).
        layers: Comma-separated layer names to merge then redraw together.
        instruction: What to change (content, position, scale, style).
        merge: If true, merge the listed layers before redrawing.
        merged_name: Name for the merged output layer.
        provider: Image provider.
        tradition: Cultural tradition.
        output_layer_name: NEW v0.17.14 — non-destructive: write to a new
            layer file (default empty = overwrite source layer in place).
        background_strategy: NEW v0.17.14 — flatten alpha-sparse layer
            before sending to provider. "transparent" (default, legacy) |
            "cream" | "white" | "sample_median". Non-transparent strategies
            stop providers from hallucinating new content into empty regions.
        preserve_alpha: NEW v0.17.14 — re-apply source layer's alpha to the
            provider output. Default False (legacy).

    Returns:
        name, file, z_index, content_type of the redrawn layer.
    """
    from vulca.layers.manifest import load_manifest
    from vulca.layers.redraw import redraw_layer, redraw_merged

    artwork = load_manifest(artwork_dir)

    if layers and merge:
        layer_names = [n.strip() for n in layers.split(",") if n.strip()]
        if not layer_names:
            return {"error": "No layer names provided"}
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
            output_layer_name=output_layer_name,
            background_strategy=background_strategy,
            preserve_alpha=preserve_alpha,
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
    """Structural layer operations — add, remove, reorder, toggle visibility, lock, merge, duplicate.

    Use after layers_list to reorganize the layer stack. Does not modify pixel data;
    for pixel changes use layers_redraw. Follow with layers_composite to see the result.

    Args:
        artwork_dir: Directory with layer PNGs + manifest.
        operation: One of: add, remove, reorder, toggle, lock, merge, duplicate.
        layer: Layer name (for remove/reorder/toggle/lock/duplicate).
        layers: Comma-separated layer names (for merge).
        name: New layer name (for add/merge/duplicate).
        description: Layer description (for add).
        z_index: Z-index position (for add/reorder; -1 = top).
        content_type: Layer role label (e.g. background, subject, decoration).
        semantic_path: Dot-notation label (e.g. "subject.face.eyes"); "" if none.
        visible: Visibility state — applies to operation="toggle".
        locked: Lock state — applies to operation="lock".

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
        layer_names = [n.strip() for n in layers.split(",") if n.strip()]
        if not layer_names:
            return {"error": "No layer names provided"}
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
    """Move, scale, rotate, or change opacity of a layer — non-destructive spatial adjustment.

    Use after layers_list when a layer's position or size needs correcting without redrawing.
    All transforms are relative to the current state. Follow with layers_composite to preview.

    Args:
        artwork_dir: Directory with layer PNGs + manifest.
        layer: Layer name to transform.
        dx: Move X by percentage (positive = right, e.g. 10 = move right 10%).
        dy: Move Y by percentage (positive = down, e.g. -5 = move up 5%).
        scale: Scale factor (1.0 = no change, 0.5 = half, 2.0 = double).
        rotate: Degrees to rotate clockwise (relative).
        opacity: Set opacity 0.0-1.0; use -1 to keep current value.

    Returns:
        status, layer, x, y, width, height, rotation, opacity.
    """
    from vulca.layers.manifest import load_manifest
    from vulca.layers.ops import transform_layer

    artwork = load_manifest(artwork_dir)
    set_opacity = opacity if opacity >= 0 else None
    transform_layer(
        artwork, artwork_dir=artwork_dir, layer_name=layer,
        dx=dx, dy=dy, scale=scale, rotate=rotate, set_opacity=set_opacity,
    )

    layer_result = next((lr for lr in artwork.layers if lr.info.name == layer), None)
    if layer_result is None:
        return {"error": f"Layer '{layer}' not found after transform"}
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
    """Sync local session data to cloud and pull evolved tradition weights — requires VULCA_API_URL.

    Call after archive_session to upload feedback signals and refresh tradition weights.
    Returns error if VULCA_API_URL is not set; non-destructive read-only operations always safe.

    Args:
        push_only: Only push local sessions, skip pulling evolved weights.
        pull_only: Only pull evolved weights, skip pushing sessions.

    Returns:
        pushed_count, pulled_evolved (bool), api_url. error key present on failure.
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
    """Flatten all visible layers into a single composite image — final step in the layer editing loop.

    Use after layers_edit or layers_redraw to preview the full result. Then call view_image
    to inspect and evaluate_artwork to score. Re-composite any time the stack changes.

    Args:
        artwork_dir: Directory containing layer PNGs and manifest.json.
        output_path: Output file path (default: <artwork_dir>/composite.png).

    Returns:
        composite_path: Absolute path to the composited PNG.
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
    export_format: str = "png",
    output_path: str = "",
) -> dict:
    """Export the artwork as a PNG composite or PSD file — for delivery or external editing.

    Use at the end of a workflow after layers_composite confirms the result looks correct.
    PSD format preserves individual layers for editing in Photoshop or Affinity Photo.

    Args:
        artwork_dir: Directory containing layer PNGs and manifest.json.
        export_format: "png" (flat composite, default) or "psd" (layered Photoshop file).
        output_path: Output path (default: <artwork_dir>/composite.png or layers.psd).

    Returns:
        export_path: Absolute path to the exported file.
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

    if export_format == "psd":
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
    """Score each layer independently on L1-L5 dimensions — identify which layers need redrawing.

    Use after layers_split to audit individual layers before compositing.
    Cheaper than re-evaluating the composite after every edit; pinpoints weak layers directly.

    Args:
        artwork_dir: Directory containing layer PNGs and manifest.json.
        tradition: Cultural tradition for evaluation (default: auto-detect).

    Returns:
        layers: Dict mapping layer name → {score, dimensions}. Error key per layer on failure.
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
    seed: int | None = None,
    steps: int | None = None,
    cfg_scale: float | None = None,
    negative_prompt: str | None = None,
    model: str | None = None,
    input_fidelity: str | None = None,
    quality: str | None = None,
    output_format: str | None = None,
) -> dict:
    """Generate a single image from a text prompt — no evaluation, no loop.

    Use after get_tradition_guide for cultural context. Then call view_image to inspect
    and evaluate_artwork to score. For generate+evaluate in one call, use create_artwork.

    Args:
        prompt: Text description of the image to generate.
        provider: Image generation provider (gemini | openai | comfyui | mock).
        tradition: Cultural tradition for prompt enrichment.
        reference_path: Optional reference/sketch image path.
        output_dir: Directory to save the generated image.
        seed: Deterministic seed (diffusion providers). Ignored by DALL-E endpoint;
            wired to generationConfig.seed on Gemini when supported.
        steps: Sampler steps (diffusion providers only). Ignored by Gemini/OpenAI.
        cfg_scale: Classifier-free guidance scale (diffusion providers only).
            Ignored by Gemini/OpenAI.
        negative_prompt: Tokens to avoid. SDXL/ComfyUI use native negative conditioning;
            OpenAI/Gemini prepend "avoid: <tokens>" to the prompt.
        model: Override the provider's default model id (e.g. "gpt-image-2").
            Currently plumbed through as a provider kwarg — providers that
            don't understand it ignore it.
        input_fidelity: OpenAI gpt-image-2 only, /edits endpoint — "high" or "low".
            Controls how closely the edit preserves input image features.
        quality: OpenAI gpt-image-2 quality knob — "low" | "medium" | "high" | "auto".
        output_format: OpenAI gpt-image-2 output encoding — "png" | "webp" | "jpeg".

    Returns:
        image_path, cost_usd, latency_ms, provider.
    """
    import base64
    import tempfile
    import time
    import uuid
    from pathlib import Path

    from vulca.providers import get_image_provider

    try:
        t0 = time.monotonic()

        prov = get_image_provider(provider)
        # Allow per-call model override (e.g. swap gpt-image-1 → gpt-image-2
        # without instantiating a new provider). Silent no-op if the provider
        # has no `model` attribute.
        if model is not None and hasattr(prov, "model"):
            prov.model = model

        ref_b64 = ""
        if reference_path:
            ref_file = Path(reference_path)
            if not ref_file.exists():
                return {"error": f"Reference image not found: {reference_path}"}
            ref_b64 = base64.b64encode(ref_file.read_bytes()).decode()

        extra: dict = {}
        if seed is not None:
            extra["seed"] = seed
        if steps is not None:
            extra["steps"] = steps
        if cfg_scale is not None:
            extra["cfg_scale"] = cfg_scale
        if negative_prompt is not None:
            extra["negative_prompt"] = negative_prompt
        if input_fidelity is not None:
            extra["input_fidelity"] = input_fidelity
        if quality is not None:
            extra["quality"] = quality
        if output_format is not None:
            extra["output_format"] = output_format

        result = await prov.generate(
            prompt,
            tradition=tradition,
            subject=prompt,
            reference_image_b64=ref_b64,
            **extra,
        )

        elapsed_ms = round((time.monotonic() - t0) * 1000)

        # Save to disk
        out = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="vulca_gen_"))
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
            "metadata": dict(result.metadata) if result.metadata else {},
        }
    except Exception as exc:
        return {"error": f"Generation failed: {exc}"}


@mcp.tool()
async def view_image(
    image_path: str,
    max_dimension: int = 1024,
) -> dict:
    """View an image — returns base64 thumbnail for agent visual inspection.

    Use after generate_image or layers_composite to inspect results before deciding next steps.
    Essential for correlating visual quality with evaluate_artwork scores.

    Args:
        image_path: Path to the image file.
        max_dimension: Max width/height in pixels for the thumbnail. Default 1024.

    Returns:
        image_base64, width, height, original_width, original_height, file_size_bytes.
    """
    import base64
    import io
    from pathlib import Path

    from PIL import Image

    p = Path(image_path)
    if not p.exists():
        return {"error": f"Image not found: {image_path}"}

    file_size = p.stat().st_size

    try:
        img = Image.open(p)
        original_width, original_height = img.size

        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
        thumb_w, thumb_h = img.size

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
    except Exception as exc:
        return {"error": f"Cannot read image: {exc}"}

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
    """Inspect the layer stack in an artwork directory — name, z_index, visibility, file status.

    Use after layers_split to understand what was generated, or before layers_edit/layers_redraw
    to identify which layer to target. Always call this before making structural changes.

    Args:
        artwork_dir: Path to artwork directory with manifest.json.

    Returns:
        layers: List of {name, z_index, content_type, visible, blend_mode, locked, opacity,
        semantic_path, file, file_exists}. layer_count, visible_count, has_composite.
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


@mcp.tool()
async def unload_models() -> dict:
    """Release cached model weights (~3GB on MPS: SAM + DINO + SegFormer + YOLO).

    Admin/diagnostic tool. Call when subsequent decompose operations hit
    MemoryError, when the MCP server feels sluggish, or between batches of
    unrelated images. Loaders will re-cache lazily on next pipeline call
    (~3-4s cold-start for SAM + DINO).

    Returns:
        status: "ok" if clears succeeded
        cleared: number of loader caches cleared (should be 4)
    """
    import gc

    from vulca.pipeline.segment.orchestrator import _import_cop

    cop = _import_cop()
    cleared = 0
    for loader_name in ("load_grounding_dino", "load_yolo",
                        "load_face_parser", "_load_sam_model"):
        loader = getattr(cop, loader_name, None)
        if loader is not None and hasattr(loader, "cache_clear"):
            loader.cache_clear()
            cleared += 1

    gc.collect()

    # Best-effort MPS cache eviction. torch import may fail on non-MPS
    # systems; the 4 lru_cache clears above are the main contract.
    try:
        import torch
        if hasattr(torch, "mps") and torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:
        pass

    return {"status": "ok", "cleared": cleared}


if __name__ == "__main__":
    mcp.run()
