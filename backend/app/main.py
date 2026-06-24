"""learnFinnish backend — FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import RateLimitMiddleware
from app.api import auth, words, srs, progress, grammar

app = FastAPI(
    title="learnFinnish API",
    description="Estonia-Finnish language learning — the best in the world",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Rate limiting middleware (60 requests per minute per IP)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(words.router, prefix="/api/words", tags=["words"])
app.include_router(srs.router, prefix="/api/srs", tags=["srs"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(grammar.router, prefix="/api/grammar", tags=["grammar"])


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "learnFinnish"}
