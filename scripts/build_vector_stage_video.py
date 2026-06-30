from __future__ import annotations

import argparse
import json
import math
import shutil
import socket
import subprocess
import sys
import textwrap
import time
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_HTML = REPO_ROOT / "docs/product/experiments/3d-vector-aesthetic-stage/index.html"
DEFAULT_OUTPUT = REPO_ROOT / "output/video/3d-vector-aesthetic-stage/vector-stage-xhs-20260630.mp4"
PLAYWRIGHT_MODULE = Path(
    "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright"
)
CHROME_EXECUTABLE = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

VOICEOVER_TEXT = (
    "这不是一张海报。"
    "它是一套三维矢量美学的训练样本。"
    "我们把二零二五年之后的网页三维、粒子、字体和着色器，拆成视觉原语。"
    "线条定义速度和深度。"
    "粒子负责呼吸和节奏。"
    "字体也能成为三维结构。"
    "接下来，用这个数据库生成更多可交互的技术美学作品。"
)

SUBTITLE_CUES = [
    (0.45, 2.75, "这不是一张海报"),
    (2.75, 5.35, "它是一套三维矢量美学的训练样本"),
    (5.35, 9.15, "把 2025+ 的网页三维、粒子、字体和着色器\\N拆成视觉原语"),
    (9.15, 11.55, "线条定义速度和深度"),
    (11.55, 14.05, "粒子负责呼吸和节奏"),
    (14.05, 17.3, "字体也能成为三维结构"),
    (17.3, 22.6, "接下来，用这个数据库\\N生成更多可交互的技术美学作品"),
]


def run(cmd: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, check=True, capture_output=True)


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"required tool not found: {name}")
    return path


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def ffprobe_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(result.stdout.strip())


def seconds_to_ass(value: float) -> str:
    total_cs = max(0, int(round(value * 100)))
    cs = total_cs % 100
    total_seconds = total_cs // 100
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours}:{minutes:02d}:{seconds:02d}.{cs:02d}"


def write_ass_subtitles(path: Path, duration: float) -> None:
    cues = []
    for start, end, text in SUBTITLE_CUES:
        if start >= duration:
            continue
        cues.append((start, min(end, duration - 0.35), text))

    ass = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 540",
        "PlayResY: 960",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        ),
        (
            "Style: Default,PingFang SC,31,&H00F5F0DF,&H000000FF,"
            "&HA0050608,&HA0050608,-1,0,0,0,100,100,0,0,3,1,0,2,36,36,122,1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for start, end, text in cues:
        ass.append(
            f"Dialogue: 0,{seconds_to_ass(start)},{seconds_to_ass(end)},Default,,0,0,0,,{text}"
        )
    path.write_text("\n".join(ass) + "\n", encoding="utf-8")


def load_subtitle_font(size: int) -> tuple[ImageFont.FreeTypeFont, str]:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size), str(path)
    return ImageFont.load_default(size=size), "Pillow default"


def wrap_subtitle_text(text: str) -> list[str]:
    return [part.strip() for part in text.replace("\\N", "\n").splitlines() if part.strip()]


def burn_subtitles_on_frames(frames_dir: Path, fps: int, duration: float, width: int, height: int) -> str:
    font, font_path = load_subtitle_font(31)
    shadow_font, _ = load_subtitle_font(31)
    margin_x = 28
    base_y = height - 166

    for frame_path in sorted(frames_dir.glob("frame_*.jpg")):
        frame_number = int(frame_path.stem.split("_")[-1])
        timestamp = frame_number / fps
        cue_text = ""
        for start, end, text in SUBTITLE_CUES:
            if start <= timestamp < min(end, duration - 0.35):
                cue_text = text
                break
        if not cue_text:
            continue

        image = Image.open(frame_path).convert("RGB")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        lines = wrap_subtitle_text(cue_text)
        line_boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
        line_widths = [box[2] - box[0] for box in line_boxes]
        line_heights = [box[3] - box[1] for box in line_boxes]
        text_w = min(width - margin_x * 2, max(line_widths))
        text_h = sum(line_heights) + max(0, len(lines) - 1) * 10
        box_w = min(width - margin_x * 2, text_w + 34)
        box_h = text_h + 24
        box_x0 = (width - box_w) / 2
        box_y0 = base_y - box_h / 2
        box_x1 = box_x0 + box_w
        box_y1 = box_y0 + box_h
        draw.rounded_rectangle(
            (box_x0, box_y0, box_x1, box_y1),
            radius=15,
            fill=(5, 6, 8, 158),
            outline=(245, 240, 223, 42),
            width=1,
        )
        y = box_y0 + 13
        for index, line in enumerate(lines):
            line_w = line_widths[index]
            x = (width - line_w) / 2
            draw.text((x + 1, y + 1), line, font=shadow_font, fill=(0, 0, 0, 170))
            draw.text((x, y), line, font=font, fill=(245, 240, 223, 242))
            y += line_heights[index] + 10
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        image.save(frame_path, quality=92, subsampling=0)

    return font_path


