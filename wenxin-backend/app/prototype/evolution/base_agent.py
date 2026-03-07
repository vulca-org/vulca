"""BaseAgent stub for evolution agents (WU-12 pattern).

This is distinct from the LangGraph BaseAgent in graph/base_agent.py.
Evolution agents use run_cycle() for periodic autonomous execution,
while graph agents use execute(state) for pipeline node execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class BaseAgent(ABC):
    """Abstract base for autonomous evolution agents."""

    name: str
    log_path: Path = field(default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.log_path is None:
            self.log_path = (
                Path(__file__).parent.parent / "data" / "agent_logs" / f"{self.name}.jsonl"
            )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def run_cycle(self) -> dict:
        """Execute one autonomous cycle and return a result summary."""
        ...

    def log_action(self, action: str, details: dict | None = None) -> None:
        """Append a structured log entry to the agent's JSONL log."""
        record = {
            "agent": self.name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
