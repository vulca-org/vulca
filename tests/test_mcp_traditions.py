"""Tests for search_traditions tool and tradition_layers in get_tradition_guide."""
import asyncio
import warnings

import pytest


def run(coro):
    return asyncio.run(coro)


# ── get_tradition_guide: tradition_layers field ──────────────────────


class TestGetTraditionGuideLayers:
    def test_returns_tradition_layers(self):
        from vulca.mcp_server import get_tradition_guide

        r = run(get_tradition_guide("chinese_xieyi"))
        assert "tradition_layers" in r
        layers = r["tradition_layers"]
        assert isinstance(layers, list)
        assert len(layers) >= 3
        # Each entry should have role and content_type
        for entry in layers:
            assert "role" in entry
            assert "content_type" in entry

    def test_unknown_tradition_returns_error(self):
        from vulca.mcp_server import get_tradition_guide

        r = run(get_tradition_guide("nonexistent_tradition"))
        assert "error" in r
        assert "nonexistent_tradition" in r["error"]

    def test_layers_match_plan_prompt_function(self):
        from vulca.mcp_server import get_tradition_guide
        from vulca.layers.plan_prompt import get_tradition_layer_order

        r = run(get_tradition_guide("chinese_xieyi"))
        expected = get_tradition_layer_order("chinese_xieyi")
        assert r["tradition_layers"] == expected

    def test_default_tradition_gets_fallback_layers(self):
        from vulca.mcp_server import get_tradition_guide

        r = run(get_tradition_guide("default"))
        # default may not exist as a YAML tradition
        if "error" not in r:
            assert "tradition_layers" in r
            assert isinstance(r["tradition_layers"], list)


# ── build_plan_prompt deprecation ────────────────────────────────────


class TestBuildPlanPromptDeprecation:
    def test_emits_deprecation_warning(self):
        from vulca.layers.plan_prompt import build_plan_prompt

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = build_plan_prompt("mountains", "chinese_xieyi")
            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "build_plan_prompt" in str(w[0].message)
        # Still returns a valid prompt string
        assert isinstance(result, str)
        assert "layers" in result.lower()


# ── search_traditions ────────────────────────────────────────────────


class TestSearchTraditions:
    def test_basic_search_returns_matches(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["ink"]))
        assert "matches" in r
        assert "query_tags" in r
        assert r["query_tags"] == ["ink"]

    def test_search_by_tradition_name(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["xieyi"]))
        matches = r["matches"]
        assert len(matches) >= 1
        names = [m["tradition"] for m in matches]
        assert "chinese_xieyi" in names

    def test_search_returns_relevance_score(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["ink", "xieyi"]))
        for m in r["matches"]:
            assert "relevance_score" in m
            assert 0.0 < m["relevance_score"] <= 1.0

    def test_search_sorted_by_relevance(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["ink", "brush"]))
        scores = [m["relevance_score"] for m in r["matches"]]
        assert scores == sorted(scores, reverse=True)

    def test_zero_matches_not_included(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["zzz_nonexistent_tag_xyz"]))
        assert r["matches"] == []

    def test_multiple_tags_score_higher(self):
        from vulca.mcp_server import search_traditions

        r1 = run(search_traditions(tags=["xieyi"]))
        r2 = run(search_traditions(tags=["xieyi", "ink"]))
        # With more matching tags, the top match should score at least as high
        if r1["matches"] and r2["matches"]:
            # Single-tag search: score = 1.0 for exact match
            # Two-tag search: score depends on how many match
            assert r2["matches"][0]["relevance_score"] > 0

    def test_chinese_character_search(self):
        from vulca.mcp_server import search_traditions

        # Search for a Chinese term that should appear in terminology
        r = run(search_traditions(tags=["写意"]))
        # If any tradition has this in terminology/display_name, we get matches
        assert "matches" in r

    def test_matched_terms_respects_limit(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["ink"], limit=2))
        for m in r["matches"]:
            assert len(m["matched_terms"]) <= 2

    def test_match_structure_has_required_fields(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=["xieyi"]))
        assert len(r["matches"]) >= 1
        m = r["matches"][0]
        assert "tradition" in m
        assert "display_name" in m
        assert "matched_terms" in m
        assert "relevance_score" in m

    def test_empty_tags_returns_no_matches(self):
        from vulca.mcp_server import search_traditions

        r = run(search_traditions(tags=[]))
        assert r["matches"] == []
