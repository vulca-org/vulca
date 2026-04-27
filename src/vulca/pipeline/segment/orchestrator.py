"""In-process orchestrator.

Thin typed facade over the stage functions in scripts/claude_orchestrated_pipeline.py.
All P0 concerns (plan schema, filename safety, in-process execution, structured
errors, stage timings) are enforced here. Heavy detector/mask logic still lives
in the script module to avoid churn; we import it.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.pipeline.segment.plan import Plan, _sanitize_name
from vulca.pipeline.segment.context import (
    PipelineContext, PipelineResult, DetectionRecord, StageTiming
)

# Import stage primitives from the existing script module.
# This is intentional: they're well-tested, heavily used, and rewriting from
# scratch would invalidate our 24-image baseline.
_REPO = Path(__file__).resolve().parents[4]
_SCRIPTS = _REPO / "scripts"


def _import_cop():
    """Import claude_orchestrated_pipeline.py as a module, ensuring sys.path
    contains the scripts/ directory. Idempotent; returns the same module
    instance on repeated calls via sys.modules cache.

    Used by orchestrator.run() and by the unload_models MCP tool so both sites
    bind the same @lru_cache'd loader instances.
    """
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))
    import claude_orchestrated_pipeline as cop
    return cop

SUCCESS_RATE_THRESHOLD = 0.70
MANIFEST_VERSION = 5


def _safe_write(path: Path, content: str):
    """Atomic write: temp file → rename."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(path)


def _load_image_safely(img_path: Path, max_pixels: int = 100_000_000):
    """Replicates script's _load_image_safely with same safety properties."""
    try:
        with Image.open(img_path) as probe:
            w, h = probe.size
            if w * h > max_pixels:
                raise ValueError(f"image too large: {w}x{h}={w*h:,} exceeds {max_pixels:,}")
            probe.verify()
    except Image.DecompressionBombError:
        raise ValueError(f"decompression bomb refused: {img_path}")
    except Image.UnidentifiedImageError:
        raise ValueError(f"unidentified image format: {img_path}")

    img = Image.open(img_path)
    try:
        from PIL import ImageOps
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    return img.convert("RGB")


def _build_layer_entry(slug: str, l: dict) -> dict:
    """Construct a manifest layer dict; sanitize the filename."""
    name = _sanitize_name(l["name"])
    file = f"{name}.png"
    layer_id = "layer_" + hashlib.md5(f"{slug}-{name}".encode()).hexdigest()[:8]
    return {
        "id": layer_id,
        "name": name,
        "label": l.get("label", name),
        "description": l.get("label", name),
        "z_index": l["z"],
        "blend_mode": "normal",
        "content_type": name,
        "semantic_path": l.get("semantic_path", name),
        "visible": True,
        "locked": False,
        "file": file,
        "bbox": l.get("bbox"),
        "det_score": l.get("det_score"),
        "sam_score": l.get("sam_score"),
        "regeneration_prompt": l.get("label", name),
        "opacity": 1.0,
        "x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0,
        "rotation": 0.0, "content_bbox": None,
    }


