"""Render 6-slide γ Scottish carousel for XHS / dev.to / X.

All slides 1080×1080 square for XHS carousel cohesion. Run from repo root.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/yhryzy/dev/vulca/docs/visual-specs/2026-04-23-scottish-chinese-fusion")
OUT = ROOT / "carousel"
SIZE = 1080

# ---------- font ----------
def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

FONT_TITLE = _load_font(56)
FONT_SUB = _load_font(36)
FONT_BODY = _load_font(28)
FONT_LABEL = _load_font(24)
FONT_MONO = _load_font(22)

WHITE = (252, 248, 240)  # warm cream like 熟绢
INK = (32, 30, 28)
RED = (180, 50, 50)
GOLD = (192, 144, 80)
MUTED = (130, 124, 116)


def _square_canvas(bg=WHITE) -> Image.Image:
    return Image.new("RGB", (SIZE, SIZE), bg)


def _fit_inside(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    img = img.copy()
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img


def _checkerboard(w: int, h: int, cell: int = 16) -> Image.Image:
    bg = Image.new("RGB", (w, h), (240, 240, 240))
    d = ImageDraw.Draw(bg)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                d.rectangle([x, y, x + cell, y + cell], fill=(220, 220, 220))
    return bg


def _draw_text_centered(d: ImageDraw.ImageDraw, text: str, y: int, font, fill=INK, max_width=SIZE):
    bbox = d.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    d.text(((SIZE - w) // 2, y), text, font=font, fill=fill)


def _paste_centered(canvas: Image.Image, img: Image.Image, y: int):
    x = (SIZE - img.width) // 2
    canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)


# =================================================================
# Slide 1 — Naive API vs Vulca-mediated
# =================================================================
def slide1():
    canvas = _square_canvas()
    d = ImageDraw.Draw(canvas)
    _draw_text_centered(d, "Same gpt-image-2 API.", 64, FONT_TITLE, fill=INK)
    _draw_text_centered(d, "Two totally different results.", 124, FONT_TITLE, fill=RED)

    # Two image columns
    src = Image.open(ROOT / "source.png").convert("RGB")
    bare = Image.open(ROOT / "iters/_baseline_bare/bare_gpt2_edit.png").convert("RGB")
    vulca = Image.open(ROOT / "iters/7/gen_bfbbacd2.png").convert("RGB")

    col_w = 510
    col_h = 700
    bare_thumb = _fit_inside(bare, col_w, col_h)
    vulca_thumb = _fit_inside(vulca, col_w, col_h)

    left_x = 30 + (col_w - bare_thumb.width) // 2
    right_x = 540 + (col_w - vulca_thumb.width) // 2
    canvas.paste(bare_thumb, (left_x, 220))
    canvas.paste(vulca_thumb, (right_x, 220))

    _draw_text_centered_at(d, "Naive API call", 940, FONT_SUB, INK, x_left=30, x_right=540)
    _draw_text_centered_at(d, "Vulca-mediated", 940, FONT_SUB, RED, x_left=540, x_right=1050)

    _draw_text_centered(d, "The difference is 3 markdown files: proposal · design · plan", 1018, FONT_BODY, fill=GOLD)

    canvas.save(OUT / "slide1.png", "PNG", optimize=True)


def _draw_text_centered_at(d, text, y, font, fill, x_left=0, x_right=SIZE):
    bbox = d.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = x_left + ((x_right - x_left) - w) // 2
    d.text((x, y), text, font=font, fill=fill)


# =================================================================
# Slide 2 — Hero (iter0 main)
# =================================================================
def slide2():
    canvas = _square_canvas()
    d = ImageDraw.Draw(canvas)
    hero = Image.open(ROOT / "iters/7/gen_bfbbacd2.png").convert("RGB")
    hero = _fit_inside(hero, 960, 880)
    _paste_centered(canvas, hero, 80)
    _draw_text_centered(d, "Glasgow street + Northern Song gongbi additive overlay", 990, FONT_BODY, INK)
    _draw_text_centered(d, "Vulca-mediated  ·  openai/gpt-image-2  ·  seed=7  ·  v0.17.12", 1028, FONT_LABEL, MUTED)
    canvas.save(OUT / "slide2.png", "PNG", optimize=True)


# =================================================================
# Slide 3 — 9-layer decompose grid + residual
# =================================================================
def slide3():
    canvas = _square_canvas()
    d = ImageDraw.Draw(canvas)
    _draw_text_centered(d, "1 image → 10 editable semantic layers", 56, FONT_TITLE, INK)
    _draw_text_centered(d, "YOLO + Grounding DINO + SAM + SegFormer · success_rate 1.0", 130, FONT_LABEL, MUTED)

    iter1 = ROOT / "decompose" / "iter1"
    layer_names = [
        "person", "lanterns", "sign_top",
        "sign_right", "spire", "bus",
        "left_buildings", "right_buildings", "sky",
    ]
    # Source: detection_report.per_entity[*].pct_after_resolve from manifest.json
    # Residual = 100 - sum(pct_after_resolve) = 31.53% (deduped accounting)
    pcts = {
        "person": "5.65%", "lanterns": "8.05%", "sign_top": "1.17%",
        "sign_right": "0.47%", "spire": "2.08%", "bus": "3.59%",
        "left_buildings": "24.45%", "right_buildings": "7.51%", "sky": "15.50%",
    }

    cell_w, cell_h = 300, 240
    grid_x0, grid_y0 = 60, 180
    pad_x, pad_y = 20, 24

    for idx, name in enumerate(layer_names):
        row, col = divmod(idx, 3)
        cx = grid_x0 + col * (cell_w + pad_x)
        cy = grid_y0 + row * (cell_h + pad_y)

        # checkerboard backdrop + layer composite
        layer = Image.open(iter1 / f"{name}.png").convert("RGBA")
        thumb = _fit_inside(layer, cell_w, cell_h - 40)
        cb = _checkerboard(thumb.width, thumb.height)
        cb.paste(thumb, (0, 0), thumb)
        canvas.paste(cb, (cx + (cell_w - thumb.width) // 2, cy))

        # label band
        label = f"{name}  ·  {pcts[name]}"
        bbox = d.textbbox((0, 0), label, font=FONT_LABEL)
        lw = bbox[2] - bbox[0]
        d.text((cx + (cell_w - lw) // 2, cy + cell_h - 32), label, font=FONT_LABEL, fill=INK)

    _draw_text_centered(d, "9 entities cover ~68% of canvas  ·  residual ~31.5% (shadows / awning / road)", 1028, FONT_LABEL, MUTED)
    canvas.save(OUT / "slide3.png", "PNG", optimize=True)


# =================================================================
# Slide 4 — lanterns alpha-iso vs gpt-image-2 redraw
# =================================================================
def slide4():
    canvas = _square_canvas()
    d = ImageDraw.Draw(canvas)
    _draw_text_centered(d, "Same layer, two paths", 56, FONT_TITLE, INK)
    _draw_text_centered(d, '"朱砂 +15%, 三矾九染 depth richer"', 124, FONT_SUB, RED)

    before = Image.open(ROOT / "decompose/lanterns_before.png").convert("RGBA")
    after = Image.open(ROOT / "decompose/lanterns_after.png").convert("RGBA")

    half_w = 480
    half_h = 720

    before_thumb = _fit_inside(before, half_w, half_h)
    cb_b = _checkerboard(before_thumb.width, before_thumb.height)
    cb_b.paste(before_thumb, (0, 0), before_thumb)
    canvas.paste(cb_b, (40 + (half_w - cb_b.width) // 2, 220))

    after_thumb = _fit_inside(after.convert("RGB"), half_w, half_h)
    canvas.paste(after_thumb, (560 + (half_w - after_thumb.width) // 2, 220))

    _draw_text_centered_at(d, "alpha-isolated", 950, FONT_SUB, INK, x_left=40, x_right=520)
    _draw_text_centered_at(d, "gpt-image-2 + gongbi prompt", 950, FONT_SUB, RED, x_left=560, x_right=1040)

    _draw_text_centered_at(d, "lantern silhouettes preserved", 990, FONT_LABEL, MUTED, x_left=40, x_right=520)
    _draw_text_centered_at(d, "reinterpretation, not preservation", 990, FONT_LABEL, MUTED, x_left=560, x_right=1040)

    _draw_text_centered(d, "Vulca exposes both paths via MCP — agent picks per intent", 1030, FONT_LABEL, MUTED)
    canvas.save(OUT / "slide4.png", "PNG", optimize=True)


# =================================================================
# Slide 5 — L1-L5 scorecard
# =================================================================
def slide5():
    """Verdict-trail slide — narrates plan.md's actual record, not a fabricated scorecard."""
    canvas = _square_canvas()
    d = ImageDraw.Draw(canvas)
    _draw_text_centered(d, "plan.md verdict trail", 56, FONT_TITLE, INK)
    _draw_text_centered(d, "iter 0  ·  seed 7  ·  V1-calibration  ·  openai/gpt-image-2", 130, FONT_LABEL, MUTED)

    # Score row — single line, plan.md canonical numbers (0.78/0.65/0.72/0.75/0.65).
    # Render via segment-by-segment positioning so we can color L2 distinctly.
    score_y = 215
    segments = [
        ("L1 0.78", INK),
        ("    ", INK),
        ("L2 0.65", RED),       # hard-fail dimension, color-coded
        ("    ", INK),
        ("L3 0.72", INK),
        ("    ", INK),
        ("L4 0.75", INK),
        ("    ", INK),
        ("L5 0.65", INK),
    ]
    full_text = "".join(s for s, _ in segments)
    full_w = d.textbbox((0, 0), full_text, font=FONT_BODY)[2]
    sx = (SIZE - full_w) // 2
    cursor = sx
    for seg, color in segments:
        d.text((cursor, score_y), seg, font=FONT_BODY, fill=color)
        cursor += d.textbbox((0, 0), seg, font=FONT_BODY)[2]

    _draw_text_centered(d, "weighted total = 0.702", score_y + 60, FONT_BODY, GOLD)

    # Verdict ladder — vertical flow showing the dual-judgment trail
    ladder_y = 360
    _draw_text_centered(d, "strict-rubric verdict",  ladder_y,           FONT_LABEL, MUTED)
    _draw_text_centered(d, "reject",                 ladder_y + 36,      FONT_SUB,   RED)
    _draw_text_centered(d, "↓",                      ladder_y + 92,      FONT_SUB,   GOLD)
    _draw_text_centered(d, "user-override-accept",   ladder_y + 138,     FONT_SUB,   INK)
    _draw_text_centered(d, "(maintainer accepted for showcase use)", ladder_y + 186, FONT_LABEL, MUTED)

    # Notes block — explains the reject + the override + the rollback non-trigger
    notes_y = 620
    notes = [
        ("L2 hard-fails 0.70 threshold", INK),
        ("→ 三矾九染 depth shallow; 石青/石绿 under-represented", MUTED),
        ("→ physics ceiling: single-pass diffusion can't simulate alum-wash", MUTED),
        ("", None),
        ("rollback rule: L1 < 0.6 OR L3 < 0.6 across 3 seeds", INK),
        ("→ neither met; hard-fail = honest disclosure, NOT rollback signal", MUTED),
    ]
    for line, color in notes:
        if line:
            d.text((90, notes_y), line, font=FONT_LABEL, fill=color)
        notes_y += 32

    # Footer
    _draw_text_centered(d, "dual-judgment provenance:  strict rubric retained honesty;  human retained veto.", 990, FONT_LABEL, GOLD)
    _draw_text_centered(d, "both records archived in plan.md — reproducible from disk.", 1028, FONT_LABEL, MUTED)

    canvas.save(OUT / "slide5.png", "PNG", optimize=True)


