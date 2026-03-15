"""Test CulturalClusterer."""
from __future__ import annotations
import pytest
from app.prototype.digestion.cultural_clusterer import CulturalClusterer, CulturalCluster, _cosine_similarity


class TestCosineSimlarity:
    def test_identical_vectors(self):
        a = {"x": 1.0, "y": 0.5}
        assert _cosine_similarity(a, a) == pytest.approx(1.0, abs=1e-6)

    def test_orthogonal_vectors(self):
        a = {"x": 1.0, "y": 0.0}
        b = {"x": 0.0, "y": 1.0}
        assert _cosine_similarity(a, b) == pytest.approx(0.0, abs=1e-6)

    def test_empty_vectors(self):
        assert _cosine_similarity({}, {}) == 0.0


class TestCulturalClusterer:
    def test_empty_sessions(self):
        c = CulturalClusterer()
        assert c.cluster([]) == []

    def test_single_session(self):
        sessions = [{"session_id": "s1", "cultural_features": {"a": 0.8}, "tradition": "default"}]
        clusters = CulturalClusterer().cluster(sessions)
        assert len(clusters) == 1
        assert clusters[0].size == 1

    def test_similar_sessions_grouped(self):
        sessions = [
            {"session_id": f"s{i}", "cultural_features": {"a": 0.8, "b": 0.7}, "tradition": "default"}
            for i in range(5)
        ]
        clusters = CulturalClusterer(similarity_threshold=0.8).cluster(sessions)
        assert len(clusters) == 1
        assert clusters[0].size == 5

    def test_dissimilar_sessions_separate(self):
        sessions = [
            {"session_id": "s1", "cultural_features": {"a": 1.0, "b": 0.0}, "tradition": "t1"},
            {"session_id": "s2", "cultural_features": {"a": 0.0, "b": 1.0}, "tradition": "t2"},
        ]
        clusters = CulturalClusterer(similarity_threshold=0.9).cluster(sessions)
        assert len(clusters) == 2

    def test_default_threshold_is_072(self):
        """Default similarity_threshold lowered to 0.72 for better fusion detection."""
        c = CulturalClusterer()
        assert c._threshold == 0.72

    def test_cluster_to_dict(self):
        c = CulturalCluster(cluster_id="c1", feature_centroid={"x": 0.5}, session_ids=["s1"], size=1)
        d = c.to_dict()
        assert d["cluster_id"] == "c1"
