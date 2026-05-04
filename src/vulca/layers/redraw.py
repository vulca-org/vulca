"""Single-layer and multi-layer merge+redraw via img2img.

v0.18.0 recontract (defaults flipped to safer values; ``in_place=True``
restores v0.17.x parity):

- ``output_layer_name``: explicit non-destructive output name. When empty
  (default) the result is auto-derived as ``f"{layer_name}_redrawn"``.
- ``background_strategy``: how to flatten the alpha-sparse layer before
  sending to the provider. ``"cream"`` (default) / ``"white"`` /
  ``"sample_median"`` paste onto a flat RGB canvas so providers don't
  hallucinate new content where the layer is empty. ``"transparent"``
  (legacy) passes the RGBA layer through.
- ``preserve_alpha``: re-apply the source layer's alpha to the provider
  output. Default ``True``.
- ``in_place``: legacy opt-out. When ``True`` the source layer's PNG is
  overwritten and no manifest entry is appended (v0.17.x parity).
- ``provider``-aware api_key: legacy code injected ``GOOGLE_API_KEY`` into
  every provider; we now hand ``api_key=""`` to the provider when the
  caller did not specify one, letting each provider self-resolve its env
  var (OPENAI_API_KEY for openai, GOOGLE_API_KEY for gemini, …).
- Aspect-preserving fit replaces blanket LANCZOS warp on non-square canvases.
"""
from __future__ import annotations

import base64
import json
import logging
import tempfile
from pathlib import Path
from typing import Literal

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork

logger = logging.getLogger("vulca.layers")

CREAM_BG_RGB = (252, 248, 240)
WHITE_BG_RGB = (255, 255, 255)

# v0.20 mask-aware redraw routing
# spec: docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md
SPARSE_AREA_PCT_THRESHOLD = 5.0
SPARSE_BBOX_FILL_THRESHOLD = 0.5
INPAINT_PROMPT_PREFIX = (
    "Repaint the transparent region of the mask (where mask alpha=0) as: {instruction}. "
    "Leave the opaque region (mask alpha=255) bit-identical. "
    "Keep the same silhouette, placement, and scale as the underlying subject. "
    "Do not bleed color outside the mask boundary."
)


def _compute_sparsity(alpha) -> tuple[bool, float, float]:
    """Compute sparsity metrics from a layer's alpha channel.

    Returns ``(sparse, area_pct, bbox_fill)`` where ``sparse`` is true when
    either ``area_pct < 5%`` (single-region small subject like IMG_6847
    flower_cluster_c) or ``bbox_fill < 0.5`` (multi-instance fragmented
    alpha like Scottish row-of-6-lanterns at 8% area).

    See spec B1 — "live alpha, not manifest area_pct" — manifest's persisted
    area_pct can be wrong (Scottish NOTES.md:116-125 documents the case).
    """
    import numpy as np

    arr = np.array(alpha)
    if arr.ndim != 2:
        raise ValueError(
            f"_compute_sparsity expected 2D alpha band; got shape {arr.shape}"
        )
    visible_px = int((arr > 0).sum())
    total_px = int(arr.size)
    if total_px == 0:
        return False, 0.0, 0.0
    area_pct = 100.0 * visible_px / total_px

    # True bounding box (min/max indices) — NOT "populated rows × populated
    # cols" which under-estimates the bbox dramatically for multi-instance
    # spread layouts (e.g. blobs at corners). Empty rows/cols between
    # subjects must count toward the bbox so that bbox_fill reflects
    # spatial sparsity, not just density-within-populated-strip.
    rows_any = (arr > 0).any(axis=1)
    cols_any = (arr > 0).any(axis=0)
    if rows_any.any() and cols_any.any():
        row_idx = np.where(rows_any)[0]
        col_idx = np.where(cols_any)[0]
        bbox_h = int(row_idx[-1] - row_idx[0] + 1)
        bbox_w = int(col_idx[-1] - col_idx[0] + 1)
    else:
        bbox_h = bbox_w = 0
    bbox_area = bbox_h * bbox_w
    bbox_fill = visible_px / bbox_area if bbox_area else 0.0
    sparse = (
        area_pct < SPARSE_AREA_PCT_THRESHOLD
        or bbox_fill < SPARSE_BBOX_FILL_THRESHOLD
    )
    return sparse, area_pct, bbox_fill


def _build_inpaint_mask(alpha):
    """Build an OpenAI-convention RGBA mask from a layer alpha channel.

    OpenAI ``/v1/images/edits`` reads the mask alpha channel: alpha=0 is the
    EDIT zone, alpha=255 is PRESERVE. For ``layers_redraw`` we want the
    SUBJECT (where layer alpha > 0) to be EDITED, and the empty zone
    (where layer alpha == 0) to be PRESERVED.

    Polarity invariant: after construction, ``mask.split()[-1]`` has value 0
    over subject pixels and 255 over empty pixels. The unit test
    ``test_mask_polarity_invariant`` pins this.

    Hard binary {0, 255} only — no GaussianBlur (intermediate alpha values
    are undefined behavior under OpenAI's mask convention).
    """
    from PIL import Image, ImageOps

    if alpha.mode != "L":
        alpha = alpha.convert("L")
    subject = alpha.point(lambda v: 255 if v > 0 else 0)
    edit_mask_channel = ImageOps.invert(subject)  # 0 where subject (edit), 255 where empty (preserve)
    mask = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    mask.putalpha(edit_mask_channel)
    return mask


def _pick_inpaint_size(w: int, h: int) -> tuple[int, int]:
    """Pick an OpenAI-supported edit size matching the layer's aspect.

    OpenAI ``/v1/images/edits`` accepts {1024×1024, 1024×1536, 1536×1024}
    (verified at openai_provider.py:410-415). Rather than letting the
    provider silently fall back to 1024×1024 on a mismatch, we pre-fit
    aspect-preserving so the model's output canvas matches the source.
    """
    if h == 0:
        return (1024, 1024)
    aspect = w / h
    if aspect > 1.3:
        return (1536, 1024)
    if aspect < 1.0 / 1.3:
        return (1024, 1536)
    return (1024, 1024)


def _build_inpaint_prompt(
    instruction: str,
    descriptions: list[str],
    *,
    tradition: str = "default",
) -> str:
    """Build the inpaint-route prompt — explicit alpha-channel reference.

    Spec B5 (reviewer round 2 corrected wording): the canonical phrasing
    "the masked subject pixels" was ambiguous given OpenAI's convention
    treats alpha=0 as the inpaint zone. This wording references the mask
    alpha channel directly.
    """
    parts = [INPAINT_PROMPT_PREFIX.format(instruction=instruction.strip())]
    layer_ctx = "; ".join(d for d in descriptions if d)
    if layer_ctx:
        parts.append("Layer context: " + layer_ctx)
    if tradition and tradition != "default":
        parts.append(
            f"Maintain the {tradition.replace('_', ' ')} cultural tradition "
            "and technique."
        )
    return "\n".join(parts)


async def _redraw_via_inpaint_mask(
    *,
    flat_img,
    src_alpha,
    canvas_size: tuple[int, int],
    instruction: str,
    provider_inst,
    tradition: str,
    target_description: str,
    quality: str = "",
    input_fidelity: str = "",
    output_format: str = "",
    resize_to_api_size: bool = True,
):
    """Mask-aware inpaint path for ``redraw_layer`` (v0.20).

    Returns the model's output as an RGBA image at the original canvas
    size. Caller is responsible for ``preserve_alpha`` re-application.

    Image+mask are downsampled aspect-preserving to a 1024-class API size
    (B8 — flower_cluster_c.png is 4032×3024 but ``/v1/images/edits``
    accepts only {1024,1024×1536,1536×1024}). The model's response is
    upsampled back to the canvas size via ``_fit_into_canvas`` so the
    caller's ``preserve_alpha`` re-application against the ORIGINAL
    canvas alpha works without size mismatch.
    """
    import base64
    import io as _io
    import tempfile

    from PIL import Image

    canvas_w, canvas_h = canvas_size

    # Full-canvas v0.20 path resizes to API-supported dimensions. v0.21 crop
    # path deliberately uploads the real crop dimensions so tiny subjects stay
    # spatially salient; provider output is still fitted back to crop size.
    if resize_to_api_size:
        api_w, api_h = _pick_inpaint_size(canvas_w, canvas_h)
        flat_for_api = _fit_into_canvas(
            flat_img.convert("RGB"), (api_w, api_h), bg_rgb=CREAM_BG_RGB
        )
    else:
        flat_for_api = flat_img.convert("RGB")

    mask_full = _build_inpaint_mask(src_alpha)
    if resize_to_api_size:
        mask_for_api = _fit_into_canvas(mask_full, (api_w, api_h), bg_rgb=None)
    else:
        mask_for_api = mask_full

    # Persist to temp files — the provider's inpaint_with_mask reads paths,
    # not bytes (openai_provider.py:403-405).
    image_tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    mask_tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        flat_for_api.save(image_tmp.name, "PNG")
        image_tmp.close()
        mask_for_api.save(mask_tmp.name, "PNG")
        mask_tmp.close()

        prompt = _build_inpaint_prompt(
            instruction, [target_description], tradition=tradition
        )
        result = await provider_inst.inpaint_with_mask(
            image_path=image_tmp.name,
            mask_path=mask_tmp.name,
            prompt=prompt,
            tradition=tradition,
            quality=quality or None,
            input_fidelity=input_fidelity or None,
            output_format=output_format or None,
        )

        raw = base64.b64decode(result.image_b64)
        if result.mime and "svg" in result.mime:
            out_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        else:
            out_img = Image.open(_io.BytesIO(raw))

        # bg_rgb=CREAM_BG_RGB letterboxes any aspect-mismatched return
        # onto cream; preserve_alpha re-crop downstream means PRESERVE-zone
        # pixels (where mask alpha=255) are discarded regardless of letterbox
        # color. If gpt-image-2 ever starts returning RGBA on the edits
        # endpoint, switch to bg_rgb=None to pass through alpha (v0.21).
        out_img = _fit_into_canvas(out_img, (canvas_w, canvas_h), bg_rgb=CREAM_BG_RGB)
        return out_img.convert("RGBA"), result
    finally:
        for tmp in (image_tmp.name, mask_tmp.name):
            try:
                Path(tmp).unlink(missing_ok=True)
            except Exception:
                pass


