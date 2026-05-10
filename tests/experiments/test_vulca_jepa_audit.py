from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from scripts.experiments.vulca_jepa_audit import (
    compute_pairwise_distances,
    mock_image_embedding,
    run_mock_audit,
    write_audit,
)
from scripts.experiments.vulca_jepa_inventory import SampleSpec, build_inventory


def _write_pattern_image(path: Path, offset: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (12, 10))
    for y in range(image.height):
        for x in range(image.width):
            image.putpixel(
                (x, y),
                (
                    (x * 23 + offset) % 256,
                    (y * 31 + offset * 2) % 256,
                    ((x + y) * 17 + offset * 3) % 256,
                ),
            )
    image.save(path)


def _write_black_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (12, 10), (0, 0, 0)).save(path)


def _write_manifest(tmp_path: Path) -> Path:
    _write_pattern_image(tmp_path / "a.png", 0)
    _write_pattern_image(tmp_path / "b.png", 40)
    _write_pattern_image(tmp_path / "c.png", 90)
    _write_black_image(tmp_path / "black.png")
    inventory = build_inventory(
        repo_root=tmp_path,
        sample_specs=[
            SampleSpec(sample_id="a", group="gallery_breadth", path="a.png", purpose="a"),
            SampleSpec(sample_id="b", group="gallery_breadth", path="b.png", purpose="b"),
            SampleSpec(sample_id="c", group="fusion", path="c.png", purpose="c"),
            SampleSpec(sample_id="black", group="edit_inpaint", path="black.png", purpose="black"),
        ],
    )
    manifest = tmp_path / "inventory.json"
    manifest.write_text(json.dumps(inventory))
    return manifest


def test_mock_image_embedding_is_deterministic(tmp_path: Path) -> None:
    _write_pattern_image(tmp_path / "a.png", 7)

    first = mock_image_embedding(tmp_path / "a.png")
    second = mock_image_embedding(tmp_path / "a.png")

    assert first == second
    assert len(first) == 9
    assert all(0.0 <= value <= 1.0 for value in first)


def test_compute_pairwise_distances_returns_unique_pairs() -> None:
    embeddings = {
        "a": [0.0, 0.0],
        "b": [1.0, 0.0],
        "c": [0.0, 1.0],
    }

    pairs = compute_pairwise_distances(embeddings)

    assert [pair["pair"] for pair in pairs] == [["a", "b"], ["a", "c"], ["b", "c"]]
    assert pairs[0]["distance"] == 1.0
    assert pairs[2]["distance"] == 1.414214


def test_run_mock_audit_filters_to_core_samples(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path)

    audit = run_mock_audit(manifest)

    assert audit["backend"] == "mock"
    assert audit["audit_set"] == "core"
    assert audit["samples_total"] == 3
    assert audit["pairwise_distances_total"] == 3
    assert [sample["sample_id"] for sample in audit["samples"]] == ["a", "b", "c"]
    assert {sample["sample_id"] for sample in audit["excluded_samples"]} == {"black"}
    assert len(audit["anomaly_ranking"]) == 3
    assert audit["anomaly_ranking"][0]["mean_distance"] >= audit["anomaly_ranking"][-1]["mean_distance"]


def test_write_audit_outputs_json(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path)
    out = tmp_path / "audit.json"

    audit = write_audit(manifest, out)

    loaded = json.loads(out.read_text())
    assert loaded == audit
    assert loaded["samples_total"] == 3
    assert loaded["pairwise_distances_total"] == 3
