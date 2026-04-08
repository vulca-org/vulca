"""v0.13.2 P2: LayerCache persists ValidationReport as sidecar JSON."""
from __future__ import annotations

import json
import os as _os
from pathlib import Path
from unittest.mock import patch

from vulca.layers.layered_cache import LayerCache


def test_put_report_and_get_report_roundtrip(tmp_path: Path):
    cache = LayerCache(tmp_path)
    report = {"ok": True, "warnings": [], "errors": [], "meta": {"k": 1}}
    cache.put_report("abc123", report)
    loaded = cache.get_report("abc123")
    assert loaded == report


def test_get_report_missing_returns_none(tmp_path: Path):
    cache = LayerCache(tmp_path)
    assert cache.get_report("nonexistent") is None


def test_report_stored_as_json_sidecar(tmp_path: Path):
    cache = LayerCache(tmp_path)
    cache.put_report("abc123", {"ok": True})
    sidecar = tmp_path / ".layered_cache" / "abc123.report.json"
    assert sidecar.exists()
    assert json.loads(sidecar.read_text()) == {"ok": True}


def test_put_report_atomic(tmp_path: Path):
    """Same atomic guarantee as put() for PNGs — uses os.replace."""
    cache = LayerCache(tmp_path)
    calls: list[str] = []
    real_replace = _os.replace

    def tracking_replace(src, dst):
        calls.append("replace")
        real_replace(src, dst)

    with patch("vulca.layers.layered_cache.os.replace", side_effect=tracking_replace):
        cache.put_report("abc123", {"ok": True})

    assert calls == ["replace"]


def test_put_report_no_partial_on_crash(tmp_path: Path):
    cache = LayerCache(tmp_path)

    class Boom(RuntimeError):
        pass

    with patch("vulca.layers.layered_cache.os.replace", side_effect=Boom("kaboom")):
        try:
            cache.put_report("abc123", {"ok": True})
        except Boom:
            pass

    final = tmp_path / ".layered_cache" / "abc123.report.json"
    assert not final.exists()


def test_get_report_disabled_cache_returns_none():
    cache = LayerCache(None, enabled=False)
    assert cache.get_report("abc") is None


def test_put_report_disabled_cache_no_op():
    # Should not raise.
    cache = LayerCache(None, enabled=False)
    cache.put_report("abc", {"ok": True})
