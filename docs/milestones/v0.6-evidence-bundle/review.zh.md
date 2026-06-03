# v0.6 Evidence Bundle Review

状态：实现完成 / 验证通过

日期：2026-06-04

## 结论

v0.6 目标是完整 Evidence Bundle：在不越过 WorldEngine public API 和本地客户端
证据边界的前提下，导出可下载、可审计、可脱敏检查的本地 session 证据包。

当前已完成 milestone 文档创建、后端 evidence bundle schema / manifest、后端
bundle 内容组装和脱敏检查、后端可下载 JSON endpoint、前端 evidence bundle
typed client / store、运行控制台 evidence panel / 下载入口，以及总体验证和 review
收口。后续审核指出的 evidence bundle 脱敏缺口也已纳入 Task 8 修复范围。v0.6
当前可判定为实现完成 / 验证通过。

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

- Commit: `3817aa8`
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

### Task 3: 后端 bundle 内容组装和脱敏检查

- Commit: `ae553c0`
- Files:
  - `apps/api/app/routes/evidence.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_evidence.py`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，1 failed，原因是
    records 仍是 Task 2 空容器，尚未导出真实 bundle 内容。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，1 failed，原因是
    subagent 审查指出的 `replay_index` 计数不一致、字符串值和 director intent 字段
    未参与敏感扫描。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 通过，`6 passed`；
    存在既有 Starlette TestClient/httpx 兼容 warning。
  - `git diff --check`: 通过
- Scope review:
  - manifest endpoint 现在按稳定顺序导出 timeline branches、commit points、
    events、state diffs、snapshots、director intents 和 api traces。
  - replay index 基于 commit point 和关联 branch 生成，包含 commit point、tick、
    event、snapshot 和 branch 摘要。
  - API trace records 只包含 method、url path、status code、request summary、
    response summary、error message 和脱敏标志。
  - request / response summary、event payload、state diff、snapshot 会做保守敏感键
    和敏感字符串值过滤；director intent 的 instruction text、public explanation 和
    error message 也会参与扫描。发现敏感内容时从 records 中移除或替换为
    `[redacted]`，并在 manifest warnings 中记录
    `sensitive content redacted from evidence records`。
  - manifest redaction flags 会结合既有 `ApiTrace` 标志和本次 payload 扫描结果；
    扫描发现 `api_key` / secret 类字段时不会标记为 clean。
  - manifest `counts.replay_index` 与实际 replay index records 数量保持一致。
  - 没有公开 evaluator 输出时不伪造结果，records 中 `evaluator_outputs` 为空，并在
    manifest warnings 中记录 `public evaluator outputs unavailable`。
- Notes:
  - 本 task 不实现下载 endpoint；下载行为留给 Task 4。

### Task 4: 后端可下载 JSON endpoint

- Commit: `eccd60f`
- Files:
  - `apps/api/app/routes/evidence.py`
  - `apps/api/tests/test_evidence.py`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，2 failed，原因是
    `/sessions/{session_id}/evidence/bundle/download` endpoint 尚不存在。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 通过，`8 passed`；
    存在既有 Starlette TestClient/httpx 兼容 warning。
  - `git diff --check`: 通过
- Scope review:
  - 新增 `/sessions/{session_id}/evidence/bundle/download` endpoint，返回完整 JSON
    evidence bundle。
  - 下载响应使用 `application/json` media type，并设置 attachment
    `Content-Disposition`。
  - 下载文件名包含 session id 和生成日期。
  - 下载 endpoint 与既有 metadata endpoint `/bundle` 和 manifest endpoint
    `/bundle/manifest` 分离，未改变旧调用方行为。
  - 缺失 session 返回 `404 Session not found`。
- Notes:
  - 本 task 不实现前端 typed client / store；前端下载行为留给 Task 5 / Task 6。

### Task 5: 前端 evidence bundle typed client 和状态

- Commit: `b3fd14e`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 红灯，2 failed，原因是
    Zustand store 尚无 `loadEvidenceBundle` / `downloadEvidenceBundle`。
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test files，
    `23 passed`；存在既有 React async store `act(...)` warning。
  - `git diff --check`: 通过
