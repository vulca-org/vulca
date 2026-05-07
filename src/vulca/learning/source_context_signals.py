"""Provider-free source-context auxiliary signals for tiny learning."""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, UnidentifiedImageError

from vulca.learning.florence_signal_runner import resolve_case_source_image_path
from vulca.learning.open_model_signal_review import (
    OPEN_MODEL_SIGNAL_LOG_KIND,
    PROJECT_PRIVACY_SCOPE,
    PROMOTION_MANIFEST_CASE_TYPE,
    REVIEWED_AUXILIARY_SIGNAL_STATUS,
)
from vulca.learning.open_model_signals import (
    SCHEMA_VERSION as SIGNAL_SCHEMA_VERSION,
    SIGNAL_RECORD_CASE_TYPE,
)
from vulca.learning.private_asset_map import load_private_asset_maps
from vulca.learning.real_user_source_artifact_coverage import _artifact_refs
from vulca.learning.tiny_dataset import build_tiny_dataset_examples
from vulca.learning.training_effectiveness import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
)


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_source_context_signal_report"
SOURCE_CONTEXT_MODEL_ID = "source_context_static_v1"
DEFAULT_OUTPUT_DIR = Path("build/source_context_signals")
DEFAULT_SIGNAL_OUTPUT_NAME = "source_context_signals.promoted.jsonl"
DEFAULT_MANIFEST_NAME = "source_context_signal_promotion_manifest.json"
DEFAULT_REPORT_NAME = "source_context_signal_report.json"
DEFAULT_SOURCE_ID = "source_context_static_v1"
TEXT_SUFFIXES: frozenset[str] = frozenset({".md", ".txt", ".json", ".jsonl"})
MAX_TEXT_FILES = 16
MAX_TEXT_BYTES_PER_FILE = 200_000


SOURCE_TAG_PATTERNS: Mapping[str, tuple[str, ...]] = {
    "source_tag:brand_design": ("brand", "logo", "sponsor", "title", "venue"),
    "source_tag:film_festival": ("film festival", "film", "festival"),
    "source_tag:gongbi": ("gongbi", "song dynasty", "song-dynasty"),
    "source_tag:layered_generation": ("layer", "layers", "z_index", "semantic_path"),
    "source_tag:poster": ("poster", "a2", "a3", "11x17"),
    "source_tag:registry_ambiguity": ("registry", "ambiguity", "unregistered"),
    "source_tag:spring_festival": ("spring festival", "festival", "spring"),
    "source_tag:tang_mural": ("tang", "mural", "court mural"),
}


