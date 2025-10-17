# Quickstart – Claim Verification API

Date: 2025-10-17  
Branch: 001-claim-verification-api

## Overview
Submit a natural-language or structured claim via HTTP and receive a structured
judgment with reasons and evidence. Quality over latency; when evidence is
insufficient or restricted, the system returns `unknown` with explanation.

## Authentication
- Header: `X-API-Key: <your-api-key>`
- Unauthorized requests return `401 Unauthorized`.

## Endpoint
- POST `/v1/verify`
- OpenAPI: /Users/wenhaonie/fact-check-v2/specs/001-claim-verification-api/contracts/openapi.yaml

## Provider Keys & Search Provider
- Keys location: `/keys` (provided by user). Example: `/keys/BRAVE_API_KEY` for Brave.
- Default search provider: Brave (base tier). Set `SEARCH_PROVIDER=brave` if needed.
- Alternatively, export environment variables mapping to the key file.

## Request Examples

Natural language input:
```bash
curl -sS -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: $API_KEY' \
  https://api.example.com/v1/verify \
  -d '{
    "input": {"type": "text", "claim_text": "公司A在2024年Q4营收同比增长超20%", "time_window": "2024Q4", "locale": "zh"},
    "output": {"kind": "both"}
  }'
```

Structured input:
```bash
curl -sS -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: $API_KEY' \
  https://api.example.com/v1/verify \
  -d '{
    "input": {"type": "structured", "claim": {"subject": "Company A", "text": "Revenue YoY growth > 20%", "time_window": "2024-10-01..2024-12-31", "locale": "en"}},
    "output": {"kind": "continuous"}
  }'
```

## Response Example
```json
{
  "judgment": {
    "kind": "both",
    "binary": "yes",
    "score": 0.83,
    "reasons": [
      "权威财报披露Q4营收同比+23%",
      "行业报道与公司公告一致"
    ],
    "evidence": [
      {
        "url": "https://sec.example/filings/abc/q4",
        "title": "Company A FY2024 Q4 Report",
        "quote": "Revenue increased by 23% YoY in Q4",
        "fetched_at": "2025-10-17T08:00:00Z",
        "credibility": "authority"
      }
    ],
    "audit": {
      "generated_at": "2025-10-17T08:00:02Z",
      "tool_traces": [],
      "usage": {"tokens_prompt": 0, "tokens_completion": 0, "duration_ms": 2000}
    }
  }
}
```

## Notes
- Evidence policy: At least one authoritative source preferred; otherwise results include a "可信度有限" note; insufficient/conflicting evidence returns `unknown`.
- Compliance: Respects `robots`/ToS. If access is restricted, response explains and may be `unknown`.
- Reliability: Global rate limit with exponential backoff (≤2 retries). Caches search/fetch responses safely.
- Cost/Performance: Prompt cache is optional and enabled only when supported by the provider.

*** End of Quickstart ***
