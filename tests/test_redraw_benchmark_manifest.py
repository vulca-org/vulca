import json
from pathlib import Path

from vulca.layers.redraw_cases import FAILURE_TYPES, PREFERRED_ACTIONS


ROOT = Path(__file__).resolve().parent.parent


def test_redraw_failure_taxonomy_matches_seed_manifest():
    taxonomy_path = ROOT / "docs" / "benchmarks" / "redraw" / "failure_taxonomy.json"
    manifest_path = ROOT / "docs" / "benchmarks" / "redraw" / "seed_manifest.json"

    taxonomy = json.loads(taxonomy_path.read_text())
    manifest = json.loads(manifest_path.read_text())

    taxonomy_failure_types = set(taxonomy["failure_types"])
    taxonomy_preferred_actions = set(taxonomy["preferred_actions"])
    expected_preferred_actions = PREFERRED_ACTIONS - {""}

    assert taxonomy_failure_types == FAILURE_TYPES
    assert len(taxonomy["failure_types"]) == len(FAILURE_TYPES)
    assert taxonomy_preferred_actions == expected_preferred_actions
    assert len(taxonomy["preferred_actions"]) == len(expected_preferred_actions)
    assert manifest["case_type"] == "redraw_case_seed"
    assert manifest["schema_version"] == 1
    assert manifest["items"]
    root = ROOT.resolve()
    for item in manifest["items"]:
        assert item["failure_type"] in taxonomy_failure_types
        assert item["preferred_action"] in taxonomy_preferred_actions
        source_artifact = Path(item["source_artifact"])
        assert not source_artifact.is_absolute(), item["source_artifact"]
        artifact = (ROOT / source_artifact).resolve()
        assert artifact.is_relative_to(root), item["source_artifact"]
        assert artifact.is_file(), item["source_artifact"]
