"""VULCA Self-Evolution System (WU-16).

Provides autonomous agents that continuously evolve the evaluation system
based on user feedback, quality monitoring, and principle distillation.

Key components:
- EvolutionAgent: Drives weight adjustments and principle extraction
- QualityAgent: Monitors evaluation quality and detects drift
- AdminAgent: Orchestrates sub-agents and generates weekly reports
- PreferenceModel: Aggregates feedback into preference signals
- PrincipleDistiller: Extracts actionable rules from feedback patterns
"""

from app.prototype.evolution.evolution_agent import EvolutionAgent
from app.prototype.evolution.quality_agent import QualityAgent
from app.prototype.evolution.admin_agent import AdminAgent
from app.prototype.evolution.preference_model import PreferenceModel
from app.prototype.evolution.principle_distiller import PrincipleDistiller

__all__ = [
    "EvolutionAgent",
    "QualityAgent",
    "AdminAgent",
    "PreferenceModel",
    "PrincipleDistiller",
]
