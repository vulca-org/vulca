from __future__ import annotations

from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-case-pack-v1"


def test_ppt_case_pack_v1_is_valid() -> None:
    result = validate_case_pack(PACK)

    assert result.ok is True, result.errors
