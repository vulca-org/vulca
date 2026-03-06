#!/usr/bin/env python3
"""Unit 4: All-tradition batch validation script.

Standalone script (NOT pytest) that runs B2B API evaluation for all
9 traditions against a real or mocked backend. Generates markdown and
JSON reports.

Usage:
    python tests/smoke/run_all_traditions.py --dry-run       # No API calls
    python tests/smoke/run_all_traditions.py                  # Real API calls
    python tests/smoke/run_all_traditions.py --tradition chinese_xieyi  # Single
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = os.environ.get("VULCA_API_BASE", "http://localhost:8001")
API_KEY = os.environ.get("VULCA_API_KEY", "test-key-m4-2026")

TRADITIONS = {
    "default": "Abstract contemporary artwork with mixed media elements",
    "chinese_xieyi": "Freehand ink mountain landscape with mist and bamboo",
    "chinese_gongbi": "Detailed meticulous brushwork painting of peonies and birds",
    "western_academic": "Renaissance-style oil portrait with chiaroscuro lighting",
    "islamic_geometric": "Geometric arabesque tile pattern with octagonal star motifs",
    "japanese_traditional": "Ukiyo-e woodblock print of cherry blossoms and Mount Fuji",
    "watercolor": "Impressionist watercolor landscape with soft wet-on-wet technique",
    "african_traditional": "Kente cloth inspired geometric pattern with symbolic colors",
    "south_asian": "Mughal miniature painting with ornate border and garden scene",
}

REPORT_DIR = Path(__file__).resolve().parents[2] / "app" / "prototype" / "reports"
JSON_OUTPUT = Path(__file__).resolve().parent / "tradition_results.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_api_key() -> bool:
    """Check if API credentials are available."""
    gemini_key = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or ""
    )
    if not gemini_key:
        print("[WARN] No GEMINI_API_KEY / GOOGLE_API_KEY found.")
        print("       Real API calls require a running backend with Gemini key.")
        return False
    return True


def check_backend_health() -> bool:
    """Quick health check against the backend."""
    try:
        import httpx
        resp = httpx.get(f"{API_BASE}/health", timeout=5)
        return resp.status_code == 200
    except Exception as e:
        print(f"[WARN] Backend health check failed: {e}")
        return False


def evaluate_tradition(tradition: str, subject: str) -> dict:
    """Call POST /api/v1/evaluate for a single tradition."""
    import httpx

    # Use a minimal 1x1 PNG since we're testing the pipeline, not image quality.
    # In a real scenario, you'd use a proper test image.
    import base64

    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    img_b64 = base64.b64encode(png_bytes).decode()

    t0 = time.monotonic()
    resp = httpx.post(
        f"{API_BASE}/api/v1/evaluate",
        json={
            "image_base64": img_b64,
            "tradition": tradition,
            "subject": subject,
        },
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=120,
    )
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    if resp.status_code != 200:
        return {
            "tradition": tradition,
            "status": "error",
            "status_code": resp.status_code,
            "detail": resp.text[:200],
            "client_latency_ms": elapsed_ms,
        }

    data = resp.json()
    data["client_latency_ms"] = elapsed_ms
    data["status"] = "ok"
    return data


def identify_tradition_call(tradition: str) -> dict | None:
    """Call POST /api/v1/identify-tradition."""
    import httpx
    import base64

    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    img_b64 = base64.b64encode(png_bytes).decode()

    try:
        resp = httpx.post(
            f"{API_BASE}/api/v1/identify-tradition",
            json={"image_base64": img_b64},
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=120,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  [WARN] identify-tradition failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(results: list[dict], dry_run: bool = False) -> str:
    """Generate markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# P0 Tradition Validation Report",
        f"",
        f"Generated: {now}",
        f"Mode: {'dry-run (no API calls)' if dry_run else 'real API calls'}",
        f"Backend: {API_BASE}",
        f"",
    ]

    if dry_run:
        lines += [
            "## Dry-run Results",
            "",
            "All 9 traditions validated structurally (no API calls made).",
            "",
            "| # | Tradition | Subject | Status |",
            "|---|-----------|---------|--------|",
        ]
        for i, r in enumerate(results, 1):
            lines.append(
                f"| {i} | `{r['tradition']}` | {r['subject']} | {r['status']} |"
            )
    else:
        lines += [
            "## Evaluation Results",
            "",
            "| # | Tradition | L1 | L2 | L3 | L4 | L5 | Weighted | Latency (ms) | Status |",
            "|---|-----------|-----|-----|-----|-----|-----|----------|-------------|--------|",
        ]
        for i, r in enumerate(results, 1):
            if r["status"] == "ok":
                s = r.get("scores", {})
                lines.append(
                    f"| {i} | `{r.get('tradition_used', r['tradition'])}` "
                    f"| {s.get('L1', 0):.3f} | {s.get('L2', 0):.3f} "
                    f"| {s.get('L3', 0):.3f} | {s.get('L4', 0):.3f} "
                    f"| {s.get('L5', 0):.3f} | {r.get('weighted_total', 0):.3f} "
                    f"| {r.get('client_latency_ms', r.get('latency_ms', 0))} "
                    f"| ok |"
                )
            else:
                lines.append(
                    f"| {i} | `{r['tradition']}` "
                    f"| - | - | - | - | - | - "
                    f"| {r.get('client_latency_ms', '-')} "
                    f"| {r['status']}: {r.get('detail', '')[:50]} |"
                )

    # Summary
    ok_count = sum(1 for r in results if r["status"] == "ok")
    lines += [
        "",
        "## Summary",
        "",
        f"- Total traditions: {len(results)}",
        f"- Passed: {ok_count}",
        f"- Failed: {len(results) - ok_count}",
    ]

    if not dry_run and ok_count > 0:
        ok_results = [r for r in results if r["status"] == "ok"]
        avg_total = sum(r.get("weighted_total", 0) for r in ok_results) / ok_count
        avg_latency = sum(r.get("client_latency_ms", 0) for r in ok_results) / ok_count
        lines += [
            f"- Avg weighted_total: {avg_total:.3f}",
            f"- Avg latency: {avg_latency:.0f} ms",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="P0 All-Tradition Batch Validation")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls, validate script structure only")
    parser.add_argument("--tradition", type=str, help="Run a single tradition")
    args = parser.parse_args()

    print("=" * 60)
    print("P0: All-Tradition Batch Validation")
    print("=" * 60)

    # Select traditions
    if args.tradition:
        if args.tradition not in TRADITIONS:
            print(f"[ERROR] Unknown tradition: {args.tradition}")
            print(f"  Available: {', '.join(TRADITIONS.keys())}")
            sys.exit(1)
        traditions_to_run = {args.tradition: TRADITIONS[args.tradition]}
    else:
        traditions_to_run = TRADITIONS

    results: list[dict] = []

    if args.dry_run:
        print("\n[DRY-RUN] Validating script structure (no API calls)...\n")
        for tradition, subject in traditions_to_run.items():
            print(f"  [{tradition}] subject: {subject[:50]}... OK")
            results.append({
                "tradition": tradition,
                "subject": subject,
                "status": "dry-run-ok",
            })
    else:
        # Pre-flight checks
        has_key = check_api_key()
        backend_ok = check_backend_health()

        if not backend_ok:
            print("\n[ERROR] Backend is not reachable at", API_BASE)
            print("  Start the backend first: cd wenxin-backend && python -m uvicorn app.main:app --port 8001")
            sys.exit(1)

        if not has_key:
            print("\n[WARN] Proceeding without Gemini key — VLM calls may fail.\n")

        # Run evaluations
        print(f"\nRunning {len(traditions_to_run)} tradition(s)...\n")
        for tradition, subject in traditions_to_run.items():
            print(f"  [{tradition}] Evaluating... ", end="", flush=True)
            result = evaluate_tradition(tradition, subject)
            result["tradition"] = tradition  # ensure key is present
            results.append(result)

            if result["status"] == "ok":
                wt = result.get("weighted_total", 0)
                ms = result.get("client_latency_ms", 0)
                print(f"OK  weighted_total={wt:.3f}  latency={ms}ms")
            else:
                print(f"FAIL  {result.get('detail', '')[:60]}")

        # Optional: identify-tradition call
        print("\n  [identify-tradition] Testing... ", end="", flush=True)
        ident = identify_tradition_call("default")
        if ident:
            print(f"OK  detected={ident.get('tradition', '?')}  conf={ident.get('confidence', 0):.2f}")
        else:
            print("SKIP (failed or unavailable)")

    # Generate reports
    report_md = generate_report(results, dry_run=args.dry_run)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "p0-tradition-validation.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"\nReport: {report_path}")

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON:   {JSON_OUTPUT}")

    # Exit code
    fail_count = sum(1 for r in results if r["status"] not in ("ok", "dry-run-ok"))
    if fail_count:
        print(f"\n[FAIL] {fail_count}/{len(results)} traditions failed.")
        sys.exit(1)
    else:
        print(f"\n[PASS] All {len(results)} traditions validated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
