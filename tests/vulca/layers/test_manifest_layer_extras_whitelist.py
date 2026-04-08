"""v0.13.2 P2: layer_extras is whitelisted; unknown keys raise."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from vulca.layers.manifest import ALLOWED_LAYER_EXTRAS_KEYS, write_manifest
from vulca.layers.types import LayerInfo


def _layer() -> LayerInfo:
    return LayerInfo(
        name="layer1",
        description="t",
        z_index=0,
        id="test-layer",
        content_type="subject",
    )


def test_whitelist_includes_known_runtime_keys():
    expected_min = {
        "source", "status", "cache_hit", "attempts",
        "canvas_color", "key_strategy", "reason", "validation",
    }
    assert expected_min.issubset(ALLOWED_LAYER_EXTRAS_KEYS)


def test_known_extras_written_successfully(tmp_path: Path):
    path = write_manifest(
        [_layer()],
        output_dir=str(tmp_path),
        width=1024, height=1024,
        layer_extras={"test-layer": {"source": "a", "status": "ok", "attempts": 1}},
    )
    m = json.loads(Path(path).read_text())
    entry = m["layers"][0]
    assert entry.get("source") == "a"
    assert entry.get("status") == "ok"
    assert entry.get("attempts") == 1


def test_unknown_extras_key_raises(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown layer_extras key"):
        write_manifest(
            [_layer()],
            output_dir=str(tmp_path),
            width=1024, height=1024,
            layer_extras={"test-layer": {"NOT_ALLOWED": 42}},
        )


def test_extras_cannot_shadow_core_field(tmp_path: Path):
    """Even a key like 'id' must be rejected by whitelist."""
    with pytest.raises(ValueError, match="unknown layer_extras key"):
        write_manifest(
            [_layer()],
            output_dir=str(tmp_path),
            width=1024, height=1024,
            layer_extras={"test-layer": {"id": "shadow-attempt"}},
        )