def _wrap(text, font, max_w, draw):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


# =================================================================
# Slide 6 — file tree of the triad
# =================================================================
def slide6():
    canvas = _square_canvas()
    d = ImageDraw.Draw(canvas)
    _draw_text_centered(d, "The whole project, in 3 markdown files", 56, FONT_TITLE, INK)
    _draw_text_centered(d, "+ generated artifacts under one directory", 130, FONT_SUB, MUTED)

    tree = [
        "docs/visual-specs/2026-04-23-scottish-chinese-fusion/",
        "├── proposal.md            ← /visual-brainstorm output (8K)",
        "├── design.md              ← /visual-spec output (10K)",
        "├── plan.md                ← /visual-plan output (11K)  *verdict trail recorded*",
        "├── source.png             ← user-supplied Scottish street photo",
        "├── iters/",
        "│   ├── _baseline_bare/",
        "│   │   └── bare_gpt2_edit.png    ← naive API control (slide 1 left)",
        "│   └── 7/",
        "│       └── gen_bfbbacd2.png      ← Vulca-mediated (slide 1 right)",
        "├── decompose/",
        "│   ├── lanterns_before.png       ← alpha-iso (slide 4 left)",
        "│   ├── lanterns_after.png        ← gongbi reinterp (slide 4 right)",
        "│   └── iter1/                    ← 9 named entities + 1 residual = 10 layers",
        "│       ├── person.png  · lanterns.png  · sign_top.png …",
        "│       └── manifest.json",
        "└── carousel/                     ← THIS deck (slides 1–6)",
    ]
    y = 220
    for ln in tree:
        d.text((80, y), ln, font=FONT_MONO, fill=INK if ".md" in ln else MUTED)
        y += 36

    _draw_text_centered(d, "Three markdown files locked the entire decision trail.", 980, FONT_BODY, INK)
    _draw_text_centered(d, "The pixels are reproducible from the markdown. The markdown is the product.", 1024, FONT_LABEL, GOLD)

    canvas.save(OUT / "slide6.png", "PNG", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    slide1()
    print("[ok] slide1.png")
    slide2()
    print("[ok] slide2.png")
    slide3()
    print("[ok] slide3.png")
    slide4()
    print("[ok] slide4.png")
    slide5()
    print("[ok] slide5.png")
    slide6()
    print("[ok] slide6.png")
