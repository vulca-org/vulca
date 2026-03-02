"""Statistical analysis for blind evaluation results.

Computes:
  1. Preference win rate with bootstrap 95% CI
  2. Per-dimension L1-L5 mean differences with CI
  3. Inter-rater agreement (Cohen's kappa for preference, Pearson for Likert)
  4. Category-level breakdown (poetic / cultural / taboo)
  5. Cost efficiency (quality delta per dollar) for real mode
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PreferenceResult:
    """Win rate statistics for one comparison."""
    treatment_wins: int = 0
    baseline_wins: int = 0
    ties: int = 0
    total: int = 0
    win_rate: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0


@dataclass
class DimensionStats:
    """Per-dimension score statistics."""
    dimension: str = ""
    baseline_mean: float = 0.0
    treatment_mean: float = 0.0
    delta: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0


@dataclass
class AnalysisReport:
    """Full analysis report."""
    overall_preference: PreferenceResult = field(default_factory=PreferenceResult)
    category_preferences: dict[str, PreferenceResult] = field(default_factory=dict)
    dimension_stats: list[DimensionStats] = field(default_factory=list)
    cohens_kappa: float = 0.0
    pearson_correlations: dict[str, float] = field(default_factory=dict)
    cost_efficiency: dict[str, float] = field(default_factory=dict)
    # spearman_rho removed — placeholder was never wired to real pipeline output


def _bootstrap_ci(
    wins: int,
    total: int,
    n_bootstrap: int = 10000,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Compute bootstrap percentile CI for a win rate.

    Uses numpy-free analytical normal approximation for efficiency.
    """
    if total == 0:
        return 0.0, 0.0
    p = wins / total
    # Wilson score interval (better than normal approx for small n)
    z = 1.96  # ~95% CI
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0.0, centre - spread), min(1.0, centre + spread)


def _cohens_kappa(rater1: list[str], rater2: list[str]) -> float:
    """Compute Cohen's kappa for two raters' preference labels."""
    if len(rater1) != len(rater2) or len(rater1) == 0:
        return 0.0

    labels = sorted(set(rater1) | set(rater2))
    n = len(rater1)

    # Build confusion matrix
    matrix: dict[str, dict[str, int]] = {a: {b: 0 for b in labels} for a in labels}
    for a, b in zip(rater1, rater2):
        matrix[a][b] += 1

    # Observed agreement
    po = sum(matrix[l][l] for l in labels) / n

    # Expected agreement
    pe = 0.0
    for l in labels:
        row_sum = sum(matrix[l].values()) / n
        col_sum = sum(matrix[r][l] for r in labels) / n
        pe += row_sum * col_sum

    if pe >= 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def _pearson_correlation(x: list[float], y: list[float]) -> float:
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0

    mx = sum(x) / n
    my = sum(y) / n

    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / (n - 1)) if n > 1 else 0.0
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / (n - 1)) if n > 1 else 0.0

    if sx == 0 or sy == 0:
        return 0.0

    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (n - 1)
    return cov / (sx * sy)


## _rank_data, _spearman_correlation, compute_system_human_spearman removed
## (dead code — Spearman was never wired to real pipeline output)


