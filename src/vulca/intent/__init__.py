"""VULCA intent subsystem -- intent parsing, skill selection, meta-orchestration.

Public API::

    from vulca.intent import IntentAgent, IntentResult
"""

from vulca.intent.types import IntentResult, ResultCard
from vulca.intent.agent import IntentAgent

__all__ = ["IntentAgent", "IntentResult", "ResultCard"]
