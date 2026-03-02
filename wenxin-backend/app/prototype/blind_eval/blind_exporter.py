"""Blind exporter: anonymize and export evaluation materials.

Produces two evaluation tracks:
  E1: Image preference (A.png / B.png per task)
  E2: Critique text preference (A.md / B.md per task)

All group identifiers are stripped. Random A/B assignment is
deterministic per (task_id, seed) for reproducibility.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

from app.prototype.blind_eval.experiment_config import ExperimentConfig

# Keywords that would leak the pipeline variant
_LEAK_PATTERNS = re.compile(
    r"(CriticLLM|agent_critic|enable_agent|rule_only|baseline|treatment|ablation"
    r"|enable_evidence_loop|enable_fix_it_plan|FixItPlan|NeedMoreEvidence"
    r"|agent=|rule=|hybrid|v2\.6|merged=)",
    re.IGNORECASE,
)

# Model/provider references that reveal the pipeline variant
_MODEL_PATTERN = re.compile(
    r"\(model=[^)]+\)",
    re.IGNORECASE,
)


def _sanitize_rationale(text: str) -> str:
    """Remove keywords that could reveal the pipeline variant."""
    text = _LEAK_PATTERNS.sub("[REDACTED]", text)
    text = _MODEL_PATTERN.sub("", text)
    return text


# Matches dimension lines like: **dim_name** (score: 0.80): rationale text...
_DIMENSION_LINE = re.compile(
    r"(\*\*\w+\*\*\s*\(score:\s*[\d.]+\)):.*",
)


def _strip_dimension_rationale(text: str) -> str:
    """Strip rationale details from dimension score lines.

    Converts lines like:
        **philosophical_aesthetic** (score: 0.80): base=0.4; no_taboo=+0.2
        **philosophical_aesthetic** (score: 0.59): [REDACTED]0.800; [REDACTED]0.500
    To:
        **philosophical_aesthetic** (score: 0.80)
        **philosophical_aesthetic** (score: 0.59)

    This prevents format differences between baseline and treatment from
    leaking group identity.
    """
    return _DIMENSION_LINE.sub(r"\1", text)


def _ab_assignment(task_id: str, seed: int) -> bool:
    """Return True if baseline=A, False if baseline=B. Deterministic."""
    h = hashlib.sha256(f"{task_id}:ab:{seed}".encode()).hexdigest()
    return int(h[0], 16) % 2 == 0


class BlindExporter:
    """Export blinded evaluation materials from raw experiment results."""

    def __init__(
        self,
        results_dir: Path,
        config: ExperimentConfig,
        baseline_group: str = "baseline",
        treatment_group: str = "treatment",
    ) -> None:
        self.results_dir = results_dir
        self.config = config
        self.baseline = baseline_group
        self.treatment = treatment_group

    def export_e1(self) -> Path:
        """Export E1: image preference materials.

        For each task, copies best_candidate.png from baseline and treatment
        as A.png / B.png (randomly assigned).

        Returns path to e1/ directory.
        """
        e1_dir = self.results_dir / "blind" / "e1"
        outputs_dir = e1_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

        metadata: list[dict] = []
        annotation_rows: list[dict] = []

        for task in self.config.tasks:
            tid = task.task_id
            baseline_img = self.results_dir / "raw" / self.baseline / tid / "best_candidate.png"
            treatment_img = self.results_dir / "raw" / self.treatment / tid / "best_candidate.png"

            task_out = outputs_dir / tid
            task_out.mkdir(parents=True, exist_ok=True)

            baseline_is_a = _ab_assignment(tid, self.config.seed_base)

            if baseline_is_a:
                a_src, b_src = baseline_img, treatment_img
                a_group, b_group = self.baseline, self.treatment
            else:
                a_src, b_src = treatment_img, baseline_img
                a_group, b_group = self.treatment, self.baseline

            # Copy images (or create placeholder)
            for label, src in [("A.png", a_src), ("B.png", b_src)]:
                dst = task_out / label
                if src.exists() and src.stat().st_size > 20:
                    shutil.copy2(src, dst)
                else:
                    dst.write_bytes(b"PLACEHOLDER_IMAGE")

            metadata.append({
                "task_id": tid,
                "A_group": a_group,
                "B_group": b_group,
                "category": task.category,
                "tradition": task.tradition,
            })

            annotation_rows.append({
                "task_id": tid,
                "rater_id": "",
                "preference": "",
                "cultural_fit_A": "",
                "cultural_fit_B": "",
                "notes": "",
            })

        # Save hidden metadata
        (e1_dir / "metadata_hidden.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Save annotation template
        self._write_csv(
            e1_dir / "annotation_template.csv",
            ["task_id", "rater_id", "preference", "cultural_fit_A", "cultural_fit_B", "notes"],
            annotation_rows,
        )

        return e1_dir

    def export_e2(self) -> Path:
        """Export E2: critique text preference materials.

        For each task, extracts critique rationale from pipeline_output.json,
        sanitizes it, and saves as A.md / B.md.

        Returns path to e2/ directory.
        """
        e2_dir = self.results_dir / "blind" / "e2"
        outputs_dir = e2_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

        metadata: list[dict] = []
        annotation_rows: list[dict] = []

        for task in self.config.tasks:
            tid = task.task_id
            baseline_is_a = _ab_assignment(tid, self.config.seed_base)

            # Load critique texts
            baseline_text = self._extract_critique_text(self.baseline, tid)
            treatment_text = self._extract_critique_text(self.treatment, tid)

            task_out = outputs_dir / tid
            task_out.mkdir(parents=True, exist_ok=True)

            if baseline_is_a:
                a_text, b_text = baseline_text, treatment_text
                a_group, b_group = self.baseline, self.treatment
            else:
                a_text, b_text = treatment_text, baseline_text
                a_group, b_group = self.treatment, self.baseline

            # Write sanitized texts
            (task_out / "A.md").write_text(
                self._format_critique_md(a_text, "A"), encoding="utf-8"
            )
            (task_out / "B.md").write_text(
                self._format_critique_md(b_text, "B"), encoding="utf-8"
            )

            metadata.append({
                "task_id": tid,
                "A_group": a_group,
                "B_group": b_group,
                "category": task.category,
                "tradition": task.tradition,
            })

            annotation_rows.append({
                "task_id": tid,
                "rater_id": "",
                "evidence_chain_A": "",
                "evidence_chain_B": "",
                "cross_cultural_A": "",
                "cross_cultural_B": "",
                "self_consistency_A": "",
                "self_consistency_B": "",
                "preference": "",
                "notes": "",
            })

        # Save hidden metadata
        (e2_dir / "metadata_hidden.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Save annotation template
        self._write_csv(
            e2_dir / "annotation_template.csv",
            [
                "task_id", "rater_id",
                "evidence_chain_A", "evidence_chain_B",
                "cross_cultural_A", "cross_cultural_B",
                "self_consistency_A", "self_consistency_B",
                "preference", "notes",
            ],
            annotation_rows,
        )

        return e2_dir

    def export_all(self) -> tuple[Path, Path]:
        """Export both E1 and E2 materials."""
        return self.export_e1(), self.export_e2()

    def _extract_critique_text(self, group_name: str, task_id: str) -> str:
        """Extract critique rationale from checkpoint or pipeline output."""
        # 1. Try critique checkpoint (has full dimension scores + rationale)
        critique_text = self._try_critique_checkpoint(group_name, task_id)
        if critique_text:
            return critique_text

        # 2. Fallback: pipeline output stages
        output_path = self.results_dir / "raw" / group_name / task_id / "pipeline_output.json"
        if not output_path.exists():
            return "(No critique available)"

        try:
            data = json.loads(output_path.read_text(encoding="utf-8"))
            for stage in data.get("stages", []):
                summary = stage.get("output_summary", {})
                if "critique" in summary:
                    critique = summary["critique"]
                    if isinstance(critique, dict):
                        parts = []
                        for dim, info in critique.items():
                            if isinstance(info, dict) and "rationale" in info:
                                parts.append(f"**{dim}**: {info['rationale']}")
                            elif isinstance(info, str):
                                parts.append(f"**{dim}**: {info}")
                        if parts:
                            return "\n\n".join(parts)
                        return json.dumps(critique, indent=2, ensure_ascii=False)
                    return str(critique)
                if "rerun_hint" in summary:
                    hint = summary["rerun_hint"]
                    hint_text = ", ".join(hint) if isinstance(hint, (list, tuple)) else str(hint)
                    return f"Rerun suggestion: {hint_text}"
        except (json.JSONDecodeError, KeyError):
            pass

        return "(Critique text not found in pipeline output)"

    def _try_critique_checkpoint(self, group_name: str, task_id: str) -> str | None:
        """Try to extract detailed critique from checkpoint files."""
        ckpt_root = Path(__file__).resolve().parent.parent / "checkpoints" / "critique"
        pipeline_task_id = f"{group_name}_{task_id}"
        run_path = ckpt_root / pipeline_task_id / "run.json"

        if not run_path.exists():
            return None

        try:
            data = json.loads(run_path.read_text(encoding="utf-8"))
            scored = data.get("scored_candidates", [])
            if not scored:
                return None

            # Format the best candidate's dimension scores as readable text
            best = scored[0]
            parts = []
            parts.append(f"**Overall Score**: {best.get('weighted_total', 0):.3f}")
            parts.append(f"**Gate**: {'PASS' if best.get('gate_passed') else 'FAIL'}")

            dims = best.get("dimension_scores", [])
            for d in dims:
                dim_name = d.get("dimension", "unknown")
                score = d.get("score", 0)
                rationale = d.get("rationale", "")
                parts.append(f"**{dim_name}** (score: {score:.2f}): {rationale}")

            risk_tags = best.get("risk_tags", [])
            if risk_tags:
                parts.append(f"**Risk Tags**: {', '.join(risk_tags)}")

            rerun = data.get("rerun_hint", [])
            if rerun:
                rerun_text = ", ".join(rerun) if isinstance(rerun, (list, tuple)) else str(rerun)
                parts.append(f"**Rerun Suggestion**: {rerun_text}")

            return "\n\n".join(parts)
        except (json.JSONDecodeError, KeyError):
            return None

    def _format_critique_md(self, raw_text: str, label: str) -> str:
        """Format and sanitize critique text as markdown."""
        sanitized = _sanitize_rationale(raw_text)
        sanitized = _strip_dimension_rationale(sanitized)
        return f"# Evaluation {label}\n\n{sanitized}\n"

    @staticmethod
    def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
        """Write a CSV file."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
