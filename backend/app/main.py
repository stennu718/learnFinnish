"""learnFinnish backend — FastAPI application (v1)."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import RateLimitMiddleware
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    get_app_uptime,
)
from app.core.exceptions import setup_exception_handlers
from app.core.structured_logging import setup_logging
from app.api import auth, words, srs, progress, grammar

import logging

logger = logging.getLogger("learnfinnish")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    setup_logging("INFO")
    logger.info("Starting %s v1.0.0", settings.APP_NAME)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="learnFinnish API",
        description=(
            "Estonian-Finnish language learning platform API.\n\n"
            "## Features\n"
            "- **Words**: Browse Estonian-Finnish word pairs with categories\n"
            "- **SRS**: Spaced repetition system (SM-2 algorithm)\n"
            "- **Grammar**: Case transformation exercises\n"
            "- **Progress**: Track learning progress, XP, and streaks\n\n"
            "## Authentication\n"
            "All endpoints except `/auth/register`, `/auth/login`, and `/health` require "
            "a Bearer token in the `Authorization` header.\n\n"
            "Use `/auth/refresh` to rotate refresh tokens."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {"name": "auth", "description": "Authentication — register, login, refresh, logout"},
            {"name": "words", "description": "Word pairs and categories"},
            {"name": "srs", "description": "Spaced repetition system"},
            {"name": "progress", "description": "User progress tracking"},
            {"name": "grammar", "description": "Grammar exercises and rules"},
            {"name": "system", "description": "System health and metadata"},
        ],
    )

    # ── Middleware (order matters: last added = first executed) ──

    # 1. Security headers (innermost — runs last)
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. Rate limiting
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

    # 3. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Response-Time", "X-RateLimit-Limit"],
    )

    # 4. Request ID + timing (outermost — runs first)
    app.add_middleware(RequestIDMiddleware)

    # ── Exception handlers ──
    setup_exception_handlers(app)

    # ── Routers (versioned under /api/v1/ + legacy /api/ for backward compat) ──
    API_V1 = "/api/v1"
    app.include_router(auth.router, prefix=f"{API_V1}/auth", tags=["auth"])
    app.include_router(words.router, prefix=f"{API_V1}/words", tags=["words"])
    app.include_router(srs.router, prefix=f"{API_V1}/srs", tags=["srs"])
    app.include_router(progress.router, prefix=f"{API_V1}/progress", tags=["progress"])
    app.include_router(grammar.router, prefix=f"{API_V1}/grammar", tags=["grammar"])
    # Legacy routes (backward compatibility)
    app.include_router(auth.router, prefix="/api/auth", tags=["auth-legacy"])
    app.include_router(words.router, prefix="/api/words", tags=["words-legacy"])
    app.include_router(srs.router, prefix="/api/srs", tags=["srs-legacy"])
    app.include_router(progress.router, prefix="/api/progress", tags=["progress-legacy"])
    app.include_router(grammar.router, prefix="/api/grammar", tags=["grammar-legacy"])

    # ── Health check ──
    @app.get("/health", tags=["system"])
    async def health():
        """Health check — returns status, DB connectivity, and uptime."""
        db_status = "ok"
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:
            db_status = "error"

        uptime = get_app_uptime()
        return {
            "status": "ok" if db_status == "ok" else "degraded",
            "app": settings.APP_NAME,
            "version": "1.0.0",
            "database": db_status,
            "uptime_seconds": round(uptime, 1),
        }

    return app


app = create_app()
