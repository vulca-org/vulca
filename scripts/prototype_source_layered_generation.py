#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from vulca.layers.reconstruction import (
    load_reconstruction_contracts,
    source_layered_generate,
)


DEFAULT_CONTRACT = Path(
    "docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--mask-dir", required=True)
    parser.add_argument("--artifact-dir", default="")
    parser.add_argument("--prompt-contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.dry_run:
        raise SystemExit(
            "provider-backed prototype is not wired yet; pass --dry-run"
        )
    source_path = Path(args.source)
    contracts = load_reconstruction_contracts(args.prompt_contract)
    if args.artifact_dir:
        artifact_dir = Path(args.artifact_dir)
    else:
        artifact_dir = (
            Path(contracts.artifact_policy["default_artifact_root"]) / source_path.stem
        )

    result = source_layered_generate(
        source_image=source_path,
        mask_dir=args.mask_dir,
        artifact_dir=artifact_dir,
        prompt_contract=args.prompt_contract,
        provider=args.provider,
        model=args.model,
        dry_run=True,
    )
    print(result.summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
