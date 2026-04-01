"""Tests for VulcaTool protocol + ImageData cross-platform type.

Task 1: VulcaTool Protocol + ToolSchema + ToolCategory
Task 2: ImageData — Cross-platform Unified Image Type
"""

from __future__ import annotations

import base64
import io
import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vulca.tools.protocol import (
    ImageData,
    ToolCategory,
    ToolConfig,
    ToolSchema,
    VulcaTool,
    VisualEvidence,
)


# ---------------------------------------------------------------------------
# Task 1: ToolCategory, ToolSchema, VisualEvidence, ToolConfig, VulcaTool
# ---------------------------------------------------------------------------


class TestToolCategory:
    def test_tool_category_values(self):
        """All 8 ToolCategory enum values exist with correct string values."""
        expected = {
            "FILTER": "filter",
            "COMPOSITE": "composite",
            "TRANSFORM": "transform",
            "GENERATOR": "generator",
            "PATTERN": "pattern",
            "CULTURAL_CHECK": "cultural",
            "COMPOSITION": "composition",
            "STYLE_ANALYSIS": "style",
        }
        actual = {m.name: m.value for m in ToolCategory}
        assert actual == expected, f"Mismatch: {actual}"


class TestToolSchema:
    def test_tool_schema_is_pydantic_model(self):
        """ToolSchema subclass creates instances + generates JSON schema."""
        from pydantic import BaseModel

        class MyInput(ToolSchema):
            value: int
            label: str = "default"

        inst = MyInput(value=42)
        assert inst.value == 42
        assert inst.label == "default"

        schema = MyInput.model_json_schema()
        assert "properties" in schema
        assert "value" in schema["properties"]
        assert "label" in schema["properties"]

        assert issubclass(ToolSchema, BaseModel)


class TestVisualEvidence:
    def test_visual_evidence_fields(self):
        """All 4 fields work: annotated_image (bytes), summary, details, confidence."""
        img_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # fake PNG bytes

        ev = VisualEvidence(
            annotated_image=img_bytes,
            summary="Composition is off-center",
            details={"region": "top-left", "severity": "medium"},
            confidence=0.87,
        )

        assert ev.annotated_image == img_bytes
        assert ev.summary == "Composition is off-center"
        assert ev.details["severity"] == "medium"
        assert abs(ev.confidence - 0.87) < 1e-9

    def test_visual_evidence_annotated_image_optional(self):
        """annotated_image is optional (None by default)."""
        ev = VisualEvidence(
            summary="test",
            details={},
            confidence=0.5,
        )
        assert ev.annotated_image is None


class TestToolConfig:
    def test_tool_config_defaults(self):
        """Default mode='check', empty params/thresholds, None force_verdict."""
        cfg = ToolConfig()
        assert cfg.mode == "check"
        assert cfg.params == {}
        assert cfg.thresholds == {}
        assert cfg.force_verdict is None

    def test_tool_config_custom(self):
        """Custom ToolConfig values propagate correctly."""
        cfg = ToolConfig(
            mode="fix",
            params={"k": 3},
            thresholds={"min": 0.6},
            force_verdict="pass",
        )
        assert cfg.mode == "fix"
        assert cfg.params["k"] == 3
        assert cfg.thresholds["min"] == 0.6
        assert cfg.force_verdict == "pass"


