"""Tests for digestion/retrieval.py — TurboQuant-inspired session retrieval."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json
import pytest
from vulca.digestion.retrieval import QuantizedRetriever, SessionVector, RetrievalResult


class TestSessionVector:
    def test_fields(self):
        sv = SessionVector(session_id="s1", tradition="chinese_xieyi", intent_hash=12345,
                           signature=[0.1, 0.2, 0.3], scores={"L1": 0.8, "L2": 0.7}, user_feedback="accepted")
        assert sv.session_id == "s1"
        assert len(sv.signature) == 3


class TestQuantizedRetriever:
    def setup_method(self):
        self.retriever = QuantizedRetriever(signature_dim=32)

    def test_compute_signature_deterministic(self):
        sig1 = self.retriever._compute_signature("写意荷花")
        sig2 = self.retriever._compute_signature("写意荷花")
        assert sig1 == sig2

    def test_compute_signature_dimension(self):
        sig = self.retriever._compute_signature("test text")
        assert len(sig) == 32

    def test_compute_signature_custom_dim(self):
        r = QuantizedRetriever(signature_dim=16)
        sig = r._compute_signature("test")
        assert len(sig) == 16

    def test_similar_texts_high_similarity(self):
        sig1 = self.retriever._compute_signature("写意荷花")
        sig2 = self.retriever._compute_signature("荷花写意画")
        sim = self.retriever._inner_product(sig1, sig2)
        assert sim > 0.5

    def test_different_texts_low_similarity(self):
        sig1 = self.retriever._compute_signature("写意荷花留白水墨")
        sig2 = self.retriever._compute_signature("oil painting landscape sunset")
        sim = self.retriever._inner_product(sig1, sig2)
        assert sim < 0.5

    def test_add_creates_session_vector(self):
        sv = self.retriever.add(session_id="s1", intent="写意荷花", tradition="chinese_xieyi",
                                scores={"L1": 0.8}, feedback="accepted")
        assert sv.session_id == "s1"
        assert sv.tradition == "chinese_xieyi"
        assert len(sv.signature) == 32

    def test_query_filters_by_tradition(self):
        self.retriever.add("s1", "写意荷花", "chinese_xieyi", {"L1": 0.8}, "accepted")
        self.retriever.add("s2", "浮世绘花鸟", "ukiyoe", {"L1": 0.7}, "accepted")
        results = self.retriever.query("荷花", tradition="chinese_xieyi")
        for r in results:
            assert r.tradition == "chinese_xieyi"

    def test_query_top_k(self):
        for i in range(10):
            self.retriever.add(f"s{i}", f"荷花画 {i}", "chinese_xieyi", {"L1": 0.5}, None)
        results = self.retriever.query("荷花", tradition="chinese_xieyi", top_k=3)
        assert len(results) <= 3

    def test_query_min_similarity(self):
        self.retriever.add("s1", "写意荷花留白", "chinese_xieyi", {"L1": 0.8}, None)
        self.retriever.add("s2", "completely unrelated english text about science", "chinese_xieyi", {"L1": 0.5}, None)
        results = self.retriever.query("写意荷花", tradition="chinese_xieyi", min_similarity=0.5)
        for r in results:
            assert r.similarity >= 0.5

    def test_add_and_query_roundtrip(self):
        self.retriever.add("s1", "写意荷花留白", "chinese_xieyi", {"L1": 0.8}, None)
        results = self.retriever.query("写意荷花留白", tradition="chinese_xieyi")
        assert len(results) >= 1
        assert results[0].session_id == "s1"

    def test_save_load_preserves_index(self, tmp_path):
        self.retriever.add("s1", "写意荷花", "chinese_xieyi", {"L1": 0.8}, "accepted")
        path = tmp_path / "index.json"
        self.retriever.save(path)
        loaded = QuantizedRetriever(signature_dim=32)
        count = loaded.load(path)
        assert count == 1
        results = loaded.query("写意荷花", tradition="chinese_xieyi")
        assert len(results) >= 1
        assert results[0].session_id == "s1"

    def test_empty_index_returns_empty(self):
        results = self.retriever.query("anything", tradition="chinese_xieyi")
        assert results == []

    def test_query_returns_sorted_by_similarity(self):
        self.retriever.add("s1", "写意荷花留白水墨", "chinese_xieyi", {}, None)
        self.retriever.add("s2", "荷花", "chinese_xieyi", {}, None)
        self.retriever.add("s3", "油画风景 landscape", "chinese_xieyi", {}, None)
        results = self.retriever.query("写意荷花留白", tradition="chinese_xieyi", top_k=10, min_similarity=0.0)
        if len(results) >= 2:
            for i in range(len(results) - 1):
                assert results[i].similarity >= results[i + 1].similarity
