from .health import router as health_router
from .health_db import router as health_db_router
from .loans import router as loans_router

__all__ = ["health_router", "health_db_router", "loans_router"]
