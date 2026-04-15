#!/usr/bin/env python3
"""Generate an interactive HTML showcase from 8x8 showcase data."""
from __future__ import annotations

import base64
import glob
import html as html_mod
import io
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "showcase" / "showcase.html"
SHOWCASE = REPO / "assets" / "showcase"

IMAGES = ['earthrise', 'migrant-mother', 'starry-night', 'girl-pearl-earring',
          'water-lilies', 'great-wave', 'qingming-bridge', 'padmapani']
TITLES = {
    'earthrise': 'Earthrise (NASA, 1968)',
    'migrant-mother': 'Migrant Mother (Lange, 1936)',
    'starry-night': 'The Starry Night (Van Gogh, 1889)',
    'girl-pearl-earring': 'Girl with a Pearl Earring (Vermeer, 1665)',
    'water-lilies': 'Water Lilies (Monet, 1906)',
    'great-wave': 'The Great Wave (Hokusai, 1831)',
    'qingming-bridge': 'Along the River (Zhang Zeduan, 1100s)',
    'padmapani': 'Padmapani (Ajanta Cave 1, 5th c.)',
}
TRADITIONS = {
    'earthrise': 'photography', 'migrant-mother': 'photography',
    'starry-night': 'western_academic', 'girl-pearl-earring': 'western_academic',
    'water-lilies': 'western_academic', 'great-wave': 'japanese_traditional',
    'qingming-bridge': 'chinese_gongbi', 'padmapani': 'south_asian',
}

# Build tradition allowlist from YAML files on disk (no hardcoded list)
_TRADITIONS_DIR = REPO / "src" / "vulca" / "cultural" / "data" / "traditions"
_VALID_TRADITIONS = {
    p.stem for p in _TRADITIONS_DIR.glob("*.yaml")
    if not p.stem.startswith("_") and p.stem != "schema"
} if _TRADITIONS_DIR.exists() else set()


def esc(text: str) -> str:
    """Escape text for safe HTML embedding."""
    return html_mod.escape(str(text)) if text else ""


def img_to_data_uri(path: str, max_kb: int = 200) -> str:
    """Convert image to data URI, resize if too large."""
    p = Path(path)
    if not p.exists():
        return ""
    is_png = p.suffix.lower() == ".png"
    size = p.stat().st_size
    if size > max_kb * 1024:
        try:
            from PIL import Image
            img = Image.open(p)
            ratio = 400 / max(img.size)
            if ratio < 1:
                img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
            buf = io.BytesIO()
            if is_png and img.mode == "RGBA":
                # Composite RGBA onto dark background before JPEG conversion
                bg = Image.new("RGBA", img.size, (34, 34, 34, 255))
                bg.paste(img, mask=img)
                bg.convert("RGB").save(buf, format="JPEG", quality=70)
            else:
                img.convert("RGB").save(buf, format="JPEG", quality=70)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/jpeg;base64,{b64}"
        except ImportError:
            return ""  # Skip oversized images without PIL
        except Exception as exc:
            print(f"Warning: could not resize {p}: {exc}", file=sys.stderr)
            return ""
    b64 = base64.b64encode(p.read_bytes()).decode()
    mime = "image/png" if is_png else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def load_json(path) -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        print(f"Warning: invalid JSON in {p}", file=sys.stderr)
        return None


def score_bar(score: float, label: str = "") -> str:
    pct = max(0, min(100, int(score * 100)))
    color = "#4caf50" if pct >= 80 else "#ff9800" if pct >= 60 else "#f44336"
    return (f'<div class="score-bar"><span class="score-label">{esc(label)}</span>'
            f'<div class="bar"><div class="fill" style="width:{pct}%;background:{color}"></div></div>'
            f'<span class="score-val">{pct}%</span></div>')


def _tool_card(title: str, metrics: list[tuple[str, str]], verdict: str) -> str:
    """Render an algorithmic analysis tool card."""
    out = f'<div class="tool-card"><h4>{esc(title)}</h4>'
    for label, val in metrics:
        out += f'<div class="metric">{esc(label)}: <strong>{val}</strong></div>'
    out += f'<div class="verdict">{esc(verdict[:120])}</div></div>\n'
    return out


# ── Per-image section builder ────────────────────────────────────────────

