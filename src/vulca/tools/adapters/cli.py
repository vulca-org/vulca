"""CLI adapter for the VULCA Tool Protocol.

Builds argparse subparsers for ``vulca tools list`` and ``vulca tools run``,
and dispatches to the appropriate tool in the registry.

Usage (from main CLI)::

    vulca tools list
    vulca tools list --category cultural
    vulca tools list --json
    vulca tools run whitespace_analyze --image art.png --tradition chinese_xieyi
    vulca tools run color_correct --image art.png --mode fix --output corrected.png
"""

from __future__ import annotations

import argparse
import base64
import json as json_mod
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vulca.tools.registry import ToolRegistry


def build_tools_parser(registry: "ToolRegistry") -> argparse.ArgumentParser:
    """Build an argparse parser for the ``tools`` command group.

    Parameters
    ----------
    registry:
        A populated ToolRegistry (after ``discover()``).

    Returns
    -------
    argparse.ArgumentParser
        Parser with ``list`` and ``run`` subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="vulca tools",
        description="Run algorithmic analysis/processing tools",
    )
    sub = parser.add_subparsers(dest="tools_command")

    # --- list ---
    list_p = sub.add_parser("list", help="List available tools")
    list_p.add_argument(
        "--category",
        default="",
        help="Filter by category (e.g. cultural, filter, composite)",
    )
    list_p.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON",
    )

    # --- run ---
    run_p = sub.add_parser("run", help="Run a tool on an image")
    run_p.add_argument("tool_name", help="Tool name (e.g. whitespace_analyze)")
    run_p.add_argument("--image", "-i", required=True, help="Image file path")
    run_p.add_argument("--tradition", "-t", default="", help="Cultural tradition")
    run_p.add_argument(
        "--mode",
        "-m",
        default="check",
        choices=["check", "fix", "suggest"],
        help="Tool execution mode: check (default), fix, suggest",
    )
    run_p.add_argument(
        "--output",
        "-o",
        default="",
        help="Output path for annotated/fixed image",
    )
    run_p.add_argument(
        "--threshold",
        action="append",
        metavar="KEY=VALUE",
        default=[],
        help="Threshold override (repeatable), e.g. --threshold ratio_min=0.2",
    )
    run_p.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON",
    )

    return parser


def run_tools_command(args: argparse.Namespace, registry: "ToolRegistry") -> str:
    """Execute the tools subcommand indicated by *args* and return output string.

    Parameters
    ----------
    args:
        Parsed namespace from ``build_tools_parser(...).parse_args(...)``.
    registry:
        A populated ToolRegistry.

    Returns
    -------
    str
        Human-readable (or JSON) output string.
    """
    cmd = getattr(args, "tools_command", None)

    if cmd == "list":
        return _cmd_list(args, registry)
    elif cmd == "run":
        return _cmd_run(args, registry)
    else:
        # No sub-command — print help
        return "Usage: vulca tools {list|run} ...\n"


# ---------------------------------------------------------------------------
# Internal: list
# ---------------------------------------------------------------------------


def _cmd_list(args: argparse.Namespace, registry: "ToolRegistry") -> str:
    from vulca.tools.protocol import ToolCategory

    tools = registry.list_all()

    # Optional category filter
    category_filter = (args.category or "").strip().lower()
    if category_filter:
        # Match against ToolCategory enum values (string)
        tools = [t for t in tools if t.category.value.lower() == category_filter]

    if getattr(args, "json", False):
        data = [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "category": t.category.value,
                "max_seconds": t.max_seconds,
                "replaces": t.__class__.replaces,
            }
            for t in tools
        ]
        return json_mod.dumps(data, indent=2)

    # Human-readable table
    if not tools:
        return f"No tools found{' for category ' + category_filter if category_filter else ''}.\n"

    lines = []
    lines.append(f"Available tools ({len(tools)} total):")
    lines.append("")
    for t in tools:
        lines.append(f"  {t.name}")
        lines.append(f"    Display: {t.display_name}")
        lines.append(f"    Category: {t.category.value}")
        lines.append(f"    Description: {t.description}")
        replaces = t.__class__.replaces
        if replaces:
            lines.append(f"    Replaces: {replaces}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal: run
# ---------------------------------------------------------------------------


def _cmd_run(args: argparse.Namespace, registry: "ToolRegistry") -> str:
    from vulca.tools.protocol import ToolConfig

    tool_name = args.tool_name
    try:
        tool = registry.get(tool_name)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Read image bytes
    try:
        with open(args.image, "rb") as fh:
            image_bytes = fh.read()
    except OSError as exc:
        print(f"Error reading image: {exc}", file=sys.stderr)
        sys.exit(1)

    # Parse thresholds
    thresholds: dict[str, float] = {}
    for raw in (args.threshold or []):
        raw = raw.strip()
        if "=" not in raw:
            print(f"Warning: skipping invalid threshold {raw!r}", file=sys.stderr)
            continue
        k, v = raw.split("=", 1)
        try:
            thresholds[k.strip()] = float(v.strip())
        except ValueError:
            print(f"Warning: skipping non-numeric threshold value {raw!r}", file=sys.stderr)

    config = ToolConfig(
        mode=args.mode,  # type: ignore[arg-type]
        thresholds=thresholds,
    )

    # Build Input — all tools share image: bytes + tradition: str schema
    input_data = tool.Input(image=image_bytes, tradition=args.tradition)
    output = tool.safe_execute(input_data, config)

    # Save annotated image / fixed image if --output specified
    output_path = (args.output or "").strip()
    if output_path:
        _save_output_image(output, output_path)

    # Render result
    if getattr(args, "json", False):
        return _output_to_json(output)
    return _output_to_text(output, tool_name)


def _save_output_image(output: object, path: str) -> None:
    """Save annotated_image or fixed_image bytes to *path*.

    Tries evidence.annotated_image first, then fixed_image on the output itself.
    """
    img_bytes: bytes | None = None

    # fixed_image (e.g. color_correct fix mode)
    fixed = getattr(output, "fixed_image", None)
    if isinstance(fixed, bytes) and fixed:
        img_bytes = fixed

    # evidence.annotated_image fallback
    if img_bytes is None:
        evidence = getattr(output, "evidence", None)
        if evidence is not None:
            ann = getattr(evidence, "annotated_image", None)
            if isinstance(ann, bytes) and ann:
                img_bytes = ann

    if img_bytes is None:
        return

    with open(path, "wb") as fh:
        fh.write(img_bytes)


def _output_to_json(output: object) -> str:
    """Serialize a ToolSchema Output instance to JSON string."""
    try:
        data = output.model_dump()  # type: ignore[attr-defined]
        # Convert bytes fields to base64 strings for JSON serialisation
        data = _bytes_to_b64_recursive(data)
        return json_mod.dumps(data, indent=2)
    except Exception as exc:
        return json_mod.dumps({"error": str(exc)})


def _output_to_text(output: object, tool_name: str) -> str:
    """Render output as human-readable text."""
    lines = [f"Tool: {tool_name}", ""]

    # Common scalar fields
    for field in ("ratio", "distribution", "cultural_verdict",
                  "brightness", "contrast", "channel_bias", "suggestions"):
        val = getattr(output, field, None)
        if val is not None:
            lines.append(f"  {field}: {val}")

    # evidence summary
    evidence = getattr(output, "evidence", None)
    if evidence is not None:
        lines.append("")
        lines.append(f"  Summary: {evidence.summary}")
        lines.append(f"  Confidence: {evidence.confidence:.2f}")

    return "\n".join(lines)


def _bytes_to_b64_recursive(obj: object) -> object:
    """Recursively convert bytes values to base64 strings."""
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("ascii")
    if isinstance(obj, dict):
        return {k: _bytes_to_b64_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_bytes_to_b64_recursive(v) for v in obj]
    return obj
