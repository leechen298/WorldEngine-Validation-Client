# v0.2 WorldEngine Integration Review

状态：计划已创建 / 实现待开始

日期：2026-06-03

## 结论

v0.2 当前尚未实现。本文档只记录里程碑计划创建和后续 task-level evidence。
在所有 planned tasks 完成、验证通过、逐 task 提交且工作区无相关未提交变更前，
不得声明 v0.2 complete 或 clean pass。

## Task Records

### Task 1: v0.2 里程碑文档

- Commit: `ce54663`（task-scoped docs commit；后续 hash 记录由 review 跟进提交补充）
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
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 2: WorldEngine 能力发现客户端

- Commit: `5a098f4`
- Files:
  - `apps/api/app/worldengine_client.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_health.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_health.py -q`: 通过，`8 passed, 1 warning`
  - `git diff --check`: 通过
  - `rg -n "worldengine|WORLDENGINE|openapi|manifest|api_key|apikey|secret|token|password|credential|authorization|private_path|file_path|source_path|internal|helper|provider" apps/api/app apps/api/tests docs/milestones/v0.2-worldengine-integration/review.zh.md`: 通过；命中项为 public API 名称、测试用脱敏 fixture 和边界说明，未发现生产代码透传 secret/private/internal payload。
- Scope review:
  - 能力发现只调用 `WORLDENGINE_API_BASE` 下 public `/health`、`/manifest`、
    `/openapi.json`；OpenAPI 失败只记录 capability/error，不阻塞
    `/health/worldengine` reachable；响应只返回白名单安全摘要，不透传原始
    manifest/OpenAPI payload。
- Notes:
  - `apps/api/app/routes/health.py` 未改动；既有 route 通过新的 response model
    返回结构化 capability 摘要。
  - subagent reviewer 指出原始 discovery payload 暴露面过大；已改为 health status、
    manifest version/capability names、OpenAPI title/version/world creation endpoint 摘要。
  - subagent re-review 指出 summary-only world creation 仍有误判风险；已移除 summary
    heuristic，并新增回归测试。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。

### Task 3: 本地 world creation 存储模型

- Commit: `775ecf6`
- Files:
  - `apps/api/app/models.py`
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py -q`: 通过，`4 passed, 1 warning`
  - `git diff --check`: 通过
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|file_path|source_path|private prompt|oracle|internal|helper|provider" apps/api/app/models.py apps/api/app/schemas.py apps/api/app/routes/sessions.py apps/api/tests/test_sessions.py docs/milestones/v0.2-worldengine-integration/review.zh.md`: 通过；命中项为 redaction flag、测试断言和边界说明，未发现实际 secret/private payload 存储字段。
- Scope review:
  - session 模型新增 WorldEngine world id、公开状态、公开 initial state 摘要和
    visualization payload 摘要字段；新增 `api_traces` 存储脱敏请求/响应摘要、
    HTTP 元数据和 redaction flags。
- Notes:
  - `apps/api/app/routes/sessions.py` 为 schema 映射需要的窄改动，保持现有本地
    session 创建语义不变。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。

### Task 4: WorldEngine world creation API

- Commit: `561675e`
- Files:
  - `apps/api/app/worldengine_client.py`
  - `apps/api/app/routes/sessions.py`
  - `apps/api/app/routes/evidence.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_sessions.py`
  - `apps/api/tests/test_evidence.py`
- Commands:
  - `cd apps/api && uv run pytest tests/test_sessions.py tests/test_evidence.py -q`: 通过，`13 passed, 1 warning`
  - `git diff --check`: 通过
  - `rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|file_path|source_path|\bpath\b|\bkey\b|private prompt|oracle|internal|helper|provider" apps/api/app apps/api/tests docs/milestones/v0.2-worldengine-integration/review.zh.md`: 通过；命中项为生产过滤表、redaction flag、测试用脱敏 fixture 和边界说明，未发现实际保存 secret/private payload。
- Scope review:
  - `POST /sessions/worldengine` 先通过 public OpenAPI 发现 world creation endpoint；
    发现不到或调用失败时返回 `502` 且不创建本地 session。成功后在一个本地事务中写入
    session、main branch、初始 snapshot、commit point、`world_created` event 和脱敏
    `api_trace`。
- Notes:
  - initial state 与 visualization payload 会过滤 private/internal/helper/path/secret
    等字段后再保存摘要和 snapshot。
  - subagent reviewer 指出裸 `path`/`key`、缺失 world id、private/internal endpoint
    和 commit point event 关联风险；已补过滤/拒绝逻辑和回归测试，并回填
    `CommitPoint.event_id`。
  - subagent re-review 确认 P1/P2 清零；已补 route 级缺失 world id 不落库回归。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。

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
