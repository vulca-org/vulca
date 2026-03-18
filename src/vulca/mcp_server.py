"""VULCA MCP Server -- expose create/evaluate/traditions as AI agent tools.

Usage:
    vulca-mcp                   # stdio transport (default)
    python -m vulca.mcp_server  # same
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("VULCA", instructions="AI-native cultural art creation & evaluation")


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


@mcp.tool()
async def create_artwork(
    intent: str,
    tradition: str = "default",
    provider: str = "mock",
    hitl: bool = False,
    weights: str = "",
) -> dict:
    """Create cultural artwork through the VULCA pipeline.

    Args:
        intent: Natural language description of what to create.
        tradition: Cultural tradition (e.g. chinese_xieyi, western_academic).
        provider: Image generation provider (mock | nb2).
        hitl: Enable human-in-the-loop (pipeline pauses before decide node).
        weights: Custom L1-L5 weights as string "L1=0.3,L2=0.2,...".

    Returns:
        Session ID, scores, weighted total, status, and creation summary.
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
    )

    interrupt_before = {"decide"} if hitl else None

    output = await execute(DEFAULT, pipeline_input, interrupt_before=interrupt_before)

    return {
        "session_id": output.session_id,
        "status": output.status,
        "interrupted_at": output.interrupted_at,
        "tradition": output.tradition,
        "weighted_total": output.weighted_total,
        "scores": output.final_scores,
        "total_rounds": output.total_rounds,
        "summary": output.summary,
        "cost_usd": output.total_cost_usd,
    }


@mcp.tool()
async def evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
) -> dict:
    """Evaluate artwork on L1-L5 cultural dimensions.

    Args:
        image_path: Path to the image file.
        tradition: Cultural tradition (auto-detected if empty).
        intent: Optional evaluation intent.

    Returns:
        Overall score, L1-L5 dimension scores, and recommendations.
    """
    from vulca import aevaluate

    result = await aevaluate(image_path, tradition=tradition, intent=intent)
    return {
        "score": result.score,
        "tradition": result.tradition,
        "dimensions": result.dimensions,
        "summary": result.summary,
        "recommendations": result.recommendations,
        "cost_usd": result.cost_usd,
    }


@mcp.tool()
async def list_traditions() -> dict:
    """List available cultural traditions with their L1-L5 weights.

    Returns:
        Dictionary mapping tradition names to L1-L5 weight vectors.
    """
    from vulca.cultural import TRADITION_WEIGHTS

    return {"traditions": TRADITION_WEIGHTS}


if __name__ == "__main__":
    mcp.run()
