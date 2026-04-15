#!/usr/bin/env python3
"""Run EVF-SAM text-prompted segmentation across all 8 showcase images.

Reads prompt config from assets/showcase/experiments/evfsam_prompts.json.
Writes per-image layer PNGs + red-bg previews to experiments/evfsam_all/<stem>/.
Skips images whose 3 layer PNGs already exist unless --force.

Design decisions (from review):
- Resize to 1024px long-side before inference (SAM backbone is ~1024).
- Load EVF-SAM once and iterate (load is ~20 min, inference ~5-10s/prompt).
- Empty MPS cache between images to avoid memory accumulation.
- Idempotent: skip done images unless --force.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _evfsam_common import (
    beit3_preprocess,
    compose_red_bg,
    imread_rgb,
    load_evfsam,
    sam_preprocess,
)

REPO = Path(__file__).resolve().parent.parent
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
OUT_ROOT = REPO / "assets" / "showcase" / "experiments" / "evfsam_all"
PROMPTS = REPO / "assets" / "showcase" / "experiments" / "evfsam_prompts.json"
INFERENCE_SIZE = 1024


def resize_for_inference(image_np: np.ndarray, max_side: int = INFERENCE_SIZE) -> tuple[np.ndarray, float]:
    h, w = image_np.shape[:2]
    scale = max_side / max(h, w) if max(h, w) > max_side else 1.0
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(image_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, scale
    return image_np, 1.0


def process_image(
    model, tokenizer, device, img_path: Path, prompts: list[tuple[str, str]],
    out_dir: Path, force: bool = False,
) -> dict:
    stem = img_path.stem
    expected = [out_dir / f"{name}.png" for name, _ in prompts]
    if not force and all(p.exists() for p in expected):
        print(f"  SKIP (already done)")
        return {"skipped": True}

    out_dir.mkdir(parents=True, exist_ok=True)

    # Load + optionally downsize for inference
    image_full = imread_rgb(img_path)
    full_h, full_w = image_full.shape[:2]
    image_infer, scale = resize_for_inference(image_full)
    ih, iw = image_infer.shape[:2]
    print(f"  Full: {full_w}x{full_h} | Inference: {iw}x{ih} (scale {scale:.2f})")

    # Preprocess once per image (shared across prompts)
    image_beit = beit3_preprocess(image_infer, 224).to(dtype=model.dtype, device=device)
    image_sam, resize_shape = sam_preprocess(image_infer, INFERENCE_SIZE)
    image_sam = image_sam.to(dtype=model.dtype, device=device)

    orig_rgba = Image.fromarray(image_full).convert("RGBA")
    r_ch, g_ch, b_ch, _ = orig_rgba.split()

    layer_masks: dict[str, np.ndarray] = {}
    stats = {"layers": {}}

    for name, prompt in prompts:
        t0 = time.time()
        input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"].to(device=device)
        with torch.no_grad():
            pred = model.inference(
                image_sam.unsqueeze(0),
                image_beit.unsqueeze(0),
                input_ids,
                resize_list=[resize_shape],
                original_size_list=[(ih, iw)],
            )
        mask_small = (pred.detach().cpu().numpy()[0] > 0).astype(np.uint8) * 255
        # Upsample to full resolution
        if scale < 1.0:
            mask_full = cv2.resize(mask_small, (full_w, full_h), interpolation=cv2.INTER_LINEAR)
            mask_full = (mask_full > 127).astype(np.uint8) * 255
        else:
            mask_full = mask_small
        layer_masks[name] = mask_full > 127

        mask_pil = Image.fromarray(mask_full, mode="L")
        layer = Image.merge("RGBA", (r_ch, g_ch, b_ch, mask_pil))
        layer.save(str(out_dir / f"{name}.png"))

        arr = np.array(layer)
        red = compose_red_bg(arr)
        Image.fromarray(red).save(str(out_dir / f"{name}_on_red.png"))

        pct = layer_masks[name].sum() / (full_h * full_w) * 100
        elapsed = time.time() - t0
        stats["layers"][name] = {"coverage_pct": round(pct, 1), "inference_s": round(elapsed, 1)}
        print(f"  [{name}] {pct:.1f}% coverage, {elapsed:.1f}s")

    # Free MPS cache between images
    if device == "mps":
        torch.mps.empty_cache()

    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Overwrite existing outputs")
    parser.add_argument("--images", default="", help="Comma-separated image stems (default: all)")
    args = parser.parse_args()

    prompts_cfg: dict = json.loads(PROMPTS.read_text())
    all_stems = list(prompts_cfg.keys())
    selected = args.images.split(",") if args.images else all_stems
    selected = [s for s in selected if s in prompts_cfg]
    print(f"Processing {len(selected)}/{len(all_stems)} images")

    # Load model once
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    tokenizer, model = load_evfsam(device)
    print()

    all_stats = {}
    total_start = time.time()
    for stem in selected:
        img_path = ORIG_DIR / f"{stem}.jpg"
        if not img_path.exists():
            print(f"MISS: {img_path}")
            continue
        print(f"[{stem}]")
        out_dir = OUT_ROOT / stem
        prompts = [(n, p) for n, p in prompts_cfg[stem]]
        all_stats[stem] = process_image(model, tokenizer, device, img_path, prompts, out_dir, args.force)

    total = time.time() - total_start
    print(f"\nDone in {total:.1f}s")
    (OUT_ROOT / "stats.json").parent.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "stats.json").write_text(json.dumps(all_stats, indent=2))
    print(f"Stats saved to {OUT_ROOT / 'stats.json'}")


if __name__ == "__main__":
    main()
