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


class TestGetEvolutionStatus:
    def test_returns_status(self):
        from vulca.mcp_server import get_evolution_status
        r = run(get_evolution_status("chinese_xieyi"))
        assert "original_weights" in r
        assert "tradition" in r

    def test_has_required_fields(self):
        from vulca.mcp_server import get_evolution_status
        r = run(get_evolution_status("chinese_xieyi"))
        assert "original_weights" in r
        assert "evolved_weights" in r
        assert "changes" in r
        assert "insight" in r
        assert "has_evolution" in r


class TestResumeArtwork:
    def test_accept(self):
        from vulca.mcp_server import create_artwork, resume_artwork
        create_r = run(create_artwork("test", provider="mock", hitl=True))
        session_id = create_r["session_id"]
        r = run(resume_artwork(session_id, "accept"))
        assert "status" in r
        assert r["status"] in ("completed", "accepted")

    def test_reject(self):
        from vulca.mcp_server import create_artwork, resume_artwork
        create_r = run(create_artwork("test", provider="mock", hitl=True))
        session_id = create_r["session_id"]
        r = run(resume_artwork(session_id, "reject"))
        assert r["status"] == "rejected"

    def test_invalid_session(self):
        from vulca.mcp_server import resume_artwork
        r = run(resume_artwork("nonexistent", "accept"))
        assert "error" in r

    def test_refine_creates_new_run(self):
        from vulca.mcp_server import create_artwork, resume_artwork
        create_r = run(create_artwork("ink wash mountain", provider="mock", hitl=True))
        session_id = create_r["session_id"]
        r = run(resume_artwork(session_id, "refine", feedback="make it more minimalist"))
        assert "status" in r
        # New session should be different from original
        assert r.get("session_id") != session_id or r.get("original_session_id") == session_id

    def test_invalid_action(self):
        from vulca.mcp_server import create_artwork, resume_artwork
        create_r = run(create_artwork("test", provider="mock", hitl=True))
        session_id = create_r["session_id"]
        r = run(resume_artwork(session_id, "unknown_action"))
        assert "error" in r
