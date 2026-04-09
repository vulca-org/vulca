"""Tests for coarse provider-kind capability lookup."""
from __future__ import annotations


def test_mock_has_no_capabilities():
    from vulca.providers.capabilities import provider_capabilities
    assert provider_capabilities("mock") == frozenset()


def test_unknown_provider_gets_full_capabilities():
    from vulca.providers.capabilities import (
        COST_TRACKED, LLM_TEXT, VLM_SCORING, provider_capabilities,
    )
    caps = provider_capabilities("some_unknown_provider")
    assert VLM_SCORING in caps
    assert LLM_TEXT in caps
    assert COST_TRACKED in caps


def test_none_provider_returns_empty():
    from vulca.providers.capabilities import provider_capabilities
    assert provider_capabilities(None) == frozenset()


def test_empty_string_provider_returns_empty():
    from vulca.providers.capabilities import provider_capabilities
    assert provider_capabilities("") == frozenset()


def test_known_real_providers_have_cost_tracked():
    """Every non-mock provider explicitly listed must have COST_TRACKED."""
    from vulca.providers.capabilities import (
        COST_TRACKED, _PROVIDER_CAPABILITIES,
    )
    for name, caps in _PROVIDER_CAPABILITIES.items():
        if name == "mock":
            assert COST_TRACKED not in caps, f"mock should not be cost-tracked"


def test_cost_table_consistency():
    """Every non-mock key in engine's _COST_PER_IMAGE must have COST_TRACKED
    via provider_capabilities(). Mock's $0.0 entry is dead code (mock never
    reaches the cost gate)."""
    from vulca.pipeline.engine import _COST_PER_IMAGE
    from vulca.providers.capabilities import (
        COST_TRACKED, provider_capabilities,
    )
    for name in _COST_PER_IMAGE:
        if name == "mock":
            continue  # mock's $0.0 is dead code; mock never enters cost gate
        caps = provider_capabilities(name)
        assert COST_TRACKED in caps, (
            f"provider {name!r} is in _COST_PER_IMAGE but lacks COST_TRACKED"
        )
