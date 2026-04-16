"""Tests for VULCA MCP Server v2 — agent-native tools returning full JSON."""
import asyncio
import pytest


def run(coro):
    return asyncio.run(coro)


class TestCreateArtwork:
    def test_returns_all_fields(self):
        from vulca.mcp_server import create_artwork
        r = run(create_artwork("test", provider="mock"))
        assert "session_id" in r
        assert "best_image_url" in r
        assert "weighted_total" in r
        # All fields always present (no summary/detailed distinction)
        assert "rationales" in r
        assert "rounds" in r
        assert "scores" in r
        assert "cost_usd" in r
        assert "recommendations" in r
        assert "risk_flags" in r

    def test_hitl_returns_session(self):
        from vulca.mcp_server import create_artwork
        r = run(create_artwork("test", provider="mock", hitl=True))
        assert r["status"] == "waiting_human"
        assert r["session_id"]


class TestEvaluateArtwork:
    def test_returns_all_fields(self):
        from vulca.mcp_server import evaluate_artwork
        r = run(evaluate_artwork("/dev/null", mock=True))
        assert "score" in r
        assert "tradition" in r
        # All fields always present
        assert "rationales" in r
        assert "recommendations" in r
        assert "risk_flags" in r
        assert "risk_level" in r


class TestListTraditions:
    def test_json(self):
        from vulca.mcp_server import list_traditions
        r = run(list_traditions())
        assert "traditions" in r
        assert "chinese_xieyi" in r["traditions"]
        xieyi = r["traditions"]["chinese_xieyi"]
        assert "emphasis" in xieyi
        # Always includes detailed fields
        assert "terminology_count" in xieyi


class TestGetTraditionGuide:
    def test_returns_guide(self):
        from vulca.mcp_server import get_tradition_guide
        r = run(get_tradition_guide("chinese_xieyi"))
        assert r["tradition"] == "chinese_xieyi"
        assert "weights" in r

    def test_returns_full_terminology(self):
        from vulca.mcp_server import get_tradition_guide
        r = run(get_tradition_guide("chinese_xieyi"))
        assert "terminology" in r
        assert "taboos" in r
        assert "weights" in r

    def test_unknown_returns_error(self):
        from vulca.mcp_server import get_tradition_guide
        r = run(get_tradition_guide("nonexistent"))
        assert "error" in r


