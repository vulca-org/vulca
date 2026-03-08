"""Integration tests for the 4 community agents.

Runs against a live local backend (localhost:8001).
Start the backend before running:
    VULCA_API_KEYS=test-key python -m uvicorn app.main:app --port 8001

Usage:
    python -m pytest tests/test_community_agents.py -v
    # or standalone:
    python tests/test_community_agents.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest
import httpx

BASE_URL = "http://localhost:8001"
TEST_API_KEY = "test-key"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _backend_is_up() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{BASE_URL}/health")
            return r.status_code == 200
    except Exception:
        return False


async def _ensure_seed_skills():
    """Make sure at least one skill exists (needed by Discussant + Curator)."""
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{BASE_URL}/api/v1/skills")
        skills = r.json()
        if len(skills) == 0:
            await c.post(
                f"{BASE_URL}/api/v1/skills",
                json={
                    "name": "test_skill",
                    "description": "A test skill for agent integration tests with sufficient description length.",
                    "tags": ["test", "integration"],
                    "author": "test",
                },
                headers={"Authorization": f"Bearer {TEST_API_KEY}"},
            )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
def check_backend(event_loop):
    up = event_loop.run_until_complete(_backend_is_up())
    if not up:
        pytest.skip("Backend not running at localhost:8001")
    event_loop.run_until_complete(_ensure_seed_skills())


# ---------------------------------------------------------------------------
# 1. VulcaAPIClient
# ---------------------------------------------------------------------------

class TestVulcaAPIClient:
    def test_get_skills(self, event_loop):
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL)
        skills = event_loop.run_until_complete(client.get_skills())
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert "name" in skills[0]

    def test_create_skill(self, event_loop):
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY)
        payload = {
            "name": "api_test_skill",
            "description": "Created by test_community_agents.py to verify create_skill API.",
            "tags": ["test"],
            "author": "pytest",
        }
        result = event_loop.run_until_complete(client.create_skill(payload))
        assert result["name"] == "api_test_skill"
        assert "id" in result

    def test_post_discussion(self, event_loop):
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY)
        # Get a skill to comment on
        skills = event_loop.run_until_complete(client.get_skills())
        skill_id = skills[0]["id"]
        result = event_loop.run_until_complete(
            client.post_discussion(skill_id, "Test comment from pytest")
        )
        assert "id" in result


# ---------------------------------------------------------------------------
# 2. CuratorAgent
# ---------------------------------------------------------------------------

class TestCuratorAgent:
    def test_run_cycle(self, event_loop):
        from app.prototype.community.curator_agent import CuratorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        agent = CuratorAgent(client=VulcaAPIClient(base_url=BASE_URL))
        result = event_loop.run_until_complete(agent.run_cycle())
        assert "featured" in result
        assert "reviewed" in result
        assert isinstance(result["featured"], list)
        assert result["reviewed"] > 0

    def test_quality_filter(self):
        from app.prototype.community.curator_agent import _passes_quality

        good = {"description": "A sufficiently long description for testing", "tags": ["x"], "upvotes": 10, "downvotes": 1}
        bad_desc = {"description": "short", "tags": ["x"], "upvotes": 10, "downvotes": 1}
        bad_tags = {"description": "A sufficiently long description for testing", "tags": [], "upvotes": 10, "downvotes": 1}
        bad_ratio = {"description": "A sufficiently long description for testing", "tags": ["x"], "upvotes": 1, "downvotes": 10}

        assert _passes_quality(good) is True
        assert _passes_quality(bad_desc) is False
        assert _passes_quality(bad_tags) is False
        assert _passes_quality(bad_ratio) is False


# ---------------------------------------------------------------------------
# 3. DiscussantAgent
# ---------------------------------------------------------------------------

class TestDiscussantAgent:
    def test_run_cycle(self, event_loop):
        from app.prototype.community.discussant_agent import DiscussantAgent
        from app.prototype.community.api_client import VulcaAPIClient

        agent = DiscussantAgent(client=VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY))
        result = event_loop.run_until_complete(agent.run_cycle())
        assert "skill_id" in result
        assert "persona" in result
        assert result["commented"] is True

    def test_persona_rotation(self):
        from app.prototype.community.discussant_agent import DiscussantAgent, PERSONAS

        agent = DiscussantAgent()
        seen = []
        for _ in range(len(PERSONAS)):
            seen.append(agent.current_persona)
            agent._rotate_persona()
        assert len(set(seen)) == len(PERSONAS)


# ---------------------------------------------------------------------------
# 4. SkillCreatorAgent
# ---------------------------------------------------------------------------

class TestSkillCreatorAgent:
    def test_run_cycle_no_patterns(self, event_loop, tmp_path):
        from app.prototype.community.skill_creator_agent import SkillCreatorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        agent = SkillCreatorAgent(
            client=VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY),
            feedback_dir=tmp_path,  # empty dir = no patterns
        )
        result = event_loop.run_until_complete(agent.run_cycle())
        assert result["created"] is None
        assert result["patterns_found"] == 0

    def test_run_cycle_with_patterns(self, event_loop, tmp_path):
        from app.prototype.community.skill_creator_agent import SkillCreatorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        # Create fake feedback with repeated keyword
        feedback_file = tmp_path / "sim_user.jsonl"
        for i in range(5):
            record = {"details": {"comment": f"I wish there was an accessibility check (mention {i})"}}
            feedback_file.write_text(
                feedback_file.read_text() + json.dumps(record) + "\n"
                if feedback_file.exists()
                else json.dumps(record) + "\n"
            )

        agent = SkillCreatorAgent(
            client=VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY),
            feedback_dir=tmp_path,
            threshold=3,
        )
        result = event_loop.run_until_complete(agent.run_cycle())
        assert result["patterns_found"] >= 1
        assert result["created"] is not None
        assert "accessibility" in result["created"]

    def test_keyword_detection(self):
        from app.prototype.community.skill_creator_agent import _count_keyword_mentions
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for _ in range(4):
                f.write(json.dumps({"details": {"comment": "need sustainability check"}}) + "\n")
            f.write(json.dumps({"details": {"comment": "no relevant keywords"}}) + "\n")
            path = Path(f.name)

        counts = _count_keyword_mentions(path, ["sustainability", "inclusivity"])
        assert counts["sustainability"] == 4
        assert counts["inclusivity"] == 0
        path.unlink()


# ---------------------------------------------------------------------------
# 5. SimUserAgent (no real evaluate call needed, test structure only)
# ---------------------------------------------------------------------------

class TestSimUserAgent:
    def test_init_valid_persona(self):
        from app.prototype.community.sim_user_agent import SimUserAgent

        agent = SimUserAgent("casual_creator", base_url=BASE_URL)
        assert agent.persona.name == "casual_creator"
        assert agent.name == "sim_casual_creator"

    def test_init_invalid_persona(self):
        from app.prototype.community.sim_user_agent import SimUserAgent

        with pytest.raises(ValueError, match="Unknown persona"):
            SimUserAgent("nonexistent_persona")

    def test_all_personas(self):
        from app.prototype.community.sim_user_agent import SimUserAgent
        from app.prototype.community.personas import PERSONAS

        for name in PERSONAS:
            agent = SimUserAgent(name, base_url=BASE_URL)
            assert agent.persona.name == name


# ---------------------------------------------------------------------------
# 6. AgentScheduler
# ---------------------------------------------------------------------------

class TestAgentScheduler:
    def test_register_and_run_once(self, event_loop):
        from app.prototype.community.scheduler import AgentScheduler
        from app.prototype.community.curator_agent import CuratorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        scheduler = AgentScheduler()
        agent = CuratorAgent(client=VulcaAPIClient(base_url=BASE_URL))
        scheduler.register(agent, interval_seconds=0)  # 0 = run immediately

        results = event_loop.run_until_complete(scheduler.run_once())
        assert len(results) == 1
        assert results[0]["agent"] == "curator"
        assert "reviewed" in results[0]

    def test_interval_prevents_rerun(self, event_loop):
        from app.prototype.community.scheduler import AgentScheduler
        from app.prototype.community.curator_agent import CuratorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        scheduler = AgentScheduler()
        agent = CuratorAgent(client=VulcaAPIClient(base_url=BASE_URL))
        scheduler.register(agent, interval_seconds=9999)

        # First run should execute
        r1 = event_loop.run_until_complete(scheduler.run_once())
        assert len(r1) == 1

        # Second run should skip (interval not elapsed)
        r2 = event_loop.run_until_complete(scheduler.run_once())
        assert len(r2) == 0


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
