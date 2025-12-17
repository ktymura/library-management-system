from .author import AuthorCreate, AuthorRead
from .book import BookCreate, BookRead, BookUpdate
from .copy import CopyCreate, CopyRead
from .error import ErrorDetail, ErrorResponse

__all__ = [
    "AuthorCreate",
    "AuthorRead",
    "BookCreate",
    "BookUpdate",
    "BookRead",
    "CopyCreate",
    "CopyRead",
    "ErrorDetail",
    "ErrorResponse",
]
