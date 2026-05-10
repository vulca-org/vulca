#!/usr/bin/env python3
"""Run lightweight Vulca JEPA audit backends.

The mock backend is intentionally not a model. It creates deterministic image
statistics so the experiment data contract can be tested before wiring DINO,
I-JEPA, or SigLIP.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageStat


def mock_image_embedding(path: Path) -> list[float]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        rgb = rgba.convert("RGB")
        luma = rgba.convert("L")
        rgb_stats = ImageStat.Stat(rgb)
        luma_stats = ImageStat.Stat(luma)
        alpha = rgba.getchannel("A")
        alpha_histogram = alpha.histogram()
        total_pixels = alpha.width * alpha.height
        alpha_coverage = sum(alpha_histogram[1:]) / total_pixels

    width, height = rgba.size
    aspect = width / height if height else 0.0
    aspect_normalized = min(aspect / 2.0, 1.0)
    return [
        round(float(rgb_stats.mean[0]) / 255.0, 6),
        round(float(rgb_stats.mean[1]) / 255.0, 6),
        round(float(rgb_stats.mean[2]) / 255.0, 6),
        round(float(rgb_stats.stddev[0]) / 255.0, 6),
        round(float(rgb_stats.stddev[1]) / 255.0, 6),
        round(float(rgb_stats.stddev[2]) / 255.0, 6),
        round(float(luma_stats.mean[0]) / 255.0, 6),
        round(float(luma_stats.stddev[0]) / 255.0, 6),
        round(float(alpha_coverage * aspect_normalized), 6),
    ]


def _euclidean(left: Iterable[float], right: Iterable[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def compute_pairwise_distances(embeddings: dict[str, list[float]]) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    for left, right in combinations(embeddings.keys(), 2):
        pairs.append(
            {
                "pair": [left, right],
                "distance": round(_euclidean(embeddings[left], embeddings[right]), 6),
            }
        )
    return pairs


def _rank_anomalies(
    sample_ids: list[str],
    pairwise_distances: list[dict[str, object]],
) -> list[dict[str, object]]:
    distances_by_sample: dict[str, list[tuple[str, float]]] = {sample_id: [] for sample_id in sample_ids}
    for pair in pairwise_distances:
        left, right = pair["pair"]
        distance = float(pair["distance"])
        distances_by_sample[left].append((right, distance))
        distances_by_sample[right].append((left, distance))

    ranking: list[dict[str, object]] = []
    for sample_id in sample_ids:
        distances = distances_by_sample[sample_id]
        if not distances:
            ranking.append(
                {
                    "sample_id": sample_id,
                    "mean_distance": 0.0,
                    "nearest_sample_id": None,
                    "nearest_distance": None,
                }
            )
            continue
        nearest_id, nearest_distance = min(distances, key=lambda item: item[1])
        mean_distance = sum(distance for _, distance in distances) / len(distances)
        ranking.append(
            {
                "sample_id": sample_id,
                "mean_distance": round(mean_distance, 6),
                "nearest_sample_id": nearest_id,
                "nearest_distance": round(nearest_distance, 6),
            }
        )
    return sorted(ranking, key=lambda item: (-float(item["mean_distance"]), str(item["sample_id"])))


def _select_samples(inventory: dict[str, object], audit_set: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    selected: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    for sample in inventory["samples"]:
        include = (
            sample.get("exists") is True
            and sample.get("usable_for_embedding") is True
            and sample.get("audit_set") == audit_set
        )
        if include:
            selected.append(sample)
        else:
            excluded.append(
                {
                    "sample_id": sample["sample_id"],
                    "path": sample["path"],
                    "audit_set": sample.get("audit_set"),
                    "usable_for_embedding": sample.get("usable_for_embedding", False),
                    "reject_reasons": sample.get("reject_reasons", []),
                }
            )
    return selected, excluded


def run_mock_audit(manifest: Path | str, *, audit_set: str = "core") -> dict[str, object]:
    manifest_path = Path(manifest)
    inventory = json.loads(manifest_path.read_text())
    repo_root = Path(inventory["repo_root"])
    selected, excluded = _select_samples(inventory, audit_set)

    embeddings = {
        sample["sample_id"]: mock_image_embedding(repo_root / sample["path"])
        for sample in selected
    }
    pairwise_distances = compute_pairwise_distances(embeddings)
    sample_ids = [sample["sample_id"] for sample in selected]
    return {
        "schema_version": "vulca_jepa_audit.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "backend": "mock",
        "model": "image-statistics-v1",
        "manifest": str(manifest_path),
        "audit_set": audit_set,
        "samples_total": len(selected),
        "pairwise_distances_total": len(pairwise_distances),
        "samples": [
            {
                "sample_id": sample["sample_id"],
                "group": sample["group"],
                "path": sample["path"],
                "embedding": embeddings[sample["sample_id"]],
            }
            for sample in selected
        ],
        "pairwise_distances": pairwise_distances,
        "anomaly_ranking": _rank_anomalies(sample_ids, pairwise_distances),
        "excluded_samples": excluded,
    }


def write_audit(
    manifest: Path | str,
    out: Path | str,
    *,
    backend: str = "mock",
    audit_set: str = "core",
) -> dict[str, object]:
    if backend != "mock":
        raise ValueError(f"unsupported backend for this script revision: {backend}")
    output_path = Path(out)
    audit = run_mock_audit(manifest, audit_set=audit_set)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Inventory JSON path.")
    parser.add_argument("--backend", default="mock", choices=("mock",), help="Audit backend to run.")
    parser.add_argument("--audit-set", default="core", choices=("core",), help="Inventory audit set to embed.")
    parser.add_argument("--out", required=True, type=Path, help="Audit JSON output path.")
    args = parser.parse_args(argv)

    audit = write_audit(args.manifest, args.out, backend=args.backend, audit_set=args.audit_set)
    print(f"wrote {args.out}")
    print(f"backend: {audit['backend']}")
    print(f"samples: {audit['samples_total']}")
    print(f"pairwise_distances: {audit['pairwise_distances_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
