"""Pipeline event types for streaming and HITL."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """All pipeline event types."""

    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    DECISION_MADE = "decision_made"
    HUMAN_REQUIRED = "human_required"
    HUMAN_RECEIVED = "human_received"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    SESSION_DIGEST = "session_digest"
    SUBSTAGE_STARTED = "substage_started"
    SUBSTAGE_COMPLETED = "substage_completed"

    # Phase 5 node editor events
    NODE_EXPANDED = "node_expanded"
    NODE_COLLAPSED = "node_collapsed"
    INLINE_PREVIEW_DATA = "inline_preview_data"
    SKILL_STARTED = "skill_started"
    SKILL_COMPLETED = "skill_completed"
    FLOW_DECISION = "flow_decision"
    MUTE_TOGGLED = "mute_toggled"
    BYPASS_TOGGLED = "bypass_toggled"


@dataclass
class PipelineEvent:
    """A single event emitted during pipeline execution."""

    event_type: EventType
    stage: str = ""           # "scout" | "draft" | "critic" | "queen" | "archivist"
    round_num: int = 0
    payload: dict = field(default_factory=dict)
    timestamp_ms: int = 0     # monotonic offset from pipeline start

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "stage": self.stage,
            "round_num": self.round_num,
            "payload": self.payload,
            "timestamp_ms": self.timestamp_ms,
        }
