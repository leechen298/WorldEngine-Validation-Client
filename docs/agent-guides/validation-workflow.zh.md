# 验证工作流：Agent 自主验证 -> 人工验证

英文镜像：`validation-workflow.md`。

## 适用范围

本工作流用于验证已经实现的验证客户端 milestone，尤其是 v0.7 之后的
Agent 自主验证、Agent 复核和人工验证交接。

它不是开发实现流程。开发实现仍按 `workflow.zh.md` 的 task loop 执行。

## 触发词

当用户说以下请求时，进入本工作流：

- `自主验证 vX.Y`
- `Codex 验证 vX.Y`
- `Agent 自主测试 vX.Y`
- `Agent 验证 vX.Y`
- `人工验证 vX.Y`
- `人工复核 vX.Y`

## 必读文档

执行验证前必须读取：

1. `docs/README.zh.md`
2. `docs/roadmap.zh.md`
3. `docs/specs/validation-client-design.zh.md`
4. active milestone 的 `README.zh.md`
5. active milestone 的 `plan.zh.md`
6. active milestone 的 `implementation-task-plan.zh.md`，如果该文件存在
7. active milestone 的 `review.zh.md`
8. active milestone 的 `validation.zh.md`
9. `docs/agent-guides/routing.zh.md`
10. `docs/agent-guides/workflow.zh.md`
11. `docs/agent-guides/boundaries.zh.md`

人工验证还必须读取最近一次 Codex / Agent 自主验证 run 记录。

## 验证角色

### Codex 自主验证

Codex 自主验证证明客户端本身可靠、边界干净、证据可复盘，并判断是否可以进
入人工验证。

Codex 可以自动判断：

- 测试和构建是否通过。
- 基础 E2E / UI smoke 是否能完成。
- API endpoint 是否返回预期结构。
- Evidence bundle 是否可下载、可解析、计数一致。
- 脱敏标志和敏感内容扫描是否符合预期。
- 客户端是否仍只通过本地后端和 WorldEngine public API 工作。

Codex 不得自动声明：

- 世界体验已经通过。
- Agent 行为已经自然可信。
- 导演引导语义效果已经符合人类预期。
- WorldEngine evaluator 已经给出权威通过结论。

### Agent 自主测试

Agent 自主测试是由一个操作 Agent 以人的视角使用客户端。当前操作 Agent 可以
是 Codex，未来也可以是 OpenClaw 或其他 Agent。

操作 Agent 必须记录细粒度日志：

- 访问的 URL。
- 点击的按钮。
- 输入的文本。
- 选择的 branch / tick / commit point。
- 每个 API 请求和响应摘要。
- 服务端返回状态、错误和 evidence bundle manifest。
- 截图、下载文件名和关键 UI 状态。

日志必须足够让另一个 Agent 或人类复盘操作过程。

### Agent 验证

Agent 验证由另一个 Agent 读取上一轮操作日志、截图、API 记录和 evidence
bundle，进行独立复核。

复核 Agent 不能重新解释未记录的行为。它只能基于记录判断：

- 操作是否按计划执行。
- 证据是否完整。
- 结果是否支持进入人工验证。
- 是否存在必须先修复的缺口。

### 人工验证

人工验证不重复 Codex 的命令检查。人工验证专注判断：

- 世界是否可观察。
- 世界观、场景、Agent、事件是否连贯。
- Agent 是否像根据公开状态和事件自然反应。
- 导演引导是否只影响外部环境和事件趋势。
- 回放和 branch 是否像世界线 / 存档。
- Evidence bundle 是否足够让另一个人复盘。

## Codex 自主验证阶段

### 1. 预检

运行：

```bash
git status --short --branch
git diff --check
```

检查：

- 当前分支。
- 是否存在无关 dirty changes。
- 是否只有验证目标相关改动。

### 2. 后端验证

按 active milestone 的 `validation.zh.md` 执行后端命令。v0.7 默认包括：

```bash
cd apps/api && uv run pytest -q
cd apps/api && uv run pytest tests/test_evidence.py -q
```

