# v0.7 跨仓库验证门禁矩阵

英文镜像：`cross-repo-validation-gate-matrix.md`。

状态：计划完成 / 待执行

用途：把 WorldEngine、Validation Client、Codex 自主验证、第二 Agent 复核和人工
验证串成一个不可跳关的执行计划。本文不是验证结果，不授权任何 runtime、API、
UI、E2E 或测试实现。

## 0. 总原则

- WorldEngine 是引擎和 LLM provider owner。
- Validation Client 是客户端、日志和证据 owner。
- Codex 自主验证只证明“可以交给人类验证”，不证明人工体验通过。
- 第二 Agent 只读复核上一轮 Codex 证据，不重新操作和补写事实。
- 人类才可以写出 `HUMAN_PASS`。
- 每一关只允许基于当前会话实际运行的命令和可读取证据写结论。
- 任一门禁未满足时，下一关不得开始。

## 1. 当前状态

当前阻塞在 Gate 1。

已知事实：

- WorldEngine `/health` 可访问。
- WorldEngine `/openapi.json` 可访问。
- WorldEngine 当前缺少 `/manifest`。
- WorldEngine 当前没有 Validation Client 可发现的 world creation endpoint。
- Validation Client `/health/worldengine` 可以发现 WorldEngine reachable。
- Validation Client `POST /sessions/worldengine` 当前失败：
  `WorldEngine public world creation endpoint not found`。

当前允许的下一步：

```text
先在 WorldEngine 仓库实现 0.8.9 public contract。
```

当前不允许：

- 进入 Codex 浏览器自主验证。
- 进入第二 Agent 复核。
- 进入人工验证。
- 声称 v0.7 已验证通过。

## 2. Gate Matrix

| Gate | 名称 | Owner | 输入 | 必须产出 | 允许结论 | 进入下一关条件 |
| --- | --- | --- | --- | --- | --- | --- |
| Gate 0 | 文档计划门禁 | 当前规划聊天 | 两个仓库已有讨论和文档 | v0.7 文档、0.8.9 文档、本文 | `PLAN_READY` / `PARTIAL` / `BLOCKED` | 两个仓库都有可执行文档入口 |
| Gate 1 | WorldEngine public contract readiness | WorldEngine | 0.8.9 package | `/manifest`、可发现 `POST /worlds`、provider readiness redaction、contract readiness checklist | `WORLDENGINE_CONTRACT_READY` / `PARTIAL` / `BLOCKED` / `FAIL` | checklist 写出 `WORLDENGINE_CONTRACT_READY` |
| Gate 2 | Validation Client v0.7 implementation readiness | Validation Client | Gate 1 结论和 v0.7 plan | operation log、event/diff + snapshot 存储、E2E/UI smoke、evidence bundle、review | `READY_FOR_CODEX_AUTONOMOUS_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | tests/build/E2E/log/evidence review 全部满足 |
| Gate 3 | Codex autonomous validation | Codex | Gate 2 review 和 runbook | `validation-runs/YYYY-MM-DD-codex/` 证据包 | `PASS_READY_FOR_HUMAN_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | Codex 结论为 `PASS_READY_FOR_HUMAN_VALIDATION` |
| Gate 4 | 第二 Agent 只读复核 | 另一个 Agent | Gate 3 run 目录 | `validation-runs/YYYY-MM-DD-agent-review.zh.md` | `READY_FOR_HUMAN_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | Agent 结论为 `READY_FOR_HUMAN_VALIDATION` |
| Gate 5 | 人工验证 | 人类 | Gate 3 + Gate 4 证据 | `validation-runs/YYYY-MM-DD-human.zh.md` | `HUMAN_PASS` / `HUMAN_PARTIAL` / `HUMAN_FAIL` | 人类写出 `HUMAN_PASS` |

## 3. Gate 0: 文档计划门禁

目标：让后续聊天不需要重新猜测工作流。

必须存在：

```text
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```

WorldEngine 侧必须存在：

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/
```

完成标准：

- 文档说明当前只能进入 WorldEngine contract implementation。
- 文档区分 Codex 结论、Agent 结论和人工结论。
- 文档说明 Validation Client 不管理 LLM key，不直接调用 provider。
- 文档说明 WorldEngine 不实现 Validation Client。
- 文档说明 branch 是 branch，commit point 是可回放时间点，branch 只表达命名、
  切换、回放和继续推进。

## 4. Gate 1: WorldEngine Public Contract Readiness

目标：让 Validation Client 可以只通过公开接口创建和观察 WorldEngine-backed
session。

WorldEngine 后续聊天必须先读取：

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/AGENTS.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/project-north-star.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/product-model.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/scope-boundaries.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/roadmap.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/README.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/AGENTS.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/README.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/technical-design.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/validation-client-contract-handoff.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-task-plan.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
```

必须实现或证明：

- `GET /health` 返回 200。
- `GET /manifest` 返回 public handoff manifest。
- `GET /openapi.json` 暴露客户端可发现的 world creation endpoint。
- 优先提供 `POST /worlds`。
- `POST /worlds` 返回 public `world_id`、`status`、public state 和 visualization
  payload。
- 如完整验证需要导演引导，提供 `POST /worlds/{world_id}/director-guidance`，或在
  manifest 中明确 unavailable reason。
- provider readiness 只输出 public summary。
- 不暴露 key、authorization header、private prompt、provider raw trace、Agent
  private memory、private goal、self_state 或 hidden_context。

Validation Client 兼容性 probe 必须成功：

```bash
curl -i http://127.0.0.1:8765/health/worldengine
curl -i -H 'Content-Type: application/json' \
  -d '{"session_name":"Codex contract check","world_prompt":"一个可观察的小型像素世界"}' \
  http://127.0.0.1:8765/sessions/worldengine
