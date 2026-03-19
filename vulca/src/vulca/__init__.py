"""VULCA -- AI-native creation organism.

Create, critique, and evolve cultural art through multi-agent AI pipelines.

Usage::

    import vulca

    # Evaluate an artwork
    result = vulca.evaluate("painting.jpg")
    print(result.score)          # 0.82
    print(result.tradition)      # "chinese_xieyi"
    print(result.dimensions)     # {"L1": 0.75, "L2": 0.82, ...}

    # With intent
    result = vulca.evaluate("painting.jpg", intent="check ink wash style")

    # With explicit tradition
    result = vulca.evaluate("painting.jpg", tradition="chinese_xieyi")

    # Async
    result = await vulca.aevaluate("painting.jpg", intent="...")
"""

from vulca._version import __version__
from vulca.create import acreate, create
from vulca.evaluate import aevaluate, evaluate
from vulca.session import asession, session
from vulca.types import CreateResult, EvalResult, SkillResult


def traditions() -> list[str]:
    """List all available cultural traditions."""
    from vulca.cultural import TRADITIONS
    return list(TRADITIONS)


def get_weights(tradition: str) -> dict[str, float]:
    """Get L1-L5 weights for a tradition (evolved if available)."""
    from vulca.cultural import get_weights as _get_weights
    return _get_weights(tradition)


__all__ = [
    "__version__",
    "evaluate",
    "aevaluate",
    "create",
    "acreate",
    "session",
    "asession",
    "traditions",
    "get_weights",
    "EvalResult",
    "CreateResult",
    "SkillResult",
]
