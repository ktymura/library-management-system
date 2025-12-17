from .authors import router as authors_router
from .books import router as books_router
from .copies import router as copies_router

__all__ = ["authors_router", "books_router", "copies_router"]
