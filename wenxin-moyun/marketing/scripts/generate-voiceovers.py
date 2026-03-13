#!/usr/bin/env python3
"""
Generate voiceover MP3 + SRT for all 7 VULCA demo videos using Edge TTS.

Usage:
    cd wenxin-moyun/marketing/scripts
    python3 generate-voiceovers.py

Requirements:
    pip install edge-tts
"""

import edge_tts
import asyncio
import re
from pathlib import Path

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "+0%"  # Normal speed, warm pace
VOLUME = "+0%"

SCRIPT_DIR = Path(__file__).parent
NARRATION_DIR = SCRIPT_DIR.parent / "narration"
OUTPUT_DIR = SCRIPT_DIR.parent / "exports" / "audio"

VIDEOS = [
    "v1-home",
    "v2-editor",
    "v3-creation",
    "v4-hitl",
    "v5-build",
    "v6-gallery",
    "v7-admin",
]


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, timestamps, and metadata lines."""
    lines = text.strip().split("\n")
    clean_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines, headers, horizontal rules, metadata
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("---"):
            continue
        if stripped.startswith("**") and stripped.endswith("**"):
            continue
        if stripped.startswith("**Duration"):
            continue
        if stripped.startswith("**Word count"):
            continue
        if stripped.startswith("**Tone"):
            continue
        if stripped.startswith("**Voice"):
            continue
        # Remove timestamp markers like [0:00], [0:15], etc.
        cleaned = re.sub(r"\[\d+:\d+\]\s*", "", stripped)
        if cleaned:
            clean_lines.append(cleaned)
    return " ".join(clean_lines)


async def generate_voiceover(video_name: str) -> None:
    """Generate MP3 and SRT for a single video."""
    narration_file = NARRATION_DIR / f"{video_name}-narration.md"
    if not narration_file.exists():
        print(f"  Warning: Narration not found: {narration_file}")
        return

    text = narration_file.read_text(encoding="utf-8")
    clean_text = strip_markdown(text)

    if not clean_text.strip():
        print(f"  Warning: No narration text extracted from {video_name}")
        return

    mp3_path = OUTPUT_DIR / f"{video_name}-voiceover.mp3"
    srt_path = OUTPUT_DIR / f"{video_name}-voiceover.srt"

    # Single stream: collect audio + subtitles simultaneously
    # boundary="WordBoundary" required in edge-tts 7.x (default is SentenceBoundary)
    communicate = edge_tts.Communicate(
        clean_text, VOICE, rate=RATE, volume=VOLUME, boundary="WordBoundary"
    )
    submaker = edge_tts.SubMaker()

    with open(mp3_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    # Write SRT only if we collected subtitle cues
    if submaker.cues:
        srt_content = submaker.get_srt()
        srt_path.write_text(srt_content, encoding="utf-8")
        print(f"  Done: {mp3_path.name} + {srt_path.name} ({len(submaker.cues)} cues)")
    else:
        print(f"  Done: {mp3_path.name} (no subtitle cues)")


async def main() -> None:
    """Generate voiceovers for all 7 videos."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("VULCA Demo Video -- Voiceover Generation")
    print(f"Voice: {VOICE}")
    print(f"Output: {OUTPUT_DIR}\n")

    for video in VIDEOS:
        print(f"Generating {video}...")
        try:
            await generate_voiceover(video)
        except Exception as e:
            print(f"  Error: {e}")

    print("\nDone! Audio files saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    asyncio.run(main())
