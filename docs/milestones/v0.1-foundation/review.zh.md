# v0.1 Foundation Review

状态：代码骨架已实现；`v0.1-review-fix` 已验证；原始 v0.1 历史不声明为强流程 clean pass

日期：2026-06-02

## 结论

v0.1 当前是可运行的本地验证客户端骨架，但原始实现历史不满足当前
`docs/agent-guides/workflow.md` 的逐 task 提交和逐 task 记录要求。

本轮 `v0.1-review-fix` 已修复审核发现的代码问题：

- 会话库 UI 改为展示真实 `/health/worldengine` 结果，避免把本地 FastAPI
  `/health` 误报为 WorldEngine 连接状态。
- 默认 SQLite 路径固定解析到 `apps/api/.worldengine-validation-client/client.sqlite3`。
- branch 创建不再接受客户端任意覆盖 `snapshot_reference`，改为从 commit point
  的 `snapshot_id` 派生。
- 同一 session 下重复 branch name 返回 `409`。
- branch 加载和创建失败会收尾 loading 状态，运行控制台展示 branch 加载错误。
- 会话创建输入和导演输入补充可访问 label；分支列表不再复用可点击 session 样式。

## 流程偏离记录

以下问题不能通过普通代码补丁修复，只能如实记录：

- v0.1 主体实现主要集中在 `116f566 chore: finalize v0.1 foundation fixes`。
- 该提交不是按 `plan.zh.md` 的 Task 1-10 逐 task 独立提交。
- 因此本 review 不声明“原始 v0.1 历史按强流程 clean pass”。
- 后续 milestone 必须按 `workflow.md` 的 task loop 执行：实现、验证、记录、提交
  一个 numbered task 后，才能进入下一个 numbered task。

## Task Records

以下 records 是对既有 v0.1 主体实现的追认记录，不代表历史提交粒度合规。

### Task 1: 仓库骨架

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `package.json`
  - `pnpm-workspace.yaml`
  - `.gitignore`
  - `apps/api/README.md`
- Commands:
  - `git diff --check`: 本轮通过
- Scope review:
  - 工作区和基础脚本存在，未引入 WorldEngine 私有路径。
- Notes:
  - 历史提交粒度不符合当前 workflow。

### Task 2: FastAPI 后端基础

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/api/pyproject.toml`
  - `apps/api/app/main.py`
  - `apps/api/app/config.py`
  - `apps/api/app/db.py`
  - `apps/api/app/routes/health.py`
  - `apps/api/tests/test_health.py`
- Commands:
  - `uv run pytest -q`: 本轮通过，`11 passed, 1 warning`
- Scope review:
  - `/health` 返回本地服务状态和 `WORLDENGINE_API_BASE`；默认数据库路径已在
    `v0.1-review-fix` 中统一到 `apps/api/.worldengine-validation-client/client.sqlite3`。
- Notes:
  - warning 来自 Starlette TestClient/httpx 兼容提示。

### Task 3: SQLite 数据模型

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/api/app/models.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
  - `apps/api/tests/test_timelines.py`
- Commands:
  - `uv run pytest -q`: 本轮通过，`11 passed, 1 warning`
- Scope review:
  - 保持 branch 是命名世界线，不引入 parent/child 层级语义。
- Notes:
  - `v0.1-review-fix` 增加同 session branch name 唯一约束。

### Task 4: WorldEngine 连接检查

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/api/app/worldengine_client.py`
  - `apps/api/app/routes/health.py`
  - `apps/api/tests/test_health.py`
- Commands:
  - `uv run pytest -q`: 本轮通过，`11 passed, 1 warning`
- Scope review:
  - 只调用 `WORLDENGINE_API_BASE/health` 与 `/manifest`，不读取 LLM key，不依赖
    WorldEngine 本地路径。
- Notes:
  - 本轮新增测试直接覆盖 client 调用 public `/health` 与 `/manifest`。

### Task 5: Session 和 Branch API

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/routes/timelines.py`
  - `apps/api/tests/test_sessions.py`
  - `apps/api/tests/test_timelines.py`
- Commands:
  - `uv run pytest -q`: 本轮通过，`11 passed, 1 warning`
- Scope review:
  - `POST /sessions` 自动创建 main branch；branch 创建校验 commit point 属于
    session。
- Notes:
  - `v0.1-review-fix` 修复 `snapshot_reference` 语义，拒绝重复 branch name。

### Task 6: Evidence Bundle Metadata

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/api/app/routes/evidence.py`
  - `apps/api/tests/test_evidence.py`
- Commands:
  - `uv run pytest -q`: 本轮通过，`11 passed, 1 warning`
- Scope review:
  - evidence metadata 明确 `llm_keys_included: false` 和
    `private_worldengine_internals_included: false`。
- Notes:
  - 完整 evidence bundle 导出仍属于后续 milestone。

