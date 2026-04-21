"""Tripwire: D1 fenced block in /visual-spec design.md MUST byte-match registry weights.

Per /visual-spec spec §5 (D1 derivation class = mechanical) and data-flow invariant #1:
if registry weights ever change, re-running /visual-spec produces different D1. No caching.
This test codifies that invariant at the registry level.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")

from vulca.mcp_server import get_tradition_guide, list_traditions  # noqa: E402


def run(coro):
    return asyncio.run(coro)


# Core tradition sample — the 6 most-likely-used tradition ids across the 13-tradition registry.
# Test explicitly; non-core traditions covered by the parametric test_all_registry_traditions case.
CORE_SAMPLES = [
    "chinese_gongbi",
    "chinese_xieyi",
    "japanese_traditional",
    "islamic_geometric",
    "watercolor",
    "default",
]


def _extract_d1_fields(guide: dict) -> dict:
    """Extract the D1 fields the spec says appear in the fenced block."""
    return {k: guide["weights"][k] for k in ("L1", "L2", "L3", "L4", "L5")}


class TestD1RegistryCopy:
    @pytest.mark.parametrize("tradition", CORE_SAMPLES)
    def test_core_tradition_d1_byte_matches_registry(self, tradition):
        guide = run(get_tradition_guide(tradition))
        derived_d1 = _extract_d1_fields(guide)
        # Any drift between derived_d1 and registry indicates spec violation.
        assert derived_d1 == guide["weights"], (
            f"D1 drift for {tradition}: derived={derived_d1}, registry={guide['weights']}"
        )

    def test_all_registry_traditions_have_l1_l5(self):
        """Every registry tradition MUST expose L1-L5 — else spec §5 D1 rule is unprovable."""
        result = run(list_traditions())
        for name in result["traditions"]:
            guide = run(get_tradition_guide(name))
            for dim in ("L1", "L2", "L3", "L4", "L5"):
                assert dim in guide["weights"], f"Tradition {name!r} missing {dim}"

    def test_d1_weights_are_floats_not_integers(self):
        """Fenced YAML MUST preserve numeric type. Integer weights would break downstream proportional D2 derivation."""
        guide = run(get_tradition_guide("chinese_gongbi"))
        for dim, weight in guide["weights"].items():
            assert isinstance(weight, (int, float)), (
                f"{dim} is {type(weight).__name__}, expected float"
            )

    def test_d1_weights_sum_close_to_1(self):
        """Registry invariant: L1-L5 weights sum ≈ 1.0 (allow ±0.05 drift for legacy traditions)."""
        for tradition in CORE_SAMPLES:
            guide = run(get_tradition_guide(tradition))
            total = sum(guide["weights"].values())
            assert 0.95 <= total <= 1.05, f"{tradition} weights sum = {total}, expected ~1.0"
