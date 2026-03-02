#!/usr/bin/env python3
"""CLI entry point for blind evaluation experiment.

Usage:
    # Mock mode (validate structure, $0)
    python3 app/prototype/blind_eval/run_blind_eval.py --mode mock

    # Real mode with diffusers
    python3 app/prototype/blind_eval/run_blind_eval.py --mode real --provider diffusers

    # Export blinded materials only (requires completed run)
    python3 app/prototype/blind_eval/run_blind_eval.py --export-only

    # Analyze completed annotations
    python3 app/prototype/blind_eval/run_blind_eval.py --analyze-only \
        --e1-annotations path/to/e1.csv --e2-annotations path/to/e2.csv
"""

from __future__ import annotations

import argparse
import csv
import logging
import shutil
import sys
import zipfile
from pathlib import Path

# Ensure project root is on path
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_ROOT))

from app.prototype.blind_eval.experiment_config import BlindTask, build_default_config
from app.prototype.blind_eval.task_sampler import sample_tasks
from app.prototype.blind_eval.experiment_runner import ExperimentRunner
from app.prototype.blind_eval.blind_exporter import BlindExporter
from app.prototype.blind_eval.blind_analyzer import generate_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("blind_eval")

_RESULTS_DIR = Path(__file__).resolve().parent / "results"


