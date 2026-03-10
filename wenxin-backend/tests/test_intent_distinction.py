"""Test intent/subject semantic distinction in CreateRunRequest."""

from __future__ import annotations

import pytest

from app.prototype.api.schemas import CreateRunRequest


class TestIntentDistinction:
    """Verify intent vs subject field semantics."""

    def test_request_has_intent_field(self):
        """CreateRunRequest accepts optional intent field."""
        req = CreateRunRequest(subject="bamboo painting", intent="express loneliness")
        assert req.intent == "express loneliness"
        assert req.subject == "bamboo painting"

    def test_intent_defaults_to_none(self):
        """When intent is not provided, it defaults to None."""
        req = CreateRunRequest(subject="bamboo painting")
        assert req.intent is None
        assert req.subject == "bamboo painting"

    def test_backward_compat_no_intent(self):
        """Omitting intent keeps the request valid (backward-compatible)."""
        req = CreateRunRequest(subject="lotus")
        # Should be fully valid
        assert req.subject == "lotus"
        assert req.intent is None

    def test_intent_or_subject_fallback(self):
        """When intent is provided, it takes priority; otherwise subject is used."""
        # With intent
        req_with = CreateRunRequest(subject="bamboo", intent="寂寞")
        effective_intent = req_with.intent or req_with.subject
        assert effective_intent == "寂寞"

        # Without intent
        req_without = CreateRunRequest(subject="bamboo")
        effective_intent = req_without.intent or req_without.subject
        assert effective_intent == "bamboo"

    def test_serialization_round_trip(self):
        """Intent field survives JSON round-trip."""
        req = CreateRunRequest(subject="lotus", intent="purity and grace")
        data = req.model_dump()
        assert data["intent"] == "purity and grace"
        assert data["subject"] == "lotus"

        req2 = CreateRunRequest(**data)
        assert req2.intent == "purity and grace"
