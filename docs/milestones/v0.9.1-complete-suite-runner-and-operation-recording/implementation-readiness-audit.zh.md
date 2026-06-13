# Implementation Readiness Audit

英文镜像：`implementation-readiness-audit.md`。

## 结论

v0.9.1 的测试方案已经可以进入实现评审，但当前代码还没有完整的
`complete-worldengine-validation-suite` runner。

当前已有能力可以复用：

- Validation Client 已经有 WorldEngine health/capability discovery。
- Validation Client 已经有旧版 validation run 和 `operation-log.jsonl` 导出接口。
- 现有 v0.8/v0.9 E2E 可以在 WorldEngine 不可达时导出 structured blocked handoff。
- evidence bundle 已经有 named artifact 和 redaction status 的基础结构。

当前缺口：

- 没有 `complete-worldengine-validation-suite.spec.ts`。
- 没有 E2E-local recorder 负责逐 step 写入 `operation-log.jsonl`、`api-log.jsonl`、
  `console.log`、`transcript.md` 和截图。
- 旧版 backend operation log schema 不包含 v0.9.1 要求的 `step_id`、`before`、
  `after`、`api_refs`、`artifact_refs`、`result` 等字段。
- 现有 blocked handoff 会写 `operation-log.jsonl`，但内容可以为空，不能满足
  “每个已执行操作都有记录”的要求。
- 现有 E2E 主要覆盖 v0.8/v0.9 handoff，不覆盖 Phase 1-4 的 Agent 自主操作脚本。
- 现有 `SCENARIO_REQUIRED_ARTIFACTS` 没有专门定义
  `complete-worldengine-validation-suite`。

因此 v0.9.1 实现应先补测试资产和 E2E result directory 生成能力，再考虑是否扩展
backend schema。第一版完整 runner 可以先在 Playwright result directory 内生成
v0.9.1 所需的 rich artifacts；backend operation log endpoint 可作为 app-internal 日志
来源，但不能作为 v0.9.1 逐操作证据的唯一来源。

## 当前可复用文件

| 文件 | 可复用内容 | 限制 |
| --- | --- | --- |
| `apps/web/e2e/v0.8-v0.9-validation-plan.spec.ts` | WorldEngine health discovery、blocked handoff 写文件、基础 UI 流程、下载 evidence bundle | 缺少逐 step recorder；blocked `operation-log.jsonl` 为空；scenario 不是 v0.9.1 |
| `apps/api/app/routes/evidence.py` | named artifacts、manifest、artifact status、redaction status | `complete-worldengine-validation-suite` required artifact set 尚未单独定义 |
| `apps/api/app/routes/validation_runs.py` | validation run、operation log、api summary endpoint | operation log schema 是旧版用户操作摘要，不是 v0.9.1 rich schema |
| `apps/web/src/api/client.ts` | `appendOperationLog`、`getValidationRunApiSummary` 等 API client | 前端 runtime log 不能自动覆盖 Playwright Agent 的每个操作 |
| `apps/web/src/store/sessionStore.ts` | UI 触发的部分 operation log hook | 只能记录应用内部事件，不能记录 E2E 的 before/after 截图、等待、下载和 phase verdict |

## 实现策略

### 第一层：E2E-local authoritative evidence

`complete-worldengine-validation-suite` 的首要权威证据由 E2E runner 在自己的 result
directory 内生成：

```text
apps/web/e2e/support/operationRecorder.ts
apps/web/e2e/support/completeSuiteResult.ts
apps/web/e2e/complete-worldengine-validation-suite.spec.ts
```

原因：

- Agent 自主测试的“用户点击了什么、输入了什么、等了什么、下载了什么”只有
  Playwright runner 最清楚。
- backend operation log 是应用事件日志，不天然知道 Playwright 的截图、等待、下载、
  phase verdict 和 blocked step。
- direct API harvest 必须和 UI 操作分离；E2E-local recorder 可以把 API harvest 写到
  `api-log.jsonl`，而不是伪装成 UI 操作。

### 第二层：Validation Client API evidence

E2E runner 可以继续调用 Validation Client API 获取：

- `/health/worldengine`
- `/sessions`
- `/sessions/{session_id}/evidence/bundle/manifest`
- `/sessions/{session_id}/evidence/bundle/artifacts`
- `/validation-runs/{run_id}/operation-log.jsonl`
- `/validation-runs/{run_id}/api-summary`

这些 API 返回属于补充 evidence，必须写入 `api-log.jsonl`，并在 `transcript.md` 中标明
它们是 direct evidence harvest，不是用户点击。

### 第三层：backend schema 后续增强

如果后续希望用户在 UI 中直接下载 v0.9.1 rich result directory，可以再扩展：

- `apps/api/app/routes/evidence.py`
- `apps/api/app/routes/validation_runs.py`
- `apps/web/src/api/client.ts`
- `apps/web/src/components/RuntimeConsole.tsx`

