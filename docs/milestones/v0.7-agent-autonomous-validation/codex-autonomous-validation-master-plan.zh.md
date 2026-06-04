# Codex 自主验证到人工验证完整计划

> **For agentic workers:** REQUIRED SUB-SKILL: 后续实现本计划时，优先使用
> subagent-driven development 或等价的 task-by-task 执行方式。每个阶段完成后必须
> 写入 evidence，再进入下一阶段。

**Goal:** 让 Codex 先以人的视角完整操作验证客户端，产出可复盘证据和只读复核
结论，再把验证入口交给人类做体验判断。

**Architecture:** WorldEngine 负责世界生成、LLM provider、Agent 行为和公开契约；
Validation Client 只消费 WorldEngine public API，记录操作、公开状态和证据；
Codex 负责自动操作和证据收集，第二 Agent 负责只读复核，人类只判断体验。

**Tech Stack:** WorldEngine FastAPI public API，Validation Client FastAPI API，
React/Vite Web UI，JSONL operation log，Playwright 或 Browser automation，
evidence bundle JSON。

---

## 0. 当前实测状态

截至 2026-06-04 当前工作树：

- Validation Client 当前本地分支：`v0.7`。
- Validation Client `v0.7` 当前 commit 仍是
  `833063b8656149b1f8163d0affd12a7ba185e81a`，与本地 `v0.6` 相同。
- `git ls-remote --heads origin` 最高只看到 `origin/v0.5`，未看到 `origin/v0.6`
  或 `origin/v0.7`。
- `pnpm run test` 已通过：Web 24 tests，API 48 tests。
- `pnpm run build` 已通过。
- WorldEngine 可以启动，`GET /health` 返回 200，`GET /openapi.json` 返回 200。
- Validation Client `GET /health/worldengine` 能看到 WorldEngine reachable。
- Validation Client `POST /sessions/worldengine` 当前失败：
  `WorldEngine public world creation endpoint not found`。

当前结论：

- 不能进入人工验证。
- 不能写 Codex 自主验证 PASS。
- 必须先补齐 WorldEngine public world creation contract，或让 Validation Client
  适配当前 WorldEngine generation API。

## 1. 验证目标分层

### 1.1 Codex 自主验证证明什么

Codex 自主验证只证明：

- 客户端可以被人类视角的 Agent 操作。
- 基础命令测试和构建通过。
- WorldEngine public API 可以被客户端消费。
- UI flow 可以完整执行。
- 操作日志可以复盘。
- evidence bundle 可以下载和解析。
- 没有 key、private prompt、provider raw trace、Agent private state 泄漏。
- 证据足以进入人工验证。

Codex 自主验证不证明：

- 世界体验已经好。
- Agent 行为已经自然可信。
- WorldEngine evaluator 权威通过。
- LLM provider 成本、速度、质量已经满足发布标准。
- 人工体验判断可以被自动化替代。

### 1.2 第二 Agent 复核证明什么

第二 Agent 只读复核只证明：

- Codex 的操作记录和证据是否完整。
- Codex 是否按计划执行。
- evidence bundle 是否能支持上一轮操作记录。
- 是否存在边界、脱敏或证据缺口。
- 是否可以交给人类验证。

第二 Agent 不重新操作浏览器，不补写事实，不替代人工体验判断。

### 1.3 人工验证判断什么

人工验证判断：

- 世界是否可观察。
- 像素界面、事件日志、公开状态是否能互相解释。
- Agent 是否像根据公开状态和事件自然反应。
- 导演引导是否只影响外部事件和环境趋势。
- replay 和 branch 是否能理解为世界线。
- evidence bundle 是否足够复盘。

## 2. 文件责任

后续实现应围绕以下文件和目录工作。

### 2.1 Validation Client

计划和证据：

```text
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
docs/milestones/v0.7-agent-autonomous-validation/review.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/
```

后端候选实现位置：

