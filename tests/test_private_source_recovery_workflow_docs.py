from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/benchmarks/learning/private_source_recovery_workflow.md"


def test_private_source_recovery_workflow_doc_is_safe_and_actionable():
    text = DOC.read_text(encoding="utf-8")

    assert "scripts/real_source_context_recovery_eval.py" in text
    assert "--max-recovered-source-context-gaps 0" in text
    assert "--min-fallback-agent-reduction 2" in text
    assert "--min-recovered-eval-cases 2" in text
    assert "no_source_context_for_required_source" in text
    assert "private asset maps" in text
    assert "/Users/" not in text
    assert "private://local_path" not in text
