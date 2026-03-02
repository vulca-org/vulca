#!/usr/bin/env python3
"""Validation script for blind evaluation experiment module.

Tests:
1. ExperimentConfig serialization roundtrip
2. TaskSampler generates 30 tasks with balanced categories
3. ExperimentRunner mock mode completes (subset)
4. BlindExporter directory structure
5. Blinding check: no leak patterns in A.md/B.md
6. Annotation template CSV format
7. BlindAnalyzer processes simulated annotations
8. metadata_hidden.json contains complete labels
9. Seed determinism: same (task, group, seed) → same result
10. Orchestrator new switches backward compatible
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

# Ensure project root is on path
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_ROOT))

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  \u2705 {name}")
    else:
        FAIL += 1
        msg = f"  \u274c {name}"
        if detail:
            msg += f" \u2014 {detail}"
        print(msg)


# =========================================================================
# 1. ExperimentConfig serialization roundtrip
# =========================================================================
print("\n=== 1. ExperimentConfig Serialization ===")

from app.prototype.blind_eval.experiment_config import (
    BlindTask,
    ExperimentConfig,
    ExperimentGroup,
    BASELINE_GROUP,
    TREATMENT_GROUP,
    ABLATION_GROUP,
    build_default_config,
)

tasks_for_test = [
    BlindTask("t1", "test subject 1", "chinese_xieyi", "poetic", ["L4"]),
    BlindTask("t2", "test subject 2", "western_academic", "cultural", ["L3"]),
    BlindTask("t3", "test subject 3", "default", "taboo", ["L1"]),
]

cfg = ExperimentConfig(
    groups=[BASELINE_GROUP, TREATMENT_GROUP],
    tasks=tasks_for_test,
    provider="mock",
    seed_base=42,
)

# Roundtrip via JSON
json_str = cfg.to_json()
cfg2 = ExperimentConfig.from_json(json_str)
check("JSON roundtrip groups count", len(cfg2.groups) == 2)
check("JSON roundtrip tasks count", len(cfg2.tasks) == 3)
check("JSON roundtrip provider", cfg2.provider == "mock")
check("JSON roundtrip seed_base", cfg2.seed_base == 42)
check("JSON roundtrip group names", [g.name for g in cfg2.groups] == ["baseline", "treatment"])

# Roundtrip via file
with tempfile.TemporaryDirectory() as tmpdir:
    fpath = Path(tmpdir) / "test_config.json"
    cfg.save(fpath)
    cfg3 = ExperimentConfig.load(fpath)
    check("File roundtrip", len(cfg3.groups) == 2 and len(cfg3.tasks) == 3)

# Pre-defined groups
check("Baseline group switches", not BASELINE_GROUP.enable_agent_critic and not BASELINE_GROUP.enable_evidence_loop and not BASELINE_GROUP.enable_fix_it_plan)
check("Treatment group switches", TREATMENT_GROUP.enable_agent_critic and TREATMENT_GROUP.enable_evidence_loop and TREATMENT_GROUP.enable_fix_it_plan)
check("Ablation group switches", ABLATION_GROUP.enable_agent_critic and not ABLATION_GROUP.enable_evidence_loop and not ABLATION_GROUP.enable_fix_it_plan)

# =========================================================================
# 2. TaskSampler
# =========================================================================
print("\n=== 2. TaskSampler ===")

from app.prototype.blind_eval.task_sampler import sample_tasks, get_category_counts

sampled = sample_tasks(n_per_category=10)
counts = get_category_counts(sampled)

check("Total tasks = 30", len(sampled) == 30, f"got {len(sampled)}")
check("Poetic count = 10", counts.get("poetic", 0) == 10, f"got {counts.get('poetic', 0)}")
check("Cultural count = 10", counts.get("cultural", 0) == 10, f"got {counts.get('cultural', 0)}")
check("Taboo count = 10", counts.get("taboo", 0) == 10, f"got {counts.get('taboo', 0)}")
check("All tasks have subjects", all(t.subject for t in sampled))
check("All tasks have traditions", all(t.tradition for t in sampled))
check("All tasks have categories", all(t.category in ("poetic", "cultural", "taboo") for t in sampled))
check("All task IDs unique", len(set(t.task_id for t in sampled)) == len(sampled))

# =========================================================================
# 3. ExperimentRunner mock mode (subset)
# =========================================================================
print("\n=== 3. ExperimentRunner (mock, subset) ===")

from app.prototype.blind_eval.experiment_runner import ExperimentRunner

with tempfile.TemporaryDirectory() as tmpdir:
    results_dir = Path(tmpdir)
    subset_tasks = sampled[:3]  # Just 3 tasks for speed
    test_config = build_default_config(tasks=subset_tasks, provider="mock")
    runner = ExperimentRunner(test_config, results_dir=results_dir)

    all_results = runner.run_all(subset_tasks)

    check("2 groups executed", len(all_results) == 2)
    for gname, gresults in all_results.items():
        check(f"Group '{gname}' has 3 results", len(gresults) == 3, f"got {len(gresults)}")
        successes = sum(1 for _, o, _ in gresults if o.success)
        check(f"Group '{gname}' all success", successes == 3, f"got {successes}/3")

    # Check output files
    for gname in ["baseline", "treatment"]:
        for task in subset_tasks:
            output_path = results_dir / "raw" / gname / task.task_id / "pipeline_output.json"
            check(f"Output file {gname}/{task.task_id}", output_path.exists())

    # Check config and tasks saved
    check("experiment_config.json saved", (results_dir / "experiment_config.json").exists())
    check("tasks.json saved", (results_dir / "tasks.json").exists())

    # =========================================================================
    # 4. BlindExporter directory structure
    # =========================================================================
    print("\n=== 4. BlindExporter ===")

    from app.prototype.blind_eval.blind_exporter import BlindExporter

    exporter = BlindExporter(results_dir, test_config)
    e1_dir, e2_dir = exporter.export_all()

    check("E1 dir exists", e1_dir.exists())
    check("E2 dir exists", e2_dir.exists())

    for task in subset_tasks:
        tid = task.task_id
        check(f"E1 A.png {tid}", (e1_dir / "outputs" / tid / "A.png").exists())
        check(f"E1 B.png {tid}", (e1_dir / "outputs" / tid / "B.png").exists())
        check(f"E2 A.md {tid}", (e2_dir / "outputs" / tid / "A.md").exists())
        check(f"E2 B.md {tid}", (e2_dir / "outputs" / tid / "B.md").exists())

    # =========================================================================
    # 5. Blinding check: no leak patterns
    # =========================================================================
    print("\n=== 5. Blinding Check ===")

    import re
    LEAK_RE = re.compile(
        r"(CriticLLM|agent_critic|enable_agent|rule_only|baseline|treatment|ablation"
        r"|enable_evidence_loop|enable_fix_it_plan|FixItPlan|NeedMoreEvidence"
        r"|agent=|rule=|hybrid|v2\.6|merged=)",
        re.IGNORECASE,
    )
    REDACTED_RE = re.compile(r"\[REDACTED\]")
    RATIONALE_LEAK_RE = re.compile(r"\*\*\w+\*\*\s*\(score:\s*[\d.]+\):\s*\S")

    leak_found = False
    redacted_found = False
    rationale_leak_found = False
    for task in subset_tasks:
        tid = task.task_id
        for label in ["A.md", "B.md"]:
            md_path = e2_dir / "outputs" / tid / label
            if md_path.exists():
                content = md_path.read_text(encoding="utf-8")
                matches = LEAK_RE.findall(content)
                if matches:
                    leak_found = True
                    check(f"No leaks in {tid}/{label}", False, f"found: {matches}")
                if REDACTED_RE.search(content):
                    redacted_found = True
                if RATIONALE_LEAK_RE.search(content):
                    rationale_leak_found = True

    if not leak_found:
        check("No leak patterns in any E2 outputs", True)
    check("No [REDACTED] residue in E2 outputs", not redacted_found)
    check("No rationale leak after dimension scores", not rationale_leak_found)

    # =========================================================================
    # 6. Annotation template CSV format
    # =========================================================================
    print("\n=== 6. Annotation Template CSV ===")

    e1_csv = e1_dir / "annotation_template.csv"
    e2_csv = e2_dir / "annotation_template.csv"

    check("E1 CSV exists", e1_csv.exists())
    check("E2 CSV exists", e2_csv.exists())

    if e1_csv.exists():
        with open(e1_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            e1_fields = reader.fieldnames or []
            e1_rows = list(reader)
        check("E1 CSV has task_id field", "task_id" in e1_fields)
        check("E1 CSV has preference field", "preference" in e1_fields)
        check("E1 CSV has cultural_fit_A field", "cultural_fit_A" in e1_fields)
        check("E1 CSV row count matches tasks", len(e1_rows) == len(subset_tasks))

    if e2_csv.exists():
        with open(e2_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            e2_fields = reader.fieldnames or []
        check("E2 CSV has evidence_chain_A field", "evidence_chain_A" in e2_fields)
        check("E2 CSV has cross_cultural_B field", "cross_cultural_B" in e2_fields)
        check("E2 CSV has self_consistency_A field", "self_consistency_A" in e2_fields)
        check("E2 CSV has preference field", "preference" in e2_fields)

    # =========================================================================
    # 7. BlindAnalyzer with simulated annotations
    # =========================================================================
    print("\n=== 7. BlindAnalyzer ===")

    from app.prototype.blind_eval.blind_analyzer import (
        analyze_e1,
        generate_report,
        _cohens_kappa,
        _pearson_correlation,
        _bootstrap_ci,
        _rank_data,
        _spearman_correlation,
        compute_system_human_spearman,
    )

    # Create simulated E1 annotations
    sim_e1_path = results_dir / "sim_e1.csv"
    with open(sim_e1_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "rater_id", "preference", "cultural_fit_A", "cultural_fit_B", "notes"])
        writer.writeheader()
        for i, task in enumerate(subset_tasks):
            writer.writerow({
                "task_id": task.task_id,
                "rater_id": "rater1",
                "preference": "A" if i % 2 == 0 else "B",
                "cultural_fit_A": str(3 + i % 3),
                "cultural_fit_B": str(2 + i % 3),
                "notes": "",
            })

    e1_meta_path = e1_dir / "metadata_hidden.json"
    overall, by_cat = analyze_e1(sim_e1_path, e1_meta_path)
    check("E1 analysis total > 0", overall.total > 0, f"total={overall.total}")
    check("E1 win rate in [0,1]", 0.0 <= overall.win_rate <= 1.0)
    check("E1 CI computed", overall.ci_lower <= overall.ci_upper)

    # Test helper functions
    ci_low, ci_high = _bootstrap_ci(7, 10)
    check("Bootstrap CI valid range", 0.0 <= ci_low <= ci_high <= 1.0)

    kappa = _cohens_kappa(["A", "B", "A", "B"], ["A", "B", "B", "A"])
    check("Cohen's kappa computable", -1.0 <= kappa <= 1.0)

    r = _pearson_correlation([1, 2, 3, 4], [1, 2, 3, 4])
    check("Pearson perfect correlation", abs(r - 1.0) < 0.001, f"r={r}")

    r0 = _pearson_correlation([1, 2, 3], [3, 2, 1])
    check("Pearson negative correlation", r0 < 0, f"r={r0}")

    # Spearman correlation tests
    rho_perfect = _spearman_correlation([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    check("Spearman perfect correlation", abs(rho_perfect - 1.0) < 0.001, f"rho={rho_perfect}")

    rho_inverse = _spearman_correlation([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    check("Spearman inverse correlation", abs(rho_inverse - (-1.0)) < 0.001, f"rho={rho_inverse}")

    rho_ties = _spearman_correlation([1, 2, 2, 4], [1, 3, 3, 4])
    check("Spearman with ties computable", -1.0 - 1e-9 <= rho_ties <= 1.0 + 1e-9, f"rho={rho_ties}")

    # Rank data tests
    ranks = _rank_data([10, 30, 20, 20])
    check("Rank data handles ties", ranks == [1.0, 4.0, 2.5, 2.5], f"ranks={ranks}")

    # compute_system_human_spearman wrapper
    rho_wrap = compute_system_human_spearman([1, 2, 3], [1, 2, 3])
    check("compute_system_human_spearman works", abs(rho_wrap - 1.0) < 0.001, f"rho={rho_wrap}")

    # Generate report
    report = generate_report(results_dir, e1_annotations=sim_e1_path)
    check("Report generated", len(report) > 100, f"len={len(report)}")
    check("Report contains header", "# Blind Evaluation Analysis Report" in report)
    check("Report saved", (results_dir / "analysis" / "analysis_report.md").exists())

    # =========================================================================
    # 8. metadata_hidden.json completeness
    # =========================================================================
    print("\n=== 8. metadata_hidden.json ===")

    for track, track_dir in [("E1", e1_dir), ("E2", e2_dir)]:
        meta_path = track_dir / "metadata_hidden.json"
        check(f"{track} metadata exists", meta_path.exists())
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            check(f"{track} metadata has entries", len(meta) == len(subset_tasks))
            for item in meta:
                check(
                    f"{track} {item['task_id']} has A_group",
                    "A_group" in item and item["A_group"] in ("baseline", "treatment"),
                )
                check(
                    f"{track} {item['task_id']} has B_group",
                    "B_group" in item and item["B_group"] in ("baseline", "treatment"),
                )
                check(
                    f"{track} {item['task_id']} A!=B",
                    item.get("A_group") != item.get("B_group"),
                )

    # =========================================================================
    # 9. Seed determinism
    # =========================================================================
    print("\n=== 9. Seed Determinism ===")

    seed1 = runner.get_deterministic_seed("task-001", "baseline")
    seed2 = runner.get_deterministic_seed("task-001", "baseline")
    seed3 = runner.get_deterministic_seed("task-001", "treatment")
    seed4 = runner.get_deterministic_seed("task-002", "baseline")

    check("Same input → same seed", seed1 == seed2)
    check("Different group → different seed", seed1 != seed3)
    check("Different task → different seed", seed1 != seed4)
    check("Seed in valid range", 0 <= seed1 < 2**31)

# =========================================================================
# 10. Orchestrator new switches backward compatible
# =========================================================================
print("\n=== 10. Orchestrator Backward Compatibility ===")

from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.pipeline.pipeline_types import PipelineInput

# Default (all True) should work identically to before
orch_default = PipelineOrchestrator()
check("Default enable_evidence_loop=True", orch_default.enable_evidence_loop is True)
check("Default enable_fix_it_plan=True", orch_default.enable_fix_it_plan is True)
check("Default enable_agent_critic=False", orch_default.enable_agent_critic is False)

# Explicit switches
orch_off = PipelineOrchestrator(
    enable_agent_critic=True,
    enable_evidence_loop=False,
    enable_fix_it_plan=False,
)
check("Explicit switches stored", not orch_off.enable_evidence_loop and not orch_off.enable_fix_it_plan)

# Quick smoke test: mock run with defaults should succeed
pi = PipelineInput(task_id="compat-test", subject="backward compat test", cultural_tradition="default")
output = orch_default.run_sync(pi)
check("Default orchestrator mock run succeeds", output.success, f"error={output.error}")

# Mock run with switches off should also succeed (just disables loops)
orch_baseline = PipelineOrchestrator(
    enable_agent_critic=False,
    enable_evidence_loop=False,
    enable_fix_it_plan=False,
)
output2 = orch_baseline.run_sync(pi)
check("Baseline orchestrator mock run succeeds", output2.success, f"error={output2.error}")


# =========================================================================
# Summary
# =========================================================================
print(f"\n{'='*60}")
print(f"Blind Evaluation Validation: {PASS} passed, {FAIL} failed")
print(f"{'='*60}")

if FAIL > 0:
    sys.exit(1)
