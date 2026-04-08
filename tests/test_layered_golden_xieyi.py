"""Golden test for A-path on chinese_xieyi — gated behind --run-real-provider.

Run with:
    pytest tests/test_layered_golden_xieyi.py --run-real-provider

The first run populates the baseline JSON (if empty). Subsequent runs compare
16-bin alpha histograms per layer against the baseline within a per-bin
absolute tolerance.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput

BASELINE = Path(__file__).parent / "golden" / "layered_xieyi_alpha_histogram.json"
BINS = 16
TOL = 0.05  # per-bin absolute fraction


def _alpha_histogram(rgba_path: str) -> list[float]:
    img = Image.open(rgba_path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    a = np.array(img)[:, :, 3].astype(np.float32) / 255.0
    hist, _ = np.histogram(a, bins=BINS, range=(0.0, 1.0))
    total = hist.sum()
    return (hist / max(total, 1)).tolist()


@pytest.mark.real_provider
def test_xieyi_golden_alpha_histograms(tmp_path):
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")

    inp = PipelineInput(
        subject="远山薄雾",
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="gemini",
        layered=True,
        output_dir=str(tmp_path),
    )
    asyncio.run(execute(LAYERED, inp))

    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["generation_path"] == "a"

    current: dict[str, list[float]] = {}
    for entry in manifest["layers"]:
        rgba = tmp_path / entry["file"]
        if rgba.exists():
            current[entry["name"]] = _alpha_histogram(str(rgba))

    baseline = json.loads(BASELINE.read_text())
    if not baseline.get("layers"):
        # First run: populate baseline and pass.
        baseline["layers"] = current
        BASELINE.write_text(json.dumps(baseline, indent=2, ensure_ascii=False))
        pytest.skip("Baseline populated — re-run to compare.")

    for name, cur_hist in current.items():
        base_hist = baseline["layers"].get(name)
        if base_hist is None:
            continue
        diffs = [abs(a - b) for a, b in zip(cur_hist, base_hist)]
        assert max(diffs) < TOL, (
            f"layer {name} drifted: max bin diff {max(diffs):.3f} >= {TOL}"
        )
