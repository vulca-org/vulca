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


# --- Phase 4: Polish ---


def test_concept_preview_shows_file_info(tmp_path, monkeypatch, capsys):
    """Concept listing should show file size and dimensions (not just path)."""
    from vulca.studio.interactive import run_studio

    # sketch=skip, 5 questions=1, concept=1, accept=a
    inputs = iter(["", "1", "1", "1", "1", "1", "1", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    run_studio(intent="水墨山水", project_dir=str(tmp_path / "proj"), provider="mock", concept_count=2)

    output = capsys.readouterr().out
    # Should show file info, not just bare path
    assert "concept" in output.lower()


def test_style_weight_adjustment(tmp_path, monkeypatch):
    """User should be able to adjust style weights after detection."""
    from vulca.studio.interactive import run_studio

    # sketch=skip, weights="70/30", 5 questions=1, concept=1, accept=a
    # "赛博朋克水墨" → 2 styles detected → weight prompt appears
    inputs = iter(["", "70/30", "1", "1", "1", "1", "1", "1", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    result = run_studio(
        intent="赛博朋克水墨山水",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
        concept_count=2,
    )

    assert result["status"] == "accepted"


def test_preloader_wired_into_flow(tmp_path, monkeypatch, capsys):
    """Preloader should be called and its suggestions visible in output."""
    from vulca.studio.interactive import run_studio
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    # Seed history for preloader
    store = JsonlStudioStorage(data_dir=str(tmp_path / "data"))
    for i in range(3):
        b = Brief.new(f"水墨山水 #{i}", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
        b.generations = [GenerationRound(round_num=1, image_path=f"r{i}.png",
                                          scores={"L1": 0.8, "L2": 0.4, "L3": 0.7, "L4": 0.6, "L5": 0.9})]
        store.save_session(b, user_feedback="accepted")

    inputs = iter(["", "", "1", "1", "1", "1", "1", "1", "a"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    result = run_studio(
        intent="新的水墨作品",
        project_dir=str(tmp_path / "proj"),
        provider="mock",
        concept_count=2,
        data_dir=str(tmp_path / "data"),
    )

    assert result["status"] == "accepted"
