# FactCheck-Agent v2 Constitution

<!--
Sync Impact Report
- Version change: 1.0.0 → 2.0.0
- Modified principles:
  - IV. 成本与性能纪律（Cost & Performance Discipline）: 强制“提示缓存” → “可选，按供应商支持优先启用，并提供降级策略”；补充当前供应商列表（OpenAI、Google、火山引擎）。
- Added sections:
  - Governance: 明确版本策略（SemVer: MAJOR/MINOR/PATCH）。
  - Governance: 合规评审期望（节奏与触发条件）。
- Removed sections:
  - 无
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md（已核对，无需修改）
  - ✅ .specify/templates/spec-template.md（已核对，无需修改）
  - ✅ .specify/templates/tasks-template.md（已核对，无需修改）
  - ⚠ .specify/templates/commands/*.md（目录不存在，暂无需处理）
- Runtime docs review:
  - ✅ readme_version_1.md（仅描述性“缓存与日志”，与宪章不冲突）
  - ✅ reference_doc.md（强调“优先/关键优化”，非强制用语，与“可选”不冲突）
  - ✅ discussion_notes_2025-01-15.md（会议记录，非规范文件）
- Deferred TODOs:
  - 无（Ratified date已知；供应商列表来自用户输入）
-->

## Core Principles

### I. 工具优先，证据为先（ReAct-Orchestrated, Evidence-Only）
- LLM 仅作为编排器执行受控 ReAct 循环（Thought → Action → Observation → Final），事实必须来自工具 Observation，不得凭模型记忆臆断。
- 最终输出只允许引用来自工具返回的来源与摘录；证据不足返回 `unknown`，不得强行给结论。
- 强约束：步数上限、成本/时间预算、域名白/黑名单、来源优先级（权威/注册表/网页）。

### II. 插件化与去耦合（Plugin‑First, Provider‑Agnostic）
- 功能通过统一“工具插件接口”注入，包含 `SEARCH`/`FETCH`/`EXTRACT`/`RESOLVE`/`QUOTE`/`STOP`；插件单一职责、可替换、可并行。
- 模型/搜索/抓取供应商通过 Provider Adapter 注入，避免供应商锁定；默认低温度与 JSON/函数调用模式以保证可解析性与确定性。
- 当前阶段明确不引入重型编排框架（如复杂 LangChain Graph）与 MCP 体系，保持实现轻量、清晰、可维护。

### III. 结构化输出与可审计（Strict JSON, Auditability）
- 严格 JSON Schema 输出：结论、置信度、理由要点、证据（URL+引用）、缺失候选、可疑点、过程摘要。
- 全过程可追溯：保留 `tool_traces`（步骤、参数、耗时、错误），支持离线审计与复现。
- 输出纪律：禁止思维链泄漏到 Final；所有断言需可溯源到证据片段。

### IV. 成本与性能纪律（Cost & Performance Discipline）
- 提示缓存为可选：若所用大模型提供商支持（如 Anthropic Claude 3.7），则应优先启用以降低成本与延迟；若不支持（当前使用的提供商为 OpenAI、Google、火山引擎），则采用降级策略（精简上下文、批处理、请求合并、重用本地模板），避免将其设为强制依赖。
- 统一速率限制与重试策略（指数退避≤2次），对搜索/抓取结果启用缓存（如 Redis），遵守对方站点 robots 与服务条款。
- 每次运行输出用量与成本统计；当触达预算或时限时提前停止并输出 partial。

### V. 质量门禁与测试（Quality Gates & Tests）
- 单元测试覆盖工具执行器的接口契约、错误路径与超时重试；集成测试小样本端到端验证（证据链接有效、报告生成、实时日志）。
- 推理质量风险的工程缓解：数学计算校验、证据完整性检查、限定词丢失检测；对一致性低样本标记人工复核。
- 版本化的输入/输出契约（Schema 变更需显式版本升级与迁移说明）。

## 体系约束与安全

- 架构基线采用 README v1（轻量 ReAct + 插件接口）；逐步吸收 Reference Doc 的精华能力，禁止一次性引入过度工程化方案。
- 近期不引入 MCP、深度 SPUQ/保形预测等重学术/重运维组件；Chain‑of‑Verification 用于“推理正确性验证”，而非替代证据检索。
- 搜索策略需“平衡查询”：面向支持/反驳/中立三个方向生成与评估，显式避免选择性偏见与语义曲解。
- 安全与合规：密钥不落盘；日志脱敏；尊重 robots；遵守来源站点 ToS；默认优先权威来源与注册表数据；支持域名白/黑名单与来源优先级策略。

## 开发流程与评审

- 工作流（建议节奏）：
  - Phase 1（MVP, 1‑4 周）：ReAct 循环、插件接口、任务 JSONL、JSON/HTML 输出、缓存与实时日志、Docker/CLI。
  - Phase 2（推理增强, 5‑6 周）：数学/完整性/限定词校验；平衡查询生成；一致性采样与低一致性标注复核。
  - Phase 3（成本优化, 7‑8 周）：提示缓存（若支持）、批处理 API、查询与抓取缓存、速率控制。
  - Phase 4（可选, 9‑12 周）：行业插件（金融等）、三层解释系统、对比多供应商运行。
- 评审与质量门槛：
  - 所有 PR 必须附最小可复现实例与测试；新增工具需含错误与超时场景测试；`agent verify --online` 通过后方可合入。
  - JSON Schema 变更需：版本号变更、迁移指南、向后兼容层（若可）。
  - 性能/成本相关改动需包含用量对比与回滚计划。

## Governance

- 本宪章高于其他工程实践；与之冲突的流程/实现必须调整以符合本宪章。
- 关键决策（自 2025‑01‑15 讨论）：
  - ✅ 采用 README v1 架构作为基础；逐步增强。
  - ✅ 提示缓存为可选；若供应商支持则优先启用；三层解释系统自 v1.1 起实施。
  - ✅ Chain‑of‑Verification 用于推理验证，不替代事实来源。
  - ❌ 暂不采用 MCP/复杂 LangChain 编排；❌ 暂不实施 SPUQ/保形预测。
- 修订流程：
  - 任何破坏性变更（工具接口/JSON Schema/执行模型）需提交轻量 RFC（问题‑方案‑影响‑迁移），获评审通过并附迁移计划。
  - 修订记录需更新本文件的版本与日期，并在变更日志中登记。
 - 版本策略（SemVer）：
   - MAJOR：破坏性治理/原则变更（移除或重新定义硬约束）。
   - MINOR：新增原则/章节或显著扩展指导但保持向后兼容。
   - PATCH：澄清、措辞调整、排版修复，不改变语义。
 - 合规评审：
   - 触发：每季度一次，或发布前，或引入/替换供应商（如从 OpenAI 切换到 Anthropic/Google/火山引擎）。
   - 内容：抽查工具轨迹可审计性、JSON Schema 合规、成本与速率限制策略、来源合规（robots/ToS）。

**Version**: 2.0.0 | **Ratified**: 2025-01-15 | **Last Amended**: 2025-10-17
