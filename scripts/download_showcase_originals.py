#!/usr/bin/env python3
"""Download showcase original images from Wikimedia Commons.

Downloads full-resolution originals and resizes to max 1280px on the
long side so they stay manageable for the showcase pipeline.
"""

from __future__ import annotations

import io
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

URLS = {
    # Commons full-res originals (no thumbnail step issues)
    "mona-lisa": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    "nighthawks": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg",
    "the-scream": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    "creation-of-adam": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg",
    "birth-of-venus": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
    "the-kiss": "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    "american-gothic": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg",
    # Wikipedia EN (non-free, no thumbnails)
    "persistence-of-memory": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
    "afghan-girl": "https://upload.wikimedia.org/wikipedia/en/b/b4/Sharbat_Gula.jpg",
    "tank-man": "https://upload.wikimedia.org/wikipedia/en/d/d8/Tianasquare.jpg",
    "lunch-atop-skyscraper": "https://upload.wikimedia.org/wikipedia/en/6/69/Lunch_atop_a_Skyscraper_-_Charles_Clyde_Ebbets.jpg",
    "raising-flag-iwo-jima": "https://upload.wikimedia.org/wikipedia/en/a/a1/WW2_Iwo_Jima_flag_raising.jpg",
}

MAX_LONG_SIDE = 1280
DEST = Path(__file__).resolve().parent.parent / "assets" / "showcase" / "originals"


def _resize_if_needed(data: bytes) -> bytes:
    """Resize to MAX_LONG_SIDE if larger, return JPEG bytes."""
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_LONG_SIDE:
        ratio = MAX_LONG_SIDE / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def download(slugs: list[str] | None = None) -> None:
    """Download originals for the given slugs (default: all)."""
    targets = slugs or list(URLS)
    DEST.mkdir(parents=True, exist_ok=True)

    for slug in targets:
        if slug not in URLS:
            print(f"SKIP unknown slug: {slug}")
            continue
        dest_path = DEST / f"{slug}.jpg"
        if dest_path.exists():
            print(f"EXISTS {dest_path}")
            continue
        url = URLS[slug]
        print(f"GET   {slug} ...")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Vulca/0.16 showcase-downloader",
        })
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
        resized = _resize_if_needed(raw)
        dest_path.write_bytes(resized)
        print(f"  -> {dest_path}  ({dest_path.stat().st_size // 1024} K)")
        time.sleep(1)  # be polite to Wikimedia


if __name__ == "__main__":
    download(sys.argv[1:] or None)
