# Data Model – Claim Verification API

Date: 2025-10-17  
Branch: 001-claim-verification-api

## Entities

### Claim（陈述）
- Fields:
  - `id` (string, optional): client-provided identifier
  - `subject` (string, optional): 实体/主题名称（公司、组织、人物等）
  - `text` (string, required for natural language input): 自然语言断言
  - `time_window` (string, optional): 时间范围，如 `2024Q4`、`2024-10-01..2024-12-31`
  - `locale` (enum: `zh`, `en`, `auto`; default `auto`)
  - `notes` (string, optional): 备注
- Validation:
  - 至少存在 `text` 或结构化字段组合可构成断言（subject + notes 等不得为空全部）
  - `time_window` 若存在需符合格式（单点或区间）

### Evidence（证据项）
- Fields:
  - `url` (string, required): 可点击来源链接（http/https）
  - `title` (string, required): 页面或文档标题/来源名
  - `quote` (string, required): 与断言直接相关的摘录片段
  - `fetched_at` (string, ISO datetime, required): 抓取时间
  - `credibility` (enum: `authority`, `registry`, `web`, `limited`; optional): 来源类型或可信度标记
- Validation:
  - `url` 必须可解析为 http/https
  - `quote` 非空且与理由要点一致

### Judgment（判断）
- Fields:
  - `kind` (enum: `binary`, `continuous`, `both`; default `both`)
  - `binary` (enum: `yes`, `no`, `unknown`, optional)
  - `score` (number, [0,1], optional): 真实性概率（经校准）
  - `reasons` (string[2..5], required): 简明理由要点
  - `evidence` (Evidence[], required, len>=1 unless `unknown`)
  - `missing_candidates` (string[], optional)
  - `suspicious_items` (string[], optional)
  - `audit` (object, required):
    - `generated_at` (ISO datetime)
    - `tool_traces` (array of trace objects)
    - `usage` (object: tokens/cost/duration)
- Validation:
  - 当 `binary` ∈ {`yes`,`no`} 时，`evidence` 长度≥1
  - 当仅有一般网页来源时，需在理由或`credibility`中标注“可信度有限”
  - 当证据冲突或不足时，`binary=unknown` 且包含原因说明

## Relationships
- A `Judgment` references one logical `Claim` and includes one or more `Evidence` items.
- `Evidence.credibility` guides reason phrasing and fallback to `unknown` when insufficient.

## State & Transitions
- `pending` → `evaluating` → `judged`
  - On transient failures (rate limit/network): retry (≤2) with backoff; otherwise fail with actionable error
  - When compliance blocks access (robots/ToS): return `unknown` with compliance reason

*** End of Data Model ***

