#!/usr/bin/env python3
"""Generate a QA contact sheet for an orchestrated slug.

The contact sheet is a single JPEG grid: original image + all layer masks.
Claude (as orchestrator) reads it and outputs structured QA JSON.

Usage:
  python scripts/claude_qa_contact_sheet.py <slug>

Output:
  assets/showcase/layers_v2/<slug>/qa_contact_sheet.jpg
  assets/showcase/layers_v2/<slug>/qa_prompt.md   # instructions for Claude
"""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
LAYERS_DIR = REPO / "assets" / "showcase" / "layers_v2"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"

CELL_W = 320
CELL_H = 320
COLS = 4
PAD = 8


def make_sheet(slug: str) -> Path:
    layer_dir = LAYERS_DIR / slug
    mf = layer_dir / "manifest.json"
    if not mf.exists():
        raise FileNotFoundError(mf)
    manifest = json.loads(mf.read_text())
    layers = sorted(manifest["layers"], key=lambda x: x["z_index"])

    # Cells: [original] + [each layer]
    n_cells = 1 + len(layers)
    rows = (n_cells + COLS - 1) // COLS
    sheet_w = COLS * CELL_W + (COLS + 1) * PAD
    sheet_h = rows * (CELL_H + 32) + (rows + 1) * PAD + 40
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#0d1117")
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        font_big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except Exception:
        font = ImageFont.load_default()
        font_big = font

    # Header
    status = manifest.get("status", "ok")
    dr = manifest.get("detection_report", {})
    draw.text((PAD, 4),
              f"{slug} | {len(layers)} layers | status={status} | detected {dr.get('detected','?')}/{dr.get('requested','?')}",
              fill="#58a6ff", font=font_big)

    def place(idx, img_path, label):
        r, c = divmod(idx, COLS)
        x0 = PAD + c * (CELL_W + PAD)
        y0 = 40 + PAD + r * (CELL_H + 32 + PAD)
        try:
            im = Image.open(img_path).convert("RGBA")
            im.thumbnail((CELL_W, CELL_H))
            # Checkerboard behind for transparency visibility
            bg = Image.new("RGB", im.size, "#262c36")
            tile = 16
            for by in range(0, im.size[1], tile):
                for bx in range(0, im.size[0], tile):
                    if ((bx // tile) + (by // tile)) % 2:
                        bg.paste("#161b22", (bx, by, bx + tile, by + tile))
            bg.paste(im, (0, 0), im)
            offset = ((CELL_W - bg.size[0]) // 2, (CELL_H - bg.size[1]) // 2)
            sheet.paste(bg, (x0 + offset[0], y0 + offset[1]))
        except Exception as e:
            draw.text((x0 + 4, y0 + 4), f"ERR: {e}", fill="#f85149", font=font)
        draw.text((x0, y0 + CELL_H + 2), label[:40], fill="#c9d1d9", font=font)

    # Cell 0: original
    place(0, ORIG_DIR / f"{slug}.jpg", f"[original] {manifest['width']}x{manifest['height']}")
    # Cells 1..N: layers
    for i, layer in enumerate(layers, 1):
        label = f"z{layer['z_index']} · {layer['name']}"
        place(i, layer_dir / layer["file"], label)

    out = layer_dir / "qa_contact_sheet.jpg"
    sheet.save(str(out), quality=85)
    return out


def make_qa_prompt(slug: str) -> Path:
    layer_dir = LAYERS_DIR / slug
    manifest = json.loads((layer_dir / "manifest.json").read_text())
    layers = sorted(manifest["layers"], key=lambda x: x["z_index"])
    dr = manifest.get("detection_report", {})

    prompt = textwrap.dedent(f"""\
    # QA Review Task — {slug}

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `{manifest.get("plan",{}).get("domain","?")}`
    - Layers produced: {len(layers)}
    - Status: `{manifest.get("status","ok")}` ({dr.get("detected","?")}/{dr.get("requested","?")} detected)

    ## Layers
    {chr(10).join(f"- z={l['z_index']:2d} **{l['name']}** ({l['semantic_path']})" for l in layers)}

    ## Output Format (strict JSON)

    ```json
    {{
      "overall": {{"quality": "excellent|good|fair|poor", "summary": "..."}},
      "layers": [
        {{
          "name": "<layer name>",
          "quality": "good|leak|incomplete|wrong|empty",
          "issue": "<if not good, describe briefly>",
          "fix": "<concrete suggestion, e.g. 'tighten bbox right edge', 'raise threshold to 0.3', 'merge with <other layer>'>"
        }}
      ],
      "missing_concepts": ["<things in the original that have NO layer>"],
      "recommended_reruns": [
        {{"entity": "<name>", "action": "<what to change in plan>"}}
      ]
    }}
    ```

    ## Quality Rubric
    - **good**: mask cleanly captures entity, no leaks, no holes
    - **leak**: includes pixels from neighboring objects (e.g. hands include sleeve)
    - **incomplete**: misses significant parts of entity (e.g. missed a leg)
    - **wrong**: captured the wrong thing entirely
    - **empty**: mask is nearly blank (<1% pixels)
    """)
    out = layer_dir / "qa_prompt.md"
    out.write_text(prompt)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    args = ap.parse_args()
    for slug in args.slugs:
        sheet = make_sheet(slug)
        prompt = make_qa_prompt(slug)
        print(f"[{slug}]")
        print(f"  contact sheet: {sheet}")
        print(f"  QA prompt:    {prompt}")


if __name__ == "__main__":
    main()
