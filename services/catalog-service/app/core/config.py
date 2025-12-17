import os
import pathlib

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import make_url

# Locate project root (directory holding docker-compose.yml) to pick the correct .env.
_HERE = pathlib.Path(__file__).resolve()
_ROOT_ENV = None
_SERVICE_ENV = None

project_root = None
env_candidates = []
for p in _HERE.parents:
    if (p / "docker-compose.yml").exists():
        project_root = p
        break
    if (p / ".env").exists():
        env_candidates.append(p / ".env")

if project_root and (project_root / ".env").exists():
    _ROOT_ENV = project_root / ".env"
elif env_candidates:
    # fall back to the highest .env we saw while walking upward
    _ROOT_ENV = env_candidates[-1]

# service-level .env (services/user-service/.env) if present
service_dir = None
for p in _HERE.parents:
    if p.name == "catalog-service":
        service_dir = p
        break
if service_dir and (service_dir / ".env").exists():
    _SERVICE_ENV = service_dir / ".env"


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str | None = None

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_ISSUER: str | None = None
    JWT_AUDIENCE: str | None = None

    ENV: str = "dev"

    # Load env vars from repo root first (if found), then service-level overrides.
    model_config = SettingsConfigDict(
        env_file=tuple(f for f in (_ROOT_ENV, _SERVICE_ENV) if f),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # allow unrelated root-level env vars
    )

    @model_validator(mode="after")
    def ensure_database_url(self):
        """Build DATABASE_URL from root .env pieces, ignoring service-level DATABASE_URL."""
        in_docker = os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "1"
        db_user = db_pass = db_name = db_host = db_port = None
        if not in_docker:
            # Parse root .env manually to avoid a service-level DATABASE_URL override.
            if _ROOT_ENV and _ROOT_ENV.exists():
                for line in _ROOT_ENV.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    if key == "CATALOG_DB_USER":
                        db_user = val
                    elif key == "CATALOG_DB_PASSWORD":
                        db_pass = val
                    elif key == "CATALOG_DB_NAME":
                        db_name = val
                    elif key == "DB_HOST":
                        db_host = val
                    elif key == "POSTGRES_PORT":
                        db_port = val

        # Allow real environment variables (e.g., CI overrides) to supersede root .env values.
        db_user = os.getenv("CATALOG_DB_USER", db_user)
        db_pass = os.getenv("CATALOG_DB_PASSWORD", db_pass)
        db_name = os.getenv("CATALOG_DB_NAME", db_name)
        db_host = os.getenv("DB_HOST", db_host or "localhost")
        db_port = os.getenv("POSTGRES_PORT", db_port or "5432")

        if all([db_user, db_pass, db_name]):
            self.DATABASE_URL = (
                f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            )
            # Adjust host when running locally but URL points to docker service name.
            if self.DATABASE_URL and not in_docker:
                u = make_url(self.DATABASE_URL)
                if u.host in {"db", "lms-db"}:
                    self.DATABASE_URL = u.set(host="127.0.0.1").render_as_string(
                        hide_password=False
                    )
            return self

        raise ValueError(
            "DATABASE_URL is not set and cannot be constructed from CATALOG_DB_* variables"
        )


settings = Settings()
