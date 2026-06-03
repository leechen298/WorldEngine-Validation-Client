# v0.5 Director Guidance Review

状态：计划已创建 / 待实现

日期：2026-06-03

## 结论

v0.5 目标是基础 Director Guidance：运行控制台提交高层自然语言方向，后端记录
director intent，并在可用时通过 WorldEngine public API 提交和记录公开状态。

当前已完成 milestone 文档创建、后端 director intent 本地 API、WorldEngine
public director guidance 提交适配、前端 director guidance typed client / store，以及
运行控制台导演引导真实提交 UI 和状态列表。总体验证和 review 收口尚未完成，不能
声明 v0.5 已完成。

## Task Records

### Task 1: v0.5 里程碑文档

- Commit: `7fcf84b`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.5-director-guidance/README.zh.md`
  - `docs/milestones/v0.5-director-guidance/plan.zh.md`
  - `docs/milestones/v0.5-director-guidance/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.5 milestone 文档，明确 Director Guidance 目标、范围、非目标、
    task 顺序、验证命令和逐 task commit 要求。
  - 计划明确导演引导只表达高层外部世界方向，不直接修改 Agent 内部状态、记忆、
    目标、身份、关系、自我状态或行为决定。
  - 计划要求 WorldEngine 连接只能通过 public API、manifest 或 OpenAPI 发现路径，
    不依赖私有源码、私有 helper、私有 prompt、LLM key 或 provider secret。
- Notes:
  - Task 1 仅创建 v0.5 milestone 文档，不包含产品代码实现。
  - Task 1 commit hash 已在后续 docs-only 记录提交中补充。

### Task 2: 后端 director intent schema 和本地 API

- Commit: `3717dcd`
- Files:
  - `apps/api/app/models.py`
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
  - `docs/milestones/v0.5-director-guidance/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q -k "director_intent"`:
    红灯，3 failed，原因是 `/sessions/{session_id}/director-intents` endpoint 尚不存在。
  - `cd apps/api && uv run pytest tests/test_sessions.py -q -k "director_intent"`:
    通过，`3 passed, 1 warning`
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`22 passed, 1 warning`
  - `git diff --check`: 通过
- Scope review:
  - 新增 `POST /sessions/{session_id}/director-intents`，创建本地 director intent，
    默认状态为 `pending`，并返回 session、branch、tick、instruction、status、
    public explanation、applied event、error 和 created at。
  - 新增 `GET /sessions/{session_id}/director-intents`，按创建时间倒序返回当前
    session 的 director intents。
  - `branch_id` 必须属于当前 session；跨 session branch 返回 `404 Branch not found`。
  - 创建 payload 使用 `extra="forbid"`，拒绝 `agent_goal`、`private_prompt` 等越界
    extra fields，并通过测试确认 422 时不落库。
  - 本 task 不调用 WorldEngine，不保存 API trace，不实现 accepted / applied 状态更新。
- Notes:
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。
  - WorldEngine public director guidance 提交适配留给 Task 3。
  - Task 2 commit hash 已在后续 docs-only 记录提交中补充。

### Task 3: WorldEngine public director guidance 提交适配

- Commit: `a2e51b8`
- Files:
  - `apps/api/app/worldengine_client.py`
  - `apps/api/app/routes/sessions.py`
  - `apps/api/tests/test_sessions.py`
  - `docs/milestones/v0.5-director-guidance/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q -k "director_guidance or director_intent"`:
    红灯，collection error，原因是 `submit_director_guidance_via_public_api` 尚未实现。
  - `cd apps/api && uv run pytest tests/test_sessions.py -q -k "director_guidance or director_intent"`:
    通过，`6 passed, 1 warning`
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`25 passed, 1 warning`
  - `git diff --check`: 通过
- Scope review:
  - 新增 `submit_director_guidance_via_public_api()`，从 WorldEngine public OpenAPI
    中发现 director guidance endpoint，拒绝 `/internal`、`/private`、helper 等私有
    endpoint。
  - 对 WorldEngine 的请求只包含 world id、instruction text、branch id、tick 和
    public context 摘要；public context 会过滤 private path / prompt / secret /
    provider / Agent internal state 相关字段。
  - WorldEngine 返回 accepted / applied / rejected / failed 等公开状态时，route 会
    更新本地 director intent 的 status、public explanation、applied event id 或
    error message。
  - 绑定 `worldengine_world_id` 的 session 会保存脱敏 `ApiTrace`，并保持
    `llm_keys_included=False`、`private_worldengine_internals_included=False`。
  - public endpoint 不可用或请求失败时，不伪造 applied 结果；本地 intent 保持
    `pending` 并记录可读 error message 和脱敏失败 trace。
