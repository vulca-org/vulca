#!/usr/bin/env python3
"""Tile-based EVF-SAM inference for extreme-aspect images (e.g., Chinese scrolls).

Problem: EVF-SAM preprocesses to 1024 square; a 2560x120 scroll becomes 1024x48,
losing 96% of vertical resolution. Solution: slice overlapping square tiles along
the long axis, run inference per tile, stitch masks with UNION semantics (any
tile that says "yes" for a pixel wins). Using union not average because average
+ threshold=0.5 rejects pixels voted "yes" by only one of two overlapping tiles,
dropping subject parts visible only in one tile.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

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
PROMPTS = REPO / "assets" / "showcase" / "experiments" / "evfsam_prompts.json"
OUT_ROOT = REPO / "assets" / "showcase" / "experiments" / "evfsam_all"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"


def infer_tile(model, tokenizer, device, tile_np: np.ndarray, prompt: str) -> np.ndarray:
    th, tw = tile_np.shape[:2]
    image_beit = beit3_preprocess(tile_np, 224).to(dtype=model.dtype, device=device)
    image_sam, resize_shape = sam_preprocess(tile_np)
    image_sam = image_sam.to(dtype=model.dtype, device=device)
    input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"].to(device=device)
    with torch.no_grad():
        pred = model.inference(
            image_sam.unsqueeze(0),
            image_beit.unsqueeze(0),
            input_ids,
            resize_list=[resize_shape],
            original_size_list=[(th, tw)],
        )
    return pred.detach().cpu().numpy()[0] > 0


def compute_x_offsets(width: int, tile_size: int, overlap: int) -> list[int]:
    """Compute starting x coordinates for sliding tile window. Guarantees coverage."""
    stride = max(tile_size - overlap, 1)  # avoid zero/negative stride
    if width <= tile_size:
        return [0]
    xs = list(range(0, width - tile_size + 1, stride))
    if xs[-1] + tile_size < width:
        xs.append(width - tile_size)
    return xs


def tile_infer(model, tokenizer, device, img_path: Path, prompts: list[tuple[str, str]],
               out_dir: Path, tile_size: int = 1024, overlap: int = 128):
    image_np, _ = imread_rgb(img_path, max_dim=4096)
    h, w = image_np.shape[:2]
    print(f"  Source: {w}x{h}, tile={tile_size}, overlap={overlap}")

    if h < tile_size:
        tile_size = h
        print(f"  Adjusted tile_size to {tile_size} (image height)")

    xs = compute_x_offsets(w, tile_size, overlap)
    print(f"  Tiles: {len(xs)} at x-offsets {xs[:5]}{'...' if len(xs) > 5 else ''}")

    out_dir.mkdir(parents=True, exist_ok=True)
    orig_rgba = Image.fromarray(image_np).convert("RGBA")
    r_ch, g_ch, b_ch, _ = orig_rgba.split()

    for layer_name, prompt in prompts:
        t0 = time.time()
        # UNION semantics: any tile voting yes wins
        merged = np.zeros((h, w), dtype=bool)

        for x_off in xs:
            tile = image_np[:, x_off:x_off + tile_size]
            mask_tile = infer_tile(model, tokenizer, device, tile, prompt)
            merged[:, x_off:x_off + tile_size] |= mask_tile

        binary = (merged * 255).astype(np.uint8)
        mask_pil = Image.fromarray(binary, mode="L")
        layer = Image.merge("RGBA", (r_ch, g_ch, b_ch, mask_pil))
        layer.save(str(out_dir / f"{layer_name}.png"))

        arr = np.array(layer)
        Image.fromarray(compose_red_bg(arr)).save(str(out_dir / f"{layer_name}_on_red.png"))

        pct = merged.sum() / (h * w) * 100
        print(f"  [{layer_name}] {pct:.1f}% coverage, {time.time()-t0:.1f}s ({len(xs)} tiles)")

        if device == "mps":
            torch.mps.empty_cache()


def main():
    prompts = json.loads(PROMPTS.read_text())
    if "qingming-bridge" not in prompts:
        print("qingming-bridge not in prompts")
        return

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    tokenizer, model = load_evfsam(device)

    img_path = ORIG_DIR / "qingming-bridge.jpg"
    out_dir = OUT_ROOT / "qingming-bridge"
    print(f"\n[qingming-bridge tile inference]")
    tile_infer(model, tokenizer, device, img_path,
               prompts["qingming-bridge"], out_dir,
               tile_size=256, overlap=64)
    print("Done")


if __name__ == "__main__":
    main()
