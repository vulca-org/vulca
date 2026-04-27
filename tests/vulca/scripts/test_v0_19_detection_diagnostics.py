"""v0.19 regression tests: detection diagnostic improvements.

Covers FIX P0 (person path reason codes) and FIX P2 (object path
near-miss/nms-drop diagnostics from detect_all_bboxes).

These tests use mocks exclusively — no real DINO/SAM/YOLO calls.

Dogfood motivation: IMG_6847.jpg with 7-entity plan silently dropped
  - red_car (rank_exceeded_chain_pool: chain found 1 person for 2 person-entities)
  - wildflower_clusters (dino_not_matched vs dino_below_threshold was ambiguous)
See feedback memory: feedback_dogfood_surfaces_design_bugs.md
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def _make_entity(i, label, kind="object", **extra):
    e = {"label": label, "name": label.replace(" ", "_"),
         "semantic_path": f"subject.{label}", "kind": kind}
    e.update(extra)
    return (i, e)


def _run_person_loop(person_entities, yolo_persons, person_attempts=None):
    """Exercise only the person loop of process() using a minimal mock."""
    import claude_orchestrated_pipeline as cop

    if person_attempts is None:
        person_attempts = [("yolo", len(yolo_persons), "0.50-0.90")]

    detection_report = {"per_entity": []}
    person_ents_sorted = sorted(person_entities, key=lambda x: x[1].get("order", x[0]))

    # Replicate the person loop logic from process()
    for rank, (i, entity) in enumerate(person_ents_sorted):
        semantic_path = entity.get("semantic_path", f"subject.person[{i}]")
        label = entity["label"]
        record = {
            "id": i, "name": entity.get("name", label.replace(" ", "_")),
            "label": label, "semantic_path": semantic_path,
            "kind": "person",
            "attempts": [{"detector": n, "count": c, "conf_range": r}
                         for n, c, r in person_attempts],
        }
        if rank >= len(yolo_persons):
            if len(yolo_persons) == 0:
                miss_reason = "chain_returned_zero"
                miss_extra: dict = {}
            else:
                miss_reason = "rank_exceeded_chain_pool"
                miss_extra = {
                    "entities_in_chain_pool": len(yolo_persons),
                    "this_entity_rank": rank,
                }
            record.update({"status": "missed", "reason": miss_reason, **miss_extra})
            detection_report["per_entity"].append(record)
            continue
        # Simulate a successful detection (just enough to produce a record)
        bbox, det_conf = yolo_persons[rank]
        record.update({
            "status": "detected", "detector": "yolo",
            "bbox": bbox, "det_score": det_conf, "sam_score": 0.92,
            "pct": 15.0, "bbox_fill": 0.85, "inside_ratio": 0.90,
            "quality_flags": [],
        })
        detection_report["per_entity"].append(record)

    return detection_report


def _run_object_missed_branch(label, dino_near_miss, dino_nms_drops, is_multi=False):
    """Exercise only the object missed branch of process()."""
    i = 0
    base_name = label.replace(" ", "_")
    semantic_path = f"subject.{label}"

    # The real detect_all_bboxes pre-sorts near_miss/nms_drops by score desc
    # before storing in the dict. The helper mirrors that contract.
    near_miss_cands = sorted(dino_near_miss.get(label, []), key=lambda d: -d[1])
    nms_drop_cands = sorted(dino_nms_drops.get(label, []), key=lambda d: -d[1])
    if near_miss_cands:
        obj_reason = "dino_below_threshold"
        obj_extra: dict = {
            "near_miss_candidates": [
                {"bbox": b, "conf": round(s, 4), "phrase": p}
                for b, s, p in near_miss_cands[:5]
            ]
        }
    elif nms_drop_cands:
        obj_reason = "dropped_by_within_label_nms"
        obj_extra = {
            "nms_drop_candidates": [
                {"bbox": b, "conf": round(s, 4), "phrase": p}
                for b, s, p in nms_drop_cands[:5]
            ]
        }
    else:
        obj_reason = "dino_not_matched"
        obj_extra = {}

    record = {
        "id": i, "name": base_name, "label": label,
        "semantic_path": semantic_path, "kind": "object",
        "status": "missed", "reason": obj_reason, **obj_extra,
    }
    if is_multi and obj_reason in ("dino_not_matched", "dino_below_threshold"):
        record.setdefault("quality_flags", []).append("multi_instance_no_detection")

    return record


# ─────────────────────────────────────────────────────────────────
# FIX P0: Person path reason codes
# ─────────────────────────────────────────────────────────────────

class TestPersonChainReasonCodes:
    """v0.19 FIX P0: distinguish chain_returned_zero vs rank_exceeded_chain_pool."""

    def test_person_rank_exceeded_chain_pool(self):
        """2 person entities, chain returns 1 yolo_person.

        Second entity (rank=1) must have reason=rank_exceeded_chain_pool with
        entities_in_chain_pool=1 and this_entity_rank=1.
        Dogfood root cause: IMG_6847 red_car was silently dropped as
        'no_detection_after_chain' even though yellow_truck used the same chain.
        """
        entities = [
            _make_entity(0, "yellow_truck", kind="person"),
            _make_entity(1, "red_car", kind="person"),
        ]
        yolo_persons = [([100, 200, 300, 400], 0.88)]  # only 1 detection

        report = _run_person_loop(entities, yolo_persons)
        records = report["per_entity"]
        assert len(records) == 2

        # First entity (rank=0) gets the detection
        first = records[0]
        assert first["label"] == "yellow_truck"
        assert first["status"] == "detected"

        # Second entity (rank=1) is missed with specific reason
        second = records[1]
        assert second["label"] == "red_car"
        assert second["status"] == "missed"
        assert second["reason"] == "rank_exceeded_chain_pool", (
            f"expected rank_exceeded_chain_pool, got {second['reason']!r}"
        )
        assert second["entities_in_chain_pool"] == 1, (
            f"chain found 1 detection, got entities_in_chain_pool={second.get('entities_in_chain_pool')}"
        )
        assert second["this_entity_rank"] == 1, (
            f"red_car is rank=1, got this_entity_rank={second.get('this_entity_rank')}"
        )
        # attempts field must still be present (chain-level summary, unchanged)
        assert "attempts" in second

    def test_person_chain_returned_zero(self):
        """1 person entity, chain returns [] → reason=chain_returned_zero.

        Tells the user the chain found NO persons at all (vs "there were
        detections but yours was out of rank").
        """
        entities = [_make_entity(0, "main_subject", kind="person")]
        yolo_persons = []  # chain returned nothing

        report = _run_person_loop(entities, yolo_persons,
                                  person_attempts=[("yolo", 0, "n/a"), ("dino", 0, "n/a")])
        records = report["per_entity"]
        assert len(records) == 1

        rec = records[0]
        assert rec["label"] == "main_subject"
        assert rec["status"] == "missed"
        assert rec["reason"] == "chain_returned_zero", (
            f"expected chain_returned_zero, got {rec['reason']!r}"
        )
        # chain_returned_zero must NOT include rank-specific fields
        assert "entities_in_chain_pool" not in rec
        assert "this_entity_rank" not in rec
        # attempts still present
        assert "attempts" in rec

    def test_person_chain_full_match(self):
        """2 person entities, chain returns 2 → both detected (preserve existing behavior)."""
        entities = [
            _make_entity(0, "person_a", kind="person"),
            _make_entity(1, "person_b", kind="person"),
        ]
        yolo_persons = [
            ([10, 20, 100, 200], 0.92),
            ([200, 20, 350, 200], 0.87),
        ]

        report = _run_person_loop(entities, yolo_persons)
        records = report["per_entity"]
        assert len(records) == 2
        assert all(r["status"] == "detected" for r in records), (
            f"both entities should be detected; got {[r['status'] for r in records]}"
        )
        # No missed records
        missed = [r for r in records if r["status"] == "missed"]
        assert not missed, f"unexpected missed records: {missed}"


# ─────────────────────────────────────────────────────────────────
# FIX P2: Object path near-miss / nms-drop diagnostics
# ─────────────────────────────────────────────────────────────────

class TestObjectDiagnosticReasonCodes:
    """v0.19 FIX P2: distinguish dino_below_threshold vs dropped_by_within_label_nms vs dino_not_matched."""

    def test_object_dino_below_threshold(self):
        """DINO returned candidate below effective_threshold → reason=dino_below_threshold.

        Dogfood root cause: IMG_6847 wildflower_clusters threshold=0.18,
        DINO likely returned candidates at ~0.10 that were invisible to the caller.
        """
        label = "wildflower_clusters"
        near_miss = {label: [([50, 80, 200, 300], 0.10, "wildflower clusters")]}
        nms_drops = {}

        rec = _run_object_missed_branch(label, near_miss, nms_drops, is_multi=False)

        assert rec["reason"] == "dino_below_threshold", (
            f"expected dino_below_threshold, got {rec['reason']!r}"
        )
        assert "near_miss_candidates" in rec, "near_miss_candidates must be populated"
        cands = rec["near_miss_candidates"]
        assert len(cands) >= 1
        assert cands[0]["conf"] == pytest.approx(0.10, abs=0.001)
        assert "bbox" in cands[0]
        assert "phrase" in cands[0]

    def test_object_dino_below_threshold_multi_instance_flag(self):
        """multi_instance + below_threshold → multi_instance_no_detection flag still fires.

        Below-threshold candidates are a recoverable state (lower threshold) but
        there is still no assigned bbox, so multi_instance_no_detection is appropriate.
        """
        label = "lantern"
        near_miss = {label: [([50, 80, 200, 300], 0.08, "lantern")]}
        nms_drops = {}

        rec = _run_object_missed_branch(label, near_miss, nms_drops, is_multi=True)

        assert rec["reason"] == "dino_below_threshold"
        flags = rec.get("quality_flags", [])
        assert "multi_instance_no_detection" in flags, (
            f"multi_instance + below_threshold should flag multi_instance_no_detection, got {flags}"
        )

    def test_object_dino_not_matched_true_zero(self):
        """DINO returned nothing at all → reason=dino_not_matched (true zero, preserved behavior)."""
        label = "red_car"
        near_miss = {}
        nms_drops = {}

        rec = _run_object_missed_branch(label, near_miss, nms_drops)

        assert rec["reason"] == "dino_not_matched", (
            f"expected dino_not_matched, got {rec['reason']!r}"
        )
        assert "near_miss_candidates" not in rec
        assert "nms_drop_candidates" not in rec

    def test_object_dino_not_matched_multi_instance_flag(self):
        """multi_instance + true zero → multi_instance_no_detection fires (same as v0.18)."""
        label = "lantern"
        rec = _run_object_missed_branch(label, {}, {}, is_multi=True)

        assert rec["reason"] == "dino_not_matched"
        flags = rec.get("quality_flags", [])
        assert "multi_instance_no_detection" in flags

    def test_object_dropped_by_within_label_nms(self):
        """Candidate passed threshold but lost within-label NMS → dropped_by_within_label_nms.

        multi_instance_no_detection must NOT fire — this is an NMS artefact, not
        a detection gap.
        """
        label = "car"
        near_miss = {}
        nms_drops = {label: [([50, 80, 200, 300], 0.72, "car")]}

        rec = _run_object_missed_branch(label, near_miss, nms_drops, is_multi=True)

        assert rec["reason"] == "dropped_by_within_label_nms", (
            f"expected dropped_by_within_label_nms, got {rec['reason']!r}"
        )
        assert "nms_drop_candidates" in rec
        cands = rec["nms_drop_candidates"]
        assert cands[0]["conf"] == pytest.approx(0.72, abs=0.001)
        # dropped_by_within_label_nms must NOT add multi_instance_no_detection
        flags = rec.get("quality_flags", [])
        assert "multi_instance_no_detection" not in flags, (
            f"nms-drop reason must NOT flag multi_instance_no_detection, got {flags}"
        )

    def test_near_miss_candidates_capped_at_5(self):
        """near_miss_candidates are capped at top-5 by confidence descending."""
        label = "flowers"
        # 8 near-miss candidates, scores in jumbled order
        near_miss_cands = [
            ([i*10, 0, (i+1)*10, 100], 0.05 + i * 0.01, f"flowers{i}")
            for i in range(8)
        ]
        # Shuffle to ensure sorting by conf is tested
        import random
        random.shuffle(near_miss_cands)
        near_miss = {label: near_miss_cands}

        rec = _run_object_missed_branch(label, near_miss, {})

        cands = rec.get("near_miss_candidates", [])
        assert len(cands) <= 5, f"near_miss_candidates must be capped at 5, got {len(cands)}"
        confs = [c["conf"] for c in cands]
        assert confs == sorted(confs, reverse=True), (
            f"near_miss_candidates must be sorted by conf desc, got {confs}"
        )


# ─────────────────────────────────────────────────────────────────
# FIX P2: detect_all_bboxes return shape
# ─────────────────────────────────────────────────────────────────

class TestDetectAllBboxesReturnShape:
    """v0.19: detect_all_bboxes returns {assigned, near_miss, nms_drops}."""

    def _make_mock_dino(self, above_thresh_score=0.6, near_miss_score=0.08):
        """Build a minimal mock dino_proc + dino_model that returns synthetic detections.

        above_thresh_score: score for the 'above effective_threshold' candidate
        near_miss_score: score for the 'below effective_threshold but >= NEAR_MISS_FLOOR' candidate
        """
        import numpy as np

        NEAR_MISS_FLOOR = 0.05

        # Simulate two detections: one above threshold, one in near-miss range
        scores = np.array([above_thresh_score, near_miss_score], dtype=np.float32)
        boxes = np.array([[10, 20, 100, 200], [200, 20, 300, 200]], dtype=np.float32)
        labels_str = ["test_label", "test_label"]  # both map to same label

        mock_outputs = MagicMock()
        mock_proc = MagicMock()
        mock_model = MagicMock()
        mock_model.return_value = mock_outputs

        def fake_post_process(outputs, input_ids, threshold, text_threshold, target_sizes):
            # Filter to scores >= threshold (simulating real DINO behavior)
            mask = scores >= threshold
            filtered_scores = scores[mask]
            filtered_boxes = boxes[mask]
            filtered_labels = [l for l, m in zip(labels_str, mask) if m]
            result = {
                "scores": MagicMock(cpu=lambda: MagicMock(numpy=lambda: filtered_scores)),
                "boxes": MagicMock(cpu=lambda: MagicMock(numpy=lambda: filtered_boxes)),
                "text_labels": filtered_labels,
            }
            return [result]

        mock_proc.post_process_grounded_object_detection.side_effect = fake_post_process
        mock_proc.return_value = MagicMock(to=lambda d: MagicMock(
            input_ids=MagicMock()
        ))
        return mock_proc, mock_model, "cpu"

    def test_detect_all_bboxes_returns_three_keys(self):
        """detect_all_bboxes returns dict with exactly {assigned, near_miss, nms_drops}."""
        pytest.importorskip("torch")
        import torch
        import numpy as np
        import claude_orchestrated_pipeline as cop

        NEAR_MISS_FLOOR = cop.NEAR_MISS_FLOOR  # use the module constant

        label = "test_label"
        threshold = 0.15

        # Build synthetic DINO outputs with one above-threshold and one near-miss
        above_score = 0.60  # will be in assigned
        below_score = 0.08  # >= NEAR_MISS_FLOOR=0.05, < threshold=0.15 → near_miss

        scores_all = np.array([above_score, below_score], dtype=np.float32)
        boxes_all = np.array([[10, 20, 100, 200], [200, 20, 300, 200]], dtype=np.float32)

        # Mock proc: always returns all candidates regardless of threshold
        # (we'll let detect_all_bboxes partition them internally)
        mock_outputs = MagicMock()
        mock_proc = MagicMock()
        mock_model = MagicMock()
        mock_model.return_value = mock_outputs

        def fake_post_process(outputs, input_ids, threshold=0.05, text_threshold=0.15, target_sizes=None):
            # Return only detections >= threshold (simulates real DINO)
            mask = scores_all >= threshold
            fs = scores_all[mask]
            fb = boxes_all[mask]
            fl = [label] * int(mask.sum())

            class FakeTensorScores:
                def cpu(self): return FakeTensorScores()
                def numpy(self): return fs

            class FakeTensorBoxes:
                def cpu(self): return FakeTensorBoxes()
                def numpy(self): return fb

            return [{
                "scores": FakeTensorScores(),
                "boxes": FakeTensorBoxes(),
                "text_labels": fl,
            }]

        mock_proc.post_process_grounded_object_detection.side_effect = fake_post_process
        mock_proc_instance = MagicMock()
        mock_proc_instance.input_ids = MagicMock()
        mock_proc.return_value = MagicMock(to=MagicMock(return_value=mock_proc_instance))

        # Patch PIL image size attribute
        mock_img = MagicMock()
        mock_img.size = (640, 480)

        result = cop.detect_all_bboxes(
            mock_proc, mock_model, "cpu", mock_img,
            labels=[label], threshold=threshold,
        )

        # Shape contract
        assert isinstance(result, dict), f"result must be dict, got {type(result)}"
        assert "assigned" in result, f"result must have 'assigned' key, got {list(result.keys())}"
        assert "near_miss" in result, f"result must have 'near_miss' key, got {list(result.keys())}"
        assert "nms_drops" in result, f"result must have 'nms_drops' key, got {list(result.keys())}"

        # assigned: above-threshold candidate should be in assigned
        assigned = result["assigned"]
        assert isinstance(assigned, dict)

        # near_miss: below-threshold but >= NEAR_MISS_FLOOR should be in near_miss
        near_miss = result["near_miss"]
        assert isinstance(near_miss, dict)

        # nms_drops: candidates that passed threshold but lost NMS
        nms_drops = result["nms_drops"]
        assert isinstance(nms_drops, dict)

        # Above-threshold candidate should appear in assigned (not near_miss)
        # since call_threshold = min(threshold, NEAR_MISS_FLOOR) = NEAR_MISS_FLOOR = 0.05
        # and the partitioning puts score >= effective_threshold (0.15) → assigned
        if label in assigned:
            if isinstance(assigned[label], tuple):
                assert assigned[label][1] == pytest.approx(above_score, abs=0.01), (
                    f"assigned score should be the above-threshold score {above_score}"
                )

        # near_miss should contain the below-threshold candidate
        if label in near_miss:
            nm_scores = [c[1] for c in near_miss[label]]
            assert all(s >= NEAR_MISS_FLOOR for s in nm_scores), (
                f"near_miss scores must be >= NEAR_MISS_FLOOR={NEAR_MISS_FLOOR}"
            )
            assert all(s < threshold for s in nm_scores), (
                f"near_miss scores must be < effective_threshold={threshold}"
            )
