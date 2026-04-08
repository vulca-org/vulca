import pytest
from vulca.layers.keying import get_keying_strategy
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.keying.chroma import ChromaKeying, DeltaEKeying

def test_get_luminance():
    assert isinstance(get_keying_strategy("luminance"), LuminanceKeying)

def test_get_chroma():
    assert isinstance(get_keying_strategy("chroma"), ChromaKeying)

def test_get_delta_e():
    assert isinstance(get_keying_strategy("delta_e"), DeltaEKeying)

def test_default_when_none():
    assert isinstance(get_keying_strategy(None), LuminanceKeying)
    assert isinstance(get_keying_strategy(""), LuminanceKeying)

def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="unknown keying strategy"):
        get_keying_strategy("nonsense")

def test_dotted_path_callable_loaded(monkeypatch):
    """Tier 2 escape hatch: 'module.path:fn' imports and uses fn."""
    import sys, types
    mod = types.ModuleType("test_keying_custom_mod")
    class Dummy:
        def extract_alpha(self, rgb, canvas):
            import numpy as np
            return np.zeros(rgb.shape[:2], dtype="float32")
    def factory():
        return Dummy()
    mod.factory = factory
    sys.modules["test_keying_custom_mod"] = mod
    try:
        strat = get_keying_strategy("test_keying_custom_mod:factory")
        assert isinstance(strat, Dummy)
    finally:
        del sys.modules["test_keying_custom_mod"]
