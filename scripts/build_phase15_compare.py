"""Build side-by-side HTML: flat (old) vs hierarchical (Phase 1.5).

Reads two snapshot dirs:
  assets/showcase/layers_v2_compare/flat/<slug>/         ← legacy partition
  assets/showcase/layers_v2_compare/hierarchical/<slug>/ ← Phase 1.5 nested overlay

Per slug, per layer: show both PNGs side-by-side, highlight layers where
area_pct differs meaningfully, color-code the "winner" of each comparison.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT  = REPO / "assets" / "demo" / "phase15-compare.html"

SLUGS = [
    ("mona-lisa",           "Renaissance — flat ate mona_lisa to 0%"),
    ("napalm-girl",         "Historical photo — 6 persons silently zeroed under flat"),
    ("american-gothic",     "Regionalism — `woman` lost 70% of pixels under flat"),
    ("nengbiye-mascot",     "Cartoon — only `glasses` eroded under flat (fg legit)"),
    ("medical-waste-split", "Composite — `right_grass` eroded under both (fg legit)"),
]

FLAT_DIR = REPO / "assets" / "showcase" / "layers_v2_compare" / "flat"
HIER_DIR = REPO / "assets" / "showcase" / "layers_v2_compare" / "hierarchical"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"


def pick_original(slug: str) -> Path:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = ORIG_DIR / f"{slug}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(slug)


def get_layer_area(manifest: dict, name: str) -> float:
    for l in manifest["layers"]:
        if l["name"] == name:
            return l.get("area_pct", 0.0)
    return 0.0


def render_pair(slug: str, flat_layer: dict, hier_layer: dict | None) -> str:
    flat_area = flat_layer.get("area_pct", 0.0)
    hier_area = hier_layer.get("area_pct", 0.0) if hier_layer else 0.0
    delta = hier_area - flat_area
    name = flat_layer["name"]
    sp   = flat_layer.get("semantic_path", "")

    # Classify the diff for color coding:
    verdict_class = "nochange"
    verdict_label = "—"
    if delta > 1.0:
        verdict_class = "win"
        verdict_label = f"+{delta:.1f}% ← hierarchical recovered pixels"
    elif delta < -1.0:
        verdict_class = "loss"
        verdict_label = f"{delta:.1f}% ← hierarchical lost pixels (unexpected!)"
    elif abs(delta) < 0.05:
        verdict_label = "identical"
    else:
        verdict_label = f"Δ {delta:+.2f}%"

    # Use relative paths from assets/demo/ → ../showcase/layers_v2_compare/...
    flat_src = f"../showcase/layers_v2_compare/flat/{slug}/{flat_layer['file']}"
    hier_src = f"../showcase/layers_v2_compare/hierarchical/{slug}/{hier_layer['file']}" if hier_layer else ""

    return f"""
    <tr class="row-{verdict_class}">
      <td class="meta">
        <div class="lname">{name}</div>
        <div class="sp">z={flat_layer.get('z_index','?')} · {sp}</div>
        <div class="verdict verdict-{verdict_class}">{verdict_label}</div>
      </td>
      <td class="cell">
        <div class="checker"><img src="{flat_src}" loading="lazy"></div>
        <div class="area">area {flat_area:.2f}%</div>
      </td>
      <td class="cell">
        {'<div class="checker"><img src="' + hier_src + '" loading="lazy"></div>' if hier_layer else '<div class="empty">—</div>'}
        <div class="area">area {hier_area:.2f}%</div>
      </td>
    </tr>
    """


def render_slug(slug: str, intro: str) -> str:
    flat_m = json.loads((FLAT_DIR / slug / "manifest.json").read_text())
    hier_m = json.loads((HIER_DIR / slug / "manifest.json").read_text())
    orig = pick_original(slug)
    rel_orig = f"../showcase/originals/{orig.name}"

    # Build aligned rows by layer NAME (stable across reruns).
    hier_by_name = {l["name"]: l for l in hier_m["layers"]}

    # Headline metrics
    def big_wins(flat_layers, hier_by_name):
        wins = 0
        for f in flat_layers:
            h = hier_by_name.get(f["name"])
            if h and h.get("area_pct", 0) - f.get("area_pct", 0) > 5.0:
                wins += 1
        return wins

    def recovered_from_zero(flat_layers, hier_by_name):
        # Layers whose flat area_pct was ≤0.1 but hierarchical is >1.0 — literal zombies revived.
        cases = []
        for f in flat_layers:
            h = hier_by_name.get(f["name"])
            if h and f.get("area_pct", 0) <= 0.1 and h.get("area_pct", 0) > 1.0:
                cases.append((f["name"], h.get("area_pct", 0)))
        return cases

    n_big = big_wins(flat_m["layers"], hier_by_name)
    zombies = recovered_from_zero(flat_m["layers"], hier_by_name)

    rows = "\n".join(
        render_pair(slug, f, hier_by_name.get(f["name"]))
        for f in sorted(flat_m["layers"], key=lambda l: -l.get("z_index", 0))
    )

    zombies_html = ""
    if zombies:
        zombie_list = ", ".join(f"<code>{n}</code> ({a:.1f}%)" for n, a in zombies)
        zombies_html = f'<div class="zombies">🧟 revived from 0%: {zombie_list}</div>'

    return f"""
    <section class="slug">
      <div class="slug-header">
        <img src="{rel_orig}" class="orig" loading="lazy">
        <div class="slug-info">
          <h2>{slug}</h2>
          <p class="intro">{intro}</p>
          <div class="stat-row">
            <span><strong>{n_big}</strong> layer(s) gained ≥5% area under hierarchical</span>
            <span>{len(zombies)} fully-zeroed under flat</span>
          </div>
          {zombies_html}
        </div>
      </div>
      <table class="compare">
        <thead>
          <tr><th>layer</th><th>flat (old)</th><th>hierarchical (Phase 1.5)</th></tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </section>
    """


def main():
    sections = "\n".join(render_slug(s, intro) for s, intro in SLUGS)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Phase 1.5 flat vs hierarchical — side-by-side</title>
<style>
  :root {{
    --bg: #0a0a0a; --panel: #161616; --border: #2a2a2a;
    --ink: #e8e8e8; --muted: #8a8a8a;
    --win: #4caf50; --loss: #f44336; --dead: #8a3a3a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, sans-serif;
    margin: 0; padding: 24px 32px; line-height: 1.5;
  }}
  h1 {{ margin: 0 0 6px 0; font-size: 24px; }}
  .intro-top {{ color: var(--muted); max-width: 900px; margin: 0 0 16px 0; }}
  .legend {{
    display: flex; gap: 20px; flex-wrap: wrap;
    background: var(--panel); padding: 10px 14px; border-radius: 6px;
    margin-bottom: 28px; font-size: 13px;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; }}
  .chip {{ padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 600; }}
  .chip-win {{ background: rgba(76,175,80,0.2); color: var(--win); border: 1px solid var(--win); }}
  .chip-loss {{ background: rgba(244,67,54,0.2); color: var(--loss); border: 1px solid var(--loss); }}
  .chip-nc  {{ background: #2a2a2a; color: var(--muted); }}

  .slug {{
    border-top: 1px solid var(--border);
    padding-top: 20px; margin-bottom: 40px;
  }}
  .slug-header {{ display: flex; gap: 20px; margin-bottom: 12px; align-items: flex-start; }}
  .orig {{ max-width: 220px; max-height: 200px; border-radius: 4px; object-fit: contain; background: #000; }}
  .slug-info h2 {{ margin: 0 0 4px 0; font-size: 20px; }}
  .intro {{ color: var(--muted); margin: 0 0 8px 0; font-size: 13px; }}
  .stat-row {{ display: flex; gap: 18px; flex-wrap: wrap; font-size: 13px; color: var(--ink); }}
  .stat-row strong {{ color: var(--win); font-size: 15px; }}
  .zombies {{
    margin-top: 8px; padding: 6px 10px; background: #2a1a1a; border-left: 3px solid var(--loss);
    border-radius: 3px; font-size: 12px;
  }}
  .zombies code {{ background: #0a0a0a; padding: 1px 4px; border-radius: 2px; color: var(--win); }}

  table.compare {{
    border-collapse: collapse; width: 100%;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    font-size: 12px;
  }}
  table.compare th {{
    text-align: left; padding: 8px 10px;
    background: var(--panel); color: var(--muted);
    border-bottom: 1px solid var(--border);
    font-weight: 500; font-size: 11px; text-transform: uppercase;
  }}
  table.compare td.meta {{
    vertical-align: top; padding: 8px 10px;
    border-bottom: 1px solid var(--border);
    min-width: 220px; max-width: 260px;
  }}
  table.compare td.cell {{
    vertical-align: top; padding: 8px 10px;
    border-bottom: 1px solid var(--border);
    width: 220px;
  }}
  tr.row-win {{ background: rgba(76,175,80,0.04); }}
  tr.row-loss {{ background: rgba(244,67,54,0.05); }}
  .lname {{ font-weight: 600; color: var(--ink); margin-bottom: 2px; }}
  .sp {{ color: var(--muted); font-size: 10px; word-break: break-all; margin-bottom: 4px; }}
  .verdict {{
    font-size: 11px; display: inline-block;
    padding: 1px 6px; border-radius: 3px;
  }}
  .verdict-win  {{ background: rgba(76,175,80,0.15); color: var(--win); }}
  .verdict-loss {{ background: rgba(244,67,54,0.15); color: var(--loss); }}
  .verdict-nochange {{ background: #222; color: var(--muted); }}
  .checker {{
    background-color: #2a2a2a;
    background-image:
      linear-gradient(45deg, #1a1a1a 25%, transparent 25%),
      linear-gradient(-45deg, #1a1a1a 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #1a1a1a 75%),
      linear-gradient(-45deg, transparent 75%, #1a1a1a 75%);
    background-size: 12px 12px;
    background-position: 0 0, 0 6px, 6px -6px, -6px 0px;
    aspect-ratio: 1; overflow: hidden; border-radius: 4px;
  }}
  .checker img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
  .empty {{
    aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
    background: #0a0a0a; border: 1px dashed #333; color: var(--muted);
    border-radius: 4px;
  }}
  .area {{ margin-top: 4px; color: var(--muted); font-size: 10px; text-align: center; }}
</style>
</head>
<body>
  <h1>flat vs hierarchical — Phase 1.5 pilot comparison · 5 images</h1>
  <p class="intro-top">
    Left column = <strong>flat</strong> (partition model, previously-shipped). Right = <strong>hierarchical</strong>
    (Phase 1.5, descendants no longer carve parents). Layers are paired by <code>name</code>, sorted by z-index descending.
    Rows shaded green = hierarchical gained meaningful area; red = lost (shouldn't happen, would be a regression).
    Bigger headline: each slug lists how many layers were fully zeroed under flat but recovered under hierarchical.
  </p>
  <div class="legend">
    <span class="legend-item"><span class="chip chip-win">+Δ</span>hierarchical restored pixels</span>
    <span class="legend-item"><span class="chip chip-loss">−Δ</span>hierarchical removed pixels (unexpected)</span>
    <span class="legend-item"><span class="chip chip-nc">—</span>identical</span>
  </div>
  {sections}
  <p style="color:var(--muted);font-size:12px;margin-top:32px;border-top:1px solid var(--border);padding-top:14px">
    Generated by <code>scripts/build_phase15_compare.py</code>. Snapshots in
    <code>assets/showcase/layers_v2_compare/{{flat,hierarchical}}/</code>.
    Production <code>layers_v2/</code> restored to hierarchical after snapshotting.
  </p>
</body>
</html>
"""
    OUT.write_text(html)
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
