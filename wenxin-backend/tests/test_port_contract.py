"""Tests for pipeline port contract system."""

from __future__ import annotations

import pytest

from app.prototype.pipeline.port_contract import (
    ARCHIVIST_CONTRACT,
    CRITIC_CONTRACT,
    DRAFT_CONTRACT,
    DataType,
    PortDirection,
    PortSpec,
    QUEEN_CONTRACT,
    SCOUT_CONTRACT,
    StageContract,
    get_contract,
    list_contracts,
    validate_edge,
)


# ---------------------------------------------------------------------------
# 1. All stages registered
# ---------------------------------------------------------------------------

def test_all_stages_registered():
    """Verify all core stage contracts exist in the registry."""
    contracts = list_contracts()
    expected_core = {"scout", "draft", "critic", "queen", "archivist"}
    assert expected_core.issubset(set(contracts.keys()))


# ---------------------------------------------------------------------------
# 2. Scout contract ports
# ---------------------------------------------------------------------------

def test_scout_contract_ports():
    """Verify scout has correct input/output ports."""
    scout = get_contract("scout")
    assert scout is not None
    assert scout.stage_name == "scout"

    # Input ports
    in_types = scout.input_types()
    assert "pipeline_input" in in_types
    assert in_types["pipeline_input"] == DataType.PIPELINE_INPUT

    # Output ports
    out_types = scout.output_types()
    assert "evidence" in out_types
    assert out_types["evidence"] == DataType.EVIDENCE
    assert "evidence_pack" in out_types
    assert out_types["evidence_pack"] == DataType.EVIDENCE_PACK


# ---------------------------------------------------------------------------
# 3. validate_edge — compatible
# ---------------------------------------------------------------------------

def test_validate_edge_compatible():
    """scout.evidence -> critic.evidence is valid (same DataType)."""
    ok, msg = validate_edge("scout", "evidence", "critic", "evidence")
    assert ok is True
    assert msg == "ok"


# ---------------------------------------------------------------------------
# 4. validate_edge — incompatible
# ---------------------------------------------------------------------------

def test_validate_edge_incompatible():
    """scout.evidence -> critic.draft_candidates fails with type mismatch."""
    ok, msg = validate_edge("scout", "evidence", "critic", "draft_candidates")
    assert ok is False
    assert "Type mismatch" in msg
    assert "evidence" in msg
    assert "draft_candidates" in msg


# ---------------------------------------------------------------------------
# 5. validate_edge — unknown stage
# ---------------------------------------------------------------------------

def test_validate_edge_unknown_stage():
    """Unknown stage returns error."""
    ok, msg = validate_edge("nonexistent", "evidence", "critic", "evidence")
    assert ok is False
    assert "Unknown source stage" in msg

    ok2, msg2 = validate_edge("scout", "evidence", "nonexistent", "evidence")
    assert ok2 is False
    assert "Unknown target stage" in msg2


# ---------------------------------------------------------------------------
# 6. validate_edge — unknown port
# ---------------------------------------------------------------------------

def test_validate_edge_unknown_port():
    """Unknown port returns error."""
    ok, msg = validate_edge("scout", "nonexistent_port", "critic", "evidence")
    assert ok is False
    assert "has no output port" in msg

    ok2, msg2 = validate_edge("scout", "evidence", "critic", "nonexistent_port")
    assert ok2 is False
    assert "has no input port" in msg2


# ---------------------------------------------------------------------------
# 7. StageContract input_types / output_types
# ---------------------------------------------------------------------------

def test_stage_contract_input_output_types():
    """Verify input_types() and output_types() methods return correct dicts."""
    draft = get_contract("draft")
    assert draft is not None

    in_types = draft.input_types()
    assert isinstance(in_types, dict)
    assert "pipeline_input" in in_types
    assert "evidence" in in_types
    assert in_types["pipeline_input"] == DataType.PIPELINE_INPUT
    assert in_types["evidence"] == DataType.EVIDENCE

    out_types = draft.output_types()
    assert isinstance(out_types, dict)
    assert "draft_candidates" in out_types
    assert out_types["draft_candidates"] == DataType.DRAFT_CANDIDATES

    # Queen has both input and output plan_state
    queen = get_contract("queen")
    assert queen is not None
    assert "plan_state" in queen.input_types()
    assert "plan_state" in queen.output_types()
    assert queen.input_types()["plan_state"] == DataType.PLAN_STATE
    assert queen.output_types()["plan_state"] == DataType.PLAN_STATE


# ---------------------------------------------------------------------------
# 8. list_contracts
# ---------------------------------------------------------------------------

def test_list_contracts():
    """Verify list_contracts returns at least the 5 core contracts."""
    contracts = list_contracts()
    assert len(contracts) >= 5
    for name in ("scout", "draft", "critic", "queen", "archivist"):
        assert name in contracts
        assert isinstance(contracts[name], StageContract)


# ---------------------------------------------------------------------------
# 9. DataType completeness
# ---------------------------------------------------------------------------

def test_data_types_are_complete():
    """Verify all core DataType enum values are used in at least one contract.

    Phase 5 extended types (sketch, video, style, mask, audio, model_3d) are
    reserved for future media-type nodes and may not yet appear in any contract.
    """
    # Types not yet wired into always-loaded core contracts:
    # - SKETCH/VIDEO/STYLE/MASK/AUDIO/MODEL_3D: reserved for future media-type nodes
    # - SCORES: used by GATE_CONTRACT but overridden when graph.nodes is loaded
    FUTURE_TYPES = {
        DataType.SKETCH, DataType.VIDEO, DataType.STYLE,
        DataType.MASK, DataType.AUDIO, DataType.MODEL_3D,
        DataType.SCORES,
    }

    contracts = list_contracts()
    used_types: set[DataType] = set()
    for contract in contracts.values():
        for port in contract.input_ports:
            used_types.add(port.data_type)
        for port in contract.output_ports:
            used_types.add(port.data_type)

    required_types = set(DataType) - FUTURE_TYPES
    unused = required_types - used_types
    assert unused == set(), (
        f"Core DataType values not used in any contract: "
        f"{[t.value for t in unused]}"
    )


# ---------------------------------------------------------------------------
# Bonus: PortSpec frozen immutability + validate_connection
# ---------------------------------------------------------------------------

def test_port_spec_frozen():
    """PortSpec is frozen — attributes cannot be reassigned."""
    port = PortSpec("test", DataType.EVIDENCE, PortDirection.INPUT)
    with pytest.raises(AttributeError):
        port.name = "changed"  # type: ignore[misc]


def test_validate_connection_method():
    """StageContract.validate_connection checks data type match."""
    src = PortSpec("evidence", DataType.EVIDENCE, PortDirection.OUTPUT)
    tgt_ok = PortSpec("evidence", DataType.EVIDENCE, PortDirection.INPUT)
    tgt_bad = PortSpec("candidates", DataType.DRAFT_CANDIDATES, PortDirection.INPUT)

    contract = StageContract(stage_name="test")
    assert contract.validate_connection(src, tgt_ok) is True
    assert contract.validate_connection(src, tgt_bad) is False


def test_contract_module_constants():
    """Module-level contract constants match their registry entries."""
    assert SCOUT_CONTRACT is get_contract("scout")
    assert DRAFT_CONTRACT is get_contract("draft")
    assert CRITIC_CONTRACT is get_contract("critic")
    assert QUEEN_CONTRACT is get_contract("queen")
    assert ARCHIVIST_CONTRACT is get_contract("archivist")
