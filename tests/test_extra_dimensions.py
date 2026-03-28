import yaml
from pathlib import Path

TRADITIONS_DIR = Path(__file__).resolve().parent.parent / "src" / "vulca" / "cultural" / "data" / "traditions"


class TestExtraDimensionsYAML:
    def test_brand_design_has_extras(self):
        data = yaml.safe_load((TRADITIONS_DIR / "brand_design.yaml").read_text())
        assert "extra_dimensions" in data
        assert len(data["extra_dimensions"]) <= 3
        assert data["extra_dimensions"][0]["key"] == "E1"

    def test_ui_ux_design_has_extras(self):
        data = yaml.safe_load((TRADITIONS_DIR / "ui_ux_design.yaml").read_text())
        assert "extra_dimensions" in data

    def test_photography_has_extras(self):
        data = yaml.safe_load((TRADITIONS_DIR / "photography.yaml").read_text())
        assert "extra_dimensions" in data

    def test_chinese_xieyi_no_extras(self):
        data = yaml.safe_load((TRADITIONS_DIR / "chinese_xieyi.yaml").read_text())
        assert "extra_dimensions" not in data or data.get("extra_dimensions") is None

    def test_extra_dimension_structure(self):
        data = yaml.safe_load((TRADITIONS_DIR / "brand_design.yaml").read_text())
        e1 = data["extra_dimensions"][0]
        assert "key" in e1
        assert "name" in e1
        assert "description" in e1
