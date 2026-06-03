# v0.6 Evidence Bundle Review

状态：实现进行中

日期：2026-06-04

## 结论

v0.6 目标是完整 Evidence Bundle：在不越过 WorldEngine public API 和本地客户端
证据边界的前提下，导出可下载、可审计、可脱敏检查的本地 session 证据包。

当前已完成 milestone 文档创建和后端 evidence bundle schema / manifest。后续
必须从 `plan.zh.md` Task 3 开始，按 numbered task 顺序实现、验证、记录并逐
task 提交。

## Task Records

### Task 1: v0.6 里程碑文档

- Commit: `9851fa9`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/README.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/plan.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.6 milestone 文档，明确 Evidence Bundle 目标、范围、非目标、task
    顺序、验证命令和逐 task commit 要求。
  - 计划明确 evidence bundle 是本地会话证据包，不是权威 evaluator 报告。
  - 计划要求 bundle 仅导出 public API 和本地客户端允许保存的公开/脱敏记录。
  - 计划禁止保存或展示 LLM key、provider secret、private prompt、WorldEngine
    私有 internals、Agent 私有内部状态、hidden context 或 evaluator oracle
    internals。
- Notes:
  - Task 1 仅创建 v0.6 milestone 文档，不包含产品代码实现。

### Task 2: 后端 evidence bundle schema 和 manifest

- Commit: `pending`
- Files:
  - `apps/api/app/schemas.py`
  - `apps/api/app/routes/evidence.py`
  - `apps/api/tests/test_evidence.py`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，2 failed，原因是
    `/sessions/{session_id}/evidence/bundle/manifest` endpoint 尚不存在。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，2 failed，原因是
    manifest 尚未说明 records 只是 Task 3 预留容器，且尚未聚合既有 `ApiTrace`
    脱敏标志。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 通过，`5 passed`；
    存在既有 Starlette TestClient/httpx 兼容 warning。
  - `git diff --check`: 通过
- Scope review:
  - 新增 evidence bundle response schema，顶层包含 `manifest` 和 `records`。
  - `manifest` 包含 bundle schema version、generated at、session id、session name、
    worldengine world id、world status、counts、redaction flags 和 warnings。
  - `records` 预留 branches、commit points、events、state diffs、snapshots、
    director intents、api traces、evaluator outputs 和 replay index 列表。
  - 保留既有 `/sessions/{session_id}/evidence/bundle` metadata endpoint；新增
    `/sessions/{session_id}/evidence/bundle/manifest` endpoint 返回 manifest 和空
    records 容器。
  - manifest warnings 明确 records 仍是 Task 3 预留容器，避免把空 records 误读为
    完整 bundle 导出。
  - manifest redaction flags 会聚合当前 session 既有 `ApiTrace` 的
    `llm_keys_included` 和 `private_worldengine_internals_included` 标志；发现已标记
    敏感内容时写入 warning。
  - 缺失 session 返回 `404 Session not found`。
  - 本 task 未新增 LLM key、provider secret、private prompt、Agent private state
    或 WorldEngine private internals 字段。
- Notes:
  - 本 task 不导出真实记录内容；稳定排序、脱敏扫描和 evaluator output warning
    留给 Task 3。
  - 本 task 不实现下载 endpoint；下载行为留给 Task 4。

## 范围审核

- 是否只通过 public API / manifest / OpenAPI 连接 WorldEngine：Task 2 未新增
  WorldEngine 调用。
- 是否未引入客户端 LLM key 管理：Task 1 / Task 2 是。
- 是否未直接调用 LLM provider：Task 1 / Task 2 是。
- 是否未生成权威世界事实或 evaluator 结论：Task 1 / Task 2 是。
- 是否未直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行为决定：
  Task 1 / Task 2 是。
- 是否未展示私有 Agent 内部状态、hidden context、私有 prompt 或 evaluator oracle：
  Task 1 / Task 2 是。
- 是否所有 planned numbered tasks 均已记录并有 task-scoped commit：否，Task 2
  进行中。
- 是否 broad checks 已通过：否，尚未进入总体验证。

## 遗留问题

- 后端 bundle 内容组装、排序、脱敏检查和下载 endpoint 尚未实现。
- 前端 typed client / store / evidence panel / 下载入口尚未实现。
- v0.6 尚未完成总体验证和 review 收口。
