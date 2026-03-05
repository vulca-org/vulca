#!/usr/bin/env python3
"""Threshold sweep — test multiple parameter combinations and find optimal config.

Usage::

    cd wenxin-backend
    python3 app/prototype/tools/run_threshold_sweep.py [--tasks path/to/tasks.json]
    python3 app/prototype/tools/run_threshold_sweep.py --provider nb2 --steps 4
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.tools.run_benchmark import compute_statistics, run_benchmark


# Sweep parameter ranges
SWEEP_PARAMS = {
    "pass_threshold": [0.3, 0.4, 0.5, 0.6],
    "min_dimension_score": [0.1, 0.15, 0.2, 0.25],
    "accept_threshold": [0.5, 0.6, 0.7],
    "early_stop_threshold": [0.7, 0.8, 0.9],
}


def run_sweep(
    tasks_path: str | Path,
    draft_config: DraftConfig | None = None,
) -> list[dict]:
    """Run threshold sweep across parameter combinations.

    To keep runtime manageable, we sweep each parameter independently
    (one-at-a-time) rather than full grid search.
    """
    tasks_path = Path(tasks_path)
    d_cfg = draft_config or DraftConfig(provider="mock", n_candidates=4, seed_base=42)
    results: list[dict] = []

    # Baseline
    baseline = _run_config(tasks_path, "baseline", CriticConfig(), QueenConfig(), d_cfg)
    results.append(baseline)

    # Sweep pass_threshold
    for val in SWEEP_PARAMS["pass_threshold"]:
        cr_cfg = CriticConfig(pass_threshold=val)
        r = _run_config(tasks_path, f"pass_threshold={val}", cr_cfg, QueenConfig(), d_cfg)
        results.append(r)

    # Sweep min_dimension_score
    for val in SWEEP_PARAMS["min_dimension_score"]:
        cr_cfg = CriticConfig(min_dimension_score=val)
        r = _run_config(tasks_path, f"min_dim_score={val}", cr_cfg, QueenConfig(), d_cfg)
        results.append(r)

    # Sweep accept_threshold (Queen)
    for val in SWEEP_PARAMS["accept_threshold"]:
        q_cfg = QueenConfig(accept_threshold=val)
        r = _run_config(tasks_path, f"accept_threshold={val}", CriticConfig(), q_cfg, d_cfg)
        results.append(r)

    # Sweep early_stop_threshold (Queen)
    for val in SWEEP_PARAMS["early_stop_threshold"]:
        q_cfg = QueenConfig(early_stop_threshold=val)
        r = _run_config(tasks_path, f"early_stop={val}", CriticConfig(), q_cfg, d_cfg)
        results.append(r)

    return results


def _run_config(
    tasks_path: Path,
    label: str,
    critic_config: CriticConfig,
    queen_config: QueenConfig,
    draft_config: DraftConfig | None = None,
) -> dict:
    """Run benchmark with a specific config and return summary."""
    d_cfg = draft_config or DraftConfig(provider="mock", n_candidates=4, seed_base=42)
    bench_results = run_benchmark(tasks_path, d_cfg, critic_config, queen_config)
    stats = compute_statistics(bench_results)
    return {
        "label": label,
        "critic_config": critic_config.to_dict(),
        "queen_config": queen_config.to_dict(),
        "stats": stats,
    }


def find_best_config(sweep_results: list[dict]) -> dict:
    """Find the best config balancing quality and cost.

    Score = pass_rate * 0.7 + (1 - normalized_cost) * 0.3
    """
    max_cost = max(r["stats"]["avg_cost_usd"] for r in sweep_results) or 0.01

    best = None
    best_score = -1

    for r in sweep_results:
        pr = r["stats"]["pass_rate"]
        cost_norm = r["stats"]["avg_cost_usd"] / max_cost if max_cost > 0 else 0
        score = pr * 0.7 + (1 - cost_norm) * 0.3

        if score > best_score:
            best_score = score
            best = {**r, "composite_score": round(score, 4)}

    return best


def print_sweep_report(results: list[dict], best: dict) -> None:
    """Print formatted sweep report."""
    print(f"\n{'='*80}")
    print(f"  Threshold Sweep Report ({len(results)} configurations)")
    print(f"{'='*80}")

    print(f"\n  {'Label':<30} {'Pass%':<8} {'AvgCost':<10} {'AvgRnds':<10} {'AvgLat':<10}")
    print(f"  {'─'*30} {'─'*8} {'─'*10} {'─'*10} {'─'*10}")

    for r in results:
        s = r["stats"]
        label = r["label"]
        print(f"  {label:<30} {s['pass_rate']*100:>5.1f}%  ${s['avg_cost_usd']:<8}  {s['avg_rounds']:<10}  {s['avg_latency_ms']:<10}")

    print(f"\n{'─'*80}")
    print(f"  RECOMMENDED CONFIG: {best['label']} (composite score: {best['composite_score']})")
    print(f"  Pass rate: {best['stats']['pass_rate']*100:.1f}%")
    print(f"  Avg cost: ${best['stats']['avg_cost_usd']}")
    print(f"{'='*80}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="VULCA Threshold Sweep")
    default_tasks = Path(__file__).resolve().parent.parent / "data" / "benchmarks" / "tasks-20.json"
    parser.add_argument("--tasks", default=str(default_tasks), help="Path to tasks JSON")
    parser.add_argument(
        "--provider", default="mock", choices=["mock", "nb2"],
        help="Image generation provider (default: mock)",
    )
    parser.add_argument("--api-key", default="", help="Provider API key (fallback: $GOOGLE_API_KEY)")
    parser.add_argument("--width", type=int, default=512, help="Image width (default: 512)")
    parser.add_argument("--height", type=int, default=512, help="Image height (default: 512)")
    parser.add_argument("--steps", type=int, default=4, help="Inference steps (default: 4)")
    parser.add_argument("--n-candidates", type=int, default=4, help="Candidates per round (default: 4)")
    parser.add_argument("--output", default="", help="Path to save JSON results (auto-generated if empty)")
    args = parser.parse_args()

    # Resolve API key
    api_key = args.api_key or os.environ.get("GOOGLE_API_KEY", "")
    if args.provider == "nb2" and not api_key:
        print("ERROR: nb2 requires --api-key or $GOOGLE_API_KEY", file=sys.stderr)
        sys.exit(1)

    d_cfg = DraftConfig(
        provider=args.provider,
        api_key=api_key,
        width=args.width,
        height=args.height,
        steps=args.steps,
        n_candidates=args.n_candidates,
        seed_base=42,
    )

    results = run_sweep(args.tasks, draft_config=d_cfg)
    best = find_best_config(results)
    print_sweep_report(results, best)

    # Save results — filename includes provider
    if args.output:
        output_path = Path(args.output)
    else:
        reports_dir = Path(__file__).resolve().parent.parent / "reports"
        output_path = reports_dir / f"sweep-{args.provider}-results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {"provider": args.provider, "results": results, "best": best},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"  Results saved to: {output_path}")


if __name__ == "__main__":
    main()
