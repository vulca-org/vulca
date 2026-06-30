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

VOICE_SCRIPT = [
    "这不是一张海报。",
    "更像是一段可以操作的三维矢量样本。",
    "二零二五年之后，网页三维开始变得不一样。",
    "粒子、字体、着色器，不再只是效果。",
    "它们变成了可以学习的视觉原语。",
    "我们用鼠标穿过这套结构，看线条怎么组织速度、深度和节奏。",
    "接下来，用这个数据库，继续生成更完整的技术美学作品。",
]

CANDIDATES = [
    {
        "id": "01_xiaoxiao_curator",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoxiaoNeural",
        "label": "Xiaoxiao / curator",
        "persona": "温暖、克制、偏策展人旁白，最接近当前方向。",
        "rate": "-6%",
        "pitch": "-2Hz",
    },
    {
        "id": "02_yunyang_documentary",
        "provider": "edge-neural",
        "voice": "zh-CN-YunyangNeural",
        "label": "Yunyang / documentary",
        "persona": "专业、可靠、偏纪录片男声，适合技术解释但可能稍正式。",
        "rate": "-7%",
        "pitch": "-4Hz",
    },
    {
        "id": "03_yunxi_creator",
        "provider": "edge-neural",
        "voice": "zh-CN-YunxiNeural",
        "label": "Yunxi / young creator",
        "persona": "年轻、清亮、有内容创作者感，适合小红书但可能偏轻。",
        "rate": "-7%",
        "pitch": "-3Hz",
    },
    {
        "id": "04_xiaoyi_soft",
        "provider": "edge-neural",
        "voice": "zh-CN-XiaoyiNeural",
        "label": "Xiaoyi / soft narrative",
        "persona": "柔和、小说感，情绪更近但可能少一点技术感。",
        "rate": "-8%",
        "pitch": "-3Hz",
    },
    {
        "id": "05_yunjian_energy",
        "provider": "edge-neural",
        "voice": "zh-CN-YunjianNeural",
        "label": "Yunjian / energetic",
        "persona": "更有推动力和能量，适合强节奏片，但可能过度用力。",
        "rate": "-8%",
        "pitch": "-5Hz",
    },
]


def run(cmd: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, check=True, capture_output=True)


def script_text() -> str:
    return "\n".join(VOICE_SCRIPT) + "\n"


async def synthesize_edge(candidate: dict[str, str], output_path: Path) -> None:
    try:
        import edge_tts
    except ModuleNotFoundError as exc:
        raise SystemExit("edge-tts is required: run `python3 -m pip install --user edge-tts`") from exc

    communicate = edge_tts.Communicate(
        script_text(),
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
              <audio controls preload="metadata" src="{audio_name}"></audio>
            </article>
            """
        )

    script_lines = "\n".join(f"<p>{html.escape(line)}</p>" for line in VOICE_SCRIPT)
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
          shared script, normalized audio, generated locally for review
        </div>
      </section>
      <section class="script">{script_lines}</section>
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
    for candidate in CANDIDATES:
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
        "script": VOICE_SCRIPT,
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
