"""VULCA MCP Server -- expose create/evaluate/traditions as AI agent tools.

Usage:
    vulca-mcp                   # stdio transport (default)
    python -m vulca.mcp_server  # same
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("VULCA", instructions="AI-native cultural art creation & evaluation")


@mcp.tool()
async def create_artwork(
    intent: str,
    tradition: str = "default",
    provider: str = "mock",
) -> dict:
    """Create cultural artwork through the VULCA pipeline.

    Args:
        intent: Natural language description of what to create.
        tradition: Cultural tradition (e.g. chinese_xieyi, western_academic).
        provider: Image generation provider (mock | nb2).

    Returns:
        Session ID, scores, weighted total, and creation summary.
    """
    from vulca import acreate

    result = await acreate(intent, tradition=tradition, provider=provider, mode="local")
    return {
        "session_id": result.session_id,
        "tradition": result.tradition,
        "weighted_total": result.weighted_total,
        "scores": result.scores,
        "total_rounds": result.total_rounds,
        "summary": result.summary,
        "cost_usd": result.cost_usd,
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
