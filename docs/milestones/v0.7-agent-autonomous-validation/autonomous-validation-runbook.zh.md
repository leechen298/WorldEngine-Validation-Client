# Codex 自主验证执行 Runbook

英文镜像：`autonomous-validation-runbook.md`。

用途：当 v0.7 实现完成且 WorldEngine 0.8.9 public contract ready 后，Codex 用本
runbook 执行一次真实浏览器自主验证，并产出进入第二 Agent 复核和人工验证所需
证据。

本文不是验证结果。未实际执行本文命令和浏览器 flow 前，不得写
`PASS_READY_FOR_HUMAN_VALIDATION`。

## 0. 必须先满足的前置条件

在开始前必须确认：

- [ ] WorldEngine 已按 0.8.9 package 实现 public contract。
- [ ] WorldEngine 已填写或等价完成 `contract-readiness-checklist.zh.md`。
- [ ] WorldEngine 结论是 `WORLDENGINE_CONTRACT_READY`。
- [ ] Validation Client v0.7 实现已完成。
- [ ] Validation Client `review.zh.md` 记录 v0.7 实现和命令结果。
- [ ] 当前目标是 Codex 自主验证，不是人工验证。

如果任一项不满足，停止并写 BLOCKED 或 PARTIAL，不进入浏览器 flow。

## 1. 必读文件

```text
AGENTS.zh.md
docs/README.zh.md
docs/specs/validation-client-design.zh.md
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/agent-guides/validation-workflow.zh.md
```

WorldEngine 侧需要读取：

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/review.zh.md
```

## 2. 创建本次 Run 目录

目录命名：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/
```

必须产出：

```text
agent-run.jsonl
codex.zh.md
api-summary.json
screenshots/
downloads/evidence-bundle.json
```

建议截图：

```text
screenshots/01-session-library.png
screenshots/02-create-world.png
screenshots/03-runtime-console.png
screenshots/04-director-guidance.png
screenshots/05-replay-branch.png
screenshots/06-evidence-panel.png
```

## 3. 记录 Git 和环境元数据

在 Validation Client 仓库运行：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
git status --short --branch
git rev-parse HEAD
git diff --check
```

在 WorldEngine 仓库运行：

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
git status --short --branch
git rev-parse HEAD
git diff --check
```

记录到 `codex.zh.md`：

- branch。
- commit。
- dirty files。
- unrelated dirty files。
- 本次 run 是否允许在 dirty worktree 下继续。

如果 dirty files 会影响本次验证且无法解释，停止。

## 4. 启动服务

### 4.1 WorldEngine

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
PYTHONPATH=backend uv run --with-requirements backend/requirements.txt --no-project \
  uvicorn app.main:app --host 127.0.0.1 --port 8000
```

记录：

```text
command:
port:
PID or session id:
startup result:
```

### 4.2 Validation Client API

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
WORLDENGINE_API_BASE=http://127.0.0.1:8000 \
WORLDENGINE_VALIDATION_DATABASE_PATH=.worldengine-validation-client/e2e.sqlite3 \
pnpm run dev:api:e2e
```

记录：

```text
command:
port:
PID or session id:
startup result:
```

### 4.3 Validation Client Web

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
VITE_API_BASE_URL=http://127.0.0.1:8765 \
pnpm --dir apps/web dev --host 127.0.0.1 --port 5173 --strictPort
```

记录实际 Web URL。v0.7 Playwright E2E 默认使用 `http://127.0.0.1:5173`。

## 5. Public Contract Preflight

运行：

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/manifest
curl -i http://127.0.0.1:8000/openapi.json
curl -i http://127.0.0.1:8765/health
curl -i http://127.0.0.1:8765/health/worldengine
curl -i -H 'Content-Type: application/json' \
  -d '{"session_name":"Codex autonomous validation preflight","world_prompt":"一个可观察的小型像素世界"}' \
  http://127.0.0.1:8765/sessions/worldengine
