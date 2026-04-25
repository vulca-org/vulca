"""v0.17.14 — composite_layers must not mutate source layer files by default.

Codex finding from the parallel review of 2026-04-25: pre-v0.17.14
``composite_layers`` unconditionally ran ``ensure_alpha`` and wrote the
result back to each ``lr.image_path``. A "preview" call thereby mutated
the user's source layers — destructive, surprising, and the kind of
side-effect that makes layered editing flows brittle.

Default is now non-destructive; legacy mutation is opt-in via
``force_alpha_writeback=True``.
"""
from __future__ import annotations

import os
import tempfile

from PIL import Image

from vulca.layers.composite import composite_layers
from vulca.layers.types import LayerInfo, LayerResult


def _make_layer_file(color, z_index=0):
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    Image.new("RGBA", (50, 50), color).save(path)
    info = LayerInfo(
        name=f"layer_{z_index}",
        description="t", z_index=z_index, blend_mode="normal",
    )
    return LayerResult(info=info, image_path=path)


def test_default_does_not_overwrite_source_layer_files(tmp_path):
    """Hash before == hash after when force_alpha_writeback unset."""
    layer = _make_layer_file((123, 45, 67, 200))
    before_bytes = open(layer.image_path, "rb").read()

    out_path = str(tmp_path / "preview.png")
    composite_layers(
        [layer], width=50, height=50, output_path=out_path,
    )

    after_bytes = open(layer.image_path, "rb").read()
    assert after_bytes == before_bytes, (
        "v0.17.14: composite_layers must not mutate source layer files in "
        "preview mode (default force_alpha_writeback=False)"
    )


def test_force_alpha_writeback_true_does_mutate(tmp_path):
    """Opt-in: force_alpha_writeback=True allows the legacy in-place rewrite.

    For ordinary RGBA layers ensure_alpha is essentially a re-encode, which
    can change the on-disk bytes (timestamps, IDAT layout). We assert the
    file still exists and is a valid PNG; bit-identity isn't required for
    the legacy path.
    """
    layer = _make_layer_file((123, 45, 67, 200))

    out_path = str(tmp_path / "writeback.png")
    composite_layers(
        [layer], width=50, height=50, output_path=out_path,
        force_alpha_writeback=True,
    )

    # Layer file still loads
    re_opened = Image.open(layer.image_path)
    assert re_opened.size == (50, 50)
    assert re_opened.mode == "RGBA"
