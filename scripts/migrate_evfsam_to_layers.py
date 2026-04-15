#!/usr/bin/env python3
"""Migrate EVF-SAM experimental outputs into Vulca's layer pipeline.

Replaces assets/showcase/layers/<stem>/ with EVF-SAM outputs from
assets/showcase/experiments/evfsam_all/<stem>/, writing a compatible manifest.json
so downstream caps (composite, re-evaluate) work unchanged.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / "assets" / "showcase" / "experiments" / "evfsam_all"
LAYERS = REPO / "assets" / "showcase" / "layers"
ORIG = REPO / "assets" / "showcase" / "originals"
PROMPTS = REPO / "assets" / "showcase" / "experiments" / "evfsam_prompts.json"

Z_INDEX = {"background": 0, "subject": 1, "foreground": 2}


def _z_index_for(layer_name: str) -> int:
    """Lookup z_index; default to 99 for unknown layer types."""
    return Z_INDEX.get(layer_name, 99)


def make_manifest(stem: str, prompts: list[tuple[str, str]]) -> dict:
    orig_path = ORIG / f"{stem}.jpg"
    im = Image.open(orig_path)
    w, h = im.size

    layers = []
    for layer_name, prompt in prompts:
        layer_id = "layer_" + hashlib.md5(f"{stem}-{layer_name}".encode()).hexdigest()[:8]
        layers.append({
            "id": layer_id,
            "name": layer_name,
            "description": prompt,
            "z_index": _z_index_for(layer_name),
            "blend_mode": "normal",
            "content_type": layer_name,
            "visible": True,
            "locked": False,
            "file": f"{layer_name}.png",
            "dominant_colors": [],
            "regeneration_prompt": prompt,
            "opacity": 1.0,
            "x": 0.0, "y": 0.0,
            "width": 100.0, "height": 100.0,
            "rotation": 0.0,
            "content_bbox": None,
            "position": "",
            "coverage": "",
        })

    return {
        "version": 3,
        "width": w,
        "height": h,
        "source_image": str(orig_path.relative_to(REPO)),
        "split_mode": "evfsam",
        "generation_path": "",
        "layerability": "",
        "tradition": "",
        "partial": False,
        "warnings": [],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layers": layers,
    }


def main():
    prompts_cfg = json.loads(PROMPTS.read_text())
    migrated = []
    skipped = []

    for stem, prompts in prompts_cfg.items():
        if not prompts:
            print(f"SKIP {stem}: empty prompt list")
            skipped.append(stem)
            continue
        src = EXP / stem
        dst = LAYERS / stem

        # Only migrate if EVF-SAM output exists
        expected = [src / f"{name}.png" for name, _ in prompts]
        if not all(p.exists() for p in expected):
            print(f"SKIP {stem}: missing EVF-SAM layers")
            skipped.append(stem)
            continue

        # Backup old extract-mode layers
        if dst.exists():
            backup = LAYERS.parent / f"layers_extract_backup" / stem
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                shutil.rmtree(backup)
            shutil.move(str(dst), str(backup))

        dst.mkdir(parents=True, exist_ok=True)

        # EVF-SAM generates each layer mask independently — no guarantee of
        # full coverage or mutual exclusivity. To get a proper composite:
        # 1) Resolve overlaps (foreground wins over subject wins over background)
        # 2) Fill unclaimed pixels into the background layer (catch-all)
        import numpy as np
        from PIL import Image
        from vulca.layers.mask import apply_mask_to_image

        # Load alpha masks
        orig_img = Image.open(ORIG / f"{stem}.jpg")
        masks: dict[str, np.ndarray] = {}
        for name, _ in prompts:
            im = np.array(Image.open(src / f"{name}.png"))
            masks[name] = im[:, :, 3] > 10

        # Resolve layer priority: foreground > subject > background
        # (higher z_index claims pixels first)
        if "foreground" in masks:
            if "subject" in masks:
                masks["subject"] &= ~masks["foreground"]
            if "background" in masks:
                masks["background"] &= ~masks["foreground"]
        if "subject" in masks and "background" in masks:
            masks["background"] &= ~masks["subject"]

        # Fill unclaimed pixels into background (catch-all)
        if "background" in masks:
            h, w = masks["background"].shape
            claimed = np.zeros((h, w), dtype=bool)
            for m in masks.values():
                claimed |= m
            masks["background"] |= ~claimed

        # Save resolved masks
        for name, _ in prompts:
            mask_u8 = (masks[name] * 255).astype(np.uint8)
            mask_pil = Image.fromarray(mask_u8, mode="L")
            layer = apply_mask_to_image(orig_img, mask_pil)
            layer.save(str(dst / f"{name}.png"))

        # Write manifest
        manifest = make_manifest(stem, prompts)
        (dst / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        print(f"OK  {stem}: 3 layers + manifest ({manifest['width']}x{manifest['height']})")
        migrated.append(stem)

    print(f"\nMigrated {len(migrated)}, skipped {len(skipped)}")
    if skipped:
        print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    main()