def _build_redraw_prompt(
    instruction: str,
    descriptions: list[str],
    *,
    tradition: str = "default",
    canvas_size: str = "",
    background_strategy: str = "transparent",
) -> str:
    """Build img2img redraw prompt from instruction + layer descriptions.

    For non-transparent background_strategy we add a canvas-guard line that
    explicitly tells the provider the flat color is canvas, not subject —
    this stops gpt-image-2 from hallucinating buildings into empty regions
    of an alpha-sparse layer (γ Scottish iter 0 spire bug).
    """
    parts = [instruction.strip()]
    if descriptions:
        parts.append("Layer context: " + "; ".join(d for d in descriptions if d))
    if background_strategy != "transparent":
        parts.append(
            "The flat background is canvas — do NOT introduce new objects, "
            "scenes, or elements where the canvas is empty. Preserve the "
            "original spatial position and bounding box of the visible subject."
        )
    parts.append(
        "Generate a complete image filling the entire canvas. Do NOT include "
        "any checkerboard pattern, grid, or transparency indicators — output "
        "a fully painted image."
    )
    if canvas_size:
        parts.append(f"Canvas size: {canvas_size}.")
    if tradition and tradition != "default":
        parts.append(
            f"Maintain the {tradition.replace('_', ' ')} cultural tradition "
            "and technique."
        )
    return "\n".join(parts)


