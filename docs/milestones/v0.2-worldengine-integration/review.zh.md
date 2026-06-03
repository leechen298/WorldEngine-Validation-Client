# v0.2 WorldEngine Integration Review

状态：计划已创建 / 实现待开始

日期：2026-06-03

## 结论

v0.2 当前尚未实现。本文档只记录里程碑计划创建和后续 task-level evidence。
在所有 planned tasks 完成、验证通过、逐 task 提交且工作区无相关未提交变更前，
不得声明 v0.2 complete 或 clean pass。

## Task Records

### Task 1: v0.2 里程碑文档

- Commit: `9002da8`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.2-worldengine-integration/README.zh.md`
  - `docs/milestones/v0.2-worldengine-integration/plan.zh.md`
  - `docs/milestones/v0.2-worldengine-integration/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.2 milestone 文档，明确 public API 边界、禁止范围、task 顺序、
    验证命令和逐 task commit 要求。
- Notes:
  - v0.2 代码实现尚未开始。

### Task 2: WorldEngine 能力发现客户端

- Commit: `pending`
- Files:
  - `apps/api/app/worldengine_client.py`
  - `apps/api/app/routes/health.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_health.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_health.py -q`: `pending`
- Scope review:
  - `pending`
- Notes:
  - `pending`

### Task 3: 本地 world creation 存储模型

- Commit: `pending`
- Files:
  - `apps/api/app/models.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: `pending`
- Scope review:
  - `pending`
- Notes:
  - `pending`

### Task 4: WorldEngine world creation API

- Commit: `pending`
- Files:
  - `apps/api/app/worldengine_client.py`
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/routes/evidence.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
  - `apps/api/tests/test_evidence.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py tests/test_evidence.py -q`: `pending`
- Scope review:
  - `pending`
- Notes:
  - `pending`

### Task 5: 前端创建世界入口

- Commit: `pending`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/pages/SessionLibrary.tsx`
  - `apps/web/src/__tests__/SessionLibrary.test.tsx`
- Commands:
  - `pnpm --dir apps/web test -- SessionLibrary.test.tsx`: `pending`
- Scope review:
  - `pending`
- Notes:
  - `pending`

### Task 6: 运行控制台公开状态摘要

- Commit: `pending`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: `pending`
  - `pnpm --dir apps/web build`: `pending`
- Scope review:
  - `pending`
- Notes:
  - `pending`

### Task 7: 总体验证和 review 收口

- Commit: `pending`
- Files:
  - `docs/milestones/v0.2-worldengine-integration/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest -q`: `pending`
  - `pnpm --dir apps/web test`: `pending`
  - `pnpm --dir apps/web build`: `pending`
  - `pnpm run test`: `pending`
  - `pnpm run build`: `pending`
  - `git diff --check`: `pending`
- Scope review:
  - `pending`
- Notes:
  - `pending`

## 范围审核

- 是否只通过 public API 连接 WorldEngine：待验证。
- 是否未引入客户端 LLM key 管理：待验证。
- 是否未直接调用 LLM provider：待验证。
- 是否未生成权威世界事实：待验证。
- 是否未引入玩家角色控制：待验证。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：待验证。
- timeline branch 是否保持命名世界线语义、不表达 parent-child ownership：待验证。

## 遗留问题

- v0.2 代码实现尚未开始。
