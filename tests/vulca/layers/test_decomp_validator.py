import numpy as np
import pytest
from vulca.layers.decomp_validator import (
    validate_decomposition,
    DecompositionValidationError,
)


def _binary(mask: np.ndarray) -> np.ndarray:
    """Helper: convert bool mask to uint8 0/255."""
    return (mask.astype(np.uint8)) * 255


def test_validator_passes_for_perfect_partition():
    a = np.zeros((4, 4), dtype=bool)
    a[:, :2] = True
    b = np.zeros((4, 4), dtype=bool)
    b[:, 2:] = True
    report = validate_decomposition([_binary(a), _binary(b)])
    assert report.coverage == 1.0
    assert report.overlap == 0.0
    assert report.holes == 0
    assert report.overlaps == 0


def test_validator_fails_on_hole():
    a = np.zeros((4, 4), dtype=bool)
    a[:, :2] = True
    b = np.zeros((4, 4), dtype=bool)
    b[:, 2:] = True
    b[0, 2] = False
    with pytest.raises(DecompositionValidationError) as exc:
        validate_decomposition([_binary(a), _binary(b)], strict=True)
    assert "coverage" in str(exc.value).lower()


def test_validator_fails_on_overlap():
    a = np.zeros((4, 4), dtype=bool)
    a[:, :3] = True
    b = np.zeros((4, 4), dtype=bool)
    b[:, 2:] = True
    with pytest.raises(DecompositionValidationError) as exc:
        validate_decomposition([_binary(a), _binary(b)], strict=True)
    assert "overlap" in str(exc.value).lower()


def test_validator_non_strict_returns_report_without_raising():
    a = np.zeros((4, 4), dtype=bool)
    a[:, :2] = True
    b = np.zeros((4, 4), dtype=bool)
    report = validate_decomposition([_binary(a), _binary(b)], strict=False)
    assert report.coverage == pytest.approx(0.5)
    assert report.holes == 8


def test_validator_tolerates_small_coverage_epsilon():
    a = np.ones((100, 100), dtype=bool)
    a[0, 0] = False
    report = validate_decomposition([_binary(a)], strict=True, epsilon=1e-3)
    assert report.coverage < 1.0


def test_validator_rejects_3d_mask():
    """3D masks include a channel axis and would silently miscount
    coverage. Reject them at the input contract."""
    m = np.zeros((4, 4, 3), dtype=np.uint8)
    with pytest.raises(ValueError, match="ndim|2D|shape"):
        validate_decomposition([m])


def test_validator_rejects_float_mask():
    """Float masks would be silently compared via >127, collapsing the
    common 0-1 SAM-style probability range to all-zero. Reject them."""
    m = np.ones((4, 4), dtype=np.float32)
    with pytest.raises(ValueError, match="dtype|uint8|bool"):
        validate_decomposition([m])
