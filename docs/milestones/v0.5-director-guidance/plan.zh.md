# v0.5 Director Guidance 实现计划

状态：实现完成 / 验证通过

## 实现目标

交付一个只通过公开接口工作的导演引导闭环：

- 用户在运行控制台输入高层自然语言方向。
- 客户端后端把输入记录为本地 director intent，并在可用时提交给 WorldEngine
  公开 API。
- 前端展示 director intent 的 `pending`、`accepted`、`applied`、`rejected` 或
  `failed` 状态、当前 branch / tick、公开结构化解释和可读错误。
- 所有记录和展示都保持外部验证客户端边界，不生成权威世界事实，不直接修改
  Agent 内部状态。

## 技术栈

- 后端：FastAPI、Pydantic、SQLAlchemy、SQLite、httpx。
- 前端：React、Vite、TypeScript、Zustand。
- 测试：pytest、Vitest。

## 任务

### 1. v0.5 里程碑文档

创建：

```text
docs/milestones/v0.5-director-guidance/README.zh.md
docs/milestones/v0.5-director-guidance/plan.zh.md
docs/milestones/v0.5-director-guidance/review.zh.md
```

更新：

```text
docs/README.zh.md
```

要求：

- 明确 v0.5 目标、范围、非目标、验证命令和 commit 边界。
- 明确导演引导只提交高层世界演化方向，不直接修改 Agent 内部状态。
- 明确客户端只能通过 WorldEngine public API、manifest 或 OpenAPI 发现并提交。
- 保持 v0.5 实现顺序和逐 task commit 要求。

验证：

```bash
git diff --check
```

### 2. 后端 director intent schema 和本地 API

更新：

```text
apps/api/app/models.py
apps/api/app/routes/sessions.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
```

要求：

- 新增 `POST /sessions/{session_id}/director-intents` 创建本地 director intent。
- 新增 `GET /sessions/{session_id}/director-intents` 返回该 session 的 director
  intent 列表，按创建时间倒序。
- 创建 payload 包含 `instruction_text`，可选 `branch_id` 和 `tick`。
- 默认状态为 `pending`；返回字段包含 id、session id、branch id、tick、
  instruction text、status、public explanation、applied event id、error message 和
  created at。
- `branch_id` 不存在或不属于 session 时返回 `404`。
- 后端拒绝明显越界字段或 extra fields，不接受 agent memory、goal、identity、
  self state、relationship、private prompt、LLM key 或 provider secret 作为输入字段。
- 本 task 只实现本地记录和列表，不调用 WorldEngine。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py -q
```

### 3. WorldEngine public director guidance 提交适配

更新：

```text
apps/api/app/worldengine_client.py
apps/api/app/routes/sessions.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
```

要求：

- 从 WorldEngine public manifest / OpenAPI 摘要或保守默认路径发现 director
  guidance endpoint；禁止依赖 WorldEngine 私有路径或源码。
- `POST /sessions/{session_id}/director-intents` 在 session 已绑定
  `worldengine_world_id` 且 public endpoint 可用时，向 WorldEngine 提交高层导演
  引导。
- 请求只包含 world id、instruction text、branch id、tick 和 public context 摘要；
  不包含 LLM key、provider secret、private prompt、Agent internal state 或本地私有路径。
- WorldEngine 返回 accepted / applied / rejected / failed 状态时，更新本地
  director intent 的 status、public explanation、applied event id 或 error message。
- WorldEngine endpoint 不可用或请求失败时，本地 intent 保持 `pending` 或 `failed`
  并返回可读 degraded / error 状态，同时保存脱敏 `ApiTrace`。
- API trace 的 `llm_keys_included` 和 `private_worldengine_internals_included` 必须为
  `False`。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py -q
```

### 4. 前端 director guidance typed client 和状态

更新：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

要求：

- 定义 director intent TypeScript 类型和 create/list client 方法。
- Zustand store 保存每个 session 的 director intents、提交中状态和可读错误。
- store 支持 `createDirectorIntent(sessionId, payload)` 和
  `loadDirectorIntents(sessionId)`。
- 提交失败时不清空用户输入，并展示可读错误。
- 不在前端类型或 store 中新增 LLM key、provider secret、private prompt、Agent
  internal state 字段。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
```

### 5. 运行控制台导演引导 UI 和状态列表

更新：

```text
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/src/styles.css
```

要求：

- 导演引导表单提交真实 API，不再只清空输入框。
- 表单显示当前 branch / tick 关联上下文。
- 展示 director intent 列表，包含输入文本、状态、tick、branch、公开解释、
  applied event id 和错误信息。
- 状态文案区分 `pending`、`accepted`、`applied`、`rejected` 和 `failed`。
- UI 文案强调“高层方向 / 外部世界趋势”，不得暗示直接控制 Agent 内心、记忆、
  目标、身份、关系或行动。
- 提交失败时保留输入内容并展示错误。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web build
```

### 6. 总体验证和 review 收口

更新：

```text
docs/milestones/v0.5-director-guidance/README.zh.md
docs/milestones/v0.5-director-guidance/plan.zh.md
docs/milestones/v0.5-director-guidance/review.zh.md
```

运行：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.5-director-guidance
```

记录：

- 每个 task 的 commit。
- 变更文件。
- 命令结果。
- Scope review。
- 未实现的后续范围。
- WorldEngine public API 边界是否保持。
- 是否未保存或展示 LLM key、provider secrets、私有 WorldEngine internals、私有
  Agent 内部状态。

## Stop Rules

- 如果导演引导需要 WorldEngine 私有源码、私有 helper、私有 prompt、LLM key 或
  provider secret，停止并记录越界风险。
- 如果 WorldEngine 没有公开 director guidance endpoint，不得伪造 applied 结果；
  应保留本地 `pending` 或 degraded 状态。
- 如果公开响应没有足够信息证明引导已应用，不得编造公开影响结果。
- 如果任何 task 的验证失败，只能继续做针对该失败的窄修复。
- 如果发现 `plan.zh.md` 与实际 public API / manifest 不匹配，先更新 milestone
  文档并提交，再恢复实现。
- 不得在相关实现文件仍未提交时声明 v0.5 完成。

## 提交边界

每个 numbered task 必须单独提交。提交应只包含该 task 需要的文件。