def write_music(path: Path, duration: float, sample_rate: int = 48_000) -> None:
    n = int(duration * sample_rate)
    t = np.arange(n, dtype=np.float64) / sample_rate
    rng = np.random.default_rng(20260630)

    def sine(freq: float, phase: float = 0.0) -> np.ndarray:
        return np.sin(2 * np.pi * freq * t + phase)

    pad = (
        0.22 * sine(55)
        + 0.12 * sine(82.41, 0.4)
        + 0.08 * sine(110, 1.1)
        + 0.05 * sine(164.81, 2.0)
    )
    lfo = 0.58 + 0.42 * np.sin(2 * np.pi * 0.055 * t)
    pad *= lfo

    arpeggio = np.zeros_like(t)
    notes = [220.0, 277.18, 329.63, 440.0, 554.37, 659.25]
    step = 0.25
    for index, start in enumerate(np.arange(0.4, duration, step)):
        start_i = int(start * sample_rate)
        length = min(int(0.22 * sample_rate), n - start_i)
        if length <= 0:
            break
        local = np.arange(length, dtype=np.float64) / sample_rate
        env = np.exp(-local * 10.0)
        freq = notes[index % len(notes)] * (0.5 if index % 8 in {0, 7} else 1.0)
        arpeggio[start_i : start_i + length] += 0.11 * np.sin(2 * np.pi * freq * local) * env

    pulse = np.zeros_like(t)
    for start in np.arange(0.0, duration, 0.5):
        start_i = int(start * sample_rate)
        length = min(int(0.08 * sample_rate), n - start_i)
        if length <= 0:
            break
        local = np.arange(length, dtype=np.float64) / sample_rate
        pulse[start_i : start_i + length] += 0.08 * np.sin(2 * np.pi * 92 * local) * np.exp(-local * 24)

    noise = rng.normal(0, 0.018, n)
    shimmer = noise * (0.25 + 0.75 * (np.sin(2 * np.pi * 0.75 * t) > 0.75))
    mix = pad + arpeggio + pulse + shimmer

    fade = min(n // 8, int(1.2 * sample_rate))
    envelope = np.ones(n)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)
    mix *= envelope
    mix /= max(1.0, np.max(np.abs(mix)) / 0.72)

    stereo = np.column_stack([mix * 0.88, np.roll(mix, int(0.011 * sample_rate)) * 0.82])
    pcm = np.clip(stereo * 32767, -32768, 32767).astype("<i2")

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def start_http_server(port: int) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_http(port: int) -> None:
    deadline = time.time() + 8
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError("local HTTP server did not start")


