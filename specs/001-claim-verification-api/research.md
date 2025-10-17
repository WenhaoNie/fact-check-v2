# Phase 0 Research – Claim Verification API (Structured Judgments)

Date: 2025-10-17  
Branch: 001-claim-verification-api  
Spec: /Users/wenhaonie/fact-check-v2/specs/001-claim-verification-api/spec.md

## Summary of Decisions

- Language/Version: Python 3.11
- Dependencies: httpx (HTTP), pydantic (schema validation), pytest (tests)
- Search Provider: Brave (base tier); read API key from /keys (e.g., BRAVE_API_KEY file or env)
- API Auth: API Key per account/project (header `X-API-Key`)
- Evidence Policy: ≥1 authoritative source required; otherwise allow general news with "可信度有限" note; unknown if none
- Score Semantics: 0–1 as calibrated "真实性概率" with periodic calibration (quarterly)
- Query Strategy: Balanced (support/refute/neutral) query generation
- Reliability: Rate limit + exponential backoff (≤2 retries); cache search/fetch results when safe
- Cost/Performance: Prompt cache optional (enable when provider supports); quality over latency/cost
- Compliance: Respect robots/ToS; unknown if restricted; domain allow/deny and source priority
- Auditability: Include tool_traces, evidence details, timestamps, usage summary

## Decisions, Rationale, Alternatives

### 1) Language/Version
- Decision: Python 3.11
- Rationale: Matches repo guidance (lightweight scripts), rich HTTP/JSON ecosystem; easy testing.
- Alternatives: Node 20 (JS ecosystem), Go 1.22 (performance); rejected to keep alignment with repo patterns and faster iteration.

### 2) Primary Dependencies
- Decision: httpx for HTTP, pydantic for JSON schema validation; keep core minimal (no heavy orchestration frameworks).
- Rationale: Constitution requires lightweight implementation; provider-agnostic integration.
- Alternatives: requests (less async-friendly), FastAPI (adds framework scope not required for spec), LangChain/LlamaIndex (overkill per constitution).

### 3) API Authentication
- Decision: API Key via `X-API-Key` header; per-project keys with quota and audit at key granularity.
- Rationale: Simple B2B integration; spec favors quality and auditability.
- Alternatives: OAuth2 Client Credentials (heavier integration); internal-only IP allowlist (limits external use).

### 4) Evidence Policy
- Decision: Require ≥1 authoritative source; allow general news/blog when flagged as "可信度有限"; conflict/insufficient → return `unknown`.
- Rationale: Balances coverage and credibility in Chinese/English web contexts.
- Alternatives: Require ≥2 authority sources (higher precision, lower recall); or accept aggregators as authority (risk of circular verification).

### 5) 0–1 Continuous Score & Calibration
- Decision: Interpret as calibrated probability of truth. Maintain small benchmark set; perform quarterly calibration; publish threshold guidance (e.g., 0.5 default).
- Rationale: Enables threshold-based decisions and comparability across claims.
- Alternatives: Evidence support score (heuristic, less comparable); 5-level discrete mapped to 0–1 (stable, less granular).

### 6) Balanced Search Strategy & Provider
- Decision: For each claim, generate queries for support/refute/neutral; merge and deduplicate results; rank with simple heuristics favoring authority domains.
- Rationale: Reduces selection bias; aligns with constitution.
- Alternatives: Single best-effort query (risk of bias and omission).
  
- Decision: Use Brave Search (base tier) by default.
- Rationale: User preference; cost-effective; sufficient for MVP.
- Alternatives: SerpAPI/Exa; keep adapters provider-agnostic for later swap.

### 7) Reliability & Rate Limiting
- Decision: Global rate limiter; exponential backoff (≤2 retries) for transient failures; cache idempotent search/fetch responses with TTL.
- Rationale: Constitution mandates rate limiting/backoff and caching on search/fetch.
- Alternatives: Aggressive retries (risks ToS/robots), no caching (worse performance and cost).

### 8) Cost/Performance & Prompt Cache
- Decision: Treat prompt cache as optional; enable when provider supports; otherwise reduce context via templates and reuse.
- Rationale: Constitution updated to "可选" per provider capability.
- Alternatives: Hard dependency on provider-specific cache (breaks portability).

### 9) Compliance & Safety
- Decision: Respect robots/ToS; apply domain allow/deny lists; prefer authority/registry sources; sanitize logs; return `unknown` if compliance blocks evidence.
- Rationale: Constitution safety and compliance gate.
- Alternatives: Ignore robots in research mode (violates policy).

### 10) Auditability & JSON Output
- Decision: Include `tool_traces`, evidence list (URL+quote+title/source), reasons, summary usage and timing; no chain-of-thought in final output.
- Rationale: Constitution requires strict JSON and audit trail; prevent thought leakage.
- Alternatives: Freeform text with inline links (not machine-verified; lacks audit details).

## Clarifications Status

All clarifications from the spec (FR-013..015) are resolved here; no outstanding NEEDS CLARIFICATION items remain for planning.

*** End of Research ***
