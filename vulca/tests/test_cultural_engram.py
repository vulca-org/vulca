"""Tests for cultural/engram.py — Engram-inspired cultural knowledge retrieval."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca.cultural.engram import CulturalEngram, CulturalFragment, EngramQuery, EngramResult
from vulca.cultural.types import TraditionConfig, TermEntry, TabooEntry


def _make_xieyi_tradition() -> TraditionConfig:
    return TraditionConfig(
        name="chinese_xieyi",
        terminology=[
            TermEntry(term="留白", term_zh="留白", definition="Use of empty space to create breathing room",
                      category="composition", l_levels=["L1"], aliases=["blank space", "negative space"]),
            TermEntry(term="墨分五色", term_zh="墨分五色", definition="Five tonal values of ink wash",
                      category="technique", l_levels=["L2"], aliases=["ink gradation", "five ink tones"]),
            TermEntry(term="气韵生动", term_zh="气韵生动", definition="Vitality and spiritual resonance",
                      category="aesthetic", l_levels=["L5"], aliases=["qi yun"]),
        ],
        taboos=[
            TabooEntry(rule="Avoid overly saturated colors", severity="medium", l_levels=["L2", "L3"],
                       trigger_patterns=["saturated", "neon", "bright"],
                       explanation="Xieyi values subtlety in ink wash."),
        ],
    )


def _make_ukiyoe_tradition() -> TraditionConfig:
    return TraditionConfig(
        name="ukiyoe",
        terminology=[
            TermEntry(term="浮世絵", term_zh="浮世绘", definition="Pictures of the floating world",
                      category="genre", l_levels=["L3"], aliases=["ukiyo-e"]),
        ],
        taboos=[],
    )


class TestCulturalFragment:
    def test_fragment_fields(self):
        frag = CulturalFragment(fragment_id="abc123", tradition="chinese_xieyi", category="terminology",
                                tags=["留白", "composition"], content="Use of empty space",
                                l_dimensions=["L1"], weight=0.8)
        assert frag.tradition == "chinese_xieyi"
        assert "留白" in frag.tags
        assert frag.weight == 0.8


class TestCulturalEngram:
    def setup_method(self):
        self.engram = CulturalEngram(max_fragments=12, max_tokens=800)
        traditions = {"chinese_xieyi": _make_xieyi_tradition(), "ukiyoe": _make_ukiyoe_tradition()}
        self.engram.build_index(traditions)

    def test_build_index_fragment_count(self):
        engram = CulturalEngram()
        count = engram.build_index({"chinese_xieyi": _make_xieyi_tradition(), "ukiyoe": _make_ukiyoe_tradition()})
        assert count == 5  # xieyi: 3 terms + 1 taboo = 4, ukiyoe: 1 term = 1

    def test_query_returns_relevant_fragments(self):
        result = self.engram.query(EngramQuery(intent="荷花留白", tradition="chinese_xieyi",
                                               tags=["留白", "荷花"], active_dimensions=["L1"]))
        names = [f.content for f in result.fragments]
        assert any("empty space" in c.lower() or "留白" in c for c in names)

    def test_query_filters_by_tradition(self):
        result = self.engram.query(EngramQuery(intent="test", tradition="chinese_xieyi",
                                               tags=["留白"], active_dimensions=["L1"]))
        for frag in result.fragments:
            assert frag.tradition == "chinese_xieyi"

    def test_query_respects_max_fragments(self):
        engram = CulturalEngram(max_fragments=2, max_tokens=10000)
        engram.build_index({"chinese_xieyi": _make_xieyi_tradition()})
        result = engram.query(EngramQuery(intent="留白 墨分五色 气韵", tradition="chinese_xieyi",
                                          tags=["留白", "墨分五色", "气韵"], active_dimensions=["L1", "L2", "L5"]))
        assert len(result.fragments) <= 2

    def test_query_respects_max_tokens(self):
        engram = CulturalEngram(max_fragments=100, max_tokens=50)
        engram.build_index({"chinese_xieyi": _make_xieyi_tradition()})
        result = engram.query(EngramQuery(intent="留白", tradition="chinese_xieyi",
                                          tags=["留白"], active_dimensions=["L1"]))
        assert result.total_tokens_estimate <= 50

    def test_dimension_weighting(self):
        result_l1 = self.engram.query(EngramQuery(intent="test", tradition="chinese_xieyi",
                                                   tags=["留白", "墨分五色"], active_dimensions=["L1"]))
        result_l2 = self.engram.query(EngramQuery(intent="test", tradition="chinese_xieyi",
                                                   tags=["留白", "墨分五色"], active_dimensions=["L2"]))
        if result_l1.fragments and result_l2.fragments:
            assert result_l1.fragments[0].fragment_id != result_l2.fragments[0].fragment_id

    def test_empty_tags_returns_top_general(self):
        result = self.engram.query(EngramQuery(intent="", tradition="chinese_xieyi",
                                               tags=[], active_dimensions=[]))
        assert len(result.fragments) > 0
        for frag in result.fragments:
            assert frag.tradition == "chinese_xieyi"

    def test_invalidate_clears_tradition(self):
        self.engram.invalidate("chinese_xieyi")
        result = self.engram.query(EngramQuery(intent="留白", tradition="chinese_xieyi",
                                               tags=["留白"], active_dimensions=["L1"]))
        assert len(result.fragments) == 0

    def test_coverage_reports_dimensions(self):
        result = self.engram.query(EngramQuery(intent="留白 墨分五色", tradition="chinese_xieyi",
                                               tags=["留白", "墨分五色"], active_dimensions=["L1", "L2"]))
        assert "L1" in result.coverage
        assert "L2" in result.coverage
        assert 0.0 <= result.coverage["L1"] <= 1.0

    def test_extract_tags_deterministic(self):
        tags1 = self.engram.extract_tags("写意荷花留白技法")
        tags2 = self.engram.extract_tags("写意荷花留白技法")
        assert tags1 == tags2

    def test_extract_tags_bilingual(self):
        tags = self.engram.extract_tags("留白 negative space technique 气韵")
        assert any("留白" in t or "negative space" in t for t in tags)