def _sample_median_bg(rgba_img) -> tuple[int, int, int]:
    """Pick a median-ish RGB from non-transparent pixels.

    Used by background_strategy="sample_median" so the flat canvas matches
    the dominant tone of the layer's actual pixels (e.g. cream parchment for
    a Scottish landscape, dark for a Goya).

    Fallback: when fewer than 0.1% of pixels meet the alpha>=32 visibility
    threshold (essentially fully-transparent layer), we log a warning and
    return CREAM. Codex 2026-04-25 review flagged the silent fallback as a
    "silent lie"; the warning is the agent's signal to inspect.
    """
    from PIL import Image

    rgba = rgba_img.convert("RGBA")
    pixels = list(rgba.getdata())
    visible = [(r, g, b) for r, g, b, a in pixels if a >= 32]
    if not visible:
        logger.warning(
            "redraw: sample_median found no visible pixels (alpha>=32) — "
            "falling back to cream background. Layer may be effectively "
            "transparent; consider background_strategy='cream' explicitly."
        )
        return CREAM_BG_RGB
    visible.sort()
    return visible[len(visible) // 2]


def _flatten_layer(
    src_rgba,
    *,
    background_strategy: str,
):
    """Return (flat_image, bg_rgb_or_None) per strategy."""
    from PIL import Image

    if background_strategy == "transparent":
        return src_rgba, None

    if background_strategy == "cream":
        bg = CREAM_BG_RGB
    elif background_strategy == "white":
        bg = WHITE_BG_RGB
    elif background_strategy == "sample_median":
        bg = _sample_median_bg(src_rgba)
    else:
        raise ValueError(
            f"unknown background_strategy={background_strategy!r}; "
            "expected one of transparent, cream, white, sample_median"
        )

    flat = Image.new("RGB", src_rgba.size, bg)
    flat.paste(src_rgba, (0, 0), src_rgba)  # alpha mask = src alpha
    return flat, bg


def _fit_into_canvas(out_img, target_size: tuple[int, int], bg_rgb):
    """Aspect-preserving fit. Letterboxes with bg_rgb (or transparent)."""
    from PIL import Image

    if out_img.size == target_size:
        return out_img

    tw, th = target_size
    sw, sh = out_img.size
    scale = min(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    resized = out_img.resize((nw, nh), Image.LANCZOS)

    if bg_rgb is None:
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
        if resized.mode != "RGBA":
            resized = resized.convert("RGBA")
    else:
        canvas = Image.new("RGB", target_size, bg_rgb)
        if resized.mode == "RGBA":
            resized = resized.convert("RGB")
    canvas.paste(resized, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def _crop_rgba_and_alpha(src_rgba, crop_box):
    box = (
        crop_box.x,
        crop_box.y,
        crop_box.x + crop_box.w,
        crop_box.y + crop_box.h,
    )
    crop = src_rgba.crop(box).convert("RGBA")
    return crop, crop.split()[-1]


def _crop_rgba_with_alpha(src_rgba, alpha, crop_box):
    box = (
        crop_box.x,
        crop_box.y,
        crop_box.x + crop_box.w,
        crop_box.y + crop_box.h,
    )
    crop = src_rgba.crop(box).convert("RGBA")
    crop_alpha = alpha.crop(box).convert("L")
    crop.putalpha(crop_alpha)
    return crop, crop_alpha


def _pad_crop_box(crop_box, canvas_w: int, canvas_h: int, padding: int):
    x = max(0, crop_box.x - padding)
    y = max(0, crop_box.y - padding)
    right = min(canvas_w, crop_box.x + crop_box.w + padding)
    bottom = min(canvas_h, crop_box.y + crop_box.h + padding)
    return type(crop_box)(x, y, max(0, right - x), max(0, bottom - y))


def _resolve_source_context_image(
    *,
    artwork_dir: str,
    manifest_data: dict,
    expected_size: tuple[int, int],
):
    source_image = manifest_data.get("source_image", "")
    if not source_image:
        return None

    from PIL import Image

    source_path = Path(source_image)
    candidates = [source_path] if source_path.is_absolute() else []
    candidates.extend(
        [
            Path(artwork_dir) / source_image,
            Path(artwork_dir).parent / source_image,
        ]
    )
    for candidate in candidates:
        if not candidate.exists():
            continue
        source = Image.open(candidate).convert("RGB")
        if source.size != expected_size:
            logger.warning(
                "redraw: source_image size %s differs from layer size %s; resizing "
                "source context for refined masked edit.",
                source.size,
                expected_size,
            )
            source = source.resize(expected_size, Image.LANCZOS)
        return source
    return None


def _remove_tiny_binary_components(mask, *, min_area: int):
    import numpy as np

    binary = np.asarray(mask).astype(bool)
    visited = np.zeros(binary.shape, dtype=bool)
    kept = np.zeros(binary.shape, dtype=bool)
    height, width = binary.shape
    for y in range(height):
        for x in range(width):
            if not binary[y, x] or visited[y, x]:
                continue
            stack = [(y, x)]
            visited[y, x] = True
            component = []
            while stack:
                cy, cx = stack.pop()
                component.append((cy, cx))
                for ny in range(max(0, cy - 1), min(height, cy + 2)):
                    for nx in range(max(0, cx - 1), min(width, cx + 2)):
                        if visited[ny, nx] or not binary[ny, nx]:
                            continue
                        visited[ny, nx] = True
                        stack.append((ny, nx))
            if len(component) >= min_area:
                ys, xs = zip(*component)
                kept[ys, xs] = True
    return kept


def _build_flower_edit_matte(source_crop, child_alpha):
    """Derive the actual edit pixels inside a refined flower child mask.

    The child mask is allowed to define the crop/context window, but the
    provider should edit only flower-like evidence inside that window. This
    keeps hedge pixels as source context instead of generated patch content.
    """
    import numpy as np

    from PIL import Image, ImageFilter

    rgb = np.asarray(source_crop.convert("RGB")).astype(np.int16)
    child = np.asarray(child_alpha.convert("L"))
    child_visible = child > 0
    if rgb.shape[:2] != child_visible.shape:
        raise ValueError("source crop and child alpha sizes must match")

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    white_like = (
        (red > 165)
        & (green > 165)
        & (blue > 145)
        & (channel_spread < 95)
    )
    yellow_center = (
        (red > 145)
        & (green > 115)
        & (blue < 135)
        & ((red - blue) > 25)
    )
    edit = (white_like | yellow_center) & child_visible

    if not edit.any():
        return child_alpha.convert("L")

    min_area = max(6, round(int(child_visible.sum()) * 0.00002))
    edit = _remove_tiny_binary_components(edit, min_area=min_area)
    if not edit.any():
        return Image.new("L", child_alpha.size, 0)

    seed = Image.fromarray((edit.astype(np.uint8) * 255))
    opened = seed.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    opened_arr = (np.asarray(opened) > 0) & child_visible
    if opened_arr.any() and int(opened_arr.sum()) >= max(6, int(edit.sum() * 0.25)):
        edit = opened_arr

    matte = Image.fromarray((edit.astype(np.uint8) * 255))
    matte = matte.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    matte_arr = np.minimum(np.asarray(matte), child).astype(np.uint8)
    matte_arr[matte_arr < 10] = 0
    return Image.fromarray(matte_arr)


def _build_flower_removal_matte(source_crop, child_alpha, edit_matte):
    import numpy as np

    from PIL import Image, ImageFilter

    rgb = np.asarray(source_crop.convert("RGB")).astype(np.int16)
    child = np.asarray(child_alpha.convert("L")) > 0
    edit = np.asarray(edit_matte.convert("L")) > 0
    if rgb.shape[:2] != child.shape or child.shape != edit.shape:
        raise ValueError("source crop, child alpha, and edit matte sizes must match")
    if not edit.any():
        return edit_matte.convert("L")

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    old_flower_residue = (
        (red > 145)
        & (green > 135)
        & (blue > 105)
        & (channel_spread < 105)
        & ~((green > red + 12) & (green > blue + 12))
    )

    seed = Image.fromarray((edit.astype(np.uint8) * 255))
    proximity = seed.filter(ImageFilter.MaxFilter(17))
    proximity_arr = np.asarray(proximity) > 0
    removal = proximity_arr | (old_flower_residue & child)
    removal = _remove_tiny_binary_components(removal, min_area=4)
    if not removal.any():
        return edit_matte.convert("L")

    matte = Image.fromarray((removal.astype(np.uint8) * 255))
    matte = matte.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    matte_arr = np.asarray(matte).astype(np.uint8)
    matte_arr[matte_arr < 10] = 0
    return Image.fromarray(matte_arr, mode="L")


def _build_flower_generation_matte(edit_matte, removal_matte):
    import numpy as np

    from PIL import Image, ImageFilter

    edit = edit_matte.convert("L")
    removal = removal_matte.convert("L")
    if edit.size != removal.size:
        raise ValueError("edit matte and removal matte sizes must match")

    edit_arr = np.asarray(edit)
    removal_arr = np.asarray(removal)
    if not np.any(edit_arr > 8):
        return edit

    expanded = edit.filter(ImageFilter.MaxFilter(13)).filter(
        ImageFilter.GaussianBlur(0.8)
    )
    generation_arr = np.minimum(np.asarray(expanded), removal_arr).astype(np.uint8)
    generation_arr = np.maximum(generation_arr, edit_arr).astype(np.uint8)
    generation_arr[generation_arr < 10] = 0
    return Image.fromarray(generation_arr, mode="L")


def _clear_source_crop_with_matte(source_crop, removal_matte):
    import numpy as np

    from PIL import Image

    source = source_crop.convert("RGB")
    arr = np.asarray(source).copy()
    remove = np.asarray(removal_matte.convert("L")) > 8
    if arr.shape[:2] != remove.shape:
        raise ValueError("source crop and removal matte sizes must match")
    if not remove.any():
        return source

    red = arr[:, :, 0].astype(np.int16)
    green = arr[:, :, 1].astype(np.int16)
    blue = arr[:, :, 2].astype(np.int16)
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    flower_like = (
        (red > 145)
        & (green > 135)
        & (blue > 105)
        & (channel_spread < 120)
    )
    background = (~remove) & (~flower_like)
    if not background.any():
        background = ~remove
    if not background.any():
        arr[remove] = np.array(CREAM_BG_RGB, dtype=np.uint8)
        return Image.fromarray(arr, mode="RGB")

    arr = _fill_removed_pixels_from_boundary(arr, remove, background)
    return Image.fromarray(arr, mode="RGB")


def _fill_removed_pixels_from_boundary(arr, remove, known):
    import numpy as np

    filled = arr.copy()
    unknown = remove.copy()
    known = known.copy()
    height, width = unknown.shape
    max_iterations = max(1, min(max(height, width), 512))

    for _ in range(max_iterations):
        if not unknown.any():
            break

        acc = np.zeros(filled.shape, dtype=np.uint32)
        count = np.zeros(unknown.shape, dtype=np.uint8)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                src_y0 = max(0, -dy)
                src_y1 = height - max(0, dy)
                dst_y0 = max(0, dy)
                dst_y1 = height - max(0, -dy)
                src_x0 = max(0, -dx)
                src_x1 = width - max(0, dx)
                dst_x0 = max(0, dx)
                dst_x1 = width - max(0, -dx)

                src_known = known[src_y0:src_y1, src_x0:src_x1]
                target = unknown[dst_y0:dst_y1, dst_x0:dst_x1] & src_known
                if not target.any():
                    continue
                src_values = filled[src_y0:src_y1, src_x0:src_x1]
                for channel in range(3):
                    acc_channel = acc[dst_y0:dst_y1, dst_x0:dst_x1, channel]
                    acc_channel[target] += src_values[:, :, channel][target]
                count_view = count[dst_y0:dst_y1, dst_x0:dst_x1]
                count_view[target] += 1

        candidates = unknown & (count > 0)
        if not candidates.any():
            break
        filled[candidates] = (
            acc[candidates] / count[candidates, None]
        ).astype(np.uint8)
        known[candidates] = True
        unknown[candidates] = False

    if unknown.any():
        fallback = np.median(filled[known], axis=0).astype(np.uint8)
        filled[unknown] = fallback
    return filled


def _build_source_flower_cover_alpha(source_crop, removal_matte):
    import numpy as np

    from PIL import Image, ImageFilter

    rgb = np.asarray(source_crop.convert("RGB")).astype(np.int16)
    removal = np.asarray(removal_matte.convert("L"))
    if rgb.shape[:2] != removal.shape:
        raise ValueError("source crop and removal matte sizes must match")

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    white_like = (
        (red > 155)
        & (green > 150)
        & (blue > 120)
        & (channel_spread < 120)
    )
    yellow_center = (
        (red > 135)
        & (green > 105)
        & (blue < 145)
        & ((red - blue) > 20)
    )
    old_flower = (white_like | yellow_center) & (removal > 8)
    if not old_flower.any():
        return Image.new("L", source_crop.size, 0)

    old_flower = _remove_tiny_binary_components(old_flower, min_area=1)
    if not old_flower.any():
        return Image.new("L", source_crop.size, 0)

    cover = Image.fromarray((old_flower.astype(np.uint8) * 255))
    cover = cover.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.5))
    cover_arr = np.minimum(np.asarray(cover), removal).astype(np.uint8)
    cover_arr[cover_arr < 10] = 0
    return Image.fromarray(cover_arr, mode="L")


def _build_generated_flower_cover_patch(
    generated_crop,
    source_cover_alpha,
    *,
    target_palette: str = "mixed",
):
    import numpy as np

    from PIL import Image, ImageFilter

    flowers = generated_crop.convert("RGBA")
    cover_alpha = source_cover_alpha.convert("L")
    if flowers.size != cover_alpha.size:
        raise ValueError("generated crop and source cover alpha sizes must match")

    flower_alpha = np.asarray(flowers.split()[-1])
    rgb = np.asarray(flowers.convert("RGB")).astype(np.int16)
    cover = np.asarray(cover_alpha)
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    white_like = (
        (red > 145)
        & (green > 145)
        & (blue > 120)
        & (channel_spread < 120)
    )
    yellow_center = (
        (red > 130)
        & (green > 95)
        & (blue < 160)
        & ((red - blue) > 20)
    )
    yellow_like = (
        (red > 160)
        & (green > 110)
        & (blue < 135)
        & ((red - blue) > 45)
        & ((green - blue) > 15)
        & ((red + green - 2 * blue) > 135)
    )
    if target_palette == "yellow":
        flower_paint = yellow_like & (flower_alpha > 8)
    else:
        flower_paint = (white_like | yellow_center) & (flower_alpha > 8)
    cover_visible = cover > 8
    if not flower_paint.any() or not cover_visible.any():
        return Image.new("RGBA", flowers.size, (0, 0, 0, 0))

    proximity = Image.fromarray((flower_paint.astype(np.uint8) * 255))
    cover_radius = 11 if target_palette == "yellow" else 25
    proximity = proximity.filter(ImageFilter.MaxFilter(cover_radius))
    fill_area = cover_visible & (np.asarray(proximity) > 8) & ~flower_paint
    if not fill_area.any():
        return Image.new("RGBA", flowers.size, (0, 0, 0, 0))

    flower_rgb = np.asarray(flowers.convert("RGB")).copy()
    filled_rgb = _fill_removed_pixels_from_boundary(
        flower_rgb,
        fill_area,
        flower_paint,
    )
    patch_arr = np.zeros((*cover.shape, 4), dtype=np.uint8)
    patch_arr[:, :, :3] = filled_rgb
    patch_alpha = cover.copy().astype(np.uint8)
    patch_alpha[~fill_area] = 0
    patch_arr[:, :, 3] = patch_alpha
    return Image.fromarray(patch_arr, mode="RGBA")


def _compose_flower_replacement_patch(
    source_crop,
    cleared_crop,
    generated_crop,
    removal_matte,
    *,
    target_palette: str = "mixed",
):
    from PIL import Image

    source_cover_alpha = _build_source_flower_cover_alpha(source_crop, removal_matte)
    base = Image.new("RGBA", cleared_crop.size, (0, 0, 0, 0))
    flowers = generated_crop.convert("RGBA")
    base.alpha_composite(flowers)
    base.alpha_composite(
        _build_generated_flower_cover_patch(
            flowers,
            source_cover_alpha,
            target_palette=target_palette,
        )
    )
    return base


def _build_square_padded_edit_inputs(
    source_crop,
    edit_matte,
    *,
    target_size: int = 1024,
):
    from PIL import Image

    crop = source_crop.convert("RGB")
    matte = edit_matte.convert("L")
    if crop.size != matte.size:
        raise ValueError("source crop and edit matte sizes must match")

    width, height = crop.size
    if width <= 0 or height <= 0:
        raise ValueError("source crop must be non-empty")

    scale = min(target_size / width, target_size / height)
    resized_size = (
        max(1, round(width * scale)),
        max(1, round(height * scale)),
    )
    offset = (
        (target_size - resized_size[0]) // 2,
        (target_size - resized_size[1]) // 2,
    )
    content_box = (
        offset[0],
        offset[1],
        offset[0] + resized_size[0],
        offset[1] + resized_size[1],
    )

    input_image = Image.new("RGB", (target_size, target_size), CREAM_BG_RGB)
    input_image.paste(crop.resize(resized_size, Image.LANCZOS), offset)

    resized_matte = matte.resize(resized_size, Image.LANCZOS)
    edit_alpha = resized_matte.point(lambda value: 0 if value > 8 else 255)
    mask_alpha = Image.new("L", (target_size, target_size), 255)
    mask_alpha.paste(edit_alpha, offset)
    mask = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    mask.putalpha(mask_alpha)
    return input_image, mask, content_box


def _new_redraw_debug_artifacts(
    debug_artifact_dir: str,
    *,
    layer_name: str,
    instruction: str,
    provider: str,
    model: str,
):
    if not debug_artifact_dir:
        return None
    out_dir = Path(debug_artifact_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "dir": out_dir,
        "layer_name": layer_name,
        "instruction": instruction,
        "provider": provider,
        "model": model,
        "calls": [],
        "failures": [],
    }


def _write_redraw_debug_summary(
    debug_artifacts,
    *,
    status: str,
    advisory: dict | None = None,
    output_path: str = "",
    final_source_pasteback_path: str = "",
    source_pasteback_error: str = "",
    error: str = "",
) -> None:
    if not debug_artifacts:
        return
    calls = debug_artifacts["calls"]
    total_cost = 0.0
    cost_known = False
    for call in calls:
        cost = call.get("cost_usd")
        if isinstance(cost, (int, float)):
            total_cost += float(cost)
            cost_known = True
    summary = {
        "status": status,
        "layer_name": debug_artifacts["layer_name"],
        "instruction": debug_artifacts["instruction"],
        "provider": debug_artifacts["provider"],
        "model": debug_artifacts["model"],
        "child_count": len(calls),
        "completed_child_count": sum(
            1 for call in calls if call.get("status") == "completed"
        ),
        "calls": calls,
        "failures": debug_artifacts["failures"],
        "total_cost_usd": round(total_cost, 6) if cost_known else None,
    }
    if advisory is not None:
        summary["redraw_advisory"] = advisory
    if output_path:
        summary["output_path"] = output_path
    if final_source_pasteback_path:
        summary["final_source_pasteback_path"] = final_source_pasteback_path
    if source_pasteback_error:
        summary["source_pasteback_error"] = source_pasteback_error
    if error:
        summary["error"] = error
    summary_path = debug_artifacts["dir"] / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))


