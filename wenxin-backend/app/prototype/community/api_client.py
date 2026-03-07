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

        The feedback endpoint is provided by WU-08.  If it is not yet
        deployed the caller will receive an ``httpx.HTTPStatusError``.

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
