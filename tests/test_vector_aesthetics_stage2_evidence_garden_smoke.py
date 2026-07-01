from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_stage02_evidence_garden_glb.py"
ASSET_DIR = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden"
    / "assets"
)
GLB = ASSET_DIR / "evidence-garden-blockout.glb"
MANIFEST = ASSET_DIR / "asset-manifest.json"
SMOKE = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden-smoke"
    / "index.html"
)


def _parse_glb(path: Path) -> tuple[dict[str, object], bytes]:
    blob = path.read_bytes()
    magic, version, total_length = struct.unpack_from("<III", blob, 0)
    assert magic == 0x46546C67
    assert version == 2
    assert total_length == len(blob)
    json_length, json_type = struct.unpack_from("<I4s", blob, 12)
    assert json_type == b"JSON"
    json_start = 20
    json_end = json_start + json_length
    gltf = json.loads(blob[json_start:json_end].decode("utf-8"))
    bin_length, bin_type = struct.unpack_from("<I4s", blob, json_end)
    assert bin_type == b"BIN\x00"
    bin_start = json_end + 8
    binary = blob[bin_start : bin_start + bin_length]
    assert len(binary) == bin_length
    return gltf, binary


def test_evidence_garden_glb_builder_script_regenerates_asset(tmp_path: Path):
    output = tmp_path / "evidence-garden-blockout.glb"
    manifest = tmp_path / "asset-manifest.json"

    subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(output), "--manifest", str(manifest)],
        check=True,
        cwd=REPO_ROOT,
    )

    assert output.is_file()
    assert output.stat().st_size > 20_000
    assert manifest.is_file()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["asset_id"] == "evidence-garden-blockout"
    assert payload["source"] == "procedural_blockout"


def test_evidence_garden_committed_glb_has_expected_scene_parts():
    assert GLB.is_file()
    gltf, binary = _parse_glb(GLB)

    assert gltf["asset"]["version"] == "2.0"
    assert gltf["asset"]["generator"] == "vulca stage02 evidence garden procedural blockout"
    assert len(gltf["materials"]) == 5
    assert len(gltf["meshes"]) == 6
    assert len(binary) > 20_000
    mesh_names = {mesh["name"] for mesh in gltf["meshes"]}
    assert mesh_names == {
        "evidence_garden_mineral_island",
        "evidence_garden_moss_specimen_surface",
        "evidence_garden_translucent_roots",
        "evidence_garden_luminous_route_veins",
        "evidence_garden_warm_data_blossoms",
        "evidence_garden_archive_seed_particles",
    }


def test_evidence_garden_asset_manifest_marks_blockout_not_final():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert payload["format"] == "glb"
    assert payload["rights_status"] == "generated_local_procedural"
    assert payload["do_not_treat_as_final_asset"] is True
    assert "evidence_garden_translucent_roots" in payload["model_parts"]
    assert "cyan_route_veins" in payload["materials"]


def test_evidence_garden_model_viewer_smoke_page_points_at_local_glb():
    html_text = SMOKE.read_text(encoding="utf-8")

    assert SMOKE.is_file()
    assert 'data-vector-stage-product="2026-06-stage-02-evidence-garden-glb-smoke"' in html_text
    assert "<model-viewer" in html_text
    assert "https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js" in html_text
    assert "../3d-vector-aesthetic-stage-02-evidence-garden/assets/evidence-garden-blockout.glb" in html_text
    for state in ["Dormant Island", "Root Scan", "Data Bloom", "Archive Constellation"]:
        assert state in html_text
