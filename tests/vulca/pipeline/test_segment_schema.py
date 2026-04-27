"""Tests for the typed Plan schema + filename sanitization + context types."""
from __future__ import annotations

import pytest
from pathlib import Path

from vulca.pipeline.segment.plan import Plan, PlanEntity, _sanitize_name


class TestSanitizeName:
    def test_plain_name_passes(self):
        assert _sanitize_name("mona_lisa") == "mona_lisa"

    def test_sanitizes_path_traversal(self):
        assert _sanitize_name("../etc/passwd") == "etc_passwd"

    def test_sanitizes_shell_chars(self):
        assert _sanitize_name("a;rm -rf;b") == "a_rm_-rf_b"

    def test_strips_null_bytes(self):
        assert _sanitize_name("evil\x00name") == "evil_name"

    def test_preserves_brackets(self):
        # person[0] needs brackets for semantic paths
        assert _sanitize_name("person[0]") == "person[0]"

    def test_preserves_dots(self):
        assert _sanitize_name("layer.png") == "layer.png"

    def test_empty_becomes_unnamed(self):
        assert _sanitize_name("") == "unnamed"
        assert _sanitize_name("...") == "unnamed"

    def test_caps_at_80_chars(self):
        assert len(_sanitize_name("x" * 200)) == 80


class TestPlanEntity:
    def test_minimal_valid(self):
        e = PlanEntity(name="mona", label="woman")
        assert e.name == "mona"
        assert e.detector == "auto"

    def test_rejects_unsafe_name(self):
        with pytest.raises(ValueError, match="unsafe"):
            PlanEntity(name="../evil", label="x")

    def test_rejects_unknown_detector(self):
        with pytest.raises(ValueError):
            PlanEntity(name="a", label="b", detector="evilnet")

    def test_threshold_range(self):
        with pytest.raises(ValueError):
            PlanEntity(name="a", label="b", threshold=1.5)

    def test_rejects_unknown_fields(self):
        # extra="forbid" catches typos
        with pytest.raises(ValueError):
            PlanEntity(name="a", label="b", threshhold=0.5)  # typo


class TestPlan:
    def test_minimal_valid(self):
        p = Plan(entities=[{"name": "bg", "label": "background"}])
        assert p.plan_version == 1
        assert p.expand_face_parts is True
        assert p.soften_edges is True

    def test_empty_entities_rejected(self):
        with pytest.raises(ValueError):
            Plan(entities=[])

    def test_duplicate_names_rejected(self):
        with pytest.raises(ValueError, match="duplicate"):
            Plan(entities=[
                {"name": "x", "label": "a"},
                {"name": "x", "label": "b"},
            ])

    def test_phase19_reserved_residual_name(self):
        """Phase 1.9 #7: `residual` is reserved for the synthetic layer."""
        with pytest.raises(ValueError, match="reserved"):
            Plan(entities=[{"name": "residual", "label": "x"}])
        with pytest.raises(ValueError, match="reserved"):
            Plan(entities=[{"name": "x", "label": "y", "semantic_path": "residual"}])

    def test_rejects_duplicate_multi_instance_labels(self):
        """Plan validator catches 2+ multi_instance entities sharing a label.

        DINO returns one bbox-list per label; two multi_instance entities
        with the same label would silently emit identical N masks per entity
        under different filenames — caught here, not at runtime.
        """
        with pytest.raises(ValueError, match="duplicate labels"):
            Plan(
                slug="test",
                domain="test",
                entities=[
                    {"name": "a", "label": "lantern",
                     "semantic_path": "subject.a", "multi_instance": True},
                    {"name": "b", "label": "lantern",
                     "semantic_path": "subject.b", "multi_instance": True},
                ],
            )

    def test_allows_duplicate_single_instance_labels(self):
        """Single-instance entities with same label are permitted.

        DINO top-1 mode returns one bbox per label per call — no duplication
        risk. Caller may legitimately want two single-instance entities the
        detector sees as one bbox (e.g. `cathedral` + `cathedral_facade`).
        """
        Plan(
            slug="test",
            domain="test",
            entities=[
                {"name": "a", "label": "lantern",
                 "semantic_path": "subject.a"},
                {"name": "b", "label": "lantern",
                 "semantic_path": "subject.b"},
            ],
        )

    def test_unknown_device_rejected(self):
        with pytest.raises(ValueError):
            Plan(entities=[{"name": "a", "label": "b"}], device="nvidia-wtf")

    def test_threshold_hint_range(self):
        with pytest.raises(ValueError):
            Plan(entities=[{"name": "a", "label": "b"}], threshold_hint=2.0)

    def test_from_existing_plan_file(self, tmp_path):
        # Use one of the committed plans as a regression fixture
        repo_plans = Path(__file__).resolve().parents[3] / "assets" / "showcase" / "plans"
        if not repo_plans.exists():
            pytest.skip("showcase plans not present")
        # Pick a known-good one
        plan_file = repo_plans / "mona-lisa.json"
        if not plan_file.exists():
            pytest.skip()
        p = Plan.from_file(plan_file)
        assert p.slug == "mona-lisa"
        assert len(p.entities) >= 3
        assert all(e.name and e.label for e in p.entities)

    def test_all_existing_plans_validate(self):
        """Every committed plan must pass schema validation — catches drift."""
        repo_plans = Path(__file__).resolve().parents[3] / "assets" / "showcase" / "plans"
        if not repo_plans.exists():
            pytest.skip()
        plan_files = list(repo_plans.glob("*.json"))
        assert len(plan_files) >= 20, "expected at least 20 showcase plans"
        for pf in plan_files:
            try:
                Plan.from_file(pf)
            except Exception as e:
                pytest.fail(f"{pf.name} failed schema validation: {e}")


