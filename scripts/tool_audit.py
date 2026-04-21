"""Tool readiness audit — PASS/FAIL/latency matrix across the 24-image showcase.

Targets the 11 Skeleton-tier MCP tools listed in the 2026-04-20 session plan.
Designed to be CI-runnable: a dry-run prints the corpus and exits 0 without
invoking any tool; a full run awaits each tool sequentially and writes a
machine-readable JSON report plus a printable summary.

Skeleton-tier tools (11):
  brief_parse, generate_image, create_artwork, generate_concepts,
  inpaint_artwork, layers_redraw, layers_edit, layers_transform,
  layers_evaluate, archive_session, sync_data

Showcase corpus (24 images) is drawn from:
  - assets/demo/v3/gallery             (13 traditions)
  - assets/demo/v3/gallery-promptfix   (5 prompt-engineered variants)
  - assets/demo/v3/layered             (up to 3)
  - assets/demo/v3/defense3            (up to 3)

See docs/tools-readiness-matrix.md for the companion analysis.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import resource
import statistics
import sys
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHOWCASE_DIRS = [
    REPO_ROOT / "assets/demo/v3/gallery",
    REPO_ROOT / "assets/demo/v3/gallery-promptfix",
    REPO_ROOT / "assets/demo/v3/layered",
    REPO_ROOT / "assets/demo/v3/defense3",
]
TARGET_CORPUS_SIZE = 24

SKELETON_TIER_TOOLS = [
    "brief_parse",
    "generate_image",
    "create_artwork",
    "generate_concepts",
    "inpaint_artwork",
    "layers_redraw",
    "layers_edit",
    "layers_transform",
    "layers_evaluate",
    "archive_session",
    "sync_data",
]


@dataclass
class ToolResult:
    tool: str
    image: str
    status: str
    error_mode: str | None = None
    latency_ms: float | None = None
    output_hash: str | None = None
    peak_rss_mb: float | None = None


@dataclass
class ToolSummary:
    tool: str
    results: list[ToolResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        total = len([r for r in self.results if r.status != "SKIP"])
        if total == 0:
            return 0.0
        passes = len([r for r in self.results if r.status == "PASS"])
        return passes / total

    @property
    def p50_latency_ms(self) -> float | None:
        values = [r.latency_ms for r in self.results if r.latency_ms is not None]
        return statistics.median(values) if values else None

    @property
    def common_error_modes(self) -> list[str]:
        return sorted({r.error_mode for r in self.results if r.error_mode})


def collect_corpus() -> list[Path]:
    """Walk the 4 showcase dirs and return up to TARGET_CORPUS_SIZE unique images."""
    images: list[Path] = []
    for d in SHOWCASE_DIRS:
        if not d.exists():
            continue
        images.extend(sorted(d.glob("*.png")))
        images.extend(sorted(d.glob("*.jpg")))

    seen: set[tuple[str, str]] = set()
    unique: list[Path] = []
    for p in images:
        key = (p.parent.name, p.stem)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique[:TARGET_CORPUS_SIZE]


async def _time_call(fn: Callable[..., Awaitable], **kwargs) -> tuple[float, object]:
    start = time.perf_counter()
    result = await fn(**kwargs)
    return (time.perf_counter() - start) * 1000, result


def _hash_result(result: object) -> str:
    try:
        payload = json.dumps(result, sort_keys=True, default=str).encode()
    except TypeError:
        payload = str(result).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def _peak_rss_mb() -> float:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1024 * 1024) if sys.platform == "darwin" else rss / 1024


async def run_tool_on_image(tool_name: str, image: Path) -> ToolResult:
    """Invoke one Skeleton-tier tool against one image; convert any exception to FAIL."""
    from vulca import mcp_server as srv

    try:
        if tool_name == "brief_parse":
            latency, result = await _time_call(
                srv.brief_parse, intent="spring festival poster, song gongbi style"
            )
        elif tool_name == "generate_image":
            latency, result = await _time_call(
                srv.generate_image,
                prompt="a single plum blossom branch, song gongbi",
                output_dir=str(image.parent),
            )
        elif tool_name == "create_artwork":
            latency, result = await _time_call(
                srv.create_artwork,
                intent="spring festival poster",
                output_dir=str(image.parent),
            )
        elif tool_name == "generate_concepts":
            latency, result = await _time_call(
                srv.generate_concepts, prompt="spring festival poster", count=2
            )
        elif tool_name == "inpaint_artwork":
            latency, result = await _time_call(
                srv.inpaint_artwork, image_path=str(image), mask_hint="background"
            )
        elif tool_name == "layers_redraw":
            latency, result = await _time_call(
                srv.layers_redraw, artwork_dir=str(image.parent), layer="background"
            )
        elif tool_name == "layers_edit":
            latency, result = await _time_call(
                srv.layers_edit, artwork_dir=str(image.parent), operation="list"
            )
        elif tool_name == "layers_transform":
            latency, result = await _time_call(
                srv.layers_transform,
                artwork_dir=str(image.parent),
                layer="subject",
                transform="identity",
            )
        elif tool_name == "layers_evaluate":
            latency, result = await _time_call(
                srv.layers_evaluate, artwork_dir=str(image.parent)
            )
        elif tool_name == "archive_session":
            latency, result = await _time_call(
                srv.archive_session,
                intent="tool-audit",
                output_dir=str(image.parent),
            )
        elif tool_name == "sync_data":
            latency, result = await _time_call(srv.sync_data, pull_only=True)
        else:
            return ToolResult(tool_name, image.name, "SKIP", error_mode="unknown-tool")

        return ToolResult(
            tool=tool_name,
            image=image.name,
            status="PASS",
            latency_ms=latency,
            output_hash=_hash_result(result),
            peak_rss_mb=_peak_rss_mb(),
        )
    except Exception as e:
        return ToolResult(
            tool=tool_name,
            image=image.name,
            status="FAIL",
            error_mode=type(e).__name__,
            peak_rss_mb=_peak_rss_mb(),
        )


async def audit(
    tools: list[str], corpus: list[Path], verbose: bool
) -> dict[str, ToolSummary]:
    summaries = {t: ToolSummary(tool=t) for t in tools}
    for tool in tools:
        for image in corpus:
            if verbose:
                print(f"[{tool}] {image.name} ...", end="", flush=True)
            result = await run_tool_on_image(tool, image)
            summaries[tool].results.append(result)
            if verbose:
                tail = (
                    f" {result.status} ({result.latency_ms:.0f}ms)"
                    if result.latency_ms is not None
                    else f" {result.status} ({result.error_mode})"
                )
                print(tail)
    return summaries


def render_text_report(summaries: dict[str, ToolSummary]) -> str:
    lines = ["tool_audit summary", "=" * 60]
    for tool, s in summaries.items():
        p50 = f"{s.p50_latency_ms:.0f}ms" if s.p50_latency_ms is not None else "n/a"
        errs = ", ".join(s.common_error_modes) or "—"
        lines.append(
            f"{tool:<20} pass={s.pass_rate:>6.1%}  p50={p50:>8}  errs={errs}"
        )
    return "\n".join(lines)


def render_json_report(summaries: dict[str, ToolSummary]) -> str:
    payload = {
        tool: {
            "pass_rate": s.pass_rate,
            "p50_latency_ms": s.p50_latency_ms,
            "common_error_modes": s.common_error_modes,
            "results": [
                {
                    "image": r.image,
                    "status": r.status,
                    "error_mode": r.error_mode,
                    "latency_ms": r.latency_ms,
                    "output_hash": r.output_hash,
                    "peak_rss_mb": r.peak_rss_mb,
                }
                for r in s.results
            ],
        }
        for tool, s in summaries.items()
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the corpus and tool list, then exit without invoking tools.",
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        default=SKELETON_TIER_TOOLS,
        help="Restrict to a subset of the Skeleton-tier tools.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write the machine-readable report to this path.",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    corpus = collect_corpus()
    if not corpus:
        print(
            "ERROR: no showcase images found under",
            [str(d.relative_to(REPO_ROOT)) for d in SHOWCASE_DIRS],
            file=sys.stderr,
        )
        return 2

    dirs_covered = sorted({p.parent.name for p in corpus})
    print(f"corpus: {len(corpus)} images across {len(dirs_covered)} dirs ({', '.join(dirs_covered)})")
    print(f"tools:  {len(args.tools)} ({', '.join(args.tools)})")

    if args.dry_run:
        print("\nDRY RUN — not invoking tools.\n")
        for p in corpus:
            print(f"  - {p.relative_to(REPO_ROOT)}")
        return 0

    summaries = asyncio.run(audit(args.tools, corpus, args.verbose))
    print()
    print(render_text_report(summaries))

    if args.json_out:
        args.json_out.write_text(render_json_report(summaries))
        print(f"\nwrote JSON report to {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