```text
apps/api/app/routes/
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/worldengine_client.py
apps/api/tests/
```

前端候选实现位置：

```text
apps/web/src/pages/SessionLibrary.tsx
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/store/sessionStore.ts
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/__tests__/
```

浏览器自动化候选位置：

```text
apps/web/e2e/
apps/web/playwright.config.ts
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/
```

### 2.2 WorldEngine

WorldEngine 侧前置契约文档：

```text
docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/
```

WorldEngine 后续实现候选位置：

```text
backend/app/api/routes/
backend/app/schemas/
backend/app/core/
backend/app/tests/
docs/contracts/
```

## 3. 端到端阶段计划

### Phase 1: WorldEngine public contract ready

目标：Validation Client 能通过 public API 创建世界、观察世界、提交高层导演引导。

必须满足：

- `GET /health` 可用。
- `GET /openapi.json` 可用。
- `GET /manifest` 或等价 handoff manifest 可用。
- OpenAPI 中存在客户端可识别的 world creation endpoint。
- world creation response 包含 public `world_id`、`status`、`initial_state` 或
  `public_initial_state`、`visualization` 或 `visualization_payload`。
- 如支持导演引导，OpenAPI 中存在 director guidance endpoint。
- provider readiness 只暴露 public summary，不暴露 key。

建议 contract：

```text
GET /manifest
POST /worlds
POST /worlds/{world_id}/director-guidance
```

`GET /manifest` 最小返回：

```json
{
  "schema_version": "0.8.x",
  "worldengine_version": "v0.8",
  "provider": {
    "provider_class": "mock|kimi_platform_api|deepseek_api|unknown",
    "provider_readiness": "ready|limited|blocked|unknown",
    "credential_source_class": "environment|not_configured|unknown",
    "model_label": "public-or-redacted-label"
  },
  "public_surfaces": [
    "/health",
    "/openapi.json",
    "/worlds",
    "/worlds/{world_id}/director-guidance"
  ],
  "redaction": {
    "secrets_included": false,
    "private_prompts_included": false,
    "provider_raw_traces_included": false
  },
  "blockers": [],
  "warnings": []
}
```

`POST /worlds` 最小 request：

```json
{
  "world_prompt": "一个可观察的小型像素世界"
}
```

`POST /worlds` 最小 response：

```json
{
  "world_id": "world-001",
  "status": "created",
  "public_initial_state": {
    "summary": "public summary",
    "public_agents": [
      {
        "agent_id": "agent-1",
        "display_name": "Ada",
        "location": "market",
        "public_status": "observing",
        "visible_action": "opens a stall"
      }
    ]
  },
  "visualization": {
    "tiles": [],
    "entities": []
  }
}
```

WorldEngine Phase 1 验证命令：

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine/backend
.venv/bin/python -m pytest app/tests -q
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
git diff --check
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/manifest
curl -i http://127.0.0.1:8000/openapi.json
curl -i -H 'Content-Type: application/json' \
  -d '{"world_prompt":"一个可观察的小型像素世界"}' \
  http://127.0.0.1:8000/worlds
```

Phase 1 stop rules：

- 没有 world creation endpoint，不进入 Phase 2。
- manifest 泄漏 key、private prompt、provider raw trace，FAIL。
- OpenAPI 存在 endpoint 但客户端无法识别，PARTIAL，不进入浏览器自主验证。

### Phase 2: Validation Client operation log ready

目标：客户端能记录 Codex 的人类视角操作日志。

必须新增或确认：

- operation log run id。
- 每个 UI action 的 JSONL 记录。
- 每个关键 API request / response summary。
- screenshot path。
- downloaded evidence bundle filename。
- redaction check result。
- validation run report 模板。

推荐 JSONL shape：

```json
{
  "timestamp": "2026-06-04T00:00:00Z",
  "run_id": "2026-06-04-codex-v0.7",
  "actor": "codex",
  "phase": "ui_smoke",
  "url": "http://127.0.0.1:5173/",
  "action_type": "click|fill|submit|api_request|api_response|screenshot|download|assertion",
  "target_label": "创建世界",
  "input_text": "一个可观察的小型像素世界",
  "request_method": "POST",
  "request_path": "/sessions/worldengine",
  "response_status": 201,
  "response_summary": {
    "session_id": "session-public-id",
    "worldengine_world_id": "world-public-id"
  },
  "visible_result": "进入运行控制台",
  "screenshot_path": "screenshots/04-runtime-console.png",
  "downloaded_file": null,
  "notes": "public summary only"
}
```

禁止写入：

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
private WorldEngine path
```

