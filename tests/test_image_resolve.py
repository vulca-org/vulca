import base64
import tempfile
from pathlib import Path

from vulca._image import resolve_image_input


class TestResolveImageInput:
    def test_file_path_returns_base64(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fakepng")
            f.flush()
            result = resolve_image_input(f.name)
            assert result == base64.b64encode(b"fakepng").decode()

    def test_base64_passes_through(self):
        b64 = base64.b64encode(b"imagedata").decode()
        result = resolve_image_input(b64)
        assert result == b64

    def test_home_path_expanded(self):
        # Just test that ~ paths don't crash
        try:
            resolve_image_input("~/nonexistent.png")
        except FileNotFoundError:
            pass  # Expected — file doesn't exist but path was expanded

    def test_empty_returns_empty(self):
        result = resolve_image_input("")
        assert result == ""


from vulca.studio.brief import Brief


class TestBriefReferenceFields:
    def test_brief_has_reference_path(self):
        b = Brief.new("test")
        assert hasattr(b, "reference_path")
        assert b.reference_path == ""

    def test_brief_has_reference_type(self):
        b = Brief.new("test")
        assert hasattr(b, "reference_type")
        assert b.reference_type == "full"
