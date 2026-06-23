"""Application configuration."""
import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "learnFinnish"
    DATABASE_URL: str = "sqlite+aiosqlite:///./learnfinnish.db"
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Auto-generated if not in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day (was 7 days)
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    class Config:
        env_file = ".env"


settings = Settings()