class TestBboxHint:
    def test_none_default(self):
        e = PlanEntity(name="a", label="b")
        assert e.bbox_hint_pct is None

    def test_valid_hint(self):
        e = PlanEntity(name="a", label="b", bbox_hint_pct=[0.1, 0.2, 0.5, 0.9])
        assert e.bbox_hint_pct == [0.1, 0.2, 0.5, 0.9]

    def test_wrong_length(self):
        with pytest.raises(ValueError, match="4-element"):
            PlanEntity(name="a", label="b", bbox_hint_pct=[0.1, 0.2, 0.5])

    def test_out_of_range(self):
        with pytest.raises(ValueError, match=r"\[0\.0, 1\.0\]"):
            PlanEntity(name="a", label="b", bbox_hint_pct=[0.1, 0.2, 1.5, 0.9])
        with pytest.raises(ValueError, match=r"\[0\.0, 1\.0\]"):
            PlanEntity(name="a", label="b", bbox_hint_pct=[-0.1, 0.2, 0.5, 0.9])

    def test_ordering(self):
        with pytest.raises(ValueError, match="must be <"):
            PlanEntity(name="a", label="b", bbox_hint_pct=[0.5, 0.2, 0.1, 0.9])

    def test_tiny_area_rejected(self):
        # 0.001 x 0.001 = 1e-6 area, way below 0.001 threshold
        with pytest.raises(ValueError, match="too small"):
            PlanEntity(name="a", label="b", bbox_hint_pct=[0.5, 0.5, 0.5001, 0.5001])

    def test_sam_bbox_requires_hint(self):
        with pytest.raises(ValueError, match="requires bbox_hint_pct"):
            PlanEntity(name="a", label="b", detector="sam_bbox")

    def test_sam_bbox_with_hint_ok(self):
        e = PlanEntity(name="a", label="b", detector="sam_bbox",
                       bbox_hint_pct=[0.1, 0.1, 0.9, 0.9])
        assert e.detector == "sam_bbox"

    def test_hint_without_sam_bbox_ok(self):
        # Hint alone is fine — it's fallback for other detectors
        e = PlanEntity(name="a", label="b", detector="yolo",
                       bbox_hint_pct=[0.1, 0.1, 0.9, 0.9])
        assert e.detector == "yolo"
        assert e.bbox_hint_pct is not None


class TestPlanSerialization:
    def test_round_trip(self):
        p = Plan(
            slug="test",
            domain="historical_bw_photo",
            entities=[
                {"name": "bg", "label": "dark background"},
                {"name": "person_0", "label": "man", "detector": "yolo", "order": 0},
            ],
        )
        js = p.model_dump_json()
        p2 = Plan.model_validate_json(js)
        assert p2.slug == p.slug
        assert len(p2.entities) == 2
