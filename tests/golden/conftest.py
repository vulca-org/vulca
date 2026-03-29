"""Golden Set regression test configuration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

BASELINE_PATH = Path(__file__).parent / "golden_baseline.json"


def pytest_addoption(parser):
    parser.addoption(
        "--run-golden",
        action="store_true",
        default=False,
        help="Run real VLM golden regression tests (requires GEMINI_API_KEY)",
    )
    parser.addoption(
        "--update-baseline",
        action="store_true",
        default=False,
        help="Update VLM golden baseline instead of asserting",
    )


@pytest.fixture
def golden_baseline() -> dict:
    """Load the stored VLM golden baseline."""
    if BASELINE_PATH.exists():
        return json.loads(BASELINE_PATH.read_text())
    return {}


@pytest.fixture
def update_baseline(request) -> bool:
    return request.config.getoption("--update-baseline")
