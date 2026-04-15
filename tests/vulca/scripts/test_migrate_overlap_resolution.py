"""Phase 0 Task 7: z-index driven overlap resolution in migrate script.

resolve_masks_zindex must:
 1. Clear higher-z masks from lower-z (foreground beats subject beats background).
 2. Fill unclaimed pixels into the layer whose content_type is_background.
 3. Work for arbitrary layer counts, not just 3.
 4. Treat dotted content_type (background.catch_all) correctly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from migrate_evfsam_to_layers import (  # noqa: E402
    _z_index_for,
    resolve_masks_zindex,
)


def _mask(h: int, w: int, *, y1: int = 0, y2: int | None = None) -> np.ndarray:
    m = np.zeros((h, w), dtype=bool)
    m[y1:y2, :] = True
    return m


def test_z_index_for_dotted_falls_back_to_coarse_bucket():
    """subject.face.eyes must resolve via coarse bucket to Z_INDEX['subject']."""
    from migrate_evfsam_to_layers import Z_INDEX
    assert _z_index_for("subject.face.eyes") == Z_INDEX["subject"]
    assert _z_index_for("background.catch_all") == Z_INDEX["background"]
    assert _z_index_for("person[0].hair") == Z_INDEX["subject"]


def test_z_index_for_exact_name_still_works():
    from migrate_evfsam_to_layers import Z_INDEX
    assert _z_index_for("subject") == Z_INDEX["subject"]
    assert _z_index_for("background") == Z_INDEX["background"]
    assert _z_index_for("foreground") == Z_INDEX["foreground"]


def test_z_index_for_unknown_falls_through_to_99():
    assert _z_index_for("completely_unknown_bucket_xyz") == 99


def test_resolve_three_layers_higher_z_wins():
    h, w = 10, 10
    bg = np.ones((h, w), dtype=bool)
    subj = _mask(h, w, y1=3, y2=8)
    fg = _mask(h, w, y1=5, y2=7)
    layers = [
        {"name": "bg", "z": 0, "content_type": "background", "mask": bg},
        {"name": "subj", "z": 30, "content_type": "subject", "mask": subj},
        {"name": "fg", "z": 80, "content_type": "foreground", "mask": fg},
    ]
    out = resolve_masks_zindex(layers)
    assert (out["fg"] == fg).all()
    assert not (out["subj"] & out["fg"]).any()
    assert not (out["bg"] & (out["subj"] | out["fg"])).any()
    assert (out["bg"] | out["subj"] | out["fg"]).sum() == h * w


def test_resolve_fills_unclaimed_into_background():
    h, w = 10, 10
    bg = np.zeros((h, w), dtype=bool)
    subj = _mask(h, w, y1=3, y2=7)
    layers = [
        {"name": "bg", "z": 0, "content_type": "background", "mask": bg},
        {"name": "subj", "z": 50, "content_type": "subject", "mask": subj},
    ]
    out = resolve_masks_zindex(layers)
    assert (out["bg"] | out["subj"]).all()
    assert not (out["bg"] & out["subj"]).any()


def test_resolve_many_layers_portrait():
    h, w = 20, 20
    rng = np.random.default_rng(42)
    layers = []
    for i in range(20):
        name = f"layer_{i}"
        mask = rng.random((h, w)) < 0.3
        layers.append({
            "name": name, "z": i * 5,
            "content_type": "background" if i == 0 else f"subject.layer_{i}",
            "mask": mask,
        })
    out = resolve_masks_zindex(layers)
    stack = np.zeros((h, w), dtype=np.uint16)
    for name in out:
        stack += out[name].astype(np.uint16)
    assert (stack == 1).all(), "some pixel is claimed by 0 or 2+ layers"


def test_dotted_background_is_catch_all():
    h, w = 10, 10
    bg = np.zeros((h, w), dtype=bool)
    subj = _mask(h, w, y1=2, y2=8)
    layers = [
        {"name": "bg", "z": 0, "content_type": "background.catch_all", "mask": bg},
        {"name": "subj", "z": 30, "content_type": "subject.face", "mask": subj},
    ]
    out = resolve_masks_zindex(layers)
    assert (out["bg"] | out["subj"]).all()


def test_resolve_tiebreaker_is_input_order():
    """Two layers at same z: first-in-input wins contested pixels."""
    h, w = 4, 4
    a = np.ones((h, w), dtype=bool)
    b = np.ones((h, w), dtype=bool)
    layers = [
        {"name": "a", "z": 50, "content_type": "subject", "mask": a},
        {"name": "b", "z": 50, "content_type": "subject", "mask": b},
    ]
    out = resolve_masks_zindex(layers)
    assert out["a"].all()
    assert not out["b"].any()


def test_resolve_raises_on_empty():
    with pytest.raises(ValueError, match="empty"):
        resolve_masks_zindex([])


def test_resolve_raises_on_shape_mismatch():
    layers = [
        {"name": "a", "z": 0, "content_type": "background",
         "mask": np.zeros((4, 4), dtype=bool)},
        {"name": "b", "z": 10, "content_type": "subject",
         "mask": np.zeros((5, 5), dtype=bool)},
    ]
    with pytest.raises(ValueError, match="shape"):
        resolve_masks_zindex(layers)


def test_resolve_raises_on_holes_without_background():
    """If no is_background layer is present AND union doesn't cover canvas,
    resolve must raise rather than silently leave holes for validator to find."""
    h, w = 4, 4
    a = _mask(h, w, y1=0, y2=2)
    b = _mask(h, w, y1=2, y2=3)
    layers = [
        {"name": "a", "z": 10, "content_type": "subject", "mask": a},
        {"name": "b", "z": 20, "content_type": "foreground", "mask": b},
    ]
    with pytest.raises(ValueError, match="background|catch-all|holes"):
        resolve_masks_zindex(layers)


def test_resolve_full_coverage_without_background_is_ok():
    """If layers happen to cover the full canvas without an is_background
    layer, that's fine — no holes to fill."""
    h, w = 4, 4
    a = _mask(h, w, y1=0, y2=2)
    b = _mask(h, w, y1=2, y2=4)
    layers = [
        {"name": "a", "z": 10, "content_type": "subject", "mask": a},
        {"name": "b", "z": 20, "content_type": "foreground", "mask": b},
    ]
    out = resolve_masks_zindex(layers)
    assert (out["a"] | out["b"]).all()


