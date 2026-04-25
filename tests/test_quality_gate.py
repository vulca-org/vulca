"""Regression tests for v0.17.13 transparency gate (compute_quality_flags).

Background: pre-v0.17.13, the orchestrated decompose pipeline's DINO-object
path silently marked entities as `status: "detected"` even when SAM produced
low-confidence masks. Surfaced 2026-04-25 by γ Scottish iter 0 lanterns:
sam_score 0.609, bbox_fill 0.256 → mask captured building structure not the
lanterns themselves, but manifest reported success_rate 1.0.

Fix: mirror the hint-path quality gate into a pure helper, apply uniformly.
These tests pin the threshold calibration (8 clean γ Scottish entities pass,
lanterns fails) so future refactors can't silently widen or narrow the gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

# scripts/ is not a package; import directly via sys.path injection
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import claude_orchestrated_pipeline as cop  # noqa: E402


def test_lanterns_baseline_triggers_suspect():
    """γ Scottish iter 0 lanterns: sam_score 0.609, bbox_fill 0.256 → suspect.

    The original failure case the gate was designed to catch.
    """
    flags, status = cop.compute_quality_flags(
        pct=8.05, sam_score=0.609, bbox_fill=0.256, inside_ratio=0.913,
    )
    assert status == "suspect"
    assert "low_sam_score" in flags
    assert "low_bbox_fill" in flags
    # inside_ratio 0.913 > 0.60 threshold, so this flag should NOT fire
    assert "mask_outside_bbox" not in flags


def test_clean_entity_person_remains_detected():
    """γ Scottish iter 0 person: sam 1.008, fill 0.584 → detected (no flags)."""
    flags, status = cop.compute_quality_flags(
        pct=5.65, sam_score=1.008, bbox_fill=0.584, inside_ratio=0.978,
    )
    assert status == "detected"
    assert flags == []


def test_clean_entity_bus_remains_detected():
    """γ Scottish iter 0 bus: sam 0.978, fill 0.859 → detected."""
    flags, status = cop.compute_quality_flags(
        pct=3.59, sam_score=0.978, bbox_fill=0.859, inside_ratio=0.975,
    )
    assert status == "detected"
    assert flags == []


def test_clean_entity_sky_remains_detected():
    """γ Scottish iter 0 sky: sam 0.981, fill 0.436 → detected.

    Sky is the closest "clean" entity to the threshold (fill 0.436 vs gate
    0.30) — pins the lower bound of healthy bbox_fill values for diffuse
    background entities.
    """
    flags, status = cop.compute_quality_flags(
        pct=15.5, sam_score=0.981, bbox_fill=0.436, inside_ratio=0.989,
    )
    assert status == "detected"
    assert flags == []


def test_empty_mask_triggers_suspect():
    """Empty mask is the most basic failure — caught regardless of other scores."""
    flags, status = cop.compute_quality_flags(
        pct=0.01, sam_score=0.95, bbox_fill=0.5, inside_ratio=0.9,
    )
    assert status == "suspect"
    assert "empty_mask" in flags


def test_mask_outside_bbox_triggers_suspect():
    """Mask escaping its bbox — SAM picked the wrong neighboring object."""
    flags, status = cop.compute_quality_flags(
        pct=2.0, sam_score=0.85, bbox_fill=0.7, inside_ratio=0.45,
    )
    assert status == "suspect"
    assert "mask_outside_bbox" in flags


def test_all_flags_fire_simultaneously():
    """Catastrophic detection — all four flags trigger together."""
    flags, status = cop.compute_quality_flags(
        pct=0.01, sam_score=0.4, bbox_fill=0.05, inside_ratio=0.2,
    )
    assert status == "suspect"
    assert set(flags) == {"empty_mask", "low_sam_score", "low_bbox_fill", "mask_outside_bbox"}


def test_threshold_calibration_pins_for_v0_17_13():
    """Pin the exact thresholds. Future refactors must update this test
    explicitly if they want to change the gate calibration — preventing
    silent threshold drift that would re-introduce the lanterns bug.
    """
    # sam_score: 0.70 boundary
    flags, _ = cop.compute_quality_flags(pct=5, sam_score=0.6999, bbox_fill=0.5, inside_ratio=0.9)
    assert "low_sam_score" in flags
    flags, _ = cop.compute_quality_flags(pct=5, sam_score=0.70, bbox_fill=0.5, inside_ratio=0.9)
    assert "low_sam_score" not in flags

    # bbox_fill: 0.30 boundary
    flags, _ = cop.compute_quality_flags(pct=5, sam_score=0.9, bbox_fill=0.2999, inside_ratio=0.9)
    assert "low_bbox_fill" in flags
    flags, _ = cop.compute_quality_flags(pct=5, sam_score=0.9, bbox_fill=0.30, inside_ratio=0.9)
    assert "low_bbox_fill" not in flags

    # inside_ratio: 0.60 boundary
    flags, _ = cop.compute_quality_flags(pct=5, sam_score=0.9, bbox_fill=0.5, inside_ratio=0.5999)
    assert "mask_outside_bbox" in flags
    flags, _ = cop.compute_quality_flags(pct=5, sam_score=0.9, bbox_fill=0.5, inside_ratio=0.60)
    assert "mask_outside_bbox" not in flags

    # pct: 0.05 boundary
    flags, _ = cop.compute_quality_flags(pct=0.0499, sam_score=0.9, bbox_fill=0.5, inside_ratio=0.9)
    assert "empty_mask" in flags
    flags, _ = cop.compute_quality_flags(pct=0.05, sam_score=0.9, bbox_fill=0.5, inside_ratio=0.9)
    assert "empty_mask" not in flags
