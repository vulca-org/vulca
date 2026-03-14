"""Tests for the digestion step-adapter pipeline.

Validates:
- Step auto-registration via __init_subclass__
- Priority ordering
- DigestContext extended fields
- Individual step execution with mock data
- Disabled-step exclusion
"""

from __future__ import annotations

import pytest

# Eagerly import steps so registration happens once at module load time
import app.prototype.digestion.steps  # noqa: F401
from app.prototype.digestion.base import BaseDigester, DigestContext


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestStepRegistration:
    """Verify that importing the steps module registers all 9 adapters."""

    def test_step_registration(self):
        expected_names = {
            "detect_patterns",
            "learn_preferences",
            "extract_layer_focus",
            "cluster_cultures",
            "distill_prompts",
            "crystallize_concepts",
            "trajectory_insights",
            "queen_strategy",
            "llm_insights",
        }
        registered_names = set(BaseDigester._registry.keys())
        assert expected_names.issubset(registered_names), (
            f"Missing steps: {expected_names - registered_names}"
        )
        # At least 9 from our steps (there may be others)
        assert len(registered_names) >= 9

    def test_step_ordering(self):
        ordered = BaseDigester.get_ordered_digesters()
        priorities = [d.PRIORITY for d in ordered]
        assert priorities == sorted(priorities), "Steps not in priority order"
        # Verify the 9 core steps appear in the expected order
        core_steps = [d for d in ordered if d.PRIORITY <= 90]
        core_priorities = [d.PRIORITY for d in core_steps]
        expected_order = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        assert core_priorities == expected_order

    def test_list_digesters(self):
        listing = BaseDigester.list_digesters()
        assert isinstance(listing, list)
        assert len(listing) >= 9
        # Each entry has the expected keys
        for entry in listing:
            assert "name" in entry
            assert "priority" in entry
            assert "enabled" in entry
            assert isinstance(entry["name"], str)
            assert isinstance(entry["priority"], int)
            assert isinstance(entry["enabled"], bool)
        # Verify sorted by priority
        priorities = [e["priority"] for e in listing]
        assert priorities == sorted(priorities)


class TestDigestContext:
    """Verify DigestContext has all required fields."""

    def test_digest_context_fields(self):
        ctx = DigestContext()
        # Original fields
        assert ctx.data == {}
        assert ctx.session_count == 0
        assert ctx.changed is False
        # New fields
        assert ctx.sessions == []
        assert ctx.patterns == []
        assert ctx.clusters == []
        assert ctx.actions == []
        assert ctx.evolver is None

    def test_digest_context_set_get(self):
        ctx = DigestContext()
        ctx.set("foo", "bar")
        assert ctx.get("foo") == "bar"
        assert ctx.changed is True

    def test_digest_context_with_data(self):
        ctx = DigestContext(
            data={"key": "value"},
            sessions=[{"id": 1}],
            patterns=["p1"],
            clusters=["c1"],
            actions=["a1"],
            session_count=5,
        )
        assert ctx.data["key"] == "value"
        assert len(ctx.sessions) == 1
        assert len(ctx.patterns) == 1
        assert len(ctx.clusters) == 1
        assert len(ctx.actions) == 1
        assert ctx.session_count == 5


class TestIndividualSteps:
    """Verify individual steps run without crashing on mock data."""

    def test_pattern_step_runs(self):
        from app.prototype.digestion.steps.pattern_step import PatternStep

        step = PatternStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_preference_step_runs(self):
        from app.prototype.digestion.steps.preference_step import PreferenceStep

        step = PreferenceStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_layer_focus_step_skips_without_evolver(self):
        from app.prototype.digestion.steps.layer_focus_step import LayerFocusStep

        step = LayerFocusStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        # Should skip gracefully -- no evolver reference
        assert isinstance(result, DigestContext)
        assert "layer_focus" not in result.data

    def test_cluster_step_runs(self):
        from app.prototype.digestion.steps.cluster_step import ClusterStep

        step = ClusterStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_distill_step_runs(self):
        from app.prototype.digestion.steps.distill_step import DistillStep

        step = DistillStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_crystallize_step_runs(self):
        from app.prototype.digestion.steps.crystallize_step import CrystallizeStep

        step = CrystallizeStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_trajectory_step_skips_without_evolver(self):
        from app.prototype.digestion.steps.trajectory_step import TrajectoryStep

        step = TrajectoryStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_strategy_step_skips_without_evolver(self):
        from app.prototype.digestion.steps.strategy_step import StrategyStep

        step = StrategyStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)

    def test_insight_step_skips_without_evolver(self):
        from app.prototype.digestion.steps.insight_step import InsightStep

        step = InsightStep()
        ctx = DigestContext()
        result = step.digest([], ctx)
        assert isinstance(result, DigestContext)


class TestDisabledStep:
    """Verify that steps with ENABLED_BY_DEFAULT=False are excluded."""

    def test_disabled_step_excluded(self):
        class _DisabledTestStep(BaseDigester):
            STEP_NAME = "_test_disabled_step"
            PRIORITY = 999
            ENABLED_BY_DEFAULT = False

            def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
                return ctx

        # Should be in the registry
        assert "_test_disabled_step" in BaseDigester._registry

        # But NOT in the ordered list
        ordered = BaseDigester.get_ordered_digesters()
        ordered_names = [d.STEP_NAME for d in ordered]
        assert "_test_disabled_step" not in ordered_names

        # And list_digesters should show enabled=False
        listing = BaseDigester.list_digesters()
        disabled_entry = [e for e in listing if e["name"] == "_test_disabled_step"]
        assert len(disabled_entry) == 1
        assert disabled_entry[0]["enabled"] is False

        # Clean up: remove the test step from registry so it doesn't
        # affect other tests
        BaseDigester._registry.pop("_test_disabled_step", None)
