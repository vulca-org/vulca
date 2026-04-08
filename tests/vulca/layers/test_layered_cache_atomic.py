"""v0.13.2 P2: LayerCache.put uses atomic temp-write-and-rename."""
from __future__ import annotations

import os as _os
from pathlib import Path
from unittest.mock import patch

from vulca.layers.layered_cache import LayerCache


def test_put_uses_atomic_replace(tmp_path: Path):
    cache = LayerCache(tmp_path)
    calls: list[str] = []
    real_replace = _os.replace

    def tracking_replace(src, dst):
        calls.append("replace")
        real_replace(src, dst)

    with patch("vulca.layers.layered_cache.os.replace", side_effect=tracking_replace):
        cache.put("abc123", b"PNGDATA")

    assert calls == ["replace"]
    assert (tmp_path / ".layered_cache" / "abc123.png").read_bytes() == b"PNGDATA"


def test_put_no_partial_file_on_crash(tmp_path: Path):
    cache = LayerCache(tmp_path)

    class Boom(RuntimeError):
        pass

    with patch("vulca.layers.layered_cache.os.replace", side_effect=Boom("kaboom")):
        try:
            cache.put("abc123", b"PNGDATA")
        except Boom:
            pass

    final = tmp_path / ".layered_cache" / "abc123.png"
    assert not final.exists(), "partial write leaked into final cache path"
