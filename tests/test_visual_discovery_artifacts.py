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
    cards = generate_direction_cards(profile, count=3)
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
    assert "sketch_prompts_json" not in result

    cards_payload = json.loads((discovery_dir / "direction_cards.json").read_text())
    assert cards_payload["schema_version"] == "0.1"
    assert cards_payload["cards"][0]["id"] == cards[0].id

    handoff = build_brainstorm_handoff(profile, cards[0])
    assert "Ready for /visual-brainstorm" in handoff
    assert "premium tea packaging" in handoff.lower()
    assert "traditions: chinese_xieyi" in handoff
    assert "output: static 2D visual brief" in handoff


def test_write_discovery_artifacts_rejects_invalid_recommended_card(tmp_path):
    import pytest

    from vulca.discovery.artifacts import write_discovery_artifacts
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=3)

    with pytest.raises(ValueError, match="recommended_card_id"):
        write_discovery_artifacts(
            root=tmp_path,
            slug="tea",
            title="Premium Tea",
            original_intent=profile.initial_intent,
            profile=profile,
            cards=cards,
            recommended_card_id="missing-card",
        )


def test_write_discovery_artifacts_rejects_unsafe_slug(tmp_path):
    import pytest

    from vulca.discovery.artifacts import write_discovery_artifacts
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=3)

    with pytest.raises(ValueError, match="slug"):
        write_discovery_artifacts(
            root=tmp_path,
            slug="../outside",
            title="Premium Tea",
            original_intent=profile.initial_intent,
            profile=profile,
            cards=cards,
            recommended_card_id=cards[0].id,
        )


def test_write_discovery_artifacts_can_write_sketch_prompts(tmp_path):
    import json

    from vulca.discovery.artifacts import write_discovery_artifacts
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile
    from vulca.discovery.types import SketchPrompt

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=3)
    sketch = SketchPrompt(
        card_id=cards[0].id,
        provider="mock",
        model="",
        prompt="mock sketch record",
        negative_prompt="busy ornament",
        size="1024x1024",
        purpose="thumbnail exploration",
    )

    result = write_discovery_artifacts(
        root=tmp_path,
        slug="tea",
        title="Premium Tea",
        original_intent=profile.initial_intent,
        profile=profile,
        cards=cards,
        recommended_card_id=cards[0].id,
        sketch_prompts=[sketch],
    )

    payload = json.loads(
        (tmp_path / "docs" / "visual-specs" / "tea" / "discovery" / "sketch_prompts.json")
        .read_text(encoding="utf-8")
    )

    assert result["sketch_prompts_json"].endswith("sketch_prompts.json")
    assert payload["sketch_prompts"][0]["card_id"] == cards[0].id
