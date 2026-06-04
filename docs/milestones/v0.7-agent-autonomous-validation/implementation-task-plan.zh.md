# v0.7 详细实施计划

状态：计划完成 / 待实现

英文镜像：`implementation-task-plan.md`。

本文把 `codex-autonomous-validation-master-plan.zh.md` 拆成后续开发聊天可以逐项
执行、逐项提交、逐项审核的任务。当前文档不授权 runtime、API、UI、E2E 或测试
实现；实现必须在后续聊天中按本文顺序推进。

## 0. 执行前置条件

后续执行 `开发 v0.7` 前，必须先确认：

- WorldEngine 已完成 0.8.9 public contract implementation。
- WorldEngine `GET /manifest` 可访问，且不包含 secret、private prompt 或 provider
  raw trace。
- WorldEngine OpenAPI 中有 Validation Client 可发现的 world creation endpoint，
  优先 `POST /worlds`。
- Validation Client `GET /health/worldengine` 返回 reachable、openapi available 和
  `world_creation: available`。
- Validation Client `POST /sessions/worldengine` 可以创建 WorldEngine-backed
  session。

如果任一条件不满足，v0.7 实现聊天只能记录 BLOCKED 或 PARTIAL，不得进入浏览器自
主验证或人工验证交接。

## 1. 文件责任

后续实现允许修改的主要文件：

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/routes/sessions.py
apps/api/app/routes/evidence.py
apps/api/app/worldengine_client.py
apps/api/tests/test_sessions.py
apps/api/tests/test_evidence.py
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/pages/SessionLibrary.tsx
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/SessionLibrary.test.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

如新增 E2E，允许创建：

```text
apps/web/e2e/
apps/web/playwright.config.ts
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/
```

禁止修改：

```text
WorldEngine 源码
LLM provider key 管理
WorldEngine 私有 prompt / oracle / evaluator internals
Agent private memory / private goal / self_state
```

## 2. 推荐提交顺序

每个 task 单独提交。若某 task 失败，先更新 `review.zh.md` 记录失败原因，不跳到
后续 task。

### Task 1: WorldEngine preflight gate

目标：让客户端在创建 session 前能明确判断 WorldEngine 是否满足 v0.7 前置契约。

实现内容：

- 在 `apps/api/app/worldengine_client.py` 增加 manifest 拉取和 OpenAPI discovery
  摘要。
- 在 `apps/api/app/routes/health.py` 或现有 health response 中暴露脱敏 preflight
  结果。
- 保持 key、authorization header、provider raw trace 不进入 response。

最小后端测试：

- WorldEngine unreachable 时返回 `reachable: false`。
- OpenAPI 可访问但没有 world creation endpoint 时返回 `world_creation: unknown`
  或 `unavailable`。
- OpenAPI 有 `POST /worlds` 时返回 `world_creation: available`。
- manifest 中若包含 forbidden private fields，客户端只记录 public redaction
  warning，不回传 private payload。

验证命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_health.py tests/test_sessions.py -q
git diff --check
```

完成标准：

- health/preflight response 能说明是否可以创建 WorldEngine session。
- 无 secret、private prompt、provider raw trace 泄漏。
- `review.zh.md` 记录命令和结果。

### Task 2: Agent operation log data model

目标：为 Codex 浏览器操作生成可复核 JSONL 日志。

实现内容：

- 在后端模型中增加 validation run / operation log 记录，或在现有 evidence 导出中
  增加等价结构。
- 定义字段：

```text
timestamp
run_id
actor
phase
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

后端必须做脱敏：

```text
api_key
authorization
credential
password
provider secret
private prompt
provider raw trace
Agent private memory
Agent private goal
Agent self_state
hidden_context
private filesystem path
```

验证命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_evidence.py -q
git diff --check
```

完成标准：

- JSONL 可逐行 parse。
- 每条记录都有 `run_id` 和 `timestamp`。
- forbidden private fields 被拒绝、脱敏或不写入。

### Task 2.5: Event/diff and snapshot storage

目标：用轻量 event/diff 加周期 snapshot 支持回放跳转、commit point 复盘和 branch
世界线。

实现内容：

- 在后端模型、schema 或 evidence 导出结构中增加 commit point、event/diff 和
  snapshot 记录。
- 每 tick/event 保存 append-only diff。
- 每隔固定 tick 数、固定 event 数或显式 checkpoint 保存 snapshot。
- 回放目标 commit point 时，从最近 snapshot 正向应用后续 diff。
- 不做从事件 2 反向推导事件 1。
- branch 只作为 branch id / branch name / current branch view 管理。
- evidence bundle 增加：

```text
commit_point_count
branch_count
event_diff_count
snapshot_count
latest_commit_point_id
active_branch_id
```

候选文件：

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/routes/evidence.py
apps/api/tests/test_evidence.py
apps/web/src/api/types.ts
apps/web/src/pages/RuntimeConsole.tsx
```

