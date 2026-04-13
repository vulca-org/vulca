#!/usr/bin/env python3
"""Produce display-quality composite images for the README from v3 E2E artifacts.

Usage:
    python scripts/make-readme-assets.py              # build all 5
    python scripts/make-readme-assets.py --only gallery,inpaint
    python scripts/make-readme-assets.py --check      # verify inputs exist
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "assets" / "demo" / "v3" / "gallery"
LAYERED = ROOT / "assets" / "demo" / "v3" / "layered"
INPAINT = ROOT / "assets" / "demo" / "v3" / "inpaint"
OUT = ROOT / "assets" / "demo" / "v3" / "readme"

# ---------------------------------------------------------------------------
# Font helper
# ---------------------------------------------------------------------------

def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ---------------------------------------------------------------------------
# Checkerboard helper (shows alpha)
# ---------------------------------------------------------------------------

def _checkerboard(size: int, cell: int = 8) -> Image.Image:
    img = Image.new("RGB", (size, size), (200, 200, 200))
    draw = ImageDraw.Draw(img)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            if (x // cell + y // cell) % 2 == 0:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(240, 240, 240))
    return img


def _thumb_on_checker(img: Image.Image, size: int) -> Image.Image:
    """Resize image to size x size and composite onto checkerboard."""
    checker = _checkerboard(size)
    thumb = img.convert("RGBA").resize((size, size), Image.LANCZOS)
    checker.paste(thumb, (0, 0), thumb)
    return checker


# ---------------------------------------------------------------------------
# Tradition name helper
# ---------------------------------------------------------------------------

def _label(filename: str) -> str:
    return filename.replace(".png", "").replace("_", " ").title()


# ---------------------------------------------------------------------------
# 1. gallery_strip.png
# ---------------------------------------------------------------------------

STRIP_NAMES = [
    "chinese_xieyi", "japanese_traditional", "watercolor",
    "islamic_geometric", "african_traditional",
]


def build_gallery_strip() -> Path | None:
    thumb_size, gap = 200, 8
    imgs: list[Image.Image] = []
    for name in STRIP_NAMES:
        p = GALLERY / f"{name}.png"
        if not p.exists():
            print(f"  WARNING: missing {p}, skipping gallery_strip")
            return None
        imgs.append(Image.open(p).convert("RGB").resize((thumb_size, thumb_size), Image.LANCZOS))

    w = thumb_size * len(imgs) + gap * (len(imgs) - 1)
    canvas = Image.new("RGB", (w, thumb_size), (255, 255, 255))
    x = 0
    for img in imgs:
        canvas.paste(img, (x, 0))
        x += thumb_size + gap
    out = OUT / "gallery_strip.png"
    canvas.save(out)
    print(f"  -> {out}  ({canvas.size[0]}x{canvas.size[1]})")
    return out


# ---------------------------------------------------------------------------
# 2. layered_exploded.png
# ---------------------------------------------------------------------------

LAYER_FILES = [
    "base_paper_texture.png",
    "distant_mist_mountains.png",
    "midground_forest_and_peaks.png",
    "signature_and_seal.png",
]

LAYER_LABELS = ["Paper texture", "Mist mountains", "Pine forest", "Signature"]


def build_layered_exploded() -> Path | None:
    tile = 160
    gap = 16
    arrow_w = 30
    label_h = 30
    bg_color = (45, 45, 45)
    font = _font(12)

    # Load layers
    layers: list[Image.Image] = []
    for f in LAYER_FILES:
        p = LAYERED / f
        if not p.exists():
            print(f"  WARNING: missing {p}, skipping layered_exploded")
            return None
        layers.append(Image.open(p).convert("RGBA"))

    # Build manual composite
    comp = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    for layer in layers:
        comp = Image.alpha_composite(comp, layer)
    composite_rgb = comp.convert("RGB")

    # 4 layers + 3 arrows + 1 equals + composite = 5 tiles, 3 arrows, 1 equals
    n_tiles = len(layers) + 1  # 4 layers + 1 composite
    n_arrows = len(layers) - 1  # 3 arrows between layers
    n_equals = 1  # equals sign before composite

    w = gap + n_tiles * (tile + gap) + n_arrows * (arrow_w + gap) + n_equals * (arrow_w + gap)
    h = gap + tile + label_h + gap

    canvas = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(canvas)

    x = gap
    for i, (layer_img, label) in enumerate(zip(layers, LAYER_LABELS)):
        # Tile on checkerboard
        thumb = _thumb_on_checker(layer_img, tile)
        canvas.paste(thumb, (x, gap))
        # Label
        tw, _ = _text_size(draw, label, font)
        draw.text((x + (tile - tw) // 2, gap + tile + 4), label, fill=(255, 255, 255), font=font)
        x += tile + gap

        # Arrow or equals
        if i < len(layers) - 1:
            # Right arrow
            ay = gap + tile // 2
            draw.text((x + 4, ay - 8), "\u2192", fill=(180, 180, 180), font=_font(18))
            x += arrow_w + gap
        else:
            # Equals before composite
            ay = gap + tile // 2
            draw.text((x + 4, ay - 8), "=", fill=(180, 180, 180), font=_font(18))
            x += arrow_w + gap

    # Composite tile
    comp_thumb = composite_rgb.resize((tile, tile), Image.LANCZOS)
    canvas.paste(comp_thumb, (x, gap))
    clabel = "Composite"
    tw, _ = _text_size(draw, clabel, font)
    draw.text((x + (tile - tw) // 2, gap + tile + 4), clabel, fill=(255, 255, 255), font=font)

    out = OUT / "layered_exploded.png"
    canvas.save(out)
    print(f"  -> {out}  ({canvas.size[0]}x{canvas.size[1]})")
    return out


# ---------------------------------------------------------------------------
# 3. inpaint_comparison.png
# ---------------------------------------------------------------------------

def build_inpaint_comparison() -> Path | None:
    size, gap_x, label_h = 400, 40, 40
    arrow_w = 40
    font = _font(14)

    before_p = INPAINT / "before.png"
    after_p = INPAINT / "after.png"
    for p in (before_p, after_p):
        if not p.exists():
            print(f"  WARNING: missing {p}, skipping inpaint_comparison")
            return None

    before = Image.open(before_p).convert("RGB").resize((size, size), Image.LANCZOS)
    after = Image.open(after_p).convert("RGBA")
    # Composite RGBA onto white
    white = Image.new("RGBA", after.size, (255, 255, 255, 255))
    after = Image.alpha_composite(white, after).convert("RGB").resize((size, size), Image.LANCZOS)

    w = size * 2 + gap_x + arrow_w
    h = label_h + size
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Labels
    l1 = "Original"
    l2 = "After (pavilion inpainted)"
    tw1, _ = _text_size(draw, l1, font)
    tw2, _ = _text_size(draw, l2, font)
    draw.text(((size - tw1) // 2, 8), l1, fill=(0, 0, 0), font=font)
    x2 = size + gap_x + arrow_w
    draw.text((x2 + (size - tw2) // 2, 8), l2, fill=(0, 0, 0), font=font)

    # Images
    canvas.paste(before, (0, label_h))
    canvas.paste(after, (x2, label_h))

    # Arrow
    ay = label_h + size // 2
    ax = size + 8
    draw.text((ax + 4, ay - 10), "\u2192", fill=(100, 100, 100), font=_font(20))

    out = OUT / "inpaint_comparison.png"
    canvas.save(out)
    print(f"  -> {out}  ({canvas.size[0]}x{canvas.size[1]})")
    return out


# ---------------------------------------------------------------------------
# 4. tradition_grid.png
# ---------------------------------------------------------------------------

def build_tradition_grid() -> Path | None:
    tile, gap, label_h = 180, 12, 22
    font = _font(11)
    cols = 5

    files = sorted(GALLERY.glob("*.png"))
    if not files:
        print("  WARNING: no gallery images found, skipping tradition_grid")
        return None

    rows = (len(files) + cols - 1) // cols
    w = cols * tile + (cols - 1) * gap
    h = rows * (tile + label_h) + (rows - 1) * gap

    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for idx, fp in enumerate(files):
        r, c = divmod(idx, cols)
        x = c * (tile + gap)
        y = r * (tile + label_h + gap)
        img = Image.open(fp).convert("RGB").resize((tile, tile), Image.LANCZOS)
        canvas.paste(img, (x, y))
        label = _label(fp.name)
        tw, _ = _text_size(draw, label, font)
        lx = x + (tile - tw) // 2
        draw.text((lx, y + tile + 2), label, fill=(60, 60, 60), font=font)

    out = OUT / "tradition_grid.png"
    canvas.save(out)
    print(f"  -> {out}  ({canvas.size[0]}x{canvas.size[1]})")
    return out


# ---------------------------------------------------------------------------
# 5. gallery_hero.png
# ---------------------------------------------------------------------------

HERO_NAMES = ["chinese_xieyi", "japanese_traditional", "brand_design"]


def build_gallery_hero() -> Path | None:
    size, gap = 300, 12
    font = _font(12)

    imgs: list[Image.Image] = []
    for name in HERO_NAMES:
        p = GALLERY / f"{name}.png"
        if not p.exists():
            print(f"  WARNING: missing {p}, skipping gallery_hero")
            return None
        imgs.append(Image.open(p).convert("RGB").resize((size, size), Image.LANCZOS))

    w = size * len(imgs) + gap * (len(imgs) - 1)
    canvas = Image.new("RGB", (w, size), (255, 255, 255))
    x = 0
    for img in imgs:
        canvas.paste(img, (x, 0))
        x += size + gap
    out = OUT / "gallery_hero.png"
    canvas.save(out)
    print(f"  -> {out}  ({canvas.size[0]}x{canvas.size[1]})")
    return out


# ---------------------------------------------------------------------------
# Registry & CLI
# ---------------------------------------------------------------------------

BUILDERS: dict[str, callable] = {
    "gallery": build_gallery_strip,
    "layered": build_layered_exploded,
    "inpaint": build_inpaint_comparison,
    "grid": build_tradition_grid,
    "hero": build_gallery_hero,
}


def check_inputs() -> bool:
    ok = True
    needed = (
        [(GALLERY / f"{n}.png") for n in STRIP_NAMES]
        + [(LAYERED / f) for f in LAYER_FILES]
        + [INPAINT / "before.png", INPAINT / "after.png"]
        + [(GALLERY / f"{n}.png") for n in HERO_NAMES]
    )
    for p in needed:
        if p.exists():
            print(f"  OK   {p.relative_to(ROOT)}")
        else:
            print(f"  MISS {p.relative_to(ROOT)}")
            ok = False
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Build README display images from v3 artifacts")
    parser.add_argument("--only", help="Comma-separated subset: gallery,layered,inpaint,grid,hero")
    parser.add_argument("--check", action="store_true", help="Only verify input files exist")
    args = parser.parse_args()

    if args.check:
        ok = check_inputs()
        sys.exit(0 if ok else 1)

    OUT.mkdir(parents=True, exist_ok=True)

    targets = list(BUILDERS.keys())
    if args.only:
        targets = [t.strip() for t in args.only.split(",")]
        bad = [t for t in targets if t not in BUILDERS]
        if bad:
            print(f"ERROR: unknown targets: {bad}")
            sys.exit(1)

    results: dict[str, Path | None] = {}
    for name in targets:
        print(f"Building {name} ...")
        results[name] = BUILDERS[name]()

    built = sum(1 for v in results.values() if v is not None)
    skipped = sum(1 for v in results.values() if v is None)
    print(f"\nDone: {built} built, {skipped} skipped")


if __name__ == "__main__":
    main()
