"""AgentMetadata — declarative metadata for graph node agents.

Provides static information about each agent's capabilities, expected
latency, I/O contract, and tags — used by the template builder for
validation and by the frontend topology viewer for display.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentMetadata:
    """Metadata describing an agent node's capabilities and contract.

    Attributes
    ----------
    display_name : str
        Human-readable name shown in the UI (e.g. "Cultural Scout").
    supports_hitl : bool
        Whether this node can be paused for human input.
    estimated_latency_ms : int
        Rough latency estimate for UI planning (0 = negligible).
    input_keys : list[str]
        PipelineState keys this node reads.
    output_keys : list[str]
        PipelineState keys this node writes.
    tags : list[str]
        Freeform tags for filtering (e.g. "evidence", "scoring", "decision").
    """

    display_name: str = ""
    supports_hitl: bool = False
    estimated_latency_ms: int = 0
    input_keys: list[str] = field(default_factory=list)
    output_keys: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
