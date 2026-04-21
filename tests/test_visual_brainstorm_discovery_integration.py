"""Integration-path tripwire for /visual-brainstorm skill's discovery dependencies.

Closes the "noted not executed" gap in the 2026-04-21 ship-gate log §Simulation scope:
`list_traditions` / `search_traditions` / `get_tradition_guide` were not actually
invoked during the subagent-simulated ship-gate. This file calls them for real
and asserts the return shapes the skill body reads from.

If any assertion here fails, the skill's decision tree (nodes B, Error #3) will
silently misbehave — agents will produce proposals with the wrong `tradition`
enum, the wrong rubric, or fabricated tradition ids.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")

from vulca.mcp_server import (  # noqa: E402
    get_tradition_guide,
    list_traditions,
    search_traditions,
)


def run(coro):
    return asyncio.run(coro)


# Baseline expected after v0.17.3: 13 tradition yaml files shipped under
# src/vulca/cultural/data. New traditions may be added — never removed without
# a deprecation cycle. Update EXPECTED_COUNT forward, never backward.
EXPECTED_MIN_TRADITIONS = 13
EXPECTED_CORE_TRADITIONS = {
    "chinese_gongbi",
    "chinese_xieyi",
    "japanese_traditional",
    "islamic_geometric",
    "african_traditional",
    "south_asian",
    "western_academic",
    "contemporary_art",
    "watercolor",
    "photography",
    "brand_design",
    "ui_ux_design",
    "default",
}


class TestListTraditions:
    def test_returns_registry_dict(self):
        result = run(list_traditions())
        assert "traditions" in result
        assert "count" in result
        assert isinstance(result["traditions"], dict)

    def test_registry_has_expected_core_traditions(self):
        result = run(list_traditions())
        missing = EXPECTED_CORE_TRADITIONS - set(result["traditions"].keys())
        assert not missing, (
            f"Core traditions missing from registry: {missing}. "
            "Removing a tradition without a deprecation cycle breaks /visual-brainstorm "
            "B7 enum-id invariant for existing proposal.md files."
        )

    def test_count_matches_registry_size(self):
        result = run(list_traditions())
        assert result["count"] == len(result["traditions"])
        assert result["count"] >= EXPECTED_MIN_TRADITIONS

    def test_each_tradition_has_skill_required_fields(self):
        result = run(list_traditions())
        required_fields = {
            "weights",
            "emphasis",
            "description",
            "terminology_count",
            "taboos_count",
            "pipeline_variant",
        }
        for name, info in result["traditions"].items():
            missing = required_fields - set(info.keys())
            assert not missing, f"Tradition {name!r} missing fields: {missing}"

    def test_tradition_names_are_valid_enum_ids(self):
        """B7 invariant: tradition names must be usable as YAML enum ids — not
        forbidden placeholder strings, no whitespace, kebab/snake-case only."""
        forbidden = {"", "null", "none", "n/a", "unknown"}
        result = run(list_traditions())
        for name in result["traditions"]:
            assert name.lower() not in forbidden, f"Reserved id leaked into registry: {name!r}"
            assert " " not in name, f"Whitespace in tradition id: {name!r}"
            assert name == name.lower(), f"Non-lowercase tradition id: {name!r}"


class TestGetTraditionGuide:
    def test_known_tradition_returns_guide_shape(self):
        result = run(get_tradition_guide("chinese_xieyi"))
        for field in ("tradition", "description", "emphasis", "weights", "terminology", "taboos", "tradition_layers"):
            assert field in result, f"Guide missing {field!r}: {list(result.keys())}"

    def test_tradition_layers_is_ordered_list(self):
        """Skill's acceptance rubric relies on tradition_layers for L1-L5 context.
        It must be a list (ordered, non-empty for non-default traditions)."""
        result = run(get_tradition_guide("chinese_gongbi"))
        assert isinstance(result["tradition_layers"], list)
        assert len(result["tradition_layers"]) > 0

    def test_unknown_tradition_returns_error_dict_not_raise(self):
        """Skill Error #3 depends on the error-dict shape, not an exception.
        If this ever raises, Error #3 handling breaks silently."""
        result = run(get_tradition_guide("totally_fake_tradition_xyz"))
        assert isinstance(result, dict)
        assert "error" in result
        assert "list_traditions" in result["error"], (
            "Error message must guide the agent to list_traditions for recovery."
        )


class TestSearchTraditions:
    def test_returns_matches_and_query_tags(self):
        result = run(search_traditions(tags=["ink wash", "留白"]))
        assert "matches" in result
        assert "query_tags" in result
        assert result["query_tags"] == ["ink wash", "留白"]

    def test_match_entries_have_required_fields(self):
        result = run(search_traditions(tags=["ink wash"]))
        assert len(result["matches"]) > 0, "ink wash should match at least chinese_xieyi"
        for match in result["matches"]:
            for field in ("tradition", "display_name", "matched_terms", "relevance_score"):
                assert field in match, f"Match missing {field!r}: {match}"

    def test_matches_sorted_by_relevance_desc(self):
        result = run(search_traditions(tags=["ink wash", "留白", "negative space"]))
        scores = [m["relevance_score"] for m in result["matches"]]
        assert scores == sorted(scores, reverse=True), (
            "Matches must be sorted by relevance_score descending — "
            "skill picks top match when disambiguating tradition."
        )

    def test_empty_tags_returns_empty_matches(self):
        result = run(search_traditions(tags=[]))
        assert result["matches"] == []
