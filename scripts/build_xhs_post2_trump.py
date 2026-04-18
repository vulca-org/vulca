"""Build Xiaohongshu Post #2 carousel — Donald Trump 3-photo decomposition.

9 slides at 1080x1440 (3:4) for Xiaohongshu feed.

Narrative (v2 — Butler-heavy per user request):
  01 cover — shooting photo hook "我让 Claude 把 Trump 拆了"
  02 Butler 2024 原图 — full shooting photo
  03 shooting: orig vs Trump subject
  04 shooting multi-subject: Trump hero + 4 side tiles (agents + sky/flag)
  05 mugshot: orig vs subject
  06 mugshot 五官自动解剖: 6-panel face-parts grid (mugshot has 8 parts)
  07 portrait: orig vs subject (single slide, portrait minimized)
  08 how it works: Claude Code + Vulca attribution
  09 outro stats (identical to Post #1)

Copies helpers + constants from build_xhs_post1_bieber.py verbatim.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets" / "social" / "post2-trump"
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


def compose_photo(img_path, canvas_size=(W, H), padding=80, centering=(0.5, 0.5)):
    bg = Image.new("RGB", canvas_size, BG_DARK)
    img = Image.open(img_path).convert("RGB")
    fit = fit_contain(img, canvas_size[0] - 2*padding, canvas_size[1] - 2*padding)
    x = (canvas_size[0] - fit.width) // 2
    y = (canvas_size[1] - fit.height) // 2
    bg.paste(fit, (x, y))
    return bg


def make_compare_slide(orig_path, layer_path, title_cn, title_en,
                       bottom_cn, bottom_en, layer_use_photo_bg=False,
                       orig_centering=None):
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


def make_anatomy_grid(face_src, parts, highlight_idx,
                      top_cn, top_en, bot_cn, bot_en, out_name):
    """6-tile 五官 grid (reused for portrait, mugshot, etc.)."""
    c = Image.new("RGB", (W, H), BG_DARK)
    cols, rows = 3, 2
    margin_top = 200
    margin_bottom = 220
    margin_x = 40
    gap = 20
    tile_w = (W - 2 * margin_x - (cols - 1) * gap) // cols
    tile_h = (H - margin_top - margin_bottom - (rows - 1) * gap) // rows

    c_rgba = c.convert("RGBA")
    f_tile_cn = font(32, heavy=True)
    f_tile_en = font(20, heavy=False)

    for idx, (fname, cn, en_) in enumerate(parts):
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
    c = add_top_badge(c.convert("RGBA"), top_cn, top_en).convert("RGB")
    c = add_bottom_caption(c.convert("RGBA"), bot_cn, bot_en).convert("RGB")
    c.save(OUT / out_name, quality=95)
    print(f"✓ {out_name}")


def slide_01_cover():
    c = Image.new("RGB", (W, H), BG_DARK)
    orig = Image.open(ORIGS / "trump-shooting.jpg").convert("RGB")
    bg = fit_cover(orig, W, H, centering=(0.5, 0.35))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 110))
    c = Image.alpha_composite(bg.convert("RGBA"), veil).convert("RGB")

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, 0, W, 440], fill=(0, 0, 0, 170))
    c = Image.alpha_composite(c.convert("RGBA"), overlay).convert("RGB")

    d = ImageDraw.Draw(c)
    f_big = font(96, heavy=True)
    for i, line in enumerate(["我让 Claude", "把 Trump 拆了"]):
        bbox = d.textbbox((0, 0), line, font=f_big)
        tw = bbox[2] - bbox[0]
        y_off = 90 + i * 120
        color = WHITE if i == 0 else ACCENT
        d.text(((W - tw) // 2, y_off), line, fill=color, font=f_big)

    f_sub = font(36, heavy=False)
    sub = "Butler 2024 · 一张新闻照 6 个主体"
    sbbox = d.textbbox((0, 0), sub, font=f_sub)
    d.text(((W - (sbbox[2] - sbbox[0])) // 2, 350), sub, fill=WHITE, font=f_sub)

    f_small = font(30, heavy=True)
    bottom = "→ 滑动看全部"
    bbox2 = d.textbbox((0, 0), bottom, font=f_small)
    overlay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od2 = ImageDraw.Draw(overlay2)
    od2.rectangle([0, H - 140, W, H - 60], fill=(0, 0, 0, 180))
    c = Image.alpha_composite(c.convert("RGBA"), overlay2).convert("RGB")
    d = ImageDraw.Draw(c)
    d.text(((W - (bbox2[2] - bbox2[0])) // 2, H - 120), bottom,
           fill=ACCENT, font=f_small)
    c.save(OUT / "01-cover.png", quality=95)
    print("✓ 01-cover.png")


def slide_02_shooting_orig():
    c = compose_photo(ORIGS / "trump-shooting.jpg")
    c = add_top_badge(c.convert("RGBA"),
                      "Butler 2024 原图", "original photo · Evan Vucci").convert("RGB")
    c = add_bottom_caption(c.convert("RGBA"),
                           "一张 387 × 258 的新闻照",
                           "6 个独立主体 + 2 个背景元素").convert("RGB")
    c.save(OUT / "02-shooting-orig.png", quality=95)
    print("✓ 02-shooting-orig.png")


def slide_03_shooting_subject():
    c = make_compare_slide(
        ORIGS / "trump-shooting.jpg",
        LAYERS / "trump-shooting" / "trump.png",
        "提取 · Trump", "subject · shooting",
        "只保留抬拳的那一秒",
        "fist raised, isolated",
    )
    c.save(OUT / "03-shooting-subject.png", quality=95)
    print("✓ 03-shooting-subject.png")


def slide_04_shooting_multi():
    """Trump hero + 4 side tiles: agent_left/right/bottom + flag + sky."""
    SRC = LAYERS / "trump-shooting"
    c = Image.new("RGB", (W, H), BG_DARK)
    c_rgba = c.convert("RGBA")

    margin_top = 200
    margin_bottom = 220
    margin_x = 40
    gap = 20

    hero_w = W - 2 * margin_x
    hero_h = 500
    bot_y = margin_top + hero_h + gap
    bot_tile_w = (W - 2 * margin_x - 3 * gap) // 4
    bot_tile_h = H - margin_bottom - bot_y

    f_tile_cn = font(30, heavy=True)
    f_tile_en = font(18, heavy=False)
    f_tile_cn_small = font(24, heavy=True)

    def draw_tile(panel_rgba, layer_path, cn, en_, highlight):
        panel_w_, panel_h_ = panel_rgba.size
        layer = Image.open(layer_path).convert("RGBA")
        bbox = layer.split()[-1].getbbox()
        if bbox is not None:
            layer = layer.crop(bbox)
        fit = fit_contain(layer, panel_w_ - 20, panel_h_ - 70)
        lx = (panel_w_ - fit.width) // 2
        ly = (panel_h_ - 60 - fit.height) // 2 + 10
        panel_rgba.paste(fit, (lx, ly), fit)
        pd = ImageDraw.Draw(panel_rgba)
        outline = ACCENT if highlight else (70, 70, 75)
        pd.rectangle([0, 0, panel_w_ - 1, panel_h_ - 1],
                     outline=outline, width=2)
        pd.rectangle([0, panel_h_ - 60, panel_w_, panel_h_],
                     fill=(10, 10, 12, 230))
        f_cn = f_tile_cn if panel_w_ > 300 else f_tile_cn_small
        cn_bbox = pd.textbbox((0, 0), cn, font=f_cn)
        cn_x = (panel_w_ - (cn_bbox[2] - cn_bbox[0])) // 2
        pd.text((cn_x, panel_h_ - 55), cn, fill=WHITE, font=f_cn)
        en_bbox = pd.textbbox((0, 0), en_, font=f_tile_en)
        en_x = (panel_w_ - (en_bbox[2] - en_bbox[0])) // 2
        pd.text((en_x, panel_h_ - 22), en_, fill=MUTED, font=f_tile_en)

    hero_panel = checker_bg((hero_w, hero_h)).convert("RGBA")
    draw_tile(hero_panel, SRC / "trump.png", "Trump (抬拳 + 血)",
              "fist raised, blood on cheek", highlight=True)
    c_rgba.paste(hero_panel, (margin_x, margin_top))

    bottom_tiles = [
        ("agent_left.png",  "特工 左",  "agent · L"),
        ("agent_right.png", "特工 右",  "agent · R"),
        ("agent_bottom.png","特工 下",  "agent · B"),
        ("flag.png",        "美国国旗",  "flag"),
    ]
    for i, (fname, cn, en_) in enumerate(bottom_tiles):
        panel = checker_bg((bot_tile_w, bot_tile_h)).convert("RGBA")
        draw_tile(panel, SRC / fname, cn, en_, highlight=False)
        tx = margin_x + i * (bot_tile_w + gap)
        c_rgba.paste(panel, (tx, bot_y))

    c = c_rgba.convert("RGB")
    c = add_top_badge(c.convert("RGBA"),
                      "一张照片 · 6 个主体",
                      "Trump + 3 agents + flag + sky").convert("RGB")
    c = add_bottom_caption(c.convert("RGBA"),
                           "Butler 2024 · 混乱场景全自动拆解",
                           "sam_bbox hints separate overlapping figures").convert("RGB")
    c.save(OUT / "04-shooting-multi.png", quality=95)
    print("✓ 04-shooting-multi.png")


def slide_05_mugshot_subject():
    c = make_compare_slide(
        ORIGS / "trump-mugshot.jpg",
        LAYERS / "trump-mugshot" / "trump.png",
        "提取 · mugshot", "subject · 2023 Georgia",
        "Fulton County 2023",
        "same pipeline, different vibe",
    )
    c.save(OUT / "05-mugshot-subject.png", quality=95)
    print("✓ 05-mugshot-subject.png")


def slide_06_mugshot_anatomy():
    parts = [
        ("trump__skin.png", "皮肤", "skin"),
        ("trump__hair.png", "头发", "hair"),
        ("trump__eyes.png", "眼睛", "eyes"),
        ("trump__nose.png", "鼻子", "nose"),
        ("trump__lips.png", "嘴唇", "lips"),
        ("trump__ears.png", "耳朵", "ears"),
    ]
    make_anatomy_grid(
        LAYERS / "trump-mugshot", parts, highlight_idx=4,
        top_cn="五官自动解剖", top_en="face parts · mugshot",
        bot_cn="mugshot 也能拆出 6 层",
        bot_en="SegFormer on booking photo",
        out_name="06-mugshot-anatomy.png",
    )


def slide_07_portrait_subject():
    c = make_compare_slide(
        ORIGS / "trump-portrait.jpg",
        LAYERS / "trump-portrait" / "trump.png",
        "提取 · 椭圆办公室", "subject · oval office",
        "第三张同理 · 椭圆办公室",
        "third photo, same SDK",
    )
    c.save(OUT / "07-portrait-subject.png", quality=95)
    print("✓ 07-portrait-subject.png")


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
    stale = {"02-portrait-subject.png", "03-portrait-bg.png",
             "04-face-anatomy.png", "06-mugshot-bg.png",
             "07-shooting-multi.png"}
    for name in stale:
        p = OUT / name
        if p.exists():
            p.unlink()
            print(f"✗ removed stale {name}")


def write_caption_md():
    path = OUT / "caption.md"
    path.write_text("""# 3 版小红书文案 · 选一个发 (Post #2 · Trump)

