from __future__ import annotations

import pytest


def _assert_ordered(text, expected_parts):
    cursor = -1
    for part in expected_parts:
        next_cursor = text.find(part, cursor + 1)
        assert next_cursor != -1, f"missing or out of order: {part!r}"
        cursor = next_cursor


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


def test_builtin_fixtures_include_expected_source_deadlines():
    from vulca.real_brief.fixtures import build_real_brief_fixtures

    expected_deadlines = {
        "gsm-community-market-campaign": "2026-03-13 17:00",
        "seattle-polish-film-festival-poster": "2026-06-01 23:59",
        "model-young-package-unpacking-taboo": "2026-04-17",
        "erie-botanical-gardens-public-art": "2026-04-20 12:00",
        "music-video-treatment-low-budget": "2026-01-31",
    }
    fixtures_by_slug = {
        fixture.slug: fixture for fixture in build_real_brief_fixtures()
    }

    assert {
        slug: fixtures_by_slug[slug].source.deadline
        for slug in expected_deadlines
    } == expected_deadlines


def test_get_real_brief_fixture_rejects_unknown_slug():
    from vulca.real_brief.fixtures import get_real_brief_fixture

    with pytest.raises(ValueError, match="unknown real brief slug"):
        get_real_brief_fixture("missing-brief")


def test_seattle_fixture_is_marked_for_internal_simulation_only():
    from vulca.real_brief.fixtures import get_real_brief_fixture

    seattle = get_real_brief_fixture("seattle-polish-film-festival-poster")

    assert seattle.simulation_only is True
    assert seattle.source.usage_note == "Internal benchmark only"


def test_build_real_brief_conditions_a_through_d():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("seattle-polish-film-festival-poster")
    conditions = build_real_brief_conditions(fixture)

    assert [condition["id"] for condition in conditions] == ["A", "B", "C", "D"]
    assert conditions[0]["label"] == "One-shot model baseline"
    assert "Raw real brief" in conditions[0]["purpose"]
    assert "Required deliverables" in conditions[1]["prompt"]
    assert "Missing questions" in conditions[2]["prompt"]
    assert "Preview plan" in conditions[3]["prompt"]
    assert conditions[3]["workflow_stage"] == "vulca-preview-iterate"


def test_condition_generation_preserves_fixture_constraints():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("gsm-community-market-campaign")
    conditions = build_real_brief_conditions(fixture)
    joined = "\n".join(condition["prompt"] for condition in conditions)

    assert "Canva-editable" in joined
    assert "real photography" in joined
    assert "19-week" in joined
    assert "clip art" in joined


def test_brief_digest_matches_task_three_field_contract():
    from vulca.real_brief.conditions import brief_digest
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("seattle-polish-film-festival-poster")
    digest = brief_digest(fixture)

    for label in [
        "Client:",
        "Context:",
        "Audience:",
        "Required deliverables:",
        "Constraints:",
        "Budget:",
        "Timeline:",
        "Risks:",
        "Avoid:",
        "AI policy:",
        "Simulation only:",
    ]:
        assert label in digest

    assert "poster concept (11 x 17 in vertical, print/digital)" in digest
    assert "program cover adaptation (same key art, print)" in digest
    assert "Brief:" not in digest
    assert "Source brief:" not in digest
    assert "Source deadline:" not in digest
    assert "Required outputs:" not in digest
    assert "simulation_only:" not in digest


def test_condition_prompts_match_task_three_contract_phrases():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("seattle-polish-film-festival-poster")
    conditions = build_real_brief_conditions(fixture)

    assert (
        conditions[0]["purpose"]
        == "Raw real brief condensed into a single model ask."
    )
    _assert_ordered(
        conditions[0]["prompt"],
        [
            "Create the requested creative output for this real brief.",
            "Client: Seattle Polish Film Festival",
            "Return a polished concept and any visual prompt needed to generate it.",
        ],
    )

    assert (
        conditions[1]["purpose"]
        == "Same brief normalized into structured client, deliverable, and constraint fields."
    )
    _assert_ordered(
        conditions[1]["prompt"],
        [
            "Create a direction from the structured brief below.",
            "Client: Seattle Polish Film Festival",
            "Success criteria:",
            "- satisfy required deliverables",
            "- respect every listed constraint",
            "- identify the most production-relevant risk",
        ],
    )

    assert conditions[2]["prompt"].startswith(
        "Build a Vulca planning package before generating final pixels."
    )
    _assert_ordered(
        conditions[2]["prompt"],
        [
            "Missing questions:",
            "- Which stakeholder approves the final direction?",
            "- Which deliverable must be most production-ready first?",
            "- Which source assets already exist?",
            "Selected direction card:",
            "Direction summary:",
            "Visual operations:",
            "Evaluation focus:",
            "Generated direction set for comparison:",
        ],
    )

    assert conditions[3]["prompt"].startswith(
        "Build a Vulca preview-and-iterate package for this brief."
    )
    _assert_ordered(
        conditions[3]["prompt"],
        [
            "Preview plan:",
            "- produce 2-3 low-cost thumbnail directions before final comp",
            "- critique each direction against constraints and risks",
            "- refine the strongest direction into a final comp prompt",
            "- document editability, redraw, and reuse notes",
        ],
    )
    assert (
        "produce 2-3 low-cost thumbnail directions before final comp"
        in conditions[3]["prompt"]
    )
    assert (
        "critique each direction against constraints and risks"
        in conditions[3]["prompt"]
    )
    assert (
        "refine the strongest direction into a final comp prompt"
        in conditions[3]["prompt"]
    )
    assert (
        "document editability, redraw, and reuse notes"
        in conditions[3]["prompt"]
    )


def test_vulca_condition_prompts_include_generated_direction_set():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("seattle-polish-film-festival-poster")
    conditions = build_real_brief_conditions(fixture)
    condition_c_prompt = conditions[2]["prompt"]
    condition_d_prompt = conditions[3]["prompt"]

    for prompt in [condition_c_prompt, condition_d_prompt]:
        assert "Generated direction set for comparison:" in prompt
        assert prompt.count("Direction ") >= 3
        assert prompt.count(f"{fixture.slug}-") >= 3


def test_preview_iterate_prompt_has_concrete_iteration_sections():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("gsm-community-market-campaign")
    prompt = build_real_brief_conditions(fixture)[3]["prompt"]

    for section in [
        "Preview prompts:",
        "Critique criteria:",
        "Refinement notes:",
        "Editability, redraw, and reuse notes:",
    ]:
        assert section in prompt

    assert "thumbnail" in prompt
    assert "required deliverables" in prompt
    assert "constraints" in prompt
    assert "risks" in prompt
    assert "Canva-editable" in prompt
