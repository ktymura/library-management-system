from __future__ import annotations

import os

from fastapi import FastAPI

from app.api.errors import domain_error_handler
from app.api.routers import authors_router, books_router, copies_router
from app.exceptions import DomainError

app = FastAPI(title="Catalog Service")
# Routers
app.include_router(authors_router)
app.include_router(books_router)
app.include_router(copies_router)

# Errors
app.add_exception_handler(DomainError, domain_error_handler)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "user-service",
        "port": os.getenv("PORT", "8000"),
        "db": os.getenv("DATABASE_URL", "<not-set>")[:40] + "...",
    }
