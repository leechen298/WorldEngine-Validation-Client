# Plan

英文镜像：`plan.md`。

## Task 1：E2E operation recorder

候选文件：

```text
apps/web/e2e/support/operationRecorder.ts
apps/web/e2e/support/operationRecorder.test.ts
```

要求：

- 提供 `recordOperation`、`recordApiCall`、`recordScreenshot`、`writeTranscript`
  等 helper。
- 生成符合 `operation-recording-contract.zh.md` 的 `operation-log.jsonl` 和
  `api-log.jsonl`。
- 支持 blocked operation 记录。
- 不记录 secret、authorization header、raw prompt、raw provider response、
  private memory、raw thought。

验证：

```bash
pnpm --dir apps/web test src/__tests__/operationRecorder.test.ts
git diff --check
```

## Task 2：complete suite blocked result exporter

候选文件：

```text
apps/web/e2e/support/completeSuiteResult.ts
apps/web/e2e/support/completeSuiteResult.test.ts
```

要求：

- 组装 result directory 的 required artifacts。
- WorldEngine 不可达或 capability 缺失时输出 structured `BLOCKED`。
- blocked path 也必须包含 operation log、api log、api summary、console log、
  transcript、screenshots placeholder/status。

验证：

```bash
pnpm --dir apps/web test src/__tests__/completeSuiteResult.test.ts
git diff --check
```

## Task 3：complete-worldengine-validation-suite E2E runner

候选文件：

```text
apps/web/e2e/complete-worldengine-validation-suite.spec.ts
```

要求：

- 按 `agent-autonomous-operation-script.zh.md` 执行 Phase 1-4。
- 具体记录按钮点击、输入、等待、下载和截图。
- direct API harvest 只进入 `api-log.jsonl`，不得进入用户操作日志。
- 支持 PASS / PARTIAL / BLOCKED / FAIL 输出。
- 如果当前 WorldEngine capability 不支持 Phase 3 或 Phase 4，记录 blocked，
  不伪造 PASS。

验证：

```bash
pnpm --dir apps/web test:e2e -- --grep "complete-worldengine-validation-suite"
git diff --check
```

## Task 4：docs/review closeout

候选文件：

```text
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/review.zh.md
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/review.md
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/test-plan.zh.md
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/scenario-assertion-matrix.zh.md
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/result-directory-contract.zh.md
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/validation.zh.md
docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/agent-execution-handoff.zh.md
docs/README.zh.md
docs/agent-guides/routing.zh.md
docs/agent-guides/routing.md
```

要求：

- 记录每个 task 的 commit、文件、命令和结果。
- 更新路由，后续 `开发 v0.9.1` 指向本包。
- 不声明 WorldEngine PASS，除非真实 checker/scorecard 已运行并通过。
- 测试方案必须完整覆盖 E2E、Agent 自主操作、每步记录、result directory、第二 Agent 复核和 FAIL/BLOCKED taxonomy。

验证：

```bash
git diff --check
rg -n "v0\\.9\\.1|complete-worldengine-validation-suite" docs/README.zh.md docs/agent-guides docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording
```

## Stop Rules

- 如果没有先看到 focused test RED，不写生产实现。
- 如果 E2E 只能靠 UI smoke 通过，不能 PASS。
- 如果 operation log 缺失已执行 step，不能 PASS。
- 如果 api log 缺失请求摘要，不能 PASS。
- 如果出现 secret/raw/private marker，立即 FAIL。
- 如果需要 WorldEngine 新 public capability，记录 blocked，不在客户端伪造。
