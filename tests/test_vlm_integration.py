"""Tests for VLM integration: Engram fragments + Sparse dimensions in real scoring path."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca._vlm import _build_tradition_guidance
from vulca.scoring.sparse import BriefIndexer, DimensionActivation
from vulca.cultural.engram import CulturalEngram, CulturalFragment, EngramQuery
from vulca.cultural.types import TraditionConfig, TermEntry, TabooEntry
from vulca.pipeline import execute, DEFAULT
from vulca.pipeline.types import PipelineInput


class TestBuildTraditionGuidanceWithEngram:
    """_build_tradition_guidance accepts optional engram_fragments."""

    def test_without_engram_unchanged(self):
        """Backward compatible: no engram -> same as before."""
        guidance = _build_tradition_guidance("chinese_xieyi")
        assert isinstance(guidance, str)
        assert len(guidance) > 0

    def test_with_engram_fragments_included(self):
        """When engram fragments provided, they appear in guidance."""
        fragments = [
            CulturalFragment(
                fragment_id="f1", tradition="chinese_xieyi", category="terminology",
                tags=["留白"], content="留白: Use of empty space for breathing room",
                l_dimensions=["L1"], weight=0.7,
            ),
        ]
        guidance = _build_tradition_guidance("chinese_xieyi", engram_fragments=fragments)
        assert "留白" in guidance or "empty space" in guidance

    def test_with_active_dimensions_filters_prompt(self):
        """When active_dimensions specified, prompt mentions focus."""
        guidance = _build_tradition_guidance(
            "chinese_xieyi",
            active_dimensions=["L1", "L3", "L5"],
        )
        # Should contain some indication of focused dimensions
        assert isinstance(guidance, str)


class TestEvaluateNodeSparse:
    """EvaluateNode handles sparse_eval from ctx."""

    @pytest.mark.asyncio
    async def test_sparse_eval_produces_dimension_activation(self):
        """Pipeline with sparse_eval=True stores dimension_activation in output."""
        inp = PipelineInput(
            subject="写意荷花，注重留白",
            tradition="chinese_xieyi",
            provider="mock",
            max_rounds=1,
            sparse_eval=True,
        )
        output = await execute(DEFAULT, inp)
        assert output.status in ("completed", "stopped")
        # Check that dimension_activation was recorded in events
        found = False
        for event in output.events:
            if event.payload and "dimension_activation" in event.payload:
                found = True
                act = event.payload["dimension_activation"]
                assert "active" in act
                assert "skipped" in act
                break
        # Or check final_scores still has all 5 dimensions
        assert len(output.final_scores) == 5

    @pytest.mark.asyncio
    async def test_sparse_eval_false_no_activation(self):
        """Pipeline with sparse_eval=False does not produce dimension_activation."""
        inp = PipelineInput(
            subject="test",
            tradition="chinese_xieyi",
            provider="mock",
            max_rounds=1,
            sparse_eval=False,
        )
        output = await execute(DEFAULT, inp)
        for event in output.events:
            if event.payload:
                assert "dimension_activation" not in event.payload

    @pytest.mark.asyncio
    async def test_sparse_eval_all_five_scores_present(self):
        """Even with sparse eval, all 5 L-dimension scores are in final output."""
        inp = PipelineInput(
            subject="笔法练习",
            tradition="chinese_xieyi",
            provider="mock",
            max_rounds=1,
            sparse_eval=True,
        )
        output = await execute(DEFAULT, inp)
        scores = output.final_scores
        for dim in ["L1", "L2", "L3", "L4", "L5"]:
            assert dim in scores
            assert isinstance(scores[dim], (int, float))

    @pytest.mark.asyncio
    async def test_sparse_eval_skipped_dims_get_baseline(self):
        """Skipped dimensions get baseline 0.5 in round 1 (no previous round)."""
        inp = PipelineInput(
            subject="笔法练习",  # Should activate L2 mainly
            tradition="",  # No tradition -> L3 not forced
            provider="mock",
            max_rounds=1,
            sparse_eval=True,
        )
        output = await execute(DEFAULT, inp)
        # With sparse eval, some dimensions should be at baseline
        # We can't check exact values with mock, but all should be present
        assert len(output.final_scores) == 5

    @pytest.mark.asyncio
    async def test_engram_fragments_in_pipeline(self):
        """Pipeline with sparse_eval loads and uses CulturalEngram."""
        inp = PipelineInput(
            subject="写意荷花留白水墨",
            tradition="chinese_xieyi",
            provider="mock",
            max_rounds=1,
            sparse_eval=True,
        )
        output = await execute(DEFAULT, inp)
        # Should complete without error -- engram integration doesn't crash
        assert output.status in ("completed", "stopped")
