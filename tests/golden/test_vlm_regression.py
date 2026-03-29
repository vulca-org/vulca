# vulca/tests/golden/test_vlm_regression.py
"""L2 Golden Set: Real VLM regression for representative traditions.

NOT run in CI. Triggered manually:
    pytest tests/golden/test_vlm_regression.py --run-golden

Update baseline:
    pytest tests/golden/test_vlm_regression.py --update-baseline

Requires GEMINI_API_KEY environment variable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import vulca

BASELINE_PATH = Path(__file__).parent / "golden_baseline.json"

# 3 representative traditions covering East Asian / Western / Non-Western-Non-Asian
VLM_TRADITIONS = ["chinese_xieyi", "western_academic", "islamic_geometric"]

# Tolerance: VLM outputs are non-deterministic, allow +-0.15 per dimension
DIM_TOLERANCE = 0.15
TOTAL_TOLERANCE = 0.10


def _needs_golden(config):
    """Check if --run-golden or --update-baseline was passed."""
    return config.getoption("--run-golden") or config.getoption("--update-baseline")


def _has_api_key():
    return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))


def _generate_test_image() -> str:
    """Generate a minimal 64x64 test PNG as base64. No external files needed."""
    import base64
    import struct
    import zlib

    width, height = 64, 64
    # Simple gradient: each row is a different shade of gray
    raw = b""
    for y in range(height):
        raw += b"\x00"  # filter byte
        gray = int(255 * y / height)
        raw += bytes([gray, gray, gray]) * width

    def _chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw))
    png += _chunk(b"IEND", b"")
    return base64.b64encode(png).decode()


@pytest.fixture(scope="module")
def test_image_b64() -> str:
    return _generate_test_image()


@pytest.fixture(scope="module")
def baseline() -> dict:
    if BASELINE_PATH.exists():
        data = json.loads(BASELINE_PATH.read_text())
        if data:
            return data
    return {}


class TestVLMRegression:
    """Real VLM golden set regression — manual trigger only."""

    @pytest.mark.parametrize("tradition", VLM_TRADITIONS)
    def test_vlm_scores_in_range(self, tradition, test_image_b64, baseline, update_baseline, request):
        if not _needs_golden(request.config):
            pytest.skip("Use --run-golden to run VLM regression tests")
        if not _has_api_key():
            pytest.skip("GEMINI_API_KEY not set")

        result = vulca.evaluate(test_image_b64, tradition=tradition)

        if update_baseline:
            # Store current scores as new baseline
            baseline[tradition] = {
                "L1": result.L1,
                "L2": result.L2,
                "L3": result.L3,
                "L4": result.L4,
                "L5": result.L5,
                "score": result.score,
            }
            BASELINE_PATH.write_text(json.dumps(baseline, indent=2) + "\n")
            pytest.skip(f"Baseline updated for {tradition}")
            return

        if tradition not in baseline:
            pytest.skip(f"No baseline for {tradition} — run with --update-baseline first")

        expected = baseline[tradition]
        for dim in ["L1", "L2", "L3", "L4", "L5"]:
            actual = result.dimensions[dim]
            base = expected[dim]
            assert abs(actual - base) <= DIM_TOLERANCE, (
                f"{tradition} {dim}: {actual:.3f} vs baseline {base:.3f} "
                f"(delta={abs(actual - base):.3f}, tolerance={DIM_TOLERANCE})"
            )

        assert abs(result.score - expected["score"]) <= TOTAL_TOLERANCE, (
            f"{tradition} total: {result.score:.3f} vs baseline {expected['score']:.3f} "
            f"(delta={abs(result.score - expected['score']):.3f}, tolerance={TOTAL_TOLERANCE})"
        )

    @pytest.mark.parametrize("tradition", VLM_TRADITIONS)
    def test_vlm_rationales_substantive(self, tradition, test_image_b64, request):
        if not _needs_golden(request.config):
            pytest.skip("Use --run-golden to run VLM regression tests")
        if not _has_api_key():
            pytest.skip("GEMINI_API_KEY not set")

        result = vulca.evaluate(test_image_b64, tradition=tradition)
        for dim in ["L1", "L2", "L3", "L4", "L5"]:
            rationale = result.rationales.get(dim, "")
            assert len(rationale) >= 10, (
                f"{tradition} {dim} rationale too short ({len(rationale)} chars): {rationale!r}"
            )

    @pytest.mark.parametrize("tradition", VLM_TRADITIONS)
    def test_vlm_suggestions_present(self, tradition, test_image_b64, request):
        if not _needs_golden(request.config):
            pytest.skip("Use --run-golden to run VLM regression tests")
        if not _has_api_key():
            pytest.skip("GEMINI_API_KEY not set")

        result = vulca.evaluate(test_image_b64, tradition=tradition)
        for dim in ["L1", "L2", "L3", "L4", "L5"]:
            suggestion = result.suggestions.get(dim, "")
            assert len(suggestion) > 0, f"{tradition} {dim} suggestion is empty"
