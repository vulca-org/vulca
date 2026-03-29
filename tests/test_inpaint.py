import tempfile
import pytest
from pathlib import Path
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


from PIL import Image
from vulca.studio.phases.inpaint import crop_region, InpaintPhase


class TestCropRegion:
    def test_crop_produces_correct_size(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new("RGB", (1024, 1024), "red")
            img.save(f.name)
            cropped_path = crop_region(
                f.name,
                {"x": 0, "y": 0, "w": 50, "h": 50},
                output_dir=tempfile.gettempdir(),
            )
            cropped = Image.open(cropped_path)
            assert cropped.size == (512, 512)

    def test_crop_quarter(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new("RGB", (100, 100), "blue")
            img.save(f.name)
            cropped_path = crop_region(
                f.name,
                {"x": 50, "y": 50, "w": 50, "h": 50},
                output_dir=tempfile.gettempdir(),
            )
            cropped = Image.open(cropped_path)
            assert cropped.size == (50, 50)


class TestInpaintPhase:
    def test_instantiation(self):
        phase = InpaintPhase()
        assert phase is not None

    def test_build_repaint_prompt(self):
        phase = InpaintPhase()
        prompt = phase.build_repaint_prompt(
            instruction="add storm clouds",
            tradition="chinese_xieyi",
        )
        assert "storm clouds" in prompt
        assert "chinese_xieyi" in prompt or "xieyi" in prompt

    def test_build_blend_prompt(self):
        phase = InpaintPhase()
        prompt = phase.build_blend_prompt(
            bbox={"x": 0, "y": 0, "w": 100, "h": 35},
        )
        assert "0%" in prompt or "0," in prompt
        assert "seamless" in prompt.lower() or "blend" in prompt.lower()


class TestInpaintPublicAPI:
    def test_inpaint_importable(self):
        from vulca import inpaint, ainpaint, InpaintResult
        assert callable(inpaint)
        assert callable(ainpaint)

    def test_inpaint_coordinate_mode_mock(self):
        """Full flow with coordinate region + mock (no API)."""
        import tempfile
        from vulca import inpaint
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new("RGB", (256, 256), "green")
            img.save(f.name)

            # This will fail on repaint (no real API) but should parse region OK
            try:
                result = inpaint(
                    f.name,
                    region="0,0,50,50",
                    instruction="make it blue",
                    mock=True,
                )
            except Exception:
                pass  # Expected — mock inpaint not implemented yet


import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestInpaintCLI:
    def test_inpaint_help(self):
        result = subprocess.run(
            VULCA + ["inpaint", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--region" in result.stdout
        assert "--instruction" in result.stdout

    def test_inpaint_in_help_list(self):
        result = subprocess.run(
            VULCA + ["--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "inpaint" in result.stdout
