"""Tests for cold storage archiver."""
from __future__ import annotations

import json
import pytest


def test_archive_session_to_local(tmp_path):
    """Archive a session to local cold storage (mock for GCS)."""
    from vulca.digestion.archiver import LocalArchiver
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    archiver = LocalArchiver(archive_dir=str(tmp_path / "archive"))

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.generations = [GenerationRound(round_num=1, image_path="r1.png",
                                      scores={"L1": 0.8, "L2": 0.5})]

    path = archiver.archive_session(b, user_feedback="accepted")

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["session_id"] == b.session_id
    assert data["user_feedback"] == "accepted"


def test_archive_all_brief_versions(tmp_path):
    """Archive should preserve all Brief update history."""
    from vulca.digestion.archiver import LocalArchiver
    from vulca.studio.brief import Brief
    from vulca.studio.types import BriefUpdate

    archiver = LocalArchiver(archive_dir=str(tmp_path / "archive"))

    b = Brief.new("test")
    b.updates = [
        BriefUpdate(timestamp="t1", instruction="changed mood", fields_changed=["mood"]),
        BriefUpdate(timestamp="t2", instruction="added element", fields_changed=["elements"]),
    ]

    path = archiver.archive_session(b)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert len(data["brief"]["updates"]) == 2


def test_archive_non_blocking(tmp_path):
    """Archiving should not block the caller."""
    from vulca.digestion.archiver import LocalArchiver
    from vulca.studio.brief import Brief
    import time

    archiver = LocalArchiver(archive_dir=str(tmp_path / "archive"))
    b = Brief.new("test")

    start = time.monotonic()
    archiver.archive_session(b)
    elapsed = time.monotonic() - start

    # Should complete very quickly (local file write)
    assert elapsed < 1.0
