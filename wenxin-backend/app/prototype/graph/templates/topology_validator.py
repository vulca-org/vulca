"""Topology validator — pre-build I/O contract checking for graph templates.

Validates that every edge in a template has compatible I/O: the source
node's ``output_keys`` must cover the target node's ``input_keys``
(minus shared PipelineState keys that are always available).

Usage::

    from app.prototype.graph.templates.topology_validator import validate_template
    result = validate_template(template)
    if not result.valid:
        for err in result.errors:
            print(err)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.prototype.graph.state import PipelineState
from app.prototype.graph.templates.template_model import GraphTemplate

# Derive ambient state keys directly from PipelineState to stay in sync
# automatically when fields are added/renamed.
STATE_KEYS: frozenset[str] = frozenset(PipelineState.__annotations__.keys())


@dataclass
class ValidationResult:
    """Result of a template topology validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_template(template: GraphTemplate) -> ValidationResult:
    """Validate I/O contracts for all edges in a template.

    Checks that for each edge ``(src, dst)``, the source node's
    ``output_keys`` (plus STATE_KEYS) cover the target node's
    ``input_keys``.

    Returns a ValidationResult with errors for missing keys and
    warnings for nodes without metadata.
    """
    from app.prototype.graph.registry import AgentRegistry

    # Ensure node classes are registered (importing the package triggers decorators)
    try:
        import app.prototype.graph.nodes  # noqa: F401
    except ImportError:
        pass

    errors: list[str] = []
    warnings: list[str] = []

    # Collect all output keys reachable up to each node via BFS-like accumulation
    # For simplicity, check each edge independently against STATE_KEYS + source outputs
    all_edges: list[tuple[str, str]] = list(template.edges)
    for cond in template.conditional_edges:
        for dst in cond.destinations.values():
            if dst != "__end__":
                all_edges.append((cond.source, dst))

    for src, dst in all_edges:
        if dst == "__end__":
            continue

        src_meta = AgentRegistry.get_metadata(src)
        dst_meta = AgentRegistry.get_metadata(dst)

        if src_meta is None:
            warnings.append(f"Node '{src}' has no metadata")
            continue
        if dst_meta is None:
            warnings.append(f"Node '{dst}' has no metadata")
            continue

        available = STATE_KEYS | set(src_meta.output_keys)
        needed = set(dst_meta.input_keys)
        missing = needed - available

        if missing:
            errors.append(
                f"Edge {src}\u2192{dst}: target needs {sorted(missing)} "
                f"not in source outputs or state"
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
