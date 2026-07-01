from __future__ import annotations

import argparse
import asyncio
import html
import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output/video/3d-vector-aesthetic-stage/voice-auditions"

SCRIPT_VARIANTS = [
    {
        "id": "01_effect_plan",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Effect + next plan",
        "persona": "推荐版：直接讲效果、继续扩展数据库、未来生成作品和教程。",
        "rate": "-6%",
        "pitch": "-2Hz",
        "script": [
            "这一版展示的是三维矢量技术美学效果。",
            "画面里有三维文字、粒子云、发光轨迹，还有鼠标触发的空间变化。",
            "接下来会继续收集新的参考案例，把更多网页三维、字体动画、着色器和界面效果拆进数据库。",
            "未来会用这些模块生成一系列互动作品，也会整理成教程，持续迭代这个风格。",
        ],
    },
    {
        "id": "02_short_direct",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Short direct",
        "persona": "更短，适合节奏更快的视频。",
        "rate": "-6%",
        "pitch": "-2Hz",
        "script": [
            "现在先看这一版效果。",
            "三维文字、粒子和光线会跟着鼠标一起变化。",
            "后面会继续补充参考案例，扩展数据库。",
            "未来会用这个数据库生成更多互动作品和制作教程。",
        ],
    },
    {
        "id": "03_product_roadmap",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Product roadmap",
        "persona": "更偏项目规划，强调数据库到作品生成的路径。",
        "rate": "-7%",
        "pitch": "-2Hz",
        "script": [
            "现在先完成第一版可交互视觉效果。",
            "它包含三维文字、粒子轨迹、发光线条和鼠标响应。",
            "下一步会继续补充参考案例，把不同风格拆成数据库字段。",
            "再往后，我们会根据这些字段自动组合出新的页面、视频和教程。",
            "目标是做出一套持续更新的技术美学创作系统。",
        ],
    },
]


def run(cmd: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, check=True, capture_output=True)


def script_text(candidate: dict[str, object]) -> str:
    return "\n".join(str(line) for line in candidate["script"]) + "\n"


async def synthesize_edge(candidate: dict[str, str], output_path: Path) -> None:
    try:
        import edge_tts
    except ModuleNotFoundError as exc:
        raise SystemExit("edge-tts is required: run `python3 -m pip install --user edge-tts`") from exc

    communicate = edge_tts.Communicate(
        script_text(candidate),
        candidate["voice"],
        rate=candidate["rate"],
        pitch=candidate["pitch"],
    )
    await communicate.save(str(output_path))


def postprocess_audio(input_path: Path, output_path: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i",
            str(input_path),
            "-af",
            "loudnorm=I=-18:TP=-2:LRA=9,acompressor=threshold=-20dB:ratio=1.8:attack=20:release=180",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )


def ffprobe(path: Path) -> dict[str, object]:
    return json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=codec_name,codec_type",
                "-of",
                "json",
                str(path),
            ]
        ).stdout
    )


