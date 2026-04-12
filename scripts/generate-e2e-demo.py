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
LAYERED_DIR = DEMO_ROOT / "layered"
DEFENSE3_DIR = DEMO_ROOT / "defense3"
EDIT_DIR = DEMO_ROOT / "edit"
INPAINT_DIR = DEMO_ROOT / "inpaint"
STUDIO_DIR = DEMO_ROOT / "studio"


# ---------------------------------------------------------------------------
# Phase 1 — Gallery (13 traditions)
# ---------------------------------------------------------------------------
# Tradition → prompt mapping. Uses the 13 actual tradition YAML definitions
# present in src/vulca/cultural/data/traditions/. Prompts match the E2E spec
# where they overlap and are invented for the traditions the spec did not
# cover (contemporary_art, ui_ux_design).
#
# Each entry carries a positive ``prompt``, an optional ``negative`` prompt,
# and an optional ``suppress_tradition_suffix`` flag. When the flag is True,
# the runner passes tradition="" to provider.generate() so the provider's
# auto-appended ", {tradition} style" suffix does not compete with the prompt.
#
# The CJK entries (xieyi, gongbi, japanese) use English-first prompts with
# token weighting and explicit negatives — validated by the prompt engineering
# experiment (2026-04-11, spec: docs/superpowers/specs/2026-04-11-...).
TRADITION_PROMPTS: list[dict] = [
    {"tradition": "chinese_xieyi",
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
     "suppress_tradition_suffix": True},
    {"tradition": "chinese_gongbi",
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
     "suppress_tradition_suffix": True},
    {"tradition": "japanese_traditional",
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
     "suppress_tradition_suffix": True},
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
# Prompt overrides — per-tradition prompt/negative substitution for
# future experiments. Empty by default: the canonical prompts now live
# directly in TRADITION_PROMPTS above (backported from the 2026-04-11
# prompt engineering experiment). Kept as scaffolding for future A/B tests.
# ---------------------------------------------------------------------------
EXPERIMENTAL_PROMPT_OVERRIDES: dict[str, dict] = {}


def _validate_experimental_overrides() -> None:
    """Fail fast if any EXPERIMENTAL_PROMPT_OVERRIDES key is unknown."""
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
            suppress_suffix = bool(entry.get("suppress_tradition_suffix", False))
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

    from vulca import aevaluate

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
            eval_result = await aevaluate(
                image_path,
                subject=subject,
                tradition=tradition,
                mode=mode,
            )
            result = {f"L{i}": eval_result.dimensions.get(f"L{i}", 0.0) for i in range(1, 6)}
            result["risk_flags"] = eval_result.risk_flags
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
# Phase 2 — Layered Create
# ---------------------------------------------------------------------------
async def run_phase2_layered(
    provider_name: str,
    *,
    width: int = 1024,
    height: int = 1024,
) -> dict:
    """Generate a layered artwork via the LAYERED pipeline template."""
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import LAYERED
    from vulca.pipeline.types import PipelineInput

    LAYERED_DIR.mkdir(parents=True, exist_ok=True)

    intent = "水墨山水，雨后春山，松间茅屋"
    tradition = "chinese_xieyi"
    subject = "Chinese xieyi ink landscape"

    print(f"[Phase 2] Layered create: {subject} via {provider_name}")
    t0 = time.time()

    try:
        output = await execute(LAYERED, PipelineInput(
            subject=subject,
            intent=intent,
            tradition=tradition,
            provider=provider_name,
            layered=True,
            output_dir=str(LAYERED_DIR),
        ))
    except Exception as exc:
        traceback.print_exc()
        return {
            "phase": 2, "name": "layered", "provider": provider_name,
            "status": "failed", "error": f"{type(exc).__name__}: {exc}",
        }

    elapsed = time.time() - t0
    entries: list[dict] = []
    errors: list[str] = []

    manifest_path = LAYERED_DIR / "manifest.json"
    composite_path = LAYERED_DIR / "composite.png"

    if not manifest_path.exists():
        errors.append("manifest.json missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
            assert "layers" in manifest, "manifest missing 'layers' key"
            assert len(manifest["layers"]) >= 2, f"only {len(manifest['layers'])} layers (need ≥2)"
            entries.append({"artifact": "manifest.json", "layers": len(manifest["layers"]), "status": "ok"})
        except Exception as exc:
            errors.append(f"manifest validation: {exc}")

    if not composite_path.exists():
        errors.append("composite.png missing")
    else:
        try:
            _validate_png_bytes(composite_path.read_bytes())
            entries.append({"artifact": "composite.png", "status": "ok"})
        except Exception as exc:
            errors.append(f"composite validation: {exc}")

    for png_path in sorted(LAYERED_DIR.glob("*.png")):
        if png_path.name == "composite.png":
            continue
        try:
            from PIL import Image
            img = Image.open(png_path)
            assert img.mode == "RGBA", f"{png_path.name} is {img.mode}, expected RGBA"
            assert len(png_path.read_bytes()) > 10_000, f"{png_path.name} too small"
            entries.append({"artifact": png_path.name, "mode": img.mode, "size": img.size, "status": "ok"})
        except Exception as exc:
            errors.append(f"layer {png_path.name}: {exc}")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s ({len(entries)} artifacts validated, {len(errors)} errors)")
    for err in errors:
        print(f"        [error] {err}")

    return {
        "phase": 2, "name": "layered", "provider": provider_name,
        "intent": intent, "tradition": tradition,
        "elapsed_s": round(elapsed, 2),
        "entries": entries, "errors": errors,
        "status": status,
    }


# ---------------------------------------------------------------------------
# Phase 4 — Defense 3 Showcase
# ---------------------------------------------------------------------------
async def run_phase4_defense3(
    provider_name: str,
    *,
    width: int = 1024,
    height: int = 1024,
) -> dict:
    """Compare layered generation with vs. without style-ref anchoring."""
    from vulca.layers.layered_generate import layered_generate
    from vulca.layers.layered_prompt import TraditionAnchor
    from vulca.layers.keying import CanvasSpec
    from vulca.layers.plan_prompt import get_tradition_layer_order
    from vulca.layers.types import LayerInfo
    from vulca.providers import get_image_provider

    DEFENSE3_DIR.mkdir(parents=True, exist_ok=True)
    no_ref_dir = DEFENSE3_DIR / "no_ref"
    with_ref_dir = DEFENSE3_DIR / "with_ref"
    no_ref_dir.mkdir(parents=True, exist_ok=True)
    with_ref_dir.mkdir(parents=True, exist_ok=True)

    tradition = "chinese_xieyi"
    intent = "水墨山水，雨后春山，松间茅屋"

    print(f"[Phase 4] Defense 3 showcase: style-ref comparison via {provider_name}")
    t0 = time.time()

    provider = get_image_provider(provider_name)

    layer_order = get_tradition_layer_order(tradition)
    plan: list[LayerInfo] = []
    for i, lo in enumerate(layer_order[:4]):
        plan.append(LayerInfo(
            name=lo["role"].replace(" ", "_").replace("/", "_"),
            description=lo["role"],
            z_index=i,
            content_type=lo.get("content_type", "subject"),
            blend_mode=lo.get("blend", "normal"),
            tradition_role=lo["role"],
            position=lo.get("position", ""),
            coverage=lo.get("coverage", ""),
            regeneration_prompt=f"{lo['role']} layer for Chinese xieyi ink painting, position: {lo.get('position', 'center')}, coverage: {lo.get('coverage', '30%')}",
        ))

    anchor = TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="white rice paper",
        style_keywords="sumi-e, ink wash, freehand brushwork, monochrome",
    )
    canvas = CanvasSpec.from_hex("#ffffff")

    caps = getattr(provider, "capabilities", frozenset())
    english_only = "multilingual_prompt" not in caps

    entries: list[dict] = []
    errors: list[str] = []

    print("      Running without style-ref (all layers parallel)...")
    try:
        result_no_ref = await layered_generate(
            plan=plan, tradition_anchor=anchor, canvas=canvas,
            key_strategy_name="luminance", provider=provider,
            output_dir=str(no_ref_dir), width=width, height=height,
            english_only=english_only, disable_style_ref=True,
        )
        entries.append({
            "variant": "no_ref",
            "layers_ok": len(result_no_ref.layers),
            "layers_failed": len(result_no_ref.failed),
            "status": "ok" if result_no_ref.is_usable else "failed",
        })
    except Exception as exc:
        traceback.print_exc()
        errors.append(f"no_ref variant: {exc}")

    print("      Running with style-ref (serial-first anchoring)...")
    try:
        result_with_ref = await layered_generate(
            plan=plan, tradition_anchor=anchor, canvas=canvas,
            key_strategy_name="luminance", provider=provider,
            output_dir=str(with_ref_dir), width=width, height=height,
            english_only=english_only, disable_style_ref=False,
        )
        entries.append({
            "variant": "with_ref",
            "layers_ok": len(result_with_ref.layers),
            "layers_failed": len(result_with_ref.failed),
            "status": "ok" if result_with_ref.is_usable else "failed",
        })
    except Exception as exc:
        traceback.print_exc()
        errors.append(f"with_ref variant: {exc}")

    elapsed = time.time() - t0
    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s")

    return {
        "phase": 4, "name": "defense3", "provider": provider_name,
        "intent": intent, "tradition": tradition,
        "elapsed_s": round(elapsed, 2),
        "entries": entries, "errors": errors,
        "status": status,
    }


# ---------------------------------------------------------------------------
# Phase 5 — Edit / Layer Redraw
# ---------------------------------------------------------------------------
async def run_phase5_edit(
    provider_name: str,
) -> dict:
    """Redraw a single layer from the Phase 2 layered artwork."""
    import shutil
    from vulca.layers.redraw import redraw_layer
    from vulca.layers.manifest import load_manifest

    EDIT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_path = LAYERED_DIR / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            "Phase 5 (edit) requires Phase 2 (layered) artifacts. Run --phases 2 first."
        )

    print(f"[Phase 5] Edit/redraw: loading Phase 2 artwork from {LAYERED_DIR}")
    t0 = time.time()

    artwork = load_manifest(str(LAYERED_DIR))

    target_layer = None
    for lr in artwork.layers:
        if lr.info.content_type != "background":
            target_layer = lr
            break
    if target_layer is None and artwork.layers:
        target_layer = artwork.layers[-1]
    if target_layer is None:
        return {"phase": 5, "name": "edit", "provider": provider_name,
                "status": "failed", "error": "No layers found in Phase 2 artwork"}

    print(f"      Redrawing layer: {target_layer.info.name}")

    composite_src = LAYERED_DIR / "composite.png"
    before_path = EDIT_DIR / "before.png"
    if composite_src.exists():
        shutil.copy2(composite_src, before_path)

    instruction = "Redraw with more vibrant autumn colors and a setting sun"
    try:
        result = await redraw_layer(
            artwork, layer_name=target_layer.info.name,
            instruction=instruction, provider=provider_name,
            tradition="chinese_xieyi", artwork_dir=str(LAYERED_DIR),
        )
    except Exception as exc:
        traceback.print_exc()
        return {"phase": 5, "name": "edit", "provider": provider_name,
                "status": "failed", "error": f"{type(exc).__name__}: {exc}"}

    elapsed = time.time() - t0
    errors: list[str] = []

    redrawn_path = EDIT_DIR / "redrawn_layer.png"
    if result.image_path and Path(result.image_path).exists():
        shutil.copy2(result.image_path, redrawn_path)
        from PIL import Image
        img = Image.open(redrawn_path)
        if img.mode != "RGBA":
            errors.append(f"redrawn layer is {img.mode}, expected RGBA")
    else:
        errors.append("redrawn layer image not produced")

    # Recomposite with the redrawn layer swapped in
    after_path = EDIT_DIR / "after.png"
    try:
        from vulca.layers.composite import composite_layers

        # Build updated layer list: swap the redrawn layer into the artwork
        updated_layers = []
        for lr in artwork.layers:
            if lr.info.name == target_layer.info.name and result.image_path:
                from vulca.layers.types import LayerResult as LR
                updated_layers.append(LR(
                    info=lr.info, image_path=result.image_path, scores=lr.scores,
                ))
            else:
                updated_layers.append(lr)
        composite_layers(updated_layers, output_path=str(after_path))
    except Exception as exc:
        # Fallback: copy original composite if recomposite fails
        if composite_src.exists():
            shutil.copy2(composite_src, after_path)
        errors.append(f"recomposite failed: {exc}")

    if before_path.exists() and after_path.exists():
        if before_path.read_bytes() == after_path.read_bytes():
            errors.append("after.png identical to before.png — redraw may not have taken effect")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s")
    for err in errors:
        print(f"        [error] {err}")

    return {"phase": 5, "name": "edit", "provider": provider_name,
            "layer_redrawn": target_layer.info.name, "instruction": instruction,
            "elapsed_s": round(elapsed, 2), "errors": errors, "status": status}


