# factcheck-agent

通用“网络事实核查智能体”参考实现与脚手架（去耦合版）。

本仓库依据《web_research_agent_requirements.md》（v2）进行设计：提供一个可复用、可插拔、与具体代码库/业务领域解耦的“网络事实核查智能体”（下称“智能体”）。它接收结构化输入，自动进行网络检索与取证，并输出严格结构化的结论与证据，便于嵌入各类质量校验或审计流水线。

状态说明
- 当前仓库为最小可运行脚手架，README/接口规范已对齐需求文档；功能实现会按路线图推进。

目录
- 概述与目标
- 核心能力
- 快速开始
- 配置与环境
- 输入/输出契约
- 工具插件接口
- CLI 用法
- 缓存与日志
- 安全与合规
- 开发与测试
- 路线图
 - Docker 部署

## 概述与目标
- 目标：提供可复用、可插拔、与业务解耦的事实核查智能体，具备受控 ReAct 循环、统一工具接口、严格 JSON 输出与可审计证据链。
- 范围：后端/CLI 工具与可嵌入流水线的库；支持容器化、实时日志、可控成本；不绑定特定数据源或领域实体。
- 非目标：不构建通用爬虫平台或搜索引擎；不实现复杂浏览器自动化。

## 核心能力
- 自主研究循环：受控 ReAct 风格（Thought → Action → Observation → Final），限定最大步数后产出结构化结论。
- 工具调用：通过统一“工具插件接口”访问 SEARCH/FETCH/EXTRACT/RESOLVE/QUOTE 等能力；具体供应商/数据源通过插件注入。
- 结构化输出：严格 JSON Schema，包含结论、置信度、理由、证据（URL+引用）、可疑点、建议与过程摘要。
- 任务适配：直接消费任务 JSONL，或经“适配器”从 CSV/JSON/HTML 等生成任务并批处理。
- 去耦合模型供应商：通过 Provider Adapter 注入具体模型/厂商（鉴权、温度、步数/预算约束等）。

## 快速开始
前置依赖
- Python/Node/Go 等具体运行时待定（根据后续实现选择）。
- 可选：Docker 以便容器化运行。

基础运行（示例占位）
- 克隆仓库并安装依赖后，使用 `agent run` 执行任务 JSONL 并生成 JSONL/HTML 报告（具体命令见“CLI 用法”）。

## 配置与环境
- Provider 注入：通过环境变量或配置文件注入模型/工具供应商（不绑定具体厂商）。
  - 典型环境变量（示例）：
    - `AGENT_PROVIDER`：提供商标识（如 openai/azure/bedrock/...），可选。
    - `AGENT_PROVIDER_CONFIG`：指向 JSON/YAML 配置文件路径，描述鉴权与模型参数。
  - 低温度与 JSON 约束：建议默认温度 0.0，并启用函数调用/JSON 模式以保证确定性与可解析性。
- 约束注入：步数上限、成本/时间预算、域名白/黑名单、语言策略等由任务内 `constraints` 指定，可叠加全局默认。

## 输入/输出契约
输入（单任务 JSON；多任务为 JSONL）
```json
{
  "request_id": "可选外部ID",
  "task": {
    "name": "任务名称",
    "version": "v1",
    "goals": ["一句话目标1", "目标2"],
    "questions": [
      { "id": "Q1", "type": "binary|text|classification|extraction", "prompt": "自然语言问题或检查指令", "accept": "可选判定标准", "expected": "可选形态约束" }
    ],
    "constraints": {
      "step_limit": 6,
      "cost_budget": {"currency": "USD", "max": 0.50},
      "time_budget_s": 60,
      "sources_priority": ["authority", "registry", "web"],
      "allowed_domains": ["可选白名单"],
      "blocked_domains": ["可选黑名单"],
      "language": "zh|en|auto"
    }
  },
  "context": {
    "id": "被核查对象ID",
    "fields": {
      "title": "可选标题",
      "claims": ["可选陈述"],
      "entities": ["可选实体名"],
      "attributes": {"k": "v"},
      "urls": ["可选上下文URL"]
    },
    "hints": {"关键词": ["..."], "禁止来源": ["..."], "偏好来源": ["..."]}
  }
}
```

输出（逐任务严格 JSON；JSONL 时每行一条）
```json
{
  "request_id": "原样返回",
  "id": "context.id",
  "answers": [
    {
      "question_id": "Q1",
      "result": "yes|no|unknown|text",
      "confidence": 0,
      "reasons": ["简短要点，最多3条"],
      "evidence": [ {"source": "https://...", "quote": "摘录短句"} ],
      "missing_candidates": ["可选"],
      "suspicious_items": ["可选"],
      "tool_traces": [ {"step": 1, "action": "SEARCH|FETCH|EXTRACT|RESOLVE|QUOTE", "args": {}, "ok": true, "latency_ms": 1200} ],
      "errors": ["错误摘要（若有）"]
    }
  ],
  "summary": { "steps_used": 4, "tokens_prompt": 0, "tokens_completion": 0, "cost": {"currency":"USD","amount":0.0}, "duration_ms": 0 }
}
```

