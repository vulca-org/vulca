import yaml
from pathlib import Path

def test_xieyi_yaml_has_layerability_fields():
    """Raw YAML file contains the 5 new layerability fields.

    This test reads the YAML directly (bypassing the loader) because
    Task 7 only edits YAML; Task 8 will wire the loader to expose them.
    """
    path = Path(__file__).resolve().parents[1] / "src" / "vulca" / "cultural" / "data" / "traditions" / "chinese_xieyi.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data.get("layerability") == "native"
    assert data.get("canvas_color") == "#ffffff"
    assert data.get("key_strategy") == "luminance"
    assert "宣纸" in (data.get("canvas_description") or "")
    assert "水墨" in (data.get("style_keywords") or "")
