import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str | None = "sqlite+pysqlite:///:memory:"

    # JWT
    JWT_SECRET: str | None = "superecret"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60  # czas ważności access tokenu
    JWT_ISSUER: str | None = None
    JWT_AUDIENCE: str | None = None

    # meta
    ENV: str = "dev"

    # Load env vars from repo root first (if found), then service-level overrides.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()  # importuj z innych modułów: from app.core.config import settings
