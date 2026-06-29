from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


REQUIRED_METADATA_FIELDS = {
    "id",
    "title",
    "canonical_url",
    "source_type",
    "year",
    "author_or_studio",
    "currentness",
    "summary",
    "why_relevant",
    "review_status",
    "quality_scores",
    "visual_families",
    "modules",
    "captures",
}
ALLOWED_SOURCE_TYPES = {"demo", "github", "tutorial", "case_study", "product_ref", "documentation"}
ALLOWED_CURRENTNESS = {"2025_plus", "still_current", "historical_reference"}
ALLOWED_REVIEW_STATUSES = {"candidate", "shortlist", "needs_deeper_review", "metadata_only", "rejected"}
ALLOWED_MODULE_TYPES = {
    "meshline",
    "typography_3d",
    "scan_depth",
    "data_tunnel",
    "wire_grid",
    "particle_vector",
    "ui_sculpture",
    "shader_material",
    "interaction_state",
    "asset_pipeline",
    "performance_runtime",
    "vulca_translation",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_MODULE_REVIEW_STATUS = {"complete", "partial", "missing", "not_applicable"}
ALLOWED_CAPTURE_TYPES = {"screenshot", "video", "trace", "code_note", "asset_manifest", "external_doc"}
ALLOWED_CAPTURE_METHODS = {"playwright", "manual_browser", "downloaded_metadata", "source_read", "user_supplied"}
ALLOWED_RIGHTS_STATUS = {"local_capture", "source_link_only", "open_asset", "unclear"}
LOCAL_CAPTURE_TYPES = {"screenshot", "video", "trace", "code_note", "asset_manifest"}
QUALITY_SCORE_FIELDS = {
    "aesthetic_relevance",
    "technical_learnability",
    "multimodal_completeness",
    "interaction_clarity",
    "vulca_transfer_value",
    "license_safety",
}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(token|secret|api[_-]?key)\s*[:=]\s*[A-Za-z0-9_./+=-]{12,}"),
]


@dataclass(frozen=True)
class CaseRecord:
    id: str
    case_dir: Path
    metadata: dict[str, Any]
    anatomy: str
    lesson: str
    vulca_translation: str
    coverage: dict[str, str]
    quality_score_total: int


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _redact(value: Any) -> Any:
    if isinstance(value, str):
        text = value
        for pattern in SECRET_PATTERNS:
            text = pattern.sub("[redacted]", text)
        return text
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact(item) for key, item in value.items()}
    return value


def _require_keys(payload: dict[str, Any], keys: set[str], label: str) -> None:
    missing = keys - set(payload)
    if missing:
        raise ValueError(f"missing required {label} fields: {sorted(missing)}")


def _validate_quality_scores(scores: dict[str, Any]) -> int:
    _require_keys(scores, QUALITY_SCORE_FIELDS, "quality score")
    total = 0
    for key in QUALITY_SCORE_FIELDS:
        value = scores[key]
        if not isinstance(value, int) or value < 0 or value > 3:
            raise ValueError(f"quality score {key} must be an integer from 0 to 3")
        total += value
    return total


def _validate_modules(modules: list[dict[str, Any]]) -> None:
    for module in modules:
        module_type = module.get("module_type")
        if module_type not in ALLOWED_MODULE_TYPES:
            raise ValueError(f"unknown module_type: {module_type}")
        if module.get("confidence") not in ALLOWED_CONFIDENCE:
            raise ValueError(f"invalid module confidence for {module_type}")
        if module.get("review_status") not in ALLOWED_MODULE_REVIEW_STATUS:
            raise ValueError(f"invalid module review_status for {module_type}")
        if not isinstance(module.get("payload"), dict):
            raise ValueError(f"module payload must be an object for {module_type}")
        if not isinstance(module["payload"].get("learning_primitive"), str):
            raise ValueError(f"module payload missing learning_primitive for {module_type}")


def _validate_captures(captures: list[dict[str, Any]], case_dir: Path) -> None:
    required = {
        "id",
        "evidence_type",
        "path_or_url",
        "capture_method",
        "viewport",
        "interaction",
        "captured_at",
        "source_url",
        "confidence",
        "rights_status",
        "notes",
    }
    for capture in captures:
        _require_keys(capture, required, "capture")
        if capture["evidence_type"] not in ALLOWED_CAPTURE_TYPES:
            raise ValueError(f"invalid evidence_type: {capture['evidence_type']}")
        if capture["capture_method"] not in ALLOWED_CAPTURE_METHODS:
            raise ValueError(f"invalid capture_method: {capture['capture_method']}")
        if capture["confidence"] not in ALLOWED_CONFIDENCE:
            raise ValueError(f"invalid capture confidence: {capture['confidence']}")
        if capture["rights_status"] not in ALLOWED_RIGHTS_STATUS:
            raise ValueError(f"invalid rights_status: {capture['rights_status']}")
        if capture["rights_status"] == "local_capture" and capture["evidence_type"] in LOCAL_CAPTURE_TYPES:
            local_path = case_dir / str(capture["path_or_url"])
            if not local_path.exists():
                raise FileNotFoundError(str(capture["path_or_url"]))


