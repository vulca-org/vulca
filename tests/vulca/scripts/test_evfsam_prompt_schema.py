"""Phase 0 Task 9: parse_prompt_entry — 2/3-tuple tolerant."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from evfsam_showcase import parse_prompt_entry  # noqa: E402


def test_parse_two_element_tuple_defaults_semantic_path_to_name():
    name, prompt, path = parse_prompt_entry(["bg", "the sky"])
    assert name == "bg"
    assert prompt == "the sky"
    assert path == "bg"


def test_parse_three_element_tuple_uses_explicit_path():
    name, prompt, path = parse_prompt_entry(["bg", "the sky", "background.sky"])
    assert name == "bg"
    assert prompt == "the sky"
    assert path == "background.sky"


def test_parse_rejects_short_tuple():
    with pytest.raises(ValueError):
        parse_prompt_entry(["bg"])


def test_parse_tolerates_tuple_input():
    """Input can be list or tuple (JSON loader yields lists; in-memory code uses tuples)."""
    name, prompt, path = parse_prompt_entry(("bg", "sky"))
    assert (name, prompt, path) == ("bg", "sky", "bg")
