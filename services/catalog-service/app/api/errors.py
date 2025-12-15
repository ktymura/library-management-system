from __future__ import annotations

from app.exceptions import DomainError, to_http_payload
from fastapi import Request
from fastapi.responses import JSONResponse


def domain_error_handler(_: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status, content=to_http_payload(exc))
