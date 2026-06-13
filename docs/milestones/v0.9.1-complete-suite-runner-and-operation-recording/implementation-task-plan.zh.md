# Implementation Task Plan

英文镜像：`implementation-task-plan.md`。

## 执行边界

本包是实现包，但当前仍未授权：

```text
implementation_authorized: no
```

收到明确授权后，按 `plan.zh.md` 的 Task 1-4 顺序执行，每个 task 独立验证、独立
commit。

## RED/GREEN 要求

- Task 1 先写 recorder focused test，确认 RED，再实现 helper。
- Task 2 先写 result exporter focused test，确认 RED，再实现 exporter。
- Task 3 先写或调整 E2E 期望，确认当前缺少 suite runner，再实现 runner。
- Task 4 只做文档 closeout。

## 记录完整性要求

实现后，任意完整 suite run 的 result directory 必须能证明：

- 每个 executed `step_id` 都在 `operation-log.jsonl` 中。
- 每个 API 请求都在 `api-log.jsonl` 中，或有明确 no-API reason。
- `api-summary.json` 能按 phase 聚合请求、失败、blocked capability 和 redaction。
- `console.log` 存在。
- `transcript.md` 存在且覆盖 Phase 1-4。
- 每个 phase 有截图或 blocked screenshot status。