class TestVulcaTool:
    def test_vulca_tool_cannot_instantiate_abstract(self):
        """Raises TypeError when trying to instantiate VulcaTool directly."""
        with pytest.raises(TypeError):
            VulcaTool()  # type: ignore[abstract]

    def test_concrete_tool_can_be_instantiated(self):
        """A fully-defined concrete subclass can be instantiated."""

        class EchoTool(VulcaTool):
            name = "echo"
            display_name = "Echo Tool"
            description = "Echoes input"
            category = ToolCategory.FILTER
            max_seconds = 5.0
            replaces: dict[str, list[str]] = {}

            class Input(ToolSchema):
                text: str

            class Output(ToolSchema):
                echoed: str

            def execute(self, input_data: "EchoTool.Input", config: ToolConfig) -> "EchoTool.Output":
                return self.Output(echoed=input_data.text)

        tool = EchoTool()
        assert tool.name == "echo"
        assert tool.category == ToolCategory.FILTER

    def test_safe_execute_validates_and_runs(self):
        """safe_execute wraps execute with validation and returns Output."""

        class PlusTool(VulcaTool):
            name = "plus"
            display_name = "Plus Tool"
            description = "Adds two numbers"
            category = ToolCategory.FILTER
            max_seconds = 1.0
            replaces: dict[str, list[str]] = {}

            class Input(ToolSchema):
                a: float
                b: float

            class Output(ToolSchema):
                result: float

            def execute(self, input_data: "PlusTool.Input", config: ToolConfig) -> "PlusTool.Output":
                return self.Output(result=input_data.a + input_data.b)

        tool = PlusTool()
        inp = PlusTool.Input(a=3.0, b=4.5)
        out = tool.safe_execute(inp)  # config optional
        assert isinstance(out, PlusTool.Output)
        assert abs(out.result - 7.5) < 1e-9

    def test_tool_class_attributes_present(self):
        """VulcaTool subclass exposes all required class attributes."""

        class MinimalTool(VulcaTool):
            name = "minimal"
            display_name = "Minimal"
            description = "Does nothing"
            category = ToolCategory.FILTER
            max_seconds = 2.0
            replaces: dict[str, list[str]] = {"evaluate": ["L1"]}

            class Input(ToolSchema):
                pass

            class Output(ToolSchema):
                pass

            def execute(self, input_data, config):
                return self.Output()

        assert MinimalTool.name == "minimal"
        assert MinimalTool.display_name == "Minimal"
        assert MinimalTool.description == "Does nothing"
        assert MinimalTool.category == ToolCategory.FILTER
        assert MinimalTool.max_seconds == 2.0
        assert MinimalTool.replaces == {"evaluate": ["L1"]}

    def test_vulca_tool_has_concurrency_attributes(self):
        """VulcaTool ABC has fail-closed defaults: is_concurrent_safe=False, is_read_only=True."""
        assert hasattr(VulcaTool, "is_concurrent_safe"), "VulcaTool must have is_concurrent_safe ClassVar"
        assert hasattr(VulcaTool, "is_read_only"), "VulcaTool must have is_read_only ClassVar"
        assert VulcaTool.is_concurrent_safe is False, "Default is_concurrent_safe must be False (fail-closed)"
        assert VulcaTool.is_read_only is True, "Default is_read_only must be True"

    def test_analysis_tools_are_concurrent_safe(self):
        """4 analysis tools are safe for concurrent use and read-only."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

        from vulca.tools.cultural.whitespace import WhitespaceAnalyzer
        from vulca.tools.cultural.brushstroke import BrushstrokeAnalyzer
        from vulca.tools.cultural.color_gamut import ColorGamutChecker
        from vulca.tools.cultural.composition import CompositionAnalyzer

        for tool_cls in (WhitespaceAnalyzer, BrushstrokeAnalyzer, ColorGamutChecker, CompositionAnalyzer):
            assert tool_cls.is_concurrent_safe is True, (
                f"{tool_cls.__name__}.is_concurrent_safe must be True (pure analysis, no side effects)"
            )
            assert tool_cls.is_read_only is True, (
                f"{tool_cls.__name__}.is_read_only must be True (analysis only)"
            )

    def test_color_correct_is_not_concurrent_safe(self):
        """ColorCorrect mutates pixel data: is_concurrent_safe=False, is_read_only=False."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

        from vulca.tools.filters.color_correct import ColorCorrect

        assert ColorCorrect.is_concurrent_safe is False, (
            "ColorCorrect.is_concurrent_safe must be False (fix mode mutates image data)"
        )
        assert ColorCorrect.is_read_only is False, (
            "ColorCorrect.is_read_only must be False (fix mode writes corrected image)"
        )


# ---------------------------------------------------------------------------
# Task 2: ImageData cross-platform type
# ---------------------------------------------------------------------------


