"""Layer 2b: PreferenceLearner — learn user preferences from feedback.

Learns from thumbs_up/down feedback to build preference profiles.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field

from app.prototype.session.store import SessionStore

logger = logging.getLogger("vulca")


@dataclass
class PreferenceProfile:
    """Learned preference for a tradition or user."""

    key: str  # tradition name or user_id
    preferred_dimensions: list[str] = field(default_factory=list)  # dims that correlate with thumbs_up
    avoided_dimensions: list[str] = field(default_factory=list)  # dims that correlate with thumbs_down
    preferred_traditions: list[str] = field(default_factory=list)
    total_positive: int = 0
    total_negative: int = 0
    negative_comments: list[str] = field(default_factory=list)  # user complaint text
    positive_comments: list[str] = field(default_factory=list)  # user praise text

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "preferred_dimensions": self.preferred_dimensions,
            "avoided_dimensions": self.avoided_dimensions,
            "preferred_traditions": self.preferred_traditions,
            "total_positive": self.total_positive,
            "total_negative": self.total_negative,
        }


class PreferenceLearner:
    """Learn preferences from session feedback data."""

    def __init__(self, store: SessionStore | None = None) -> None:
        self._store = store or SessionStore.get()

    def learn(self) -> dict[str, PreferenceProfile]:
        """Analyze sessions + explicit feedback to build preference profiles."""
        sessions = self._store.get_all()
        if not sessions:
            return {}

        # Group sessions with feedback by tradition
        by_tradition: dict[str, list[dict]] = defaultdict(list)
        for s in sessions:
            if s.get("feedback"):
                by_tradition[s.get("tradition", "default")].append(s)

        # Also ingest explicit feedback from FeedbackStore (POST /feedback)
        self._ingest_explicit_feedback(sessions, by_tradition)

        profiles: dict[str, PreferenceProfile] = {}
        for tradition, sess_list in by_tradition.items():
            profile = PreferenceProfile(key=tradition)

            # Track which dimensions score high in positive vs negative feedback
            pos_dim_scores: dict[str, list[float]] = defaultdict(list)
            neg_dim_scores: dict[str, list[float]] = defaultdict(list)

            for s in sess_list:
                scores = s.get("final_scores", {})
                for fb in s.get("feedback", []):
                    liked = fb.get("liked")
                    rating = fb.get("rating", "")
                    comment = fb.get("comment", "").strip()
                    is_positive = liked is True or rating == "thumbs_up"
                    is_negative = liked is False or rating == "thumbs_down"
                    if is_positive:
                        profile.total_positive += 1
                        if comment:
                            profile.positive_comments.append(comment)
                        for dim, score in scores.items():
                            if isinstance(score, (int, float)):
                                pos_dim_scores[dim].append(score)
                    elif is_negative:
                        profile.total_negative += 1
                        if comment:
                            profile.negative_comments.append(comment)
                        for dim, score in scores.items():
                            if isinstance(score, (int, float)):
                                neg_dim_scores[dim].append(score)

            # Implicit feedback signals (WU-10)
            for s in sess_list:
                scores = s.get("final_scores", {})

                # Downloaded = implicit positive
                if s.get("downloaded", False):
                    profile.total_positive += 1
                    for dim, score in scores.items():
                        if isinstance(score, (int, float)):
                            pos_dim_scores[dim].append(score)

                # Fast selection (< 5s) = strong preference signal
                time_ms = s.get("time_to_select_ms", 0)
                if time_ms > 0 and time_ms < 5000:
                    profile.total_positive += 1
                    for dim, score in scores.items():
                        if isinstance(score, (int, float)):
                            pos_dim_scores[dim].append(score * 1.1)  # slight boost for fast picks

                # Slow selection (> 30s) = indecision, slight negative signal
                elif time_ms > 30000:
                    profile.total_negative += 1
                    for dim, score in scores.items():
                        if isinstance(score, (int, float)):
                            neg_dim_scores[dim].append(score)

            # Find dimensions that are higher in positive-rated sessions
            MIN_SAMPLES = 3
            for dim in set(pos_dim_scores) | set(neg_dim_scores):
                pos_list = pos_dim_scores.get(dim, [])
                neg_list = neg_dim_scores.get(dim, [])
                if len(pos_list) + len(neg_list) < MIN_SAMPLES:
                    continue
                pos_avg = sum(pos_list) / len(pos_list) if pos_list else 0.0
                neg_avg = sum(neg_list) / len(neg_list) if neg_list else 0.0
                if pos_avg > neg_avg + 0.1:
                    profile.preferred_dimensions.append(dim)
                elif neg_avg > pos_avg + 0.1:
                    profile.avoided_dimensions.append(dim)

            profiles[tradition] = profile

        return profiles

    def _ingest_explicit_feedback(
        self,
        sessions: list[dict],
        by_tradition: dict[str, list[dict]],
    ) -> None:
        """Merge explicit feedback (POST /feedback → feedback.jsonl) into session groups.

        For each feedback record, find the matching session and inject the
        feedback if not already present. This bridges the gap between
        FeedbackStore (explicit) and SessionStore (implicit) feedback.
        """
        try:
            from app.prototype.feedback.feedback_store import FeedbackStore
            fb_store = FeedbackStore.get()
            records = fb_store.get_recent(limit=200)
        except Exception:
            return

        if not records:
            return

        # Build session lookup by ID
        session_by_id: dict[str, dict] = {}
        for s in sessions:
            sid = s.get("session_id", "")
            if sid:
                session_by_id[sid] = s

        for record in records:
            eid = record.evaluation_id
            if not eid:
                continue
            session = session_by_id.get(eid)
            if not session:
                continue

            tradition = record.tradition or session.get("tradition", "default")

            # Inject feedback into session if not already there
            existing_fb = session.get("feedback") or []
            if isinstance(existing_fb, dict):
                existing_fb = [existing_fb]

            # Check if this feedback is already present
            already = any(
                fb.get("rating") == record.rating and fb.get("comment") == record.comment
                for fb in existing_fb
                if isinstance(fb, dict)
            )
            if not already:
                new_fb = {
                    "liked": record.rating == "thumbs_up",
                    "rating": record.rating,
                    "comment": record.comment,
                }
                existing_fb.append(new_fb)
                session["feedback"] = existing_fb

                # Ensure this session is in the tradition group
                if session not in by_tradition.get(tradition, []):
                    by_tradition[tradition].append(session)