def _image_result_cost_usd(result) -> float | None:
    metadata = getattr(result, "metadata", {}) or {}
    cost = metadata.get("cost_usd")
    if isinstance(cost, (int, float)):
        return float(cost)
    return None


def _infer_small_botanical_target_palette(
    *,
    description: str = "",
    instruction: str = "",
) -> str:
    text = f"{description} {instruction}".lower()
    if any(term in text for term in ("dandelion", "buttercup")):
        return "yellow"
    if "yellow" in text and not any(
        term in text for term in ("white flower", "white wildflower", "white petal")
    ):
        return "yellow"
    return "mixed"


def _build_small_botanical_child_prompt(
    *,
    instruction: str,
    tradition: str,
    target_palette: str,
    head_count: int = 1,
) -> str:
    if target_palette == "yellow":
        subject = "compact yellow dandelion or buttercup flower head replacements"
        style = (
            "hand-painted flower heads with warm centers, varied spacing, and "
            "natural scale"
        )
    else:
        subject = "compact small wildflower head replacements"
        style = "hand-painted petals with warm centers, varied spacing, and natural scale"
    parts = [
        "Repaint only the transparent mask pixels (mask alpha=0) as "
        f"{subject}.",
        "Treat the source crop only as scale, lighting, and edge context.",
        "Leave every opaque/unmasked pixel unchanged.",
        f"Paint exactly {max(1, head_count)} separated flower head"
        f"{'' if max(1, head_count) == 1 else 's'}; do not add extra heads.",
        "Match the original head size and footprint.",
        f"Paint separated {style}.",
        "Do not generate non-botanical background scene content, rectangular "
        "thumbnails, or broad texture patches.",
    ]
    lower_instruction = instruction.lower()
    if "storybook" in lower_instruction:
        parts.append("Use a subtle storybook botanical accent, not a new scene.")
    if tradition and tradition != "default":
        parts.append(
            f"Maintain the {tradition.replace('_', ' ')} cultural tradition "
            "and technique."
        )
    return "\n".join(parts)


def _estimate_small_botanical_head_count(edit_matte) -> int:
    import numpy as np
    from collections import deque

    arr = np.asarray(edit_matte.convert("L")) > 8
    height, width = arr.shape
    seen = np.zeros(arr.shape, dtype=bool)
    count = 0
    for y in range(height):
        for x in range(width):
            if not arr[y, x] or seen[y, x]:
                continue
            q: deque[tuple[int, int]] = deque([(x, y)])
            seen[y, x] = True
            area = 0
            while q:
                cx, cy = q.popleft()
                area += 1
                for nx in (cx - 1, cx, cx + 1):
                    for ny in (cy - 1, cy, cy + 1):
                        if nx < 0 or ny < 0 or nx >= width or ny >= height:
                            continue
                        if seen[ny, nx] or not arr[ny, nx]:
                            continue
                        seen[ny, nx] = True
                        q.append((nx, ny))
            if area >= 8:
                count += 1
    return max(1, min(count, 8))


def _build_flower_output_alpha(crop_rgba, edit_matte, *, target_palette: str = "mixed"):
    import numpy as np

    from PIL import Image, ImageFilter

    base_alpha = edit_matte.convert("L")
    alpha_arr = np.asarray(base_alpha).copy()
    rgb = np.asarray(crop_rgba.convert("RGB")).astype(np.int16)

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    white_like = (
        (red > 145)
        & (green > 145)
        & (blue > 120)
        & (channel_spread < 120)
    )
    yellow_center = (
        (red > 130)
        & (green > 95)
        & (blue < 160)
        & ((red - blue) > 20)
    )
    yellow_like = (
        (red > 160)
        & (green > 110)
        & (blue < 135)
        & ((red - blue) > 45)
        & ((green - blue) > 15)
        & ((red + green - 2 * blue) > 135)
    )
    if target_palette == "yellow":
        flower_like = yellow_like & (alpha_arr > 0)
    else:
        flower_like = (white_like | yellow_center) & (alpha_arr > 0)
    if flower_like.any():
        support = Image.fromarray((flower_like.astype(np.uint8) * 255))
        support = support.filter(ImageFilter.MaxFilter(5)).filter(
            ImageFilter.GaussianBlur(0.7)
        )
        alpha_arr = np.minimum(alpha_arr, np.asarray(support))
    else:
        alpha_arr[:] = 0

    if target_palette == "yellow":
        alpha_arr[~yellow_like] = 0

    dark_artifact = (
        (alpha_arr > 0)
        & (rgb.mean(axis=2) < 35)
        & (rgb.max(axis=2) < 45)
    )
    hedge_like = (
        (green > red + 10)
        & (green > blue + 10)
        & (red < 140)
        & (blue < 130)
        & (green < 190)
        & ~white_like
        & ~yellow_center
        & ~yellow_like
    )
    olive_halo = (
        (red > 45)
        & (red < 120)
        & (green > 55)
        & (green < 135)
        & (blue > 25)
        & (blue < 95)
        & (green >= red - 10)
        & ~white_like
        & ~yellow_center
        & ~yellow_like
    )
    alpha_arr[dark_artifact] = 0
    alpha_arr[hedge_like] = 0
    alpha_arr[olive_halo] = 0
    return Image.fromarray(alpha_arr.astype(np.uint8), mode="L")


def _small_botanical_scene_like_mask(rgb_arr):
    import numpy as np

    rgb = rgb_arr.astype(np.int16)
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )
    mean = rgb.mean(axis=2)
    sky_like = (blue > 135) & (blue > red + 35) & (blue > green + 20) & (red < 135)
    vehicle_red = (red > 120) & (red > green + 45) & (red > blue + 35)
    road_or_metal_gray = (mean > 105) & (mean < 225) & (spread < 34)
    return sky_like | vehicle_red | road_or_metal_gray


def _small_botanical_raw_scene_rejection(
    *,
    source_crop,
    generated_crop,
    target_palette: str,
) -> dict:
    import numpy as np

    if target_palette != "yellow":
        return {"reject": False, "reason": ""}
    source = source_crop.convert("RGB")
    generated = generated_crop.convert("RGB")
    if source.size != generated.size:
        from PIL import Image

        source = source.resize(generated.size, Image.LANCZOS)
    src_scene = _small_botanical_scene_like_mask(np.asarray(source))
    gen_scene = _small_botanical_scene_like_mask(np.asarray(generated))
    if not gen_scene.any():
        return {"reject": False, "reason": "", "new_scene_like_pct": 0.0}
    scene_growth = gen_scene & ~src_scene
    new_scene_like_pct = 100.0 * float(scene_growth.sum()) / float(gen_scene.size)
    if new_scene_like_pct > 8.0:
        return {
            "reject": True,
            "reason": "raw_scene_thumbnail_leak",
            "new_scene_like_pct": round(new_scene_like_pct, 3),
        }
    return {
        "reject": False,
        "reason": "",
        "new_scene_like_pct": round(new_scene_like_pct, 3),
    }


