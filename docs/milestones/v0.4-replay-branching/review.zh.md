# v0.4 Replay And Branching Review

状态：实现完成 / 验证通过

日期：2026-06-03

## 结论

v0.4 目标是基础 Replay And Branching：后端从公开 snapshot + state diff 重建
replay view，前端运行控制台展示时间线 scrubber、commit point 浏览、branch 切换
和从 commit point 创建 branch 的基础体验。

当前已完成 milestone 文档创建、后端 replay read model API、timeline branch /
commit point 上下文深化，以及前端 replay / branch typed client、时间线 scrubber、
commit point 浏览、branch 切换和从 commit point 创建 branch 的基础 UI。

## Task Records

### Task 1: v0.4 里程碑文档

- Commit: `27ba785`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.4-replay-branching/README.zh.md`
  - `docs/milestones/v0.4-replay-branching/plan.zh.md`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.4 milestone 文档，明确 Replay And Branching 目标、范围、非目标、
    task 顺序、验证命令和逐 task commit 要求。
- Notes:
  - Task 1 仅创建 v0.4 milestone 文档，不包含产品代码实现。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录将在后续
    docs-only review 更新中补充可见 hash。

### Task 2: 后端 replay read model API

- Commit: `eb1b021`
- Files:
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`17 passed, 1 warning`
  - `git diff --check`: 通过
- Scope review:
  - 新增 `GET /sessions/{session_id}/replay-view`，支持 `branch_id` 和 `tick`
    query；未提供 `branch_id` 时默认使用 main branch。
  - replay view 从目标 branch 中不晚于目标 tick 的最近 snapshot 开始，按 tick 顺序
    应用公开 `StateDiff.diff_json`，并按目标 tick 截取公开事件日志。
  - replay 输出复用 public runtime view 语义，包含 branch id、snapshot id、目标
    tick、公开 visualization、Agent public state、world log、Agent life log 和
    latest event。
  - diff patch、visualization、Agent state 和 log payload 均经过既有 public
    filtering / allowlist 路径，不透传 private/internal/helper/path/secret/key/prompt/
    memory/goal/thought 字段。
- Notes:
  - 新增测试先红灯复现 `/replay-view` 404，再实现 API 后转绿。
  - session 或 branch 不存在返回 `404`；目标 tick 早于可重建 snapshot 返回 `422`。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。
  - 本 task 不新增 state diff 写入 API，不深化 commit point / branch 列表，不实现
    前端 UI。

### Task 3: 后端 commit point / branch 上下文深化

- Commit: `99812a5`
- Files:
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/routes/timelines.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_timelines.py`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_timelines.py -q`: 通过，`5 passed, 1 warning`
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`17 passed, 1 warning`
  - `git diff --check`: 通过
- Scope review:
  - branch response 增加 `is_main` 和 `current_tick`，branch 列表和创建 branch 响应均
    返回可直接用于 replay 的 branch context。
  - commit point 列表增加关联 branch ids / names 和公开 `payload_summary`。
  - commit point 列表不再返回 raw `payload_json`，避免绕过 runtime / replay view
    的 public filtering 路径。
  - 保持 branch 是“世界线”的平铺模型，没有引入 parent / child timeline 层级语义。
- Notes:
  - 新增测试先红灯复现 response 字段缺失和 raw `payload_json` 泄漏，再实现后转绿。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。
  - 本 task 不新增前端 UI，不实现 timeline scrubber。

### Task 4: 前端 replay / branch typed client 和状态

- Commit: `b0530e1`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test
    files，`15 passed`
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 新增 replay view、commit point summary、branch context TypeScript 类型。
  - 新增 `getReplayView()` 和 `getCommitPoints()` typed client 方法。
  - Zustand store 现在可缓存 commit points、replay view、replay error、selected
    branch 和 replay tick。
  - store 加载 replay view 失败时记录可读错误，不展示 raw payload。
- Notes:
  - 新增测试先红灯复现 `loadCommitPoints` / `loadReplayView` 缺失，再实现后转绿。
  - 本 task 不新增 scrubber UI、不新增 commit point browser UI、不实现 branch
    切换和创建 UI。

### Task 5: 运行控制台时间线 scrubber 和 commit point 浏览

- Commit: `087a48d`
- Files:
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/styles.css`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test
    files，`16 passed`；存在既有 React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 运行控制台新增时间线回放区域，展示目标 tick range scrubber、当前 replay tick
    和 commit point 列表。
  - commit point browser 只展示公开 `payload_summary`、tick 和 branch 名称，不展示
    raw payload / snapshot / diff JSON。
  - 点击 commit point 可按当前 branch 加载目标 tick 的 replay view；页面优先展示
    replay view，缺失时回退 runtime view。
  - replay view 加载失败时展示可读错误。
- Notes:
  - 新增测试先红灯复现缺少“时间线回放”UI，再实现后转绿。
  - 本 task 不实现 branch 切换和从 commit point 创建 branch；这些仍留给 Task 6。

### Task 6: 运行控制台 branch 切换和创建

