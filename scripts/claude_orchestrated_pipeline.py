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
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
PLANS_DIR = REPO / "assets" / "showcase" / "plans"
OUT_DIR = REPO / "assets" / "showcase" / "layers_v2"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
SAM_CKPT = "/tmp/sam_vit_l.pth"


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
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    proc = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-tiny")
    model = AutoModelForZeroShotObjectDetection.from_pretrained(
        "IDEA-Research/grounding-dino-tiny"
    ).to(device).eval()
    return proc, model


@functools.lru_cache(maxsize=1)
def load_yolo():
    """YOLO26 for person detection — best person recall + precise bboxes."""
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

    Returns (x1,y1,x2,y2) in seg_map coords, or None.
    """
    anchor = np.isin(seg_map, [2, 4, 5])  # nose, l_eye, r_eye
    if anchor.sum() < 20:
        # Fallback: all face classes
        anchor = np.isin(seg_map, [1, 2, 4, 5, 6, 7, 11, 12])
    if anchor.sum() < 50:
        return None
    ys, xs = np.where(anchor)
    cy, cx = int(ys.mean()), int(xs.mean())
    # Expand from anchor center by 4x the anchor extent (face ~= 4x nose-eye span)
    anchor_h = ys.max() - ys.min()
    anchor_w = xs.max() - xs.min()
    face_size = max(anchor_h, anchor_w, 50) * 4
    H, W = seg_map.shape
    x1 = max(0, cx - face_size // 2)
    x2 = min(W, cx + face_size // 2)
    y1 = max(0, cy - face_size // 2)
    y2 = min(H, cy + face_size // 2)
    return (x1, y1, x2, y2)


def face_parse_person(face_proc, face_model, device, img_np, person_bbox, min_face_px=80):
    """Two-pass face-parsing: person crop -> face anchor -> tight face crop -> fine parts.

    Returns dict part_name -> HxW bool mask in full image coords.
    """
    x1, y1, x2, y2 = person_bbox
    person_crop = img_np[y1:y2, x1:x2]
    if person_crop.shape[0] < min_face_px or person_crop.shape[1] < min_face_px:
        return {}

    # Pass 1: parse full person crop (coarse — finds skin/hair/hat + weak anchor)
    seg_person = _run_face_parser(face_proc, face_model, device, person_crop)

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
            seg_face = _run_face_parser(face_proc, face_model, device, face_crop)
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


def segment_bbox(sam_pred, bbox, multimask=True):
    """Run SAM with bbox prompt, return best mask by bbox-fill."""
    box = np.array(bbox)
    masks, scores, _ = sam_pred.predict(box=box, multimask_output=multimask)
    x1, y1, x2, y2 = bbox
    bbox_area = (x2 - x1) * (y2 - y1)
    best_idx = max(
        range(len(masks)),
        key=lambda i: masks[i][y1:y2, x1:x2].sum() / max(bbox_area, 1)
    )
    return masks[best_idx], float(scores[best_idx])


def hint_to_bbox_px(hint_pct, W: int, H: int) -> list[int]:
    """Convert normalized bbox hint [x1,y1,x2,y2] in [0,1] to pixel xyxy.

    Clamps to image bounds defensively; the schema validator already rejects
    out-of-range values but user-provided plans can't be trusted at runtime.
    """
    x1, y1, x2, y2 = hint_pct
    return [
        max(0, min(W - 1, int(x1 * W))),
        max(0, min(H - 1, int(y1 * H))),
        max(0, min(W - 1, int(x2 * W))),
        max(0, min(H - 1, int(y2 * H))),
    ]


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


def resolve_overlaps(layers_raw):
    """Higher z wins contested pixels. Fill unclaimed into bg if present."""
    if not layers_raw:
        raise ValueError("empty layers")
    H, W = layers_raw[0]["mask"].shape
    ordered = sorted(layers_raw, key=lambda l: -l["z"])
    claimed = np.zeros((H, W), dtype=bool)
    for layer in ordered:
        m = layer["mask"] & ~claimed
        layer["mask_resolved"] = m
        claimed |= m
    # Fill unclaimed into first background-level layer
    bg_candidates = [l for l in layers_raw if l["z"] <= 10]
    if bg_candidates:
        bg = min(bg_candidates, key=lambda l: l["z"])
        bg["mask_resolved"] = bg["mask_resolved"] | ~claimed
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
        plan = json.loads(plan_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL {slug}: invalid plan JSON: {e}")
        return {"status": "error", "reason": "invalid_plan_json", "detail": str(e)}

    # Schema minimum: must have 'entities' list
    if "entities" not in plan or not isinstance(plan["entities"], list):
        print(f"FAIL {slug}: plan missing 'entities' list")
        return {"status": "error", "reason": "plan_schema"}

    img_path = ORIG_DIR / f"{slug}.jpg"
    if not img_path.exists():
        print(f"FAIL {slug}: no image at {img_path}")
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
    person_chain = profile["person_chain"]
    object_thresh = profile["object_thresh"]
    print(f"  domain={domain} chain={person_chain} obj_thresh={object_thresh}")

    # Partition entities: persons (need chain) vs objects (→DINO)
    # Pattern B: entities with detector="sam_bbox" skip YOLO/DINO entirely
    # and go straight to SAM using bbox_hint_pct. Short-circuit partition.
    hint_entities = [(i, e) for i, e in enumerate(plan["entities"])
                     if e.get("detector") == "sam_bbox"]
    person_entities = [(i, e) for i, e in enumerate(plan["entities"])
                       if (i, e) not in hint_entities and (
                           e.get("detector") == "yolo"
                           or "person[" in e.get("semantic_path", ""))]
    object_entities = [(i, e) for i, e in enumerate(plan["entities"])
                       if (i, e) not in person_entities
                       and (i, e) not in hint_entities]

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
        mask, sam_score = segment_bbox(sam_pred, bbox)
        pct = mask.sum() / (H * W) * 100
        print(f"  [P{i}] {label[:30]:30s} {person_detector_used}[{rank}] bbox={bbox} "
              f"det={det_conf:.2f} sam={sam_score:.2f} pct={pct:.1f}%")
        record.update({"status": "detected", "detector": person_detector_used,
                       "bbox": bbox, "det_score": det_conf, "sam_score": sam_score,
                       "pct": round(pct, 2)})
        detection_report["per_entity"].append(record)
        layers_raw.append({
            "id": i, "label": label, "name": record["name"],
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": det_conf, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
        })

    # ── Stage 4: Face-parsing per person (eyes, nose, lips, brows, skin, hair, ears, hat) ──
    # Gate includes hinted persons: any layer with "person[" in semantic_path.
    has_any_person = len(yolo_persons) > 0 or any(
        "person[" in l.get("semantic_path", "") for l in layers_raw
    )
    expand_faces = plan.get("expand_face_parts", True) and has_any_person
    if expand_faces:
        t0 = time.time()
        face_proc, face_model = load_face_parser(device)
        face_layers_added = 0
        # Total image area for dynamic threshold
        img_area = W * H
        for person_layer in [l for l in layers_raw if "person[" in l["semantic_path"]]:
            parts = face_parse_person(face_proc, face_model, device, img_np, person_layer["bbox"])
            if not parts:
                continue
            person_mask = person_layer["mask"]
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

    # Pattern #3 fix: union of all person masks for DINO-object subtraction
    all_persons_mask = np.zeros((H, W), dtype=bool)
    for pl in [l for l in layers_raw if "person[" in l["semantic_path"]]:
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
        mask, sam_score = segment_bbox(sam_pred, bbox)

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
        print(f"  [O{i}] {label[:30]:30s} → '{phrase[:20]}' bbox={bbox} "
              f"det={score:.2f} sam={sam_score:.2f} pct={pct:.1f}%")
        record.update({"status": "detected", "detector": "dino",
                       "matched_phrase": phrase, "bbox": bbox,
                       "det_score": score, "sam_score": sam_score,
                       "pct": round(pct, 2)})
        detection_report["per_entity"].append(record)
        layers_raw.append({
            "id": i, "label": label, "name": record["name"],
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": score, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
        })

    # ── Pattern A+B: sam_bbox entities — skip detection, hint → SAM ──
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
        mask, sam_score = segment_bbox(sam_pred, bbox)
        pct = mask.sum() / (H * W) * 100
        print(f"  [H{i}] {label[:30]:30s} hint bbox={bbox} sam={sam_score:.2f} pct={pct:.1f}%")
        record.update({"status": "detected", "detector": "sam_bbox",
                       "source": "bbox_hint", "bbox": bbox,
                       "det_score": 1.0,  # synthetic — hint is authoritative
                       "sam_score": sam_score,
                       "pct": round(pct, 2)})
        detection_report["per_entity"].append(record)
        layers_raw.append({
            "id": i, "label": label,
            "name": entity.get("name", label.replace(" ", "_")),
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": 1.0, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
        })

    # Add background catch-all if none detected
    if not any(l["z"] <= 10 for l in layers_raw):
        H0, W0 = img_np.shape[:2]
        layers_raw.append({
            "id": 999, "label": "background", "name": "background",
            "semantic_path": "background",
            "bbox": [0, 0, W0, H0], "det_score": 1.0, "sam_score": 1.0,
            "z": 0, "mask": np.ones((H0, W0), dtype=bool),
        })

    # Overlap resolution
    resolve_overlaps(layers_raw)

    # Save per-layer RGBA + manifest (with soft-alpha edge refinement)
    try:
        sys.path.insert(0, str(REPO / "src"))
        from vulca.layers.matting import soften_mask
    except ImportError:
        soften_mask = None

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
        manifest_layers.append({
            "id": "layer_" + hashlib.md5(f"{slug}-{l['name']}".encode()).hexdigest()[:8],
            "name": l["name"],
            "label": l["label"],
            "description": l["label"],
            "z_index": l["z"],
            "blend_mode": "normal",
            "content_type": l["name"],
            "semantic_path": l["semantic_path"],
            "visible": True, "locked": False,
            "file": fname,
            "bbox": l["bbox"],
            "det_score": l["det_score"],
            "sam_score": l["sam_score"],
            "regeneration_prompt": l["label"],
            "opacity": 1.0,
            "x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0,
            "rotation": 0.0, "content_bbox": None,
        })

    # Finalize detection report: success rate + overall status
    detected_count = sum(1 for e in detection_report["per_entity"] if e.get("status") == "detected")
    missed_count = sum(1 for e in detection_report["per_entity"] if e.get("status") == "missed")
    detection_report["detected"] = detected_count
    detection_report["missed"] = missed_count
    success_rate = detected_count / max(detection_report["requested"], 1)
    detection_report["success_rate"] = round(success_rate, 3)
    status = "ok" if success_rate >= SUCCESS_RATE_THRESHOLD else "partial"
    detection_report["status"] = status

    manifest = {
        "version": 4,
        "width": W, "height": H,
        "source_image": str(img_path.relative_to(REPO)),
        "split_mode": "claude_orchestrated",
        "status": status,
        "detection_report": detection_report,
        "plan": plan,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layers": manifest_layers,
    }
    (out_subdir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    marker = "✓" if status == "ok" else "⚠"
    print(f"{marker} {slug}: {status.upper()} "
          f"[{detected_count}/{detection_report['requested']} detected] "
          f"→ {len(manifest_layers)} layers ({out_subdir})")
    if missed_count > 0:
        missed_names = [e["name"] for e in detection_report["per_entity"] if e.get("status") == "missed"]
        print(f"   Missed: {missed_names}")


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
