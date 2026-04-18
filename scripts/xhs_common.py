"""Shared helpers for the Xiaohongshu / dev.to carousel builders.

Four builders render nine 1080x1440 slides each:
- build_xhs_post1_bieber.py     (CN, Bieber)
- build_xhs_post2_trump.py      (CN, Trump)
- build_post1_bieber_en.py      (EN, Bieber)
- build_post2_trump_en.py       (EN, Trump)

They share identical canvas geometry, palette, panel layout, and the
`how it works` + `outro stats` slides. Per-post slides 01..07 still live
in each builder — only the cross-cutting primitives live here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------------------------------------------------------------------------
# Canvas + palette (identical across all 4 builders)
# ---------------------------------------------------------------------------
W, H = 1080, 1440
BG_DARK = (16, 16, 18)
ACCENT = (255, 92, 48)
WHITE = (240, 240, 240)
MUTED = (150, 150, 155)

# ---------------------------------------------------------------------------
# Font paths
# ---------------------------------------------------------------------------
# CN posts use two distinct font files (STHeiti heavy + Hiragino light).
FONT_CN_HEAVY = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_CN_LIGHT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# EN posts use a single .ttc with two named indexes.
FONT_EN_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_EN_HEAVY_INDEX = 1  # Bold
FONT_EN_LIGHT_INDEX = 0  # Regular

# Fallback used when an EN font file is missing.
FONT_FALLBACK = FONT_CN_HEAVY


# ---------------------------------------------------------------------------
# Font loader factories
# ---------------------------------------------------------------------------
FontFn = Callable[..., ImageFont.FreeTypeFont]


def make_cn_font_loader() -> FontFn:
    """Return a `font(size, heavy=True)` closure for CN posts."""

    def font(size: int, heavy: bool = True) -> ImageFont.FreeTypeFont:
        path = FONT_CN_HEAVY if heavy else FONT_CN_LIGHT
        return ImageFont.truetype(path, size)

    return font


def make_en_font_loader() -> FontFn:
    """Return a `font(size, heavy=True)` closure for EN posts (falls back to STHeiti)."""

    def font(size: int, heavy: bool = True) -> ImageFont.FreeTypeFont:
        idx = FONT_EN_HEAVY_INDEX if heavy else FONT_EN_LIGHT_INDEX
        try:
            return ImageFont.truetype(FONT_EN_PATH, size, index=idx)
        except Exception:
            return ImageFont.truetype(FONT_FALLBACK, size)

    return font


# ---------------------------------------------------------------------------
# Generic image primitives (byte-identical across all 4 builders)
# ---------------------------------------------------------------------------
def checker_bg(canvas_size, tile=20, color1=(30, 30, 32), color2=(20, 20, 22)):
    """2-tone checker background — used behind every extracted layer panel."""
    c = Image.new("RGB", canvas_size, color1)
    d = ImageDraw.Draw(c)
    for y in range(0, canvas_size[1], tile):
        for x in range(0, canvas_size[0], tile):
            if ((x // tile) + (y // tile)) % 2 == 0:
                d.rectangle([x, y, x + tile, y + tile], fill=color2)
    return c


def subject_centering(layer_path, default=(0.5, 0.5)):
    """Return (cx, cy) in [0,1] from the layer's alpha bounding box.

    Used to bias center-crop toward the subject so a 16:9 source doesn't
    crop the person out of the frame.
    """
    try:
        img = Image.open(layer_path).convert("RGBA")
        bbox = img.split()[-1].getbbox()
        if bbox is None:
            return default
        cx = (bbox[0] + bbox[2]) / 2 / img.width
        cy = (bbox[1] + bbox[3]) / 2 / img.height
        return (max(0.0, min(1.0, cx)), max(0.0, min(1.0, cy)))
    except Exception:
        return default


def fit_cover(img, box_w, box_h, centering=(0.5, 0.5)):
    """Center-crop + resize so the image exactly fills (box_w, box_h)."""
    return ImageOps.fit(img, (box_w, box_h), method=Image.LANCZOS,
                        centering=centering)


def fit_contain(img, box_w, box_h):
    """Proportional downscale so the image fits inside (box_w, box_h)."""
    iw, ih = img.size
    r = min(box_w / iw, box_h / ih)
    return img.resize((int(iw * r), int(ih * r)), Image.LANCZOS)


def compose_photo(img_path, canvas_size=(W, H), padding=80, centering=(0.5, 0.5)):
    """Letterboxed photo on BG_DARK — used for full-photo slides (post2 only)."""
    del centering  # preserved for API symmetry with fit_cover
    bg = Image.new("RGB", canvas_size, BG_DARK)
    img = Image.open(img_path).convert("RGB")
    fit = fit_contain(img, canvas_size[0] - 2 * padding, canvas_size[1] - 2 * padding)
    x = (canvas_size[0] - fit.width) // 2
    y = (canvas_size[1] - fit.height) // 2
    bg.paste(fit, (x, y))
    return bg


# ---------------------------------------------------------------------------
# Top badge + bottom caption — geometry differs between CN and EN posts
# ---------------------------------------------------------------------------
# CN: 56pt heavy title, 22pt light subtitle, badge height 102px.
# EN: 48pt heavy title, 22pt light subtitle, badge height 84px.
# Bottom caption: CN uses 44pt heavy + 26pt light; EN uses 40pt heavy + 24pt light.
def add_top_badge(canvas, title, subtitle="", color=ACCENT, pad_top=60, *,
                  font: FontFn, title_size: int, subtitle_size: int = 22,
                  badge_height: int = 102, subtitle_gap: int = 80):
    d = ImageDraw.Draw(canvas)
    f_title = font(title_size, heavy=True)
    bbox = d.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    x = (canvas.width - tw) // 2
    d.rectangle([x - 30, pad_top - 18, x + tw + 30, pad_top + badge_height - 18],
                fill=(0, 0, 0, 200), outline=color, width=3)
    d.text((x, pad_top), title, fill=WHITE, font=f_title)
    if subtitle:
        f_sub = font(subtitle_size, heavy=False)
        ebbox = d.textbbox((0, 0), subtitle, font=f_sub)
        ex = (canvas.width - (ebbox[2] - ebbox[0])) // 2
        d.text((ex, pad_top + subtitle_gap), subtitle, fill=MUTED, font=f_sub)
    return canvas


def add_bottom_caption(canvas, text, sub_text="", color=WHITE, *,
                       font: FontFn, text_size: int, sub_size: int,
                       sub_gap: int):
    d = ImageDraw.Draw(canvas)
    f = font(text_size, heavy=True)
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    x = (canvas.width - tw) // 2
    y = canvas.height - 160
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, y - 20, canvas.width, y + 110], fill=(0, 0, 0, 180))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.text((x, y), text, fill=color, font=f)
    if sub_text:
        f2 = font(sub_size, heavy=False)
        sbbox = d.textbbox((0, 0), sub_text, font=f2)
        sx = (canvas.width - (sbbox[2] - sbbox[0])) // 2
        d.text((sx, y + sub_gap), sub_text, fill=MUTED, font=f2)
    return canvas


# ---------------------------------------------------------------------------
# Locale bundle — per-builder font loader + badge/caption sizes + labels
# ---------------------------------------------------------------------------
class Locale:
    """Bundles everything that varies between CN and EN builders.

    Carried as a single argument through the shared slide helpers so each
    builder only constructs it once and hands it off.
    """

    def __init__(self, *, font: FontFn, badge_title_size: int,
                 badge_subtitle_size: int, badge_height: int,
                 badge_subtitle_gap: int, caption_text_size: int,
                 caption_sub_size: int, caption_sub_gap: int,
                 original_label: str, extracted_label: str,
                 panel_label_size: int, panel_label_y_offset: int):
        self.font = font
        self.badge_title_size = badge_title_size
        self.badge_subtitle_size = badge_subtitle_size
        self.badge_height = badge_height
        self.badge_subtitle_gap = badge_subtitle_gap
        self.caption_text_size = caption_text_size
        self.caption_sub_size = caption_sub_size
        self.caption_sub_gap = caption_sub_gap
        self.original_label = original_label
        self.extracted_label = extracted_label
        self.panel_label_size = panel_label_size
        self.panel_label_y_offset = panel_label_y_offset

    def top_badge(self, canvas, title, subtitle=""):
        return add_top_badge(
            canvas, title, subtitle, font=self.font,
            title_size=self.badge_title_size,
            subtitle_size=self.badge_subtitle_size,
            badge_height=self.badge_height,
            subtitle_gap=self.badge_subtitle_gap,
        )

    def bottom_caption(self, canvas, text, sub_text=""):
        return add_bottom_caption(
            canvas, text, sub_text, font=self.font,
            text_size=self.caption_text_size,
            sub_size=self.caption_sub_size,
            sub_gap=self.caption_sub_gap,
        )


def cn_locale() -> Locale:
    return Locale(
        font=make_cn_font_loader(),
        badge_title_size=56, badge_subtitle_size=22,
        badge_height=102, badge_subtitle_gap=80,
        caption_text_size=44, caption_sub_size=26, caption_sub_gap=60,
        original_label="原图", extracted_label="提取层 →",
        panel_label_size=28, panel_label_y_offset=40,
    )


def en_locale() -> Locale:
    return Locale(
        font=make_en_font_loader(),
        badge_title_size=48, badge_subtitle_size=22,
        badge_height=84, badge_subtitle_gap=78,
        caption_text_size=40, caption_sub_size=24, caption_sub_gap=58,
        original_label="Original", extracted_label="Extracted layer  >",
        panel_label_size=26, panel_label_y_offset=38,
    )


# ---------------------------------------------------------------------------
# Shared compound slides
# ---------------------------------------------------------------------------
def make_compare_slide(loc: Locale, orig_path, layer_path, title, subtitle,
                       bottom, bottom_sub, layer_use_photo_bg=False,
                       orig_centering=None):
    """Half/half compare: original (center-cropped cover) | layer on checker."""
    c = Image.new("RGB", (W, H), BG_DARK)
    panel_w, panel_h = 500, 1100
    gap = 40
    start_x = (W - 2 * panel_w - gap) // 2
    start_y = (H - panel_h) // 2 + 40

    if orig_centering is None:
        orig_centering = subject_centering(layer_path)

    orig_img = Image.open(orig_path).convert("RGB")
    orig_fitted = fit_cover(orig_img, panel_w, panel_h, centering=orig_centering)
    orig_panel = Image.new("RGB", (panel_w, panel_h), BG_DARK)
    orig_panel.paste(orig_fitted, (0, 0))
    od = ImageDraw.Draw(orig_panel)
    od.rectangle([0, 0, panel_w - 1, panel_h - 1], outline=(60, 60, 65), width=2)
    c.paste(orig_panel, (start_x, start_y))

    if layer_use_photo_bg:
        layer_panel = Image.new("RGB", (panel_w, panel_h), BG_DARK)
    else:
        layer_panel = checker_bg((panel_w, panel_h))
    layer_img = Image.open(layer_path).convert("RGBA")
    lbbox = layer_img.split()[-1].getbbox()
    if lbbox is not None:
        layer_img = layer_img.crop(lbbox)
    fit_l = fit_contain(layer_img, panel_w - 40, panel_h - 40)
    lx = (panel_w - fit_l.width) // 2
    ly = (panel_h - fit_l.height) // 2
    layer_panel_rgba = layer_panel.convert("RGBA")
    layer_panel_rgba.paste(fit_l, (lx, ly), fit_l)
    ld = ImageDraw.Draw(layer_panel_rgba)
    ld.rectangle([0, 0, panel_w - 1, panel_h - 1], outline=ACCENT, width=2)
    c.paste(layer_panel_rgba.convert("RGB"), (start_x + panel_w + gap, start_y))

    d = ImageDraw.Draw(c)
    f_pl = loc.font(loc.panel_label_size, heavy=False)
    d.text((start_x + 20, start_y - loc.panel_label_y_offset),
           loc.original_label, fill=MUTED, font=f_pl)
    d.text((start_x + panel_w + gap + 20, start_y - loc.panel_label_y_offset),
           loc.extracted_label, fill=ACCENT, font=f_pl)

    c = loc.top_badge(c.convert("RGBA"), title, subtitle).convert("RGB")
    c = loc.bottom_caption(c.convert("RGBA"), bottom, bottom_sub).convert("RGB")
    return c


def make_anatomy_grid(loc: Locale, out_path: Path, face_src: Path,
                      parts: Sequence, highlight_idx: int,
                      top_title: str, top_sub: str,
                      bot_text: str, bot_sub: str):
    """6-tile face-parts grid.

    `parts` accepts either 2-tuples (fname, label) — EN form — or 3-tuples
    (fname, cn, en) — CN form. CN tiles render label + subtitle; EN tiles
    render a single label.
    """
    c = Image.new("RGB", (W, H), BG_DARK)
    cols, rows = 3, 2
    margin_top = 200
    margin_bottom = 220
    margin_x = 40
    gap = 20
    tile_w = (W - 2 * margin_x - (cols - 1) * gap) // cols
    tile_h = (H - margin_top - margin_bottom - (rows - 1) * gap) // rows

    c_rgba = c.convert("RGBA")

    # Tile label typography matches the builder style.
    is_cn = len(parts[0]) == 3
    if is_cn:
        f_tile_primary = loc.font(32, heavy=True)
        f_tile_secondary = loc.font(20, heavy=False)
    else:
        f_tile_primary = loc.font(30, heavy=True)
        f_tile_secondary = None

    for idx, part in enumerate(parts):
        if is_cn:
            fname, primary, secondary = part
        else:
            fname, primary = part
            secondary = None
        r, col = idx // cols, idx % cols
        tx = margin_x + col * (tile_w + gap)
        ty = margin_top + r * (tile_h + gap)
        panel = checker_bg((tile_w, tile_h))
        layer = Image.open(face_src / fname).convert("RGBA")
        bbox = layer.split()[-1].getbbox()
        if bbox is not None:
            layer = layer.crop(bbox)
        fit = fit_contain(layer, tile_w - 20, tile_h - 80)
        lx = (tile_w - fit.width) // 2
        ly = (tile_h - 60 - fit.height) // 2 + 10
        panel_rgba = panel.convert("RGBA")
        panel_rgba.paste(fit, (lx, ly), fit)
        pd = ImageDraw.Draw(panel_rgba)
        outline = ACCENT if idx == highlight_idx else (70, 70, 75)
        pd.rectangle([0, 0, tile_w - 1, tile_h - 1], outline=outline, width=2)
        pd.rectangle([0, tile_h - 60, tile_w, tile_h], fill=(10, 10, 12, 230))

        if is_cn:
            p_bbox = pd.textbbox((0, 0), primary, font=f_tile_primary)
            p_x = (tile_w - (p_bbox[2] - p_bbox[0])) // 2
            pd.text((p_x, tile_h - 55), primary, fill=WHITE, font=f_tile_primary)
            s_bbox = pd.textbbox((0, 0), secondary, font=f_tile_secondary)
            s_x = (tile_w - (s_bbox[2] - s_bbox[0])) // 2
            pd.text((s_x, tile_h - 22), secondary, fill=MUTED, font=f_tile_secondary)
        else:
            p_bbox = pd.textbbox((0, 0), primary, font=f_tile_primary)
            p_x = (tile_w - (p_bbox[2] - p_bbox[0])) // 2
            pd.text((p_x, tile_h - 48), primary, fill=WHITE, font=f_tile_primary)

        c_rgba.paste(panel_rgba, (tx, ty))

    c = c_rgba.convert("RGB")
    c = loc.top_badge(c.convert("RGBA"), top_title, top_sub).convert("RGB")
    c = loc.bottom_caption(c.convert("RGBA"), bot_text, bot_sub).convert("RGB")
    c.save(out_path, quality=95)
    return c


# ---------------------------------------------------------------------------
# Shared "how it works" + "outro" slides
# ---------------------------------------------------------------------------
def render_how_slide(out_path: Path, loc: Locale, lang: dict):
    """Build the 8th slide — same layout for CN and EN, text comes from `lang`.

    lang keys:
      title         — main heading (e.g. "怎么做到的?" / "How it works")
      subtitle      — optional small caption below title (EN omits it)
      brand         — centered brand line ("Claude Code  +  Vulca")
      steps         — list of (primary, secondary) string tuples
      tag           — bordered tag at bottom ("零人工抠图" / "Zero manual masking")
      title_size    — primary title font size (80 default)
      brand_size    — brand line size (72 CN / 64 EN)
      step_size     — step primary size (40 CN / 34 EN)
      step_sub_size — step secondary size (26 CN / 22 EN)
      step_y0       — first step y (540 CN / 500 EN)
      step_gap      — step-to-step gap (130)
      step_sub_gap  — primary-to-sub gap (60 CN / 52 EN)
      tag_size      — tag size (44 CN / 42 EN)
      title_y       — y of main title (120 CN / 140 EN)
    """
    font = loc.font
    c = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(c)

    f_title = font(lang.get("title_size", 80), heavy=True)
    title = lang["title"]
    title_bbox = d.textbbox((0, 0), title, font=f_title)
    title_y = lang.get("title_y", 120)
    d.text(((W - (title_bbox[2] - title_bbox[0])) // 2, title_y),
           title, fill=WHITE, font=f_title)

    brand_y_default = 340
    if lang.get("subtitle"):
        f_sub = font(28, heavy=False)
        sub = lang["subtitle"]
        sub_bbox = d.textbbox((0, 0), sub, font=f_sub)
        d.text(((W - (sub_bbox[2] - sub_bbox[0])) // 2, 230),
               sub, fill=MUTED, font=f_sub)
    else:
        brand_y_default = 290

    f_brand = font(lang.get("brand_size", 72), heavy=True)
    brand = lang["brand"]
    brand_bbox = d.textbbox((0, 0), brand, font=f_brand)
    d.text(((W - (brand_bbox[2] - brand_bbox[0])) // 2,
            lang.get("brand_y", brand_y_default)),
           brand, fill=ACCENT, font=f_brand)

    f_step = font(lang.get("step_size", 40), heavy=True)
    f_step_sub = font(lang.get("step_sub_size", 26), heavy=False)
    y0 = lang.get("step_y0", 540)
    step_gap = lang.get("step_gap", 130)
    sub_gap = lang.get("step_sub_gap", 60)
    for i, (primary, secondary) in enumerate(lang["steps"]):
        y = y0 + i * step_gap
        p_bbox = d.textbbox((0, 0), primary, font=f_step)
        d.text(((W - (p_bbox[2] - p_bbox[0])) // 2, y),
               primary, fill=WHITE, font=f_step)
        s_bbox = d.textbbox((0, 0), secondary, font=f_step_sub)
        d.text(((W - (s_bbox[2] - s_bbox[0])) // 2, y + sub_gap),
               secondary, fill=MUTED, font=f_step_sub)

    f_tag = font(lang.get("tag_size", 44), heavy=True)
    tag = lang["tag"]
    tag_bbox = d.textbbox((0, 0), tag, font=f_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    d.rectangle([(W - tag_w) // 2 - 30, H - 150,
                 (W + tag_w) // 2 + 30, H - 80],
                outline=ACCENT, width=3)
    d.text(((W - tag_w) // 2, H - 140), tag, fill=ACCENT, font=f_tag)
    c.save(out_path, quality=95)
    return c


def render_outro_slide(out_path: Path, loc: Locale, lang: dict,
                       layer_count: int = 485, image_count: int = 47):
    """Build the 9th outro-stats slide — same layout for CN and EN.

    lang keys:
      layers_label  — small label below the big number
      hr_main       — line with `{image_count} ...`
      credit_lines  — 3 small muted lines
      cta           — accent CTA near the bottom
      num_y         — big number y (260 CN / 240 EN)
      label_size    — size of small label (42 CN / 40 EN)
      label_y       — y of small label (490 CN / 480 EN)
      hr_size       — size of hr_main (54 CN / 52 EN)
      hr_y          — y of hr_main (680 CN / 670 EN)
      credit_size   — size of credit lines (28 CN / 26 EN)
      credit_y0     — first credit line y (810 CN / 790 EN)
      credit_gap    — gap between credit lines (44 CN / 42 EN)
      cta_size      — cta size (38 CN / 36 EN)
    """
    del image_count  # included in the pre-formatted `hr_main` caption
    font = loc.font
    c = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(c)

    f_num = font(200, heavy=True)
    num = str(layer_count)
    num_bbox = d.textbbox((0, 0), num, font=f_num)
    d.text(((W - (num_bbox[2] - num_bbox[0])) // 2, lang.get("num_y", 260)),
           num, fill=ACCENT, font=f_num)

    f_label = font(lang.get("label_size", 42), heavy=False)
    lbl = lang["layers_label"]
    lbl_bbox = d.textbbox((0, 0), lbl, font=f_label)
    d.text(((W - (lbl_bbox[2] - lbl_bbox[0])) // 2, lang.get("label_y", 490)),
           lbl, fill=WHITE, font=f_label)

    f_hr = font(lang.get("hr_size", 54), heavy=True)
    hr = lang["hr_main"]
    hr_bbox = d.textbbox((0, 0), hr, font=f_hr)
    d.text(((W - (hr_bbox[2] - hr_bbox[0])) // 2, lang.get("hr_y", 680)),
           hr, fill=WHITE, font=f_hr)

    f_credit = font(lang.get("credit_size", 28), heavy=False)
    credit_y0 = lang.get("credit_y0", 810)
    credit_gap = lang.get("credit_gap", 44)
    for i, line in enumerate(lang["credit_lines"]):
        c_bbox = d.textbbox((0, 0), line, font=f_credit)
        d.text(((W - (c_bbox[2] - c_bbox[0])) // 2, credit_y0 + i * credit_gap),
               line, fill=MUTED, font=f_credit)

    f_cta = font(lang.get("cta_size", 38), heavy=True)
    cta = lang["cta"]
    cta_bbox = d.textbbox((0, 0), cta, font=f_cta)
    d.text(((W - (cta_bbox[2] - cta_bbox[0])) // 2, H - 220),
           cta, fill=ACCENT, font=f_cta)
    c.save(out_path, quality=95)
    return c
