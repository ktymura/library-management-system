from __future__ import annotations

import re
from datetime import datetime, timezone

_ISBN10_RE = re.compile(r"^\d{9}[\dX]$")
_ISBN13_RE = re.compile(r"^\d{13}$")


def normalize_isbn(isbn: str | None) -> str | None:
    if not isbn:
        return None
    # usuń spacje i myślniki, zamień x->X
    return re.sub(r"[\s\-]", "", isbn).upper()


def is_valid_isbn10(isbn10: str) -> bool:
    if not _ISBN10_RE.match(isbn10):
        return False
    total = 0
    for i, ch in enumerate(isbn10[:9], start=1):
        total += i * int(ch)
    check = total % 11
    check_ch = "X" if check == 10 else str(check)
    return isbn10[-1] == check_ch


def is_valid_isbn13(isbn13: str) -> bool:
    if not _ISBN13_RE.match(isbn13):
        return False
    digits = [int(c) for c in isbn13]
    total = sum((d if i % 2 == 0 else 3 * d) for i, d in enumerate(digits[:-1]))
    check = (10 - (total % 10)) % 10
    return digits[-1] == check


def validate_isbn(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    norm = normalize_isbn(value)
    if norm and (is_valid_isbn10(norm) or is_valid_isbn13(norm)):
        return norm
    raise ValueError("Invalid ISBN (expect ISBN-10 or ISBN-13).")


def validate_year(year: int | None) -> int | None:
    if year is None:
        return None
    current = datetime.now(timezone.utc).year
    # typowy zakres publikacji
    if 1400 <= year <= current + 1:
        return year
    raise ValueError(f"Invalid published_year (must be 1400..{current + 1}).")
