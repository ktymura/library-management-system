from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60  # czas ważności access tokenu

    # meta
    ENV: str = "dev"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()  # importuj z innych modułów: from app.core.config import settings