## Version A · 短直接（推荐首发）

```
我让 Claude 把 Donald Trump 的 3 张照片都拆了 👀

重点是 Butler 2024 抬拳头那张 —
一张 387×258 的新闻照，Claude 识出 6 个独立主体
Trump + 3 个特工 + 美国国旗 + 蓝天
全自动 · 零人工抠图

#donaldtrump #trump #特朗普 #butler2024 #AI拆图 #AI艺术
#claudecode #AIGC #新闻摄影 #计算机视觉
```

## Version B · 技术感

```
Butler PA 2024 · Claude Code 配合 Vulca SDK 自动拆层

shooting: 6 主体（Trump + 3 特工 + 国旗 + 天空）
mugshot:  8 层（含完整五官解剖）
portrait: 12 层（椭圆办公室 + 国旗）

agent 驱动：Claude 读图 → 写 JSON plan
→ Vulca 跑 YOLO+DINO+SAM+SegFormer
→ 结果回到 Claude 核查 flags

对 Butler 那张的 4 人拥挤场景，agent 自己切到 sam_bbox
用 bbox hint 把重叠的特工分开 — 这才是 agent-native

#trump #donaldtrump #butler2024 #AI艺术 #计算机视觉
#claudecode #AIGC #开源项目
```

## Version C · 悬念式

