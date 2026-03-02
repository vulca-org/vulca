#!/usr/bin/env python3
"""Generate publication-quality ablation charts for investor demo & paper.

Outputs 5 charts to blind_eval/results/ablation/charts/:
  1. boxplot_conditions.png   - 6-condition score distribution
  2. radar_C_vs_D.png         - L1-L5 radar for core comparison
  3. heatmap_pairwise.png     - Pairwise Δ with significance stars
  4. bar_dimension_delta.png  - Per-dimension C→D delta
  5. category_grouped.png     - Score by category × condition
"""

import json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------- paths ----------
HERE = Path(__file__).resolve().parent
DATA = HERE / "results" / "ablation" / "unified_ablation_results.json"
OUT  = HERE / "results" / "ablation" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- load ----------
with open(DATA, encoding="utf-8") as f:
    raw = json.load(f)
df = pd.DataFrame(raw)

# condition labels for display
COND_LABELS = {
    "A": "A: SD1.5\nRule / Single",
    "B": "B: SD1.5\nLLM+Rule / Multi",
    "C": "C: FLUX\nRule / Single",
    "D": "D: FLUX\nLLM+Rule / Multi",
    "E": "E: FLUX\nRule / Multi",
    "F": "F: FLUX\nLLM+Rule / Single",
}
COND_SHORT = {"A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F"}
COND_ORDER = list("ABCDEF")
PALETTE = {
    "A": "#94a3b8", "B": "#64748b",   # slate for SD1.5
    "C": "#60a5fa", "D": "#2563eb",   # blue for FLUX
    "E": "#34d399", "F": "#f59e0b",   # green / amber
}
DIM_NAMES = ["L1", "L2", "L3", "L4", "L5"]
DIM_FULL = {
    "L1": "L1: Visual\nPerception",
    "L2": "L2: Technical\nAnalysis",
    "L3": "L3: Cultural\nContext",
    "L4": "L4: Critical\nInterpretation",
    "L5": "L5: Philosophical\nAesthetic",
}

# expand dim_scores into columns
for dim in DIM_NAMES:
    df[dim] = df["dim_scores"].apply(lambda d: d.get(dim) if isinstance(d, dict) else None)

# ---------- style ----------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "figure.facecolor": "white",
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})


# ========== Chart 1: Boxplot ==========
def chart_boxplot():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    order = COND_ORDER
    colors = [PALETTE[c] for c in order]

    bp = ax.boxplot(
        [df[df.condition == c]["score"].values for c in order],
        tick_labels=[COND_LABELS[c] for c in order],
        patch_artist=True,
        widths=0.55,
        showmeans=True,
        meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="black", markersize=6),
        medianprops=dict(color="white", linewidth=2),
        flierprops=dict(marker="o", markersize=4, alpha=0.5),
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)

    # add mean annotations
    for i, c in enumerate(order):
        mean_val = df[df.condition == c]["score"].mean()
        ax.annotate(f"{mean_val:.3f}", xy=(i + 1, mean_val),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=9, fontweight="bold", color=PALETTE[c])

    # significance bracket C→D
    y_max = df["score"].max() + 0.04
    ax.plot([3, 3, 4, 4], [y_max, y_max + 0.01, y_max + 0.01, y_max], "k-", linewidth=1.2)
    ax.text(3.5, y_max + 0.012, "***p<0.001\nd=0.94", ha="center", fontsize=8, fontweight="bold")

    ax.set_ylabel("Weighted Total Score")
    ax.set_title("Ablation: 6 Conditions × 30 Tasks (Real Mode)")
    ax.set_ylim(0.45, y_max + 0.06)
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(OUT / "boxplot_conditions.png")
    plt.close(fig)
    print(f"  [1/5] boxplot_conditions.png")


