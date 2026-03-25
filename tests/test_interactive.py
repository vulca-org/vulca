"""Tests for interactive studio terminal."""
from __future__ import annotations

import pytest


def test_interactive_run_mock(tmp_path, monkeypatch):
    """Full studio run with simulated user input."""
    from vulca.studio.interactive import run_studio

    # sketch=skip, mood=1, composition=1, palette=1, elements=1, brush=1, concept=1, accept=a
    inputs = iter(["", "1", "1", "1", "1", "1", "1", "a"])
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
    # sketch=skip, 5 questions=1, concept=1, update, instruction, accept
    inputs = iter(["", "1", "1", "1", "1", "1", "1", "u", "加入更多雾气", "a"])
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
    inputs = iter(["", "q"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    from vulca.studio.interactive import run_studio
    result = run_studio(
        intent="test",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
    )

    assert result is not None
    assert result["status"] == "quit"


# --- Step 1.5: Sketch Upload in Interactive Flow (E6) ---


def test_interactive_asks_for_sketch(tmp_path, monkeypatch):
    """Interactive flow should ask user for a sketch path."""
    from vulca.studio.interactive import run_studio

    asked_prompts = []
    # sketch=empty, 5 questions=1, concept=1, accept=a
    inputs = iter(["", "1", "1", "1", "1", "1", "1", "a"])

    def fake_input(prompt=""):
        asked_prompts.append(prompt)
        return next(inputs)

    monkeypatch.setattr("builtins.input", fake_input)

    run_studio(intent="水墨山水", project_dir=str(tmp_path / "proj"), provider="mock", concept_count=2)

    # At least one prompt should mention sketch/reference
    sketch_asked = any("sketch" in p.lower() or "参考" in p or "草图" in p for p in asked_prompts)
    assert sketch_asked, f"No sketch prompt found in: {asked_prompts}"


def test_interactive_sketch_path_set_on_brief(tmp_path, monkeypatch):
    """When user provides a sketch path, it should be set on Brief."""
    from vulca.studio.interactive import run_studio

    # Create a fake sketch file
    sketch = tmp_path / "sketch.jpg"
    sketch.write_bytes(b"\xff\xd8\xff")  # Fake JPEG header

    # sketch=path, 5 questions=1, concept=1, accept=a
    inputs = iter([str(sketch), "1", "1", "1", "1", "1", "1", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    result = run_studio(
        intent="水墨山水",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
        concept_count=2,
    )

    assert result["status"] == "accepted"
    # Check Brief was saved with sketch
    from vulca.studio.brief import Brief
    brief = Brief.load(tmp_path / "proj")
    assert brief.user_sketch == str(sketch)


def test_interactive_sketch_skip_on_empty(tmp_path, monkeypatch):
    """Empty Enter should skip sketch, user_sketch stays empty."""
    from vulca.studio.interactive import run_studio

    # sketch=empty, 5 questions=1, concept=1, accept=a
    inputs = iter(["", "1", "1", "1", "1", "1", "1", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    result = run_studio(
        intent="水墨山水",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
        concept_count=2,
    )

    assert result["status"] == "accepted"
    from vulca.studio.brief import Brief
    brief = Brief.load(tmp_path / "proj")
    assert brief.user_sketch == ""
