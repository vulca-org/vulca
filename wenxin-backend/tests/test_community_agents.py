"""Unit tests for the community agents.

All HTTP interactions are mocked so that no running backend is required.

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
from unittest.mock import AsyncMock, patch

import pytest

BASE_URL = "http://localhost:8001"
TEST_API_KEY = "test-key"

# ---------------------------------------------------------------------------
# Seed data returned by mocked get_skills
# ---------------------------------------------------------------------------
_SEED_SKILLS: list[dict] = [
    {
        "id": "1",
        "name": "test_skill",
        "description": "A test skill for agent integration tests with sufficient description length.",
        "tags": ["test", "integration"],
        "author": "test",
        "upvotes": 10,
        "downvotes": 1,
        "discussions": [],
    },
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# 1. VulcaAPIClient
# ---------------------------------------------------------------------------

class TestVulcaAPIClient:
    def test_get_skills(self, event_loop):
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL)
        client.get_skills = AsyncMock(return_value=list(_SEED_SKILLS))
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
        client.create_skill = AsyncMock(return_value={"id": "42", **payload})
        result = event_loop.run_until_complete(client.create_skill(payload))
        assert result["name"] == "api_test_skill"
        assert "id" in result

    def test_post_discussion(self, event_loop):
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY)
        client.get_skills = AsyncMock(return_value=list(_SEED_SKILLS))
        client.post_discussion = AsyncMock(
            return_value={"id": "disc-1", "content": "Test comment from pytest", "author": "agent"}
        )
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
    def test_run_cycle(self, event_loop, tmp_path):
        from app.prototype.community.curator_agent import CuratorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL)
        client.get_skills = AsyncMock(return_value=list(_SEED_SKILLS))
        agent = CuratorAgent(client=client)
        agent.log_path = tmp_path / "curator.jsonl"
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
    def test_run_cycle(self, event_loop, tmp_path):
        from app.prototype.community.discussant_agent import DiscussantAgent
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY)
        client.get_skills = AsyncMock(return_value=list(_SEED_SKILLS))
        client.post_discussion = AsyncMock(
            return_value={"id": "disc-1", "content": "mock", "author": "agent"}
        )
        agent = DiscussantAgent(client=client)
        agent.log_path = tmp_path / "discussant.jsonl"
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

        client = VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY)
        agent = SkillCreatorAgent(
            client=client,
            feedback_dir=tmp_path,  # empty dir = no patterns
        )
        agent.log_path = tmp_path / "skill_creator.jsonl"
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

        client = VulcaAPIClient(base_url=BASE_URL, api_key=TEST_API_KEY)
        client.create_skill = AsyncMock(
            return_value={"id": "99", "name": "auto_accessibility"}
        )
        agent = SkillCreatorAgent(
            client=client,
            feedback_dir=tmp_path,
            threshold=3,
        )
        agent.log_path = tmp_path / "skill_creator.jsonl"
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
    def test_register_and_run_once(self, event_loop, tmp_path):
        from app.prototype.community.scheduler import AgentScheduler
        from app.prototype.community.curator_agent import CuratorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL)
        client.get_skills = AsyncMock(return_value=list(_SEED_SKILLS))
        scheduler = AgentScheduler()
        agent = CuratorAgent(client=client)
        agent.log_path = tmp_path / "curator.jsonl"
        scheduler.register(agent, interval_seconds=0)  # 0 = run immediately

        results = event_loop.run_until_complete(scheduler.run_once())
        assert len(results) == 1
        assert results[0]["agent"] == "curator"
        assert "reviewed" in results[0]

    def test_interval_prevents_rerun(self, event_loop, tmp_path):
        from app.prototype.community.scheduler import AgentScheduler
        from app.prototype.community.curator_agent import CuratorAgent
        from app.prototype.community.api_client import VulcaAPIClient

        client = VulcaAPIClient(base_url=BASE_URL)
        client.get_skills = AsyncMock(return_value=list(_SEED_SKILLS))
        scheduler = AgentScheduler()
        agent = CuratorAgent(client=client)
        agent.log_path = tmp_path / "curator.jsonl"
        scheduler.register(agent, interval_seconds=9999)

        # First run should execute
        r1 = event_loop.run_until_complete(scheduler.run_once())
        assert len(r1) == 1

        # Second run should skip (interval not elapsed)
        r2 = event_loop.run_until_complete(scheduler.run_once())
        assert len(r2) == 0


# ---------------------------------------------------------------------------
# 7. Digest Parity (WU-11)
# ---------------------------------------------------------------------------

class TestDigestParity:
    """Test that agent sessions produce digests with full schema parity."""

    def test_session_digest_has_cultural_features_field(self):
        """SessionDigest must have the cultural_features field (WU-07)."""
        import dataclasses
        from app.prototype.session.types import SessionDigest

        field_names = {f.name for f in dataclasses.fields(SessionDigest)}
        assert "cultural_features" in field_names
        assert "critic_insights" in field_names
        assert "candidate_choice_index" in field_names
        assert "time_to_select_ms" in field_names
        assert "downloaded" in field_names

    def test_agent_digest_serializes_cultural_features(self):
        """Agent-created digest should serialize cultural_features correctly."""
        from app.prototype.session.types import SessionDigest

        digest = SessionDigest(
            session_id="agent-test-001",
            mode="create",
            user_type="agent",
            tradition="chinese_xieyi",
            cultural_features={"l5_emphasis": 0.85, "tradition_specificity": 0.8},
            critic_insights=["strong L5 presence"],
        )
        d = digest.to_dict()
        assert d["user_type"] == "agent"
        assert d["cultural_features"]["l5_emphasis"] == 0.85
        assert d["critic_insights"] == ["strong L5 presence"]

    def test_human_and_agent_digest_same_schema(self):
        """Human and agent digests should have identical field sets."""
        from app.prototype.session.types import SessionDigest

        human = SessionDigest(user_type="human", tradition="default")
        agent = SessionDigest(user_type="agent", tradition="chinese_xieyi")

        human_keys = set(human.to_dict().keys())
        agent_keys = set(agent.to_dict().keys())

        assert human_keys == agent_keys, f"Schema mismatch: {human_keys ^ agent_keys}"


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
