"""Phase B1 · Agent-native showcase viewer for 44-image corpus.

Reads every manifest.json under assets/showcase/layers_v2/ and renders a
single standalone HTML page at assets/demo/showcase.html.

Design goals:
- One page, zero deps, opens on double-click
- Grid of thumbnails at top → click to expand a slug's layer detail view
- Layer cards show every Phase 1.5/1.6/1.7 signal (area_pct, quality_status,
  parent_layer_id, residual tag, erosion flags, bbox_fill/inside_ratio)
- Residual + locked layers get distinct visual treatment (red-outline +
  lock badge) so readers can see the agent-native story at a glance
- Relative paths only — no base64, no inlined PNGs (file stays small;
  browser lazy-loads layers only when expanded)
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from collections import Counter

# Phase 2 compat guard: refuse or warn if we see an older/newer manifest shape.
# Phase 1.9: imported from canonical pipeline module so all three constants
# (pipeline writer, orchestrator stamp, viewer) stay in sync automatically.
try:
    import sys as _sys
    _sys.path.insert(0, str(REPO / "scripts"))
    from claude_orchestrated_pipeline import ORCHESTRATED_MANIFEST_VERSION as EXPECTED_MANIFEST_VERSION
except Exception:
    EXPECTED_MANIFEST_VERSION = 5  # fallback only


def esc(s) -> str:
    """HTML-escape any string-ish value for f-string interpolation.

    Defense-in-depth: Plan sanitizer already restricts slug charset, but the
    HTML layer should not depend on that invariant (the viewer is a publishable
    artifact and will outlive schema guarantees).
    """
    if s is None:
        return ""
    return html.escape(str(s), quote=True)

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets" / "demo" / "showcase.html"
LAYERS_ROOT = REPO / "assets" / "showcase" / "layers_v2"
ORIG_DIR = REPO / "assets" / "showcase" / "originals"


def pick_original(slug: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = ORIG_DIR / f"{slug}{ext}"
        if p.exists():
            return p
    return None


def load_slug(slug: str) -> dict | None:
    """Load manifest.json; warn + skip on any read failure or unexpected version."""
    mf = LAYERS_ROOT / slug / "manifest.json"
    if not mf.exists():
        return None
    try:
        manifest = json.loads(mf.read_text())
    except Exception as e:
        import sys
        print(f"WARN: skipped {slug}: {e}", file=sys.stderr)
        return None
    version = manifest.get("version")
    if version != EXPECTED_MANIFEST_VERSION:
        import sys
        print(f"WARN: {slug} manifest version={version} (expected {EXPECTED_MANIFEST_VERSION}) "
              f"— rendering anyway but signals may be incomplete", file=sys.stderr)
    return manifest


def quality_badges(layer: dict, per_entity_rec: dict | None) -> str:
    parts = []
    status = layer.get("quality_status", "detected")
    if status == "residual":
        parts.append('<span class="pill pill-residual" title="synthetic pipeline layer">residual</span>')
    elif status == "suspect":
        parts.append('<span class="pill pill-suspect" title="SAM quality gate flagged">suspect</span>')
    elif status == "missed":
        parts.append('<span class="pill pill-missed">missed</span>')
    if layer.get("locked"):
        parts.append('<span class="pill pill-locked" title="locked — redraw blocked">🔒</span>')
    if per_entity_rec:
        for flag in per_entity_rec.get("quality_flags", []):
            parts.append(f'<span class="flag flag-{flag}">{flag}</span>')
    return "".join(parts)


def render_layer_card(slug: str, layer: dict, per_entity_map: dict) -> str:
    name = layer.get("name", "?")
    rec = per_entity_map.get(name, {})
    layer_file = layer.get("file", f"{name}.png")
    rel_img = f"../showcase/layers_v2/{esc(slug)}/{esc(layer_file)}"
    area = layer.get("area_pct", 0.0)
    sp = layer.get("semantic_path", "")
    z = layer.get("z_index", 0)
    parent_id = layer.get("parent_layer_id")
    layer_id = layer.get("id", "")
    status = layer.get("quality_status", "detected")
    locked = bool(layer.get("locked"))
    badges = quality_badges(layer, rec)

    # Metric line: show fill/in only if present (hint path or detector path)
    metrics = []
    if "bbox_fill" in rec:
        metrics.append(f"fill={rec['bbox_fill']:.2f}")
    if "inside_ratio" in rec:
        metrics.append(f"in={rec['inside_ratio']:.2f}")
    metrics.append(f"area={area:.1f}%")
    metric_line = " · ".join(metrics)

    # Erosion bar
    pre = rec.get("pct_before_resolve")
    post = rec.get("pct_after_resolve")
    retention_bar = ""
    if pre is not None and post is not None and pre > 0:
        retain = min(1.0, post / pre)
        bar_cls = "eroded" if retain < 0.5 else ""
        retention_bar = (
            f'<div class="retention" title="pre-resolve {pre:.1f}% → post-resolve {post:.1f}%">'
            f'  <div class="bar"><div class="fill {bar_cls}" style="width:{retain*100:.0f}%"></div></div>'
            f'  <span class="ret-label">{retain*100:.0f}% retained</span>'
            f'</div>'
        )

    card_cls = ["layer-card"]
    if status == "residual":
        card_cls.append("is-residual")
    if locked:
        card_cls.append("is-locked")

    # Parent link: real anchor to #layer-<slug>-<parent_id> so humans + agents
    # can traverse the hierarchy by click, not just tooltip-read it.
    parent_info = ""
    if parent_id:
        parent_info = (f'<a class="parent-link" href="#layer-{esc(slug)}-{esc(parent_id)}" '
                       f'title="{esc(parent_id)}">↑ parent</a>')

    # Stable per-layer anchor id + data-attrs so agents can extract signals
    # without parsing prose or CSS class names.
    return f'''
    <div class="{' '.join(card_cls)}"
         id="layer-{esc(slug)}-{esc(layer_id)}"
         data-layer-name="{esc(name)}"
         data-layer-id="{esc(layer_id)}"
         data-slug="{esc(slug)}"
         data-quality-status="{esc(status)}"
         data-area-pct="{area:.2f}"
         data-z-index="{z}"
         data-semantic-path="{esc(sp)}"
         data-parent-layer-id="{esc(parent_id or '')}"
         data-locked="{str(locked).lower()}">
      <div class="checker"><img src="{rel_img}" alt="layer {esc(name)} from {esc(slug)}" loading="lazy"></div>
      <div class="layer-head">
        <span class="lname">{esc(name)}</span>
        {badges}
      </div>
      <div class="meta">
        <code>z={z}</code> <code>{esc(sp) if sp else "(no path)"}</code> {parent_info}
      </div>
      <div class="meta metrics">{metric_line}</div>
      {retention_bar}
    </div>
    '''


def render_slug_section(slug: str, manifest: dict, orig_path: Path | None) -> str:
    layers = manifest.get("layers", [])
    dr = manifest.get("detection_report", {})
    per_entity_map = {e["name"]: e for e in dr.get("per_entity", [])}
    W = manifest.get("width", 0)
    H = manifest.get("height", 0)

    # Group metrics
    n_total = len(layers)
    n_residual = sum(1 for l in layers if l.get("quality_status") == "residual")
    n_locked = sum(1 for l in layers if l.get("locked"))
    n_suspect = sum(1 for l in layers if l.get("quality_status") == "suspect")
    n_face_parts = sum(1 for l in layers if "__" in l.get("name", ""))
    residual_area = next((l["area_pct"] for l in layers
                          if l.get("quality_status") == "residual"), 0.0)
    mix = dr.get("authority_mix", {})
    mix_text = " · ".join(f"{k}={v}" for k, v in mix.items() if v)

    rel_orig = f"../showcase/originals/{esc(orig_path.name)}" if orig_path else ""
    orig_html = (f'<img class="orig-thumb" src="{rel_orig}" loading="lazy" alt="original image for {esc(slug)}">'
                 if orig_path else '<div class="orig-thumb empty">—</div>')

    residual_badge = (f'<span class="headline-stat stat-residual">'
                      f'residual {residual_area:.1f}%</span>' if residual_area > 0 else "")

    # Sort layers: background → subject → residual → face-parts → foreground, ascending z
    layer_cards = "\n".join(
        render_layer_card(slug, l, per_entity_map)
        for l in sorted(layers, key=lambda l: (l.get("z_index", 0), l.get("name", "")))
    )

    plan_domain = manifest.get("plan", {}).get("domain", "—")
    status = manifest.get("status", "?")

    return f'''
    <section class="slug"
             id="slug-{esc(slug)}"
             data-slug="{esc(slug)}"
             data-status="{esc(status)}"
             data-layer-count="{n_total}"
             data-residual-pct="{residual_area:.2f}"
             data-suspect-count="{n_suspect}"
             data-domain="{esc(plan_domain)}">
      <header class="slug-header">
        <a href="#top" class="top-link">↑ top</a>
        <div class="orig-wrap">{orig_html}</div>
        <div class="slug-info">
          <h2>{esc(slug)} <span class="dims">{W}×{H}</span></h2>
          <div class="headline-stats">
            <span>domain: <code>{esc(plan_domain)}</code></span>
            <span>status: <code class="status-{esc(status)}">{esc(status)}</code></span>
            <span>{n_total} layers</span>
            {residual_badge}
            <span>{n_face_parts} face-parts</span>
            <span>{n_locked} locked</span>
            {'<span class="stat-warn">' + str(n_suspect) + ' suspect</span>' if n_suspect else ''}
          </div>
          <div class="mix-row">{esc(mix_text)}</div>
        </div>
      </header>
      <div class="layer-grid">
        {layer_cards}
      </div>
    </section>
    '''


def render_thumbnail(slug: str, manifest: dict, orig_path: Path | None) -> str:
    rel_orig = f"../showcase/originals/{esc(orig_path.name)}" if orig_path else ""
    dr = manifest.get("detection_report", {}) if manifest else {}
    layers = manifest.get("layers", []) if manifest else []
    n_layers = len(layers)
    residual_area = next(
        (l.get("area_pct", 0.0) for l in layers
         if l.get("quality_status") == "residual"),
        0.0,
    )
    status = manifest.get("status", "?") if manifest else "?"
    status_cls = f"status-{esc(status)}"
    badge = f'<span class="thumb-residual">r:{residual_area:.0f}%</span>' if residual_area > 0 else ""
    return f'''
    <a class="thumb" href="#slug-{esc(slug)}"
       data-slug="{esc(slug)}"
       data-status="{esc(status)}"
       data-layer-count="{n_layers}"
       data-residual-pct="{residual_area:.2f}">
      <img src="{rel_orig}" loading="lazy" alt="thumbnail of {esc(slug)}">
      <div class="thumb-label">
        <span class="tlabel-name">{esc(slug)}</span>
        <span class="tlabel-meta"><span class="{status_cls}">{esc(status)}</span> · {n_layers}L {badge}</span>
      </div>
    </a>
    '''


def compute_global_stats(slugs_data: list[tuple[str, dict, Path | None]]) -> dict:
    total_images = len(slugs_data)
    total_layers = sum(len(m.get("layers", [])) for _, m, _ in slugs_data)
    residual_images = sum(
        1 for _, m, _ in slugs_data
        if any(l.get("quality_status") == "residual" for l in m.get("layers", []))
    )
    total_residual_area = sum(
        next((l["area_pct"] for l in m.get("layers", [])
              if l.get("quality_status") == "residual"), 0.0)
        for _, m, _ in slugs_data
    )
    avg_residual = total_residual_area / residual_images if residual_images else 0.0
    status_counts = Counter(m.get("status", "?") for _, m, _ in slugs_data)
    return {
        "images": total_images,
        "layers": total_layers,
        "avg_per_image": total_layers / max(total_images, 1),
        "residual_images": residual_images,
        "avg_residual_pct": avg_residual,
        "status_counts": dict(status_counts),
    }


def main():
    slugs = sorted(p.name for p in LAYERS_ROOT.iterdir()
                   if p.is_dir() and not p.name.startswith("_"))
    slugs_data: list[tuple[str, dict, Path | None]] = []
    for slug in slugs:
        m = load_slug(slug)
        if not m:
            continue
        slugs_data.append((slug, m, pick_original(slug)))

    stats = compute_global_stats(slugs_data)
    status_pills = " ".join(
        f'<span class="pill pill-{k}">{k}: {v}</span>'
        for k, v in sorted(stats["status_counts"].items())
    )

    thumbs = "\n".join(render_thumbnail(s, m, o) for s, m, o in slugs_data)
    sections = "\n".join(render_slug_section(s, m, o) for s, m, o in slugs_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Vulca showcase · {stats['images']} images × hierarchical layers</title>
<style>
  :root {{
    --bg: #0a0a0a; --panel: #141414; --border: #2a2a2a;
    --ink: #e8e8e8; --muted: #9a9a9a; --dim: #7a7a7a;
    --accent: #4a9eff; --win: #4caf50; --warn: #e0b400;
    --danger: #ff6b35; --residual: #c77ad6;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, sans-serif;
    margin: 0; padding: 24px 32px; line-height: 1.5;
  }}
  code {{
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    font-size: 0.9em;
    background: #1a1a1a; padding: 1px 5px; border-radius: 3px;
  }}
  header.top {{
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px; margin-bottom: 24px;
  }}
  h1 {{ margin: 0 0 6px 0; font-size: 24px; letter-spacing: -0.02em; }}
  .subtitle {{ color: var(--muted); max-width: 900px; font-size: 14px; }}
  .global-stats {{
    display: flex; gap: 20px; flex-wrap: wrap;
    margin: 14px 0 10px; font-size: 13px;
  }}
  .global-stats .num {{ font-size: 18px; font-weight: 600; color: var(--accent); }}
  .legend {{
    display: flex; gap: 14px; flex-wrap: wrap;
    font-size: 12px; color: var(--muted);
  }}
  .narrative {{
    color: var(--ink); font-size: 13px; max-width: 900px;
    background: rgba(199,122,214,0.05); border-left: 3px solid var(--residual);
    padding: 10px 14px; margin: 16px 0 0;
  }}
  .narrative code {{ background: #0f0f0f; }}

  /* Thumbnail grid */
  .thumb-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 10px; margin-bottom: 36px;
  }}
  .thumb {{
    display: block; text-decoration: none; color: var(--ink);
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 6px; overflow: hidden; transition: transform 0.15s, border-color 0.15s;
  }}
  .thumb:hover {{ transform: translateY(-2px); border-color: var(--accent); }}
  .thumb img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; background: #000; }}
  .thumb-label {{
    padding: 6px 8px; display: flex; flex-direction: column; gap: 2px;
    font-size: 11px; font-family: ui-monospace, monospace;
  }}
  .tlabel-name {{ color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .tlabel-meta {{ color: var(--muted); }}
  .thumb-residual {{ color: var(--residual); font-weight: 600; }}

  /* Slug section */
  .slug {{
    margin-bottom: 48px; border-top: 1px solid var(--border);
    padding-top: 24px; scroll-margin-top: 20px;
  }}
  .slug-header {{ display: flex; gap: 18px; margin-bottom: 16px; align-items: flex-start; }}
  .top-link {{
    color: var(--muted); font-size: 12px; text-decoration: none;
    padding: 4px 8px; border: 1px solid var(--border); border-radius: 3px;
    position: sticky; top: 0;
  }}
  .top-link:hover {{ color: var(--accent); border-color: var(--accent); }}
  .orig-wrap {{ flex-shrink: 0; }}
  .orig-thumb {{
    width: 180px; max-height: 180px; object-fit: contain;
    background: #000; border-radius: 4px;
  }}
  .orig-thumb.empty {{
    width: 180px; height: 180px; display: flex; align-items: center;
    justify-content: center; color: var(--dim);
    border: 1px dashed var(--border); border-radius: 4px;
  }}
  .slug-info {{ flex: 1; min-width: 0; }}
  .slug-info h2 {{ margin: 0 0 6px; font-size: 22px; letter-spacing: -0.02em; }}
  .slug-info h2 .dims {{ color: var(--muted); font-size: 14px; font-weight: 400; }}
  .headline-stats {{
    display: flex; gap: 14px; flex-wrap: wrap; font-size: 13px;
    margin-bottom: 6px;
  }}
  .headline-stat {{ color: var(--muted); }}
  .stat-residual {{ color: var(--residual); font-weight: 600; }}
  .stat-warn {{ color: var(--warn); font-weight: 600; }}
  .mix-row {{ font-size: 11px; color: var(--dim); font-family: ui-monospace, monospace; }}
  .status-ok {{ color: var(--win); }}
  .status-partial {{ color: var(--warn); }}
  .status-error {{ color: var(--danger); }}

  /* Layer grid */
  .layer-grid {{
    display: grid; gap: 10px;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  }}
  .layer-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 5px; padding: 6px; transition: border-color 0.1s;
  }}
  .layer-card:hover {{ border-color: #3a3a3a; }}
  .layer-card.is-residual {{ border-color: var(--residual); }}
  /* Lock: amber outline-dashed (distinct channel from residual purple).
     A layer can be residual+locked; both signals remain visible. */
  .layer-card.is-locked {{ outline: 2px dashed var(--warn); outline-offset: -2px; }}
  .checker {{
    background-color: #2a2a2a;
    background-image:
      linear-gradient(45deg, #1a1a1a 25%, transparent 25%),
      linear-gradient(-45deg, #1a1a1a 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #1a1a1a 75%),
      linear-gradient(-45deg, transparent 75%, #1a1a1a 75%);
    background-size: 10px 10px;
    background-position: 0 0, 0 5px, 5px -5px, -5px 0;
    aspect-ratio: 1; border-radius: 3px; overflow: hidden;
  }}
  .checker img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
  .layer-head {{
    display: flex; gap: 4px; align-items: center; flex-wrap: wrap;
    margin: 6px 0 2px; font-size: 12px;
  }}
  .lname {{
    font-weight: 600; color: var(--ink); font-size: 12px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    max-width: 100%; flex: 1;
    font-family: ui-monospace, monospace;
  }}
  .meta {{
    font-size: 10px; color: var(--muted); line-height: 1.4;
    font-family: ui-monospace, monospace;
  }}
  .meta code {{ background: transparent; padding: 0; color: var(--muted); font-size: 10px; }}
  .meta.metrics {{ color: var(--dim); }}
  .parent-link {{ color: var(--accent); font-size: 9px; margin-left: 4px; }}
  .retention {{ margin-top: 4px; }}
  .retention .bar {{
    background: #2a2a2a; height: 3px; border-radius: 2px; overflow: hidden;
    margin-top: 2px;
  }}
  .retention .fill {{ height: 100%; background: var(--win); }}
  .retention .fill.eroded {{ background: var(--warn); }}
  .ret-label {{ font-size: 9px; color: var(--muted); }}

  /* Pills + flags */
  .pill {{
    font-size: 9px; font-weight: 600; padding: 1px 5px;
    border-radius: 8px; text-transform: uppercase; letter-spacing: 0.3px;
  }}
  .pill-detected {{ background: #1e3a1e; color: #6fcf6f; }}
  .pill-suspect  {{ background: #4a2410; color: var(--danger); }}
  .pill-residual {{ background: rgba(177,78,204,0.15); color: var(--residual); border: 1px solid var(--residual); }}
  .pill-missed {{ background: #4a0000; color: #ff8080; }}
  .pill-locked {{ background: #333; color: #ccc; font-size: 10px; padding: 1px 4px; }}
  .pill-ok {{ color: var(--win); border: 1px solid var(--win); background: transparent; }}
  .pill-partial {{ color: var(--warn); border: 1px solid var(--warn); background: transparent; }}
  .flag {{
    display: inline-block; font-size: 9px; font-weight: 600;
    padding: 1px 4px; border-radius: 2px;
    font-family: ui-monospace, monospace;
  }}
  .flag-over_eroded {{ background: var(--warn); color: #000; }}
  .flag-low_bbox_fill, .flag-mask_outside_bbox, .flag-empty_mask {{
    background: var(--danger); color: #fff;
  }}
</style>
</head>
<body>
<header class="top" id="top">
  <h1>Vulca layer decomposition showcase</h1>
  <p class="subtitle">
    Each image is decomposed into ordered transparent layers — subjects, faces, objects,
    and a synthetic <strong>residual</strong> layer for anything the plan didn't name —
    via an agent-directed segmentation pipeline (YOLO + Grounding DINO + SAM ViT-L +
    SegFormer face-parsing). Layer order is hierarchical: a face is a child of its
    person, sub-parts don't carve parents.
  </p>
  <div class="global-stats">
    <div><span class="num">{stats['images']}</span> images</div>
    <div><span class="num">{stats['layers']}</span> layers total ({stats['avg_per_image']:.1f}/image)</div>
    <div><span class="num">{stats['residual_images']}</span>/<span>{stats['images']}</span> emit residual</div>
    <div>avg residual coverage: <span class="num">{stats['avg_residual_pct']:.1f}%</span></div>
    <div>{status_pills}</div>
  </div>
  <div class="legend">
    <span><span class="pill pill-residual">residual</span> = pipeline-synthesized, contains plan-uncovered pixels</span>
    <span><span class="pill pill-locked">🔒</span> = locked, redraw blocked by pipeline</span>
    <span>yellow retention bar = higher-z foreground occluded this layer</span>
  </div>
  <p class="narrative">
    The <strong>residual</strong> layer is the agent-native honesty signal: when the
    pipeline can't cover every pixel with a named entity, the remainder is emitted
    as a locked <code>quality_status="residual"</code> layer rather than silently
    dumped into <code>background</code>. Lower residual % = higher plan coverage.
    Visible residual means "plan could be more specific" — useful input for a
    VLM QA loop to patch the plan and re-run.
  </p>
</header>

<section>
  <h2 style="font-size: 16px; color: var(--muted); margin: 0 0 12px; letter-spacing: 0.05em; text-transform: uppercase;">
    Index · {stats['images']} images
  </h2>
  <div class="thumb-grid">
    {thumbs}
  </div>
</section>

{sections}

<footer style="color: var(--muted); font-size: 11px; margin-top: 48px;
               border-top: 1px solid var(--border); padding-top: 14px;">
  Generated by <code>scripts/build_showcase_viewer.py</code>.
  Re-run after pipeline changes to refresh. Static HTML, no server needed.
</footer>
</body>
</html>
"""
    OUT.write_text(html)
    print(f"→ {OUT}")
    print(f"  {stats['images']} images, {stats['layers']} layers "
          f"({stats['residual_images']} with residual, avg {stats['avg_residual_pct']:.1f}%)")


if __name__ == "__main__":
    main()
