from __future__ import annotations

import os
from typing import List, Optional

from ..search_adapter import SearchAdapter, SearchResult
from ..logging import get_logger


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

    def search(self, query: str, topk: int = 5, site: Optional[str] = None) -> List[SearchResult]:
        # Intentionally not performing network calls yet. Provide a clear error
        # so tests fail until implementation tasks are completed.
        raise NotImplementedError("BraveAdapter.search not implemented yet")

