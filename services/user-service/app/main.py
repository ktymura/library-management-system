import os

from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

tags_metadata = [
    {"name": "auth", "description": "Rejestracja, logowanie i tokeny JWT"},
    {"name": "users", "description": "Operacje na użytkownikach (wymaga JWT)"},
]

app = FastAPI(
    title="User Service",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "user-service",
        "port": os.getenv("PORT", "8000"),
        "db": os.getenv("DATABASE_URL", "<not-set>")[:40] + "...",
    }
