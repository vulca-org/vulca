#!/usr/bin/env python3
"""Generate demo GIFs for README from v2 assets. PIL only — no moviepy.

Usage:
    cd vulca && .venv/bin/python scripts/generate-demo-gifs.py

Generates:
    assets/demo/v2/gif-create.gif      — create workflow
    assets/demo/v2/gif-evaluate.gif    — evaluate 3 modes
    assets/demo/v2/gif-layers.gif      — layers V2 decomposition
    assets/demo/v2/gif-full.gif        — complete showcase
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540  # Half HD for reasonable GIF size
BG = (15, 13, 11)
ACCENT = (0, 90, 180)
GREEN = (130, 220, 130)
BLUE = (100, 200, 255)
WHITE = (255, 255, 255)
MUTED = (136, 136, 136)

BASE = Path(__file__).parent.parent / "assets" / "demo" / "v2"
OUT = BASE

# Try to load fonts
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
MONO_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def _load_font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT = _load_font(FONT_PATHS, 20)
FONT_LG = _load_font(FONT_PATHS, 32)
FONT_XL = _load_font(FONT_PATHS, 48)
MONO = _load_font(MONO_PATHS, 16)
MONO_SM = _load_font(MONO_PATHS, 14)


def _frame(duration_ms=2000):
    """Create a blank frame."""
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img), duration_ms


def _title_frame(title, subtitle="", duration_ms=3000):
    """Full-screen title card."""
    img, draw, dur = _frame(duration_ms)
    tw = draw.textlength(title, font=FONT_XL)
    draw.text(((W - tw) / 2, H / 2 - 40), title, font=FONT_XL, fill=WHITE)
    if subtitle:
        sw = draw.textlength(subtitle, font=FONT)
        draw.text(((W - sw) / 2, H / 2 + 30), subtitle, font=FONT, fill=MUTED)
    return img, dur


def _code_frame(lines, title="", duration_ms=4000):
    """Terminal-style code frame."""
    img, draw, dur = _frame(duration_ms)

    # Terminal background
    pad = 30
    tw, th = W - 80, len(lines) * 22 + pad * 2 + 10
    tx, ty = 40, 50
    draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=8, fill=(25, 25, 30))

    # Terminal dots
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse((tx + 12 + i * 18, ty + 8, tx + 22 + i * 18, ty + 18), fill=c)

    # Lines
    y = ty + pad + 5
    for line in lines:
        color = (220, 220, 220)
        if line.startswith("$"):
            color = GREEN
        elif "%" in line and ("█" in line or "░" in line):
            color = BLUE
        elif "✓" in line:
            color = (100, 255, 100)
        elif line.startswith("#"):
            color = MUTED
        elif "→" in line or "Score" in line:
            color = (255, 200, 100)
        draw.text((tx + pad, y), line, font=MONO_SM, fill=color)
        y += 22

    # Title bar
    if title:
        draw.rectangle([0, H - 40, W, H], fill=ACCENT)
        draw.text((20, H - 35), title, font=FONT, fill=WHITE)

    return img, dur


def _image_frame(img_path, title="", subtitle="", duration_ms=3000):
    """Show an image centered."""
    frame, draw, dur = _frame(duration_ms)

    if Path(img_path).exists():
        art = Image.open(img_path).convert("RGB")
        # Scale to fit
        max_w, max_h = W - 60, H - 120
        scale = min(max_w / art.width, max_h / art.height)
        new_w, new_h = int(art.width * scale), int(art.height * scale)
        art = art.resize((new_w, new_h), Image.LANCZOS)
        x, y = (W - new_w) // 2, (H - 100 - new_h) // 2 + 20
        frame.paste(art, (x, y))

    if title:
        draw.rectangle([0, H - 40, W, H], fill=ACCENT)
        draw.text((20, H - 35), title, font=FONT, fill=WHITE)
    if subtitle:
        draw.text((20, H - 65), subtitle, font=MONO_SM, fill=MUTED)

    return frame, dur


def _multi_image_frame(paths, title="", duration_ms=3000):
    """Show multiple images in a row."""
    frame, draw, dur = _frame(duration_ms)
    n = len(paths)
    if n == 0:
        return frame, dur

    gap = 10
    slot_w = (W - 60 - gap * (n - 1)) // n
    max_h = H - 120

    x = 30
    for p in paths:
        if Path(p).exists():
            art = Image.open(p).convert("RGB")
            scale = min(slot_w / art.width, max_h / art.height)
            new_w, new_h = int(art.width * scale), int(art.height * scale)
            art = art.resize((new_w, new_h), Image.LANCZOS)
            y = (H - 80 - new_h) // 2 + 20
            frame.paste(art, (x + (slot_w - new_w) // 2, y))
        x += slot_w + gap

    if title:
        draw.rectangle([0, H - 40, W, H], fill=ACCENT)
        draw.text((20, H - 35), title, font=FONT, fill=WHITE)

    return frame, dur


def _save_gif(frames, output_path, loop=0):
    """Save frames as optimized GIF."""
    images = [f[0].quantize(colors=128, method=2) for f in frames]
    durations = [f[1] for f in frames]
    images[0].save(
        str(output_path),
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=loop,
        optimize=True,
    )
    size_kb = Path(output_path).stat().st_size / 1024
    print(f"  {output_path.name}: {size_kb:.0f}KB ({len(frames)} frames)")


# ===========================================================================
# GIF Scenes
# ===========================================================================

def gif_create():
    """Create workflow showcase."""
    frames = []
    frames.append(_title_frame("VULCA — Create", "One command, cultural art", 2500))
    frames.append(_multi_image_frame(
        [str(BASE / "hero-xieyi.png"), str(BASE / "hero-japanese.png"), str(BASE / "hero-brand.png")],
        title="Chinese Xieyi  |  Japanese Traditional  |  Brand Design",
        duration_ms=4000,
    ))
    frames.append(_code_frame([
        '$ vulca create "Misty mountains" -t chinese_xieyi -o art.png',
        "",
        "  Session:   6577ab31",
        "  Tradition: chinese_xieyi",
        "  Rounds:    1",
        "  Image:     art.png",
        "  Score:     0.915",
        "  Latency:   43s | Cost: $0.067",
    ], title="Create — Score 91.5% in One Round", duration_ms=4000))
    frames.append(_title_frame("pip install vulca", "13 traditions | 1104 tests", 2000))
    _save_gif(frames, OUT / "gif-create.gif")


def gif_evaluate():
    """Evaluate 3 modes showcase."""
    frames = []
    frames.append(_title_frame("VULCA — Evaluate", "Judge | Advisor | Cross-Cultural", 2000))
    frames.append(_code_frame([
        "$ vulca evaluate artwork.png -t chinese_xieyi",
        "",
        "  Score:     90%   Tradition: chinese_xieyi   Risk: low",
        "",
        "  L1 Visual Perception         ██████████████████░░ 90%  ✓",
        "  L2 Technical Execution       █████████████████░░░ 85%  ✓",
        "  L3 Cultural Context          ██████████████████░░ 90%  ✓",
        "  L4 Critical Interpretation   ████████████████████ 100% ✓",
        "  L5 Philosophical Aesthetics  ██████████████████░░ 90%  ✓",
    ], title="Strict Mode — Judge with Scores", duration_ms=4000))
    frames.append(_code_frame([
        "$ vulca evaluate artwork.png -t chinese_xieyi --mode reference",
        "",
        "  L2 Technical Execution  85%  (traditional)",
        '     Explore texture strokes: axe-cut (斧劈皴)',
        '     for sharper rocks, rain-drop (雨点皴)',
        "     for rounded forms...",
        "",
        "  L3 Cultural Context  95%  (traditional)",
        '     Add a poem (题画诗) for poetry-calligraphy-',
        '     painting-seal (诗书画印) harmony...',
    ], title="Reference Mode — Advisor with Cultural Terminology", duration_ms=5000))
    frames.append(_code_frame([
        "$ vulca evaluate artwork.png \\",
        "    -t chinese_xieyi,japanese_traditional,western_academic \\",
        "    --mode fusion",
        "",
        "  Dimension              Chinese  Japanese  Western",
        "  Visual Perception        90%      90%       10%",
        "  Cultural Context         95%      80%        0%",
        "  Overall Alignment        93%      90%        8%",
        "",
        "  → Closest: chinese_xieyi (93%)",
    ], title="Fusion Mode — Cross-Cultural Comparison", duration_ms=4000))
    _save_gif(frames, OUT / "gif-evaluate.gif")


def gif_layers():
    """Layers V2 decomposition showcase."""
    frames = []
    frames.append(_title_frame("VULCA Layers V2", "Full-canvas RGBA | Blend Modes | Edit", 2000))
    frames.append(_image_frame(
        str(BASE / "hero-xieyi.png"),
        title="Original Artwork (1024x1024)",
        duration_ms=2500,
    ))
    # Show individual layers
    layer_dir = BASE / "layers-split"
    layer_files = sorted(layer_dir.glob("*.png"))
    if layer_files:
        frames.append(_multi_image_frame(
            [str(f) for f in layer_files[:3]],
            title="Layers 0-2: background | mountains | mist",
            duration_ms=3000,
        ))
        frames.append(_multi_image_frame(
            [str(f) for f in layer_files[3:6]],
            title="Layers 3-5: landscape | pavilion | calligraphy",
            duration_ms=3000,
        ))
    frames.append(_image_frame(
        str(BASE / "layers-composite.png"),
        title="Composite — All 6 Layers Blended Back",
        duration_ms=2500,
    ))
    frames.append(_code_frame([
        "$ vulca layers split artwork.png -o ./layers/ --mode regenerate",
        "  [0] background_paper       → full-canvas RGBA",
        "  [1] distant_mountains      → full-canvas RGBA",
        "  [2] mist_and_clouds        → full-canvas RGBA",
        "  [3] midground_landscape    → full-canvas RGBA",
        "  [4] pavilion_and_pine_trees → full-canvas RGBA",
        "  [5] calligraphy_and_seals  → full-canvas RGBA",
        "",
        "$ vulca layers redraw ./layers/ --layer sky -i 'add sunset'",
        "$ vulca layers merge ./layers/ --layers fg,mid --name merged",
        "$ vulca layers composite ./layers/ -o final.png",
    ], title="14 Subcommands: analyze | split | edit | redraw | composite | export", duration_ms=5000))
    _save_gif(frames, OUT / "gif-layers.gif")


def gif_full():
    """Complete showcase — all features."""
    frames = []

    # Title
    frames.append(_title_frame("VULCA", "AI-native cultural art creation organism", 3000))

    # Hero
    frames.append(_multi_image_frame(
        [str(BASE / "hero-xieyi.png"), str(BASE / "hero-japanese.png"), str(BASE / "hero-brand.png")],
        title="Create — 13 Cultural Traditions",
        duration_ms=3500,
    ))

    # Evaluate
    frames.append(_code_frame([
        "$ vulca evaluate artwork.png -t chinese_xieyi",
        "",
        "  Score: 90%  Risk: low",
        "  L1 ██████████████████░░ 90%  ✓  Visual Perception",
        "  L2 █████████████████░░░ 85%  ✓  Technical Execution",
        "  L3 ██████████████████░░ 90%  ✓  Cultural Context",
        "  L4 ████████████████████ 100% ✓  Critical Interpretation",
        "  L5 ██████████████████░░ 90%  ✓  Philosophical Aesthetics",
    ], title="Evaluate — L1-L5 Cultural Scoring", duration_ms=4000))

    # Layers
    layer_dir = BASE / "layers-split"
    layer_files = sorted(layer_dir.glob("*.png"))
    if len(layer_files) >= 4:
        frames.append(_multi_image_frame(
            [str(BASE / "hero-xieyi.png")] + [str(f) for f in layer_files[:2]] + [str(BASE / "layers-composite.png")],
            title="Layers V2 — Split → Edit → Composite",
            duration_ms=4000,
        ))

    # Tools
    frames.append(_code_frame([
        "$ vulca tools run brushstroke_analyze -t chinese_xieyi",
        "  Energy: 0.87 — aligns with expressive style  ✓",
        "",
        "$ vulca tools run whitespace_analyze -t chinese_xieyi",
        "  Whitespace: 32.8% — in ideal range (30%-55%)  ✓",
        "",
        "$ vulca tools run composition_analyze -t chinese_xieyi",
        "  Thirds: 0.75 — asymmetric, dynamic  ✓",
        "",
        "# 5 tools, zero API cost, instant results",
    ], title="Tools — Algorithmic Analysis (No API Required)", duration_ms=4000))

    # Studio
    frames.append(_code_frame([
        "$ vulca studio 'Cyberpunk ink wash' --provider gemini --auto",
        "",
        "  Style: chinese_xieyi (50%) + cyberpunk (50%)",
        "  Concepts: 4 generated (831-921KB)",
        "",
        "  L1 ███████████████████░ 95%",
        "  L2 ██████████████████░░ 90%",
        "  L4 ████████████████████ 100%",
        "",
        "  Score: 93% → Accepted (round 1/2)",
    ], title="Studio — Brief-Driven Creative Session", duration_ms=4000))

    # Evolution
    frames.append(_code_frame([
        "$ vulca evolution chinese_xieyi",
        "",
        "  Dim     Original  Evolved   Change",
        "  L1        10.0%    10.0%   +  0.0%",
        "  L2        15.0%    20.0%   +  5.0%  ← strengthened",
        "  L3        25.0%    35.0%   + 10.0%  ← most evolved",
        "  L4        20.0%    15.0%   -  5.0%",
        "  L5        30.0%    20.0%   - 10.0%",
        "  Sessions: 71",
    ], title="Self-Evolution — Weights Adapt from 1100+ Sessions", duration_ms=4000))

    # Outro
    frames.append(_title_frame(
        "pip install vulca",
        "1104 tests | 21 MCP tools | 13 traditions | Apache 2.0",
        3000,
    ))

    _save_gif(frames, OUT / "gif-full.gif")


def main():
    print("Generating VULCA demo GIFs...")
    print(f"Output: {OUT}/")
    print()

    gif_create()
    gif_evaluate()
    gif_layers()
    gif_full()

    print()
    total = sum(f.stat().st_size for f in OUT.glob("gif-*.gif")) / 1024
    print(f"Total GIF size: {total:.0f}KB")
    print("Done!")


if __name__ == "__main__":
    main()