Phase 2 验证命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_prompt|raw_response|hidden_context|self_state" \
  apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

Phase 2 stop rules：

- 无法生成 operation log，不能进入 Agent 复核。
- operation log 缺少关键 UI action、API summary、截图、下载记录，PARTIAL。
- 任何真实 secret 出现在日志或 bundle 中，FAIL。

### Phase 3: Codex browser autonomous run

目标：Codex 用浏览器像人一样完整操作客户端。

正式执行必须使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
```

服务启动：

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine/backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

cd /Users/leechen/projects/WorldEngine-Validation-Client
uv run --project apps/api uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir apps/api
pnpm --dir apps/web dev
```

浏览器 flow：

1. 打开 Web URL。
2. 记录 landing/session library screenshot。
3. 检查 WorldEngine connection status。
4. 输入 session name。
5. 输入基础世界观。
6. 点击创建世界。
7. 等待进入运行控制台。
8. 记录 runtime screenshot。
9. 检查公开状态摘要。
10. 检查像素画布。
11. 检查 Agent 公开状态。
12. 检查 World Log。
13. 检查 Agent Life Log。
14. 输入高层导演引导。
15. 点击提交引导。
16. 记录导演引导状态。
17. 使用 replay slider。
18. 选择 commit point。
19. 输入 branch name。
20. 从 commit point 创建 branch。
21. 切换 branch。
22. 打开 evidence panel。
23. 下载 evidence bundle。
24. 解析 evidence bundle。
25. 生成 `agent-run.jsonl`。
26. 生成 `codex.zh.md`。

Codex run artifact 目录：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-codex/
```

建议目录内容：

```text
agent-run.jsonl
codex.zh.md
screenshots/01-session-library.png
screenshots/02-create-world.png
screenshots/03-runtime-console.png
screenshots/04-director-guidance.png
screenshots/05-replay-branch.png
screenshots/06-evidence-panel.png
downloads/evidence-bundle.json
api-summary.json
```

`codex.zh.md` 必须包含：

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
redaction scan result
known gaps
conclusion
```

生成 `codex.zh.md` 时必须使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

Codex conclusion 只能是：

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

Phase 3 stop rules：

- WorldEngine session 创建失败，BLOCKED 或 FAIL，取决于原因。
- 浏览器 UI 无法完成创建世界，BLOCKED。
- evidence bundle 无法下载，PARTIAL 或 FAIL。
- 日志不可复盘，FAIL。
- 结论写成“世界体验已通过”，FAIL。

### Phase 4: second Agent read-only review

目标：另一个 Agent 只读审查 Phase 3 证据。

输入：

```text
agent-run.jsonl
codex.zh.md
screenshots/
downloads/evidence-bundle.json
api-summary.json
git status output
test/build output
WorldEngine manifest/openapi summaries
```

复核检查表：

- Codex 是否运行了必需命令。
- Codex 是否启动了 WorldEngine、API、Web。
- operation log 是否覆盖每个关键 UI action。
- API request / response summary 是否能和 UI 状态对应。
- screenshot 是否覆盖会话库、运行控制台、导演引导、回放、branch、evidence。
- evidence bundle `session_id` 是否匹配本次 run。
- evidence bundle counts 是否与 records 长度一致。
- redaction flags 是否为 clean。
- private data scan 是否无真实泄漏。
- Codex 结论是否只声明可以进入人工验证。