def write_source_context_signal_pack(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    private_asset_map_paths: Sequence[str | Path] = (),
    output_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    report_path: str | Path | None = None,
    include_local_seeds: bool = True,
    max_examples: int | None = None,
    source_id: str = DEFAULT_SOURCE_ID,
) -> dict[str, Any]:
    """Write reviewed-promoted provider-free source context signal records."""
    if max_examples is not None and max_examples < 0:
        raise ValueError("max_examples must be >= 0")

    root = Path(repo_root)
    resolved_manifest = _resolve_repo_path(root, case_source_manifest_path)
    resolved_output = Path(output_path) if output_path else (
        root / DEFAULT_OUTPUT_DIR / DEFAULT_SIGNAL_OUTPUT_NAME
    )
    resolved_pack_manifest = Path(manifest_path) if manifest_path else (
        root / DEFAULT_OUTPUT_DIR / DEFAULT_MANIFEST_NAME
    )
    resolved_report = Path(report_path) if report_path else (
        root / DEFAULT_OUTPUT_DIR / DEFAULT_REPORT_NAME
    )
    private_asset_map = load_private_asset_maps(private_asset_map_paths)
    examples = build_tiny_dataset_examples(
        repo_root=root,
        case_source_manifest_path=resolved_manifest,
        include_local_seeds=include_local_seeds,
    )
    if max_examples is not None:
        examples = examples[:max_examples]

    records: list[dict[str, Any]] = []
    skipped = 0
    for example in examples:
        record = _build_source_context_signal_record(
            example,
            repo_root=root,
            private_asset_map=private_asset_map,
        )
        if record is None:
            skipped += 1
            continue
        records.append(record)

    _write_jsonl(resolved_output, records)
    _write_promotion_manifest(
        manifest_path=resolved_pack_manifest,
        output_path=resolved_output,
        source_id=source_id,
        record_count=len(records),
    )
    report = _build_report(
        examples=examples,
        records=records,
        skipped=skipped,
        repo_root=root,
        case_source_manifest_path=resolved_manifest,
        output_path=resolved_output,
        manifest_path=resolved_pack_manifest,
        report_path=resolved_report,
        include_local_seeds=include_local_seeds,
        private_asset_map_count=len(private_asset_map_paths),
    )
    resolved_report.parent.mkdir(parents=True, exist_ok=True)
    resolved_report.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_source_context_signal_record(
    example: Mapping[str, Any],
    *,
    repo_root: Path,
    private_asset_map: Mapping[str, str | Path],
) -> dict[str, Any] | None:
    source_case = _mapping(example.get("source_case"))
    case_record = _mapping(_mapping(example.get("input")).get("case_record"))
    source_image = _source_image_signal(
        case_record,
        repo_root=repo_root,
        private_asset_map=private_asset_map,
    )
    source_artifacts = _source_artifact_signal(
        case_record,
        repo_root=repo_root,
        private_asset_map=private_asset_map,
    )
    has_source_context = (
        bool(source_image["available"])
        or int(source_artifacts["available_count"] or 0) > 0
    )
    if not has_source_context:
        return None

    tags = sorted(
        set(source_image["tags"])
        | set(source_artifacts["tags"])
        | set(_case_visible_source_tags(case_record))
    )

    signal_id = _make_signal_id(example)
    return {
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "case_type": SIGNAL_RECORD_CASE_TYPE,
        "signal_id": signal_id,
        "example_id": str(example.get("example_id") or ""),
        "source_case": {
            "case_type": str(source_case.get("case_type") or ""),
            "case_id": str(source_case.get("case_id") or ""),
            "schema_version": int(source_case.get("schema_version") or 0),
        },
        "model": {
            "id": SOURCE_CONTEXT_MODEL_ID,
            "name": "Provider-free source context summarizer",
            "model_role": "source_context_static",
            "output_training_policy": "auxiliary_training_feature",
            "default_runtime_enabled": True,
        },
        "signals": {
            "status": "completed",
            "signal_source": "source_context_static",
            "label_source": "provider_free_deterministic",
            "source_context_tags": tags,
            "source_image": source_image["summary"],
            "source_artifacts": source_artifacts["summary"],
        },
        "signal_review": {
            "schema_version": SCHEMA_VERSION,
            "decision": "promote",
            "reviewer": SOURCE_CONTEXT_MODEL_ID,
            "reviewed_at": "",
            "notes": "Provider-free deterministic source context summary.",
        },
        "training_use": {
            "default_training_input": False,
            "approved_for_auxiliary_training": True,
            "review_status": "reviewed_promoted",
            "approved_signal_use": "auxiliary_training_feature",
        },
    }


def _source_image_signal(
    case_record: Mapping[str, Any],
    *,
    repo_root: Path,
    private_asset_map: Mapping[str, str | Path],
) -> dict[str, Any]:
    resolved = resolve_case_source_image_path(
        case_record,
        repo_root=repo_root,
        private_asset_map=private_asset_map,
    )
    summary: dict[str, Any] = {
        "available": resolved.path is not None,
        "ref_kind": resolved.ref_kind,
    }
    tags: list[str] = []
    if resolved.path is None:
        return {"available": False, "summary": summary, "tags": tags}

    probe = _image_probe(resolved.path)
    summary.update(probe)
    tags.append("source_image:present")
    aspect = str(probe.get("aspect") or "")
    if aspect:
        tags.append(f"source_image.aspect:{aspect}")
    size_bucket = str(probe.get("size_bucket") or "")
    if size_bucket:
        tags.append(f"source_image.size:{size_bucket}")
    return {"available": True, "summary": summary, "tags": tags}


