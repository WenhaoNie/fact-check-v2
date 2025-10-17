# Implementation Plan: Claim Verification API (Structured Judgments)

**Branch**: `001-claim-verification-api` | **Date**: 2025-10-17 | **Spec**: /Users/wenhaonie/fact-check-v2/specs/001-claim-verification-api/spec.md
**Input**: Feature specification from `/specs/001-claim-verification-api/spec.md`

## Summary

Expose a programmatic API that accepts a natural-language or structured claim
and returns a structured judgment: binary yes/no and/or a calibrated 0–1
probability with concise reasons and linkable evidence excerpts. The approach
follows the project constitution: ReAct-style tool orchestration (search/fetch),
strict JSON output and audit traces, provider-agnostic adapters, quality over
latency, and optional prompt caching when supported.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Lightweight core (stdlib); httpx (HTTP), pydantic (schema validation)  
**Storage**: N/A (stateless; logs/artifacts externalized by caller)  
**Testing**: pytest (unit + small end-to-end)  
**Target Platform**: Linux server/CLI; container-friendly  
**Project Type**: single  
**Performance Goals**: 90% requests complete ≤30s while maintaining evidence completeness (per spec SC-004)  
**Constraints**: Evidence-only outputs; provider-agnostic; prompt cache optional; rate limit + backoff (≤2 retries); respect robots/ToS; budgets/step limits; default search provider Brave (base tier), keys in `/keys`  
**Scale/Scope**: Initial low throughput (up to hundreds/day); single POST endpoint + CLI parity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates (from `.specify/memory/constitution.md`) and evaluation:
- ReAct orchestration; facts from tool Observations only → PASS (API returns evidence-linked judgments; unknown when insufficient)
- Plugin-first, provider-agnostic; no heavy orchestration (no complex LangChain Graph/MCP) → PASS (lightweight adapters only)
- Strict JSON + auditability (tool_traces) → PASS (response includes audit metadata; traces design-ready)
- Cost/performance discipline; prompt cache optional; rate limiting/backoff; caching of search/fetch → PASS (design includes these; cache optional)
- Quality gates & tests → PASS (unit tests for tools; e2e small set planned)
- Safety & compliance (robots/ToS, authority-first sources, domain allow/deny) → PASS (evidence policy defined; unknown on non-compliant)
- Balanced search (support/refute/neutral) → PASS (query strategy in research)
- CoV used for reasoning verification, not source replacement → PASS (optional check only)

Post-Design Re-Check: PASS (no violations introduced by contracts/data model)

## Project Structure

### Documentation (this feature)

```
specs/001-claim-verification-api/
├── plan.md              # This file (/speckit.plan)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output (OpenAPI)
```

### Source Code (repository root)

```
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Single-project layout with clear separation between
models, services, CLI, and tests. Keeps implementation lightweight and aligned
to the constitution’s plugin-first approach.

## Complexity Tracking

No violations; section intentionally empty.
