"""Tests for the Marketplace-Execution Bridge (pipeline_hook.py).

Covers stage→skill mapping, skill selection override, graceful failure
when executors are missing, and the async→sync bridge.

Usage:
    cd wenxin-backend
    PYTHONPATH=. python -m pytest tests/test_skill_pipeline_hook.py -x -v
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.prototype.skills.pipeline_hook import (
    _STAGE_SKILLS,
    list_available_pipeline_skills,
    run_pipeline_skills,
)
from app.prototype.skills.types import SkillResult


# ---------------------------------------------------------------------------
# Test: list_available_pipeline_skills
# ---------------------------------------------------------------------------


class TestListAvailablePipelineSkills:
    def test_returns_correct_mapping(self):
        """list_available_pipeline_skills returns the stage→skills dict."""
        mapping = list_available_pipeline_skills()
        assert isinstance(mapping, dict)
        assert "post_critic" in mapping
        assert "post_draft" in mapping
        assert "post_accept" in mapping

    def test_returns_copy_not_reference(self):
        """Mutations to the returned dict should not affect internal state."""
        mapping = list_available_pipeline_skills()
        mapping["new_stage"] = ["some_skill"]
        assert "new_stage" not in list_available_pipeline_skills()

    def test_post_critic_skills(self):
        """post_critic stage should default to composition_balance and color_harmony."""
        mapping = list_available_pipeline_skills()
        assert mapping["post_critic"] == ["composition_balance", "color_harmony"]

    def test_post_draft_skills(self):
        mapping = list_available_pipeline_skills()
        assert mapping["post_draft"] == ["style_transfer"]

    def test_post_accept_skills(self):
        mapping = list_available_pipeline_skills()
        assert mapping["post_accept"] == [
            "brand_consistency", "audience_fit", "trend_alignment"
        ]


# ---------------------------------------------------------------------------
# Test: _STAGE_SKILLS mapping completeness
# ---------------------------------------------------------------------------


class TestStageSkillsMapping:
    def test_all_three_stages_defined(self):
        """Verify all 3 pipeline stages are defined in _STAGE_SKILLS."""
        expected_stages = {"post_critic", "post_draft", "post_accept"}
        assert set(_STAGE_SKILLS.keys()) == expected_stages

    def test_no_empty_skill_lists(self):
        """Every stage should have at least one skill mapped."""
        for stage, skills in _STAGE_SKILLS.items():
            assert len(skills) > 0, f"Stage {stage} has no skills"

    def test_all_skill_names_are_strings(self):
        """All skill names in the mapping should be strings."""
        for stage, skills in _STAGE_SKILLS.items():
            for skill in skills:
                assert isinstance(skill, str), (
                    f"Non-string skill in {stage}: {skill!r}"
                )


# ---------------------------------------------------------------------------
# Test: run_pipeline_skills — empty / unknown stage
# ---------------------------------------------------------------------------


class TestRunPipelineSkillsEmptyStage:
    def test_unknown_stage_returns_empty_list(self):
        """Calling with an unknown stage should return an empty list."""
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent.png",
            stage="unknown_stage",
        )
        assert results == []

    def test_unknown_stage_with_none_skill_names(self):
        """Unknown stage + skill_names=None → empty list."""
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent.png",
            stage="pre_scout",
            skill_names=None,
        )
        assert results == []


# ---------------------------------------------------------------------------
# Test: run_pipeline_skills — explicit skill_names override
# ---------------------------------------------------------------------------


class TestRunPipelineSkillsExplicitNames:
    def test_explicit_names_override_stage_defaults(self):
        """Passing skill_names should ignore stage defaults."""
        # Use non-existent skill names so they'll be "not found" but
        # we can verify the override logic by checking which names appear.
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent.png",
            stage="post_critic",
            skill_names=["custom_skill_a", "custom_skill_b"],
        )
        assert len(results) == 2
        assert results[0]["skill_name"] == "custom_skill_a"
        assert results[1]["skill_name"] == "custom_skill_b"
        # Both should fail (not found), confirming override was used
        assert results[0]["success"] is False
        assert results[1]["success"] is False

    def test_empty_explicit_names_returns_empty(self):
        """Passing an empty skill_names list should return no results."""
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent.png",
            stage="post_critic",
            skill_names=[],
        )
        assert results == []


# ---------------------------------------------------------------------------
# Test: run_pipeline_skills — graceful failure
# ---------------------------------------------------------------------------


class TestRunPipelineSkillsGracefulFailure:
    def test_missing_executor_does_not_crash(self):
        """If a skill executor isn't registered, the function should log and skip."""
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent.png",
            stage="post_critic",
            skill_names=["nonexistent_skill_xyz"],
        )
        assert len(results) == 1
        assert results[0]["skill_name"] == "nonexistent_skill_xyz"
        assert results[0]["success"] is False
        assert "not found" in results[0]["error"].lower()

    def test_mixed_found_and_not_found(self):
        """When some skills exist and some don't, each returns its own result."""
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent.png",
            skill_names=["nonexistent_alpha", "nonexistent_beta"],
        )
        assert len(results) == 2
        for r in results:
            assert r["success"] is False

    def test_executor_exception_is_caught(self):
        """If an executor's execute() raises, it should be caught gracefully."""
        from app.prototype.skills.executors.base import BaseSkillExecutor

        # Create a mock executor class that raises on execute
        class FailingExecutor(BaseSkillExecutor):
            SKILL_NAME = "_test_failing_executor"

            def __init__(self) -> None:
                super().__init__(skill_name="_test_failing_executor")

            async def execute(self, image_path, context=None):
                raise RuntimeError("Intentional test failure")

        try:
            results = run_pipeline_skills(
                image_path="/tmp/nonexistent.png",
                skill_names=["_test_failing_executor"],
            )
            assert len(results) == 1
            assert results[0]["skill_name"] == "_test_failing_executor"
            assert results[0]["success"] is False
            assert "Intentional test failure" in results[0]["error"]
        finally:
            # Clean up the test executor from the registry
            BaseSkillExecutor._registry.pop("_test_failing_executor", None)


