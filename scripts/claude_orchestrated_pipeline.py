#!/usr/bin/env python3
"""Claude-orchestrated segmentation pipeline.

Stage 0: Claude produces layer plan (JSON, externally written).
Stage 1: Grounding DINO detects bboxes per Claude's labels.
Stage 2: SAM ViT-L extracts masks per bbox.
Stage 3: Output per-layer RGBA PNGs + merged manifest.

Usage:
  python scripts/claude_orchestrated_pipeline.py <slug>

Reads: assets/showcase/plans/<slug>.json (Claude's plan)
Writes: assets/showcase/layers_v2/<slug>/*.png + manifest.json
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

# Module-level lock shared by all 4 @lru_cache'd model loaders.
# Protects the first-call race where two threads simultaneously miss the
# cache and each trigger a multi-second from_pretrained(). Lock does NOT
# protect subsequent cache hits (lru_cache has its own read lock for those).
_MODEL_LOCK = threading.Lock()

import numpy as np
import torch
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
PLANS_DIR = REPO / "assets" / "showcase" / "plans"
OUT_DIR = REPO / "assets" / "showcase" / "layers_v2"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
SAM_CKPT = "/tmp/sam_vit_l.pth"

# Phase 1.9: single source of truth for orchestrated manifest version.
# Distinct from `src/vulca/layers/manifest.py:MANIFEST_VERSION=3` which governs
# the LAYERED generate path (different pipeline). Consumers (showcase viewer,
# MCP tools) should import from here.
ORCHESTRATED_MANIFEST_VERSION = 5


# ── Domain routing: which detector chain to use per image domain ──
# "person_chain" is the ORDERED fallback list for person entities.
# Empty chain = image has no people (space/landscape/abstract).
DOMAIN_PROFILES = {
    # ── Photography: YOLO works great, DINO as fallback ──
    "space_photograph":        {"person_chain": [],                "object_thresh": 0.20},
    "portrait_photograph":     {"person_chain": ["yolo", "dino"],  "object_thresh": 0.20},
    "historical_bw_photo":     {"person_chain": ["yolo", "dino"],  "object_thresh": 0.20},
    "news_photograph_2024":    {"person_chain": ["yolo", "dino"],  "object_thresh": 0.20},
    "photojournalism_1993":    {"person_chain": ["yolo", "dino"],  "object_thresh": 0.15},
    "booking_photograph":      {"person_chain": ["yolo", "dino"],  "object_thresh": 0.20},
    "official_portrait_photo": {"person_chain": ["yolo", "dino"],  "object_thresh": 0.20},

    # ── Paintings: YOLO fails (cross-depiction gap), DINO primary ──
    "renaissance_painting":         {"person_chain": ["dino"],         "object_thresh": 0.15},
    "baroque_painting":             {"person_chain": ["yolo", "dino"], "object_thresh": 0.15},
    "renaissance_fresco":           {"person_chain": ["yolo", "dino"], "object_thresh": 0.15},
    "expressionist_painting":       {"person_chain": ["dino"],         "object_thresh": 0.15},
    "post_impressionist_painting":  {"person_chain": ["dino"],         "object_thresh": 0.15},
    "impressionist_painting":       {"person_chain": ["dino"],         "object_thresh": 0.15},
    "surrealist_painting":          {"person_chain": ["dino"],         "object_thresh": 0.15},
    "art_nouveau_painting":         {"person_chain": ["dino"],         "object_thresh": 0.15},
    "american_realism_painting":    {"person_chain": ["yolo", "dino"], "object_thresh": 0.20},
    "american_regionalist_painting":{"person_chain": ["yolo", "dino"], "object_thresh": 0.20},
    "japanese_woodblock":           {"person_chain": ["dino"],         "object_thresh": 0.15},
    "chinese_gongbi_scroll":        {"person_chain": ["dino"],         "object_thresh": 0.12, "tile": True},
    "south_asian_fresco":           {"person_chain": ["yolo", "dino"], "object_thresh": 0.15},
}

DEFAULT_PROFILE = {"person_chain": ["yolo", "dino"], "object_thresh": 0.20}

# Person-like prompts for DINO fallback on art domains
DINO_PERSON_PROMPTS = "person . human figure . face . body ."

# Minimum fraction of plan entities that must be detected to mark status="ok"
SUCCESS_RATE_THRESHOLD = 0.70


# ── Module-level model cache: loaders are expensive (~5-20s each) ──
# All @lru_cache'd on device so repeated slug runs reuse the same instance.

@functools.lru_cache(maxsize=2)
def load_grounding_dino(device="mps"):
    with _MODEL_LOCK:
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
        proc = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-tiny")
        model = AutoModelForZeroShotObjectDetection.from_pretrained(
            "IDEA-Research/grounding-dino-tiny"
        ).to(device).eval()
        return proc, model


@functools.lru_cache(maxsize=1)
def load_yolo():
    """YOLO26 for person detection — best person recall + precise bboxes."""
    with _MODEL_LOCK:
        from ultralytics import YOLO
        return YOLO("yolo26m.pt")


# SegFormer face-parsing (CelebAMask-HQ 19 classes)
FACE_PARSE_LABELS = {
    0: "background", 1: "skin", 2: "nose", 3: "eye_g", 4: "l_eye",
    5: "r_eye", 6: "l_brow", 7: "r_brow", 8: "l_ear", 9: "r_ear",
    10: "mouth", 11: "u_lip", 12: "l_lip", 13: "hair", 14: "hat",
    15: "ear_r", 16: "neck_l", 17: "neck", 18: "cloth"
}
FACE_MERGE_MAP = {
    "l_eye": "eyes", "r_eye": "eyes",
    "l_brow": "eyebrows", "r_brow": "eyebrows",
    "u_lip": "lips", "l_lip": "lips", "mouth": "lips",
    "l_ear": "ears", "r_ear": "ears", "ear_r": "ears",
    "neck_l": "neck",
}
FACE_PART_MIN_PX = 80  # below this, merge into skin


@functools.lru_cache(maxsize=2)
def load_face_parser(device="mps"):
    with _MODEL_LOCK:
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
        proc = SegformerImageProcessor.from_pretrained("jonathandinu/face-parsing")
        model = SegformerForSemanticSegmentation.from_pretrained(
            "jonathandinu/face-parsing"
        ).to(device).eval()
        return proc, model


def _run_face_parser(face_proc, face_model, device, crop_np):
    """Run SegFormer on a crop, return seg_map (HxW class indices)."""
    from PIL import Image
    import torch as _t
    pil = Image.fromarray(crop_np)
    inputs = face_proc(images=pil, return_tensors="pt").to(device)
    with _t.no_grad():
        outputs = face_model(**inputs)
    upsampled = _t.nn.functional.interpolate(
        outputs.logits, size=crop_np.shape[:2], mode="bilinear", align_corners=False
    )
    return upsampled.argmax(dim=1).cpu().numpy()[0]


def _find_face_bbox_from_segmap(seg_map, padding=0.3):
    """Anchor on nose+eyes (classes 2,4,5) to find tight face bbox.

    Phase 1.9: multi-tier fallback when pass-1 SegFormer doesn't confidently
    emit nose/eyes (common on small/occluded/unusual faces — hoods, helmets,
    side profiles, low-light). Returns (x1,y1,x2,y2) in seg_map coords, or None.

    Tier 1: nose + eyes (classes 2,4,5) — tightest, highest signal
    Tier 2: all fine face classes (1,2,4-7,11,12) — lips/brows help
    Tier 3: skin (class 1) alone — works whenever head is visible at all;
            catches 46 previously-skipped cases across the 47-image corpus
    """
    # Tier 1: strict anchor
    anchor = np.isin(seg_map, [2, 4, 5])  # nose, l_eye, r_eye
    if anchor.sum() >= 8:        # Phase 1.9: 20 → 8 (catch small faces)
        return _bbox_from_anchor(anchor, seg_map.shape)

    # Tier 2: broader face classes
    anchor = np.isin(seg_map, [1, 2, 4, 5, 6, 7, 11, 12])
    if anchor.sum() >= 30:       # Phase 1.9: 50 → 30
        return _bbox_from_anchor(anchor, seg_map.shape)

    # Tier 3 (Phase 1.9 new): skin-only geometric fallback. If the head is
    # visible at all, SegFormer reliably emits skin — use its centroid as
    # face anchor. Minimum 500 px to avoid noise triggers.
    skin = (seg_map == 1)
    if skin.sum() >= 500:
        return _bbox_from_anchor(skin, seg_map.shape)

    return None


def _bbox_from_anchor(anchor, shape):
    """Expand from anchor centroid by 4x its extent to approximate face bbox."""
    ys, xs = np.where(anchor)
    cy, cx = int(ys.mean()), int(xs.mean())
    anchor_h = ys.max() - ys.min()
    anchor_w = xs.max() - xs.min()
    face_size = max(anchor_h, anchor_w, 50) * 4
    H, W = shape
    x1 = max(0, cx - face_size // 2)
    x2 = min(W, cx + face_size // 2)
    y1 = max(0, cy - face_size // 2)
    y2 = min(H, cy + face_size // 2)
    return (x1, y1, x2, y2)


def face_parse_person(face_proc, face_model, device, img_np, person_bbox, min_face_px=80):
    """Two-pass face-parsing: person crop -> face anchor -> tight face crop -> fine parts.

    Phase 1.9: person crop is upscaled to 512px min side before pass 1.
    SegFormer was trained on 512×512 inputs; crops smaller than that lose
    face resolution inside the model's own resize. For a 150-px person
    crop, the face (~50 px) becomes ~170 px after 3.4× upscale, enough to
    trigger nose/eye detection that was previously silently lost.

    Returns dict part_name -> HxW bool mask in full image coords.
    """
    from PIL import Image as _PILImage
    x1, y1, x2, y2 = person_bbox
    person_crop = img_np[y1:y2, x1:x2]
    if person_crop.shape[0] < min_face_px or person_crop.shape[1] < min_face_px:
        return {}

    # Phase 1.9: upscale to give SegFormer enough pixels.
    ch, cw = person_crop.shape[:2]
    min_side = min(ch, cw)
    upscale_factor = max(1.0, 512.0 / min_side)
    if upscale_factor > 1.05:
        new_w = int(cw * upscale_factor)
        new_h = int(ch * upscale_factor)
        pil = _PILImage.fromarray(person_crop).resize(
            (new_w, new_h), _PILImage.LANCZOS
        )
        person_crop_seg_input = np.array(pil)
    else:
        person_crop_seg_input = person_crop

    # Pass 1: parse full person crop (coarse — finds skin/hair/hat + weak anchor)
    seg_person_upscaled = _run_face_parser(
        face_proc, face_model, device, person_crop_seg_input
    )
    # Resize seg back to original crop size for downstream coord math
    if upscale_factor > 1.05:
        seg_pil = _PILImage.fromarray(seg_person_upscaled.astype(np.uint8)).resize(
            (cw, ch), _PILImage.NEAREST
        )
        seg_person = np.array(seg_pil)
    else:
        seg_person = seg_person_upscaled

    # Find tight face bbox within person crop
    face_bbox_in_crop = _find_face_bbox_from_segmap(seg_person)
    full_shape = img_np.shape[:2]
    parts = {}

    def _accumulate(seg, offset_y, offset_x, crop_h, crop_w):
        """Add seg_map classes to parts dict, translating to full image coords."""
        for cls_id in np.unique(seg):
            name = FACE_PARSE_LABELS.get(int(cls_id), f"cls_{cls_id}")
            if name == "background":
                continue
            merged_name = FACE_MERGE_MAP.get(name, name)
            crop_mask = (seg == cls_id)
            if crop_mask.sum() < 10:
                continue
            full_mask = np.zeros(full_shape, dtype=bool)
            full_mask[offset_y:offset_y + crop_h, offset_x:offset_x + crop_w] = crop_mask
            parts[merged_name] = parts.get(merged_name, np.zeros(full_shape, dtype=bool)) | full_mask

    # Accumulate coarse (skin/hair/hat/cloth/neck from person pass)
    _accumulate(seg_person, y1, x1, person_crop.shape[0], person_crop.shape[1])

    # Pass 2: if face bbox found, re-parse tight face crop (catches eyes/nose/lips/brows)
    if face_bbox_in_crop is not None:
        fx1, fy1, fx2, fy2 = face_bbox_in_crop
        face_crop = person_crop[fy1:fy2, fx1:fx2]
        if face_crop.shape[0] >= 40 and face_crop.shape[1] >= 40:
            # Phase 1.9: upscale face crop to 512 min side for pass 2 too.
            fh, fw = face_crop.shape[:2]
            f_up = max(1.0, 512.0 / min(fh, fw))
            if f_up > 1.05:
                face_in = np.array(
                    _PILImage.fromarray(face_crop).resize(
                        (int(fw * f_up), int(fh * f_up)), _PILImage.LANCZOS
                    )
                )
            else:
                face_in = face_crop
            seg_face_upscaled = _run_face_parser(
                face_proc, face_model, device, face_in
            )
            # Downsample seg back to face_crop native size
            if f_up > 1.05:
                seg_face = np.array(
                    _PILImage.fromarray(seg_face_upscaled.astype(np.uint8)).resize(
                        (fw, fh), _PILImage.NEAREST
                    )
                )
            else:
                seg_face = seg_face_upscaled
            # Only accumulate FINE parts (eyes/nose/lips/brows) — fine pass is more accurate
            fine_classes = {4, 5, 2, 11, 12, 10, 6, 7}  # eyes, nose, lips, brows
            # Zero out non-fine classes to avoid polluting coarse results
            fine_seg = np.where(np.isin(seg_face, list(fine_classes)), seg_face, 0)
            # For fine parts, REPLACE (not union) to prefer the tight-crop result
            face_offset_y = y1 + fy1
            face_offset_x = x1 + fx1
            for cls_id in fine_classes:
                mask = (fine_seg == cls_id)
                if mask.sum() < 10:
                    continue
                merged_name = FACE_MERGE_MAP.get(FACE_PARSE_LABELS[cls_id], FACE_PARSE_LABELS[cls_id])
                full_mask = np.zeros(full_shape, dtype=bool)
                full_mask[face_offset_y:face_offset_y + face_crop.shape[0],
                          face_offset_x:face_offset_x + face_crop.shape[1]] = mask
                # Union with coarse (in case eye was also partially detected in coarse)
                parts[merged_name] = parts.get(merged_name, np.zeros(full_shape, dtype=bool)) | full_mask

    return parts


def detect_persons_yolo(yolo_model, img_path, min_conf=0.25):
    """Return list of (bbox, conf) for all detected persons, sorted by x-center."""
    r = yolo_model(img_path, conf=min_conf, classes=[0], verbose=False)[0]
    persons = []
    for b in r.boxes:
        xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
        persons.append((xyxy, float(b.conf[0])))
    persons.sort(key=lambda p: (p[0][0] + p[0][2]) / 2)
    return persons


def detect_persons_dino(dino_proc, dino_model, device, img_pil, threshold=0.20):
    """Fallback person detector via Grounding DINO.
    Returns list of (bbox, conf) sorted by x-center, like YOLO output.
    Used when YOLO fails on stylized artwork (screaming figures, gold-wrapped
    couples, Renaissance nudes — all outside COCO's 'person' manifold).
    """
    inputs = dino_proc(images=img_pil, text=DINO_PERSON_PROMPTS,
                       return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = dino_model(**inputs)
    results = dino_proc.post_process_grounded_object_detection(
        outputs, inputs.input_ids,
        threshold=threshold, text_threshold=threshold,
        target_sizes=[img_pil.size[::-1]]
    )[0]
    persons = []
    for i in range(len(results["boxes"])):
        bbox = results["boxes"][i].cpu().numpy().astype(int).tolist()
        conf = float(results["scores"][i])
        persons.append((bbox, conf))
    # Dedupe: if any two bboxes have IoU > 0.5, keep higher score
    persons.sort(key=lambda p: -p[1])
    deduped = []
    for bbox, conf in persons:
        is_dup = False
        for kept_bbox, _ in deduped:
            if _iou(bbox, kept_bbox) > 0.5:
                is_dup = True
                break
        if not is_dup:
            deduped.append((bbox, conf))
    deduped.sort(key=lambda p: (p[0][0] + p[0][2]) / 2)
    return deduped


def _iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter == 0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)


def detect_persons_with_chain(chain, yolo_model, dino_proc, dino_model, device,
                               img_pil, img_path, yolo_conf=0.20, dino_conf=0.20):
    """Try detector chain (e.g., ['yolo', 'dino']) until persons found.

    Auto-adapts to image shape: small images (<384px) get 2x upscale for DINO.
    Extreme-aspect images skip person detection (usually landscapes without people).

    Returns: (persons, detector_used, attempts)
      - persons: list of (bbox, conf)
      - detector_used: str name of successful detector, or None
      - attempts: list of (name, count, conf_range) for reporting
    """
    W, H = img_pil.size
    use_upscale = needs_upscale(W, H)
    attempts = []
    for detector_name in chain:
        if detector_name == "yolo":
            persons = detect_persons_yolo(yolo_model, img_path, min_conf=yolo_conf)
        elif detector_name == "dino":
            if use_upscale:
                persons = detect_persons_upscaled(dino_proc, dino_model, device,
                                                   img_pil, threshold=dino_conf)
            else:
                persons = detect_persons_dino(dino_proc, dino_model, device, img_pil,
                                               threshold=dino_conf)
        else:
            attempts.append((detector_name, 0, "unknown detector"))
            continue
        conf_range = f"{min(p[1] for p in persons):.2f}-{max(p[1] for p in persons):.2f}" \
            if persons else "none"
        attempts.append((detector_name, len(persons), conf_range))
        if persons:
            return persons, detector_name, attempts
    return [], None, attempts


@functools.lru_cache(maxsize=2)
def _load_sam_model(device: str):
    """Cache the heavy SAM weights; predictor itself is cheap to build."""
    with _MODEL_LOCK:
        from segment_anything import sam_model_registry
        return sam_model_registry["vit_l"](checkpoint=SAM_CKPT).to(device)


def load_sam(device="mps"):
    """SAM ViT-L predictor — wraps cached model. Predictor state is image-specific."""
    from segment_anything import SamPredictor
    return SamPredictor(_load_sam_model(device))


# ── Image adaptation: upscale tiny images + tile extreme-aspect images ──
UPSCALE_MIN_SIDE = 384        # if min side < this, upscale 2x before detection
TILE_ASPECT_RATIO = 3.0       # if max/min > this, use tile inference
TILE_OVERLAP = 0.2            # 20% overlap between tiles


def needs_upscale(W: int, H: int) -> bool:
    return min(W, H) < UPSCALE_MIN_SIDE and max(W, H) < UPSCALE_MIN_SIDE * 3


def needs_tile(W: int, H: int) -> bool:
    return max(W, H) / max(min(W, H), 1) >= TILE_ASPECT_RATIO


def tile_image(img_pil, tile_size=None, overlap=TILE_OVERLAP):
    """Slice extreme-aspect image into overlapping square tiles.

    For 2560x120 scroll: yields tiles of size 120x120 (or configured),
    sliding along the long dimension with 20% overlap.

    Yields: (tile_pil, (ox, oy, ow, oh)) — tile + offset/size in original coords.
    """
    from PIL import Image
    W, H = img_pil.size
    if tile_size is None:
        tile_size = min(W, H)  # square tile sized to short side
    tile_size = min(tile_size, max(W, H))
    stride = int(tile_size * (1 - overlap))
    if stride < 1:
        stride = tile_size
    if W >= H:
        # horizontal scroll
        x = 0
        while x < W:
            x_end = min(x + tile_size, W)
            # shift last tile back to fit
            if x_end == W:
                x = max(0, W - tile_size)
                x_end = W
            tile = img_pil.crop((x, 0, x_end, H))
            yield tile, (x, 0, x_end - x, H)
            if x_end == W:
                break
            x += stride
    else:
        # vertical
        y = 0
        while y < H:
            y_end = min(y + tile_size, H)
            if y_end == H:
                y = max(0, H - tile_size)
                y_end = H
            tile = img_pil.crop((0, y, W, y_end))
            yield tile, (0, y, W, y_end - y)
            if y_end == H:
                break
            y += stride


def _nms_bboxes(detections, iou_threshold=0.5):
    """Non-max suppression on (bbox, score, phrase) tuples.
    Keeps higher-score detections; removes lower-score ones that overlap >threshold.
    """
    detections = sorted(detections, key=lambda d: -d[1])
    kept = []
    for d in detections:
        bbox, score, phrase = d
        is_dup = False
        for k in kept:
            if _iou(bbox, k[0]) > iou_threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(d)
    return kept


def detect_all_bboxes_tiled(dino_proc, dino_model, device, img_pil, labels, threshold=0.15):
    """Tile-based detection for extreme-aspect images.

    Run Grounding DINO on each tile, translate bboxes to full-image coords, NMS merge.
    """
    all_detections_per_label = {lbl: [] for lbl in labels}
    tile_count = 0
    for tile, (ox, oy, ow, oh) in tile_image(img_pil):
        tile_count += 1
        tile_assigned = detect_all_bboxes(dino_proc, dino_model, device, tile,
                                           labels, threshold=threshold)
        for lbl, (bbox, score, phrase) in tile_assigned.items():
            # Translate bbox from tile coords to full-image coords
            x1, y1, x2, y2 = bbox
            full_bbox = [x1 + ox, y1 + oy, x2 + ox, y2 + oy]
            all_detections_per_label[lbl].append((full_bbox, score, phrase))
    print(f"    Tile inference: {tile_count} tiles processed")

    # NMS per label, keep highest-score detection per label
    assigned = {}
    for lbl, dets in all_detections_per_label.items():
        if not dets:
            continue
        kept = _nms_bboxes(dets, iou_threshold=0.5)
        best = max(kept, key=lambda d: d[1])
        assigned[lbl] = best
    return assigned


def detect_all_bboxes_upscaled(dino_proc, dino_model, device, img_pil, labels, threshold=0.15):
    """Detection with 2x upscale for tiny images. Bboxes scaled back to original."""
    W, H = img_pil.size
    upscaled = img_pil.resize((W * 2, H * 2), Image.LANCZOS)
    assigned = detect_all_bboxes(dino_proc, dino_model, device, upscaled,
                                  labels, threshold=threshold)
    # Scale bboxes back to original resolution
    scaled = {}
    for lbl, (bbox, score, phrase) in assigned.items():
        x1, y1, x2, y2 = bbox
        scaled[lbl] = ([x1 // 2, y1 // 2, x2 // 2, y2 // 2], score, phrase)
    return scaled


def detect_persons_upscaled(dino_proc, dino_model, device, img_pil, threshold=0.20):
    """DINO person detection with 2x upscale for tiny images."""
    W, H = img_pil.size
    upscaled = img_pil.resize((W * 2, H * 2), Image.LANCZOS)
    persons = detect_persons_dino(dino_proc, dino_model, device, upscaled, threshold)
    return [([b[0] // 2, b[1] // 2, b[2] // 2, b[3] // 2], c) for b, c in persons]


def detect_all_bboxes(dino_proc, dino_model, device, img_pil, labels, threshold=0.15):
    """Single Grounding DINO pass with all labels jointly.

    Returns: dict label -> (bbox, score, matched_phrase) or None if no match.
    """
    # Join all labels with period separator (Grounding DINO convention)
    text = ". ".join(labels) + "."
    inputs = dino_proc(images=img_pil, text=text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = dino_model(**inputs)
    results = dino_proc.post_process_grounded_object_detection(
        outputs, inputs.input_ids,
        threshold=threshold, text_threshold=0.15,
        target_sizes=[img_pil.size[::-1]]
    )[0]

    # Match each detection back to the closest requested label
    # via substring overlap on the returned phrase
    assigned = {}  # label -> (bbox, score)
    det_scores = results["scores"].cpu().numpy()
    det_boxes = results["boxes"].cpu().numpy()
    det_labels = results.get("text_labels", results.get("labels", []))
    if hasattr(det_labels, "cpu"):
        det_labels = det_labels.cpu().numpy().tolist()
    # det_labels may be list of strings or ids
    for i in range(len(det_boxes)):
        phrase = det_labels[i] if isinstance(det_labels[i], str) else str(det_labels[i])
        # Find best matching label by word overlap
        phrase_words = set(phrase.lower().split())
        best_label = None
        best_overlap = 0
        for lbl in labels:
            lbl_words = set(lbl.lower().split())
            overlap = len(phrase_words & lbl_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_label = lbl
        if best_label is None:
            continue
        score = float(det_scores[i])
        # Keep highest-score detection per label
        if best_label not in assigned or score > assigned[best_label][1]:
            assigned[best_label] = (
                det_boxes[i].astype(int).tolist(),
                score,
                phrase,
            )
    return assigned


def detect_bbox(dino_proc, dino_model, device, img_pil, label, threshold=0.25):
    """Legacy single-label detection (kept for compatibility)."""
    assigned = detect_all_bboxes(dino_proc, dino_model, device, img_pil, [label], threshold)
    if label not in assigned:
        return None, 0.0
    bbox, score, _ = assigned[label]
    return bbox, score


def compute_quality_flags(
    *,
    pct: float,
    sam_score: float,
    bbox_fill: float,
    inside_ratio: float,
) -> tuple[list[str], str]:
    """v0.17.13 transparency gate for DINO-object segmentation results.

    Mirrors the hint-path gate (lines around the sam_bbox branch) into a
    pure helper so the DINO-object loop can apply the same suspect/detected
    logic. Pre-v0.17.13 this branch silently wrote `status: "detected"` even
    when SAM was low-confidence, leading to silent "the lanterns layer
    captured building structure" failures (γ Scottish iter 0 lanterns:
    sam_score 0.609, bbox_fill 0.256 → suspect).

    DINO-tier thresholds: looser than hint-path (0.05) because DINO bboxes
    are model-supplied and tend wider. Calibrated against γ Scottish 9-entity
    baseline (8 clean entities pass at sam>=0.93 / fill>=0.55, lanterns gets
    flagged).

    Returns:
        (quality_flags, status) — flags is a list of triggered conditions;
        status is "suspect" if any flag fired, else "detected".
    """
    flags: list[str] = []
    if pct < 0.05:
        flags.append("empty_mask")
    if sam_score < 0.70:
        flags.append("low_sam_score")
    if bbox_fill < 0.30:
        flags.append("low_bbox_fill")
    if inside_ratio < 0.60:
        flags.append("mask_outside_bbox")
    status = "suspect" if flags else "detected"
    return flags, status


def segment_bbox(sam_pred, bbox, multimask=True):
    """Run SAM with bbox prompt, return best mask + quality signals.

    Returns: (mask, sam_score, bbox_fill, inside_ratio)
    - bbox_fill: fraction of bbox pixels covered by mask (mask∩bbox / bbox)
    - inside_ratio: fraction of mask pixels inside bbox (mask∩bbox / mask)

    Low bbox_fill → mask too small for this bbox (likely wrong tiny object).
    Low inside_ratio → mask extends far outside bbox (likely picked wrong
    object whose centroid is elsewhere — classic sam_bbox failure mode).
    """
    box = np.array(bbox)
    masks, scores, _ = sam_pred.predict(box=box, multimask_output=multimask)
    x1, y1, x2, y2 = bbox
    bbox_area = max((x2 - x1) * (y2 - y1), 1)
    best_idx = max(
        range(len(masks)),
        key=lambda i: masks[i][y1:y2, x1:x2].sum() / bbox_area
    )
    mask = masks[best_idx]
    inside_px = int(mask[y1:y2, x1:x2].sum())
    total_px = max(int(mask.sum()), 1)
    return mask, float(scores[best_idx]), inside_px / bbox_area, inside_px / total_px


def hint_to_bbox_px(hint_pct, W: int, H: int) -> list[int]:
    """Convert normalized bbox hint [x1,y1,x2,y2] in [0,1] to pixel xyxy.

    Clamps to image bounds defensively; the schema validator already rejects
    out-of-range values but user-provided plans can't be trusted at runtime.

    Phase 1.9: guard against degenerate (zero-area) bbox from int() truncation
    on high-decimal hints in small images. E.g. [0.998, 0.998, 0.999, 0.999]
    on a 400px image → all coords = 399 → zero area. Widen by 1px if
    degenerate so SAM receives a valid box.
    """
    x1, y1, x2, y2 = hint_pct
    bx1 = max(0, min(W - 1, int(x1 * W)))
    by1 = max(0, min(H - 1, int(y1 * H)))
    bx2 = max(0, min(W - 1, int(x2 * W)))
    by2 = max(0, min(H - 1, int(y2 * H)))
    # Ensure non-degenerate area: at least 2x2 px.
    if bx2 <= bx1:
        bx2 = min(W - 1, bx1 + 1)
        if bx2 == bx1 and bx1 > 0:
            bx1 -= 1  # image too small at right edge; shrink left instead
    if by2 <= by1:
        by2 = min(H - 1, by1 + 1)
        if by2 == by1 and by1 > 0:
            by1 -= 1
    return [bx1, by1, bx2, by2]


def _z_index_for(semantic_path: str) -> int:
    """Derive z from semantic_path prefix (higher = foreground)."""
    rules = [
        ("foreground.", 80),
        ("subject.head.face.", 70),
        ("subject.head.face", 65),
        ("subject.head.", 60),
        ("subject.body.hands", 58),
        ("subject.body.", 55),
        ("subject.person[", 50),
        ("subject.", 45),
        ("background.", 10),
        ("background", 0),
    ]
    for prefix, z in rules:
        if semantic_path.startswith(prefix):
            return z
    return 50


def _is_descendant(sp: str, ancestor: str) -> bool:
    """Return True iff sp is nested strictly below ancestor via dotted path.

    Uses semantic_path prefix with trailing '.' to avoid false matches
    (e.g. `person[10]` is NOT descendant of `person[1]`).
    """
    return bool(ancestor) and sp.startswith(ancestor + ".")


def _is_person_path(sp: str) -> bool:
    """Phase 1.9 unified person-detection: a semantic_path is a person if any
    segment contains `person[` or `figure[` (latter for stylized art).
    Drives both the partition AND the Stage 4 face-parsing gate so they
    stay in sync.
    """
    return bool(sp) and ("person[" in sp or "figure[" in sp)


def _is_ancestor_or_descendant(sp_a: str, sp_b: str) -> bool:
    """Return True iff sp_a and sp_b are in the same ancestor/descendant chain.

    Phase 1.8: the hierarchical blocker rule must be BIDIRECTIONAL.
    Phase 1.5 only implemented "descendants don't block ancestors",
    but forgot the dual "ancestors don't block descendants".

    Consequence before this fix: face-parse sub-layers with negative z-boost
    (e.g. `cloth` z=46 under a parent person z=50) had their entire mask
    eaten by the parent's SAM mask, because the parent is NOT a descendant
    of the child (it's the ancestor), so the one-way rule didn't skip it.
    Observed: `bieber__cloth` area_pct=0.00% in every Bieber Coachella
    output; `__neck` would show the same bug when present.

    Fix: treat any ancestor/descendant relationship (either direction) as
    non-blocking. Unrelated layers (siblings, foreground/background) still
    block normally via z-order.
    """
    return _is_descendant(sp_a, sp_b) or _is_descendant(sp_b, sp_a)


def resolve_overlaps(layers_raw, unclaimed_threshold_pct: float = 2.0):
    """Assign per-pixel ownership across layers — hierarchical model.

    Rules (Phase 1.5 + Phase 1.8 correction):
    - Strictly higher-z UNRELATED layers block a layer's pixels.
    - Ancestor/descendant pairs (either direction) do NOT block each other.
    - Same-z siblings do NOT block each other (render order breaks ties).

    This is the correct model for agent-native editing: a parent layer
    contains the whole subject (woman keeps eyes/lips pixels); sub-layers
    are addressable overlays, not carve-outs. Sub-layers with negative
    z-boost (cloth, neck) also survive intact because the parent no longer
    eats them.

    Phase 1.6: a synthetic `residual` layer is emitted at z=1 when the
    unclaimed coverage exceeds `unclaimed_threshold_pct`, with
    `locked=True, quality_status="residual"`. This replaces the legacy
    "dump unclaimed into background" behavior that polluted bg with
    un-segmented subject pixels. Composite still reconstructs the original
    image pixel-perfectly (bg + residual + fg z-stack).

    Complexity: O(n²) in layer count, allocates one H×W bool array per
    pair. At n≈30 layers × 4MB per 2048² bool array this is fine. For
    crowd scenes (100+ layers) consider pre-sorting by -z and maintaining
    a cumulative non-descendant blocker to drop to O(n × avg_depth).
    """
    if not layers_raw:
        raise ValueError("empty layers")
    H, W = layers_raw[0]["mask"].shape

    claimed_any = np.zeros((H, W), dtype=bool)
    for layer in layers_raw:
        sp = layer.get("semantic_path", "")
        z = layer["z"]
        blocker = np.zeros((H, W), dtype=bool)
        for other in layers_raw:
            if other is layer:
                continue
            if other["z"] <= z:            # rule 2: same/lower z doesn't block
                continue
            other_sp = other.get("semantic_path", "")
            # Phase 1.8: BOTH ancestor→descendant AND descendant→ancestor are skipped.
            # Phase 1.5 only had _is_descendant(other_sp, sp) which was half-right.
            if _is_ancestor_or_descendant(other_sp, sp):
                continue
            blocker |= other["mask"]
        layer["mask_resolved"] = layer["mask"] & ~blocker
        claimed_any |= layer["mask_resolved"]

    # Emit `residual` synthetic layer when unclaimed coverage is material.
    unclaimed = ~claimed_any
    unclaimed_pct = unclaimed.sum() / (H * W) * 100
    if unclaimed_pct > unclaimed_threshold_pct:
        print(f"  [residual] {unclaimed_pct:.1f}% unclaimed — emitting synthetic layer")
        layers_raw.append({
            "id": -1,
            "name": "residual",
            "label": "plan residual — pixels not covered by any named entity",
            "semantic_path": "residual",
            "bbox": [0, 0, W, H],
            "det_score": None, "sam_score": None,
            "z": 1,   # just above bg (z=0), below subject (z=50+)
            "mask": unclaimed,
            "mask_resolved": unclaimed,
            "quality_status": "residual",
            "locked": True,
        })
    return layers_raw


def _load_image_safely(img_path: Path, max_pixels: int = 100_000_000):
    """Load image with production-grade safety checks.

    Guards against:
    - Decompression bombs (PIL default: 178M pixels, we cap at 100M)
    - Wrong format / corruption
    - EXIF orientation (auto-rotate to visible orientation)

    Raises ValueError with a structured reason on failure.
    """
    try:
        with Image.open(img_path) as probe:
            probe_w, probe_h = probe.size
            if probe_w * probe_h > max_pixels:
                raise ValueError(
                    f"image too large: {probe_w}x{probe_h}={probe_w*probe_h:,} "
                    f"pixels exceeds {max_pixels:,} safety cap"
                )
            probe.verify()  # catches truncated files
    except Image.DecompressionBombError:
        raise ValueError(f"decompression bomb refused: {img_path}")
    except Image.UnidentifiedImageError:
        raise ValueError(f"unidentified image format: {img_path}")

    # Re-open for actual decode (verify() invalidates the image)
    img_pil = Image.open(img_path)
    # Apply EXIF orientation so we process what humans see
    try:
        from PIL import ImageOps
        img_pil = ImageOps.exif_transpose(img_pil)
    except Exception:
        pass
    img_pil = img_pil.convert("RGB")
    return img_pil


def process(slug: str, force: bool = False):
    plan_path = PLANS_DIR / f"{slug}.json"
    if not plan_path.exists():
        print(f"FAIL {slug}: no plan at {plan_path}")
        return {"status": "error", "reason": "missing_plan"}

    try:
        plan_raw = json.loads(plan_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL {slug}: invalid plan JSON: {e}")
        return {"status": "error", "reason": "invalid_plan_json", "detail": str(e)}

    # Phase 1.9: run full Pydantic validation on CLI path too. Previously
    # only MCP path validated — CLI trusted raw JSON. A malicious/typo'd
    # plan with unsafe `name` like "../etc/passwd" could be written to disk.
    # Also catches typos in field names (extra="forbid") early.
    # exclude_none=True so dict matches old raw-JSON behavior — code uses
    # `.get(key, default)` patterns that would break if Pydantic-injected
    # None values populated keys that were absent in the raw JSON.
    try:
        from vulca.pipeline.segment.plan import Plan
        validated = Plan.model_validate(plan_raw)
        plan = validated.model_dump(exclude_none=True)
    except Exception as e:
        print(f"FAIL {slug}: plan schema validation: {e}")
        return {"status": "error", "reason": "plan_schema", "detail": str(e)[:500]}

    img_path = None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = ORIG_DIR / f"{slug}{ext}"
        if candidate.exists():
            img_path = candidate
            break
    if img_path is None:
        print(f"FAIL {slug}: no image at {ORIG_DIR}/{slug}.{{jpg,jpeg,png,webp}}")
        return {"status": "error", "reason": "missing_image"}

    try:
        img_pil = _load_image_safely(img_path)
    except ValueError as e:
        print(f"FAIL {slug}: {e}")
        return {"status": "error", "reason": "image_load", "detail": str(e)}

    W, H = img_pil.size
    img_np = np.array(img_pil)

    out_subdir = OUT_DIR / slug
    out_subdir.mkdir(parents=True, exist_ok=True)
    if not force and (out_subdir / "manifest.json").exists():
        print(f"SKIP {slug}: output exists (--force to redo)")
        return

    device = plan.get("device", "mps")
    print(f"\n[{slug}] {W}x{H} · {len(plan['entities'])} entities · plan={plan.get('domain','?')}")

    # ── Domain profile: routes person detection + sets thresholds ──
    domain = plan.get("domain", "")
    profile = DOMAIN_PROFILES.get(domain, DEFAULT_PROFILE)
    if domain and domain not in DOMAIN_PROFILES:
        print(f"  [warn] unknown domain {domain!r} — falling back to DEFAULT_PROFILE")
    person_chain = profile["person_chain"]
    object_thresh = profile["object_thresh"]
    print(f"  domain={domain} chain={person_chain} obj_thresh={object_thresh}")

    # Partition entities: persons (need chain) vs objects (→DINO)
    # Pattern B: entities with detector="sam_bbox" skip YOLO/DINO entirely
    # and go straight to SAM using bbox_hint_pct. Short-circuit partition.
    # Use index-sets (O(n) + unambiguous identity) instead of dict equality.
    hint_ids = {i for i, e in enumerate(plan["entities"])
                if e.get("detector") == "sam_bbox"}
    person_ids = {i for i, e in enumerate(plan["entities"])
                  if i not in hint_ids and (
                      e.get("detector") == "yolo"
                      or _is_person_path(e.get("semantic_path", "")))}
    object_ids = set(range(len(plan["entities"]))) - hint_ids - person_ids
    hint_entities = [(i, plan["entities"][i]) for i in sorted(hint_ids)]
    person_entities = [(i, plan["entities"][i]) for i in sorted(person_ids)]
    object_entities = [(i, plan["entities"][i]) for i in sorted(object_ids)]

    # detection_report: every entity gets a record regardless of outcome
    detection_report = {
        "requested": len(plan["entities"]),
        "domain": domain,
        "person_chain": person_chain,
        "per_entity": [],  # populated below
    }

    t0 = time.time()
    sam_pred = load_sam(device)
    sam_pred.set_image(img_np)
    print(f"  SAM loaded: {time.time()-t0:.1f}s")

    # Pre-load both detectors if needed (cost once, share across person+object)
    yolo = None
    dino_proc, dino_model = None, None
    if person_entities and person_chain:
        if "yolo" in person_chain:
            yolo = load_yolo()
        if "dino" in person_chain or object_entities:
            dino_proc, dino_model = load_grounding_dino(device)
    elif object_entities:
        dino_proc, dino_model = load_grounding_dino(device)

    # ── Person detection via fallback chain ──
    yolo_persons = []
    person_detector_used = None
    person_attempts = []
    if person_entities and person_chain:
        t0 = time.time()
        yolo_persons, person_detector_used, person_attempts = detect_persons_with_chain(
            person_chain, yolo, dino_proc, dino_model, device,
            img_pil, str(img_path),
            yolo_conf=0.20, dino_conf=0.20,
        )
        attempts_str = ", ".join(f"{n}:{c}" for n, c, _ in person_attempts)
        print(f"  PersonChain [{attempts_str}] → used={person_detector_used} "
              f"got {len(yolo_persons)} persons in {time.time()-t0:.1f}s")

    # ── Object detection via Grounding DINO (joint pass) ──
    dino_assigned = {}
    if object_entities and dino_proc is not None:
        t0 = time.time()
        object_labels = [e["label"] for _, e in object_entities]
        # Phase 1.9: warn on duplicate labels. `dino_assigned` is keyed by
        # label text, so two entities with identical labels share one bbox
        # (whichever scored higher) — silently collapsing one entity.
        # Plan authors should give each entity a distinctive label.
        label_counts = {}
        for l in object_labels:
            label_counts[l] = label_counts.get(l, 0) + 1
        dup_labels = [l for l, c in label_counts.items() if c > 1]
        if dup_labels:
            print(f"  [warn] duplicate DINO labels will collapse: {dup_labels} — "
                  "entities sharing a label will be assigned the same bbox; "
                  "differentiate them in the plan")
        low_thresh = min((e.get("threshold", object_thresh)
                          for _, e in object_entities), default=object_thresh)
        # Adapt to image shape: tile extreme-aspect, upscale tiny
        if needs_tile(W, H) or profile.get("tile", False):
            print(f"    [adapt] tile inference (aspect {max(W,H)/min(W,H):.1f}:1)")
            dino_assigned = detect_all_bboxes_tiled(dino_proc, dino_model, device,
                                                     img_pil, object_labels,
                                                     threshold=low_thresh)
        elif needs_upscale(W, H):
            print(f"    [adapt] 2x upscale inference ({W}x{H} → {W*2}x{H*2})")
            dino_assigned = detect_all_bboxes_upscaled(dino_proc, dino_model, device,
                                                        img_pil, object_labels,
                                                        threshold=low_thresh)
        else:
            dino_assigned = detect_all_bboxes(dino_proc, dino_model, device, img_pil,
                                               object_labels, threshold=low_thresh)
        print(f"  DINO objects: {len(dino_assigned)}/{len(object_labels)} in {time.time()-t0:.1f}s")

    layers_raw = []

    # Person layers: match detections to plan's person entities by left-to-right order
    person_ents_sorted = sorted(person_entities, key=lambda x: x[1].get("order", x[0]))
    for rank, (i, entity) in enumerate(person_ents_sorted):
        semantic_path = entity.get("semantic_path", f"subject.person[{i}]")
        label = entity["label"]
        record = {"id": i, "name": entity.get("name", label.replace(" ", "_")),
                  "label": label, "semantic_path": semantic_path,
                  "kind": "person",
                  "attempts": [{"detector": n, "count": c, "conf_range": r}
                               for n, c, r in person_attempts]}
        if rank >= len(yolo_persons):
            print(f"  [{i}] {label[:40]:40s} MISSED (chain: {[n for n,_,_ in person_attempts]})")
            record.update({"status": "missed", "reason": "no_detection_after_chain"})
            detection_report["per_entity"].append(record)
            continue
        bbox, det_conf = yolo_persons[rank]
        mask, sam_score, bbox_fill, inside_ratio = segment_bbox(sam_pred, bbox)
        pct = mask.sum() / (H * W) * 100
        # v0.17.14 — mirror the v0.17.13 transparency gate from the
        # DINO-object path. Person path had the same silent-success bug:
        # status: "detected" even on low-confidence SAM masks. The gate
        # uses the same DINO-tier thresholds calibrated against γ Scottish.
        quality_flags, status = compute_quality_flags(
            pct=pct, sam_score=sam_score,
            bbox_fill=bbox_fill, inside_ratio=inside_ratio,
        )
        marker = "?" if quality_flags else " "
        print(f"  [P{i}]{marker}{label[:30]:30s} {person_detector_used}[{rank}] bbox={bbox} "
              f"det={det_conf:.2f} sam={sam_score:.2f} pct={pct:.1f}%"
              + (f" flags={quality_flags}" if quality_flags else ""))
        record.update({"status": status, "detector": person_detector_used,
                       "bbox": bbox, "det_score": det_conf, "sam_score": sam_score,
                       "pct": round(pct, 2),
                       "bbox_fill": round(bbox_fill, 3),
                       "inside_ratio": round(inside_ratio, 3),
                       "quality_flags": quality_flags})
        detection_report["per_entity"].append(record)
        layers_raw.append({
            "id": i, "label": label, "name": record["name"],
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": det_conf, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
        })

    # ── Stage 3b: sam_bbox hint entities — MUST run before face-parsing ──
    # so hinted persons appear in layers_raw when face-parsing gate checks.
    for i, entity in hint_entities:
        label = entity["label"]
        semantic_path = entity.get("semantic_path", f"subject.entity[{i}]")
        hint_pct = entity.get("bbox_hint_pct")
        record = {"id": i, "name": entity.get("name", label.replace(" ", "_")),
                  "label": label, "semantic_path": semantic_path,
                  "kind": "hinted"}
        if hint_pct is None:
            print(f"  [H{i}] {label[:40]:40s} ERROR: sam_bbox needs bbox_hint_pct")
            record.update({"status": "missed", "reason": "missing_hint"})
            detection_report["per_entity"].append(record)
            continue
        bbox = hint_to_bbox_px(hint_pct, W, H)
        mask, sam_score, bbox_fill, inside_ratio = segment_bbox(sam_pred, bbox)
        pct = mask.sum() / (H * W) * 100
        # Quality backstop: sam_bbox always returns SOMETHING, so gate on shape.
        # bbox_fill < 0.05 → mask too sparse for hint (tiny object missed)
        # inside_ratio < 0.50 → mask mostly outside hint (wrong object picked)
        # pct < 0.05 → mask is trivially empty
        quality_flags = []
        if pct < 0.05:
            quality_flags.append("empty_mask")
        if bbox_fill < 0.05:
            quality_flags.append("low_bbox_fill")
        if inside_ratio < 0.50:
            quality_flags.append("mask_outside_bbox")
        status = "suspect" if quality_flags else "detected"
        marker = "?" if quality_flags else " "
        print(f"  [H{i}]{marker}{label[:30]:30s} hint bbox={bbox} sam={sam_score:.2f} "
              f"pct={pct:.1f}% fill={bbox_fill:.2f} in={inside_ratio:.2f}"
              + (f" flags={quality_flags}" if quality_flags else ""))
        record.update({
            "status": status,
            "detector": "sam_bbox",
            "source": "bbox_hint",  # explicit: not detector-inferred
            "bbox": bbox,
            "det_score": None,  # null — hint is authoritative, no inferred confidence
            "sam_score": sam_score,
            "pct": round(pct, 2),
            "bbox_fill": round(bbox_fill, 3),
            "inside_ratio": round(inside_ratio, 3),
            "quality_flags": quality_flags,
        })
        detection_report["per_entity"].append(record)
        layers_raw.append({
            "id": i, "label": label,
            "name": entity.get("name", label.replace(" ", "_")),
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": None, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
            "quality_status": status,
        })

    # ── Stage 4: Face-parsing per person (eyes, nose, lips, brows, skin, hair, ears, hat) ──
    # Gate scans layers_raw AFTER hint stage so hinted persons get face-parsing too.
    has_any_person = len(yolo_persons) > 0 or any(
        _is_person_path(l.get("semantic_path", "")) for l in layers_raw
    )
    expand_faces = plan.get("expand_face_parts", True) and has_any_person
    if expand_faces:
        t0 = time.time()
        face_proc, face_model = load_face_parser(device)
        face_layers_added = 0
        # Total image area for dynamic threshold
        img_area = W * H
        # Phase 1.9: lookup per_entity records by id so we can flag skipped face-parsing
        id_to_record = {r.get("id"): r for r in detection_report["per_entity"]}
        # Phase 1.11: precompute per-person "exclusive mask" (own mask minus
        # all OTHER persons' raw masks). This prevents face-part cross-
        # contamination when SAM returned over-broad masks for crowded scenes
        # (e.g. migrant-mother child_right's mask included the mother's face).
        # Persons here are all top-level `subject.person[N]` — face-parts are
        # added later so not in this loop's scan set.
        persons_top = [l for l in layers_raw if _is_person_path(l.get("semantic_path", ""))]
        exclusive_masks = {}
        for i, pl in enumerate(persons_top):
            others_union = np.zeros_like(pl["mask"])
            for j, other in enumerate(persons_top):
                if i == j:
                    continue
                others_union |= other["mask"]
            exclusive_masks[id(pl)] = pl["mask"] & ~others_union

        for person_layer in persons_top:
            # Pass the exclusive mask via a throwaway key so face_parse_person
            # sees bbox + (later) uses person_mask from the layer itself. We
            # instead constrain AFTER face_parse_person returns — cleaner.
            parts = face_parse_person(face_proc, face_model, device, img_np, person_layer["bbox"])
            if not parts:
                # Phase 1.9: emit face_parse_skipped quality_flag so downstream
                # can tell "face-parsing decided there's no face" apart from
                # "no face was detected". Formerly silent.
                pid = person_layer.get("id")
                rec = id_to_record.get(pid)
                if rec is not None:
                    flags = rec.setdefault("quality_flags", [])
                    if "face_parse_skipped" not in flags:
                        flags.append("face_parse_skipped")
                print(f"  [face-parse-skipped] {person_layer.get('name','?')}: "
                      "no face parts detected (small/occluded/unusual face)")
                continue
            # Phase 1.11: use EXCLUSIVE mask (raw mask minus other persons) for
            # face-part constraint. Prevents one person's face-parts from leaking
            # into another's when SAM masks overlap (classic crowd scene bug
            # fixed for migrant-mother child_right__skin showing mother).
            person_mask = exclusive_masks.get(id(person_layer), person_layer["mask"])
            # Dynamic threshold: larger persons get lower threshold; small persons
            # (background figures) need bigger parts to be worth emitting as sub-layers.
            # Pattern #2 fix: FACE_PART_MIN_PX scales with person size.
            person_px = person_mask.sum()
            person_frac = person_px / img_area
            if person_frac < 0.02:       # tiny person (<2% of image)
                min_part_px = max(FACE_PART_MIN_PX, 200)
            elif person_frac < 0.05:     # small (<5%)
                min_part_px = max(FACE_PART_MIN_PX, 100)
            else:
                min_part_px = FACE_PART_MIN_PX
            # Collect constrained sub-part masks (union used below for remainder)
            subparts_kept = []  # list of (part_name, mask)
            union_subparts = np.zeros(person_mask.shape, dtype=bool)
            for part_name, part_mask in parts.items():
                constrained = part_mask & person_mask
                if constrained.sum() < min_part_px:
                    continue
                subparts_kept.append((part_name, constrained))
                union_subparts |= constrained

            # Add sub-part layers
            for part_name, constrained in subparts_kept:
                parent_path = person_layer["semantic_path"]
                sub_sp = f"{parent_path}.{part_name}"
                parent_name = person_layer["name"]
                sub_name = f"{parent_name}__{part_name}"
                part_z_boost = {"eyes": 12, "lips": 12, "nose": 10, "eyebrows": 8,
                                "ears": 6, "hair": 4, "hat": 3, "neck": -2,
                                "cloth": -4, "skin": 2}.get(part_name, 0)
                layers_raw.append({
                    "id": 1000 + face_layers_added,
                    "label": f"{parent_name} {part_name}",
                    "name": sub_name,
                    "semantic_path": sub_sp,
                    "bbox": person_layer["bbox"],
                    "det_score": person_layer["det_score"],
                    "sam_score": 0.95,
                    "z": person_layer["z"] + part_z_boost,
                    "mask": constrained,
                })
                face_layers_added += 1

            # Pattern #1 fix: add body_remainder = person_mask - union(sub-parts)
            # so torso/clothing/etc below face region doesn't become a hollow shell.
            if subparts_kept:
                remainder = person_mask & ~union_subparts
                if remainder.sum() > min_part_px:
                    parent_name = person_layer["name"]
                    layers_raw.append({
                        "id": 1000 + face_layers_added,
                        "label": f"{parent_name} body remainder",
                        "name": f"{parent_name}__body",
                        "semantic_path": f"{person_layer['semantic_path']}.body",
                        "bbox": person_layer["bbox"],
                        "det_score": person_layer["det_score"],
                        "sam_score": 0.95,
                        "z": person_layer["z"] + 1,  # just above parent
                        "mask": remainder,
                    })
                    face_layers_added += 1
        print(f"  Face-parsing: +{face_layers_added} sub-parts (incl body_remainder) in {time.time()-t0:.1f}s")

    # Pattern #3 fix: union of all person masks (RAW, pre-resolve) for DINO-object
    # subtraction. Uses raw SAM mask intentionally — leak-fix's purpose is to
    # clean DINO's misclassification onto person areas, and raw is MORE
    # CONSERVATIVE than resolved (catches pixels even if later hidden by
    # hats/accessories). Phase 1.9 reviewer (Superpowers I3) raised a theoretical
    # concern about using resolved here, but structurally that's impossible
    # (resolve_overlaps runs AFTER this loop), and raw is correct anyway.
    all_persons_mask = np.zeros((H, W), dtype=bool)
    for pl in [l for l in layers_raw if _is_person_path(l.get("semantic_path", ""))]:
        all_persons_mask |= pl["mask"]

    # Object layers: use DINO results
    for i, entity in object_entities:
        label = entity["label"]
        semantic_path = entity.get("semantic_path", f"subject.entity[{i}]")
        record = {"id": i, "name": entity.get("name", label.replace(" ", "_")),
                  "label": label, "semantic_path": semantic_path, "kind": "object"}
        if label not in dino_assigned:
            print(f"  [O{i}] {label[:40]:40s} MISSED (dino)")
            record.update({"status": "missed", "reason": "dino_not_matched"})
            detection_report["per_entity"].append(record)
            continue
        bbox, score, phrase = dino_assigned[label]
        mask, sam_score, bbox_fill, inside_ratio = segment_bbox(sam_pred, bbox)

        # Pattern #3 fix: subtract person overlap ONLY in the "suspicious middle
        # range" (30%-90%). Rationale:
        #   - <30% overlap: probably no leak
        #   - 30-90% overlap: partial leak (e.g. chair_parapet grabbed arms)
        #   - >90% overlap: object is *contained* inside person by design
        #     (jewelry, flag_pin, held object, vulture near child) — KEEP IT.
        # Background layers (sky, ground, water) are exempt entirely.
        if not semantic_path.startswith("background"):
            overlap = (mask & all_persons_mask).sum()
            obj_px = mask.sum()
            if obj_px > 0:
                ratio = overlap / obj_px
                if 0.30 < ratio < 0.90:
                    mask = mask & ~all_persons_mask
                    print(f"    [leak-fix] {record['name']}: subtracted person overlap ({ratio*100:.0f}%)")
                elif ratio >= 0.90:
                    # Fully contained — accessory/held object. Keep as-is.
                    pass

        pct = mask.sum() / (H * W) * 100

        # v0.17.13 transparency gate — see compute_quality_flags() above.
        quality_flags, status = compute_quality_flags(
            pct=pct, sam_score=sam_score,
            bbox_fill=bbox_fill, inside_ratio=inside_ratio,
        )
        marker = "?" if quality_flags else " "
        print(f"  [O{i}]{marker}{label[:30]:30s} → '{phrase[:20]}' bbox={bbox} "
              f"det={score:.2f} sam={sam_score:.2f} pct={pct:.1f}% fill={bbox_fill:.2f}"
              + (f" flags={quality_flags}" if quality_flags else ""))
        record.update({"status": status, "detector": "dino",
                       "matched_phrase": phrase, "bbox": bbox,
                       "det_score": score, "sam_score": sam_score,
                       "pct": round(pct, 2),
                       "bbox_fill": round(bbox_fill, 3),
                       "inside_ratio": round(inside_ratio, 3),
                       "quality_flags": quality_flags})
        detection_report["per_entity"].append(record)
        layers_raw.append({
            "id": i, "label": label, "name": record["name"],
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": score, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
            "quality_status": status,
        })

    # (hint_entities were processed earlier, before face-parsing — see Stage 3b.)

    # Add background catch-all if none detected
    if not any(l["z"] <= 10 for l in layers_raw):
        H0, W0 = img_np.shape[:2]
        layers_raw.append({
            "id": 999, "label": "background", "name": "background",
            "semantic_path": "background",
            "bbox": [0, 0, W0, H0], "det_score": 1.0, "sam_score": 1.0,
            "z": 0, "mask": np.ones((H0, W0), dtype=bool),
        })

    # Capture pre-resolve areas so we can measure overlap erosion (observability).
    # Map by id for O(1) lookup when annotating per_entity records later.
    H_full, W_full = layers_raw[0]["mask"].shape
    total_px = H_full * W_full
    pre_resolve_pct = {l["id"]: l["mask"].sum() / total_px * 100 for l in layers_raw}

    # Overlap resolution: hierarchical-only (Phase 1.6+). Residual synthetic
    # layer emitted for plan-uncovered pixels above unclaimed_threshold_pct.
    residual_threshold = plan.get("unclaimed_threshold_pct", 2.0)
    print(f"  resolve_overlaps: residual_threshold={residual_threshold}%")
    resolve_overlaps(layers_raw, unclaimed_threshold_pct=residual_threshold)

    # Post-resolve areas + over-erosion detection (ratio < 0.5 → flagged).
    # This catches same-z layers stealing pixels (e.g. body eating feet).
    post_resolve_pct = {l["id"]: l["mask_resolved"].sum() / total_px * 100 for l in layers_raw}
    id_to_layer = {l["id"]: l for l in layers_raw}
    for rec in detection_report["per_entity"]:
        if rec.get("status") == "missed":
            continue
        lid = rec.get("id")
        if lid in pre_resolve_pct:
            pre = pre_resolve_pct[lid]
            post = post_resolve_pct.get(lid, 0.0)
            rec["pct_before_resolve"] = round(pre, 2)
            rec["pct_after_resolve"] = round(post, 2)
            # Over-erosion is a DOWNSTREAM problem (same-z siblings stole
            # pixels in resolve_overlaps), NOT a SAM quality failure — so
            # we record it as a flag for downstream consumers + QA loops
            # but do NOT downgrade status (which is SAM-quality-gated).
            # See claude_orchestrated_pipeline notes: erosion vs. detection
            # failures are categorically different and should not be mixed.
            if pre > 0.1 and post / pre < 0.5:
                flags = rec.setdefault("quality_flags", [])
                if "over_eroded" not in flags:
                    flags.append("over_eroded")
                # Under hierarchical model (Phase 1.5), descendant-caused
                # erosion is impossible by construction — so this fires only
                # for true foreground-over-background occlusion by a strictly
                # higher-z NON-descendant layer (e.g. pitchfork over farmer).
                print(f"  [erosion] {rec.get('name','?')}: {pre:.1f}%→{post:.1f}% "
                      f"({post/pre*100:.0f}% retained) — non-descendant higher-z occlusion")
            # Phase 1.9 symmetric observability: pair of `over_eroded`. Flag when
            # a small layer suspiciously grew >3x post-resolve. Under hierarchical
            # model this shouldn't happen normally (resolve only removes pixels)
            # but signals something unexpected — e.g. face-part mask leaking
            # into parent space, or a mask union bug.
            if 0.01 < pre < 0.5 and post > pre * 3.0:
                flags = rec.setdefault("quality_flags", [])
                if "area_ballooned" not in flags:
                    flags.append("area_ballooned")
                print(f"  [balloon] {rec.get('name','?')}: {pre:.1f}%→{post:.1f}% "
                      f"({post/pre:.1f}x) — unexpected growth post-resolve")

    # Save per-layer RGBA + manifest (with soft-alpha edge refinement)
    try:
        sys.path.insert(0, str(REPO / "src"))
        from vulca.layers.matting import soften_mask
    except ImportError:
        soften_mask = None

    # Two-pass build: we need stable layer IDs first so that parent_layer_id
    # can reference them. Otherwise we'd have a forward-reference chicken-and-egg
    # since parents may appear after children in layers_raw (face-parts come
    # after the person they refine).
    def _layer_id(name: str) -> str:
        return "layer_" + hashlib.md5(f"{slug}-{name}".encode()).hexdigest()[:8]

    # Pass 1: assign IDs + build semantic_path → id lookup for parent resolution.
    layer_ids = {id(l): _layer_id(l["name"]) for l in layers_raw}
    sp_to_id: dict[str, str] = {}
    for l in layers_raw:
        sp = l.get("semantic_path", "")
        if sp and sp not in sp_to_id:
            sp_to_id[sp] = layer_ids[id(l)]

    def _find_parent_id(sp: str) -> str | None:
        """Longest existing ancestor semantic_path wins (deepest parent)."""
        if not sp:
            return None
        best_sp = ""
        for candidate_sp in sp_to_id:
            if _is_descendant(sp, candidate_sp) and len(candidate_sp) > len(best_sp):
                best_sp = candidate_sp
        return sp_to_id.get(best_sp) if best_sp else None

    # Pass 2: write PNGs + build manifest entries with parent_layer_id wired.
    manifest_layers = []
    for l in layers_raw:
        if soften_mask is not None and plan.get("soften_edges", True):
            # soft alpha: guided filter or feathered + despill → smoother edges
            soft = soften_mask(l["mask_resolved"], img_np, feather_px=2,
                                guided=True, despill=True)
            mask_u8 = (soft * 255).astype(np.uint8)
        else:
            mask_u8 = (l["mask_resolved"] * 255).astype(np.uint8)
        rgba = np.dstack([img_np, mask_u8])
        fname = f"{l['name']}.png"
        Image.fromarray(rgba).save(str(out_subdir / fname))
        # area_pct is post-resolve (what consumers see on disk). Lets
        # downstream tools (HTML viewer, VLM QA) reason about layer size
        # without re-reading PNG alpha.
        area_pct = round(l["mask_resolved"].sum() / total_px * 100, 2)
        layer_sp = l.get("semantic_path", "")
        manifest_layers.append({
            "id": layer_ids[id(l)],
            "name": l["name"],
            "label": l["label"],
            "description": l["label"],
            "z_index": l["z"],
            "blend_mode": "normal",
            "content_type": l["name"],
            "semantic_path": layer_sp,
            "parent_layer_id": _find_parent_id(layer_sp),
            "visible": True,
            "locked": bool(l.get("locked", False)),
            "file": fname,
            "bbox": l["bbox"],
            "det_score": l["det_score"],
            "sam_score": l["sam_score"],
            "area_pct": area_pct,
            "quality_status": l.get("quality_status", "detected"),
            "regeneration_prompt": l["label"],
            "opacity": 1.0,
            "x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0,
            "rotation": 0.0, "content_bbox": None,
        })

    # Finalize detection report: success rate + overall status.
    # "suspect" is a new 3rd status (Fix #1) — SAM returned a mask but quality
    # backstop flagged it (low bbox_fill, mask mostly outside hint, or over-
    # eroded). Suspects are still rendered but don't count toward success_rate,
    # so hint-heavy failures naturally surface as status=partial.
    detected_count = sum(1 for e in detection_report["per_entity"] if e.get("status") == "detected")
    suspect_count  = sum(1 for e in detection_report["per_entity"] if e.get("status") == "suspect")
    missed_count   = sum(1 for e in detection_report["per_entity"] if e.get("status") == "missed")
    hint_count = sum(
        1 for e in detection_report["per_entity"]
        if e.get("status") in ("detected", "suspect") and e.get("source") == "bbox_hint"
    )
    detector_detected = detected_count - sum(
        1 for e in detection_report["per_entity"]
        if e.get("status") == "detected" and e.get("source") == "bbox_hint"
    )
    detection_report["detected"] = detected_count
    detection_report["suspect"] = suspect_count
    detection_report["missed"] = missed_count
    # authority_mix: transparently separate detector-found vs human-hinted.
    # Review (I3) — downstream consumers need this to compute detector recall.
    detection_report["authority_mix"] = {
        "detected_by_model": detector_detected,
        "hinted_by_plan": hint_count,
        "suspect": suspect_count,
        "missed": missed_count,
    }
    success_rate = detected_count / max(detection_report["requested"], 1)
    detection_report["success_rate"] = round(success_rate, 3)
    # Any suspect → downgrade from ok to partial (quality gate, not just count).
    status = "ok" if (success_rate >= SUCCESS_RATE_THRESHOLD and suspect_count == 0) else "partial"
    detection_report["status"] = status
    # Warning if >50% entities needed hints — plan may be mis-using sam_bbox
    if detection_report["requested"] > 2 and hint_count / detection_report["requested"] > 0.5:
        detection_report["warning"] = (
            f"hint-heavy plan ({hint_count}/{detection_report['requested']} entities "
            f"via bbox_hint); consider whether detectors were misconfigured"
        )

    manifest = {
        "version": ORCHESTRATED_MANIFEST_VERSION,  # sourced from module constant above
        "width": W, "height": H,
        "source_image": str(
            img_path.relative_to(REPO) if REPO in img_path.parents else img_path
        ),
        "split_mode": "claude_orchestrated",
        "status": status,
        "detection_report": detection_report,
        "plan": plan,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layers": manifest_layers,
    }
    # Phase 1.9: atomic write (tmp + rename) — interrupted write would otherwise
    # leave a corrupted manifest.json that downstream readers silently skip.
    _mf_path = out_subdir / "manifest.json"
    _mf_tmp = out_subdir / "manifest.json.tmp"
    _mf_tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    _mf_tmp.replace(_mf_path)  # POSIX-atomic rename on same filesystem

    # Phase 1.11: clean up orphan PNG files left from previous reruns. When a
    # layer gets dropped (below threshold, plan edit, etc.) its PNG remains
    # unless we explicitly delete. Stale PNGs confuse visual review (I was
    # looking at old mother-face in child_right__skin.png post-fix).
    expected_png_names = {l["file"] for l in manifest_layers}
    for existing_png in out_subdir.glob("*.png"):
        if existing_png.name not in expected_png_names:
            existing_png.unlink()
            print(f"  [cleanup] removed stale {existing_png.name}")

    marker = "✓" if status == "ok" else "⚠"
    print(f"{marker} {slug}: {status.upper()} "
          f"[{detected_count}/{detection_report['requested']} detected, "
          f"{suspect_count} suspect, {missed_count} missed] "
          f"→ {len(manifest_layers)} layers ({out_subdir})")
    if missed_count > 0:
        missed_names = [e["name"] for e in detection_report["per_entity"] if e.get("status") == "missed"]
        print(f"   Missed: {missed_names}")
    if suspect_count > 0:
        suspects = [(e["name"], e.get("quality_flags", []))
                    for e in detection_report["per_entity"] if e.get("status") == "suspect"]
        print(f"   Suspect: {suspects}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="+")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any slug has status=partial")
    args = parser.parse_args()
    partial_slugs = []
    for slug in args.slugs:
        process(slug, force=args.force)
        # Check status from freshly-written manifest
        mf = OUT_DIR / slug / "manifest.json"
        if mf.exists():
            m = json.loads(mf.read_text())
            if m.get("status") == "partial":
                partial_slugs.append(slug)

    if partial_slugs:
        print(f"\n⚠  {len(partial_slugs)} slug(s) with status=partial: {partial_slugs}")
        if args.strict:
            sys.exit(2)


if __name__ == "__main__":
    main()