def test_z_index_for_empty_name_raises():
    with pytest.raises(ValueError, match="empty|name"):
        _z_index_for("")


def test_make_manifest_passes_semantic_path_through(tmp_path):
    """3-tuple entries emit semantic_path into per-layer dict."""
    from PIL import Image
    import migrate_evfsam_to_layers as m

    prompts = [
        ("background", "the sky", "background.sky"),
        ("subject", "the person", "subject.body"),
    ]
    orig_orig = m.ORIG
    orig_repo = m.REPO
    m.ORIG = tmp_path
    m.REPO = tmp_path
    try:
        Image.new("RGB", (100, 100), "red").save(tmp_path / "test.jpg", "JPEG")
        manifest = m.make_manifest("test", prompts)
        paths = {l["name"]: l.get("semantic_path") for l in manifest["layers"]}
        assert paths["background"] == "background.sky"
        assert paths["subject"] == "subject.body"
    finally:
        m.ORIG = orig_orig
        m.REPO = orig_repo


def test_make_manifest_defaults_semantic_path_to_name_for_2tuple(tmp_path):
    """2-tuple legacy entries: semantic_path defaults to layer_name
    (NOT empty string — matches Task 9 parse_prompt_entry policy)."""
    from PIL import Image
    import migrate_evfsam_to_layers as m

    prompts = [
        ("background", "the sky"),
        ("subject", "the person"),
    ]
    orig_orig = m.ORIG
    orig_repo = m.REPO
    m.ORIG = tmp_path
    m.REPO = tmp_path
    try:
        Image.new("RGB", (100, 100), "red").save(tmp_path / "test.jpg", "JPEG")
        manifest = m.make_manifest("test", prompts)
        paths = {l["name"]: l.get("semantic_path") for l in manifest["layers"]}
        assert paths["background"] == "background"
        assert paths["subject"] == "subject"
    finally:
        m.ORIG = orig_orig
        m.REPO = orig_repo
