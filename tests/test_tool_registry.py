"""Tests for ToolRegistry — auto-discovery + register/get/list/replacements.

Uses inline stub tools so no real cultural/filter tools need to exist yet.
"""

from __future__ import annotations

import pytest

from vulca.tools.protocol import ToolCategory, ToolConfig, ToolSchema, VulcaTool
from vulca.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Stub tools (inline — no real tools needed)
# ---------------------------------------------------------------------------


class StubCulturalTool(VulcaTool):
    name = "stub_cultural"
    display_name = "Stub Cultural Tool"
    description = "Stub for testing."
    category = ToolCategory.CULTURAL_CHECK
    max_seconds = 1.0
    replaces: dict[str, list[str]] = {"evaluate": ["L1"]}

    class Input(ToolSchema):
        pass

    class Output(ToolSchema):
        pass

    def execute(self, input_data: "StubCulturalTool.Input", config: ToolConfig) -> "StubCulturalTool.Output":
        return self.Output()


class StubFilterTool(VulcaTool):
    name = "stub_filter"
    display_name = "Stub Filter Tool"
    description = "Stub for testing."
    category = ToolCategory.FILTER
    max_seconds = 0.5
    replaces: dict[str, list[str]] = {}

    class Input(ToolSchema):
        pass

    class Output(ToolSchema):
        pass

    def execute(self, input_data: "StubFilterTool.Input", config: ToolConfig) -> "StubFilterTool.Output":
        return self.Output()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_registry_register_and_get():
    """register() + get() round-trip for both stub tools."""
    registry = ToolRegistry()
    registry.register(StubCulturalTool)
    registry.register(StubFilterTool)

    cultural = registry.get("stub_cultural")
    assert isinstance(cultural, StubCulturalTool)

    flt = registry.get("stub_filter")
    assert isinstance(flt, StubFilterTool)


def test_registry_get_unknown_raises():
    """get() raises KeyError for an unregistered name."""
    registry = ToolRegistry()
    registry.register(StubCulturalTool)

    with pytest.raises(KeyError):
        registry.get("nonexistent_tool")


def test_registry_list_by_category():
    """list_by_category() filters correctly by ToolCategory."""
    registry = ToolRegistry()
    registry.register(StubCulturalTool)
    registry.register(StubFilterTool)

    cultural_tools = registry.list_by_category(ToolCategory.CULTURAL_CHECK)
    assert len(cultural_tools) == 1
    assert isinstance(cultural_tools[0], StubCulturalTool)

    filter_tools = registry.list_by_category(ToolCategory.FILTER)
    assert len(filter_tools) == 1
    assert isinstance(filter_tools[0], StubFilterTool)

    # Category with no tools returns empty list
    empty = registry.list_by_category(ToolCategory.GENERATOR)
    assert empty == []


def test_registry_list_all():
    """list_all() returns all registered tools."""
    registry = ToolRegistry()
    registry.register(StubCulturalTool)
    registry.register(StubFilterTool)

    all_tools = registry.list_all()
    assert len(all_tools) == 2
    names = {t.name for t in all_tools}
    assert names == {"stub_cultural", "stub_filter"}


def test_registry_list_replacements():
    """list_replacements() returns only tools with non-empty replaces."""
    registry = ToolRegistry()
    registry.register(StubCulturalTool)  # replaces={"evaluate": ["L1"]}
    registry.register(StubFilterTool)    # replaces={}

    replacements = registry.list_replacements()
    # Only stub_cultural has non-empty replaces
    assert "stub_cultural" in replacements
    assert replacements["stub_cultural"] == {"evaluate": ["L1"]}
    # stub_filter should NOT appear
    assert "stub_filter" not in replacements


def test_registry_discover_does_not_crash():
    """discover() scans vulca.tools.cultural and vulca.tools.filters without error.

    Since those packages are currently empty, this just verifies no import errors.
    """
    registry = ToolRegistry()
    # Should not raise even when subpackages are empty
    registry.discover()
    # After discover, list_all() still returns a valid list (may be empty)
    tools = registry.list_all()
    assert isinstance(tools, list)