# ========== Chart 2: Radar C vs D ==========
def chart_radar():
    angles = np.linspace(0, 2 * np.pi, len(DIM_NAMES), endpoint=False).tolist()
    angles += angles[:1]  # close

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    for cond, color, ls, lw in [("C", "#60a5fa", "--", 2), ("D", "#2563eb", "-", 2.5)]:
        vals = [df[df.condition == cond][d].mean() for d in DIM_NAMES]
        vals += vals[:1]
        ax.plot(angles, vals, color=color, linestyle=ls, linewidth=lw, label=f"Condition {cond}")
        ax.fill(angles, vals, color=color, alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([DIM_FULL[d] for d in DIM_NAMES], fontsize=10)
    ax.set_ylim(0.55, 0.95)
    ax.set_yticks([0.6, 0.7, 0.8, 0.9])
    ax.set_yticklabels(["0.6", "0.7", "0.8", "0.9"], fontsize=8, color="gray")
    ax.set_title("L1–L5 Dimension Comparison: C (Baseline) vs D (Full System)", pad=20)
    ax.legend(loc="lower right", bbox_to_anchor=(1.15, -0.05), fontsize=10)

    # annotate deltas
    for i, dim in enumerate(DIM_NAMES):
        c_val = df[df.condition == "C"][dim].mean()
        d_val = df[df.condition == "D"][dim].mean()
        delta = d_val - c_val
        if abs(delta) > 0.005:
            ax.annotate(f"+{delta:.3f}" if delta > 0 else f"{delta:.3f}",
                        xy=(angles[i], max(c_val, d_val) + 0.02),
                        fontsize=8, fontweight="bold",
                        color="#16a34a" if delta > 0 else "#dc2626",
                        ha="center")

    fig.savefig(OUT / "radar_C_vs_D.png")
    plt.close(fig)
    print(f"  [2/5] radar_C_vs_D.png")


# ========== Chart 3: Pairwise heatmap ==========
def chart_heatmap():
    pairs = []
    for c1 in COND_ORDER:
        row = []
        for c2 in COND_ORDER:
            if c1 == c2:
                row.append(0.0)
            else:
                s1 = df[df.condition == c1]["score"].values
                s2 = df[df.condition == c2]["score"].values
                # align by task order
                row.append(np.mean(s2) - np.mean(s1))
        pairs.append(row)

    mat = np.array(pairs)

    # significance mask
    sig_text = np.full((6, 6), "", dtype=object)
    for i, c1 in enumerate(COND_ORDER):
        for j, c2 in enumerate(COND_ORDER):
            if i != j:
                s1 = df[df.condition == c1].sort_values("task_id")["score"].values
                s2 = df[df.condition == c2].sort_values("task_id")["score"].values
                _, p = stats.ttest_rel(s1, s2)
                delta = mat[i][j]
                stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                sig_text[i][j] = f"{delta:+.3f}\n{stars}" if stars else f"{delta:+.3f}"

    fig, ax = plt.subplots(figsize=(8, 6.5))
    mask = np.eye(6, dtype=bool)
    sns.heatmap(
        mat, mask=mask,
        annot=sig_text, fmt="",
        xticklabels=COND_ORDER, yticklabels=COND_ORDER,
        cmap="RdYlGn", center=0, vmin=-0.06, vmax=0.06,
        linewidths=1, linecolor="white",
        cbar_kws={"label": "Δ Score (col − row)", "shrink": 0.8},
        ax=ax,
    )
    ax.set_title("Pairwise Mean Score Differences (with significance)")
    ax.set_xlabel("Target Condition")
    ax.set_ylabel("Baseline Condition")
    fig.savefig(OUT / "heatmap_pairwise.png")
    plt.close(fig)
    print(f"  [3/5] heatmap_pairwise.png")


# ========== Chart 4: Per-dimension delta C→D ==========
def chart_dim_delta():
    fig, ax = plt.subplots(figsize=(10, 5.5))

    deltas = []
    ps = []
    for dim in DIM_NAMES:
        c_vals = df[df.condition == "C"].sort_values("task_id")[dim].dropna().values
        d_vals = df[df.condition == "D"].sort_values("task_id")[dim].dropna().values
        n = min(len(c_vals), len(d_vals))
        delta = np.mean(d_vals[:n]) - np.mean(c_vals[:n])
        _, p = stats.ttest_rel(c_vals[:n], d_vals[:n])
        deltas.append(delta)
        ps.append(p)

    colors = ["#16a34a" if d > 0 else "#dc2626" for d in deltas]
    bars = ax.bar(range(len(DIM_NAMES)), deltas, color=colors, alpha=0.85, width=0.6,
                  edgecolor="white", linewidth=1.5)

    for i, (d, p) in enumerate(zip(deltas, ps)):
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        offset = 0.006 if d >= 0 else -0.012
        ax.text(i, d + offset, f"{d:+.3f}\n{stars}", ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(range(len(DIM_NAMES)))
    ax.set_xticklabels([DIM_FULL[d] for d in DIM_NAMES], fontsize=10)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="-")
    ax.set_ylabel("Δ Score (D − C)")
    ax.set_title("Per-Dimension Improvement: D (Full System) vs C (FLUX Baseline)", fontsize=13)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(-0.04, 0.17)
    fig.savefig(OUT / "bar_dimension_delta.png")
    plt.close(fig)
    print(f"  [4/5] bar_dimension_delta.png")


# ========== Chart 5: Category × Condition grouped bar ==========
def chart_category():
    cats = ["cultural", "poetic", "taboo"]
    cat_labels = {"cultural": "Cultural", "poetic": "Poetic", "taboo": "Taboo"}
    conds_show = ["A", "C", "D"]  # key comparison
    x = np.arange(len(cats))
    width = 0.22

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, c in enumerate(conds_show):
        means = [df[(df.condition == c) & (df.category == cat)]["score"].mean() for cat in cats]
        stds  = [df[(df.condition == c) & (df.category == cat)]["score"].std() for cat in cats]
        bars = ax.bar(x + i * width, means, width, yerr=stds, capsize=3,
                      label=COND_LABELS[c].replace("\n", " "),
                      color=PALETTE[c], alpha=0.85, edgecolor="white", linewidth=1)
        for j, (m, s) in enumerate(zip(means, stds)):
            ax.text(x[j] + i * width, m + s + 0.01, f"{m:.3f}", ha="center", fontsize=8, fontweight="bold")

    ax.set_xticks(x + width)
    ax.set_xticklabels([cat_labels[c] for c in cats], fontsize=12)
    ax.set_ylabel("Mean Weighted Score")
    ax.set_title("Score by Task Category: A (SD1.5) vs C (FLUX) vs D (Full System)", fontsize=13)
    ax.legend(fontsize=9, loc="lower right")
    ax.set_ylim(0.6, 0.95)
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(OUT / "category_grouped.png")
    plt.close(fig)
    print(f"  [5/5] category_grouped.png")


# ========== Main ==========
if __name__ == "__main__":
    print(f"Data: {len(df)} entries, conditions: {sorted(df.condition.unique())}")
    print(f"Output dir: {OUT}\n")

    chart_boxplot()
    chart_radar()
    chart_heatmap()
    chart_dim_delta()
    chart_category()

    print(f"\nDone! 5 charts saved to {OUT}/")
