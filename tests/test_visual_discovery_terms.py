from __future__ import annotations


def test_expand_liubai_from_chinese_xieyi_registry():
    from vulca.discovery.terms import expand_terms

    expansions = expand_terms("chinese_xieyi", ["liubai"])

    assert len(expansions) == 1
    payload = expansions[0]
    assert payload["term"] == "reserved white space"
    assert payload["term_zh"] == "留白"
    assert "large negative space" in payload["visual_ops"]["composition"]
    assert "generic minimalism unrelated to subject" in payload["visual_ops"]["avoid"]
    assert payload["evaluation_focus"]["L5"] != ""


def test_expand_unknown_term_returns_operational_fallback():
    from vulca.discovery.terms import expand_terms

    expansions = expand_terms("brand_design", ["quiet luxury"])

    assert expansions[0]["term"] == "quiet luxury"
    assert expansions[0]["visual_ops"]["composition"] != ""
    assert "generic ai aesthetic" in expansions[0]["visual_ops"]["avoid"]


def test_extract_terms_from_intent_uses_registry_aliases():
    from vulca.discovery.terms import extract_terms_from_intent

    terms = extract_terms_from_intent(
        "premium tea packaging with liu bai and ink atmosphere",
        tradition="chinese_xieyi",
    )

    assert "reserved white space" in terms
