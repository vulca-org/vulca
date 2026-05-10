#!/usr/bin/env python3
"""Build the Vulca-only JEPA visual audit sample inventory."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageStat


REPO_ROOT = Path(__file__).resolve().parents[2]
INTERMEDIATE_ARTIFACT_GROUPS = {"layered", "defense"}
NEAR_BLACK_LUMA_MAX = 5.0
LOW_INFORMATION_STDDEV_MAX = 2.0
OPAQUE_ALPHA_COVERAGE_MIN = 0.95


@dataclass(frozen=True)
class SampleSpec:
    sample_id: str
    group: str
    path: str
    purpose: str
    prompt: str = ""
    context: tuple[str, ...] = field(default_factory=tuple)


DEFAULT_SAMPLES: tuple[SampleSpec, ...] = (
    SampleSpec(
        sample_id="gongbi_baseline_failed_subject",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery/chinese_gongbi.png",
        purpose="Baseline failure: prompt asked for gongbi peony, existing VLM rescore says the image is a landscape.",
        prompt="工笔牡丹，细腻勾线，三矾九染",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/gemini-vlm-rescore.json"),
    ),
    SampleSpec(
        sample_id="gongbi_promptfix_seed1",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery-promptfix/chinese_gongbi_seed1.png",
        purpose="Promptfix gongbi peony seed 1; expected to separate from the failed landscape baseline.",
        prompt="single large peony flower, close-up centered botanical portrait, Chinese gongbi",
        context=("assets/demo/v3/e2e-report-gallery-promptfix.json", "assets/demo/v3/gemini-vlm-rescore.json"),
    ),
    SampleSpec(
        sample_id="gongbi_promptfix_seed2",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery-promptfix/chinese_gongbi_seed2.png",
        purpose="Promptfix gongbi peony seed 2; VLM notes weaker subject dominance.",
        prompt="single large peony flower, close-up centered botanical portrait, Chinese gongbi",
        context=("assets/demo/v3/e2e-report-gallery-promptfix.json", "assets/demo/v3/gemini-vlm-rescore.json"),
    ),
    SampleSpec(
        sample_id="gongbi_promptfix_seed3",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery-promptfix/chinese_gongbi_seed3.png",
        purpose="Promptfix gongbi peony seed 3; used for multi-seed stability.",
        prompt="single large peony flower, close-up centered botanical portrait, Chinese gongbi",
        context=("assets/demo/v3/e2e-report-gallery-promptfix.json", "assets/demo/v3/gemini-vlm-rescore.json"),
    ),
    SampleSpec(
        sample_id="xieyi_baseline",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery/chinese_xieyi.png",
        purpose="Positive xieyi landscape baseline; useful nearest-neighbor target for the failed gongbi baseline.",
        prompt="水墨山水，雨后春山，松间茅屋",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/gemini-vlm-rescore.json"),
    ),
    SampleSpec(
        sample_id="xieyi_promptfix",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery-promptfix/chinese_xieyi.png",
        purpose="Promptfix xieyi landscape sample.",
        prompt="traditional Chinese xieyi freehand ink painting, misty mountains after spring rain",
        context=("assets/demo/v3/e2e-report-gallery-promptfix.json",),
    ),
    SampleSpec(
        sample_id="japanese_baseline_failed_style",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery/japanese_traditional.png",
        purpose="Baseline with partial subject/style mismatch in VLM rescore.",
        prompt="京都金閣寺の雪景色、墨絵風",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/gemini-vlm-rescore.json"),
    ),
    SampleSpec(
        sample_id="japanese_promptfix",
        group="gallery_promptfix",
        path="assets/demo/v3/gallery-promptfix/japanese_traditional.png",
        purpose="Promptfix Japanese traditional sample for before/after comparison.",
        prompt="Kinkaku-ji Golden Pavilion, Kyoto, winter snow, sumi-e monochrome ink painting",
        context=("assets/demo/v3/e2e-report-gallery-promptfix.json",),
    ),
    SampleSpec(
        sample_id="western_academic",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/western_academic.png",
        purpose="Western academic or impressionist gallery contrast sample.",
        prompt="Impressionist garden at golden hour, oil on canvas",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/western_academic_scores.json"),
    ),
    SampleSpec(
        sample_id="watercolor",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/watercolor.png",
        purpose="Watercolor medium contrast sample.",
        prompt="English countryside cottage, loose wet-on-wet watercolor",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/watercolor_scores.json"),
    ),
    SampleSpec(
        sample_id="islamic_geometric",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/islamic_geometric.png",
        purpose="Geometric pattern contrast sample.",
        prompt="Alhambra-inspired geometric pattern, turquoise and gold",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/islamic_geometric_scores.json"),
    ),
    SampleSpec(
        sample_id="african_traditional",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/african_traditional.png",
        purpose="Bold pattern and color contrast sample.",
        prompt="Ndebele mural pattern, bold primary colors",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/african_traditional_scores.json"),
    ),
    SampleSpec(
        sample_id="south_asian",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/south_asian.png",
        purpose="Mughal miniature contrast sample.",
        prompt="Mughal miniature, garden scene with lotus pond",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/south_asian_scores.json"),
    ),
    SampleSpec(
        sample_id="brand_design",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/brand_design.png",
        purpose="Product and brand visual contrast sample.",
        prompt="Premium tea packaging, mountain watermark, Eastern aesthetics",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/brand_design_scores.json"),
    ),
    SampleSpec(
        sample_id="photography",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/photography.png",
        purpose="Photography style contrast sample.",
        prompt="Misty mountain landscape at dawn, cinematic",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/photography_scores.json"),
    ),
    SampleSpec(
        sample_id="contemporary_art",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/contemporary_art.png",
        purpose="Abstract contemporary art contrast sample.",
        prompt="Abstract expressionist canvas with bold gestural strokes",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/contemporary_art_scores.json"),
    ),
    SampleSpec(
        sample_id="ui_ux_design",
        group="gallery_breadth",
        path="assets/demo/v3/gallery/ui_ux_design.png",
        purpose="UI image type contrast sample.",
        prompt="Clean dashboard UI mockup with card layout and soft shadows",
        context=("assets/demo/v3/e2e-report.json", "assets/demo/v3/eval-v2merged/ui_ux_design_scores.json"),
    ),
    SampleSpec(
        sample_id="layered_composite",
        group="layered",
        path="assets/demo/v3/layered/composite.png",
        purpose="Layered scene composite for recomposition consistency checks.",
        context=("assets/demo/v3/layered/manifest.json",),
    ),
    SampleSpec(
        sample_id="layer_base_xuan_paper",
        group="layered",
        path="assets/demo/v3/layered/base_xuan_paper.png",
        purpose="Base paper layer for alpha coverage checks.",
        context=("assets/demo/v3/layered/manifest.json",),
    ),
    SampleSpec(
        sample_id="layer_distant_mountains",
        group="layered",
        path="assets/demo/v3/layered/distant_haze_mountains.png",
        purpose="Distant mountain layer for semantic layer consistency checks.",
        context=("assets/demo/v3/layered/manifest.json",),
    ),
    SampleSpec(
        sample_id="layer_midground_river_forest",
        group="layered",
        path="assets/demo/v3/layered/midground_river_forest.png",
        purpose="Midground river and forest layer for duplicate-layer checks.",
        context=("assets/demo/v3/layered/manifest.json",),
    ),
    SampleSpec(
        sample_id="layer_foreground_details_hut",
        group="layered",
        path="assets/demo/v3/layered/foreground_details_hut.png",
        purpose="Foreground details layer for subject-layer retention checks.",
        context=("assets/demo/v3/layered/manifest.json",),
    ),
    SampleSpec(
        sample_id="defense_no_ref_composite",
        group="defense",
        path="assets/demo/v3/defense3/no_ref/composite.png",
        purpose="No-reference defense composite for reference impact comparison.",
        context=("assets/demo/v3/defense3/no_ref/.layered_cache",),
    ),
    SampleSpec(
        sample_id="defense_with_ref_composite",
        group="defense",
        path="assets/demo/v3/defense3/with_ref/composite.png",
        purpose="With-reference defense composite for reference impact comparison.",
        context=("assets/demo/v3/defense3/with_ref/.layered_cache",),
    ),
    SampleSpec(
        sample_id="edit_before",
        group="edit_inpaint",
        path="assets/demo/v3/edit/before.png",
        purpose="Before image for edit drift check.",
    ),
    SampleSpec(
        sample_id="edit_after",
        group="edit_inpaint",
        path="assets/demo/v3/edit/after.png",
        purpose="After image for edit drift check.",
    ),
    SampleSpec(
        sample_id="inpaint_before",
        group="edit_inpaint",
        path="assets/demo/v3/inpaint/before.png",
        purpose="Before image for inpaint drift check.",
    ),
    SampleSpec(
        sample_id="inpaint_after",
        group="edit_inpaint",
        path="assets/demo/v3/inpaint/after.png",
        purpose="After image for inpaint drift check.",
    ),
    SampleSpec(
        sample_id="fusion_source",
        group="fusion",
        path="docs/visual-specs/2026-04-23-scottish-chinese-fusion/source.png",
        purpose="Original Scottish street source image for anchor-preservation checks.",
        context=("docs/visual-specs/2026-04-23-scottish-chinese-fusion/design.md",),
    ),
    SampleSpec(
        sample_id="fusion_iter0",
        group="fusion",
        path="docs/visual-specs/2026-04-23-scottish-chinese-fusion/iters/7/gen_bfbbacd2.png",
        purpose="Accepted iteration 0 output with strict L2 hard-fail and user override.",
        context=(
            "docs/visual-specs/2026-04-23-scottish-chinese-fusion/design.md",
            "docs/visual-specs/2026-04-23-scottish-chinese-fusion/plan.md",
        ),
    ),
)


def _read_image_metadata(path: Path) -> dict[str, int | str | None]:
    if not path.exists():
        return {"width": None, "height": None, "mode": None}
    with Image.open(path) as image:
        return {"width": image.width, "height": image.height, "mode": image.mode}


def analyze_image_quality(path: Path) -> dict[str, float | bool | None]:
    if not path.exists():
        return {
            "luma_mean": None,
            "luma_stddev": None,
            "alpha_coverage": None,
            "near_black_opaque": False,
            "low_information": False,
        }

    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        luma = ImageStat.Stat(rgba.convert("L"))
        alpha = rgba.getchannel("A")
        alpha_histogram = alpha.histogram()
        total_pixels = alpha.width * alpha.height
        alpha_coverage = sum(alpha_histogram[1:]) / total_pixels

    luma_mean = round(float(luma.mean[0]), 2)
    luma_stddev = round(float(luma.stddev[0]), 2)
    alpha_coverage = round(float(alpha_coverage), 4)
    near_black_opaque = luma_mean <= NEAR_BLACK_LUMA_MAX and alpha_coverage >= OPAQUE_ALPHA_COVERAGE_MIN
    low_information = luma_stddev <= LOW_INFORMATION_STDDEV_MAX and alpha_coverage >= OPAQUE_ALPHA_COVERAGE_MIN
    return {
        "luma_mean": luma_mean,
        "luma_stddev": luma_stddev,
        "alpha_coverage": alpha_coverage,
        "near_black_opaque": near_black_opaque,
        "low_information": low_information,
    }


def _classify_sample(group: str, exists: bool, quality: dict[str, float | bool | None]) -> tuple[str, bool, list[str]]:
    reject_reasons: list[str] = []
    if not exists:
        reject_reasons.append("missing_file")
    if group in INTERMEDIATE_ARTIFACT_GROUPS:
        reject_reasons.append("intermediate_artifact")
    if quality["near_black_opaque"]:
        reject_reasons.append("near_black_opaque")
    if quality["low_information"]:
        reject_reasons.append("low_information")

    if reject_reasons:
        return "artifact_qa", False, reject_reasons
    return "core", True, []


def build_inventory(
    repo_root: Path | str | None = None,
    sample_specs: Iterable[SampleSpec] | None = None,
) -> dict[str, object]:
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    root = root.resolve()
    specs = tuple(sample_specs or DEFAULT_SAMPLES)

    samples: list[dict[str, object]] = []
    groups: Counter[str] = Counter()
    audit_sets: Counter[str] = Counter()
    missing_total = 0
    for spec in specs:
        groups[spec.group] += 1
        image_path = root / spec.path
        exists = image_path.exists()
        if not exists:
            missing_total += 1
        metadata = _read_image_metadata(image_path)
        quality = analyze_image_quality(image_path)
        audit_set, usable_for_embedding, reject_reasons = _classify_sample(spec.group, exists, quality)
        audit_sets[audit_set] += 1
        sample = asdict(spec)
        sample["context"] = list(spec.context)
        sample.update(
            {
                "absolute_path": str(image_path),
                "exists": exists,
                **metadata,
                "quality": quality,
                "audit_set": audit_set,
                "usable_for_embedding": usable_for_embedding,
                "reject_reasons": reject_reasons,
            }
        )
        samples.append(sample)

    return {
        "schema_version": "vulca_jepa_inventory.v2",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": str(root),
        "samples_total": len(samples),
        "missing_total": missing_total,
        "groups": dict(groups),
        "audit_sets": dict(audit_sets),
        "samples": samples,
    }


def write_inventory(
    out: Path | str,
    repo_root: Path | str | None = None,
    sample_specs: Iterable[SampleSpec] | None = None,
) -> dict[str, object]:
    output_path = Path(out)
    inventory = build_inventory(repo_root=repo_root, sample_specs=sample_specs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    return inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="Inventory JSON output path.")
    parser.add_argument("--repo-root", default=REPO_ROOT, type=Path, help="Repository root for relative sample paths.")
    parser.add_argument("--allow-missing", action="store_true", help="Exit 0 even if sample files are missing.")
    args = parser.parse_args(argv)

    inventory = write_inventory(args.out, repo_root=args.repo_root)
    print(f"wrote {args.out}")
    print(f"samples: {inventory['samples_total']}")
    print(f"missing: {inventory['missing_total']}")
    print(f"groups: {', '.join(inventory['groups'])}")
    print(f"audit_sets: {', '.join(f'{key}={value}' for key, value in inventory['audit_sets'].items())}")
    if inventory["missing_total"] and not args.allow_missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
