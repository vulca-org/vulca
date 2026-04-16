import re

from vulca.layers.prompt import build_analyze_prompt


def test_analyze_prompt_documents_semantic_path():
    p = build_analyze_prompt()
    assert "semantic_path" in p


def test_analyze_prompt_mentions_high_layer_ceiling():
    p = build_analyze_prompt()
    m = re.search(r"(\d+)\s*-\s*(\d+)\s+layers", p, re.I)
    assert m is not None, f"layer range not found: {p[:200]}"
    assert int(m.group(2)) >= 12
