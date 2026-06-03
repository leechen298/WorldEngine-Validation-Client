# v0.6 Evidence Bundle 实现计划

状态：文档创建完成 / 实现待开始

## 实现目标

交付一个只基于本地公开验证记录的 evidence bundle 导出闭环：

- 后端可以为单个 session 生成稳定 JSON bundle。
- bundle manifest 记录 schema version、生成时间、session metadata、内容计数、
  脱敏标志、warning 和可重建 replay 索引摘要。
- bundle 内容包含客户端已保存的公开 event、state diff、snapshot、commit point、
  timeline branch、director intent、脱敏 API trace 和公开 evaluator 输出。
- 前端运行控制台展示 evidence bundle 状态并提供下载入口。
- 所有导出内容保持外部验证客户端边界，不保存或展示 LLM key、provider secret、
  private prompt、WorldEngine 私有 internals 或 Agent 私有内部状态。

## 技术栈

- 后端：FastAPI、Pydantic、SQLAlchemy、SQLite。
- 前端：React、Vite、TypeScript、Zustand。
- 测试：pytest、Vitest。

## 任务

### 1. v0.6 里程碑文档

创建：

```text
docs/milestones/v0.6-evidence-bundle/README.zh.md
docs/milestones/v0.6-evidence-bundle/plan.zh.md
docs/milestones/v0.6-evidence-bundle/review.zh.md
```

更新：

```text
docs/README.zh.md
```

要求：

- 明确 v0.6 目标、范围、非目标、验证命令和 commit 边界。
- 明确 evidence bundle 是本地证据包，不是权威 evaluator 报告。
- 明确客户端只能导出公开接口和本地客户端记录中允许保存的内容。
- 明确 bundle 不得包含 LLM key、provider secret、private prompt、WorldEngine
  私有 internals、Agent 私有内部状态或隐藏 evaluator oracle 信息。
- 保持 v0.6 实现顺序和逐 task commit 要求。

验证：

```bash
git diff --check
```

### 2. 后端 evidence bundle schema 和 manifest

更新：

```text
apps/api/app/schemas.py
apps/api/app/routes/evidence.py
apps/api/tests/test_evidence.py
```

要求：

- 新增 evidence bundle response schema，包含 `manifest` 和 `records` 两部分。
- `manifest` 至少包含 bundle schema version、generated at、session id、session
  name、worldengine world id、world status、counts、redaction flags 和 warnings。
- `records` 保持结构化 JSON，预留 events、state diffs、snapshots、commit points、
  branches、director intents、api traces、evaluator outputs 和 replay index。
- 保留现有 metadata endpoint 的兼容行为；不得破坏 `/sessions/{session_id}/evidence/bundle`
  现有调用方，除非在本 task 文档中明确迁移路径。
- 缺失 session 返回 `404`。
- 不新增任何 LLM key、provider secret、private prompt、Agent private state 或
  WorldEngine private internals 字段。

验证：

```bash
cd apps/api && uv run pytest tests/test_evidence.py -q
```

### 3. 后端 bundle 内容组装和脱敏检查

更新：

```text
apps/api/app/routes/evidence.py
apps/api/app/schemas.py
apps/api/tests/test_evidence.py
```

要求：

- 按稳定顺序导出 timeline branches、commit points、events、state diffs、snapshots、
  director intents 和 api traces。
- bundle 中的 API trace 只包含 method、url path、status code、request summary、
  response summary、error message 和脱敏标志。
- 对 request / response summary、event payload、state diff、snapshot 和 director
  intent public fields 做保守敏感词扫描；发现可能越界内容时不得标记为 clean，
  并在 manifest warnings 中记录可读 warning。
- 保持 `llm_keys_included=False` 和
  `private_worldengine_internals_included=False` 只在实际扫描结果支持时成立。
- 不伪造 WorldEngine evaluator 输出；没有公开 evaluator 输出时导出空列表或
 明确 warning。

验证：

```bash
cd apps/api && uv run pytest tests/test_evidence.py -q
```

### 4. 后端可下载 JSON endpoint

更新：

```text
apps/api/app/routes/evidence.py
apps/api/tests/test_evidence.py
```

要求：

- 新增下载 endpoint，返回完整 JSON evidence bundle，并设置明确文件名和
  `application/json` media type。
- 文件名应包含 session id 或安全 session slug，以及生成日期。
- 下载 endpoint 与 metadata / manifest endpoint 保持分离，避免旧 metadata 调用方
  被迫下载完整 bundle。
- 缺失 session 返回 `404`。
- 导出失败时返回可读错误，不写入不完整文件。

验证：

```bash
cd apps/api && uv run pytest tests/test_evidence.py -q
```

### 5. 前端 evidence bundle typed client 和状态

更新：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

要求：

- 定义 evidence bundle metadata / manifest / warning TypeScript 类型。
- 新增读取 bundle metadata 或 manifest 的 typed client 方法。
- 新增下载 bundle 的 client helper，保持浏览器下载行为可测试。
- Zustand store 保存每个 session 的 evidence bundle metadata、加载中状态和可读错误。
- 失败时保留现有 runtime console 状态，并展示可读错误。
- 前端类型和 store 不新增 LLM key、provider secret、private prompt、Agent private
  state 或 raw private response 字段。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
```

### 6. 运行控制台 evidence panel 和下载入口

更新：

```text
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/src/styles.css
```

要求：

- 运行控制台展示 evidence bundle panel，包含内容计数、脱敏状态、warning 和最后加载结果。
- 提供“下载 evidence bundle”入口，调用真实后端下载 endpoint。
- 下载失败时展示可读错误，不清空当前 session / replay / director guidance 状态。
- UI 文案明确 bundle 是“本地会话证据包”，不得暗示它是权威 evaluator 通过结论。
- UI 不展示 private payload、hidden context、raw private response 或 Agent 内部状态。

验证：

```bash
pnpm --dir apps/web test -- RuntimeConsole.test.tsx
pnpm --dir apps/web build
```

### 7. 总体验证和 review 收口

更新：

```text
docs/milestones/v0.6-evidence-bundle/README.zh.md
docs/milestones/v0.6-evidence-bundle/plan.zh.md
docs/milestones/v0.6-evidence-bundle/review.zh.md
```

运行：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.6-evidence-bundle
```

记录：

- 每个 task 的 commit。
- 变更文件。
- 命令结果。
- Scope review。
- 未实现的后续范围。
- WorldEngine public API 边界是否保持。
- 是否未保存或展示 LLM key、provider secrets、私有 WorldEngine internals、私有
  Agent 内部状态、hidden context 或 evaluator oracle internals。

## Stop Rules

- 如果 bundle 导出需要 WorldEngine 私有源码、私有 helper、私有 prompt、LLM key
  或 provider secret，停止并记录越界风险。
- 如果公开 evaluator 输出不可用，不得伪造 evaluator 结果。
- 如果扫描发现可能包含 key、secret、private prompt、private path、WorldEngine
  private internals、Agent private state 或 hidden context，不得把 bundle 标记为
  clean；必须记录 warning 或阻塞。
- 如果任何 task 的验证失败，只能继续做针对该失败的窄修复。
- 如果发现 `plan.zh.md` 与现有 API / 存储模型不匹配，先更新 milestone 文档并提交，
  再恢复实现。
- 不得在相关实现文件仍未提交时声明 v0.6 完成。

## 提交边界

每个 numbered task 必须单独提交。提交应只包含该 task 需要的文件。
