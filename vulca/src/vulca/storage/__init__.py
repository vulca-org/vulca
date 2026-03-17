"""VULCA storage subsystem -- session and feedback backend protocols.

Usage::

    from vulca.storage import SessionBackend, FeedbackBackend
    from vulca.storage.jsonl import JsonlSessionBackend, JsonlFeedbackBackend
"""

from vulca.storage.protocol import FeedbackBackend, SessionBackend

__all__ = ["SessionBackend", "FeedbackBackend"]
