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

import numpy as np
from PIL import Image

# Prefer an installed `vulca` (pip install -e .), fall back to the sibling
# src/ tree so running `python scripts/migrate_...` directly still works
# for contributors who haven't editable-installed the package yet.
try:
    from vulca.layers.coarse_bucket import coarse_bucket_of, is_background
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from vulca.layers.coarse_bucket import coarse_bucket_of, is_background  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / "assets" / "showcase" / "experiments" / "evfsam_all"
LAYERS = REPO / "assets" / "showcase" / "layers"
ORIG = REPO / "assets" / "showcase" / "originals"
PROMPTS = REPO / "assets" / "showcase" / "experiments" / "evfsam_prompts.json"

Z_INDEX = {"background": 0, "subject": 1, "foreground": 2}

# Semantic-path prefix → z-index.  More specific (deeper) paths should
# have HIGHER z so they win contested pixels over broader regions.
_SP_Z_MAP = [
    # Prefix match, z-index.  Checked in order; first match wins.
    ("foreground.", 80),
    ("foreground",  80),
    ("subject.head.face.", 70),   # eyes/nose/lips beat face_skin
    ("subject.head.face",  65),   # face_skin
    ("subject.head.",      60),   # hair, veil
    ("subject.body.",      55),
    ("subject.person[",    50),   # per-person layers
    ("subject.",           45),
    ("subject",            40),
    ("architecture.",      35),
    ("background.",        10),   # background sub-layers (sky, water)
    ("background",          0),
]


def _z_index_for(layer_name: str, semantic_path: str | None = None) -> int:
    """Derive z_index from semantic_path (preferred) or layer_name.

    Uses _SP_Z_MAP prefix matching on semantic_path for multi-layer schemas.
    Falls back to exact Z_INDEX lookup and coarse_bucket for legacy 3-layer.

    Higher z = wins contested pixels in overlap resolution.
    """
    if not layer_name:
        raise ValueError("layer_name must be a non-empty string")

    # Try semantic_path first (multi-layer schema)
    sp = semantic_path or layer_name
    for prefix, z in _SP_Z_MAP:
        if sp.startswith(prefix):
            return z

    # Legacy exact-name lookup
    if layer_name in Z_INDEX:
        return Z_INDEX[layer_name]
    bucket = coarse_bucket_of(layer_name)
    if bucket in Z_INDEX:
        return Z_INDEX[bucket]
    return 50  # unknown → mid-range, not 99


def resolve_masks_zindex(layers: list[dict]) -> dict[str, np.ndarray]:
    """Resolve overlaps between layer masks by z-index.

    Higher z_index wins: each layer's mask is cleared of all pixels claimed
    by any higher-z layer. After overlap resolution, any unclaimed pixels
    are filled into the is_background layer (if one exists).

    Args:
        layers: list of dicts with REQUIRED keys ``name`` (str), ``z`` (int),
            ``content_type`` (str), ``mask`` (HxW bool ndarray). Extra keys
            are ignored.

    Returns:
        dict name -> bool mask. Together, these cover 100% of the canvas
        with no overlap iff a catch-all background layer is present.

    Tiebreaker:
        When two layers share the same ``z``, the one appearing **earlier
        in the input list** wins contested pixels (stable sort).

    Raises:
        ValueError: on empty input or mismatched mask shapes.
    """
    if not layers:
        raise ValueError("layers list is empty")

    first_shape = layers[0]["mask"].shape
    for i, l in enumerate(layers):
        if l["mask"].shape != first_shape:
            raise ValueError(
                f"layer {i} ({l['name']!r}) mask shape "
                f"{l['mask'].shape} != first shape {first_shape}"
            )

    # Sort by z DESCENDING. Stable sort preserves input order on ties.
    ordered = sorted(layers, key=lambda l: -l["z"])
    out: dict[str, np.ndarray] = {}
    claimed = np.zeros(first_shape, dtype=bool)
    for layer in ordered:
        mask = layer["mask"] & ~claimed
        out[layer["name"]] = mask
        claimed |= mask

    # Fill unclaimed pixels into the lowest-z catch-all background layer.
    # If no background is present but the layers already cover the canvas,
    # that's fine — nothing to fill. If there ARE unclaimed pixels AND
    # no catch-all, fail fast so the caller knows to add a background
    # layer rather than silently producing a composite with holes.
    unclaimed = ~claimed
    bg_candidates = [l for l in layers if is_background(l["content_type"])]
    if bg_candidates:
        bg_layer = min(bg_candidates, key=lambda l: l["z"])
        out[bg_layer["name"]] = out[bg_layer["name"]] | unclaimed
    elif unclaimed.any():
        raise ValueError(
            f"{int(unclaimed.sum())} unclaimed pixels remain and no "
            f"is_background layer is available as catch-all. Add a "
            f"background layer to layers[]."
        )

    return out


def make_manifest(stem: str, prompts: list) -> dict:
    orig_path = ORIG / f"{stem}.jpg"
    im = Image.open(orig_path)
    w, h = im.size

    layers = []
    for entry in prompts:
        if len(entry) < 2:
            continue
        layer_name = entry[0]
        prompt = entry[1]
        # 2-tuple fallback: semantic_path defaults to layer_name (matches
        # Task 9 parse_prompt_entry policy — DO NOT let these drift).
        semantic_path = entry[2] if len(entry) >= 3 else layer_name
        layer_id = "layer_" + hashlib.md5(f"{stem}-{layer_name}".encode()).hexdigest()[:8]
        layers.append({
            "id": layer_id,
            "name": layer_name,
            "description": prompt,
            "z_index": _z_index_for(layer_name, semantic_path),
            "blend_mode": "normal",
            "content_type": layer_name,
            "semantic_path": semantic_path,
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

    for stem in prompts_cfg:
        prompts_raw = prompts_cfg[stem]
        if not prompts_raw:
            print(f"SKIP {stem}: empty prompt list")
            skipped.append(stem)
            continue
        prompts = []
        for entry in prompts_raw:
            if len(entry) < 2:
                continue
            name, prompt = entry[0], entry[1]
            semantic_path = entry[2] if len(entry) >= 3 else name
            prompts.append((name, prompt, semantic_path))
        src = EXP / stem
        dst = LAYERS / stem

        # Only migrate if EVF-SAM output exists
        expected = [src / f"{name}.png" for name, *_ in prompts]
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
        # full coverage or mutual exclusivity. Resolve via z-index (higher
        # wins) then fill unclaimed pixels into the catch-all background.
        from vulca.layers.decomp_validator import validate_decomposition
        from vulca.layers.mask import apply_mask_to_image

        orig_img = Image.open(ORIG / f"{stem}.jpg")
        layer_info: list[dict] = []
        for name, prompt, semantic_path in prompts:
            im = np.array(Image.open(src / f"{name}.png"))
            layer_info.append({
                "name": name,
                "z": _z_index_for(name, semantic_path),
                "content_type": name,
                "mask": im[:, :, 3] > 10,
            })

        resolved = resolve_masks_zindex(layer_info)
        report = validate_decomposition(
            [(resolved[n] * 255).astype(np.uint8) for n, *_ in prompts],
            strict=True,
        )
        print(f"  coverage={report.coverage:.4f} overlap={report.overlap:.4f}")

        for name, *_ in prompts:
            mask_u8 = (resolved[name] * 255).astype(np.uint8)
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