- Commit: `f9f5005`
- Files:
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/components/TimelineBranchList.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/styles.css`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test
    files，`17 passed`；存在既有 React async store `act(...)` warning
  - `pnpm --dir apps/web test -- SessionLibrary.test.tsx`: 通过，`2 passed` test
    files，`17 passed`；存在既有 React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - `TimelineBranchList` 支持选择 branch，并标识当前 branch / main branch / current
    tick。
  - 运行控制台支持切换 branch 后按该 branch current tick 加载 replay view。
  - 运行控制台支持从当前选中 commit point 创建新 branch；创建成功后刷新 branch、
    commit point 和 replay view 状态。
  - UI 文案使用 branch / 世界线语义，没有引入 parent / child timeline 层级语义。
- Notes:
  - 新增测试先红灯复现缺少 branch 切换按钮，再实现后转绿。
  - 本 task 不新增 WorldEngine 运行推进 API，不实现实时 tick streaming。

### Task 7: 总体验证和 review 收口

- Commit: `07f4dd8`
- Files:
  - `docs/milestones/v0.4-replay-branching/README.zh.md`
  - `docs/milestones/v0.4-replay-branching/plan.zh.md`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest -q`: 通过，`33 passed, 1 warning`
  - `pnpm --dir apps/web test`: 通过，`2 passed` test files，`17 passed`；存在既有
    React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `pnpm run test`: 通过；web `17 passed`，API `33 passed, 1 warning`
  - `pnpm run build`: 通过
  - `git diff --check`: 通过
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|reasoning|hidden_context|raw_response|payload_json" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.4-replay-branching`: 通过；命中项为过滤常量、边界文档、既有兼容 raw event 类型/模型、测试反例和 review 记录，未发现新增 replay / branch UI 展示 raw private payload。
- Scope review:
  - v0.4 仅基于本地公开 evidence 数据实现 replay / branch 观察能力，不新增
    WorldEngine 私有接口调用。
  - 后端 replay view 使用 branch 隔离、snapshot + state diff 重建和 public filtering。
  - 前端运行控制台只展示 replay/runtime view、commit point 公开摘要和 branch
    context，不展示 raw event / snapshot / diff payload。
  - 所有 planned numbered tasks 均已记录并有 task-scoped commit。
- Notes:
  - warning 来自现有 Starlette TestClient/httpx 兼容提示和 React async store 测试
    提示，不影响当前通过结论。
  - 实时 tick streaming、运行推进 API、导演引导提交闭环和完整 evidence bundle
    导出仍属于后续 milestone。

## Post-Review Fix Records

### Review Fix 1: 修复新建 branch 后立即 replay 的基准 snapshot 查询

- Commit: `待提交`
- Files:
  - `apps/api/app/routes/sessions.py`
  - `apps/api/tests/test_sessions.py`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`19 passed, 1 warning`
  - `cd apps/api && uv run pytest tests/test_sessions.py tests/test_timelines.py -q`: 通过，
    `24 passed, 1 warning`
  - `cd apps/api && uv run pytest -q`: 通过，`35 passed, 1 warning`
  - `pnpm --dir apps/web test`: 通过，`2 passed` test files，`17 passed`；存在既有
    React async store `act(...)` warning
  - `pnpm --dir apps/web build`: 通过
  - `pnpm run test`: 通过；web `17 passed`，API `35 passed, 1 warning`
  - `pnpm run build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 新增回归测试覆盖从 main commit point 创建新 branch 后，立即
    `GET /sessions/{session_id}/replay-view?branch_id=<new>&tick=<commit tick>`。
  - `replay-view` 现在优先使用目标 branch 自己的 snapshot；没有 branch-local snapshot
    时，允许使用该 branch 的 `snapshot_reference` 或 commit point snapshot 作为基准。
  - 后续 `StateDiff` 和 `Event` 查询仍严格使用目标 branch id，避免混入 main branch
    的 diff / event。
  - 回归测试覆盖 branch-local snapshot 优先、main branch diff/event 不混入，以及
    target branch 自己的 diff/event 可应用。
- Notes:
  - 修复前新增测试红灯，复现 `422 No replay snapshot is available...`。
  - 本修复不复制 snapshot 行，不新增 WorldEngine 调用，不改变 branch 平铺语义。

## 范围审核

- 是否只通过 public API / 本地公开 evidence 数据连接 WorldEngine：Task 2 是；
  replay view 只读取本地公开 snapshot、state diff、event 和 branch 数据。
- 是否未引入客户端 LLM key 管理：Task 2 是。
- 是否未直接调用 LLM provider：Task 2 是。
- 是否未生成权威世界事实：Task 2 是；缺少可重建 snapshot 时返回错误，不编造
  replay 状态。
- 是否未引入 parent / child timeline 层级语义：Task 3 是。
- 是否未展示私有 Agent 内部状态、记忆、目标、隐藏推理或自我状态：Task 4 是；
  前端新增类型和 store 状态不引入 raw payload 展示。
- 是否不从摘要文本推断权威世界事实：Task 5 是；commit point browser 只显示后端
  提供的公开摘要和 tick。
- 是否未引入 parent / child timeline 层级语义：Task 6 是；UI 使用 branch / 世界线
  平铺语义。
- 是否未引入玩家角色控制：是。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：是。
- 是否未保存或展示 LLM key、provider secrets、私有 WorldEngine internals、私有
  Agent 内部状态：是；敏感字段扫描命中项均为过滤常量、边界文档、既有兼容
  raw event 类型/模型、测试反例或 review 记录。

## 遗留问题

- 实时 tick streaming 尚未实现。
- WorldEngine 运行推进 API 尚未实现。
- 导演引导提交闭环尚未实现。
- 完整 evidence bundle 导出尚未实现。
