"""Tripwire: per-dim source-tag allowability + confidence enum.

Spec §6.3 defines which source values are valid per dim. This test asserts only allowed tags appear.
"""

from __future__ import annotations

import re

import pytest

# Allowed source tags per spec §6.2 + §6.3
ALLOWED_SOURCES = {"measured", "derived", "assumed"}
ALLOWED_CONFIDENCES = {"low", "med", "high"}

# Per-dim allowed source sets per spec §6.3 rules
DIM_ALLOWED_SOURCES = {
    "A": {"derived", "assumed"},
    "B": {"derived", "assumed"},
    "C": {"derived", "assumed"},
    "D1": set(),  # D1 has no source field (registry-authority)
    "D2": {"assumed", "measured"},  # measured only if spike ran; assumed default
    "E": {"measured"},  # spike actual output
    "F": {"measured", "derived", "assumed"},
}


def _extract_fenced_block(md: str, dim: str) -> str:
    match = re.search(f"## {dim}\\..*?```yaml\\n(.*?)\\n```", md, re.DOTALL)
    assert match, f"Dim {dim} fenced block not found"
    return match.group(1)


def _extract_sources(block: str) -> set:
    return set(re.findall(r"source:\s*(\w+)", block))


def _extract_confidences(block: str) -> set:
    return set(re.findall(r"confidence:\s*(\w+)", block))


# Fixture reused from schema_invariants (copy-paste to keep inline independence)
SAMPLE_MD = """## A. Provider + generation params
```yaml
reviewed: true
provider: sdxl
seed: 1337
steps: 30
cfg_scale: 7.5
```

## D1. L1-L5 weights
```yaml
reviewed: true
L1: 0.3
L2: 0.25
L3: 0.2
L4: 0.15
L5: 0.1
```

## D2. Thresholds + batch + rollback
```yaml
reviewed: true
L1_threshold: {value: 0.7, source: assumed, confidence: low}
L2_threshold: {value: 0.7, source: assumed, confidence: low}
batch_size: {value: 4, source: assumed, confidence: med}
override_rationale: null
```

## F. Cost budget
```yaml
reviewed: true
per_gen_sec: {value: 80, source: measured, confidence: high}
total_session_sec: {value: 480, source: derived, confidence: med}
fail_fast_consecutive: {value: 2, source: assumed, confidence: low}
```
"""


class TestSourceConfidenceMatrix:
    def test_d1_has_no_source_tags(self):
        block = _extract_fenced_block(SAMPLE_MD, "D1")
        assert _extract_sources(block) == set(), "D1 MUST have no source tags per spec §5"

    def test_d2_sources_within_allowed(self):
        block = _extract_fenced_block(SAMPLE_MD, "D2")
        sources = _extract_sources(block)
        illegal = sources - DIM_ALLOWED_SOURCES["D2"]
        assert not illegal, f"D2 has illegal source tags: {illegal}"

    def test_f_sources_within_allowed(self):
        block = _extract_fenced_block(SAMPLE_MD, "F")
        sources = _extract_sources(block)
        illegal = sources - DIM_ALLOWED_SOURCES["F"]
        assert not illegal, f"F has illegal source tags: {illegal}"

    def test_all_confidences_within_enum(self):
        """Every confidence tag in the document MUST be one of {low, med, high}."""
        all_confidences = set(re.findall(r"confidence:\s*(\w+)", SAMPLE_MD))
        illegal = all_confidences - ALLOWED_CONFIDENCES
        assert not illegal, f"Illegal confidence values: {illegal}"

    def test_all_sources_within_global_enum(self):
        """Every source tag MUST be one of {measured, derived, assumed}."""
        all_sources = set(re.findall(r"source:\s*(\w+)", SAMPLE_MD))
        illegal = all_sources - ALLOWED_SOURCES
        assert not illegal, f"Illegal source values: {illegal}"
