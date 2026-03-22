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

# Detect CI placeholder keys that are not real API keys
_FAKE_KEY_PREFIXES = ("test-", "fake-", "dummy-", "placeholder")


def _is_real_api_key(key: str) -> bool:
    """Return True only if the key looks like a real Gemini/Google API key."""
    if not key:
        return False
    if any(key.lower().startswith(p) for p in _FAKE_KEY_PREFIXES):
        return False
    # Real Gemini keys start with "AIza" and are 39 chars
    if key.startswith("AIza") and len(key) >= 39:
        return True
    # Accept any other non-trivially-short key as potentially real
    return len(key) >= 20


_has_real_key = _is_real_api_key(_gemini_key)

# Note: do NOT set pytestmark = pytest.mark.integration here.
# Only test_real_*.py and test_sdk_real*.py files carry their own
# @pytest.mark.integration marker. Mock-based integration tests
# (test_canvas_pipeline, test_digestion, etc.) must run in CI.


def pytest_collection_modifyitems(config, items):
    """Skip real-API integration tests when no valid GEMINI_API_KEY is available.

    Tests in files named ``test_real_*`` or ``test_sdk_real*`` require a real
    API key and are skipped when only a CI placeholder key is present.
    Other integration tests (mock-based) always run.
    """
    if _has_real_key:
        return
    skip_real = pytest.mark.skip(
        reason="No real GEMINI_API_KEY — skipping real-API integration tests"
    )
    for item in items:
        fspath = str(item.fspath)
        if "integration" not in fspath:
            continue
        # Only skip tests that need real API keys (test_real_*, test_sdk_real*)
        fname = os.path.basename(fspath)
        if fname.startswith("test_real_") or fname.startswith("test_sdk_real"):
            item.add_marker(skip_real)


@pytest.fixture(scope="session")
def gemini_api_key() -> str:
    """Return the real Gemini API key, or skip."""
    if not _has_real_key:
        pytest.skip("No real GEMINI_API_KEY available")
    return _gemini_key
