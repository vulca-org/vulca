from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from scripts.experiments.vulca_jepa_inventory import SampleSpec, analyze_image_quality, build_inventory, write_inventory


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 6), color).save(path)


def _write_pattern_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (8, 6))
    for y in range(image.height):
        for x in range(image.width):
            image.putpixel((x, y), (x * 31 % 256, y * 47 % 256, (x + y) * 29 % 256))
    image.save(path)


def test_build_inventory_records_dimensions_and_missing_count(tmp_path: Path) -> None:
    _write_image(tmp_path / "assets" / "ok.png", (255, 0, 0))

    specs = [
        SampleSpec(
            sample_id="existing",
            group="gallery_promptfix",
            path="assets/ok.png",
            purpose="existing image",
            prompt="red tile",
        ),
        SampleSpec(
            sample_id="missing",
            group="gallery_promptfix",
            path="assets/missing.png",
            purpose="missing image",
        ),
    ]

    inventory = build_inventory(repo_root=tmp_path, sample_specs=specs)

    assert inventory["samples_total"] == 2
    assert inventory["missing_total"] == 1
    assert inventory["groups"] == {"gallery_promptfix": 2}
    assert inventory["samples"][0]["exists"] is True
    assert inventory["samples"][0]["width"] == 8
    assert inventory["samples"][0]["height"] == 6
    assert inventory["samples"][0]["mode"] == "RGB"
    assert inventory["samples"][1]["exists"] is False
    assert inventory["samples"][1]["width"] is None


def test_analyze_image_quality_marks_opaque_black_as_unusable(tmp_path: Path) -> None:
    _write_image(tmp_path / "black.png", (0, 0, 0))

    quality = analyze_image_quality(tmp_path / "black.png")

    assert quality["luma_mean"] == 0.0
    assert quality["luma_stddev"] == 0.0
    assert quality["alpha_coverage"] == 1.0
    assert quality["near_black_opaque"] is True
    assert quality["low_information"] is True


def test_inventory_splits_black_image_into_artifact_qa(tmp_path: Path) -> None:
    _write_image(tmp_path / "assets" / "black.png", (0, 0, 0))

    inventory = build_inventory(
        repo_root=tmp_path,
        sample_specs=[
            SampleSpec(
                sample_id="black_edit",
                group="edit_inpaint",
                path="assets/black.png",
                purpose="black edit artifact",
            )
        ],
    )

    sample = inventory["samples"][0]
    assert sample["audit_set"] == "artifact_qa"
    assert sample["usable_for_embedding"] is False
    assert sample["reject_reasons"] == ["near_black_opaque", "low_information"]
    assert inventory["audit_sets"] == {"artifact_qa": 1}


def test_inventory_keeps_visual_gallery_image_in_core(tmp_path: Path) -> None:
    _write_pattern_image(tmp_path / "assets" / "visual.png")

    inventory = build_inventory(
        repo_root=tmp_path,
        sample_specs=[
            SampleSpec(
                sample_id="visual_gallery",
                group="gallery_breadth",
                path="assets/visual.png",
                purpose="usable visual sample",
            )
        ],
    )

    sample = inventory["samples"][0]
    assert sample["audit_set"] == "core"
    assert sample["usable_for_embedding"] is True
    assert sample["reject_reasons"] == []
    assert inventory["audit_sets"] == {"core": 1}


def test_inventory_keeps_intermediate_layers_out_of_core(tmp_path: Path) -> None:
    _write_pattern_image(tmp_path / "assets" / "layer.png")

    inventory = build_inventory(
        repo_root=tmp_path,
        sample_specs=[
            SampleSpec(
                sample_id="layer",
                group="layered",
                path="assets/layer.png",
                purpose="intermediate layer",
            )
        ],
    )

    sample = inventory["samples"][0]
    assert sample["audit_set"] == "artifact_qa"
    assert sample["usable_for_embedding"] is False
    assert sample["reject_reasons"] == ["intermediate_artifact"]


def test_default_inventory_is_vulca_only() -> None:
    inventory = build_inventory()
    paths = [sample["path"] for sample in inventory["samples"]]

    assert inventory["samples_total"] == 30
    assert inventory["audit_sets"]["core"] >= 1
    assert inventory["audit_sets"]["artifact_qa"] >= 1
    assert "gallery_promptfix" in inventory["groups"]
    assert "fusion" in inventory["groups"]
    assert all("/Users/yhryzy/dev/emoart-130k" not in path for path in paths)
    assert all("Track2" not in path and "track2" not in path for path in paths)


def test_write_inventory_outputs_json(tmp_path: Path) -> None:
    _write_image(tmp_path / "assets" / "ok.png", (0, 255, 0))
    out = tmp_path / "inventory.json"

    inventory = write_inventory(
        out,
        repo_root=tmp_path,
        sample_specs=[
            SampleSpec(
                sample_id="existing",
                group="edit_inpaint",
                path="assets/ok.png",
                purpose="existing image",
            )
        ],
    )

    loaded = json.loads(out.read_text())
    assert loaded == inventory
    assert loaded["samples_total"] == 1
    assert loaded["missing_total"] == 0


def test_contact_sheet_inputs_are_valid() -> None:
    inventory = build_inventory()

    assert len({sample["sample_id"] for sample in inventory["samples"]}) == inventory["samples_total"]
    assert all(not Path(sample["path"]).is_absolute() for sample in inventory["samples"])
    assert all("/Users/yhryzy/dev/emoart-130k" not in sample["path"] for sample in inventory["samples"])
