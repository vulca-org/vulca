"""Pipeline runner — thin wrapper around PipelineOrchestrator.

All execution logic lives in the orchestrator. This module preserves the
original ``run_pipeline()`` signature for backward compatibility.
"""

from __future__ import annotations

from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.queen_config import QueenConfig
try:
    from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
except ImportError:
    PipelineOrchestrator = None  # type: ignore[misc,assignment]
from app.prototype.pipeline.pipeline_types import (
    PipelineInput,
    PipelineOutput,
)


def run_pipeline(
    pipeline_input: PipelineInput,
    draft_config: DraftConfig | None = None,
    critic_config: CriticConfig | None = None,
    queen_config: QueenConfig | None = None,
) -> PipelineOutput:
    """Execute the full Scout → Draft → Critic → Queen pipeline.

    This is a backward-compatible wrapper: it creates a
    :class:`PipelineOrchestrator` and calls :meth:`run_sync`.
    """
    orchestrator = PipelineOrchestrator(
        draft_config=draft_config,
        critic_config=critic_config,
        queen_config=queen_config,
        enable_hitl=False,
        enable_archivist=False,  # Original run_pipeline didn't call Archivist
    )
    return orchestrator.run_sync(pipeline_input)
