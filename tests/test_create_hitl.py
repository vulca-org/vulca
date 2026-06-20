"""Tests for HITL and custom weights in SDK create() / acreate()."""

from __future__ import annotations

import pytest

from vulca.create import acreate, create
from vulca.types import CreateResult


class TestCreateHITL:
    """HITL flag pauses pipeline before decide node."""

    @pytest.mark.asyncio
    async def test_hitl_returns_waiting_human(self):
        result = await acreate("test artwork", provider="mock", mode="local", hitl=True)
        assert isinstance(result, CreateResult)
        assert result.status == "waiting_human"
        assert result.interrupted_at == "decide"

    @pytest.mark.asyncio
    async def test_hitl_has_scores(self):
        """HITL pauses after evaluate, so scores should be populated."""
        result = await acreate("test artwork", provider="mock", mode="local", hitl=True)
        assert result.scores  # evaluate ran, so scores exist
        assert result.weighted_total > 0.0

    @pytest.mark.asyncio
    async def test_no_hitl_returns_completed(self):
        result = await acreate("test artwork", provider="mock", mode="local", hitl=False)
        assert result.status == "completed"
        assert result.interrupted_at == ""

    def test_hitl_sync(self):
        result = create("test artwork", provider="mock", mode="local", hitl=True)
        assert result.status == "waiting_human"
        assert result.interrupted_at == "decide"


class TestCreateWeights:
    """Custom weights change the weighted_total."""

    @pytest.mark.asyncio
    async def test_custom_weights_change_total(self):
        r_default = await acreate("test", provider="mock", mode="local")
        r_custom = await acreate(
            "test",
            provider="mock",
            mode="local",
            weights={"L1": 1.0, "L2": 0.0, "L3": 0.0, "L4": 0.0, "L5": 0.0},
        )
        assert r_default.weighted_total != r_custom.weighted_total

    @pytest.mark.asyncio
    async def test_weights_with_hitl(self):
        """weights + hitl work together."""
        result = await acreate(
            "test",
            provider="mock",
            mode="local",
            hitl=True,
            weights={"L1": 1.0, "L2": 0.0, "L3": 0.0, "L4": 0.0, "L5": 0.0},
        )
        assert result.status == "waiting_human"
        assert result.weighted_total > 0.0

    def test_weights_sync(self):
        r_custom = create(
            "test",
            provider="mock",
            mode="local",
            weights={"L1": 0.0, "L2": 0.0, "L3": 0.0, "L4": 0.0, "L5": 1.0},
        )
        assert r_custom.weighted_total > 0.0

    @pytest.mark.asyncio
    async def test_none_weights_uses_default(self):
        """weights=None uses tradition defaults."""
        result = await acreate("test", provider="mock", mode="local", weights=None)
        assert result.status == "completed"
        assert result.weighted_total > 0.0


class TestCreateResultFields:
    """Verify new fields on CreateResult."""

    @pytest.mark.asyncio
    async def test_status_field_exists(self):
        result = await acreate("test", provider="mock", mode="local")
        assert hasattr(result, "status")
        assert hasattr(result, "interrupted_at")

    @pytest.mark.asyncio
    async def test_repr_includes_status(self):
        result = await acreate("test", provider="mock", mode="local")
        assert "status=" in repr(result)


class TestCreateEvalMetadata:
    """Optional eval metadata is preserved in local create pipeline output."""

    @pytest.mark.asyncio
    async def test_acreate_local_carries_eval_metadata_in_raw_output(self):
        metadata = {
            "schema_version": "vulca_eval_metadata.v1",
            "guards": {
                "vulca_jepa_subject_drift": {
                    "status": "warning",
                    "non_blocking": True,
                    "warnings_total": 1,
                    "warnings": [{"sample_id": "gongbi_baseline_failed_subject"}],
                }
            },
        }

        result = await acreate(
            "test artwork",
            provider="mock",
            mode="local",
            eval_metadata=metadata,
        )

        assert result.raw["eval_metadata"] == metadata
        assert result.rounds[0]["decision"] == "accept"
        assert result.weighted_total > 0.0
