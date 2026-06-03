# v0.2 WorldEngine Integration 实现计划

状态：实现完成 / 总体验证通过 / review 修复已收口

## 实现目标

交付一个只通过 public API 与 WorldEngine 集成的创建世界闭环：

- 发现 WorldEngine public manifest / OpenAPI 能力。
- 代理调用 WorldEngine public world creation API。
- 保存本地 session、main branch、初始 snapshot、commit point 和公开事件。
- 保存脱敏 API trace。
- 前端支持输入世界观并创建世界。
- 运行控制台展示公开初始状态摘要和 visualization payload 摘要。

## 技术栈

- 后端：FastAPI、Pydantic、SQLAlchemy、SQLite、httpx。
- 前端：React、Vite、TypeScript、Zustand。
- 测试：pytest、Vitest。

## 任务

### 1. v0.2 里程碑文档

创建：

```text
docs/milestones/v0.2-worldengine-integration/README.zh.md
docs/milestones/v0.2-worldengine-integration/plan.zh.md
docs/milestones/v0.2-worldengine-integration/review.zh.md
```

更新：

```text
docs/README.zh.md
```

要求：

- 明确 v0.2 目标、范围、非目标、验证命令和 commit 边界。
- 明确缺少里程碑文档时不得直接实现。
- 保持 WorldEngine 外部验证客户端边界。

验证：

```bash
git diff --check
```

### 2. WorldEngine 能力发现客户端

更新：

```text
apps/api/app/worldengine_client.py
apps/api/app/routes/health.py
apps/api/app/schemas.py
apps/api/tests/test_health.py
```

要求：

- 读取 public `/health`、`/manifest`。
- 尝试读取 public `/openapi.json`，失败时以 degraded capability 记录，不阻塞
  `/health/worldengine`。
- 返回能力摘要时不得包含 LLM key、provider secrets、私有路径或内部 helper 信息。
- 不依赖 WorldEngine 源码。

验证：

```bash
cd apps/api && uv run pytest tests/test_health.py -q
```

### 3. 本地 world creation 存储模型

更新：

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
```

要求：

- session 支持保存 WorldEngine world id、公开 world status、公开 initial state
  摘要和 visualization payload 摘要。
- 新增或扩展 `api_traces` 存储脱敏请求/响应元数据。
- 不存储 LLM key、私有 prompt、私有 evaluator oracle internals、私有 WorldEngine
  路径或非公开 payload。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py -q
```

### 4. WorldEngine world creation API

更新：

```text
apps/api/app/worldengine_client.py
apps/api/app/routes/sessions.py
apps/api/app/routes/evidence.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
apps/api/tests/test_evidence.py
```

要求：

- `POST /sessions/worldengine` 接收自然语言世界观和 session name。
- 后端只调用配置的 `WORLDENGINE_API_BASE` 下 public world creation endpoint。
- 成功后创建本地 session、main branch、初始 snapshot、commit point 和
  `world_created` 公开事件。
- 保存脱敏 API trace，trace 不包含 secrets 或私有 internals。
- WorldEngine 不可达或返回错误时返回可解释错误，不创建半成品 session。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py tests/test_evidence.py -q
```

### 5. 前端创建世界入口

更新：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/pages/SessionLibrary.tsx
apps/web/src/__tests__/SessionLibrary.test.tsx
```

要求：

- 会话库提供世界观输入和创建世界按钮。
- 创建世界只调用本地 FastAPI 后端。
- 创建成功后刷新 session 列表并可进入运行控制台。
- 创建失败时展示可读错误。

验证：

```bash
pnpm --dir apps/web test -- SessionLibrary.test.tsx
```

### 6. 运行控制台公开状态摘要

更新：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

要求：

- 运行控制台展示 session 绑定的 WorldEngine world id。
- 展示公开初始状态摘要、visualization payload 摘要、最新公开事件。
- 继续保持 Run / Pause / Single Tick 为非业务占位，不实现实时 tick。
- 不展示或暗示私有 Agent 内部状态。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web build
```

### 7. 总体验证和 review 收口

更新：

```text
docs/milestones/v0.2-worldengine-integration/review.zh.md
```

运行：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

记录：

- 每个 task 的 commit。
- 变更文件。
- 命令结果。
- Scope review。
- 未实现的后续范围。
- WorldEngine public API 边界是否保持。
- LLM key、provider secrets、私有 WorldEngine internals 是否未保存和未展示。

## Stop Rules

- 如果 WorldEngine public world creation endpoint 的路径或返回结构无法从 public
  manifest / OpenAPI 推断，不得调用私有路径；应记录 blocker。
- 如果实现需要 WorldEngine 源码、私有 helper、私有 prompt 或 LLM key，停止并
  记录越界风险。
- 如果任何 task 的验证失败，只能继续做针对该失败的窄修复。
- 如果发现 `plan.zh.md` 与实际 public API 不匹配，先更新 milestone 文档并提交，
  再恢复实现。
- 不得在相关实现文件仍未提交时声明 v0.2 完成。

## 提交边界

每个 numbered task 必须单独提交。提交应只包含该 task 需要的文件。
