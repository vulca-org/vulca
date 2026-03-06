"""VULCA CLI — command-line cultural art evaluation.

Usage:
    # Evaluate a local image
    python -m app.prototype.integrations.cli evaluate image.png --tradition chinese_xieyi

    # Auto-detect tradition
    python -m app.prototype.integrations.cli evaluate image.png

    # Identify tradition
    python -m app.prototype.integrations.cli identify image.png

    # List available traditions
    python -m app.prototype.integrations.cli traditions

    # Validate a tradition YAML
    python -m app.prototype.integrations.cli validate traditions/my_tradition.yaml

    # Output as JSON (for CI/CD integration)
    python -m app.prototype.integrations.cli evaluate image.png --json

Environment variables:
    VULCA_API_URL  — API base URL (default: http://localhost:8001)
    VULCA_API_KEY  — API bearer token
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path


VULCA_API_URL = os.environ.get("VULCA_API_URL", "http://localhost:8001")
VULCA_API_KEY = os.environ.get("VULCA_API_KEY", "")


def _read_image_b64(path: str) -> str:
    """Read image file and return base64 string."""
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    if not p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"):
        print(f"Warning: unusual image extension: {p.suffix}", file=sys.stderr)
    return base64.b64encode(p.read_bytes()).decode("utf-8")


def _api_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if VULCA_API_KEY:
        headers["Authorization"] = f"Bearer {VULCA_API_KEY}"
    return headers


def _api_post(endpoint: str, body: dict) -> dict:
    """POST to VULCA API and return JSON response."""
    import httpx

    url = f"{VULCA_API_URL}{endpoint}"
    try:
        with httpx.Client(timeout=90) as client:
            resp = client.post(url, json=body, headers=_api_headers())
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        print(f"API error {e.response.status_code}: {e.response.text[:300]}", file=sys.stderr)
        sys.exit(1)
    except httpx.ConnectError:
        print(f"Cannot connect to {url}. Is the VULCA API running?", file=sys.stderr)
        print(f"Set VULCA_API_URL env var or start the backend: uvicorn app.main:app --port 8001", file=sys.stderr)
        sys.exit(1)


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Evaluate an image for cultural quality."""
    image_b64 = _read_image_b64(args.image)

    body: dict = {"image_base64": image_b64}
    if args.tradition and args.tradition != "auto":
        body["tradition"] = args.tradition
    if args.subject:
        body["subject"] = args.subject
    if args.evidence:
        body["include_evidence"] = True

    result = _api_post("/api/v1/evaluate", body)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    scores = result.get("scores", {})
    total = result.get("weighted_total", 0)
    tradition = result.get("tradition_used", "unknown")
    diagnosis = result.get("cultural_diagnosis", "")
    latency = result.get("latency_ms", 0)

    print(f"\n  VULCA Cultural Evaluation")
    print(f"  Tradition: {tradition}  |  Score: {total:.3f}  |  Latency: {latency}ms\n")

    dim_names = {
        "L1": "Visual Perception   ",
        "L2": "Technical Analysis  ",
        "L3": "Cultural Context    ",
        "L4": "Critical Interpret. ",
        "L5": "Philosophical Aesth.",
    }
    for key, label in dim_names.items():
        score = scores.get(key, 0)
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"  {label}  {score:.3f}  {bar}")

    if diagnosis:
        print(f"\n  Diagnosis: {diagnosis[:200]}")

    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n  Recommendations:")
        for r in recommendations[:3]:
            print(f"    - {r}")

    risks = result.get("risk_flags", [])
    if risks:
        print(f"\n  Risk Flags:")
        for r in risks:
            print(f"    ! {r}")

    print()


def cmd_identify(args: argparse.Namespace) -> None:
    """Identify the cultural tradition of an image."""
    image_b64 = _read_image_b64(args.image)
    result = _api_post("/api/v1/identify-tradition", {"image_base64": image_b64})

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    tradition = result.get("tradition", "unknown")
    confidence = result.get("confidence", 0)
    alternatives = result.get("alternatives", [])

    print(f"\n  Tradition: {tradition} (confidence: {confidence:.0%})")
    if alternatives:
        for alt in alternatives[:3]:
            print(f"    - {alt.get('tradition', '?')}: {alt.get('confidence', 0):.0%}")
    print()


def cmd_traditions(args: argparse.Namespace) -> None:
    """List available traditions."""
    try:
        from app.prototype.cultural_pipelines.tradition_loader import get_all_traditions
        traditions = get_all_traditions()
    except ImportError:
        print("Cannot load traditions locally. Listing built-in names:")
        traditions = {}
        names = [
            "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
            "islamic_geometric", "japanese_traditional", "watercolor",
            "african_traditional", "south_asian",
        ]
        for n in names:
            print(f"  {n}")
        return

    if args.json:
        data = {}
        for name, tc in sorted(traditions.items()):
            data[name] = {
                "display_name": tc.display_name,
                "weights": tc.weights_l,
                "terms": len(tc.terminology),
                "taboos": len(tc.taboos),
                "pipeline": tc.pipeline.variant,
            }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f"\n  Available Traditions ({len(traditions)}):\n")
    for name, tc in sorted(traditions.items()):
        en_name = tc.display_name.get("en", name)
        print(f"  {name:25s}  {en_name:35s}  {len(tc.terminology)} terms  {len(tc.taboos)} taboos")
    print()


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate a tradition YAML file."""
    from app.prototype.cultural_pipelines.tradition_loader import validate_tradition_yaml

    errors = validate_tradition_yaml(args.file)
    if errors:
        print(f"FAIL: {len(errors)} error(s) in {args.file}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"PASS: {args.file} is valid")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vulca",
        description="VULCA Cultural Art Evaluation CLI",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    # evaluate
    p_eval = sub.add_parser("evaluate", help="Evaluate an image")
    p_eval.add_argument("image", help="Path to image file")
    p_eval.add_argument("--tradition", "-t", default="auto", help="Cultural tradition (default: auto-detect)")
    p_eval.add_argument("--subject", "-s", default="", help="Subject description")
    p_eval.add_argument("--evidence", "-e", action="store_true", help="Include Scout evidence")
    p_eval.set_defaults(func=cmd_evaluate)

    # identify
    p_id = sub.add_parser("identify", help="Identify cultural tradition")
    p_id.add_argument("image", help="Path to image file")
    p_id.set_defaults(func=cmd_identify)

    # traditions
    p_trad = sub.add_parser("traditions", help="List available traditions")
    p_trad.set_defaults(func=cmd_traditions)

    # validate
    p_val = sub.add_parser("validate", help="Validate a tradition YAML file")
    p_val.add_argument("file", help="Path to YAML file")
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
