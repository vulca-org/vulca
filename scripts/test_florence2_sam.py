#!/usr/bin/env python3
"""Test Florence-2 + SAM 2 for pixel-perfect text-prompted segmentation."""
from __future__ import annotations

import time
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from PIL import ImageDraw
from transformers import AutoProcessor, AutoModelForCausalLM

REPO = Path(__file__).resolve().parent.parent
IMG = REPO / "assets" / "showcase" / "originals" / "earthrise.jpg"
OUT = REPO / "assets" / "showcase" / "experiments" / "J_florence2"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Device: {device}")

    print("Loading Florence-2-base...")  # use base first (0.2B) for speed
    t0 = time.time()
    proc = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Florence-2-base",
        torch_dtype=torch.float32,
        trust_remote_code=True,
    ).to(device).eval()
    print(f"Loaded in {time.time()-t0:.1f}s")

    img = Image.open(IMG).convert("RGB")
    w, h = img.size

    # Florence-2 <REFERRING_EXPRESSION_SEGMENTATION> returns polygons
    # Try it for each prompt
    prompts = {
        "earth_planet": "the blue planet Earth",
        "foreground_lunar_surface": "the gray lunar surface at the bottom",
    }

    task = "<REFERRING_EXPRESSION_SEGMENTATION>"

    for name, text in prompts.items():
        print(f"\n{name}: '{text}'")
        t0 = time.time()
        inputs = proc(text=task + text, images=img, return_tensors="pt").to(device)

        with torch.no_grad():
            gen = model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                num_beams=3,
                do_sample=False,
            )

        parsed = proc.post_process_generation(
            proc.batch_decode(gen, skip_special_tokens=False)[0],
            task=task,
            image_size=(w, h),
        )
        elapsed = time.time() - t0
        print(f"  Inference: {elapsed:.1f}s")
        print(f"  Raw parsed keys: {list(parsed.keys())}")

        # Florence-2 returns polygons
        if task in parsed:
            result = parsed[task]
            polygons = result.get("polygons", [])
            labels = result.get("labels", [])
            print(f"  Polygons: {len(polygons)} instance(s)")

            mask_img = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(mask_img)

            for poly_group in polygons:
                # poly_group is list of polygons for one instance
                for poly in poly_group:
                    # poly is flat list [x1,y1,x2,y2,...]
                    if len(poly) >= 6:
                        points = [(poly[i], poly[i+1]) for i in range(0, len(poly), 2)]
                        draw.polygon(points, fill=255)

            mask = np.array(mask_img)
            pct = (mask > 127).sum() / (h*w) * 100
            print(f"  Coverage: {pct:.1f}%")

            # Save layer
            rgba = img.convert("RGBA")
            r, g, b, _ = rgba.split()
            mask_pil = Image.fromarray(mask, mode="L")
            layer = Image.merge("RGBA", (r, g, b, mask_pil))
            layer.save(str(OUT / f"{name}.png"))

            arr = np.array(layer)
            mask_bool = arr[:,:,3] > 10
            red = np.full_like(arr, [255, 0, 0, 255])
            red = np.where(mask_bool[..., None], arr, red)
            Image.fromarray(red).save(str(OUT / f"{name}_on_red.png"))

    # Background — only computed if both layer files exist
    earth_path = OUT / "earth_planet.png"
    lunar_path = OUT / "foreground_lunar_surface.png"
    if not (earth_path.exists() and lunar_path.exists()):
        print(f"\nSkip background: missing layer files")
        print(f"Saved to {OUT}/")
        return
    earth_a = np.array(Image.open(str(earth_path)))[:,:,3] > 10
    lunar_a = np.array(Image.open(str(lunar_path)))[:,:,3] > 10
    bg = ~(earth_a | lunar_a)
    bg_img = Image.fromarray((bg * 255).astype(np.uint8), mode="L")
    rgba = img.convert("RGBA")
    r, g, b, _ = rgba.split()
    Image.merge("RGBA", (r, g, b, bg_img)).save(str(OUT / "deep_space_background.png"))
    arr = np.array(Image.merge("RGBA", (r, g, b, bg_img)))
    mask_bool = arr[:,:,3] > 10
    red = np.full_like(arr, [255, 0, 0, 255])
    red = np.where(mask_bool[..., None], arr, red)
    Image.fromarray(red).save(str(OUT / "deep_space_background_on_red.png"))

    # Stats
    ea = np.array(Image.open(str(OUT / "earth_planet.png")))
    eo = ea[:,:,3] > 10
    img_np = np.array(img)
    if eo.any():
        dark = (img_np[eo].mean(axis=1) < 30).sum()
        print(f"\nEarth dark pixels: {dark:,} / {eo.sum():,} ({dark/eo.sum()*100:.1f}%)")

    print(f"\nSaved to {OUT}/")


if __name__ == "__main__":
    main()
