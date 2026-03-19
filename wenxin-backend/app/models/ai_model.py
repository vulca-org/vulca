from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
from app.core.config import settings


class AIModel(Base):
    __tablename__ = "ai_models"
    
    # Use String for SQLite, UUID for PostgreSQL
    if settings.DATABASE_URL.startswith("sqlite"):
        id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    organization = Column(String(100))
    version = Column(String(20))
    category = Column(String(50))  # text, multimodal, etc.
    description = Column(Text)
    api_endpoint = Column(String(500))
    api_key_encrypted = Column(Text)  # Encrypted API key if needed
    
    # Scores
    overall_score = Column(Float, default=0.0)
    metrics = Column(JSON, default={})  # Store all metrics as JSON
    
    # Individual score columns (for production database compatibility)
    rhythm_score = Column(Float, default=0.0)
    composition_score = Column(Float, default=0.0)
    narrative_score = Column(Float, default=0.0)
    emotion_score = Column(Float, default=0.0)
    creativity_score = Column(Float, default=0.0)
    cultural_score = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    release_date = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional metadata
    tags = Column(JSON, default=[])
    avatar_url = Column(String(500))
    
    # Data source tracking (new fields for benchmark system)
    data_source = Column(String(20), default="mock")  # mock, real, benchmark
    verification_count = Column(Integer, default=0)  # Number of times verified
    benchmark_score = Column(Float, nullable=True)  # Score from benchmark tests
    benchmark_metadata = Column(JSON, default={})  # Detailed benchmark results
    confidence_level = Column(Float, default=0.0)  # 0-1 confidence in score accuracy
    last_benchmark_at = Column(DateTime(timezone=True), nullable=True)
    
    # Enhanced benchmark results (v2)
    benchmark_responses = Column(JSON, default={})  # Store actual API responses
    scoring_details = Column(JSON, default={})  # Detailed scoring from GPT-4o-mini
    score_highlights = Column(JSON, default=[])  # Highlighted excellent parts
    score_weaknesses = Column(JSON, default=[])  # Identified weaknesses
    improvement_suggestions = Column(Text, nullable=True)  # Improvement recommendations
    
    # Model type and ranking fields
    model_type = Column(String(20), nullable=True)  # llm, image, multimodal
    model_tier = Column(String(20), nullable=True)  # flagship, professional, efficient, lightweight
    llm_rank = Column(Integer, nullable=True)  # Rank in LLM category
    image_rank = Column(Integer, nullable=True)  # Rank in image category
    
    # VULCA Integration fields
    vulca_scores_47d = Column(JSON, nullable=True)  # 47-dimensional VULCA scores
    vulca_cultural_perspectives = Column(JSON, nullable=True)  # 9 cultural tradition scores
    vulca_evaluation_date = Column(DateTime(timezone=True), nullable=True)  # Last VULCA evaluation
    vulca_sync_status = Column(String(20), default="pending")  # pending, syncing, completed, failed
    
    # Relationships
    from sqlalchemy.orm import relationship
    evaluation_tasks = relationship("EvaluationTask", back_populates="model")