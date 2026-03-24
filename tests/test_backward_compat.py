"""Backward compatibility tests — existing APIs must remain unchanged."""
from __future__ import annotations

import pytest


def test_existing_evaluate_api():
    """vulca.evaluate() signature and mock behavior unchanged."""
    import vulca
    result = vulca.evaluate("nonexistent.jpg", tradition="chinese_xieyi", mock=True)
    assert hasattr(result, "score")
    assert hasattr(result, "dimensions")
    assert hasattr(result, "tradition")
    assert hasattr(result, "suggestions")


def test_existing_create_api():
    """vulca.create() signature and mock behavior unchanged."""
    import vulca
    result = vulca.create("test art", tradition="chinese_xieyi", provider="mock")
    assert hasattr(result, "session_id")
    assert hasattr(result, "status")
    assert hasattr(result, "weighted_total")


def test_existing_traditions_api():
    """vulca.traditions() returns list of strings."""
    import vulca
    traditions = vulca.traditions()
    assert isinstance(traditions, list)
    assert "chinese_xieyi" in traditions


def test_existing_get_weights_api():
    """vulca.get_weights() returns L1-L5 dict."""
    import vulca
    weights = vulca.get_weights("chinese_xieyi")
    assert isinstance(weights, dict)
    assert "L1" in weights
    assert abs(sum(weights.values()) - 1.0) < 0.01


def test_studio_import_does_not_break_existing():
    """Importing studio should not affect existing vulca API."""
    from vulca.studio import Brief, StudioSession, SessionState
    import vulca

    # Existing API still works
    traditions = vulca.traditions()
    assert len(traditions) > 0
    assert hasattr(vulca, "evaluate")
    assert hasattr(vulca, "create")