def capture_frames(work_dir: Path, url: str, width: int, height: int, fps: int, frame_count: int) -> None:
    if not CHROME_EXECUTABLE.exists():
        raise SystemExit(f"Chrome executable not found: {CHROME_EXECUTABLE}")
    if not PLAYWRIGHT_MODULE.exists():
        raise SystemExit(f"Playwright module not found: {PLAYWRIGHT_MODULE}")

    frames_dir = work_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    capture_script = work_dir / "capture_frames.cjs"
    capture_script.write_text(
        textwrap.dedent(
            f"""
            const {{ chromium }} = require({json.dumps(str(PLAYWRIGHT_MODULE))});

            (async () => {{
              const browser = await chromium.launch({{
                executablePath: {json.dumps(str(CHROME_EXECUTABLE))},
                headless: true,
                args: [
                  '--disable-background-timer-throttling',
                  '--disable-backgrounding-occluded-windows',
                  '--disable-renderer-backgrounding'
                ]
              }});
              const page = await browser.newPage({{
                viewport: {{ width: {width}, height: {height} }},
                deviceScaleFactor: 1
              }});
              await page.goto({json.dumps(url)}, {{ waitUntil: 'domcontentloaded' }});
              await page.waitForFunction(() => typeof window.__VULCA_RENDER_FRAME__ === 'function');
              for (let frame = 0; frame < {frame_count}; frame += 1) {{
                await page.evaluate(
                  (payload) => window.__VULCA_RENDER_FRAME__(payload.frame, payload.fps),
                  {{ frame, fps: {fps} }}
                );
                const name = `frame_${{String(frame).padStart(5, '0')}}.jpg`;
                await page.screenshot({{
                  path: {json.dumps(str(frames_dir))} + '/' + name,
                  type: 'jpeg',
                  quality: 92,
                  animations: 'disabled',
                  fullPage: false
                }});
                if (frame % {fps * 2} === 0) {{
                  console.log(`captured ${{frame}}/{frame_count}`);
                }}
              }}
              await browser.close();
            }})().catch((error) => {{
              console.error(error);
              process.exit(1);
            }});
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    run(["node", str(capture_script)])


def build_video(
    *,
    output: Path,
    duration: float,
    fps: int,
    width: int,
    height: int,
    voice: str,
    voice_rate: int,
    keep_frames: bool,
) -> dict[str, object]:
    require_tool("node")
    require_tool("say")
    require_tool("ffmpeg")
    require_tool("ffprobe")
    if not PRODUCT_HTML.exists():
        raise SystemExit(f"product HTML not found: {PRODUCT_HTML}")

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work_dir = output.parent / "_build"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    voice_txt = work_dir / "voiceover.txt"
    voice_aiff = work_dir / "voiceover.aiff"
    music_wav = work_dir / "music.wav"
    subtitles_ass = work_dir / "subtitles.ass"
    poster = output.with_suffix(".poster.jpg")

    voice_txt.write_text(VOICEOVER_TEXT, encoding="utf-8")
    run(["say", "-v", voice, "-r", str(voice_rate), "-o", str(voice_aiff), "-f", str(voice_txt)])
    voice_duration = ffprobe_duration(voice_aiff)
    final_duration = max(duration, math.ceil((voice_duration + 1.2) * 10) / 10)
    frame_count = int(math.ceil(final_duration * fps))

    write_music(music_wav, final_duration)
    write_ass_subtitles(subtitles_ass, final_duration)

    port = find_free_port()
    server = start_http_server(port)
    try:
        wait_for_http(port)
        url = (
            f"http://127.0.0.1:{port}/"
            "docs/product/experiments/3d-vector-aesthetic-stage/index.html?record=1"
        )
        capture_frames(work_dir, url, width, height, fps, frame_count)
    finally:
        server.terminate()
        try:
            server.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server.kill()

    frames_pattern = work_dir / "frames/frame_%05d.jpg"
    font_path = burn_subtitles_on_frames(work_dir / "frames", fps, final_duration, width, height)
    filter_graph = (
        f"[0:v]scale={width}:{height}:flags=lanczos,format=yuv420p[v];"
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
            "-framerate",
            str(fps),
            "-i",
            str(frames_pattern),
            "-i",
            str(voice_aiff),
            "-i",
            str(music_wav),
            "-filter_complex",
            filter_graph,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-r",
            str(fps),
            "-t",
            f"{final_duration:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output),
        ],
        cwd=work_dir,
    )
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

    probe = json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate",
                "-of",
                "json",
                str(output),
            ]
        ).stdout
    )

    if not keep_frames:
        frames_dir = work_dir / "frames"
        if frames_dir.exists():
            shutil.rmtree(frames_dir)

    manifest = {
        "output": str(output),
        "poster": str(poster),
        "duration_seconds": final_duration,
        "fps": fps,
        "width": width,
        "height": height,
        "frame_count": frame_count,
        "voice": voice,
        "voice_duration_seconds": round(voice_duration, 3),
        "subtitles": str(subtitles_ass),
        "subtitle_font": font_path,
        "music": str(music_wav),
        "probe": probe,
    }
    (output.parent / "vector-stage-xhs-20260630.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the VULCA vector stage Xiaohongshu MP4.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--duration", type=float, default=24.0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=540)
    parser.add_argument("--height", type=int, default=960)
    parser.add_argument("--voice", default="Tingting")
    parser.add_argument("--voice-rate", type=int, default=180)
    parser.add_argument("--keep-frames", action="store_true")
    args = parser.parse_args(argv)

    manifest = build_video(
        output=args.output,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
        voice=args.voice,
        voice_rate=args.voice_rate,
        keep_frames=args.keep_frames,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