但这不是 v0.9.1 第一版 runner 的必要前置。v0.9.1 的最低目标是让 Agent 自主测试可以
生成完整 result directory，并能交给第二 Agent 复核。

## 文件级实现清单

### `apps/web/e2e/support/operationRecorder.ts`

必须提供：

- `createOperationRecorder(options)`
- `recordOperation(entry)`
- `recordApiCall(entry)`
- `recordScreenshot(stepId, phase, page, name)`
- `recordTranscript(section, lines)`
- `writeAll()`
- `redactText(value, options)`
- `scanForBlockingMarkers(files)`

最低行为：

- 自动生成递增 `api-log:0001`、`operation-log:0001`。
- 每个 operation 必须有 `step_id`、`phase`、`operation_kind`、`target`、`before`、
  `after`、`api_refs`、`artifact_refs`、`result`、`timestamp`。
- 每个 API record 必须有 `source_step_id`、`method`、`url_origin`、`path_template`、
  `request_summary`、`response_summary`、`duration_ms`。
- 写文件前执行 redaction scan。
- redaction fail 时仍写 result directory，但最终 status 必须是 `fail`。

### `apps/web/e2e/support/completeSuiteResult.ts`

必须提供：

- `createCompleteSuiteResult(options)`
- `markStepPlanned(stepId)`
- `markStepExecuted(stepId, refs)`
- `markStepBlocked(stepId, reason)`
- `writeCoverageMatrix()`
- `writeApiSummary()`
- `writeResultJson(status)`
- `writeCommandMatrix(commands)`
- `writeCompatibilityArtifacts()`

最低行为：

- WorldEngine 不可达时输出 structured `BLOCKED`。
- capability 缺失时输出 phase-level `BLOCKED`，并保留已执行 step 的 evidence。
- 缺 required artifact 时最终不能 `pass`。
- `result.json` 的 status 只能是 `pass`、`partial`、`blocked`、`fail`。

### `apps/web/e2e/complete-worldengine-validation-suite.spec.ts`

必须按顺序执行：

1. Phase 1：页面打开、连接发现、创建世界、运行 5 tick、下载基础 evidence。
2. Phase 2：运行 20 tick、pause/resume/single tick、事件/快照/branch、提交两段自然语言方向。
3. Phase 3：Agent public state、Agent step/observe、30 tick 观察、memory summary、
   consolidation、narrative projection、diagnostic dialogue。
4. Phase 4：导出完整 result directory、redaction scan、WorldEngine checker handoff、
   second-Agent review placeholder。

如果某个 UI 控件或 WorldEngine capability 不存在：

- 写 `operation-log.jsonl` blocked entry。
- 写 `coverage-matrix.json` blocked entry。
- 写 `transcript.md` 说明原因。
- 继续执行 closeout，不直接抛出导致 result directory 缺失。

### `apps/web/src/__tests__/operationRecorder.test.ts`

必须覆盖：

- UI click/fill/wait/download/screenshot operation entry。
- blocked operation entry。
- API log entry。
- API summary aggregation。
- redaction fail。
- JSONL 每行可解析。

### `apps/web/src/__tests__/completeSuiteResult.test.ts`

必须覆盖：

- WorldEngine unreachable blocked result。
- missing capability phase blocked result。
- missing artifact prevents pass。
- redaction fail forces fail。
- coverage matrix maps every planned step。

## 执行顺序

实现时按以下顺序推进，避免一次性写太大补丁：

1. 写 `operationRecorder.test.ts` RED。
2. 实现 `operationRecorder.ts`，跑 focused GREEN。
3. 写 `completeSuiteResult.test.ts` RED。
4. 实现 `completeSuiteResult.ts`，跑 focused GREEN。
5. 写 `complete-worldengine-validation-suite.spec.ts` 的 blocked path，跑 E2E GREEN。
6. 扩展 connected path Phase 1-2，跑 E2E。
7. 扩展 Agent depth Phase 3，缺 capability 时记录 blocked。
8. 扩展 closeout Phase 4，确保 result directory 完整。
9. 跑完整 web tests/build。
10. 更新 review。

## 最低验收

实现完成后，即使 WorldEngine 不可达，也必须能得到：

```text
validation-runs/<timestamp>-complete-worldengine-validation-suite/
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

并且：

- `operation-log.jsonl` 至少包含 `P1-01 page_open`、`P1-02 connection check`、
  blocked phase verdict、closeout export。
- `api-log.jsonl` 至少包含 health/capability discovery 请求。
- `result.json.status=blocked`。
- `redaction-report.json.status=pass` 或真实 fail。
- E2E 测试进程可以通过，但最终验证结论是 `BLOCKED`，不是 `PASS`。

## 实现授权状态

当前仍是：

```text
implementation_authorized: no
```

本审计只补完整测试方案和实现路线，不改 runtime/API/UI/test 代码。

