"""EvolutionAgent - Drives self-evolution of the VULCA evaluation system.

On each cycle:
1. Loads feedback via PreferenceModel
2. Computes preference adjustments
3. Distills principles via PrincipleDistiller
4. Writes evolved context to data/evolved_context.json
5. Logs the evolution step
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from app.prototype.evolution.base_agent import BaseAgent
from app.prototype.evolution.preference_model import PreferenceModel
from app.prototype.evolution.principle_distiller import PrincipleDistiller

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"
_EVOLVED_CONTEXT_PATH = _DATA_DIR / "evolved_context.json"


@dataclass
class EvolutionAgent(BaseAgent):
    """Autonomous agent that evolves evaluation weights and principles."""

    name: str = "evolution"
    preference_model: PreferenceModel = field(default_factory=PreferenceModel)
    principle_distiller: PrincipleDistiller = field(default_factory=PrincipleDistiller)

    async def run_cycle(self) -> dict:
        """Execute one evolution cycle.

        Returns
        -------
        dict with keys:
          - principles: int (number of distilled principles)
          - adjustments: dict (weight adjustment map)
        """
        self.log_action("cycle_start")

        # 1. Load feedback
        records = self.preference_model.load_feedback()
        self.log_action("feedback_loaded", {"count": len(records)})

        # 2. Compute preference adjustments
        self.preference_model.compute_preferences()
        adjustments = self.preference_model.get_weight_adjustments()
        self.log_action("adjustments_computed", {"adjustments": adjustments})

        # 3. Distill principles
        principles = self.principle_distiller.distill(records)
        self.log_action("principles_distilled", {"count": len(principles)})

        # 4. Write evolved context
        evolved_context = {
            "weight_adjustments": adjustments,
            "principles": principles,
            "last_evolved": datetime.utcnow().isoformat(),
            "feedback_count": len(records),
        }
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(_EVOLVED_CONTEXT_PATH, "w", encoding="utf-8") as f:
            json.dump(evolved_context, f, indent=2, ensure_ascii=False)

        self.log_action("context_written", {"path": str(_EVOLVED_CONTEXT_PATH)})

        # 5. Save preference cache
        self.preference_model.save_cache()

        result = {
            "principles": len(principles),
            "adjustments": adjustments,
        }
        self.log_action("cycle_complete", result)
        return result
