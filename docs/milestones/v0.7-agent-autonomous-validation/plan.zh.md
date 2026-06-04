# v0.7 Agent Autonomous Validation 实现计划

状态：计划完成 / 待实现

## 实现目标

交付一套可审计的 Agent 自主验证闭环：

- 有基础 E2E / UI smoke 验证。
- 有 Agent 自主操作流程。
- 有详细操作日志。
- 有 evidence bundle 关联。
- 有另一个 Agent 的只读复核流程。
- 有人工验证交接清单。
- 有 WorldEngine LLM provider 前置评估边界。

## 任务

### 1. v0.7 里程碑文档和路由

创建：

```text
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.md
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.md
docs/milestones/v0.7-agent-autonomous-validation/review.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/.gitkeep
docs/agent-guides/validation-workflow.zh.md
docs/agent-guides/validation-workflow.md
```

更新：

```text
AGENTS.md
AGENTS.zh.md
docs/README.zh.md
docs/roadmap.zh.md
docs/agent-guides/routing.md
docs/agent-guides/routing.zh.md
docs/agent-guides/workflow.md
docs/agent-guides/workflow.zh.md
```

要求：

- 明确 v0.7 是 Agent 自主验证和人工验证交接 milestone。
- 自主验证、Agent 复核和人工验证必须区分结论。
- 完整计划必须覆盖 WorldEngine public contract、operation log、浏览器 flow、
  第二 Agent 复核和人工验证交接。
- `implementation-task-plan.zh.md` 必须把后续开发拆成可逐项提交的任务。
- 报告模板必须固定 Codex 自主验证、第二 Agent 复核和人工验证的结论枚举。
- `autonomous-validation-runbook.zh.md` 必须定义真实运行当天的服务启动、preflight、
  命令测试、浏览器 flow、日志、evidence bundle、第二 Agent 和人工入口顺序。
- `cross-repo-validation-gate-matrix.zh.md` 必须定义 WorldEngine、Validation
  Client、Codex、第二 Agent 和人工验证的不可跳关门禁、证据、结论枚举和 stop
  rules。
- `planning-readiness-checklist.zh.md` 必须明确计划是否已可交给后续聊天执行、
  当前唯一允许的下一步、仍未完成的工作和 stop rules。
- `handoff-status.zh.md` 必须用单页摘要记录当前等待的 gate、owner、blocker、
  禁止事项和唯一允许的下一步。
- `next-chat-quickstart.zh.md` 必须提供后续聊天可复制的分阶段 `/goal` prompts。
- 路由支持 `自主验证 v0.7`、`Agent 验证 v0.7`、`人工验证 v0.7`。
- 不授权任何 runtime / API / UI / test 实现。

验证：

```bash
git diff --check
```

### 2. WorldEngine LLM provider 前置评估

创建或更新后续实现文档时，应补充 provider preflight 能力。当前计划只定义评估
要求，不实现 provider。

评估项：

- WorldEngine 是否配置 provider。
- WorldEngine 是否能通过 public health / manifest / OpenAPI 暴露 provider 可用性
  摘要。
- WorldEngine 是否能隐藏 API key 和 provider secret。
- WorldEngine 是否能记录公开 evaluator output 或明确 unavailable warning。

候选方案：

1. Kimi Code subscription / `kimi-for-coding`
   - 适合开发和 Agent 工具场景。
   - 官方说明支持 OpenAI / Anthropic compatible endpoint。
   - 额度按会员和窗口限制，不是普通产品调用的 pay-as-you-go 形态。
   - 如果用于 WorldEngine runtime，需要先确认条款、稳定性和是否适合作为产品内
     LLM provider。
2. Kimi Platform / Moonshot API
   - 更接近产品集成和按量 API。
   - 适合 WorldEngine runtime provider 评估。
   - 成本和模型选择需要由 WorldEngine 控制。
3. DeepSeek pay-as-you-go
   - 已有按量 API 方案。
   - 成本可控性需要用限额、max tokens、预算和测试用例规模控制。

要求：

- 验证客户端不保存 key。
- 验证客户端不直接调用 provider。
- provider 失败时验证客户端只能记录 WorldEngine public error / warning。

验证：

```bash
git diff --check
```

### 2.5 WorldEngine public contract 前置修复

当前实测阻塞：

- Validation Client 能访问 WorldEngine `/health` 和 `/openapi.json`。
- Validation Client `/health/worldengine` 显示 WorldEngine reachable。
- Validation Client `POST /sessions/worldengine` 失败，原因是
  `WorldEngine public world creation endpoint not found`。
- WorldEngine 当前没有 `/manifest`。

