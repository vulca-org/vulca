"""Tests for the agent factory — lazy-import catalog + runtime registration."""

from __future__ import annotations

import types
from unittest.mock import MagicMock, patch

import pytest

from app.prototype.orchestrator.agent_factory import (
    _AGENT_CATALOG,
    _RUNTIME_REGISTRY,
    create_agent,
    list_agents,
    register_agent,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_runtime_registry():
    """Ensure each test starts with an empty runtime registry."""
    _RUNTIME_REGISTRY.clear()
    yield
    _RUNTIME_REGISTRY.clear()


# ---------------------------------------------------------------------------
# test_create_known_agents
# ---------------------------------------------------------------------------

_KNOWN_AGENTS = [
    ("draft", "app.prototype.agents.draft_agent", "DraftAgent"),
    ("critic", "app.prototype.agents.critic_agent", "CriticAgent"),
    ("queen", "app.prototype.agents.queen_agent", "QueenAgent"),
    ("archivist", "app.prototype.agents.archivist_agent", "ArchivistAgent"),
    ("critic_llm", "app.prototype.agents.critic_llm", "CriticLLM"),
    ("queen_llm", "app.prototype.agents.queen_llm", "QueenLLMAgent"),
]


@pytest.mark.parametrize("name,module_path,class_name", _KNOWN_AGENTS)
def test_create_known_agents(name: str, module_path: str, class_name: str):
    """Each catalog agent can be resolved via importlib without error."""
    mock_cls = MagicMock(name=class_name)
    mock_module = types.ModuleType(module_path)
    setattr(mock_module, class_name, mock_cls)

    with patch("app.prototype.orchestrator.agent_factory.importlib.import_module", return_value=mock_module):
        agent = create_agent(name, config="test_config")

    mock_cls.assert_called_once_with(config="test_config")
    assert agent is mock_cls.return_value


# ---------------------------------------------------------------------------
# test_create_unknown_agent_raises
# ---------------------------------------------------------------------------

def test_create_unknown_agent_raises():
    """Requesting a non-existent agent name raises KeyError."""
    with pytest.raises(KeyError, match="nonexistent"):
        create_agent("nonexistent")


# ---------------------------------------------------------------------------
# test_register_and_create_custom_agent
# ---------------------------------------------------------------------------

def test_register_and_create_custom_agent():
    """Runtime-registered agents can be created via create_agent."""
    register_agent("my_custom", "my_plugin.agents", "CustomAgent")

    mock_cls = MagicMock(name="CustomAgent")
    mock_module = types.ModuleType("my_plugin.agents")
    setattr(mock_module, "CustomAgent", mock_cls)

    with patch("app.prototype.orchestrator.agent_factory.importlib.import_module", return_value=mock_module):
        agent = create_agent("my_custom", foo="bar")

    mock_cls.assert_called_once_with(foo="bar")
    assert agent is mock_cls.return_value


def test_register_overrides_catalog():
    """Runtime registration overrides built-in catalog entries."""
    # Register a custom "draft" that should take priority
    register_agent("draft", "my_plugin.draft", "MyDraft")

    mock_cls = MagicMock(name="MyDraft")
    mock_module = types.ModuleType("my_plugin.draft")
    setattr(mock_module, "MyDraft", mock_cls)

    with patch("app.prototype.orchestrator.agent_factory.importlib.import_module", return_value=mock_module) as mock_import:
        create_agent("draft")

    # Should import from the registered path, not the catalog
    mock_import.assert_called_once_with("my_plugin.draft")


# ---------------------------------------------------------------------------
# test_list_agents
# ---------------------------------------------------------------------------

def test_list_agents():
    """list_agents returns all 6 default agents, sorted."""
    agents = list_agents()
    assert len(agents) == 6
    assert agents == sorted(agents)
    expected = {"archivist", "critic", "critic_llm", "draft", "queen", "queen_llm"}
    assert set(agents) == expected


def test_list_agents_includes_registered():
    """list_agents includes runtime-registered agents."""
    register_agent("my_custom", "my_plugin.agents", "CustomAgent")
    agents = list_agents()
    assert "my_custom" in agents
    assert len(agents) == 7  # 6 built-in + 1 custom


# ---------------------------------------------------------------------------
# test_skill_hook_disabled_by_default
# ---------------------------------------------------------------------------

def test_skill_hook_disabled_by_default():
    """Orchestrator has skill_hook disabled by default and _run_skill_hook returns []."""
    from app.prototype.orchestrator.orchestrator import PipelineOrchestrator

    # Patch LangfuseObserver at its source module (lazy import inside __init__)
    with patch("app.prototype.observability.langfuse_observer.LangfuseObserver"):
        orch = PipelineOrchestrator()

    assert orch.enable_skill_hook is False
    assert orch.skill_hook_names is None
    result = orch._run_skill_hook(image_path="/tmp/test.png", tradition="chinese_painting")
    assert result == []


def test_skill_hook_import_error_returns_empty():
    """_run_skill_hook returns [] gracefully when pipeline_hook import fails."""
    from app.prototype.orchestrator.orchestrator import PipelineOrchestrator

    with patch("app.prototype.observability.langfuse_observer.LangfuseObserver"):
        orch = PipelineOrchestrator(enable_skill_hook=True)

    # Simulate ImportError by patching the import target away
    with patch.dict("sys.modules", {"app.prototype.skills.pipeline_hook": None}):
        result = orch._run_skill_hook(image_path="/tmp/test.png", tradition="chinese_painting")
    assert result == []


# ---------------------------------------------------------------------------
# test_catalog_matches_actual_modules
# ---------------------------------------------------------------------------

def test_catalog_entries_are_valid():
    """Verify catalog has exactly 6 entries with expected keys."""
    assert len(_AGENT_CATALOG) == 6
    expected_keys = {"draft", "critic", "queen", "archivist", "critic_llm", "queen_llm"}
    assert set(_AGENT_CATALOG.keys()) == expected_keys
    # Each entry is a (module_path, class_name) tuple
    for name, (mod, cls) in _AGENT_CATALOG.items():
        assert isinstance(mod, str) and mod.startswith("app.prototype.agents."), \
            f"Agent '{name}' has unexpected module path: {mod}"
        assert isinstance(cls, str) and cls[0].isupper(), \
            f"Agent '{name}' has unexpected class name: {cls}"