```

完成证据写入：

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/review.zh.md
```

进入 Gate 2 的唯一条件：

```text
WorldEngine contract-readiness-checklist.zh.md 结论是 WORLDENGINE_CONTRACT_READY。
```

## 5. Gate 2: Validation Client v0.7 Implementation Readiness

目标：验证客户端具备被 Codex 像人一样操作并完整留证的能力。

后续聊天必须按 `implementation-task-plan.zh.md` task 顺序实现。

必须实现：

- WorldEngine preflight gate。
- Agent operation log JSONL。
- 每 tick/event 的轻量 event/diff 保存。
- 周期 snapshot 保存。
- 从最近 snapshot 正向应用 diff 还原任意 commit point 的状态。
- branch 作为独立世界线标识和可切换视图。
- evidence bundle 与 session、worldengine world id、run id、commit point 和 branch
  对齐。
- Web UI operation-log hooks。
- 浏览器 E2E / UI smoke 或等价自动化 flow。
- Codex run report、第二 Agent review、人类验证模板。

数据存储要求：

- event/diff 是 append-only。
- snapshot 按固定间隔或显式 checkpoint 保存。
- 回放跳转使用“最近 snapshot + 后续 diff”。
- 不做从事件 2 反向推导事件 1。
- evidence bundle 记录 diff count、snapshot count、commit point count 和 branch
  count。
- 客户端日志和证据不得包含 private prompt、provider raw trace、LLM key 或 Agent
  private state。

必须运行：

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

如果新增 Playwright 或等价 E2E，必须运行 E2E 并保存 artifact。

完成证据写入：

```text
docs/milestones/v0.7-agent-autonomous-validation/review.zh.md
```

进入 Gate 3 的条件：

- v0.7 review 记录所有 task 已实现。
- tests/build/E2E 通过或有明确非阻塞解释。
- operation log 可解析。
- evidence bundle 可下载和解析。
- redaction scan 没有未解释泄漏。
- 结论是 `READY_FOR_CODEX_AUTONOMOUS_VALIDATION`。

## 6. Gate 3: Codex Autonomous Validation

目标：Codex 以人类视角操作完整 Web 客户端，生成可复盘证据。

必须按以下文档执行：

```text
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

必须产出目录：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/
  agent-run.jsonl
  codex.zh.md
  api-summary.json
  screenshots/
  downloads/evidence-bundle.json
```

浏览器 flow 必须覆盖：

- 打开会话库。
- 检查 WorldEngine 连接状态。
- 输入基础世界观。
- 创建 WorldEngine session。
- 进入运行控制台。
- 查看像素画布。
- 查看 public world state。
- 查看 Agent public state。
- 查看 World Log。
- 查看 Agent Life Log。
- 输入高层导演引导。
- 提交导演引导。
- 使用 replay slider。
- 从 commit point 创建 branch。
- 切换 branch 视图。
- 下载 evidence bundle。

进入 Gate 4 的唯一条件：

```text
codex.zh.md 结论是 PASS_READY_FOR_HUMAN_VALIDATION。
```

## 7. Gate 4: 第二 Agent 只读复核

目标：让另一个 Agent 检查 Codex run 证据是否足够支持进入人工验证。

只读输入：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/codex.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/api-summary.json
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/screenshots/
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/downloads/evidence-bundle.json
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

必须检查：

- Codex 是否按 runbook 操作。
- operation log 是否覆盖关键 UI action。
- API summary 是否能支持 UI 可见结果。
- screenshots 是否覆盖关键页面。
- evidence bundle 是否匹配 session/run/commit point/branch。
- redaction scan 是否 clean。
- Codex 结论是否没有越界声明 human pass。

进入 Gate 5 的唯一条件：

```text
agent-review 结论是 READY_FOR_HUMAN_VALIDATION。
```

## 8. Gate 5: Human Validation

目标：人类判断游戏式验证客户端体验和世界运行是否可信。

人工验证只判断：

- 世界是否可观察。
- 像素界面、公开状态和事件日志是否能互相解释。
- Agent 公开状态和公开行为是否像自然生活。
- 导演引导是否只是高层方向，不是投放物品或玩家命令。
- replay 和 branch 是否像世界线。
- evidence bundle 是否足够复盘。

人工输出：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-human.zh.md
```

只有人类写出：

```text
HUMAN_PASS
```

才可以说人工验证通过。

## 9. 全局 Stop Rules

立即停止并记录 `BLOCKED`、`PARTIAL` 或 `FAIL` 的情况：

- WorldEngine 缺少 `/manifest`。
- WorldEngine OpenAPI 没有可发现 world creation endpoint。
- Validation Client 不能创建 WorldEngine-backed session。
- provider readiness 伪装成 ready。
- 出现 API key、authorization header、private prompt、provider raw trace 或 Agent
  private state 泄漏。
- operation log 无法 parse。
- evidence bundle 和 run/session/commit point/branch 无法对应。
- E2E 缺少关键截图或失败原因。
- 第二 Agent 复核未执行。
- Codex 或 Agent 把自动化结论写成人工体验通过。

## 10. 后续聊天顺序

严格按这个顺序开新聊天：

1. WorldEngine：`/goal 实现 0.8.9-external-validation-provider-and-handoff-manifest`
2. Validation Client：`/goal 开发 v0.7 Agent Autonomous Validation`
3. Validation Client：`/goal 自主验证 v0.7`
4. Validation Client 或新 Agent：`/goal 复核 v0.7 Codex 自主验证记录`
5. 人类：`/goal 人工验证 v0.7`

可复制 prompt 见：

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```
