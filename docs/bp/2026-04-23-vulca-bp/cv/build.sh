#!/usr/bin/env bash
# Build Haorui Yu's CV — xelatex single pass (no TOC / refs)
set -euo pipefail

export PATH="/Library/TeX/texbin:$PATH"

cd "$(dirname "$0")"

echo "==> xelatex (single pass)"
xelatex -interaction=nonstopmode -halt-on-error cv.tex > .build.log 2>&1 || {
  echo "✗ xelatex failed — see .build.log"
  tail -60 .build.log
  exit 1
}

pages=$(mdls -name kMDItemNumberOfPages cv.pdf 2>/dev/null | awk -F'= ' '{print $2}')
size=$(du -h cv.pdf | cut -f1)

echo "✓ cv.pdf built — ${pages:-?} pages, ${size}"
