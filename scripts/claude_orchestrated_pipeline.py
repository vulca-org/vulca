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


def load_grounding_dino(device="mps"):
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    proc = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-tiny")
    model = AutoModelForZeroShotObjectDetection.from_pretrained(
        "IDEA-Research/grounding-dino-tiny"
    ).to(device).eval()
    return proc, model


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
    # Sort by left-to-right (x center) for consistent naming
    persons.sort(key=lambda p: (p[0][0] + p[0][2]) / 2)
    return persons


def load_sam(device="mps"):
    from segment_anything import sam_model_registry, SamPredictor
    sam = sam_model_registry["vit_l"](checkpoint=SAM_CKPT).to(device)
    return SamPredictor(sam)


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


def process(slug: str, force: bool = False):
    plan_path = PLANS_DIR / f"{slug}.json"
    if not plan_path.exists():
        print(f"FAIL: no plan at {plan_path}")
        return
    plan = json.loads(plan_path.read_text())

    img_path = ORIG_DIR / f"{slug}.jpg"
    if not img_path.exists():
        print(f"FAIL: no image at {img_path}")
        return

    img_pil = Image.open(img_path).convert("RGB")
    W, H = img_pil.size
    img_np = np.array(img_pil)

    out_subdir = OUT_DIR / slug
    out_subdir.mkdir(parents=True, exist_ok=True)
    if not force and (out_subdir / "manifest.json").exists():
        print(f"SKIP {slug}: output exists (--force to redo)")
        return

    device = plan.get("device", "mps")
    print(f"\n[{slug}] {W}x{H} · {len(plan['entities'])} entities · plan={plan.get('domain','?')}")

    # Partition entities: persons (→YOLO) vs objects (→Grounding DINO)
    person_entities = [(i, e) for i, e in enumerate(plan["entities"])
                       if e.get("detector") == "yolo" or "person[" in e.get("semantic_path", "")]
    object_entities = [(i, e) for i, e in enumerate(plan["entities"])
                       if (i, e) not in person_entities]

    t0 = time.time()
    sam_pred = load_sam(device)
    sam_pred.set_image(img_np)
    print(f"  SAM loaded: {time.time()-t0:.1f}s")

    # ── Person detection via YOLO26 (precise bboxes, left-to-right order) ──
    yolo_persons = []
    if person_entities:
        t0 = time.time()
        yolo = load_yolo()
        yolo_persons = detect_persons_yolo(yolo, str(img_path), min_conf=0.20)
        print(f"  YOLO26 persons: {len(yolo_persons)} detected in {time.time()-t0:.1f}s")

    # ── Object detection via Grounding DINO (joint pass) ──
    dino_assigned = {}
    if object_entities:
        t0 = time.time()
        dino_proc, dino_model = load_grounding_dino(device)
        object_labels = [e["label"] for _, e in object_entities]
        low_thresh = min((e.get("threshold", plan.get("threshold_hint", 0.25))
                          for _, e in object_entities), default=0.15)
        dino_assigned = detect_all_bboxes(dino_proc, dino_model, device, img_pil,
                                           object_labels, threshold=low_thresh)
        print(f"  DINO objects: {len(dino_assigned)}/{len(object_labels)} in {time.time()-t0:.1f}s")

    layers_raw = []

    # Person layers: match YOLO detections to plan's person entities by left-to-right order
    person_ents_sorted = sorted(person_entities, key=lambda x: x[1].get("order", x[0]))
    for rank, (i, entity) in enumerate(person_ents_sorted):
        semantic_path = entity.get("semantic_path", f"subject.person[{i}]")
        label = entity["label"]
        if rank >= len(yolo_persons):
            print(f"  [{i}] {label[:40]:40s} NO YOLO DETECTION (only {len(yolo_persons)} persons found)")
            continue
        bbox, yolo_conf = yolo_persons[rank]
        mask, sam_score = segment_bbox(sam_pred, bbox)
        pct = mask.sum() / (H * W) * 100
        print(f"  [P{i}] {label[:30]:30s} yolo[{rank}] bbox={bbox} yolo={yolo_conf:.2f} sam={sam_score:.2f} pct={pct:.1f}%")
        layers_raw.append({
            "id": i, "label": label,
            "name": entity.get("name", label.replace(" ", "_")),
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": yolo_conf, "sam_score": sam_score,
            "z": _z_index_for(semantic_path), "mask": mask,
        })

    # ── Stage 4: Face-parsing per person (eyes, nose, lips, brows, skin, hair, ears, hat) ──
    expand_faces = plan.get("expand_face_parts", True) and len(yolo_persons) > 0
    if expand_faces:
        t0 = time.time()
        face_proc, face_model = load_face_parser(device)
        face_layers_added = 0
        for person_layer in [l for l in layers_raw if "person[" in l["semantic_path"]]:
            parts = face_parse_person(face_proc, face_model, device, img_np, person_layer["bbox"])
            if not parts:
                continue
            # Constrain parts to person's mask (prevent bleeding into other persons)
            person_mask = person_layer["mask"]
            for part_name, part_mask in parts.items():
                constrained = part_mask & person_mask
                if constrained.sum() < FACE_PART_MIN_PX:
                    continue
                parent_path = person_layer["semantic_path"]  # subject.person[N]
                sub_sp = f"{parent_path}.{part_name}"
                parent_name = person_layer["name"]
                sub_name = f"{parent_name}__{part_name}"
                # Face parts get z = parent z + offset based on part priority
                part_z_boost = {"eyes": 12, "lips": 12, "nose": 10, "eyebrows": 8, "ears": 6, "hair": 4, "hat": 3, "neck": -2, "cloth": -4, "skin": 2}.get(part_name, 0)
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
        print(f"  Face-parsing: +{face_layers_added} sub-parts in {time.time()-t0:.1f}s")

    # Object layers: use DINO results
    for i, entity in object_entities:
        label = entity["label"]
        semantic_path = entity.get("semantic_path", f"subject.entity[{i}]")
        if label not in dino_assigned:
            print(f"  [O{i}] {label[:40]:40s} NOT DETECTED")
            continue
        bbox, score, phrase = dino_assigned[label]
        mask, sam_score = segment_bbox(sam_pred, bbox)
        pct = mask.sum() / (H * W) * 100
        print(f"  [O{i}] {label[:30]:30s} → '{phrase[:20]}' bbox={bbox} det={score:.2f} sam={sam_score:.2f} pct={pct:.1f}%")
        layers_raw.append({
            "id": i, "label": label,
            "name": entity.get("name", label.replace(" ", "_")),
            "semantic_path": semantic_path, "bbox": bbox,
            "det_score": score, "sam_score": sam_score,
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

    # Save per-layer RGBA + manifest
    manifest_layers = []
    for l in layers_raw:
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

    manifest = {
        "version": 3,
        "width": W, "height": H,
        "source_image": str(img_path.relative_to(REPO)),
        "split_mode": "claude_orchestrated",
        "plan": plan,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layers": manifest_layers,
    }
    (out_subdir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"OK {slug}: {len(manifest_layers)} layers → {out_subdir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="+")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for slug in args.slugs:
        process(slug, force=args.force)


if __name__ == "__main__":
    main()