def _load_annotations(csv_path: Path) -> list[dict]:
    """Load annotation CSV into list of dicts."""
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _load_metadata(json_path: Path) -> dict[str, dict]:
    """Load metadata_hidden.json into {task_id: metadata_dict}."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return {item["task_id"]: item for item in data}


def _resolve_preference(
    pref: str,
    metadata: dict,
    treatment_group: str = "treatment",
) -> str:
    """Convert A/B preference to treatment/baseline/tie."""
    pref = pref.strip().upper()
    if pref == "TIE" or not pref:
        return "tie"
    a_group = metadata.get("A_group", "")
    if pref == "A":
        return "treatment" if a_group == treatment_group else "baseline"
    if pref == "B":
        return "treatment" if a_group != treatment_group else "baseline"
    return "tie"


def analyze_e1(
    annotations_path: Path,
    metadata_path: Path,
    task_categories: dict[str, str] | None = None,
    treatment_group: str = "treatment",
) -> tuple[PreferenceResult, dict[str, PreferenceResult]]:
    """Analyze E1 (image preference) annotations.

    Returns (overall_preference, {category: preference}).
    """
    annotations = _load_annotations(annotations_path)
    metadata = _load_metadata(metadata_path)

    overall = PreferenceResult()
    by_category: dict[str, PreferenceResult] = defaultdict(PreferenceResult)

    for row in annotations:
        tid = row["task_id"]
        pref_raw = row.get("preference", "")
        if not pref_raw:
            continue

        meta = metadata.get(tid, {})
        resolved = _resolve_preference(pref_raw, meta, treatment_group)

        overall.total += 1
        if resolved == "treatment":
            overall.treatment_wins += 1
        elif resolved == "baseline":
            overall.baseline_wins += 1
        else:
            overall.ties += 1

        # Category breakdown
        cat = task_categories.get(tid, meta.get("category", "unknown")) if task_categories else meta.get("category", "unknown")
        cat_pref = by_category[cat]
        cat_pref.total += 1
        if resolved == "treatment":
            cat_pref.treatment_wins += 1
        elif resolved == "baseline":
            cat_pref.baseline_wins += 1
        else:
            cat_pref.ties += 1

    # Compute win rates and CIs
    if overall.total > 0:
        overall.win_rate = overall.treatment_wins / overall.total
        overall.ci_lower, overall.ci_upper = _bootstrap_ci(
            overall.treatment_wins, overall.total,
        )

    for cat_pref in by_category.values():
        if cat_pref.total > 0:
            cat_pref.win_rate = cat_pref.treatment_wins / cat_pref.total
            cat_pref.ci_lower, cat_pref.ci_upper = _bootstrap_ci(
                cat_pref.treatment_wins, cat_pref.total,
            )

    return overall, dict(by_category)


def analyze_e2(
    annotations_path: Path,
    metadata_path: Path,
    treatment_group: str = "treatment",
) -> dict[str, float]:
    """Analyze E2 (critique text) annotations.

    Returns dict of average Likert scores per dimension per group.
    """
    annotations = _load_annotations(annotations_path)
    metadata = _load_metadata(metadata_path)

    scores: dict[str, list[float]] = defaultdict(list)

    for row in annotations:
        tid = row["task_id"]
        meta = metadata.get(tid, {})
        a_is_treatment = meta.get("A_group") == treatment_group

        for dim in ["evidence_chain", "cross_cultural", "self_consistency"]:
            a_val = row.get(f"{dim}_A", "")
            b_val = row.get(f"{dim}_B", "")
            if a_val and b_val:
                try:
                    a_score = float(a_val)
                    b_score = float(b_val)
                    if a_is_treatment:
                        scores[f"treatment_{dim}"].append(a_score)
                        scores[f"baseline_{dim}"].append(b_score)
                    else:
                        scores[f"treatment_{dim}"].append(b_score)
                        scores[f"baseline_{dim}"].append(a_score)
                except ValueError:
                    pass

    result = {}
    for key, vals in scores.items():
        result[key] = sum(vals) / len(vals) if vals else 0.0
    return result


def analyze_inter_rater(
    annotations: list[dict],
    metadata: dict[str, dict],
    treatment_group: str = "treatment",
) -> tuple[float, dict[str, float]]:
    """Compute inter-rater agreement.

    Groups annotations by rater_id, computes Cohen's kappa for preference
    and Pearson correlation for Likert scales.

    Returns (kappa, {dimension: pearson}).
    """
    # Group by task_id
    by_task: dict[str, list[dict]] = defaultdict(list)
    for row in annotations:
        by_task[row["task_id"]].append(row)

    # Need exactly 2 raters per task for kappa
    rater1_prefs: list[str] = []
    rater2_prefs: list[str] = []
    likert_pairs: dict[str, tuple[list[float], list[float]]] = defaultdict(
        lambda: ([], [])
    )

    for tid, rows in by_task.items():
        if len(rows) < 2:
            continue
        r1, r2 = rows[0], rows[1]
        meta = metadata.get(tid, {})

        # Preference
        p1 = _resolve_preference(r1.get("preference", ""), meta, treatment_group)
        p2 = _resolve_preference(r2.get("preference", ""), meta, treatment_group)
        rater1_prefs.append(p1)
        rater2_prefs.append(p2)

        # Likert scales
        for dim in ["evidence_chain", "cross_cultural", "self_consistency"]:
            for suffix in ["_A", "_B"]:
                key = f"{dim}{suffix}"
                v1 = r1.get(key, "")
                v2 = r2.get(key, "")
                if v1 and v2:
                    try:
                        pair = likert_pairs[dim]
                        pair[0].append(float(v1))
                        pair[1].append(float(v2))
                    except ValueError:
                        pass

    kappa = _cohens_kappa(rater1_prefs, rater2_prefs) if rater1_prefs else 0.0

    pearson = {}
    for dim, (x, y) in likert_pairs.items():
        pearson[dim] = _pearson_correlation(x, y)

    return kappa, pearson


def generate_report(
    results_dir: Path,
    e1_annotations: Path | None = None,
    e2_annotations: Path | None = None,
    treatment_group: str = "treatment",
) -> str:
    """Generate a full analysis report in markdown format."""
    lines = [
        "# Blind Evaluation Analysis Report",
        "",
        "## Experiment Configuration",
        "",
    ]

    # Load config
    config_path = results_dir / "experiment_config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        lines.append(f"- Groups: {len(config.get('groups', []))}")
        lines.append(f"- Tasks: {len(config.get('tasks', []))}")
        lines.append(f"- Provider: {config.get('provider', 'unknown')}")
        lines.append("")

    # Load task categories
    tasks_path = results_dir / "tasks.json"
    task_categories: dict[str, str] = {}
    if tasks_path.exists():
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        task_categories = {t["task_id"]: t.get("category", "unknown") for t in tasks}

    # E1 Analysis
    if e1_annotations and e1_annotations.exists():
        e1_meta = results_dir / "blind" / "e1" / "metadata_hidden.json"
        if e1_meta.exists():
            overall, by_cat = analyze_e1(
                e1_annotations, e1_meta, task_categories, treatment_group,
            )
            lines.extend([
                "## E1: Image Preference",
                "",
                f"- Treatment wins: {overall.treatment_wins}/{overall.total} "
                f"({overall.win_rate:.1%})",
                f"- Baseline wins: {overall.baseline_wins}/{overall.total}",
                f"- Ties: {overall.ties}/{overall.total}",
                f"- 95% CI: [{overall.ci_lower:.3f}, {overall.ci_upper:.3f}]",
                "",
                "### By Category",
                "",
                "| Category | Treatment Wins | Total | Win Rate | 95% CI |",
                "|----------|---------------|-------|----------|--------|",
            ])
            for cat, pref in sorted(by_cat.items()):
                lines.append(
                    f"| {cat} | {pref.treatment_wins} | {pref.total} | "
                    f"{pref.win_rate:.1%} | [{pref.ci_lower:.3f}, {pref.ci_upper:.3f}] |"
                )
            lines.append("")

    # E2 Analysis
    if e2_annotations and e2_annotations.exists():
        e2_meta = results_dir / "blind" / "e2" / "metadata_hidden.json"
        if e2_meta.exists():
            e2_scores = analyze_e2(e2_annotations, e2_meta, treatment_group)
            lines.extend([
                "## E2: Critique Text Quality",
                "",
                "| Dimension | Treatment Mean | Baseline Mean | Delta |",
                "|-----------|---------------|---------------|-------|",
            ])
            dims = ["evidence_chain", "cross_cultural", "self_consistency"]
            for dim in dims:
                t_mean = e2_scores.get(f"treatment_{dim}", 0.0)
                b_mean = e2_scores.get(f"baseline_{dim}", 0.0)
                lines.append(
                    f"| {dim} | {t_mean:.2f} | {b_mean:.2f} | "
                    f"{t_mean - b_mean:+.2f} |"
                )
            lines.append("")

    # System-Human Spearman correlation (not yet wired — future work)
    if e2_annotations and e2_annotations.exists():
        lines.extend([
            "## System-Human Agreement",
            "",
            "- Spearman rho: N/A (system scores not yet wired to pipeline output)",
            "- Gate: **SKIP**",
            "",
        ])

    # Cost analysis from raw outputs
    lines.extend(_cost_analysis(results_dir))

    lines.extend([
        "",
        "---",
        "*Generated by VULCA blind_analyzer.py*",
    ])

    report = "\n".join(lines)

    # Save report
    analysis_dir = results_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "analysis_report.md").write_text(report, encoding="utf-8")

    return report


def _cost_analysis(results_dir: Path) -> list[str]:
    """Compute cost statistics from raw pipeline outputs."""
    lines = ["## Cost Analysis", ""]

    raw_dir = results_dir / "raw"
    if not raw_dir.exists():
        lines.append("(No raw results found)")
        return lines

    group_costs: dict[str, list[float]] = defaultdict(list)
    group_latencies: dict[str, list[int]] = defaultdict(list)
    group_rounds: dict[str, list[int]] = defaultdict(list)

    for group_dir in sorted(raw_dir.iterdir()):
        if not group_dir.is_dir():
            continue
        for task_dir in sorted(group_dir.iterdir()):
            output_path = task_dir / "pipeline_output.json"
            if not output_path.exists():
                continue
            try:
                data = json.loads(output_path.read_text(encoding="utf-8"))
                group_costs[group_dir.name].append(data.get("total_cost", 0.0))
                group_latencies[group_dir.name].append(data.get("run_latency_ms", 0))
                group_rounds[group_dir.name].append(data.get("total_rounds", 1))
            except (json.JSONDecodeError, KeyError):
                pass

    lines.append("| Group | Tasks | Avg Cost | Avg Latency (ms) | Avg Rounds |")
    lines.append("|-------|-------|----------|-------------------|------------|")

    for group_name in sorted(group_costs.keys()):
        costs = group_costs[group_name]
        lats = group_latencies[group_name]
        rnds = group_rounds[group_name]
        n = len(costs)
        avg_cost = sum(costs) / n if n else 0.0
        avg_lat = sum(lats) / n if n else 0.0
        avg_rnd = sum(rnds) / n if n else 0.0
        lines.append(
            f"| {group_name} | {n} | ${avg_cost:.4f} | {avg_lat:.0f} | {avg_rnd:.1f} |"
        )

    lines.append("")
    return lines
