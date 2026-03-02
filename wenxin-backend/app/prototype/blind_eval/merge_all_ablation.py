"""
Merge all ablation results across scattered runs into a unified dataset,
run statistical tests, and produce a comprehensive analysis report.
"""
import json, os, glob, sys
from collections import defaultdict
from pathlib import Path
import math

BASE = Path(__file__).parent / "results" / "ablation"

# ── Condition definitions ──
COND_LABELS = {
    "A": "SD1.5 + Rule-Only + Single + No Route",
    "B": "SD1.5 + Rule+LLM + Multi + Cultural Route",
    "C": "FLUX + Rule-Only + Single + No Route",
    "D": "FLUX + Rule+LLM + Multi + Cultural Route",
    "E": "FLUX + Rule-Only + Multi + Cultural Route",
    "F": "FLUX + Rule+LLM + Single + Cultural Route",
    # v2 conditions (tightened thresholds)
    "Cp": "FLUX + Rule-Only + Single + Route (v2 baseline)",
    "Dp": "FLUX + Rule+LLM + Multi + Route (v2 full)",
    "Ep": "FLUX + Rule-Only + Multi + Route (v2 loop)",
}

DIMS = ["visual_perception", "technical_analysis", "cultural_context",
        "critical_interpretation", "philosophical_aesthetic"]
DIM_SHORT = {"visual_perception": "L1", "technical_analysis": "L2",
             "cultural_context": "L3", "critical_interpretation": "L4",
             "philosophical_aesthetic": "L5"}

