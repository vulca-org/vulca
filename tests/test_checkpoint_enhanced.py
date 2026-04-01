import json
import pytest
from pathlib import Path


def test_save_and_load_node_checkpoint(tmp_path):
    from vulca.pipeline.checkpoint import save_node_checkpoint, load_node_checkpoint

    session_id = "test-session-123"
    ctx_data = {
        "scores": {"L1": 0.7, "L2": 0.8},
        "weighted_total": 0.75,
        "image_b64": "very_long_base64_string_here" * 100,
        "decision": "rerun",
    }

    save_node_checkpoint(session_id, round_num=1, node_name="evaluate", ctx_data=ctx_data, base_dir=str(tmp_path))

    loaded = load_node_checkpoint(session_id, round_num=1, node_name="evaluate", base_dir=str(tmp_path))
    assert loaded is not None
    assert loaded["scores"]["L1"] == 0.7
    assert loaded["weighted_total"] == 0.75
    assert loaded["decision"] == "rerun"
    # image_b64 should be stripped
    assert loaded.get("image_b64") != ctx_data["image_b64"]


def test_load_latest_checkpoint(tmp_path):
    from vulca.pipeline.checkpoint import save_node_checkpoint, load_node_checkpoint

    session_id = "test-latest"
    save_node_checkpoint(session_id, 1, "generate", {"step": "gen1"}, base_dir=str(tmp_path))
    save_node_checkpoint(session_id, 1, "evaluate", {"step": "eval1"}, base_dir=str(tmp_path))
    save_node_checkpoint(session_id, 2, "generate", {"step": "gen2"}, base_dir=str(tmp_path))

    latest = load_node_checkpoint(session_id, base_dir=str(tmp_path))
    assert latest is not None
    assert latest["step"] == "gen2"  # Round 2 is latest


def test_list_checkpoints(tmp_path):
    from vulca.pipeline.checkpoint import save_node_checkpoint, list_checkpoints

    session_id = "test-list"
    save_node_checkpoint(session_id, 1, "generate", {"x": 1}, base_dir=str(tmp_path))
    save_node_checkpoint(session_id, 1, "evaluate", {"x": 2}, base_dir=str(tmp_path))

    cps = list_checkpoints(session_id, base_dir=str(tmp_path))
    assert len(cps) == 2
    assert any(cp["node_name"] == "generate" for cp in cps)
    assert any(cp["node_name"] == "evaluate" for cp in cps)


def test_load_nonexistent_returns_none(tmp_path):
    from vulca.pipeline.checkpoint import load_node_checkpoint
    result = load_node_checkpoint("nonexistent", base_dir=str(tmp_path))
    assert result is None