- Scope review:
  - 新增 evidence bundle counts、redaction flags、manifest、records、response 和
    download TypeScript 类型。
  - 新增 `getEvidenceBundleManifest()` typed client 方法，读取
    `/sessions/{session_id}/evidence/bundle/manifest`。
  - 新增 `downloadEvidenceBundle()` client helper，读取下载 endpoint，解析 attachment
    filename，并返回 `{ filename, bundle }`，便于后续 UI 触发浏览器下载。
  - Zustand store 新增每 session 的 evidence bundle、加载中状态和可读错误状态。
  - store 新增 `loadEvidenceBundle()` 和 `downloadEvidenceBundle()`；失败时保留当前
    runtime state，只记录 evidence bundle 错误和加载结束状态。
  - 前端类型和 store 未新增 raw private response、LLM key、provider secret、
    private prompt 或 Agent private state 字段；仅保留后端公开 redaction flags。
- Notes:
  - 本 task 不新增运行控制台 evidence panel；UI 展示和点击下载留给 Task 6。

### Task 6: 运行控制台 evidence panel 和下载入口

- Commit: `de17509`
- Files:
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/styles.css`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 红灯，1 failed，原因是运行
    控制台尚未展示 evidence bundle panel。
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test files，
    `24 passed`；存在既有 React async store `act(...)` warning。
  - `pnpm --dir apps/web build`: 通过。
  - `git diff --check`: 通过
- Scope review:
  - 运行控制台挂载时加载当前 session 的 evidence bundle manifest。
  - 新增“本地会话证据包”panel，展示 branches、commit points、events、snapshots、
    api traces 等内容计数。
  - panel 展示脱敏状态和 manifest warnings，文案明确该 bundle 是本地会话证据包，
    未暗示权威 evaluator 通过结论。
  - 新增“下载 evidence bundle”按钮，调用 store/client 的真实后端下载路径，并在
    浏览器中创建 JSON 下载。
  - 下载失败时由 store 记录可读 evidence bundle 错误，不清空当前 session / replay /
    director guidance 状态。
  - UI 未展示 private payload、hidden context、raw private response 或 Agent 内部状态。
- Notes:
  - 本 task 不新增后端逻辑。

### Task 7: 总体验证和 review 收口

- Commit: `cd1fdb2`
- Files:
  - `docs/milestones/v0.6-evidence-bundle/README.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/plan.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest -q`: 通过，`47 passed, 1 warning`；warning 为既有
    Starlette TestClient/httpx 兼容提示。
  - `pnpm --dir apps/web test`: 通过，`2 passed` test files，`24 passed`；存在既有
    React async store `act(...)` warning。
  - `pnpm --dir apps/web build`: 通过。
  - `pnpm run test`: 通过；web `24 passed`，API `47 passed, 1 warning`。
  - `pnpm run build`: 通过。
  - `git diff --check`: 通过。
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.6-evidence-bundle`:
    已审查；命中项为脱敏扫描常量、redaction flags、边界/计划/review 文档、既有
    测试反例和负向断言，未发现新增 UI 展示或 bundle records 输出私有 payload。
- Scope review:
  - 所有 planned numbered tasks 均已记录并有 task-scoped commit。
  - 后端 manifest、records、脱敏扫描、下载 endpoint 均有测试覆盖。
  - 前端 typed client / store / 运行控制台 evidence panel 和下载入口均有测试覆盖。
  - WorldEngine 边界保持：v0.6 未新增 WorldEngine 私有源码、私有路径、internal helper、
    LLM key 管理或 LLM provider 直连。
  - Evidence bundle 不生成权威 world facts 或 evaluator 结论；公开 evaluator 输出不可用
    时仅导出空列表和 warning。
  - UI 只展示 counts、redaction status 和 warnings，不展示 private payload、hidden
    context、raw private response 或 Agent 内部状态。
- Notes:
  - v0.6 不包含实时 tick streaming 或运行推进 API。

### Task 8: 审核反馈脱敏修复和复验

