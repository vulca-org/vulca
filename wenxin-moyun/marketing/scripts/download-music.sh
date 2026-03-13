#!/bin/bash
set -euo pipefail

# Download ambient background music for VULCA demo videos
# Pixabay Music is free for commercial use without attribution
#
# Usage: bash marketing/scripts/download-music.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MUSIC_DIR="${SCRIPT_DIR}/../exports/music"
mkdir -p "$MUSIC_DIR"

BG_MUSIC="${MUSIC_DIR}/ambient-bg.mp3"

if [ -f "$BG_MUSIC" ]; then
    echo "Background music already exists: $BG_MUSIC"
    echo "Delete it manually to re-download."
    exit 0
fi

echo "=== VULCA Demo — Background Music Download ==="
echo ""
echo "Pixabay provides free music for commercial use."
echo "Please download an ambient/inspiring track manually:"
echo ""
echo "  1. Visit: https://pixabay.com/music/search/ambient%20inspiring/"
echo "  2. Choose a soft, ambient track (60-120 seconds)"
echo "  3. Download as MP3"
echo "  4. Save to: $BG_MUSIC"
echo ""
echo "Recommended search terms: 'ambient corporate', 'inspiring technology', 'soft piano'"
echo ""

# Generate a silent placeholder so compose-video.sh doesn't fail
echo "Generating silent placeholder (replace with real music later)..."
ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 120 -q:a 2 "$BG_MUSIC" -y 2>/dev/null
echo "Silent placeholder created: $BG_MUSIC"
echo "  Replace with a real track from Pixabay for best results."
