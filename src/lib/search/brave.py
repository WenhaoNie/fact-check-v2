from __future__ import annotations

import os
from typing import List, Optional

from ..search_adapter import SearchAdapter, SearchResult
from ..logging import get_logger
from ..retry import with_retries
import httpx


logger = get_logger(__name__)


def _read_key_from_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


class BraveAdapter(SearchAdapter):
    """Skeleton adapter for Brave Search (base tier).

    Notes: Reads API key from /keys/BRAVE_API_KEY by default. Networking and
    full response parsing will be added in later tasks.
    """

    def __init__(self) -> None:
        key_file = os.getenv("BRAVE_KEY_FILE", "/keys/BRAVE_API_KEY")
        self.api_key = os.getenv("BRAVE_API_KEY") or _read_key_from_file(key_file)
        if not self.api_key:
            logger.warning("Brave API key not found at env BRAVE_API_KEY or %s", key_file)

    @with_retries(max_attempts=3, base_delay=0.5)
    def _request(self, q: str, topk: int) -> dict:
        if not self.api_key:
            raise RuntimeError("BRAVE_API_KEY missing. Place key in /keys/BRAVE_API_KEY or env.")
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json",
            "User-Agent": "FactCheck-Agent/0.1",
        }
        params = {
            "q": q,
            "count": max(1, min(topk, 20)),
            "safesearch": "off",
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()

    def search(self, query: str, topk: int = 5, site: Optional[str] = None) -> List[SearchResult]:
        q = query
        if site:
            q = f"site:{site} {query}"

        try:
            data = self._request(q, topk)
        except Exception as e:
            logger.warning("Brave search failed: %s", e)
            return []

        results: List[SearchResult] = []
        # Web results
        web = data.get("web", {})
        for item in web.get("results", [])[:topk]:
            url = item.get("url") or item.get("link") or ""
            title = item.get("title") or url
            desc = item.get("description") or item.get("snippet") or ""
            if url:
                results.append(SearchResult(url=url, title=title, snippet=desc))
        # News results (fallback/augment)
        if len(results) < topk:
            news = data.get("news", {})
            for item in news.get("results", [])[: (topk - len(results))]:
                url = item.get("url") or item.get("link") or ""
                title = item.get("title") or url
                desc = item.get("description") or item.get("snippet") or ""
                if url:
                    results.append(SearchResult(url=url, title=title, snippet=desc))

        return results[:topk]
