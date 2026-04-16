#!/usr/bin/env python3
"""Generate EVF-SAM layer prompts via Ollama VLM (gemma4).

Sends each image to Ollama with a structured prompt asking for semantic
layer decomposition. Outputs per-slug JSON matching the manual prompt format.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parent.parent
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
OUT_DIR = REPO / "assets" / "showcase" / "experiments" / "prompts" / "ollama"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4"

SYSTEM_PROMPT = """You are an image segmentation planner. Given an artwork or photograph,
decompose it into 10-20 semantic layers for text-prompted segmentation (EVF-SAM).

Rules:
- Each layer has: name (snake_case), description (one sentence describing EXACTLY what pixels to segment), semantic_path (dot-notation hierarchy)
- The first layer MUST be "background" — it catches all unclaimed pixels
- For portraits: decompose face into eyes, nose, lips, hair, skin
- For groups: use person[0], person[1] etc. in semantic_path
- Descriptions must be unambiguous visual descriptions of pixel regions, NOT artistic interpretations
- Higher-z layers (foreground) take priority over lower-z (background) when overlapping

Output valid JSON array of [name, description, semantic_path] triples. No commentary."""

USER_PROMPT = """Analyze this image and output a JSON array of semantic layer definitions.
Each element: ["layer_name", "pixel-level description of what to segment", "semantic.path"]
Return ONLY the JSON array, no markdown fences or commentary."""


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def generate_prompts(slug: str, image_path: Path) -> list[list[str]]:
    b64 = encode_image(image_path)
    payload = {
        "model": MODEL,
        "prompt": USER_PROMPT,
        "system": SYSTEM_PROMPT,
        "images": [b64],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048},
    }
    resp = httpx.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    text = resp.json()["response"]

    # Extract JSON from response (handle markdown fences if present)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slugs = sys.argv[1:] if len(sys.argv) > 1 else None

    for img_path in sorted(ORIG_DIR.glob("*.jpg")):
        slug = img_path.stem
        if slug.endswith("-1024"):
            continue
        if slugs and slug not in slugs:
            continue
        out = OUT_DIR / f"{slug}.json"
        if out.exists():
            print(f"SKIP {slug}: {out} exists")
            continue
        print(f"GEN  {slug} via {MODEL} ...")
        try:
            layers = generate_prompts(slug, img_path)
            result = {"slug": slug, "layers": layers}
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"  OK {len(layers)} layers -> {out}")
        except Exception as e:
            print(f"  FAIL {slug}: {e}")


if __name__ == "__main__":
    main()
