"""Tests for the extracted _obtain_validation_report helper."""
from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
from PIL import Image

from vulca.layers.layered_generate import (
    _REPORT_SCHEMA_VERSION,
    _obtain_validation_report,
    _report_to_dict,
)
from vulca.layers.validate import ValidationReport, ValidationWarning


def _write_rgba_png(path: Path, w=32, h=32) -> None:
    """Write a simple RGBA PNG to disk for validate_layer_alpha to read."""
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:, :, 3] = 128  # 50% alpha everywhere
    Image.fromarray(arr, mode="RGBA").save(str(path))


class TestSidecarHit:
    """Branch 1: cache hit with valid sidecar — reuse persisted report."""

    def test_returns_cached_report(self, tmp_path: Path):
        out_path = tmp_path / "layer.png"
        _write_rgba_png(out_path)

        report = ValidationReport(
            ok=True, warnings=[], coverage_actual=0.5, position_iou=0.8,
        )
        cached_dict = _report_to_dict(report)

        cache = MagicMock()
        cache.get_report.return_value = cached_dict

        result = _obtain_validation_report(
            cache_hit=True, cache=cache, cache_key="abc",
            out_path=str(out_path), position="", coverage="",
            cache_put_ok=True,
        )
        assert result is not None
        assert result.ok is True
        assert result.coverage_actual == 0.5
        assert result.position_iou == 0.8


class TestSidecarMissMigrate:
    """Branch 2: cache hit, sidecar missing — re-validate and write sidecar."""

    def test_revalidates_and_writes_sidecar(self, tmp_path: Path):
        out_path = tmp_path / "layer.png"
        _write_rgba_png(out_path)

        cache = MagicMock()
        cache.get_report.return_value = None

        result = _obtain_validation_report(
            cache_hit=True, cache=cache, cache_key="abc",
            out_path=str(out_path), position="", coverage="",
            cache_put_ok=True,
        )
        assert result is not None
        assert isinstance(result, ValidationReport)
        cache.put_report.assert_called_once()


class TestFreshValidation:
    """Branch 3: fresh generation — validate from disk, write sidecar."""

    def test_validates_fresh_and_writes_sidecar(self, tmp_path: Path):
        out_path = tmp_path / "layer.png"
        _write_rgba_png(out_path)

        cache = MagicMock()

        result = _obtain_validation_report(
            cache_hit=False, cache=cache, cache_key="abc",
            out_path=str(out_path), position="", coverage="",
            cache_put_ok=True,
        )
        assert result is not None
        assert isinstance(result, ValidationReport)
        cache.put_report.assert_called_once()


class TestOrphanSidecarGuard:
    """v0.13.2 G4 invariant: no sidecar write when cache_put_ok=False."""

    def test_skips_sidecar_write_when_cache_put_failed(self, tmp_path: Path):
        out_path = tmp_path / "layer.png"
        _write_rgba_png(out_path)

        cache = MagicMock()
        cache.get_report.return_value = None

        result = _obtain_validation_report(
            cache_hit=False, cache=cache, cache_key="abc",
            out_path=str(out_path), position="", coverage="",
            cache_put_ok=False,
        )
        assert result is not None
        cache.put_report.assert_not_called()


class TestNoCacheProvided:
    """When cache is None, still returns a valid report (no sidecar ops)."""

    def test_validates_without_cache(self, tmp_path: Path):
        out_path = tmp_path / "layer.png"
        _write_rgba_png(out_path)

        result = _obtain_validation_report(
            cache_hit=False, cache=None, cache_key="",
            out_path=str(out_path), position="", coverage="",
            cache_put_ok=True,
        )
        assert result is not None
        assert isinstance(result, ValidationReport)
