#!/bin/bash
set -euo pipefail

# Compose all 7 VULCA demo videos
#
# Usage: bash marketing/scripts/compose-all.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VIDEOS=("v1-home" "v2-editor" "v3-creation" "v4-hitl" "v5-build" "v6-gallery" "v7-admin")

echo "=== VULCA Demo Video Composition ==="
echo "Composing ${#VIDEOS[@]} videos..."
echo ""

FAILED=()
SUCCEEDED=()

for NAME in "${VIDEOS[@]}"; do
    echo "────────────────────────────────────"
    if bash "${SCRIPT_DIR}/compose-video.sh" "$NAME"; then
        SUCCEEDED+=("$NAME")
    else
        echo "✗ Failed to compose ${NAME}"
        FAILED+=("$NAME")
    fi
    echo ""
done

echo "════════════════════════════════════"
echo "SUMMARY"
echo "────────────────────────────────────"
echo "Succeeded: ${#SUCCEEDED[@]}/${#VIDEOS[@]}"
for v in "${SUCCEEDED[@]}"; do
    echo "  ✓ ${v}"
done

if [ ${#FAILED[@]} -gt 0 ]; then
    echo ""
    echo "Failed: ${#FAILED[@]}"
    for v in "${FAILED[@]}"; do
        echo "  ✗ ${v}"
    done
fi

echo ""
echo "Output directory:"
ls -lh "${SCRIPT_DIR}/../exports/final/"*.mp4 2>/dev/null || echo "  (no MP4 files yet)"
