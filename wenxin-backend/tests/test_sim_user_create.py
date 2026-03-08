"""Unit tests for SimUserAgent create cycle and intent templates."""

from __future__ import annotations

import pytest

from app.prototype.community.intent_templates import (
    INTENT_TEMPLATES,
    get_intents_for_tradition,
)


def test_intent_templates_cover_all_traditions():
    expected = [
        "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
        "islamic_geometric", "japanese_traditional", "watercolor",
        "african_traditional", "south_asian",
    ]
    for t in expected:
        assert t in INTENT_TEMPLATES, f"Missing template for {t}"
        assert len(INTENT_TEMPLATES[t]) >= 2, f"{t} needs at least 2 intents"


def test_get_intents_fallback():
    intents = get_intents_for_tradition("nonexistent_tradition")
    assert intents == INTENT_TEMPLATES["default"]


def test_get_intents_specific():
    intents = get_intents_for_tradition("chinese_xieyi")
    assert any("ink" in i.lower() or "xieyi" in i.lower() for i in intents)


def test_sim_user_agent_init():
    from app.prototype.community.sim_user_agent import SimUserAgent

    agent = SimUserAgent("casual_creator", base_url="http://localhost:9999")
    assert agent.persona.name == "casual_creator"
    assert agent.name == "sim_casual_creator"


def test_sim_user_agent_invalid_persona():
    from app.prototype.community.sim_user_agent import SimUserAgent

    with pytest.raises(ValueError, match="Unknown persona"):
        SimUserAgent("nonexistent_persona")


def test_api_client_create_session_method_exists():
    from app.prototype.community.api_client import VulcaAPIClient

    client = VulcaAPIClient(base_url="http://localhost:9999")
    assert hasattr(client, "create_session")
    assert callable(client.create_session)
