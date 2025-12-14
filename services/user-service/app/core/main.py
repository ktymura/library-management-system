from app.core.config import settings
from fastapi import FastAPI

tags_metadata = [
    {"name": "auth", "description": "Rejestracja, logowanie i tokeny JWT"},
    {"name": "users", "description": "Operacje na użytkownikach (wymaga JWT)"},
]

app = FastAPI(
    title="User Service",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

# Tu później podłączymy routery:
# from app.api.v1.auth import router as auth_router
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# from app.api.v1.users import router as users_router
# app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}
