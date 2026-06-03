# v0.4 Replay And Branching 实现计划

状态：实现完成 / 验证通过

## 实现目标

交付一个只基于公开 WorldEngine 状态和本地 evidence 数据的基础回放与世界线
分支体验：

- 后端可以从指定 branch 的最近前置 snapshot 开始，按 tick 顺序应用公开
  state diff，重建目标 tick 的公开 replay view。
- 前端运行控制台可以浏览 commit point、拖动或选择 replay tick、切换 branch，并
  从 commit point 创建新 branch。
- 所有 replay / branch 展示都复用 v0.3 的 public runtime view 字段，不透传原始
  private/internal payload。

## 技术栈

- 后端：FastAPI、Pydantic、SQLAlchemy、SQLite。
- 前端：React、Vite、TypeScript、Zustand、PixiJS。
- 测试：pytest、Vitest。

## 任务

### 1. v0.4 里程碑文档

创建：

```text
docs/milestones/v0.4-replay-branching/README.zh.md
docs/milestones/v0.4-replay-branching/plan.zh.md
docs/milestones/v0.4-replay-branching/review.zh.md
```

更新：

```text
docs/README.zh.md
```

要求：

- 明确 v0.4 目标、范围、非目标、验证命令和 commit 边界。
- 明确 replay / branch 只能来自公开 snapshot、state diff、event 和 commit point。
- 保持 WorldEngine 外部验证客户端边界。

验证：

```bash
git diff --check
```

### 2. 后端 replay read model API

更新：

```text
apps/api/app/routes/sessions.py
apps/api/app/schemas.py
apps/api/tests/test_sessions.py
```

要求：

- 新增 `GET /sessions/{session_id}/replay-view`，支持 `branch_id` 和 `tick` query。
- 未提供 `branch_id` 时默认使用 main branch。
- 找到目标 branch 中不晚于目标 tick 的最近 snapshot，并按 tick 顺序应用后续
  `StateDiff.diff_json`。
- 返回字段沿用 public runtime view 语义：目标 tick、公开 visualization、公开 Agent
  状态、world log、Agent life log、latest event、branch id 和 snapshot id。
- state diff 只支持公开 patch 数据；禁止透传 private/internal/helper/path/secret/key
  等字段。
- session 或 branch 不存在时返回 `404`；目标 tick 早于可重建 snapshot 时返回可读
  错误。

验证：

```bash
cd apps/api && uv run pytest tests/test_sessions.py -q
```

### 3. 后端 commit point / branch 上下文深化

更新：

```text
apps/api/app/routes/timelines.py
apps/api/app/schemas.py
apps/api/tests/test_timelines.py
```

要求：

- commit point 列表包含 tick、event id、snapshot id、branch 引用和可展示摘要。
- branch 列表标识 main branch、当前 tick 和 snapshot reference。
- 从 commit point 创建 branch 时，返回可直接用于 replay 的 branch context。
- 不引入 parent / child timeline 层级语义。

验证：

```bash
cd apps/api && uv run pytest tests/test_timelines.py -q
```

### 4. 前端 replay / branch typed client 和状态

更新：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

要求：

- 定义 replay view、commit point 和 branch context TypeScript 类型。
- 新增 replay view、commit point list、branch list 和 branch creation client 方法。
- store 能保存当前 branch、目标 tick、commit point 列表、branch 列表和 replay
  view。
- replay 或 branch 加载失败时展示可读错误状态。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
```

### 5. 运行控制台时间线 scrubber 和 commit point 浏览

更新：

```text
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/src/styles.css
```

要求：

- 展示当前 branch、目标 tick、可用 tick 范围和基础 scrubber。
- 展示 commit point 列表，可选择 commit point 并加载对应 replay view。
- replay view 缺少 payload 时展示 degraded / empty state。
- 不从摘要文本推断权威世界事实。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web build
```

### 6. 运行控制台 branch 切换和创建

更新：

```text
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/components/TimelineBranchList.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/src/__tests__/SessionLibrary.test.tsx
apps/web/src/styles.css
```

要求：

- 展示 branch 列表并支持切换当前 branch。
- 支持从选中的 commit point 创建 branch。
- 创建成功后刷新 branch / commit point / replay view 状态。
- UI 文案使用“branch / 世界线”，不使用 parent / child timeline 层级语义。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web test -- SessionLibrary.test.tsx
pnpm --dir apps/web build
```

### 7. 总体验证和 review 收口

更新：

```text
docs/milestones/v0.4-replay-branching/README.zh.md
docs/milestones/v0.4-replay-branching/plan.zh.md
docs/milestones/v0.4-replay-branching/review.zh.md
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

- 如果 replay / branch 需要 WorldEngine 私有源码、私有 helper、私有 prompt 或
  LLM key，停止并记录越界风险。
- 如果公开 snapshot / state diff 中没有足够信息，不得编造权威世界事实；应展示
  empty / degraded state。
- 如果任何 task 的验证失败，只能继续做针对该失败的窄修复。
- 如果发现 `plan.zh.md` 与实际 public payload 不匹配，先更新 milestone 文档并提
  交，再恢复实现。
- 不得在相关实现文件仍未提交时声明 v0.4 完成。

## 提交边界

每个 numbered task 必须单独提交。提交应只包含该 task 需要的文件。
