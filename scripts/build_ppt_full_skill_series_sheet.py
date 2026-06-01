from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class SheetItem:
    label: str
    path: Path


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


def parse_item(value: str) -> SheetItem:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--item must use LABEL=PATH")
    label, raw_path = value.split("=", 1)
    label = label.strip()
    path = Path(raw_path.strip())
    if not label:
        raise argparse.ArgumentTypeError("--item label cannot be empty")
    if not path.exists():
        raise argparse.ArgumentTypeError(f"--item path does not exist: {path}")
    return SheetItem(label=label, path=path)


def fitted_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, *, start_size: int, bold: bool) -> ImageFont.ImageFont:
    size = start_size
    while size > 10:
        font = load_font(size, bold=bold)
        text_width = draw.textbbox((0, 0), text, font=font)[2]
        if text_width <= max_width:
            return font
        size -= 1
    return load_font(10, bold=bold)


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * (width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def build_series_sheet(
    items: list[SheetItem],
    out: Path,
    *,
    title: str,
    item_width: int,
    margin: int,
    gap: int,
) -> None:
    if not items:
        raise ValueError("at least one --item is required")

    title_h = 68
    label_h = 46
    resized: list[Image.Image] = []
    for item in items:
        resized.append(resize_to_width(Image.open(item.path).convert("RGB"), item_width))

    max_image_h = max(image.height for image in resized)
    sheet_w = margin * 2 + len(items) * item_width + (len(items) - 1) * gap
    sheet_h = title_h + label_h + max_image_h + margin * 2
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#f4f2ed")
    draw = ImageDraw.Draw(sheet)

    title_font = load_font(28, bold=True)
    label_font = load_font(15, bold=True)
    small_font = load_font(11)
    draw.text((margin, 22), title, fill="#17181c", font=title_font)

    y_label = title_h + margin // 2
    y_image = y_label + label_h
    for index, (item, image) in enumerate(zip(items, resized, strict=True)):
        x = margin + index * (item_width + gap)
        draw.rounded_rectangle(
            (x, y_label, x + item_width, y_label + label_h - 8),
            radius=4,
            fill="#17181c",
        )
        fit_font = fitted_font(draw, item.label, item_width - 24, start_size=15, bold=True)
        draw.text((x + 12, y_label + 10), item.label, fill="#ffffff", font=fit_font)
        frame = Image.new("RGB", (item_width, max_image_h), "#ffffff")
        frame.paste(image, (0, (max_image_h - image.height) // 2))
        sheet.paste(frame, (x, y_image))
        draw.rectangle((x, y_image, x + item_width, y_image + max_image_h), outline="#c8c4b8", width=1)
        draw.text((x + 12, y_image + max_image_h - 22), item.path.name, fill="#626a73", font=small_font)

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a horizontal PPT comparison sheet from labeled PNG inputs.")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--title", default="PPT full skill series")
    parser.add_argument("--item-width", type=int, default=520)
    parser.add_argument("--margin", type=int, default=32)
    parser.add_argument("--gap", type=int, default=28)
    parser.add_argument("--item", action="append", required=True, type=parse_item)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_series_sheet(
        args.item,
        args.out,
        title=args.title,
        item_width=args.item_width,
        margin=args.margin,
        gap=args.gap,
    )
    print(f"created comparison sheet: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
