# Operation Recording Contract

英文镜像：`operation-recording-contract.md`。

## 目标

Agent 自主测试必须保存完整、详细、可复核的原始操作记录。本文件定义
`operation-log.jsonl`、`api-log.jsonl`、`console.log`、`transcript.md` 和截图的最低
记录要求。

## 操作记录边界

操作记录分三类，不能混写：

| 类型 | 文件 | 含义 |
| --- | --- | --- |
| 用户/Agent UI 操作 | `operation-log.jsonl` | Agent 以用户视角做了什么：点击、输入、等待、选择、下载、截图。 |
| HTTP/API 交互 | `api-log.jsonl`、`api-summary.json` | Validation Client 与 WorldEngine / 自身 API 的请求和响应摘要。 |
| Agent 执行叙事 | `transcript.md` | Agent 用自然语言记录观察、判断、继续/停止原因和阶段结论。 |

Direct API harvest 不得写成 `operation-log.jsonl` 的用户点击。它必须写入
`api-log.jsonl`，并在 `transcript.md` 标明这是补充 evidence 采集。

## `operation-log.jsonl` schema

每行是一个 JSON object。最低字段：

```json
{
  "schema_version": "0.9.0",
  "run_id": "uuid-or-stable-id",
  "step_id": "P1-05",
  "phase": "phase-1",
  "actor": "codex-agent",
  "operation_kind": "click",
  "target": {
    "page": "Runtime Console",
    "role": "button",
    "label": "创建世界",
    "test_id": null,
    "selector": null
  },
  "input": {
    "text_redacted": null,
    "value_redacted": null,
    "value_length": null
  },
  "before": {
    "url": "http://127.0.0.1:5173/",
    "visible_text_summary": "会话库可见",
    "screenshot": "screenshots/phase-1-before-create-world.png"
  },
  "after": {
    "url": "http://127.0.0.1:5173/",
    "visible_text_summary": "运行控制可见",
    "screenshot": "screenshots/phase-1-after-create-world.png"
  },
  "api_refs": ["api-log:0004"],
  "artifact_refs": ["world-creation-summary.json"],
  "result": {
    "status": "executed",
    "blocked_reason": null,
    "error_message": null
  },
  "timestamp": "ISO-8601"
}
```

## `operation_kind`

允许值：

```text
page_open
click
fill
select
keyboard
wait_for_visible
wait_for_response
download
screenshot
observe
phase_verdict
blocked
```

如果实际操作不在允许值中，应先扩展 schema，而不是写自由文本。

## 输入记录规则

- 可以记录用户输入的公开世界观和公开方向，但必须同时记录长度和摘要。
- 不允许记录 provider API key、authorization header、raw prompt、raw provider
  response、private memory、raw thought。
- 如果输入文本可能包含敏感内容，`text_redacted` 只保留脱敏摘要，原文不得进入
  evidence bundle。
- 用户公开输入可以保存原文，但必须标记 `source: user_public_input`。

## `api-log.jsonl` schema

每行是一个 JSON object。最低字段：

```json
{
  "schema_version": "0.9.0",
  "run_id": "uuid-or-stable-id",
  "api_ref": "api-log:0004",
  "phase": "phase-1",
  "source_step_id": "P1-05",
  "method": "POST",
  "url_origin": "validation-client-api",
  "path_template": "/sessions/worldengine",
  "path_redacted": "/sessions/worldengine",
  "request_summary": {
    "body_shape": ["session_name", "worldview"],
    "public_input_lengths": {"worldview": 58},
    "secrets_included": false,
    "raw_prompt_included": false
  },
  "response_summary": {
    "status_code": 201,
    "body_shape": ["session", "world"],
    "world_id": "world-...",
    "error_class": null
  },
  "duration_ms": 123,
  "timestamp": "ISO-8601"
}
```

## `api-summary.json`

必须聚合：

- request count by phase。
- request count by method/path template。
- non-2xx responses。
- blocked capability calls。
- redaction status。
- direct API harvest entries。
- mapping from `step_id` to API refs。

## Screenshot 要求

最低截图：

```text
screenshots/phase-1-before-create-world.png
screenshots/phase-1-after-create-world.png
screenshots/phase-1-final.png
screenshots/phase-2-final.png
screenshots/phase-3-final.png
screenshots/phase-4-final.png
```

如果某阶段 blocked，也要保存 blocked 当时页面截图。

## `console.log`

必须保存：

- browser console warnings/errors。
- Validation Client frontend runtime errors。
- failed network requests 的公开摘要。

禁止保存 secret、authorization header、raw provider payload。

## `transcript.md`

必须包含：

```text
# Agent Autonomous Validation Transcript

## Run Metadata

## Phase 1
- What the Agent saw
- Operations performed
- Evidence downloaded
- Blockers or pass source

## Phase 2
...

## Phase 3
...

## Phase 4
...

## Final Classification
PASS / PARTIAL / BLOCKED / FAIL
```

Transcript 可以是人类可读文本，但不能替代 `operation-log.jsonl` 和 `api-log.jsonl`。

## PASS 门禁

完整自主验证要 PASS，必须满足：

- 每个 executed step 都有 `operation-log.jsonl` 记录。
- 每个请求都有 `api-log.jsonl` 记录或明确说明为什么没有 API。
- 每个 phase 有截图。
- 每个 downloaded artifact 有 `artifact_refs`。
- `transcript.md` 覆盖每个阶段。
- `redaction-report.json` 为 pass。

任何一项缺失，最终最多只能是 `PARTIAL` 或 `BLOCKED`，不能是 `PASS`。

