"""Unified API connection validator for Gemini-based pipeline.

Tests:
1. Gemini 2.5 Flash — litellm.completion("gemini/gemini-2.5-flash")

Usage:
    ./run_prototype.sh python3 app/prototype/tools/validate_api_connections.py
"""

from __future__ import annotations

import base64
import os
import sys
import time


def _check_env_keys() -> dict[str, str]:
    """Return available API keys from environment."""
    keys = {
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", ""),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
    }
    return keys


def test_gemini(verbose: bool = True) -> bool:
    """Test Gemini 2.5 Flash via LiteLLM."""
    import litellm

    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        print("[SKIP] Gemini: GOOGLE_API_KEY / GEMINI_API_KEY not set")
        return False

    t0 = time.monotonic()
    try:
        resp = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=[{"role": "user", "content": "Reply with only the word: PONG"}],
            max_tokens=10,
            temperature=0.0,
        )
        text = resp.choices[0].message.content.strip()
        ms = int((time.monotonic() - t0) * 1000)
        if verbose:
            print(f"  Response: {text!r}")
            print(f"  Latency: {ms}ms")
        print(f"[PASS] Gemini 2.5 Flash ({ms}ms)")
        return True
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        print(f"[FAIL] Gemini 2.5 Flash ({ms}ms): {exc}")
        return False


def main() -> int:
    print("=" * 60)
    print("VULCA Prototype — API Connection Validator")
    print("=" * 60)

    keys = _check_env_keys()
    print("\nEnvironment keys:")
    for k, v in keys.items():
        status = f"set ({len(v)} chars)" if v else "NOT SET"
        print(f"  {k}: {status}")

    print("\n--- Testing API connections ---\n")

    results = {
        "Gemini 2.5 Flash": test_gemini(),
    }

    print("\n--- Summary ---\n")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL/SKIP'} {name}")
    print(f"\n{passed}/{total} API connections verified.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