# ── Priority: prefer REAL mode, then latest run ──
def _collect_all():
    """Collect ALL successful task results, preferring real-mode runs."""
    # First pass: catalog every run's mode
    run_modes = {}
    for run_dir in sorted(glob.glob(str(BASE / "run_*"))):
        cfg_path = os.path.join(run_dir, "experiment_config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = json.load(f)
            run_modes[os.path.basename(run_dir)] = cfg.get("mode", "mock")

    # Second pass: for each (condition, task), collect best result
    # Priority: real > mock, then latest run timestamp
    results = {}  # (cond, task_id) -> {score, dims, rounds, ...}

    for run_dir in sorted(glob.glob(str(BASE / "run_*"))):
        run_name = os.path.basename(run_dir)
        mode = run_modes.get(run_name, "mock")
        
        # Try all_results.json first (has dimension scores)
        arf = os.path.join(run_dir, "all_results.json")
        ar_data = {}
        if os.path.exists(arf):
            with open(arf) as f:
                ar_data = json.load(f)

        # Also get task categories from config
        cfg_path = os.path.join(run_dir, "experiment_config.json")
        task_cats = {}
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = json.load(f)
            for t in cfg.get("tasks", []):
                task_cats[t["task_id"]] = t.get("category", "?")

        raw_dir = os.path.join(run_dir, "raw")
        if not os.path.isdir(raw_dir):
            continue

        for cond_name in os.listdir(raw_dir):
            cond_dir = os.path.join(raw_dir, cond_name)
            if not os.path.isdir(cond_dir):
                continue
            cond = cond_name.replace("condition_", "")

            for task_name in os.listdir(cond_dir):
                pf = os.path.join(cond_dir, task_name, "pipeline_output.json")
                if not os.path.exists(pf):
                    continue
                with open(pf) as f:
                    po = json.load(f)
                if not po.get("success"):
                    continue

                key = (cond, task_name)
                existing = results.get(key)

                # Extract score from pipeline_output stages
                score = None
                for s in po.get("stages", []):
                    if s.get("stage") == "critic":
                        out = s.get("output_summary", {})
                        if isinstance(out, dict):
                            score = out.get("best_weighted_total")

                # Try to get dimension scores from all_results.json
                dim_scores = {}
                ar_entries = ar_data.get(cond, [])
                for e in ar_entries:
                    if isinstance(e, dict) and e.get("task_id") == task_name and e.get("success"):
                        dim_scores = e.get("dimension_scores", {})
                        if score is None:
                            score = e.get("best_weighted_total", score)
                        break

                # Fallback: get dimension scores from checkpoint files
                if not dim_scores:
                    ckpt_id = f"abl-{cond}_{task_name}"
                    ckpt_path = (
                        Path(__file__).resolve().parent.parent
                        / "checkpoints" / "pipeline" / ckpt_id / "stage_critic.json"
                    )
                    if ckpt_path.exists():
                        try:
                            ckpt = json.loads(ckpt_path.read_text(encoding="utf-8"))
                            scored = ckpt.get("scored_candidates", [])
                            if scored:
                                best = scored[0]
                                for ds in best.get("dimension_scores", []):
                                    dim_scores[ds["dimension"]] = ds["score"]
                                if score is None:
                                    score = best.get("weighted_total", score)
                        except Exception:
                            pass

                if score is None:
                    continue

                entry = {
                    "score": score,
                    "rounds": po.get("total_rounds", 1),
                    "decision": po.get("final_decision", "?"),
                    "latency_ms": po.get("total_latency_ms", 0),
                    "category": task_cats.get(task_name, "?"),
                    "dim_scores": dim_scores,
                    "mode": mode,
                    "run": run_name,
                }

                # Priority: real > mock, then newer run
                if existing is None:
                    results[key] = entry
                elif mode == "real" and existing["mode"] == "mock":
                    results[key] = entry
                elif mode == existing["mode"] and run_name > existing["run"]:
                    results[key] = entry

    return results


def _paired_ttest(scores_a, scores_b):
    """Paired t-test (two-tailed).

    Returns (t_stat, p_value, cohen_dz, cohen_dav).

    cohen_dz  = mean(diffs) / sd(diffs)   — paired effect size (within-subject)
    cohen_dav = mean(diffs) / pooled_sd    — average-SD effect size (between-subject comparable)
    """
    n = len(scores_a)
    if n < 2:
        return 0, 1.0, 0, 0
    diffs = [b - a for a, b in zip(scores_a, scores_b)]
    mean_d = sum(diffs) / n
    var_d = sum((d - mean_d) ** 2 for d in diffs) / (n - 1)
    sd_d = math.sqrt(var_d) if var_d > 0 else 1e-10
    t_stat = mean_d / (sd_d / math.sqrt(n))
    # p-value via t-distribution (Abramowitz-Stegun approximation)
    df = n - 1
    if df >= 30:
        p = 2 * (1 - _norm_cdf(abs(t_stat)))
    else:
        p = 2 * (1 - _t_cdf(abs(t_stat), df))
    # R6-2: Compute both effect size variants to avoid misinterpretation
    cohen_dz = mean_d / sd_d if sd_d > 0 else 0
    # Pooled SD (d_av): sqrt((var_a + var_b) / 2)
    mean_a = sum(scores_a) / n
    mean_b = sum(scores_b) / n
    var_a = sum((x - mean_a) ** 2 for x in scores_a) / (n - 1) if n > 1 else 0
    var_b = sum((x - mean_b) ** 2 for x in scores_b) / (n - 1) if n > 1 else 0
    pooled_sd = math.sqrt((var_a + var_b) / 2) if (var_a + var_b) > 0 else 1e-10
    cohen_dav = mean_d / pooled_sd
    return t_stat, p, cohen_dz, cohen_dav


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _t_cdf(t, df):
    """Approximation of Student's t CDF."""
    x = df / (df + t * t)
    # Regularized incomplete beta function approximation
    # Use series expansion for I_x(a, b) where a=df/2, b=0.5
    a = df / 2
    b = 0.5
    # For reasonable accuracy, use the continued fraction method
    # Simplified: just use normal approx with correction
    z = t * (1 - 1/(4*df)) / math.sqrt(1 + t*t/(2*df))
    return _norm_cdf(z)


def _wilcoxon_test(scores_a, scores_b):
    """Wilcoxon signed-rank test. Returns (W_stat, approx_p, r_effect)."""
    n = len(scores_a)
    diffs = [(b - a) for a, b in zip(scores_a, scores_b)]
    # Remove zeros
    nonzero = [(abs(d), 1 if d > 0 else -1, d) for d in diffs if abs(d) > 1e-10]
    if len(nonzero) < 2:
        return 0, 1.0, 0
    # Rank by absolute value
    nonzero.sort(key=lambda x: x[0])
    n_eff = len(nonzero)
    W_plus = 0
    W_minus = 0
    for rank, (_, sign, _) in enumerate(nonzero, 1):
        if sign > 0:
            W_plus += rank
        else:
            W_minus += rank
    W = min(W_plus, W_minus)
    # Normal approximation for n >= 10
    mean_w = n_eff * (n_eff + 1) / 4
    sd_w = math.sqrt(n_eff * (n_eff + 1) * (2 * n_eff + 1) / 24)
    z = (W - mean_w) / sd_w if sd_w > 0 else 0
    p = 2 * (1 - _norm_cdf(abs(z)))
    r = abs(z) / math.sqrt(n_eff)
    return W, p, r


def main():
    results = _collect_all()
    
    # Get all task IDs (should be 30)
    all_tasks = sorted(set(tid for _, tid in results.keys()))
    all_conds = sorted(set(c for c, _ in results.keys()))
    
    print("=" * 80)
    print("VULCA ABLATION EXPERIMENT — UNIFIED ANALYSIS")
    from datetime import date
    print(f"Date: {date.today().isoformat()} | Tasks: {len(all_tasks)} | Conditions: {len(all_conds)}")
    print("=" * 80)
    
    # ── 1. Overview table ──
    print("\n## 1. Condition Overview\n")
    print(f"{'Cond':>4} | {'Label':40s} | {'Mode':>4} | {'N':>3} | {'Avg':>6} | {'Rnd':>4} | {'Rerun%':>6} | {'Accept%':>7}")
    print("-" * 100)
    
    cond_scores = {}
    cond_task_scores = {}  # {cond: {task_id: score}}
    
    for cond in all_conds:
        entries = {tid: results[(cond, tid)] for tid in all_tasks if (cond, tid) in results}
        scores = [e["score"] for e in entries.values()]
        rounds = [e["rounds"] for e in entries.values()]
        rerun = sum(1 for e in entries.values() if e["rounds"] > 1)
        accept = sum(1 for e in entries.values() if e["decision"] == "accept")
        modes = set(e["mode"] for e in entries.values())
        mode_str = "/".join(sorted(modes))
        
        avg_s = sum(scores) / len(scores) if scores else 0
        avg_r = sum(rounds) / len(rounds) if rounds else 0
        rerun_pct = rerun / len(entries) * 100 if entries else 0
        accept_pct = accept / len(entries) * 100 if entries else 0
        
        cond_scores[cond] = {"avg": avg_s, "entries": entries}
        cond_task_scores[cond] = {tid: e["score"] for tid, e in entries.items()}
        
        print(f"  {cond:>2} | {COND_LABELS.get(cond,''):40s} | {mode_str:>4} | {len(entries):>3} | {avg_s:.3f} | {avg_r:.1f} | {rerun_pct:5.1f}% | {accept_pct:6.1f}%")
    
    # ── 2. Per-dimension breakdown ──
    print("\n## 2. L1-L5 Dimension Averages\n")
    header = f"{'Cond':>4}"
    for d in DIMS:
        header += f" | {DIM_SHORT[d]:>6}"
    print(header)
    print("-" * 60)
    
    for cond in all_conds:
        entries = {tid: results[(cond, tid)] for tid in all_tasks if (cond, tid) in results}
        line = f"  {cond:>2}"
        for d in DIMS:
            vals = [e["dim_scores"].get(d, 0) for e in entries.values() if e["dim_scores"]]
            avg = sum(vals) / len(vals) if vals else 0
            line += f" | {avg:6.3f}" if vals else " |    N/A"
        print(line)
    
    # ── 3. Category breakdown ──
    print("\n## 3. Category Breakdown\n")
    for cat in ["cultural", "poetic", "taboo"]:
        print(f"\n### {cat.title()}")
        print(f"{'Cond':>4} | {'N':>3} | {'Avg':>6} | {'Rnd':>4} | {'Rerun%':>6}")
        print("-" * 40)
        for cond in all_conds:
            entries = {tid: results[(cond, tid)] for tid in all_tasks 
                      if (cond, tid) in results and results[(cond, tid)]["category"] == cat}
            if not entries:
                continue
            scores = [e["score"] for e in entries.values()]
            rounds = [e["rounds"] for e in entries.values()]
            rerun = sum(1 for e in entries.values() if e["rounds"] > 1)
            avg_s = sum(scores) / len(scores)
            avg_r = sum(rounds) / len(rounds)
            print(f"  {cond:>2} | {len(entries):>3} | {avg_s:.3f} | {avg_r:.1f} | {rerun/len(entries)*100:5.1f}%")
    
    # ── 4. Statistical Tests ──
    print("\n" + "=" * 80)
    print("## 4. STATISTICAL SIGNIFICANCE TESTS")
    print("=" * 80)
    
    comparisons = [
        # v1 comparisons
        ("A", "B", "Agent loop effect (SD1.5): single-rule vs multi-LLM-route"),
        ("C", "D", "Agent loop effect (FLUX): single-rule vs multi-LLM-route [CORE]"),
        ("A", "C", "Model upgrade: SD1.5 → FLUX (both rule-only)"),
        ("B", "D", "Model upgrade: SD1.5 → FLUX (both agent)"),
        ("C", "E", "Multi-round effect: single vs multi (both rule-only, FLUX)"),
        ("C", "F", "LLM effect: rule-only vs rule+LLM (both single, FLUX)"),
        ("E", "D", "LLM incremental: add LLM to loop+route"),
        ("F", "D", "Loop incremental: add loop to LLM+route"),
        # v2 comparisons (tightened thresholds — actually trigger multi-round)
        ("Cp", "Dp", "v2 CORE: baseline vs full system"),
        ("Cp", "Ep", "v2: loop effect (rule-only multi-round)"),
        ("Ep", "Dp", "v2: LLM incremental in loop"),
        ("C", "Cp", "v1→v2 baseline comparison"),
    ]
    
    print(f"\n{'Comparison':>8} | {'Hypothesis':55s} | {'Δ Score':>8} | {'t-stat':>7} | {'p-value':>8} | {'Cohen d':>8} | {'Sig?':>5}")
    print("-" * 130)
    
    for c1, c2, hypothesis in comparisons:
        # Get paired scores (same tasks)
        common_tasks = sorted(set(cond_task_scores.get(c1, {}).keys()) & 
                             set(cond_task_scores.get(c2, {}).keys()))
        if len(common_tasks) < 5:
            print(f"  {c1}→{c2:>2} | {hypothesis:55s} | N/A (only {len(common_tasks)} paired)")
            continue
        
        s1 = [cond_task_scores[c1][t] for t in common_tasks]
        s2 = [cond_task_scores[c2][t] for t in common_tasks]
        
        delta = sum(s2) / len(s2) - sum(s1) / len(s1)
        t_stat, p_val, cohen_dz, cohen_dav = _paired_ttest(s1, s2)
        w_stat, w_p, w_r = _wilcoxon_test(s1, s2)

        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
        sign = "+" if delta > 0 else ""

        print(f"  {c1}→{c2:>2} | {hypothesis:55s} | {sign}{delta:.4f} | {t_stat:7.3f} | {p_val:8.5f} | dz={cohen_dz:.3f} dav={cohen_dav:.3f} | {sig:>5}")
    
    # ── 4b. Per-dimension paired tests for CORE comparison C vs D ──
    print(f"\n### C vs D Per-Dimension (CORE comparison)")
    print(f"{'Dim':>6} | {'C avg':>6} | {'D avg':>6} | {'Δ':>7} | {'t-stat':>7} | {'p-value':>8} | {'Sig?':>5}")
    print("-" * 65)
    
    common_cd = sorted(set(cond_task_scores.get("C", {}).keys()) & 
                       set(cond_task_scores.get("D", {}).keys()))
    
    for d in DIMS:
        c_vals = []
        d_vals = []
        for tid in common_cd:
            c_entry = results.get(("C", tid))
            d_entry = results.get(("D", tid))
            if c_entry and d_entry and c_entry["dim_scores"] and d_entry["dim_scores"]:
                cv = c_entry["dim_scores"].get(d)
                dv = d_entry["dim_scores"].get(d)
                if cv is not None and dv is not None:
                    c_vals.append(cv)
                    d_vals.append(dv)
        
        if len(c_vals) >= 5:
            c_avg = sum(c_vals) / len(c_vals)
            d_avg = sum(d_vals) / len(d_vals)
            delta = d_avg - c_avg
            t_stat, p_val, cohen_dz, cohen_dav = _paired_ttest(c_vals, d_vals)
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            sign = "+" if delta > 0 else ""
            print(f"  {DIM_SHORT[d]:>4} | {c_avg:.3f} | {d_avg:.3f} | {sign}{delta:.4f} | {t_stat:7.3f} | {p_val:8.5f} | dz={cohen_dz:.3f} dav={cohen_dav:.3f} | {sig:>5}")
    
    # ── 4c. v2 Per-dimension: Cp vs Dp ──
    common_v2 = sorted(set(cond_task_scores.get("Cp", {}).keys()) &
                       set(cond_task_scores.get("Dp", {}).keys()))
    if common_v2:
        print(f"\n### Cp vs Dp Per-Dimension (v2 CORE comparison, n={len(common_v2)})")
        print(f"{'Dim':>6} | {'Cp avg':>7} | {'Dp avg':>7} | {'Δ':>7} | {'t-stat':>7} | {'p-value':>8} | {'Cohen d':>8} | {'Sig?':>5}")
        print("-" * 80)
        for d in DIMS:
            cp_vals, dp_vals = [], []
            for tid in common_v2:
                cp_e = results.get(("Cp", tid))
                dp_e = results.get(("Dp", tid))
                if cp_e and dp_e and cp_e["dim_scores"] and dp_e["dim_scores"]:
                    cv = cp_e["dim_scores"].get(d)
                    dv = dp_e["dim_scores"].get(d)
                    if cv is not None and dv is not None:
                        cp_vals.append(cv)
                        dp_vals.append(dv)
            if len(cp_vals) >= 5:
                cp_avg = sum(cp_vals) / len(cp_vals)
                dp_avg = sum(dp_vals) / len(dp_vals)
                delta = dp_avg - cp_avg
                t_stat, p_val, cohen_dz, cohen_dav = _paired_ttest(cp_vals, dp_vals)
                sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
                sign = "+" if delta > 0 else ""
                print(f"  {DIM_SHORT[d]:>4} | {cp_avg:.4f} | {dp_avg:.4f} | {sign}{delta:.4f} | {t_stat:7.3f} | {p_val:8.5f} | dz={cohen_dz:.3f} dav={cohen_dav:.3f} | {sig:>5}")

    # ── 5. Key Research Questions ──
    print("\n" + "=" * 80)
    print("## 5. RESEARCH QUESTIONS — VERDICT")
    print("=" * 80)
    
    def _get_avg(cond):
        return cond_scores.get(cond, {}).get("avg", 0)
    
    # RQ1: Does the agent loop work?
    delta_cd = _get_avg("D") - _get_avg("C")
    delta_ab = _get_avg("B") - _get_avg("A")
    
    print(f"""
RQ1: Does the multi-agent self-correction loop improve generation quality?
     C→D (FLUX):  {_get_avg('C'):.3f} → {_get_avg('D'):.3f} (Δ={delta_cd:+.3f})
     A→B (SD1.5): {_get_avg('A'):.3f} → {_get_avg('B'):.3f} (Δ={delta_ab:+.3f})
     → {'YES ✓' if delta_cd > 0 and delta_ab > 0 else 'MIXED' if delta_cd > 0 or delta_ab > 0 else 'NO ✗'}
""")
    
    # RQ2: LLM vs Rule-only
    delta_ef = _get_avg("D") - _get_avg("E")
    delta_cf = _get_avg("F") - _get_avg("C")
    print(f"""RQ2: Does LLM Critic add value beyond rules?
     E→D (add LLM to loop):    {_get_avg('E'):.3f} → {_get_avg('D'):.3f} (Δ={delta_ef:+.3f})
     C→F (add LLM, no loop):   {_get_avg('C'):.3f} → {_get_avg('F'):.3f} (Δ={delta_cf:+.3f})
     → {'YES ✓' if delta_ef > 0 and delta_cf > 0 else 'MIXED' if delta_ef > 0 or delta_cf > 0 else 'NO ✗'}
""")
    
    # RQ3: Multi-round
    delta_ce = _get_avg("E") - _get_avg("C")
    delta_fd = _get_avg("D") - _get_avg("F")
    print(f"""RQ3: Does multi-round iteration help?
     C→E (add loop, no LLM):   {_get_avg('C'):.3f} → {_get_avg('E'):.3f} (Δ={delta_ce:+.3f})
     F→D (add loop to LLM):    {_get_avg('F'):.3f} → {_get_avg('D'):.3f} (Δ={delta_fd:+.3f})
     → {'YES ✓' if delta_ce > 0 and delta_fd > 0 else 'MIXED' if delta_ce > 0 or delta_fd > 0 else 'NO ✗'}
""")
    
    # RQ4: Cultural routing
    # Compare B (with route) taboo rerun rate
    b_taboo = [results[(c, t)] for c, t in results if c == "B" and results[(c,t)].get("category") == "taboo"]
    b_taboo_rerun = sum(1 for e in b_taboo if e["rounds"] > 1) / len(b_taboo) * 100 if b_taboo else 0
    d_taboo = [results[(c, t)] for c, t in results if c == "D" and results[(c,t)].get("category") == "taboo"]
    d_taboo_rerun = sum(1 for e in d_taboo if e["rounds"] > 1) / len(d_taboo) * 100 if d_taboo else 0
    
    b_entries = cond_scores.get("B", {}).get("entries", {})
    d_entries = cond_scores.get("D", {}).get("entries", {})
    b_overall_rerun = sum(1 for e in b_entries.values() if e["rounds"] > 1) / len(b_entries) * 100 if b_entries else 0
    d_overall_rerun = sum(1 for e in d_entries.values() if e["rounds"] > 1) / len(d_entries) * 100 if d_entries else 0
    print(f"""RQ4: Does cultural routing concentrate correction on sensitive tasks?
     B taboo rerun rate: {b_taboo_rerun:.0f}%   (vs overall B: {b_overall_rerun:.0f}%)
     D taboo rerun rate: {d_taboo_rerun:.0f}%   (vs overall D: {d_overall_rerun:.0f}%)
     → {'YES ✓' if b_taboo_rerun > 30 or d_taboo_rerun > 30 else 'WEAK'}
""")
    
    # RQ5: Model quality
    delta_ac = _get_avg("C") - _get_avg("A")
    delta_bd = _get_avg("D") - _get_avg("B")
    print(f"""RQ5: Does base model quality matter?
     A→C (SD1.5→FLUX, rule):   {_get_avg('A'):.3f} → {_get_avg('C'):.3f} (Δ={delta_ac:+.3f})
     B→D (SD1.5→FLUX, agent):  {_get_avg('B'):.3f} → {_get_avg('D'):.3f} (Δ={delta_bd:+.3f})
     → {'YES ✓' if delta_ac > 0 or delta_bd > 0 else 'NO ✗'}
""")
    
    # ── 6. Export unified dataset ──
    export = []
    for (cond, tid), entry in sorted(results.items()):
        export.append({
            "condition": cond,
            "task_id": tid,
            "category": entry["category"],
            "score": round(entry["score"], 4),
            "rounds": entry["rounds"],
            "decision": entry["decision"],
            "latency_ms": entry["latency_ms"],
            "mode": entry["mode"],
            "source_run": entry["run"],
            "dim_scores": {DIM_SHORT.get(k, k): round(v, 4) for k, v in entry["dim_scores"].items()} if entry["dim_scores"] else {},
        })
    
    out_path = BASE / "unified_ablation_results.json"
    with open(out_path, "w") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"\nUnified dataset exported: {out_path} ({len(export)} entries)")


if __name__ == "__main__":
    main()