```
Butler 2024 那张 Trump 抬拳头的照片
除了 Trump 自己，你能数出几个主体？

→ 滑到第 4 张看全答案
→ 再滑到第 6 张看 mugshot 的五官拆解

#trump #donaldtrump #butler2024 #特朗普 #mugshot
#AI拆图 #AI艺术 #AIGC #claudecode
```

---

# 发布 checklist

- [ ] 封面 (01-cover.png) — Butler 抬拳头 + "我让 Claude 把 Trump 拆了"
- [ ] 9 张按顺序上传
- [ ] Version A 首发（最短，突出 Butler 6 主体）
- [ ] 发布时间 19:00-22:00
- [ ] 首 2h 盯评论，前 24h 不改

# 内容叙事 (v2 · Butler-heavy)

1. **01 cover** — Butler 抬拳头 + "我让 Claude 把 Trump 拆了"
2. **02 Butler 2024 原图** — 全图展示（让用户看到源头）
3. **03 shooting · Trump** — 单独拆出抬拳头的 Trump
4. **04 shooting 多主体** — Trump hero + 3 特工 + 国旗并排
5. **05 mugshot · 人物** — 2023 Georgia mugshot 拆出人
6. **06 mugshot · 五官解剖** — 6 宫格：皮肤 / 头发 / 眼 / 鼻 / 嘴 / 耳
7. **07 portrait · 人物** — 椭圆办公室照压轴，说明流程对任何照都管用
8. **08 怎么做到的** — Claude Code + Vulca 四步流程
9. **09 数据总结** — 47 张 · 485 层 · 零人工

