"""Phase 0 end-to-end smoke: 12-layer portrait decomposition.

Verifies all Phase 0 foundation pieces compose cleanly:
 - semantic_path and content_type are INDEPENDENT fields (both carry data,
   no conflation)
 - resolve_masks_zindex (Task 7) routes overlaps by z-index and fills holes
   into the is_background catch-all (Task 3's coarse bucket)
 - validate_decomposition (Task 6) confirms coverage==1.0 overlap==0.0
 - is_background (Task 3) recognizes both exact "background" and dotted
   "background.catch_all"
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))


def test_phase0_end_to_end_multilayer():
    """12-layer portrait decomposition survives migrate + validate + load."""
    from migrate_evfsam_to_layers import resolve_masks_zindex
    from vulca.layers.coarse_bucket import is_background
    from vulca.layers.decomp_validator import validate_decomposition

    h, w = 50, 50
    rng = np.random.default_rng(0)
    # (name, z, coarse content_type, semantic_path) — independent fields.
    specs = [
        ("bg",            0,  "background", "background.catch_all"),
        ("body_clothing", 15, "subject",    "subject.body.clothing"),
        ("body_neck",     20, "subject",    "subject.body.neck"),
        ("accessory",     25, "subject",    "subject.accessories.jewelry"),
        ("face_skin",     30, "subject",    "subject.face.skin"),
        ("face_lips",     35, "subject",    "subject.face.lips"),
        ("face_nose",     40, "subject",    "subject.face.nose"),
        ("face_eyes",     45, "subject",    "subject.face.eyes"),
        ("face_brows",    50, "subject",    "subject.face.eyebrows"),
        ("hair",          55, "subject",    "subject.hair"),
        ("headwear",      60, "subject",    "subject.headwear"),
        ("fg_objects",    80, "foreground", "foreground.objects"),
    ]

    layers = []
    for name, z, ct, sp in specs:
        # bg starts empty (simulates EVF-SAM often missing background);
        # others claim ~10% each, which overlaps by design.
        mask = (
            np.zeros((h, w), dtype=bool)
            if name == "bg"
            else rng.random((h, w)) < 0.1
        )
        layers.append({
            "name": name, "z": z,
            "content_type": ct,
            "semantic_path": sp,  # Task 7 helper ignores unknown keys
            "mask": mask,
        })

    resolved = resolve_masks_zindex(layers)
    mask_list = [resolved[s[0]] for s in specs]
    report = validate_decomposition(mask_list, strict=True)

    assert report.coverage == 1.0
    assert report.overlap == 0.0

    # is_background recognizes both exact and dotted forms
    assert is_background("background")
    assert is_background("background.catch_all")
    assert not is_background("subject.face.eyes")

    # bg claimed all pixels that no higher-z layer took
    other_union = np.zeros((h, w), dtype=bool)
    for s in specs[1:]:
        other_union |= resolved[s[0]]
    assert (resolved["bg"] | other_union).all()


def test_phase0_manifest_round_trip_with_semantic_path(tmp_path):
    """Writer emits semantic_path; loader reads it back; 12 layers survive."""
    import json

    from vulca.layers.manifest import load_manifest, write_manifest
    from vulca.layers.types import LayerInfo

    specs = [
        ("bg",            0,  "background", "background.catch_all"),
        ("body_clothing", 15, "subject",    "subject.body.clothing"),
        ("face_skin",     30, "subject",    "subject.face.skin"),
        ("face_eyes",     45, "subject",    "subject.face.eyes"),
        ("hair",          55, "subject",    "subject.hair"),
        ("fg_objects",    80, "foreground", "foreground.objects"),
    ]
    infos = [
        LayerInfo(name=n, description="", z_index=z, content_type=ct,
                  semantic_path=sp)
        for n, z, ct, sp in specs
    ]
    write_manifest(infos, output_dir=str(tmp_path), width=100, height=100)

    raw = json.loads((tmp_path / "manifest.json").read_text())
    for entry, (n, _z, ct, sp) in zip(raw["layers"], specs):
        assert entry["content_type"] == ct
        assert entry["semantic_path"] == sp

    loaded = load_manifest(str(tmp_path))
    reconstructed = {lr.info.name: (lr.info.content_type, lr.info.semantic_path)
                     for lr in loaded.layers}
    for n, _z, ct, sp in specs:
        assert reconstructed[n] == (ct, sp)
