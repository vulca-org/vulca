"""VULCA cultural subsystem -- tradition weights, classifiers, dynamic adjustments.

Each tradition assigns different importance to the five evaluation levels:
- L1: Visual Perception
- L2: Technical Execution
- L3: Cultural Context
- L4: Critical Interpretation
- L5: Philosophical Aesthetics
"""

from __future__ import annotations

# Hardcoded fallback weights (used when YAML loader unavailable)
TRADITION_WEIGHTS: dict[str, dict[str, float]] = {
    "default": {"L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20},
    "chinese_xieyi": {"L1": 0.10, "L2": 0.15, "L3": 0.25, "L4": 0.20, "L5": 0.30},
    "chinese_gongbi": {"L1": 0.15, "L2": 0.30, "L3": 0.25, "L4": 0.15, "L5": 0.15},
    "western_academic": {"L1": 0.20, "L2": 0.25, "L3": 0.15, "L4": 0.25, "L5": 0.15},
    "islamic_geometric": {"L1": 0.25, "L2": 0.30, "L3": 0.20, "L4": 0.15, "L5": 0.10},
    "japanese_traditional": {"L1": 0.15, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.25},
    "watercolor": {"L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20},
    "african_traditional": {"L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20},
    "south_asian": {"L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20},
}

TRADITIONS = list(TRADITION_WEIGHTS.keys())


def get_weights(tradition: str) -> dict[str, float]:
    """Return L1-L5 weights for a given tradition.

    Priority: YAML config (if loaded) > hardcoded TRADITION_WEIGHTS > default.
    """
    try:
        from vulca.cultural.loader import get_weights as _yaml_get_weights
        return _yaml_get_weights(tradition)
    except Exception:
        logging.getLogger("vulca").debug("YAML weight loader unavailable, using hardcoded weights")
        return TRADITION_WEIGHTS.get(tradition, TRADITION_WEIGHTS["default"])
