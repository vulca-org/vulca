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

DEFAULT_DINOV2_MODEL = "facebook/dinov2-base"
DEFAULT_SIGLIP_MODEL = "google/siglip2-base-patch16-224"


class BackendUnavailable(RuntimeError):
    """Raised when an optional embedding backend cannot run in this environment."""


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


def _load_inventory_and_samples(
    manifest: Path | str,
    audit_set: str,
) -> tuple[Path, dict[str, object], Path, list[dict[str, object]], list[dict[str, object]]]:
    manifest_path = Path(manifest)
    inventory = json.loads(manifest_path.read_text())
    repo_root = Path(inventory["repo_root"])
    selected, excluded = _select_samples(inventory, audit_set)
    return manifest_path, inventory, repo_root, selected, excluded


def _build_audit_result(
    *,
    manifest_path: Path,
    backend: str,
    model: str,
    audit_set: str,
    selected: list[dict[str, object]],
    excluded: list[dict[str, object]],
    embeddings: dict[str, list[float]],
) -> dict[str, object]:
    embeddings = {
        sample_id: [round(float(value), 6) for value in embedding]
        for sample_id, embedding in embeddings.items()
    }
    pairwise_distances = compute_pairwise_distances(embeddings)
    sample_ids = [sample["sample_id"] for sample in selected]
    return {
        "schema_version": "vulca_jepa_audit.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "backend": backend,
        "status": "ok",
        "model": model,
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


def run_mock_audit(manifest: Path | str, *, audit_set: str = "core") -> dict[str, object]:
    manifest_path, _inventory, repo_root, selected, excluded = _load_inventory_and_samples(manifest, audit_set)
    embeddings = {
        sample["sample_id"]: mock_image_embedding(repo_root / sample["path"])
        for sample in selected
    }
    return _build_audit_result(
        manifest_path=manifest_path,
        backend="mock",
        model="image-statistics-v1",
        audit_set=audit_set,
        selected=selected,
        excluded=excluded,
        embeddings=embeddings,
    )


def _load_dinov2_components(model: str):
    try:
        import torch
        from transformers import AutoImageProcessor, AutoModel
    except ImportError as exc:
        raise BackendUnavailable("backend unavailable: install torch/transformers or run with --backend mock") from exc

    try:
        processor = AutoImageProcessor.from_pretrained(model)
        model_obj = AutoModel.from_pretrained(model)
        model_obj.eval()
    except Exception as exc:
        raise BackendUnavailable(f"backend unavailable: {exc}") from exc
    return torch, processor, model_obj


def _load_siglip_components(model: str):
    try:
        import torch
        from transformers import AutoModel, AutoProcessor
    except ImportError as exc:
        raise BackendUnavailable("backend unavailable: install torch/transformers or run with --backend mock") from exc

    try:
        processor = AutoProcessor.from_pretrained(model)
        model_obj = AutoModel.from_pretrained(model)
        model_obj.eval()
    except Exception as exc:
        raise BackendUnavailable(f"backend unavailable: {exc}") from exc
    return torch, processor, model_obj


def dinov2_image_embedding(path: Path, *, torch_module, processor, model_obj) -> list[float]:
    with Image.open(path) as image:
        inputs = processor(images=image.convert("RGB"), return_tensors="pt")

    with torch_module.no_grad():
        outputs = model_obj(**inputs)

    pooled = getattr(outputs, "pooler_output", None)
    if pooled is None:
        pooled = outputs.last_hidden_state[:, 0]
    vector = pooled[0].detach().cpu().float()
    norm = torch_module.linalg.vector_norm(vector)
    if float(norm) > 0:
        vector = vector / norm
    return [round(float(value), 6) for value in vector.tolist()]


def _text_for_sample(sample: dict[str, object]) -> tuple[str, str]:
    prompt = str(sample.get("prompt") or "").strip()
    if prompt:
        return prompt, "prompt"
    return str(sample.get("purpose") or sample["sample_id"]), "purpose"


def siglip_text_image_score(path: Path, text: str, *, torch_module, processor, model_obj) -> dict[str, float]:
    with Image.open(path) as image:
        inputs = processor(
            text=[text],
            images=image.convert("RGB"),
            padding="max_length",
            return_tensors="pt",
        )

    with torch_module.no_grad():
        outputs = model_obj(**inputs)

    logits = getattr(outputs, "logits_per_image", None)
    if logits is None:
        raise BackendUnavailable("backend unavailable: SigLIP output did not include logits_per_image")
    logit = float(logits[0][0])
    probability = float(torch_module.sigmoid(logits)[0][0])
    return {
        "logit": round(logit, 6),
        "probability": round(probability, 6),
    }


def run_dinov2_audit(
    manifest: Path | str,
    *,
    audit_set: str = "core",
    model: str = DEFAULT_DINOV2_MODEL,
) -> dict[str, object]:
    manifest_path, _inventory, repo_root, selected, excluded = _load_inventory_and_samples(manifest, audit_set)
    torch_module, processor, model_obj = _load_dinov2_components(model)
    embeddings = {
        sample["sample_id"]: dinov2_image_embedding(
            repo_root / sample["path"],
            torch_module=torch_module,
            processor=processor,
            model_obj=model_obj,
        )
        for sample in selected
    }
    return _build_audit_result(
        manifest_path=manifest_path,
        backend="dinov2",
        model=model,
        audit_set=audit_set,
        selected=selected,
        excluded=excluded,
        embeddings=embeddings,
    )


def run_siglip_audit(
    manifest: Path | str,
    *,
    audit_set: str = "core",
    model: str = DEFAULT_SIGLIP_MODEL,
) -> dict[str, object]:
    manifest_path, _inventory, repo_root, selected, excluded = _load_inventory_and_samples(manifest, audit_set)
    torch_module, processor, model_obj = _load_siglip_components(model)

    scored_samples: list[dict[str, object]] = []
    for sample in selected:
        text, text_source = _text_for_sample(sample)
        score = siglip_text_image_score(
            repo_root / sample["path"],
            text,
            torch_module=torch_module,
            processor=processor,
            model_obj=model_obj,
        )
        scored_samples.append(
            {
                "sample_id": sample["sample_id"],
                "group": sample["group"],
                "path": sample["path"],
                "text": text,
                "text_source": text_source,
                **score,
            }
        )

    return {
        "schema_version": "vulca_jepa_text_image_audit.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "backend": "siglip",
        "status": "ok",
        "model": model,
        "manifest": str(manifest_path),
        "audit_set": audit_set,
        "samples_total": len(scored_samples),
        "text_image_scores_total": len(scored_samples),
        "samples": scored_samples,
        "text_image_scores": sorted(scored_samples, key=lambda item: float(item["probability"])),
        "excluded_samples": excluded,
    }


def _unavailable_result(
    manifest: Path | str,
    *,
    backend: str,
    model: str,
    audit_set: str,
    error: str,
) -> dict[str, object]:
    return {
        "schema_version": "vulca_jepa_audit.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "backend": backend,
        "status": "unavailable",
        "model": model,
        "manifest": str(Path(manifest)),
        "audit_set": audit_set,
        "error": error,
        "samples_total": 0,
        "pairwise_distances_total": 0,
        "text_image_scores_total": 0,
        "samples": [],
        "pairwise_distances": [],
        "text_image_scores": [],
        "anomaly_ranking": [],
        "excluded_samples": [],
    }


def write_audit(
    manifest: Path | str,
    out: Path | str,
    *,
    backend: str = "mock",
    audit_set: str = "core",
    model: str | None = None,
) -> dict[str, object]:
    if backend == "mock":
        audit = run_mock_audit(manifest, audit_set=audit_set)
    elif backend == "dinov2":
        model_name = model or DEFAULT_DINOV2_MODEL
        try:
            audit = run_dinov2_audit(manifest, audit_set=audit_set, model=model_name)
        except BackendUnavailable as exc:
            audit = _unavailable_result(
                manifest,
                backend=backend,
                model=model_name,
                audit_set=audit_set,
                error=str(exc),
            )
    elif backend == "siglip":
        model_name = model or DEFAULT_SIGLIP_MODEL
        try:
            audit = run_siglip_audit(manifest, audit_set=audit_set, model=model_name)
        except BackendUnavailable as exc:
            audit = _unavailable_result(
                manifest,
                backend=backend,
                model=model_name,
                audit_set=audit_set,
                error=str(exc),
            )
    else:
        raise ValueError(f"unsupported backend for this script revision: {backend}")
    output_path = Path(out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Inventory JSON path.")
    parser.add_argument("--backend", default="mock", choices=("mock", "dinov2", "siglip"), help="Audit backend to run.")
    parser.add_argument("--model", default=None, help="Backend model id, e.g. facebook/dinov2-base.")
    parser.add_argument("--audit-set", default="core", choices=("core",), help="Inventory audit set to embed.")
    parser.add_argument("--out", required=True, type=Path, help="Audit JSON output path.")
    args = parser.parse_args(argv)

    audit = write_audit(args.manifest, args.out, backend=args.backend, audit_set=args.audit_set, model=args.model)
    print(f"wrote {args.out}")
    print(f"backend: {audit['backend']}")
    if audit.get("status") == "unavailable":
        print(audit["error"])
        return 0
    if audit.get("model"):
        print(f"model: {audit['model']}")
    print(f"samples: {audit['samples_total']}")
    if "text_image_scores_total" in audit and audit.get("backend") == "siglip":
        print(f"text_image_scores: {audit['text_image_scores_total']}")
    else:
        print(f"pairwise_distances: {audit['pairwise_distances_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
