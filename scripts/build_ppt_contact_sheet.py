from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_contact_sheet(slides: list[Path], out: Path, title: str, *, cols: int = 3) -> None:
    if not slides:
        raise ValueError("at least one slide PNG is required")

    thumb_w, thumb_h = 640, 360
    margin = 28
    title_h = 58
    label_h = 28
    rows = (len(slides) + cols - 1) // cols
    sheet_w = cols * thumb_w + (cols + 1) * margin
    sheet_h = title_h + rows * (thumb_h + label_h) + (rows + 1) * margin

    sheet = Image.new("RGB", (sheet_w, sheet_h), "#f4f2ed")
    draw = ImageDraw.Draw(sheet)
    title_font = load_font(28, bold=True)
    label_font = load_font(16, bold=True)
    draw.text((margin, 18), title, fill="#17181c", font=title_font)

    for idx, slide_path in enumerate(slides):
        src = Image.open(slide_path).convert("RGB")
        src.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        col = idx % cols
        row = idx // cols
        x = margin + col * (thumb_w + margin)
        y = title_h + margin + row * (thumb_h + label_h + margin)
        frame = Image.new("RGB", (thumb_w, thumb_h), "#ffffff")
        frame.paste(src, ((thumb_w - src.width) // 2, (thumb_h - src.height) // 2))
        sheet.paste(frame, (x, y))
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline="#c8c4b8", width=1)
        draw.text((x, y + thumb_h + 7), f"Slide {idx + 1:02d}", fill="#626a73", font=label_font)

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a PNG contact sheet from rendered presentation slides.")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument("slides", nargs="+", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_contact_sheet(args.slides, args.out, args.title, cols=max(1, args.cols))
    print(f"created contact sheet: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
