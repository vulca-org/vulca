#!/usr/bin/env python3
"""Validate image-aware scoring: verify CLIP-blended scores vary across images.

Uses the FLUX sensitivity test images (already generated) to confirm that:
1. ImageScorer loads and produces scores
2. Different images for the same subject get different scores
3. CriticRules.score() integrates image scores into L1-L5
4. Score variation across images is sufficient for self-correction
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main() -> None:
    from app.prototype.agents.image_scorer import ImageScorer
    from app.prototype.agents.critic_rules import CriticRules

    checks_pass = 0
    checks_total = 0

    img_dir = Path(__file__).resolve().parent.parent / "checkpoints" / "flux_sensitivity"

    # ── Test 1: ImageScorer availability ──
    print("=" * 60)
    print("  Image-Aware Scoring Validation")
    print("=" * 60)

    scorer = ImageScorer.get()
    checks_total += 1
    if scorer.available:
        print(f"[PASS] ImageScorer available (CLIP ViT-B/32)")
        checks_pass += 1
    else:
        print(f"[FAIL] ImageScorer not available — CLIP model missing")
        print("  Cannot proceed without CLIP. Install: pip install sentence-transformers")
        sys.exit(1)

    # ── Test 2: Score images from sensitivity test ──
    test_cases = [
        {
            "subject": "Islamic geometric pattern",
            "tradition": "islamic_geometric",
            "poor": img_dir / "islamic-1_poor.jpg",
            "rich": img_dir / "islamic-1_rich.jpg",
        },
        {
            "subject": "Chinese ink landscape",
            "tradition": "chinese_xieyi",
            "poor": img_dir / "xieyi-1_poor.jpg",
            "rich": img_dir / "xieyi-1_rich.jpg",
        },
        {
            "subject": "Romantic landscape with dramatic light",
            "tradition": "western_academic",
            "poor": img_dir / "turner-1_poor.jpg",
            "rich": img_dir / "turner-1_rich.jpg",
        },
        {
            "subject": "African textile pattern",
            "tradition": "african_traditional",
            "poor": img_dir / "african-1_poor.jpg",
            "rich": img_dir / "african-1_rich.jpg",
        },
        {
            "subject": "Chinese court painting with birds",
            "tradition": "chinese_gongbi",
            "poor": img_dir / "gongbi-1_poor.jpg",
            "rich": img_dir / "gongbi-1_rich.jpg",
        },
    ]

    # Check if test images exist
    missing = [tc["subject"] for tc in test_cases if not tc["poor"].exists()]
    if missing:
        print(f"\n[SKIP] Sensitivity test images not found. Run validate_flux_sensitivity.py first.")
        print(f"  Missing: {missing}")
        sys.exit(0)

    print(f"\n--- ImageScorer.score_image() on {len(test_cases)} pairs ---\n")

    deltas_l1 = []
    deltas_l3 = []
    deltas_l5 = []

    for tc in test_cases:
        poor_scores = scorer.score_image(
            str(tc["poor"]), tc["subject"], tc["tradition"]
        )
        rich_scores = scorer.score_image(
            str(tc["rich"]), tc["subject"], tc["tradition"]
        )

        checks_total += 1
        if poor_scores is not None and rich_scores is not None:
            print(f"  {tc['tradition']}:")
            print(f"    POOR: L1={poor_scores['L1']:.3f} L3={poor_scores['L3']:.3f} L5={poor_scores['L5']:.3f}")
            print(f"    RICH: L1={rich_scores['L1']:.3f} L3={rich_scores['L3']:.3f} L5={rich_scores['L5']:.3f}")

            d1 = rich_scores["L1"] - poor_scores["L1"]
            d3 = rich_scores["L3"] - poor_scores["L3"]
            d5 = rich_scores["L5"] - poor_scores["L5"]
            print(f"    DELTA: L1={d1:+.3f} L3={d3:+.3f} L5={d5:+.3f}")
            print(f"    SCORES DIFFER: {abs(d1) > 0.001 or abs(d3) > 0.001 or abs(d5) > 0.001}")

            deltas_l1.append(abs(d1))
            deltas_l3.append(abs(d3))
            deltas_l5.append(abs(d5))
            checks_pass += 1
        else:
            print(f"  {tc['tradition']}: [FAIL] score_image returned None")

    # ── Test 3: Scores actually vary ──
    checks_total += 1
    avg_delta = (sum(deltas_l1) + sum(deltas_l3) + sum(deltas_l5)) / (len(deltas_l1) * 3)
    print(f"\n  Average |delta| across dimensions: {avg_delta:.4f}")
    if avg_delta > 0.01:
        print(f"  [PASS] Scores vary meaningfully across images (avg delta > 0.01)")
        checks_pass += 1
    else:
        print(f"  [FAIL] Scores don't vary enough (avg delta = {avg_delta:.4f})")

    # ── Test 4: CriticRules integration ──
    print(f"\n--- CriticRules.score() with image blending ---\n")
    rules = CriticRules()

    # Score same candidate with two different images
    base_candidate = {
        "prompt": "Islamic geometric pattern with arabesque tessellation, traditional art",
        "steps": 20,
        "sampler": "euler",
        "model_ref": "FLUX.1-schnell",
    }
    evidence = {
        "terminology_hits": [{"term": "arabesque"}, {"term": "tessellation"}],
        "sample_matches": [{"id": "s1"}],
        "taboo_violations": [],
    }

    # Without image (old behavior)
    scores_no_img = rules.score(
        candidate=base_candidate,
        evidence=evidence,
        cultural_tradition="islamic_geometric",
        subject="Islamic geometric pattern",
    )
    print("  No image (rule-only):")
    for ds in scores_no_img:
        print(f"    {ds.dimension}: {ds.score:.4f} — {ds.rationale}")

    # With poor image
    cand_poor = {**base_candidate, "image_path": str(test_cases[0]["poor"])}
    scores_poor = rules.score(
        candidate=cand_poor,
        evidence=evidence,
        cultural_tradition="islamic_geometric",
        subject="Islamic geometric pattern",
    )
    print("\n  With POOR image:")
    for ds in scores_poor:
        print(f"    {ds.dimension}: {ds.score:.4f} — {ds.rationale}")

    # With rich image
    cand_rich = {**base_candidate, "image_path": str(test_cases[0]["rich"])}
    scores_rich = rules.score(
        candidate=cand_rich,
        evidence=evidence,
        cultural_tradition="islamic_geometric",
        subject="Islamic geometric pattern",
    )
    print("\n  With RICH image:")
    for ds in scores_rich:
        print(f"    {ds.dimension}: {ds.score:.4f} — {ds.rationale}")

    # Check that image-blended scores differ from each other
    checks_total += 1
    score_diffs = []
    for i in range(5):
        d = abs(scores_poor[i].score - scores_rich[i].score)
        score_diffs.append(d)
    total_diff = sum(score_diffs)
    print(f"\n  Total score difference (poor vs rich): {total_diff:.4f}")
    if total_diff > 0.01:
        print(f"  [PASS] CriticRules produces different scores for different images")
        checks_pass += 1
    else:
        print(f"  [FAIL] CriticRules scores don't differ between images")

    # Check backward compatibility: no image = no CLIP in rationale
    checks_total += 1
    has_clip_in_no_img = any("CLIP" in ds.rationale for ds in scores_no_img)
    if not has_clip_in_no_img:
        print(f"  [PASS] No-image path is backward compatible (no CLIP in rationale)")
        checks_pass += 1
    else:
        print(f"  [FAIL] No-image path incorrectly has CLIP rationale")

    # Check that image path has CLIP in rationale
    checks_total += 1
    has_clip_in_img = any("CLIP" in ds.rationale for ds in scores_rich)
    if has_clip_in_img:
        print(f"  [PASS] Image path includes CLIP in rationale")
        checks_pass += 1
    else:
        print(f"  [FAIL] Image path missing CLIP rationale")

    # ── Test 5: Self-correction potential ──
    print(f"\n--- Self-Correction Potential ---\n")

    # The key question: would Round N+1 (with enriched prompt + new image)
    # get a measurably different score from Round N?
    checks_total += 1
    weighted_poor = sum(
        {"visual_perception": 0.15, "technical_analysis": 0.20,
         "cultural_context": 0.25, "critical_interpretation": 0.20,
         "philosophical_aesthetic": 0.20}.get(ds.dimension, 0) * ds.score
        for ds in scores_poor
    )
    weighted_rich = sum(
        {"visual_perception": 0.15, "technical_analysis": 0.20,
         "cultural_context": 0.25, "critical_interpretation": 0.20,
         "philosophical_aesthetic": 0.20}.get(ds.dimension, 0) * ds.score
        for ds in scores_rich
    )
    wt_delta = weighted_rich - weighted_poor
    print(f"  Weighted total (poor): {weighted_poor:.4f}")
    print(f"  Weighted total (rich): {weighted_rich:.4f}")
    print(f"  Delta: {wt_delta:+.4f}")

    if abs(wt_delta) > 0.005:
        print(f"  [PASS] Weighted total varies between images (self-correction viable)")
        checks_pass += 1
    else:
        print(f"  [FAIL] Weighted total doesn't vary enough")

    # ── Summary ──
    print(f"\n{'=' * 60}")
    print(f"  RESULT: {checks_pass}/{checks_total} PASS")
    print(f"{'=' * 60}")

    if checks_pass == checks_total:
        print("\n  Image-aware scoring is WORKING.")
        print("  Self-correction loop can now produce score changes across rounds.")
    else:
        print(f"\n  {checks_total - checks_pass} check(s) failed — review above.")


if __name__ == "__main__":
    main()
