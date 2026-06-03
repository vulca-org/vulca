from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


DEFAULT_THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK_REL = Path("docs") / "product" / "ppt-run2-data-skill-quality"
BOUNDARY = "not_pptx_not_keynote_animation"

SCENES: list[dict[str, Any]] = [
    {
        "scene_id": "cover_attention_reset",
        "role": "cover",
        "title": "Data becomes a presentation system",
        "subtitle": "One field appears before proof density.",
        "source_motion_contract_ids": [
            "beat_opening_scale_reset",
            "motion_target_opening_attention_reset",
            "sequence_component_opening_reset",
        ],
        "animation_steps": [
            "hold a quiet field",
            "bring in the claim",
            "settle on one proof object",
        ],
        "reduced_motion_fallback": "show final claim and proof object without movement",
        "accent": "#e84d2a",
    },
    {
        "scene_id": "before_after_reveal",
        "role": "before_after",
        "title": "Before becomes after through memory",
        "subtitle": "The route moves from weak prompt output to selected module output.",
        "source_motion_contract_ids": [
            "beat_before_after_transformation",
            "motion_target_before_after_reveal",
            "sequence_component_before_after_reveal",
        ],
        "animation_steps": [
            "show before state",
            "move through selector memory",
            "resolve to after state",
        ],
        "reduced_motion_fallback": "show before, selector, and after states at once",
        "accent": "#2d6cdf",
    },
    {
        "scene_id": "climax_scale_emphasis",
        "role": "climax",
        "title": "The climax becomes one object",
        "subtitle": "The metric enlarges after proof is understood.",
        "source_motion_contract_ids": [
            "beat_climax_scale_up",
            "motion_target_climax_scale_emphasis",
            "sequence_component_climax_scale",
        ],
        "animation_steps": [
            "dim surrounding proof",
            "scale the outcome object",
            "hold on the release gate",
        ],
        "reduced_motion_fallback": "show enlarged outcome and release gate without scaling",
        "accent": "#13a678",
    },
]


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def scene_markup(scene: dict[str, Any], index: int) -> str:
    chips = "".join(f"<span>{esc(item)}</span>" for item in scene["source_motion_contract_ids"])
    steps = "".join(
        f"<li><b>{step_index:02d}</b><span>{esc(step)}</span></li>"
        for step_index, step in enumerate(scene["animation_steps"], start=1)
    )
    return f"""
      <section class="scene {esc(scene['role'])}" data-scene-id="{esc(scene['scene_id'])}" style="--accent:{esc(scene['accent'])}">
        <div class="sceneMeta">
          <span class="kicker">Scene {index:02d}</span>
          <h2>{esc(scene['title'])}</h2>
          <p>{esc(scene['subtitle'])}</p>
          <div class="chips">{chips}</div>
        </div>
        <div class="stage" aria-label="{esc(scene['scene_id'])} motion stage">
          <div class="field fieldA"></div>
          <div class="field fieldB"></div>
          <div class="orbit"></div>
          <div class="proof proofA">source</div>
          <div class="proof proofB">memory</div>
          <div class="proof proofC">output</div>
          <div class="heroMark">{esc(scene['role']).replace('_', '<br>')}</div>
          <div class="route"></div>
        </div>
        <ol class="steps">{steps}</ol>
      </section>
    """


