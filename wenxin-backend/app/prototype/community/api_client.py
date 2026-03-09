"""Async HTTP client for the VULCA REST API.

Wraps ``/api/v1/evaluate`` and ``/api/v1/feedback`` endpoints so that
community agents can interact with the platform using the same contract
as real browser / CLI users.

Dependencies WU-01 (intent-based evaluate) and WU-08 (feedback) may not
be deployed yet; this client will surface the HTTP error transparently.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = os.environ.get("VULCA_API_URL", "http://localhost:8001")
_DEFAULT_API_KEY = os.environ.get("VULCA_API_KEY", "")


@dataclass
class VulcaAPIClient:
    """Thin async wrapper around the public VULCA REST API."""

    base_url: str = field(default_factory=lambda: _DEFAULT_BASE_URL)
    api_key: str = field(default_factory=lambda: _DEFAULT_API_KEY)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def evaluate(
        self,
        image_url: str,
        intent: str = "",
        tradition: str = "default",
    ) -> dict:
        """Call POST /api/v1/evaluate and return the JSON response.

        Parameters
        ----------
        image_url:
            HTTP(S) URL of the image to evaluate.
        intent:
            Free-text user intent (consumed by WU-01 Intent Layer when available).
        tradition:
            Cultural tradition identifier, e.g. ``"chinese_xieyi"``.
        """
        body: dict = {
            "image_url": image_url,
            "tradition": tradition,
        }
        if intent:
            body["intent"] = intent

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/api/v1/evaluate",
                json=body,
                headers=self._auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def submit_feedback(
        self,
        evaluation_id: str,
        rating: str,
        comment: str = "",
        feedback_type: str = "implicit",
    ) -> dict:
        """Call POST /api/v1/feedback and return the JSON response.

        Parameters
        ----------
        evaluation_id:
            Identifier of the evaluation to attach feedback to.
        rating:
            ``"thumbs_up"`` or ``"thumbs_down"``.
        comment:
            Optional free-text comment.
        feedback_type:
            ``"implicit"`` (automated) or ``"explicit"`` (human).
        """
        body: dict = {
            "evaluation_id": evaluation_id,
            "rating": rating,
            "comment": comment,
            "feedback_type": feedback_type,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/api/v1/feedback",
                json=body,
                headers=self._auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Unified Create API
    # ------------------------------------------------------------------

    async def create_session(
        self,
        intent: str,
        tradition: str = "default",
        subject: str = "",
        provider: str = "nb2",
        user_type: str = "human",
    ) -> dict:
        """Call POST /api/v1/create (synchronous mode) and return the JSON response.

        Falls back to POST /api/v1/evaluate/nocode if /create is unavailable.
        """
        body: dict = {
            "intent": intent,
            "tradition": tradition,
            "subject": subject or intent,
            "provider": provider,
            "stream": False,
            "user_type": user_type,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/v1/create",
                    json=body,
                    headers=self._auth_headers(),
                )
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.ConnectError) as exc:
                logger.warning("POST /create failed: %s", exc)
                # Return a minimal error response instead of falling back
                # to evaluate/nocode which produces non-homogeneous sessions
                return {
                    "session_id": "",
                    "mode": "create",
                    "tradition": tradition,
                    "error": str(exc),
                    "best_candidate_id": "",
                    "total_rounds": 0,
                }

    # ------------------------------------------------------------------
    # Skills API
    # ------------------------------------------------------------------

    async def get_skills(self) -> list[dict]:
        """Call GET /api/v1/skills and return the list of skills."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/api/v1/skills",
                headers=self._auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def create_skill(self, payload: dict) -> dict:
        """Call POST /api/v1/skills to create a new skill.

        Parameters
        ----------
        payload:
            Dict with keys ``name``, ``description``, ``tags``, etc.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/api/v1/skills",
                json=payload,
                headers=self._auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def post_discussion(self, skill_id: str, comment: str) -> dict:
        """Call POST /api/v1/skills/{skill_id}/discussions.

        Parameters
        ----------
        skill_id:
            The skill to comment on.
        comment:
            Comment body text.
        """
        body = {"content": comment, "author": "agent"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/api/v1/skills/{skill_id}/discussions",
                json=body,
                headers=self._auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()