def run(
    plan: "Plan | dict | str | Path",
    image_path: "str | Path",
    output_dir: "str | Path",
    *,
    force: bool = True,
    strict: bool = False,
) -> PipelineResult:
    """Main entrypoint — run the full pipeline on one image.

    Args:
        plan: Plan instance, dict, JSON string path (will validate via Pydantic).
        image_path: source image.
        output_dir: destination for per-layer PNGs + manifest.json.
        force: overwrite existing manifest.
        strict: raise if success_rate < SUCCESS_RATE_THRESHOLD.

    Returns:
        PipelineResult with status, layers, detection_report, stage_timings.

    Raises:
        ValueError on plan schema / image validation failures.
        RuntimeError if strict=True and partial detection.
    """
    t0 = time.time()

    # ── Plan validation (fixes C3) ──
    if isinstance(plan, (str, Path)):
        plan_obj = Plan.from_file(plan)
    elif isinstance(plan, dict):
        plan_obj = Plan.model_validate(plan)
    elif isinstance(plan, Plan):
        plan_obj = plan
    else:
        raise ValueError(f"plan must be Plan, dict, or path; got {type(plan)}")

    image_path = Path(image_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not image_path.exists():
        return PipelineResult(
            slug=plan_obj.slug or image_path.stem,
            status="error",
            layers=[], detection_report={},
            stage_timings=[], manifest_path=output_dir / "manifest.json",
            output_dir=output_dir,
            reason=f"image not found: {image_path}",
        )

    slug = plan_obj.slug or _sanitize_name(image_path.stem)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists() and not force:
        existing = json.loads(manifest_path.read_text())
        return PipelineResult(
            slug=slug, status="skipped",
            layers=existing.get("layers", []),
            detection_report=existing.get("detection_report", {}),
            stage_timings=existing.get("stage_timings", []),
            manifest_path=manifest_path, output_dir=output_dir,
            reason="output exists (force=False)",
        )

    # ── Image loading (safety-checked) ──
    try:
        img_pil = _load_image_safely(image_path)
    except ValueError as e:
        return PipelineResult(
            slug=slug, status="error", layers=[], detection_report={},
            stage_timings=[], manifest_path=manifest_path, output_dir=output_dir,
            reason=f"image_load: {e}",
        )

    # ── v0.18.0: collect labels with multi_instance=True into {label: 8} dict ──
    # 8 = max_instances cap from spec Q4. Empty dict (no opt-in entities) makes
    # the downstream forward a no-op — legacy top-1 behavior preserved.
    multi_instance_labels: dict[str, int] = {
        e.label: 8 for e in plan_obj.entities if getattr(e, "multi_instance", False)
    }

    # ── Delegate to existing script for actual heavy work ──
    # We reuse `claude_orchestrated_pipeline` but redirect its ORIG_DIR and
    # OUT_DIR so it doesn't pollute the repo's showcase assets (fixes part
    # of C1 — MCP no longer needs to shutil.copy into repo).
    cop = _import_cop()

    # Temporarily override the paths in the script module for this call
    saved_orig_dir = cop.ORIG_DIR
    saved_out_dir = cop.OUT_DIR
    saved_plans_dir = cop.PLANS_DIR
    try:
        # Stage inputs into a temp-scoped structure that the script expects
        import tempfile
        with tempfile.TemporaryDirectory(prefix=f"vulca_{slug}_") as td:
            td_path = Path(td)
            staging_orig = td_path / "originals"
            staging_plans = td_path / "plans"
            staging_out = td_path / "out"
            staging_orig.mkdir(parents=True)
            staging_plans.mkdir(parents=True)
            staging_out.mkdir(parents=True)

            # Hard-copy image + plan into staging (symlinks fail on some FS)
            import shutil as _sh
            _sh.copy2(image_path, staging_orig / f"{slug}.jpg")
            (staging_plans / f"{slug}.json").write_text(
                plan_obj.model_dump_json(indent=2)
            )

            cop.ORIG_DIR = staging_orig
            cop.OUT_DIR = staging_out
            cop.PLANS_DIR = staging_plans

            # Invoke the script's process() — it writes to staging_out/{slug}/
            cop.process(slug, force=True, multi_instance_labels=multi_instance_labels)

            # Move results to requested output_dir
            produced = staging_out / slug
            if not produced.exists() or not (produced / "manifest.json").exists():
                return PipelineResult(
                    slug=slug, status="error", layers=[], detection_report={},
                    stage_timings=[StageTiming("total", time.time() - t0).to_dict()],
                    manifest_path=manifest_path, output_dir=output_dir,
                    reason="pipeline produced no manifest",
                )

            # Clear target, copy over
            if output_dir.exists():
                for p in output_dir.iterdir():
                    if p.is_file():
                        p.unlink()
                    elif p.is_dir():
                        _sh.rmtree(p)
            for src in produced.iterdir():
                dest = output_dir / src.name
                if src.is_file():
                    _sh.copy2(src, dest)
    finally:
        cop.ORIG_DIR = saved_orig_dir
        cop.OUT_DIR = saved_out_dir
        cop.PLANS_DIR = saved_plans_dir

    # ── Re-parse manifest, annotate with total time ──
    manifest = json.loads(manifest_path.read_text())
    total_time = time.time() - t0
    manifest["stage_timings"] = [
        {"stage": "total", "seconds": round(total_time, 3)}
    ]
    manifest["manifest_version"] = MANIFEST_VERSION
    _safe_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False))

    dr = manifest.get("detection_report", {})
    success_rate = dr.get("success_rate", 0.0)
    status = manifest.get("status", "unknown")

    if strict and success_rate < SUCCESS_RATE_THRESHOLD:
        raise RuntimeError(
            f"{slug}: partial detection ({success_rate*100:.0f}% < {SUCCESS_RATE_THRESHOLD*100:.0f}%)"
        )

    return PipelineResult(
        slug=slug, status=status,
        layers=manifest.get("layers", []),
        detection_report=dr,
        stage_timings=manifest["stage_timings"],
        manifest_path=manifest_path, output_dir=output_dir,
    )
