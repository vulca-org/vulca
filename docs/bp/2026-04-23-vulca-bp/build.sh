#!/usr/bin/env bash
# Build script for Vulca BP — runs xelatex twice for TOC/refs
set -euo pipefail

export PATH="/Library/TeX/texbin:$PATH"

cd "$(dirname "$0")"

echo "==> pass 1 (xelatex)"
xelatex -interaction=nonstopmode -halt-on-error main.tex > .build.log 2>&1 || {
  echo "✗ xelatex pass 1 failed — see .build.log"
  tail -60 .build.log
  exit 1
}

echo "==> pass 2 (xelatex, for TOC / hyperref)"
xelatex -interaction=nonstopmode -halt-on-error main.tex > .build.log 2>&1 || {
  echo "✗ xelatex pass 2 failed — see .build.log"
  tail -60 .build.log
  exit 1
}

pages=$(pdfinfo main.pdf 2>/dev/null | awk '/Pages:/ {print $2}' || echo "?")
size=$(du -h main.pdf | cut -f1)

echo "✓ main.pdf built — ${pages} pages, ${size}"
