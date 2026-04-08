"""v0.13.2 P2: tier-2 keying loader wraps import errors as ValueError."""
from __future__ import annotations

import pytest

from vulca.layers.keying import get_keying_strategy


def test_unknown_module_path_raises_valueerror():
    with pytest.raises(ValueError, match="keying strategy"):
        get_keying_strategy("vulca.does_not_exist:Bogus")


def test_unknown_attribute_raises_valueerror():
    with pytest.raises(ValueError, match="keying strategy"):
        get_keying_strategy("vulca.layers.keying:NoSuchThing")


def test_known_name_still_works():
    from vulca.layers.keying.luminance import LuminanceKeying
    assert isinstance(get_keying_strategy("luminance"), LuminanceKeying)
