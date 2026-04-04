"""Tests that blend.py is a pure blend math engine with no alpha extraction."""
import inspect
import pytest

from vulca.layers.blend import blend_layers, blend_normal, blend_multiply, blend_screen


class TestBlendPurity:
    def test_no_white_to_alpha_function(self):
        import vulca.layers.blend as mod
        assert not hasattr(mod, "_white_to_alpha"), \
            "_white_to_alpha does not belong in blend.py"

    def test_blend_layers_no_content_type_check(self):
        source = inspect.getsource(blend_layers)
        assert "content_type" not in source, \
            "blend_layers should not check content_type"

    def test_blend_layers_no_z_index_conditional(self):
        source = inspect.getsource(blend_layers)
        assert "z_index > " not in source and "z_index !=" not in source, \
            "blend_layers should not branch on z_index"

    def test_blend_normal_is_pure_math(self):
        source = inspect.getsource(blend_normal)
        assert "content_type" not in source
        assert "white" not in source.lower()

    def test_blend_multiply_is_pure_math(self):
        source = inspect.getsource(blend_multiply)
        assert "content_type" not in source
        assert "white" not in source.lower()