验证命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_evidence.py -q
pnpm --dir apps/web test
git diff --check
```

完成标准：

- 从最近 snapshot 正向应用 diff 能得到目标 commit point 的公开状态。
- evidence bundle 能说明每个 commit point 和 branch 的公开状态位置。
- branch 切换只依赖 branch id、commit point 和当前视图状态。
- 存储数据不包含 private prompt、provider raw trace、LLM key 或 Agent private
  state。

### Task 3: API summary and evidence bundle association

目标：让每次自主验证 run 的 API 摘要、截图、下载 evidence bundle 可以互相追踪。

实现内容：

- evidence bundle 增加 validation run metadata。
- API trace 只保留 method、path、status、public summary、error class。
- session id、worldengine world id、timeline branch id 和 evidence bundle filename
  必须能互相对应。

验证命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_evidence.py tests/test_sessions.py -q
pnpm run test
git diff --check
```

完成标准：

- evidence bundle 中的 `session_id` 与 validation run 一致。
- API summary 不包含 raw provider response。
- evidence bundle 可下载并被测试解析。

### Task 4: Web UI operation-log hooks

目标：Web 操作能产生 Agent 视角的日志点。

实现内容：

- 会话库记录页面打开、WorldEngine 状态检查、创建 session 输入和提交。
- 运行控制台记录进入页面、查看公开状态、提交导演引导、replay、branch、下载
  evidence bundle。
- 日志记录必须由 UI action 或 API response 驱动，不从 hidden state 读取私有内容。

验证命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

完成标准：

- Web tests 覆盖关键操作记录。
- 页面仍能创建 local session 和 WorldEngine session。
- 日志不让用户误解为 WorldEngine evaluator PASS。

### Task 5: Browser E2E / UI smoke runner

目标：提供 Codex 可执行的浏览器自主验证路径。

实现内容：

- 新增 E2E 或等价浏览器脚本。
- Flow 覆盖：
  - 打开会话库。
  - 检查 WorldEngine 连接状态。
  - 创建 WorldEngine session。
  - 进入运行控制台。
  - 查看像素画布、公开状态、World Log、Agent Life Log。
  - 提交高层导演引导。
  - 使用 replay slider。
  - 从 commit point 创建 branch。
  - 下载 evidence bundle。
- 失败时保存 screenshot 和 error context。

验证命令由实现选型确定。若使用 Playwright，推荐：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm --dir apps/web exec playwright test
git diff --check
```

完成标准：

- E2E artifact 保存到 validation run 目录或可引用的测试输出目录。
- 失败时有截图。
- 成功时能产出 `agent-run.jsonl` 和 `api-summary.json`。

### Task 6: Codex run report template

目标：让自主验证聊天有固定输出格式。

创建或更新：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.md
```

模板内容必须包含：

```text
run_id
branch
commit
WorldEngine API base
Validation Client API base
Web URL
commands run
test results
browser flow summary
operation log path
screenshots path
evidence bundle path
api summary path
redaction scan result
known gaps
conclusion
```

结论只能使用：

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

### Task 7: Second Agent read-only review template

目标：让另一个 Agent 可以只读复核上一轮 Codex run。

创建或更新：

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.md
```

模板必须检查：

- operation log 是否覆盖关键 UI action。
- screenshot 是否覆盖关键页面。
- API summary 是否能支持 UI 结果。
- evidence bundle 是否匹配 session/run。
- redaction scan 是否 clean。
- Codex 结论是否没有越界到 human pass。

结论只能使用：

```text
READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

### Task 8: Human validation handoff template

目标：把自动化证据交给人类体验判断。

创建或更新：

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.md
```

模板必须让人类只判断：

- 世界是否可观察。
- 像素画布、公开状态、事件日志是否互相解释。
- Agent 公开行为是否自然。
- 导演引导是否仍是高层方向。
- replay 和 branch 是否像世界线。
- evidence bundle 是否足够复盘。

结论只能使用：

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

### Task 9: Full v0.7 closeout check

目标：确认 v0.7 可以进入 Codex 自主验证，或明确停在 BLOCKED/PARTIAL。

必须运行：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

如果新增 E2E，也必须运行 E2E 命令。

完成标准：

- `review.zh.md` 写明每个 task 的 commit、文件、命令、结果、遗留问题。
- 未完成第二 Agent 复核前，不进入人工验证。
- 未得到 `HUMAN_PASS` 前，不声明人工验证通过。

## 3. 验证路径总览

```text
WorldEngine 0.8.9 contract ready
-> Validation Client v0.7 implementation complete
-> Codex browser autonomous run
-> second Agent read-only review
-> human validation
```

## 4. Stop Rules

- WorldEngine public contract 不满足时停止。
- provider 缺失时只记录 WorldEngine public warning，不伪造生成结果。
- operation log 不完整时停止。
- evidence bundle 无法匹配 session/run 时停止。
- 发现 secret 或 private state 泄漏时 FAIL。
- 第二 Agent 未复核时不得交给人工验证。
- 人工验证未完成时不得声明产品通过。
