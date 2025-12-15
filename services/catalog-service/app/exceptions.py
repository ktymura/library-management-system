from __future__ import annotations


class DomainError(Exception):
    code = "domain_error"
    status = 400


class NotFound(DomainError):
    code = "not_found"
    status = 404


class AlreadyExists(DomainError):
    code = "already_exists"
    status = 409


class Forbidden(DomainError):
    code = "forbidden"
    status = 403


def to_http_payload(exc: DomainError) -> dict:
    # Użyjemy w warstwie API
    return {
        "error": {
            "code": exc.code,
            "message": str(exc),
        }
    }
