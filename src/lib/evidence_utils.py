from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from .logging import get_logger


logger = get_logger(__name__)


AUTHORITY_DOMAINS = (
    # Common authority-like domains; extend via config later
    "sec.gov",
    "gov.cn",
    "caixin.com",
    "chinadaily.com.cn",
    "bloomberg.com",
    "reuters.com",
    "ft.com",
)

REGISTRY_HINTS = (
    "shenzhen stock exchange",
    "shanghai stock exchange",
    "国家企业信用信息公示系统",
)


def classify_domain(url: str) -> str:
    u = url.lower()
    for d in AUTHORITY_DOMAINS:
        if d in u:
            return "authority"
    # Simple heuristic for registry-like content
    if any(h in u for h in (".gov", ".gouv", ".go.")):
        return "registry"
    return "web"


def tag_credibility(url: str, page_text: Optional[str] = None) -> str:
    kind = classify_domain(url)
    if kind == "web" and page_text:
        text = page_text.lower()
        if any(h in text for h in REGISTRY_HINTS):
            return "registry"
    return kind


def best_excerpt(page_text: str, claim_terms: Iterable[str], max_len: int = 240) -> str:
    """Extract a short excerpt around the first matched claim term.

    Falls back to the first sentence-like chunk.
    """
    txt = re.sub(r"\s+", " ", page_text).strip()
    for term in claim_terms:
        m = re.search(re.escape(term), txt, flags=re.I)
        if m:
            start = max(0, m.start() - max_len // 2)
            end = min(len(txt), m.end() + max_len // 2)
            snippet = txt[start:end]
            return snippet[:max_len]
    # Fallback: first sentence-ish
    m = re.search(r"[^.!?。！？]{20,300}[.!?。！？]", txt)
    return (m.group(0) if m else txt[:max_len]).strip()

