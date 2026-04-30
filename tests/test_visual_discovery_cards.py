from __future__ import annotations


def test_infer_profile_detects_packaging_and_xieyi_terms():
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )

    payload = profile.to_dict()
    assert payload["domain"]["primary"] == "packaging"
    assert "chinese_xieyi" in payload["culture"]["candidate_traditions"]
    assert "reserved white space" in payload["culture"]["terms"]


def test_generate_direction_cards_returns_operational_cards():
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=3)

    assert len(cards) == 3
    assert cards[0].provider_hint["final"].provider == "openai"
    assert cards[0].provider_hint["final"].model == "gpt-image-2"
    assert cards[0].visual_ops.composition != ""
    assert cards[0].evaluation_focus.L5 != ""
    assert cards[0].status == "candidate"


def test_generate_direction_cards_clamps_to_three_to_five_cards():
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )

    assert len(generate_direction_cards(profile, count=1)) == 3
    assert len(generate_direction_cards(profile, count=8)) == 5
