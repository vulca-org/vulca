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


def test_inner_importerror_propagates(tmp_path, monkeypatch):
    """A valid tier-2 module whose own body raises ImportError from an
    internal dependency must NOT be misclassified as 'unknown strategy'.
    The original ImportError should propagate unchanged."""
    mod_path = tmp_path / "broken_keying_module.py"
    mod_path.write_text('raise ImportError("inner")\n')
    monkeypatch.syspath_prepend(str(tmp_path))

    # Ensure a stale cached import doesn't mask the failure.
    import sys
    sys.modules.pop("broken_keying_module", None)

    with pytest.raises(ImportError, match="inner"):
        get_keying_strategy("broken_keying_module:Foo")


def test_tier_two_loader_resolves_valid_module_callable(tmp_path, monkeypatch):
    """Tier-2 escape hatch resolves a real module:callable spec."""
    mod_dir = tmp_path / "tier2_pkg"
    mod_dir.mkdir()
    (mod_dir / "__init__.py").write_text("")
    (mod_dir / "fake_keying.py").write_text(
        "from vulca.layers.keying.luminance import LuminanceKeying\n"
        "def make() -> LuminanceKeying:\n"
        "    return LuminanceKeying()\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    import sys
    sys.modules.pop("tier2_pkg", None)
    sys.modules.pop("tier2_pkg.fake_keying", None)

    from vulca.layers.keying import get_keying_strategy
    from vulca.layers.keying.luminance import LuminanceKeying

    strategy = get_keying_strategy("tier2_pkg.fake_keying:make")
    assert isinstance(strategy, LuminanceKeying)
