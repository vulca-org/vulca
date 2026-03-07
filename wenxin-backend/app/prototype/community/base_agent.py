"""Abstract base class for all VULCA community agents.

Every agent must implement :meth:`run_cycle` which performs one
unit of autonomous work (evaluate an image, submit feedback, etc.)
and returns a summary dict.  Actions are appended to a per-agent
JSONL log file under ``data/agent_logs/``.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.prototype.community.api_client import VulcaAPIClient

logger = logging.getLogger(__name__)


@dataclass
class BaseAgent(ABC):
    """Minimal contract for a community agent."""

    name: str
    client: VulcaAPIClient | None = field(default=None)
    log_path: Path = field(default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.log_path is None:
            self.log_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "agent_logs"
                / f"{self.name}.jsonl"
            )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def run_cycle(self) -> dict:
        """Execute one cycle of agent behaviour.

        Returns a summary dict describing what happened.
        """
        ...

    # ------------------------------------------------------------------
    # Hooks (override as needed)
    # ------------------------------------------------------------------

    def should_run(self) -> bool:
        """Return ``True`` if this agent is due to run.

        Sub-classes can override this to implement custom scheduling
        logic (e.g. time-of-day restrictions, cooldown windows).
        """
        return True

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_action(self, action: str, details: dict | None = None) -> None:
        """Append a structured JSONL record to the agent log file."""
        record = {
            "agent": self.name,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.info("Agent %s: %s", self.name, action)
