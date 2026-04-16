#!/usr/bin/env python3
"""Merge EVF-SAM scene layers + SegFormer face-parsing layers into final output.

For portrait images: replaces the coarse head_and_face EVF-SAM layer with
fine-grained face parts (eyes, nose, lips, skin, hair, eyebrows) from
face-parsing. Non-portrait images keep EVF-SAM layers unchanged.

Output: assets/showcase/layers/<slug>/ with merged manifest + layer PNGs.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
EVFSAM_LAYERS = REPO / "assets" / "showcase" / "layers"
FACE_PARSING = REPO / "assets" / "showcase" / "experiments" / "face_parsing"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
OUT_DIR = REPO / "assets" / "showcase" / "layers"  # overwrite in-place

# Face-parsing parts that replace "head_and_face" EVF-SAM layer
FACE_PARTS = {"skin", "eyes", "eyebrows", "nose", "lips", "hair", "neck", "ears", "hat", "cloth"}

# Minimum pixel count for a face part to be its own layer.
# Below this, pixels are merged into the "skin" layer (parent).
# Key parts (eyes, nose, lips) are NEVER merged regardless of size.
MIN_PART_PIXELS = 500
NEVER_MERGE = {"eyes", "nose", "lips", "skin", "hair"}

# semantic_path for face parts
FACE_SP = {
    "skin": "subject.head.face",
    "eyes": "subject.head.face.eyes",
    "eyebrows": "subject.head.face.eyebrows",
    "nose": "subject.head.face.nose",
    "lips": "subject.head.face.lips",
    "hair": "subject.head.hair",
    "neck": "subject.body.neck",
    "ears": "subject.head.ears",
    "hat": "subject.head.hat",
    "cloth": "subject.body.clothing",
}

# z-index for face parts (higher = wins overlap)
FACE_Z = {
    "hair": 58,
    "hat": 57,
    "cloth": 53,
    "neck": 52,
    "skin": 60,
    "ears": 62,
    "eyebrows": 68,
    "eyes": 70,
    "nose": 70,
    "lips": 70,
}


def has_face_parsing(slug: str) -> bool:
    d = FACE_PARSING / slug
    return d.exists() and any(d.glob("*.png"))


def merge_image(slug: str, force: bool = False) -> None:
    evfsam_manifest_path = EVFSAM_LAYERS / slug / "manifest.json"
    if not evfsam_manifest_path.exists():
        print(f"SKIP {slug}: no EVF-SAM manifest")
        return

    evfsam_manifest = json.loads(evfsam_manifest_path.read_text())
    fp_dir = FACE_PARSING / slug

    if not has_face_parsing(slug):
        print(f"KEEP {slug}: no face-parsing data, EVF-SAM only ({len(evfsam_manifest['layers'])} layers)")
        return

    # Find the head_and_face layer to replace
    head_layer = None
    other_layers = []
    for layer in evfsam_manifest["layers"]:
        if layer["name"] in ("head_and_face", "face_skin") or "head" in layer.get("semantic_path", ""):
            head_layer = layer
        else:
            other_layers.append(layer)

    if head_layer is None:
        print(f"KEEP {slug}: no head layer found in EVF-SAM, keeping as-is")
        return

    # Load the head mask from EVF-SAM (this is the region face parts should fill)
    head_mask_path = EVFSAM_LAYERS / slug / head_layer["file"]
    head_rgba = np.array(Image.open(head_mask_path))
    head_mask = head_rgba[:, :, 3] > 10  # bool HxW
    H, W = head_mask.shape

    # Load face-parsing parts
    orig_img = Image.open(ORIG_DIR / f"{slug}.jpg").convert("RGB")
    orig_np = np.array(orig_img)

    face_layers = []
    face_claimed = np.zeros((H, W), dtype=bool)
    skin_extra = np.zeros((H, W), dtype=bool)  # tiny parts merged into skin

    # Sort by z descending so higher-z parts claim first
    fp_parts = []
    for png in sorted(fp_dir.glob("*.png")):
        name = png.stem
        if name not in FACE_PARTS:
            continue
        fp_parts.append((name, png))

    fp_parts.sort(key=lambda x: -FACE_Z.get(x[0], 50))

    # First pass: collect all constrained masks and decide what's too small
    part_masks: dict[str, np.ndarray] = {}
    for name, png in fp_parts:
        fp_rgba = np.array(Image.open(png))
        fp_mask = fp_rgba[:, :, 3] > 10
        constrained = fp_mask & head_mask & ~face_claimed
        if constrained.sum() < 10:
            continue
        face_claimed |= constrained
        part_masks[name] = constrained

    # Second pass: merge tiny NON-KEY parts into skin
    for name, mask in list(part_masks.items()):
        if name in NEVER_MERGE:
            continue
        if mask.sum() < MIN_PART_PIXELS:
            print(f"  MERGE {name} ({mask.sum()} px) -> skin (below {MIN_PART_PIXELS} threshold)")
            skin_extra |= mask
            del part_masks[name]

    # Add merged pixels to skin
    if "skin" in part_masks:
        part_masks["skin"] = part_masks["skin"] | skin_extra
    elif skin_extra.any():
        part_masks["skin"] = skin_extra

    # Save surviving parts
    for name, mask in part_masks.items():
        mask_u8 = (mask * 255).astype(np.uint8)
        layer_rgba = np.dstack([orig_np, mask_u8])
        out_path = OUT_DIR / slug / f"{name}.png"
        Image.fromarray(layer_rgba).save(str(out_path))

        layer_id = "layer_" + hashlib.md5(f"{slug}-{name}".encode()).hexdigest()[:8]
        face_layers.append({
            "id": layer_id,
            "name": name,
            "description": f"face part: {name}",
            "z_index": FACE_Z.get(name, 60),
            "blend_mode": "normal",
            "content_type": name,
            "semantic_path": FACE_SP.get(name, f"subject.head.{name}"),
            "visible": True,
            "locked": False,
            "file": f"{name}.png",
            "dominant_colors": [],
            "regeneration_prompt": "",
            "opacity": 1.0,
            "x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0,
            "rotation": 0.0,
            "content_bbox": None,
            "position": "",
            "coverage": "",
        })

    # Remaining head pixels (not claimed by face parts) become "head_remainder"
    remainder = head_mask & ~face_claimed
    if remainder.sum() > 100:
        mask_u8 = (remainder * 255).astype(np.uint8)
        layer_rgba = np.dstack([orig_np, mask_u8])
        out_path = OUT_DIR / slug / "head_remainder.png"
        Image.fromarray(layer_rgba).save(str(out_path))

        layer_id = "layer_" + hashlib.md5(f"{slug}-head_remainder".encode()).hexdigest()[:8]
        face_layers.append({
            "id": layer_id,
            "name": "head_remainder",
            "description": "remaining head pixels not covered by face parts",
            "z_index": 55,
            "blend_mode": "normal",
            "content_type": "head_remainder",
            "semantic_path": "subject.head.other",
            "visible": True,
            "locked": False,
            "file": "head_remainder.png",
            "dominant_colors": [],
            "regeneration_prompt": "",
            "opacity": 1.0,
            "x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0,
            "rotation": 0.0,
            "content_bbox": None,
            "position": "",
            "coverage": "",
        })

    # Remove old head_and_face PNG
    old_head_png = OUT_DIR / slug / head_layer["file"]
    if old_head_png.exists():
        old_head_png.unlink()

    # Build merged manifest
    merged_layers = other_layers + sorted(face_layers, key=lambda l: l["z_index"])
    evfsam_manifest["layers"] = merged_layers
    evfsam_manifest["split_mode"] = "hybrid_evfsam_faceparse"
    evfsam_manifest["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest_path = OUT_DIR / slug / "manifest.json"
    manifest_path.write_text(json.dumps(evfsam_manifest, indent=2, ensure_ascii=False))

    scene_count = len(other_layers)
    face_count = len(face_layers)
    print(f"OK  {slug}: {scene_count} scene + {face_count} face = {scene_count + face_count} total layers")


def main():
    slugs = sys.argv[1:] if len(sys.argv) > 1 else None

    if slugs is None:
        # Process all that have face-parsing data
        slugs = [d.name for d in FACE_PARSING.iterdir() if d.is_dir()]

    for slug in sorted(slugs):
        merge_image(slug)


if __name__ == "__main__":
    main()
