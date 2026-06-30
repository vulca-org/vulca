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
        "id": "01_quiet_gallery",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Quiet gallery",
        "persona": "推荐版：更像展览导览，语气轻，画面连续，时长更适合视频。",
        "rate": "-8%",
        "pitch": "-3Hz",
        "script": [
            "画面先从一组细线展开。",
            "鼠标靠近时，空间像被轻轻推开。",
            "中间的粒子开始聚集，光带绕过字体，又回到中心。",
            "这套样本记录的，是线条、深度和交互之间的关系。",
            "它让一个网页场景拥有可分析的结构。",
            "后面的作品，会从这些结构继续往外延展。",
        ],
    },
    {
        "id": "02_scene_method",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Scene method",
        "persona": "更完整地讲样本库和原语，信息量更高，时长也更长。",
        "rate": "-6%",
        "pitch": "-2Hz",
        "script": [
            "屏幕里的这套结构，来自我们的三维矢量样本库。",
            "鼠标划过时，线条先把空间拉开。",
            "粒子跟着聚成一层流动的密度。",
            "字体被放进深度里，像一个可以进入的界面。",
            "我们把这些变化拆成线条、轨迹、材质、字体和交互几个原语。",
            "下一次生成作品时，就可以沿着这些原语继续组合。",
            "让技术美学，从一次画面，变成一套可以生长的方法。",
        ],
    },
    {
        "id": "03_database_method",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Database method",
        "persona": "更强调数据库和方法论，适合解释项目价值。",
        "rate": "-7%",
        "pitch": "-2Hz",
        "script": [
            "这段画面来自三维矢量美学数据库的第一组样本。",
            "每一次鼠标移动，都会改变线条的角度、粒子的密度和字体的空间关系。",
            "我们记录这些变化，是为了让风格可以被学习、复用和继续扩展。",
            "当数据库变得更完整，新的互动作品会从这里一步步生成。",
            "它会保留技术的结构，也保留视觉的气质。",
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
        <p>目标：保留温暖克制的策展人声音，去掉 AI 式反转句，让旁白顺着画面连续讲下去。</p>
        <p>检查点：避开 AI 式反转句；每一句都能对应画面里的动作、结构或方法。</p>
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
