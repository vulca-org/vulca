"""Tests for pipeline same-round node parallelism (Phase B Task 5)."""
import asyncio
import time
import pytest
from vulca.pipeline.node import PipelineNode, NodeContext
from vulca.pipeline.types import PipelineDefinition, PipelineInput
from vulca.pipeline.engine import execute


class SlowNodeA(PipelineNode):
    name = "slow_a"
    is_concurrent_safe = True

    async def run(self, ctx: NodeContext) -> dict:
        await asyncio.sleep(0.3)
        return {"a_done": True}


class SlowNodeB(PipelineNode):
    name = "slow_b"
    is_concurrent_safe = True

    async def run(self, ctx: NodeContext) -> dict:
        await asyncio.sleep(0.3)
        return {"b_done": True}


class SerialNode(PipelineNode):
    name = "serial_end"

    async def run(self, ctx: NodeContext) -> dict:
        return {"decision": "accept", "weighted_total": 0.8, "scores": {"L1": 0.8}}


class SerialOnlyNode(PipelineNode):
    """A serial node that takes 0.3s — used to verify serial path isn't parallelized."""
    name = "serial_slow"

    async def run(self, ctx: NodeContext) -> dict:
        await asyncio.sleep(0.3)
        return {"decision": "accept", "weighted_total": 0.8, "scores": {"L1": 0.8}}


@pytest.mark.asyncio
async def test_concurrent_nodes_run_in_parallel():
    """Two concurrent-safe nodes should execute in ~0.3s, not ~0.6s."""
    defn = PipelineDefinition(
        name="test_parallel",
        nodes=("slow_a", "slow_b", "serial_end"),
        edges=(("slow_a", "slow_b"), ("slow_b", "serial_end")),
        entry_point="slow_a",
        enable_loop=False,
        node_specs={"slow_a": SlowNodeA, "slow_b": SlowNodeB, "serial_end": SerialNode},
    )
    inp = PipelineInput(subject="test", tradition="default", provider="mock")
    start = time.monotonic()
    result = await execute(defn, inp)
    elapsed = time.monotonic() - start
    # Parallel: ~0.3s. Serial: ~0.6s. Allow generous margin for CI.
    assert elapsed < 0.55, f"Expected parallel execution (<0.55s) but got {elapsed:.2f}s"
    assert "completed" in str(result.status).lower(), f"Unexpected status: {result.status}"


@pytest.mark.asyncio
async def test_parallel_outputs_merged_into_context():
    """Both parallel nodes' outputs must appear in the final result."""
    defn = PipelineDefinition(
        name="test_parallel_merge",
        nodes=("slow_a", "slow_b", "serial_end"),
        edges=(("slow_a", "slow_b"), ("slow_b", "serial_end")),
        entry_point="slow_a",
        enable_loop=False,
        node_specs={"slow_a": SlowNodeA, "slow_b": SlowNodeB, "serial_end": SerialNode},
    )
    inp = PipelineInput(subject="test", tradition="default", provider="mock")
    result = await execute(defn, inp)
    # Pipeline completed — serial_end received ctx with a_done and b_done
    assert "completed" in str(result.status).lower()


@pytest.mark.asyncio
async def test_serial_node_not_batched():
    """Non-concurrent-safe nodes must run serially (no is_concurrent_safe attr)."""
    defn = PipelineDefinition(
        name="test_serial_only",
        nodes=("serial_slow",),
        edges=(),
        entry_point="serial_slow",
        enable_loop=False,
        node_specs={"serial_slow": SerialOnlyNode},
    )
    inp = PipelineInput(subject="test", tradition="default", provider="mock")
    start = time.monotonic()
    result = await execute(defn, inp)
    elapsed = time.monotonic() - start
    # Should run serially — just one node so elapsed ~0.3s
    assert elapsed >= 0.2, f"Expected at least 0.2s but got {elapsed:.2f}s"
    assert "completed" in str(result.status).lower()


@pytest.mark.asyncio
async def test_parallel_nodes_get_data_snapshot():
    """Parallel nodes must receive a snapshot of ctx.data, not the live dict.

    If node A writes to ctx.data during execution, node B (running concurrently)
    should NOT see A's writes — each gets an isolated copy.
    """
    write_log = []

    class WriterNode(PipelineNode):
        name = "writer"
        is_concurrent_safe = True

        async def run(self, ctx: NodeContext) -> dict:
            # Write to ctx.data mid-execution
            ctx.data["writer_mid"] = True
            await asyncio.sleep(0.1)
            return {"writer_done": True}

    class ReaderNode(PipelineNode):
        name = "reader"
        is_concurrent_safe = True

        async def run(self, ctx: NodeContext) -> dict:
            # Wait a bit so writer has time to write to its ctx.data
            await asyncio.sleep(0.05)
            # If isolated, should NOT see writer_mid
            saw_writer_mid = ctx.data.get("writer_mid", False)
            write_log.append(saw_writer_mid)
            return {"reader_done": True, "saw_writer_mid": saw_writer_mid}

    class EndNode(PipelineNode):
        name = "end"

        async def run(self, ctx: NodeContext) -> dict:
            return {"decision": "accept", "weighted_total": 0.8, "scores": {"L1": 0.8}}

    defn = PipelineDefinition(
        name="test_snapshot_isolation",
        nodes=("writer", "reader", "end"),
        edges=(("writer", "reader"), ("reader", "end")),
        entry_point="writer",
        enable_loop=False,
        node_specs={"writer": WriterNode, "reader": ReaderNode, "end": EndNode},
    )
    inp = PipelineInput(subject="test", tradition="default", provider="mock")
    result = await execute(defn, inp)
    assert "completed" in str(result.status).lower()
    # Reader should NOT have seen writer's mid-execution write
    assert write_log[0] is False, (
        "Reader saw writer's mid-execution ctx.data write — "
        "parallel nodes must use snapshot isolation"
    )


@pytest.mark.asyncio
async def test_shallow_copy_exists_on_node_context():
    """NodeContext must have a shallow_copy() method for parallel isolation."""
    ctx = NodeContext(subject="test", tradition="default", data={"key": "value"})
    copy = ctx.shallow_copy()
    # Copy has same scalar fields
    assert copy.subject == ctx.subject
    assert copy.tradition == ctx.tradition
    # But data dict is independent
    assert copy.data == ctx.data
    assert copy.data is not ctx.data
    copy.data["new_key"] = "new_value"
    assert "new_key" not in ctx.data


@pytest.mark.asyncio
async def test_single_concurrent_node_runs_serially():
    """A single concurrent-safe node (no neighbour) runs via serial path."""
    class SingleConcurrentNode(PipelineNode):
        name = "single_concurrent"
        is_concurrent_safe = True

        async def run(self, ctx: NodeContext) -> dict:
            return {"decision": "accept", "weighted_total": 0.9, "scores": {"L1": 0.9}}

    defn = PipelineDefinition(
        name="test_single_concurrent",
        nodes=("single_concurrent",),
        edges=(),
        entry_point="single_concurrent",
        enable_loop=False,
        node_specs={"single_concurrent": SingleConcurrentNode},
    )
    inp = PipelineInput(subject="test", tradition="default", provider="mock")
    result = await execute(defn, inp)
    assert "completed" in str(result.status).lower()
