from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

import scripts.experiments.vulca_jepa_audit as audit_mod
from scripts.experiments.vulca_jepa_audit import (
    BackendUnavailable,
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


def test_write_audit_dispatches_dinov2_backend(tmp_path: Path, monkeypatch) -> None:
    manifest = _write_manifest(tmp_path)
    out = tmp_path / "dinov2.json"
    calls = {}

    def fake_run(manifest_path, *, audit_set, model):
        calls["manifest"] = manifest_path
        calls["audit_set"] = audit_set
        calls["model"] = model
        return {
            "schema_version": "vulca_jepa_audit.v1",
            "backend": "dinov2",
            "status": "ok",
            "model": model,
            "audit_set": audit_set,
            "samples_total": 0,
            "pairwise_distances_total": 0,
            "samples": [],
            "pairwise_distances": [],
            "anomaly_ranking": [],
            "excluded_samples": [],
        }

    monkeypatch.setattr(audit_mod, "run_dinov2_audit", fake_run)

    audit = write_audit(manifest, out, backend="dinov2", model="fake/dinov2")

    assert audit["backend"] == "dinov2"
    assert audit["model"] == "fake/dinov2"
    assert calls == {"manifest": manifest, "audit_set": "core", "model": "fake/dinov2"}
    assert json.loads(out.read_text()) == audit


def test_write_audit_records_unavailable_dinov2_backend(tmp_path: Path, monkeypatch) -> None:
    manifest = _write_manifest(tmp_path)
    out = tmp_path / "dinov2.json"

    def fake_run(manifest_path, *, audit_set, model):
        raise BackendUnavailable("install torch/transformers")

    monkeypatch.setattr(audit_mod, "run_dinov2_audit", fake_run)

    audit = write_audit(manifest, out, backend="dinov2", model="fake/dinov2")

    assert audit["backend"] == "dinov2"
    assert audit["status"] == "unavailable"
    assert audit["error"] == "install torch/transformers"
    assert audit["samples_total"] == 0
    assert json.loads(out.read_text()) == audit


def test_write_audit_dispatches_siglip_backend(tmp_path: Path, monkeypatch) -> None:
    manifest = _write_manifest(tmp_path)
    out = tmp_path / "siglip.json"
    calls = {}

    def fake_run(manifest_path, *, audit_set, model):
        calls["manifest"] = manifest_path
        calls["audit_set"] = audit_set
        calls["model"] = model
        return {
            "schema_version": "vulca_jepa_text_image_audit.v1",
            "backend": "siglip",
            "status": "ok",
            "model": model,
            "audit_set": audit_set,
            "samples_total": 1,
            "text_image_scores_total": 1,
            "text_image_scores": [{"sample_id": "a", "score": 0.5}],
            "samples": [],
            "excluded_samples": [],
        }

    monkeypatch.setattr(audit_mod, "run_siglip_audit", fake_run)

    audit = write_audit(manifest, out, backend="siglip", model="fake/siglip")

    assert audit["backend"] == "siglip"
    assert audit["text_image_scores_total"] == 1
    assert calls == {"manifest": manifest, "audit_set": "core", "model": "fake/siglip"}
    assert json.loads(out.read_text()) == audit


def test_write_audit_records_unavailable_siglip_backend(tmp_path: Path, monkeypatch) -> None:
    manifest = _write_manifest(tmp_path)
    out = tmp_path / "siglip.json"

    def fake_run(manifest_path, *, audit_set, model):
        raise BackendUnavailable("install torch/transformers")

    monkeypatch.setattr(audit_mod, "run_siglip_audit", fake_run)

    audit = write_audit(manifest, out, backend="siglip", model="fake/siglip")

    assert audit["backend"] == "siglip"
    assert audit["status"] == "unavailable"
    assert audit["error"] == "install torch/transformers"
    assert audit["samples_total"] == 0
    assert json.loads(out.read_text()) == audit
