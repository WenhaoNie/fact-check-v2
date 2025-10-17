from __future__ import annotations

import time
from typing import Any, Dict, List

from lib.logging import get_logger
from lib.search_adapter import get_search_adapter, SearchResult
from lib.query_strategy import generate_queries
from lib.evidence_utils import tag_credibility, best_excerpt
from lib.policy import evaluate_evidence_credibility
from models.schemas import EvidenceItem, Judgment
from models.audit import AuditInfo, ToolTrace, Usage


logger = get_logger(__name__)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _assemble_evidence(results: List[SearchResult], claim_text: str) -> List[EvidenceItem]:
    # Placeholder: we only have search results (no page fetch). Use snippet as quote.
    items: List[EvidenceItem] = []
    for r in results[:1]:  # keep minimal evidence for MVP
        cred = tag_credibility(r.url)
        items.append(
            EvidenceItem(
                url=r.url,
                title=r.title or r.url,
                quote=r.snippet or best_excerpt(r.title or "", [claim_text]),
                fetched_at=_now_iso(),
                credibility=cred,
            )
        )
    return items


def run(input_payload: Dict[str, Any], output_kind: str = "both") -> Judgment:
    """Natural-language text pipeline.

    Best-effort structure that tolerates missing adapter implementation and
    returns `unknown` with reasons when evidence cannot be gathered.
    """
    claim_text: str = input_payload.get("claim_text") or input_payload.get("text") or ""
    locale: str = input_payload.get("locale") or "auto"
    subject: str = input_payload.get("subject") or ""

    traces: List[ToolTrace] = []
    results: List[SearchResult] = []

    # Step 1: generate queries
    t0 = time.time()
    queries = generate_queries(claim_text, locale=locale, subject=subject or None)
    traces.append(
        ToolTrace(step=1, action="generate_queries", args={"n": len(queries)}, ok=True, latency_ms=int((time.time() - t0) * 1000))
    )

    # Step 2: search
    try:
        adapter = get_search_adapter()
        for i, q in enumerate(queries, start=1):
            t = time.time()
            try:
                rs = adapter.search(q, topk=3)
                results.extend(rs)
                traces.append(
                    ToolTrace(step=2, action="search", args={"query": q}, ok=True, latency_ms=int((time.time() - t) * 1000))
                )
            except NotImplementedError as e:  # adapter not ready yet
                traces.append(
                    ToolTrace(step=2, action="search", args={"query": q}, ok=False, error=str(e))
                )
                break
            except Exception as e:  # conservative: mark failed
                traces.append(
                    ToolTrace(step=2, action="search", args={"query": q}, ok=False, error=str(e))
                )
                continue
    except Exception as e:
        traces.append(ToolTrace(step=2, action="get_adapter", args={}, ok=False, error=str(e)))

    # Step 3: assemble evidence (no fetch yet)
    evidence = _assemble_evidence(results, claim_text) if results else []

    # Step 4: apply evidence policy
    policy = evaluate_evidence_credibility([e.credibility or "web" for e in evidence])

    reasons: List[str] = []
    binary = None
    if policy.sufficient:
        # Without LLM reasoning and full fetch, we cannot assert yes/no reliably
        # Use conservative default to unknown until full pipeline exists.
        binary = "unknown"
        reasons.append("证据收集流程未完成；保守返回 unknown")
    else:
        binary = "unknown"
        if policy.limited_trust:
            reasons.append("仅一般网页来源，可信度有限")
        else:
            reasons.append("权威来源不足或不可访问")

    audit = AuditInfo(generated_at=_now_iso(), tool_traces=traces, usage=Usage(duration_ms=None))
    judgment = Judgment(kind=output_kind, binary=binary, reasons=reasons, evidence=evidence, audit=audit)
    return judgment
