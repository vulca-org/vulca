from __future__ import annotations

import pytest


def _valid_fixture(**overrides):
    from vulca.real_brief.types import Deliverable, RealBriefFixture, SourceInfo

    data = {
        "slug": "valid-fixture",
        "title": "Valid Fixture",
        "source": SourceInfo(
            url="https://example.test/brief",
            retrieved_on="2026-05-01",
            usage_note="Internal benchmark only",
        ),
        "client": "Client exists",
        "context": "Context exists",
        "audience": ["audience"],
        "deliverables": [Deliverable("poster", "print", "campaign")],
        "constraints": ["constraint"],
        "budget": "not specified by source",
        "timeline": "source-specific deadline",
        "required_outputs": ["decision_package", "production_package"],
        "ai_policy": "unspecified",
        "simulation_only": True,
        "risks": ["risk"],
        "avoid": ["avoid"],
        "evaluation_dimensions": ["brief_compliance"],
    }
    data.update(overrides)
    return RealBriefFixture(**data)


def test_safe_slug_accepts_fixture_style_ids():
    from vulca.real_brief.types import safe_slug

    assert safe_slug("seattle-polish-film-festival-poster") == (
        "seattle-polish-film-festival-poster"
    )
    assert safe_slug("gsm-community-market-campaign") == (
        "gsm-community-market-campaign"
    )


@pytest.mark.parametrize(
    "slug",
    [
        "",
        ".",
        "..",
        "../escape",
        "/abs/path",
        "has space",
        "UpperCase",
        "x/y",
        "abc\n",
    ],
)
def test_safe_slug_rejects_unsafe_ids(slug):
    from vulca.real_brief.types import safe_slug

    with pytest.raises(ValueError, match="safe slug"):
        safe_slug(slug)


def test_fixture_validation_rejects_url_without_netloc():
    from vulca.real_brief.types import Deliverable, RealBriefFixture, SourceInfo

    fixture = RealBriefFixture(
        slug="broken-fixture",
        title="Broken Fixture",
        source=SourceInfo(
            url="https://",
            retrieved_on="2026-05-01",
            usage_note="Internal benchmark only",
        ),
        client="Client exists",
        context="Context exists",
        audience=["audience"],
        deliverables=[Deliverable("deliverable", "format", "channel")],
        constraints=["constraint"],
        budget="not specified by source",
        timeline="source-specific deadline",
        required_outputs=["decision_package", "production_package"],
        ai_policy="unspecified",
        simulation_only=True,
        risks=["risk"],
        avoid=["avoid"],
        evaluation_dimensions=["brief_compliance"],
    )

    with pytest.raises(ValueError, match="source.url"):
        fixture.validate()


def test_fixture_validation_accepts_valid_fixture_and_serializes():
    fixture = _valid_fixture()

    fixture.validate()
    payload = fixture.to_dict()

    assert payload["schema_version"] == "0.1"
    assert payload["source"]["retrieved_on"] == "2026-05-01"
    assert payload["deliverables"][0]["name"] == "poster"


def test_fixture_validation_rejects_ai_prohibited_non_simulation_fixture():
    fixture = _valid_fixture(
        ai_policy="prohibited_for_submission",
        simulation_only=False,
    )

    with pytest.raises(ValueError, match="simulation_only"):
        fixture.validate()


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("audience", [""]),
        ("constraints", [" "]),
        ("risks", [""]),
        ("avoid", [""]),
        ("required_outputs", [""]),
        ("evaluation_dimensions", [""]),
    ],
)
def test_fixture_validation_rejects_blank_string_list_entries(field_name, value):
    fixture = _valid_fixture(**{field_name: value})

    with pytest.raises(ValueError, match=field_name):
        fixture.validate()


def test_fixture_validation_rejects_blank_deliverable_fields():
    from vulca.real_brief.types import Deliverable

    fixture = _valid_fixture(deliverables=[Deliverable("", "", "")])

    with pytest.raises(ValueError, match="deliverables"):
        fixture.validate()


def test_fixture_validation_rejects_blank_source_retrieved_on():
    from vulca.real_brief.types import SourceInfo

    fixture = _valid_fixture(
        source=SourceInfo(
            url="https://example.test/brief",
            retrieved_on=" ",
            usage_note="Internal benchmark only",
        )
    )

    with pytest.raises(ValueError, match="retrieved_on"):
        fixture.validate()


def test_fixture_validation_rejects_missing_required_field():
    from vulca.real_brief.types import RealBriefFixture, SourceInfo

    fixture = RealBriefFixture(
        slug="broken-fixture",
        title="Broken Fixture",
        source=SourceInfo(
            url="https://example.test/brief",
            retrieved_on="2026-05-01",
            usage_note="Internal benchmark only",
        ),
        client="",
        context="Context exists",
        audience=["audience"],
        deliverables=[],
        constraints=["constraint"],
        budget="not specified by source",
        timeline="source-specific deadline",
        required_outputs=["decision_package", "production_package"],
        ai_policy="unspecified",
        simulation_only=True,
        risks=["risk"],
        avoid=["avoid"],
        evaluation_dimensions=["brief_compliance"],
    )

    with pytest.raises(ValueError, match="client"):
        fixture.validate()


def test_builtin_fixtures_are_valid_and_ordered():
    from vulca.real_brief.fixtures import build_real_brief_fixtures

    fixtures = build_real_brief_fixtures()

    assert [fixture.slug for fixture in fixtures] == [
        "gsm-community-market-campaign",
        "seattle-polish-film-festival-poster",
        "model-young-package-unpacking-taboo",
        "erie-botanical-gardens-public-art",
        "music-video-treatment-low-budget",
    ]
    for fixture in fixtures:
        fixture.validate()
        payload = fixture.to_dict()
        assert payload["schema_version"] == "0.1"
        assert payload["source"]["retrieved_on"] == "2026-04-30"
        assert payload["source"]["usage_note"] == "Internal benchmark only"
        assert payload["simulation_only"] is True


def test_get_real_brief_fixture_rejects_unknown_slug():
    from vulca.real_brief.fixtures import get_real_brief_fixture

    with pytest.raises(ValueError, match="unknown real brief slug"):
        get_real_brief_fixture("missing-brief")


def test_ai_prohibited_fixture_is_marked_for_internal_simulation_only():
    from vulca.real_brief.fixtures import get_real_brief_fixture

    imageout_like = get_real_brief_fixture("seattle-polish-film-festival-poster")

    assert imageout_like.simulation_only is True
    assert imageout_like.source.usage_note == "Internal benchmark only"
