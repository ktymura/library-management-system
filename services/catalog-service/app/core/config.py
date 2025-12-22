import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str | None = "sqlite+pysqlite:///:memory:"

    # JWT
    JWT_SECRET: str | None = "supersecret"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60  # czas ważności access tokenu
    JWT_ISSUER: str | None = "lms-user-service"
    JWT_AUDIENCE: str | None = "lms-catalog-service"

    # meta
    ENV: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


settings = Settings()  # importuj z innych modułów: from app.core.config import settings
