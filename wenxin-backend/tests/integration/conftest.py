"""Integration test fixtures — load .env, skip if no real API key."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Load .env from wenxin-backend/ root (two levels up from this file)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


def _load_dotenv() -> None:
    """Minimal .env loader — no dependency on python-dotenv."""
    if not _ENV_FILE.exists():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        os.environ.setdefault(key, value)


_load_dotenv()

_gemini_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

# Auto-skip all tests in this directory if no real key
pytestmark = pytest.mark.integration


def pytest_collection_modifyitems(config, items):
    """Skip integration tests when no GEMINI_API_KEY is available."""
    if _gemini_key:
        return
    skip = pytest.mark.skip(reason="No GEMINI_API_KEY — skipping integration tests")
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def gemini_api_key() -> str:
    """Return the real Gemini API key, or skip."""
    if not _gemini_key:
        pytest.skip("No GEMINI_API_KEY available")
    return _gemini_key
