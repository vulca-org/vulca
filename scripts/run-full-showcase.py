#!/usr/bin/env python3
"""Run the full 8×8 showcase: 8 images × 8 capabilities.

Capabilities per image:
  1. Evaluate (primary tradition, --mode reference, full JSON with rationales)
  2. Cross-tradition (3-4 traditions per image, fusion comparison)
  3. Tools (brushstroke + whitespace + composition analysis)
  4. Decompose (extract mode, 3 layers per image)
  5. Redraw (img2img one layer → chinese_xieyi style via ComfyUI)
  6. Composite (reassemble with redrawn layer)
  7. Inpaint (add cultural element to composited result via ComfyUI)
  8. Re-evaluate (score improvement measurement)

Usage:
    python scripts/run-full-showcase.py                    # all capabilities, all images
    python scripts/run-full-showcase.py --caps 1,2,3       # specific capabilities
    python scripts/run-full-showcase.py --images starry-night,earthrise  # specific images
    python scripts/run-full-showcase.py --caps 3 --dry-run # preview commands
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORIGINALS = REPO_ROOT / "assets" / "showcase" / "originals"
RESULTS = REPO_ROOT / "assets" / "showcase" / "results"
LAYERS_ROOT = REPO_ROOT / "assets" / "showcase" / "layers"
COMPOSITES = REPO_ROOT / "assets" / "showcase" / "composites"
INPAINTED = REPO_ROOT / "assets" / "showcase" / "inpainted"
TOOLS_DIR = REPO_ROOT / "assets" / "showcase" / "tools"

# Image → primary tradition mapping
IMAGE_TRADITIONS: dict[str, str] = {
    "earthrise": "photography",
    "migrant-mother": "photography",
    "starry-night": "western_academic",
    "girl-pearl-earring": "western_academic",
    "water-lilies": "western_academic",
    "great-wave": "japanese_traditional",
    "qingming-bridge": "chinese_gongbi",
    "padmapani": "south_asian",
}

# Image → cross-tradition targets (excluding primary)
CROSS_TRADITIONS: dict[str, list[str]] = {
    "earthrise": ["chinese_xieyi", "japanese_traditional", "contemporary_art"],
    "migrant-mother": ["western_academic", "chinese_xieyi", "south_asian"],
    "starry-night": ["chinese_xieyi", "japanese_traditional", "south_asian"],
    "girl-pearl-earring": ["photography", "chinese_gongbi", "japanese_traditional"],
    "water-lilies": ["chinese_xieyi", "japanese_traditional", "watercolor"],
    "great-wave": ["western_academic", "chinese_xieyi", "south_asian"],
    "qingming-bridge": ["chinese_xieyi", "western_academic", "japanese_traditional"],
    "padmapani": ["western_academic", "chinese_xieyi", "islamic_geometric"],
}

# Image → inpaint instruction
INPAINT_INSTRUCTIONS: dict[str, dict] = {
    "earthrise": {"region": "0,60,40,40", "instruction": "add a small Chinese scholar pavilion silhouette on the lunar horizon"},
    "migrant-mother": {"region": "60,0,40,50", "instruction": "add soft ink-wash mountains fading into mist in the background"},
    "starry-night": {"region": "0,0,100,30", "instruction": "add a subtle Chinese dragon constellation winding through the stars"},
    "girl-pearl-earring": {"region": "60,0,40,60", "instruction": "add delicate cherry blossom branches in the dark background"},
    "water-lilies": {"region": "0,0,50,30", "instruction": "add a misty Chinese bridge silhouette reflected in the water"},
    "great-wave": {"region": "30,0,40,40", "instruction": "add a traditional Chinese junk boat riding the wave"},
    "qingming-bridge": {"region": "0,0,100,25", "instruction": "add distant misty pagodas and flying cranes in the sky"},
    "padmapani": {"region": "60,0,40,100", "instruction": "add ornate Islamic geometric patterns along the border"},
}

VLM_MODEL = "ollama_chat/gemma4"
VLM_BASE = "http://localhost:11434"
COMFYUI_PROVIDER = "comfyui"

# Per-capability timeouts (seconds)
TIMEOUT_VLM = 300       # VLM calls (evaluate, decompose)
TIMEOUT_COMFYUI = 600   # ComfyUI img2img (redraw, inpaint)
TIMEOUT_LOCAL = 120      # Local algorithmic (tools, composite)

# Counters for summary report
_stats: dict[str, int] = {"ok": 0, "skip": 0, "fail": 0, "timeout": 0}


def run_cmd(cmd: list[str], label: str, dry_run: bool = False,
            timeout: int = TIMEOUT_VLM) -> dict | None:
    """Run a vulca CLI command and return parsed JSON if --json was used."""
    print(f"\n{'[DRY]' if dry_run else '[RUN]'} {label}")
    print(f"  $ {' '.join(cmd)}")
    if dry_run:
        return None
    start = time.time()
    env = {**os.environ, "VULCA_VLM_MODEL": VLM_MODEL, "OLLAMA_API_BASE": VLM_BASE}
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"  TIMEOUT ({elapsed:.1f}s)")
        _stats["timeout"] += 1
        return None
    elapsed = time.time() - start
    if result.returncode != 0:
        stderr_tail = result.stderr.strip()[-300:] if result.stderr else "(no stderr)"
        print(f"  FAILED ({elapsed:.1f}s): ...{stderr_tail}")
        _stats["fail"] += 1
        return None
    print(f"  OK ({elapsed:.1f}s)")
    _stats["ok"] += 1
    if "--json" in cmd:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            print("  (could not parse JSON output)")
            return None
    return {"stdout": result.stdout[:500]}


def save_result(name: str, data: dict, subdir: Path = RESULTS):
    subdir.mkdir(parents=True, exist_ok=True)
    path = subdir / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  → saved {path.relative_to(REPO_ROOT)}")


def _skip(cap: int, img: str, reason: str):
    print(f"\n[SKIP] Cap {cap} {img} ({reason})")
    _stats["skip"] += 1


# ── Capability 1: Primary evaluate ──────────────────────────────────────

def cap1_evaluate(img: str, tradition: str, dry_run: bool):
    out = RESULTS / f"{img}-primary.json"
    if out.exists() and not dry_run:
        return _skip(1, img, "already exists")
    data = run_cmd([
        "vulca", "evaluate", str(ORIGINALS / f"{img}.jpg"),
        "-t", tradition, "--mode", "reference",
        "--vlm-model", VLM_MODEL, "--vlm-base-url", VLM_BASE, "--json",
    ], f"Cap 1: evaluate {img} ({tradition})", dry_run, timeout=TIMEOUT_VLM)
    if data:
        save_result(f"{img}-primary", data)


# ── Capability 2: Cross-tradition ────────────────────────────────────────

def cap2_cross(img: str, traditions: list[str], dry_run: bool):
    for t in traditions:
        out = RESULTS / f"{img}-cross-{t}.json"
        old_out = RESULTS / f"{img}-{t}.json"  # legacy naming from prior session
        if (out.exists() or old_out.exists()) and not dry_run:
            _skip(2, f"{img}/{t}", "already exists")
            continue
        data = run_cmd([
            "vulca", "evaluate", str(ORIGINALS / f"{img}.jpg"),
            "-t", t, "--mode", "reference",
            "--vlm-model", VLM_MODEL, "--vlm-base-url", VLM_BASE, "--json",
        ], f"Cap 2: cross-evaluate {img} ({t})", dry_run, timeout=TIMEOUT_VLM)
        if data:
            save_result(f"{img}-cross-{t}", data)


# ── Capability 3: Tools ──────────────────────────────────────────────────

def cap3_tools(img: str, tradition: str, dry_run: bool):
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    for tool in ["brushstroke_analyze", "whitespace_analyze", "composition_analyze"]:
        short = tool.replace("_analyze", "")
        out = TOOLS_DIR / f"{img}-{short}.json"
        if out.exists() and not dry_run:
            _skip(3, f"{tool} {img}", "already exists")
            continue
        data = run_cmd([
            "vulca", "tools", "run", tool,
            "--image", str(ORIGINALS / f"{img}.jpg"),
            "-t", tradition, "--json",
        ], f"Cap 3: {tool} on {img}", dry_run, timeout=TIMEOUT_LOCAL)
        if data:
            save_result(f"{img}-{short}", data, TOOLS_DIR)


# ── Capability 4: Decompose ──────────────────────────────────────────────

def cap4_decompose(img: str, dry_run: bool):
    layer_dir = LAYERS_ROOT / img
    manifest = layer_dir / "manifest.json"
    if manifest.exists() and not dry_run:
        return _skip(4, img, "manifest exists")
    run_cmd([
        "vulca", "layers", "split", str(ORIGINALS / f"{img}.jpg"),
        "--mode", "extract", "-o", str(layer_dir),
    ], f"Cap 4: decompose {img} (extract)", dry_run, timeout=TIMEOUT_VLM)


# ── Capability 5: Redraw ─────────────────────────────────────────────────

def cap5_redraw(img: str, tradition: str, dry_run: bool):
    layer_dir = LAYERS_ROOT / img
    manifest = layer_dir / "manifest.json"
    if not manifest.exists():
        return _skip(5, img, "no manifest — run cap 4 first")
    with open(manifest) as f:
        mdata = json.load(f)
    layers = mdata.get("layers", [])
    if len(layers) < 2:
        return _skip(5, img, f"need ≥2 layers, got {len(layers)}")
    # Pick the middle layer (most visually interesting)
    target_layer = layers[len(layers) // 2]
    layer_name = target_layer.get("name", target_layer.get("info", {}).get("name", "layer_1"))
    redrawn_marker = layer_dir / f".redrawn-{layer_name}"
    if redrawn_marker.exists() and not dry_run:
        return _skip(5, f"{img}/{layer_name}", "already redrawn")
    result = run_cmd([
        "vulca", "layers", "redraw", str(layer_dir),
        "--layer", layer_name,
        "-i", f"Redraw in {tradition} style with expressive brushwork",
        "-p", COMFYUI_PROVIDER, "-t", tradition,
    ], f"Cap 5: redraw {img}/{layer_name} → {tradition}", dry_run,
        timeout=TIMEOUT_COMFYUI)
    # Only mark success when command actually succeeded
    if result is not None and not dry_run:
        redrawn_marker.touch()


# ── Capability 6: Composite ──────────────────────────────────────────────

def cap6_composite(img: str, dry_run: bool):
    layer_dir = LAYERS_ROOT / img
    COMPOSITES.mkdir(parents=True, exist_ok=True)
    out = COMPOSITES / f"{img}-composite.png"
    if out.exists() and not dry_run:
        return _skip(6, img, "already exists")
    if not (layer_dir / "manifest.json").exists():
        return _skip(6, img, "no layers")
    run_cmd([
        "vulca", "layers", "composite", str(layer_dir),
        "-o", str(out),
    ], f"Cap 6: composite {img}", dry_run, timeout=TIMEOUT_LOCAL)


# ── Capability 7: Inpaint ────────────────────────────────────────────────

def cap7_inpaint(img: str, tradition: str, dry_run: bool, *, mock: bool = False):
    INPAINTED.mkdir(parents=True, exist_ok=True)
    composite = COMPOSITES / f"{img}-composite.png"
    out = INPAINTED / f"{img}-inpainted.png"
    if out.exists() and not dry_run:
        return _skip(7, img, "already exists")
    if not composite.exists():
        return _skip(7, img, "no composite — run cap 6 first")
    instr = INPAINT_INSTRUCTIONS[img]
    cmd = [
        "vulca", "inpaint", str(composite),
        "--region", instr["region"],
        "--instruction", instr["instruction"],
        "-t", tradition, "-p", COMFYUI_PROVIDER,
        "-n", "2", "-s", "1",
        "-o", str(out),
    ]
    if mock:
        cmd.append("--mock")
    run_cmd(cmd, f"Cap 7: inpaint {img}", dry_run, timeout=TIMEOUT_COMFYUI)


# ── Capability 8: Re-evaluate ────────────────────────────────────────────

def cap8_reevaluate(img: str, tradition: str, dry_run: bool):
    out = RESULTS / f"{img}-reevaluate.json"
    if out.exists() and not dry_run:
        return _skip(8, img, "already exists")
    # Prefer inpainted, fall back to composite
    inpainted = INPAINTED / f"{img}-inpainted.png"
    composite = COMPOSITES / f"{img}-composite.png"
    if inpainted.exists():
        source = str(inpainted)
    elif composite.exists():
        source = str(composite)
    else:
        return _skip(8, img, "no composite/inpainted image")
    data = run_cmd([
        "vulca", "evaluate", source,
        "-t", tradition, "--mode", "reference",
        "--vlm-model", VLM_MODEL, "--vlm-base-url", VLM_BASE, "--json",
    ], f"Cap 8: re-evaluate {img} ({tradition})", dry_run, timeout=TIMEOUT_VLM)
    if data:
        save_result(f"{img}-reevaluate", data)


# ── Main ─────────────────────────────────────────────────────────────────

ALL_CAPS = [1, 2, 3, 4, 5, 6, 7, 8]

def main():
    parser = argparse.ArgumentParser(description="Run 8×8 showcase")
    parser.add_argument("--caps", default="all", help="Comma-separated capability numbers (1-8) or 'all'")
    parser.add_argument("--images", default="all", help="Comma-separated image names or 'all'")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running")
    parser.add_argument("--mock-inpaint", action="store_true", help="Use mock mode for inpaint (no provider needed)")
    args = parser.parse_args()

    caps = ALL_CAPS if args.caps == "all" else [int(c) for c in args.caps.split(",")]
    images = list(IMAGE_TRADITIONS.keys()) if args.images == "all" else args.images.split(",")

    # Validate inputs
    invalid_caps = [c for c in caps if c not in ALL_CAPS]
    if invalid_caps:
        print(f"ERROR: invalid capability numbers: {invalid_caps}. Valid: 1-8")
        sys.exit(1)
    invalid_imgs = [i for i in images if i not in IMAGE_TRADITIONS]
    if invalid_imgs:
        print(f"ERROR: unknown images: {invalid_imgs}")
        print(f"  Valid: {', '.join(IMAGE_TRADITIONS.keys())}")
        sys.exit(1)

    # Ensure output dirs exist
    for d in [RESULTS, LAYERS_ROOT, COMPOSITES, INPAINTED, TOOLS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    total_start = time.time()
    for img in images:
        tradition = IMAGE_TRADITIONS[img]
        print(f"\n{'='*60}")
        print(f"  IMAGE: {img} (primary: {tradition})")
        print(f"{'='*60}")

        if 1 in caps:
            cap1_evaluate(img, tradition, args.dry_run)
        if 2 in caps:
            cap2_cross(img, CROSS_TRADITIONS[img], args.dry_run)
        if 3 in caps:
            cap3_tools(img, tradition, args.dry_run)
        if 4 in caps:
            cap4_decompose(img, args.dry_run)
        if 5 in caps:
            cap5_redraw(img, "chinese_xieyi", args.dry_run)
        if 6 in caps:
            cap6_composite(img, args.dry_run)
        if 7 in caps:
            cap7_inpaint(img, tradition, args.dry_run, mock=args.mock_inpaint)
        if 8 in caps:
            cap8_reevaluate(img, tradition, args.dry_run)

    elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"  DONE — {elapsed:.0f}s total")
    print(f"  OK: {_stats['ok']}  SKIP: {_stats['skip']}  "
          f"FAIL: {_stats['fail']}  TIMEOUT: {_stats['timeout']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
