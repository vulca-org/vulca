"""Unit tests for SessionDigest types and SessionStore."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.prototype.session.types import RoundSnapshot, SessionDigest
from app.prototype.session.store import SessionStore


def test_round_snapshot_to_dict():
    snap = RoundSnapshot(round_num=1, candidates_generated=4, weighted_total=0.72)
    d = snap.to_dict()
    assert d["round_num"] == 1
    assert d["weighted_total"] == 0.72


def test_session_digest_defaults():
    digest = SessionDigest()
    assert digest.session_id.startswith("sess-")
    assert digest.mode == "create"
    assert digest.tradition == "default"
    assert digest.user_type == "human"
    assert digest.rounds == []
    assert digest.feedback == []


def test_session_digest_to_dict():
    digest = SessionDigest(
        mode="evaluate",
        intent="check ink wash",
        tradition="chinese_xieyi",
        final_scores={"L1": 0.8, "L2": 0.7},
        final_weighted_total=0.75,
    )
    d = digest.to_dict()
    assert d["mode"] == "evaluate"
    assert d["tradition"] == "chinese_xieyi"
    assert d["final_scores"]["L1"] == 0.8


def test_session_digest_with_rounds():
    snap = RoundSnapshot(round_num=1, decision="accept", weighted_total=0.85)
    digest = SessionDigest(
        mode="create",
        rounds=[snap],
        total_rounds=1,
    )
    d = digest.to_dict()
    assert len(d["rounds"]) == 1
    assert d["rounds"][0]["decision"] == "accept"


def test_store_append_and_read():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "sessions.jsonl")
        # Reset singleton for isolated test
        SessionStore._instance = None
        store = SessionStore(path)

        assert store.count() == 0
        assert store.get_all() == []

        digest1 = SessionDigest(mode="evaluate", tradition="chinese_xieyi")
        digest2 = SessionDigest(mode="create", tradition="watercolor")
        store.append(digest1)
        store.append(digest2)

        assert store.count() == 2
        all_records = store.get_all()
        assert len(all_records) == 2
        assert all_records[0]["mode"] == "evaluate"
        assert all_records[1]["tradition"] == "watercolor"

        # Reset singleton
        SessionStore._instance = None


def test_store_get_recent():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "sessions.jsonl")
        SessionStore._instance = None
        store = SessionStore(path)

        for i in range(5):
            store.append(SessionDigest(intent=f"intent_{i}"))

        recent = store.get_recent(limit=3)
        assert len(recent) == 3
        assert recent[0]["intent"] == "intent_2"

        SessionStore._instance = None


def test_store_get_by_tradition():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "sessions.jsonl")
        SessionStore._instance = None
        store = SessionStore(path)

        store.append(SessionDigest(tradition="chinese_xieyi"))
        store.append(SessionDigest(tradition="watercolor"))
        store.append(SessionDigest(tradition="chinese_xieyi"))

        by_xieyi = store.get_by_tradition("chinese_xieyi")
        assert len(by_xieyi) == 2

        SessionStore._instance = None


def test_store_handles_malformed_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sessions.jsonl"
        path.write_text('{"session_id": "ok"}\n{bad json}\n{"session_id": "ok2"}\n')

        SessionStore._instance = None
        store = SessionStore(str(path))
        records = store.get_all()
        assert len(records) == 2

        SessionStore._instance = None
