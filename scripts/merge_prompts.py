#!/usr/bin/env python3
"""Compare 3-way prompts (ollama, gpt, manual) and produce merged evfsam_prompts.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO / "assets" / "showcase" / "experiments" / "prompts"
OUT = REPO / "assets" / "showcase" / "experiments" / "evfsam_prompts.json"


def load_source(source: str, slug: str) -> list[list[str]] | None:
    path = PROMPTS_DIR / source / f"{slug}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data.get("layers", data) if isinstance(data, dict) else data


def compare(slug: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {slug}")
    print(f"{'='*60}")
    for src in ["manual", "ollama", "gpt"]:
        layers = load_source(src, slug)
        if layers is None:
            print(f"  {src:8s}: NOT FOUND")
            continue
        print(f"  {src:8s}: {len(layers)} layers")
        for layer in layers:
            name = layer[0]
            desc = layer[1][:60] + "..." if len(layer[1]) > 60 else layer[1]
            sp = layer[2] if len(layer) >= 3 else name
            print(f"    {name:30s} | {sp:30s} | {desc}")


def merge(slug: str, source: str) -> list[list[str]]:
    """Use a specific source as the winner for a slug."""
    layers = load_source(source, slug)
    if layers is None:
        raise FileNotFoundError(f"No {source} prompts for {slug}")
    return layers


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  merge_prompts.py compare <slug> [slug...]  — side-by-side comparison")
        print("  merge_prompts.py pick <slug> <source>       — pick winner, update evfsam_prompts.json")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "compare":
        for slug in sys.argv[2:]:
            compare(slug)
    elif cmd == "pick":
        slug, source = sys.argv[2], sys.argv[3]
        existing = json.loads(OUT.read_text()) if OUT.exists() else {}
        existing[slug] = merge(slug, source)
        OUT.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
        print(f"OK  {slug} <- {source} ({len(existing[slug])} layers)")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
