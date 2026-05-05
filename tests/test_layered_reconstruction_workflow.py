import json
import subprocess
import sys

import numpy as np
from PIL import Image

from vulca.layers.reconstruction import (
    apply_owned_mask_to_source,
    should_use_local_redraw,
    source_layered_generate,
)


def test_preserve_layer_copies_source_pixels_under_owned_mask(tmp_path):
    source = Image.new("RGB", (4, 4), (10, 20, 30))
    mask = Image.new("L", (4, 4), 0)
    mask.paste(Image.new("L", (2, 2), 255), (1, 1))
    out_path = tmp_path / "hedge.png"

    result = apply_owned_mask_to_source(source, mask, out_path)

    assert result == out_path
    rgba = Image.open(out_path).convert("RGBA")
    arr = np.asarray(rgba)
    assert tuple(arr[1, 1]) == (10, 20, 30, 255)
    assert tuple(arr[0, 0]) == (10, 20, 30, 0)


def test_only_flower_detail_layers_use_local_redraw():
    assert should_use_local_redraw("detail.white_flower_cluster", "local_redraw")
    assert should_use_local_redraw("detail.yellow_dandelion_heads", "local_redraw")
    assert not should_use_local_redraw("foreground.hedge_bush", "preserve")
    assert not should_use_local_redraw("foreground.grass_bank", "preserve")


def test_prototype_cli_dry_run_writes_summary_without_provider(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8), (80, 120, 60)).save(source)
    mask_dir = tmp_path / "masks"
    mask_dir.mkdir()
    Image.new("L", (8, 8), 255).save(mask_dir / "foreground.hedge_bush.png")
    artifact_dir = tmp_path / "artifacts"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prototype_source_layered_generation.py",
            "--source",
            str(source),
            "--mask-dir",
            str(mask_dir),
            "--artifact-dir",
            str(artifact_dir),
            "--dry-run",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert str(artifact_dir / "summary.json") in result.stdout
    assert (artifact_dir / "manifest.json").exists()
    assert (artifact_dir / "layered_composite.png").exists()
    summary = json.loads((artifact_dir / "summary.json").read_text())
    assert summary["model"] == "gpt-image-2"
    assert summary["layer_policies"]["foreground.hedge_bush"]["policy"] == "preserve"


def test_prototype_cli_requires_dry_run_until_provider_is_wired(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8), (80, 120, 60)).save(source)
    mask_dir = tmp_path / "masks"
    mask_dir.mkdir()
    artifact_dir = tmp_path / "artifacts"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prototype_source_layered_generation.py",
            "--source",
            str(source),
            "--mask-dir",
            str(mask_dir),
            "--artifact-dir",
            str(artifact_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--dry-run" in result.stderr


def test_source_layered_generate_dry_run_creates_manifest_composite_and_summary(
    tmp_path,
):
    source = tmp_path / "source.png"
    Image.new("RGB", (10, 10), (90, 120, 70)).save(source)
    mask_dir = tmp_path / "masks"
    mask_dir.mkdir()
    Image.new("L", (10, 10), 255).save(mask_dir / "foreground.hedge_bush.png")

    result = source_layered_generate(
        source_image=source,
        mask_dir=mask_dir,
        artifact_dir=tmp_path / "run",
        dry_run=True,
    )

    assert result.summary_path.exists()
    assert result.manifest_path.exists()
    assert result.composite_path.exists()
    assert result.artifact_dir == tmp_path / "run"


def test_source_layered_generate_summary_records_parent_subtraction(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (10, 10), (90, 120, 70)).save(source)
    mask_dir = tmp_path / "masks"
    mask_dir.mkdir()
    Image.new("L", (10, 10), 255).save(mask_dir / "foreground.hedge_bush.png")
    flower = Image.new("L", (10, 10), 0)
    flower.paste(Image.new("L", (2, 2), 255), (4, 4))
    flower.save(mask_dir / "detail.white_flower_cluster.png")

    result = source_layered_generate(
        source_image=source,
        mask_dir=mask_dir,
        artifact_dir=tmp_path / "run",
        dry_run=True,
    )

    summary = json.loads(result.summary_path.read_text())
    hedge = summary["layer_policies"]["foreground.hedge_bush"]
    assert hedge["mask_area_pct"] == 100.0
    assert hedge["owned_area_pct"] == 96.0
    assert hedge["subtracted_by"] == ["detail.white_flower_cluster"]
    assert hedge["subtracted_pixel_count"] == 4
