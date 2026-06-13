# v0.9.1 Complete Suite Runner And Operation Recording

英文镜像：`README.md`。

状态：implementation package drafted / ready for user approval
implementation_authorized: no
external_validation_authorized: no
provider_live_call_authorized: no

## 目标

把 v0.9 的完整分阶段验证文档变成可执行能力：

```text
Agent 按具体 UI 操作脚本运行 complete-worldengine-validation-suite，
并保存每个操作的详细完整记录。
```

## 背景

v0.9 已经定义：

- `agent-autonomous-operation-script.zh.md`：逐步操作脚本，包含按钮、输入、下载、
  截图和 blocked 行为。
- `operation-recording-contract.zh.md`：`operation-log.jsonl`、`api-log.jsonl`、
  `api-summary.json`、`console.log`、`transcript.md`、`screenshots/` 的记录契约。

但当前客户端还没有完整实现这些可执行能力。

## 范围

- 新增 `complete-worldengine-validation-suite` E2E runner。
- E2E 按 v0.9 operation script 执行 Phase 1-4。
- 每个 Playwright UI action 写入 `operation-log.jsonl`。
- 每个 Validation Client / WorldEngine API 请求摘要写入 `api-log.jsonl`。
- 生成 `api-summary.json`。
- 保存每阶段截图和关键 before/after 截图。
- 保存 `console.log`。
- 保存 `transcript.md`。
- 导出或组装 suite-level result directory。
- WorldEngine capability 缺失时输出 structured `BLOCKED`，不得伪造 PASS。

## 非目标

- 不直接调用 LLM provider。
- 不管理 provider key。
- 不生成 WorldEngine 权威世界事实。
- 不直接写 Agent memory、goal、thought、identity 或 hidden context。
- 不把 UI smoke 当 WorldEngine PASS。
- 不实现 WorldEngine 缺失的 public capability。

## 成功标准

- 可以运行完整 E2E runner。
- runner 产出 result directory。
- result directory 至少包含：
  - `operation-log.jsonl`
  - `api-log.jsonl`
  - `api-summary.json`
  - `console.log`
  - `transcript.md`
  - `screenshots/`
  - `result.json`
  - `coverage-matrix.json`
- 每个已执行 step 都有 `operation-log.jsonl` 记录。
- 每个 API 请求都有 `api-log.jsonl` 记录或明确 no-API reason。
- blocked path 也能输出完整 handoff evidence。
- redaction scan 不发现 secret/raw/private marker。

## 完整测试方案文件

```text
test-plan.zh.md
scenario-assertion-matrix.zh.md
result-directory-contract.zh.md
validation.zh.md
agent-execution-handoff.zh.md
```

这些文件合起来定义：

- 测试分层。
- 逐 step 断言。
- result directory schema。
- PASS/PARTIAL/BLOCKED/FAIL 规则。
- 实现聊天和自主验证聊天可直接使用的 prompt。

## 入口文档

实现前必须读取：

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/agent-autonomous-operation-script.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/operation-recording-contract.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/artifact-contract.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-runbook.zh.md
```

同时读取本包：

```text
test-plan.zh.md
scenario-assertion-matrix.zh.md
result-directory-contract.zh.md
validation.zh.md
agent-execution-handoff.zh.md
```