def _source_artifact_signal(
    case_record: Mapping[str, Any],
    *,
    repo_root: Path,
    private_asset_map: Mapping[str, str | Path],
) -> dict[str, Any]:
    artifact_paths = [
        path
        for path in (
            _resolve_artifact_ref(
                str(item.get("ref") or ""),
                repo_root=repo_root,
                private_asset_map=private_asset_map,
            )
            for item in _artifact_refs(case_record)
        )
        if path is not None and path.exists()
    ]
    kind_counts: Counter[str] = Counter()
    suffix_counts: Counter[str] = Counter()
    tags: list[str] = []
    text_chunks: list[str] = []
    text_file_count = 0

    for path in artifact_paths:
        if path.is_dir():
            kind_counts["directory"] += 1
            for child in _iter_text_files(path):
                suffix_counts[child.suffix.lower()] += 1
                text_file_count += 1
                text_chunks.append(_read_text_prefix(child))
        elif path.is_file():
            kind_counts["file"] += 1
            suffix_counts[path.suffix.lower()] += 1
            if path.suffix.lower() in TEXT_SUFFIXES:
                text_file_count += 1
                text_chunks.append(_read_text_prefix(path))

    if artifact_paths:
        tags.append("source_artifact:present")
    tags.extend(_controlled_tags_from_text("\n".join(text_chunks)))
    summary = {
        "available_count": len(artifact_paths),
        "artifact_kind_counts": dict(sorted(kind_counts.items())),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "text_file_count": text_file_count,
        "text_char_bucket": _count_bucket(sum(len(chunk) for chunk in text_chunks)),
    }
    return {
        "available_count": len(artifact_paths),
        "summary": summary,
        "tags": tags,
    }


def _resolve_artifact_ref(
    ref: str,
    *,
    repo_root: Path,
    private_asset_map: Mapping[str, str | Path],
) -> Path | None:
    if not ref:
        return None
    if ref.startswith("private://"):
        mapped = private_asset_map.get(ref)
        return Path(mapped) if mapped is not None else None
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    path = Path(ref)
    if not path.is_absolute():
        path = repo_root / path
    return path


