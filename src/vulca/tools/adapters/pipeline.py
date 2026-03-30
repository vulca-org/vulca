"""Pipeline adapter — wrap any VulcaTool as a PipelineNode.

Usage::

    from vulca.tools.adapters.pipeline import tool_as_pipeline_node
    from vulca.tools.cultural.whitespace import WhitespaceAnalyzer

    NodeCls = tool_as_pipeline_node(WhitespaceAnalyzer)
    node = NodeCls()
    output = await node.run(ctx)

The wrapped node:
- Reads ``image_b64`` from ctx and base64-decodes it to bytes.
- Builds the tool's Input (image=bytes, tradition=ctx.tradition).
- Reads ``node_params[tool_name]`` for mode/thresholds/params → ToolConfig.
- Executes ``tool.safe_execute(input_data, config)``.
- Writes results to ctx:
    - ``{tool_name}_result``  : serialisable dict of the full output
    - ``{tool_name}_evidence``: {summary, confidence, details}
- In fix mode, if the output has a non-None ``fixed_image`` bytes field,
  re-encodes it as base64 and overwrites ``image_b64`` in ctx.
"""

from __future__ import annotations

import base64
import logging
from typing import Any, Type

from vulca.pipeline.node import NodeContext, PipelineNode
from vulca.tools.protocol import ToolConfig, VulcaTool

logger = logging.getLogger("vulca.tools.pipeline")


def tool_as_pipeline_node(tool_cls: Type[VulcaTool]) -> Type[PipelineNode]:
    """Create a PipelineNode subclass that wraps *tool_cls*.

    Parameters
    ----------
    tool_cls:
        A concrete subclass of :class:`VulcaTool`.

    Returns
    -------
    Type[PipelineNode]
        A new ``PipelineNode`` subclass whose ``name`` equals ``tool_cls.name``.
    """

    # Capture the tool name for closure
    _tool_name: str = tool_cls.name
    # Instantiate the tool once for the class (shared instance, tools are stateless)
    _tool_instance: VulcaTool = tool_cls()

    class WrappedToolNode(PipelineNode):
        name = _tool_name

        async def run(self, ctx: NodeContext) -> dict[str, Any]:
            # ------------------------------------------------------------------
            # 1. Read image_b64 from ctx; base64-decode to bytes
            # ------------------------------------------------------------------
            image_b64: str = ctx.get("image_b64", "") or ""
            image_mime: str = ctx.get("image_mime", "image/png") or "image/png"

            if image_b64:
                try:
                    raw_bytes = base64.b64decode(image_b64)
                    # SVG is not a raster image — tool pixel algorithms cannot
                    # process it.  Convert to a small raster PNG placeholder.
                    if "svg" in image_mime.lower() or _is_svg(raw_bytes):
                        image_bytes = _svg_to_png(raw_bytes)
                    else:
                        image_bytes = raw_bytes
                except Exception as exc:
                    logger.error(
                        "WrappedToolNode(%s): failed to decode image_b64: %s",
                        _tool_name, exc,
                    )
                    image_bytes = _empty_png()
            else:
                # No image yet — produce empty 1x1 white PNG as fallback
                image_bytes = _empty_png()

            # ------------------------------------------------------------------
            # 2. Build tool Input
            # ------------------------------------------------------------------
            tradition: str = ctx.tradition or ""
            input_data = _tool_instance.Input(image=image_bytes, tradition=tradition)

            # ------------------------------------------------------------------
            # 3. Read node_params[tool_name] → ToolConfig
            # ------------------------------------------------------------------
            node_params: dict[str, Any] = ctx.get("node_params") or {}
            tool_params: dict[str, Any] = node_params.get(_tool_name) or {}

            config = ToolConfig(
                mode=tool_params.get("mode", "check"),
                thresholds={
                    k: float(v)
                    for k, v in (tool_params.get("thresholds") or {}).items()
                },
                params=tool_params.get("params") or {},
            )

            # ------------------------------------------------------------------
            # 4. Execute tool
            # ------------------------------------------------------------------
            output = _tool_instance.safe_execute(input_data, config)

            # ------------------------------------------------------------------
            # 5a. Serialize output to a plain dict (drop bytes fields)
            # ------------------------------------------------------------------
            try:
                result_dict: dict[str, Any] = output.model_dump()
                result_dict = _sanitize_result(result_dict)
            except Exception:
                result_dict = {}

            # ------------------------------------------------------------------
            # 5b. Extract evidence summary
            # ------------------------------------------------------------------
            evidence = getattr(output, "evidence", None)
            evidence_dict: dict[str, Any] = {}
            if evidence is not None:
                evidence_dict = {
                    "summary": getattr(evidence, "summary", ""),
                    "confidence": getattr(evidence, "confidence", 0.0),
                    "details": getattr(evidence, "details", {}),
                }

            out: dict[str, Any] = {
                f"{_tool_name}_result": result_dict,
                f"{_tool_name}_evidence": evidence_dict,
            }

            # ------------------------------------------------------------------
            # 5c. Fix mode: if fixed_image present, update image_b64 in ctx
            # ------------------------------------------------------------------
            fixed_image: bytes | None = getattr(output, "fixed_image", None)
            if fixed_image and isinstance(fixed_image, bytes) and config.mode == "fix":
                new_b64 = base64.b64encode(fixed_image).decode("ascii")
                out["image_b64"] = new_b64
                logger.debug(
                    "WrappedToolNode(%s): fix mode updated image_b64 (%d bytes → b64)",
                    _tool_name, len(fixed_image),
                )

            return out

    # Set a meaningful class name for debugging
    WrappedToolNode.__name__ = f"WrappedToolNode_{_tool_name}"
    WrappedToolNode.__qualname__ = f"WrappedToolNode_{_tool_name}"
    return WrappedToolNode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _empty_png() -> bytes:
    """Return a minimal 1×1 white PNG as a fallback image."""
    import io
    from PIL import Image

    img = Image.new("RGB", (1, 1), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


def _is_svg(data: bytes) -> bool:
    """Return True if *data* looks like SVG markup."""
    try:
        head = data[:200].lstrip()
        return head.startswith(b"<svg") or b"<svg" in head[:100]
    except Exception:
        return False


def _svg_to_png(svg_bytes: bytes) -> bytes:
    """Convert SVG bytes to a small 64×64 raster PNG for tool processing.

    Falls back to a solid-colour placeholder if conversion fails.
    """
    import io
    from PIL import Image

    # Try cairosvg first (optional dep); fall back to placeholder
    try:
        import cairosvg  # type: ignore[import]
        png_bytes: bytes = cairosvg.svg2png(
            bytestring=svg_bytes, output_width=64, output_height=64
        )
        return png_bytes
    except Exception:
        pass

    # Fallback: return a 64×64 mid-grey PNG
    img = Image.new("RGB", (64, 64), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


def _sanitize_result(obj: Any) -> Any:
    """Recursively replace bytes values with a placeholder string."""
    if isinstance(obj, bytes):
        return f"<bytes:{len(obj)}>"
    if isinstance(obj, dict):
        return {k: _sanitize_result(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_result(v) for v in obj]
    return obj
