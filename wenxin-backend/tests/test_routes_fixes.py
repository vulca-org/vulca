"""Test route fixes: schema field validation, instruct inheritance, n_candidates."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# CreateRunRequest schema
# ---------------------------------------------------------------------------

class TestCreateRunRequest:
    def test_default_fields(self):
        """Verify default values for all optional fields."""
        from app.prototype.api.schemas import CreateRunRequest

        req = CreateRunRequest(subject="test artwork")
        assert req.subject == "test artwork"
        assert req.tradition == "default"
        assert req.provider == "auto"
        assert req.n_candidates == 4
        assert req.max_rounds == 3
        assert req.enable_hitl is False
        assert req.node_params is None
        assert req.reference_image_base64 is None

    def test_n_candidates_bounds(self):
        """n_candidates must be between 1 and 8."""
        from app.prototype.api.schemas import CreateRunRequest
        from pydantic import ValidationError

        req = CreateRunRequest(subject="test", n_candidates=1)
        assert req.n_candidates == 1

        req = CreateRunRequest(subject="test", n_candidates=8)
        assert req.n_candidates == 8

        with pytest.raises(ValidationError):
            CreateRunRequest(subject="test", n_candidates=0)

        with pytest.raises(ValidationError):
            CreateRunRequest(subject="test", n_candidates=9)

    def test_max_rounds_bounds(self):
        """max_rounds must be between 1 and 5."""
        from app.prototype.api.schemas import CreateRunRequest
        from pydantic import ValidationError

        req = CreateRunRequest(subject="test", max_rounds=1)
        assert req.max_rounds == 1

        req = CreateRunRequest(subject="test", max_rounds=5)
        assert req.max_rounds == 5

        with pytest.raises(ValidationError):
            CreateRunRequest(subject="test", max_rounds=0)

        with pytest.raises(ValidationError):
            CreateRunRequest(subject="test", max_rounds=6)

    def test_cultural_intent_alias(self):
        """cultural_intent should be accepted as alias for intent."""
        from app.prototype.api.schemas import CreateRunRequest

        req = CreateRunRequest(subject="test", cultural_intent="ink wash")
        assert req.intent == "ink wash"

    def test_node_params_accepted(self):
        """node_params dict with nested weight config should be accepted."""
        from app.prototype.api.schemas import CreateRunRequest

        req = CreateRunRequest(
            subject="test",
            node_params={"critic": {"w_l1": 0.5, "w_l2": 0.1}},
        )
        assert req.node_params["critic"]["w_l1"] == 0.5

    def test_reference_image_base64_stored(self):
        """Reference image base64 string should be stored."""
        from app.prototype.api.schemas import CreateRunRequest

        req = CreateRunRequest(
            subject="test",
            reference_image_base64="abc123==",
        )
        assert req.reference_image_base64 == "abc123=="

    def test_deprecated_fields_still_accepted(self):
        """Deprecated boolean flags must still be accepted for backward compatibility."""
        from app.prototype.api.schemas import CreateRunRequest

        req = CreateRunRequest(
            subject="test",
            enable_agent_critic=True,
            enable_prompt_enhancer=True,
            enable_llm_queen=False,
            enable_parallel_critic=False,
        )
        assert req.enable_agent_critic is True
        assert req.enable_prompt_enhancer is True
        assert req.enable_llm_queen is False
        assert req.enable_parallel_critic is False


# ---------------------------------------------------------------------------
# SubmitActionRequest schema
# ---------------------------------------------------------------------------

class TestSubmitActionRequest:
    def test_all_valid_actions(self):
        """All documented action types should be accepted without error."""
        from app.prototype.api.schemas import SubmitActionRequest

        for action in ("approve", "reject", "rerun", "lock_dimensions", "force_accept"):
            req = SubmitActionRequest(action=action)
            assert req.action == action

    def test_invalid_action_rejected(self):
        """Unknown action strings must be rejected."""
        from app.prototype.api.schemas import SubmitActionRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SubmitActionRequest(action="unknown_action")

    def test_locked_dimensions_default_empty(self):
        """locked_dimensions should default to an empty list."""
        from app.prototype.api.schemas import SubmitActionRequest

        req = SubmitActionRequest(action="approve")
        assert req.locked_dimensions == []

    def test_locked_dimensions_accepted(self):
        """locked_dimensions list of strings should be stored."""
        from app.prototype.api.schemas import SubmitActionRequest

        req = SubmitActionRequest(
            action="lock_dimensions",
            locked_dimensions=["L1", "L3"],
        )
        assert req.locked_dimensions == ["L1", "L3"]

    def test_candidate_id_and_reason_defaults(self):
        """candidate_id and reason should default to empty strings."""
        from app.prototype.api.schemas import SubmitActionRequest

        req = SubmitActionRequest(action="approve")
        assert req.candidate_id == ""
        assert req.reason == ""


# ---------------------------------------------------------------------------
# RunStatusResponse schema
# ---------------------------------------------------------------------------

class TestRunStatusResponse:
    def test_required_fields(self):
        """task_id and status are the only required fields."""
        from app.prototype.api.schemas import RunStatusResponse

        resp = RunStatusResponse(task_id="api-abc12345", status="running")
        assert resp.task_id == "api-abc12345"
        assert resp.status == "running"

    def test_default_numeric_fields(self):
        """Numeric fields should default to zero-values."""
        from app.prototype.api.schemas import RunStatusResponse

        resp = RunStatusResponse(task_id="t", status="pending")
        assert resp.current_round == 0
        assert resp.total_rounds == 0
        assert resp.total_latency_ms == 0
        assert resp.total_cost_usd == 0.0
        assert resp.weighted_total == 0.0

    def test_final_scores_default_empty_dict(self):
        """final_scores should default to an empty dict."""
        from app.prototype.api.schemas import RunStatusResponse

        resp = RunStatusResponse(task_id="t", status="completed")
        assert resp.final_scores == {}

    def test_stages_and_rounds_default_empty_list(self):
        """stages and rounds should default to empty lists."""
        from app.prototype.api.schemas import RunStatusResponse

        resp = RunStatusResponse(task_id="t", status="completed")
        assert resp.stages == []
        assert resp.rounds == []


# ---------------------------------------------------------------------------
# SubmitActionResponse schema
# ---------------------------------------------------------------------------

class TestSubmitActionResponse:
    def test_accepted_field(self):
        """accepted boolean is required and controls response semantics."""
        from app.prototype.api.schemas import SubmitActionResponse

        ok = SubmitActionResponse(accepted=True, message="Pipeline accepted")
        assert ok.accepted is True

        nok = SubmitActionResponse(accepted=False, message="Action rejected")
        assert nok.accepted is False

    def test_new_task_id_optional(self):
        """new_task_id should be None by default (only set for rerun action)."""
        from app.prototype.api.schemas import SubmitActionResponse

        resp = SubmitActionResponse(accepted=True)
        assert resp.new_task_id is None

        resp_with_task = SubmitActionResponse(accepted=True, new_task_id="api-new001")
        assert resp_with_task.new_task_id == "api-new001"
