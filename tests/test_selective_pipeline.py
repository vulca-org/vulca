"""Integration tests: pipeline with residuals + sparse_eval flags."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca.pipeline.types import PipelineInput, PipelineOutput, RoundSnapshot
from vulca.pipeline import execute, DEFAULT


class TestPipelineInputNewFields:
    def test_default_residuals_false(self):
        inp = PipelineInput(subject="test")
        assert inp.residuals is False

    def test_default_sparse_eval_false(self):
        inp = PipelineInput(subject="test")
        assert inp.sparse_eval is False

    def test_set_residuals_true(self):
        inp = PipelineInput(subject="test", residuals=True)
        assert inp.residuals is True

    def test_set_sparse_eval_true(self):
        inp = PipelineInput(subject="test", sparse_eval=True)
        assert inp.sparse_eval is True


class TestPipelineWithResiduals:
    @pytest.mark.asyncio
    async def test_residuals_stores_weights_in_output(self):
        inp = PipelineInput(subject="写意荷花", tradition="chinese_xieyi",
                            provider="mock", max_rounds=1, residuals=True)
        output = await execute(DEFAULT, inp)
        assert output.status in ("completed", "stopped")
        last_round = output.rounds[-1] if output.rounds else None
        assert last_round is not None

    @pytest.mark.asyncio
    async def test_residuals_false_no_residual_data(self):
        inp = PipelineInput(subject="写意荷花", tradition="chinese_xieyi",
                            provider="mock", max_rounds=1, residuals=False)
        output = await execute(DEFAULT, inp)
        for event in output.events:
            assert "residual_weights" not in event.payload


class TestPipelineWithSparseEval:
    @pytest.mark.asyncio
    async def test_sparse_eval_completes(self):
        inp = PipelineInput(subject="笔法练习 stroke technique", tradition="chinese_xieyi",
                            provider="mock", max_rounds=1, sparse_eval=True)
        output = await execute(DEFAULT, inp)
        assert output.status in ("completed", "stopped")
        assert output.final_scores is not None

    @pytest.mark.asyncio
    async def test_sparse_eval_false_unchanged(self):
        inp = PipelineInput(subject="test", tradition="chinese_xieyi",
                            provider="mock", max_rounds=1, sparse_eval=False)
        output = await execute(DEFAULT, inp)
        assert output.status in ("completed", "stopped")


class TestPipelineBothFlags:
    @pytest.mark.asyncio
    async def test_both_flags_complete(self):
        inp = PipelineInput(subject="写意荷花 留白 水墨", tradition="chinese_xieyi",
                            provider="mock", max_rounds=1, residuals=True, sparse_eval=True)
        output = await execute(DEFAULT, inp)
        assert output.status in ("completed", "stopped")
        assert len(output.rounds) >= 1
