from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_deck_builder_requires_explicit_approval() -> None:
    result = subprocess.run(
        ["node", "scripts/build_customer_solution_pack_deck.mjs"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--approval-recorded" in result.stderr
    assert "output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx" in result.stderr
    assert "output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf" in result.stderr
