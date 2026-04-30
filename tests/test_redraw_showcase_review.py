import json
from pathlib import Path

from scripts.build_redraw_review import build_html, payload_from_summary, write_review_html


def _path(tmp_path: Path, name: str) -> str:
    p = tmp_path / name
    p.write_text("fake image bytes")
    return str(p)


def test_payload_from_summary_prefers_final_source_pasteback(tmp_path):
    summary = {
        "layer_path": _path(tmp_path, "layer.png"),
        "final_source_pasteback_path": _path(tmp_path, "final_on_source.png"),
        "quality_gate_passed": True,
        "refinement": {"applied": True, "child_count_prepared": 4},
    }

    payload = payload_from_summary(summary)

    assert payload["file"].endswith("layer.png")
    assert payload["source_pasteback_path"].endswith("final_on_source.png")
    assert payload["quality_gate_passed"] is True
    assert payload["refinement_applied"] is True
    assert payload["refined_child_count"] == 4


def test_payload_from_summary_uses_last_succeeded_child_when_no_final(tmp_path):
    summary = {
        "layer_path": _path(tmp_path, "layer.png"),
        "children": [
            {
                "index": 1,
                "status": "succeeded",
                "source_pasteback_path": _path(tmp_path, "child_01_on_source.png"),
            },
            {
                "index": 2,
                "status": "succeeded",
                "source_pasteback_path": _path(tmp_path, "child_02_on_source.png"),
            },
            {
                "index": 3,
                "status": "prepared_waiting_for_api_key",
                "source_pasteback_path": _path(tmp_path, "child_03_on_source.png"),
            },
        ],
    }

    payload = payload_from_summary(summary)

    assert payload["source_pasteback_path"].endswith("child_02_on_source.png")
    assert "quality_gate_passed" not in payload


def test_payload_from_summary_copies_quality_failures(tmp_path):
    summary = {
        "layer_path": _path(tmp_path, "layer.png"),
        "source_pasteback_path": _path(tmp_path, "after.png"),
        "quality_gate_passed": False,
        "quality_failures": ["background_bleed", "edge_halo"],
    }

    payload = payload_from_summary(summary)

    assert payload["quality_gate_passed"] is False
    assert payload["quality_failures"] == ["background_bleed", "edge_halo"]


def test_build_html_shows_source_pasteback_as_after_image(tmp_path):
    summary = {
        "status": "completed",
        "prompt": "Make the flower cluster a storybook botanical accent.",
        "source_path": _path(tmp_path, "source.png"),
        "layer_path": _path(tmp_path, "layer.png"),
        "final_source_pasteback_path": _path(tmp_path, "final_on_source.png"),
        "quality_gate_passed": True,
        "children": [
            {
                "index": 1,
                "status": "succeeded",
                "input_path": _path(tmp_path, "child_01_input.png"),
                "mask_path": _path(tmp_path, "child_01_mask.png"),
                "source_pasteback_path": _path(tmp_path, "child_01_on_source.png"),
                "cost_usd": 0.061,
            }
        ],
    }
    output_path = tmp_path / "review.html"

    html = build_html(summary, output_path)

    assert "Ready for review" in html
    assert "final_on_source.png" in html
    assert "layer.png" in html
    assert "Make the flower cluster" in html
    assert "child_01_on_source.png" in html


def test_build_html_does_not_show_layer_as_main_after_when_source_pasteback_missing(tmp_path):
    summary = {
        "status": "completed",
        "prompt": "Make the flower cluster a storybook botanical accent.",
        "source_path": _path(tmp_path, "source.png"),
        "layer_path": _path(tmp_path, "transparent_layer.png"),
        "quality_gate_passed": True,
        "children": [],
    }
    output_path = tmp_path / "review.html"

    html = build_html(summary, output_path)

    assert "Layer-only result" in html
    assert "source_pasteback_path_missing" in html
    assert "After: source pasteback" not in html
    assert 'alt="source pasteback result"' not in html
    assert '<code>transparent_layer.png</code>' in html


def test_build_html_does_not_show_layer_as_main_after_when_source_pasteback_errors(tmp_path):
    summary = {
        "status": "completed",
        "prompt": "Make the flower cluster a storybook botanical accent.",
        "source_path": _path(tmp_path, "source.png"),
        "layer_path": _path(tmp_path, "transparent_layer.png"),
        "source_pasteback_error": "mask was outside source bounds",
        "children": [],
    }
    output_path = tmp_path / "review.html"

    html = build_html(summary, output_path)

    assert "Pasteback warning" in html
    assert "mask was outside source bounds" in html
    assert "After: source pasteback" not in html
    assert 'alt="source pasteback result"' not in html
    assert '<code>transparent_layer.png</code>' in html


def test_write_review_html_creates_file(tmp_path):
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "review.html"
    summary_path.write_text(
        json.dumps(
            {
                "source_path": _path(tmp_path, "source.png"),
                "layer_path": _path(tmp_path, "layer.png"),
                "source_pasteback_path": _path(tmp_path, "after.png"),
                "quality_gate_passed": True,
                "children": [],
            }
        )
    )

    result = write_review_html(summary_path, output_path)

    assert result == output_path
    assert output_path.exists()
    assert "after.png" in output_path.read_text()
