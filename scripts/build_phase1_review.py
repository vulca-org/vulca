"""Build a standalone HTML review page for Phase 1 observability work.

Shows 5 images:
  - 3 existing (mona-lisa, napalm-girl, american-gothic) — revealed silent erosion
  - 2 new    (nengbiye-mascot, medical-waste-split)     — tested domain-shift

For each layer we surface the new Phase-1 signals (area_pct, quality_status,
quality_flags, pct_before/after_resolve, bbox_fill, inside_ratio) so the user
can eyeball which failures are already flagged vs. which slipped through.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT  = REPO / "assets" / "demo" / "phase1-review.html"

SLUGS = [
    ("mona-lisa",           "Renaissance — erosion silently ate main subject"),
    ("napalm-girl",         "Historical photo — 6 of 10 layers fully eaten"),
    ("american-gothic",     "American Regionalism — woman lost 70% of pixels"),
    ("nengbiye-mascot",     "Cartoon — domain-shift + sam_bbox wrong-object picks"),
    ("medical-waste-split", "Split composite — no-person, many small objects"),
]

LAYERS_DIR   = REPO / "assets" / "showcase" / "layers_v2"
ORIG_DIR     = REPO / "assets" / "showcase" / "originals"


def pick_original(slug: str) -> Path:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = ORIG_DIR / f"{slug}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(slug)


def layer_classes(layer: dict, per_entity_map: dict) -> list[str]:
    """CSS classes to color-code a layer card."""
    classes = ["layer-card"]
    rec = per_entity_map.get(layer["name"], {})
    flags = rec.get("quality_flags", [])
    status = layer.get("quality_status", "detected")
    area = layer.get("area_pct", 0.0)

    if status == "suspect":
        classes.append("suspect")
    if "over_eroded" in flags:
        classes.append("eroded")
    if area < 0.1:
        classes.append("empty")
    return classes


def render_flag(flag: str) -> str:
    return f'<span class="flag flag-{flag}">{flag}</span>'


def render_layer_card(layer: dict, per_entity_map: dict, slug: str) -> str:
    rec = per_entity_map.get(layer["name"], {})
    classes = layer_classes(layer, per_entity_map)
    rel_img = f"../showcase/layers_v2/{slug}/{layer['file']}"
    flags = rec.get("quality_flags", [])
    status = layer.get("quality_status", "detected")
    area = layer.get("area_pct", 0.0)
    fill = rec.get("bbox_fill")
    inside = rec.get("inside_ratio")
    pre = rec.get("pct_before_resolve")
    post = rec.get("pct_after_resolve")

    # Diff bar: visualises how much of the raw SAM mask survived resolve_overlaps.
    retention_html = ""
    if pre is not None and post is not None and pre > 0:
        ratio = min(1.0, post / pre)
        bar_class = "eroded" if ratio < 0.5 else ""
        retention_html = (
            f'<div class="retention-row">'
            f'<span class="retention-label">resolve: {pre:.1f}% → {post:.1f}%</span>'
            f'<div class="diff-bar"><div class="diff-fill {bar_class}" '
            f'style="width:{ratio*100:.0f}%"></div></div></div>'
        )

    metrics = []
    if fill is not None:  metrics.append(f"fill={fill:.2f}")
    if inside is not None: metrics.append(f"in={inside:.2f}")
    if area is not None:  metrics.append(f"area={area:.2f}%")
    metrics_html = " · ".join(metrics)

    flag_html = " ".join(render_flag(f) for f in flags)

    status_pill = f'<span class="pill pill-{status}">{status}</span>'

    return f"""
    <div class="{' '.join(classes)}">
      <div class="checker-bg"><img src="{rel_img}" alt="{layer['name']}" loading="lazy"></div>
      <div class="layer-name">{layer['name']} {status_pill}</div>
      <div class="layer-meta">z={layer.get('z_index','?')} · {layer.get('semantic_path','')}</div>
      <div class="layer-meta">{metrics_html}</div>
      {retention_html}
      <div>{flag_html}</div>
    </div>
    """


def render_slug(slug: str, intro: str) -> str:
    manifest = json.loads((LAYERS_DIR / slug / "manifest.json").read_text())
    orig = pick_original(slug)
    rel_orig = f"../showcase/originals/{orig.name}"

    dr = manifest["detection_report"]
    per_entity_map = {e["name"]: e for e in dr["per_entity"]}

    # Count flags for headline bar
    n_layers = len(manifest["layers"])
    n_eroded = sum(1 for l in manifest["layers"]
                   if "over_eroded" in per_entity_map.get(l["name"], {}).get("quality_flags", []))
    n_suspect = sum(1 for l in manifest["layers"] if l.get("quality_status") == "suspect")
    n_empty = sum(1 for l in manifest["layers"] if l.get("area_pct", 0) < 0.1)

    mix = dr.get("authority_mix", {})
    mix_html = " · ".join(f"{k}={v}" for k, v in mix.items() if v > 0)

    cards = "\n".join(
        render_layer_card(l, per_entity_map, slug)
        for l in sorted(manifest["layers"], key=lambda l: -l.get("z_index", 0))
    )

    return f"""
    <section class="slug">
      <div class="slug-header">
        <img src="{rel_orig}" class="slug-orig" alt="{slug}" loading="lazy">
        <div class="slug-info">
          <h2>{slug}</h2>
          <p class="intro-line">{intro}</p>
          <div class="stat-row">
            <span>status=<strong>{manifest['status']}</strong></span>
            <span>{n_layers} layers</span>
            <span class="stat-warn">{n_eroded} over-eroded</span>
            <span class="stat-warn">{n_suspect} suspect</span>
            <span class="stat-warn">{n_empty} near-empty (&lt;0.1%)</span>
          </div>
          <div class="stat-row stat-small">authority_mix: {mix_html}</div>
        </div>
      </div>
      <div class="grid">
        {cards}
      </div>
    </section>
    """


def main():
    sections = "\n".join(render_slug(s, intro) for s, intro in SLUGS)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Phase 1 Observability Review</title>
<style>
  :root {{
    --bg: #0a0a0a; --panel: #161616; --border: #2a2a2a;
    --ink: #e8e8e8; --muted: #8a8a8a;
    --accent: #4a9eff; --warn: #e0b400; --danger: #ff6b35; --dead: #ff4444;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, sans-serif;
    margin: 0; padding: 24px 32px; line-height: 1.5;
  }}
  h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
  .intro {{ color: var(--muted); max-width: 900px; margin: 0 0 24px 0; }}
  .legend {{
    display: flex; gap: 16px; flex-wrap: wrap;
    background: var(--panel); padding: 12px 16px; border-radius: 6px;
    margin-bottom: 32px; font-size: 13px;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .swatch {{ width: 12px; height: 12px; border-radius: 2px; border: 2px solid; }}
  .swatch-suspect {{ border-color: var(--danger); background: transparent; }}
  .swatch-eroded {{ border-color: var(--warn); background: transparent; }}
  .swatch-empty {{ border-color: var(--dead); background: rgba(255,68,68,0.1); }}

  .slug {{
    border-top: 1px solid var(--border);
    padding-top: 24px; margin-bottom: 48px;
  }}
  .slug-header {{ display: flex; gap: 20px; margin-bottom: 16px; align-items: flex-start; }}
  .slug-orig {{ max-width: 240px; max-height: 200px; border-radius: 4px; object-fit: contain; background: #000; }}
  .slug-info {{ flex: 1; min-width: 0; }}
  .slug-info h2 {{ margin: 0 0 6px 0; font-size: 20px; }}
  .intro-line {{ color: var(--muted); margin: 0 0 12px 0; }}
  .stat-row {{ display: flex; gap: 16px; flex-wrap: wrap; font-size: 13px; }}
  .stat-row strong {{ color: var(--accent); }}
  .stat-row .stat-warn {{ color: var(--warn); }}
  .stat-small {{ font-size: 11px; color: var(--muted); margin-top: 4px; }}

  .grid {{
    display: grid; gap: 12px;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }}
  .layer-card {{
    background: var(--panel); border: 2px solid transparent; border-radius: 6px;
    padding: 8px; overflow: hidden;
  }}
  .layer-card.suspect {{ border-color: var(--danger); }}
  .layer-card.eroded  {{ border-color: var(--warn); }}
  .layer-card.empty   {{ border-color: var(--dead); background: rgba(255,68,68,0.05); }}
  .checker-bg {{
    background-color: #2a2a2a;
    background-image:
      linear-gradient(45deg, #1a1a1a 25%, transparent 25%),
      linear-gradient(-45deg, #1a1a1a 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #1a1a1a 75%),
      linear-gradient(-45deg, transparent 75%, #1a1a1a 75%);
    background-size: 12px 12px;
    background-position: 0 0, 0 6px, 6px -6px, -6px 0px;
    border-radius: 4px;
    aspect-ratio: 1;
    overflow: hidden;
  }}
  .checker-bg img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
  .layer-name {{
    font-size: 12px; font-weight: 600; margin: 8px 0 2px;
    word-break: break-word; display: flex; gap: 6px; align-items: center;
  }}
  .layer-meta {{
    font-size: 10px; color: var(--muted); line-height: 1.4;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
  }}
  .pill {{
    font-size: 9px; font-weight: 600; padding: 1px 6px;
    border-radius: 8px; text-transform: uppercase; letter-spacing: 0.3px;
  }}
  .pill-detected {{ background: #1e3a1e; color: #6fcf6f; }}
  .pill-suspect  {{ background: #4a2410; color: var(--danger); }}
  .flag {{
    display: inline-block; font-size: 9px; font-weight: 600;
    padding: 1px 5px; border-radius: 2px; margin: 2px 2px 0 0;
    font-family: ui-monospace, monospace;
  }}
  .flag-over_eroded       {{ background: var(--warn); color: #000; }}
  .flag-low_bbox_fill     {{ background: var(--danger); color: #fff; }}
  .flag-mask_outside_bbox {{ background: var(--danger); color: #fff; }}
  .flag-empty_mask        {{ background: var(--dead); color: #fff; }}

  .retention-row {{ margin-top: 4px; }}
  .retention-label {{ font-size: 9px; color: var(--muted); font-family: ui-monospace, monospace; }}
  .diff-bar {{ height: 3px; background: #2a2a2a; border-radius: 2px; overflow: hidden; margin-top: 2px; }}
  .diff-fill {{ height: 100%; background: #4a9; }}
  .diff-fill.eroded {{ background: var(--warn); }}
</style>
</head>
<body>
  <h1>Phase 1 Observability Review · 5 images</h1>
  <p class="intro">
    Visual sanity-check for the backstop (Fix&nbsp;#1) + observability (Fix&nbsp;#2) work.
    3 existing images show what the new <code>over_eroded</code> flag reveals on the already-shipped showcase;
    2 new images test how the pipeline holds up on domain-shift (cartoon watercolor + split composite).
    Hover any card for tooltip; numbers are <code>fill</code>/<code>in</code>/<code>area</code>.
  </p>
  <div class="legend">
    <span class="legend-item"><span class="swatch swatch-suspect"></span>orange border — SAM-gate <code>suspect</code> (low fill / outside bbox / empty)</span>
    <span class="legend-item"><span class="swatch swatch-eroded"></span>yellow border — <code>over_eroded</code> (retained &lt; 50% after resolve_overlaps)</span>
    <span class="legend-item"><span class="swatch swatch-empty"></span>red border + tint — near-empty on disk (&lt; 0.1% of image)</span>
  </div>
  {sections}
  <p style="color:var(--muted);font-size:12px;margin-top:48px;border-top:1px solid var(--border);padding-top:16px">
    Generated by <code>scripts/build_phase1_review.py</code>. Re-run it after pipeline changes to refresh.
  </p>
</body>
</html>
"""
    OUT.write_text(html)
    print(f"→ {OUT}")
    print(f"   5 slugs, relative paths resolve from {OUT.parent}")


if __name__ == "__main__":
    main()
