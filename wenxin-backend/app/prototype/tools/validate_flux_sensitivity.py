#!/usr/bin/env python3
"""Route C: Validate FLUX prompt sensitivity for aesthetic steering.

Tests whether FLUX generates measurably different images when given
aesthetically rich vs aesthetically poor prompts for the same subject.

Uses CLIP similarity to cultural reference concepts as a proxy for quality.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Prompt pairs: same subject, different aesthetic depth ──

PROMPT_PAIRS = [
    {
        "id": "islamic-1",
        "subject": "Islamic geometric pattern",
        "poor": "Islamic geometric pattern",
        "rich": "Islamic geometric pattern with intricate tessellation, arabesques interlocking in infinite symmetry, gold leaf on lapis lazuli ground, Alhambra-inspired muqarnas geometry, sacred mathematical precision",
        "reference_concept": "Islamic geometric art Alhambra tessellation arabesque",
    },
    {
        "id": "xieyi-1",
        "subject": "Chinese ink landscape",
        "poor": "Chinese ink landscape painting",
        "rich": "Chinese xieyi landscape in the style of Dong Yuan, hemp-fiber texture strokes (pima cun), layered ink washes suggesting mist and distance, one-corner composition with vast empty space (liubai), mounted on xuan paper",
        "reference_concept": "Chinese xieyi ink landscape painting shanshui Dong Yuan",
    },
    {
        "id": "turner-1",
        "subject": "Romantic landscape with dramatic light",
        "poor": "landscape painting with sunlight",
        "rich": "Turner-esque atmospheric landscape, luminous golden light breaking through storm clouds, dissolving forms at the boundary of abstraction, wet-in-wet watercolor technique, sublime terror of nature's vastness, warm-to-cool tonal gradation",
        "reference_concept": "Turner atmospheric landscape sublime romantic painting light",
    },
    {
        "id": "african-1",
        "subject": "African textile pattern",
        "poor": "African pattern textile",
        "rich": "Asante Kente cloth with symbolic adinkra motifs, bold geometric strips in gold and black, each color encoding social meaning, woven silk and cotton texture visible, royal ceremonial quality",
        "reference_concept": "Kente cloth Asante African textile pattern adinkra",
    },
    {
        "id": "gongbi-1",
        "subject": "Chinese court painting with birds",
        "poor": "Chinese painting of birds and flowers",
        "rich": "Gongbi meticulous court painting in the style of Emperor Huizong, exquisite detail in feather rendering, mineral pigments on silk, fine iron-wire lines (tiexi miao), auspicious crane motif with precise anatomical observation, Song dynasty aesthetic refinement",
        "reference_concept": "Chinese gongbi meticulous painting birds Song dynasty Huizong",
    },
]


def generate_flux_image(prompt: str, seed: int, output_path: Path) -> float:
    """Generate one FLUX image via Together.ai. Returns latency in seconds."""
    import base64
    from litellm import image_generation

    t0 = time.monotonic()
    response = image_generation(
        model="together_ai/black-forest-labs/FLUX.1-schnell",
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="b64_json",
        seed=seed,
    )
    latency = time.monotonic() - t0

    # Save image
    img_data = base64.b64decode(response.data[0].b64_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(img_data)
    return latency


def compute_clip_similarity(image_path: Path, text: str) -> float:
    """Compute CLIP cosine similarity between image and text concept."""
    try:
        from sentence_transformers import SentenceTransformer
        from PIL import Image
        import numpy as np

        # Use CLIP model
        model = SentenceTransformer("clip-ViT-B-32")
        img = Image.open(image_path).convert("RGB")

        img_emb = model.encode(img, convert_to_numpy=True)
        txt_emb = model.encode(text, convert_to_numpy=True)

        # Cosine similarity
        sim = float(np.dot(img_emb, txt_emb) / (np.linalg.norm(img_emb) * np.linalg.norm(txt_emb)))
        return sim
    except Exception as e:
        print(f"  CLIP error: {e}")
        return 0.0


def main() -> None:
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        print("ERROR: TOGETHER_API_KEY not set")
        sys.exit(1)

    output_dir = Path(__file__).resolve().parent.parent / "checkpoints" / "flux_sensitivity"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    seed = 42  # Same seed for both variants to isolate prompt effect

    print("=" * 70)
    print("  FLUX Prompt Sensitivity Test")
    print("  5 subjects × 2 variants (poor/rich) × same seed")
    print("=" * 70)

    for pair in PROMPT_PAIRS:
        print(f"\n--- {pair['id']}: {pair['subject']} ---")

        # Generate poor variant
        poor_path = output_dir / f"{pair['id']}_poor.jpg"
        print(f"  Generating POOR variant...")
        poor_latency = generate_flux_image(pair["poor"], seed, poor_path)
        print(f"    Saved: {poor_path.name} ({poor_path.stat().st_size // 1024}KB, {poor_latency:.1f}s)")

        # Generate rich variant
        rich_path = output_dir / f"{pair['id']}_rich.jpg"
        print(f"  Generating RICH variant...")
        rich_latency = generate_flux_image(pair["rich"], seed, rich_path)
        print(f"    Saved: {rich_path.name} ({rich_path.stat().st_size // 1024}KB, {rich_latency:.1f}s)")

        # CLIP similarity to reference concept
        print(f"  Computing CLIP similarity to: '{pair['reference_concept'][:50]}...'")
        poor_clip = compute_clip_similarity(poor_path, pair["reference_concept"])
        rich_clip = compute_clip_similarity(rich_path, pair["reference_concept"])
        delta = rich_clip - poor_clip

        print(f"    POOR CLIP: {poor_clip:.4f}")
        print(f"    RICH CLIP: {rich_clip:.4f}")
        print(f"    DELTA:     {delta:+.4f} {'✓ RICH wins' if delta > 0 else '✗ POOR wins'}")

        results.append({
            "id": pair["id"],
            "subject": pair["subject"],
            "poor_clip": round(poor_clip, 4),
            "rich_clip": round(rich_clip, 4),
            "delta": round(delta, 4),
            "rich_wins": delta > 0,
            "poor_prompt": pair["poor"],
            "rich_prompt": pair["rich"],
        })

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"{'ID':<12} {'Poor CLIP':>10} {'Rich CLIP':>10} {'Delta':>8} {'Winner':>10}")
    print("-" * 52)
    wins = 0
    for r in results:
        winner = "RICH" if r["rich_wins"] else "POOR"
        if r["rich_wins"]:
            wins += 1
        print(f"{r['id']:<12} {r['poor_clip']:>10.4f} {r['rich_clip']:>10.4f} {r['delta']:>+8.4f} {winner:>10}")

    print("-" * 52)
    avg_delta = sum(r["delta"] for r in results) / len(results)
    print(f"Average delta: {avg_delta:+.4f}")
    print(f"Rich wins: {wins}/{len(results)}")
    print()

    if avg_delta > 0.01 and wins >= 3:
        print("CONCLUSION: FLUX IS sensitive to aesthetic prompt engineering.")
        print("  → Route A (image-aware scoring) is viable for self-correction.")
    elif avg_delta > 0 and wins >= 2:
        print("CONCLUSION: FLUX shows WEAK sensitivity to aesthetic prompts.")
        print("  → Route A may work but prompt_delta needs to be more specific.")
    else:
        print("CONCLUSION: FLUX is NOT sensitive to aesthetic prompt engineering.")
        print("  → Self-correction via prompt modification is not viable on FLUX.")
        print("  → Consider SD1.5+ControlNet inpainting (Phase A) instead.")

    # Save results
    results_path = output_dir / "sensitivity_results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved: {results_path}")


if __name__ == "__main__":
    main()
