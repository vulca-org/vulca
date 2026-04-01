"""Tests for build_plan_prompt — intent-to-layers planning prompt."""
from vulca.layers.plan_prompt import build_plan_prompt, get_tradition_layer_order


class TestBuildPlanPrompt:
    def test_basic_prompt_structure(self):
        prompt = build_plan_prompt("水墨山水", "chinese_xieyi")
        assert "水墨山水" in prompt
        assert "layers" in prompt.lower()
        assert "z_index" in prompt
        assert "json" in prompt.lower()

    def test_tradition_layer_order_injected(self):
        prompt = build_plan_prompt("水墨山水", "chinese_xieyi")
        assert "chinese_xieyi" in prompt or "xieyi" in prompt.lower()

    def test_default_tradition(self):
        prompt = build_plan_prompt("abstract art", "default")
        assert "z_index" in prompt

    def test_output_format_matches_analyze(self):
        prompt = build_plan_prompt("test", "default")
        for field in ["name", "description", "z_index", "blend_mode",
                       "dominant_colors", "content_type", "regeneration_prompt"]:
            assert field in prompt


class TestGetTraditionLayerOrder:
    def test_xieyi_has_entries(self):
        order = get_tradition_layer_order("chinese_xieyi")
        assert len(order) >= 3
        assert order[0]["role"] == "底纸/绢底"

    def test_unknown_tradition_returns_default(self):
        order = get_tradition_layer_order("nonexistent")
        assert len(order) >= 2


class TestTraditionLayerOrderFromYAML:
    def test_xieyi_loaded_from_yaml(self):
        order = get_tradition_layer_order("chinese_xieyi")
        assert len(order) >= 3
        assert order[0]["role"] == "底纸/绢底"

    def test_gongbi_loaded(self):
        order = get_tradition_layer_order("chinese_gongbi")
        assert len(order) >= 3
        assert any("白描" in o["role"] for o in order)

    def test_photography_loaded(self):
        order = get_tradition_layer_order("photography")
        assert len(order) >= 3
        assert order[0]["content_type"] == "background"

    def test_unknown_tradition_fallback(self):
        order = get_tradition_layer_order("totally_unknown_tradition_xyz")
        assert len(order) >= 2
        assert order[0]["content_type"] == "background"