# ---------------------------------------------------------------------------
# Phase 6 — Inpaint
# ---------------------------------------------------------------------------
async def run_phase6_inpaint(
    provider_name: str,
) -> dict:
    """Inpaint a region of a Phase 1 gallery image."""
    import shutil
    from vulca.inpaint import ainpaint

    INPAINT_DIR.mkdir(parents=True, exist_ok=True)

    input_image = GALLERY_DIR / "chinese_xieyi.png"
    if not input_image.exists():
        if GALLERY_DIR.exists():
            for p in sorted(GALLERY_DIR.glob("*.png")):
                input_image = p
                break
    if not input_image.exists():
        raise FileNotFoundError(
            "Phase 6 (inpaint) requires Phase 1 gallery artifacts. Run --phases 1 first."
        )

    print(f"[Phase 6] Inpaint: {input_image.name} via {provider_name}")
    t0 = time.time()

    before_path = INPAINT_DIR / "before.png"
    shutil.copy2(input_image, before_path)

    instruction = "Add a small red pavilion near the water"
    region = "center 30%"

    try:
        result = await ainpaint(
            str(input_image), region=region, instruction=instruction,
            tradition="chinese_xieyi", provider=provider_name,
            count=1, select=0, output=str(INPAINT_DIR / "after.png"),
        )
    except Exception as exc:
        traceback.print_exc()
        return {"phase": 6, "name": "inpaint", "provider": provider_name,
                "status": "failed", "error": f"{type(exc).__name__}: {exc}"}

    elapsed = time.time() - t0
    errors: list[str] = []

    after_path = INPAINT_DIR / "after.png"
    if result.blended and Path(result.blended).exists():
        if str(after_path) != result.blended:
            shutil.copy2(result.blended, after_path)
    elif not after_path.exists():
        errors.append("after.png not produced")

    if before_path.exists() and after_path.exists():
        from PIL import Image
        before_img = Image.open(before_path)
        after_img = Image.open(after_path)
        if before_img.size != after_img.size:
            errors.append(f"dimension mismatch: before={before_img.size}, after={after_img.size}")
        if before_path.read_bytes() == after_path.read_bytes():
            errors.append("after.png identical to before.png")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s")
    for err in errors:
        print(f"        [error] {err}")

    return {"phase": 6, "name": "inpaint", "provider": provider_name,
            "instruction": instruction, "region": region,
            "elapsed_s": round(elapsed, 2), "errors": errors, "status": status}


