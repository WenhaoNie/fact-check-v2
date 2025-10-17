from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import httpx

from .logging import get_logger
from .retry import with_retries
from .cache import memoize_ttl


logger = get_logger(__name__)


DEFAULT_TIMEOUT = 10.0
DEFAULT_UA = (
    "FactCheck-Agent/0.1 (+https://example.com; compliance=robots,ToS; contact=ops@example.com)"
)


@dataclass
class FetchResult:
    url: str
    status: int
    text: str
    headers: Dict[str, str]
    fetched_at: str


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_client(timeout: float) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": DEFAULT_UA})


@memoize_ttl(ttl=600.0)
@with_retries(max_attempts=3, base_delay=0.5)
def fetch_url(url: str, timeout: float = DEFAULT_TIMEOUT) -> FetchResult:
    """HTTP GET fetch with conservative timeouts and retries (≤2 retries).

    Notes:
    - Respects server-side rate limiting by retrying 429/5xx with backoff.
    - Caller is responsible for honoring robots/ToS; we surface headers for
      compliance decisions (e.g., X-Robots-Tag).
    """
    start = time.time()
    with _build_client(timeout) as client:
        resp = client.get(url, follow_redirects=True)
        duration_ms = int((time.time() - start) * 1000)
        logger.debug("fetch_url %s -> %s in %dms", url, resp.status_code, duration_ms)
        resp.raise_for_status()
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return FetchResult(
            url=str(resp.url),
            status=resp.status_code,
            text=resp.text,
            headers=headers,
            fetched_at=_now_iso(),
        )
