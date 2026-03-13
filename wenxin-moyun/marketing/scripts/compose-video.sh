#!/bin/bash
set -euo pipefail

# Compose a single VULCA demo video: WebM + Voiceover + Background Music → MP4
#
# Usage: bash marketing/scripts/compose-video.sh v1-home
#
# Inputs:
#   exports/v1-home/    — Directory with raw WebM recording(s)
#   exports/audio/v1-home-voiceover.mp3 — Edge TTS voiceover
#   exports/audio/v1-home-voiceover.srt — SRT subtitles (optional)
#   exports/music/ambient-bg.mp3        — Background music
#
# Output:
#   exports/final/v1-home.mp4 — Composed 1920x1080 30fps MP4

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORTS_DIR="${SCRIPT_DIR}/../exports"

NAME="${1:?Usage: compose-video.sh <video-name> (e.g., v1-home)}"

# Input paths
VIDEO_DIR="${EXPORTS_DIR}/${NAME}"
VOICEOVER="${EXPORTS_DIR}/audio/${NAME}-voiceover.mp3"
SRT_FILE="${EXPORTS_DIR}/audio/${NAME}-voiceover.srt"
BG_MUSIC="${EXPORTS_DIR}/music/ambient-bg.mp3"

# Output
FINAL_DIR="${EXPORTS_DIR}/final"
OUTPUT="${FINAL_DIR}/${NAME}.mp4"
mkdir -p "$FINAL_DIR"

echo "=== Composing ${NAME} ==="

# Find the source video (WebM)
# Check: exports/{name}.webm, exports/videos/{name}.webm, exports/{name}/*.webm
if [ -f "${EXPORTS_DIR}/${NAME}.webm" ]; then
    SOURCE_VIDEO="${EXPORTS_DIR}/${NAME}.webm"
elif [ -f "${EXPORTS_DIR}/videos/${NAME}.webm" ]; then
    SOURCE_VIDEO="${EXPORTS_DIR}/videos/${NAME}.webm"
elif [ -d "$VIDEO_DIR" ]; then
    SOURCE_VIDEO=$(find "$VIDEO_DIR" -name "*.webm" -type f | sort | tail -1)
    if [ -z "$SOURCE_VIDEO" ]; then
        echo "✗ No WebM video found in ${VIDEO_DIR}"
        exit 1
    fi
else
    echo "✗ No video source found for ${NAME}"
    echo "  Expected: ${EXPORTS_DIR}/${NAME}.webm or ${VIDEO_DIR}/*.webm"
    exit 1
fi
echo "  Video: ${SOURCE_VIDEO}"

# Check voiceover
if [ ! -f "$VOICEOVER" ]; then
    echo "  ⚠ Voiceover not found: ${VOICEOVER}"
    echo "  Composing video without voiceover."
    HAS_VOICEOVER=false
else
    echo "  Voiceover: ${VOICEOVER}"
    HAS_VOICEOVER=true
fi

# Check background music
if [ ! -f "$BG_MUSIC" ]; then
    echo "  ⚠ Background music not found: ${BG_MUSIC}"
    HAS_MUSIC=false
else
    echo "  Music: ${BG_MUSIC}"
    HAS_MUSIC=true
fi

# Check SRT subtitles (must exist AND be non-empty)
HAS_SUBS=false
if [ -f "$SRT_FILE" ] && [ -s "$SRT_FILE" ]; then
    echo "  Subtitles: ${SRT_FILE}"
    HAS_SUBS=true
fi

echo "  Output: ${OUTPUT}"
echo ""

# Build FFmpeg command
FFMPEG_INPUTS=(-i "$SOURCE_VIDEO")
FILTER_COMPLEX=""
AUDIO_FILTER=""

if $HAS_VOICEOVER && $HAS_MUSIC; then
    # Mix voiceover (100%) + background music (15%)
    FFMPEG_INPUTS+=(-i "$VOICEOVER" -i "$BG_MUSIC")
    AUDIO_FILTER="[1:a]volume=1.0[voice];[2:a]volume=0.15,atrim=0:120[music];[voice][music]amix=inputs=2:duration=shortest[aout]"
elif $HAS_VOICEOVER; then
    FFMPEG_INPUTS+=(-i "$VOICEOVER")
    AUDIO_FILTER="[1:a]volume=1.0[aout]"
elif $HAS_MUSIC; then
    FFMPEG_INPUTS+=(-i "$BG_MUSIC")
    AUDIO_FILTER="[1:a]volume=0.3[aout]"
fi

# Get video duration for fade-out calculation
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SOURCE_VIDEO" 2>/dev/null || echo "60")
DURATION_INT=$(echo "$DURATION" | cut -d. -f1)
FADE_OUT_START=$((DURATION_INT > 1 ? DURATION_INT - 1 : 0))

VIDEO_FILTER="[0:v]scale=1920:1080:flags=lanczos,fps=30,fade=t=in:st=0:d=0.5,fade=t=out:st=${FADE_OUT_START}:d=1[vout]"

# Compose the FFmpeg command
if [ -n "$AUDIO_FILTER" ]; then
    ffmpeg -y \
        "${FFMPEG_INPUTS[@]}" \
        -filter_complex "${VIDEO_FILTER};${AUDIO_FILTER}" \
        -map "[vout]" -map "[aout]" \
        -c:v libx264 -crf 18 -preset slow \
        -c:a aac -b:a 192k \
        -shortest \
        -movflags +faststart \
        "$OUTPUT"
else
    # Video only, no audio
    ffmpeg -y \
        "${FFMPEG_INPUTS[@]}" \
        -filter_complex "${VIDEO_FILTER}" \
        -map "[vout]" \
        -c:v libx264 -crf 18 -preset slow \
        -an \
        -movflags +faststart \
        "$OUTPUT"
fi

# Burn subtitles if available (second pass for simplicity)
if $HAS_SUBS; then
    SUBBED_OUTPUT="${FINAL_DIR}/${NAME}-subbed.mp4"
    echo "  Burning subtitles..."
    ffmpeg -y -i "$OUTPUT" -vf "subtitles=${SRT_FILE}:force_style='FontSize=16,FontName=Arial,PrimaryColour=&HFFFFFF,OutlineColour=&H40000000,Outline=0,BorderStyle=4,BackColour=&H80000000,MarginV=50,Alignment=2'" \
        -c:v libx264 -crf 18 -preset slow \
        -c:a copy \
        -movflags +faststart \
        "$SUBBED_OUTPUT"
    mv "$SUBBED_OUTPUT" "$OUTPUT"
fi

# Print result
SIZE=$(du -h "$OUTPUT" | cut -f1)
echo ""
echo "✓ ${NAME}.mp4 composed (${SIZE})"
echo "  Resolution: 1920x1080 @ 30fps"
echo "  Path: ${OUTPUT}"