async def _redraw_source_context_with_edit_matte(
    *,
    source_crop,
    edit_matte,
    removal_matte=None,
    instruction: str,
    provider_inst,
    tradition: str,
    target_description: str,
    quality: str = "",
    input_fidelity: str = "",
    output_format: str = "",
    debug_artifacts=None,
    debug_child_index: int = 0,
    target_palette: str = "mixed",
):
    import base64
    import io as _io
    import tempfile

    from PIL import Image

    replacement_matte = (
        removal_matte.convert("L") if removal_matte is not None else edit_matte
    )
    generation_matte = _build_flower_generation_matte(edit_matte, replacement_matte)
    cleared_crop = _clear_source_crop_with_matte(source_crop, replacement_matte)
    input_image, mask, content_box = _build_square_padded_edit_inputs(
        cleared_crop,
        generation_matte,
        target_size=1024,
    )
    image_tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    mask_tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    debug_record = None
    try:
        input_image.save(image_tmp.name, "PNG")
        image_tmp.close()
        mask.save(mask_tmp.name, "PNG")
        mask_tmp.close()

        if debug_artifacts:
            index = debug_child_index or len(debug_artifacts["calls"]) + 1
            prefix = f"child_{index:02d}"
            source_crop_path = debug_artifacts["dir"] / f"{prefix}_source_crop.png"
            edit_matte_path = debug_artifacts["dir"] / f"{prefix}_edit_matte.png"
            removal_matte_path = (
                debug_artifacts["dir"] / f"{prefix}_removal_matte.png"
            )
            cleared_crop_path = (
                debug_artifacts["dir"] / f"{prefix}_cleared_crop.png"
            )
            input_path = debug_artifacts["dir"] / f"{prefix}_input.png"
            mask_path = debug_artifacts["dir"] / f"{prefix}_mask.png"
            raw_path = debug_artifacts["dir"] / f"{prefix}_raw.png"
            patch_path = debug_artifacts["dir"] / f"{prefix}_patch.png"
            pasteback_path = debug_artifacts["dir"] / f"{prefix}_pasteback.png"
            source_crop.save(source_crop_path)
            generation_matte.save(edit_matte_path)
            replacement_matte.save(removal_matte_path)
            cleared_crop.save(cleared_crop_path)
            input_image.save(input_path)
            mask.save(mask_path)
            debug_record = {
                "index": index,
                "status": "started",
                "source_crop_path": str(source_crop_path),
                "edit_matte_path": str(edit_matte_path),
                "removal_matte_path": str(removal_matte_path),
                "cleared_crop_path": str(cleared_crop_path),
                "input_path": str(input_path),
                "mask_path": str(mask_path),
                "raw_path": str(raw_path),
                "patch_path": str(patch_path),
                "pasteback_path": str(pasteback_path),
            }
            debug_artifacts["calls"].append(debug_record)
            _write_redraw_debug_summary(debug_artifacts, status="running")

        prompt = _build_small_botanical_child_prompt(
            instruction=instruction,
            tradition=tradition,
            target_palette=target_palette,
            head_count=_estimate_small_botanical_head_count(edit_matte),
        )
        result = await provider_inst.inpaint_with_mask(
            image_path=image_tmp.name,
            mask_path=mask_tmp.name,
            prompt=prompt,
            tradition=tradition,
            size="1024x1024",
            quality=quality or None,
            input_fidelity=input_fidelity or None,
            output_format=output_format or None,
        )

        raw = base64.b64decode(result.image_b64)
        if result.mime and "svg" in result.mime:
            out_img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        else:
            out_img = Image.open(_io.BytesIO(raw))
            out_img.load()

        if debug_record is not None:
            out_img.convert("RGBA").save(debug_record["raw_path"])

        out_img = _fit_into_canvas(out_img, (1024, 1024), bg_rgb=CREAM_BG_RGB)
        crop_out = out_img.crop(content_box).resize(source_crop.size, Image.LANCZOS)
        crop_out = crop_out.convert("RGBA")
        raw_scene_gate = _small_botanical_raw_scene_rejection(
            source_crop=source_crop,
            generated_crop=crop_out,
            target_palette=target_palette,
        )
        if raw_scene_gate.get("reject"):
            crop_out = Image.new("RGBA", source_crop.size, (0, 0, 0, 0))
            if debug_record is not None:
                debug_record.update(
                    {
                        "raw_scene_rejected": True,
                        "raw_scene_reject_reason": raw_scene_gate.get("reason", ""),
                        "raw_scene_gate": raw_scene_gate,
                    }
                )
        else:
            if debug_record is not None:
                debug_record.update(
                    {
                        "raw_scene_rejected": False,
                        "raw_scene_gate": raw_scene_gate,
                    }
                )
        flower_alpha = _build_flower_output_alpha(
            crop_out,
            generation_matte,
            target_palette=target_palette,
        )
        crop_out.putalpha(flower_alpha)
        crop_out = _compose_flower_replacement_patch(
            source_crop,
            cleared_crop,
            crop_out,
            replacement_matte,
            target_palette=target_palette,
        )
        if debug_record is not None:
            crop_out.save(debug_record["patch_path"])
            pasteback = source_crop.convert("RGBA")
            pasteback.alpha_composite(crop_out)
            pasteback.save(debug_record["pasteback_path"])
            metadata = getattr(result, "metadata", {}) or {}
            debug_record.update(
                {
                    "status": "completed",
                    "cost_usd": metadata.get("cost_usd"),
                    "usage": metadata.get("usage"),
                    "metadata": metadata,
                }
            )
            _write_redraw_debug_summary(debug_artifacts, status="running")
        return crop_out, result
    except Exception as exc:
        if debug_record is not None:
            debug_record.update({"status": "failed", "error": str(exc)})
            debug_artifacts["failures"].append(debug_record)
            _write_redraw_debug_summary(
                debug_artifacts,
                status="failed",
                error=str(exc),
            )
        raise
    finally:
        for tmp in (image_tmp.name, mask_tmp.name):
            try:
                Path(tmp).unlink(missing_ok=True)
            except Exception:
                pass


def _paste_crop_preserving_alpha(canvas, crop_rgba, crop_alpha, crop_box) -> None:
    crop_rgba = crop_rgba.convert("RGBA")
    if crop_rgba.size != crop_alpha.size:
        from PIL import Image

        crop_rgba = crop_rgba.resize(crop_alpha.size, Image.LANCZOS)
    crop_rgba.putalpha(crop_alpha)
    canvas.alpha_composite(crop_rgba, dest=(crop_box.x, crop_box.y))


def _add_or_replace_layer_in_manifest(
    artwork_dir: str,
    *,
    new_name: str,
    template: LayerInfo,
    description: str = "",
) -> int:
    """Append a new layer entry mirroring template's metadata.

    Used when output_layer_name diverges from the source layer name. If a
    layer of the same name already exists, it is replaced (idempotent).

    Returns the z_index assigned to the new layer so the caller's
    in-memory ``LayerResult`` agrees with what was just written to disk
    (P1.1 from 2026-04-25 review — disagreement caused the layer to
    silently move on the next ``load_manifest``).
    """
    from vulca.layers.manifest import load_manifest, write_manifest

    artwork = load_manifest(artwork_dir)
    layers = [lr.info for lr in artwork.layers if lr.info.name != new_name]
    new_z = max((l.z_index for l in layers), default=template.z_index) + 1

    new_info = LayerInfo(
        name=new_name,
        description=description or template.description,
        z_index=new_z,
        content_type=template.content_type,
        semantic_path=template.semantic_path,
        blend_mode=template.blend_mode,
        visible=True,
    )
    layers.append(new_info)

    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest_data = json.loads(manifest_path.read_text())
    write_manifest(
        layers,
        output_dir=artwork_dir,
        width=manifest_data.get("width", 1024),
        height=manifest_data.get("height", 1024),
        source_image=manifest_data.get("source_image", ""),
        split_mode=manifest_data.get("split_mode", ""),
        generation_path=manifest_data.get("generation_path", ""),
        layerability=manifest_data.get("layerability", ""),
        partial=manifest_data.get("partial", False),
        warnings=manifest_data.get("warnings", []),
        tradition=manifest_data.get("tradition", ""),
    )
    return new_z


