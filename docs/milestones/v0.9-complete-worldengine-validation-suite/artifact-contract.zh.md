# Artifact Contract

英文镜像：`artifact-contract.md`。

## Result Directory

推荐输出：

```text
validation-runs/<timestamp>-complete-worldengine-validation-suite/
```

如果交给 WorldEngine checker，需要复制或同步到 WorldEngine 接受的 result path。

## 必需文件

```text
result.json
coverage-matrix.json
command-matrix.md
operation-log.jsonl
api-log.jsonl
api-summary.json
capability-discovery.json
world-creation-summary.json
session-summary.json
runtime-control-summary.json
timeline-evidence.json
direction-boundary-summary.json
agent-evidence.json
memory-continuity-summary.json
inspection-evidence.json
scorecard-input.json
redaction-report.json
console.log
transcript.md
second-agent-review.md
screenshots/
```

`operation-log.jsonl` 和 `api-log.jsonl` 的字段级要求见
`operation-recording-contract.zh.md`。完整自主测试的具体 step id、按钮、输入和
截图要求见 `agent-autonomous-operation-script.zh.md`。

## 操作记录要求

`operation-log.jsonl` 必须覆盖每一个由 Agent 执行的 UI 操作：

- 页面打开。
- 输入框填值。
- 按钮点击。
- 下拉选择。
- 等待页面元素或 API 响应。
- 下载 artifact。
- 截图。
- 阶段结论记录。
- blocked 操作。

`api-log.jsonl` 必须覆盖每一个 Validation Client API 或 WorldEngine public API 请求
摘要。direct API harvest 必须记录为 API evidence，不能伪装成用户点击。

如果任一已执行操作缺失记录，完整 suite 不能 PASS。

## 兼容输出

为了兼容 WorldEngine 当前 checker，可以同时生成旧名称：

```text
world-lifecycle-summary.json
diff-replay-summary.json
scorecard-summary.json
redaction-scan.json
```

但兼容文件不能替代 suite-level 必需文件。

## Redaction

禁止包含：

- API key、authorization header、credential、token、password、secret。
- raw prompt、raw provider request、raw provider response。
- private memory、private goal、raw thought、chain-of-thought、hidden context。
- WorldEngine private path、internal helper、source path。

任何 redaction blocking finding 都使 suite `fail`。
