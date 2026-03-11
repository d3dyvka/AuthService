from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "change-me-in-production-secret-key"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 30

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = "noreply@example.com"
    smtp_password: str = "smtp_password"
    smtp_from: str = "Auth Service <noreply@example.com>"

    debug: bool = False
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