async def redraw_layer(
    artwork: LayeredArtwork,
    *,
    layer_name: str,
    instruction: str,
    provider: str = "gemini",
    tradition: str = "default",
    api_key: str = "",
    artwork_dir: str,
    output_layer_name: str = "",
    background_strategy: str = "cream",
    preserve_alpha: bool = True,
    in_place: bool = False,
    route: Literal["auto", "img2img", "inpaint"] = "auto",
    model: str = "",
    quality: str = "",
    input_fidelity: str = "",
    output_format: str = "",
    debug_artifact_dir: str = "",
    max_refinement_children: int = 0,
    max_redraw_cost_usd: float = 0.0,
) -> LayerResult:
    """Redraw a single layer via img2img or mask-aware inpaint (v0.20).

    Output path resolution (v0.18.0):
      - if ``in_place=True`` → overwrite the source layer's PNG (legacy parity)
      - elif ``output_layer_name`` is non-empty → write to ``<output_layer_name>.png``
      - else → write to ``<layer_name>_redrawn.png`` (new safe default)

    ``in_place=True`` takes precedence; ``output_layer_name`` is silently
    ignored when ``in_place=True``.

    Defaults preserve alpha (``preserve_alpha=True``) and use a cream
    background (``background_strategy="cream"``) so providers don't
    hallucinate scenes into the alpha-empty regions of sparse layers.
    To restore v0.17.x legacy behavior verbatim, pass
    ``in_place=True, background_strategy="transparent", preserve_alpha=False``.

    v0.20 routing (``route``):
      - ``"auto"`` (default): when the layer alpha is sparse (area_pct<5%
        OR bbox_fill<0.5) AND the provider implements ``inpaint_with_mask``,
        route through OpenAI's mask-aware ``/v1/images/edits`` so the model
        receives explicit "edit here, preserve there" guidance instead of
        unmasked img2img. Dense layers and providers without mask support
        stay on the legacy img2img path bit-identically.
      - ``"img2img"``: force the legacy unmasked path (v0.18.x parity).
        The ``background_strategy="cream"`` workaround is most useful here.
      - ``"inpaint"``: force the mask-aware path. Falls back to img2img
        with a warning if the provider lacks ``inpaint_with_mask``.

    On the inpaint path, ``background_strategy`` is honored only in the
    sense that it controls how ``flat`` is built (which is used as the
    inpaint base image); its semantic effect is reduced because the model
    is told via mask which pixels to actually edit. ``cream`` remains the
    recommended setting on inpaint so the visible-but-preserved subject
    pixels read coherently if the API ever returns content outside the
    mask zone.

    v0.20.1 model contract (fix the silent-drop bug uncovered in v0.20 PR audit):
      - ``model``: provider model id (e.g. ``"gpt-image-2"``). Empty → provider default.
        Plumbed by setting ``provider.model`` after instantiation, matching the
        ``generate_image`` MCP tool's per-call override pattern.
      - ``quality``: ``"low" | "medium" | "high" | "auto"`` for gpt-image-*.
      - ``input_fidelity``: ``"high" | "low"`` — model-specific knob. Silently
        dropped by ``_drop_unsupported_params`` if the current model lacks
        the capability flag.
      - ``output_format``: ``"png" | "webp" | "jpeg"`` for gpt-image-*.

    Spec: ``docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md``.
    """
    import numpy as np

    from PIL import Image

    from vulca.layers.redraw_strategy import (
        RedrawRoute,
        analyze_alpha_geometry,
        choose_redraw_route,
    )
    from vulca.layers.mask_refine import refine_mask_for_target
    from vulca.layers.redraw_quality import (
        evaluate_redraw_quality,
        is_texture_redraw_request,
    )
    from vulca.providers import get_image_provider

    # 1. Find target layer
    target: LayerResult | None = None
    for lr in artwork.layers:
        if lr.info.name == layer_name:
            target = lr
            break
    if target is None:
        raise ValueError(
            f"Layer {layer_name!r} not found in artwork "
            f"(available: {[l.info.name for l in artwork.layers]})"
        )

    if target.info.locked:
        raise ValueError(
            f"Layer {layer_name!r} is locked and cannot be redrawn "
            f"(likely a pipeline-synthesized layer like 'residual'). "
            f"Unlock it explicitly via layers_edit if you really mean to."
        )

    # 2. Read source layer + flatten per strategy
    src_path = Path(target.image_path)
    src_rgba = Image.open(str(src_path)).convert("RGBA")
    src_alpha = src_rgba.split()[-1]

    # v0.20 — degenerate empty-layer guard (spec C7). A layer with no
    # opaque pixels can't be redrawn coherently regardless of route.
    if int((np.array(src_alpha) > 0).sum()) == 0:
        raise ValueError(
            f"Layer {layer_name!r} has no visible pixels (alpha == 0 everywhere); "
            "cannot redraw an empty layer."
        )

    flat, bg_rgb = _flatten_layer(src_rgba, background_strategy=background_strategy)

    # 3. Build prompt + read canvas size
    canvas_size_hint = ""
    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest_data = json.loads(manifest_path.read_text())
    canvas_w = manifest_data.get("width", src_rgba.width)
    canvas_h = manifest_data.get("height", src_rgba.height)
    if canvas_w and canvas_h:
        canvas_size_hint = f"{canvas_w}x{canvas_h}"

    # v0.20 mask-aware routing decision (spec B1+B4+B6).
    sparse, area_pct, bbox_fill = _compute_sparsity(src_alpha)
    geometry = analyze_alpha_geometry(src_alpha)
    redraw_plan = choose_redraw_route(geometry)
    refinement_max_children = (
        max_refinement_children if max_refinement_children > 0 else 24
    )
    refinement = refine_mask_for_target(
        src_rgba.convert("RGB"),
        src_alpha,
        description=target.info.description,
        instruction=instruction,
        max_children=refinement_max_children,
    )
    target_palette = _infer_small_botanical_target_palette(
        description=target.info.description,
        instruction=instruction,
    )
    bbox_area_pct = area_pct / max(0.0001, bbox_fill)
    preflight_skip_reason = ""
    if (
        route == "auto"
        and not refinement.applied
        and is_texture_redraw_request(
            description=target.info.description,
            instruction=instruction,
        )
        and (area_pct > 5.0 or bbox_area_pct > 10.0)
    ):
        preflight_skip_reason = "broad_texture_repaint_risk"
    img_provider = get_image_provider(provider, api_key=api_key)
    # v0.20.1 — per-call model override, matching generate_image MCP pattern
    # (mcp_server.py:1340-1344). Silent no-op if provider has no `model` attr.
    if model and hasattr(img_provider, "model"):
        img_provider.model = model
    debug_artifacts = _new_redraw_debug_artifacts(
        debug_artifact_dir,
        layer_name=layer_name,
        instruction=instruction,
        provider=provider,
        model=getattr(img_provider, "model", model),
    )
    has_inpaint = hasattr(img_provider, "inpaint_with_mask")
    edit_caps = (
        img_provider.edit_capabilities()
        if hasattr(img_provider, "edit_capabilities")
        else None
    )

    refinement_path_available = refinement.applied and has_inpaint and route != "img2img"

    if preflight_skip_reason:
        chosen_route = "skip"
    elif route == "auto":
        chosen_route = "inpaint" if (sparse and has_inpaint) else "img2img"
    elif route == "inpaint":
        if not has_inpaint:
            logger.warning(
                "Provider %s lacks inpaint_with_mask; falling back to img2img.",
                type(img_provider).__name__,
            )
            chosen_route = "img2img"
        else:
            chosen_route = "inpaint"
    elif route == "img2img":
        chosen_route = "img2img"
    else:
        raise ValueError(
            f"Unknown route={route!r}; expected one of 'auto', 'img2img', 'inpaint'."
        )
    if refinement_path_available:
        chosen_route = "inpaint"

    # Spec E — log-channel advisory in v0.20 (typed return advisory deferred to v0.21).
    logger.info(
        "[layers_redraw] layer=%s sparse=%s area_pct=%.2f bbox_fill=%.3f "
        "route_requested=%s route_chosen=%s provider=%s",
        layer_name, sparse, area_pct, bbox_fill,
        route, chosen_route, type(img_provider).__name__,
    )

    sparse_crop_routes = {
        RedrawRoute.SPARSE_BBOX_CROP,
        RedrawRoute.SPARSE_PER_INSTANCE,
    }

    refined_alpha = None
    source_context = None
    processed_refined_child_count = 0
    redraw_estimated_cost_usd = 0.0
    redraw_cost_cap_reached = False
    if refinement_path_available:
        source_context = _resolve_source_context_image(
            artwork_dir=artwork_dir,
            manifest_data=manifest_data,
            expected_size=src_rgba.size,
        )
    if preflight_skip_reason:
        rgba = src_rgba.copy()
    elif refinement_path_available:
        rgba = Image.new("RGBA", src_rgba.size, (0, 0, 0, 0))
        refined_alpha = Image.new("L", src_alpha.size, 0)
        for child_index, child_mask in enumerate(refinement.child_masks, start=1):
            if (
                max_redraw_cost_usd > 0
                and redraw_estimated_cost_usd >= max_redraw_cost_usd
            ):
                redraw_cost_cap_reached = True
                break
            child_geometry = analyze_alpha_geometry(child_mask)
            crop_box = child_geometry.bbox
            if crop_box.w <= 0 or crop_box.h <= 0:
                continue
            if source_context is not None:
                crop_box = _pad_crop_box(
                    crop_box,
                    src_rgba.size[0],
                    src_rgba.size[1],
                    padding=max(8, round(max(crop_box.w, crop_box.h) * 0.5)),
                )
                box = (
                    crop_box.x,
                    crop_box.y,
                    crop_box.x + crop_box.w,
                    crop_box.y + crop_box.h,
                )
                source_crop = source_context.crop(box).convert("RGB")
                crop_alpha = child_mask.crop(box).convert("L")
                edit_matte = _build_flower_edit_matte(source_crop, crop_alpha)
                removal_matte = _build_flower_removal_matte(
                    source_crop,
                    crop_alpha,
                    edit_matte,
                )
                crop_out, _result = await _redraw_source_context_with_edit_matte(
                    source_crop=source_crop,
                    edit_matte=edit_matte,
                    removal_matte=removal_matte,
                    instruction=instruction,
                    provider_inst=img_provider,
                    tradition=tradition,
                    target_description=target.info.description,
                    quality=quality,
                    input_fidelity=input_fidelity,
                    output_format=output_format,
                    debug_artifacts=debug_artifacts,
                    debug_child_index=child_index,
                    target_palette=target_palette,
                )
                cost_usd = _image_result_cost_usd(_result)
                if cost_usd is not None:
                    redraw_estimated_cost_usd += cost_usd
                output_alpha = crop_out.split()[-1]
                _paste_crop_preserving_alpha(rgba, crop_out, output_alpha, crop_box)
                refined_alpha.paste(output_alpha, (crop_box.x, crop_box.y))
            else:
                crop_rgba, crop_alpha = _crop_rgba_with_alpha(
                    src_rgba,
                    child_mask,
                    crop_box,
                )
                crop_flat, _crop_bg = _flatten_layer(
                    crop_rgba,
                    background_strategy=background_strategy,
                )
                crop_out, _result = await _redraw_via_inpaint_mask(
                    flat_img=crop_flat,
                    src_alpha=crop_alpha,
                    canvas_size=crop_rgba.size,
                    instruction=instruction,
                    provider_inst=img_provider,
                    tradition=tradition,
                    target_description=target.info.description,
                    quality=quality,
                    input_fidelity=input_fidelity,
                    output_format=output_format,
                    resize_to_api_size=False,
                )
                cost_usd = _image_result_cost_usd(_result)
                if cost_usd is not None:
                    redraw_estimated_cost_usd += cost_usd
                _paste_crop_preserving_alpha(rgba, crop_out, crop_alpha, crop_box)
                refined_alpha.paste(crop_alpha, (crop_box.x, crop_box.y))
            processed_refined_child_count += 1
            if (
                max_redraw_cost_usd > 0
                and redraw_estimated_cost_usd >= max_redraw_cost_usd
            ):
                redraw_cost_cap_reached = True
    elif chosen_route == "inpaint" and redraw_plan.route in sparse_crop_routes:
        rgba = Image.new("RGBA", src_rgba.size, (0, 0, 0, 0))
        for crop_box in redraw_plan.crop_boxes:
            crop_rgba, crop_alpha = _crop_rgba_and_alpha(src_rgba, crop_box)
            crop_flat, _crop_bg = _flatten_layer(
                crop_rgba, background_strategy=background_strategy
            )
            crop_out, _result = await _redraw_via_inpaint_mask(
                flat_img=crop_flat,
                src_alpha=crop_alpha,
                canvas_size=crop_rgba.size,
                instruction=instruction,
                provider_inst=img_provider,
                tradition=tradition,
                target_description=target.info.description,
                quality=quality,
                input_fidelity=input_fidelity,
                output_format=output_format,
                resize_to_api_size=False,
            )
            _paste_crop_preserving_alpha(rgba, crop_out, crop_alpha, crop_box)
    elif chosen_route == "inpaint":
        # 4-5. Mask-aware inpaint path (B2 + B3 + B5 + B8 in spec).
        rgba_with_alpha, _result = await _redraw_via_inpaint_mask(
            flat_img=flat,
            src_alpha=src_alpha,
            canvas_size=(canvas_w, canvas_h),
            instruction=instruction,
            provider_inst=img_provider,
            tradition=tradition,
            target_description=target.info.description,
            quality=quality,
            input_fidelity=input_fidelity,
            output_format=output_format,
        )
        # _redraw_via_inpaint_mask returns RGBA at canvas size with the
        # model's (cream-bg) painted output but WITHOUT the source alpha
        # re-applied. Step 7 below handles preserve_alpha re-application.
        rgba = rgba_with_alpha
    else:
        # 4-5. Legacy img2img path — unchanged from v0.18 behavior.
        prompt = _build_redraw_prompt(
            instruction,
            [target.info.description],
            tradition=tradition,
            canvas_size=canvas_size_hint,
            background_strategy=background_strategy,
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
            flat.save(fh.name, "PNG")
            ref_b64 = base64.b64encode(Path(fh.name).read_bytes()).decode()
        try:
            Path(fh.name).unlink(missing_ok=True)
        except Exception:
            pass

        # v0.20.1 — quality/input_fidelity/output_format honored on img2img too
        gen_kwargs = {"tradition": tradition, "reference_image_b64": ref_b64}
        if quality:
            gen_kwargs["quality"] = quality
        if input_fidelity:
            gen_kwargs["input_fidelity"] = input_fidelity
        if output_format:
            gen_kwargs["output_format"] = output_format

        requires_masked_edit = bool(
            edit_caps
            and edit_caps.requires_mask_for_edits
            and has_inpaint
        )
        if requires_masked_edit:
            # gpt-image-2 rejects maskless /images/edits. Keep the user-facing
            # img2img route semantics by sending a full-canvas edit mask.
            all_edit_alpha = Image.new("L", flat.size, 255)
            rgba_with_alpha, _result = await _redraw_via_inpaint_mask(
                flat_img=flat,
                src_alpha=all_edit_alpha,
                canvas_size=(canvas_w, canvas_h),
                instruction=instruction,
                provider_inst=img_provider,
                tradition=tradition,
                target_description=target.info.description,
                quality=quality,
                input_fidelity=input_fidelity,
                output_format=output_format,
            )
            rgba = rgba_with_alpha
        else:
            result = await img_provider.generate(prompt, **gen_kwargs)

            # 6. Decode + aspect-preserving fit (replaces blanket LANCZOS warp)
            raw = base64.b64decode(result.image_b64)
            if result.mime and "svg" in result.mime:
                # SVG fallback only — preserved for unusual mock branches
                out_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            else:
                import io as _io

                out_img = Image.open(_io.BytesIO(raw))

            out_img = _fit_into_canvas(out_img, (canvas_w, canvas_h), bg_rgb)
            rgba = out_img.convert("RGBA")

    # 7. Optionally re-apply original alpha
    if preserve_alpha:
        output_alpha = refined_alpha if refined_alpha is not None else src_alpha
        # Resize alpha to match if canvas resized (rare; manifest dims drive both)
        if output_alpha.size != rgba.size:
            output_alpha = output_alpha.resize(rgba.size, Image.LANCZOS)
        rgba.putalpha(output_alpha)

    quality_report = evaluate_redraw_quality(
        src_rgba,
        rgba,
        description=target.info.description,
        instruction=instruction,
        refinement_applied=refinement_path_available,
        refined_child_count=processed_refined_child_count,
        refined_coverage_pct=refinement.metrics.get("refined_coverage_pct", 0.0)
        if refinement_path_available
        else 0.0,
        mask_granularity_score=refinement.metrics.get(
            "mask_granularity_score", 0.0
        ),
    )
    quality_failures = list(quality_report.failures)
    quality_gate_passed = quality_report.passed
    if preflight_skip_reason:
        quality_failures.append(preflight_skip_reason)
        quality_gate_passed = False

    if not quality_gate_passed:
        logger.warning(
            "redraw quality gate failed for layer=%s failures=%s metrics=%s",
            layer_name,
            quality_failures,
            quality_report.metrics,
        )
    actual_redraw_route = (
        RedrawRoute.SPARSE_PER_INSTANCE
        if refinement_path_available
        else redraw_plan.route
        if chosen_route == "inpaint"
        else RedrawRoute.DENSE_FULL_CANVAS
    )
    redraw_advisory = {
        "redraw_route": actual_redraw_route.value,
        "geometry_redraw_route": redraw_plan.route.value,
        "route_requested": route,
        "route_chosen": chosen_route,
        "sparse_detected": redraw_plan.route != RedrawRoute.DENSE_FULL_CANVAS,
        "area_pct": area_pct,
        "bbox_fill": bbox_fill,
        "component_count": geometry.component_count,
        "provider_requires_mask_for_edits": bool(
            edit_caps and edit_caps.requires_mask_for_edits
        ),
        "quality_gate_passed": quality_gate_passed,
        "quality_failures": quality_failures,
        "redraw_skipped": bool(preflight_skip_reason),
        "redraw_skip_reason": preflight_skip_reason,
        "refinement_applied": refinement_path_available,
        "refinement_reason": refinement.reason,
        "refinement_strategy": refinement.strategy,
        "refinement_source_context_used": bool(
            refinement_path_available and source_context is not None
        ),
        "refinement_edit_matte": "small_botanical_evidence"
        if refinement_path_available and source_context is not None
        else "child_alpha"
        if refinement_path_available
        else "none",
        "refinement_replacement_matte": "small_botanical_removal"
        if refinement_path_available and source_context is not None
        else "none",
        "refinement_target_palette": target_palette
        if refinement_path_available
        else "none",
        "refinement_composition": "small_botanical_evidence_paint_cover"
        if refinement_path_available and source_context is not None
        else "generated_patch",
        "refined_child_count": processed_refined_child_count,
        "max_refinement_children": max_refinement_children,
        "redraw_cost_cap_usd": max_redraw_cost_usd,
        "redraw_cost_cap_reached": redraw_cost_cap_reached,
        "redraw_estimated_cost_usd": round(redraw_estimated_cost_usd, 6),
        "mask_granularity_score": refinement.metrics.get(
            "mask_granularity_score", 0.0
        ),
    }

    # 8. Decide output path (v0.18.0 3-way resolution).
    if in_place:
        out_name = layer_name
        out_path = Path(artwork_dir) / f"{layer_name}.png"
    elif output_layer_name:
        out_name = output_layer_name
        out_path = Path(artwork_dir) / f"{output_layer_name}.png"
    else:
        out_name = f"{layer_name}_redrawn"
        out_path = Path(artwork_dir) / f"{out_name}.png"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(str(out_path), "PNG")
    final_source_pasteback_path = ""
    source_pasteback_error = ""
    if debug_artifacts and source_context is not None:
        try:
            source_pasteback = source_context.convert("RGBA")
            source_pasteback.alpha_composite(rgba.convert("RGBA"))
            final_source_pasteback_path = str(
                debug_artifacts["dir"] / "final_source_pasteback.png"
            )
            source_pasteback.save(final_source_pasteback_path)
        except Exception as exc:
            source_pasteback_error = str(exc)
    _write_redraw_debug_summary(
        debug_artifacts,
        status="completed",
        advisory=redraw_advisory,
        output_path=str(out_path),
        final_source_pasteback_path=final_source_pasteback_path,
        source_pasteback_error=source_pasteback_error,
    )

    # v0.18.0: manifest update happens whenever the caller is NOT in legacy
    # in-place mode. Both the auto-derived else branch and the explicit
    # output_layer_name branch append to the manifest.
    non_destructive = not in_place

    # Hybrid alpha mask still applies for legacy `extract`-mode layers whose
    # dominant_colors are stored — keep behavior parity across all branches.
    _maybe_apply_legacy_color_mask(artwork_dir, manifest_data, target, out_path)

    # 9. Manifest update branch.
    #
    # Legacy in-place (``in_place=True``) mutates the source layer in place
    # and skips manifest mutation. Both the auto-derived else branch and the
    # explicit ``output_layer_name`` branch take the non-destructive path:
    # write a new file + append a manifest entry.
    if not non_destructive:
        # Legacy in-place: mutate target, no manifest changes.
        target.image_path = str(out_path)
        setattr(target, "redraw_advisory", redraw_advisory)
        return target

    # Non-destructive (auto-derived ``<layer>_redrawn`` or explicit
    # ``output_layer_name``): append manifest entry. Capture the assigned
    # z_index so the in-memory LayerResult agrees with disk — otherwise next
    # load_manifest silently moves the layer (P1 finding, 2026-04-25 review).
    assigned_z = target.info.z_index
    try:
        assigned_z = _add_or_replace_layer_in_manifest(
            artwork_dir,
            new_name=out_name,
            template=target.info,
            description=f"Redraw of {layer_name}: {instruction[:60]}",
        )
    except Exception as exc:
        logger.warning("redraw: manifest update failed (non-fatal): %s", exc)

    new_info = LayerInfo(
        name=out_name,
        description=target.info.description,
        z_index=assigned_z,
        content_type=target.info.content_type,
        semantic_path=target.info.semantic_path,
        blend_mode=target.info.blend_mode,
    )
    result = LayerResult(info=new_info, image_path=str(out_path))
    setattr(result, "redraw_advisory", redraw_advisory)
    return result


def _maybe_apply_legacy_color_mask(
    artwork_dir: str, manifest_data: dict, target: LayerResult, out_path: Path
) -> None:
    """Hybrid alpha mask for legacy `extract`-mode layers (dominant_colors).

    Lifted verbatim from the old redraw_layer body so the legacy path stays
    bit-identical for backwards compatibility.
    """
    source_img_name = manifest_data.get("source_image", "")
    if not (source_img_name and target.info.dominant_colors):
        return
    source_path = Path(artwork_dir) / source_img_name
    if not source_path.exists():
        source_path = Path(artwork_dir).parent / source_img_name
    if not source_path.exists():
        return
    from PIL import Image as _PIL

    from vulca.layers.mask import build_color_mask

    source_img = _PIL.open(str(source_path))
    gen_img = _PIL.open(str(out_path))
    mask = build_color_mask(source_img, target.info, tolerance=30)
    r, g, b, _ = gen_img.convert("RGBA").split()
    hybrid = _PIL.merge("RGBA", (r, g, b, mask))
    hybrid.save(str(out_path))


async def redraw_merged(
    artwork: LayeredArtwork,
    *,
    layer_names: list[str],
    instruction: str,
    merged_name: str = "merged",
    provider: str = "gemini",
    tradition: str = "default",
    api_key: str = "",
    artwork_dir: str,
    re_split: bool = False,
    model: str = "",
    quality: str = "",
    input_fidelity: str = "",
    output_format: str = "",
) -> LayerResult | list[LayerResult]:
    """Merge selected layers, redraw via img2img, return as single new layer.

    Composites the selected layers into a temporary file, uses that as the
    img2img reference, generates a new image, and returns it as a LayerResult
    with name=merged_name and z_index=min of selected layers.
    """
    from vulca.layers.blend import blend_layers
    from vulca.providers import get_image_provider

    name_set = set(layer_names)
    selected: list[LayerResult] = [lr for lr in artwork.layers if lr.info.name in name_set]
    found_names = {lr.info.name for lr in selected}
    missing = name_set - found_names
    if missing:
        raise ValueError(
            f"Layers not found in artwork: {sorted(missing)} "
            f"(available: {[l.info.name for l in artwork.layers]})"
        )

    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    width = manifest.get("width", 1024)
    height = manifest.get("height", 1024)

    merged_img = blend_layers(selected, width=width, height=height)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        merged_img.save(tmp_file.name)
        tmp_file.close()
        ref_b64 = base64.b64encode(Path(tmp_file.name).read_bytes()).decode()

        descriptions = [lr.info.description for lr in selected]
        prompt = _build_redraw_prompt(
            instruction,
            descriptions,
            tradition=tradition,
            canvas_size=f"{width}x{height}",
        )

        # Provider-aware api_key (Patch 6 from spec, folded in)
        img_provider = get_image_provider(provider, api_key=api_key)
        # v0.20.1 — per-call model/quality override; same plumbing as redraw_layer
        if model and hasattr(img_provider, "model"):
            img_provider.model = model
        gen_kwargs = {"tradition": tradition, "reference_image_b64": ref_b64}
        if quality:
            gen_kwargs["quality"] = quality
        if input_fidelity:
            gen_kwargs["input_fidelity"] = input_fidelity
        if output_format:
            gen_kwargs["output_format"] = output_format
        result = await img_provider.generate(prompt, **gen_kwargs)
    finally:
        try:
            Path(tmp_file.name).unlink(missing_ok=True)
        except Exception:
            pass

    out_path = Path(artwork_dir) / f"{merged_name}.png"
    # Aspect-preserving fit (codex 2026-04-25 P2 — redraw_merged was using
    # blanket LANCZOS warp via _save_as_rgba, asymmetric with the new
    # redraw_layer fit logic). Letterbox transparent so merged result keeps
    # alpha-stack semantics for downstream composite.
    _save_as_rgba_fit(
        result.image_b64, result.mime, out_path,
        width=width, height=height,
    )

    min_z = min(lr.info.z_index for lr in selected)
    merged_info = LayerInfo(
        name=merged_name,
        description=f"Merged redraw of: {', '.join(layer_names)}",
        z_index=min_z,
        content_type="subject",
    )
    if not re_split:
        return LayerResult(info=merged_info, image_path=str(out_path))

    from vulca.layers.analyze import analyze_layers
    from vulca.layers.split import split_extract
    import shutil

    new_layers = await analyze_layers(str(out_path), api_key=api_key)
    resplit_dir = Path(artwork_dir) / f"_resplit_{merged_name}"
    results = split_extract(str(out_path), new_layers, output_dir=str(resplit_dir))

    final_results = []
    for r in results:
        dest = Path(artwork_dir) / Path(r.image_path).name
        if Path(r.image_path) != dest:
            shutil.move(str(r.image_path), str(dest))
        r.image_path = str(dest)
        final_results.append(r)

    shutil.rmtree(str(resplit_dir), ignore_errors=True)
    out_path.unlink(missing_ok=True)

    return final_results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _save_as_rgba(
    image_b64: str, mime: str, out_path: Path,
    *, width: int = 0, height: int = 0,
) -> None:
    """Decode image_b64, convert to RGBA, resize to canvas if needed, save as PNG.

    Legacy helper — uses LANCZOS warp on size mismatch. Kept for any
    out-of-tree callers; new code should use _save_as_rgba_fit which is
    aspect-preserving.
    """
    from PIL import Image
    import io

    raw = base64.b64decode(image_b64)

    if mime and "svg" in mime:
        # SVG from mock provider — create transparent placeholder at target size
        w = width or 100
        h = height or 100
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    else:
        img = Image.open(io.BytesIO(raw))

    img = img.convert("RGBA")
    if width and height and img.size != (width, height):
        img = img.resize((width, height), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), format="PNG")


def _save_as_rgba_fit(
    image_b64: str, mime: str, out_path: Path,
    *, width: int = 0, height: int = 0,
) -> None:
    """Aspect-preserving variant of _save_as_rgba — letterboxes with alpha=0
    when provider output's aspect differs from the canvas. Symmetric with
    redraw_layer's flow."""
    from PIL import Image
    import io

    raw = base64.b64decode(image_b64)

    if mime and "svg" in mime:
        w = width or 100
        h = height or 100
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    else:
        img = Image.open(io.BytesIO(raw))

    img = img.convert("RGBA")
    if width and height and img.size != (width, height):
        img = _fit_into_canvas(img, (width, height), bg_rgb=None)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), format="PNG")
