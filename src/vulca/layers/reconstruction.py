"""Source-conditioned layered generation helpers."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image

from vulca.layers.composite import composite_layers
from vulca.layers.manifest import write_manifest
from vulca.layers.types import LayerInfo, LayerResult


LayerPolicy = Literal["reconstruct", "preserve", "local_redraw", "residual"]


@dataclass(frozen=True)
class LayerPromptContract:
    semantic_path: str
    display_name: str
    z_index: int
    visual_role: str
    mvp_policy: LayerPolicy
    allowed_policies: tuple[str, ...]
    edit_risk: str
    parent_layer: str | None
    mask_prompt: str
    prompt_lines: tuple[str, ...]
    forbidden_content: tuple[str, ...]


@dataclass(frozen=True)
class ReconstructionContracts:
    schema_version: str
    product: dict
    provider: dict
    artifact_policy: dict
    common_edit_prefix_lines: tuple[str, ...]
    negative_prompt_block_lines: tuple[str, ...]
    layers: tuple[LayerPromptContract, ...]
    summary_json_required_keys: tuple[str, ...]


@dataclass(frozen=True)
class SourceLayeredGenerationResult:
    artifact_dir: Path
    manifest_path: Path
    composite_path: Path
    summary_path: Path


def load_reconstruction_contracts(path: str | Path) -> ReconstructionContracts:
    contract_path = Path(path)
    data = json.loads(contract_path.read_text())
    layers = tuple(
        LayerPromptContract(
            semantic_path=item["semantic_path"],
            display_name=item["display_name"],
            z_index=int(item["z_index"]),
            visual_role=item["visual_role"],
            mvp_policy=item["mvp_policy"],
            allowed_policies=tuple(item.get("allowed_policies", ())),
            edit_risk=item.get("edit_risk", "medium"),
            parent_layer=item.get("parent_layer"),
            mask_prompt=item.get("mask_prompt", ""),
            prompt_lines=tuple(item.get("prompt_lines", ())),
            forbidden_content=tuple(item.get("forbidden_content", ())),
        )
        for item in data.get("layers", ())
    )
    paths = {layer.semantic_path for layer in layers}
    if "residual.source_texture" not in paths:
        raise ValueError("contract must include residual.source_texture")
    return ReconstructionContracts(
        schema_version=data["schema_version"],
        product=data["product_contract"],
        provider=data["provider_contract"],
        artifact_policy=data["artifact_policy"],
        common_edit_prefix_lines=tuple(data.get("common_edit_prefix_lines", ())),
        negative_prompt_block_lines=tuple(data.get("negative_prompt_block_lines", ())),
        layers=layers,
        summary_json_required_keys=tuple(data.get("summary_json_required_keys", ())),
    )


def _mask_bool(mask: Image.Image, size: tuple[int, int]) -> np.ndarray:
    if mask.size != size:
        mask = mask.resize(size, Image.Resampling.NEAREST)
    return np.asarray(mask.convert("L")) > 0


def normalize_layer_ownership(
    *,
    size: tuple[int, int],
    layers: tuple[LayerPromptContract, ...],
    source_masks: dict[str, Image.Image],
) -> dict[str, Image.Image]:
    width, height = size
    shape = (height, width)
    residual_path = "residual.source_texture"
    claimed = np.zeros(shape, dtype=bool)
    owned: dict[str, np.ndarray] = {}

    for layer in sorted(layers, key=lambda item: item.z_index, reverse=True):
        if layer.semantic_path == residual_path:
            continue
        raw_mask = source_masks.get(layer.semantic_path)
        if raw_mask is None:
            layer_mask = np.zeros(shape, dtype=bool)
        else:
            layer_mask = _mask_bool(raw_mask, size)
        layer_owned = layer_mask & ~claimed
        owned[layer.semantic_path] = layer_owned
        claimed |= layer_owned

    owned[residual_path] = ~claimed
    return {
        semantic_path: Image.fromarray(mask.astype(np.uint8) * 255).convert("L")
        for semantic_path, mask in owned.items()
    }


def apply_owned_mask_to_source(
    source_rgb: Image.Image,
    owned_mask: Image.Image,
    output_path: str | Path,
) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba = source_rgb.convert("RGBA")
    mask = owned_mask.convert("L")
    if mask.size != rgba.size:
        mask = mask.resize(rgba.size, Image.Resampling.NEAREST)
    r, g, b, _ = rgba.split()
    Image.merge("RGBA", (r, g, b, mask)).save(out_path)
    return out_path


def assert_image_edits_endpoint_allowed() -> None:
    mode = os.environ.get("VULCA_OPENAI_IMAGE_ENDPOINT", "").strip().lower()
    normalized = mode.replace("-", "_")
    if normalized == "chat_completions":
        raise ValueError(
            "Source-conditioned layered generation must use OpenAI-compatible "
            "/v1/images/edits; /v1/chat/completions is forbidden for this workflow."
        )


def should_use_local_redraw(semantic_path: str, policy: str) -> bool:
    return policy == "local_redraw" and semantic_path in {
        "detail.white_flower_cluster",
        "detail.yellow_dandelion_heads",
    }


def write_reconstruction_summary(
    artifact_dir: str | Path,
    *,
    source_image: str,
    provider: str,
    model: str,
    layer_policies: dict,
    usage: dict,
    cost: dict,
    failures: list,
    quality_gates: dict,
) -> Path:
    out_dir = Path(artifact_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2026-05-05.source_layered_generation.summary.v1",
        "source_image": source_image,
        "artifact_dir": str(out_dir),
        "provider": provider,
        "model": model,
        "layer_policies": layer_policies,
        "ownership": {
            "exclusive": bool(quality_gates.get("ownership_no_overlap", False)),
            "residual_visible": True,
        },
        "usage": usage,
        "cost": cost,
        "failures": failures,
        "quality_gates": quality_gates,
    }
    path = out_dir / "summary.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return path


DEFAULT_PROMPT_CONTRACT = Path(
    "docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json"
)


def _load_source_masks(mask_dir: str | Path) -> dict[str, Image.Image]:
    return {
        path.stem: Image.open(path).convert("L")
        for path in Path(mask_dir).glob("*.png")
    }


def _area_pct(mask: np.ndarray, total_pixels: int) -> float:
    if total_pixels == 0:
        return 0.0
    return round(float(mask.sum()) * 100.0 / float(total_pixels), 4)


def build_layer_policy_records(
    *,
    layers: tuple[LayerPromptContract, ...],
    source_masks: dict[str, Image.Image],
    owned_masks: dict[str, Image.Image],
    size: tuple[int, int],
    dry_run: bool,
) -> dict:
    width, height = size
    total_pixels = width * height
    raw = {
        path: _mask_bool(mask, size)
        for path, mask in source_masks.items()
    }
    owned = {
        path: _mask_bool(mask, size)
        for path, mask in owned_masks.items()
    }
    records = {}

    for layer in layers:
        policy = layer.mvp_policy
        skipped_provider = dry_run and policy in {"reconstruct", "local_redraw"}
        raw_mask = raw.get(layer.semantic_path, np.zeros((height, width), dtype=bool))
        owned_mask = owned.get(
            layer.semantic_path,
            np.zeros((height, width), dtype=bool),
        )
        records[layer.semantic_path] = {
            "policy": policy,
            "status": "skipped_provider" if skipped_provider else "completed",
            "mask_area_pct": _area_pct(raw_mask, total_pixels),
            "owned_area_pct": _area_pct(owned_mask, total_pixels),
            "subtracted_by": [],
            "subtracted_pixel_count": 0,
        }

    for child in layers:
        if not child.parent_layer or child.parent_layer not in records:
            continue
        parent_raw = raw.get(child.parent_layer)
        child_owned = owned.get(child.semantic_path)
        if parent_raw is None or child_owned is None:
            continue
        subtracted_count = int(np.logical_and(parent_raw, child_owned).sum())
        if subtracted_count <= 0:
            continue
        parent_record = records[child.parent_layer]
        parent_record["subtracted_by"].append(child.semantic_path)
        parent_record["subtracted_pixel_count"] += subtracted_count

    return records


def evaluate_ownership_quality_gates(
    *,
    size: tuple[int, int],
    layers: tuple[LayerPromptContract, ...],
    owned_masks: dict[str, Image.Image],
) -> dict[str, bool]:
    width, height = size
    shape = (height, width)
    counts = np.zeros(shape, dtype=np.uint16)
    owned = {}
    for layer in layers:
        mask = owned_masks.get(layer.semantic_path)
        if mask is None:
            arr = np.zeros(shape, dtype=bool)
        else:
            arr = _mask_bool(mask, size)
        owned[layer.semantic_path] = arr
        counts += arr.astype(np.uint16)

    residual = owned.get("residual.source_texture", np.zeros(shape, dtype=bool))
    hedge = owned.get("foreground.hedge_bush", np.zeros(shape, dtype=bool))
    white = owned.get("detail.white_flower_cluster", np.zeros(shape, dtype=bool))
    yellow = owned.get("detail.yellow_dandelion_heads", np.zeros(shape, dtype=bool))
    union = counts > 0
    return {
        "ownership_no_overlap": bool((counts <= 1).all()),
        "residual_fills_unassigned": bool(union.all() and residual.any()),
        "flower_pixels_absent_from_parent_hedge": bool(
            not np.logical_and(hedge, white | yellow).any()
        ),
    }


async def asource_layered_generate(
    *,
    source_image: str | Path,
    mask_dir: str | Path,
    artifact_dir: str | Path,
    prompt_contract: str | Path = DEFAULT_PROMPT_CONTRACT,
    provider: str = "openai",
    model: str = "gpt-image-2",
    dry_run: bool = False,
) -> SourceLayeredGenerationResult:
    if not dry_run:
        raise NotImplementedError(
            "Provider-backed source_layered_generate is not wired in v0.24 yet; "
            "run with dry_run=True for ownership and artifact validation."
        )

    source_path = Path(source_image)
    out_dir = Path(artifact_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source = Image.open(source_path).convert("RGB")
    contracts = load_reconstruction_contracts(prompt_contract)
    source_masks = _load_source_masks(mask_dir)
    owned = normalize_layer_ownership(
        size=source.size,
        layers=contracts.layers,
        source_masks=source_masks,
    )
    layer_policies = build_layer_policy_records(
        layers=contracts.layers,
        source_masks=source_masks,
        owned_masks=owned,
        size=source.size,
        dry_run=dry_run,
    )
    quality_gates = evaluate_ownership_quality_gates(
        size=source.size,
        layers=contracts.layers,
        owned_masks=owned,
    )

    layer_results: list[LayerResult] = []
    for contract in sorted(contracts.layers, key=lambda item: item.z_index):
        path = out_dir / f"{contract.semantic_path}.png"
        apply_owned_mask_to_source(source, owned[contract.semantic_path], path)
        info = LayerInfo(
            name=contract.semantic_path,
            description=contract.display_name,
            z_index=contract.z_index,
            content_type=contract.visual_role,
            semantic_path=contract.semantic_path,
            parent_layer_id=None,
            locked=contract.mvp_policy == "residual",
        )
        layer_results.append(LayerResult(info=info, image_path=str(path)))
        layer_policies[contract.semantic_path]["file"] = str(path)

    manifest_path = Path(
        write_manifest(
            [layer.info for layer in layer_results],
            output_dir=str(out_dir),
            width=source.size[0],
            height=source.size[1],
            source_image=str(source_path),
            split_mode="source_layered_generation",
        )
    )
    composite_path = Path(
        composite_layers(
            layer_results,
            width=source.size[0],
            height=source.size[1],
            output_path=str(out_dir / "layered_composite.png"),
        )
    )
    summary_path = write_reconstruction_summary(
        out_dir,
        source_image=str(source_path),
        provider=provider,
        model=model,
        layer_policies=layer_policies,
        usage={},
        cost={"total_cost_usd": 0.0, "known": True},
        failures=[],
        quality_gates=quality_gates,
    )
    return SourceLayeredGenerationResult(
        artifact_dir=out_dir,
        manifest_path=manifest_path,
        composite_path=composite_path,
        summary_path=summary_path,
    )


def source_layered_generate(**kwargs) -> SourceLayeredGenerationResult:
    import asyncio

    return asyncio.run(asource_layered_generate(**kwargs))
