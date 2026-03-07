from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import os

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import api_router
from app.vulca import vulca_router
from app.prototype.api import get_prototype_router
from app.prototype.api.evaluate_routes import evaluate_router
from app.prototype.feedback.feedback_routes import feedback_router
from app.prototype.skills.api.skill_routes import skill_api_router
from app.prototype.skills.api.discussion_routes import discussion_router
from app.prototype.skills.api.version_routes import version_router
# Temporarily disabled - requires sentence-transformers
# from app.exhibition.api import router as exhibition_router

# Determine production environment
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
# B2B API clients need docs even in production — opt-in via env var
ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() in ("true", "1", "yes")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("Starting up...")
    # init_db is idempotent: create_all + seed only if empty
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        # In production, don't block startup if DB init fails (tables may already exist)
        print(f"WARNING: init_db failed: {type(e).__name__}: {e}")
        if not IS_PRODUCTION:
            raise
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app with conditional API docs
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    # Disable API docs in production unless ENABLE_API_DOCS is set (for B2B clients)
    openapi_url=None if (IS_PRODUCTION and not ENABLE_API_DOCS) else f"{settings.API_V1_STR}/openapi.json",
    docs_url=None if (IS_PRODUCTION and not ENABLE_API_DOCS) else "/docs",
    redoc_url=None if (IS_PRODUCTION and not ENABLE_API_DOCS) else "/redoc",
    lifespan=lifespan
)

# Set up CORS from configuration
print(f"Setting up CORS with origins: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    # Additional security headers for production
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Mount prototype draft images first (more specific route).
prototype_draft_dir = os.path.join(os.path.dirname(__file__), "prototype", "checkpoints", "draft")
os.makedirs(prototype_draft_dir, exist_ok=True)
app.mount(
    "/static/prototype/draft",
    StaticFiles(directory=prototype_draft_dir),
    name="prototype-draft-static",
)
print(f"Prototype draft static mounted at /static/prototype/draft from {prototype_draft_dir}")

# Mount static files for generated images
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"Static files mounted at /static from {static_dir}")
else:
    print(f"Warning: Static directory not found at {static_dir}")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include VULCA router
app.include_router(vulca_router)

# Include Prototype pipeline router
app.include_router(get_prototype_router())

# Include B2B Evaluate API (M4)
app.include_router(evaluate_router)

# Include Feedback API
app.include_router(feedback_router)

# Include Skill Marketplace API
app.include_router(skill_api_router)
app.include_router(discussion_router)
app.include_router(version_router)

# Include Exhibition router (Echoes and Returns)
# Temporarily disabled - requires sentence-transformers
# app.include_router(exhibition_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment readiness"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "wenxin-backend",
        "version": settings.APP_VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/health/deep")
async def deep_health_check():
    """Deep health check — reports component availability for monitoring."""
    components = {}

    # Database connectivity
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        components["database"] = "connected"
    except Exception as e:
        components["database"] = f"error: {type(e).__name__}: {e}"

    # VLM Critic availability
    try:
        from app.prototype.agents.vlm_critic import VLMCritic
        vlm = VLMCritic.get()
        components["vlm_critic"] = "available" if vlm.available else "no_api_key"
    except Exception as e:
        components["vlm_critic"] = f"error: {type(e).__name__}"

    # Scout service (terminology + taboo)
    try:
        from app.prototype.tools.terminology_loader import TerminologyLoader
        tl = TerminologyLoader()
        components["scout_terminology"] = f"{sum(len(v) for v in tl._traditions.values())} terms"
    except Exception as e:
        components["scout_terminology"] = f"error: {type(e).__name__}"

    # Cultural Pipeline Router
    try:
        from app.prototype.cultural_pipelines.pipeline_router import CulturalPipelineRouter
        router = CulturalPipelineRouter()
        components["cultural_router"] = f"{len(router.list_traditions())} traditions"
    except Exception as e:
        components["cultural_router"] = f"error: {type(e).__name__}"

    # B2B API key configuration
    api_keys_configured = bool(os.getenv("VULCA_API_KEYS", ""))
    components["b2b_api_keys"] = "configured" if api_keys_configured else "not_configured"

    all_ok = all(
        "error" not in str(v) for v in components.values()
    )

    return {
        "status": "healthy" if all_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "wenxin-backend",
        "version": settings.APP_VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "components": components,
    }

@app.get("/")
async def root():
    """Root endpoint - redirect to frontend"""
    from fastapi.responses import HTMLResponse
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>文心墨韵 - AI艺术创作评测平台</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; text-align: center; min-height: 100vh; display: flex;
                flex-direction: column; justify-content: center; align-items: center;
            }}
            .container {{ background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 1rem;
                -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); max-width: 500px; }}
            .logo {{ font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem; }}
            .subtitle {{ font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9; }}
            .btn {{ display: inline-block; padding: 1rem 2rem; background: rgba(255,255,255,0.2);
                color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 600;
                transition: all 0.3s; margin: 0.5rem; }}
            .btn:hover {{ background: rgba(255,255,255,0.3); transform: translateY(-2px); }}
            .api-info {{ margin-top: 2rem; font-size: 0.9rem; opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎨 文心墨韵</div>
            <div class="subtitle">AI艺术创作评测平台</div>
            <p>您正在访问后端API服务器</p>
            
            <a href="http://localhost:5173" class="btn">🚀 访问前端应用</a>
            <a href="/docs" class="btn">📖 API文档</a>
            
            <div class="api-info">
                <p><strong>API信息</strong></p>
                <p>版本: {settings.APP_VERSION}</p>
                <p>API根路径: {settings.API_V1_STR}</p>
                <p>前端地址: <a href="http://localhost:5173" style="color: #FFD700;">http://localhost:5173</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to avoid 404 errors"""
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon")