- Commit: `ad92336`
- Files:
  - `apps/api/app/routes/evidence.py`
  - `apps/api/tests/test_evidence.py`
  - `docs/milestones/v0.6-evidence-bundle/plan.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，1 failed，原因是
    `llm_keys_included` 在同一 payload 内先发现 LLM key、后发现非 LLM 敏感键时被覆盖
    成 `False`。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，1 failed，原因是
    subagent 复审指出的纯文本 `WorldEngine internal helper failed` 仍会从
    `ApiTrace.error_message` 原样导出。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 红灯，1 failed，原因是
    `api_traces[]` 内单条记录的 redaction flags 仍按数据库原始值断言，未反映本次
    request / response / url / error 二次扫描。
  - `cd apps/api && uv run pytest tests/test_evidence.py -q`: 通过，`9 passed`；
    存在既有 Starlette TestClient/httpx 兼容 warning。
  - `cd apps/api && uv run pytest -q`: 通过，`48 passed, 1 warning`；warning 为既有
    Starlette TestClient/httpx 兼容提示。
  - `pnpm --dir apps/web test`: 通过，`2 passed` test files，`24 passed`；存在既有
    React async store `act(...)` warning。
  - `pnpm --dir apps/web build`: 通过。
  - `pnpm run test`: 通过；web `24 passed`，API `48 passed, 1 warning`。
  - `pnpm run build`: 通过。
  - `git diff --check`: 通过。
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.6-evidence-bundle`:
    已审查；命中项为脱敏扫描常量、redaction flags、边界/计划/review 文档、既有
    测试反例和负向断言、ORM `relationship` 关系字段，未发现新增 UI 展示或 bundle
    records 输出私有 payload。
- Scope review:
  - Evidence bundle records 将 Agent `goal`、`identity`、`relationship` 作为私有
    Agent 边界字段处理，不再从 payload records 导出。
  - 敏感键扫描发现多个敏感字段时，`llm_keys_included` 按 OR 累积，不会被后续非
    LLM 敏感键覆盖成 clean。
  - API trace 的 `url_path` 和 `error_message` 已纳入敏感字符串扫描；发现
    `/internal`、`/private`、`private_path`、`internal`、`helper` 或 provider
    secret 等越界内容时导出 `[redacted]`，并设置 manifest warning / redaction
    flags。
  - `api_traces[]` 内单条记录的 `llm_keys_included` /
    `private_worldengine_internals_included` 也会合并本次二次扫描结果，避免 records
    内部标志和实际导出内容不一致。
  - Task 8 未新增 WorldEngine 私有源码、私有 helper、LLM key 管理或 LLM provider
    直连。
  - Task 8 未新增前端 UI 展示，不展示 private payload、hidden context、raw private
    response 或 Agent 内部状态。
  - Subagent 复审：Locke 指出 2 个问题；文档 pending 项在本记录中收口，纯文本
    `internal/helper` 错误泄漏风险已补回归测试并修复。
  - 最终提交：`ad92336`。
  - v0.6 不包含实时 tick streaming 或运行推进 API。

## 范围审核

- 是否只通过 public API / manifest / OpenAPI 连接 WorldEngine：Task 2 / Task 3 /
  Task 4 / Task 5 / Task 6 / Task 8 未新增 WorldEngine 调用。
- 是否未引入客户端 LLM key 管理：Task 1 / Task 2 / Task 3 / Task 4 / Task 5 /
  Task 6 / Task 8 是。
- 是否未直接调用 LLM provider：Task 1 / Task 2 / Task 3 / Task 4 / Task 5 /
  Task 6 / Task 8 是。
- 是否未生成权威世界事实或 evaluator 结论：Task 1 / Task 2 / Task 3 / Task 4 /
  Task 5 / Task 6 / Task 8 是。
- 是否未直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行为决定：
  Task 1 / Task 2 / Task 3 / Task 4 / Task 5 / Task 6 / Task 8 是。
- 是否未展示私有 Agent 内部状态、hidden context、私有 prompt 或 evaluator oracle：
  Task 1 / Task 2 / Task 3 / Task 4 / Task 5 / Task 6 / Task 8 是。
- 是否所有 planned numbered tasks 均已记录并有 task-scoped commit：Task 7 是；
  Task 8 是。
- 是否 broad checks 已通过：Task 7 是；Task 8 是。

## 遗留问题

- 实时 tick streaming 尚未实现。
- 运行推进 API 尚未实现。
- 正式 evaluator 报告生成不属于 v0.6。
