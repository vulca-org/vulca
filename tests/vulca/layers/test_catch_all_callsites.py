"""Phase 0 Task 4: catch-all contract lock for dotted content_type.

Regression contract: a layer named 'background.catch_all' MUST be treated as
background (fill unclaimed pixels) rather than as a named foreground layer.
Locking the contract via is_background() at every former
`content_type == "background"` call site.
"""
from __future__ import annotations

from vulca.layers.coarse_bucket import is_background
from vulca.layers.types import LayerInfo


def test_is_background_matches_dotted_content_type():
    info = LayerInfo(name="bg", description="", z_index=0,
                     content_type="background",
                     semantic_path="background.catch_all")
    assert is_background(info.content_type) is True
    assert is_background(info.semantic_path) is True


def test_is_background_rejects_subject_face_eyes():
    info = LayerInfo(name="eyes", description="", z_index=45,
                     content_type="subject",
                     semantic_path="subject.face.eyes")
    assert is_background(info.content_type) is False
    assert is_background(info.semantic_path) is False


def test_is_background_rejects_person_indexed():
    info = LayerInfo(name="face", description="", z_index=30,
                     content_type="subject",
                     semantic_path="person[0].face")
    assert is_background(info.content_type) is False
    assert is_background(info.semantic_path) is False


def test_effect_bucket_covers_dotted_effect_paths():
    """mask.py routes `effect` content_type into the saturation-channel
    mask branch. Dotted paths like `effect.glow` or `effect.mist` must
    hit the same branch — i.e. their coarse bucket must be `effect`."""
    from vulca.layers.coarse_bucket import coarse_bucket_of
    assert coarse_bucket_of("effect") == "effect"
    assert coarse_bucket_of("effect.glow") == "effect"
    assert coarse_bucket_of("effect.mist") == "effect"
