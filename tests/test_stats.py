"""Tests for session statistics module."""
from __future__ import annotations

from vulca.stats import compute_session_stats


SAMPLE_SESSIONS = [
    {"session_id": "s1", "mode": "create", "tradition": "chinese_xieyi",
     "final_weighted_total": 0.82, "status": "completed", "total_rounds": 3,
     "created_at": 1711756800},
    {"session_id": "s2", "mode": "create", "tradition": "chinese_xieyi",
     "final_weighted_total": 0.75, "status": "completed", "total_rounds": 2,
     "created_at": 1711760400},
    {"session_id": "s3", "mode": "evaluate", "tradition": "brand_design",
     "final_weighted_total": 0.90, "status": "completed", "total_rounds": 1,
     "created_at": 1711764000},
    {"session_id": "s4", "mode": "create", "tradition": "brand_design",
     "final_weighted_total": 0.41, "status": "failed", "total_rounds": 0,
     "created_at": 1711767600},
]


class TestComputeSessionStats:
    def test_total_count(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        assert stats["total"] == 4

    def test_by_mode(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        assert stats["by_mode"]["create"] == 3
        assert stats["by_mode"]["evaluate"] == 1

    def test_by_tradition(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        traditions = {t["name"]: t for t in stats["by_tradition"]}
        assert "chinese_xieyi" in traditions
        assert traditions["chinese_xieyi"]["count"] == 2

    def test_score_distribution(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        dist = stats["score_distribution"]
        assert dist["min"] == 0.41
        assert dist["max"] == 0.90
        assert 0.7 < dist["mean"] < 0.8

    def test_anomalies_low_scores(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        assert len(stats["anomalies"]["low_scores"]) == 1

    def test_anomalies_failed(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        assert len(stats["anomalies"]["failed"]) == 1

    def test_filter_by_tradition(self):
        stats = compute_session_stats(SAMPLE_SESSIONS, tradition="brand_design")
        assert stats["total"] == 2

    def test_empty_sessions(self):
        stats = compute_session_stats([])
        assert stats["total"] == 0
        assert stats["score_distribution"]["mean"] == 0.0

    def test_top_and_bottom(self):
        stats = compute_session_stats(SAMPLE_SESSIONS)
        assert stats["top_sessions"][0]["session_id"] == "s3"
        assert stats["bottom_sessions"][0]["session_id"] == "s4"
