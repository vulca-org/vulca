#!/usr/bin/env python3
"""Generate all README v2 assets in one run.

Usage:
    source wenxin-backend/.env && export GOOGLE_API_KEY
    cd vulca && .venv/bin/python scripts/generate-readme-assets.py
"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

VULCA = [sys.executable, "-m", "vulca.cli"]
OUT = Path("assets/demo/v2")


def run(cmd: list[str], output_file: str = "", timeout: int = 120) -> str:
    """Run command, optionally save stdout to file."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "PYTHONPATH": "src"})
    if result.returncode != 0:
        print(f"    WARN: exit {result.returncode}: {result.stderr[:200]}")
    if output_file:
        Path(output_file).write_text(result.stdout)
        print(f"    → {output_file}")
    return result.stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "layers-split").mkdir(exist_ok=True)
    (OUT / "layers-export").mkdir(exist_ok=True)

    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set")
        sys.exit(1)

    print("=" * 60)
    print("VULCA README v2 — Asset Generation")
    print("=" * 60)

    # ── 1. Hero artworks ──
    print("\n[1/6] Generating hero artworks...")
    heroes = [
        ("Misty mountains after rain pine pavilion hidden in clouds ink wash style",
         "chinese_xieyi", "hero-xieyi.png"),
        ("Autumn maple leaves on ancient stone temple steps warm golden afternoon light",
         "japanese_traditional", "hero-japanese.png"),
        ("Premium artisan tea packaging mountain landscape watercolor Eastern minimalism",
         "brand_design", "hero-brand.png"),
    ]
    for intent, tradition, filename in heroes:
        try:
            run(VULCA + ["create", intent, "-t", tradition, "--provider", "gemini",
                         "-o", str(OUT / filename)], timeout=120)
        except Exception as e:
            print(f"    ERROR: {e}")

    # ── 2. Layers V2 showcase ──
    print("\n[2/6] Generating Layers V2 showcase...")
    layers_src = str(OUT / "hero-xieyi.png")
    if Path(layers_src).exists():
        # Analyze
        run(VULCA + ["layers", "analyze", layers_src],
            output_file=str(OUT / "layers-analyze.txt"))
        # Split (regenerate mode)
        run(VULCA + ["layers", "split", layers_src,
                     "-o", str(OUT / "layers-split"),
                     "--mode", "regenerate", "--provider", "gemini"],
            output_file=str(OUT / "layers-split.txt"), timeout=180)
        # Composite
        split_dir = str(OUT / "layers-split")
        if (Path(split_dir) / "manifest.json").exists():
            run(VULCA + ["layers", "composite", split_dir,
                         "-o", str(OUT / "layers-composite.png")])
            # Export
            run(VULCA + ["layers", "export", split_dir,
                         "-o", str(OUT / "layers-export")])
    else:
        print("    SKIP: hero-xieyi.png not generated")

    # ── 3. Evaluate outputs ──
    print("\n[3/6] Running evaluate (3 modes)...")
    eval_img = layers_src
    if Path(eval_img).exists():
        run(VULCA + ["evaluate", eval_img, "-t", "chinese_xieyi"],
            output_file=str(OUT / "eval-strict.txt"))
        run(VULCA + ["evaluate", eval_img, "-t", "chinese_xieyi", "--mode", "reference"],
            output_file=str(OUT / "eval-reference.txt"))
        run(VULCA + ["evaluate", eval_img,
                     "-t", "chinese_xieyi,japanese_traditional,western_academic",
                     "--mode", "fusion"],
            output_file=str(OUT / "eval-fusion.txt"))
    else:
        print("    SKIP: no image to evaluate")

    # ── 4. Studio --auto ──
    print("\n[4/6] Running Studio --auto...")
    try:
        run(VULCA + ["studio", "Cyberpunk ink wash neon pavilions in misty mountains",
                     "--provider", "gemini", "--auto", "--max-rounds", "2"],
            output_file=str(OUT / "studio-auto.txt"), timeout=300)
    except Exception as e:
        print(f"    ERROR: {e}")

    # ── 5. Tool outputs ──
    print("\n[5/6] Running 5 analysis tools...")
    if Path(eval_img).exists():
        tools = ["brushstroke_analyze", "whitespace_analyze", "composition_analyze",
                 "color_gamut_check", "color_correct"]
        for tool in tools:
            run(VULCA + ["tools", "run", tool, "--image", eval_img,
                         "--tradition", "chinese_xieyi"],
                output_file=str(OUT / f"tool-{tool}.txt"))

    # ── 6. Evolution data ──
    print("\n[6/6] Collecting evolution data...")
    run(VULCA + ["evolution", "chinese_xieyi"],
        output_file=str(OUT / "evolution-xieyi.txt"))
    run(VULCA + ["evolution", "default"],
        output_file=str(OUT / "evolution-default.txt"))

    # ── Summary ──
    print("\n" + "=" * 60)
    print("Asset generation complete. Files:")
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            size = f.stat().st_size
            size_str = f"{size / 1024:.0f}KB" if size >= 1024 else f"{size}B"
            print(f"  {str(f.relative_to(OUT)):<50s} {size_str}")
    print("=" * 60)


if __name__ == "__main__":
    main()
