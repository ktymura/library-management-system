from fastapi import FastAPI

from app.api import health_db_router, health_router

app = FastAPI(title="Circulation Service")
# Routers
app.include_router(health_router)
app.include_router(health_db_router)