def write_review_html(output_dir: Path, manifest: dict[str, object]) -> Path:
    cards = []
    for item in manifest["candidates"]:
        audio_name = html.escape(Path(item["path"]).name)
        candidate_script = "\n".join(
            f"<p>{html.escape(str(line))}</p>" for line in item["script"]
        )
        cards.append(
            f"""
            <article class="card">
              <div class="rank">{html.escape(item["id"].split("_", 1)[0])}</div>
              <h2>{html.escape(item["label"])}</h2>
              <p>{html.escape(item["persona"])}</p>
              <dl>
                <dt>voice</dt><dd>{html.escape(item["voice"])}</dd>
                <dt>rate / pitch</dt><dd>{html.escape(item["rate"])} / {html.escape(item["pitch"])}</dd>
                <dt>duration</dt><dd>{item["duration_seconds"]:.2f}s</dd>
              </dl>
              <div class="copy">{candidate_script}</div>
              <audio controls preload="metadata" src="{audio_name}"></audio>
            </article>
            """
        )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vector Stage Voice Auditions</title>
  <style>
    :root {{
      color-scheme: dark;
      --ink: #090b0e;
      --paper: #f3eedf;
      --muted: rgba(243, 238, 223, 0.66);
      --cyan: #46e2dd;
      --acid: #b7ff62;
      --line: rgba(243, 238, 223, 0.14);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 24% 22%, rgba(70, 226, 221, 0.14), transparent 34%),
        radial-gradient(circle at 80% 20%, rgba(183, 255, 98, 0.08), transparent 28%),
        var(--ink);
      color: var(--paper);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(1180px, calc(100vw - 44px));
      margin: 0 auto;
      padding: 38px 0 48px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(300px, 0.8fr);
      gap: 28px;
      align-items: start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 24px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(30px, 6vw, 66px);
      line-height: 0.92;
      letter-spacing: 0;
    }}
    .meta {{
      color: var(--muted);
      font: 13px/1.55 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    .script {{
      border-left: 2px solid var(--cyan);
      padding-left: 18px;
      color: rgba(243, 238, 223, 0.84);
    }}
    .script p {{
      margin: 0 0 8px;
      line-height: 1.45;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .card {{
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.035);
      padding: 18px;
      border-radius: 8px;
      min-height: 250px;
      position: relative;
    }}
    .rank {{
      position: absolute;
      top: 16px;
      right: 16px;
      font: 700 12px/1 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: var(--acid);
    }}
    h2 {{
      margin: 0 42px 8px 0;
      font-size: 20px;
      letter-spacing: 0;
    }}
    p {{
      color: var(--muted);
      line-height: 1.55;
    }}
    dl {{
      display: grid;
      grid-template-columns: 92px minmax(0, 1fr);
      gap: 6px 10px;
      margin: 14px 0;
      font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    dt {{ color: rgba(183, 255, 98, 0.8); }}
    dd {{ margin: 0; color: rgba(243, 238, 223, 0.74); }}
    .copy {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
      margin-top: 12px;
      min-height: 156px;
    }}
    .copy p {{
      margin: 0 0 7px;
      color: rgba(243, 238, 223, 0.82);
      line-height: 1.5;
    }}
    audio {{
      width: 100%;
      margin-top: 8px;
    }}
    @media (max-width: 820px) {{
      header, .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <section>
        <h1>Voice Auditions</h1>
        <div class="meta">
          VULCA VECTOR STAGE / HORIZONTAL VIDEO<br>
          selected Xiaoxiao voice, copy variants, normalized audio
        </div>
      </section>
      <section class="script">
        <p>正式视频使用推荐版：先说明视觉效果，再说明继续补案例和未来作品规划。</p>
        <p>字幕与配音来自同一组分句，试听只用于比较节奏和时长。</p>
      </section>
    </header>
    <section class="grid">
      {"".join(cards)}
    </section>
  </main>
</body>
</html>
"""
    path = output_dir / "index.html"
    path.write_text(html_text, encoding="utf-8")
    return path


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_dir / "_tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    candidates = []
    for candidate in SCRIPT_VARIANTS:
        raw_path = tmp_dir / f"{candidate['id']}.mp3"
        final_path = output_dir / f"{candidate['id']}.mp3"
        asyncio.run(synthesize_edge(candidate, raw_path))
        postprocess_audio(raw_path, final_path)
        probe = ffprobe(final_path)
        enriched = {
            **candidate,
            "path": str(final_path),
            "duration_seconds": float(probe["format"]["duration"]),
            "size_bytes": int(probe["format"]["size"]),
        }
        candidates.append(enriched)

    manifest = {
        "script_variants": [
            {"id": candidate["id"], "script": candidate["script"]}
            for candidate in SCRIPT_VARIANTS
        ],
        "candidates": candidates,
    }
    manifest["review_html"] = str(write_review_html(output_dir, manifest))
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    shutil.rmtree(tmp_dir)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build voice audition audio for the vector stage video.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    manifest = build(args.output_dir.resolve())
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
