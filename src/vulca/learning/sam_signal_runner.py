"""Explicit local SAM runner for open-model signal records.

The runner is opt-in and produces reviewable mask proposal signals only. It
does not convert masks into accepted decompose or redraw labels.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol

from PIL import Image

from vulca.learning.florence_signal_runner import resolve_case_source_image_path


DEFAULT_SAM_MODEL_TYPE = "vit_b"
DEFAULT_SAM_POINTS_PER_SIDE = 16


class SamSignalBackend(Protocol):
    def run(
        self,
        image_path: str | Path,
        *,
        case_record: Mapping[str, Any],
        model_spec: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Run SAM on a local image and return raw mask signal fields."""


def build_sam_vit_signal_runner(
    *,
    repo_root: str | Path,
    backend: SamSignalBackend | None = None,
    checkpoint_path: str | Path | None = None,
    model_type: str = DEFAULT_SAM_MODEL_TYPE,
    device: str = "auto",
    points_per_side: int = DEFAULT_SAM_POINTS_PER_SIDE,
    **_: Any,
) -> Any:
    """Build a local SAM signal runner.

    The real backend never downloads weights. A checkpoint path is required
    when no test/experiment backend is injected.
    """
    root = Path(repo_root)
    resolved_backend = backend or SamVitLocalBackend(
        checkpoint_path=checkpoint_path,
        model_type=model_type,
        device=device,
        points_per_side=points_per_side,
    )

    def run(example: Mapping[str, Any], model_spec: Mapping[str, Any]) -> dict[str, Any]:
        case_record = _case_record_from_example(example)
        source = resolve_case_source_image_path(case_record, repo_root=root)
        if source.path is None:
            return {
                "status": "skipped",
                "skip_reason": "source_image_unavailable",
                "signal_source": "local_runner",
                "label_source": "assistant_labeled",
                "review_status": "needs_human_review",
                "source_image": {
                    "available": False,
                    "ref_kind": source.ref_kind,
                },
            }

        image_info = _image_info(source.path)
        backend_signals = dict(
            resolved_backend.run(
                source.path,
                case_record=case_record,
                model_spec=model_spec,
            )
        )
        normalized = _normalize_backend_signals(
            backend_signals,
            width=image_info["width"],
            height=image_info["height"],
        )
        normalized.update(
            {
                "status": "completed",
                "signal_source": "local_runner",
                "label_source": "assistant_labeled",
                "review_status": "needs_human_review",
                "source_image": {
                    "available": True,
                    "ref_kind": source.ref_kind,
                    "width": image_info["width"],
                    "height": image_info["height"],
                },
            }
        )
        return normalized

    return run


