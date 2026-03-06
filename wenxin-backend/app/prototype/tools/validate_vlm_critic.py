#!/usr/bin/env python3
"""Validate the VLM Critic module (Line A).

Tests:
1. VLMCritic instantiation (no API needed)
2. JSON response parsing (mock data)
3. Live VLM scoring on real ablation images
4. VLM vs CLIP score comparison
5. CriticRules integration (VLM→blend path)

Usage:
  # Dry run (no API key needed)
  python3 -m app.prototype.tools.validate_vlm_critic

  # With live VLM (needs GLOBALAI_API_KEY)
  python3 -m app.prototype.tools.validate_vlm_critic --with-vlm

  # Verbose output
  python3 -m app.prototype.tools.validate_vlm_critic --with-vlm -v
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Real ablation test cases with known checkpoint images
_TEST_CASES = [
    {
        "task_id": "bench-005",
        "subject": "Alhambra tessellation geometric pattern",
        "tradition": "islamic_geometric",
        "category": "cultural",
        "conditions": ["C", "D"],
    },
    {
        "task_id": "bench-017",
        "subject": "Zhang Daqian splashed ink landscape",
        "tradition": "chinese_xieyi",
        "category": "poetic",
        "conditions": ["C", "D"],
    },
    {
        "task_id": "bench-020",
        "subject": "oriental uncivilized naive exotic primitive",
        "tradition": "islamic_geometric",
        "category": "taboo",
        "conditions": ["C", "D"],
    },
]

_CHECKPOINT_ROOT = (
    Path(__file__).resolve().parent.parent / "checkpoints" / "draft"
)


def _find_image(condition: str, task_id: str) -> str | None:
    """Find the first candidate image for a condition+task."""
    task_dir = _CHECKPOINT_ROOT / f"abl-{condition}_{task_id}"
    if not task_dir.exists():
        return None
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        images = sorted(task_dir.glob(ext))
        if images:
            return str(images[0])
    return None


def main():
    parser = argparse.ArgumentParser(description="Validate VLM Critic")
    parser.add_argument("--with-vlm", action="store_true", help="Run live VLM tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
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
        from app.prototype.agents.vlm_critic import VLMCritic
        vlm = VLMCritic.get()
        check("Import VLMCritic", True)
        check("Has score_image method", hasattr(vlm, "score_image"))
        check("Singleton pattern works", VLMCritic.get() is vlm)
    except Exception as e:
        check("Import VLMCritic", False, str(e))

    # ── Test 2: JSON parsing ──
    print("\n[2/5] JSON Response Parsing")
    try:
        from app.prototype.agents.vlm_critic import VLMCritic

        # Clean JSON
        clean = '{"L1": 0.75, "L2": 0.80, "L3": 0.65, "L4": 0.90, "L5": 0.70, "L1_rationale": "good"}'
        result = VLMCritic._parse_scores(clean)
        check("Clean JSON parsing", result is not None and result["L1"] == 0.75)

        # Markdown-wrapped JSON
        md = '```json\n{"L1": 0.6, "L2": 0.7, "L3": 0.5, "L4": 0.8, "L5": 0.6}\n```'
        result_md = VLMCritic._parse_scores(md)
        check("Markdown-wrapped JSON", result_md is not None and result_md["L1"] == 0.6)

        # Out-of-range clamping
        oob = '{"L1": 1.5, "L2": -0.3, "L3": 0.5, "L4": 0.8, "L5": 0.6}'
        result_oob = VLMCritic._parse_scores(oob)
        check("Out-of-range clamping",
              result_oob is not None and result_oob["L1"] == 1.0 and result_oob["L2"] == 0.0)

        # Invalid JSON
        bad = "This is not JSON at all"
        result_bad = VLMCritic._parse_scores(bad)
        check("Invalid JSON returns None", result_bad is None)

    except Exception as e:
        check("JSON parsing", False, str(e))

    # ── Test 3: CriticRules integration (dry) ──
    print("\n[3/5] CriticRules Integration (dry)")
    try:
        from app.prototype.agents.critic_rules import CriticRules
        rules = CriticRules()

        # Mock VLM scores
        mock_vlm = {
            "L1": 0.75, "L2": 0.80, "L3": 0.65, "L4": 0.90, "L5": 0.70,
            "_L1_raw": 0.75, "_L2_raw": 0.80, "_L3_raw": 0.65,
            "_L4_raw": 0.90, "_L5_raw": 0.70,
        }

        from app.prototype.agents.critic_types import DimensionScore
        from app.prototype.agents.critic_config import DIMENSIONS
        base_scores = [
            DimensionScore(dimension=DIMENSIONS[i], score=0.5, rationale="base=0.5")
            for i in range(5)
        ]

        blended = CriticRules._blend_vlm_scores(base_scores, mock_vlm)
        check("Blend produces 5 scores", len(blended) == 5)
        check("L1 blended higher (VLM=0.75, w=0.7)",
              blended[0].score > 0.5,
              f"got {blended[0].score:.3f}")
        check("L5 blended higher (VLM=0.70, w=0.7)",
              blended[4].score > 0.5,
              f"got {blended[4].score:.3f}")
        check("Rationale contains VLM",
              "VLM_L1" in blended[0].rationale,
              blended[0].rationale[:80])

        if args.verbose:
            for s in blended:
                print(f"    {s.dimension}: {s.score:.3f} — {s.rationale[:100]}")

    except Exception as e:
        check("CriticRules integration", False, str(e))

    if not args.with_vlm:
        print("\n[4/5] Live VLM Scoring — SKIPPED (use --with-vlm)")
        print("[5/5] VLM vs CLIP Comparison — SKIPPED (use --with-vlm)")
        print(f"\n{'='*50}")
        print(f"Results: {passed}/{total} passed, {failed} failed")
        print(f"{'='*50}")
        sys.exit(0 if failed == 0 else 1)

    # ── Test 4: Live VLM scoring on real images ──
    print("\n[4/5] Live VLM Scoring on Real Ablation Images")
    from app.prototype.agents.vlm_critic import VLMCritic
    vlm = VLMCritic.get()

    if not vlm.available:
        check("VLM available", False, "No API key set (GLOBALAI_API_KEY)")
    else:
        check("VLM available", True)

        vlm_results = []
        for tc in _TEST_CASES:
            for cond in tc["conditions"]:
                img = _find_image(cond, tc["task_id"])
                if not img:
                    check(f"{cond}_{tc['task_id']}: image found", False, "not found")
                    continue

                result = vlm.score_image(
                    image_path=img,
                    subject=tc["subject"],
                    cultural_tradition=tc["tradition"],
                )
                if result is None:
                    check(f"{cond}_{tc['task_id']}: VLM scored", False, "returned None")
                    continue

                has_all = all(k in result for k in ("L1", "L2", "L3", "L4", "L5"))
                check(f"{cond}_{tc['task_id']}: all 5 dimensions",
                      has_all, str(list(result.keys())))

                if has_all:
                    vlm_results.append({
                        "condition": cond,
                        "task_id": tc["task_id"],
                        "category": tc["category"],
                        "scores": {k: result[k] for k in ("L1", "L2", "L3", "L4", "L5")},
                    })
                    if args.verbose:
                        print(f"    L1={result['L1']:.2f} L2={result['L2']:.2f} "
                              f"L3={result['L3']:.2f} L4={result['L4']:.2f} "
                              f"L5={result['L5']:.2f}")
                        for k in ("L1", "L2", "L3", "L4", "L5"):
                            rat = result.get(f"{k}_rationale", "")
                            if rat:
                                print(f"      {k}: {rat}")

        # ── Test 5: Taboo detection check ──
        print("\n[5/5] Taboo Task Detection")
        taboo_results = [r for r in vlm_results if r["category"] == "taboo"]
        if taboo_results:
            for tr in taboo_results:
                # bench-020 uses offensive terms — L4 should be LOW
                l4 = tr["scores"]["L4"]
                check(
                    f"Taboo task {tr['condition']}_{tr['task_id']}: L4 < 0.5",
                    l4 < 0.5,
                    f"L4={l4:.2f} (expected low for taboo content)"
                )
        else:
            check("Taboo detection", False, "No taboo task results available")

        # Summary table
        if vlm_results:
            print(f"\n  {'Cond':>4} {'Task':>12} {'Cat':>8} {'L1':>5} {'L2':>5} {'L3':>5} {'L4':>5} {'L5':>5}")
            print(f"  {'─'*4} {'─'*12} {'─'*8} {'─'*5} {'─'*5} {'─'*5} {'─'*5} {'─'*5}")
            for r in vlm_results:
                s = r["scores"]
                print(f"  {r['condition']:>4} {r['task_id']:>12} {r['category']:>8} "
                      f"{s['L1']:5.2f} {s['L2']:5.2f} {s['L3']:5.2f} {s['L4']:5.2f} {s['L5']:5.2f}")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print(f"{'='*50}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
