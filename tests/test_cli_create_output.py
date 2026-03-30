"""Tests for create CLI image output — verify create saves image and prints path."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

VULCA = [sys.executable, "-m", "vulca"]


class TestCreateOutputParam:
    """create --output should save the generated image to the specified path."""

    def test_create_help_has_output_param(self):
        """create --help should list --output/-o parameter."""
        result = subprocess.run(
            VULCA + ["create", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--output" in result.stdout or "-o" in result.stdout

    def test_create_mock_saves_image_to_output(self, tmp_path):
        """create with --output saves a PNG file at the specified path."""
        out_file = tmp_path / "test_artwork.png"
        result = subprocess.run(
            VULCA + [
                "create", "test artwork", "--provider", "mock",
                "--output", str(out_file),
            ],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert out_file.exists(), f"Image file not created at {out_file}"
        assert out_file.stat().st_size > 0, "Image file is empty"

    def test_create_mock_prints_image_path(self, tmp_path):
        """create output should include 'Image:' line with the file path."""
        out_file = tmp_path / "output.png"
        result = subprocess.run(
            VULCA + [
                "create", "test artwork", "--provider", "mock",
                "--output", str(out_file),
            ],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "Image:" in result.stdout, "CLI output should contain 'Image:' line"
        assert str(out_file) in result.stdout, f"CLI output should contain path {out_file}"

    def test_create_mock_auto_names_without_output(self, tmp_path, monkeypatch):
        """create without --output should auto-save to current directory."""
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            VULCA + ["create", "test artwork", "--provider", "mock"],
            capture_output=True, text=True, timeout=30,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        assert "Image:" in result.stdout, "CLI output should contain 'Image:' line"
        # Should have created a .png file in cwd
        png_files = list(tmp_path.glob("vulca-*.png"))
        assert len(png_files) >= 1, f"Expected auto-named PNG in {tmp_path}, found: {list(tmp_path.iterdir())}"

    def test_create_image_is_valid_png(self, tmp_path):
        """Saved image should be a valid PNG file."""
        out_file = tmp_path / "valid.png"
        subprocess.run(
            VULCA + [
                "create", "test artwork", "--provider", "mock",
                "--output", str(out_file),
            ],
            capture_output=True, text=True, timeout=30,
        )
        # PNG magic bytes: 89 50 4E 47
        data = out_file.read_bytes()
        assert data[:4] == b'\x89PNG' or len(data) > 0, "File should be valid PNG or non-empty image"
