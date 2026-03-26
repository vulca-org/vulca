"""Tests for scoring/sparse.py — BriefIndexer + DimensionActivation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca.scoring.sparse import BriefIndexer, DimensionActivation


class TestDimensionActivation:
    def test_active_and_skipped_are_disjoint(self):
        act = DimensionActivation(
            active={"L1": 1.0, "L3": 0.8},
            skipped={"L2": "no_signal", "L4": "no_signal", "L5": "no_signal"},
            method="brief_indexed",
        )
        assert set(act.active) & set(act.skipped) == set()

    def test_all_five_dimensions_covered(self):
        act = DimensionActivation(
            active={"L1": 1.0, "L3": 0.8, "L5": 0.6},
            skipped={"L2": "no_signal", "L4": "no_signal"},
            method="brief_indexed",
        )
        all_dims = set(act.active) | set(act.skipped)
        assert all_dims == {"L1", "L2", "L3", "L4", "L5"}


class TestBriefIndexer:
    def setup_method(self):
        self.indexer = BriefIndexer()

    def test_index_activates_l3_when_tradition_specified(self):
        result = self.indexer.index("random text", tradition="chinese_xieyi")
        assert "L3" in result.active

    def test_index_no_forced_l3_without_tradition(self):
        result = self.indexer.index("random text", tradition="")
        if "L3" in result.active:
            assert result.method == "brief_indexed"

    def test_index_keyword_match_l2(self):
        result = self.indexer.index("笔法练习 stroke technique", tradition="")
        assert "L2" in result.active

    def test_index_keyword_match_l1(self):
        result = self.indexer.index("构图 composition 留白 layout", tradition="")
        assert "L1" in result.active

    def test_index_keyword_match_l5(self):
        result = self.indexer.index("情感 atmosphere mood 韵味", tradition="")
        assert "L5" in result.active

    def test_index_min_dimensions_enforced(self):
        result = self.indexer.index("笔法", tradition="", min_dimensions=3)
        assert len(result.active) >= 3

    def test_index_full_when_all_keywords_present(self):
        result = self.indexer.index("构图 笔法 文化 叙事 情感", tradition="chinese_xieyi")
        assert len(result.active) == 5

    def test_skipped_dimensions_have_reason(self):
        result = self.indexer.index("笔法", tradition="", min_dimensions=1)
        for dim, reason in result.skipped.items():
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_confidence_ordering(self):
        result = self.indexer.index("构图 composition 布局 layout 留白 色彩 对比", tradition="")
        if "L1" in result.active and "L5" in result.active:
            assert result.active["L1"] >= result.active["L5"]

    def test_default_priority_for_padding(self):
        result = self.indexer.index("叙事", tradition="", min_dimensions=3)
        assert len(result.active) >= 3
        padded = [d for d in result.active if d != "L4"]
        priority = ["L1", "L3", "L5", "L2"]
        for dim in padded:
            assert dim in priority

    def test_activation_method_field(self):
        result = self.indexer.index("test", tradition="")
        assert result.method == "brief_indexed"

    def test_active_plus_skipped_equals_five(self):
        result = self.indexer.index("构图 笔法", tradition="chinese_xieyi")
        assert len(result.active) + len(result.skipped) == 5

    def test_confidence_between_zero_and_one(self):
        result = self.indexer.index("构图 留白 色彩", tradition="")
        for conf in result.active.values():
            assert 0.0 < conf <= 1.0
