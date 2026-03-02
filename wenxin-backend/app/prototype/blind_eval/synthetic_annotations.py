"""Generate synthetic human annotations for validation.

Produces deterministic, realistic annotations for E1 (image preference)
and E2 (critique Likert scoring) tracks. Uses only stdlib random —
no numpy/scipy dependency.
"""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


def _extract_system_scores(results_dir: Path) -> dict[str, float]:
    """Extract weighted_total from pipeline outputs as system scores.

    Returns {task_id: score} where score is in [0, 1].
    Falls back to deterministic hash-based scores when real scores
    are unavailable or all identical (e.g., mock mode).
    """
    import hashlib

    scores: dict[str, float] = {}

    for group_name in ("treatment", "baseline"):
        raw_dir = results_dir / "raw" / group_name
        if not raw_dir.exists():
            continue
        for task_dir in sorted(raw_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            output_path = task_dir / "pipeline_output.json"
            if not output_path.exists():
                continue
            try:
                data = json.loads(output_path.read_text(encoding="utf-8"))
                for stage in data.get("stages", []):
                    summary = stage.get("output_summary", {})
                    if "weighted_total" in summary:
                        scores[task_dir.name] = float(summary["weighted_total"])
                        break
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

    # If no real scores found or all scores are identical (mock mode),
    # generate deterministic per-task scores from task_id hash
    unique_vals = set(scores.values())
    if len(unique_vals) <= 1:
        raw_dir = results_dir / "raw"
        if raw_dir.exists():
            for group_dir in raw_dir.iterdir():
                if not group_dir.is_dir():
                    continue
                for task_dir in group_dir.iterdir():
                    if task_dir.is_dir() and task_dir.name not in scores:
                        scores[task_dir.name] = 0.5  # placeholder
            # Replace all with hash-based scores
            for tid in list(scores.keys()):
                h = hashlib.sha256(f"sys_score:{tid}".encode()).hexdigest()
                scores[tid] = int(h[:8], 16) / 0xFFFFFFFF  # [0, 1]

    return scores


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def generate_synthetic_e1(
    metadata_path: Path,
    output_path: Path,
    n_raters: int = 3,
    seed: int = 42,
) -> Path:
    """Generate synthetic E1 annotations (image preference).

    Each rater has a slight bias. ~10% tie rate.
    Returns path to the written CSV.
    """
    rng = random.Random(seed)

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    rater_biases = [rng.gauss(0, 0.1) for _ in range(n_raters)]

    rows: list[dict] = []
    for item in metadata:
        tid = item["task_id"]
        a_is_treatment = item.get("A_group") == "treatment"

        for rater_idx in range(n_raters):
            bias = rater_biases[rater_idx]
            # treatment slightly favoured (p=0.55 + bias)
            p_treatment = _clamp(0.55 + bias, 0.1, 0.9)

            roll = rng.random()
            if roll < 0.10:  # ~10% tie
                pref = "TIE"
            elif roll < 0.10 + (0.90 * p_treatment):
                # Prefer treatment
                pref = "A" if a_is_treatment else "B"
            else:
                pref = "B" if a_is_treatment else "A"

            # Cultural fit Likert (1-5)
            fit_a = _clamp(round(rng.gauss(3.5, 0.8)), 1, 5)
            fit_b = _clamp(round(rng.gauss(3.2, 0.8)), 1, 5)

            rows.append({
                "task_id": tid,
                "rater_id": f"rater{rater_idx + 1}",
                "preference": pref,
                "cultural_fit_A": str(int(fit_a)),
                "cultural_fit_B": str(int(fit_b)),
                "notes": "",
            })

    fieldnames = ["task_id", "rater_id", "preference", "cultural_fit_A",
                  "cultural_fit_B", "notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def generate_synthetic_e2(
    metadata_path: Path,
    output_path: Path,
    system_scores: dict[str, float] | None = None,
    n_raters: int = 3,
    seed: int = 42,
) -> Path:
    """Generate synthetic E2 annotations (critique Likert scoring).

    Likert scores are correlated with system scores (sigma=0.5, mapped
    [0,1] -> [1,5]) when system_scores are provided. Otherwise uses
    random but realistic scores.

    Returns path to the written CSV.
    """
    rng = random.Random(seed + 1)  # different seed from E1

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    rater_biases = [rng.gauss(0, 0.3) for _ in range(n_raters)]

    dims = ["evidence_chain", "cross_cultural", "self_consistency"]

    rows: list[dict] = []
    for item in metadata:
        tid = item["task_id"]
        a_is_treatment = item.get("A_group") == "treatment"

        sys_score = (system_scores or {}).get(tid, 0.6)

        for rater_idx in range(n_raters):
            bias = rater_biases[rater_idx]
            row: dict[str, str] = {
                "task_id": tid,
                "rater_id": f"rater{rater_idx + 1}",
            }

            for dim in dims:
                # Treatment score: correlated with system score
                t_base = sys_score * 4.0 + 1.0  # map [0,1] -> [1,5]
                t_score = _clamp(round(t_base + rng.gauss(0, 0.5) + bias), 1, 5)

                # Baseline score: slightly lower
                b_base = (sys_score - 0.15) * 4.0 + 1.0
                b_score = _clamp(round(b_base + rng.gauss(0, 0.5) + bias), 1, 5)

                if a_is_treatment:
                    row[f"{dim}_A"] = str(int(t_score))
                    row[f"{dim}_B"] = str(int(b_score))
                else:
                    row[f"{dim}_A"] = str(int(b_score))
                    row[f"{dim}_B"] = str(int(t_score))

            # Preference derived from scores
            a_avg = sum(int(row[f"{d}_A"]) for d in dims) / len(dims)
            b_avg = sum(int(row[f"{d}_B"]) for d in dims) / len(dims)
            diff = a_avg - b_avg
            if abs(diff) < 0.4:
                row["preference"] = "TIE"
            elif diff > 0:
                row["preference"] = "A"
            else:
                row["preference"] = "B"
            row["notes"] = ""

            rows.append(row)

    fieldnames = ["task_id", "rater_id"]
    for dim in dims:
        fieldnames.extend([f"{dim}_A", f"{dim}_B"])
    fieldnames.extend(["preference", "notes"])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path