# ---------------------------------------------------------------------------
# Phase 7 — Studio
# ---------------------------------------------------------------------------
async def run_phase7_studio(
    provider_name: str,
) -> dict:
    """Run a brief-driven studio session in auto mode."""
    from vulca.studio.interactive import run_studio

    STUDIO_DIR.mkdir(parents=True, exist_ok=True)

    intent = (
        "Create a serene Chinese landscape with mountains emerging from "
        "morning mist, in the style of Chinese xieyi ink painting"
    )

    print(f"[Phase 7] Studio session: auto mode via {provider_name}")
    t0 = time.time()

    try:
        session = await asyncio.wait_for(
            asyncio.to_thread(
                run_studio, intent,
                project_dir=str(STUDIO_DIR), provider=provider_name,
                auto=True, max_rounds=3,
            ),
            timeout=900,  # 15-min safety net (studio can take 10+ min on MPS)
        )
    except asyncio.TimeoutError:
        return {"phase": 7, "name": "studio", "provider": provider_name,
                "status": "failed", "error": "Studio session timed out after 900s"}
    except Exception as exc:
        traceback.print_exc()
        return {"phase": 7, "name": "studio", "provider": provider_name,
                "status": "failed", "error": f"{type(exc).__name__}: {exc}"}

    elapsed = time.time() - t0
    errors: list[str] = []

    # Studio writes to subdirectories: concepts/, output/, refs/
    concepts_dir = STUDIO_DIR / "concepts"
    output_dir = STUDIO_DIR / "output"

    concept_pngs = sorted(concepts_dir.glob("*.png")) if concepts_dir.exists() else []
    if not concept_pngs:
        # Fallback: check root dir
        concept_pngs = sorted(STUDIO_DIR.glob("*.png"))
    if not concept_pngs:
        errors.append("no concept PNGs produced")

    # Final output is the last round's render
    output_pngs = sorted(output_dir.glob("*.png")) if output_dir.exists() else []
    final_path = STUDIO_DIR / "final.png"
    if output_pngs:
        import shutil
        shutil.copy2(output_pngs[-1], final_path)
    elif concept_pngs:
        import shutil
        shutil.copy2(concept_pngs[-1], final_path)
    else:
        errors.append("final.png not produced")

    if final_path.exists():
        try:
            _validate_png_bytes(final_path.read_bytes())
        except Exception as exc:
            errors.append(f"final.png validation: {exc}")

    # Session log: studio writes session.yaml or session.json
    session_path = STUDIO_DIR / "session.json"
    session_yaml = STUDIO_DIR / "session.yaml"
    if isinstance(session, dict):
        session_path.write_text(json.dumps(session, indent=2, ensure_ascii=False, default=str))
    elif session_yaml.exists() and not session_path.exists():
        # Convert YAML session to JSON for report consistency
        try:
            import yaml
            data = yaml.safe_load(session_yaml.read_text())
            session_path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        except Exception:
            pass
    if not session_path.exists():
        errors.append("session.json not produced")

    if session_path.exists():
        try:
            data = json.loads(session_path.read_text())
            assert isinstance(data, dict), "session.json is not a dict"
        except Exception as exc:
            errors.append(f"session.json validation: {exc}")

    status = "ok" if not errors else "partial"
    print(f"      → {status} in {elapsed:.1f}s ({len(concept_pngs)} concepts)")
    for err in errors:
        print(f"        [error] {err}")

    return {"phase": 7, "name": "studio", "provider": provider_name,
            "intent": intent, "concepts_produced": len(concept_pngs),
            "elapsed_s": round(elapsed, 2), "errors": errors, "status": status}


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
        elif phase == 2:
            try:
                rep = await run_phase2_layered(
                    args.provider, width=args.width, height=args.height,
                )
            except Exception as exc:
                traceback.print_exc()
                rep = {"phase": 2, "name": "layered", "provider": args.provider,
                       "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 4:
            try:
                rep = await run_phase4_defense3(
                    args.provider, width=args.width, height=args.height,
                )
            except Exception as exc:
                traceback.print_exc()
                rep = {"phase": 4, "name": "defense3", "provider": args.provider,
                       "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 5:
            try:
                rep = await run_phase5_edit(args.provider)
            except Exception as exc:
                traceback.print_exc()
                rep = {"phase": 5, "name": "edit", "provider": args.provider,
                       "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 6:
            try:
                rep = await run_phase6_inpaint(args.provider)
            except Exception as exc:
                traceback.print_exc()
                rep = {"phase": 6, "name": "inpaint", "provider": args.provider,
                       "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            phase_reports.append(rep)
            if rep["status"] != "ok":
                overall_status = "partial"
        elif phase == 7:
            try:
                rep = await run_phase7_studio(args.provider)
            except Exception as exc:
                traceback.print_exc()
                rep = {"phase": 7, "name": "studio", "provider": args.provider,
                       "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
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