_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _create_annotation_package(results_dir: Path) -> Path:
    """Create a distributable zip package for raters.

    Package structure:
        vulca-blind-eval-package/
        ├── README.md
        ├── SCORING_RUBRIC.md
        ├── e1/
        │   ├── annotation.csv
        │   └── images/{task_id}/A.png, B.png
        ├── e2/
        │   ├── annotation.csv
        │   └── critiques/{task_id}/A.md, B.md
        └── example/
            └── filled_example.csv
    """
    pkg_name = "vulca-blind-eval-package"
    zip_path = results_dir / f"{pkg_name}.zip"

    e1_blind = results_dir / "blind" / "e1"
    e2_blind = results_dir / "blind" / "e2"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Templates
        for tmpl in ("README_instructions.md", "SCORING_RUBRIC.md"):
            src = _TEMPLATES_DIR / tmpl
            dst_name = "README.md" if "README" in tmpl else "SCORING_RUBRIC.md"
            if src.exists():
                zf.write(src, f"{pkg_name}/{dst_name}")

        # E1 materials
        e1_csv = e1_blind / "annotation_template.csv"
        if e1_csv.exists():
            zf.write(e1_csv, f"{pkg_name}/e1/annotation.csv")

        e1_outputs = e1_blind / "outputs"
        if e1_outputs.exists():
            for task_dir in sorted(e1_outputs.iterdir()):
                if not task_dir.is_dir():
                    continue
                for img in task_dir.iterdir():
                    if img.suffix in (".png", ".jpg", ".jpeg"):
                        zf.write(img, f"{pkg_name}/e1/images/{task_dir.name}/{img.name}")

        # E2 materials
        e2_csv = e2_blind / "annotation_template.csv"
        if e2_csv.exists():
            zf.write(e2_csv, f"{pkg_name}/e2/annotation.csv")

        e2_outputs = e2_blind / "outputs"
        if e2_outputs.exists():
            for task_dir in sorted(e2_outputs.iterdir()):
                if not task_dir.is_dir():
                    continue
                for md in task_dir.iterdir():
                    if md.suffix == ".md":
                        zf.write(md, f"{pkg_name}/e2/critiques/{task_dir.name}/{md.name}")

        # Example filled CSV
        example_rows = [
            {
                "task_id": "example-001",
                "rater_id": "rater1",
                "evidence_chain_A": "4",
                "evidence_chain_B": "3",
                "cross_cultural_A": "5",
                "cross_cultural_B": "2",
                "self_consistency_A": "4",
                "self_consistency_B": "4",
                "preference": "A",
                "notes": "A provides stronger visual grounding",
            },
        ]
        import io
        buf = io.StringIO()
        fieldnames = list(example_rows[0].keys())
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(example_rows)
        zf.writestr(f"{pkg_name}/example/filled_example.csv", buf.getvalue())

    logger.info("Package created: %s (%.1f KB)", zip_path, zip_path.stat().st_size / 1024)
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="VULCA Blind Evaluation Experiment")
    parser.add_argument(
        "--mode", choices=["mock", "real"], default="mock",
        help="Execution mode: mock ($0) or real (uses providers)",
    )
    parser.add_argument(
        "--provider", default="mock",
        help="Provider for real mode (default: mock)",
    )
    parser.add_argument(
        "--include-ablation", action="store_true",
        help="Include ablation group (3 groups instead of 2)",
    )
    parser.add_argument(
        "--export-only", action="store_true",
        help="Only export blinded materials from existing results",
    )
    parser.add_argument(
        "--analyze-only", action="store_true",
        help="Only analyze completed annotations",
    )
    parser.add_argument(
        "--e1-annotations", type=Path, default=None,
        help="Path to E1 annotation CSV",
    )
    parser.add_argument(
        "--e2-annotations", type=Path, default=None,
        help="Path to E2 annotation CSV",
    )
    parser.add_argument(
        "--package", action="store_true",
        help="Create vulca-blind-eval-package.zip for distribution to raters",
    )
    parser.add_argument(
        "--results-dir", type=Path, default=_RESULTS_DIR,
        help="Results directory",
    )
    parser.add_argument(
        "--tasks-subset", type=int, default=None,
        help="Limit tasks per category (for quick testing)",
    )
    parser.add_argument(
        "--n-seeds", type=int, default=1,
        help="Number of seeds per task for statistical replication (default: 1)",
    )

    args = parser.parse_args()

    if args.analyze_only:
        logger.info("=== Analyze Only Mode ===")
        report = generate_report(
            args.results_dir,
            e1_annotations=args.e1_annotations,
            e2_annotations=args.e2_annotations,
        )
        print(report)
        return

    if args.package:
        logger.info("=== Package Mode ===")
        _create_annotation_package(args.results_dir)
        return

    # Sample tasks — use all available when tasks_subset not specified
    n_per_cat = args.tasks_subset if args.tasks_subset else 100  # default: all
    tasks = sample_tasks(n_per_category=n_per_cat)
    logger.info("Sampled %d tasks (up to %d per category)", len(tasks), n_per_cat)

    # Replicate tasks with multiple seeds
    if args.n_seeds > 1:
        base_tasks = tasks[:]
        tasks = []
        for seed_idx in range(args.n_seeds):
            for bt in base_tasks:
                tasks.append(BlindTask(
                    task_id=f"{bt.task_id}_s{seed_idx}",
                    subject=bt.subject,
                    tradition=bt.tradition,
                    category=bt.category,
                    expected_emphasis=bt.expected_emphasis,
                ))
        logger.info("Replicated to %d tasks (%d seeds × %d base)", len(tasks), args.n_seeds, len(base_tasks))

    # Build config
    provider = args.provider if args.mode == "real" else "mock"
    config = build_default_config(
        tasks=tasks,
        provider=provider,
        include_ablation=args.include_ablation,
    )

    if args.export_only:
        logger.info("=== Export Only Mode ===")
        exporter = BlindExporter(args.results_dir, config)
        e1_dir, e2_dir = exporter.export_all()
        logger.info("E1 exported to: %s", e1_dir)
        logger.info("E2 exported to: %s", e2_dir)
        return

    # Run experiment
    logger.info("=== Running Blind Evaluation (%s mode) ===", args.mode)
    logger.info("Groups: %s", [g.name for g in config.groups])
    logger.info("Provider: %s", provider)

    runner = ExperimentRunner(config, results_dir=args.results_dir)
    all_results = runner.run_all(tasks)

    # Summary
    for group_name, results in all_results.items():
        successes = sum(1 for _, o, _ in results if o.success)
        logger.info("  %s: %d/%d success", group_name, successes, len(results))

    # Export blinded materials
    logger.info("=== Exporting Blinded Materials ===")
    exporter = BlindExporter(args.results_dir, config)
    e1_dir, e2_dir = exporter.export_all()
    logger.info("E1 exported to: %s", e1_dir)
    logger.info("E2 exported to: %s", e2_dir)

    # Generate preliminary analysis (no annotations yet)
    report = generate_report(args.results_dir)
    logger.info("Analysis report saved to: %s", args.results_dir / "analysis")

    logger.info("=== Blind Evaluation Complete ===")
    logger.info("Next steps:")
    logger.info("  1. Distribute E1/E2 materials to raters")
    logger.info("  2. Collect filled annotation CSVs")
    logger.info("  3. Run: python3 ... --analyze-only --e1-annotations ... --e2-annotations ...")


if __name__ == "__main__":
    main()