- Notes:
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。
  - 本 task 不实现前端 typed client / store 或运行控制台真实提交 UI。
  - Task 3 commit hash 已在后续 docs-only 记录提交中补充。

### Task 4: 前端 director guidance typed client 和状态

- Commit: `09436bb`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `docs/milestones/v0.5-director-guidance/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 红灯，2 failed，原因是
    Zustand store 尚无 `loadDirectorIntents` / `createDirectorIntent`。
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test
    files，`19 passed`；存在既有 React async store `act(...)` warning。
  - `git diff --check`: 通过
- Scope review:
  - 新增 `DirectorIntent`、`DirectorIntentStatus` 和 `CreateDirectorIntentRequest`
    TypeScript 类型。
  - 新增 `getDirectorIntents()` 和 `createDirectorIntent()` typed client 方法，路径为
    `/sessions/{session_id}/director-intents`。
  - Zustand store 新增每 session 的 director intents、提交中状态和可读错误状态。
  - `loadDirectorIntents()` 会缓存列表并清空该 session 的 director intent 错误；
    `createDirectorIntent()` 成功后把新 intent 放到当前列表前部。
  - 提交失败时 store 返回 `null`，保留现有 intents，并记录可读错误和提交结束状态；
    后续 UI 可据此保留输入内容。
  - 前端类型和 store 未新增 LLM key、provider secret、private prompt 或 Agent
    internal state 字段。
- Notes:
  - 本 task 不改运行控制台 UI 的表单行为；真实提交和列表展示留给 Task 5。
  - Task 4 commit hash 已在后续 docs-only 记录提交中补充。

### Task 5: 运行控制台导演引导 UI 和状态列表

- Commit: `待提交`
- Files:
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `docs/milestones/v0.5-director-guidance/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 红灯，2 failed，原因是
    运行控制台尚未加载 director intents、表单仍未接入真实提交、缺少状态列表。
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test
    files，`21 passed`；存在既有 React async store `act(...)` warning。
  - `pnpm --dir apps/web build`: 通过。
  - `git diff --check`: 通过。
- Scope review:
  - 运行控制台挂载时加载当前 session 的 director intents。
  - 导演引导表单现在调用 store/API，提交 payload 包含 instruction text、当前
    branch id 和 target tick。
  - 提交成功后清空输入并刷新 director intent 列表；提交失败时保留输入内容并展示
    可读错误。
  - 新增 director intent 状态列表，展示输入文本、状态、branch / tick、公开解释、
    applied event id 和错误信息。
  - UI 文案使用“高层方向 / 外部世界趋势”，不暗示直接控制 Agent 内心、记忆、目标、
    身份、关系或行动。
  - 状态列表只读取后端返回的 public fields，不展示 raw/private payload。
- Notes:
  - 本 task 不新增运行推进 API，不实现完整 evidence bundle 导出。

## 范围审核

- 是否只通过 public API / manifest / OpenAPI 连接 WorldEngine：Task 3 是；仅从
  public OpenAPI 发现 director guidance endpoint。
- 是否未引入客户端 LLM key 管理：Task 2 / Task 3 是。
- 是否未直接调用 LLM provider：Task 2 / Task 3 是。
- 是否未生成权威世界事实：Task 2 / Task 3 是；WorldEngine 未证明 applied 时不
  编造公开影响结果。
- 是否未直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行为决定：
  Task 2 / Task 3 是；extra field 和 public payload filtering 覆盖相关反例。
- 是否未展示私有 Agent 内部状态、隐藏推理或私有 prompt：Task 2 / Task 3 是；
  Task 4 / Task 5 未新增相关前端字段，后端 trace 摘要过滤私有字段。
- 是否未引入玩家角色控制、物品放置或手动事件注入：Task 2 / Task 3 / Task 5 是。

## 遗留问题

- 总体验证和 review 收口尚未完成。
- 完整 evidence bundle 导出仍属于后续 milestone。
