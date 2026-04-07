"""SAM3 text-prompted segmentation for pixel-precise layer extraction.

Optional dependency: pip install vulca[sam3]

SAM3 uses text prompts (info.description) instead of point prompts,
giving far more accurate masks than SAM2's single-point approach.
Requires CUDA GPU.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.manifest import write_manifest
from vulca.layers.mask import apply_mask_to_image

logger = logging.getLogger("vulca")

SAM3_AVAILABLE = False
Sam3Model = None
Sam3Processor = None

try:
    from transformers import Sam3Model, Sam3Processor  # type: ignore[assignment]
    SAM3_AVAILABLE = True
except ImportError:
    pass


def sam3_split(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    checkpoint: str = "facebook/sam3",
    threshold: float = 0.5,
) -> list[LayerResult]:
    """Split image using SAM3 text-prompted pixel-precise masks.

    For each non-background layer, uses info.description as the text prompt
    to SAM3, which returns a pixel-precise segmentation mask. Background
    layers receive all pixels not claimed by foreground layers.

    Args:
        image_path: Path to the source image.
        layers: LayerInfo list describing the semantic layers.
        output_dir: Directory to write layer PNGs and manifest.json.
        checkpoint: SAM3 model checkpoint (default "facebook/sam3").
        threshold: Confidence threshold for mask acceptance (default 0.5).

    Returns:
        List of LayerResult sorted by z_index ascending.

    Raises:
        ImportError: If SAM3/transformers not installed.
    """
    if not SAM3_AVAILABLE:
        raise ImportError(
            "SAM3 required for --mode sam3. Install: pip install vulca[sam3]\n"
            "Requires CUDA GPU. For CPU, use --mode vlm instead."
        )

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        logger.warning("SAM3 on CPU may be very slow. Consider --mode vlm for CPU.")

    model = Sam3Model.from_pretrained(checkpoint).to(device)
    model.eval()
    processor = Sam3Processor.from_pretrained(checkpoint)

    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    assigned = np.zeros((h, w), dtype=bool)

    # Phase 1: Generate masks foreground-first (high z_index = priority).
    layer_masks: dict[str, np.ndarray] = {}
    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        if info.content_type == "background":
            continue

        inputs = processor(images=img, text=info.description, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)

        seg_results = processor.post_process_instance_segmentation(
            outputs, threshold=threshold,
        )

        # SAM3 PCS returns multiple instance masks per concept (e.g. multiple
        # mountains). Combine all instances via OR to get full concept coverage.
        # masks tensor shape: [N, mask_h, mask_w]; scores tensor shape: [N]
        masks_t = seg_results[0].get("masks") if seg_results else None
        if masks_t is not None and len(masks_t) > 0:
            # Move to CPU + convert to numpy boolean array
            if hasattr(masks_t, "cpu"):
                masks_arr = masks_t.cpu().numpy()
            else:
                masks_arr = np.asarray(masks_t)
            # Union all instances → single concept mask
            concept_mask = np.any(masks_arr > 0.5, axis=0)

            # Resize from model resolution to original image size if needed
            if concept_mask.shape != (h, w):
                mask_pil = Image.fromarray(
                    concept_mask.astype(np.uint8) * 255, mode="L"
                )
                mask_pil = mask_pil.resize((w, h), Image.NEAREST)
                concept_mask = np.array(mask_pil) > 127

            mask_np = concept_mask & ~assigned
        else:
            logger.warning("SAM3 found no mask for layer %s", info.name)
            mask_np = np.zeros((h, w), dtype=bool)

        assigned |= mask_np
        layer_masks[info.id] = mask_np

    # Phase 2: Background gets everything unclaimed.
    for info in layers:
        if info.content_type == "background":
            layer_masks[info.id] = ~assigned

    # Phase 3: Apply masks and save (z_index ascending).
    results_list: list[LayerResult] = []
    for info in sorted(layers, key=lambda l: l.z_index):
        mask_bool = layer_masks.get(info.id)
        if mask_bool is None:
            mask_bool = np.zeros((h, w), dtype=bool)
        mask_uint8 = (mask_bool.astype(np.uint8)) * 255
        mask_pil = Image.fromarray(mask_uint8, mode="L")
        layer_rgba = apply_mask_to_image(img, mask_pil)

        out_path = out_dir / f"{info.name}.png"
        layer_rgba.save(str(out_path))
        results_list.append(LayerResult(info=info, image_path=str(out_path)))

    write_manifest(layers, output_dir=output_dir, width=w, height=h, split_mode="sam3")
    return sorted(results_list, key=lambda r: r.info.z_index)
