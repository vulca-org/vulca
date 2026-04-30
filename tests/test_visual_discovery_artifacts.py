from __future__ import annotations

import json


def test_write_discovery_artifacts(tmp_path):
    from vulca.discovery.artifacts import (
        build_brainstorm_handoff,
        write_discovery_artifacts,
    )
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=2)
    result = write_discovery_artifacts(
        root=tmp_path,
        slug="tea",
        title="Premium Tea",
        original_intent=profile.initial_intent,
        profile=profile,
        cards=cards,
        recommended_card_id=cards[0].id,
    )

    assert result["discovery_md"].endswith("discovery.md")
    discovery_dir = tmp_path / "docs" / "visual-specs" / "tea" / "discovery"
    assert (discovery_dir / "discovery.md").exists()
    assert (discovery_dir / "taste_profile.json").exists()
    assert (discovery_dir / "direction_cards.json").exists()

    cards_payload = json.loads((discovery_dir / "direction_cards.json").read_text())
    assert cards_payload["schema_version"] == "0.1"
    assert cards_payload["cards"][0]["id"] == cards[0].id

    handoff = build_brainstorm_handoff(profile, cards[0])
    assert "Ready for /visual-brainstorm" in handoff
    assert "premium tea packaging" in handoff.lower()
