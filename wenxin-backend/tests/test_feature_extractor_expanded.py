"""Test expanded cultural feature extraction (5→8 dimensions)."""

from __future__ import annotations

import pytest

from app.prototype.digestion.feature_extractor import extract_cultural_features


class TestDimensionVariance:
    """Test the new dimension_variance feature."""

    def test_uniform_scores_low_variance(self):
        """Uniform L1-L5 scores produce low variance."""
        features = extract_cultural_features(
            "chinese_xieyi",
            final_scores={"L1": 0.7, "L2": 0.7, "L3": 0.7, "L4": 0.7, "L5": 0.7},
        )
        assert "dimension_variance" in features
        assert features["dimension_variance"] == 0.0

    def test_diverse_scores_higher_variance(self):
        """Diverse L1-L5 scores produce higher variance."""
        features = extract_cultural_features(
            "chinese_xieyi",
            final_scores={"L1": 0.3, "L2": 0.9, "L3": 0.5, "L4": 0.8, "L5": 0.4},
        )
        assert features["dimension_variance"] > 0.0

    def test_empty_scores_no_variance(self):
        """Empty scores → no features at all."""
        features = extract_cultural_features("default", final_scores={})
        assert "dimension_variance" not in features


class TestL4Emphasis:
    """Test the new l4_emphasis feature (mirrors l5_emphasis)."""

    def test_l4_emphasis_computed(self):
        """L4 / max_score ratio is computed."""
        features = extract_cultural_features(
            "default",
            final_scores={"L1": 0.5, "L2": 0.6, "L3": 0.7, "L4": 0.8, "L5": 0.9},
        )
        assert "l4_emphasis" in features
        # L4=0.8, max=0.9 → 0.8/0.9 ≈ 0.8889
        assert abs(features["l4_emphasis"] - 0.8889) < 0.01

    def test_l4_with_alternate_key(self):
        """L4 can also be keyed as critical_interpretation."""
        features = extract_cultural_features(
            "default",
            final_scores={"L1": 0.5, "L2": 0.6, "L3": 0.7, "critical_interpretation": 0.8, "L5": 1.0},
        )
        assert "l4_emphasis" in features
        assert features["l4_emphasis"] == 0.8  # 0.8/1.0

    def test_l4_zero_max_no_crash(self):
        """All-zero scores don't crash."""
        features = extract_cultural_features("default", final_scores={"L1": 0, "L4": 0})
        # No positive scores → no l4_emphasis
        assert "l4_emphasis" not in features


class TestGenerationEfficiency:
    """Test the new generation_efficiency feature."""

    def test_efficiency_with_rounds(self):
        """generation_efficiency = 1.0 - total_rounds/max_rounds."""
        features = extract_cultural_features(
            "default",
            final_scores={"L1": 0.7, "L2": 0.8},
            total_rounds=1,
            max_rounds=3,
        )
        assert "generation_efficiency" in features
        # 1.0 - 1/3 ≈ 0.6667
        assert abs(features["generation_efficiency"] - 0.6667) < 0.01

    def test_efficiency_max_rounds_used(self):
        """All rounds used → efficiency = 0."""
        features = extract_cultural_features(
            "default",
            final_scores={"L1": 0.7},
            total_rounds=3,
            max_rounds=3,
        )
        assert features["generation_efficiency"] == 0.0

    def test_efficiency_skipped_when_no_rounds(self):
        """total_rounds=0 → skip generation_efficiency."""
        features = extract_cultural_features(
            "default",
            final_scores={"L1": 0.7},
        )
        assert "generation_efficiency" not in features

    def test_efficiency_skipped_when_max_rounds_zero(self):
        """max_rounds=0 → skip generation_efficiency (avoid division by zero)."""
        features = extract_cultural_features(
            "default",
            final_scores={"L1": 0.7},
            total_rounds=1,
            max_rounds=0,
        )
        assert "generation_efficiency" not in features


class TestBackwardCompatibility:
    """Verify original 5 features still work."""

    def test_original_features_unchanged(self):
        """All original 5 features are still present."""
        features = extract_cultural_features(
            "chinese_xieyi",
            final_scores={"L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.6, "L5": 0.75},
            risk_flags=["minor_issue"],
        )
        assert "tradition_specificity" in features
        assert features["tradition_specificity"] == 0.8  # non-default
        assert "l5_emphasis" in features
        assert "avg_score" in features
        assert "risk_level" in features
        assert "cultural_depth" in features

    def test_no_scores_returns_empty(self):
        """No scores still returns empty dict."""
        features = extract_cultural_features("default", final_scores=None)
        assert features == {}
