# v0.3 Runtime Visualization Review

状态：Task 3 已完成 / milestone 进行中

日期：2026-06-03

## 结论

v0.3 目标是基础 Runtime Visualization：后端提供 public runtime view，前端用
PixiJS 和面板展示公开 tick、地图、Agent 公开状态、事件气泡、world log 和 Agent
life log。

当前已完成 v0.3 里程碑文档、后端 public runtime view API、前端 runtime view
typed client / store 和加载错误展示。PixiJS 地图、Agent 公开状态面板、事件气泡和
总体验证仍未完成，不能声明 v0.3 已实现或通过。

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

- Commit: `待提交`
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

## 范围审核

- 是否只通过 public API / 本地公开 evidence 数据连接 WorldEngine：Task 2 是；仅
  读取本地公开 snapshot / event。
- 是否未引入客户端 LLM key 管理：Task 2 是。
- 是否未直接调用 LLM provider：Task 2 是。
- 是否未生成权威世界事实：Task 2 是；仅规整本地公开 runtime view，缺 main branch
  时不混合 branch 数据。
- 是否未引入玩家角色控制：待实现后确认。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：Task 2 是。
- 是否未展示私有 Agent 内部状态、记忆、目标、隐藏推理或自我状态：Task 2 是；
  runtime view 使用 allowlist 输出并覆盖私有字段反例。
  Task 3 是；仅新增 typed client/store 和错误展示，未展示 Agent 状态内容。

## 遗留问题

- Task 4-6 尚未开始。
- 实时 tick streaming、完整 replay / branch 重建、导演引导提交闭环和完整 evidence
  bundle 导出仍属于后续 milestone。
