# v0.1 Foundation 实现计划

状态：待实现

## 实现目标

交付一个可启动的本地验证客户端骨架：

- `apps/web`：React/Vite 前端。
- `apps/api`：FastAPI 后端。
- SQLite 本地数据库。
- 会话库第一屏。
- 运行控制台骨架。
- WorldEngine public API 连接检查。
- commit point / branch 存储模型。
- evidence bundle metadata endpoint。

## 技术栈

- 前端：React、Vite、TypeScript、PixiJS、Zustand。
- 后端：Python、FastAPI、Pydantic、SQLAlchemy。
- 数据库：SQLite。
- 测试：pytest、Vitest。

## 任务

### 1. 仓库骨架

创建：

```text
package.json
pnpm-workspace.yaml
apps/api/README.md
```

更新：

```text
.gitignore
```

要求：

- 支持 `pnpm --dir apps/web dev`。
- 支持 `cd apps/api && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8765`。
- 忽略 `.env`、SQLite 文件、Python cache、node_modules 和构建产物。

验证：

```bash
git diff --check
```

### 2. FastAPI 后端基础

创建：

```text
apps/api/pyproject.toml
apps/api/app/main.py
apps/api/app/config.py
apps/api/app/db.py
apps/api/app/routes/health.py
apps/api/tests/test_health.py
```

要求：

- `/health` 返回本地服务状态和 `WORLDENGINE_API_BASE`。
- 配置来自环境变量。
- SQLite 默认保存在 `apps/api/.worldengine-validation-client/client.sqlite3`。

验证：

```bash
cd apps/api && uv run pytest tests/test_health.py -q
```

### 3. SQLite 数据模型

创建：

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
apps/api/tests/test_timelines.py
```

模型：

- `sessions`
- `timeline_branches`
- `commit_points`
- `events`
- `state_diffs`
- `snapshots`
- `director_intents`

语义：

- 可重建 tick / event point 作为 `commit_point`。
- `branch` 是命名世界线。
- branch 记录 `branch_id`、`branch_name`、`commit_point_id`、`tick`、
  `snapshot_reference`，不表达父子关系。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py tests/test_timelines.py -q
```

### 4. WorldEngine 连接检查

创建：

```text
apps/api/app/worldengine_client.py
```

更新：

```text
apps/api/app/routes/health.py
apps/api/tests/test_health.py
```

要求：

- `/health/worldengine` 调用 WorldEngine public `/health`。
- 尝试读取 public `/manifest`。
- 不读取 LLM key。
- 不依赖 WorldEngine 本地路径。

验证：

```bash
cd apps/api && uv run pytest tests/test_health.py -q
```

### 5. Session 和 Branch API

创建：

```text
apps/api/app/routes/sessions.py
apps/api/app/routes/timelines.py
```

要求：

- `POST /sessions` 创建 session，并自动创建 `main` branch。
- `GET /sessions` 列出本地 sessions。
- `GET /sessions/{session_id}/branches` 列出 branches。
- `POST /sessions/{session_id}/branches` 从指定 commit point 创建命名 branch。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py tests/test_timelines.py -q
```

### 6. Evidence Bundle Metadata

创建：

```text
apps/api/app/routes/evidence.py
apps/api/tests/test_evidence.py
```

要求：

- `GET /sessions/{session_id}/evidence/bundle` 返回证据包 metadata。
- 返回 session 信息、branch/event/diff/snapshot 计数。
- 明确 redaction flags：
  - `llm_keys_included: false`
  - `private_worldengine_internals_included: false`

验证：

```bash
cd apps/api && uv run pytest tests/test_evidence.py -q
```

### 7. React 前端基础

创建：

```text
apps/web/package.json
apps/web/index.html
apps/web/vite.config.ts
apps/web/tsconfig.json
apps/web/src/main.tsx
apps/web/src/App.tsx
apps/web/src/styles.css
```

要求：

- 可启动 Vite。
- 可构建。
- 页面显示 `WorldEngine Validation Client`。

验证：

```bash
pnpm install
pnpm --dir apps/web build
```

### 8. 会话库 UI

创建：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/pages/SessionLibrary.tsx
apps/web/src/components/ConnectionStatus.tsx
apps/web/src/__tests__/SessionLibrary.test.tsx
```

要求：

- 显示 WorldEngine 连接状态。
- 显示 session 列表。
- 支持创建本地 session。
- 前端只调用本地 FastAPI 后端。

验证：

```bash
pnpm --dir apps/web test
```

### 9. 运行控制台骨架

创建：

```text
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/components/PixelWorldCanvas.tsx
apps/web/src/components/TimelineBranchList.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

要求：

- 显示 Run / Pause / Single Tick 控制。
- 显示导演引导输入框。
- 显示 PixiJS 像素画布占位。
- 显示 branch 列表和事件日志占位。

验证：

```bash
pnpm --dir apps/web test
pnpm --dir apps/web build
```

### 10. 总体验证

运行：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

完成后更新：

```text
docs/milestones/v0.1-foundation/review.zh.md
```

记录：

- 变更文件。
- 命令结果。
- 未实现的后续范围。
- WorldEngine 边界是否保持。
- LLM key 是否未暴露。

## 提交建议

每完成 1-2 个任务提交一次，避免一个大提交吞掉所有实现。