后续必须先由 WorldEngine 提供或调整：

- `GET /manifest` 或等价 public handoff manifest。
- OpenAPI 可识别的 world creation endpoint，例如 `POST /worlds`。
- world creation response 包含 public `world_id`、`status`、
  `public_initial_state` 或 `initial_state`、`visualization`。
- 如要验证导演引导，提供 public director guidance endpoint。

不满足这些条件时，Codex 自主验证只能写 BLOCKED 或 PARTIAL，不得进入人工验证。

### 3. 基础 E2E / UI smoke 验证方案

后续实现应增加可运行的 E2E / UI smoke。计划范围：

- 会话库加载。
- WorldEngine 连接状态展示。
- 创建本地 session。
- 如果 WorldEngine 可用，创建 WorldEngine session。
- 进入运行控制台。
- 查看像素画布、公开状态、事件日志、Agent 公开状态。
- 提交高层导演引导。
- 使用 replay slider。
- 从 commit point 创建 branch。
- 查看 evidence panel。
- 下载 evidence bundle。

要求：

- 失败时保存截图和错误上下文。
- 不需要真实长期世界演化。
- 不判断 Agent 行为自然性。

验证命令由实现阶段确定，可使用 Playwright 或等价浏览器自动化。

### 4. Agent 自主测试和操作日志

后续实现应定义并实现操作日志格式。日志必须记录：

```text
timestamp
run_id
actor
url
action_type
target_label
input_text
request_method
request_path
response_status
response_summary
visible_result
screenshot_path
downloaded_file
notes
```

要求：

- 每次点击、输入、提交、下载、branch 切换都要记录。
- API response 只记录脱敏摘要。
- 日志可保存为 JSONL。
- 日志必须能被另一个 Agent 复核。
- 不记录 private prompt、LLM key、provider secret、Agent private state、
  private memory、private goal、identity、relationship、hidden context。

### 4.5 Event/diff 和 snapshot 存储压缩

后续实现应按客户端日志和回放需要实现压缩存储：

- 每 tick/event 保存轻量 event/diff。
- 每隔固定 tick 数、固定事件数或显式 checkpoint 保存 snapshot。
- 回放某个 commit point 时，从最近 snapshot 开始正向应用后续 diff。
- 不做从事件 2 反向推导事件 1。
- branch 是独立世界线标识和可切换视图。
- evidence bundle 记录 diff count、snapshot count、commit point count 和 branch
  count，方便 Codex 和第二 Agent 复核。
- 存储实现可以使用数据库，也可以使用文件化 evidence bundle；选择以后续实现
  阶段的现有技术栈和测试可维护性为准。

### 5. Agent 验证 / 二次复核

后续实现应创建 Agent 复核流程。复核 Agent 输入：

- Agent 操作日志。
- evidence bundle。
- E2E 截图。
- validation run 文档。
- WorldEngine public health / manifest 摘要。

复核 Agent 输出：

- 是否按验证计划执行。
- 日志是否完整。
- evidence bundle 是否匹配操作流程。
- 是否存在脱敏或边界风险。
- 是否可以进入人工验证。

要求：

- 复核 Agent 只读。
- 复核 Agent 不补写未记录的事实。
- 复核 PASS 不等于人工验证 PASS。

### 6. 人工验证交接

后续实现应提供人工验证清单。人工验证者需要确认：

- 会话库是否像可用的世界存档入口。
- 世界是否可观察。
- 地图、Agent 状态、事件日志是否能互相解释。
- 导演引导是否保持高层方向，而不是玩家命令。
- Agent 公开反应是否自然。
- replay / branch 是否能理解为世界线。
- evidence bundle 是否足够复盘。

人工验证记录应包含：

```text
session_id
worldengine_world_id
world_prompt
screenshots
evidence_bundle_filename
agent_run_log
agent_review_result
human_scores
human_conclusion
must_fix_items
```

### 7. 总体验证和 review 收口

后续实现完成后必须运行：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

如果实现包含浏览器 E2E，还必须记录 E2E 命令、截图和 artifact 路径。

## Stop Rules

- WorldEngine 未提供足够 public API 时，停止并记录 WorldEngine 前置缺口。
- LLM provider 未配置时，不得伪造 WorldEngine 生成或 evaluator 结果。
- 任何 key、secret、private prompt、Agent private state 泄漏都必须 FAIL。
- 操作日志不完整时，不得进入 Agent 复核。
- Agent 复核未完成时，不得进入人工验证。
- 人工验证缺失时，不得声明完整产品通过。

## 提交边界

每个 numbered task 必须单独提交。当前文档生成只完成 Task 1 的计划文档部分。
