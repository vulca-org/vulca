#!/bin/bash
set -euo pipefail

# VULCA Demo Video Production Pipeline
# =====================================
# Records all 7 demo videos, generates voiceovers, and composes final MP4s.
#
# Usage:
#   bash marketing/scripts/record-all.sh          # Full pipeline
#   bash marketing/scripts/record-all.sh record    # Record only
#   bash marketing/scripts/record-all.sh voice     # Voiceovers only
#   bash marketing/scripts/record-all.sh compose   # Compose only
#
# Pre-requisites:
#   - Frontend running on :5173
#   - Backend running on :8001
#   - ffmpeg installed
#   - edge-tts pip package installed
#   - Playwright browsers installed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}/../.."
MARKETING_DIR="${SCRIPT_DIR}/.."

# Default: run all steps
STEP="${1:-all}"

# ─────────────────────────────────────
# Pre-flight checks
# ─────────────────────────────────────
check_prerequisites() {
    echo "=== Pre-flight Checks ==="
    local FAILED=false

    # Check frontend
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200"; then
        echo "  ✓ Frontend running on :5173"
    else
        echo "  ✗ Frontend not running on :5173"
        echo "    Run: cd wenxin-moyun && npm run dev"
        FAILED=true
    fi

    # Check backend
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null | grep -q "200"; then
        echo "  ✓ Backend running on :8001"
    else
        echo "  ⚠ Backend not running on :8001 (some videos need it)"
    fi

    # Check ffmpeg
    if command -v ffmpeg &>/dev/null; then
        echo "  ✓ ffmpeg: $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
    else
        echo "  ✗ ffmpeg not installed"
        FAILED=true
    fi

    # Check edge-tts
    if python3 -c "import edge_tts" 2>/dev/null; then
        echo "  ✓ edge-tts installed"
    else
        echo "  ✗ edge-tts not installed"
        echo "    Run: pip install edge-tts"
        FAILED=true
    fi

    # Check Playwright
    if npx playwright --version &>/dev/null; then
        echo "  ✓ Playwright: $(npx playwright --version 2>&1)"
    else
        echo "  ✗ Playwright not installed"
        FAILED=true
    fi

    echo ""

    if $FAILED; then
        echo "Pre-flight checks failed. Fix the issues above and try again."
        exit 1
    fi
}

# ─────────────────────────────────────
# Step 1: Record all 7 videos
# ─────────────────────────────────────
record_videos() {
    echo "=== Step 1: Recording 7 Demo Videos ==="
    echo ""

    VIDEOS=("v1-home" "v2-editor" "v3-creation" "v4-hitl" "v5-build" "v6-gallery" "v7-admin")

    cd "${PROJECT_DIR}/wenxin-moyun"

    for NAME in "${VIDEOS[@]}"; do
        echo "Recording ${NAME}..."
        if npx ts-node "marketing/demo-scripts/${NAME}.ts"; then
            echo "  ✓ ${NAME} recorded"
        else
            echo "  ✗ ${NAME} failed (continuing...)"
        fi
        echo ""
    done

    cd "$SCRIPT_DIR"
}

# ─────────────────────────────────────
# Step 2: Generate voiceovers
# ─────────────────────────────────────
generate_voiceovers() {
    echo "=== Step 2: Generating Voiceovers ==="
    echo ""

    cd "$SCRIPT_DIR"
    python3 generate-voiceovers.py
    echo ""
}

# ─────────────────────────────────────
# Step 3: Download background music
# ─────────────────────────────────────
download_music() {
    echo "=== Step 3: Background Music ==="
    echo ""

    cd "$SCRIPT_DIR"
    bash download-music.sh
    echo ""
}

# ─────────────────────────────────────
# Step 4: Compose final videos
# ─────────────────────────────────────
compose_videos() {
    echo "=== Step 4: Composing Final Videos ==="
    echo ""

    cd "$SCRIPT_DIR"
    bash compose-all.sh
    echo ""
}

# ─────────────────────────────────────
# Summary
# ─────────────────────────────────────
print_summary() {
    FINAL_DIR="${MARKETING_DIR}/exports/final"

    echo "══════════════════════════════════════"
    echo "  VULCA Demo Video Production — Done"
    echo "══════════════════════════════════════"
    echo ""

    if [ -d "$FINAL_DIR" ] && ls "$FINAL_DIR"/*.mp4 &>/dev/null; then
        echo "Final videos:"
        ls -lh "$FINAL_DIR"/*.mp4
        echo ""
        echo "Windows path:"
        echo "  \\\\wsl.localhost\\Ubuntu${FINAL_DIR}"
    else
        echo "No final MP4 files found yet."
        echo "Run individual steps or the full pipeline."
    fi

    echo ""
    echo "Individual steps:"
    echo "  bash record-all.sh record   — Record videos"
    echo "  bash record-all.sh voice    — Generate voiceovers"
    echo "  bash record-all.sh compose  — Compose final MP4s"
}

# ─────────────────────────────────────
# Main
# ─────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║  VULCA Demo Video Production        ║"
echo "║  7 Videos × (Record + Voice + Mix)  ║"
echo "╚══════════════════════════════════════╝"
echo ""

case "$STEP" in
    all)
        check_prerequisites
        record_videos
        generate_voiceovers
        download_music
        compose_videos
        print_summary
        ;;
    record)
        check_prerequisites
        record_videos
        ;;
    voice)
        generate_voiceovers
        ;;
    compose)
        download_music
        compose_videos
        print_summary
        ;;
    *)
        echo "Usage: record-all.sh [all|record|voice|compose]"
        exit 1
        ;;
esac