```

必须满足：

- [ ] `/manifest` 200。
- [ ] `/openapi.json` 可访问。
- [ ] Validation Client 报告 `world_creation: available`。
- [ ] `POST /sessions/worldengine` 成功。
- [ ] public response 不包含 key、private prompt、provider raw trace 或 Agent
      private state。

不满足时，停止并用 `codex-run-report-template.zh.md` 写 BLOCKED、PARTIAL 或
FAIL。

## 6. 命令测试

运行：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

如果 v0.7 实现加入 Playwright 或等价 E2E，运行对应 E2E 命令并记录 artifact
路径。

v0.7 Playwright E2E 命令：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
WORLDENGINE_API_BASE=http://127.0.0.1:8000 \
VALIDATION_CLIENT_API_BASE=http://127.0.0.1:8765 \
pnpm --dir apps/web test:e2e
```

该命令要求 4.1 到 4.3 的三个服务已经启动；Playwright 只负责浏览器 flow 和
artifact 输出，不负责启动 API 服务。

任何命令失败时：

- 不进入人工验证。
- 如果失败阻止 UI flow，停止浏览器 flow。
- 在 `codex.zh.md` 记录命令、错误和复现路径。

## 7. 浏览器自主验证 Flow

用浏览器以人类视角执行：

1. 打开 Web URL。
2. 截图会话库。
3. 检查 WorldEngine 连接状态。
4. 输入 session name。
5. 输入基础世界观。
6. 创建 WorldEngine session。
7. 进入运行控制台。
8. 截图运行控制台。
9. 检查像素画布。
10. 检查公开状态摘要。
11. 检查 Agent 公开状态。
12. 检查 World Log。
13. 检查 Agent Life Log。
14. 输入高层导演引导。
15. 提交导演引导。
16. 截图导演引导状态。
17. 使用 replay slider。
18. 选择 commit point。
19. 创建 branch。
20. 切换 branch。
21. 截图 replay / branch 状态。
22. 打开 evidence panel。
23. 下载 evidence bundle。
24. 截图 evidence panel。

每一步都必须进入 `agent-run.jsonl`。只截图不写日志，不能算完整通过。

## 8. Operation Log 要求

每条 JSONL 至少包含：

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

检查：

- [ ] JSONL 每行可 parse。
- [ ] run_id 一致。
- [ ] session_id 一致。
- [ ] worldengine_world_id 一致。
- [ ] 覆盖所有关键 UI action。
- [ ] 不记录 private prompt、provider raw trace、Agent private memory、private
      goal、self_state 或 hidden_context。

## 9. Evidence Bundle 检查

检查下载文件：

```text
downloads/evidence-bundle.json
```

必须确认：

- [ ] JSON 可 parse。
- [ ] bundle session_id 与本次 run 一致。
- [ ] bundle 和 operation log 能互相解释。
- [ ] event、diff、snapshot、api summary counts 与 records 一致。
- [ ] redaction flags clean。
- [ ] 没有伪造 evaluator PASS。
- [ ] 没有 private content 泄漏。

## 10. Redaction Scan

运行并分类：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

分类：

```text
allowed documentation hits:
allowed test redaction hits:
forbidden UI hits:
forbidden bundle hits:
forbidden real secret hits:
```

真实 secret、private prompt、provider raw trace 或 Agent private state 泄漏时，结
论必须为 `FAIL`。

## 11. 写 Codex 报告

使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

输出：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/codex.zh.md
```

结论只能是：

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

## 12. 第二 Agent 复核交接

只有 `codex.zh.md` 结论是 `PASS_READY_FOR_HUMAN_VALIDATION` 时，才进入第二
Agent 复核。

交接输入：

```text
codex.zh.md
agent-run.jsonl
api-summary.json
screenshots/
downloads/evidence-bundle.json
```

第二 Agent 使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

输出：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-agent-review.zh.md
```

## 13. 人工验证入口

只有第二 Agent 结论是 `READY_FOR_HUMAN_VALIDATION` 时，才交给人类。

人工验证使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
```

人工验证输出：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-human.zh.md
```

人工验证结论只能是：

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

## 14. Stop Rules

- WorldEngine contract 未 ready，停止。
- Validation Client 无法创建 WorldEngine session，停止。
- 命令测试或构建失败，停止或写 PARTIAL/FAIL。
- 浏览器 flow 无法完成，不能进入第二 Agent READY。
- operation log 不完整，不能进入人工验证。
- evidence bundle 无法 parse 或不匹配本次 run，不能进入人工验证。
- 发现真实 secret 或 private state 泄漏，FAIL。
- Codex 不得声明 human validation pass。
- 第二 Agent 不得替代人工体验判断。