def build_image_section(img: str) -> str:
    tradition = TRADITIONS[img]
    title = TITLES[img]
    orig_path = SHOWCASE / "originals" / f"{img}.jpg"
    orig_uri = img_to_data_uri(str(orig_path))

    primary = load_json(SHOWCASE / "results" / f"{img}-primary.json")

    # Cross-tradition: match {img}-cross-{t}.json and legacy {img}-{t}.json
    # Only include files whose suffix is a valid tradition name (allowlist).
    cross: dict[str, dict] = {}
    for f in sorted(glob.glob(str(SHOWCASE / "results" / f"{img}-*.json"))):
        stem = Path(f).stem
        if stem == img:
            continue
        suffix = stem.removeprefix(f"{img}-cross-").removeprefix(f"{img}-")
        if suffix not in _VALID_TRADITIONS:
            continue
        if suffix not in cross:
            cross[suffix] = load_json(f) or {}

    # Tools
    tools: dict[str, dict] = {}
    for tool in ['brushstroke', 'whitespace', 'composition']:
        t = load_json(SHOWCASE / "tools" / f"{img}-{tool}.json")
        if t:
            tools[tool] = t

    # Layers
    manifest = load_json(SHOWCASE / "layers" / img / "manifest.json")
    layers: list[dict] = []
    layer_uris: list[str] = []
    if manifest:
        for l in manifest.get('layers', []):
            info = l.get('info', l)
            layers.append(info)
            lp = SHOWCASE / "layers" / img / f"{info.get('name', 'unknown')}.png"
            layer_uris.append(img_to_data_uri(str(lp), max_kb=150))

    comp_uri = img_to_data_uri(str(SHOWCASE / "composites" / f"{img}-composite.png"))

    # Inpaint
    inpaint_uri = img_to_data_uri(str(SHOWCASE / "inpainted" / f"{img}-inpainted.png"))

    # Re-evaluate
    reevaluate = load_json(SHOWCASE / "results" / f"{img}-reevaluate.json")

    # Translation (starry-night only)
    trans_uri = ""
    if img == "starry-night":
        trans_uri = img_to_data_uri(str(SHOWCASE / "translations" / "starry-night-xieyi.png"))

    h = f'<section class="image-section" id="{img}">\n'
    h += f'<h2>{esc(title)}</h2>\n'
    h += f'<div class="tradition-badge">{esc(tradition.replace("_", " ").title())}</div>\n'

    # ── Row 1: Original + Primary Eval ──
    h += '<div class="row">\n'
    h += f'<div class="col img-col"><img src="{orig_uri}" alt="{esc(title)}"><div class="caption">Original</div></div>\n'
    if primary:
        h += '<div class="col eval-col">\n'
        h += f'<h3>Cap 1: Primary Evaluation ({esc(tradition.replace("_", " "))})</h3>\n'
        h += score_bar(primary.get('score', 0), 'Overall')
        dim_labels = {'L1': 'Visual Perception', 'L2': 'Technical Execution',
                      'L3': 'Cultural Context', 'L4': 'Critical Interpretation',
                      'L5': 'Philosophical Aesthetics'}
        for dim, val in primary.get('dimensions', {}).items():
            h += score_bar(val, dim_labels.get(dim, dim))
        h += f'<div class="summary">{esc(primary.get("summary", ""))}</div>\n'
        rats = primary.get('rationales', {})
        if rats.get('L1'):
            h += f'<blockquote class="rationale">{esc(rats["L1"][:200])}...</blockquote>\n'
        h += '</div>\n'
    h += '</div>\n'

    # ── Row 2: Cross-tradition ──
    if cross:
        h += '<div class="subsection"><h3>Cap 2: Cross-Tradition Analysis</h3>\n'
        h += '<div class="cross-grid">\n'
        for t, ev in sorted(cross.items()):
            dims = ev.get('dimensions', {k: ev.get(k, 0) for k in ['L1', 'L2', 'L3', 'L4', 'L5'] if k in ev})
            s = ev.get('score', sum(dims.values()) / max(len(dims), 1))
            h += f'<div class="cross-card"><div class="cross-name">{esc(t.replace("_", " ").title())}</div>\n'
            h += score_bar(s, 'Score')
            for d, v in dims.items():
                h += f'<div class="mini-score">{esc(d)}: {max(0, min(100, int(v * 100)))}%</div>\n'
            h += '</div>\n'
        h += '</div></div>\n'

    # ── Row 3: Tools ──
    if tools:
        h += '<div class="subsection"><h3>Cap 3: Algorithmic Analysis</h3>\n'
        h += '<div class="tools-grid">\n'

        if 'brushstroke' in tools:
            b = tools['brushstroke']
            h += _tool_card("Brushstroke", [
                ("Energy", f'{b.get("texture_energy", 0):.2f}'),
                ("Uniformity", f'{b.get("uniformity", 0):.2f}'),
                ("Edge Density", f'{b.get("edge_density", 0):.2f}'),
            ], str(b.get("cultural_verdict", "")))
        if 'whitespace' in tools:
            w = tools['whitespace']
            h += _tool_card("Whitespace", [
                ("Ratio", f'{w.get("ratio", 0):.0%}'),
                ("Distribution", esc(str(w.get("distribution", "")))),
            ], str(w.get("cultural_verdict", "")))
        if 'composition' in tools:
            c = tools['composition']
            h += _tool_card("Composition", [
                ("Thirds", f'{c.get("thirds_alignment", 0):.2f}'),
                ("Balance", esc(str(c.get("balance", "")))),
                ("Rules", esc(", ".join(c.get("detected_rules", [])))),
            ], str(c.get("cultural_verdict", "")))
        h += '</div></div>\n'

    # ── Row 4: Layers + Composite ──
    if layers:
        h += '<div class="subsection"><h3>Cap 4: Layer Decomposition</h3>\n'
        h += '<div class="layer-strip">\n'
        for i, (info, uri) in enumerate(zip(layers, layer_uris)):
            name = info.get('name', f'layer_{i}')
            ctype = info.get('content_type', '')
            h += '<div class="layer-card">'
            if uri:
                h += f'<img src="{uri}" alt="{esc(name)}">'
            h += f'<div class="layer-name">{esc(name.replace("_", " "))}</div>'
            h += f'<div class="layer-type">z={info.get("z_index", i)} | {esc(ctype)}</div>'
            h += '</div>\n'
        h += '</div>\n'
        if comp_uri:
            h += '<div class="composite-row">'
            h += '<div class="arrow-label">Cap 6: Composite &rarr;</div>'
            h += f'<img src="{comp_uri}" alt="Composite" class="composite-img">'
            h += '</div>\n'
        h += '</div>\n'

    # ── Row 5: Inpaint ──
    if inpaint_uri:
        h += '<div class="subsection"><h3>Cap 7: Inpaint</h3>\n'
        h += '<div class="row">'
        if comp_uri:
            h += f'<div class="col"><img src="{comp_uri}" class="compare-img"><div class="caption">Composite</div></div>'
        h += f'<div class="col"><img src="{inpaint_uri}" class="compare-img"><div class="caption">Inpainted</div></div>'
        h += '</div></div>\n'

    # ── Row 6: Re-evaluate ──
    if reevaluate and primary:
        h += '<div class="subsection"><h3>Cap 8: Re-evaluate (Score Delta)</h3>\n'
        h += '<div class="delta-grid">\n'
        old_score = primary.get('score', 0)
        new_score = reevaluate.get('score', 0)
        delta = new_score - old_score
        sign = "+" if delta >= 0 else ""
        color = "#4caf50" if delta >= 0 else "#f44336"
        h += f'<div class="delta-card"><div class="delta-label">Overall</div>'
        h += f'<div class="delta-val" style="color:{color}">{sign}{delta:.0%}</div>'
        h += f'<div class="delta-detail">{old_score:.0%} &rarr; {new_score:.0%}</div></div>\n'
        old_dims = primary.get('dimensions', {})
        new_dims = reevaluate.get('dimensions', {})
        for dim in ['L1', 'L2', 'L3', 'L4', 'L5']:
            if dim not in old_dims or dim not in new_dims:
                h += f'<div class="delta-card"><div class="delta-label">{dim}</div>'
                h += '<div class="delta-val" style="color:#8b949e">N/A</div></div>\n'
                continue
            dd = new_dims[dim] - old_dims[dim]
            s = "+" if dd >= 0 else ""
            c = "#4caf50" if dd >= 0 else "#f44336"
            h += f'<div class="delta-card"><div class="delta-label">{dim}</div>'
            h += f'<div class="delta-val" style="color:{c}">{s}{dd:.0%}</div></div>\n'
        h += '</div></div>\n'

    # ── Row 7: Cultural translation (starry-night only) ──
    if trans_uri:
        h += '<div class="subsection"><h3>Cap 5: Cultural Translation (Xieyi Style)</h3>\n'
        h += '<div class="row">'
        h += f'<div class="col"><img src="{orig_uri}" class="compare-img"><div class="caption">Original</div></div>'
        h += f'<div class="col"><img src="{trans_uri}" class="compare-img"><div class="caption">Chinese Xieyi Translation</div></div>'
        h += '</div></div>\n'

    h += '</section>\n'
    return h


