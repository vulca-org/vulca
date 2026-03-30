"""Tests that stats correctly reads scores from real pipeline output format.

The pipeline writes 'weighted_total' to sessions.jsonl (via PipelineOutput.to_dict()),
but stats.py must read this field correctly — not a different field name.
"""
from __future__ import annotations

from vulca.stats import compute_session_stats


# Real pipeline output format — uses "weighted_total", NOT "final_weighted_total"
REAL_FORMAT_SESSIONS = [
    {"session_id": "r1", "mode": "create", "tradition": "chinese_xieyi",
     "weighted_total": 0.915, "status": "completed", "total_rounds": 1,
     "created_at": 1711756800},
    {"session_id": "r2", "mode": "create", "tradition": "brand_design",
     "weighted_total": 0.922, "status": "completed", "total_rounds": 1,
     "created_at": 1711760400},
    {"session_id": "r3", "mode": "create", "tradition": "japanese_traditional",
     "weighted_total": 0.732, "status": "completed", "total_rounds": 2,
     "created_at": 1711764000},
]


class TestStatsReadsRealPipelineFormat:
    """Stats module must read 'weighted_total' — the field pipeline actually writes."""

    def test_scores_are_not_zero(self):
        """Core regression: scores from real format must NOT be 0.00."""
        stats = compute_session_stats(REAL_FORMAT_SESSIONS)
        dist = stats["score_distribution"]
        assert dist["mean"] > 0, f"Mean score is {dist['mean']} — stats is reading wrong field"
        assert dist["max"] > 0, f"Max score is {dist['max']} — stats is reading wrong field"
        assert dist["min"] > 0, f"Min score is {dist['min']} — stats is reading wrong field"

    def test_mean_score_matches_data(self):
        """Mean of [0.915, 0.922, 0.732] ≈ 0.856."""
        stats = compute_session_stats(REAL_FORMAT_SESSIONS)
        expected_mean = (0.915 + 0.922 + 0.732) / 3
        assert abs(stats["score_distribution"]["mean"] - expected_mean) < 0.01

    def test_top_session_is_highest_score(self):
        """Top session should be r2 (0.922), not r1."""
        stats = compute_session_stats(REAL_FORMAT_SESSIONS)
        assert stats["top_sessions"][0]["session_id"] == "r2"

    def test_bottom_session_is_lowest_score(self):
        """Bottom session should be r3 (0.732)."""
        stats = compute_session_stats(REAL_FORMAT_SESSIONS)
        assert stats["bottom_sessions"][0]["session_id"] == "r3"

    def test_tradition_avg_score_nonzero(self):
        """Per-tradition average score must reflect real data."""
        stats = compute_session_stats(REAL_FORMAT_SESSIONS)
        traditions = {t["name"]: t for t in stats["by_tradition"]}
        assert traditions["chinese_xieyi"]["avg_score"] > 0.9
        assert traditions["brand_design"]["avg_score"] > 0.9

    def test_no_low_score_anomalies(self):
        """All sessions > 0.5, so no low score anomalies."""
        stats = compute_session_stats(REAL_FORMAT_SESSIONS)
        assert len(stats["anomalies"]["low_scores"]) == 0
