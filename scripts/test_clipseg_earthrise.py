#!/usr/bin/env python3
"""Test CLIPSeg text-prompted segmentation on Earthrise."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation

REPO = Path(__file__).resolve().parent.parent
IMG = REPO / "assets" / "showcase" / "originals" / "earthrise.jpg"
OUT = REPO / "assets" / "showcase" / "experiments"


def main():
    print("Loading CLIPSeg model...")
    t0 = time.time()
    processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
    model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined")

    # Use MPS if available
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = model.to(device)
    print(f"Model loaded in {time.time()-t0:.1f}s (device: {device})")

    img = Image.open(IMG).convert("RGB")
    w, h = img.size
    print(f"Image: {w}x{h}")

    # Text prompts for each semantic layer
    labels = [
        "deep black outer space void",
        "blue planet Earth with white clouds",
        "gray rocky lunar surface terrain",
    ]
    layer_names = ["deep_space_background", "earth_planet", "foreground_lunar_surface"]

    print(f"\nRunning CLIPSeg with labels: {labels}")
    t1 = time.time()

    inputs = processor(
        text=labels,
        images=[img] * len(labels),
        return_tensors="pt",
        padding=True,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    # outputs.logits: [N, 352, 352] — per-class logit maps
    logits = outputs.logits.cpu()  # [3, 352, 352]
    probs = torch.sigmoid(logits)  # per-class probabilities

    print(f"Inference: {time.time()-t1:.1f}s")
    print(f"Output shape: {logits.shape}")

    # Upscale to original resolution
    probs_up = torch.nn.functional.interpolate(
        probs.unsqueeze(0),  # [1, 3, 352, 352]
        size=(h, w),
        mode="bilinear",
        align_corners=False,
    ).squeeze(0)  # [3, H, W]

    probs_np = probs_up.numpy()  # [3, H, W]

    # Method 1: Argmax — assign each pixel to highest-probability class
    argmax = np.argmax(probs_np, axis=0)  # [H, W]

    # Method 2: Threshold — per-class binary mask at 0.5
    # (allows overlap, then resolve by argmax)

    # Save per-class masks and layers
    out_dir = OUT / "CLIPSeg"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, (name, label) in enumerate(zip(layer_names, labels)):
        # Argmax mask
        mask = (argmax == i).astype(np.uint8) * 255
        mask_img = Image.fromarray(mask, mode="L")

        # Apply mask to original image
        rgba = img.convert("RGBA")
        r, g, b, _ = rgba.split()
        layer = Image.merge("RGBA", (r, g, b, mask_img))
        layer.save(str(out_dir / f"{name}.png"))

        # Stats
        pct = mask.sum() / 255 / (h * w) * 100
        prob_mean = probs_np[i][mask > 127].mean() if (mask > 127).any() else 0
        print(f"\n{name} ({label}):")
        print(f"  Coverage: {pct:.1f}%")
        print(f"  Mean probability in mask: {prob_mean:.3f}")

        # Save probability heatmap
        prob_vis = (probs_np[i] * 255).astype(np.uint8)
        Image.fromarray(prob_vis, mode="L").save(str(out_dir / f"{name}_prob.png"))

    # Check Earth region leak in lunar surface
    lunar_mask = (argmax == 2).astype(np.uint8) * 255
    earth_region = lunar_mask[int(h*0.35):int(h*0.55), :]
    leak = (earth_region > 127).sum()
    total_lunar = (lunar_mask > 127).sum()
    print(f"\n--- Leak Analysis ---")
    print(f"Lunar surface pixels in Earth region: {leak:,} ({leak/max(total_lunar,1)*100:.2f}%)")

    print(f"\nSaved to {out_dir}/")


if __name__ == "__main__":
    main()