class SamVitLocalBackend:
    """Lazy SAM v1 automatic mask backend."""

    def __init__(
        self,
        *,
        checkpoint_path: str | Path | None,
        model_type: str = DEFAULT_SAM_MODEL_TYPE,
        device: str = "auto",
        points_per_side: int = DEFAULT_SAM_POINTS_PER_SIDE,
    ) -> None:
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.model_type = model_type
        self.device = device
        self.points_per_side = int(points_per_side)
        self._generator = None

    def run(
        self,
        image_path: str | Path,
        *,
        case_record: Mapping[str, Any],
        model_spec: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        generator = self._load()
        import numpy as np

        image = np.array(Image.open(image_path).convert("RGB"))
        masks = generator.generate(image)
        return {
            "masks": masks,
            "boundary_complexity": _estimate_boundary_complexity(masks),
        }

    def _load(self):
        if self._generator is not None:
            return self._generator
        if self.checkpoint_path is None:
            raise RuntimeError(
                "SAM local runner requires --sam-checkpoint when no backend is injected."
            )
        if not self.checkpoint_path.exists():
            raise RuntimeError("SAM checkpoint path does not exist")

        try:
            import torch
            from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
        except ImportError as exc:
            raise RuntimeError(
                "SAM local runner requires segment-anything and torch. "
                "Install vulca[sam] and provide --sam-checkpoint."
            ) from exc

        device = self._resolved_device(torch)
        sam = sam_model_registry[self.model_type](checkpoint=str(self.checkpoint_path))
        sam.to(device=device)
        self._generator = SamAutomaticMaskGenerator(
            sam,
            points_per_side=self.points_per_side,
        )
        return self._generator

    def _resolved_device(self, torch_module) -> str:
        if self.device != "auto":
            return self.device
        if (
            getattr(torch_module.backends, "mps", None) is not None
            and torch_module.backends.mps.is_available()
        ):
            return "mps"
        if torch_module.cuda.is_available():
            return "cuda"
        return "cpu"


def _case_record_from_example(example: Mapping[str, Any]) -> Mapping[str, Any]:
    input_block = example.get("input")
    if isinstance(input_block, Mapping):
        case_record = input_block.get("case_record")
        if isinstance(case_record, Mapping):
            return case_record
    return {}


def _image_info(path: Path) -> dict[str, int]:
    with Image.open(path) as image:
        return {"width": int(image.width), "height": int(image.height)}


def _normalize_backend_signals(
    signals: Mapping[str, Any],
    *,
    width: int,
    height: int,
) -> dict[str, Any]:
    masks = signals.get("masks") or []
    candidates = [
        _normalize_mask_candidate(mask, width=width, height=height)
        for mask in masks
        if isinstance(mask, Mapping)
    ]
    candidates = [candidate for candidate in candidates if candidate is not None]
    total_pct = round(sum(float(item["area_pct"]) for item in candidates), 4)
    return {
        "mask_count": len(candidates),
        "total_mask_area_pct": total_pct,
        "mask_coverage_candidates": candidates,
        "boundary_complexity": _normalize_boundary_complexity(
            signals.get("boundary_complexity")
        ),
    }


def _normalize_mask_candidate(
    mask: Mapping[str, Any],
    *,
    width: int,
    height: int,
) -> dict[str, Any] | None:
    area_pixels = _mask_area_pixels(mask)
    canvas_pixels = max(int(width) * int(height), 1)
    if area_pixels <= 0:
        return None
    return {
        "area_pct": round(area_pixels / canvas_pixels * 100.0, 4),
        "bbox": _bbox(mask.get("bbox")),
        "predicted_iou": _optional_float(mask.get("predicted_iou")),
        "stability_score": _optional_float(mask.get("stability_score")),
    }


def _mask_area_pixels(mask: Mapping[str, Any]) -> int:
    value = mask.get("area_pixels", mask.get("area"))
    try:
        return max(int(value or 0), 0)
    except (TypeError, ValueError):
        return 0


def _bbox(value: Any) -> list[int]:
    if isinstance(value, (list, tuple)):
        return [int(float(item)) for item in list(value)[:4]]
    return []


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def _normalize_boundary_complexity(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, float):
            normalized[str(key)] = round(float(item), 4)
        elif isinstance(item, int):
            normalized[str(key)] = int(item)
        else:
            normalized[str(key)] = item
    return normalized


def _estimate_boundary_complexity(masks: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not masks:
        return {"mean_edge_density": 0.0, "high_complexity_mask_count": 0}
    # Lightweight placeholder from SAM metadata only; pixel-boundary analysis can
    # be added later without changing the public signal schema.
    high_complexity = 0
    densities: list[float] = []
    for mask in masks:
        area = max(_mask_area_pixels(mask), 1)
        bbox = _bbox(mask.get("bbox"))
        if len(bbox) == 4:
            perimeter = max(2 * (bbox[2] + bbox[3]), 0)
            density = perimeter / area
            densities.append(density)
            if density > 1.0:
                high_complexity += 1
    mean = sum(densities) / len(densities) if densities else 0.0
    return {
        "mean_edge_density": round(mean, 4),
        "high_complexity_mask_count": high_complexity,
    }
