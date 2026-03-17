"""Storage backend protocols -- abstract interfaces for session and feedback persistence.

These protocols decouple the pipeline from any specific storage implementation.
Implementations:
- JsonlSessionBackend / JsonlFeedbackBackend (local dev, JSONL files)
- PostgresSessionBackend (production, lives in wenxin-backend, not in vulca/)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SessionBackend(ABC):
    """Abstract backend for session (SessionDigest) persistence."""

    @abstractmethod
    def append(self, session: dict[str, Any]) -> None:
        """Persist a new session record."""

    @abstractmethod
    def get_all(self, limit: int = 0) -> list[dict[str, Any]]:
        """Retrieve all sessions, optionally limited. 0 = no limit."""

    @abstractmethod
    def count(self) -> int:
        """Return total number of stored sessions."""

    @abstractmethod
    def get_by_tradition(self, tradition: str, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve sessions filtered by tradition."""

    @abstractmethod
    def update_field(self, session_id: str, field: str, value: Any) -> bool:
        """Update a single field on a session. Returns True if found and updated."""


class FeedbackBackend(ABC):
    """Abstract backend for explicit feedback persistence."""

    @abstractmethod
    def append(self, record: dict[str, Any]) -> None:
        """Persist a new feedback record."""

    @abstractmethod
    def get_all(self, limit: int = 0) -> list[dict[str, Any]]:
        """Retrieve all feedback records."""

    @abstractmethod
    def get_by_tradition(self, tradition: str, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve feedback filtered by tradition."""

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Return aggregated feedback statistics."""
