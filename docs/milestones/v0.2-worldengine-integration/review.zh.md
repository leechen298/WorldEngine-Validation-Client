# v0.2 WorldEngine Integration Review

状态：实现完成 / 总体验证通过 / review 修复已收口

日期：2026-06-03

## 结论

v0.2 已完成 WorldEngine public API 集成闭环：能力发现、public world creation
代理、本地公开状态/visualization 摘要落库、脱敏 API trace、前端创建世界入口和
运行控制台公开状态摘要。

本轮按 `docs/agent-guides/workflow.md` 的 numbered task loop 执行；Task 1-6
均已有 task-scoped implementation commit 和 review record。Task 7 为总体验证和
review 收口记录。当前记录使用 `v0.2` 分支经 current-time rewrite 后的提交 hash；
`v0.2-local` 上同内容旧 hash 仅作为 patch 等价来源，不作为本分支证据引用。

## Task Records

### Task 1: v0.2 里程碑文档

- Commit: `ab3f3fa`（task-scoped docs commit；后续 hash 记录由 review 跟进提交补充）
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
  - Task 1 提交时 v0.2 代码实现尚未开始；后续 task 已完成实现和验证。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录用后续
    docs-only review 提交补充可见 hash。

### Task 2: WorldEngine 能力发现客户端

- Commit: `3d95d98`
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
  - review 修复：health 成功后立即保留 `reachable=True`；`/manifest` 或
    `/openapi.json` 失败只记录 degraded capability/error，不把已确认可达误报为不可达。
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。

### Task 3: 本地 world creation 存储模型

- Commit: `7f1cd1a`
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

- Commit: `c6a555e`
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

- Commit: `5828ecd`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/pages/SessionLibrary.tsx`
  - `apps/web/src/__tests__/SessionLibrary.test.tsx`
  - `apps/web/src/styles.css`
- Commands:
  - `pnpm --dir apps/web test -- SessionLibrary.test.tsx`: 通过，`2 passed` test files，`6 passed`
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 会话库创建入口改为输入 session name 和世界观，调用本地 FastAPI
    `/sessions/worldengine`，成功后刷新本地 session store 并打开运行控制台，失败时展示
    可读错误。
- Notes:
  - `apps/web/src/styles.css` 是表单布局所需窄改动。
  - subagent reviewer 指出创建成功后应重新拉取 session 列表、错误应展示后端
    `detail`；已补 `getSessions()` refresh 和 JSON error parsing 回归测试。

### Task 6: 运行控制台公开状态摘要

- Commit: `473894c`
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
- Commands:
  - `pnpm --dir apps/web test -- RuntimeConsole.test.tsx`: 通过，`2 passed` test files，`7 passed`
  - `pnpm --dir apps/web build`: 通过
  - `git diff --check`: 通过
- Scope review:
  - 运行控制台展示 session 绑定的 WorldEngine world id、公开状态、初始状态摘要、
    visualization payload 摘要和最新公开事件；Run/Pause/Single Tick 仍保持占位。
- Notes:
  - 事件读取只调用本地 FastAPI `/sessions/{session_id}/events`。
  - subagent reviewer 未发现 P1/P2；已补多事件测试锁定“最新公开事件”选择逻辑。

### Task 7: 总体验证和 review 收口

- Commit: `2ea9ef8`
- Files:
  - `docs/milestones/v0.2-worldengine-integration/review.zh.md`
- Commands:
  - `cd apps/api && uv run pytest -q`: 通过，`26 passed, 1 warning`
  - `pnpm --dir apps/web test`: 通过，`2 passed` test files，`7 passed`
  - `pnpm --dir apps/web build`: 通过
  - `pnpm run test`: sandbox 内因 `~/.cache/uv` 权限失败；提升权限重跑通过，web
    `7 passed`，API `26 passed, 1 warning`
  - `pnpm run build`: 通过
  - `git diff --check`: 通过
  - review 修复补跑 `cd apps/api && uv run pytest tests/test_health.py -q`: 通过，`9 passed, 1 warning`
  - review 修复补跑 `cd apps/api && uv run pytest -q`: 通过，`26 passed, 1 warning`
  - review 修复补跑 `pnpm --dir apps/web test`: 通过，`7 passed`
  - review 修复补跑 `pnpm --dir apps/web build`: 通过
  - review 修复补跑 `pnpm run test`: sandbox 内因 `~/.cache/uv` 权限失败；提升权限重跑通过，web
    `7 passed`，API `26 passed, 1 warning`
  - review 修复补跑 `pnpm run build`: 通过
  - review 修复补跑 `git diff --check`: 通过
- Scope review:
  - v0.2 仅通过 `WORLDENGINE_API_BASE` 下 public `/health`、`/manifest`、
    `/openapi.json` 和发现到的 public world creation endpoint 与 WorldEngine 通信。
    前端只调用本地 FastAPI；未实现实时 tick streaming、完整 PixiJS 渲染、完整
    evidence bundle 导出或玩家角色控制。
- Notes:
  - warning 来自现有 Starlette TestClient/httpx 兼容提示。
  - root `pnpm run test` 的首次失败是 sandbox cache 权限问题，不是测试失败。

## 范围审核

- 是否只通过 public API 连接 WorldEngine：是。
- 是否未引入客户端 LLM key 管理：是。
- 是否未直接调用 LLM provider：是。
- 是否未生成权威世界事实：是；仅保存 WorldEngine public response 的脱敏摘要。
- 是否未引入玩家角色控制：是。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：是。
- timeline branch 是否保持命名世界线语义、不表达 parent-child ownership：是。

## 遗留问题

- 实时 tick streaming、完整 PixiJS 像素渲染、回放/分支操作深化和完整 evidence bundle
  导出仍属于后续 milestone。
- `StarletteDeprecationWarning` 来自当前 TestClient/httpx 组合，未影响本轮通过结论。
