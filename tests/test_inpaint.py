import pytest
from vulca.types import InpaintResult
from vulca.studio.phases.inpaint import parse_region_coordinates


class TestInpaintResult:
    def test_defaults(self):
        r = InpaintResult(
            bbox={"x": 0, "y": 0, "w": 100, "h": 35},
            variants=[], selected=0, blended="",
            original="img.jpg", instruction="fix sky",
            tradition="default",
        )
        assert r.bbox["h"] == 35
        assert r.cost_usd == 0.0

    def test_latency_default(self):
        r = InpaintResult(
            bbox={}, variants=[], selected=0, blended="",
            original="", instruction="", tradition="",
        )
        assert r.latency_ms == 0


class TestParseRegionCoordinates:
    def test_valid_coordinates(self):
        bbox = parse_region_coordinates("0,0,100,35")
        assert bbox == {"x": 0, "y": 0, "w": 100, "h": 35}

    def test_with_spaces(self):
        bbox = parse_region_coordinates("10, 20, 50, 30")
        assert bbox == {"x": 10, "y": 20, "w": 50, "h": 30}

    def test_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            parse_region_coordinates("0,0,101,35")

    def test_rejects_too_small(self):
        with pytest.raises(ValueError):
            parse_region_coordinates("0,0,4,4")

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            parse_region_coordinates("-1,0,50,50")

    def test_is_coordinate_string(self):
        from vulca.studio.phases.inpaint import is_coordinate_string
        assert is_coordinate_string("0,0,100,35") is True
        assert is_coordinate_string("fix the sky") is False
        assert is_coordinate_string("10, 20, 50, 30") is True
        assert is_coordinate_string("50") is False
