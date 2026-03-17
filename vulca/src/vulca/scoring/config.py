"""CriticConfig -- L1-L5 weights, gate thresholds, and risk policy.

Re-exports the canonical CriticConfig from scoring.types for backward compatibility.
"""

from vulca.scoring.types import CriticConfig, DIMENSIONS

__all__ = ["CriticConfig", "DIMENSIONS"]
