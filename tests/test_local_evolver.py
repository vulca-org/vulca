import json
import tempfile
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
