#!/usr/bin/env python3
"""Generate E2E demo artifacts for VULCA.

Implements the phases defined in docs/superpowers/specs/2026-04-10-e2e-readme-rewrite-design.md
against a configurable image provider. Unlike the original Gemini-only spec, this
script can also drive local providers (ComfyUI + Ollama) for zero-cost runs.

Usage:
    # Run Phase 8 (tools, zero API) on a specific input image
    python scripts/generate-e2e-demo.py --phases 8 --input-image path/to/img.png

    # Run Phase 1 (gallery, 13 traditions) via ComfyUI
    VULCA_IMAGE_BASE_URL=http://localhost:8188 \
        python scripts/generate-e2e-demo.py --phases 1 --provider comfyui

    # Both in sequence
    python scripts/generate-e2e-demo.py --phases 1,8 --provider comfyui
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Output layout
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_ROOT = REPO_ROOT / "assets" / "demo" / "v3"
GALLERY_DIR = DEMO_ROOT / "gallery"
TOOLS_DIR = DEMO_ROOT / "tools"
EVAL_DIR = DEMO_ROOT / "eval"
REPORT_PATH = DEMO_ROOT / "e2e-report.json"


# ---------------------------------------------------------------------------
# Phase 1 — Gallery (13 traditions)
# ---------------------------------------------------------------------------
# Tradition → prompt mapping. Uses the 13 actual tradition YAML definitions
# present in src/vulca/cultural/data/traditions/. Prompts match the E2E spec
# where they overlap and are invented for the traditions the spec did not
# cover (contemporary_art, ui_ux_design).
TRADITION_PROMPTS: list[tuple[str, str]] = [
    ("chinese_xieyi", "水墨山水，雨后春山，松间茅屋"),
    ("chinese_gongbi", "工笔牡丹，细腻勾线，三矾九染"),
    ("japanese_traditional", "京都金閣寺の雪景色、墨絵風"),
    ("western_academic", "Impressionist garden at golden hour, oil on canvas"),
    ("watercolor", "English countryside cottage, loose wet-on-wet watercolor"),
    ("islamic_geometric", "Alhambra-inspired geometric pattern, turquoise and gold"),
    ("african_traditional", "Ndebele mural pattern, bold primary colors"),
    ("south_asian", "Mughal miniature, garden scene with lotus pond"),
    ("brand_design", "Premium tea packaging, mountain watermark, Eastern aesthetics"),
    ("photography", "Misty mountain landscape at dawn, cinematic"),
    ("contemporary_art", "Abstract expressionist canvas with bold gestural strokes"),
    ("ui_ux_design", "Clean dashboard UI mockup with card layout and soft shadows"),
    ("default", "Serene landscape with mountains and water"),
]


def _validate_png_bytes(raw: bytes) -> tuple[int, int]:
    """Raise AssertionError unless ``raw`` is a valid PNG >10KB with w,h>0."""
    from PIL import Image

    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "not a valid PNG"
    assert len(raw) > 10_000, f"image too small: {len(raw)} bytes"
    img = Image.open(io.BytesIO(raw))
    assert img.width > 0 and img.height > 0, f"invalid dimensions: {img.size}"
    return img.width, img.height


async def run_phase1_gallery(provider_name: str, *, width: int, height: int) -> dict:
    """Generate one image per tradition, save to ``gallery/{tradition}.png``."""
    from vulca.providers import get_image_provider

    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    provider = get_image_provider(provider_name)

    entries: list[dict] = []
    total_start = time.time()
    for idx, (tradition, prompt) in enumerate(TRADITION_PROMPTS, start=1):
        out_path = GALLERY_DIR / f"{tradition}.png"
        t0 = time.time()
        status = "ok"
        error: str | None = None
        dims: tuple[int, int] | None = None
        size_bytes = 0
        try:
            print(
                f"[{idx:>2}/{len(TRADITION_PROMPTS)}] {tradition} "
                f"via {provider_name}: {prompt}",
                flush=True,
            )
            result = await provider.generate(
                prompt,
                tradition=tradition,
                width=width,
                height=height,
            )
            assert result.image_b64, "provider returned empty image_b64"
            raw = base64.b64decode(result.image_b64)
            size_bytes = len(raw)
            dims = _validate_png_bytes(raw)
            out_path.write_bytes(raw)
        except Exception as exc:
            status = "failed"
            error = f"{type(exc).__name__}: {exc}"
            traceback.print_exc()
        elapsed = time.time() - t0
        entries.append(
            {
                "tradition": tradition,
                "prompt": prompt,
                "status": status,
                "path": str(out_path.relative_to(REPO_ROOT)) if status == "ok" else None,
                "width": dims[0] if dims else None,
                "height": dims[1] if dims else None,
                "size_bytes": size_bytes if status == "ok" else None,
                "elapsed_s": round(elapsed, 2),
                "error": error,
            }
        )
        print(
            f"      → {status} in {elapsed:.1f}s"
            + (f" ({dims[0]}x{dims[1]}, {size_bytes // 1024} KB)" if dims else "")
            + (f" [{error}]" if error else "")
        )

    total_elapsed = time.time() - total_start
    ok_count = sum(1 for e in entries if e["status"] == "ok")
    return {
        "phase": 1,
        "name": "gallery",
        "provider": provider_name,
        "traditions_total": len(TRADITION_PROMPTS),
        "traditions_ok": ok_count,
        "traditions_failed": len(TRADITION_PROMPTS) - ok_count,
        "elapsed_s": round(total_elapsed, 2),
        "entries": entries,
        "status": "ok" if ok_count == len(TRADITION_PROMPTS) else "partial",
    }


# ---------------------------------------------------------------------------
# Phase 8 — Tools (zero API)
# ---------------------------------------------------------------------------
def _pick_phase8_input(explicit: Path | None) -> Path:
    """Resolve which image Phase 8 should analyse.

    Priority:
    1. ``--input-image`` explicit path (resolved relative to repo root if relative)
    2. first successful gallery image from Phase 1 (chinese_xieyi preferred)
    3. raise — Phase 8 cannot run without an input
    """
    if explicit is not None:
        p = explicit if explicit.is_absolute() else (REPO_ROOT / explicit)
        if not p.exists():
            raise FileNotFoundError(f"--input-image not found: {p}")
        return p.resolve()

    if GALLERY_DIR.exists():
        xieyi = GALLERY_DIR / "chinese_xieyi.png"
        if xieyi.exists():
            return xieyi
        for p in sorted(GALLERY_DIR.glob("*.png")):
            return p

    raise FileNotFoundError(
        "Phase 8 needs an input image. Either pass --input-image or run "
        "Phase 1 first so assets/demo/v3/gallery/ has at least one PNG."
    )


def run_phase8_tools(input_image: Path, tradition: str) -> dict:
    """Run brushstroke + composition analyzers on ``input_image`` and write JSON."""
    from vulca.tools.cultural.brushstroke import (
        BrushstrokeAnalyzer,
        BrushstrokeInput,
    )
    from vulca.tools.cultural.composition import (
        CompositionAnalyzer,
        CompositionInput,
    )
    from vulca.tools.protocol import ToolConfig

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    image_bytes = input_image.read_bytes()
    _validate_png_bytes(image_bytes)  # sanity

    config = ToolConfig()

    # --- Brushstroke ---
    brush_result = BrushstrokeAnalyzer().safe_execute(
        BrushstrokeInput(image=image_bytes, tradition=tradition),
        config,
    )
    brush_json = {
        "tool": "brushstroke_analyze",
        "input_image": str(input_image.relative_to(REPO_ROOT)),
        "tradition": tradition,
        "texture_energy": brush_result.texture_energy,
        "uniformity": brush_result.uniformity,
        "dominant_direction": brush_result.dominant_direction,
        "edge_density": brush_result.edge_density,
        "cultural_verdict": brush_result.cultural_verdict,
        "confidence": brush_result.evidence.confidence,
    }
    # Required-key assertions per the spec: "expected keys (energy, confidence, etc.)"
    assert "texture_energy" in brush_json
    assert isinstance(brush_json["texture_energy"], (int, float))
    assert 0.0 <= brush_json["texture_energy"] <= 1.0
    assert 0.0 <= brush_json["confidence"] <= 1.0
    brush_path = TOOLS_DIR / "brushstroke.json"
    brush_path.write_text(json.dumps(brush_json, indent=2, ensure_ascii=False))

    # --- Composition ---
    comp_result = CompositionAnalyzer().safe_execute(
        CompositionInput(image=image_bytes, tradition=tradition),
        config,
    )
    comp_json = {
        "tool": "composition_analyze",
        "input_image": str(input_image.relative_to(REPO_ROOT)),
        "tradition": tradition,
        "center_weight": comp_result.center_weight,
        "thirds_alignment": comp_result.thirds_alignment,
        "visual_center": comp_result.visual_center,
        "balance": comp_result.balance,
        "detected_rules": list(comp_result.detected_rules),
        "cultural_verdict": comp_result.cultural_verdict,
        "confidence": comp_result.evidence.confidence,
    }
    assert 0.0 <= comp_json["center_weight"] <= 1.0
    assert 0.0 <= comp_json["thirds_alignment"] <= 1.0
    assert 0.0 <= comp_json["confidence"] <= 1.0
    assert isinstance(comp_json["detected_rules"], list)
    comp_path = TOOLS_DIR / "composition.json"
    comp_path.write_text(json.dumps(comp_json, indent=2, ensure_ascii=False))

    return {
        "phase": 8,
        "name": "tools",
        "provider": "local-cv2",
        "input_image": str(input_image.relative_to(REPO_ROOT)),
        "tradition": tradition,
        "outputs": [
            str(brush_path.relative_to(REPO_ROOT)),
            str(comp_path.relative_to(REPO_ROOT)),
        ],
        "brushstroke": brush_json,
        "composition": comp_json,
        "status": "ok",
    }


# ---------------------------------------------------------------------------
# Phase 3 — Evaluate (gallery × VLM)
# ---------------------------------------------------------------------------
async def run_phase3_evaluate(*, mode: str = "strict") -> dict:
    """Score every gallery image via the configured VLM (Ollama for local).

    Validates the max_tokens fix at scale: a 13/13 parse-success rate at the
    new 8192 starting budget confirms the truncation issue is fixed.  An
    escalation log line ("VLM response truncated... escalating to") indicates
    8192 is still insufficient for some images.
    """
    # Surface vulca info logs (escalation messages, etc.) to stdout for diagnostics.
    import logging

    vulca_logger = logging.getLogger("vulca")
    if not any(isinstance(h, logging.StreamHandler) for h in vulca_logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("    [vulca] %(message)s"))
        vulca_logger.addHandler(handler)
    vulca_logger.setLevel(logging.INFO)

    from vulca._vlm import score_image

    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    if not GALLERY_DIR.exists() or not any(GALLERY_DIR.glob("*.png")):
        raise FileNotFoundError(
            "Phase 3 needs Phase 1 gallery output. Run --phases 1 first."
        )

    prompt_by_tradition = dict(TRADITION_PROMPTS)
    gallery_images = sorted(GALLERY_DIR.glob("*.png"))

    entries: list[dict] = []
    total_start = time.time()

    for idx, image_path in enumerate(gallery_images, start=1):
        tradition = image_path.stem
        subject = prompt_by_tradition.get(tradition, tradition)
        out_path = EVAL_DIR / f"{tradition}_scores.json"

        print(
            f"[{idx:>2}/{len(gallery_images)}] {tradition}: scoring (subject={subject!r})",
            flush=True,
        )

        t0 = time.time()
        result: dict
        try:
            raw_bytes = image_path.read_bytes()
            img_b64 = base64.b64encode(raw_bytes).decode()
            result = await score_image(
                img_b64,
                "image/png",
                subject,
                tradition,
                "local",
                mode=mode,
            )
        except Exception as exc:
            traceback.print_exc()
            result = {"error": f"{type(exc).__name__}: {exc}"}

        elapsed = time.time() - t0
        parse_ok = "error" not in result

        if parse_ok:
            scores = {f"L{i}": float(result.get(f"L{i}", 0.0)) for i in range(1, 6)}
            risk_flags = result.get("risk_flags", [])
        else:
            scores = None
            risk_flags = []

        entry = {
            "tradition": tradition,
            "subject": subject,
            "image": str(image_path.relative_to(REPO_ROOT)),
            "status": "ok" if parse_ok else "failed",
            "elapsed_s": round(elapsed, 2),
            "scores": scores,
            "risk_flags": risk_flags,
            "error": result.get("error") if not parse_ok else None,
            "result_path": str(out_path.relative_to(REPO_ROOT)),
        }
        entries.append(entry)

        # Persist full result for downstream README rendering. Strip the
        # underscore-prefixed internal keys (_extra_keys, _extra_names) which
        # are runtime hints, not data the README cares about.
        serializable = {k: v for k, v in result.items() if not k.startswith("_")}
        out_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))

        if parse_ok:
            score_str = " ".join(f"{k}={scores[k]:.2f}" for k in ("L1", "L2", "L3", "L4", "L5"))
            print(f"      → ok in {elapsed:.1f}s  {score_str}")
        else:
            print(f"      → FAILED in {elapsed:.1f}s [{result.get('error')}]")

    total_elapsed = time.time() - total_start
    ok_entries = [e for e in entries if e["status"] == "ok"]
    ok_count = len(ok_entries)

    per_dim_mean: dict[str, float] | None
    if ok_entries:
        per_dim_mean = {
            f"L{i}": round(
                sum(e["scores"][f"L{i}"] for e in ok_entries) / len(ok_entries),
                3,
            )
            for i in range(1, 6)
        }
    else:
        per_dim_mean = None

    parse_rate = round(ok_count / len(gallery_images), 3) if gallery_images else 0.0
    elapsed_per_call = (
        round(total_elapsed / len(gallery_images), 1) if gallery_images else 0.0
    )

    return {
        "phase": 3,
        "name": "evaluate",
        "provider": "ollama-gemma4",
        "mode": mode,
        "images_total": len(gallery_images),
        "images_ok": ok_count,
        "images_failed": len(gallery_images) - ok_count,
        "parse_success_rate": parse_rate,
        "elapsed_s": round(total_elapsed, 2),
        "mean_elapsed_per_call_s": elapsed_per_call,
        "per_dim_mean_score": per_dim_mean,
        "entries": entries,
        "status": "ok" if ok_count == len(gallery_images) else "partial",
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
async def main_async(args: argparse.Namespace) -> int:
    phases = sorted({int(p) for p in args.phases.split(",") if p.strip()})
    DEMO_ROOT.mkdir(parents=True, exist_ok=True)
    phase_reports: list[dict] = []
    overall_status = "ok"

    for phase in phases:
        if phase == 1:
            try:
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                )
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 1,
                    "name": "gallery",
                    "provider": args.provider,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 3:
            try:
                rep = await run_phase3_evaluate(mode=args.eval_mode)
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 3,
                    "name": "evaluate",
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 8:
            try:
                input_image = _pick_phase8_input(
                    Path(args.input_image) if args.input_image else None
                )
                rep = run_phase8_tools(input_image, args.phase8_tradition)
            except Exception as exc:
                traceback.print_exc()
                rep = {
                    "phase": 8,
                    "name": "tools",
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        else:
            print(f"[warn] phase {phase} not implemented in this runner")

    # Merge with any existing report so re-running one phase preserves the
    # others' results.  Newer entries replace older ones for the same phase.
    merged: dict[int, dict] = {}
    if REPORT_PATH.exists():
        try:
            prior = json.loads(REPORT_PATH.read_text())
            for entry in prior.get("phases", []):
                if isinstance(entry, dict) and "phase" in entry:
                    merged[int(entry["phase"])] = entry
        except Exception:
            pass
    for entry in phase_reports:
        if isinstance(entry, dict) and "phase" in entry:
            merged[int(entry["phase"])] = entry
    final_phases = [merged[k] for k in sorted(merged.keys())]
    aggregate_status = (
        "ok" if all(p.get("status") == "ok" for p in final_phases) else "partial"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": aggregate_status,
        "phases": final_phases,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print()
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"Overall: {overall_status}")
    return 0 if overall_status == "ok" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phases",
        default="1,8",
        help="Comma-separated phase numbers to run (e.g. '1,8'). Default: 1,8",
    )
    parser.add_argument(
        "--provider",
        default="comfyui",
        help="Image provider for Phase 1 (comfyui | gemini | openai | mock). "
        "Default: comfyui",
    )
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument(
        "--input-image",
        default=None,
        help="Input image path for Phase 8. Default: first gallery PNG.",
    )
    parser.add_argument(
        "--phase8-tradition",
        default="chinese_xieyi",
        help="Tradition hint for Phase 8 cultural analysis. Default: chinese_xieyi",
    )
    parser.add_argument(
        "--eval-mode",
        default="strict",
        choices=("strict", "reference", "fusion"),
        help="VLM evaluation mode for Phase 3. Default: strict",
    )
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