# ---------------------------------------------------------------------------
# Test: run_pipeline_skills — post_critic default selection
# ---------------------------------------------------------------------------


class TestRunPipelineSkillsPostCriticDefault:
    def test_post_critic_selects_correct_skills(self):
        """post_critic stage should attempt composition_balance and color_harmony."""
        # These executors exist in the registry (via __init_subclass__),
        # but they will fail because the image doesn't exist and there's no
        # Gemini API key. We verify the correct skills were selected by
        # checking the skill_name fields in the results.
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent_test_image.png",
            stage="post_critic",
        )
        assert len(results) == 2
        skill_names = [r["skill_name"] for r in results]
        assert "composition_balance" in skill_names
        assert "color_harmony" in skill_names

    def test_post_critic_results_have_required_keys(self):
        """Each result dict should have skill_name and success keys."""
        results = run_pipeline_skills(
            image_path="/tmp/nonexistent_test_image.png",
            stage="post_critic",
        )
        for r in results:
            assert "skill_name" in r
            assert "success" in r
            # Should have either "result" or "error"
            assert "result" in r or "error" in r


# ---------------------------------------------------------------------------
# Test: run_pipeline_skills — successful execution with mock
# ---------------------------------------------------------------------------


class TestRunPipelineSkillsSuccess:
    def test_successful_execution_returns_result_dict(self):
        """When a skill executor succeeds, the result should be a dict."""
        from app.prototype.skills.executors.base import BaseSkillExecutor

        mock_result = SkillResult(
            skill_name="_test_success_executor",
            score=0.85,
            summary="Test passed",
            details={"sub_score": 0.9},
            suggestions=["Try harder"],
        )

        class SuccessExecutor(BaseSkillExecutor):
            SKILL_NAME = "_test_success_executor"

            def __init__(self) -> None:
                super().__init__(skill_name="_test_success_executor")

            async def execute(self, image_path, context=None):
                return mock_result

        try:
            results = run_pipeline_skills(
                image_path="/tmp/nonexistent.png",
                skill_names=["_test_success_executor"],
            )
            assert len(results) == 1
            r = results[0]
            assert r["skill_name"] == "_test_success_executor"
            assert r["success"] is True
            assert "result" in r
            assert r["result"]["score"] == 0.85
            assert r["result"]["summary"] == "Test passed"
            assert r["result"]["details"] == {"sub_score": 0.9}
            assert r["result"]["suggestions"] == ["Try harder"]
        finally:
            BaseSkillExecutor._registry.pop("_test_success_executor", None)

    def test_context_includes_tradition_and_stage(self):
        """The context dict passed to the executor should include tradition and stage."""
        from app.prototype.skills.executors.base import BaseSkillExecutor

        captured_ctx: dict = {}

        class CtxCapture(BaseSkillExecutor):
            SKILL_NAME = "_test_ctx_capture"

            def __init__(self) -> None:
                super().__init__(skill_name="_test_ctx_capture")

            async def execute(self, image_path, context=None):
                captured_ctx.update(context or {})
                return SkillResult(
                    skill_name="_test_ctx_capture",
                    score=0.5,
                    summary="ok",
                )

        try:
            run_pipeline_skills(
                image_path="/tmp/test.png",
                tradition="japanese_ukiyoe",
                stage="post_draft",
                skill_names=["_test_ctx_capture"],
                context={"extra": "data"},
            )
            assert captured_ctx["tradition"] == "japanese_ukiyoe"
            assert captured_ctx["stage"] == "post_draft"
            assert captured_ctx["extra"] == "data"
        finally:
            BaseSkillExecutor._registry.pop("_test_ctx_capture", None)
