"""Node runtime state management for mute/bypass/expand.

Tracks per-node visual and execution state that can be toggled
from the frontend via REST API.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class NodeRuntimeState:
    """Runtime state for a single node."""
    muted: bool = False
    bypassed: bool = False
    expanded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "muted": self.muted,
            "bypassed": self.bypassed,
            "expanded": self.expanded,
        }


class NodeRuntimeManager:
    """Manages runtime state for all nodes in a pipeline run.

    One instance per task_id; stored in the routes._node_runtime_managers dict.
    """

    def __init__(self) -> None:
        self._states: dict[str, NodeRuntimeState] = {}

    def get(self, node_name: str) -> NodeRuntimeState:
        """Get or create runtime state for a node."""
        if node_name not in self._states:
            self._states[node_name] = NodeRuntimeState()
        return self._states[node_name]

    # ------------------------------------------------------------------
    # Toggle methods — flip the current state and return the new value
    # ------------------------------------------------------------------

    def toggle_mute(self, node_name: str) -> bool:
        """Toggle mute state. Returns new muted value."""
        state = self.get(node_name)
        state.muted = not state.muted
        logger.debug("Node '%s' muted=%s", node_name, state.muted)
        return state.muted

    def toggle_bypass(self, node_name: str) -> bool:
        """Toggle bypass state. Returns new bypassed value."""
        state = self.get(node_name)
        state.bypassed = not state.bypassed
        logger.debug("Node '%s' bypassed=%s", node_name, state.bypassed)
        return state.bypassed

    def toggle_expand(self, node_name: str) -> bool:
        """Toggle expand state. Returns new expanded value."""
        state = self.get(node_name)
        state.expanded = not state.expanded
        logger.debug("Node '%s' expanded=%s", node_name, state.expanded)
        return state.expanded

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def is_muted(self, node_name: str) -> bool:
        return self.get(node_name).muted

    def is_bypassed(self, node_name: str) -> bool:
        return self.get(node_name).bypassed

    def is_expanded(self, node_name: str) -> bool:
        return self.get(node_name).expanded

    def get_all(self) -> dict[str, dict[str, Any]]:
        """Get all node states as a dict."""
        return {name: state.to_dict() for name, state in self._states.items()}

    def get_state(self, node_name: str) -> dict[str, bool]:
        """Return full runtime state dict for a node (compatibility alias)."""
        return self.get(node_name).to_dict()

    def get_all_states(self) -> dict[str, dict[str, bool]]:
        """Return runtime state for all nodes that have been toggled (compatibility alias)."""
        return {name: state.to_dict() for name, state in sorted(self._states.items())}