def _capture_coverage(captures: list[dict[str, Any]], evidence_type: str, *, missing: str = "missing") -> str:
    matching = [capture for capture in captures if capture.get("evidence_type") == evidence_type]
    if not matching:
        return missing
    if any(capture.get("interaction") == "capture_failed" for capture in matching):
        return "partial"
    if any(capture.get("rights_status") == "local_capture" for capture in matching):
        return "complete"
    return "partial"


def coverage_for_case(record: CaseRecord) -> dict[str, str]:
    captures = record.metadata.get("captures", [])
    modules = record.metadata.get("modules", [])
    module_types = {module.get("module_type") for module in modules}
    license_score = record.metadata["quality_scores"]["license_safety"]
    return {
        "metadata": "complete",
        "screenshots": _capture_coverage(captures, "screenshot"),
        "video": _capture_coverage(captures, "video"),
        "trace": _capture_coverage(captures, "trace", missing="not_applicable"),
        "code_anatomy": "complete" if record.anatomy.strip() else "missing",
        "asset_manifest": "complete" if "asset_pipeline" in module_types else "missing",
        "license_review": "clear" if license_score >= 2 else "unclear",
        "lesson": "complete" if record.lesson.strip() else "missing",
        "vulca_translation": "complete" if record.vulca_translation.strip() else "missing",
    }


def validate_case_folder(case_dir: Path) -> CaseRecord:
    metadata_path = case_dir / "metadata.json"
    if not metadata_path.exists():
        raise ValueError(f"metadata.json missing for {case_dir}")
    metadata = _read_json(metadata_path)
    _require_keys(metadata, REQUIRED_METADATA_FIELDS, "metadata")
    if metadata["source_type"] not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"invalid source_type: {metadata['source_type']}")
    if metadata["currentness"] not in ALLOWED_CURRENTNESS:
        raise ValueError(f"invalid currentness: {metadata['currentness']}")
    if metadata["review_status"] not in ALLOWED_REVIEW_STATUSES:
        raise ValueError(f"invalid review_status: {metadata['review_status']}")
    if not str(metadata["canonical_url"]).startswith("https://"):
        raise ValueError("canonical_url must start with https://")
    total = _validate_quality_scores(metadata["quality_scores"])
    _validate_modules(metadata["modules"])
    _validate_captures(metadata["captures"], case_dir)

    anatomy = (case_dir / "anatomy.md").read_text(encoding="utf-8") if (case_dir / "anatomy.md").exists() else ""
    lesson = (case_dir / "lesson.md").read_text(encoding="utf-8") if (case_dir / "lesson.md").exists() else ""
    translation_path = case_dir / "vulca_translation.md"
    vulca_translation = translation_path.read_text(encoding="utf-8") if translation_path.exists() else ""
    draft = CaseRecord(
        id=str(metadata["id"]),
        case_dir=case_dir,
        metadata=metadata,
        anatomy=anatomy,
        lesson=lesson,
        vulca_translation=vulca_translation,
        coverage={},
        quality_score_total=total,
    )
    return CaseRecord(
        id=draft.id,
        case_dir=draft.case_dir,
        metadata=draft.metadata,
        anatomy=draft.anatomy,
        lesson=draft.lesson,
        vulca_translation=draft.vulca_translation,
        coverage=coverage_for_case(draft),
        quality_score_total=draft.quality_score_total,
    )


def case_to_review_dict(record: CaseRecord) -> dict[str, Any]:
    return _redact(
        {
            "id": record.id,
            "title": record.metadata["title"],
            "canonical_url": record.metadata["canonical_url"],
            "source_type": record.metadata["source_type"],
            "year": record.metadata["year"],
            "author_or_studio": record.metadata["author_or_studio"],
            "currentness": record.metadata["currentness"],
            "summary": record.metadata["summary"],
            "why_relevant": record.metadata["why_relevant"],
            "review_status": record.metadata["review_status"],
            "visual_families": record.metadata["visual_families"],
            "quality_scores": record.metadata["quality_scores"],
            "quality_score_total": record.quality_score_total,
            "coverage": record.coverage,
            "modules": record.metadata["modules"],
            "captures": record.metadata["captures"],
            "anatomy_excerpt": record.anatomy[:1200],
            "lesson_excerpt": record.lesson[:1200],
            "vulca_translation_excerpt": record.vulca_translation[:1200],
            "case_rel": record.case_dir.as_posix(),
        }
    )
