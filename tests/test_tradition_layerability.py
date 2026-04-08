"""Tests for tradition layerability config (Tasks 7-9)."""
import yaml
from pathlib import Path

from vulca.cultural.loader import get_tradition, reload_traditions


def _xieyi_yaml_path() -> Path:
    return Path(__file__).resolve().parents[1] / "src" / "vulca" / "cultural" / "data" / "traditions" / "chinese_xieyi.yaml"


def test_xieyi_yaml_has_layerability_fields_raw():
    """Regression guard from Task 7: raw YAML still contains the 5 fields."""
    data = yaml.safe_load(_xieyi_yaml_path().read_text(encoding="utf-8"))
    assert data.get("layerability") == "native"
    assert data.get("canvas_color") == "#ffffff"
    assert data.get("key_strategy") == "luminance"
    assert "宣纸" in (data.get("canvas_description") or "")
    assert "水墨" in (data.get("style_keywords") or "")


def test_xieyi_loader_exposes_layerability_native():
    reload_traditions()
    t = get_tradition("chinese_xieyi")
    assert t is not None
    assert t.layerability == "native"
    assert t.canvas_color == "#ffffff"
    assert t.key_strategy == "luminance"
    assert "宣纸" in t.canvas_description
    assert "水墨" in t.style_keywords


def test_tradition_without_layerability_fields_uses_defaults():
    """Traditions not yet migrated (all except xieyi) default to safe fallbacks."""
    reload_traditions()
    t = get_tradition("default")  # 'default' tradition doesn't have the new fields yet
    if t is None:
        # 'default' may not be in loaded traditions; pick any other unmigrated one
        from vulca.cultural.loader import get_all_traditions
        for name, cfg in get_all_traditions().items():
            if name != "chinese_xieyi":
                t = cfg
                break
    assert t is not None
    assert t.layerability == "split"               # default
    assert t.canvas_color == "#ffffff"             # default
    assert t.canvas_description == ""              # default
    assert t.key_strategy == "luminance"           # default
    assert t.style_keywords == ""                  # default
