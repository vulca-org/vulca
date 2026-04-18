"""Build Xiaohongshu Post #1 carousel — Justin Bieber Coachella 2026.

9 slides at 1080x1440 (3:4) for Xiaohongshu feed.

Narrative:
  01 cover
  02 stayed: orig vs subject
  03 stayed: orig vs teal stage
  04 baby: orig vs frontal subject     (NEW — frontal face pose)
  05 baby: orig vs face skin only      (NEW — face-parsing depth)
  06 speed-demon: orig vs subject
  07 speed-demon: orig vs red stage
  08 how it works: Claude Code + Vulca attribution
  09 outro stats

Fixes vs v2:
- fit_cover() center-crops originals so 16:9 speed-demon doesn't letterbox
- subject-aware centering pulled from extracted layer's alpha bbox
- honest attribution: Claude Code reads -> writes plan -> calls Vulca SDK,
  zero manual masking
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets" / "social" / "post1-bieber"
OUT.mkdir(parents=True, exist_ok=True)

LAYERS = REPO / "assets" / "showcase" / "layers_v2"
ORIGS  = REPO / "assets" / "showcase" / "originals"

W, H = 1080, 1440
BG_DARK  = (16, 16, 18)
ACCENT   = (255, 92, 48)
WHITE    = (240, 240, 240)
MUTED    = (150, 150, 155)

FONT_HEAVY = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def font(size, heavy=True):
    return ImageFont.truetype(FONT_HEAVY if heavy else FONT_LIGHT, size)


def checker_bg(canvas_size, tile=20, color1=(30, 30, 32), color2=(20, 20, 22)):
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
    iw, ih = img.size
    r = min(box_w / iw, box_h / ih)
    return img.resize((int(iw * r), int(ih * r)), Image.LANCZOS)


def add_top_badge(canvas, text_cn, text_en="", color=ACCENT, pad_top=60):
    d = ImageDraw.Draw(canvas)
    f_cn = font(56, heavy=True)
    bbox = d.textbbox((0, 0), text_cn, font=f_cn)
    tw = bbox[2] - bbox[0]
    x = (canvas.width - tw) // 2
    d.rectangle([x - 30, pad_top - 18, x + tw + 30, pad_top + 84],
                fill=(0, 0, 0, 200), outline=color, width=3)
    d.text((x, pad_top), text_cn, fill=WHITE, font=f_cn)
    if text_en:
        f_en = font(22, heavy=False)
        ebbox = d.textbbox((0, 0), text_en, font=f_en)
        ex = (canvas.width - (ebbox[2] - ebbox[0])) // 2
        d.text((ex, pad_top + 80), text_en, fill=MUTED, font=f_en)
    return canvas


def add_bottom_caption(canvas, text, sub_text="", color=WHITE):
    d = ImageDraw.Draw(canvas)
    f = font(44, heavy=True)
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
        f2 = font(26, heavy=False)
        sbbox = d.textbbox((0, 0), sub_text, font=f2)
        sx = (canvas.width - (sbbox[2] - sbbox[0])) // 2
        d.text((sx, y + 60), sub_text, fill=MUTED, font=f2)
    return canvas


def make_compare_slide(orig_path, layer_path, title_cn, title_en,
                       bottom_cn, bottom_en, layer_use_photo_bg=False,
                       orig_centering=None):
    """Half/half compare: original (center-cropped cover) | layer on checker."""
    c = Image.new("RGB", (W, H), BG_DARK)
    panel_w, panel_h = 500, 1100
    gap = 40
    start_x = (W - 2*panel_w - gap) // 2
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
    f_pl = font(28, heavy=False)
    d.text((start_x + 20, start_y - 40), "原图", fill=MUTED, font=f_pl)
    d.text((start_x + panel_w + gap + 20, start_y - 40),
           "提取层 →", fill=ACCENT, font=f_pl)

    c = add_top_badge(c.convert("RGBA"), title_cn, title_en).convert("RGB")
    c = add_bottom_caption(c.convert("RGBA"), bottom_cn, bottom_en).convert("RGB")
    return c


def slide_01_cover():
    c = Image.new("RGB", (W, H), BG_DARK)
    orig = Image.open(ORIGS / "bieber-coachella-stayed.png").convert("RGB")
    bg = fit_cover(orig, W, H, centering=(0.5, 0.5))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 120))
    c = Image.alpha_composite(bg.convert("RGBA"), veil).convert("RGB")

    d = ImageDraw.Draw(c)
    f_big = font(96, heavy=True)
    for i, line in enumerate(["我让 Claude", "把 Bieber 拆了"]):
        bbox = d.textbbox((0, 0), line, font=f_big)
        tw = bbox[2] - bbox[0]
        y_off = 120 + i * 120
        color = WHITE if i == 0 else ACCENT
        d.text(((W - tw) // 2, y_off), line, fill=color, font=f_big)

    f_sub = font(36, heavy=False)
    sub = "Coachella 2026 · 全自动图层解构"
    sbbox = d.textbbox((0, 0), sub, font=f_sub)
    d.text(((W - (sbbox[2] - sbbox[0])) // 2, 380), sub, fill=WHITE, font=f_sub)

    f_small = font(30, heavy=True)
    bottom = "→ 滑动看全部"
    bbox2 = d.textbbox((0, 0), bottom, font=f_small)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, H - 140, W, H - 60], fill=(0, 0, 0, 180))
    c = Image.alpha_composite(c.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(c)
    d.text(((W - (bbox2[2] - bbox2[0])) // 2, H - 120), bottom,
           fill=ACCENT, font=f_small)
    c.save(OUT / "01-cover.png", quality=95)
    print("✓ 01-cover.png")


def slide_02_stayed_subject():
    c = make_compare_slide(
        ORIGS / "bieber-coachella-stayed.png",
        LAYERS / "bieber-coachella-stayed" / "bieber.png",
        "提取 · 人物", "subject extraction · pose 1",
        "AI 单独拆出人物", "background removed automatically",
    )
    c.save(OUT / "02-stayed-subject.png", quality=95)
    print("✓ 02-stayed-subject.png")


def slide_03_stayed_bg():
    c = make_compare_slide(
        ORIGS / "bieber-coachella-stayed.png",
        LAYERS / "bieber-coachella-stayed" / "teal_stage.png",
        "提取 · 舞台背景", "background · pose 1",
        "单独拆出舞台灯光", "stage lighting isolated",
        layer_use_photo_bg=True,
    )
    c.save(OUT / "03-stayed-bg.png", quality=95)
    print("✓ 03-stayed-bg.png")


def slide_04_baby_subject():
    c = make_compare_slide(
        ORIGS / "bieber-coachella-baby.png",
        LAYERS / "bieber-coachella-baby" / "bieber.png",
        "正脸 · 人物", "frontal view · pose 2",
        "正脸也能拆出来", "frontal face, same pipeline",
    )
    c.save(OUT / "04-baby-subject.png", quality=95)
    print("✓ 04-baby-subject.png")


def slide_05_face_anatomy():
    """6-panel grid: 五官 multi-level decomposition from face-only source."""
    FACE_SRC = LAYERS / "bieber-baby-faceonly"
    parts = [
        ("bieber__skin.png",     "皮肤",    "skin"),
        ("bieber__hair.png",     "头发",    "hair"),
        ("bieber__eyebrows.png", "眉毛",    "eyebrows"),
        ("bieber__nose.png",     "鼻子",    "nose"),
        ("bieber__ears.png",     "耳朵",    "ears"),
        ("bieber.png",           "合成",    "all parts"),
    ]

    c = Image.new("RGB", (W, H), BG_DARK)
    cols, rows = 3, 2
    margin_top = 200
    margin_bottom = 220
    margin_x = 40
    gap = 20
    tile_w = (W - 2 * margin_x - (cols - 1) * gap) // cols
    tile_h = (H - margin_top - margin_bottom - (rows - 1) * gap) // rows

    c_rgba = c.convert("RGBA")
    d_rgba = ImageDraw.Draw(c_rgba)
    f_tile_cn = font(32, heavy=True)
    f_tile_en = font(20, heavy=False)

    for idx, (fname, cn, en_) in enumerate(parts):
        r, col = idx // cols, idx % cols
        tx = margin_x + col * (tile_w + gap)
        ty = margin_top + r * (tile_h + gap)
        panel = checker_bg((tile_w, tile_h))
        layer = Image.open(FACE_SRC / fname).convert("RGBA")
        bbox = layer.split()[-1].getbbox()
        if bbox is not None:
            layer = layer.crop(bbox)
        fit = fit_contain(layer, tile_w - 20, tile_h - 80)
        lx = (tile_w - fit.width) // 2
        ly = (tile_h - 60 - fit.height) // 2 + 10
        panel_rgba = panel.convert("RGBA")
        panel_rgba.paste(fit, (lx, ly), fit)
        pd = ImageDraw.Draw(panel_rgba)
        outline = ACCENT if idx == len(parts) - 1 else (70, 70, 75)
        pd.rectangle([0, 0, tile_w - 1, tile_h - 1], outline=outline, width=2)
        pd.rectangle([0, tile_h - 60, tile_w, tile_h],
                     fill=(10, 10, 12, 230))
        cn_bbox = pd.textbbox((0, 0), cn, font=f_tile_cn)
        cn_x = (tile_w - (cn_bbox[2] - cn_bbox[0])) // 2
        pd.text((cn_x, tile_h - 55), cn, fill=WHITE, font=f_tile_cn)
        en_bbox = pd.textbbox((0, 0), en_, font=f_tile_en)
        en_x = (tile_w - (en_bbox[2] - en_bbox[0])) // 2
        pd.text((en_x, tile_h - 22), en_, fill=MUTED, font=f_tile_en)
        c_rgba.paste(panel_rgba, (tx, ty))

    c = c_rgba.convert("RGB")
    c = add_top_badge(c.convert("RGBA"),
                      "五官自动解剖", "face parts · one photo").convert("RGB")
    c = add_bottom_caption(c.convert("RGBA"),
                           "SegFormer 一次拆出 10 层",
                           "zero manual annotation").convert("RGB")
    c.save(OUT / "05-face-anatomy.png", quality=95)
    print("✓ 05-face-anatomy.png")


def slide_06_sd_subject():
    c = make_compare_slide(
        ORIGS / "bieber-coachella-speed-demon.png",
        LAYERS / "bieber-coachella-speed-demon" / "bieber.png",
        "提取 · 人物", "subject extraction · pose 3",
        "同一个 pipeline · 不同姿势",
        "same SDK across all 3 poses",
    )
    c.save(OUT / "06-sd-subject.png", quality=95)
    print("✓ 06-sd-subject.png")


def slide_07_sd_bg():
    c = make_compare_slide(
        ORIGS / "bieber-coachella-speed-demon.png",
        LAYERS / "bieber-coachella-speed-demon" / "red_stage.png",
        "提取 · 红色舞台", "red stage · pose 3",
        "红色灯光单独剥离", "red-lit stage isolated",
        layer_use_photo_bg=True,
    )
    c.save(OUT / "07-sd-bg.png", quality=95)
    print("✓ 07-sd-bg.png")


def slide_08_how():
    c = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(c)

    f_title = font(80, heavy=True)
    title = "怎么做到的?"
    bbox = d.textbbox((0, 0), title, font=f_title)
    d.text(((W - (bbox[2] - bbox[0])) // 2, 120), title, fill=WHITE, font=f_title)

    f_en = font(28, heavy=False)
    en = "how it was made"
    ebox = d.textbbox((0, 0), en, font=f_en)
    d.text(((W - (ebox[2] - ebox[0])) // 2, 230), en, fill=MUTED, font=f_en)

    f_brand = font(72, heavy=True)
    brand = "Claude Code  +  Vulca"
    bbrand = d.textbbox((0, 0), brand, font=f_brand)
    d.text(((W - (bbrand[2] - bbrand[0])) // 2, 340), brand,
           fill=ACCENT, font=f_brand)

    f_step = font(40, heavy=True)
    f_step_sub = font(26, heavy=False)
    steps = [
        ("① Claude 读图", "agent looks at the photo"),
        ("② Claude 写 plan", "agent authors JSON plan"),
        ("③ Vulca SDK 自动拆层", "SDK runs YOLO+DINO+SAM+SegFormer"),
        ("④ 结果回到 Claude 核查", "agent checks manifest + flags"),
    ]
    y0 = 540
    for i, (cn, en_) in enumerate(steps):
        y = y0 + i * 130
        cbox = d.textbbox((0, 0), cn, font=f_step)
        d.text(((W - (cbox[2] - cbox[0])) // 2, y), cn, fill=WHITE, font=f_step)
        ebox2 = d.textbbox((0, 0), en_, font=f_step_sub)
        d.text(((W - (ebox2[2] - ebox2[0])) // 2, y + 60), en_,
               fill=MUTED, font=f_step_sub)

    f_tag = font(44, heavy=True)
    tag = "零人工抠图"
    tbox = d.textbbox((0, 0), tag, font=f_tag)
    d.rectangle([(W - (tbox[2] - tbox[0])) // 2 - 30, H - 150,
                 (W + (tbox[2] - tbox[0])) // 2 + 30, H - 80],
                outline=ACCENT, width=3)
    d.text(((W - (tbox[2] - tbox[0])) // 2, H - 140), tag,
           fill=ACCENT, font=f_tag)
    c.save(OUT / "08-how.png", quality=95)
    print("✓ 08-how.png")


def slide_09_outro():
    c = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(c)
    f_num = font(200, heavy=True)
    num = "485"
    bbox = d.textbbox((0, 0), num, font=f_num)
    d.text(((W - (bbox[2] - bbox[0])) // 2, 260), num, fill=ACCENT, font=f_num)
    f_label = font(42, heavy=False)
    lbl = "个图层"
    lbox = d.textbbox((0, 0), lbl, font=f_label)
    d.text(((W - (lbox[2] - lbox[0])) // 2, 490), lbl, fill=WHITE, font=f_label)

    f_hr = font(54, heavy=True)
    hr = "47 张图 · 全自动解构"
    hbox = d.textbbox((0, 0), hr, font=f_hr)
    d.text(((W - (hbox[2] - hbox[0])) // 2, 680), hr, fill=WHITE, font=f_hr)

    f_sub = font(28, heavy=False)
    for i, line in enumerate([
        "Claude Code 指挥 · Vulca SDK 执行",
        "YOLO + DINO + SAM + SegFormer",
        "hierarchical resolve · residual honesty",
    ]):
        lbbox = d.textbbox((0, 0), line, font=f_sub)
        d.text(((W - (lbbox[2] - lbbox[0])) // 2, 810 + i * 44), line,
               fill=MUTED, font=f_sub)

    f_cta = font(38, heavy=True)
    cta = "想看更多?  评论区告诉我"
    cbbox = d.textbbox((0, 0), cta, font=f_cta)
    d.text(((W - (cbbox[2] - cbbox[0])) // 2, H - 220), cta,
           fill=ACCENT, font=f_cta)
    c.save(OUT / "09-outro.png", quality=95)
    print("✓ 09-outro.png")


def cleanup_stale():
    """Remove previous v2 slides that no longer exist in v3."""
    stale = {"02-stayed-orig.png", "04-stayed-bg.png", "05-sd-orig.png",
             "08-both-persons.png", "03-stayed-subject.png",
             "05-baby-face.png"}
    for name in stale:
        p = OUT / name
        if p.exists():
            p.unlink()
            print(f"✗ removed stale {name}")


def main():
    cleanup_stale()
    slide_01_cover()
    slide_02_stayed_subject()
    slide_03_stayed_bg()
    slide_04_baby_subject()
    slide_05_face_anatomy()
    slide_06_sd_subject()
    slide_07_sd_bg()
    slide_08_how()
    slide_09_outro()
    print(f"\n✅ All 9 slides → {OUT}")


if __name__ == "__main__":
    main()
