# v0.4 Replay And Branching Review

状态：实现中

日期：2026-06-03

## 结论

v0.4 目标是基础 Replay And Branching：后端从公开 snapshot + state diff 重建
replay view，前端运行控制台展示时间线 scrubber、commit point 浏览、branch 切换
和从 commit point 创建 branch 的基础体验。

当前已完成 milestone 文档创建和后端 replay read model API。后续仍需深化
commit point / branch 上下文，并完成前端 replay / branch 体验。

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

- Commit: `待提交`
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
- 是否未引入玩家角色控制：待实现后验证。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：待实现后验证。

## 遗留问题

- 时间线 scrubber、commit point 浏览、branch 切换和创建 UI 尚未实现。
