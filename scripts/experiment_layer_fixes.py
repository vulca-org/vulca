#!/usr/bin/env python3
"""Experiment: 4 approaches to fix foreground/subject pixel leakage in extract mode.

Problem: Earthrise foreground (lunar surface) leaks gray pixels into the Earth region
because both share similar gray tones. The color-range mask can't distinguish them.

Approaches:
  A. Spatial bbox from VLM analysis (simulated with manual bbox for experiment)
  B. Spatial weight decay: foreground layers get lower weight in upper image regions
  C. Post-process: subject mask takes priority over foreground where they overlap
  D. Content-type priority: subject layers claim pixels before foreground layers

Usage:
    python scripts/experiment_layer_fixes.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.mask import build_color_mask, apply_mask_to_image
from vulca.layers.types import LayerInfo

REPO = Path(__file__).resolve().parent.parent
IMG_PATH = REPO / "assets" / "showcase" / "originals" / "earthrise.jpg"
MANIFEST = REPO / "assets" / "showcase" / "layers" / "earthrise" / "manifest.json"
EXP_ROOT = REPO / "assets" / "showcase" / "experiments"


def load_layers() -> list[LayerInfo]:
    m = json.loads(MANIFEST.read_text())
    layers = []
    for l in m["layers"]:
        info = l.get("info", l)
        layers.append(LayerInfo(
            name=info["name"],
            description=info.get("description", ""),
            z_index=info["z_index"],
            content_type=info["content_type"],
            dominant_colors=info.get("dominant_colors", []),
        ))
    return layers


def measure_leak(fg_mask: np.ndarray, h: int) -> dict:
    """Measure how many foreground pixels leak into the Earth region (35-55% height)."""
    earth_start, earth_end = int(h * 0.35), int(h * 0.55)
    total_opaque = (fg_mask > 127).sum()
    earth_leak = (fg_mask[earth_start:earth_end] > 127).sum()
    return {
        "total_opaque": int(total_opaque),
        "earth_leak": int(earth_leak),
        "leak_pct": round(earth_leak / max(total_opaque, 1) * 100, 2),
    }


def run_baseline(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """Current behavior: pure z_index ordering, foreground first."""
    h, w = img.size[1], img.size[0]
    assigned = np.zeros((h, w), dtype=bool)
    masks = {}

    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        mask = build_color_mask(img, info, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask)
        assigned |= (mask_arr > 127)
        masks[info.name] = mask

    save_layers(img, layers, masks, out_dir, "baseline")
    fg_name = [l.name for l in layers if l.content_type == "foreground"][0]
    return measure_leak(np.array(masks[fg_name]), h)


def run_approach_A(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """A: Spatial bbox constraint — foreground only in bottom 40%, subject in middle 30%."""
    h, w = img.size[1], img.size[0]
    assigned = np.zeros((h, w), dtype=bool)
    masks = {}

    # Define spatial regions per content_type
    spatial_masks = {
        "foreground": np.zeros((h, w), dtype=bool),
        "subject": np.zeros((h, w), dtype=bool),
        "background": np.ones((h, w), dtype=bool),
    }
    spatial_masks["foreground"][int(h * 0.6):, :] = True   # bottom 40%
    spatial_masks["subject"][int(h * 0.3):int(h * 0.6), :] = True  # middle 30%

    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        mask = build_color_mask(img, info, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask).astype(np.float32)
        # Apply spatial constraint
        spatial = spatial_masks.get(info.content_type, np.ones((h, w), dtype=bool))
        mask_arr[~spatial] = 0
        assigned |= (mask_arr > 127)
        masks[info.name] = Image.fromarray(mask_arr.astype(np.uint8), mode="L")

    save_layers(img, layers, masks, out_dir, "A_bbox")
    fg_name = [l.name for l in layers if l.content_type == "foreground"][0]
    return measure_leak(np.array(masks[fg_name]), h)


def run_approach_B(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """B: Spatial weight decay — foreground weight fades to 0 toward top of image."""
    h, w = img.size[1], img.size[0]
    assigned = np.zeros((h, w), dtype=bool)
    masks = {}

    # Weight gradient: 0 at top, 1 at bottom
    y_weight = np.linspace(0, 1, h).reshape(-1, 1)  # H x 1

    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        mask = build_color_mask(img, info, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask).astype(np.float32)
        if info.content_type == "foreground":
            mask_arr *= y_weight
        # Binarize to avoid ghost-translucent pixels that hide from measure_leak's >127 check
        mask_bin = (mask_arr > 127).astype(np.uint8) * 255
        assigned |= (mask_bin > 127)
        masks[info.name] = Image.fromarray(mask_bin, mode="L")

    save_layers(img, layers, masks, out_dir, "B_spatial_weight")
    fg_name = [l.name for l in layers if l.content_type == "foreground"][0]
    return measure_leak(np.array(masks[fg_name]), h)


def run_approach_C(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """C: Post-process — where foreground and subject masks overlap, subject wins.

    Each layer's mask is built INDEPENDENTLY (no assigned accumulator), so
    overlap between subject and foreground actually exists and can be resolved.
    """
    h, w = img.size[1], img.size[0]
    masks = {}

    # Build each layer's raw color mask independently (no exclusive ownership yet)
    for info in layers:
        mask = build_color_mask(img, info, tolerance=30, assigned=None)
        masks[info.name] = np.array(mask)

    # Post-process: where subject and foreground overlap, subject wins
    subject_names = [l.name for l in layers if l.content_type == "subject"]
    fg_names = [l.name for l in layers if l.content_type == "foreground"]

    for sn in subject_names:
        for fn in fg_names:
            overlap = (masks[sn] > 127) & (masks[fn] > 127)
            if overlap.any():
                masks[fn][overlap] = 0  # Subject wins

    pil_masks = {k: Image.fromarray(v, mode="L") for k, v in masks.items()}
    save_layers(img, layers, pil_masks, out_dir, "C_post_mask")
    return measure_leak(masks[fg_names[0]], h)


def run_approach_D(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """D: Content-type priority — subject claims pixels before foreground."""
    h, w = img.size[1], img.size[0]
    assigned = np.zeros((h, w), dtype=bool)
    masks = {}

    # Priority: subject (0) first, then foreground (1), detail, atmosphere, background last.
    # Ascending sort puts lower priority number first = processed first = claims pixels first.
    type_priority = {"subject": 0, "foreground": 1, "detail": 2,
                     "atmosphere": 3, "background": 99}

    def sort_key(l):
        return (type_priority.get(l.content_type, 50), -l.z_index)

    for info in sorted(layers, key=sort_key):
        mask = build_color_mask(img, info, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask)
        assigned |= (mask_arr > 127)
        masks[info.name] = mask

    save_layers(img, layers, masks, out_dir, "D_priority")
    fg_name = [l.name for l in layers if l.content_type == "foreground"][0]
    return measure_leak(np.array(masks[fg_name]), h)


def _connected_component_filter(mask_arr: np.ndarray, keep_top_n: int = 1,
                                  min_pct: float = 0.05) -> np.ndarray:
    """Keep only the largest N connected components, discard small fragments.

    Earthrise assumes a single-object foreground (the moon). For images with
    multiple foreground objects, keep_top_n should be raised.

    Args:
        mask_arr: uint8 mask array (0 or 255).
        keep_top_n: Keep at most this many largest components.
        min_pct: Also keep any component with >= this fraction of total opaque pixels.

    Returns:
        Filtered uint8 mask array.
    """
    import cv2
    binary = (mask_arr > 127).astype(np.uint8)
    if not binary.any():
        return mask_arr

    # 4-connectivity, stats in one C call
    num, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=4)
    if num <= 1:
        return mask_arr

    # Component 0 is background; areas from component 1 onward
    areas = stats[1:, cv2.CC_STAT_AREA]
    total = int(areas.sum())

    # Keep top-N largest + any component >= min_pct of total
    order = np.argsort(areas)[::-1]
    keep_idx = set(order[:keep_top_n].tolist())
    keep_idx.update(int(i) for i in np.where(areas / total >= min_pct)[0])
    keep_labels = np.array(sorted(i + 1 for i in keep_idx), dtype=np.int32)

    filtered = np.isin(labels, keep_labels)
    result = mask_arr.copy()
    result[~filtered] = 0
    return result


def run_approach_E(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """E: Connected component filtering — foreground only, keep largest region."""
    h, w = img.size[1], img.size[0]
    assigned = np.zeros((h, w), dtype=bool)
    masks = {}

    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        mask = build_color_mask(img, info, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask)
        # Only filter foreground layers — subject may have small but important regions
        if info.content_type == "foreground":
            mask_arr = _connected_component_filter(mask_arr, keep_top_n=1)
        assigned |= (mask_arr > 127)
        masks[info.name] = Image.fromarray(mask_arr, mode="L")

    save_layers(img, layers, masks, out_dir, "E_connected")
    fg_name = [l.name for l in layers if l.content_type == "foreground"][0]
    return measure_leak(np.array(masks[fg_name]), h)


def run_approach_F(img: Image.Image, layers: list[LayerInfo], out_dir: Path):
    """F: Combined — connected component filter (fg only) + spatial weight."""
    h, w = img.size[1], img.size[0]
    assigned = np.zeros((h, w), dtype=bool)
    masks = {}

    y_weight = np.linspace(0, 1, h).reshape(-1, 1)

    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        mask = build_color_mask(img, info, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask).astype(np.float32)
        if info.content_type == "foreground":
            mask_arr *= y_weight
        # Binarize before CC filter + assigned update (keeps consistent with measure_leak's >127 threshold)
        mask_bin = (mask_arr > 127).astype(np.uint8) * 255
        if info.content_type == "foreground":
            mask_bin = _connected_component_filter(mask_bin, keep_top_n=1)
        assigned |= (mask_bin > 127)
        masks[info.name] = Image.fromarray(mask_bin, mode="L")

    save_layers(img, layers, masks, out_dir, "F_combined")
    fg_name = [l.name for l in layers if l.content_type == "foreground"][0]
    return measure_leak(np.array(masks[fg_name]), h)


def save_layers(img, layers, masks, out_dir, label):
    d = out_dir / label
    d.mkdir(parents=True, exist_ok=True)
    for info in layers:
        mask = masks[info.name]
        layer_img = apply_mask_to_image(img, mask)
        layer_img.save(str(d / f"{info.name}.png"))


def main():
    img = Image.open(IMG_PATH)
    layers = load_layers()

    print("Running 7 experiments on Earthrise...\n")

    results = {}
    results["baseline"] = run_baseline(img, layers, EXP_ROOT)
    results["A_bbox"] = run_approach_A(img, layers, EXP_ROOT)
    results["B_spatial_weight"] = run_approach_B(img, layers, EXP_ROOT)
    results["C_post_mask"] = run_approach_C(img, layers, EXP_ROOT)
    results["D_priority"] = run_approach_D(img, layers, EXP_ROOT)
    results["E_connected"] = run_approach_E(img, layers, EXP_ROOT)
    results["F_combined"] = run_approach_F(img, layers, EXP_ROOT)

    print(f"{'Approach':<20} {'Total opaque':>14} {'Earth leak':>12} {'Leak %':>8}")
    print("-" * 58)
    for name, r in results.items():
        print(f"{name:<20} {r['total_opaque']:>14,} {r['earth_leak']:>12,} {r['leak_pct']:>7.2f}%")

    # Save results JSON
    (EXP_ROOT / "results.json").write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {EXP_ROOT / 'results.json'}")
    print(f"Layer PNGs saved to {EXP_ROOT}/{{baseline,A_bbox,...}}/")


if __name__ == "__main__":
    main()
