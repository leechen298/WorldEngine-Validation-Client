# v0.3 Runtime Visualization Review

状态：实现完成 / 总体验证通过

日期：2026-06-03

## 结论

v0.3 目标是基础 Runtime Visualization：后端提供 public runtime view，前端用
PixiJS 和面板展示公开 tick、地图、Agent 公开状态、事件气泡、world log 和 Agent
life log。

当前已完成 v0.3 里程碑文档、后端 public runtime view API、前端 runtime view
typed client / store、加载错误展示和 PixiJS 基础地图画面。Agent 公开状态面板、
事件气泡、world / Agent life log 也已完成，并通过当前会话总体验证。

## Task Records

### Task 1: v0.3 里程碑文档

- Commit: `e991210`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.3-runtime-visualization/README.zh.md`
  - `docs/milestones/v0.3-runtime-visualization/plan.zh.md`
  - `docs/milestones/v0.3-runtime-visualization/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.3 milestone 文档，明确 Runtime Visualization 目标、范围、非目标、
    task 顺序、验证命令和逐 task commit 要求。
- Notes:
  - Task 1 仅创建 v0.3 milestone 文档，不包含产品代码实现。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 2: 本地 runtime view API

- Commit: `c0d7133`
- Files:
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`15 passed, 1 warning`
  - `git diff --check`: 通过
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|reasoning|hidden_context|raw_response" apps/api/app/routes/sessions.py apps/api/app/schemas.py apps/api/tests/test_sessions.py docs/milestones/v0.3-runtime-visualization`: 通过；命中项为过滤常量、边界文档、既有 redaction flag 和测试反例，未发现 runtime view 透传私有 payload。
- Scope review:
  - 新增 `GET /sessions/{session_id}/runtime-view`，从本地已保存 main branch
    snapshot / events 生成基础 tick、公开 world status、allowlist visualization、
    Agent 公开状态、world log、Agent life log 和 latest event。
  - session 不存在返回 `404`；无 main branch 时返回空 runtime 数据，不混合其他
    branch。
- Notes:
  - subagent reviewer 指出黑名单过滤和 branch 混合风险；已改为 allowlist 输出，并
    增加未知字段与多 branch/无 main branch 回归测试。
  - 本 task 不调用 WorldEngine 新接口，不实现 runtime tick ingest、实时 streaming、
    回放重建或前端展示。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 3: 前端 runtime view client 和状态

- Commit: `3a38910`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test files，`8 passed`
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 已定义 runtime view TypeScript 类型，新增 `getRuntimeView()` client 调用，并在
    Zustand store 中按 session 缓存 runtime view / runtime error。
  - `RuntimeConsole` 进入 session 时会触发 runtime view 加载，并展示可读运行视图
    加载失败信息。
- Notes:
  - 本 task 不渲染 PixiJS 地图、不展示 Agent 公开状态面板、不实现事件气泡或 log
    UI；这些仍留给 Task 4/5。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 4: PixiJS 基础地图画面

- Commit: `8711785`
- Files:
  - `apps/web/src/components/PixelWorldCanvas.tsx`
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/styles.css`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test files，`11 passed`；存在既有 React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - `PixelWorldCanvas` 接收 runtime visualization payload，并用 PixiJS 静态绘制
    allowlist tiles / entities。
  - 缺少公开 visualization payload 时展示 empty state；测试中 mock PixiJS，生产
    build 使用真实 PixiJS。
- Notes:
  - 本 task 不展示 Agent 公开状态面板、不实现事件气泡、world log 或 Agent life
    log UI；这些仍留给 Task 5。
  - 画布只消费后端 Task 2 已过滤的 `visualization` 字段，不从摘要字符串推断权威
    世界事实。
  - subagent reviewer 指出缺失坐标时默认渲染到 `(0,0)` 会推断位置；已改为只渲染
    finite `x` / `y` 的 tiles / entities，并增加 malformed payload 回归测试。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 5: Agent 公开状态和事件日志面板

- Commit: `60662a1`
- Files:
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/styles.css`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test files，`12 passed`；存在既有 React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 运行控制台展示基础 tick、Agent 公开状态、最新事件气泡、World Log 和 Agent
    Life Log。
  - UI 只读取 runtime view 的 public 字段，不展示 runtime payload 中的
    `memory`、`goal`、`thought`、hidden/debug 字段。
- Notes:
  - 本 task 不实现实时 tick streaming、director guidance 提交闭环、回放重建或
    branch 深化。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 6: 总体验证和 review 收口

- Commit: `待提交`
- Files:
  - `docs/milestones/v0.3-runtime-visualization/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest -q`: sandbox 内因 `~/.cache/uv` 权限失败；提升权限重跑通过，`30 passed, 1 warning`
  - `pnpm --dir apps/web test`: 通过，`2 passed` test files，`12 passed`；存在既有 React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `pnpm run test`: sandbox 内 API 阶段因 `~/.cache/uv` 权限失败；提升权限重跑通过，web `12 passed`，API `30 passed, 1 warning`
  - `pnpm run build`: 通过
  - `git diff --check`: 通过
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|reasoning|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.3-runtime-visualization`: 通过；命中项为过滤常量、边界文档、既有 redaction flag 和测试反例，未发现新增运行 UI 展示私有字段。
- Scope review:
  - v0.3 仅基于本地公开 runtime evidence 展示 Runtime Visualization，不新增
    WorldEngine 私有接口调用、不引入 LLM key 管理、不直接调用 LLM provider。
  - 前端展示公开 tick、地图、Agent public state、事件气泡、world log 和 Agent
    life log；未实现玩家控制、实时 tick streaming、完整回放重建、branch 深化或
    完整 evidence bundle 导出。
- Notes:
  - warning 来自现有 Starlette TestClient/httpx 兼容提示和 React async store 测试
    提示，不影响当前通过结论。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

## 范围审核

- 是否只通过 public API / 本地公开 evidence 数据连接 WorldEngine：是；v0.3 仅
  读取本地公开 snapshot / event / runtime view。
- 是否未引入客户端 LLM key 管理：是。
- 是否未直接调用 LLM provider：是。
- 是否未生成权威世界事实：Task 2 是；仅规整本地公开 runtime view，缺 main branch
  时不混合 branch 数据。
- 是否未引入玩家角色控制：是。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：是。
- 是否未展示私有 Agent 内部状态、记忆、目标、隐藏推理或自我状态：Task 2 是；
  runtime view 使用 allowlist 输出并覆盖私有字段反例。
  Task 3 是；仅新增 typed client/store 和错误展示，未展示 Agent 状态内容。
  Task 4 是；仅渲染公开 visualization 的 tiles / entities。
  Task 5 是；只展示 Agent public state 和 public log text。

## 遗留问题

- 实时 tick streaming、完整 replay / branch 重建、导演引导提交闭环和完整 evidence
  bundle 导出仍属于后续 milestone。
