# Test Plan

英文镜像：`test-plan.md`。

## 目标

本测试计划用于验证 v0.9.1 实现是否真正满足：

```text
E2E + Agent 自主测试 + 每个操作完整详细记录 + 可交给二次复核的 result directory
```

它不是 UI smoke，也不是只检查 API 可用。它要求 Agent 以用户视角操作 Validation
Client，同时把每个用户操作、每个 API 摘要、每个截图、console log、transcript 和
result directory 保存下来。

## 测试分层

| 层级 | 名称 | 目的 | 最低结论 |
| --- | --- | --- | --- |
| T0 | unit recorder tests | 验证 operation/API/transcript/screenshot 记录 helper | required pass |
| T1 | blocked exporter tests | 验证 WorldEngine 不可达时也能导出 structured BLOCKED | required pass |
| T2 | E2E blocked path | 验证完整 runner 在 capability 缺失时不伪造 PASS | required pass |
| T3 | E2E connected path | 验证 Phase 1-2 可通过真实 UI 操作连接 WorldEngine | pass 或 blocked with evidence |
| T4 | Agent depth path | 验证 Phase 3 Agent/memory/inspection evidence | pass 或 blocked with taxonomy |
| T5 | closeout path | 验证 Phase 4 result directory、redaction、checker handoff | pass 或 blocked with evidence |

## Required Commands

实现完成后必须运行：

```bash
pnpm --dir apps/web test src/__tests__/operationRecorder.test.ts
pnpm --dir apps/web test src/__tests__/completeSuiteResult.test.ts
pnpm --dir apps/web test:e2e -- --grep "complete-worldengine-validation-suite"
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

如果 E2E 因 WorldEngine 不可达而输出 `BLOCKED` result directory，只要 blocked
artifact 完整且测试断言通过，E2E 可以通过；但最终 WorldEngine 验证结论必须是
`BLOCKED`，不能写 `PASS`。

## T0：Recorder Unit Tests

### T0.1 records UI operations

输入：

- step id: `P1-05`
- phase: `phase-1`
- operation kind: `click`
- target role/label: `button` / `创建世界`
- before/after screenshot refs
- api refs

断言：

- 输出 `operation-log.jsonl`。
- 每行是合法 JSON。
- 包含 `schema_version=0.9.0`。
- 包含 `step_id`、`phase`、`actor`、`operation_kind`、`target`、`before`、`after`、
  `api_refs`、`artifact_refs`、`result`、`timestamp`。
- 不包含 secret/raw/private marker。

### T0.2 records blocked operations

输入：

- step id: `P3-07`
- operation kind: `blocked`
- blocked reason: `missing_client_control`

断言：

- `result.status=blocked`。
- `result.blocked_reason` 存在。
- blocked 操作也进入 `operation-log.jsonl`。

### T0.3 records API summaries

输入：

- API ref: `api-log:0004`
- source step id: `P1-05`
- method: `POST`
- path template: `/sessions/worldengine`
- response status: `201`

断言：

- 输出 `api-log.jsonl`。
- request summary 只包含 body shape、公开输入长度、redaction flags。
- 不包含 authorization header、API key、raw prompt、raw provider response。

### T0.4 aggregates API summary

断言：

- `api-summary.json` 按 phase 聚合 request count。
- 聚合 non-2xx responses。
- 聚合 blocked capability calls。
- 聚合 redaction result。
- 映射 `step_id -> api_refs`。

## T1：Blocked Exporter Tests

### T1.1 WorldEngine unreachable exports full blocked handoff

模拟：

- `/health/worldengine` 返回 `reachable=false`。

断言 result directory 包含：

```text
result.json
coverage-matrix.json
command-matrix.md
operation-log.jsonl
api-log.jsonl
api-summary.json
capability-discovery.json
redaction-report.json
console.log
transcript.md
screenshots/
```

断言：

- `result.status=blocked`。
- taxonomy 包含 `worldengine_unreachable`。
- `operation-log.jsonl` 包含页面打开、连接状态检查、blocked phase verdict。
- `api-log.jsonl` 包含 health check 摘要。
- `transcript.md` 说明 blocked 原因。

### T1.2 capability missing exports phase blocked

模拟：

- WorldEngine reachable。
- world creation available。
- Agent public state missing。

断言：

- Phase 1/2 可 pass 或 partial。
- Phase 3 为 `blocked/missing_worldengine_capability`。
- Phase 4 不能 PASS。

## T2：E2E Blocked Path

场景名：

```text
complete-worldengine-validation-suite
```

操作要求：

1. 打开 Validation Client。
2. 记录 `P1-01 page_open`。
3. 检查 WorldEngine connection。
4. 如果 unreachable，写 `P1-02 blocked`。
5. 导出 blocked result directory。

断言：

- E2E 测试进程通过。
- validation conclusion 是 `BLOCKED`。
- 不存在 UI smoke PASS。
- 所有已执行操作都有 operation record。

## T3：E2E Connected Path

如果 WorldEngine reachable 且支持 world creation：

必须执行：

- 填写 Session 名称。
- 填写固定基础世界观。
- 点击 `创建世界`。
- 等待 `运行控制` 可见。
- 设置 tick 数。
- 点击 run。
- 点击 pause/resume/single tick。
- 下载 evidence。

断言：

- 每个点击/输入/等待/下载都有 `operation-log.jsonl`。
- 每个 API 请求都有 `api-log.jsonl`。
- `world-creation-summary.json` 存在或 blocked reason 存在。
- Phase 1/2 verdict 有 PASS 来源或 blocked taxonomy。

## T4：Agent Depth Path

如果 WorldEngine 和客户端支持 Agent public evidence：

必须执行：

- 打开 Agent 面板。
- 读取 Agent public state。
- 触发或观察 Agent step。
- 运行观察 tick。
- 读取 memory summary。
- 尝试 consolidation。
- 运行 narrative projection。
- 运行 diagnostic dialogue。

断言：

- `agent-evidence.json` 存在或明确 blocked。
- `memory-continuity-summary.json` 存在或明确 blocked。
- narrative/diagnostic 不写 canonical world state。
- 不出现 private memory、raw thought、hidden context。

## T5：Closeout Path

必须执行：

- 导出完整 result directory。
- 保存 `console.log`。
- 保存 `transcript.md`。
- 生成 `coverage-matrix.json`。
- 生成 `redaction-report.json`。
- 如果 WorldEngine checker 可用，记录 checker command 和结果。
- 如果 checker 不可用，记录 `blocked/checker_gap`。

断言：

- 缺少任何 required artifact 时最终不能 PASS。
- redaction fail 时最终必须 FAIL。
- checker/scorecard/second-Agent review 缺失时最终不能 PASS。

## Redaction Test Cases

所有测试必须扫描以下 marker：

```text
api key
authorization
credential
token
password
secret
raw prompt
raw provider request
raw provider response
private memory
private goal
raw thought
chain-of-thought
hidden context
WorldEngine private path
```

命中任何 blocking marker，最终 `FAIL`。

