"""Tests for StudioSession state machine."""
from __future__ import annotations

import pytest


def test_session_new():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("水墨山水", project_dir="/tmp/vulca-test-session-new")
    assert s.state == SessionState.INTENT
    assert s.brief.intent == "水墨山水"
    assert s.session_id


def test_session_state_transitions():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("test", project_dir="/tmp/vulca-test-session-trans")
    assert s.state == SessionState.INTENT
    s.advance_to(SessionState.CONCEPT)
    assert s.state == SessionState.CONCEPT
    s.advance_to(SessionState.GENERATE)
    assert s.state == SessionState.GENERATE


def test_session_rollback():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("test", project_dir="/tmp/vulca-test-session-roll")
    s.advance_to(SessionState.GENERATE)
    s.rollback_to(SessionState.CONCEPT)
    assert s.state == SessionState.CONCEPT


def test_session_save_load(tmp_path):
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("save test", project_dir=str(tmp_path / "proj"))
    s.advance_to(SessionState.CONCEPT)
    s.brief.mood = "serene"
    s.save()

    loaded = StudioSession.load(str(tmp_path / "proj"))
    assert loaded.state == SessionState.CONCEPT
    assert loaded.brief.mood == "serene"
    assert loaded.brief.intent == "save test"


def test_session_cannot_advance_backward():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("test", project_dir="/tmp/vulca-test-session-back")
    s.advance_to(SessionState.GENERATE)
    with pytest.raises(ValueError):
        s.advance_to(SessionState.INTENT)
