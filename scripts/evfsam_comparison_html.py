#!/usr/bin/env python3
"""Generate comparison HTML: baseline extract vs EVF-SAM for all 8 images."""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
EXP_DIR = REPO / "assets" / "showcase" / "experiments" / "evfsam_all"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
LAYER_DIR = REPO / "assets" / "showcase" / "layers"  # baseline extract outputs
OUT = REPO / "assets" / "showcase" / "experiments" / "evfsam_comparison.html"

TITLES = {
    "earthrise": "Earthrise (NASA, 1968)",
    "migrant-mother": "Migrant Mother (Lange, 1936)",
    "starry-night": "The Starry Night (Van Gogh, 1889)",
    "girl-pearl-earring": "Girl with a Pearl Earring (Vermeer, 1665)",
    "water-lilies": "Water Lilies (Monet, 1906)",
    "great-wave": "The Great Wave (Hokusai, 1831)",
    "qingming-bridge": "Along the River (Zhang Zeduan, 1100s)",
    "padmapani": "Padmapani (Ajanta Cave 1, 5th c.)",
}


def to_uri(path: Path, max_w: int = 500) -> str:
    if not path.exists():
        return ""
    im = Image.open(path)
    r = max_w / max(im.size)
    if r < 1:
        im = im.resize((int(im.size[0] * r), int(im.size[1] * r)), Image.LANCZOS)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (255, 0, 0, 255))
        bg.paste(im, mask=im)
        im = bg.convert("RGB")
    elif im.mode != "RGB":
        im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=82)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"


def main():
    prompts_path = EXP_DIR.parent / "evfsam_prompts.json"
    stats_path = EXP_DIR / "stats.json"
    if not prompts_path.exists():
        raise SystemExit(f"Missing prompts config: {prompts_path}")
    if not stats_path.exists():
        raise SystemExit(f"Missing stats: {stats_path} — run evfsam_showcase.py first")
    prompts = json.loads(prompts_path.read_text())
    stats = json.loads(stats_path.read_text())

    html = ['<!DOCTYPE html><html><head><meta charset="UTF-8">',
            '<title>EVF-SAM Showcase — All 8 Images</title>',
            '<style>',
            'body{background:#0d1117;color:#c9d1d9;font-family:system-ui;padding:2rem;max-width:1700px;margin:0 auto;}',
            'h1{color:#58a6ff;}h2{color:#f0f6fc;margin-top:2rem;border-top:1px solid #30363d;padding-top:1rem;}',
            '.row{display:grid;grid-template-columns:180px repeat(3,1fr);gap:0.8rem;align-items:center;margin:0.5rem 0;}',
            '.orig{width:100%;max-width:180px;border-radius:6px;border:1px solid #30363d;}',
            '.layer{width:100%;border-radius:6px;border:1px solid #30363d;}',
            '.tag{display:inline-block;background:#1f6feb22;color:#58a6ff;padding:0.15rem 0.5rem;border-radius:1rem;font-size:0.7rem;margin-right:0.4rem;}',
            '.layerlabel{font-size:0.75rem;color:#8b949e;text-align:center;margin-top:0.3rem;}',
            '.prompt{font-size:0.7rem;color:#8b949e;font-style:italic;text-align:center;margin-top:0.2rem;}',
            '.stats{font-size:0.7rem;color:#f78166;text-align:center;}',
            '.info{color:#8b949e;font-size:0.85rem;margin-bottom:0.5rem;}',
            '</style></head><body>',
            '<h1>EVF-SAM Text-Prompted Layer Decomposition</h1>',
            f'<p>8 images × 3 prompts (background / subject / foreground). Red = transparent. Total: 94s on MPS.</p>']

    for stem, title in TITLES.items():
        orig_uri = to_uri(ORIG_DIR / f"{stem}.jpg", 200)
        img_prompts = prompts.get(stem, [])
        img_stats = stats.get(stem, {}).get("layers", {})

        html.append(f'<h2>{title}</h2>')
        html.append('<div class="row">')
        html.append(f'<div><img src="{orig_uri}" class="orig"><div class="layerlabel">Original</div></div>')

        for layer_name, prompt in img_prompts:
            p = EXP_DIR / stem / f"{layer_name}_on_red.png"
            uri = to_uri(p, 500)
            layer_stat = img_stats.get(layer_name, {})
            cov = layer_stat.get("coverage_pct", "?")
            t = layer_stat.get("inference_s", "?")
            html.append(f'<div>')
            if uri:
                html.append(f'<img src="{uri}" class="layer">')
            else:
                html.append('<div style="color:#f44336">MISSING</div>')
            html.append(f'<div class="layerlabel"><span class="tag">{layer_name}</span>{cov}% · {t}s</div>')
            html.append(f'<div class="prompt">"{prompt}"</div>')
            html.append('</div>')
        html.append('</div>')

    html.append('</body></html>')
    OUT.write_text('\n'.join(html))
    size_kb = len('\n'.join(html)) // 1024
    print(f"Written to {OUT} ({size_kb}KB)")


if __name__ == "__main__":
    main()
