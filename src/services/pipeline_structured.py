from __future__ import annotations

import time
from typing import Any, Dict, List

from lib.logging import get_logger
from lib.search_adapter import get_search_adapter, SearchResult
from lib.query_strategy import generate_queries
from lib.evidence_utils import tag_credibility, best_excerpt
from lib.policy import evaluate_evidence_credibility
from lib.fetcher import fetch_url
from lib.llm import reason_claim
from models.schemas import EvidenceItem, Judgment
from models.audit import AuditInfo, ToolTrace, Usage


logger = get_logger(__name__)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _assemble_evidence(results: List[SearchResult], claim_text: str) -> List[EvidenceItem]:
    items: List[EvidenceItem] = []
    seen: set[str] = set()
    terms = [t for t in [claim_text] if t]
    for r in results:
        if r.url in seen:
            continue
        seen.add(r.url)
        fetched_at = _now_iso()
        excerpt = r.snippet
        try:
            fr = fetch_url(r.url)
            fetched_at = fr.fetched_at
            excerpt = best_excerpt(fr.text, terms, max_len=240) or r.snippet or r.title
        except Exception:
            excerpt = excerpt or best_excerpt(r.title or "", terms, max_len=160)

        cred = tag_credibility(r.url)
        items.append(
            EvidenceItem(
                url=r.url,
                title=r.title or r.url,
                quote=excerpt or r.title or r.url,
                fetched_at=fetched_at,
                credibility=cred,
            )
        )
        if len(items) >= 3:
            break
    return items


def run(input_payload: Dict[str, Any], output_kind: str = "both") -> Judgment:
    """Structured claim pipeline.

    Input payload expected shape (subset):
      { "claim": { "subject": str?, "text": str, "time_window": str?, "locale": "zh|en|auto" } }
    """
    claim_obj = input_payload.get("claim") or {}
    claim_text: str = claim_obj.get("text") or ""
    locale: str = claim_obj.get("locale") or "auto"
    subject: str = claim_obj.get("subject") or ""

    traces: List[ToolTrace] = []
    results: List[SearchResult] = []

    # Step 1: queries
    t0 = time.time()
    queries = generate_queries(claim_text, locale=locale, subject=subject or None)
    traces.append(ToolTrace(step=1, action="generate_queries", args={"n": len(queries)}, ok=True, latency_ms=int((time.time() - t0) * 1000)))

    # Step 2: search
    try:
        adapter = get_search_adapter()
        for q in queries:
            t = time.time()
            try:
                rs = adapter.search(q, topk=3)
                results.extend(rs)
                traces.append(ToolTrace(step=2, action="search", args={"query": q}, ok=True, latency_ms=int((time.time() - t) * 1000)))
            except Exception as e:
                traces.append(ToolTrace(step=2, action="search", args={"query": q}, ok=False, error=str(e)))
                continue
    except Exception as e:
        traces.append(ToolTrace(step=2, action="get_adapter", args={}, ok=False, error=str(e)))

    # Step 3: evidence
    evidence = _assemble_evidence(results, claim_text) if results else []

    # Step 4: policy
    policy = evaluate_evidence_credibility([e.credibility or "web" for e in evidence])

    # Step 5: optional LLM reasoning
    llm_reasons: List[str] = []
    llm_score = None
    try:
        llm_reasons, llm_score = reason_claim(claim_text, [e.model_dump() for e in evidence])
    except Exception:
        llm_reasons, llm_score = [], None

    reasons: List[str] = []
    binary = "unknown"
    if policy.sufficient:
        reasons.append("发现权威/登记类来源，但需进一步核验；暂返回 unknown")
    else:
        if policy.limited_trust:
            reasons.append("仅一般网页来源，可信度有限")
        else:
            reasons.append("权威来源不足或不可访问")

    if llm_reasons:
        reasons = llm_reasons[:4] + reasons[:1]

    audit = AuditInfo(generated_at=_now_iso(), tool_traces=traces, usage=Usage(duration_ms=None))
    return Judgment(kind=output_kind, binary=binary, reasons=reasons, evidence=evidence, audit=audit)
