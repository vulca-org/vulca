#!/usr/bin/env python3
"""Verify README.md — all image paths exist, tracked, and reasonable.

Run before any push that changes README:
    .venv/bin/python scripts/verify-readme.py
"""
import re
import subprocess
import sys
from pathlib import Path

README = Path("README.md")
ERRORS = []
WARNINGS = []


def error(msg):
    ERRORS.append(msg)
    print(f"  ❌ {msg}")


def warn(msg):
    WARNINGS.append(msg)
    print(f"  ⚠️  {msg}")


def ok(msg):
    print(f"  ✅ {msg}")


def main():
    if not README.exists():
        print("ERROR: README.md not found. Run from vulca/ directory.")
        sys.exit(1)

    content = README.read_text()
    print("VULCA README Verification")
    print("=" * 50)

    # 1. Check all image references
    print("\n[1] Image references:")
    img_refs = re.findall(r'<img src="([^"]+)"', content)
    seen = set()
    for ref in img_refs:
        if ref in seen:
            continue
        seen.add(ref)
        path = Path(ref)
        if not path.exists():
            error(f"Missing file: {ref}")
        else:
            size_kb = path.stat().st_size / 1024
            if size_kb < 1:
                error(f"Suspiciously small ({size_kb:.0f}B): {ref}")
            else:
                try:
                    from PIL import Image
                    img = Image.open(path)
                    ok(f"{ref} ({size_kb:.0f}KB, {img.size[0]}x{img.size[1]})")
                except Exception as e:
                    warn(f"Cannot verify image {ref}: {e}")
    print(f"  Total: {len(seen)} unique images")

    # 2. Check git tracking
    print("\n[2] Git tracking:")
    result = subprocess.run(["git", "ls-files", "--error-unmatch"] + [str(Path(r)) for r in seen],
                           capture_output=True, text=True)
    if result.returncode != 0:
        for line in result.stderr.strip().split("\n"):
            if "not in" in line or "did not match" in line:
                error(f"Untracked: {line}")
    else:
        ok(f"All {len(seen)} images tracked in git")

    # 3. Check numbers consistency
    print("\n[3] Number consistency:")
    test_match = re.search(r'(\d+)%20passing', content)
    if test_match:
        readme_tests = int(test_match.group(1))
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
                               capture_output=True, text=True, timeout=300)
        actual_line = result.stdout.strip().split("\n")[-1]
        actual_match = re.match(r"(\d+) passed", actual_line)
        if actual_match:
            actual_tests = int(actual_match.group(1))
            if readme_tests != actual_tests:
                warn(f"Test count mismatch: README={readme_tests}, actual={actual_tests}")
            else:
                ok(f"Test count: {actual_tests}")

    mcp_match = re.search(r'(\d+) MCP tools', content)
    if mcp_match:
        readme_mcp = int(mcp_match.group(1))
        result = subprocess.run(["grep", "-c", "@mcp.tool", "src/vulca/mcp_server.py"],
                               capture_output=True, text=True)
        actual_mcp = int(result.stdout.strip()) if result.returncode == 0 else 0
        if readme_mcp != actual_mcp:
            warn(f"MCP tool count mismatch: README={readme_mcp}, actual={actual_mcp}")
        else:
            ok(f"MCP tools: {actual_mcp}")

    # 4. Mermaid
    print("\n[4] Mermaid diagrams:")
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
    for i, block in enumerate(mermaid_blocks):
        if "graph" in block or "flowchart" in block:
            ok(f"Mermaid block {i+1}: valid")
        else:
            warn(f"Mermaid block {i+1}: unusual syntax")

    # Summary
    print(f"\n{'=' * 50}")
    if ERRORS:
        print(f"FAIL: {len(ERRORS)} errors, {len(WARNINGS)} warnings")
        sys.exit(1)
    elif WARNINGS:
        print(f"PASS with {len(WARNINGS)} warnings")
    else:
        print("PASS: all checks passed")


if __name__ == "__main__":
    main()
