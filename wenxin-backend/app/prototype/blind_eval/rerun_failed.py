"""Re-run specific failed Dp tasks one at a time with GPU cleanup between each."""
import asyncio, json, os, sys, time, gc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

FAILED_TASKS = ["vulca-bench-0010", "vulca-bench-0011", "vulca-bench-0012", "vulca-bench-0024"]
OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "results", "ablation", "run_20260224_192133", "raw", "condition_Dp")


async def run_one(task_id: str) -> dict:
    # Import fresh each time to avoid stale CUDA state
    from app.prototype.blind_eval.run_ablation import (
        _make_conditions, _build_ablation_orchestrator, sample_tasks,
        _deterministic_seed, _save_run_output,
    )
    from app.prototype.orchestrator.orchestrator import PipelineInput

    tasks = sample_tasks(n_per_category=10)
    task = None
    for t in tasks:
        if t.task_id == task_id:
            task = t
            break
    if not task:
        return {"error": f"Task {task_id} not found"}

    conditions = _make_conditions("real")
    cond = conditions["Dp"]
    seed = _deterministic_seed(task_id, cond.name, 42)
    orch = _build_ablation_orchestrator(cond, seed, 4)

    tradition = task.tradition if cond.use_cultural_routing else "default"
    pipeline_task_id = f"abl-Dp_{task_id}"

    pi = PipelineInput(
        task_id=pipeline_task_id,
        subject=task.subject,
        cultural_tradition=tradition,
    )

    t0 = time.monotonic()
    output = orch.run_sync(pi)
    latency_ms = int((time.monotonic() - t0) * 1000)

    # Extract score
    score = None
    for s in output.stages:
        if s.stage == "critic" and s.output_summary:
            score = s.output_summary.get("best_weighted_total")

    result = {
        "task_id": task_id,
        "success": output.success,
        "score": score,
        "rounds": output.total_rounds,
        "decision": output.final_decision,
        "latency_s": latency_ms // 1000,
        "error": output.error,
    }

    # Save to existing run directory (overwrite failed result)
    out_dir = os.path.join(OUTPUT_BASE, task_id)
    os.makedirs(out_dir, exist_ok=True)
    po_dict = {
        "success": output.success,
        "total_rounds": output.total_rounds,
        "final_decision": output.final_decision,
        "total_latency_ms": latency_ms,
        "error": output.error,
        "stages": [s.to_dict() for s in output.stages],
    }
    with open(os.path.join(out_dir, "pipeline_output.json"), "w") as f:
        json.dump(po_dict, f, indent=2, default=str)

    return result


def cleanup_gpu():
    """Force GPU memory cleanup."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except Exception:
        pass
    gc.collect()


def main():
    for i, task_id in enumerate(FAILED_TASKS):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(FAILED_TASKS)}] Running {task_id}")
        print(f"{'='*60}")

        try:
            result = asyncio.run(run_one(task_id))
            print(f"  Result: score={result.get('score')}, rounds={result.get('rounds')}, "
                  f"decision={result.get('decision')}, success={result.get('success')}, "
                  f"time={result.get('latency_s')}s")
            if result.get("error"):
                print(f"  Error: {result['error']}")
        except Exception as e:
            print(f"  FAILED: {e}")

        # Cleanup between tasks
        print("  Cleaning up GPU...")
        cleanup_gpu()
        time.sleep(5)

    print("\nDone!")


if __name__ == "__main__":
    main()
