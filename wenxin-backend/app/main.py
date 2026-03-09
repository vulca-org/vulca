from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import asyncio
import logging
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
from app.prototype.api.create_routes import create_router
from app.prototype.digestion.routes import digestion_router
# Temporarily disabled - requires sentence-transformers
# from app.exhibition.api import router as exhibition_router

# Determine production environment
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
# B2B API clients need docs even in production — opt-in via env var
ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() in ("true", "1", "yes")

# Digestion interval (default: 1 hour)
DIGESTION_INTERVAL_SECONDS = int(os.getenv("DIGESTION_INTERVAL_SECONDS", "3600"))

_digestion_logger = logging.getLogger("vulca.digestion")


async def _periodic_digestion() -> None:
    """Background task: run ContextEvolver.evolve() periodically."""
    await asyncio.sleep(30)  # Initial delay to let the app fully start
    while True:
        try:
            from app.prototype.digestion.context_evolver import ContextEvolver
            evolver = ContextEvolver()
            result = evolver.evolve()
            _digestion_logger.info(
                "Periodic digestion: %d actions, %d patterns, %d sessions (%s)",
                len(result.actions), result.patterns_found,
                result.sessions_analyzed, result.skipped_reason or "ok",
            )
        except Exception:
            _digestion_logger.exception("Periodic digestion failed")
        await asyncio.sleep(DIGESTION_INTERVAL_SECONDS)


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

    # Bootstrap check: backfill cultural features + sync feedback if no evolutions yet
    try:
        from app.prototype.digestion.feature_extractor import backfill_missing_features
        from app.prototype.feedback.feedback_store import FeedbackStore

        _evolved_path = Path(__file__).parent / "prototype" / "data" / "evolved_context.json"
        _should_bootstrap = True
        if _evolved_path.exists():
            import json as _json
            _ctx = _json.loads(_evolved_path.read_text())
            if _ctx.get("evolutions", 0) > 0:
                _should_bootstrap = False

        if _should_bootstrap:
            _bootstrap_logger = logging.getLogger("vulca.bootstrap")
            _bootstrap_logger.info("No evolutions yet — running bootstrap backfill")
            _bf_count = backfill_missing_features()
            _bootstrap_logger.info("Backfilled %d sessions", _bf_count)
            FeedbackStore.get().sync_from_sessions()
            from app.prototype.digestion.context_evolver import ContextEvolver
            _evolver = ContextEvolver()
            _evolver.evolve()
            _bootstrap_logger.info("Bootstrap evolution complete")
    except Exception as _bootstrap_exc:
        print(f"WARNING: Bootstrap backfill failed (non-fatal): {_bootstrap_exc}")

    # Start periodic digestion background task
    digestion_task = asyncio.create_task(_periodic_digestion())
    print(f"Periodic digestion started (interval={DIGESTION_INTERVAL_SECONDS}s)")

    yield

    # Shutdown
    print("Shutting down...")
    digestion_task.cancel()
    try:
        await digestion_task
    except asyncio.CancelledError:
        pass


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

# Include Unified Create API (creation + evaluation entry point)
app.include_router(create_router)

# Include Digestion System API
app.include_router(digestion_router)

# Include Exhibition router (Echoes and Returns)
# Temporarily disabled - requires sentence-transformers
# app.include_router(exhibition_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment readiness"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "wenxin-backend",
        "version": settings.APP_VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "components": components,
    }

# --- Frontend Serving ---
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if _frontend_dist.exists() and (_frontend_dist / "index.html").exists():
    # SPA mode: serve React frontend (for `vulca serve` local app mode)
    _assets_dir = _frontend_dist / "assets"
    if _assets_dir.exists():
        app.mount(
            "/_assets",
            StaticFiles(directory=str(_assets_dir)),
            name="frontend-assets",
        )

    @app.get("/", include_in_schema=False)
    async def spa_root():
        return FileResponse(
            str(_frontend_dist / "index.html"), media_type="text/html"
        )

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        fav = _frontend_dist / "favicon.ico"
        if fav.exists():
            return FileResponse(str(fav), media_type="image/x-icon")
        return Response(content=b"", media_type="image/x-icon")

    @app.api_route("/{path:path}", methods=["GET"], include_in_schema=False)
    async def spa_catchall(request: Request, path: str):
        # Don't intercept API routes, docs, health, or static files
        if path.startswith((
            "api/", "docs", "redoc", "openapi", "health",
            "static", "_assets", "favicon.ico",
        )):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Try to serve the exact file if it exists (e.g., images, fonts)
        file_path = _frontend_dist / path
        if file_path.is_file() and ".." not in path:
            return FileResponse(str(file_path))

        # Otherwise serve index.html for SPA routing
        return FileResponse(
            str(_frontend_dist / "index.html"), media_type="text/html"
        )

    print(f"SPA frontend mounted from {_frontend_dist}")

else:
    # API-only mode: show info page
    @app.get("/")
    async def root():
        """Root endpoint - redirect to frontend"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VULCA - AI Art Evaluation Platform</title>
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
                <div class="logo">VULCA</div>
                <div class="subtitle">AI Art Evaluation Platform</div>
                <p>You are accessing the backend API server</p>

                <a href="http://localhost:5173" class="btn">Frontend App</a>
                <a href="/docs" class="btn">API Docs</a>

                <div class="api-info">
                    <p><strong>API Info</strong></p>
                    <p>Version: {settings.APP_VERSION}</p>
                    <p>API Root: {settings.API_V1_STR}</p>
                    <p>Frontend: <a href="http://localhost:5173" style="color: #FFD700;">http://localhost:5173</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

    @app.get("/favicon.ico")
    async def favicon():
        """Return empty favicon to avoid 404 errors"""
        return Response(content=b"", media_type="image/x-icon")
