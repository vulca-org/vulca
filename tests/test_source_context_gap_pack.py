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
SCRIPT = ROOT / "scripts" / "source_context_gap_pack.py"


def test_source_context_gap_pack_prioritizes_remaining_v3_router_gaps(tmp_path):
    from vulca.learning.source_context_gap_pack import run_source_context_gap_pack

    report = run_source_context_gap_pack(
        repo_root=ROOT,
        output_dir=tmp_path / "gap_pack",
        report_path=tmp_path / "source_context_gap_pack_report.json",
    )

    assert report["case_type"] == "learning_source_context_gap_pack_report"
    assert report["status"] == "needs_source_context_gap_pack"
    assert report["summary"] == {
        "remaining_gap_count": 3,
        "source_context_gap_closable_count": 3,
        "tiny_model_dispatch_recoverable_count": 2,
        "still_agent_required_after_source_context_count": 1,
    }
    assert report["counts_by_case_type"] == {
        "layer_generate_case": 3,
    }
    assert report["counts_by_source_kind"] == {
        "local_seed": 1,
        "user_case_log": 2,
    }
    assert report["counts_by_gap_task"] == {
        "recover_real_user_source_context": 2,
        "review_seed_source_dependency": 1,
    }
    assert report["counts_by_secondary_blocker"] == {
        "low_action_confidence": 1,
        "source_context_only": 2,
    }

    groups = {item["gap_task"]: item for item in report["gap_groups"]}
    assert groups["recover_real_user_source_context"]["priority"] == "p0"
    assert groups["recover_real_user_source_context"]["case_count"] == 2
    assert "author_synthetic_source_packet" not in groups

    real_cases = [
        item
        for item in report["gap_cases"]
        if item["gap_task"] == "recover_real_user_source_context"
    ]
    assert [item["case_id"] for item in real_cases] == [
        "real_v1_winter_solstice_tang_mural_registry_gap",
        "real_v2_layer_tang_mural_prompt_ambiguity",
    ]
    assert all(item["priority"] == "p0" for item in real_cases)
    assert all(
        item["expected_effect"] == "remove_source_context_fallback"
        for item in real_cases
    )

    assert Path(report["artifacts"]["training_effectiveness_report_path"]).exists()
    assert Path(report["artifacts"]["report_path"]).exists()
    encoded = json.dumps(report, sort_keys=True)
    assert "private://local_path" not in encoded
    assert "/Users/" not in encoded


def test_source_context_gap_pack_cli_writes_summary(tmp_path):
    output_dir = tmp_path / "gap_pack"
    report_path = tmp_path / "source_context_gap_pack_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        timeout=45,
        env=CLI_ENV,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    assert "Source context gap pack report:" in result.stdout
    assert "Remaining source-context gaps: 3" in result.stdout
    assert "Tiny-model dispatch recoverable after source context: 2" in result.stdout
    assert "Gap task recover_real_user_source_context: 2" in result.stdout
    assert "Gap task author_synthetic_source_packet:" not in result.stdout

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["remaining_gap_count"] == 3