# ── Dynamic stats ────────────────────────────────────────────────────────

def compute_stats() -> dict[str, int]:
    results = list(glob.glob(str(SHOWCASE / "results" / "*.json")))
    tools = list(glob.glob(str(SHOWCASE / "tools" / "*.json")))
    layer_count = 0
    for img in IMAGES:
        m = load_json(SHOWCASE / "layers" / img / "manifest.json")
        if m:
            layer_count += len(m.get("layers", []))
    composites = list(glob.glob(str(SHOWCASE / "composites" / "*.png")))
    inpainted = list(glob.glob(str(SHOWCASE / "inpainted" / "*.png")))
    translations = list(glob.glob(str(SHOWCASE / "translations" / "*.png")))
    return {
        "Masterworks": len(IMAGES),
        "Evaluations": len(results),
        "Tool Analyses": len(tools),
        "Extracted Layers": layer_count,
        "Composites": len(composites),
        "Inpainted": len(inpainted),
        "Translations": len(translations),
    }


# ── Main ─────────────────────────────────────────────────────────────────

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.6; }
header { background: linear-gradient(135deg, #161b22, #0d1117); padding: 2rem; text-align: center; border-bottom: 1px solid #30363d; }
header h1 { font-size: 2.5rem; background: linear-gradient(90deg, #58a6ff, #f78166); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
header p { color: #8b949e; margin-top: 0.5rem; }
nav { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; padding: 1rem; background: #161b22; border-bottom: 1px solid #30363d; position: sticky; top: 0; z-index: 100; }
nav a { color: #58a6ff; text-decoration: none; padding: 0.3rem 0.8rem; border: 1px solid #30363d; border-radius: 1rem; font-size: 0.85rem; white-space: nowrap; }
nav a:hover { background: #21262d; }
.image-section { max-width: 1200px; margin: 2rem auto; padding: 2rem; background: #161b22; border: 1px solid #30363d; border-radius: 12px; }
.image-section h2 { font-size: 1.8rem; color: #f0f6fc; margin-bottom: 0.3rem; }
.tradition-badge { display: inline-block; background: #1f6feb33; color: #58a6ff; padding: 0.2rem 0.8rem; border-radius: 1rem; font-size: 0.8rem; margin-bottom: 1.5rem; }
.row { display: flex; gap: 2rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.col { flex: 1; min-width: 280px; }
.img-col img { width: 100%; max-width: 400px; border-radius: 8px; border: 1px solid #30363d; }
.caption { text-align: center; color: #8b949e; font-size: 0.85rem; margin-top: 0.3rem; }
.eval-col h3 { color: #f0f6fc; margin-bottom: 0.8rem; }
.score-bar { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.score-label { width: 140px; font-size: 0.8rem; color: #8b949e; text-align: right; }
.bar { flex: 1; height: 18px; background: #21262d; border-radius: 9px; overflow: hidden; }
.fill { height: 100%; border-radius: 9px; transition: width 0.5s; }
.score-val { width: 40px; font-size: 0.8rem; font-weight: 600; }
.summary { color: #8b949e; font-size: 0.85rem; margin-top: 0.8rem; padding: 0.8rem; background: #0d1117; border-radius: 6px; }
blockquote.rationale { font-style: italic; color: #8b949e; border-left: 3px solid #1f6feb; padding: 0.5rem 1rem; margin-top: 0.5rem; font-size: 0.82rem; }
.subsection { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #21262d; }
.subsection h3 { color: #f0f6fc; margin-bottom: 1rem; }
.cross-grid { display: flex; gap: 1rem; flex-wrap: wrap; }
.cross-card { flex: 1; min-width: 200px; background: #0d1117; padding: 1rem; border-radius: 8px; border: 1px solid #21262d; }
.cross-name { font-weight: 600; color: #58a6ff; margin-bottom: 0.5rem; }
.mini-score { font-size: 0.75rem; color: #8b949e; }
.tools-grid { display: flex; gap: 1rem; flex-wrap: wrap; }
.tool-card { flex: 1; min-width: 200px; background: #0d1117; padding: 1rem; border-radius: 8px; border: 1px solid #21262d; }
.tool-card h4 { color: #f78166; margin-bottom: 0.5rem; }
.metric { font-size: 0.85rem; margin-bottom: 0.3rem; }
.metric strong { color: #58a6ff; }
.verdict { font-size: 0.75rem; color: #8b949e; margin-top: 0.5rem; border-top: 1px solid #21262d; padding-top: 0.5rem; }
.layer-strip { display: flex; gap: 0.8rem; overflow-x: auto; padding-bottom: 0.5rem; }
.layer-card { flex: 0 0 auto; width: 160px; text-align: center; }
.layer-card img { width: 160px; height: 120px; object-fit: cover; border-radius: 6px; border: 1px solid #30363d; background: #21262d; }
.layer-name { font-size: 0.75rem; color: #c9d1d9; margin-top: 0.3rem; }
.layer-type { font-size: 0.65rem; color: #8b949e; }
.composite-row { display: flex; align-items: center; gap: 1rem; margin-top: 1rem; }
.arrow-label { color: #8b949e; font-weight: 600; }
.composite-img { max-width: 300px; border-radius: 8px; border: 1px solid #30363d; }
.compare-img { width: 100%; max-width: 350px; border-radius: 8px; border: 1px solid #30363d; }
.stats { max-width: 1200px; margin: 2rem auto; padding: 1.5rem; background: #161b22; border: 1px solid #30363d; border-radius: 12px; }
.stats h2 { color: #f0f6fc; margin-bottom: 1rem; }
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.stat-card { background: #0d1117; padding: 1.2rem; border-radius: 8px; text-align: center; }
.stat-num { font-size: 2rem; font-weight: 700; color: #58a6ff; }
.stat-desc { font-size: 0.8rem; color: #8b949e; }
.delta-grid { display: flex; gap: 1rem; flex-wrap: wrap; }
.delta-card { background: #0d1117; padding: 0.8rem 1.2rem; border-radius: 8px; text-align: center; min-width: 80px; }
.delta-label { font-size: 0.75rem; color: #8b949e; }
.delta-val { font-size: 1.4rem; font-weight: 700; }
.delta-detail { font-size: 0.7rem; color: #8b949e; }
"""


def main():
    nav_items = ''.join(
        f'<a href="#{img}">{esc(TITLES[img].split("(")[0].strip())}</a>'
        for img in IMAGES
    )

    stats = compute_stats()
    stat_cards = ''.join(
        f'<div class="stat-card"><div class="stat-num">{v}</div>'
        f'<div class="stat-desc">{esc(k)}</div></div>'
        for k, v in stats.items() if v > 0
    )

    sections = ''.join(build_image_section(img) for img in IMAGES)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VULCA 8x8 Showcase</title>
<style>{CSS}</style>
</head>
<body>
<header>
<h1>VULCA 8&times;8 Showcase</h1>
<p>8 masterworks &times; 8 AI capabilities &mdash; evaluate, cross-tradition, tools, decompose, redraw, composite, inpaint, re-evaluate</p>
</header>
<nav>{nav_items}</nav>

<div class="stats">
<h2>Overview</h2>
<div class="stat-grid">{stat_cards}</div>
</div>

{sections}

<footer style="text-align:center; padding:2rem; color:#484f58; font-size:0.8rem;">
Generated by VULCA v0.14.0 &mdash; AI-native cultural art advisor
</footer>
</body>
</html>
"""
    OUT.write_text(page)
    print(f"Written to {OUT} ({len(page) // 1024}KB)")


if __name__ == "__main__":
    main()
