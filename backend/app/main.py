"""EdilEngine - FastAPI Backend Application.

Italian construction law navigation system with RAG chatbot.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import close_db, init_db
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.models import *  # noqa: F401, F403 - Register all models with Base.metadata
from app.routers import chat, guide, incentivi, leggi, vincoli

# -------------------------------------------
# Logging configuration
# -------------------------------------------
settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


# -------------------------------------------
# Application lifespan
# -------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("Starting EdilEngine backend...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed (may be expected in prod): {e}")

    # Pre-load embedding model if using local provider (download on first run)
    if settings.EMBEDDING_PROVIDER.lower() == "local":
        try:
            logger.info(f"Pre-loading local embedding model: {settings.EMBEDDING_MODEL_NAME}...")
            from app.services.embedding_service import EmbeddingService
            svc = EmbeddingService()
            # Trigger model download/load
            import asyncio
            await svc.generate_embedding("test")
            logger.info(f"Embedding model loaded successfully (dim={svc.dimension})")
        except Exception as e:
            logger.warning(f"Embedding model pre-load failed (will load on first use): {e}")
    else:
        logger.info(f"Using OpenAI embedding provider (model={settings.OPENAI_EMBEDDING_MODEL})")

    logger.info("EdilEngine backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down EdilEngine backend...")
    await close_db()
    logger.info("EdilEngine backend shut down")


# -------------------------------------------
# FastAPI application
# -------------------------------------------
app = FastAPI(
    title="EdilEngine API",
    description=(
        "API per la navigazione delle leggi italiane dell'edilizia. "
        "Include ricerca full-text, semantic search, chatbot RAG, "
        "e guida personalizzata per progetti edilizi."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# -------------------------------------------
# Middleware
# -------------------------------------------
setup_cors(app)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)

# -------------------------------------------
# Routers
# -------------------------------------------
app.include_router(leggi.router)
app.include_router(incentivi.router)
app.include_router(vincoli.router)
app.include_router(chat.router)
app.include_router(guide.router)

# -------------------------------------------
# Global exception handler
# -------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Errore interno del server"},
    )


# -------------------------------------------
# Endpoints
# -------------------------------------------
@app.get("/api/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint for Cloud Run and monitoring."""
    return {
        "status": "healthy",
        "service": "edilengine-backend",
        "version": "1.0.0",
    }


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint with project information."""
    return {
        "name": "EdilEngine API",
        "description": "Sistema per navigare le leggi italiane dell'edilizia",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
        "endpoints": {
            "leggi": "/api/leggi",
            "incentivi": "/api/incentivi",
            "vincoli": "/api/vincoli",
            "chat": "/api/chat",
            "personalized_guide": "/api/personalized-guide",
        },
    }
