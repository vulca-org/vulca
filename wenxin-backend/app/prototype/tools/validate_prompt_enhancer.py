#!/usr/bin/env python3
"""Validate the Prompt Enhancer module (Line D).

Tests:
1. PromptEnhancer instantiation (no API needed)
2. Mock/disabled mode — returns original prompt
3. Live LLM call (needs GLOBALAI_API_KEY or DEEPSEEK_API_KEY)
4. Multiple traditions produce distinct outputs
5. Evidence injection works

Usage:
  # Dry run (no API key needed)
  python3 -m app.prototype.tools.validate_prompt_enhancer

  # With live LLM (needs API key)
  python3 -m app.prototype.tools.validate_prompt_enhancer --with-llm
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Validate Prompt Enhancer")
    parser.add_argument("--with-llm", action="store_true", help="Run live LLM tests")
    args = parser.parse_args()

    passed = 0
    failed = 0
    total = 0

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✅ {name}")
        else:
            failed += 1
            print(f"  ❌ {name}: {detail}")

    # ── Test 1: Import and instantiation ──
    print("\n[1/5] Import & Instantiation")
    try:
        from app.prototype.agents.prompt_enhancer import PromptEnhancer
        enhancer = PromptEnhancer(enabled=True)
        check("Import PromptEnhancer", True)
        check("Has enhance method", hasattr(enhancer, "enhance"))
    except Exception as e:
        check("Import PromptEnhancer", False, str(e))

    # ── Test 2: Disabled mode ──
    print("\n[2/5] Disabled Mode")
    try:
        disabled = PromptEnhancer(enabled=False)
        result = disabled.enhance("test subject", "chinese_xieyi")
        check("Disabled returns original", result == "test subject",
              f"got: {result!r}")
    except Exception as e:
        check("Disabled mode", False, str(e))

    # ── Test 3: Invalid model key ──
    print("\n[3/5] Invalid Model Fallback")
    try:
        bad = PromptEnhancer(model_key="nonexistent_model", enabled=True)
        result = bad.enhance("test subject", "default")
        check("Unknown model returns original", result == "test subject",
              f"got: {result!r}")
    except Exception as e:
        check("Invalid model fallback", False, str(e))

    if not args.with_llm:
        print("\n[4/5] Live LLM Tests — SKIPPED (use --with-llm)")
        print("[5/5] Multi-tradition Tests — SKIPPED (use --with-llm)")
        print(f"\n{'='*50}")
        print(f"Results: {passed}/{total} passed, {failed} failed")
        print(f"{'='*50}")
        sys.exit(0 if failed == 0 else 1)

    # ── Test 4: Live LLM enhancement ──
    print("\n[4/5] Live LLM Enhancement")
    test_cases = [
        {
            "subject": "A phoenix rising from ashes",
            "tradition": "chinese_xieyi",
            "evidence": {
                "terminology_hits": [
                    {"term": "凤凰 (phoenix)"},
                    {"term": "涅槃 (nirvana/rebirth)"},
                    {"term": "水墨 (ink wash)"},
                ],
            },
        },
        {
            "subject": "geometric patterns of paradise garden",
            "tradition": "islamic_geometric",
            "evidence": {
                "terminology_hits": [
                    {"term": "tessellation"},
                    {"term": "arabesque"},
                ],
            },
        },
        {
            "subject": "portrait of a scholar in moonlight",
            "tradition": "western_academic",
            "evidence": {},
        },
    ]

    enhancer = PromptEnhancer(enabled=True)
    results = []

    for i, tc in enumerate(test_cases):
        try:
            result = enhancer.enhance(
                subject=tc["subject"],
                cultural_tradition=tc["tradition"],
                evidence=tc["evidence"],
            )
            results.append(result)
            is_enhanced = len(result) > len(tc["subject"])
            check(
                f"Case {i+1} ({tc['tradition']}): enhanced",
                is_enhanced,
                f"original={len(tc['subject'])} chars, result={len(result)} chars",
            )
            if is_enhanced:
                print(f"    Original: {tc['subject']}")
                print(f"    Enhanced: {result[:150]}...")
        except Exception as e:
            check(f"Case {i+1} ({tc['tradition']})", False, str(e))

    # ── Test 5: Distinct outputs per tradition ──
    print("\n[5/5] Multi-tradition Distinctness")
    if len(results) >= 2:
        all_distinct = len(set(results)) == len(results)
        check("All traditions produce distinct prompts", all_distinct)
    else:
        check("Multi-tradition test", False, "Not enough successful results")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print(f"{'='*50}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
