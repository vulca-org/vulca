"""Tests for Digestion V2 storage protocol — session, artifact, signal persistence."""
from __future__ import annotations

import pytest


def test_save_session(tmp_path):
    """Save a studio session and retrieve it."""
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief

    store = JsonlStudioStorage(data_dir=str(tmp_path))
    b = Brief.new("水墨山水", mood="serene")
    b.session_id = "test-001"

    store.save_session(b, user_feedback="accepted")

    sessions = store.get_sessions()
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == "test-001"
    assert sessions[0]["user_feedback"] == "accepted"
    assert sessions[0]["brief"]["mood"] == "serene"


def test_save_artifact(tmp_path):
    """Save an artifact analysis record."""
    from vulca.digestion.storage import JsonlStudioStorage

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    store.save_artifact(
        session_id="test-001",
        artifact_type="concept",
        file_path="concepts/c1.png",
        analysis={"l1": {"composition_type": "diagonal"}, "l2": {"stroke_style": "ink_wash"}},
    )

    artifacts = store.get_artifacts(session_id="test-001")
    assert len(artifacts) == 1
    assert artifacts[0]["artifact_type"] == "concept"
    assert artifacts[0]["analysis"]["l1"]["composition_type"] == "diagonal"


def test_append_signal(tmp_path):
    """Append per-action signals and retrieve them."""
    from vulca.digestion.storage import JsonlStudioStorage

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    store.append_signal(
        session_id="test-001",
        action="concept_select",
        phase="concept",
        data={"concept_index": 2, "total_candidates": 4, "had_notes": True},
    )
    store.append_signal(
        session_id="test-001",
        action="nl_update",
        phase="generate",
        data={"instruction": "加一座山", "fields_changed": ["elements"]},
    )

    signals = store.get_signals(session_id="test-001")
    assert len(signals) == 2
    assert signals[0]["action"] == "concept_select"
    assert signals[1]["action"] == "nl_update"
    assert signals[1]["data"]["instruction"] == "加一座山"


def test_jsonl_fallback(tmp_path):
    """Storage should work with JSONL files (no database required)."""
    from vulca.digestion.storage import JsonlStudioStorage

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    # Verify files are created in the data dir
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    store.save_session(b)
    store.append_signal(session_id=b.session_id, action="test", phase="intent", data={})
    store.save_artifact(session_id=b.session_id, artifact_type="generation", file_path="out.png", analysis={})

    # All three JSONL files should exist
    assert (tmp_path / "studio_sessions.jsonl").exists()
    assert (tmp_path / "signals.jsonl").exists()
    assert (tmp_path / "artifacts.jsonl").exists()


def test_get_sessions_by_style(tmp_path):
    """Filter sessions by style tradition."""
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    b1 = Brief.new("水墨", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b2 = Brief.new("油画", style_mix=[StyleWeight(tradition="western_academic", weight=1.0)])
    b3 = Brief.new("水墨2", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])

    store.save_session(b1)
    store.save_session(b2)
    store.save_session(b3)

    xieyi = store.get_sessions(tradition="chinese_xieyi")
    assert len(xieyi) == 2

    western = store.get_sessions(tradition="western_academic")
    assert len(western) == 1


def test_get_signals_all_sessions(tmp_path):
    """Get all signals without session filter."""
    from vulca.digestion.storage import JsonlStudioStorage

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    store.append_signal(session_id="s1", action="accept", phase="evaluate", data={})
    store.append_signal(session_id="s2", action="reject", phase="evaluate", data={})

    all_signals = store.get_signals()
    assert len(all_signals) == 2
