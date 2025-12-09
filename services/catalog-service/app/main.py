import os

from fastapi import FastAPI

app = FastAPI(title="LMS - Catalog Service")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "user-service",
        "port": os.getenv("PORT", "8000"),
        "db": os.getenv("DATABASE_URL", "<not-set>")[:40] + "...",
    }