def build_html(manifest: dict[str, Any]) -> str:
    scenes = "\n".join(scene_markup(scene, index) for index, scene in enumerate(manifest["scenes"], start=1))
    payload = json.dumps(manifest, ensure_ascii=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Run 2.17 Motion Renderer Proof</title>
  <style>
    :root {{
      --ink: #14171c;
      --paper: #f6f3ec;
      --panel: #ffffff;
      --line: #d6d0c5;
      --muted: #66707c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .shell {{ min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 24px;
      border-bottom: 1px solid var(--line);
      background: rgba(246, 243, 236, 0.94);
      position: sticky;
      top: 0;
      z-index: 3;
    }}
    h1 {{ margin: 0; font-size: 22px; line-height: 1.1; }}
    .meta {{ margin-top: 4px; color: var(--muted); font-size: 12px; }}
    .controls {{ display: flex; align-items: center; gap: 8px; }}
    button {{
      height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 0 12px;
      cursor: pointer;
      font: inherit;
    }}
    button.primary {{ background: var(--ink); border-color: var(--ink); color: #fff; }}
    .timeline {{ height: 3px; background: #ddd8cf; }}
    .progress {{ width: 0%; height: 100%; background: #e84d2a; transition: width 0.2s linear; }}
    main {{ padding: 22px; display: grid; gap: 18px; }}
    .scene {{
      display: grid;
      grid-template-columns: minmax(280px, 0.62fr) minmax(520px, 1fr) minmax(230px, 0.44fr);
      gap: 18px;
      min-height: 520px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      padding: 18px;
    }}
    .sceneMeta {{ align-self: stretch; display: flex; flex-direction: column; justify-content: space-between; gap: 18px; }}
    .kicker {{ color: var(--accent); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    h2 {{ margin: 0; font-size: clamp(34px, 5vw, 76px); line-height: 0.95; letter-spacing: 0; }}
    p {{ margin: 0; color: var(--muted); font-size: 15px; line-height: 1.45; max-width: 34em; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .chips span {{
      display: inline-flex;
      min-height: 24px;
      align-items: center;
      border: 1px solid #dcd6cc;
      border-radius: 999px;
      padding: 3px 8px;
      background: #f8f7f3;
      color: #3c434d;
      font-size: 11px;
    }}
    .stage {{
      position: relative;
      min-height: 470px;
      border: 1px solid #c9c4bb;
      border-radius: 8px;
      background: linear-gradient(135deg, #fbfaf7 0%, #ede8dd 100%);
      overflow: hidden;
      isolation: isolate;
    }}
    .field, .orbit, .proof, .heroMark, .route {{ position: absolute; }}
    .field {{
      border: 1px solid color-mix(in srgb, var(--accent) 36%, #bbb 64%);
      background: color-mix(in srgb, var(--accent) 9%, #fff 91%);
    }}
    .fieldA {{ left: 9%; top: 12%; width: 54%; height: 38%; }}
    .fieldB {{ right: 8%; bottom: 13%; width: 44%; height: 34%; }}
    .orbit {{
      width: 280px;
      height: 280px;
      left: calc(50% - 140px);
      top: calc(50% - 140px);
      border: 1px dashed color-mix(in srgb, var(--accent) 60%, #999 40%);
      border-radius: 50%;
    }}
    .proof {{
      display: grid;
      place-items: center;
      width: 110px;
      height: 70px;
      border-radius: 6px;
      border: 1px solid #bdc3cb;
      background: #fff;
      color: #333a44;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .proofA {{ left: 10%; bottom: 18%; }}
    .proofB {{ left: calc(50% - 55px); bottom: 32%; }}
    .proofC {{ right: 11%; top: 18%; }}
    .heroMark {{
      right: 9%;
      bottom: 14%;
      min-width: 190px;
      min-height: 150px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      background: var(--ink);
      color: #fff;
      font-size: 34px;
      font-weight: 900;
      line-height: 0.96;
      text-transform: uppercase;
      text-align: center;
      transform-origin: 50% 50%;
    }}
    .route {{
      left: 12%;
      top: 48%;
      width: 70%;
      height: 3px;
      background: var(--accent);
      transform-origin: 0 50%;
    }}
    .steps {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      align-content: end;
      gap: 10px;
    }}
    .steps li {{
      min-height: 58px;
      border-top: 1px solid var(--line);
      padding-top: 10px;
      display: grid;
      gap: 3px;
    }}
    .steps b {{ color: var(--accent); font-size: 12px; }}
    .steps span {{ color: #252a31; font-size: 13px; line-height: 1.35; }}
    body.playing .cover .fieldA {{ animation: rise 4.8s ease-in-out infinite; }}
    body.playing .cover .heroMark {{ animation: settle 4.8s ease-in-out infinite; }}
    body.playing .before_after .route {{ animation: routeGrow 4.8s ease-in-out infinite; }}
    body.playing .before_after .proofB {{ animation: travel 4.8s ease-in-out infinite; }}
    body.playing .climax .heroMark {{ animation: climax 4.8s ease-in-out infinite; }}
    body.playing .climax .fieldB {{ animation: dimPulse 4.8s ease-in-out infinite; }}
    @keyframes rise {{
      0%, 18% {{ opacity: 0.2; transform: translateY(18px) scale(0.98); }}
      42%, 100% {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    @keyframes settle {{
      0%, 45% {{ transform: scale(0.72); opacity: 0.2; }}
      68%, 100% {{ transform: scale(1); opacity: 1; }}
    }}
    @keyframes routeGrow {{
      0%, 16% {{ transform: scaleX(0.04); }}
      55%, 100% {{ transform: scaleX(1); }}
    }}
    @keyframes travel {{
      0%, 18% {{ transform: translateX(-170px); opacity: 0.25; }}
      54%, 100% {{ transform: translateX(0); opacity: 1; }}
    }}
    @keyframes climax {{
      0%, 24% {{ transform: scale(0.58); opacity: 0.3; }}
      58%, 76% {{ transform: scale(1.18); opacity: 1; }}
      100% {{ transform: scale(1); opacity: 1; }}
    }}
    @keyframes dimPulse {{
      0%, 30% {{ opacity: 1; }}
      60%, 100% {{ opacity: 0.34; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{ animation: none !important; transition: none !important; }}
      .progress {{ width: 100% !important; }}
    }}
    @media (max-width: 980px) {{
      .scene {{ grid-template-columns: 1fr; }}
      .stage {{ min-height: 360px; }}
      h2 {{ font-size: 42px; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
    }}
  </style>
</head>
<body class="playing">
  <div class="shell">
    <header>
      <div class="topbar">
        <div>
          <h1>Run 2.17 Motion Renderer Proof</h1>
          <div class="meta">{esc(manifest['delivery_boundary']['motion_proof_role'])} / {esc(manifest['delivery_boundary']['native_pptx_animation_claim'])} / public blocked</div>
        </div>
        <div class="controls" aria-label="Motion controls">
          <button class="primary" id="play">Play</button>
          <button id="pause">Pause</button>
          <button id="restart">Restart</button>
        </div>
      </div>
      <div class="timeline"><div class="progress" id="progress"></div></div>
    </header>
    <main>{scenes}</main>
  </div>
  <script type="application/json" id="manifest">{esc(payload)}</script>
  <script>
    const body = document.body;
    const progress = document.getElementById("progress");
    let started = performance.now();
    let playing = true;
    function tick(now) {{
      if (playing) {{
        const pct = ((now - started) % 4800) / 48;
        progress.style.width = pct.toFixed(2) + "%";
      }}
      requestAnimationFrame(tick);
    }}
    document.getElementById("play").addEventListener("click", () => {{
      playing = true;
      body.classList.add("playing");
    }});
    document.getElementById("pause").addEventListener("click", () => {{
      playing = false;
      body.classList.remove("playing");
    }});
    document.getElementById("restart").addEventListener("click", () => {{
      started = performance.now();
      playing = true;
      body.classList.remove("playing");
      void body.offsetWidth;
      body.classList.add("playing");
    }});
    requestAnimationFrame(tick);
  </script>
</body>
</html>
"""


def build_manifest(repo_root: Path, presentations_dir: Path) -> dict[str, Any]:
    html_path = presentations_dir / "run2-17-motion-renderer-proof.html"
    manifest_path = presentations_dir / "run2-17-motion-renderer-proof-manifest.json"
    return {
        "schema_version": 1,
        "status": "motion_renderer_proof_created_public_blocked",
        "public_ready": False,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "run_id": "2.17-motion-proof",
        "source_generated_run_id": "2.16",
        "source_audit": "run2_17_motion_delivery_audit.json",
        "delivery_boundary": {
            "static_ppt_role": "editable_product_output",
            "motion_proof_role": "separate_html_motion_renderer",
            "native_pptx_animation_claim": "not_claimed",
            "keynote_animation_claim": "not_claimed",
            "boundary_id": BOUNDARY,
        },
        "local_outputs": {
            "html": rel(html_path, repo_root),
            "manifest": rel(manifest_path, repo_root),
        },
        "scenes": [
            {
                **scene,
                "public_release_gate": "blocked_until_human_review_and_video_export_gate",
            }
            for scene in SCENES
        ],
        "qa_summary": {
            "scene_count": "passed: cover, before/after, and climax proof scenes generated",
            "motion_boundary": "passed: motion proof is separate HTML and does not claim Keynote animation",
            "reduced_motion": "passed: CSS prefers-reduced-motion fallback included",
            "public_release_gate": "blocked pending human review, video export gate, and native render inspection",
        },
    }


def write_markdown(result: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# Run 2.17 Motion Renderer Proof Result",
        "",
        "Status: motion renderer proof created, public blocked.",
        "",
        "Run 2.17 motion renderer proof creates a separate HTML motion renderer. It is not Keynote animation and it does not replace the editable static PPT output.",
        "",
        "## Local Outputs",
        "",
        f"- HTML: `{result['local_outputs']['html']}`",
        f"- Manifest: `{result['local_outputs']['manifest']}`",
        "",
        "## Scenes",
        "",
    ]
    for scene in result["scenes"]:
        lines.extend(
            [
                f"### `{scene['scene_id']}`",
                "",
                f"- Role: `{scene['role']}`",
                f"- Source motion contracts: `{', '.join(scene['source_motion_contract_ids'])}`",
                f"- Steps: `{', '.join(scene['animation_steps'])}`",
                f"- Reduced motion fallback: {scene['reduced_motion_fallback']}",
                f"- Gate: `{scene['public_release_gate']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "- Static PPT remains the editable product output.",
            "- Motion proof role: `separate HTML motion renderer`.",
            "- Native PPT animation claim: `not_claimed`.",
            "- Keynote animation claim: `not_claimed`.",
            "- Public release remains blocked.",
            "",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Run 2.17 HTML motion renderer proof.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--thread-id", default=DEFAULT_THREAD_ID)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    presentations_dir = repo_root / "outputs" / args.thread_id / "presentations"
    pack = repo_root / PACK_REL
    result = build_manifest(repo_root, presentations_dir)

    html_path = repo_root / result["local_outputs"]["html"]
    manifest_path = repo_root / result["local_outputs"]["manifest"]
    result_json_path = pack / "results" / "run2_17_motion_renderer_proof_result.json"
    result_md_path = pack / "results" / "run2_17_motion_renderer_proof_result.md"

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(build_html(result), encoding="utf-8")
    manifest_path.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    result_json_path.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, result_md_path)

    print(json.dumps({"html": rel(html_path, repo_root), "manifest": rel(manifest_path, repo_root)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
