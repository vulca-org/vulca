"""Build local seed case logs from tracked Vulca artifacts."""
from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from vulca.layers.decompose_cases import build_decompose_case
from vulca.layers.layer_generate_cases import build_layer_generate_case
from vulca.layers.redraw_cases import build_redraw_case
from vulca.layers.types import LayerInfo


DEFAULT_SEED_MANIFEST = Path("docs/benchmarks/learning/local_seed_manifest.json")
CREATED_AT = "2026-05-05T14:45:00Z"


@dataclass(frozen=True)
class SeedWriteResult:
    output_dir: str
    paths: dict[str, str]
    counts: dict[str, int]
    index_path: str


def build_local_seed_cases(
    repo_root: str | Path,
    manifest_path: str | Path = DEFAULT_SEED_MANIFEST,
) -> dict[str, list[dict[str, Any]]]:
    root = Path(repo_root).resolve()
    manifest = _load_manifest(root, manifest_path)
    return {
        "redraw_case": _build_redraw_seeds(root, manifest),
        "decompose_case": _build_decompose_seeds(root, manifest),
        "layer_generate_case": _build_layer_generate_seeds(root, manifest),
    }


def write_local_seed_case_logs(
    *,
    repo_root: str | Path,
    output_dir: str | Path,
    manifest_path: str | Path = DEFAULT_SEED_MANIFEST,
) -> SeedWriteResult:
    bundle = build_local_seed_cases(repo_root, manifest_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    names = {
        "redraw_case": "redraw_cases.seed.jsonl",
        "decompose_case": "decompose_cases.seed.jsonl",
        "layer_generate_case": "layer_generate_cases.seed.jsonl",
    }
    paths: dict[str, str] = {}
    counts: dict[str, int] = {}
    for case_type, records in bundle.items():
        path = out_dir / names[case_type]
        _write_jsonl(path, records)
        paths[case_type] = str(path)
        counts[case_type] = len(records)

    index_path = out_dir / "seed_index.json"
    index_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_seed_index",
                "source_manifest": str(manifest_path),
                "paths": paths,
                "counts": counts,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return SeedWriteResult(
        output_dir=str(out_dir),
        paths=paths,
        counts=counts,
        index_path=str(index_path),
    )


def _load_manifest(root: Path, manifest_path: str | Path) -> dict[str, Any]:
    path = _repo_file(root, manifest_path)
    data = json.loads(path.read_text())
    if data.get("case_type") != "learning_local_seed_manifest":
        raise ValueError("local seed manifest has unexpected case_type")
    if int(data.get("schema_version", 0) or 0) != 1:
        raise ValueError("local seed manifest has unsupported schema_version")
    return data


def _build_redraw_seeds(
    root: Path,
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    redraw_manifest_path = manifest.get("redraw_seed_manifest", "")
    redraw_manifest = json.loads(_repo_file(root, redraw_manifest_path).read_text())
    records = []
    for item in redraw_manifest.get("items", []) or []:
        source_artifact = str(item["source_artifact"])
        _repo_file(root, source_artifact)
        layer = LayerInfo(
            id=str(item["id"]),
            name=str(item["id"]),
            description=str(item.get("notes", "")),
            z_index=0,
            content_type="seed",
            semantic_path=str(item["id"]).replace("_", "."),
            quality_status="seed",
            area_pct=0.0,
        )
        records.append(
            build_redraw_case(
                artwork_dir=str(Path(source_artifact).parent),
                source_image=source_artifact,
                layer_info=layer,
                instruction=str(item.get("notes", "")),
                provider="local_seed",
                model="tracked_artifact",
                route_requested="seed",
                source_layer_path=source_artifact,
                redrawn_layer_path="",
                redraw_advisory={
                    "route_chosen": "",
                    "quality_gate_passed": False,
                    "quality_failures": [str(item["failure_type"])],
                },
                created_at=CREATED_AT,
                human_accept=False,
                failure_type=str(item["failure_type"]),
                preferred_action=str(item["preferred_action"]),
                reviewer="seed_manifest",
                reviewed_at=CREATED_AT,
            )
        )
    return records


def _build_decompose_seeds(
    root: Path,
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    records = []
    for item in manifest.get("decompose_seeds", []) or []:
        source_image = str(item["source_image"])
        output_dir = str(item["output_dir"])
        manifest_path = str(item["manifest_path"])
        _repo_file(root, source_image)
        manifest_file = _repo_file(root, manifest_path)
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        records.append(
            build_decompose_case(
                source_image=source_image,
                mode=str(item.get("mode", "")),
                provider=str(item.get("provider", "")),
                model=str(item.get("model", "")),
                tradition=str(item.get("tradition", "")),
                output_dir=output_dir,
                manifest_path=manifest_path,
                manifest_data=manifest_data,
                target_layer_hints=[],
                created_at=CREATED_AT,
                human_accept=bool(item.get("human_accept", False)),
                failure_type=str(item.get("failure_type", "")),
                preferred_action=str(item.get("preferred_action", "")),
                reviewer="seed_manifest",
                reviewed_at=CREATED_AT,
                notes=str(item.get("notes", "")),
            )
        )
    return records


def _build_layer_generate_seeds(
    root: Path,
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    records = []
    for item in manifest.get("layer_generate_seeds", []) or []:
        artifact_dir = str(item["artifact_dir"])
        layer_manifest_path = str(item["layer_manifest_path"])
        composite_path = str(item.get("composite_path", ""))
        preview_path = str(item.get("preview_path", ""))
        manifest_file = _repo_file(root, layer_manifest_path)
        if composite_path:
            _repo_file(root, composite_path)
        if preview_path:
            _repo_file(root, preview_path)
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        layers = manifest_data.get("layers", []) or []
        for layer in layers:
            layer_file = str(layer.get("file", ""))
            if layer_file:
                _repo_file(root, Path(artifact_dir) / layer_file)
        layer_status = _accepted_layer_status(item)
        records.append(
            build_layer_generate_case(
                user_intent=str(item["user_intent"]),
                tradition=str(item.get("tradition", "")),
                style_constraints=_style_constraints(manifest_data),
                layer_plan=_layer_plan(layers),
                prompt_stack=_prompt_stack(layers),
                provider=str(item.get("provider", "")),
                model=str(item.get("model", "")),
                artifact_dir=artifact_dir,
                layer_manifest_path=layer_manifest_path,
                layers=_layer_outputs(artifact_dir, layers, status=layer_status),
                composite_path=composite_path,
                preview_path=preview_path,
                created_at=CREATED_AT,
                human_accept=bool(item.get("human_accept", False)),
                failure_type=str(item.get("failure_type", "")),
                preferred_action=str(item.get("preferred_action", "")),
                reviewer="seed_manifest",
                reviewed_at=CREATED_AT,
            )
        )
    return records


def _accepted_layer_status(item: Mapping[str, Any]) -> str:
    if item.get("human_accept") is True and item.get("preferred_action") == "accept":
        return "accepted"
    return "generated"


def _style_constraints(manifest_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "positive": ["tracked layered artifact", "manifest-backed layer assets"],
        "negative": [],
        "palette": [],
        "composition": [],
        "required_motifs": [
            str(layer.get("name", ""))
            for layer in manifest_data.get("layers", []) or []
            if layer.get("name")
        ],
        "prohibited_motifs": [],
    }


def _layer_plan(layers: list[Mapping[str, Any]]) -> dict[str, Any]:
    planned = []
    for layer in layers:
        semantic_path = _semantic_path(layer)
        planned.append(
            {
                "semantic_path": semantic_path,
                "display_name": str(layer.get("name", semantic_path)),
                "role": str(layer.get("content_type", "")),
                "z_index": int(layer.get("z_index", 0) or 0),
                "generation_prompt_ref": "",
                "alpha_strategy": "manifest_layer_asset",
                "required": True,
            }
        )
    return {
        "source": "tracked_manifest",
        "desired_layer_count": len(planned),
        "layers": planned,
    }


def _prompt_stack(layers: list[Mapping[str, Any]]) -> dict[str, Any]:
    refs = []
    for layer in layers:
        prompt = str(layer.get("regeneration_prompt", ""))
        refs.append(
            {
                "semantic_path": _semantic_path(layer),
                "prompt_path": "",
                "prompt_text_hash": _hash_text(prompt),
            }
        )
    return {
        "system_prompt_path": "",
        "plan_prompt_path": "",
        "layer_prompt_refs": refs,
        "negative_prompt_path": "",
        "provider_request": {"source": "tracked_manifest"},
    }


def _layer_outputs(
    artifact_dir: str,
    layers: list[Mapping[str, Any]],
    *,
    status: str,
) -> list[dict[str, Any]]:
    outputs = []
    for layer in layers:
        semantic_path = _semantic_path(layer)
        outputs.append(
            {
                "semantic_path": semantic_path,
                "asset_path": str(Path(artifact_dir) / str(layer.get("file", ""))),
                "mask_path": "",
                "alpha_path": "",
                "visible": bool(layer.get("visible", True)),
                "locked": bool(layer.get("locked", False)),
                "status": status,
            }
        )
    return outputs


def _semantic_path(layer: Mapping[str, Any]) -> str:
    return str(layer.get("semantic_path", "") or layer.get("name", "layer"))


def _hash_text(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _repo_file(root: Path, relative_path: str | Path) -> Path:
    path = Path(relative_path)
    if path.is_absolute():
        raise ValueError(f"seed artifact must be repo-relative: {relative_path}")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"seed artifact escapes repo: {relative_path}")
    if not resolved.is_file():
        raise FileNotFoundError(str(relative_path))
    subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return resolved


def _write_jsonl(path: Path, records: list[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")
