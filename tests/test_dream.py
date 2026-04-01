import json
import time
import pytest
from pathlib import Path


def _write_sessions(data_dir: Path, count: int, tradition: str = "chinese_xieyi", base_time: float = 0):
    sessions_file = data_dir / "sessions.jsonl"
    for i in range(count):
        session = {
            "session_id": f"s{i}",
            "tradition": tradition,
            "timestamp": base_time + i if base_time else time.time(),
            "weighted_total": 0.7 + (i % 5) * 0.02,
            "scores": {"L1": 0.7, "L2": 0.6, "L3": 0.8, "L4": 0.7, "L5": 0.75},
            "final_scores": {"L1": 0.7, "L2": 0.6, "L3": 0.8, "L4": 0.7, "L5": 0.75},
            "user_feedback": "accepted",
            "eval_mode": "strict",
            "deviations": {"L1": "traditional", "L2": "traditional", "L3": "traditional", "L4": "traditional", "L5": "intentional_departure"},
        }
        with open(sessions_file, "a") as f:
            f.write(json.dumps(session) + "\n")


def test_should_run_gates(tmp_path):
    from vulca.digestion.dream import DreamConsolidator
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dc = DreamConsolidator(data_dir=str(data_dir))

    # No sessions at all → False
    assert dc.should_run() is False

    # Add 10 sessions but recent dream run → False
    _write_sessions(data_dir, 10)
    (data_dir / "evolved").mkdir(parents=True, exist_ok=True)
    (data_dir / "evolved" / "_dream_meta.json").write_text(json.dumps({"last_run": time.time()}))
    assert dc.should_run() is False

    # Old dream run + enough sessions → True
    (data_dir / "evolved" / "_dream_meta.json").write_text(json.dumps({"last_run": time.time() - 90000}))
    assert dc.should_run() is True


def test_run_produces_insights(tmp_path):
    from vulca.digestion.dream import DreamConsolidator
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_sessions(data_dir, 12, tradition="chinese_xieyi")

    dc = DreamConsolidator(data_dir=str(data_dir))
    result = dc.run()

    assert result["status"] == "completed"
    assert "chinese_xieyi" in result["traditions_updated"]
    assert result["sessions_analyzed"] == 12

    insights_path = data_dir / "evolved" / "chinese_xieyi" / "insights.json"
    assert insights_path.exists()
    insights = json.loads(insights_path.read_text())
    assert insights["tradition"] == "chinese_xieyi"
    assert "dimension_averages" in insights
    assert len(insights["score_history"]) == 12


def test_run_handles_multiple_traditions(tmp_path):
    from vulca.digestion.dream import DreamConsolidator
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_sessions(data_dir, 5, tradition="chinese_xieyi")
    _write_sessions(data_dir, 5, tradition="japanese_traditional")

    dc = DreamConsolidator(data_dir=str(data_dir))
    result = dc.run()

    assert result["status"] == "completed"
    assert len(result["traditions_updated"]) == 2


def test_run_records_completion(tmp_path):
    from vulca.digestion.dream import DreamConsolidator
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_sessions(data_dir, 5)

    dc = DreamConsolidator(data_dir=str(data_dir))
    dc.run()

    meta_path = data_dir / "evolved" / "_dream_meta.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text())
    assert "last_run" in meta
    assert meta["last_run"] > 0


def test_deviation_filter_innovation_signals(tmp_path):
    from vulca.digestion.dream import DreamConsolidator
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Write sessions where L5 has >30% intentional_departure
    sessions_file = data_dir / "sessions.jsonl"
    for i in range(10):
        dev_l5 = "intentional_departure" if i < 5 else "traditional"
        session = {
            "session_id": f"s{i}", "tradition": "chinese_xieyi",
            "timestamp": time.time(), "weighted_total": 0.7,
            "scores": {"L1": 0.7, "L2": 0.5, "L3": 0.8, "L4": 0.7, "L5": 0.6},
            "final_scores": {"L1": 0.7, "L2": 0.5, "L3": 0.8, "L4": 0.7, "L5": 0.6},
            "user_feedback": "accepted", "eval_mode": "strict",
            "deviations": {"L1": "traditional", "L2": "traditional", "L3": "traditional", "L4": "traditional", "L5": dev_l5},
        }
        with open(sessions_file, "a") as f:
            f.write(json.dumps(session) + "\n")

    dc = DreamConsolidator(data_dir=str(data_dir))
    result = dc.run()
    assert result["status"] == "completed"

    insights = json.loads((data_dir / "evolved" / "chinese_xieyi" / "insights.json").read_text())
    # L5 should be in innovation_signals (50% intentional_departure > 30% threshold)
    assert "L5" in insights["innovation_signals"]
    # L5 should NOT be in weak_dimensions (filtered out)
    assert "L5" not in insights["weak_dimensions"]
