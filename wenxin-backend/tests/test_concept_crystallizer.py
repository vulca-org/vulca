"""Test ConceptCrystallizer."""
from __future__ import annotations
import pytest
from unittest.mock import patch
from app.prototype.digestion.concept_crystallizer import ConceptCrystallizer, CulturalConcept
from app.prototype.digestion.cultural_clusterer import CulturalCluster


class TestConceptCrystallizer:
    def test_empty_clusters(self):
        c = ConceptCrystallizer()
        assert c.crystallize([], []) == []

    def test_small_cluster_ignored(self):
        """Cluster with size=2 is still below the lowered threshold of 3."""
        cluster = CulturalCluster(cluster_id="c1", size=2, session_ids=["s1", "s2"],
                                   feature_centroid={"a": 0.5}, tradition="default")
        c = ConceptCrystallizer(min_cluster_size=3)
        assert c.crystallize([cluster], []) == []

    def test_large_cluster_crystallized(self):
        cluster = CulturalCluster(
            cluster_id="c1", size=6,
            session_ids=[f"s{i}" for i in range(6)],
            feature_centroid={"l5_emphasis": 0.9, "cultural_depth": 0.8},
            tradition="chinese_xieyi",
        )
        sessions = [
            {"session_id": f"s{i}", "intent": f"test {i}", "tradition": "chinese_xieyi"}
            for i in range(6)
        ]
        c = ConceptCrystallizer(min_cluster_size=3)
        # Will use rule-based since no LLM
        concepts = c.crystallize([cluster], sessions)
        assert len(concepts) == 1
        assert concepts[0].name != ""
        assert concepts[0].confidence > 0

    def test_three_sessions_trigger_crystallization(self):
        """WU-02: 3 similar sessions can now trigger crystallization (was impossible with MIN=5)."""
        cluster = CulturalCluster(
            cluster_id="c2", size=3,
            session_ids=["s0", "s1", "s2"],
            feature_centroid={"tradition_specificity": 0.85, "l5_emphasis": 0.7},
            tradition="japanese_wabi_sabi",
        )
        sessions = [
            {"session_id": f"s{i}", "intent": f"wabi-sabi intent {i}", "tradition": "japanese_wabi_sabi"}
            for i in range(3)
        ]
        # Use default min_cluster_size which is now 3
        c = ConceptCrystallizer()
        concepts = c.crystallize([cluster], sessions)
        assert len(concepts) == 1, "3 sessions should now trigger crystallization"
        assert concepts[0].name != ""
        assert len(concepts[0].description) >= 10  # non-trivial description (rule-based or LLM)
        assert concepts[0].confidence == pytest.approx(min(1.0, 3 / 20))  # 0.15

    def test_concept_to_dict(self):
        c = CulturalConcept(name="test_concept", description="A test")
        d = c.to_dict()
        assert d["name"] == "test_concept"