def _iter_text_files(path: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for child in sorted(path.rglob("*")):
        if len(files) >= MAX_TEXT_FILES:
            break
        if not child.is_file() or ".git" in child.parts:
            continue
        if child.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(child)
    return tuple(files)


def _read_text_prefix(path: Path) -> str:
    try:
        data = path.read_bytes()[:MAX_TEXT_BYTES_PER_FILE]
        return data.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def _case_visible_source_tags(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    visible_text: list[str] = []
    inputs = _mapping(case_record.get("inputs"))
    for key in ("tradition", "user_intent"):
        value = inputs.get(key)
        if isinstance(value, str):
            visible_text.append(value)
    style_constraints = _mapping(inputs.get("style_constraints"))
    for value in style_constraints.values():
        if isinstance(value, str):
            visible_text.append(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            visible_text.extend(str(item) for item in value)
    source_summary = _mapping(case_record.get("source_summary"))
    for key in ("origin", "physical_form"):
        value = source_summary.get(key)
        if isinstance(value, str):
            visible_text.append(value)
    return _controlled_tags_from_text("\n".join(visible_text))


def _controlled_tags_from_text(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    tags: list[str] = []
    for tag, patterns in SOURCE_TAG_PATTERNS.items():
        if _matches_tag_patterns(lowered, patterns):
            tags.append(tag)
    return tuple(tags)


def _matches_tag_patterns(text: str, patterns: Sequence[str]) -> bool:
    for pattern in patterns:
        if pattern in text:
            return True
    return False


def _image_probe(path: Path) -> dict[str, Any]:
    try:
        with Image.open(path) as image:
            width = int(image.width)
            height = int(image.height)
            return {
                "width": width,
                "height": height,
                "format": str(image.format or "").lower(),
                "aspect": _aspect_bucket(width, height),
                "size_bucket": _pixel_bucket(width * height),
            }
    except (OSError, UnidentifiedImageError):
        return {
            "width": 0,
            "height": 0,
            "format": "",
            "aspect": "",
            "size_bucket": "invalid",
        }


def _aspect_bucket(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        return "unknown"
    ratio = width / height
    if ratio > 1.15:
        return "landscape"
    if ratio < 0.87:
        return "portrait"
    return "square"


def _pixel_bucket(pixels: int) -> str:
    if pixels <= 0:
        return "unknown"
    if pixels < 250_000:
        return "small"
    if pixels < 1_500_000:
        return "medium"
    return "large"


def _count_bucket(value: int) -> str:
    if value <= 0:
        return "zero"
    if value < 500:
        return "short"
    if value < 5_000:
        return "medium"
    return "long"


def _build_report(
    *,
    examples: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    skipped: int,
    repo_root: Path,
    case_source_manifest_path: Path,
    output_path: Path,
    manifest_path: Path,
    report_path: Path,
    include_local_seeds: bool,
    private_asset_map_count: int,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "ready_for_auxiliary_signal_training" if records else "no_signals",
        "inputs": {
            "repo_root": _safe_repo_root(repo_root),
            "case_source_manifest_path": _safe_path(case_source_manifest_path),
            "include_local_seeds": bool(include_local_seeds),
            "private_asset_map_count": int(private_asset_map_count),
        },
        "artifacts": {
            "output_path": _safe_artifact_path(repo_root, output_path),
            "manifest_path": _safe_artifact_path(repo_root, manifest_path),
            "report_path": _safe_artifact_path(repo_root, report_path),
        },
        "summary": {
            "example_count": len(examples),
            "promoted_signal_count": len(records),
            "skipped_count": int(skipped),
        },
        "counts_by_source_kind": _counts_by_source_kind(records),
        "counts_by_case_type": _counts_by_case_type(records),
        "training_use": {
            "default_training_input": False,
            "requires_explicit_dataset_flag": True,
            "approved_signal_use": "auxiliary_training_feature",
        },
        "safety": {
            "copies_raw_source_text": False,
            "copies_local_paths": False,
            "copies_private_refs": False,
            "calls_model_provider": False,
            "downloads_weights": False,
        },
    }


def _counts_by_source_kind(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        signals = _mapping(record.get("signals"))
        source_image = _mapping(signals.get("source_image"))
        source_artifacts = _mapping(signals.get("source_artifacts"))
        if bool(source_image.get("available")):
            counts["source_image"] += 1
        if int(source_artifacts.get("available_count") or 0) > 0:
            counts["source_artifact"] += 1
    return dict(sorted(counts.items()))


def _counts_by_case_type(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        counts[str(_mapping(record.get("source_case")).get("case_type") or "unknown")] += 1
    return dict(sorted(counts.items()))


def _write_promotion_manifest(
    *,
    manifest_path: Path,
    output_path: Path,
    source_id: str,
    record_count: int,
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "case_type": PROMOTION_MANIFEST_CASE_TYPE,
        "sources": [
            {
                "source_id": str(source_id or DEFAULT_SOURCE_ID),
                "kind": OPEN_MODEL_SIGNAL_LOG_KIND,
                "path": _manifest_relative_path(output_path, manifest_path.parent),
                "privacy_scope": PROJECT_PRIVACY_SCOPE,
                "curation_status": REVIEWED_AUXILIARY_SIGNAL_STATUS,
                "approved_signal_use": "auxiliary_training_feature",
                "record_count": int(record_count),
                "counts_by_model": {SOURCE_CONTEXT_MODEL_ID: int(record_count)},
            }
        ],
        "record_count": int(record_count),
        "counts_by_model": {SOURCE_CONTEXT_MODEL_ID: int(record_count)},
        "training_use": {
            "default_training_input": False,
            "requires_explicit_dataset_flag": True,
            "approved_signal_use": "auxiliary_training_feature",
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _make_signal_id(example: Mapping[str, Any]) -> str:
    seed = json.dumps(
        {
            "example_id": str(example.get("example_id") or ""),
            "model_id": SOURCE_CONTEXT_MODEL_ID,
            "case_type": SIGNAL_RECORD_CASE_TYPE,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"source_context_signal_{digest}"


def _write_jsonl(path: str | Path, records: Sequence[Mapping[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")


def _resolve_repo_path(repo_root: str | Path, path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = Path(repo_root) / resolved
    return resolved


def _safe_repo_root(path: str | Path) -> str:
    return Path(path).name


def _safe_path(path: str | Path) -> str:
    value = Path(path)
    parts = value.parts
    if "docs" in parts:
        index = parts.index("docs")
        return str(Path(*parts[index:]))
    if "build" in parts:
        index = parts.index("build")
        return str(Path(*parts[index:]))
    return value.name


def _safe_artifact_path(repo_root: str | Path, path: str | Path) -> str:
    artifact_path = Path(path)
    try:
        return str(artifact_path.relative_to(Path(repo_root)))
    except ValueError:
        return artifact_path.name


def _manifest_relative_path(output_path: Path, manifest_dir: Path) -> str:
    rel = os.path.relpath(output_path, manifest_dir)
    return Path(rel).as_posix()


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
