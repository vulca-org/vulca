from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_vector_stage_video import (  # noqa: E402
    CHROME_EXECUTABLE,
    DEFAULT_OUTPUT,
    PLAYWRIGHT_MODULE,
    PRODUCT_HTML,
    REPO_ROOT,
    ffprobe_duration,
    find_free_port,
    require_tool,
    run,
    start_http_server,
    synthesize_voiceover,
    wait_for_http,
    write_ass_subtitles,
    write_music,
)


DEFAULT_LIVE_OUTPUT = DEFAULT_OUTPUT.with_name("vector-stage-xhs-horizontal-live-20260630.mp4")


def escape_filter_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def run_live_browser(
    *,
    work_dir: Path,
    url: str,
    width: int,
    height: int,
    duration: float,
    pre_roll: float,
) -> Path:
    if not CHROME_EXECUTABLE.exists():
        raise SystemExit(f"Chrome executable not found: {CHROME_EXECUTABLE}")
    if not PLAYWRIGHT_MODULE.exists():
        raise SystemExit(f"Playwright module not found: {PLAYWRIGHT_MODULE}")

    raw_dir = work_dir / "raw-live"
    raw_dir.mkdir(parents=True, exist_ok=True)
    capture_script = work_dir / "record_live.cjs"
    capture_script.write_text(
        textwrap.dedent(
            f"""
            const {{ chromium }} = require({json.dumps(str(PLAYWRIGHT_MODULE))});

            (async () => {{
              const browser = await chromium.launch({{
                executablePath: {json.dumps(str(CHROME_EXECUTABLE))},
                headless: false,
                args: [
                  '--window-size={width},{height}',
                  '--disable-background-timer-throttling',
                  '--disable-backgrounding-occluded-windows',
                  '--disable-renderer-backgrounding'
                ]
              }});
              const context = await browser.newContext({{
                viewport: {{ width: {width}, height: {height} }},
                deviceScaleFactor: 1,
                recordVideo: {{
                  dir: {json.dumps(str(raw_dir))},
                  size: {{ width: {width}, height: {height} }}
                }}
              }});
              const page = await context.newPage();
              await page.goto({json.dumps(url)}, {{ waitUntil: 'domcontentloaded' }});
              await page.evaluate((preRollMs) => {{
                const badge = document.createElement('div');
                badge.textContent = 'LIVE CAPTURE';
                badge.style.cssText = [
                  'position:fixed',
                  'left:24px',
                  'bottom:24px',
                  'z-index:9999',
                  'padding:10px 14px',
                  'border:1px solid rgba(245,240,223,.28)',
                  'background:rgba(5,6,8,.72)',
                  'color:#f5f0df',
                  'font:700 12px ui-monospace,SFMono-Regular,Menlo,monospace',
                  'letter-spacing:0',
                  'pointer-events:none'
                ].join(';');
                document.body.appendChild(badge);
                window.setTimeout(() => badge.remove(), preRollMs);
              }}, {int(pre_roll * 1000)});
              console.log('LIVE_CAPTURE_READY move the mouse in the Chrome window now');
              await page.waitForTimeout({int((pre_roll + duration + 0.75) * 1000)});
              const video = page.video();
              await context.close();
              await browser.close();
              console.log(JSON.stringify({{ raw: await video.path() }}));
            }})().catch((error) => {{
              console.error(error);
              process.exit(1);
            }});
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    process = subprocess.Popen(
        ["node", str(capture_script)],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    raw_path: Path | None = None
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "raw" in payload:
            raw_path = Path(payload["raw"])
    code = process.wait()
    if code != 0:
        raise subprocess.CalledProcessError(code, ["node", str(capture_script)])
    if raw_path is None or not raw_path.exists():
        raise RuntimeError("live capture did not produce a raw Playwright video")
    return raw_path


def build_live_video(
    *,
    output: Path,
    duration: float,
    width: int,
    height: int,
    voice: str,
    voice_rate: int,
    pre_roll: float,
    video_bitrate: str,
    video_maxrate: str,
    video_bufsize: str,
) -> dict[str, object]:
    require_tool("node")
    require_tool("say")
    require_tool("ffmpeg")
    require_tool("ffprobe")
    if not PRODUCT_HTML.exists():
        raise SystemExit(f"product HTML not found: {PRODUCT_HTML}")

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work_dir = output.parent / "_live_build"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    voiceover = synthesize_voiceover(work_dir, voice, voice_rate)
    voice_path = Path(str(voiceover["path"]))
    voice_duration = float(voiceover["duration"])
    final_duration = duration if duration > 0 else round(voice_duration + 1.2, 3)
    music_wav = work_dir / "music.wav"
    subtitles_ass = work_dir / "subtitles.ass"
    write_music(music_wav, final_duration)
    write_ass_subtitles(subtitles_ass, list(voiceover["cues"]), width, height, final_duration)

    port = find_free_port()
    server = start_http_server(port)
    try:
        wait_for_http(port)
        url = (
            f"http://127.0.0.1:{port}/"
            "docs/product/experiments/3d-vector-aesthetic-stage/index.html?capture=1"
        )
        raw_video = run_live_browser(
            work_dir=work_dir,
            url=url,
            width=width,
            height=height,
            duration=final_duration,
            pre_roll=pre_roll,
        )
    finally:
        server.terminate()
        try:
            server.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server.kill()

    filter_graph = (
        f"[0:v]trim=start={pre_roll:.3f}:duration={final_duration:.3f},setpts=PTS-STARTPTS,"
        f"scale={width}:{height}:flags=lanczos,ass='{escape_filter_path(subtitles_ass)}',format=yuv420p[v];"
        "[1:a]volume=1.12,adelay=220|220,apad[a1];"
        f"[2:a]volume=0.18,afade=t=in:st=0:d=1.0,"
        f"afade=t=out:st={max(0.0, final_duration - 1.4):.2f}:d=1.4[a2];"
        f"[a1][a2]amix=inputs=2:duration=longest:normalize=0,"
        f"atrim=0:{final_duration:.3f},volume=0.86,alimiter=limit=0.90[a]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i",
            str(raw_video),
            "-i",
            str(voice_path),
            "-i",
            str(music_wav),
            "-filter_complex",
            filter_graph,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-r",
            "24",
            "-t",
            f"{final_duration:.3f}",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            video_bitrate,
            "-maxrate",
            video_maxrate,
            "-bufsize",
            video_bufsize,
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    poster = output.with_suffix(".poster.jpg")
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-ss",
            "4.0",
            "-i",
            str(output),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(poster),
        ]
    )
    manifest = {
        "output": str(output),
        "poster": str(poster),
        "raw_video": str(raw_video),
        "duration_seconds": final_duration,
        "width": width,
        "height": height,
        "pre_roll_seconds": pre_roll,
        "voice": voiceover["voice"],
        "voice_duration_seconds": round(voice_duration, 3),
        "voice_script": voiceover["script"],
        "subtitles": str(subtitles_ass),
        "music": str(music_wav),
        "video_bitrate": video_bitrate,
        "video_duration_probe": ffprobe_duration(output),
    }
    output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record the vector stage from real mouse interaction.")
    parser.add_argument("--output", type=Path, default=DEFAULT_LIVE_OUTPUT)
    parser.add_argument("--duration", type=float, default=0)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--voice-rate", type=int, default=170)
    parser.add_argument("--pre-roll", type=float, default=3.0)
    parser.add_argument("--video-bitrate", default="24M")
    parser.add_argument("--video-maxrate", default="30M")
    parser.add_argument("--video-bufsize", default="48M")
    args = parser.parse_args(argv)

    manifest = build_live_video(
        output=args.output,
        duration=args.duration,
        width=args.width,
        height=args.height,
        voice=args.voice,
        voice_rate=args.voice_rate,
        pre_roll=args.pre_roll,
        video_bitrate=args.video_bitrate,
        video_maxrate=args.video_maxrate,
        video_bufsize=args.video_bufsize,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
