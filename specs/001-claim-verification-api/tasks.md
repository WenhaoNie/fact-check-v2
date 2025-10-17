---
description: "Task list for Claim Verification API (Structured Judgments)"
---

# Tasks: Claim Verification API (Structured Judgments)

**Input**: Design documents from `/specs/001-claim-verification-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included per user request (TDD). Write tests first in each user story phase; ensure they FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

 - [X] T001 Create project structure per implementation plan (src/, src/models/, src/services/, src/cli/, src/lib/, tests/contract/, tests/integration/, tests/unit/)
 - [X] T002 Initialize Python project with minimal dependencies in `pyproject.toml` (pydantic, httpx)
 - [X] T003 [P] Create logging configuration utility in `src/lib/logging.py` (info/debug levels, redact secrets)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

 - [X] T004 Implement Pydantic schemas for Claim/Evidence/Judgment in `src/models/schemas.py` (align with data-model.md)
 - [X] T005 [P] Implement audit/usage trace models in `src/models/audit.py` (generated_at, tool_traces, usage)
 - [X] T006 [P] Define provider-agnostic search adapter + factory in `src/lib/search_adapter.py` (search(query, topk, site)); include Brave adapter skeleton (read `/keys/BRAVE_API_KEY`, base tier default)
 - [X] T007 [P] Implement HTTP fetcher in `src/lib/fetcher.py` (timeouts, robots/ToS flags)
 - [X] T008 [P] Implement balanced query strategy generator in `src/lib/query_strategy.py` (support/refute/neutral variants)
 - [X] T009 [P] Implement evidence utilities in `src/lib/evidence_utils.py` (credibility tagging, excerpt extraction)
 - [X] T010 [P] Implement API key auth utilities in `src/lib/auth.py` (validate `X-API-Key`, quota hooks)
 - [X] T011 [P] Implement rate limit/backoff wrappers in `src/lib/retry.py` (≤2 retries, exponential backoff)
 - [X] T012 Implement `VerificationService.verify_claim()` skeleton in `src/services/verification_service.py` (input dispatch, output mapping)
 - [X] T013 Implement evidence policy in `src/lib/policy.py` (≥1 authority or flag "可信度有限"; else `unknown`)
 - [X] T014 Implement scoring calibrator in `src/lib/calibration.py` (pluggable calibrate(score), quarterly calibration hook)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 提交自然语言事实并获取结构化结论 (Priority: P1) 🎯 MVP

**Goal**: 接收自然语言陈述，返回结构化判断（yes/no 或 0–1），附理由与证据；证据不足时返回 `unknown`。

**Independent Test**: 通过单一接口提交一句自然语言陈述，响应包含结论、理由、≥1条证据（链接+摘录）；证据不足时为 `unknown` 并含原因。

 - [X] T015 [P] [US1] Contract test for POST /v1/verify (text input) in `tests/contract/test_verify_text.py`
 - [X] T016 [P] [US1] Integration test for natural language flow in `tests/integration/test_text_flow.py`
 - [X] T017 [US1] Implement text→Claim normalization pipeline in `src/services/pipeline_text.py` (locale, time_window handling)
 - [X] T018 [US1] Integrate query strategy + search + fetch + evidence assembly in `src/services/pipeline_text.py`
 - [X] T019 [US1] Implement `unknown` fallback & reason mapping in `src/services/pipeline_text.py`
 - [X] T020 [P] [US1] Wire `VerificationService.verify_claim()` to text pipeline in `src/services/verification_service.py` (output kind=both)
 - [X] T021 [US1] Implement API handler for text input in `src/services/api_handlers.py` (validate against contracts/openapi.yaml)
 - [X] T022 [P] [US1] Implement CLI entry `verify` in `src/cli/verify.py` (read stdin JSON, print JSON)

**Checkpoint**: User Story 1 independently functional (API/CLI both return structured judgments for text input)

---

## Phase 4: User Story 2 - 提交结构化事实对象以支持批量与一致性 (Priority: P1)

**Goal**: 接收结构化事实对象，输出字段化、与输入对齐的判断结果。

**Independent Test**: 提交结构化载荷，返回字段齐全、类型正确的判断对象，证据/理由/结论齐备。

 - [X] T023 [P] [US2] Contract test for POST /v1/verify (structured input) in `tests/contract/test_verify_structured.py`
 - [X] T024 [P] [US2] Integration test for structured flow in `tests/integration/test_structured_flow.py`
 - [X] T025 [US2] Implement structured pipeline in `src/services/pipeline_structured.py` (field validation & normalization)
 - [X] T026 [P] [US2] Ensure response alignment with input fields in `src/services/verification_service.py` (subject, time_window)
 - [X] T027 [US2] Extend API handler to support `type=structured` in `src/services/api_handlers.py`

**Checkpoint**: User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - 获取连续0-1评分与可解释理由 (Priority: P2)

**Goal**: 在需要时返回0–1连续真实性概率（经校准），并可选返回二元结论与可解释理由。

**Independent Test**: 对相同陈述多次调用，评分与理由小幅波动且不改变主要结论；响应包含审计元信息。

- [ ] T028 [P] [US3] Contract test for continuous scoring in `tests/contract/test_verify_continuous.py`
- [ ] T029 [P] [US3] Integration test for score consistency in `tests/integration/test_continuous_consistency.py`
- [ ] T030 [US3] Implement calibrated continuous scoring flow in `src/services/verification_service.py` (use `src/lib/calibration.py`)
- [ ] T031 [P] [US3] Update API handler to support `output.kind=continuous` in `src/services/api_handlers.py`
- [ ] T032 [US3] Add consistency smoothing utilities in `src/lib/consistency.py` and integrate in `src/services/verification_service.py`
- [ ] T033 [US3] Update evidence policy/threshold guidance in `src/lib/policy.py` (document default threshold e.g. 0.5)

**Checkpoint**: All user stories independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T034 [P] Update Quickstart with final examples in `specs/001-claim-verification-api/quickstart.md`
- [ ] T035 Code cleanup and refactoring across `src/`
- [ ] T036 Performance tuning across `src/lib/*` (batching, request merging, cache where safe)
- [ ] T037 Security hardening in `src/lib/auth.py` and `src/lib/logging.py` (redaction, error handling)
- [ ] T038 Run Quickstart validation steps in `specs/001-claim-verification-api/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies
- Foundational (Phase 2): Depends on Setup completion — BLOCKS all user stories
- User Stories (Phase 3+): All depend on Foundational; proceed in priority order or parallel where capacity allows
- Polish (Final): Depends on desired user stories being complete

### User Story Dependencies

- User Story 1 (P1): Can start after Foundational; no dependency on US2/US3
- User Story 2 (P1): Can start after Foundational; independent of US1 but shares VerificationService
- User Story 3 (P2): Can start after Foundational; independent of US1/US2, consumes Calibration

### Within Each User Story

- Models/schemas and adapters before service wiring
- Service orchestration before API handler/CLI
- Unknown fallback and policy application before declaring story complete

### Parallel Opportunities

- Phase 2: T005–T011 can proceed in parallel (distinct files)
- US1: T018 and T020 can proceed in parallel once T016 completes
- US2: T022 can proceed in parallel with T021 after schemas are ready
- US3: T025 can proceed in parallel with T024 after service hooks exist

---

## Parallel Example: User Story 1

```bash
# After T018 completes (evidence assembly ready), run these in parallel:
Task: "T020 [US1] Wire verify_claim to text pipeline in src/services/verification_service.py"
Task: "T022 [US1] Implement CLI entry verify in src/cli/verify.py"
```

---

## Implementation Strategy

- MVP scope: Deliver User Story 1 (text input → structured judgment via API/CLI) with auditability.
- Next: Add User Story 2 (structured claims) for consistency and batch scenarios.
- Then: Add User Story 3 (calibrated 0–1 probability) to support thresholding and ranking.
