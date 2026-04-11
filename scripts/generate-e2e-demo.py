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
#
# Each entry carries a positive ``prompt`` and an optional ``negative`` prompt
# (default empty). The experimental-override path (see
# EXPERIMENTAL_PROMPT_OVERRIDES below) can substitute either per tradition
# without mutating this list.
TRADITION_PROMPTS: list[dict] = [
    {"tradition": "chinese_xieyi",        "prompt": "水墨山水，雨后春山，松间茅屋",                                                "negative": ""},
    {"tradition": "chinese_gongbi",       "prompt": "工笔牡丹，细腻勾线，三矾九染",                                                "negative": ""},
    {"tradition": "japanese_traditional", "prompt": "京都金閣寺の雪景色、墨絵風",                                                  "negative": ""},
    {"tradition": "western_academic",     "prompt": "Impressionist garden at golden hour, oil on canvas",                        "negative": ""},
    {"tradition": "watercolor",           "prompt": "English countryside cottage, loose wet-on-wet watercolor",                  "negative": ""},
    {"tradition": "islamic_geometric",    "prompt": "Alhambra-inspired geometric pattern, turquoise and gold",                   "negative": ""},
    {"tradition": "african_traditional",  "prompt": "Ndebele mural pattern, bold primary colors",                                "negative": ""},
    {"tradition": "south_asian",          "prompt": "Mughal miniature, garden scene with lotus pond",                            "negative": ""},
    {"tradition": "brand_design",         "prompt": "Premium tea packaging, mountain watermark, Eastern aesthetics",             "negative": ""},
    {"tradition": "photography",          "prompt": "Misty mountain landscape at dawn, cinematic",                               "negative": ""},
    {"tradition": "contemporary_art",     "prompt": "Abstract expressionist canvas with bold gestural strokes",                  "negative": ""},
    {"tradition": "ui_ux_design",         "prompt": "Clean dashboard UI mockup with card layout and soft shadows",               "negative": ""},
    {"tradition": "default",              "prompt": "Serene landscape with mountains and water",                                 "negative": ""},
]


# ---------------------------------------------------------------------------
# Experimental prompt overrides — see
# docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md
#
# Applied only when --traditions is passed AND the listed tradition is a
# key in this map. Each override replaces the positive prompt, sets a
# negative, and may suppress the provider's auto-appended
# `, {tradition} style` suffix by causing the runner to pass tradition=""
# to provider.generate(). The baseline TRADITION_PROMPTS list is not
# mutated; invocations without --traditions behave exactly as today.
# ---------------------------------------------------------------------------
EXPERIMENTAL_PROMPT_OVERRIDES: dict[str, dict] = {
    "chinese_gongbi": {
        "prompt": (
            "(single large peony flower:1.4), close-up centered botanical "
            "portrait, Chinese gongbi meticulous brush painting, fine ink "
            "outlines, mineral pigments, peony blossom with green leaves, "
            "blank silk background, Chinese court flower-and-bird painting, "
            "museum quality botanical study"
        ),
        "negative": (
            "landscape, scenery, mountain, mountains, distant mountains, "
            "temple, pagoda, building, architecture, pine tree, river, lake, "
            "clouds, misty background, cottage, loose brushstrokes, xieyi, "
            "abstract, photography, impressionist"
        ),
        "suppress_tradition_suffix": True,
    },
    "chinese_xieyi": {
        "prompt": (
            "traditional Chinese xieyi freehand ink painting, misty mountains "
            "after spring rain, pine trees by a thatched cottage, sumi-e style, "
            "monochrome ink on rice paper, expressive loose brushwork, "
            "abundant reserved white space"
        ),
        "negative": (
            "photorealistic, saturated colors, western oil painting, gongbi, "
            "tight line work, peony, botanical portrait"
        ),
        "suppress_tradition_suffix": True,
    },
    "japanese_traditional": {
        "prompt": (
            "(Kinkaku-ji Golden Pavilion:1.3), Kyoto, winter snow, "
            "sumi-e monochrome ink painting, traditional Japanese ink wash "
            "suiboku-ga, minimal brushwork, atmospheric, gold temple "
            "reflecting on pond"
        ),
        "negative": (
            "saturated color, ukiyo-e print, anime, photography, western "
            "painting, cherry blossoms, red bridge, generic pagoda, "
            "snow on trees"
        ),
        "suppress_tradition_suffix": True,
    },
}