## 工具插件接口（示例约定）
- SEARCH(query, topk, site?): 站内/全网搜索；由外部搜索插件提供。
- FETCH(url): 抓取 URL 内容（超时、压缩、HTML 清洗、可配置 robots 策略）。
- EXTRACT(text, schema?): 从文本中进行结构化抽取（可由 LLM 或规则实现）。
- RESOLVE(name, namespace?): 实体规范化/对齐（由可插拔注册表/字典提供）。
- QUOTE(text, pattern): 从文本中抽取证据片段。
- STOP(): 输出最终 JSON。

实现建议
- 每个工具作为独立插件，通过统一接口注册/调用；错误、超时与重试应被宿主管理（指数退避≤2次）。

## CLI 用法（示例）
- 直接任务运行：
  - `agent run --tasks tasks.jsonl --out-jsonl out.jsonl --out-html out.html`
- 结果适配采样：
  - `agent sample --src results.html --n 150 --seed 42 | agent run --out-jsonl fc.jsonl --out-html fc.html`

注：上述命令为接口占位，具体参数名称与行为以后续实现为准，但会保持与需求文档一致的语义。

## 缓存与日志
- 缓存：对重复 URL/查询的抓取与解析做本地缓存（可配置存储、TTL）。
- 实时标准输出：
  - `[agent] i/N id=… step=… act=SEARCH args=…`
  - `[observe] status=200 bytes=… from=FETCH url=…`
  - `[summary] processed=X errors=Y cost=… tokens=…`
- 结构化日志（可选）：NDJSON/JSONL 持久化 tool_traces 与错误，便于回溯与分析。

## 安全与合规
- 来源策略：来源优先级与域名白/黑名单可配置；默认优先权威来源。
- 抓取策略：尊重 robots 协议（策略可调）；频率限制与退避机制。
- 密钥安全：不记录敏感信息；遵循外部站点服务条款与合规要求。
- 输出纪律：Final 仅引用工具 Observation 的来源与摘录；证据不足应返回 `unknown` 并说明原因。

## 开发与测试
- 单元测试建议：
  - 工具执行器（SEARCH/FETCH/EXTRACT/RESOLVE/QUOTE）的接口契约、错误路径与超时重试。
  - 智能体循环：步数上限、失败降级为 unknown、严格 JSON 输出。
- 集成测试建议：
  - 小样本端到端（n≈20）：验证实时日志、证据链接有效、报告生成。
- 验收指标：
  - 成本/时延在约束内（触达预算时提前停止并输出 partial）。
  - 输出 JSON 100% 合规；无“思考”泄漏到 Final。

## 路线图
- MVP（v1）
  - 智能体循环、工具插件接口、任务 JSONL 输入、JSON/HTML 输出、缓存与实时日志。
  - 适配器：从通用结果文件采样生成任务。
- v1.1
  - 并发与速率控制；失败重试与指数退避；更多插件示例（多搜索源/多解析器）。
- v2
  - 插件热插拔加载；跨任务共享记忆（缓存/知识片段）；结果对比与趋势分析。

## 许可证
本仓库尚未声明许可证。如需在生产环境使用，请先在组织内部明确许可策略。

## Docker 部署
- 构建镜像：
  - `docker compose build`
- 配置密钥：
  - 将密钥放入 `secrets/.env`（参考 `secrets/.env.example`）或设置 `AGENT_PROVIDER_CONFIG` 指向配置文件。
- 运行校验：
  - `docker compose run --rm agent verify --online`
- 运行任务：
  - `docker compose run --rm agent run --tasks /examples/tasks_min.jsonl --out-jsonl /data/out.jsonl --out-html /data/out.html`
  - 可选导出用量统计：追加 `--out-usage-json /data/usage.json`
- 开发（热更新）环境：
  - 启动 dev 容器：`docker compose up -d dev`
  - 进入：`docker compose exec dev bash`
  - 容器内已执行 `pip install -e .`，可直接运行：`agent verify --online`

### 搜索供应商选择与限流
- 选择搜索供应商（当同时配置 SerpAPI 与 Brave 时）：设置环境变量 `SEARCH_PROVIDER=serpapi|brave`。
- Free/付费套餐限流：可通过环境变量或 `/secrets/*.txt` 文件声明 tier 与限额（RPS、单次运行最大请求数等）。示例参见 `configs/providers.example.toml` 与 `docker/entrypoint.sh`。

### 一键在线验收脚本
- 使用 `scripts/accept_online.sh` 在 Docker 内依次对搜索/LLM 进行连通性与端到端验证，生成 JSONL/HTML 与 usage JSON：
  - `scripts/accept_online.sh --providers "google volcengine openai" --search "serpapi brave" --tasks examples/tasks_min.jsonl --topk 1 --max-steps 3 --tier free`

### 多供应商对比运行
- 使用新命令同时在多个 LLM 供应商上运行同一任务集并生成对比报告：
  - `agent providers --tasks examples/tasks_medical.jsonl --out-dir outputs/med_multi`
  - 默认运行 `openai,google,volcengine` 三家，输出每家各自的 JSONL/HTML 以及 `compare_providers.html` 多列对比报告（深色主题，显示 provider:model）。

### 样例任务
- `examples/tasks_ambiguous.jsonl`：语义模糊的 10 道题
- `examples/tasks_medical.jsonl`：医药类 10 道较为模糊的问题（需结合权威来源判读）
