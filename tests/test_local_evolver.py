import json
import tempfile
import time
from pathlib import Path

from vulca.digestion.local_evolver import LocalEvolver


class TestLocalEvolver:
    def test_no_data_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            assert result is None

    def test_insufficient_feedback_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            sessions_file = Path(td) / "sessions.jsonl"
            # 2 sessions — below minimum of 3 with feedback
            for i in range(2):
                entry = {
                    "session_id": f"s{i}", "tradition": "chinese_xieyi",
                    "user_feedback": "accepted",
                    "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.9, "L5": 0.75},
                    "weighted_total": 0.75,
                }
                with open(sessions_file, "a") as f:
                    f.write(json.dumps(entry) + "\n")

            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            assert result is None

    def test_sufficient_feedback_produces_evolved_context(self):
        with tempfile.TemporaryDirectory() as td:
            sessions_file = Path(td) / "sessions.jsonl"
            for i in range(5):
                entry = {
                    "session_id": f"s{i}", "tradition": "chinese_xieyi",
                    "user_feedback": "accepted",
                    "final_scores": {"L1": 0.8, "L2": 0.5, "L3": 0.9, "L4": 0.7, "L5": 0.85},
                    "weighted_total": 0.75,
                }
                with open(sessions_file, "a") as f:
                    f.write(json.dumps(entry) + "\n")

            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            assert result is not None
            assert "traditions" in result

    def test_evolved_context_written_to_file(self):
        with tempfile.TemporaryDirectory() as td:
            sessions_file = Path(td) / "sessions.jsonl"
            for i in range(5):
                entry = {
                    "session_id": f"s{i}", "tradition": "chinese_xieyi",
                    "user_feedback": "accepted",
                    "final_scores": {"L1": 0.8, "L2": 0.5, "L3": 0.9, "L4": 0.7, "L5": 0.85},
                    "weighted_total": 0.75,
                }
                with open(sessions_file, "a") as f:
                    f.write(json.dumps(entry) + "\n")

            evolver = LocalEvolver(data_dir=td)
            evolver.evolve()

            evolved_path = Path(td) / "evolved_context.json"
            assert evolved_path.exists()
            data = json.loads(evolved_path.read_text())
            assert "traditions" in data

    def test_evolve_skips_when_too_few_new_sessions(self, tmp_path):
        """Should return None when fewer than _MIN_NEW_SESSIONS sessions exist since last evolution."""
        # Write evolved_context.json with a very recent last_evolved_at timestamp
        evolved_path = tmp_path / "evolved_context.json"
        recent_ts = time.time() - 10  # 10 seconds ago
        evolved_path.write_text(json.dumps({
            "_meta": {"last_evolved_at": recent_ts},
            "traditions": {},
            "total_sessions": 0,
        }))

        # Write only 2 sessions (both newer than last_evolved_at, but below gate of 3)
        sessions_file = tmp_path / "sessions.jsonl"
        now = time.time()
        for i in range(2):
            entry = {
                "session_id": f"s{i}",
                "tradition": "chinese_xieyi",
                "timestamp": now + i,
                "user_feedback": "accepted",
                "final_scores": {"L1": 0.8, "L2": 0.5, "L3": 0.9, "L4": 0.7, "L5": 0.85},
                "weighted_total": 0.75,
            }
            with open(sessions_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

        evolver = LocalEvolver(data_dir=str(tmp_path))
        result = evolver.evolve()
        assert result is None

    def test_evolve_runs_with_enough_new_sessions(self, tmp_path):
        """Should run evolution when enough new sessions exist since last evolution."""
        # Write evolved_context.json with an OLD timestamp (24h ago)
        evolved_path = tmp_path / "evolved_context.json"
        old_ts = time.time() - 86400  # 24 hours ago
        evolved_path.write_text(json.dumps({
            "_meta": {"last_evolved_at": old_ts},
            "traditions": {},
            "total_sessions": 0,
        }))

        # Write 6 sessions with timestamps newer than old_ts
        sessions_file = tmp_path / "sessions.jsonl"
        now = time.time()
        for i in range(6):
            entry = {
                "session_id": f"s{i}",
                "tradition": "chinese_xieyi",
                "timestamp": now + i,
                "user_feedback": "accepted",
                "final_scores": {"L1": 0.8, "L2": 0.5, "L3": 0.9, "L4": 0.7, "L5": 0.85},
                "weighted_total": 0.75,
            }
            with open(sessions_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

        evolver = LocalEvolver(data_dir=str(tmp_path))
        result = evolver.evolve()
        assert result is not None
        assert "_meta" in result
        assert "last_evolved_at" in result["_meta"]


def test_evolve_writes_tradition_insights(tmp_path):
    """Evolution should write per-tradition insight files."""
    import time

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "evolved_context.json").write_text(json.dumps({"_meta": {"last_evolved_at": 0}}))

    sessions_file = data_dir / "sessions.jsonl"
    for i in range(8):
        session = {
            "session_id": f"s{i}", "tradition": "chinese_xieyi",
            "timestamp": time.time(), "weighted_total": 0.7 + i * 0.01,
            "scores": {"L1": 0.7, "L2": 0.6, "L3": 0.8, "L4": 0.7, "L5": 0.75},
            "user_feedback": "accepted", "eval_mode": "strict",
        }
        with open(sessions_file, "a") as f:
            f.write(json.dumps(session) + "\n")

    evolver = LocalEvolver(data_dir=str(data_dir))
    result = evolver.evolve()
    assert result is not None

    insights_path = data_dir / "evolved" / "chinese_xieyi" / "insights.json"
    assert insights_path.exists()
    insights = json.loads(insights_path.read_text())
    assert insights["tradition"] == "chinese_xieyi"
    assert "dimension_averages" in insights
    assert "score_history" in insights
    assert len(insights["score_history"]) == 8


def test_load_tradition_insights(tmp_path):
    from vulca.digestion.local_evolver import LocalEvolver

    data_dir = tmp_path / "data"
    (data_dir / "evolved" / "chinese_xieyi").mkdir(parents=True)
    insights = {"tradition": "chinese_xieyi", "dimension_averages": {"L1": 0.7}}
    (data_dir / "evolved" / "chinese_xieyi" / "insights.json").write_text(json.dumps(insights))

    evolver = LocalEvolver(data_dir=str(data_dir))
    result = evolver.load_tradition_insights("chinese_xieyi")
    assert result is not None
    assert result["dimension_averages"]["L1"] == 0.7

    # Non-existent tradition
    assert evolver.load_tradition_insights("nonexistent") is None
