"""VULCA storage subsystem -- session and feedback backend protocols.

Usage::

    from vulca.storage import SessionBackend, FeedbackBackend, UnifiedSessionStore
    from vulca.storage.jsonl import JsonlSessionBackend, JsonlFeedbackBackend
"""

from vulca.storage.protocol import FeedbackBackend, SessionBackend
from vulca.storage.unified import UnifiedSessionStore

__all__ = ["SessionBackend", "FeedbackBackend", "UnifiedSessionStore"]
