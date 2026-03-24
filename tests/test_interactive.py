"""Tests for interactive studio terminal."""
from __future__ import annotations

import pytest


def test_interactive_run_mock(tmp_path, monkeypatch):
    """Full studio run with simulated user input."""
    from vulca.studio.interactive import run_studio

    # Simulate user inputs: mood=1 (first option), brush=1, select concept=1, accept=a
    inputs = iter(["1", "1", "1", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    result = run_studio(
        intent="水墨山水",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
        concept_count=2,
    )

    assert result is not None
    assert result["status"] == "accepted"
    assert (tmp_path / "proj" / "brief.yaml").exists()


def test_interactive_with_update(tmp_path, monkeypatch):
    """Studio run where user updates Brief mid-flow."""
    # mood=1, brush=1, select=1, then update instead of accept, then accept
    inputs = iter(["1", "1", "1", "u", "加入更多雾气", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    from vulca.studio.interactive import run_studio
    result = run_studio(
        intent="山水画",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
        concept_count=2,
    )

    assert result is not None
    assert result["status"] == "accepted"


def test_interactive_quit(tmp_path, monkeypatch):
    """User can quit at any time."""
    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    from vulca.studio.interactive import run_studio
    result = run_studio(
        intent="test",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
    )

    assert result is not None
    assert result["status"] == "quit"
