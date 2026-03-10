#!/usr/bin/env bash
# Download public domain artworks for VULCA demo recordings
# All images are public domain — see sources.md for license details

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/images"

mkdir -p "${OUTPUT_DIR}"

echo "=== VULCA Demo Assets Downloader ==="
echo "Downloading 3 public domain artworks..."
echo ""

# 1. Dunhuang Flying Apsaras
echo "[1/3] Downloading: Dunhuang Flying Apsaras..."
if curl -fsSL -o "${OUTPUT_DIR}/01-dunhuang-flying-apsaras.jpg" \
  "https://upload.wikimedia.org/wikipedia/commons/f/fc/Dunhuang_Flying_Apsaras.jpg"; then
  echo "  OK: Dunhuang saved"
else
  echo "  FAIL: Dunhuang (try alt URL in sources.md)"
fi

# 2. The Great Wave off Kanagawa
echo "[2/3] Downloading: Hokusai - The Great Wave..."
if curl -fsSL -o "${OUTPUT_DIR}/02-hokusai-great-wave.jpg" \
  "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tsunami_by_hokusai_19th_century.jpg"; then
  echo "  OK: Great Wave saved"
else
  echo "  FAIL: Great Wave (try alt URL in sources.md)"
fi

# 3. Persian Mihrab (Islamic Geometric Art)
echo "[3/3] Downloading: Met Mihrab (Islamic Geometric Art)..."
if curl -fsSL -o "${OUTPUT_DIR}/03-met-mihrab-geometric.jpg" \
  "https://images.metmuseum.org/CRDImages/is/original/DP235183.jpg"; then
  echo "  OK: Mihrab saved"
else
  echo "  FAIL: Mihrab (try Wikimedia alt URL in sources.md)"
fi

echo ""
echo "=== Download Complete ==="
echo "Images saved to: ${OUTPUT_DIR}/"
ls -lh "${OUTPUT_DIR}/"
echo ""
echo "Next steps:"
echo "  1. Verify image quality and resolution"
echo "  2. Optionally crop to recommended ratios (see sources.md)"
echo "  3. Use in Compare mode demo recording (script 03)"
