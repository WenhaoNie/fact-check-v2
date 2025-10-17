from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str


class SearchAdapter:
    def search(self, query: str, topk: int = 5, site: Optional[str] = None) -> List[SearchResult]:  # noqa: D401
        """Search for query and return a list of results."""
        raise NotImplementedError


def _load_provider_config() -> dict:
    cfg_path = os.getenv("PROVIDERS_CONFIG", os.path.join(os.getcwd(), "configs", "providers.toml"))
    if not os.path.exists(cfg_path):
        return {}
    with open(cfg_path, "rb") as f:
        return tomllib.load(f)


def get_search_adapter() -> SearchAdapter:
    """Factory: returns a concrete SearchAdapter based on env/config (default brave)."""
    provider = os.getenv("SEARCH_PROVIDER") or _load_provider_config().get("search", {}).get("provider", "brave")
    provider = (provider or "brave").lower()
    if provider == "brave":
        from .search.brave import BraveAdapter

        return BraveAdapter()
    raise RuntimeError(f"Unsupported SEARCH_PROVIDER: {provider}")


def iter_results_text(results: Iterable[SearchResult]) -> str:
    return "\n".join(f"- {r.title} {r.url}\n  {r.snippet}" for r in results)

