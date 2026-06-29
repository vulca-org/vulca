# 3D Vector Aesthetics Learning DB Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v0.1 infrastructure for a curated, multimodal, teaching-oriented 2025+ 3D vector technical aesthetics corpus with a local HTML review atlas.

**Architecture:** Case folders are the authoring source of truth; SQLite is a compiled index; review JSON is a bounded export; the HTML atlas reads only the review JSON and local evidence paths. The first version ships deterministic schema validation, 12 seed cases, coverage scoring, a static review page, and capture-record tooling without mirroring restricted source assets.

**Tech Stack:** Python 3.10+, stdlib `json`/`sqlite3`/`pathlib`/`html`, dataclasses, pytest, optional Playwright command hooks recorded as capture manifests, static HTML/CSS/vanilla JS.

## Global Constraints

- Source spec: `docs/superpowers/specs/2026-06-29-3d-vector-aesthetics-learning-db-design.md`.
- Authoring source of truth: `data/vector-aesthetics/cases/<case_id>/`.
- SQLite is generated output at `data/vector-aesthetics/references.sqlite`.
- Review JSON is generated output at `output/review/3d-vector-aesthetics-learning-db/data/references.json`.
- HTML review output is `output/review/3d-vector-aesthetics-learning-db/index.html`.
- Generated SQLite and review HTML/JSON are local build outputs and are not committed by default.
- Commit source case folders under `data/vector-aesthetics/cases/`; commit generated review artifacts only after a separate human release decision.
- Do not archive commercial source code, private assets, paid 3D models, fonts, or textures without explicit permission.
- Cases with unclear rights use `rights_status: source_link_only` and cannot be treated as direct implementation sources.
- Every generated HTML page must redact API-key-like strings before embedding JSON.
- v0.1 target: 12 seed cases, 12 cases at Level 0, at least clear capture coverage/failure status for every case, 6 cases with technical anatomy, 3 cases with rebuild exercise metadata.

---

## File Structure

Create a focused `vulca.vector_aesthetics` package and keep scripts as thin CLIs.

- Create: `src/vulca/vector_aesthetics/__init__.py`
  - Public exports for schema validation, seed writing, compilation, capture records, and review rendering.
- Create: `src/vulca/vector_aesthetics/schema.py`
  - Constants, dataclasses, JSON loading, enum checks, coverage computation, and case-folder validation.
- Create: `src/vulca/vector_aesthetics/seeds.py`
  - Literal 12-case seed list and `write_seed_cases(root: Path) -> list[Path]`.
- Create: `src/vulca/vector_aesthetics/compiler.py`
  - Compile case folders into SQLite and bounded JSON.
- Create: `src/vulca/vector_aesthetics/captures.py`
  - Add screenshot/video/trace/code-note capture records and explicit capture-failure records.
- Create: `src/vulca/vector_aesthetics/review_html.py`
  - Render the local HTML atlas from bounded review JSON.
- Create: `scripts/vector_aesthetics_seed_cases.py`
  - CLI wrapper for creating or refreshing seed case folders.
- Create: `scripts/vector_aesthetics_build_review.py`
  - CLI wrapper for validate -> compile SQLite -> export JSON -> render HTML.
- Create: `scripts/vector_aesthetics_record_capture.py`
  - CLI wrapper for local evidence records and capture failures.
- Modify: `.gitignore`
  - Ignore `data/vector-aesthetics/references.sqlite` and `output/review/3d-vector-aesthetics-learning-db/`.
- Create generated authoring folders under `data/vector-aesthetics/cases/<case_id>/`.
- Create tests:
  - `tests/test_vector_aesthetics_schema.py`
  - `tests/test_vector_aesthetics_seed_cases.py`
  - `tests/test_vector_aesthetics_compiler.py`
  - `tests/test_vector_aesthetics_review_html.py`
  - `tests/test_vector_aesthetics_captures.py`
  - `tests/test_vector_aesthetics_cli.py`

---

## Task 1: Schema And Case-Folder Validation

**Files:**
- Create: `src/vulca/vector_aesthetics/__init__.py`
- Create: `src/vulca/vector_aesthetics/schema.py`
- Create: `tests/test_vector_aesthetics_schema.py`

**Interfaces:**
- Produces: `validate_case_folder(case_dir: Path) -> CaseRecord`
- Produces: `coverage_for_case(record: CaseRecord) -> dict[str, str]`
- Produces: `case_to_review_dict(record: CaseRecord) -> dict[str, object]`
- Consumes: only stdlib JSON files and markdown file presence.

- [ ] **Step 1: Write the failing schema tests**

