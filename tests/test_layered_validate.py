import numpy as np
import pytest
from vulca.layers.validate import (
    validate_layer_alpha, ValidationReport, parse_coverage, parse_position,
)

def _alpha_in_region(h, w, top_pct, bottom_pct, left_pct=0.0, right_pct=1.0):
    a = np.zeros((h, w), dtype=np.float32)
    t, b = int(h * top_pct), int(h * bottom_pct)
    l, r = int(w * left_pct), int(w * right_pct)
    a[t:b, l:r] = 0.9
    return a

def test_parse_coverage_range():
    assert parse_coverage("20-30%") == (0.20, 0.30)
    assert parse_coverage("5-10%") == (0.05, 0.10)
    assert parse_coverage("100%") == (1.0, 1.0)

def test_parse_position_upper_30():
    region = parse_position("upper 30%")
    assert region["top"] == 0.0 and region["bottom"] == 0.30

def test_parse_position_lower_30():
    region = parse_position("lower 30%")
    assert region["top"] == 0.70 and region["bottom"] == 1.0

def test_empty_layer_is_failure():
    alpha = np.zeros((100, 100), dtype=np.float32)
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert not rep.ok
    assert "empty_layer" in [w.kind for w in rep.warnings]

def test_coverage_in_range_no_warning():
    alpha = _alpha_in_region(100, 100, 0.0, 0.25)
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert rep.ok
    assert "coverage_drift" not in [w.kind for w in rep.warnings]

def test_coverage_too_large_warns():
    alpha = _alpha_in_region(100, 100, 0.0, 0.80)
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert "coverage_drift" in [w.kind for w in rep.warnings]

def test_position_drift_warns():
    alpha = _alpha_in_region(100, 100, 0.70, 1.0)
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert "position_drift" in [w.kind for w in rep.warnings]
