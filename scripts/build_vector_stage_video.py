from __future__ import annotations

import argparse
import asyncio
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
DEFAULT_OUTPUT = REPO_ROOT / "output/video/3d-vector-aesthetic-stage/vector-stage-xhs-horizontal-20260630.mp4"
PLAYWRIGHT_MODULE = Path(
    "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright"
)
CHROME_EXECUTABLE = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

VOICE_FALLBACKS = [
    "zh-CN-XiaoxiaoNeural",
    "Shelley (中文（中国大陆）)",
    "Tingting",
]

VOICEOVER_SEGMENTS = [
    {
        "text": "这一版展示的是三维矢量技术美学效果。",
        "subtitle": "这一版展示的是三维矢量技术美学效果。",
    },
    {
        "text": "画面里有三维文字、粒子云、发光轨迹，还有鼠标触发的空间变化。",
        "subtitle": "画面里有三维文字、粒子云、发光轨迹，还有鼠标触发的空间变化。",
    },
    {
        "text": "接下来会继续收集新的参考案例，把更多网页三维、字体动画、着色器和界面效果拆进数据库。",
        "subtitle": "接下来会继续收集新的参考案例，把更多网页三维、字体动画、着色器和界面效果拆进数据库。",
    },
    {
        "text": "未来会用这些模块生成一系列互动作品，也会整理成教程，持续迭代这个风格。",
        "subtitle": "未来会用这些模块生成一系列互动作品，也会整理成教程，持续迭代这个风格。",
    },
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


def write_ass_subtitles(
    path: Path,
    cues: list[tuple[float, float, str]],
    width: int,
    height: int,
    duration: float,
) -> None:
    ass = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
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
        if start >= duration:
            continue
        ass.append(
            f"Dialogue: 0,{seconds_to_ass(start)},{seconds_to_ass(min(end, duration - 0.25))},"
            f"Default,,0,0,0,,{text}"
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


def burn_subtitles_on_frames(
    frames_dir: Path,
    cues: list[tuple[float, float, str]],
    fps: int,
    duration: float,
    width: int,
    height: int,
) -> str:
    font_size = max(30, min(54, round(min(width, height) * 0.047)))
    font, font_path = load_subtitle_font(font_size)
    shadow_font, _ = load_subtitle_font(font_size)
    margin_x = max(34, round(width * 0.09))
    base_y = height - max(88, round(height * 0.14))

    frame_paths = sorted(frames_dir.glob("frame_*.png")) or sorted(frames_dir.glob("frame_*.jpg"))
    for frame_path in frame_paths:
        frame_number = int(frame_path.stem.split("_")[-1])
        timestamp = frame_number / fps
        cue_text = ""
        for start, end, text in cues:
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
        box_h = text_h + round(font_size * 0.8)
        box_x0 = (width - box_w) / 2
        box_y0 = base_y - box_h / 2
        box_x1 = box_x0 + box_w
        box_y1 = box_y0 + box_h
        draw.rounded_rectangle(
            (box_x0, box_y0, box_x1, box_y1),
            radius=max(14, round(font_size * 0.42)),
            fill=(5, 6, 8, 158),
            outline=(245, 240, 223, 42),
            width=1,
        )
        y = box_y0 + round(font_size * 0.38)
        for index, line in enumerate(lines):
            line_w = line_widths[index]
            x = (width - line_w) / 2
            draw.text((x + 1, y + 1), line, font=shadow_font, fill=(0, 0, 0, 170))
            draw.text((x, y), line, font=font, fill=(245, 240, 223, 242))
            y += line_heights[index] + 10
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        if frame_path.suffix.lower() == ".png":
            image.save(frame_path, compress_level=3)
        else:
            image.save(frame_path, quality=96, subsampling=0)

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


def unique_voice_candidates(preferred: str) -> list[str]:
    candidates = [preferred, *VOICE_FALLBACKS]
    result = []
    for candidate in candidates:
        if candidate and candidate not in result:
            result.append(candidate)
    return result


def is_edge_voice(voice: str) -> bool:
    return voice.startswith("zh-CN-")


async def synthesize_edge_text(text: str, voice: str, output_path: Path) -> None:
    try:
        import edge_tts
    except ModuleNotFoundError as exc:
        raise RuntimeError("edge-tts is not installed") from exc

    communicate = edge_tts.Communicate(text, voice, rate="-6%", pitch="-2Hz")
    await communicate.save(str(output_path))


def synthesize_voiceover_with_voice(
    *,
    work_dir: Path,
    voice: str,
    voice_rate: int,
    initial_silence: float = 0.38,
    segment_gap: float = 0.24,
) -> dict[str, object]:
    segment_dir = work_dir / "voice_segments"
    segment_dir.mkdir(parents=True, exist_ok=True)
    segment_paths = []
    segment_durations = []

    script_path = work_dir / "voiceover.txt"
    script_path.write_text(
        "\n".join(segment["text"] for segment in VOICEOVER_SEGMENTS) + "\n",
        encoding="utf-8",
    )

    for index, segment in enumerate(VOICEOVER_SEGMENTS):
        segment_path = segment_dir / f"voiceover_{index:02d}.{'mp3' if is_edge_voice(voice) else 'aiff'}"
        if is_edge_voice(voice):
            asyncio.run(synthesize_edge_text(segment["text"], voice, segment_path))
        else:
            run(["say", "-v", voice, "-r", str(voice_rate), "-o", str(segment_path), segment["text"]])
        segment_paths.append(segment_path)
        segment_durations.append(ffprobe_duration(segment_path))

    voiceover_path = work_dir / "voiceover.wav"
    cmd = ["ffmpeg", "-y", "-hide_banner"]
    for segment_path in segment_paths:
        cmd.extend(["-i", str(segment_path)])

    filter_parts = [f"anullsrc=r=44100:cl=mono:d={initial_silence:.3f}[lead]"]
    concat_inputs = ["[lead]"]
    cue_cursor = initial_silence
    cues = []
    for index, (segment, segment_duration) in enumerate(zip(VOICEOVER_SEGMENTS, segment_durations)):
        filter_parts.append(
            f"[{index}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=mono[s{index}]"
        )
        concat_inputs.append(f"[s{index}]")
        cues.append((cue_cursor, cue_cursor + segment_duration, segment["subtitle"]))
        cue_cursor += segment_duration
        if index < len(segment_paths) - 1:
            filter_parts.append(f"anullsrc=r=44100:cl=mono:d={segment_gap:.3f}[g{index}]")
            concat_inputs.append(f"[g{index}]")
            cue_cursor += segment_gap

    concat_count = 1 + len(segment_paths) + max(0, len(segment_paths) - 1)
    filter_parts.append(f"{''.join(concat_inputs)}concat=n={concat_count}:v=0:a=1[a]")
    cmd.extend(["-filter_complex", ";".join(filter_parts), "-map", "[a]", str(voiceover_path)])
    run(cmd)
    return {
        "path": voiceover_path,
        "voice": voice,
        "duration": ffprobe_duration(voiceover_path),
        "segment_durations": segment_durations,
        "cues": cues,
        "script": str(script_path),
    }


def synthesize_voiceover(work_dir: Path, preferred_voice: str, voice_rate: int) -> dict[str, object]:
    errors = []
    for voice in unique_voice_candidates(preferred_voice):
        try:
            return synthesize_voiceover_with_voice(
                work_dir=work_dir,
                voice=voice,
                voice_rate=voice_rate,
            )
        except subprocess.CalledProcessError as error:
            errors.append(f"{voice}: {error.stderr.strip() or error.stdout.strip()}")
    raise SystemExit("could not synthesize voiceover with any configured voice: " + " | ".join(errors))


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


def capture_frames(
    work_dir: Path,
    url: str,
    width: int,
    height: int,
    fps: int,
    frame_count: int,
    render_scale: float,
) -> None:
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
                deviceScaleFactor: {render_scale:.3f}
              }});
              await page.goto({json.dumps(url)}, {{ waitUntil: 'domcontentloaded' }});
              await page.waitForFunction(() => typeof window.__VULCA_RENDER_FRAME__ === 'function');
              let mouseDown = false;
              for (let frame = 0; frame < {frame_count}; frame += 1) {{
                const state = await page.evaluate(
                  (payload) => window.__VULCA_RENDER_FRAME__(payload.frame, payload.fps),
                  {{ frame, fps: {fps} }}
                );
                if (state.cursor) {{
                  await page.mouse.move(state.cursor.x, state.cursor.y);
                  if (state.cursor.down && !mouseDown) {{
                    await page.mouse.down();
                    mouseDown = true;
                  }} else if (!state.cursor.down && mouseDown) {{
                    await page.mouse.up();
                    mouseDown = false;
                  }}
                }}
                const name = `frame_${{String(frame).padStart(5, '0')}}.png`;
                await page.screenshot({{
                  path: {json.dumps(str(frames_dir))} + '/' + name,
                  type: 'png',
                  animations: 'disabled',
                  fullPage: false
                }});
                if (frame % {fps * 2} === 0) {{
                  console.log(`captured ${{frame}}/{frame_count}`);
                }}
              }}
              if (mouseDown) await page.mouse.up();
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
    render_scale: float,
    video_bitrate: str,
    video_maxrate: str,
    video_bufsize: str,
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

    music_wav = work_dir / "music.wav"
    subtitles_ass = work_dir / "subtitles.ass"
    poster = output.with_suffix(".poster.jpg")

    voiceover = synthesize_voiceover(work_dir, voice, voice_rate)
    voice_path = Path(str(voiceover["path"]))
    voice_duration = float(voiceover["duration"])
    subtitle_cues = list(voiceover["cues"])
    final_duration = max(duration, math.ceil((voice_duration + 1.2) * 10) / 10)
    frame_count = int(math.ceil(final_duration * fps))
    capture_width = int(round(width * render_scale))
    capture_height = int(round(height * render_scale))

    write_music(music_wav, final_duration)
    write_ass_subtitles(subtitles_ass, subtitle_cues, width, height, final_duration)

    port = find_free_port()
    server = start_http_server(port)
    try:
        wait_for_http(port)
        url = (
            f"http://127.0.0.1:{port}/"
            "docs/product/experiments/3d-vector-aesthetic-stage/index.html?record=1"
        )
        capture_frames(work_dir, url, width, height, fps, frame_count, render_scale)
    finally:
        server.terminate()
        try:
            server.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server.kill()

    frames_pattern = work_dir / "frames/frame_%05d.png"
    font_path = burn_subtitles_on_frames(
        work_dir / "frames",
        subtitle_cues,
        fps,
        final_duration,
        capture_width,
        capture_height,
    )
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
            str(fps),
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
        "render_scale": render_scale,
        "source_frame_width": capture_width,
        "source_frame_height": capture_height,
        "video_bitrate": video_bitrate,
        "video_maxrate": video_maxrate,
        "video_bufsize": video_bufsize,
        "frame_count": frame_count,
        "voice": voiceover["voice"],
        "voice_duration_seconds": round(voice_duration, 3),
        "voice_segment_durations_seconds": [round(value, 3) for value in voiceover["segment_durations"]],
        "subtitle_cues": [
            {"start": round(start, 3), "end": round(end, 3), "text": text}
            for start, end, text in subtitle_cues
        ],
        "voice_script": voiceover["script"],
        "subtitles": str(subtitles_ass),
        "subtitle_font": font_path,
        "music": str(music_wav),
        "probe": probe,
    }
    output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the VULCA vector stage Xiaohongshu MP4.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--duration", type=float, default=24.0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--render-scale", type=float, default=2.0)
    parser.add_argument("--video-bitrate", default="24M")
    parser.add_argument("--video-maxrate", default="30M")
    parser.add_argument("--video-bufsize", default="48M")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--voice-rate", type=int, default=170)
    parser.add_argument("--keep-frames", action="store_true")
    args = parser.parse_args(argv)

    manifest = build_video(
        output=args.output,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
        render_scale=max(1.0, args.render_scale),
        video_bitrate=args.video_bitrate,
        video_maxrate=args.video_maxrate,
        video_bufsize=args.video_bufsize,
        voice=args.voice,
        voice_rate=args.voice_rate,
        keep_frames=args.keep_frames,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
