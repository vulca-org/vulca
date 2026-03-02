"""Archivist Agent data types — ArchivistInput / ArchivistOutput."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "ArchivistInput",
    "ArchivistOutput",
]


@dataclass
class ArchivistInput:
    """Input to the Archivist — the complete pipeline output + all configs."""

    task_id: str
    subject: str
    cultural_tradition: str
    pipeline_output_dict: dict           # PipelineOutput.to_dict()
    scout_evidence_dict: dict            # ScoutEvidence.to_dict()
    critique_dicts: list[dict]           # List of CritiqueOutput.to_dict() per round
    queen_dicts: list[dict]              # List of QueenOutput.to_dict() per round
    draft_config_dict: dict = field(default_factory=dict)
    critic_config_dict: dict = field(default_factory=dict)
    queen_config_dict: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "cultural_tradition": self.cultural_tradition,
            "pipeline_output": self.pipeline_output_dict,
            "scout_evidence": self.scout_evidence_dict,
            "critique_dicts": self.critique_dicts,
            "queen_dicts": self.queen_dicts,
            "draft_config": self.draft_config_dict,
            "critic_config": self.critic_config_dict,
            "queen_config": self.queen_config_dict,
        }


@dataclass
class ArchivistOutput:
    """Output of the Archivist — paths to generated archive artifacts."""

    task_id: str
    evidence_chain_path: str = ""
    critique_card_path: str = ""
    params_snapshot_path: str = ""
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "evidence_chain_path": self.evidence_chain_path,
            "critique_card_path": self.critique_card_path,
            "params_snapshot_path": self.params_snapshot_path,
            "success": self.success,
            "error": self.error,
        }
