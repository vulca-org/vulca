"""Integration tests: pipeline with sparse_eval flag."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca.pipeline.types import PipelineInput, PipelineOutput, RoundSnapshot
from vulca.pipeline import execute, DEFAULT


class TestPipelineInputNewFields:
    def test_default_sparse_eval_false(self):
        inp = PipelineInput(subject="test")
        assert inp.sparse_eval is False

    def test_set_sparse_eval_true(self):
        inp = PipelineInput(subject="test", sparse_eval=True)
        assert inp.sparse_eval is True


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
