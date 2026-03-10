"""Tests for FewShotUpdater — few-shot example selection from sessions."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.prototype.digestion.few_shot_updater import (
    MAX_EXAMPLES_PER_TRADITION,
    MAX_TOTAL_EXAMPLES,
    MIN_SCORE_THRESHOLD,
    FewShotUpdater,
)


def _make_session(
    session_id: str = "s1",
    tradition: str = "chinese_xieyi",
    subject: str = "mountain",
    intent: str = "mountain in ink wash",
    weighted_total: float = 0.80,
    scores: dict | None = None,
) -> dict:
    """Helper to build a session dict matching sessions.jsonl format."""
    if scores is None:
        scores = {"L1": 0.80, "L2": 0.75, "L3": 0.85, "L4": 0.70, "L5": 0.68}
    return {
        "session_id": session_id,
        "mode": "create",
        "tradition": tradition,
        "subject": subject,
        "intent": intent,
        "final_scores": scores,
        "final_weighted_total": weighted_total,
    }


def _write_sessions(path: Path, sessions: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for s in sessions:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


class TestFewShotUpdaterEmpty:
    """Tests with no sessions / empty data."""

    def test_no_sessions_file(self, tmp_path: Path) -> None:
        updater = FewShotUpdater(
            sessions_path=str(tmp_path / "missing.jsonl"),
            evolved_path=str(tmp_path / "evolved.json"),
        )
        assert updater.update() == 0

    def test_empty_sessions(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        sessions_path.write_text("")
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(tmp_path / "evolved.json"),
        )
        assert updater.update() == 0

    def test_all_below_threshold(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        _write_sessions(sessions_path, [
            _make_session(weighted_total=0.50),
            _make_session(session_id="s2", weighted_total=0.60),
        ])
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(tmp_path / "evolved.json"),
        )
        assert updater.update() == 0


class TestFewShotSelection:
    """Tests for filtering and selection logic."""

    def test_selects_high_scoring(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        evolved_path = tmp_path / "evolved.json"
        _write_sessions(sessions_path, [
            _make_session(session_id="high", weighted_total=0.85),
            _make_session(session_id="low", weighted_total=0.50),
        ])
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(evolved_path),
        )
        count = updater.update()
        assert count == 1

        ctx = json.loads(evolved_path.read_text())
        examples = ctx["few_shot_examples"]
        assert len(examples) == 1
        assert examples[0]["session_id"] == "high"
        assert examples[0]["score"] == 0.85

    def test_per_tradition_cap(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        evolved_path = tmp_path / "evolved.json"
        # Create more sessions than MAX_EXAMPLES_PER_TRADITION for one tradition
        sessions = [
            _make_session(
                session_id=f"s{i}",
                tradition="chinese_xieyi",
                weighted_total=0.80 + i * 0.01,
            )
            for i in range(MAX_EXAMPLES_PER_TRADITION + 3)
        ]
        _write_sessions(sessions_path, sessions)
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(evolved_path),
        )
        count = updater.update()
        assert count == MAX_EXAMPLES_PER_TRADITION

        ctx = json.loads(evolved_path.read_text())
        examples = ctx["few_shot_examples"]
        assert len(examples) == MAX_EXAMPLES_PER_TRADITION
        # Verify they are the highest-scoring ones
        scores = [e["score"] for e in examples]
        assert scores == sorted(scores, reverse=True)

    def test_global_cap(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        evolved_path = tmp_path / "evolved.json"
        # Create sessions across many traditions to exceed global cap
        traditions = [f"tradition_{i}" for i in range(10)]
        sessions = []
        for i, t in enumerate(traditions):
            for j in range(MAX_EXAMPLES_PER_TRADITION):
                sessions.append(
                    _make_session(
                        session_id=f"s-{t}-{j}",
                        tradition=t,
                        weighted_total=0.76 + i * 0.01 + j * 0.001,
                    )
                )
        _write_sessions(sessions_path, sessions)
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(evolved_path),
        )
        count = updater.update()
        assert count == MAX_TOTAL_EXAMPLES

    def test_multiple_traditions(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        evolved_path = tmp_path / "evolved.json"
        _write_sessions(sessions_path, [
            _make_session(session_id="xieyi1", tradition="chinese_xieyi", weighted_total=0.85),
            _make_session(session_id="wabi1", tradition="japanese_wabi_sabi", weighted_total=0.80),
            _make_session(session_id="ren1", tradition="european_renaissance", weighted_total=0.78),
        ])
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(evolved_path),
        )
        count = updater.update()
        assert count == 3

        ctx = json.loads(evolved_path.read_text())
        traditions = {e["tradition"] for e in ctx["few_shot_examples"]}
        assert traditions == {"chinese_xieyi", "japanese_wabi_sabi", "european_renaissance"}


class TestFewShotFormat:
    """Tests for the output format of few-shot examples."""

    def test_example_fields(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        evolved_path = tmp_path / "evolved.json"
        _write_sessions(sessions_path, [
            _make_session(
                session_id="fmt1",
                tradition="chinese_xieyi",
                subject="bamboo",
                intent="bamboo in wind",
                weighted_total=0.80,
                scores={"L1": 0.85, "L2": 0.70, "L3": 0.90, "L4": 0.65, "L5": 0.60},
            ),
        ])
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(evolved_path),
        )
        updater.update()

        ctx = json.loads(evolved_path.read_text())
        ex = ctx["few_shot_examples"][0]
        assert ex["tradition"] == "chinese_xieyi"
        assert ex["subject"] == "bamboo"
        assert ex["intent"] == "bamboo in wind"
        assert ex["score"] == 0.80
        assert ex["session_id"] == "fmt1"
        assert isinstance(ex["key_strengths"], list)
        # L1=0.85 and L3=0.90 are >= 0.8
        assert "L1" in ex["key_strengths"]
        assert "L3" in ex["key_strengths"]

    def test_preserves_existing_evolved_context(self, tmp_path: Path) -> None:
        sessions_path = tmp_path / "sessions.jsonl"
        evolved_path = tmp_path / "evolved.json"

        # Pre-populate evolved context with other data
        evolved_path.write_text(json.dumps({
            "tradition_weights": {"chinese_xieyi": {"visual_perception": 0.20}},
            "cultures": {"test_concept": {"name": "test"}},
            "evolutions": 5,
        }))

        _write_sessions(sessions_path, [
            _make_session(weighted_total=0.80),
        ])
        updater = FewShotUpdater(
            sessions_path=str(sessions_path),
            evolved_path=str(evolved_path),
        )
        updater.update()

        ctx = json.loads(evolved_path.read_text())
        # Original data preserved
        assert ctx["tradition_weights"]["chinese_xieyi"]["visual_perception"] == 0.20
        assert "test_concept" in ctx["cultures"]
        assert ctx["evolutions"] == 5
        # New data added
        assert "few_shot_examples" in ctx
        assert len(ctx["few_shot_examples"]) == 1


class TestFewShotScoreExtraction:
    """Tests for score extraction from different session formats."""

    def test_final_weighted_total(self, tmp_path: Path) -> None:
        updater = FewShotUpdater(
            sessions_path=str(tmp_path / "s.jsonl"),
            evolved_path=str(tmp_path / "e.json"),
        )
        session = {"final_weighted_total": 0.82}
        assert updater._get_score(session) == 0.82

    def test_fallback_to_final_scores_weighted_total(self, tmp_path: Path) -> None:
        updater = FewShotUpdater(
            sessions_path=str(tmp_path / "s.jsonl"),
            evolved_path=str(tmp_path / "e.json"),
        )
        session = {"final_scores": {"weighted_total": 0.75}}
        assert updater._get_score(session) == 0.75

    def test_zero_score_when_missing(self, tmp_path: Path) -> None:
        updater = FewShotUpdater(
            sessions_path=str(tmp_path / "s.jsonl"),
            evolved_path=str(tmp_path / "e.json"),
        )
        assert updater._get_score({}) == 0.0

    def test_strengths_extraction(self) -> None:
        session = {
            "final_scores": {
                "L1": 0.85, "L2": 0.60, "L3": 0.92, "L4": 0.45, "L5": 0.81,
                "weighted_total": 0.73,
            }
        }
        strengths = FewShotUpdater._extract_strengths(session)
        assert "L1" in strengths
        assert "L3" in strengths
        assert "L5" in strengths
        assert "L2" not in strengths
        assert "L4" not in strengths
        assert "weighted_total" not in strengths


class TestFewShotPromptInjection:
    """Test that few-shot examples are consumed by get_evolved_prompt_context."""

    def test_few_shot_in_prompt_context(self, tmp_path: Path, monkeypatch) -> None:
        """Verify get_evolved_prompt_context includes few-shot examples."""
        evolved_path = tmp_path / "evolved_context.json"
        evolved_path.write_text(json.dumps({
            "evolutions": 1,
            "tradition_weights": {},
            "few_shot_examples": [
                {
                    "tradition": "chinese_xieyi",
                    "subject": "bamboo",
                    "intent": "bamboo in wind",
                    "score": 0.85,
                    "session_id": "s1",
                    "key_strengths": ["L1", "L3"],
                },
            ],
        }))

        # Monkeypatch the path used by _build_evolved_context
        import app.prototype.cultural_pipelines.cultural_weights as cw
        monkeypatch.setattr(cw, "_EVOLVED_CONTEXT_PATH", str(evolved_path))
        # Clear cache
        cw._evolved_prompt_cache.clear()

        result = cw.get_evolved_prompt_context("chinese_xieyi")
        assert "Successful examples" in result
        assert "bamboo" in result
        assert "0.85" in result
        assert "L1" in result

    def test_no_few_shot_no_regression(self, tmp_path: Path, monkeypatch) -> None:
        """Without few_shot_examples, prompt context should still work."""
        evolved_path = tmp_path / "evolved_context.json"
        evolved_path.write_text(json.dumps({
            "evolutions": 1,
            "tradition_weights": {
                "chinese_xieyi": {
                    "visual_perception": 0.20,
                    "technical_analysis": 0.20,
                    "cultural_context": 0.25,
                    "critical_interpretation": 0.15,
                    "philosophical_aesthetic": 0.20,
                }
            },
        }))

        import app.prototype.cultural_pipelines.cultural_weights as cw
        monkeypatch.setattr(cw, "_EVOLVED_CONTEXT_PATH", str(evolved_path))
        cw._evolved_prompt_cache.clear()

        result = cw.get_evolved_prompt_context("chinese_xieyi")
        # Should still contain weight hints
        assert "Priority dimensions" in result
        # Should NOT contain few-shot section
        assert "Successful examples" not in result

    def test_few_shot_tradition_filtering(self, tmp_path: Path, monkeypatch) -> None:
        """Only examples matching the requested tradition should appear."""
        evolved_path = tmp_path / "evolved_context.json"
        evolved_path.write_text(json.dumps({
            "evolutions": 1,
            "tradition_weights": {},
            "few_shot_examples": [
                {
                    "tradition": "chinese_xieyi",
                    "subject": "bamboo",
                    "score": 0.85,
                    "key_strengths": ["L1"],
                },
                {
                    "tradition": "japanese_wabi_sabi",
                    "subject": "tea bowl",
                    "score": 0.82,
                    "key_strengths": ["L3"],
                },
            ],
        }))

        import app.prototype.cultural_pipelines.cultural_weights as cw
        monkeypatch.setattr(cw, "_EVOLVED_CONTEXT_PATH", str(evolved_path))
        cw._evolved_prompt_cache.clear()

        result = cw.get_evolved_prompt_context("chinese_xieyi")
        assert "bamboo" in result
        assert "tea bowl" not in result
