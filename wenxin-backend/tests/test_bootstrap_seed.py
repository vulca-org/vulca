"""Tests for bootstrap seed feature backfill."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.prototype.digestion.feature_extractor import (
    extract_cultural_features,
    backfill_missing_features,
)


class TestExtractCulturalFeatures:
    def test_empty_scores(self):
        result = extract_cultural_features("default", {}, [])
        assert result == {}

    def test_none_scores(self):
        result = extract_cultural_features("default", None, None)
        assert result == {}

    def test_basic_extraction(self):
        scores = {"L1": 0.7, "L2": 0.8, "L3": 0.6, "L4": 0.75, "L5": 0.9}
        result = extract_cultural_features("chinese_xieyi", scores, [])
        assert result["tradition_specificity"] == 0.8
        assert result["l5_emphasis"] == round(0.9 / 0.9, 4)  # L5/max
        assert 0 < result["avg_score"] < 1
        assert result["risk_level"] == 0
        assert "cultural_depth" in result

    def test_default_tradition(self):
        scores = {"L1": 0.5}
        result = extract_cultural_features("default", scores, [])
        assert result["tradition_specificity"] == 0.3

    def test_risk_flags(self):
        scores = {"L1": 0.5}
        result = extract_cultural_features("default", scores, ["flag1", "flag2"])
        assert result["risk_level"] == 0.5  # 2 * 0.25

    def test_risk_flags_capped(self):
        scores = {"L1": 0.5}
        result = extract_cultural_features("default", scores, ["a", "b", "c", "d", "e"])
        assert result["risk_level"] == 1.0  # capped at 1.0

    def test_l5_emphasis_ratio(self):
        scores = {"L1": 0.4, "L5": 0.8}
        result = extract_cultural_features("default", scores, [])
        assert result["l5_emphasis"] == round(0.8 / 0.8, 4)  # L5/max(0.8)

    def test_cultural_depth_from_l3(self):
        scores = {"L1": 0.5, "L3": 0.72}
        result = extract_cultural_features("default", scores, [])
        assert result["cultural_depth"] == 0.72

    def test_philosophical_aesthetic_fallback(self):
        scores = {"L1": 0.5, "philosophical_aesthetic": 0.65}
        result = extract_cultural_features("default", scores, [])
        assert result["l5_emphasis"] == round(0.65 / 0.65, 4)


class TestBackfillMissingFeatures:
    def test_backfill_updates_empty_features(self, tmp_path):
        sessions_file = tmp_path / "sessions.jsonl"
        session = {
            "session_id": "test-1",
            "tradition": "chinese_xieyi",
            "cultural_features": {},
            "final_scores": {"L1": 0.7, "L2": 0.8, "L3": 0.6, "L4": 0.75, "L5": 0.9},
            "risk_flags": [],
        }
        sessions_file.write_text(json.dumps(session) + "\n")

        with patch("app.prototype.digestion.feature_extractor._DATA_DIR", tmp_path):
            count = backfill_missing_features()

        assert count == 1
        updated = json.loads(sessions_file.read_text().strip())
        assert updated["cultural_features"]["tradition_specificity"] == 0.8

    def test_backfill_skips_existing(self, tmp_path):
        sessions_file = tmp_path / "sessions.jsonl"
        session = {
            "session_id": "test-1",
            "tradition": "chinese_xieyi",
            "cultural_features": {"avg_score": 0.7, "tradition_specificity": 0.8},
            "final_scores": {"L1": 0.7},
        }
        sessions_file.write_text(json.dumps(session) + "\n")

        with patch("app.prototype.digestion.feature_extractor._DATA_DIR", tmp_path):
            count = backfill_missing_features()

        assert count == 0

    def test_backfill_no_file(self, tmp_path):
        with patch("app.prototype.digestion.feature_extractor._DATA_DIR", tmp_path):
            count = backfill_missing_features()
        assert count == 0

    def test_backfill_uses_round_snapshots(self, tmp_path):
        sessions_file = tmp_path / "sessions.jsonl"
        session = {
            "session_id": "test-2",
            "tradition": "ukiyoe",
            "cultural_features": {},
            "round_snapshots": [
                {"dimension_scores": {"L1": 0.6, "L2": 0.5, "L3": 0.7}}
            ],
        }
        sessions_file.write_text(json.dumps(session) + "\n")

        with patch("app.prototype.digestion.feature_extractor._DATA_DIR", tmp_path):
            count = backfill_missing_features()

        assert count == 1
        updated = json.loads(sessions_file.read_text().strip())
        assert updated["cultural_features"]["avg_score"] > 0

    def test_backfill_multiple_sessions(self, tmp_path):
        sessions_file = tmp_path / "sessions.jsonl"
        s1 = {
            "session_id": "test-1",
            "tradition": "chinese_xieyi",
            "cultural_features": {},
            "final_scores": {"L1": 0.7},
        }
        s2 = {
            "session_id": "test-2",
            "tradition": "default",
            "cultural_features": {"avg_score": 0.5},
            "final_scores": {"L1": 0.5},
        }
        s3 = {
            "session_id": "test-3",
            "tradition": "ukiyoe",
            "cultural_features": {},
            "final_scores": {"L1": 0.6, "L3": 0.8},
        }
        sessions_file.write_text(
            json.dumps(s1) + "\n" + json.dumps(s2) + "\n" + json.dumps(s3) + "\n"
        )

        with patch("app.prototype.digestion.feature_extractor._DATA_DIR", tmp_path):
            count = backfill_missing_features()

        assert count == 2  # s1 and s3 updated, s2 skipped
