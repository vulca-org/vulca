"""SQLAlchemy model for prototype sessions (replaces sessions.jsonl)."""

from sqlalchemy import Column, String, Float, Text, Boolean, Integer, JSON
from app.core.database import Base


class PrototypeSession(Base):
    __tablename__ = "prototype_sessions"

    session_id = Column(String, primary_key=True)
    mode = Column(String, default="create")           # create | evaluate
    intent = Column(Text, default="")
    tradition = Column(String, index=True, default="default")
    subject = Column(Text, default="")
    user_type = Column(String, default="human")        # human | agent
    user_id = Column(String, default="")
    media_type = Column(String, default="image")       # image | video | 3d_model | sound

    # Pipeline results (complex fields as JSON)
    rounds = Column(JSON, default=list)
    final_scores = Column(JSON, default=dict)
    final_weighted_total = Column(Float, default=0.0, index=True)
    best_image_url = Column(Text, default="")
    risk_flags = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    # Feedback & insights
    feedback = Column(JSON, default=list)
    cultural_features = Column(JSON, default=dict)
    critic_insights = Column(JSON, default=list)

    # Implicit feedback signals
    candidate_choice_index = Column(Integer, default=-1)
    time_to_select_ms = Column(Integer, default=0)
    downloaded = Column(Boolean, default=False)

    # Gallery
    published = Column(Boolean, default=False, index=True)
    likes_count = Column(Integer, default=0)

    # Metadata
    total_rounds = Column(Integer, default=0)
    total_latency_ms = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    created_at = Column(Float, index=True)             # Unix timestamp

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "mode": self.mode,
            "intent": self.intent,
            "tradition": self.tradition,
            "subject": self.subject,
            "user_type": self.user_type,
            "user_id": self.user_id,
            "media_type": self.media_type,
            "rounds": self.rounds or [],
            "final_scores": self.final_scores or {},
            "final_weighted_total": self.final_weighted_total or 0.0,
            "best_image_url": self.best_image_url or "",
            "risk_flags": self.risk_flags or [],
            "recommendations": self.recommendations or [],
            "feedback": self.feedback or [],
            "cultural_features": self.cultural_features or {},
            "critic_insights": self.critic_insights or [],
            "candidate_choice_index": self.candidate_choice_index or -1,
            "time_to_select_ms": self.time_to_select_ms or 0,
            "downloaded": self.downloaded or False,
            "published": self.published or False,
            "likes_count": self.likes_count or 0,
            "total_rounds": self.total_rounds or 0,
            "total_latency_ms": self.total_latency_ms or 0,
            "total_cost_usd": self.total_cost_usd or 0.0,
            "created_at": self.created_at or 0.0,
        }
