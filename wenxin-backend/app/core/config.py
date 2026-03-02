from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WenxinMoyun"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # Default to False for security, enable via env var
    API_V1_STR: str = "/api/v1"

    # Security - MUST be set via environment variable in production
    SECRET_KEY: str = ""

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY is properly set"""
        if not v:
            # Development environment: use a fixed dev key
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be set in production environment")
            return "dev-secret-key-do-not-use-in-production-32chars"
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database Configuration
    # Support both SQLite (development) and PostgreSQL (production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./wenxin.db"
    
    # PostgreSQL settings for production (Cloud SQL)
    POSTGRES_USER: str = "wenxin"
    POSTGRES_PASSWORD: str = ""  # Will be loaded from Secret Manager
    POSTGRES_DB: str = "wenxin_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Cloud SQL specific settings
    CLOUD_SQL_INSTANCE: str = ""  # Format: project:region:instance
    USE_CLOUD_SQL: bool = False
    
    # Redis - Optional for production caching
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # Production Environment Settings
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # CORS Configuration - supports development ports and production URLs
    CORS_ORIGINS: List[str] = [
        # Development localhost ports (5173-5181 for Vite hot reload)
        *[f"http://localhost:{port}" for port in range(5173, 5182)],
        *[f"http://127.0.0.1:{port}" for port in range(5173, 5182)],
        "http://localhost:3000",
        # Production URLs
        "https://vulcaart.art",
        "https://www.vulcaart.art",
        "https://storage.googleapis.com",
        # Render deployment
        "https://vulca-api.onrender.com"
    ]
    
    # Rate Limiting
    GUEST_DAILY_LIMIT: int = 5
    AUTHENTICATED_DAILY_LIMIT: int = 50
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_BUCKET: str = ""
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/webp", "text/plain"
    ]
    
    # Monitoring and Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = False
    SENTRY_DSN: str = ""
    
    # Feature Flags
    ENABLE_REAL_AI_EVALUATION: bool = True
    ENABLE_BATTLE_MODE: bool = True
    ENABLE_GUEST_MODE: bool = True
    ENABLE_BENCHMARKS: bool = True
    
    # Vector Database - Disabled for now
    # QDRANT_HOST: str = "localhost"
    # QDRANT_PORT: int = 6333
    USE_QDRANT: bool = False
    
    # AI Models API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    ZHIPU_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    GLOBALAI_API_KEY: str = ""
    GLOBALAI_API_BASE: str = ""
    QWEN_API_KEY: str = ""
    XAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""
    FAL_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # Langfuse Observability
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Cost Control
    ENABLE_COST_CONTROL: bool = True
    DAILY_COST_LIMIT: float = 10.0

    # Lead Notifications
    # Webhook for internal notifications (Discord/Slack compatible)
    LEAD_NOTIFICATION_WEBHOOK_URL: str = ""
    # Team email for notifications (used with SMTP)
    LEAD_NOTIFICATION_EMAIL: str = ""
    # Enable/disable lead notifications
    ENABLE_LEAD_NOTIFICATIONS: bool = True

    # Email Configuration (SMTP)
    # Works with SendGrid, SES, Mailgun, or any SMTP provider
    SMTP_HOST: str = ""  # e.g., smtp.sendgrid.net
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # e.g., apikey (for SendGrid)
    SMTP_PASSWORD: str = ""  # SMTP password or API key
    SMTP_FROM_EMAIL: str = "noreply@vulca.ai"
    SMTP_FROM_NAME: str = "VULCA Team"
    SMTP_USE_TLS: bool = True
    ENABLE_EMAIL_CONFIRMATION: bool = True
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                # Parse JSON array
                origins = json.loads(v)
                # Ensure all are strings without trailing slashes
                return [str(origin).rstrip('/') for origin in origins]
            else:
                # Parse comma-separated string
                return [i.strip().rstrip('/') for i in v.split(",")]
        elif isinstance(v, list):
            return [str(origin).rstrip('/') for origin in v]
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()