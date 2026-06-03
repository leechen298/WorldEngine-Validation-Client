# v0.3 Runtime Visualization 实现计划

状态：实现完成 / review 修复验证通过

## 实现目标

交付一个只基于公开 WorldEngine 状态和本地 evidence 数据的基础运行可视化：

- 后端把公开 snapshot、event 和 visualization payload 规整成 runtime view。
- 前端读取 runtime view 并在运行控制台展示基础 tick、像素地图、Agent 公开状态
  和公开事件日志。
- PixiJS 画面可在缺少 payload 时降级显示 empty state。
- 不引入实时 streaming、回放分支重建、玩家控制或私有 Agent 内部状态展示。

## 技术栈

- 后端：FastAPI、Pydantic、SQLAlchemy、SQLite。
- 前端：React、Vite、TypeScript、Zustand、PixiJS。
- 测试：pytest、Vitest。

## 任务

### 1. v0.3 里程碑文档

创建：

```text
docs/milestones/v0.3-runtime-visualization/README.zh.md
docs/milestones/v0.3-runtime-visualization/plan.zh.md
docs/milestones/v0.3-runtime-visualization/review.zh.md
```

更新：

```text
docs/README.zh.md
```

要求：

- 明确 v0.3 目标、范围、非目标、验证命令和 commit 边界。
- 明确 runtime visualization 只能来自公开 snapshot、event 和 visualization
  payload。
- 保持 WorldEngine 外部验证客户端边界。

验证：

```bash
git diff --check
```

### 2. 本地 runtime view API

更新：

```text
apps/api/app/routes/sessions.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
```

要求：

- 新增 `GET /sessions/{session_id}/runtime-view`。
- 返回基础 tick、公开 world status、公开 visualization payload、公开 Agent 状态列
  表、world log、Agent life log 和最新公开事件。
- 数据只能来自本地已保存的公开 snapshot / event，不调用 WorldEngine 私有接口。
- 对 payload 做 allowlist / redaction，禁止透传 private/internal/helper/path/secret/key
  等字段。
- session 不存在时返回 `404`。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py -q
```

### 3. 前端 runtime view client 和状态

更新：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

要求：

- 定义 runtime view TypeScript 类型。
- 新增本地 API client 调用 `GET /sessions/{session_id}/runtime-view`。
- store 能加载并缓存当前 session 的 runtime view。
- 运行控制台加载失败时展示可读错误。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
```

### 4. PixiJS 基础地图画面

更新：

```text
apps/web/src/components/PixelWorldCanvas.tsx
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/src/styles.css
```

要求：

- `PixelWorldCanvas` 接收 runtime visualization payload。
- 使用 PixiJS 渲染基础 tile / entity 静态视图。
- 缺少 payload 或 payload 为空时展示 empty state。
- 画布只展示公开可视化数据，不推断权威世界事实。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web build
```

### 5. Agent 公开状态和事件日志面板

更新：

```text
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/src/styles.css
```

要求：

- 展示基础 tick。
- 展示 Agent 公开状态面板，只包含 public payload 中的展示字段。
- 展示公开事件气泡、world log 和 Agent life log。
- 不展示或暗示私有 Agent 内部记忆、目标、隐藏推理或自我状态。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web build
```

### 6. 总体验证和 review 收口

更新：

```text
docs/milestones/v0.3-runtime-visualization/review.zh.md
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
- 是否未保存或展示 LLM key、provider secrets、私有 WorldEngine internals、私有
  Agent 内部状态。

## Stop Rules

- 如果 runtime visualization 需要 WorldEngine 私有源码、私有 helper、私有 prompt
  或 LLM key，停止并记录越界风险。
- 如果公开 snapshot / visualization payload 中没有足够信息，不得编造权威世界事
  实；应展示 empty / degraded state。
- 如果任何 task 的验证失败，只能继续做针对该失败的窄修复。
- 如果发现 `plan.zh.md` 与实际 public payload 不匹配，先更新 milestone 文档并提
  交，再恢复实现。
- 不得在相关实现文件仍未提交时声明 v0.3 完成。

## 提交边界

每个 numbered task 必须单独提交。提交应只包含该 task 需要的文件。
