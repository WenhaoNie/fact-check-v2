from __future__ import annotations

from typing import List, Optional


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def generate_queries(
    claim_text: str,
    *,
    locale: str = "auto",
    topk: int = 5,
    subject: Optional[str] = None,
) -> List[str]:
    """Generate balanced support/refute/neutral queries for a claim.

    Heuristic, provider-agnostic; avoids implementation-specific operators.
    """
    t = _normalize_text(claim_text)
    base = [t]
    if subject and subject not in t:
        base.append(f"{subject} {t}")

    support = [f"证实 {q}" if locale == "zh" else f"confirm {q}" for q in base]
    refute = [f"驳斥 {q}" if locale == "zh" else f"refute {q}" for q in base]
    neutral = [f"报道 {q}" if locale == "zh" else f"report {q}" for q in base]

    queries = []
    for trio in zip(support, refute, neutral):
        queries.extend(trio)
    # Deduplicate and limit
    seen = set()
    uniq = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq[: max(3, topk)]

