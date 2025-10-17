from __future__ import annotations

from typing import Iterable, Optional

from .logging import get_logger


logger = get_logger(__name__)


def _read_allowed_keys_files(paths: Iterable[str]) -> set[str]:
    keys: set[str] = set()
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    t = line.strip()
                    if t:
                        keys.add(t)
        except FileNotFoundError:
            continue
    return keys


def is_valid_api_key(provided: Optional[str]) -> bool:
    if not provided:
        return False
    allowed = _read_allowed_keys_files(["/keys/APP_API_KEYS", "/keys/API_KEYS"])  # optional
    if allowed:
        if provided in allowed:
            return True
        logger.warning("API key provided but not found in allowlist file")
        return False
    # No allowlist file configured
    allow_all = os.getenv("AUTH_ALLOW_ALL", "1") in {"1", "true", "TRUE", "yes", "YES"}
    if allow_all:
        return True
    logger.warning("No allowlist present and AUTH_ALLOW_ALL disabled")
    return False


def require_api_key(headers: dict) -> None:
    key = headers.get("X-API-Key") or headers.get("x-api-key")
    if not is_valid_api_key(key):
        raise PermissionError("Unauthorized: missing or invalid API key")
