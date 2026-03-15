"""Tests for socket color mapping."""
from app.prototype.pipeline.port_contract import DataType
from app.prototype.pipeline.socket_colors import get_socket_color, get_all_socket_colors


def test_all_datatypes_have_colors():
    """Every DataType should have a socket color."""
    for dt in DataType:
        color = get_socket_color(dt)
        assert color.startswith("#"), f"{dt} has invalid color: {color}"
        assert len(color) == 7, f"{dt} color should be 7 chars: {color}"


def test_get_all_returns_dict():
    colors = get_all_socket_colors()
    assert isinstance(colors, dict)
    assert len(colors) >= 10  # At least the original 10


def test_new_datatypes_exist():
    """New DataType members should be accessible."""
    assert DataType.IMAGE.value == "image"
    assert DataType.TEXT.value == "text"
    assert DataType.SKETCH.value == "sketch"
    assert DataType.MASK.value == "mask"
    assert DataType.SCORES.value == "scores"
    assert DataType.DECISION.value == "decision"
