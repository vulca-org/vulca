"""Port contracts for pipeline stage data flow.

Each pipeline stage declares its input and output ports with explicit
data types.  This enables:
- Type checking at graph construction time
- Auto-documentation of data flow
- Future ComfyUI-style visual editor type matching
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PortDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"


class DataType(Enum):
    """Canonical data types flowing between pipeline stages."""
    PIPELINE_INPUT = "pipeline_input"        # PipelineInput
    EVIDENCE = "evidence"                     # ScoutEvidence dict
    EVIDENCE_PACK = "evidence_pack"          # EvidencePack (typed)
    DRAFT_CANDIDATES = "draft_candidates"    # list[DraftCandidate]
    CRITIQUE = "critique"                     # CritiqueOutput
    PLAN_STATE = "plan_state"                # PlanState
    QUEEN_DECISION = "queen_decision"        # QueenDecision
    PIPELINE_OUTPUT = "pipeline_output"      # PipelineOutput
    ARCHIVE = "archive"                      # ArchivistOutput
    SKILL_RESULTS = "skill_results"          # list[dict] from pipeline_hook

    # Extended types for node editor (Phase 5)
    IMAGE = "image"              # Raw image data
    TEXT = "text"                # Text/prompt
    SKETCH = "sketch"            # Sketch/line art
    MASK = "mask"                # Mask/region
    AUDIO = "audio"              # Audio data
    VIDEO = "video"              # Video data
    MODEL_3D = "model_3d"        # 3D model
    CONFIG = "config"            # Configuration params
    STYLE = "style"              # Style vector
    SCORES = "scores"            # L1-L5 scores
    DECISION = "decision"        # Queen decision


@dataclass(frozen=True)
class PortSpec:
    """Specification for a single input or output port."""
    name: str
    data_type: DataType
    direction: PortDirection
    required: bool = True
    description: str = ""


@dataclass
class StageContract:
    """Declares the data contract for a pipeline stage."""
    stage_name: str
    input_ports: list[PortSpec] = field(default_factory=list)
    output_ports: list[PortSpec] = field(default_factory=list)
    description: str = ""

    def input_types(self) -> dict[str, DataType]:
        return {p.name: p.data_type for p in self.input_ports}

    def output_types(self) -> dict[str, DataType]:
        return {p.name: p.data_type for p in self.output_ports}

    def validate_connection(self, source_port: PortSpec, target_port: PortSpec) -> bool:
        """Check if source output port can connect to target input port."""
        return source_port.data_type == target_port.data_type


# ---------------------------------------------------------------------------
# Stage contract registry
# ---------------------------------------------------------------------------

_STAGE_CONTRACTS: dict[str, StageContract] = {}


def register_contract(contract: StageContract) -> StageContract:
    """Register a stage contract."""
    _STAGE_CONTRACTS[contract.stage_name] = contract
    return contract


def get_contract(stage_name: str) -> StageContract | None:
    """Look up a registered stage contract."""
    return _STAGE_CONTRACTS.get(stage_name)


def list_contracts() -> dict[str, StageContract]:
    """Return all registered stage contracts."""
    return dict(_STAGE_CONTRACTS)


def validate_edge(source_stage: str, source_port: str,
                  target_stage: str, target_port: str) -> tuple[bool, str]:
    """Validate that a graph edge connecting two ports is type-compatible."""
    src = _STAGE_CONTRACTS.get(source_stage)
    tgt = _STAGE_CONTRACTS.get(target_stage)
    if not src:
        return False, f"Unknown source stage: {source_stage}"
    if not tgt:
        return False, f"Unknown target stage: {target_stage}"

    src_out = {p.name: p for p in src.output_ports}
    tgt_in = {p.name: p for p in tgt.input_ports}

    if source_port not in src_out:
        return False, f"Stage '{source_stage}' has no output port '{source_port}'"
    if target_port not in tgt_in:
        return False, f"Stage '{target_stage}' has no input port '{target_port}'"

    if src_out[source_port].data_type != tgt_in[target_port].data_type:
        return False, (
            f"Type mismatch: {source_stage}.{source_port} outputs "
            f"{src_out[source_port].data_type.value} but "
            f"{target_stage}.{target_port} expects "
            f"{tgt_in[target_port].data_type.value}"
        )

    return True, "ok"


# ---------------------------------------------------------------------------
# Built-in stage contracts
# ---------------------------------------------------------------------------

SCOUT_CONTRACT = register_contract(StageContract(
    stage_name="scout",
    input_ports=[
        PortSpec("pipeline_input", DataType.PIPELINE_INPUT, PortDirection.INPUT,
                 description="Task specification with subject and tradition"),
    ],
    output_ports=[
        PortSpec("evidence", DataType.EVIDENCE, PortDirection.OUTPUT,
                 description="Gathered cultural evidence as dict"),
        PortSpec("evidence_pack", DataType.EVIDENCE_PACK, PortDirection.OUTPUT,
                 description="Structured evidence pack with anchors"),
    ],
    description="Gather cultural evidence and terminology for the subject",
))

DRAFT_CONTRACT = register_contract(StageContract(
    stage_name="draft",
    input_ports=[
        PortSpec("pipeline_input", DataType.PIPELINE_INPUT, PortDirection.INPUT),
        PortSpec("evidence", DataType.EVIDENCE, PortDirection.INPUT),
        PortSpec("evidence_pack", DataType.EVIDENCE_PACK, PortDirection.INPUT, required=False),
        PortSpec("plan_state", DataType.PLAN_STATE, PortDirection.INPUT, required=False,
                 description="From Queen's rerun decision (rounds 2+)"),
        PortSpec("skill_results", DataType.SKILL_RESULTS, PortDirection.INPUT, required=False,
                 description="Pre-processing results from skill marketplace hooks"),
    ],
    output_ports=[
        PortSpec("draft_candidates", DataType.DRAFT_CANDIDATES, PortDirection.OUTPUT,
                 description="Generated image candidates"),
    ],
    description="Generate art candidates from evidence and cultural context",
))

CRITIC_CONTRACT = register_contract(StageContract(
    stage_name="critic",
    input_ports=[
        PortSpec("pipeline_input", DataType.PIPELINE_INPUT, PortDirection.INPUT),
        PortSpec("evidence", DataType.EVIDENCE, PortDirection.INPUT),
        PortSpec("draft_candidates", DataType.DRAFT_CANDIDATES, PortDirection.INPUT),
    ],
    output_ports=[
        PortSpec("critique", DataType.CRITIQUE, PortDirection.OUTPUT,
                 description="Scored candidates with L1-L5 dimension scores"),
    ],
    description="Evaluate candidates across L1-L5 cultural dimensions",
))

QUEEN_CONTRACT = register_contract(StageContract(
    stage_name="queen",
    input_ports=[
        PortSpec("critique", DataType.CRITIQUE, PortDirection.INPUT),
        PortSpec("plan_state", DataType.PLAN_STATE, PortDirection.INPUT),
    ],
    output_ports=[
        PortSpec("queen_decision", DataType.QUEEN_DECISION, PortDirection.OUTPUT,
                 description="Accept/rerun/stop decision with target dimensions"),
        PortSpec("plan_state", DataType.PLAN_STATE, PortDirection.OUTPUT,
                 description="Updated plan state for next round"),
    ],
    description="Decide whether to accept, rerun, or stop the pipeline",
))

ARCHIVIST_CONTRACT = register_contract(StageContract(
    stage_name="archivist",
    input_ports=[
        PortSpec("pipeline_output", DataType.PIPELINE_OUTPUT, PortDirection.INPUT),
        PortSpec("evidence", DataType.EVIDENCE, PortDirection.INPUT),
        PortSpec("critique", DataType.CRITIQUE, PortDirection.INPUT),
        PortSpec("queen_decision", DataType.QUEEN_DECISION, PortDirection.INPUT),
    ],
    output_ports=[
        PortSpec("archive", DataType.ARCHIVE, PortDirection.OUTPUT),
    ],
    description="Archive the pipeline run results and artifacts",
))

# ---------------------------------------------------------------------------
# Phase 5 node editor contracts
# ---------------------------------------------------------------------------

SKILL_CONTRACT = register_contract(StageContract(
    stage_name="skill",
    input_ports=[
        PortSpec("pipeline_input", DataType.PIPELINE_INPUT, PortDirection.INPUT),
        PortSpec("data_in", DataType.TEXT, PortDirection.INPUT, required=False),
    ],
    output_ports=[
        PortSpec("skill_results", DataType.SKILL_RESULTS, PortDirection.OUTPUT),
    ],
    description="Execute a skill from the marketplace",
))

PROCESSING_CONTRACT = register_contract(StageContract(
    stage_name="processing",
    input_ports=[
        PortSpec("image_in", DataType.IMAGE, PortDirection.INPUT),
        PortSpec("config", DataType.CONFIG, PortDirection.INPUT, required=False),
    ],
    output_ports=[
        PortSpec("image_out", DataType.IMAGE, PortDirection.OUTPUT),
    ],
    description="Apply image processing operations",
))

GATE_CONTRACT = register_contract(StageContract(
    stage_name="gate",
    input_ports=[
        PortSpec("scores", DataType.SCORES, PortDirection.INPUT),
        PortSpec("config", DataType.CONFIG, PortDirection.INPUT, required=False),
    ],
    output_ports=[
        PortSpec("decision", DataType.DECISION, PortDirection.OUTPUT),
    ],
    description="Quality gate with conditional routing",
))

INPUT_CONTRACT = register_contract(StageContract(
    stage_name="input",
    input_ports=[],
    output_ports=[
        PortSpec("data_out", DataType.TEXT, PortDirection.OUTPUT),
    ],
    description="External data input node",
))

OUTPUT_CONTRACT = register_contract(StageContract(
    stage_name="output",
    input_ports=[
        PortSpec("data_in", DataType.PIPELINE_OUTPUT, PortDirection.INPUT),
    ],
    output_ports=[],
    description="Pipeline output/export node",
))
