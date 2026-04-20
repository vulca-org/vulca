"""SAM2 integration for pixel-precise layer extraction.

Meta's SAM2 is not published on PyPI. Two-step install:
    pip install vulca[sam]
    pip install git+https://github.com/facebookresearch/sam2.git
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.coarse_bucket import is_background
from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.manifest import write_manifest
from vulca.layers.mask import apply_mask_to_image

SAM_AVAILABLE = False
try:
    from sam2.build_sam import build_sam2  # noqa: F401
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    SAM_AVAILABLE = True
except ImportError:
    pass


def _compute_layer_point(
    image: Image.Image,
    info: LayerInfo,
) -> tuple[int, int]:
    """Compute the best SAM point prompt for a layer.

    Uses color centroid: find all pixels close to dominant_colors,
    compute their centroid. Falls back to image center if no colors
    or no matching pixels.

    Args:
        image: Source PIL image.
        info: LayerInfo with dominant_colors (hex strings).

    Returns:
        (cx, cy) integer pixel coordinate for the SAM point prompt.
    """
    w, h = image.size
    center = (w // 2, h // 2)

    if not info.dominant_colors:
        return center

    from vulca.layers.mask import hex_to_rgb

    rgb = np.array(image.convert("RGB"), dtype=np.float32)
    mask = np.zeros((h, w), dtype=bool)

    for hex_c in info.dominant_colors:
        try:
            target = np.array(hex_to_rgb(hex_c), dtype=np.float32)
        except (ValueError, IndexError):
            continue
        dist = np.sqrt(np.sum((rgb - target) ** 2, axis=2))
        mask |= (dist < 60)  # Generous threshold for point finding

    if not np.any(mask):
        return center

    ys, xs = np.where(mask)
    mean_x, mean_y = np.mean(xs), np.mean(ys)
    # Use medoid (closest actual pixel to centroid) instead of centroid,
    # because centroid of non-convex shapes (rings, C-curves) can fall
    # outside the shape, producing a bad SAM point prompt.
    dists = (xs - mean_x) ** 2 + (ys - mean_y) ** 2
    best = int(np.argmin(dists))
    cx, cy = int(xs[best]), int(ys[best])
    return (cx, cy)


def sam_split(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    checkpoint: str = "",
) -> list[LayerResult]:
    """Split image using SAM2 pixel-precise masks.

    Processes layers from highest z_index (foreground) to lowest (background)
    to enforce non-overlapping pixel ownership. Background layers receive all
    pixels not claimed by foreground layers.

    Args:
        image_path: Path to the source image.
        layers: LayerInfo list describing the semantic layers.
        output_dir: Directory to write layer PNGs and manifest.json.
        checkpoint: SAM2 model checkpoint name or path.
                    Defaults to "sam2.1_hiera_small".

    Returns:
        List of LayerResult sorted by z_index ascending.

    Raises:
        ImportError: If SAM2 is not installed. See module docstring for the
            two-step install (vulca[sam] deps + sam2 from git).
    """
    if not SAM_AVAILABLE:
        raise ImportError(
            "SAM2 required for --mode sam. Meta's SAM2 is not on PyPI; install via: "
            "pip install vulca[sam] && "
            "pip install git+https://github.com/facebookresearch/sam2.git"
        )

    img = Image.open(image_path).convert("RGB")
    img_np = np.array(img)
    h, w = img_np.shape[:2]

    model_name = checkpoint or "sam2.1_hiera_small"
    predictor = SAM2ImagePredictor.from_pretrained(model_name)
    predictor.set_image(img_np)

    # Track which pixels have already been assigned (foreground priority)
    assigned = np.zeros((h, w), dtype=bool)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sort highest z_index first (foreground) → lowest (background)
    sorted_layers_desc = sorted(layers, key=lambda l: l.z_index, reverse=True)

    layer_masks: dict[str, np.ndarray] = {}

    for info in sorted_layers_desc:
        if is_background(info.content_type):
            # Background gets everything not yet assigned
            mask_bool = ~assigned
        else:
            # Use layer-specific point from color centroid
            cx, cy = _compute_layer_point(img, info)
            point_coords = np.array([[cx, cy]], dtype=np.float32)
            point_labels = np.array([1], dtype=np.int32)

            masks, scores, _ = predictor.predict(
                point_coords=point_coords,
                point_labels=point_labels,
                multimask_output=True,
            )
            # Pick the highest-scoring mask
            best_idx = int(np.argmax(scores))
            mask_bool = masks[best_idx].astype(bool)

            # Remove pixels already claimed by higher-priority layers
            mask_bool = mask_bool & ~assigned

        assigned |= mask_bool
        layer_masks[info.id] = mask_bool

    # Build LayerResult list and save files
    results: list[LayerResult] = []
    for info in sorted_layers_desc:
        mask_bool = layer_masks[info.id]

        # Convert boolean mask to uint8 L-mode image (255=opaque, 0=transparent)
        mask_uint8 = (mask_bool.astype(np.uint8)) * 255
        mask_pil = Image.fromarray(mask_uint8, mode="L")

        layer_rgba = apply_mask_to_image(img, mask_pil)

        out_path = out_dir / f"{info.name}.png"
        layer_rgba.save(str(out_path))
        results.append(LayerResult(info=info, image_path=str(out_path)))

    write_manifest(layers, output_dir=output_dir, width=w, height=h, split_mode="sam")

    # Return sorted by z_index ascending
    return sorted(results, key=lambda r: r.info.z_index)