复核输出：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-agent-review.zh.md
```

生成复核输出时必须使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

复核结论：

```text
READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

Phase 4 stop rules：

- 第二 Agent 发现 operation log 不完整，不进入人工验证。
- 第二 Agent 发现证据与 session 不匹配，不进入人工验证。
- 第二 Agent 发现泄漏，FAIL。

### Phase 5: human validation handoff

目标：把自动验证证据交给人类，只让人判断体验。

人类读取：

```text
codex.zh.md
agent-review.zh.md
agent-run.jsonl
screenshots/
evidence-bundle.json
```

人类检查：

- 会话库是否能理解。
- 创建世界是否自然。
- 世界是否可观察。
- 地图、Agent、事件日志是否能互相解释。
- Agent 公开状态是否有生命感。
- 导演引导是否像高层趋势，不是玩家直接操作。
- replay 是否能回看状态。
- branch 是否像世界线。
- evidence bundle 是否足够复盘。
- 体验问题是否足以阻止下一轮开发。

人工记录输出：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-human.zh.md
```

生成人工记录时必须使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
```

人工结论：

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

## 4. 后续聊天建议

### 4.1 WorldEngine 开发聊天

建议 prompt：

```text
/goal 实现 0.8.9-external-validation-provider-and-handoff-manifest 的 public handoff manifest 和 world creation contract。

只做 WorldEngine 侧：
- GET /manifest
- OpenAPI 可识别的 POST /worlds 或等价 create_world endpoint
- 如可行，POST /worlds/{world_id}/director-guidance
- provider readiness public summary
- redaction tests

不要实现 Validation Client，不要加入具体 demo 世界内容，不要暴露 key/private prompt/provider raw trace。
```

### 4.2 Validation Client 开发聊天

建议 prompt：

```text
/goal 开发 v0.7 Agent Autonomous Validation。

按 docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md 执行：
- Agent operation log JSONL
- 浏览器 E2E/UI smoke
- screenshots/download artifacts
- evidence bundle 关联
- Codex run report 模板
- Agent review report 模板
- human validation handoff 模板

每个 numbered task 单独提交。不要让客户端管理 LLM key，不要直接调用 provider。
```

### 4.3 Codex 自主验证聊天

建议 prompt：

```text
/goal 自主验证 v0.7。

先读取：
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
- docs/agent-guides/validation-workflow.zh.md

启动 WorldEngine、Validation Client API、Validation Client Web。
用浏览器完成完整 UI flow。
产出 agent-run.jsonl、codex.zh.md、screenshots、evidence bundle。
结论只能写 PASS_READY_FOR_HUMAN_VALIDATION、PARTIAL、BLOCKED 或 FAIL。
```

### 4.4 人工验证聊天

建议 prompt：

```text
/goal 人工验证 v0.7。

读取最近一次 Codex 自主验证 run 和第二 Agent 复核报告。
不要重复命令测试。
只判断世界可观察性、Agent 自然性、导演边界、replay/branch 可理解性和证据可复盘性。
输出 human.zh.md。
```

## 5. 最终完成标准

只有同时满足以下条件，才可以说“Codex 自主验证阶段完成，可以进入人工验证”：

- WorldEngine public contract ready。
- Validation Client 测试和构建通过。
- 浏览器 UI flow 完整执行。
- operation log JSONL 完整。
- screenshots 覆盖关键界面。
- evidence bundle 下载并解析成功。
- evidence bundle 与 session/run 匹配。
- redaction scan clean。
- 第二 Agent 只读复核通过。
- Codex 结论明确限定为 `PASS_READY_FOR_HUMAN_VALIDATION`。

只有人类写出 `HUMAN_PASS`，才可以说“人工验证通过”。