def _make_test_png_bytes(w: int = 4, h: int = 4) -> bytes:
    """Return valid PNG bytes for a small solid-color image."""
    img = Image.new("RGB", (w, h), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_test_ndarray(w: int = 4, h: int = 4) -> np.ndarray:
    """Return (H, W, C) uint8 RGB ndarray."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, 0] = 100
    arr[:, :, 1] = 150
    arr[:, :, 2] = 200
    return arr


class TestImageData:
    def test_image_data_from_bytes(self):
        """Create from PNG bytes, roundtrip to numpy."""
        png = _make_test_png_bytes(4, 4)
        img = ImageData.from_bytes(png)

        # roundtrip to numpy
        arr = img.to_numpy()
        assert arr.shape == (4, 4, 3)
        assert arr.dtype == np.uint8
        # Check colour values (PNG lossless)
        assert int(arr[0, 0, 0]) == 100
        assert int(arr[0, 0, 1]) == 150
        assert int(arr[0, 0, 2]) == 200

    def test_image_data_from_numpy(self):
        """Create from ndarray, roundtrip to bytes and back."""
        arr = _make_test_ndarray(4, 4)
        img = ImageData.from_numpy(arr)

        # to_bytes returns PNG bytes
        raw = img.to_bytes()
        assert isinstance(raw, bytes)
        assert raw[:4] == b"\x89PNG"

        # roundtrip back to numpy preserves shape + values
        arr2 = img.to_numpy()
        assert arr2.shape == (4, 4, 3)
        np.testing.assert_array_equal(arr, arr2)

    def test_image_data_from_base64(self):
        """Decode base64 string, verify numpy shape, roundtrip."""
        png = _make_test_png_bytes(8, 6)
        b64 = base64.b64encode(png).decode()

        img = ImageData.from_base64(b64)
        arr = img.to_numpy()
        assert arr.shape == (6, 8, 3)  # (H, W, C)

        # roundtrip base64
        b64_out = img.to_base64()
        assert isinstance(b64_out, str)
        # decode and re-verify
        arr2 = ImageData.from_base64(b64_out).to_numpy()
        np.testing.assert_array_equal(arr, arr2)

    def test_image_data_from_path(self, tmp_path):
        """Save PIL image to tmp_path, load via from_path."""
        p = tmp_path / "test.png"
        pil_img = Image.new("RGB", (5, 3), color=(10, 20, 30))
        pil_img.save(str(p))

        img = ImageData.from_path(str(p))
        arr = img.to_numpy()
        assert arr.shape == (3, 5, 3)  # (H=3, W=5, C=3)
        assert int(arr[0, 0, 0]) == 10
        assert int(arr[0, 0, 1]) == 20
        assert int(arr[0, 0, 2]) == 30

    def test_image_data_save(self, tmp_path):
        """from_numpy, save to path, read back and verify."""
        arr = _make_test_ndarray(6, 6)
        img = ImageData.from_numpy(arr)

        out_path = tmp_path / "saved.png"
        img.save(str(out_path))
        assert out_path.exists()

        loaded = ImageData.from_path(str(out_path))
        arr2 = loaded.to_numpy()
        np.testing.assert_array_equal(arr, arr2)

    def test_image_data_to_pil(self):
        """to_pil returns a PIL Image with correct mode and size."""
        arr = _make_test_ndarray(8, 5)  # H=5, W=8
        img = ImageData.from_numpy(arr)

        pil = img.to_pil()
        assert isinstance(pil, Image.Image)
        assert pil.mode == "RGB"
        assert pil.size == (8, 5)  # PIL size = (W, H)

    def test_image_data_from_pil(self):
        """from_pil accepts PIL Image and roundtrips."""
        pil = Image.new("RGB", (7, 3), color=(55, 66, 77))
        img = ImageData.from_pil(pil)

        arr = img.to_numpy()
        assert arr.shape == (3, 7, 3)
        assert int(arr[0, 0, 0]) == 55
        assert int(arr[0, 0, 1]) == 66
        assert int(arr[0, 0, 2]) == 77