def _validate_experimental_overrides() -> None:
    """Fail fast if any EXPERIMENTAL_PROMPT_OVERRIDES key is unknown.

    Guards against silent drift between the override map and
    TRADITION_PROMPTS (e.g., a tradition renamed or removed without the
    override being updated).
    """
    valid = {e["tradition"] for e in TRADITION_PROMPTS}
    invalid = [k for k in EXPERIMENTAL_PROMPT_OVERRIDES if k not in valid]
    if invalid:
        raise SystemExit(
            f"EXPERIMENTAL_PROMPT_OVERRIDES contains unknown traditions: "
            f"{invalid}. Valid names: {sorted(valid)}"
        )


def _validate_png_bytes(raw: bytes) -> tuple[int, int]:
    """Raise AssertionError unless ``raw`` is a valid PNG >10KB with w,h>0."""
    from PIL import Image

    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "not a valid PNG"
    assert len(raw) > 10_000, f"image too small: {len(raw)} bytes"
    img = Image.open(io.BytesIO(raw))
    assert img.width > 0 and img.height > 0, f"invalid dimensions: {img.size}"
    return img.width, img.height


async def run_phase1_gallery(
    provider_name: str,
    *,
    width: int,
    height: int,
    traditions: set[str] | None = None,
    gallery_dir: Path | None = None,
    seeds_map: dict[str, int] | None = None,
) -> dict:
    """Generate one image per tradition, save to ``gallery/{tradition}.png``."""
    from vulca.providers import get_image_provider

    target_dir = gallery_dir if gallery_dir is not None else GALLERY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    provider = get_image_provider(provider_name)

    entries: list[dict] = []
    total_start = time.time()
    selected_entries = (
        [e for e in TRADITION_PROMPTS if e["tradition"] in traditions]
        if traditions is not None
        else list(TRADITION_PROMPTS)
    )
    seeds_map = seeds_map or {}

    # Flatten (entry, seed_idx, seed_count) so the progress counter and
    # entry list are per-image, not per-tradition.
    work: list[tuple[dict, int, int]] = []
    for entry in selected_entries:
        count = seeds_map.get(entry["tradition"], 1)
        for seed_idx in range(1, count + 1):
            work.append((entry, seed_idx, count))

    for idx, (entry, seed_idx, seed_count) in enumerate(work, start=1):
        tradition = entry["tradition"]
        # Resolve override per-tradition. Mixed invocations (some with
        # override, some without) work correctly: each tradition is looked
        # up independently.
        override = EXPERIMENTAL_PROMPT_OVERRIDES.get(tradition)
        if override is not None:
            resolved_prompt = override["prompt"]
            resolved_negative = override["negative"]
            suppress_suffix = bool(override.get("suppress_tradition_suffix", False))
        else:
            resolved_prompt = entry["prompt"]
            resolved_negative = entry.get("negative", "")
            suppress_suffix = False
        # When suppressing the auto-suffix, pass tradition="" to the provider.
        # The file name still uses the real tradition key from the loop.
        tradition_arg = "" if suppress_suffix else tradition

        if seed_count == 1:
            filename = f"{tradition}.png"
        else:
            filename = f"{tradition}_seed{seed_idx}.png"
        out_path = target_dir / filename
        t0 = time.time()
        status = "ok"
        error: str | None = None
        dims: tuple[int, int] | None = None
        size_bytes = 0
        try:
            label = f"{tradition}" if seed_count == 1 else f"{tradition}#seed{seed_idx}"
            override_tag = " [override]" if override is not None else ""
            print(
                f"[{idx:>2}/{len(work)}] {label}{override_tag} "
                f"via {provider_name}: {resolved_prompt[:80]}"
                f"{'...' if len(resolved_prompt) > 80 else ''}",
                flush=True,
            )
            result = await provider.generate(
                resolved_prompt,
                tradition=tradition_arg,
                width=width,
                height=height,
                negative_prompt=resolved_negative,
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
        entry_report = {
            "tradition": tradition,
            "prompt": resolved_prompt,
            "negative": resolved_negative,
            "override_applied": override is not None,
            "tradition_suffix_suppressed": suppress_suffix,
            "status": status,
            "path": str(out_path.relative_to(REPO_ROOT)) if status == "ok" else None,
            "width": dims[0] if dims else None,
            "height": dims[1] if dims else None,
            "size_bytes": size_bytes if status == "ok" else None,
            "elapsed_s": round(elapsed, 2),
            "error": error,
        }
        if seed_count > 1:
            entry_report["seed_index"] = seed_idx
            entry_report["seed_count"] = seed_count
        entries.append(entry_report)
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
        "traditions_total": len(selected_entries),
        "images_total": len(work),
        "images_ok": ok_count,
        "images_failed": len(work) - ok_count,
        "elapsed_s": round(total_elapsed, 2),
        "entries": entries,
        "status": "ok" if ok_count == len(work) else "partial",
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

    prompt_by_tradition = {e["tradition"]: e["prompt"] for e in TRADITION_PROMPTS}
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

    # Scope Phase 1 output and report path to --gallery-subdir when set.
    # Phase 3 and Phase 8 still use the default GALLERY_DIR / REPORT_PATH.
    if args.gallery_subdir:
        scoped_gallery_dir = DEMO_ROOT / args.gallery_subdir
        scoped_report_path = DEMO_ROOT / f"e2e-report-{args.gallery_subdir}.json"
    else:
        scoped_gallery_dir = None  # run_phase1_gallery falls back to GALLERY_DIR
        scoped_report_path = REPORT_PATH

    for phase in phases:
        if phase == 1:
            try:
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                    traditions=args.traditions_set,
                    gallery_dir=scoped_gallery_dir,
                    seeds_map=args.seeds_map,
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
    # When --gallery-subdir is set, merges are scoped to that subdir's own
    # report file — the default e2e-report.json is never touched.
    merged: dict[int, dict] = {}
    if scoped_report_path.exists():
        try:
            prior = json.loads(scoped_report_path.read_text())
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
    scoped_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print()
    print(f"Report: {scoped_report_path.relative_to(REPO_ROOT)}")
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
    parser.add_argument(
        "--traditions",
        default=None,
        help="Comma-separated list of tradition names to regenerate in "
             "Phase 1 (e.g. 'chinese_gongbi,chinese_xieyi'). When unset, "
             "all 13 traditions run. Unknown names fail fast at startup.",
    )
    parser.add_argument(
        "--gallery-subdir",
        default=None,
        help="Subdirectory under assets/demo/v3/ to write Phase 1 gallery "
             "images into (e.g. 'gallery-promptfix'). When set, the Phase "
             "1 report is scoped to e2e-report-<subdir>.json instead of "
             "merging into the default e2e-report.json. Phase 3 and Phase "
             "8 continue reading from the default gallery/ — this flag "
             "only affects Phase 1 output isolation.",
    )
    parser.add_argument(
        "--seeds-per-tradition",
        default=None,
        help="Comma-separated 'tradition:count' pairs (e.g. "
             "'chinese_gongbi:3,japanese_traditional:2'). For each listed "
             "tradition, generate 'count' images with independent random "
             "seeds. Traditions not listed default to 1 image. When "
             "unset, all traditions produce 1 image (existing behavior). "
             "Files with count>1 are named {tradition}_seed{N}.png; "
             "count==1 uses the flat {tradition}.png name.",
    )
    args = parser.parse_args()
    _validate_experimental_overrides()

    # Parse and validate --traditions into a set (or None for "all 13")
    if args.traditions:
        requested = [t.strip() for t in args.traditions.split(",") if t.strip()]
        valid = {e["tradition"] for e in TRADITION_PROMPTS}
        unknown = [t for t in requested if t not in valid]
        if unknown:
            raise SystemExit(
                f"--traditions contains unknown names: {unknown}. "
                f"Valid: {sorted(valid)}"
            )
        args.traditions_set = set(requested)
    else:
        args.traditions_set = None

    # Parse --seeds-per-tradition into {tradition: int}. Missing traditions
    # default to 1 seed at lookup time.
    args.seeds_map = {}
    if args.seeds_per_tradition:
        valid = {e["tradition"] for e in TRADITION_PROMPTS}
        for pair in args.seeds_per_tradition.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" not in pair:
                raise SystemExit(
                    f"--seeds-per-tradition entry {pair!r} must be "
                    f"'tradition:count' (e.g. 'chinese_gongbi:3')"
                )
            name, _, count_s = pair.partition(":")
            name = name.strip()
            if name not in valid:
                raise SystemExit(
                    f"--seeds-per-tradition unknown tradition {name!r}. "
                    f"Valid: {sorted(valid)}"
                )
            try:
                count = int(count_s.strip())
            except ValueError:
                raise SystemExit(
                    f"--seeds-per-tradition count for {name!r} "
                    f"must be an integer, got {count_s!r}"
                )
            if count < 1:
                raise SystemExit(
                    f"--seeds-per-tradition count for {name!r} "
                    f"must be >= 1, got {count}"
                )
            args.seeds_map[name] = count

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
