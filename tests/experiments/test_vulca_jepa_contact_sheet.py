from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from scripts.experiments.vulca_jepa_contact_sheet import make_contact_sheet


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (10, 8), color).save(path)


def test_make_contact_sheet_writes_grid_from_inventory(tmp_path: Path) -> None:
    _write_image(tmp_path / "a.png", (255, 0, 0))
    _write_image(tmp_path / "b.png", (0, 255, 0))

    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text(
        json.dumps(
            {
                "repo_root": str(tmp_path),
                "samples_total": 2,
                "missing_total": 0,
                "groups": {"demo": 2},
                "samples": [
                    {
                        "sample_id": "red",
                        "group": "demo",
                        "path": "a.png",
                        "exists": True,
                        "width": 10,
                        "height": 8,
                        "mode": "RGB",
                        "purpose": "red tile",
                        "prompt": "",
                        "context": [],
                    },
                    {
                        "sample_id": "green",
                        "group": "demo",
                        "path": "b.png",
                        "exists": True,
                        "width": 10,
                        "height": 8,
                        "mode": "RGB",
                        "purpose": "green tile",
                        "prompt": "",
                        "context": [],
                    },
                ],
            }
        )
    )

    out = tmp_path / "sheet.png"
    result = make_contact_sheet(inventory_path, out, tile_size=64, columns=2)

    assert result == out
    assert out.exists()
    with Image.open(out) as image:
        assert image.mode == "RGB"
        assert image.size[0] >= 2 * 64
        assert image.size[1] >= 64
