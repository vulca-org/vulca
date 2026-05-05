import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_build_local_seed_cases_uses_tracked_repo_artifacts():
    from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST, build_local_seed_cases

    bundle = build_local_seed_cases(ROOT, DEFAULT_SEED_MANIFEST)

    assert len(bundle["redraw_case"]) == 6
    assert len(bundle["decompose_case"]) == 1
    assert len(bundle["layer_generate_case"]) == 5

    redraw = bundle["redraw_case"][0]
    assert redraw["case_type"] == "redraw_case"
    assert redraw["review"]["failure_type"] == "color_drift"
    assert redraw["review"]["preferred_action"] == "adjust_mask"
    assert redraw["artifacts"]["source_layer_path"].startswith("docs/")

    decompose = bundle["decompose_case"][0]
    assert decompose["case_type"] == "decompose_case"
    assert decompose["review"]["human_accept"] is True
    assert decompose["review"]["preferred_action"] == "accept"
    assert decompose["output"]["layers"]

    layer_generate = bundle["layer_generate_case"][0]
    assert layer_generate["case_type"] == "layer_generate_case"
    assert layer_generate["review"]["human_accept"] is True
    assert layer_generate["review"]["preferred_action"] == "accept"
    assert layer_generate["outputs"]["layers"]
    assert {item["status"] for item in layer_generate["outputs"]["layers"]} == {"accepted"}
    assert {
        item["outputs"]["artifact_dir"]
        for item in bundle["layer_generate_case"]
    } == {
        "assets/demo/v2/layers-extract",
        "assets/demo/v2/scenario1",
        "assets/demo/v2/scenario1-redo",
        "assets/showcase/layers/great-wave",
        "assets/showcase/layers_v2/nighthawks",
    }


def test_write_local_seed_case_logs_creates_reviewable_jsonl(tmp_path):
    from vulca.learning.case_review import review_case_log
    from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST, write_local_seed_case_logs

    result = write_local_seed_case_logs(
        repo_root=ROOT,
        output_dir=tmp_path,
        manifest_path=DEFAULT_SEED_MANIFEST,
    )

    assert result.counts == {
        "redraw_case": 6,
        "decompose_case": 1,
        "layer_generate_case": 5,
    }
    assert set(result.paths) == {
        "redraw_case",
        "decompose_case",
        "layer_generate_case",
    }
    assert (tmp_path / "seed_index.json").exists()

    decompose_cases = _read_jsonl(Path(result.paths["decompose_case"]))
    review_case_log(
        result.paths["decompose_case"],
        case_id=decompose_cases[0]["case_id"],
        output_path=tmp_path / "decompose.reviewed.jsonl",
        failure_type="under_split",
        preferred_action="adjust_hints",
        reviewed_at="2026-05-05T14:30:00Z",
    )
    reviewed = _read_jsonl(tmp_path / "decompose.reviewed.jsonl")
    assert reviewed[0]["review"]["failure_type"] == "under_split"
    assert reviewed[0]["review"]["preferred_action"] == "adjust_hints"


def test_cases_seed_cli_writes_seed_logs(tmp_path):
    output_dir = tmp_path / "seed-output"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vulca.cli",
            "cases",
            "seed",
            "--repo-root",
            str(ROOT),
            "--output",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert "redraw_case: 6" in result.stdout
    assert "decompose_case: 1" in result.stdout
    assert "layer_generate_case: 5" in result.stdout
    assert (output_dir / "redraw_cases.seed.jsonl").exists()
    assert (output_dir / "decompose_cases.seed.jsonl").exists()
    assert (output_dir / "layer_generate_cases.seed.jsonl").exists()

    decompose_cases = _read_jsonl(output_dir / "decompose_cases.seed.jsonl")
    assert decompose_cases[0]["output"]["layers"]