### 3. 前端验证

按 active milestone 的 `validation.zh.md` 执行前端命令。v0.7 默认包括：

```bash
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
```

### 4. 基础 E2E / UI Smoke

Agent 必须用浏览器或 Playwright 以用户视角执行基础功能：

- 打开会话库。
- 检查 WorldEngine 连接状态。
- 创建本地 session 或 WorldEngine session。
- 进入运行控制台。
- 查看像素画布、公开状态、日志和 Agent 公开状态。
- 提交高层导演引导。
- 使用 replay / branch 控件。
- 打开 evidence panel。
- 下载 evidence bundle。

### 5. 操作日志

基础 E2E / UI smoke 必须产出结构化操作日志。日志至少包含：

```text
timestamp
actor
url
action_type
target
input_text
request_method
request_path
response_status
response_summary
visible_result
screenshot_path
notes
```

日志不允许包含 LLM key、provider secret、private prompt、private WorldEngine
internals、Agent private memory、private goal、identity、relationship 或 hidden
context。

### 6. Evidence Bundle 检查

Codex 必须检查下载的 evidence bundle：

- JSON 可解析。
- `manifest.session_id` 与验证 session 一致。
- counts 与 records 长度一致。
- warnings 可读。
- redaction flags 与 records 内容一致。
- bundle 不声称 evaluator 通过，除非 WorldEngine public evaluator 输出明确存在。

### 7. 边界扫描

执行敏感词扫描。命中项必须分类：

```bash
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones
```

允许命中：

- 脱敏常量。
- 负向测试。
- 边界文档。

不允许命中：

- UI 展示私有内容。
- bundle records 输出私有内容。
- 真实 secret。
- WorldEngine 私有路径或 helper 调用。

## 结论标准

### PASS

只有同时满足以下条件，Codex 自主验证才能写 PASS：

- 所有必跑命令在当前会话通过。
- 基础 E2E / UI smoke 完成。
- 操作日志完整。
- evidence bundle 可下载、可解析、可复盘。
- 脱敏和边界扫描通过。
- 没有相关未提交实现改动。
- 结论明确限定为“可以进入人工验证”。

### PARTIAL

核心命令通过，但 E2E、真实 WorldEngine 接入、evidence 下载或人工前置材料有缺
口时，写 PARTIAL。

### BLOCKED

依赖不可用、WorldEngine 未启动、LLM provider 未配置、端口冲突、沙箱权限或
真实浏览器不可用导致无法继续时，写 BLOCKED。

### FAIL

测试失败、构建失败、bundle 泄漏私有内容、边界违规、UI 误导为权威 evaluator
结论、操作日志缺失关键步骤时，写 FAIL。

## 输出位置

Codex 自主验证 run 记录写入：

```text
docs/milestones/vX.Y-*/validation-runs/YYYY-MM-DD-codex.zh.md
```

如果 active milestone 提供 `codex-run-report-template.zh.md`，必须按该模板输出。

Agent 操作日志可以保存为：

```text
docs/milestones/vX.Y-*/validation-runs/YYYY-MM-DD-agent-run.jsonl
```

如果 active milestone 提供 `agent-review-template.zh.md`，第二 Agent 复核必须按
该模板输出。

人工验证 run 记录写入：

```text
docs/milestones/vX.Y-*/validation-runs/YYYY-MM-DD-human.zh.md
```

如果 active milestone 提供 `human-validation-template.zh.md`，人工验证必须按该
模板输出。

## Stop Rules

- 如果 WorldEngine public API 不足以支持验证，停止并记录为 WorldEngine 前置缺口。
- 如果需要 LLM provider，必须由 WorldEngine 管理 provider 和 key，验证客户端不得
  接管。
- 如果 evidence bundle 出现私有内容，停止并记录 FAIL。
- 如果操作 Agent 无法生成可复盘日志，不得进入 Agent 验证。
- 如果 Codex 自主验证未完成，不得要求人工验证者直接判断完整产品通过。
