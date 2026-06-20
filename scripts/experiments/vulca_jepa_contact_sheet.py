#!/usr/bin/env python3
"""Generate a visual contact sheet from a Vulca JEPA inventory."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BG = "#0d1117"
PANEL = "#161b22"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
ERROR = "#f85149"
WARN = "#f0883e"


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _fit_image(path: Path, size: int) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), PANEL)
    checker = Image.new("RGB", image.size, "#22272e")
    tile = 12
    for y in range(0, image.size[1], tile):
        for x in range(0, image.size[0], tile):
            if ((x // tile) + (y // tile)) % 2:
                checker.paste("#30363d", (x, y, min(x + tile, image.size[0]), min(y + tile, image.size[1])))
    checker.paste(image, (0, 0), image)
    offset = ((size - image.size[0]) // 2, (size - image.size[1]) // 2)
    canvas.paste(checker, offset)
    return canvas


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    max_chars: int,
    max_lines: int,
    line_height: int,
) -> None:
    lines = textwrap.wrap(text, width=max_chars, break_long_words=True)[:max_lines]
    x, y = xy
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * line_height), line, fill=fill, font=font)


def make_contact_sheet(
    inventory_path: Path | str,
    out: Path | str,
    *,
    tile_size: int = 192,
    columns: int = 5,
    audit_set: str | None = None,
) -> Path:
    inv_path = Path(inventory_path)
    output_path = Path(out)
    inventory = json.loads(inv_path.read_text())
    repo_root = Path(inventory.get("repo_root") or ".")
    samples = [sample for sample in inventory["samples"] if sample.get("exists")]
    if audit_set:
        samples = [sample for sample in samples if sample.get("audit_set") == audit_set]
    samples = sorted(
        samples,
        key=lambda sample: (
            0 if sample.get("audit_set") == "core" else 1,
            str(sample.get("group", "")),
            str(sample.get("sample_id", "")),
        ),
    )

    label_h = 82
    pad = 12
    header_h = 72
    cell_w = tile_size
    cell_h = tile_size + label_h
    rows = max(1, (len(samples) + columns - 1) // columns)
    width = columns * cell_w + (columns + 1) * pad
    height = header_h + rows * cell_h + (rows + 1) * pad
    sheet = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(sheet)
    font = _load_font(12)
    small = _load_font(11)
    title = _load_font(17)

    title_suffix = f" ({audit_set})" if audit_set else ""
    draw.text((pad, 12), f"Vulca JEPA visual audit sample pack{title_suffix}", fill=ACCENT, font=title)
    audit_sets = inventory.get("audit_sets", {})
    audit_summary = ", ".join(f"{key}={value}" for key, value in audit_sets.items()) or "unclassified"
    summary = (
        f"shown={len(samples)} samples={inventory['samples_total']} missing={inventory['missing_total']} "
        f"audit_sets={audit_summary}"
    )
    draw.text((pad, 40), summary, fill=TEXT, font=font)

    for idx, sample in enumerate(samples):
        row, col = divmod(idx, columns)
        x = pad + col * (cell_w + pad)
        y = header_h + pad + row * (cell_h + pad)
        path = repo_root / sample["path"]
        try:
            tile = _fit_image(path, tile_size)
            sheet.paste(tile, (x, y))
        except Exception as exc:
            draw.rectangle((x, y, x + tile_size, y + tile_size), fill=PANEL)
            draw.text((x + 6, y + 6), f"ERR: {exc}", fill=ERROR, font=small)

        draw.text((x, y + tile_size + 6), sample["sample_id"][:34], fill=TEXT, font=font)
        set_label = sample.get("audit_set", "unclassified")
        set_color = ACCENT if set_label == "core" else WARN
        draw.text((x, y + tile_size + 24), f"{sample['group']} · {set_label}", fill=set_color, font=small)
        size_label = f"{sample.get('width')}x{sample.get('height')} {sample.get('mode')}"
        draw.text((x, y + tile_size + 40), size_label, fill=MUTED, font=small)
        if sample.get("reject_reasons"):
            reason = ",".join(sample["reject_reasons"])
            draw.text((x, y + tile_size + 56), reason[:34], fill=WARN, font=small)
            purpose_y = y + tile_size + 68
            max_lines = 1
        else:
            purpose_y = y + tile_size + 56
            max_lines = 2
        _draw_wrapped_text(
            draw,
            (x, purpose_y),
            sample.get("purpose", ""),
            small,
            MUTED,
            max_chars=30,
            max_lines=max_lines,
            line_height=12,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Inventory JSON path.")
    parser.add_argument("--out", required=True, type=Path, help="Contact sheet PNG output path.")
    parser.add_argument("--tile-size", type=int, default=192)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--audit-set", choices=("core", "artifact_qa"), help="Only render one audit set.")
    args = parser.parse_args(argv)

    out = make_contact_sheet(
        args.manifest,
        args.out,
        tile_size=args.tile_size,
        columns=args.columns,
        audit_set=args.audit_set,
    )
    inventory = json.loads(args.manifest.read_text())
    shown = inventory["samples_total"] - inventory["missing_total"]
    if args.audit_set:
        shown = sum(
            1
            for sample in inventory["samples"]
            if sample.get("exists") and sample.get("audit_set") == args.audit_set
        )
    print(f"wrote {out}")
    print(f"tiles: {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