### Task 7: React 前端基础

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/web/package.json`
  - `apps/web/index.html`
  - `apps/web/vite.config.ts`
  - `apps/web/tsconfig.json`
  - `apps/web/src/main.tsx`
  - `apps/web/src/App.tsx`
  - `apps/web/src/styles.css`
- Commands:
  - `pnpm --dir apps/web build`: 本轮通过
- Scope review:
  - Vite/React 基础骨架可构建。
- Notes:
  - 无。

### Task 8: 会话库 UI

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/pages/SessionLibrary.tsx`
  - `apps/web/src/components/ConnectionStatus.tsx`
  - `apps/web/src/__tests__/SessionLibrary.test.tsx`
- Commands:
  - `pnpm --dir apps/web test`: 本轮通过，`4 passed`
  - `pnpm --dir apps/web build`: 本轮通过
- Scope review:
  - 前端只调用本地 FastAPI 后端；会话库显示真实 WorldEngine 连接状态。
- Notes:
  - `v0.1-review-fix` 修复 UI 误报 WorldEngine 连接状态。

### Task 9: 运行控制台骨架

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/components/PixelWorldCanvas.tsx`
  - `apps/web/src/components/TimelineBranchList.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
- Commands:
  - `pnpm --dir apps/web test`: 本轮通过，`4 passed`
  - `pnpm --dir apps/web build`: 本轮通过
- Scope review:
  - 保持运行控制台骨架范围，不实现 run/tick 业务动作。
- Notes:
  - `v0.1-review-fix` 增加 branch 加载失败错误态。

### Task 10: 总体验证

- Commit: `116f566`（历史聚合提交，非 task-scoped）
- Files:
  - `docs/milestones/v0.1-foundation/review.zh.md`
- Commands:
  - `uv run pytest -q`: 本轮通过，`11 passed, 1 warning`
  - `pnpm --dir apps/web test`: 本轮通过，`4 passed`
  - `pnpm --dir apps/web build`: 本轮通过
  - `pnpm run test`: 本轮通过，前端 `4 passed`，后端 `11 passed, 1 warning`
  - `pnpm run build`: 本轮通过
  - `git diff --check`: 本轮通过
- Scope review:
  - 当前代码通过总体验证；原始 task-level commit 证据不足已单独记录。
- Notes:
  - 首次 sandbox 内运行 `pnpm run test` 时，API 子命令被 `~/.cache/uv` 权限阻止；
    已按权限规则提升权限重跑并通过。

## v0.1-review-fix Record

### Review Fix: 修复审核阻塞项

- Commit: `7683744`
- Files:
  - `apps/api/app/config.py`
  - `apps/api/app/models.py`
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_health.py`
  - `apps/api/tests/test_timelines.py`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/__tests__/SessionLibrary.test.tsx`
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/components/TimelineBranchList.tsx`
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/pages/SessionLibrary.tsx`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/styles.css`
  - `docs/milestones/v0.1-foundation/README.zh.md`
  - `docs/milestones/v0.1-foundation/plan.zh.md`
  - `docs/milestones/v0.1-foundation/review.zh.md`
- Commands:
  - `uv run pytest tests/test_health.py tests/test_timelines.py -q`: RED 后 GREEN，本轮最终
    `8 passed, 1 warning`
  - `pnpm --dir apps/web test -- SessionLibrary.test.tsx RuntimeConsole.test.tsx`: RED 后
    GREEN，本轮最终 `4 passed`
  - `uv run pytest -q`: `11 passed, 1 warning`
  - `pnpm --dir apps/web test`: `4 passed`
  - `pnpm --dir apps/web build`: 通过
  - `pnpm run test`: 通过
  - `pnpm run build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 保持本仓库为外部验证客户端，只通过 public API 与 WorldEngine 通信。
  - 未管理 LLM key，未调用 LLM provider，未导入 WorldEngine 源码，未生成权威世界事实。
  - 未实现 v0.1 禁止范围：完整像素模拟、实时 tick streaming、完整 evidence bundle 导出、
    玩家角色控制。
- Notes:
  - 本轮修复不重写历史，不把 `116f566` 伪造成 task-scoped commit。

## 范围审核

- 是否只通过 public API 连接 WorldEngine：是。
- 是否未引入客户端 LLM key 管理：是。
- 是否未直接调用 LLM provider：是。
- 是否未生成权威世界事实：是。
- 是否未引入玩家角色控制：是。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：是。
- timeline branch 是否保持命名世界线语义、不表达 parent-child ownership：是。

## 遗留问题

- 原始 v0.1 历史提交粒度不满足当前强流程，不能作为“强流程 clean pass”证据。
- 后续 v0.2 或其他 milestone 必须严格按 numbered task loop 执行并逐 task 提交。
- 完整 world create/run/tick、实时 streaming、像素渲染和 evidence bundle 导出仍属于后续
  milestone。
