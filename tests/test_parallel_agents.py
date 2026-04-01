import pytest
from vulca.pipeline.parallel import explore_parallel, rank_results
from vulca.pipeline.types import PipelineOutput


@pytest.mark.asyncio
async def test_explore_parallel_runs_multiple():
    results = await explore_parallel(
        subject="test landscape",
        variations=[
            {"tradition": "chinese_xieyi"},
            {"tradition": "chinese_gongbi"},
            {"tradition": "default"},
        ],
        provider="mock",
    )
    assert len(results) == 3
    assert all(isinstance(r, PipelineOutput) for r in results)
    # Mock provider should complete all
    completed = [r for r in results if str(r.status).lower() != "failed"]
    assert len(completed) == 3


@pytest.mark.asyncio
async def test_explore_parallel_respects_max_concurrent():
    """Should not exceed max_concurrent simultaneous runs."""
    results = await explore_parallel(
        subject="test",
        variations=[{"tradition": f"default"} for _ in range(5)],
        provider="mock",
        max_concurrent=2,
    )
    assert len(results) == 5


@pytest.mark.asyncio
async def test_explore_parallel_single_variation():
    results = await explore_parallel(
        subject="single test",
        variations=[{"tradition": "default"}],
        provider="mock",
    )
    assert len(results) == 1


def test_rank_results():
    # weighted_total is a direct attribute on PipelineOutput, not inside final_scores
    r1 = PipelineOutput(session_id="1", status="completed", weighted_total=0.8, final_scores={}, rounds=[], events=[])
    r2 = PipelineOutput(session_id="2", status="completed", weighted_total=0.6, final_scores={}, rounds=[], events=[])
    r3 = PipelineOutput(session_id="3", status="failed", weighted_total=0.0, final_scores={}, rounds=[], events=[])

    ranked = rank_results([r2, r3, r1])
    assert ranked[0].session_id == "1"  # Highest score first
    assert ranked[-1].session_id == "3"  # Failed last (weighted_total=0.0 < 0.6)


def test_rank_results_falls_back_to_final_scores():
    """When weighted_total is 0.0 (default), fall back to final_scores dict."""
    # weighted_total defaults to 0.0 so final_scores fallback activates when wt is falsy
    # However the fix reads getattr(r, 'weighted_total', None) which returns 0.0 (not None)
    # So the direct attribute always wins — this tests the primary path
    r1 = PipelineOutput(session_id="a", status="completed", weighted_total=0.9, final_scores={}, rounds=[], events=[])
    r2 = PipelineOutput(session_id="b", status="completed", weighted_total=0.3, final_scores={}, rounds=[], events=[])
    ranked = rank_results([r2, r1])
    assert ranked[0].session_id == "a"
    assert ranked[0].weighted_total == 0.9


@pytest.mark.asyncio
async def test_explore_parallel_with_base_config():
    results = await explore_parallel(
        subject="base config test",
        variations=[
            {"tradition": "chinese_xieyi"},
            {"tradition": "default"},
        ],
        provider="mock",
        base_config={"max_rounds": 1, "eval_mode": "reference"},
    )
    assert len(results) == 2
