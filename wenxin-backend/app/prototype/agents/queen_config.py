"""QueenConfig — budget guardrails, round limits, and decision thresholds."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "QueenConfig",
]


@dataclass
class QueenConfig:
    """Configuration for the Queen Agent decision logic."""

    max_rounds: int = 3                # maximum iteration rounds (2 rerun chances)
    max_cost_usd: float = 0.10        # per-task cost ceiling
    accept_threshold: float = 0.80     # weighted_total >= 0.80 → accept
    early_stop_threshold: float = 0.93 # >= 0.93 → immediate accept, skip further rounds
    min_improvement: float = 0.05      # improvement < 0.05 between rounds → stop
    mock_cost_per_round: float = 0.02  # simulated cost per round in mock mode

    def to_dict(self) -> dict:
        return {
            "max_rounds": self.max_rounds,
            "max_cost_usd": self.max_cost_usd,
            "accept_threshold": self.accept_threshold,
            "early_stop_threshold": self.early_stop_threshold,
            "min_improvement": self.min_improvement,
            "mock_cost_per_round": self.mock_cost_per_round,
        }
