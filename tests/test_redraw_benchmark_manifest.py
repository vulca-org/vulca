import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_redraw_failure_taxonomy_matches_seed_manifest():
    taxonomy_path = ROOT / "docs" / "benchmarks" / "redraw" / "failure_taxonomy.json"
    manifest_path = ROOT / "docs" / "benchmarks" / "redraw" / "seed_manifest.json"

    taxonomy = json.loads(taxonomy_path.read_text())
    manifest = json.loads(manifest_path.read_text())

    allowed = set(taxonomy["failure_types"])
    assert "mask_too_broad" in allowed
    assert manifest["case_type"] == "redraw_case_seed"
    assert manifest["schema_version"] == 1
    assert manifest["items"]
    for item in manifest["items"]:
        assert item["failure_type"] in allowed
        artifact = ROOT / item["source_artifact"]
        assert artifact.exists(), item["source_artifact"]
