"""E2E mock tests — verify pipeline logic without GPU.

Uses MockImageProvider (solid-color PNGs) to exercise the E2E demo runner.
Tests verify report structure, file output, and pipeline orchestration.
"""
from __future__ import annotations

import asyncio
import io
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))


def _validate_png_bytes_permissive(raw: bytes):
    """Relaxed PNG validator for mock tests — skips the 10 KB size floor.

    MockImageProvider produces valid but highly-compressed solid-color PNGs
    that are always well under 10 KB even at large canvas dimensions.
    """
    from PIL import Image

    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "not a valid PNG"
    assert len(raw) > 0, "empty image"
    img = Image.open(io.BytesIO(raw))
    assert img.width > 0 and img.height > 0, f"invalid dimensions: {img.size}"
    return img.width, img.height


@pytest.fixture
def e2e_dirs(tmp_path, monkeypatch):
    """Patch E2E output directories to use tmp_path and relax PNG size check."""
    from scripts import generate_e2e_demo as mod

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "DEMO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "GALLERY_DIR", tmp_path / "gallery")
    monkeypatch.setattr(mod, "TOOLS_DIR", tmp_path / "tools")
    monkeypatch.setattr(mod, "EVAL_DIR", tmp_path / "eval")
    monkeypatch.setattr(mod, "REPORT_PATH", tmp_path / "e2e-report.json")
    monkeypatch.setattr(mod, "LAYERED_DIR", tmp_path / "layered")
    monkeypatch.setattr(mod, "DEFENSE3_DIR", tmp_path / "defense3")
    monkeypatch.setattr(mod, "EDIT_DIR", tmp_path / "edit")
    monkeypatch.setattr(mod, "INPAINT_DIR", tmp_path / "inpaint")
    monkeypatch.setattr(mod, "STUDIO_DIR", tmp_path / "studio")
    # Relax PNG size validator — mock images are valid but tiny (solid color).
    monkeypatch.setattr(mod, "_validate_png_bytes", _validate_png_bytes_permissive)
    return tmp_path


@pytest.fixture
def gallery_image(e2e_dirs):
    """Create a synthetic gallery PNG for phases that depend on Phase 1 output."""
    from PIL import Image

    gallery_dir = e2e_dirs / "gallery"
    gallery_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1024, 1024), (200, 180, 160))
    path = gallery_dir / "chinese_xieyi.png"
    img.save(path, format="PNG")
    return path


def test_phase1_gallery_mock(e2e_dirs):
    """Phase 1: gallery generation produces reports with expected structure."""
    from scripts.generate_e2e_demo import run_phase1_gallery

    rep = asyncio.run(run_phase1_gallery(
        "mock", width=64, height=64, traditions={"chinese_xieyi"},
    ))

    assert rep["phase"] == 1
    assert rep["name"] == "gallery"
    assert rep["status"] in ("ok", "partial")
    assert len(rep["entries"]) >= 1
    entry = rep["entries"][0]
    assert "tradition" in entry
    assert "status" in entry
    # Verify file was written
    gallery_dir = e2e_dirs / "gallery"
    assert any(gallery_dir.glob("*.png"))


def test_phase8_tools_mock(e2e_dirs, gallery_image):
    """Phase 8: tools analysis produces expected JSON outputs."""
    # Skip if cv2 is unavailable — pre-existing baseline gap (~61 failures)
    pytest.importorskip("cv2")

    from scripts.generate_e2e_demo import run_phase8_tools

    rep = run_phase8_tools(gallery_image, "chinese_xieyi")

    assert rep["phase"] == 8
    assert rep["name"] == "tools"
    assert rep["status"] == "ok"
    assert "brushstroke" in rep
    assert "composition" in rep
    assert 0.0 <= rep["brushstroke"]["texture_energy"] <= 1.0
    assert 0.0 <= rep["composition"]["center_weight"] <= 1.0
    # Verify JSON files written
    tools_dir = e2e_dirs / "tools"
    assert (tools_dir / "brushstroke.json").exists()
    assert (tools_dir / "composition.json").exists()