Create `tests/test_vector_aesthetics_schema.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest


def write_case(root: Path, *, case_id: str = "makio-meshline") -> Path:
    case_dir = root / case_id
    case_dir.mkdir(parents=True)
    (case_dir / "metadata.json").write_text(
        json.dumps(
            {
                "id": case_id,
                "title": "Makio MeshLine",
                "canonical_url": "https://meshline.makio.io/",
                "source_type": "demo",
                "year": 2025,
                "author_or_studio": "Makio64",
                "currentness": "still_current",
                "summary": "Modern Three.js wide-line rendering reference.",
                "why_relevant": "Core reference for 3D route and trail primitives.",
                "review_status": "candidate",
                "quality_scores": {
                    "aesthetic_relevance": 3,
                    "technical_learnability": 3,
                    "multimodal_completeness": 1,
                    "interaction_clarity": 2,
                    "vulca_transfer_value": 3,
                    "license_safety": 2,
                },
                "visual_families": ["meshline", "data_tunnel"],
                "modules": [
                    {
                        "module_type": "meshline",
                        "payload": {
                            "path_source": "curve_points",
                            "line_form": "thick_ribbon",
                            "material": ["gradient", "dash"],
                            "animation": ["trail_reveal"],
                            "spatial_role": "route",
                            "learning_primitive": "animated 3D route line",
                        },
                        "evidence_refs": [],
                        "confidence": "medium",
                        "review_status": "partial",
                        "review_notes": "Seeded from public project page.",
                    }
                ],
                "captures": [
                    {
                        "id": "metadata-source",
                        "evidence_type": "external_doc",
                        "path_or_url": "https://meshline.makio.io/",
                        "capture_method": "source_read",
                        "viewport": "none",
                        "interaction": "none",
                        "captured_at": "2026-06-29",
                        "source_url": "https://meshline.makio.io/",
                        "confidence": "high",
                        "rights_status": "source_link_only",
                        "notes": "Metadata seed only.",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (case_dir / "anatomy.md").write_text(
        "# Anatomy\n\nPrimitive: animated 3D route line.\n", encoding="utf-8"
    )
    (case_dir / "lesson.md").write_text(
        "# Lesson\n\nMinimal rebuild: 12 nodes connected by animated thick lines.\n",
        encoding="utf-8",
    )
    (case_dir / "vulca_translation.md").write_text(
        "# VULCA Translation\n\nMaps to source trail and route decision.\n",
        encoding="utf-8",
    )
    return case_dir


def test_validate_case_folder_accepts_complete_seed(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    record = validate_case_folder(write_case(tmp_path))

    assert record.id == "makio-meshline"
    assert record.quality_score_total == 14
    assert record.metadata["visual_families"] == ["meshline", "data_tunnel"]
    assert record.coverage["metadata"] == "complete"
    assert record.coverage["lesson"] == "complete"


def test_validate_case_folder_rejects_unknown_module(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["modules"][0]["module_type"] = "retro_plotter"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="unknown module_type"):
        validate_case_folder(case_dir)


def test_validate_case_folder_rejects_missing_core_field(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    del payload["canonical_url"]
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required metadata fields"):
        validate_case_folder(case_dir)


def test_case_to_review_dict_redacts_secret_like_values(tmp_path: Path):
    from vulca.vector_aesthetics.schema import case_to_review_dict, validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["summary"] = "accidental key sk-proj-abc123"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    review = case_to_review_dict(validate_case_folder(case_dir))

    assert "sk-proj" not in json.dumps(review)
    assert "[redacted]" in json.dumps(review)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.vector_aesthetics'`.

- [ ] **Step 3: Implement schema validation**

Create `src/vulca/vector_aesthetics/__init__.py` with:

```python
"""3D vector technical aesthetics learning corpus helpers."""

from .schema import CaseRecord, case_to_review_dict, coverage_for_case, validate_case_folder

__all__ = [
    "CaseRecord",
    "case_to_review_dict",
    "coverage_for_case",
    "validate_case_folder",
]
```

Create `src/vulca/vector_aesthetics/schema.py` with:

```python
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
QUALITY_SCORE_FIELDS = {
    "aesthetic_relevance",
    "technical_learnability",
    "multimodal_completeness",
    "interaction_clarity",
    "vulca_transfer_value",
    "license_safety",
}
SECRET_PATTERNS = [re.compile(r"sk-[A-Za-z0-9_-]+")]


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


def _validate_captures(captures: list[dict[str, Any]]) -> None:
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


def coverage_for_case(record: CaseRecord) -> dict[str, str]:
    captures = record.metadata.get("captures", [])
    evidence_types = {capture.get("evidence_type") for capture in captures}
    modules = record.metadata.get("modules", [])
    module_types = {module.get("module_type") for module in modules}
    license_score = record.metadata["quality_scores"]["license_safety"]
    return {
        "metadata": "complete",
        "screenshots": "complete" if "screenshot" in evidence_types else "missing",
        "video": "complete" if "video" in evidence_types else "missing",
        "trace": "complete" if "trace" in evidence_types else "not_applicable",
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
    _validate_captures(metadata["captures"])

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/vector_aesthetics/__init__.py src/vulca/vector_aesthetics/schema.py tests/test_vector_aesthetics_schema.py
git commit -m "feat: add vector aesthetics schema validation"
```

---

## Task 2: Seed Authoring Corpus

**Files:**
- Create: `src/vulca/vector_aesthetics/seeds.py`
- Create: `scripts/vector_aesthetics_seed_cases.py`
- Create: `tests/test_vector_aesthetics_seed_cases.py`
- Generated by script: `data/vector-aesthetics/cases/*`

**Interfaces:**
- Consumes: `validate_case_folder` from Task 1.
- Produces: `SEED_CASES: list[dict[str, object]]`
- Produces: `write_seed_cases(root: Path) -> list[Path]`

- [ ] **Step 1: Write failing seed tests**

Create `tests/test_vector_aesthetics_seed_cases.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path


def test_seed_cases_write_twelve_valid_case_folders(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder
    from vulca.vector_aesthetics.seeds import SEED_CASES, write_seed_cases

    written = write_seed_cases(tmp_path)

    assert len(SEED_CASES) == 12
    assert len(written) == 12
    assert len({path.name for path in written}) == 12
    records = [validate_case_folder(path) for path in written]
    assert {record.metadata["review_status"] for record in records} == {"candidate"}
    assert all(record.coverage["metadata"] == "complete" for record in records)


def test_seed_cases_use_source_link_only_for_unclear_assets(tmp_path: Path):
    from vulca.vector_aesthetics.seeds import write_seed_cases

    written = write_seed_cases(tmp_path)

    for case_dir in written:
        metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
        for capture in metadata["captures"]:
            assert capture["rights_status"] in {"source_link_only", "open_asset", "local_capture", "unclear"}
        assert "/Users/" not in json.dumps(metadata)
        assert "private://local_path/" not in json.dumps(metadata)


def test_seed_script_writes_requested_root(tmp_path: Path, capsys):
    from scripts.vector_aesthetics_seed_cases import main

    rc = main(["--root", str(tmp_path)])

    captured = capsys.readouterr().out
    assert rc == 0
    assert '"status": "written"' in captured
    assert len(list((tmp_path / "cases").iterdir())) == 12
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_seed_cases.py -q
```

Expected: FAIL with missing `vulca.vector_aesthetics.seeds`.

- [ ] **Step 3: Implement seed writer**

