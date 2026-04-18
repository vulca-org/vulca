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

Cross-post helpers live in xhs_common.py.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from xhs_common import (
    ACCENT, BG_DARK, H, W, WHITE,
    cn_locale, fit_cover, make_anatomy_grid, make_compare_slide,
    render_how_slide, render_outro_slide,
)

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets" / "social" / "post1-bieber"
OUT.mkdir(parents=True, exist_ok=True)

LAYERS = REPO / "assets" / "showcase" / "layers_v2"
ORIGS = REPO / "assets" / "showcase" / "originals"

LOC = cn_locale()
font = LOC.font


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
        LOC,
        ORIGS / "bieber-coachella-stayed.png",
        LAYERS / "bieber-coachella-stayed" / "bieber.png",
        "提取 · 人物", "subject extraction · pose 1",
        "AI 单独拆出人物", "background removed automatically",
    )
    c.save(OUT / "02-stayed-subject.png", quality=95)
    print("✓ 02-stayed-subject.png")


def slide_03_stayed_bg():
    c = make_compare_slide(
        LOC,
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
        LOC,
        ORIGS / "bieber-coachella-baby.png",
        LAYERS / "bieber-coachella-baby" / "bieber.png",
        "正脸 · 人物", "frontal view · pose 2",
        "正脸也能拆出来", "frontal face, same pipeline",
    )
    c.save(OUT / "04-baby-subject.png", quality=95)
    print("✓ 04-baby-subject.png")


def slide_05_face_anatomy():
    """6-panel grid: 五官 multi-level decomposition from face-only source."""
    parts = [
        ("bieber__skin.png",     "皮肤",    "skin"),
        ("bieber__hair.png",     "头发",    "hair"),
        ("bieber__eyebrows.png", "眉毛",    "eyebrows"),
        ("bieber__nose.png",     "鼻子",    "nose"),
        ("bieber__ears.png",     "耳朵",    "ears"),
        ("bieber.png",           "合成",    "all parts"),
    ]
    make_anatomy_grid(
        LOC, OUT / "05-face-anatomy.png",
        LAYERS / "bieber-baby-faceonly", parts, highlight_idx=len(parts) - 1,
        top_title="五官自动解剖", top_sub="face parts · one photo",
        bot_text="SegFormer 一次拆出 10 层", bot_sub="zero manual annotation",
    )
    print("✓ 05-face-anatomy.png")


def slide_06_sd_subject():
    c = make_compare_slide(
        LOC,
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
        LOC,
        ORIGS / "bieber-coachella-speed-demon.png",
        LAYERS / "bieber-coachella-speed-demon" / "red_stage.png",
        "提取 · 红色舞台", "red stage · pose 3",
        "红色灯光单独剥离", "red-lit stage isolated",
        layer_use_photo_bg=True,
    )
    c.save(OUT / "07-sd-bg.png", quality=95)
    print("✓ 07-sd-bg.png")


def slide_08_how():
    render_how_slide(OUT / "08-how.png", LOC, {
        "title": "怎么做到的?",
        "subtitle": "how it was made",
        "brand": "Claude Code  +  Vulca",
        "steps": [
            ("① Claude 读图", "agent looks at the photo"),
            ("② Claude 写 plan", "agent authors JSON plan"),
            ("③ Vulca SDK 自动拆层", "SDK runs YOLO+DINO+SAM+SegFormer"),
            ("④ 结果回到 Claude 核查", "agent checks manifest + flags"),
        ],
        "tag": "零人工抠图",
    })
    print("✓ 08-how.png")


def slide_09_outro():
    render_outro_slide(OUT / "09-outro.png", LOC, {
        "layers_label": "个图层",
        "hr_main": "47 张图 · 全自动解构",
        "credit_lines": [
            "Claude Code 指挥 · Vulca SDK 执行",
            "YOLO + DINO + SAM + SegFormer",
            "hierarchical resolve · residual honesty",
        ],
        "cta": "想看更多?  评论区告诉我",
    })
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
