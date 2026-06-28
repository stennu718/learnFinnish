"""Application configuration."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "learnFinnish"
    DATABASE_URL: str = "sqlite+aiosqlite:///./learnfinnish.db"
    SECRET_KEY: str = Field(..., min_length=32, description="JWT signing secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # Long-lived refresh tokens
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    class Config:
        env_file = ".env"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


settings = Settings()
