"""Basic tests for ComfyUI VULCA nodes (no ComfyUI runtime required)."""
from __future__ import annotations

import sys
import os
import pytest

# Add vulca to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "vulca", "src"))


def test_node_mappings():
    from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    assert "VULCABrief" in NODE_CLASS_MAPPINGS
    assert "VULCAConcept" in NODE_CLASS_MAPPINGS
    assert "VULCAEvaluate" in NODE_CLASS_MAPPINGS
    assert "VULCAGenerate" in NODE_CLASS_MAPPINGS
    assert "VULCAUpdate" in NODE_CLASS_MAPPINGS
    assert len(NODE_CLASS_MAPPINGS) == 5
    assert len(NODE_DISPLAY_NAME_MAPPINGS) == 5


def test_brief_node_input_types():
    from nodes import VULCABriefNode
    inputs = VULCABriefNode.INPUT_TYPES()
    assert "required" in inputs
    assert "intent" in inputs["required"]


def test_evaluate_node_return_types():
    from nodes import VULCAEvaluateNode
    assert len(VULCAEvaluateNode.RETURN_TYPES) == 6  # scores_json + L1-L5


def test_brief_node_creates_brief(tmp_path):
    os.environ["VULCA_PROJECT_DIR"] = str(tmp_path)
    from nodes import VULCABriefNode
    node = VULCABriefNode()
    result = node.create_brief("水墨山水", mood="serene")
    assert result[0]  # brief_path
    assert (tmp_path / "brief.yaml").exists()
    del os.environ["VULCA_PROJECT_DIR"]


def test_evaluate_node_mock():
    from nodes import VULCAEvaluateNode
    node = VULCAEvaluateNode()
    result = node.evaluate("nonexistent.jpg", mock=True)
    scores_json, l1, l2, l3, l4, l5 = result
    assert isinstance(l1, float)
    assert isinstance(l5, float)
