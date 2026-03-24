"""Tests for StudioSession -> Digestion integration."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_session_accept_saves_data(tmp_path):
    from vulca.studio.session import StudioSession, SessionState

    s = StudioSession.new("test accept", project_dir=str(tmp_path / "proj"))
    s.advance_to(SessionState.EVALUATE)

    result = await s.accept(data_dir=str(tmp_path / "data"))

    assert result["status"] == "accepted"
    assert result["session_id"] == s.session_id
    assert s.state == SessionState.DONE

    # Check data was saved
    from vulca.digestion.store import StudioStore
    store = StudioStore(data_dir=tmp_path / "data")
    sessions = store.load_sessions()
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == s.session_id


@pytest.mark.asyncio
async def test_session_accept_extracts_signals(tmp_path):
    from vulca.studio.session import StudioSession, SessionState
    from vulca.studio.types import GenerationRound

    s = StudioSession.new("signals test", project_dir=str(tmp_path / "proj"))
    s.brief.generations = [
        GenerationRound(round_num=1, image_path="r1.png",
                        scores={"L1": 0.9, "L2": 0.5, "L3": 0.8, "L4": 0.7, "L5": 0.6})
    ]
    s.advance_to(SessionState.EVALUATE)

    result = await s.accept(data_dir=str(tmp_path / "data"))

    assert "signals" in result
    assert result["signals"]["dimension_difficulty"]["weakest"] == "L2"


def test_session_on_complete_sync(tmp_path):
    """on_complete can be called synchronously too."""
    from vulca.studio.session import StudioSession, SessionState

    s = StudioSession.new("sync test", project_dir=str(tmp_path / "proj"))
    s.advance_to(SessionState.DONE)
    s.on_complete_sync(data_dir=str(tmp_path / "data"))

    from vulca.digestion.store import StudioStore
    store = StudioStore(data_dir=tmp_path / "data")
    sessions = store.load_sessions()
    assert len(sessions) == 1
