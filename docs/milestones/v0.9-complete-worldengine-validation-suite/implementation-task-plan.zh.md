# Implementation Task Plan

英文镜像：`implementation-task-plan.md`。

## 执行边界

本 milestone 当前只交付分阶段验证文档。它不实现 runtime/API/UI/test 代码。

当前文档状态仍是 `implementation_authorized: no`。实现前需要用户明确批准。

## 后续实现任务拆分

这些任务是后续开发依据，不在当前文档迭代中执行。

### Future Task 1：Capability discovery

- 发现当前 WorldEngine 支持的 capability，而不是查某个固定 WorldEngine 版本。
- 输出 `capability-discovery.json`。

### Future Task 2：Runtime execution

- Run N ticks、Single Tick、Pause、Resume 都要调用 WorldEngine public API。
- 调用失败则写 blocked evidence。

### Future Task 3：Agent / memory / inspection

- 采集 Agent public state、observe/intent/action-or-wait/rest。
- 采集 memory continuity / rest consolidation。
- 采集 narrative projection 和 diagnostic dialogue。

### Future Task 4：Result directory exporter

- 生成完整 suite result directory。
- 同时生成当前 WorldEngine checker 需要的兼容 artifact。

### Future Task 5：E2E 和 autonomous runbook

- 新增 `complete-worldengine-validation-suite.spec.ts`。
- 按 `agent-autonomous-operation-script.zh.md` 实现 Phase 1-4 的 UI 操作流程。
- 每个 Playwright action 都要生成对应 `operation-log.jsonl` entry。
- 所有 API request/response 摘要都要生成 `api-log.jsonl` entry。
- 每阶段保存截图，最终保存 `console.log`、`transcript.md` 和完整 result directory。
- 如果控件缺失或 capability 不支持，写 blocked artifact，不能静默跳过。

## Done Criteria

- 完整 suite 可以运行到 PASS / PARTIAL / BLOCKED / FAIL 之一。
- 所有层级都有明确 evidence 或 blocked 原因。
- 没有把 UI smoke 当 WorldEngine PASS。
- 每个 Agent 操作都有详细完整记录。
- 没有 provider key、raw prompt、raw response、private memory、raw thought 泄露。
