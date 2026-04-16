#!/usr/bin/env python3
"""Run SegFormer face-parsing on showcase images.

Detects face region, crops for fine-grained parsing, maps masks back
to original coordinates. Outputs per-part RGBA PNGs.

Complements EVF-SAM (scene-level) with face-part detail (eyes, nose, lips).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor

REPO = Path(__file__).resolve().parent.parent
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
OUT_ROOT = REPO / "assets" / "showcase" / "experiments" / "face_parsing"

# CelebAMask-HQ 19-class label map
LABELS = {
    0: "background", 1: "skin", 2: "nose", 3: "eye_g", 4: "l_eye",
    5: "r_eye", 6: "l_brow", 7: "r_brow", 8: "l_ear", 9: "r_ear",
    10: "mouth", 11: "u_lip", 12: "l_lip", 13: "hair", 14: "hat",
    15: "ear_r", 16: "neck_l", 17: "neck", 18: "cloth",
}

# Merge small symmetric parts into single layers
MERGE_MAP = {
    "l_eye": "eyes", "r_eye": "eyes",
    "l_brow": "eyebrows", "r_brow": "eyebrows",
    "u_lip": "lips", "l_lip": "lips", "mouth": "lips",
    "l_ear": "ears", "r_ear": "ears", "ear_r": "ears",
    "neck_l": "neck",
}

# Face-region classes for bounding-box detection
FACE_CLASSES = {1, 2, 4, 5, 6, 7, 11, 12}  # skin, nose, eyes, brows, lips

# Minimum fraction of pixels that must be "skin" to count as portrait
SKIN_THRESHOLD = 0.03


def load_model(device: str = "mps"):
    """Load SegFormer face-parsing model and processor."""
    print("Loading SegFormer face-parsing model...")
    t0 = time.time()
    processor = SegformerImageProcessor.from_pretrained("jonathandinu/face-parsing")
    model = SegformerForSemanticSegmentation.from_pretrained("jonathandinu/face-parsing")
    model = model.to(device).eval()
    print(f"  Model loaded in {time.time() - t0:.1f}s")
    return model, processor


def segment(model, processor, image: Image.Image, device: str = "mps") -> np.ndarray:
    """Run segmentation, return HxW class map at original image size."""
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        logits = model(**inputs).logits  # (1, C, h, w)
    # Upsample to original size
    upsampled = torch.nn.functional.interpolate(
        logits, size=image.size[::-1], mode="bilinear", align_corners=False,
    )
    seg_map = upsampled.argmax(dim=1).squeeze().cpu().numpy()
    return seg_map


def find_face_bbox(
    seg_map: np.ndarray, padding: float = 0.2,
) -> tuple[int, int, int, int] | None:
    """Find bounding box of face region with padding. Returns (x1, y1, x2, y2) or None."""
    face_mask = np.isin(seg_map, list(FACE_CLASSES))
    if face_mask.sum() < 100:
        return None
    ys, xs = np.where(face_mask)
    y1, y2 = int(ys.min()), int(ys.max())
    x1, x2 = int(xs.min()), int(xs.max())
    h, w = y2 - y1, x2 - x1
    pad_h, pad_w = int(h * padding), int(w * padding)
    H, W = seg_map.shape
    return (
        max(0, x1 - pad_w),
        max(0, y1 - pad_h),
        min(W, x2 + pad_w),
        min(H, y2 + pad_h),
    )


def masks_from_seg_map(seg_map: np.ndarray) -> dict[str, np.ndarray]:
    """Convert class map to dict of merged-name -> bool mask."""
    masks: dict[str, np.ndarray] = {}
    for cls_id, raw_name in LABELS.items():
        if raw_name == "background":
            continue
        merged_name = MERGE_MAP.get(raw_name, raw_name)
        cls_mask = seg_map == cls_id
        if cls_mask.sum() == 0:
            continue
        if merged_name in masks:
            masks[merged_name] = masks[merged_name] | cls_mask
        else:
            masks[merged_name] = cls_mask
    return masks


def save_rgba_layer(
    image: Image.Image, mask: np.ndarray, out_path: Path,
) -> None:
    """Save RGBA PNG where alpha = mask."""
    rgba = image.copy().convert("RGBA")
    alpha = (mask.astype(np.uint8) * 255)
    rgba.putalpha(Image.fromarray(alpha))
    rgba.save(out_path)


def process_image(
    model,
    processor,
    img_path: Path,
    out_dir: Path,
    device: str = "mps",
    force: bool = False,
) -> dict:
    """Full pipeline: detect face, crop, fine-parse, map back, save."""
    slug = img_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check idempotency
    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists() and not force:
        print(f"  [{slug}] Already done, skipping (use --force to redo)")
        return json.loads(manifest_path.read_text())

    image = Image.open(img_path).convert("RGB")
    W, H = image.size
    print(f"  [{slug}] Image size: {W}x{H}")

    # 1. Full-image pass to detect face
    t0 = time.time()
    full_seg = segment(model, processor, image, device)
    t_full = time.time() - t0
    print(f"  [{slug}] Full-image segmentation: {t_full:.2f}s")

    skin_frac = (full_seg == 1).sum() / full_seg.size
    is_portrait = skin_frac > SKIN_THRESHOLD
    print(f"  [{slug}] Skin fraction: {skin_frac:.3f} -> {'PORTRAIT' if is_portrait else 'non-portrait'}")

    if not is_portrait:
        # Use full-image segmentation as-is
        masks = masks_from_seg_map(full_seg)
        strategy = "full-image"
    else:
        # 2. Find face bbox and crop
        bbox = find_face_bbox(full_seg)
        if bbox is None:
            masks = masks_from_seg_map(full_seg)
            strategy = "full-image (bbox failed)"
        else:
            x1, y1, x2, y2 = bbox
            print(f"  [{slug}] Face bbox: ({x1},{y1})-({x2},{y2})")
            crop = image.crop((x1, y1, x2, y2))

            # 3. Re-run face-parsing on the crop
            t0 = time.time()
            crop_seg = segment(model, processor, crop, device)
            t_crop = time.time() - t0
            print(f"  [{slug}] Crop segmentation: {t_crop:.2f}s")

            # 4. Map crop masks back to original coordinates
            crop_masks = masks_from_seg_map(crop_seg)
            masks = {}
            for name, cmask in crop_masks.items():
                full_mask = np.zeros((H, W), dtype=bool)
                full_mask[y1:y1 + cmask.shape[0], x1:x1 + cmask.shape[1]] = cmask
                masks[name] = full_mask

            # Also include full-image classes not in the crop (hair, cloth, etc.)
            full_masks = masks_from_seg_map(full_seg)
            for name, fmask in full_masks.items():
                if name not in masks:
                    masks[name] = fmask

            strategy = "crop-refine"

    # 5. Save RGBA PNGs
    layers = []
    for name, mask in sorted(masks.items()):
        px_count = int(mask.sum())
        if px_count < 50:
            continue
        fname = f"{name}.png"
        save_rgba_layer(image, mask, out_dir / fname)
        layers.append({
            "name": name,
            "file": fname,
            "pixels": px_count,
            "fraction": round(px_count / (H * W), 4),
        })
        print(f"    {name}: {px_count:,} px ({layers[-1]['fraction']:.3%})")

    manifest = {
        "slug": slug,
        "source": str(img_path.relative_to(REPO)),
        "strategy": strategy,
        "image_size": [W, H],
        "is_portrait": bool(is_portrait),
        "skin_fraction": round(float(skin_frac), 4),
        "layers": layers,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"  [{slug}] Saved {len(layers)} layers -> {out_dir}")
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Run SegFormer face-parsing on showcase images.",
    )
    parser.add_argument(
        "--images",
        help="Comma-separated slugs (default: all originals)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing outputs",
    )
    parser.add_argument(
        "--device", default="mps",
        help="Torch device (default: mps)",
    )
    args = parser.parse_args()

    # Resolve image list
    if args.images:
        slugs = [s.strip() for s in args.images.split(",")]
        img_paths = []
        for slug in slugs:
            p = ORIG_DIR / f"{slug}.jpg"
            if not p.exists():
                print(f"ERROR: {p} not found", file=sys.stderr)
                sys.exit(1)
            img_paths.append(p)
    else:
        img_paths = sorted(ORIG_DIR.glob("*.jpg"))
        if not img_paths:
            print(f"ERROR: no images in {ORIG_DIR}", file=sys.stderr)
            sys.exit(1)

    print(f"Processing {len(img_paths)} image(s) with device={args.device}")

    model, processor = load_model(args.device)

    results = []
    for img_path in img_paths:
        t0 = time.time()
        manifest = process_image(
            model, processor, img_path,
            OUT_ROOT / img_path.stem,
            device=args.device, force=args.force,
        )
        results.append(manifest)
        elapsed = time.time() - t0
        print(f"  [{img_path.stem}] Total: {elapsed:.1f}s")
        # Free MPS cache between images
        if args.device == "mps":
            torch.mps.empty_cache()

    print(f"\nDone. {len(results)} image(s) processed.")


if __name__ == "__main__":
    main()