Create `src/vulca/vector_aesthetics/seeds.py` with a literal `SEED_CASES` list containing these exact IDs and URLs:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SEED_CASES: list[dict[str, Any]] = [
    {
        "id": "makio-meshline",
        "title": "Makio MeshLine",
        "canonical_url": "https://meshline.makio.io/",
        "source_type": "demo",
        "year": 2025,
        "author_or_studio": "Makio64",
        "currentness": "still_current",
        "summary": "Modern Three.js/WebGPU-oriented wide-line reference for route-like vector forms.",
        "why_relevant": "Core learning source for thick 3D vector routes, animated trails, gradients, and dash behavior.",
        "visual_families": ["meshline", "data_tunnel"],
        "module_types": ["meshline", "shader_material", "performance_runtime", "vulca_translation"],
        "canonical_sources": ["https://meshline.makio.io/", "https://github.com/Makio64/makio-meshline"],
    },
    {
        "id": "codrops-threejs-meshline-family",
        "title": "Codrops Three.js MeshLines Demo Family",
        "canonical_url": "https://tympanus.net/codrops/hub/tag/three-js/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops / featured creative technologists",
        "currentness": "2025_plus",
        "summary": "2025+ Three.js demo family containing contemporary line-sculpture and WebGPU/TSL directions.",
        "why_relevant": "Useful as a source for selecting meshline sculpture and vector-space motion cases.",
        "visual_families": ["meshline", "wire_grid", "shader_material"],
        "module_types": ["meshline", "shader_material", "performance_runtime"],
        "canonical_sources": ["https://tympanus.net/codrops/hub/tag/three-js/"],
    },
    {
        "id": "interactive-text-destruction-webgpu-tsl",
        "title": "Interactive Text Destruction with Three.js, WebGPU and TSL",
        "canonical_url": "https://tympanus.net/codrops/2025/07/22/interactive-text-destruction-with-three-js-webgpu-and-tsl/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "Interactive 3D text destruction and reconstruction using Three.js, WebGPU, and TSL.",
        "why_relevant": "Maps directly to technical evidence labels exploding into fragments and rebuilding into readable state.",
        "visual_families": ["typography_3d", "particle_vector"],
        "module_types": ["typography_3d", "shader_material", "interaction_state", "vulca_translation"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/07/22/interactive-text-destruction-with-three-js-webgpu-and-tsl/"],
    },
    {
        "id": "webgpu-gommage-msdf-dissolve",
        "title": "WebGPU Gommage Effect",
        "canonical_url": "https://tympanus.net/codrops/2026/01/28/webgpu-gommage-effect-dissolving-msdf-text-into-dust-and-petals-with-three-js-tsl/",
        "source_type": "tutorial",
        "year": 2026,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "MSDF text dissolve into dust and petals using Three.js TSL and WebGPU-era rendering.",
        "why_relevant": "Strong teaching case for turning typography into particle-vector material states.",
        "visual_families": ["typography_3d", "particle_vector", "shader_material"],
        "module_types": ["typography_3d", "particle_vector", "shader_material", "asset_pipeline"],
        "canonical_sources": ["https://tympanus.net/codrops/2026/01/28/webgpu-gommage-effect-dissolving-msdf-text-into-dust-and-petals-with-three-js-tsl/"],
    },
    {
        "id": "webgpu-scanning-depth-maps",
        "title": "WebGPU Scanning Effect with Depth Maps",
        "canonical_url": "https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "Depth-map driven scanning effect for technical reveal and inspection aesthetics.",
        "why_relevant": "Directly maps to VULCA review-gap inspection and scan-plane primitives.",
        "visual_families": ["scan_depth", "shader_material"],
        "module_types": ["scan_depth", "shader_material", "asset_pipeline", "vulca_translation"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/"],
    },
    {
        "id": "matrix-sentinels-particle-trails-tsl",
        "title": "Matrix Sentinels Dynamic Particle Trails",
        "canonical_url": "https://tympanus.net/codrops/2025/05/05/matrix-sentinels-building-dynamic-particle-trails-with-tsl/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "TSL particle trails and dynamic motion structure in Three.js.",
        "why_relevant": "Useful for hybrid particle-vector trail behavior and uncertainty-state visualization.",
        "visual_families": ["particle_vector", "data_tunnel"],
        "module_types": ["particle_vector", "shader_material", "interaction_state", "performance_runtime"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/05/05/matrix-sentinels-building-dynamic-particle-trails-with-tsl/"],
    },
    {
        "id": "countertype-three-text",
        "title": "Countertype three-text",
        "canonical_url": "https://countertype.com/",
        "source_type": "documentation",
        "year": 2025,
        "author_or_studio": "Countertype",
        "currentness": "still_current",
        "summary": "Modern Three.js text layout and 3D typography pipeline reference.",
        "why_relevant": "Provides technical baseline for treating words and labels as 3D vector material.",
        "visual_families": ["typography_3d"],
        "module_types": ["typography_3d", "asset_pipeline", "performance_runtime"],
        "canonical_sources": ["https://countertype.com/"],
    },
    {
        "id": "phantom-land-interactive-grid",
        "title": "Phantom.land Interactive Grid and 3D Face Particle System",
        "canonical_url": "https://tympanus.net/codrops/2025/06/30/invisible-forces-the-making-of-phantom-lands-interactive-grid-and-3d-face-particle-system/",
        "source_type": "case_study",
        "year": 2025,
        "author_or_studio": "Phantom.land / Codrops",
        "currentness": "2025_plus",
        "summary": "Interactive grid and 3D particle system case study with contemporary technical atmosphere.",
        "why_relevant": "Good reference for spatial technical surfaces and interactive distortion.",
        "visual_families": ["wire_grid", "particle_vector", "ui_sculpture"],
        "module_types": ["wire_grid", "particle_vector", "interaction_state", "vulca_translation"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/06/30/invisible-forces-the-making-of-phantom-lands-interactive-grid-and-3d-face-particle-system/"],
    },
    {
        "id": "false-earth-webgpu-world",
        "title": "False Earth",
        "canonical_url": "https://tympanus.net/codrops/2026/04/21/false-earth-from-webgl-limits-to-a-webgpu-driven-world/",
        "source_type": "case_study",
        "year": 2026,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "WebGPU-driven world logic and atmosphere case study.",
        "why_relevant": "Useful high-risk reference for world-scale technical space and WebGPU constraints.",
        "visual_families": ["ui_sculpture", "shader_material"],
        "module_types": ["shader_material", "performance_runtime", "asset_pipeline"],
        "canonical_sources": ["https://tympanus.net/codrops/2026/04/21/false-earth-from-webgl-limits-to-a-webgpu-driven-world/"],
    },
    {
        "id": "spline-contemporary-3d-web",
        "title": "Spline Contemporary 3D Web References",
        "canonical_url": "https://spline.design/",
        "source_type": "product_ref",
        "year": 2025,
        "author_or_studio": "Spline",
        "currentness": "still_current",
        "summary": "Contemporary 3D web design aesthetic reference for spatial UI sculpture.",
        "why_relevant": "Aesthetic reference only; implementation should remain code-native in this repo.",
        "visual_families": ["ui_sculpture"],
        "module_types": ["ui_sculpture", "interaction_state", "vulca_translation"],
        "canonical_sources": ["https://spline.design/"],
    },
    {
        "id": "threejs-webgpu-tsl-docs",
        "title": "Three.js WebGPURenderer and TSL Documentation",
        "canonical_url": "https://threejs.org/docs/pages/WebGPURenderer.html",
        "source_type": "documentation",
        "year": 2025,
        "author_or_studio": "Three.js",
        "currentness": "still_current",
        "summary": "Technical baseline for WebGPU renderer, TSL, and fallback risk.",
        "why_relevant": "Defines implementation constraints for 2025+ Three.js technical aesthetics.",
        "visual_families": ["shader_material"],
        "module_types": ["shader_material", "performance_runtime"],
        "canonical_sources": ["https://threejs.org/docs/pages/WebGPURenderer.html", "https://threejs.org/docs/pages/TSL.html"],
    },
    {
        "id": "maxime-heckel-tsl-webgpu-guide",
        "title": "Field Guide to TSL and WebGPU",
        "canonical_url": "https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Maxime Heckel",
        "currentness": "still_current",
        "summary": "Teaching reference for TSL and WebGPU mental models.",
        "why_relevant": "Best seed for lesson-path explanations and implementation risk notes.",
        "visual_families": ["shader_material"],
        "module_types": ["shader_material", "performance_runtime"],
        "canonical_sources": ["https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/"],
    },
]
```

In the same file, add writer helpers:

```python
def _default_scores(case: dict[str, Any]) -> dict[str, int]:
    license_score = 2 if case["source_type"] in {"github", "documentation", "tutorial"} else 1
    return {
        "aesthetic_relevance": 3,
        "technical_learnability": 2,
        "multimodal_completeness": 0,
        "interaction_clarity": 1,
        "vulca_transfer_value": 2,
        "license_safety": license_score,
    }


def _module_payload(module_type: str) -> dict[str, Any]:
    return {"learning_primitive": f"{module_type} learning primitive", "seed_status": "metadata_only"}


def _metadata(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["id"],
        "title": case["title"],
        "canonical_url": case["canonical_url"],
        "source_type": case["source_type"],
        "year": case["year"],
        "author_or_studio": case["author_or_studio"],
        "currentness": case["currentness"],
        "summary": case["summary"],
        "why_relevant": case["why_relevant"],
        "review_status": "candidate",
        "quality_scores": _default_scores(case),
        "visual_families": case["visual_families"],
        "canonical_sources": case["canonical_sources"],
        "modules": [
            {
                "module_type": module_type,
                "payload": _module_payload(module_type),
                "evidence_refs": [],
                "confidence": "low",
                "review_status": "partial",
                "review_notes": "Seed module; requires ingestion review.",
            }
            for module_type in case["module_types"]
        ],
        "captures": [
            {
                "id": "canonical-source",
                "evidence_type": "external_doc",
                "path_or_url": case["canonical_url"],
                "capture_method": "source_read",
                "viewport": "none",
                "interaction": "none",
                "captured_at": "2026-06-29",
                "source_url": case["canonical_url"],
                "confidence": "high",
                "rights_status": "source_link_only",
                "notes": "Seed metadata record. Screenshots and motion captures are not complete yet.",
            }
        ],
    }


def write_seed_cases(root: Path) -> list[Path]:
    cases_root = root / "cases"
    cases_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for case in SEED_CASES:
        case_dir = cases_root / str(case["id"])
        case_dir.mkdir(parents=True, exist_ok=True)
        for child in ["screenshots", "videos", "traces", "code", "assets"]:
            (case_dir / child).mkdir(exist_ok=True)
        (case_dir / "metadata.json").write_text(
            json.dumps(_metadata(case), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (case_dir / "anatomy.md").write_text(
            f"# Anatomy: {case['title']}\n\nSeed anatomy. Ingestion must identify scenes, moments, primitives, and techniques.\n",
            encoding="utf-8",
        )
        (case_dir / "lesson.md").write_text(
            f"# Lesson: {case['title']}\n\nSeed lesson. Ingestion must define a minimal rebuild exercise before shortlist promotion.\n",
            encoding="utf-8",
        )
        (case_dir / "vulca_translation.md").write_text(
            f"# VULCA Translation: {case['title']}\n\nSeed translation. Review must map this case to source trail, evidence layer, review gap, route decision, or uncertainty.\n",
            encoding="utf-8",
        )
        (case_dir / "assets" / "asset_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "case_id": case["id"],
                    "assets": [],
                    "rights_status": "source_link_only",
                    "notes": "No local assets archived in seed state.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(case_dir)
    return written
```

Create `scripts/vector_aesthetics_seed_cases.py` with:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write seed case folders for the 3D vector aesthetics corpus.")
    parser.add_argument("--root", default="data/vector-aesthetics")
    args = parser.parse_args(argv)

    from vulca.vector_aesthetics.seeds import write_seed_cases

    written = write_seed_cases(Path(args.root))
    print(
        json.dumps(
            {"status": "written", "root": args.root, "case_count": len(written), "cases": [path.name for path in written]},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run seed tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_seed_cases.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Write real seed folders**

Run:

```bash
PYTHONPATH=src python scripts/vector_aesthetics_seed_cases.py --root data/vector-aesthetics
```

Expected output includes `"case_count": 12`.

- [ ] **Step 6: Commit**

```bash
git add src/vulca/vector_aesthetics/seeds.py scripts/vector_aesthetics_seed_cases.py tests/test_vector_aesthetics_seed_cases.py data/vector-aesthetics/cases
git commit -m "data: seed vector aesthetics reference cases"
```

---

## Task 3: Compile Case Folders To SQLite And Review JSON

**Files:**
- Create: `src/vulca/vector_aesthetics/compiler.py`
- Create: `tests/test_vector_aesthetics_compiler.py`

**Interfaces:**
- Consumes: `validate_case_folder` and `case_to_review_dict`.
- Produces: `compile_database(root: Path, sqlite_path: Path) -> list[CaseRecord]`
- Produces: `export_review_json(records: list[CaseRecord], output_path: Path) -> Path`

- [ ] **Step 1: Write failing compiler tests**

Create `tests/test_vector_aesthetics_compiler.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
import sqlite3


def test_compile_database_writes_case_and_module_rows(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    sqlite_path = root / "references.sqlite"

    records = compile_database(root, sqlite_path)

    assert len(records) == 12
    with sqlite3.connect(sqlite_path) as conn:
        assert conn.execute("select count(*) from cases").fetchone()[0] == 12
        assert conn.execute("select count(*) from module_payloads").fetchone()[0] >= 12
        assert conn.execute("select count(*) from captures").fetchone()[0] == 12


def test_export_review_json_is_bounded_and_sorted(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    records = compile_database(root, root / "references.sqlite")
    output_path = tmp_path / "references.json"

    export_review_json(records, output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["summary"]["case_count"] == 12
    assert [case["id"] for case in payload["cases"]] == sorted(case["id"] for case in payload["cases"])
    assert "sk-" not in json.dumps(payload)


def test_compile_database_is_deterministic_for_same_case_folders(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    first_records = compile_database(root, root / "first.sqlite")
    second_records = compile_database(root, root / "second.sqlite")
    first_json = export_review_json(first_records, tmp_path / "first.json").read_text(encoding="utf-8")
    second_json = export_review_json(second_records, tmp_path / "second.json").read_text(encoding="utf-8")

    assert first_json == second_json
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_compiler.py -q
```

Expected: FAIL with missing `vulca.vector_aesthetics.compiler`.

- [ ] **Step 3: Implement compiler**

Create `src/vulca/vector_aesthetics/compiler.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .schema import CaseRecord, case_to_review_dict, validate_case_folder


SCHEMA_SQL = """
drop table if exists cases;
drop table if exists module_payloads;
drop table if exists captures;
create table cases (
  id text primary key,
  title text not null,
  canonical_url text not null,
  source_type text not null,
  year integer not null,
  author_or_studio text not null,
  currentness text not null,
  review_status text not null,
  quality_score_total integer not null,
  coverage_json text not null,
  metadata_json text not null
);
create table module_payloads (
  id integer primary key autoincrement,
  case_id text not null,
  module_type text not null,
  payload_json text not null,
  evidence_refs_json text not null,
  confidence text not null,
  review_status text not null,
  review_notes text not null
);
create table captures (
  id text not null,
  case_id text not null,
  evidence_type text not null,
  path_or_url text not null,
  capture_method text not null,
  rights_status text not null,
  confidence text not null,
  notes text not null,
  primary key (case_id, id)
);
"""


def _case_dirs(root: Path) -> list[Path]:
    cases_root = root / "cases"
    if not cases_root.exists():
        return []
    return sorted(path for path in cases_root.iterdir() if path.is_dir())


def compile_database(root: Path, sqlite_path: Path) -> list[CaseRecord]:
    records = [validate_case_folder(path) for path in _case_dirs(root)]
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(sqlite_path) as conn:
        conn.executescript(SCHEMA_SQL)
        for record in records:
            conn.execute(
                """
                insert into cases values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.metadata["title"],
                    record.metadata["canonical_url"],
                    record.metadata["source_type"],
                    int(record.metadata["year"]),
                    record.metadata["author_or_studio"],
                    record.metadata["currentness"],
                    record.metadata["review_status"],
                    record.quality_score_total,
                    json.dumps(record.coverage, sort_keys=True),
                    json.dumps(record.metadata, sort_keys=True),
                ),
            )
            for module in record.metadata["modules"]:
                conn.execute(
                    """
                    insert into module_payloads
                    (case_id, module_type, payload_json, evidence_refs_json, confidence, review_status, review_notes)
                    values (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        module["module_type"],
                        json.dumps(module["payload"], sort_keys=True),
                        json.dumps(module.get("evidence_refs", []), sort_keys=True),
                        module["confidence"],
                        module["review_status"],
                        module.get("review_notes", ""),
                    ),
                )
            for capture in record.metadata["captures"]:
                conn.execute(
                    """
                    insert into captures
                    (id, case_id, evidence_type, path_or_url, capture_method, rights_status, confidence, notes)
                    values (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        capture["id"],
                        record.id,
                        capture["evidence_type"],
                        capture["path_or_url"],
                        capture["capture_method"],
                        capture["rights_status"],
                        capture["confidence"],
                        capture["notes"],
                    ),
                )
    return records


def export_review_json(records: list[CaseRecord], output_path: Path) -> Path:
    cases = [case_to_review_dict(record) for record in sorted(records, key=lambda item: item.id)]
    payload = {
        "schema_version": 1,
        "summary": {
            "case_count": len(cases),
            "shortlist_count": sum(1 for case in cases if case["review_status"] == "shortlist"),
            "candidate_count": sum(1 for case in cases if case["review_status"] == "candidate"),
        },
        "cases": cases,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path
```

- [ ] **Step 4: Run compiler tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_compiler.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/vector_aesthetics/compiler.py tests/test_vector_aesthetics_compiler.py
git commit -m "feat: compile vector aesthetics corpus index"
```

---

## Task 4: Static HTML Review Atlas

**Files:**
- Create: `src/vulca/vector_aesthetics/review_html.py`
- Create: `tests/test_vector_aesthetics_review_html.py`

**Interfaces:**
- Consumes: review JSON from Task 3.
- Produces: `write_review_html(review_json_path: Path, html_path: Path) -> Path`

- [ ] **Step 1: Write failing HTML tests**

Create `tests/test_vector_aesthetics_review_html.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path


def test_write_review_html_renders_required_views(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json
    from vulca.vector_aesthetics.review_html import write_review_html
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    records = compile_database(root, root / "references.sqlite")
    review_json = export_review_json(records, tmp_path / "references.json")
    html_path = write_review_html(review_json, tmp_path / "index.html")
    html_text = html_path.read_text(encoding="utf-8")

    assert "3D Vector Aesthetics Learning Atlas" in html_text
    assert "Atlas View" in html_text
    assert "Anatomy View" in html_text
    assert "Compare View" in html_text
    assert "Coverage View" in html_text
    assert "Lesson Path View" in html_text
    assert "Makio MeshLine" in html_text
    assert "<script id=\"review-data\" type=\"application/json\">" in html_text


def test_write_review_html_redacts_secret_like_json(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "secret-case",
                        "title": "Secret Case",
                        "summary": "contains sk-proj-secret",
                        "visual_families": [],
                        "coverage": {},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com",
                        "modules": [],
                        "captures": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_path = write_review_html(review_json, tmp_path / "index.html")

    assert "sk-proj-secret" not in html_path.read_text(encoding="utf-8")
    assert "[redacted]" in html_path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_review_html.py -q
```

Expected: FAIL with missing `vulca.vector_aesthetics.review_html`.

- [ ] **Step 3: Implement static HTML renderer**

Create `src/vulca/vector_aesthetics/review_html.py` with:

```python
from __future__ import annotations

import html
import json
from pathlib import Path
import re
from typing import Any


SECRET_PATTERNS = [re.compile(r"sk-[A-Za-z0-9_-]+")]


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _redact(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[redacted]", result)
    return result


def _safe_json_script(payload: dict[str, Any]) -> str:
    return _redact(json.dumps(payload, ensure_ascii=False, sort_keys=True)).replace("</", "<\\/")


def _badge_list(items: list[str]) -> str:
    return "".join(f"<span>{_escape(item)}</span>" for item in items)


def _coverage(coverage: dict[str, str]) -> str:
    rows = []
    for key, value in sorted(coverage.items()):
        rows.append(f"<li><strong>{_escape(key)}</strong><span>{_escape(value)}</span></li>")
    return "<ul class=\"coverage-list\">" + "".join(rows) + "</ul>"


def _case_card(case: dict[str, Any]) -> str:
    captures = case.get("captures", [])
    capture_links = "".join(
        f"<a href=\"{_escape(capture.get('path_or_url', ''))}\">{_escape(capture.get('evidence_type', 'capture'))}</a>"
        for capture in captures[:4]
    )
    modules = [module.get("module_type", "") for module in case.get("modules", [])]
    return "\n".join(
        [
            "<article class=\"case-card\">",
            "<div class=\"case-head\">",
            f"<h2>{_escape(case.get('title', 'Untitled'))}</h2>",
            f"<span class=\"score\">{_escape(case.get('quality_score_total', 0))}/18</span>",
            "</div>",
            f"<p>{_escape(case.get('summary', ''))}</p>",
            f"<p><a href=\"{_escape(case.get('canonical_url', ''))}\">{_escape(case.get('canonical_url', ''))}</a></p>",
            f"<div class=\"badges\">{_badge_list(case.get('visual_families', []))}</div>",
            f"<div class=\"badges muted-badges\">{_badge_list(modules)}</div>",
            _coverage(case.get("coverage", {})),
            f"<div class=\"links\">{capture_links}</div>",
            "</article>",
        ]
    )


def _html(payload: dict[str, Any]) -> str:
    cases = payload.get("cases", [])
    cards = "\n".join(_case_card(case) for case in cases)
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "<title>3D Vector Aesthetics Learning Atlas</title>",
            "<style>",
            ":root{color-scheme:dark;font-family:Arial,sans-serif;background:#0d1014;color:#e8edf2}",
            "body{margin:0;padding:28px;background:#0d1014}",
            "main{max-width:1280px;margin:0 auto}",
            "header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:22px}",
            "h1{font-size:32px;margin:0 0 8px}h2{font-size:18px;margin:0}p{color:#aeb8c4;line-height:1.5}",
            ".views{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:18px 0}",
            ".view-pill,.case-card{border:1px solid #27313d;background:#131922;border-radius:8px}",
            ".view-pill{padding:12px;color:#d8e4ef}",
            ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}",
            ".case-card{padding:16px}.case-head{display:flex;justify-content:space-between;gap:12px}",
            ".score{font:12px/1.2 monospace;border:1px solid #415061;border-radius:999px;padding:5px 8px;color:#c9f3ff}",
            ".badges{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.badges span{font:12px/1.2 monospace;background:#1e2a36;border:1px solid #32404f;border-radius:999px;padding:5px 7px}",
            ".muted-badges span{color:#b3bcc6}.coverage-list{list-style:none;padding:0;margin:12px 0;display:grid;gap:5px}.coverage-list li{display:flex;justify-content:space-between;gap:12px;border-top:1px solid #222b35;padding-top:5px}",
            "a{color:#8ed7ff}.links{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<header><div><h1>3D Vector Aesthetics Learning Atlas</h1><p>Archive + Lab + Course review surface for contemporary technical vector references.</p></div></header>",
            "<section class=\"views\">",
            "<div class=\"view-pill\">Atlas View</div>",
            "<div class=\"view-pill\">Anatomy View</div>",
            "<div class=\"view-pill\">Compare View</div>",
            "<div class=\"view-pill\">Coverage View</div>",
            "<div class=\"view-pill\">Lesson Path View</div>",
            "</section>",
            f"<section class=\"grid\">{cards}</section>",
            f"<script id=\"review-data\" type=\"application/json\">{_safe_json_script(payload)}</script>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_review_html(review_json_path: Path, html_path: Path) -> Path:
    payload = json.loads(review_json_path.read_text(encoding="utf-8"))
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(_html(payload), encoding="utf-8")
    return html_path
```

- [ ] **Step 4: Run HTML tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_review_html.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/vector_aesthetics/review_html.py tests/test_vector_aesthetics_review_html.py
git commit -m "feat: render vector aesthetics review atlas"
```

---

## Task 5: Capture Record Tooling

**Files:**
- Create: `src/vulca/vector_aesthetics/captures.py`
- Create: `scripts/vector_aesthetics_record_capture.py`
- Create: `tests/test_vector_aesthetics_captures.py`

**Interfaces:**
- Consumes: existing `metadata.json`.
- Produces: `add_capture(case_dir: Path, capture: dict[str, str]) -> dict[str, object]`
- Produces: `record_capture_failure(case_dir: Path, *, evidence_type: str, notes: str, source_url: str) -> dict[str, object]`

- [ ] **Step 1: Write failing capture tests**

Create `tests/test_vector_aesthetics_captures.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path


def test_record_capture_failure_adds_explicit_missing_evidence(tmp_path: Path):
    from vulca.vector_aesthetics.captures import record_capture_failure
    from vulca.vector_aesthetics.schema import validate_case_folder
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]

    record_capture_failure(
        case_dir,
        evidence_type="video",
        notes="Autoplay blocked in automated browser.",
        source_url="https://meshline.makio.io/",
    )

    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    assert any(capture["evidence_type"] == "video" for capture in metadata["captures"])
    assert validate_case_folder(case_dir).coverage["video"] == "complete"


def test_add_capture_rejects_missing_local_file(tmp_path: Path):
    from vulca.vector_aesthetics.captures import add_capture
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]

    try:
        add_capture(
            case_dir,
            {
                "id": "missing-screenshot",
                "evidence_type": "screenshot",
                "path_or_url": "screenshots/missing.png",
                "capture_method": "manual_browser",
                "viewport": "1440x900",
                "interaction": "idle",
                "captured_at": "2026-06-29",
                "source_url": "https://meshline.makio.io/",
                "confidence": "low",
                "rights_status": "local_capture",
                "notes": "Missing file should fail.",
            },
        )
    except FileNotFoundError as exc:
        assert "screenshots/missing.png" in str(exc)
    else:
        raise AssertionError("missing local file was accepted")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_captures.py -q
```

Expected: FAIL with missing `vulca.vector_aesthetics.captures`.

- [ ] **Step 3: Implement capture record helpers**

Create `src/vulca/vector_aesthetics/captures.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import validate_case_folder


LOCAL_EVIDENCE_TYPES = {"screenshot", "video", "trace", "code_note", "asset_manifest"}


def _metadata_path(case_dir: Path) -> Path:
    return case_dir / "metadata.json"


def _load(case_dir: Path) -> dict[str, Any]:
    return json.loads(_metadata_path(case_dir).read_text(encoding="utf-8"))


def _write(case_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    _metadata_path(case_dir).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_case_folder(case_dir)
    return payload


def _assert_local_file(case_dir: Path, capture: dict[str, str]) -> None:
    if capture["rights_status"] != "local_capture":
        return
    if capture["evidence_type"] not in LOCAL_EVIDENCE_TYPES:
        return
    local_path = case_dir / capture["path_or_url"]
    if not local_path.exists():
        raise FileNotFoundError(capture["path_or_url"])


def add_capture(case_dir: Path, capture: dict[str, str]) -> dict[str, Any]:
    _assert_local_file(case_dir, capture)
    payload = _load(case_dir)
    captures = [item for item in payload["captures"] if item["id"] != capture["id"]]
    captures.append(capture)
    payload["captures"] = sorted(captures, key=lambda item: item["id"])
    return _write(case_dir, payload)


def record_capture_failure(case_dir: Path, *, evidence_type: str, notes: str, source_url: str) -> dict[str, Any]:
    capture = {
        "id": f"{evidence_type}-capture-failure",
        "evidence_type": evidence_type,
        "path_or_url": source_url,
        "capture_method": "manual_browser",
        "viewport": "none",
        "interaction": "capture_failed",
        "captured_at": "2026-06-29",
        "source_url": source_url,
        "confidence": "medium",
        "rights_status": "source_link_only",
        "notes": notes,
    }
    return add_capture(case_dir, capture)
```

Create `scripts/vector_aesthetics_record_capture.py` with:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record local evidence or capture failures for a vector aesthetics case.")
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--failure", action="store_true")
    parser.add_argument("--evidence-type", required=True)
    parser.add_argument("--path-or-url")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--notes", required=True)
    parser.add_argument("--id", default="")
    parser.add_argument("--viewport", default="none")
    parser.add_argument("--interaction", default="none")
    parser.add_argument("--captured-at", default="2026-06-29")
    args = parser.parse_args(argv)

    from vulca.vector_aesthetics.captures import add_capture, record_capture_failure

    case_dir = Path(args.case_dir)
    if args.failure:
        payload = record_capture_failure(
            case_dir,
            evidence_type=args.evidence_type,
            notes=args.notes,
            source_url=args.source_url,
        )
    else:
        if not args.path_or_url:
            raise SystemExit("error: --path-or-url is required unless --failure is set")
        payload = add_capture(
            case_dir,
            {
                "id": args.id or f"{args.evidence_type}-{args.interaction}",
                "evidence_type": args.evidence_type,
                "path_or_url": args.path_or_url,
                "capture_method": "manual_browser",
                "viewport": args.viewport,
                "interaction": args.interaction,
                "captured_at": args.captured_at,
                "source_url": args.source_url,
                "confidence": "medium",
                "rights_status": "local_capture",
                "notes": args.notes,
            },
        )
    print(json.dumps({"status": "recorded", "case_id": payload["id"], "capture_count": len(payload["captures"])}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run capture tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_captures.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/vector_aesthetics/captures.py scripts/vector_aesthetics_record_capture.py tests/test_vector_aesthetics_captures.py
git commit -m "feat: record vector aesthetics evidence captures"
```

---

## Task 6: Build Review CLI And End-To-End Verification

**Files:**
- Create: `scripts/vector_aesthetics_build_review.py`
- Create: `tests/test_vector_aesthetics_cli.py`
- Generated by script:
  - local build output: `data/vector-aesthetics/references.sqlite`
  - local build output: `output/review/3d-vector-aesthetics-learning-db/data/references.json`
  - local build output: `output/review/3d-vector-aesthetics-learning-db/index.html`

**Interfaces:**
- Consumes: seed folders, compiler, and review HTML renderer.
- Produces: one command that validates and builds the local review atlas.

- [ ] **Step 1: Write failing CLI tests**

Create `tests/test_vector_aesthetics_cli.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path


def test_build_review_cli_writes_sqlite_json_and_html(tmp_path: Path, capsys):
    from scripts.vector_aesthetics_seed_cases import main as seed_main
    from scripts.vector_aesthetics_build_review import main as build_main

    root = tmp_path / "vector-aesthetics"
    output = tmp_path / "review"
    assert seed_main(["--root", str(root)]) == 0

    rc = build_main(["--root", str(root), "--output", str(output)])

    captured = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(captured)
    assert payload["status"] == "written"
    assert payload["case_count"] == 12
    assert (root / "references.sqlite").exists()
    assert (output / "data" / "references.json").exists()
    assert (output / "index.html").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_cli.py -q
```

Expected: FAIL with missing `scripts.vector_aesthetics_build_review`.

- [ ] **Step 3: Implement build CLI**

Create `scripts/vector_aesthetics_build_review.py` with:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the 3D vector aesthetics learning DB review atlas.")
    parser.add_argument("--root", default="data/vector-aesthetics")
    parser.add_argument("--output", default="output/review/3d-vector-aesthetics-learning-db")
    args = parser.parse_args(argv)

    from vulca.vector_aesthetics.compiler import compile_database, export_review_json
    from vulca.vector_aesthetics.review_html import write_review_html

    root = Path(args.root)
    output = Path(args.output)
    sqlite_path = root / "references.sqlite"
    review_json = output / "data" / "references.json"
    html_path = output / "index.html"
    records = compile_database(root, sqlite_path)
    export_review_json(records, review_json)
    write_review_html(review_json, html_path)
    print(
        json.dumps(
            {
                "status": "written",
                "case_count": len(records),
                "sqlite": str(sqlite_path),
                "review_json": str(review_json),
                "html": str(html_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Ignore local generated review outputs**

Append these lines to `.gitignore` if they are not already present:

```gitignore
# 3D vector aesthetics learning DB local build outputs
data/vector-aesthetics/references.sqlite
output/review/3d-vector-aesthetics-learning-db/
```

- [ ] **Step 5: Run full vector aesthetics tests**

Run:

```bash
PYTHONPATH=src pytest \
  tests/test_vector_aesthetics_schema.py \
  tests/test_vector_aesthetics_seed_cases.py \
  tests/test_vector_aesthetics_compiler.py \
  tests/test_vector_aesthetics_review_html.py \
  tests/test_vector_aesthetics_captures.py \
  tests/test_vector_aesthetics_cli.py \
  -q
```

Expected: all tests pass.

- [ ] **Step 6: Build real local review atlas**

Run:

```bash
PYTHONPATH=src python scripts/vector_aesthetics_build_review.py \
  --root data/vector-aesthetics \
  --output output/review/3d-vector-aesthetics-learning-db
```

Expected output includes `"status": "written"` and `"case_count": 12`.

- [ ] **Step 7: Inspect generated HTML smoke output**

Run:

```bash
python - <<'PY'
from pathlib import Path
html = Path("output/review/3d-vector-aesthetics-learning-db/index.html").read_text(encoding="utf-8")
required = [
    "3D Vector Aesthetics Learning Atlas",
    "Atlas View",
    "Coverage View",
    "Makio MeshLine",
    "WebGPU Gommage Effect",
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit(f"missing HTML markers: {missing}")
print("html smoke passed")
PY
```

Expected: `html smoke passed`.

- [ ] **Step 8: Confirm generated outputs are ignored**

Run:

```bash
git status --short data/vector-aesthetics/references.sqlite output/review/3d-vector-aesthetics-learning-db
```

Expected: no output.

- [ ] **Step 9: Commit**

```bash
git add .gitignore scripts/vector_aesthetics_build_review.py tests/test_vector_aesthetics_cli.py
git commit -m "feat: build vector aesthetics review atlas"
```

---

## Final Verification

After all tasks are complete, run:

```bash
PYTHONPATH=src pytest \
  tests/test_vector_aesthetics_schema.py \
  tests/test_vector_aesthetics_seed_cases.py \
  tests/test_vector_aesthetics_compiler.py \
  tests/test_vector_aesthetics_review_html.py \
  tests/test_vector_aesthetics_captures.py \
  tests/test_vector_aesthetics_cli.py \
  -q
```

Expected: all tests pass.

Run:

```bash
git status --short
```

Expected: no modified or staged files from this plan except unrelated pre-existing untracked files that were already present before execution.

Open the generated review page:

```text
output/review/3d-vector-aesthetics-learning-db/index.html
```

Verify that it shows:

- 12 seed cases;
- visible score and coverage state for each case;
- canonical source links;
- module badges;
- capture links or explicit capture status;
- the five view markers: Atlas, Anatomy, Compare, Coverage, Lesson Path.
