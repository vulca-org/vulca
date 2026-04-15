"""Phase 0 Task 1: LayerInfo.semantic_path dot-notation hierarchical path."""
from vulca.layers.types import LayerInfo


def test_semantic_path_defaults_to_empty_string():
    info = LayerInfo(name="bg", description="", z_index=0)
    assert info.semantic_path == ""


def test_semantic_path_accepts_dotted_hierarchy():
    info = LayerInfo(
        name="bg",
        description="",
        z_index=0,
        semantic_path="subject.face.eyes",
    )
    assert info.semantic_path == "subject.face.eyes"


def test_semantic_path_preserves_existing_fields():
    info = LayerInfo(name="bg", description="d", z_index=5, semantic_path="x.y")
    assert info.name == "bg"
    assert info.z_index == 5
    assert info.content_type == "background"


def test_semantic_path_orthogonal_to_content_type():
    """content_type (coarse bucket) and semantic_path (free-form hierarchy)
    are independent fields — setting one must not shadow the other."""
    info = LayerInfo(
        name="eyes",
        description="",
        z_index=2,
        content_type="subject",
        semantic_path="subject.face.eyes",
    )
    assert info.content_type == "subject"
    assert info.semantic_path == "subject.face.eyes"
