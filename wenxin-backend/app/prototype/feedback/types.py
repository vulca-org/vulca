"""Pydantic v2 schemas for the feedback system."""

from pydantic import BaseModel, Field


class FeedbackSubmit(BaseModel):
    evaluation_id: str
    rating: str = Field(description="thumbs_up or thumbs_down")
    comment: str = ""
    feedback_type: str = Field(
        default="explicit",
        description="implicit|explicit|knowledge|create",
    )


class FeedbackRecord(BaseModel):
    id: str
    evaluation_id: str
    rating: str
    comment: str
    feedback_type: str
    timestamp: str
    api_key_hash: str = ""  # hashed for privacy


class FeedbackStats(BaseModel):
    total_feedback: int
    thumbs_up: int
    thumbs_down: int
    by_type: dict[str, int]
    recent_comments: list[str]