# 封面点击率关键

- Butler 抬拳头是近 50 年最有记忆点的新闻摄影之一
- "我让 Claude 把 Trump 拆了" 双钩子（AI 圈 + 政治圈）
- KPI: 收藏 ≥ 点赞 = 找对受众
""", encoding="utf-8")
    print("✓ caption.md")


def write_hashtags_txt():
    path = OUT / "hashtags.txt"
    path.write_text("""# 小红书 hashtag bank - Post #2 Trump - 每发一帖选 8-12 个
# 组合原则: 2 明星热度 + 3-4 赛道定位 + 2-3 垂直 + 1-2 兴趣

## 明星/热度 (流量池)
#donaldtrump     ← 英文版,国际搜索
#trump
#特朗普
#mugshot
#butler2024
#ovaloffice

## 赛道定位 (目标受众)
#AI艺术
#AI拆图
#AIGC
#计算机视觉
#设计灵感
#图层设计

## 垂直 (找同好)
#摄影后期
#图像处理
#SAM
#开源项目
#独立开发

## 兴趣/美学
#美学
#新闻摄影
#人像摄影
#政治影像
""", encoding="utf-8")
    print("✓ hashtags.txt")


def main():
    cleanup_stale()
    slide_01_cover()
    slide_02_shooting_orig()
    slide_03_shooting_subject()
    slide_04_shooting_multi()
    slide_05_mugshot_subject()
    slide_06_mugshot_anatomy()
    slide_07_portrait_subject()
    slide_08_how()
    slide_09_outro()
    write_caption_md()
    write_hashtags_txt()
    print(f"\n✅ All 9 slides + caption + hashtags → {OUT}")


if __name__ == "__main__":
    main()
